import asyncio
import json
import logging

import aiohttp

from guillotina import app_settings
from guillotina import configure
from guillotina.exceptions import RequestNotFound
from guillotina.utils import get_authenticated_user_id
from guillotina.utils import get_current_request
from guillotina.utils import resolve_dotted_name
from guillotina_hive import client
from guillotina_hive import etcd
from guillotina_hive.exceptions import EtcdError
from guillotina_hive.exceptions import HiveNotInitialized
from guillotina_hive.exceptions import NoAvailableWorkers
from guillotina_hive.interfaces import IHiveUtility
from guillotina_hive.task import TaskInfo
from guillotina_hive.worker import Worker

logger = logging.getLogger('guillotina_hive')


class WorkerManager:
    '''
    Abstraction done here so we can run tests without running an actual server...
    '''

    def __init__(self, utility):
        self._utility = utility
        self._client = utility._client
        self._workers = {}
        self._this_worker = None

    async def register(self, worker: Worker):
        # only one possible worker can be registered per app, keep track of it..
        self._this_worker = worker
        await self._client.write(
            self._utility.worker_registration_key + '/' + worker.worker_id,
            worker.serialize())

    async def add_task(self, worker: Worker, task: TaskInfo):
        task.set_worker_id(worker.worker_id)
        try:
            req = get_current_request()
            task.data['initiated_by'] = get_authenticated_user_id(req)
        except RequestNotFound:
            pass
        await client.send_data(worker, {
            'message_type': 'task',
            'data': task.serialize()
        })
        worker._scheduled_tasks['count'] += 1
        worker._scheduled_tasks['keys'].append(task.task_id)

    async def sync_workers(self):
        result = await self._client.get(
            self._utility.worker_registration_key, recursive=True)
        found = {}
        logger.warning('Starting Sync of %d nodes' % len(result['node'].get('nodes', [])))
        for node in result['node'].get('nodes', []):
            if node.get('dir') is True:
                # it's the folder, ignore
                continue
            worker = Worker.deserialize(node)
            success = False
            if self._this_worker is not None:
                if self._this_worker.worker_id == worker.worker_id:
                    continue
                if (self._this_worker.host == worker.host and
                        self._this_worker.port == worker.port and
                        self._this_worker.hostname == worker.hostname):
                    # running on same port, just stale, delete and continue
                    try:
                        await self._client.delete(node['key'])
                    except etcd.EtcdKeyNotFound:
                        pass
                    continue

            try:
                resp = await client.send_data(worker, {'message_type': 'ping'})
                value = resp['value']
                if resp['success'] and 'pong' == value['response']:
                    success = True
                    worker.register_stats(value['active'], value['scheduled'],
                                          value['execution_time'])
                    self._workers[worker.worker_id] = worker
            except (ConnectionRefusedError, OSError):
                logger.warning(f'Connection error on {worker.worker_id}',
                               exc_info=True)
                # I may have no connection to it but be a valid worker
                # TODO: so we need to have a backoff policy
            except json.decoder.JSONDecodeError:
                logger.warning(f'json decode error trying to ping {worker.worker_id}',
                               exc_info=True)
                continue
            except Exception as ex:
                logger.warning('Unknown error checking worker availability',
                               exc_info=True)
            if success:
                found[worker.worker_id] = node['key']
            else:
                # Ping has not worked
                if worker.worker_id in self._workers:
                    logger.info(f'Removing stale worker {worker.worker_id}')
                    del self._workers[worker.worker_id]
                try:
                    await self._client.delete(node['key'])
                except etcd.EtcdKeyNotFound:
                    pass

        if self._this_worker is not None:
            # make sure we're registered...
            await self.register(self._this_worker)

        workers_to_delete = []
        for worker_id in self._workers.keys():
            if worker_id not in found:
                workers_to_delete.append(worker_id)

        for to_delete in workers_to_delete:
                del self._workers[to_delete]

    def remove_worker(self, worker: Worker):
        del self._workers[worker.worker_id]
        if self._this_worker == worker.worker_id:
            self._this_worker = None

    def pick_worker(self, avoid=None, tags=None):
        # Pick the one with less work to do
        if len(self._workers) == 0:
            raise NoAvailableWorkers('Could not find worker')
        picked = None
        for worker in self._workers.values():
            if avoid is not None and worker in avoid:
                continue
            if picked is None or picked.num_tasks > worker.num_tasks:
                if tags is None:
                    picked = worker
                    continue
                elif worker.tags is not None:
                    common = [tag for tag in tags if tag in worker.tags]
                    if len(common) == len(tags):
                        picked = worker
                        continue

        if picked is None:
            raise NoAvailableWorkers('Could not find worker')
        return picked

    async def get_task_status(self, worker: Worker, task_id: str):
        data = await client.send_data(worker, {
            'message_type': 'status',
            'task_id': task_id
        })
        if data and data['success']:
            return TaskInfo.deserialize(data['value'])


@configure.utility(provides=IHiveUtility)
class HiveUtility:

    def __init__(self, settings=None, loop=None):
        self._loop = loop
        self._settings = {}
        self._app = None
        self._initialized = False
        self._workers = {}
        self._tasks = {}
        self._worker_manager = None
        self._client = None

    @property
    def base_key(self):
        return self._settings['etcd'].get('base-key', 'guillotina-')

    @property
    def worker_registration_key(self):
        return self.base_key + 'hiveworkers'

    @property
    def initialized(self):
        return self._initialized

    @property
    def workers(self):
        return self._worker_manager._workers

    async def create_worker_folders(self):
        for folder_key in (self.worker_registration_key,):
            try:
                await self._client.get(folder_key)
            except etcd.EtcdKeyNotFound:
                await self._client.write(folder_key, directory=True)
            except etcd.EtcdException as ex:
                raise EtcdError('Unexpected error creating etcd queue {}'.format(
                    json.dumps(ex.resp)))

    async def initialize(self, app=None):
        self._app = app
        self._settings = app_settings['hive']
        if self._settings['etcd']['host'] != '<test>':
            # disable when set to testing...
            try:
                self._client = etcd.Client(loop=self._loop, **self._settings['etcd'])
                await self._client.version()  # test connection
            except (ConnectionRefusedError, GeneratorExit, RuntimeError, OSError,
                    aiohttp.client_exceptions.ClientConnectorError, asyncio.CancelledError):
                logger.warning('Failed to connect to etcd. Hive not operable.')
                return
            except Exception:
                logger.error('Failed to initialize etcd. Hive is not operable', exc_info=True)
                return

        worker_class = resolve_dotted_name(
            self._settings.get('worker_manager_class', 'guillotina_hive.utility.WorkerManager'))
        self._worker_manager = worker_class(self)

        # check that queue directory is created
        await self.create_worker_folders()
        self._initialized = True
        await self.run()

    async def run(self):
        while True:
            try:
                await self._worker_manager.sync_workers()
            except EtcdError:
                logger.warning('Etcd error', exc_info=True)
            except Exception:
                logger.warning('Error Syncing Workers', exc_info=True)
            await asyncio.sleep(self._settings['sync_timeout'])

    async def finalize(self, app=None):
        if self._worker_manager is not None and self._worker_manager._this_worker is not None:
            worker_id = self._worker_manager._this_worker.worker_id
            try:
                await self._client.delete(
                    self.worker_registration_key + '/' + worker_id)
            except etcd.EtcdKeyNotFound:
                pass

    async def add_task(self, task, retries=0):
        """
        lookup registered workers and push task to it
        """
        try:
            worker = self._worker_manager.pick_worker()
        except NoAvailableWorkers:
            await self._worker_manager.sync_workers()
            worker = self._worker_manager.pick_worker()

        try:
            await self._worker_manager.add_task(worker, task)
        except (ConnectionRefusedError, OSError):
            if retries < 2:
                # resync workers and try again, we might have a stale worker...
                await self._worker_manager.sync_workers()
                await self.add_task(task, retries=retries + 1)
            else:
                raise

    async def dist_task(self, tasks):
        """
        allocate num of tasks workers
        """
        if len(tasks) > len(self._worker_manager._workers):
            raise NoAvailableWorkers('Too much tasks to run')

        # Create cluster config with the tasks
        cluster_info = {}
        workers = []

        for task in tasks:
            try:
                worker = self._worker_manager.pick_worker(tags=task.tags, avoid=workers)
            except NoAvailableWorkers:
                # If there is no available worker quit
                await self._worker_manager.sync_workers()
                worker = self._worker_manager.pick_worker(tags=task.tags, avoid=workers)

            if task._name in cluster_info:
                cluster_info[task._name].append((worker.hostname, task.port))
            else:
                cluster_info[task._name] = [(worker.hostname, task.port)]
            task._data['myself'] = worker.hostname
            task._data['myport'] = task.port
            task._data['cluster'] = cluster_info
            workers.append(worker)

        # { task_name : [hostname, hostname] }
        for x in range(len(tasks)):
            await self._worker_manager.add_task(workers[x], tasks[x])

    async def get_task_status(self, worker: Worker, task_id):
        return await self._worker_manager.get_task_status(worker, task_id)

    async def _register_worker(self, worker: Worker):
        while not self.initialized:
            await asyncio.sleep(0.1)
        await self._worker_manager.register(worker)

    async def register_worker(self, worker: Worker):
        try:
            await asyncio.wait_for(self._register_worker(worker), timeout=10)
        except asyncio.TimeoutError:
            raise HiveNotInitialized('Timed out registering worker because '
                                     'the hive still has not initialized.')

    async def cancel_task(self, worker: Worker, task_id):
        return await client.send_data(worker, {
            'message_type': 'cancel',
            'task_id': task_id
        })

    async def query_tasks(self, query, worker: Worker=None):
        results = []
        query['message_type'] = 'query'

        await self._worker_manager.sync_workers()

        if worker is None:
            workers = self.workers.values()
        else:
            workers = [worker]

        for worker in workers:
            result = await client.send_data(worker, query)
            results.extend(result['value'])
        return results
