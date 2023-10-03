import asyncio
import io

import pytest

from connect.client import AsyncConnectClient, ClientError
from connect.client.logger import RequestLogger
from connect.client.models import AsyncCollection, AsyncNS


@pytest.mark.asyncio
async def test_async_get(async_mocker):
    url = 'https://localhost'
    kwargs = {
        'arg1': 'val1',
    }
    c = AsyncConnectClient('API_KEY')
    mocked = async_mocker.AsyncMock()
    c.execute = mocked
    await c.get(url, **kwargs)
    mocked.assert_awaited_once_with('get', url, **kwargs)


@pytest.mark.asyncio
@pytest.mark.parametrize('attr', ('payload', 'json'))
async def test_create(async_mocker, attr):
    mocked = async_mocker.AsyncMock()
    url = 'https://localhost'
    kwargs = {
        'arg1': 'val1',
    }
    kwargs[attr] = {'k1': 'v1'}

    c = AsyncConnectClient('API_KEY')
    c.execute = mocked

    await c.create(url, **kwargs)

    mocked.assert_awaited_once_with(
        'post',
        url,
        **{
            'arg1': 'val1',
            'json': {
                'k1': 'v1',
            },
        },
    )


@pytest.mark.asyncio
@pytest.mark.parametrize('attr', ('payload', 'json'))
async def test_update(async_mocker, attr):
    mocked = async_mocker.AsyncMock()
    url = 'https://localhost'
    kwargs = {
        'arg1': 'val1',
    }
    kwargs[attr] = {'k1': 'v1'}

    c = AsyncConnectClient('API_KEY')
    c.execute = mocked

    await c.update(url, **kwargs)

    mocked.assert_awaited_once_with(
        'put',
        url,
        **{
            'arg1': 'val1',
            'json': {
                'k1': 'v1',
            },
        },
    )


@pytest.mark.asyncio
async def test_delete_no_args(async_mocker):
    mocked = async_mocker.AsyncMock()
    url = 'https://localhost'

    c = AsyncConnectClient('API_KEY')
    c.execute = mocked

    await c.delete(url)

    mocked.assert_awaited_once_with('delete', url)


@pytest.mark.asyncio
@pytest.mark.parametrize('attr', ('payload', 'json'))
async def test_delete(async_mocker, attr):
    mocked = async_mocker.AsyncMock()
    url = 'https://localhost'

    kwargs = {
        'arg1': 'val1',
    }
    kwargs[attr] = {'k1': 'v1'}

    c = AsyncConnectClient('API_KEY')
    c.execute = mocked

    await c.delete(url, **kwargs)

    mocked.assert_awaited_once_with(
        'delete',
        url,
        **{
            'arg1': 'val1',
            'json': {
                'k1': 'v1',
            },
        },
    )


@pytest.mark.asyncio
async def test_execute(httpx_mock):
    expected = [{'id': i} for i in range(10)]
    httpx_mock.add_response(
        method='GET',
        url='https://localhost/resources',
        json=expected,
    )

    ios = io.StringIO()
    c = AsyncConnectClient('API_KEY', endpoint='https://localhost', logger=RequestLogger(file=ios))

    results = await c.execute('get', 'resources')

    assert httpx_mock.get_requests()[0].method == 'GET'
    headers = httpx_mock.get_requests()[0].headers

    assert 'Authorization' in headers and headers['Authorization'] == 'API_KEY'
    assert 'User-Agent' in headers and headers['User-Agent'].startswith('connect-fluent')

    assert results == expected


@pytest.mark.asyncio
async def test_execute_validate_with_specs(async_mocker):
    mocked_specs = async_mocker.MagicMock()
    mocked_specs.exists.return_value = False

    c = AsyncConnectClient('API_KEY')
    c.specs = mocked_specs
    c._use_specs = True
    with pytest.raises(ClientError) as cv:
        await c.execute('GET', 'resources')

    assert str(cv.value) == 'The path `resources` does not exist.'


@pytest.mark.asyncio
async def test_execute_non_json_response(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='https://localhost/resources',
        status_code=200,
        text='This is a non json response.',
    )
    c = AsyncConnectClient(
        'API_KEY',
        endpoint='https://localhost',
    )
    result = await c.execute('get', 'resources')
    assert result == b'This is a non json response.'


@pytest.mark.asyncio
async def test_execute_retries(httpx_mock):
    expected = [{'id': i} for i in range(10)]
    httpx_mock.add_response(
        method='GET',
        url='https://localhost/resources',
        status_code=502,
    )

    httpx_mock.add_response(
        method='GET',
        url='https://localhost/resources',
        status_code=502,
    )

    httpx_mock.add_response(
        method='GET',
        url='https://localhost/resources',
        status_code=200,
        json=expected,
    )

    c = AsyncConnectClient(
        'API_KEY',
        endpoint='https://localhost',
        max_retries=2,
    )

    results = await c.execute('get', 'resources')

    assert httpx_mock.get_requests()[0].method == 'GET'
    headers = httpx_mock.get_requests()[0].headers

    assert 'Authorization' in headers and headers['Authorization'] == 'API_KEY'
    assert 'User-Agent' in headers and headers['User-Agent'].startswith('connect-fluent')

    assert results == expected


@pytest.mark.asyncio
async def test_execute_max_retries_exceeded(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='https://localhost/resources',
        status_code=502,
    )
    httpx_mock.add_response(
        method='GET',
        url='https://localhost/resources',
        status_code=502,
    )
    httpx_mock.add_response(
        method='GET',
        url='https://localhost/resources',
        status_code=502,
    )

    c = AsyncConnectClient(
        'API_KEY',
        endpoint='https://localhost',
        max_retries=2,
    )

    with pytest.raises(ClientError):
        await c.execute('get', 'resources')


@pytest.mark.asyncio
async def test_execute_default_headers(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='https://localhost/resources',
        json=[],
    )

    c = AsyncConnectClient(
        'API_KEY',
        endpoint='https://localhost',
        default_headers={'X-Custom-Header': 'custom-header-value'},
    )

    await c.execute('get', 'resources')

    headers = httpx_mock.get_requests()[0].headers

    assert 'Authorization' in headers and headers['Authorization'] == 'API_KEY'
    assert 'User-Agent' in headers and headers['User-Agent'].startswith('connect-fluent')
    assert 'X-Custom-Header' in headers and headers['X-Custom-Header'] == 'custom-header-value'


@pytest.mark.asyncio
async def test_execute_with_kwargs(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='https://localhost/resources',
        json=[],
        status_code=201,
    )

    c = AsyncConnectClient('API_KEY', endpoint='https://localhost')
    kwargs = {
        'headers': {
            'X-Custom-Header': 'value',
        },
    }

    await c.execute('post', 'resources', **kwargs)

    assert httpx_mock.get_requests()[0].method == 'POST'

    headers = httpx_mock.get_requests()[0].headers

    assert 'Authorization' in headers and headers['Authorization'] == 'API_KEY'
    assert 'User-Agent' in headers and headers['User-Agent'].startswith('connect-fluent')
    assert 'X-Custom-Header' in headers and headers['X-Custom-Header'] == 'value'


@pytest.mark.asyncio
async def test_execute_connect_error(httpx_mock):
    connect_error = {
        'error_code': 'code',
        'errors': ['first', 'second'],
    }

    httpx_mock.add_response(
        method='POST',
        url='https://localhost/resources',
        json=connect_error,
        status_code=400,
    )

    c = AsyncConnectClient('API_KEY', endpoint='https://localhost')

    with pytest.raises(ClientError) as cv:
        await c.execute('post', 'resources')

    assert cv.value.status_code == 400
    assert cv.value.error_code == 'code'
    assert cv.value.errors == ['first', 'second']


@pytest.mark.asyncio
async def test_execute_unexpected_connect_error(httpx_mock):
    connect_error = {
        'unrecognized': 'code',
        'attributes': ['first', 'second'],
    }

    httpx_mock.add_response(
        method='POST',
        url='https://localhost/resources',
        json=connect_error,
        status_code=400,
    )

    c = AsyncConnectClient('API_KEY', endpoint='https://localhost')

    with pytest.raises(ClientError) as cv:
        await c.execute('post', 'resources')

    assert str(cv.value) == '400 Bad Request'


@pytest.mark.asyncio
async def test_execute_uparseable_connect_error(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='https://localhost/resources',
        text='error text',
        status_code=400,
    )

    c = AsyncConnectClient('API_KEY', endpoint='https://localhost')

    with pytest.raises(ClientError):
        await c.execute('post', 'resources')


@pytest.mark.asyncio
@pytest.mark.parametrize('encoding', ('utf-8', 'iso-8859-1'))
async def test_execute_error_with_reason(httpx_mock, encoding):
    httpx_mock.add_response(
        method='POST',
        url='https://localhost/resources',
        status_code=500,
        content='Internal Server Error'.encode(encoding),
    )

    c = AsyncConnectClient('API_KEY', endpoint='https://localhost')

    with pytest.raises(ClientError):
        await c.execute('post', 'resources')


@pytest.mark.asyncio
async def test_execute_delete(httpx_mock):
    httpx_mock.add_response(
        method='DELETE',
        url='https://localhost/resources',
        text='error text',
        status_code=204,
    )

    c = AsyncConnectClient('API_KEY', endpoint='https://localhost')

    results = await c.execute('delete', 'resources')

    assert results is None


def test_collection():
    c = AsyncConnectClient('API_KEY')
    assert isinstance(c.collection('resources'), AsyncCollection)


def test_ns():
    c = AsyncConnectClient('API_KEY')
    assert isinstance(c.ns('namespace'), AsyncNS)


@pytest.mark.asyncio
async def test_execute_with_qs_and_params(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='https://localhost/resources?eq(a,b)&limit=100&offset=0',
        json=[],
        status_code=201,
    )

    c = AsyncConnectClient('API_KEY', endpoint='https://localhost')
    kwargs = {
        'params': {
            'limit': 100,
            'offset': 0,
        },
    }

    await c.execute('get', 'resources?eq(a,b)', **kwargs)


@pytest.mark.asyncio
async def test_execute_with_params_only(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='https://localhost/resources?limit=100&offset=0',
        json=[],
        status_code=201,
    )

    c = AsyncConnectClient('API_KEY', endpoint='https://localhost')
    kwargs = {
        'params': {
            'limit': 100,
            'offset': 0,
        },
    }

    await c.execute('get', 'resources', **kwargs)


@pytest.mark.asyncio
async def test_async_client_manage_response():
    c = AsyncConnectClient('API_KEY')
    assert c.response is None
    c.response = 'Some response'
    assert c._response.get() == 'Some response'


@pytest.mark.asyncio
async def test_parallel_tasks(httpx_mock):
    for idx in range(100):
        httpx_mock.add_response(
            method='GET',
            url=f'https://localhost/resources/{idx}',
            json={'idx': idx},
            status_code=200,
        )

    c = AsyncConnectClient('API_KEY', endpoint='https://localhost')

    async def fetcher(client, idx):
        obj = await client.resources[str(idx)].get()
        assert obj == {'idx': idx}

    asyncio.gather(*[asyncio.create_task(fetcher(c, idx)) for idx in range(100)])


@pytest.mark.asyncio
async def test_concurrency(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='https://localhost/resources?limit=1&offset=0',
        json=[{'id': 1}],
        status_code=200,
    )

    httpx_mock.add_response(
        method='GET',
        url='https://localhost/resources?limit=1&offset=0',
        json=[{'id': 2}],
        status_code=200,
    )

    async def io_func(client):
        resp = await client.resources.all().first()
        return resp, client.response, client.session

    c = AsyncConnectClient('API_KEY', endpoint='https://localhost')

    res1, resp1, ses1 = await asyncio.create_task(io_func(c))
    res2, resp2, ses2 = await asyncio.create_task(io_func(c))

    assert res1 != res2
    assert resp1.json() != resp2.json()
    assert ses1 != ses2
    assert ses1._transport == ses2._transport
    assert c.response is None
