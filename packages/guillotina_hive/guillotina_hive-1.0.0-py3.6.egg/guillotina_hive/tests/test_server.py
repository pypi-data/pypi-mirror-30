from guillotina_hive.server import MANAGED_TASKS
from guillotina_hive.server import REQUEST_TASKS
from guillotina_hive.server import Server
from guillotina_hive.task import TaskInfo

import asyncio
import json


class DummyReader:

    def set_message(self, data):
        self.data = data

    async def read(self):
        return self.data


class DummyWriter:

    def write(self, data):
        self.data = data

    def write_eof(self):
        pass

    async def drain(self):
        pass

    def close(self):
        pass


class DummyWorker:

    worker_id = 'foobar'


async def test_ping(dummy_request, loop):
    server = Server(None, None, loop)
    len_tasks = len(asyncio.Task.all_tasks(loop))
    reader = DummyReader()
    reader.set_message(json.dumps({
        'message_type': 'ping'
    }).encode('utf-8'))
    writer = DummyWriter()
    server(reader, writer)
    assert len(asyncio.Task.all_tasks(loop)) == (len_tasks + 1)
    assert len(REQUEST_TASKS) == 1
    await asyncio.wait_for(REQUEST_TASKS[0], 1, loop=loop)
    assert len(REQUEST_TASKS) == 0
    data = json.loads(writer.data.decode('utf-8'))
    assert data['value']['response'] == 'pong'
    assert data['value']['active']['count'] == 0
    assert data['value']['execution_time'] == 0


async def test_ping_with_tasks(dummy_request, loop):
    server = Server(None, DummyWorker(), loop)
    reader = DummyReader()
    task_info = TaskInfo('slow_task', {
        'timeout': 0.5
    })
    reader.set_message(json.dumps({
        'message_type': 'task',
        'data': task_info.serialize()
    }).encode('utf-8'))
    writer = DummyWriter()
    server(reader, writer)
    await asyncio.wait_for(REQUEST_TASKS[0], 1, loop=loop)

    assert len(MANAGED_TASKS) == 1
    reader.set_message(json.dumps({
        'message_type': 'ping'
    }).encode('utf-8'))
    server(reader, writer)
    await asyncio.wait_for(REQUEST_TASKS[0], 1, loop=loop)
    data = json.loads(writer.data.decode('utf-8'))
    assert data['value']['active']['count'] == 1
    await asyncio.wait_for([v for v in MANAGED_TASKS.values()][0]._aio_task, 1, loop=loop)

    server(reader, writer)
    await asyncio.wait_for(REQUEST_TASKS[0], 1, loop=loop)
    data = json.loads(writer.data.decode('utf-8'))
    assert data['value']['active']['count'] == 0
