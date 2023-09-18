import io

import pytest
import responses
from requests import RequestException, Timeout

from connect.client.exceptions import ClientError
from connect.client.fluent import ConnectClient
from connect.client.logger import RequestLogger
from connect.client.models import NS, Collection


def test_default_headers():
    c = ConnectClient(
        'Api Key',
        default_headers={'X-Custom-Header': 'value'},
    )

    assert c.default_headers == {'X-Custom-Header': 'value'}


def test_default_headers_invalid():
    with pytest.raises(ValueError):
        ConnectClient(
            'Api Key',
            default_headers={'Authorization': 'value'},
        )


def test_default_limit():
    c = ConnectClient(
        'Api Key',
        default_limit=10,
    )

    rs = c.products.all()

    assert rs._limit == 10


def test_ns(mocker):
    c = ConnectClient('Api Key')

    assert isinstance(c.ns('namespace'), NS)


def test_ns_invalid_type():
    c = ConnectClient('Api Key')
    with pytest.raises(TypeError):
        c.ns(c)


def test_ns_invalid_value():
    c = ConnectClient('Api Key')
    with pytest.raises(ValueError):
        c.ns('')


def test_collection(mocker):
    c = ConnectClient('Api Key')

    assert isinstance(c.collection('resources'), Collection)


def test_collection_invalid_type():
    c = ConnectClient('Api Key')
    with pytest.raises(TypeError):
        c.collection(c)


def test_collection_invalid_value():
    c = ConnectClient('Api Key')
    with pytest.raises(ValueError):
        c.collection('')


def test_get(mocker):
    mocked = mocker.patch.object(ConnectClient, 'execute')
    url = 'https://localhost'
    kwargs = {
        'arg1': 'val1',
    }

    c = ConnectClient('API_KEY')

    c.get(url, **kwargs)

    mocked.assert_called_once_with('get', url, **kwargs)


@pytest.mark.parametrize('attr', ('payload', 'json'))
def test_create(mocker, attr):
    mocked = mocker.patch.object(ConnectClient, 'execute')
    url = 'https://localhost'
    kwargs = {
        'arg1': 'val1',
    }
    kwargs[attr] = {'k1': 'v1'}

    c = ConnectClient('API_KEY')

    c.create(url, **kwargs)

    mocked.assert_called_once_with(
        'post',
        url,
        **{
            'arg1': 'val1',
            'json': {
                'k1': 'v1',
            },
        },
    )


@pytest.mark.parametrize('attr', ('payload', 'json'))
def test_update(mocker, attr):
    mocked = mocker.patch.object(ConnectClient, 'execute')
    url = 'https://localhost'
    kwargs = {
        'arg1': 'val1',
    }
    kwargs[attr] = {'k1': 'v1'}

    c = ConnectClient('API_KEY')

    c.update(url, **kwargs)

    mocked.assert_called_once_with(
        'put',
        url,
        **{
            'arg1': 'val1',
            'json': {
                'k1': 'v1',
            },
        },
    )


def test_delete_no_args(mocker):
    mocked = mocker.patch.object(ConnectClient, 'execute')
    url = 'https://localhost'

    c = ConnectClient('API_KEY')

    c.delete(url)

    mocked.assert_called_once_with('delete', url)


@pytest.mark.parametrize('attr', ('payload', 'json'))
def test_delete(mocker, attr):
    mocked = mocker.patch.object(ConnectClient, 'execute')
    url = 'https://localhost'

    kwargs = {
        'arg1': 'val1',
    }
    kwargs[attr] = {'k1': 'v1'}

    c = ConnectClient('API_KEY')

    c.delete(url, **kwargs)

    mocked.assert_called_once_with(
        'delete',
        url,
        **{
            'arg1': 'val1',
            'json': {
                'k1': 'v1',
            },
        },
    )


def test_execute(mocked_responses):
    expected = [{'id': i} for i in range(10)]
    mocked_responses.add(
        responses.GET,
        'https://localhost/resources',
        json=expected,
    )

    ios = io.StringIO()
    c = ConnectClient('API_KEY', endpoint='https://localhost', logger=RequestLogger(file=ios))

    results = c.execute('get', 'resources')

    assert mocked_responses.calls[0].request.method == 'GET'
    headers = mocked_responses.calls[0].request.headers

    assert 'Authorization' in headers and headers['Authorization'] == 'API_KEY'
    assert 'User-Agent' in headers and headers['User-Agent'].startswith('connect-fluent')

    assert results == expected


def test_execute_validate_with_specs(mocker):
    mocked_specs = mocker.MagicMock()
    mocked_specs.exists.return_value = False

    c = ConnectClient('API_KEY', use_specs=False)
    c.specs = mocked_specs
    c._use_specs = True
    with pytest.raises(ClientError) as cv:
        c.execute('GET', 'resources')

    assert str(cv.value) == 'The path `resources` does not exist.'


def test_execute_non_json_response(mocked_responses):
    mocked_responses.add(
        responses.GET,
        'https://localhost/resources',
        status=200,
        body='This is a non json response.',
    )
    c = ConnectClient(
        'API_KEY',
        endpoint='https://localhost',
    )
    result = c.execute('get', 'resources')
    assert result == b'This is a non json response.'


@pytest.mark.parametrize(
    'mock_config',
    (
        {'status': 500},
        {'status': 501},
        {'status': 502},
        {'body': Timeout()},
    ),
)
def test_execute_retries(mocked_responses, mock_config):
    expected = [{'id': i} for i in range(10)]
    mocked_responses.add(
        responses.GET,
        'https://localhost/resources',
        **mock_config,
    )

    mocked_responses.add(
        responses.GET,
        'https://localhost/resources',
        **mock_config,
    )

    mocked_responses.add(
        responses.GET,
        'https://localhost/resources',
        status=200,
        json=expected,
    )

    c = ConnectClient(
        'API_KEY',
        endpoint='https://localhost',
        max_retries=2,
    )

    results = c.execute('get', 'resources')

    assert mocked_responses.calls[0].request.method == 'GET'
    headers = mocked_responses.calls[0].request.headers

    assert 'Authorization' in headers and headers['Authorization'] == 'API_KEY'
    assert 'User-Agent' in headers and headers['User-Agent'].startswith('connect-fluent')

    assert results == expected


@pytest.mark.parametrize(
    'mock_config',
    (
        {'status': 500},
        {'status': 501},
        {'status': 502},
        {'body': Timeout()},
    ),
)
def test_execute_max_retries_exceeded(mocked_responses, mock_config):
    mocked_responses.add(
        responses.GET,
        'https://localhost/resources',
        **mock_config,
    )

    mocked_responses.add(
        responses.GET,
        'https://localhost/resources',
        **mock_config,
    )

    mocked_responses.add(
        responses.GET,
        'https://localhost/resources',
        **mock_config,
    )

    c = ConnectClient(
        'API_KEY',
        endpoint='https://localhost',
        max_retries=2,
    )

    with pytest.raises(ClientError):
        c.execute('get', 'resources')


def test_execute_default_headers(mocked_responses):
    mocked_responses.add(
        responses.GET,
        'https://localhost/resources',
        json=[],
    )

    c = ConnectClient(
        'API_KEY',
        endpoint='https://localhost',
        default_headers={'X-Custom-Header': 'custom-header-value'},
    )

    c.execute('get', 'resources')

    headers = mocked_responses.calls[0].request.headers

    assert 'Authorization' in headers and headers['Authorization'] == 'API_KEY'
    assert 'User-Agent' in headers and headers['User-Agent'].startswith('connect-fluent')
    assert 'X-Custom-Header' in headers and headers['X-Custom-Header'] == 'custom-header-value'


def test_execute_with_kwargs(mocked_responses):
    mocked_responses.add(
        responses.POST,
        'https://localhost/resources',
        json=[],
        status=201,
    )

    c = ConnectClient('API_KEY', endpoint='https://localhost')
    kwargs = {
        'headers': {
            'X-Custom-Header': 'value',
        },
    }

    c.execute('post', 'resources', **kwargs)

    assert mocked_responses.calls[0].request.method == 'POST'

    headers = mocked_responses.calls[0].request.headers

    assert 'Authorization' in headers and headers['Authorization'] == 'API_KEY'
    assert 'User-Agent' in headers and headers['User-Agent'].startswith('connect-fluent')
    assert 'X-Custom-Header' in headers and headers['X-Custom-Header'] == 'value'


def test_execute_with_overwritten_timeout(mocker):
    http_call = mocker.patch(
        'connect.client.mixins.SyncClientMixin._execute_http_call',
        side_effect=RequestException(),
    )

    c = ConnectClient('API_KEY', endpoint='https://localhost')
    kwargs = {
        'timeout': 500,
    }

    with pytest.raises(ClientError):
        c.execute('post', 'resources', **kwargs)

    http_call.assert_called_with(
        'post',
        'https://localhost/resources',
        {
            'timeout': 500,
            'headers': {
                'Authorization': 'API_KEY',
                'User-Agent': mocker.ANY,
            },
        },
    )


def test_execute_with_default_timeout(mocker):
    http_call = mocker.patch(
        'connect.client.mixins.SyncClientMixin._execute_http_call',
        side_effect=RequestException(),
    )

    c = ConnectClient('API_KEY', endpoint='https://localhost')

    with pytest.raises(ClientError):
        c.execute('post', 'resources')

    http_call.assert_called_with(
        'post',
        'https://localhost/resources',
        {
            'timeout': (15.0, 180.0),
            'headers': {
                'Authorization': 'API_KEY',
                'User-Agent': mocker.ANY,
            },
        },
    )


def test_execute_connect_error(mocked_responses):
    connect_error = {
        'error_code': 'code',
        'errors': ['first', 'second'],
    }

    mocked_responses.add(
        responses.POST,
        'https://localhost/resources',
        json=connect_error,
        status=400,
    )

    c = ConnectClient('API_KEY', endpoint='https://localhost')

    with pytest.raises(ClientError) as cv:
        c.execute('post', 'resources')

    assert cv.value.status_code == 400
    assert cv.value.error_code == 'code'
    assert cv.value.errors == ['first', 'second']


def test_execute_unexpected_connect_error(mocked_responses):
    connect_error = {
        'unrecognized': 'code',
        'attributes': ['first', 'second'],
    }

    mocked_responses.add(
        responses.POST,
        'https://localhost/resources',
        json=connect_error,
        status=400,
    )

    c = ConnectClient('API_KEY', endpoint='https://localhost')

    with pytest.raises(ClientError) as cv:
        c.execute('post', 'resources')

    assert str(cv.value) == '400 Bad Request'


def test_execute_uparseable_connect_error(mocked_responses):
    mocked_responses.add(
        responses.POST,
        'https://localhost/resources',
        body='error text',
        status=400,
    )

    c = ConnectClient('API_KEY', endpoint='https://localhost')

    with pytest.raises(ClientError):
        c.execute('post', 'resources')


@pytest.mark.parametrize('encoding', ('utf-8', 'iso-8859-1'))
def test_execute_error_with_reason(mocked_responses, encoding):
    mocked_responses.add(
        responses.POST,
        'https://localhost/resources',
        status=500,
        body='Interñal Server Error'.encode(encoding),
    )

    c = ConnectClient('API_KEY', endpoint='https://localhost')

    with pytest.raises(ClientError):
        c.execute('post', 'resources')


def test_execute_delete(mocked_responses):
    mocked_responses.add(
        responses.DELETE,
        'https://localhost/resources',
        body='error text',
        status=204,
    )

    c = ConnectClient('API_KEY', endpoint='https://localhost')

    results = c.execute('delete', 'resources')

    assert results is None


def test_create_client_with_defaults(mocker):
    mocked_specs = mocker.patch('connect.client.fluent.OpenAPISpecs')
    ConnectClient('API_KEY')
    assert mocked_specs.called is False


def test_get_attr_with_underscore(mocker):
    c = ConnectClient('API_KEY', endpoint='https://localhost')

    coll = c.my_collection
    assert coll.path == 'my-collection'


def test_call(mocker):
    c = ConnectClient('API_KEY', endpoint='https://localhost')

    ns = c('ns')
    assert isinstance(ns, NS)
    assert ns.path == 'ns'


def test_print_help(mocker):
    format_mock = mocker.MagicMock()
    c = ConnectClient('API_KEY', endpoint='https://localhost')
    c._help_formatter.format = format_mock

    c.print_help(None)
    format_mock.assert_called_once_with(None)


def test_help(mocker):
    format_mock = mocker.MagicMock()
    c = ConnectClient('API_KEY', endpoint='https://localhost')
    c._help_formatter.format = format_mock
    c.help()
    format_mock.assert_called_once_with(None)


def test_non_server_error(mocker):
    c = ConnectClient('API_KEY', endpoint='https://localhost')
    c._session.request = mocker.MagicMock(side_effect=RequestException('generic'))

    with pytest.raises(ClientError) as cv:
        c.execute('get', 'path')

    assert str(cv.value) == 'Unexpected error'


def test_sync_client_manage_response():
    c = ConnectClient('API_KEY')
    assert c.response is None
    c.response = 'Some response'
    assert c._response == 'Some response'
