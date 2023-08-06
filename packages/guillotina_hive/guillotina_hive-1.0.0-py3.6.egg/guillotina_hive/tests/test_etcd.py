from guillotina_hive import etcd

import pytest


async def test_set_key(etcd_server):
    client = etcd.Client(host=etcd_server[0], port=etcd_server[1])
    await client.write('foo', 'bar')
    result = await client.get('foo')
    assert result['node']['value'] == 'bar'


async def test_create_folder(etcd_server):
    client = etcd.Client(host=etcd_server[0], port=etcd_server[1])
    await client.write('food', directory=True)
    await client.write('food/1', '1')
    await client.write('food/2', '2')
    await client.write('food/3', '3')
    result = await client.get('food', recursive=True)
    assert len(result['node']['nodes']) == 3


async def test_delete(etcd_server):
    client = etcd.Client(host=etcd_server[0], port=etcd_server[1])
    await client.write('foo', 'bar')
    result = await client.get('foo')
    assert result['node']['value'] == 'bar'
    await client.delete('foo')
    with pytest.raises(etcd.EtcdKeyNotFound):
        await client.get('foo')
