import json
import uuid


class Worker:

    def __init__(self, host, port, tags=None, worker_id=None, hostname=None,
                 connect_host=None, active_tasks={}, scheduled_tasks={}, execution_time=0):
        self._host = host
        self._port = port
        self._tags = tags
        if worker_id is None:
            worker_id = str(uuid.uuid4().hex)
        self._worker_id = worker_id
        self._connect_host = connect_host
        self._hostname = hostname
        self._execution_time = execution_time
        self._active_tasks = active_tasks
        self._scheduled_tasks = scheduled_tasks

    @property
    def host(self):
        return self._host

    @property
    def connect_host(self):
        if self._connect_host is None:
            return self._host
        return self._connect_host

    @property
    def port(self):
        return self._port

    @property
    def worker_id(self):
        return self._worker_id

    @property
    def hostname(self):
        return self._hostname

    @property
    def tags(self):
        return self._tags

    @property
    def execution_time(self):
        return self._execution_time

    @property
    def active_tasks(self):
        return self._active_tasks

    @property
    def scheduled_tasks(self):
        return self._scheduled_tasks

    @property
    def num_tasks(self):
        return len(self._scheduled_tasks) + len(self._active_tasks)

    def register_stats(self, active, scheduled, execution_time):
        self._active_tasks = active
        self._scheduled_tasks = scheduled
        self._execution_time = execution_time

    def serialize(self):
        return json.dumps({
            'id': self.worker_id,
            'host': self.host,
            'port': self.port,
            'hostname': self.hostname,
            'active_tasks': self._active_tasks,
            'scheduled_tasks': self._scheduled_tasks,
            'execution_time': self._execution_time,
            'connect_host': self._connect_host,
            'tags': self._tags
        })

    @classmethod
    def deserialize(kls, node):
        value = json.loads(node.pop('value'))
        return kls(
            value.pop('host'),
            value.pop('port'),
            worker_id=value.pop('id'),
            hostname=value.pop('hostname', 'unknown...'),
            tags=value.pop('tags', None),
            active_tasks=value.pop('active_tasks'),
            scheduled_tasks=value.pop('scheduled_tasks'),
            execution_time=value.pop('execution_time'),
            connect_host=value.pop('connect_host', None)
        )
