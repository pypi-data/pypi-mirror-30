import aiohttp


class EtcdException(Exception):
    def __init__(self, resp):
        self.resp = resp


class EtcdKeyNotFound(EtcdException):
    pass


class Client:

    def __init__(self, host='127.0.0.1', port=2379, loop=None):
        self._host = host
        self._port = port
        self._session = aiohttp.ClientSession()
        self._base_url = f'http://{host}:{port}/'

    def _get_url(self, path):
        return f'{self._base_url}{path}'

    def _check_response(self, resp):
        if resp.status == 404:
            raise EtcdKeyNotFound(resp)

    async def version(self):
        url = self._get_url('version')
        async with self._session.get(url) as resp:
            return await resp.json()

    async def get(self, key, recursive=False):
        params = {}
        if recursive:
            params['recursive'] = 'true'
        url = self._get_url('v2/keys/' + key)
        async with self._session.get(url, params=params) as resp:
            self._check_response(resp)
            return await resp.json()

    async def write(self, key, value=None, directory=False):
        params = {}
        if value is not None:
            params['value'] = value
        elif directory:
            params['dir'] = 'true'

        url = self._get_url('v2/keys/' + key)
        async with self._session.put(url, params=params) as resp:
            self._check_response(resp)
            return await resp.json()

    async def delete(self, key):
        url = self._get_url('v2/keys/' + key)
        async with self._session.delete(url) as resp:
            self._check_response(resp)
            return await resp.json()
