import asyncio
import concurrent
import json
import logging
import socket
import traceback
from datetime import datetime
from fnmatch import fnmatch

import aiotask_context

from guillotina import app_settings
from guillotina.component import get_utility
from guillotina_hive.interfaces import CANCELLED
from guillotina_hive.interfaces import ERRORED
from guillotina_hive.interfaces import FINISHED
from guillotina_hive.interfaces import IHiveUtility
from guillotina_hive.interfaces import SCHEDULED
from guillotina_hive.interfaces import STARTED
from guillotina_hive.task import TaskInfo
from guillotina_hive.task import run_task
from guillotina_hive.utils import create_task_request
from guillotina_hive.worker import Worker

logger = logging.getLogger('guillotina_hive')


MANAGED_TASKS = {}
REQUEST_TASKS = []


def _cleanup_tasks():
    cleanup_seconds = app_settings['hive']['task_cache_duration']
    now = datetime.utcnow()
    for task_id in [k for k in MANAGED_TASKS.keys()]:
        task = MANAGED_TASKS[task_id]
        if task.status in (FINISHED, ERRORED, CANCELLED):
            if (now - task.finished_on).seconds > cleanup_seconds:
                del MANAGED_TASKS[task_id]


def _count_active_tasks():
    count = 0
    for task in MANAGED_TASKS.values():
        if task.status == STARTED:
            count += 1
    return count


class TaskRunner:

    def __init__(self, task_info, server):
        self._server = server
        self._task_info = task_info

    async def __call__(self):
        request = create_task_request(self._task_info)
        aiotask_context.set('request', request)
        try:
            self._task_info._status = SCHEDULED

            while _count_active_tasks() >= app_settings['hive']['concurrency']:
                await asyncio.sleep(5)
        except concurrent.futures.CancelledError:
            # we're okay with tasks being cancelled and this one is cancelled
            # before it even starts
            _cleanup_tasks()
            return

        self._task_info.start()
        try:
            await run_task(self._task_info, request)
        except concurrent.futures.CancelledError:
            # we're okay with tasks being cancelled...
            pass
        except Exception as ex:
            logger.error('Task error', exc_info=True)
            self._task_info.error(traceback.format_exc())
        else:
            self._task_info.finish()
        aiotask_context.set('request', None)
        _cleanup_tasks()


class RequestAction:

    def __init__(self, req, data):
        self._request = req
        self._data = data
        self._server = self._request._server

    def __call__(self):
        pass


class CancelAction(RequestAction):

    def __call__(self):
        task_id = self._data['task_id']
        logger.warning(f'Cancelling task {task_id}')
        if task_id in MANAGED_TASKS:
            task = MANAGED_TASKS[task_id]
            task.cancel()
            _cleanup_tasks()
            self._request.handle_success(f'cancelled task {task_id}')
        else:
            self._request.handle_error('Task not found')


class PingAction(RequestAction):

    def __call__(self):
        execution_time = 0
        now = datetime.utcnow()
        active = []
        scheduled = []
        for task in MANAGED_TASKS.values():
            if task.status == STARTED:
                active.append(task.task_id)
                execution_time += (now - task.started_on).seconds
            elif task.status == SCHEDULED:
                scheduled.append(task.task_id)
        self._request.handle_success({
            'response': 'pong',
            'active': {
                'count': len(active),
                'keys': active
            },
            'scheduled': {
                'count': len(scheduled),
                'keys': scheduled
            },
            'execution_time': execution_time
        })


class StatusAction(RequestAction):

    def __call__(self):
        task_id = self._data['task_id']
        if task_id in MANAGED_TASKS:
            self._request.handle_success(MANAGED_TASKS[task_id].serialize_dict())
        else:
            self._request.handle_error('Task not found')


class TaskAction(RequestAction):

    def __call__(self):
        task_info = TaskInfo.deserialize(self._data['data'])
        logger.warning('New Task received on %s' % self._server._worker.worker_id)
        task_info.set_worker_id(self._server._worker.worker_id)
        runner = TaskRunner(task_info, self._server)

        task = self._server.loop.create_task(runner())
        task_info.assign_aio_task(task)
        MANAGED_TASKS[task_info.task_id] = task_info
        self._request.handle_success('scheduled')


class QueryAction(RequestAction):

    def __call__(self):
        maxi = int(self._data.pop('max', 50))
        target_status = self._data.pop('status', None)
        if target_status is not None and type(target_status) != list:
            target_status = [target_status]
        target_name = self._data.pop('task_name', None)

        results = []
        for task in MANAGED_TASKS.values():
            if target_status is not None and task.status not in target_status:
                continue
            if target_name is not None and task.name != target_name:
                continue
            matches = True
            for key, val in self._data.items():
                if key not in task.data:
                    matches = False
                    break
                if not fnmatch(task.data[key], val):
                    matches = False
                    break
            if matches:
                results.append(task.serialize_dict())
                if len(results) > maxi:
                    break

        self._request.handle_success(results)


class Request:
    _request_actions = {
        'cancel': CancelAction,
        'ping': PingAction,
        'status': StatusAction,
        'task': TaskAction,
        'query': QueryAction
    }

    def __init__(self, reader, writer, server):
        self._reader = reader
        self._writer = writer
        self._server = server

    async def __call__(self):
        message = await self._reader.read()

        try:
            data = json.loads(message.decode('utf8'))
        except Exception:
            logger.warning('Error decoding client message', exc_info=True)
            await self.handle_error('Error decoding client message')
        else:
            self.handle_message(data)

        self._writer.write_eof()
        await self._writer.drain()
        self._writer.close()

    def handle_message(self, data):
        message_type = data.pop('message_type')
        if message_type in self._request_actions:
            action = self._request_actions[message_type](self, data)
            action()
        else:
            self.handle_error(f'Invalid message_type of {message_type}. '
                              f'Valid types are {", ".join(self._request_actions.keys())}')

    def handle_success(self, value):
        self._writer.write(json.dumps({
            'success': True,
            'value': value
        }).encode('utf-8'))

    def handle_error(self, msg):
        logger.warning(msg)
        self._writer.write(json.dumps({
            'success': False,
            'message': msg
        }).encode('utf-8'))


class Server:

    def __init__(self, app, worker, loop):
        self._app = app
        self._utility = get_utility(IHiveUtility)
        self._worker = worker
        self.loop = loop
        self._aioserver = None

    def __call__(self, reader, writer):
        req = Request(reader, writer, self)
        task = self.loop.create_task(req())
        REQUEST_TASKS.append(task)

        def client_done(task):
            REQUEST_TASKS.remove(task)
            writer.close()

        task.add_done_callback(client_done)

    def set_aio_server(self, aioserver):
        self._aioserver = aioserver

    def close(self):
        if self._aioserver is not None:
            self._aioserver.close()


class ServerRouter:
    def __init__(self, application_server):
        self.application_server = application_server

    def set_root(self, root):
        self.application_server.root = root
        self._root = root


class ApplicationServer:
    root = None

    def __init__(self, loop=None):
        self.router = ServerRouter(self)
        self.on_cleanup = []
        self.loop = loop


def get_ip():
    # from https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


async def run_server(gapp, loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()
    loop.set_task_factory(aiotask_context.task_factory)

    # Each client connection will create a new protocol instance
    settings = app_settings['hive']
    host = settings['worker_host']
    connect_host = settings.get('worker_connect_host')
    if connect_host is None:
        if host == '0.0.0.0':
            # it is only local...
            connect_host = get_ip()
        else:
            connect_host = host
    if 'tags' in settings:
        tags = settings['tags']
    else:
        tags = []

    worker = Worker(host, settings['worker_port'],
                    hostname=socket.gethostname(),
                    connect_host=connect_host,
                    tags=tags)
    server = Server(gapp, worker, loop)
    if 'local_host' in settings:
        hostname = settings['local_host']
    else:
        hostname = worker.host
    aioserver = await asyncio.start_server(server, hostname, worker.port)
    server.set_aio_server(aioserver)
    utility = get_utility(IHiveUtility)
    await utility.register_worker(worker)
    logger.warning(f'Serving worker({worker.worker_id}) on {connect_host}')
    return server
