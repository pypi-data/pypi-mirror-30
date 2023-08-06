from datetime import datetime
from guillotina import app_settings
from guillotina.component import get_utility
from guillotina.exceptions import RequestNotFound
from guillotina.interfaces import IApplication
from guillotina.renderers import GuillotinaJSONEncoder
from guillotina.utils import get_current_request
from guillotina.utils import lazy_apply
from guillotina.utils import resolve_dotted_name
from guillotina_hive.exceptions import NoTaskFunctionFoundError
from guillotina_hive.interfaces import CANCELLED
from guillotina_hive.interfaces import ERRORED
from guillotina_hive.interfaces import FINISHED
from guillotina_hive.interfaces import STARTED
from guillotina_hive.interfaces import UNSCHEDULED
from guillotina_hive.utils import create_task_request

import asyncio
import json
import logging
import uuid


logger = logging.getLogger('guillotina_hive')


class TaskInfo:
    _request_headers = {}

    def __init__(self, name, data={}, status=UNSCHEDULED,
                 task_id=None, worker_id=None, started_on=None,
                 finished_on=None, error_msg=None, return_value=None,
                 request_url=None, request_headers=None, request=None,
                 tags=None, port=None):
        self._name = name
        self._data = data
        self._status = status
        if task_id is None:
            task_id = str(uuid.uuid4().hex)
        self._task_id = task_id
        self._worker_id = worker_id
        self._started_on = started_on
        self._finished_on = finished_on
        self._error_msg = error_msg
        self._tags = tags
        self._port = port
        self._aio_task = None
        self._return_value = return_value
        self._request_url = request_url
        if request_headers is not None:
            self._request_headers = request_headers

        if request_url is None:
            try:
                if request is None:
                    request = get_current_request()
                self._request_url = str(request.url)
                self._request_headers = dict(request.headers)
            except RequestNotFound:
                pass

    @property
    def status(self):
        return self._status

    @property
    def data(self):
        return self._data

    @property
    def name(self):
        return self._name

    @property
    def task_id(self):
        return self._task_id

    @property
    def tags(self):
        return self._tags

    @property
    def port(self):
        return self._port

    @property
    def worker_id(self):
        return self._worker_id

    @property
    def finished_on(self):
        return self._finished_on

    @property
    def started_on(self):
        return self._started_on

    @property
    def error_msg(self):
        return self._error_msg

    @property
    def return_value(self):
        return self._return_value

    @property
    def request_url(self):
        return self._request_url

    @property
    def request_headers(self):
        return self._request_headers

    def set_task_id(self, _id):
        self._task_id = _id

    def set_worker_id(self, _id):
        self._worker_id = _id

    def issue_new_id(self):
        self._task_id = str(uuid.uuid4().hex)

    def start(self):
        self._started_on = datetime.utcnow()
        self._status = STARTED

    def finish(self):
        self._finished_on = datetime.utcnow()
        self._status = FINISHED
        self._aio_task = None

    def cancel(self):
        self._finished_on = datetime.utcnow()
        self._status = CANCELLED
        if self._aio_task is not None:
            self._aio_task.cancel()
            self._aio_task = None

    def error(self, reason):
        self._finished_on = datetime.utcnow()
        self._status = ERRORED
        self._error_msg = reason
        self._aio_task = None

    def assign_aio_task(self, aio_task):
        self._aio_task = aio_task

    def serialize_dict(self):
        return {
            'name': self._name,
            'status': self._status,
            'data': self._data,
            'task_id': self._task_id,
            'worker_id': self._worker_id,
            'tags': self._tags,
            'port': self._port,
            'started_on': self._started_on and self._started_on.isoformat(),
            'finished_on': self._finished_on and self._finished_on.isoformat(),
            'error_msg': self._error_msg,
            'return_value': self._return_value,
            'request_url': self._request_url,
            'request_headers': self._request_headers
        }

    def serialize(self):
        return json.dumps(self.serialize_dict(), cls=GuillotinaJSONEncoder)

    @classmethod
    def deserialize(kls, value):
        if isinstance(value, str):
            value = json.loads(value)
        started_on = value.pop('started_on', None)
        finished_on = value.pop('finished_on', None)

        return kls(
            value.pop('name'),
            data=value.pop('data'),
            status=value.pop('status'),
            task_id=value.pop('task_id'),
            worker_id=value.pop('worker_id'),
            tags=value.pop('tags', []),
            port=value.pop('port', None),
            started_on=started_on and datetime.strptime(started_on, "%Y-%m-%dT%H:%M:%S.%f"),
            finished_on=finished_on and datetime.strptime(finished_on, "%Y-%m-%dT%H:%M:%S.%f"),
            error_msg=value.pop('error_msg', None),
            return_value=value.pop('return_value', None),
            request_url=value.pop('request_url', None),
            request_headers=value.pop('request_headers', {})
        )

    def clone(self):
        return TaskInfo(self._name, data=self._data)


class TaskRunner:

    def __init__(self, task_info, func, request=None):
        self.task_info = task_info
        if request is None:
            request = create_task_request(task_info)
        self.request = request
        self.func = func

    async def run(self):
        result = lazy_apply(
            self.func, request=self.request, task_info=self.task_info,
            root=get_utility(IApplication, name='root'))

        if asyncio.iscoroutine(result):
            result = await result
        return result


async def run_task(task_info, request=None):
    if task_info.name not in app_settings['hive_tasks']:
        raise NoTaskFunctionFoundError(task_info.name)

    try:
        func = resolve_dotted_name(app_settings['hive_tasks'][task_info.name])
    except ModuleNotFoundError:
        raise NoTaskFunctionFoundError(app_settings['hive_tasks'][task_info.name])

    logger.warning('Running task {}({})'.format(task_info.name, task_info.task_id))
    runner = TaskRunner(task_info, func, request)
    value = await runner.run()
    task_info._return_value = value
    return value
