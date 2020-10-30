import pytest

from cnct.client.exceptions import APIError, HttpError, NotFoundError
from cnct.client.fluent import ConnectClient
from cnct.client.models import Collection, NS
from cnct.help import DefaultFormatter


def test_default_headers():
    c = ConnectClient(
        'Api Key',
        specs_location=None,
        default_headers={'X-Custom-Header': 'value'},
    )

    assert c.default_headers == {'X-Custom-Header': 'value'}


def test_default_headers_invalid():
    with pytest.raises(ValueError):
        ConnectClient(
            'Api Key',
            specs_location=None,
            default_headers={'Authorization': 'value'},
        )


def test_getattr(mocker):
    mocker.patch(
        'cnct.client.fluent.parse',
        return_value=None,
    )

    c = ConnectClient('Api Key')

    with pytest.raises(AttributeError) as cv:
        c.resources

    assert str(cv.value) == (
        'No specs available. Use `ns` '
        'or `collection` methods instead.'
    )


def test_getattr_with_specs_dash(mocker, apiinfo_factory, nsinfo_factory, colinfo_factory):
    specs = apiinfo_factory(
        collections=[colinfo_factory(name='my-resources')],
        namespaces=[nsinfo_factory(name='name-space')],
    )
    mocker.patch(
        'cnct.client.fluent.parse',
        return_value=specs,
    )

    c = ConnectClient('Api Key')

    assert isinstance(c.my_resources, Collection)
    assert isinstance(c.name_space, NS)

    specs = apiinfo_factory(
        collections=[colinfo_factory('resources')],
        namespaces=[nsinfo_factory('namespace')],
    )
    mocker.patch(
        'cnct.client.fluent.parse',
        return_value=specs,
    )

    c = ConnectClient('Api Key')

    assert isinstance(c.resources, Collection)
    assert isinstance(c.namespace, NS)


def test_getattr_with_specs_unresolved(mocker, apiinfo_factory, nsinfo_factory, colinfo_factory):
    specs = apiinfo_factory(
        collections=[colinfo_factory(name='resources')],
        namespaces=[nsinfo_factory(name='namespace')],
    )
    mocker.patch(
        'cnct.client.fluent.parse',
        return_value=specs,
    )

    c = ConnectClient('Api Key')

    with pytest.raises(AttributeError) as cv:
        c.others

    assert str(cv.value) == 'Unable to resolve others.'


def test_ns(mocker):
    mocker.patch(
        'cnct.client.fluent.parse',
        return_value=None,
    )

    c = ConnectClient('Api Key')

    assert isinstance(c.ns('namespace'), NS)


def test_ns_invalid_type():
    c = ConnectClient('Api Key', specs_location=None)
    with pytest.raises(TypeError):
        c.ns(c)


def test_ns_invalid_value():
    c = ConnectClient('Api Key', specs_location=None)
    with pytest.raises(ValueError):
        c.ns('')


def test_ns_unresolved(mocker, apiinfo_factory, nsinfo_factory):
    mocker.patch(
        'cnct.client.fluent.parse',
        return_value=apiinfo_factory(namespaces=[nsinfo_factory(name='namespace')]),
    )

    c = ConnectClient('Api Key')

    with pytest.raises(NotFoundError) as cv:
        c.ns('invalid')

    assert str(cv.value) == 'The namespace invalid does not exist.'


def test_collection(mocker):
    mocker.patch(
        'cnct.client.fluent.parse',
        return_value=None,
    )

    c = ConnectClient('Api Key')

    assert isinstance(c.collection('resources'), Collection)


def test_collection_invalid_type():
    c = ConnectClient('Api Key', specs_location=None)
    with pytest.raises(TypeError):
        c.collection(c)


def test_collection_invalid_value():
    c = ConnectClient('Api Key', specs_location=None)
    with pytest.raises(ValueError):
        c.collection('')


def test_collection_unresolved(mocker, apiinfo_factory, colinfo_factory):
    mocker.patch(
        'cnct.client.fluent.parse',
        return_value=apiinfo_factory(collections=[colinfo_factory('resources')]),
    )

    c = ConnectClient('Api Key')

    with pytest.raises(NotFoundError) as cv:
        c.collection('invalid')

    assert str(cv.value) == 'The collection invalid does not exist.'


def test_dir_with_specs(mocker, apiinfo_factory, nsinfo_factory, colinfo_factory):
    mocker.patch(
        'cnct.client.fluent.parse',
        return_value=apiinfo_factory(
            collections=[
                colinfo_factory(name='resources'),
                colinfo_factory(name='res-with-dash')
            ],
            namespaces=[
                nsinfo_factory(name='namespace'),
                nsinfo_factory(name='ns-with-dash'),
            ],
        ),
    )

    c = ConnectClient('Api Key')

    dir_ = dir(c)
    assert 'resources' in dir_
    assert 'namespace' in dir_
    assert 'res_with_dash' in dir_
    assert 'ns_with_dash' in dir_


def test_dir_without_specs(mocker):
    mocker.patch(
        'cnct.client.fluent.parse',
        return_value=None,
    )

    c = ConnectClient('Api Key')

    dir_ = dir(c)

    assert 'collection' in dir_
    assert 'ns' in dir_
    assert 'resource' not in dir_


def test_get(mocker):
    mocked = mocker.patch.object(ConnectClient, 'execute')
    url = 'https://localhost'
    kwargs = {
        'arg1': 'val1',
    }

    c = ConnectClient('API_KEY', specs_location=None)

    c.get(url, **kwargs)

    assert mocked.called_once_with('get', url, 200, **kwargs)


def test_create(mocker):
    mocked = mocker.patch.object(ConnectClient, 'execute')
    url = 'https://localhost'
    payload = {
        'k1': 'v1',
    }
    kwargs = {
        'arg1': 'val1',
    }

    c = ConnectClient('API_KEY', specs_location=None)

    c.create(url, payload=payload, **kwargs)

    mocked.assert_called_once_with('post', url, 201, **{
        'arg1': 'val1',
        'json': {
            'k1': 'v1',
        },
    })


def test_update(mocker):
    mocked = mocker.patch.object(ConnectClient, 'execute')
    url = 'https://localhost'
    payload = {
        'k1': 'v1',
    }
    kwargs = {
        'arg1': 'val1',
    }

    c = ConnectClient('API_KEY', specs_location=None)

    c.update(url, payload=payload, **kwargs)

    mocked.assert_called_once_with('put', url, 200, **{
        'arg1': 'val1',
        'json': {
            'k1': 'v1',
        },
    })


def test_delete(mocker):
    mocked = mocker.patch.object(ConnectClient, 'execute')
    url = 'https://localhost'

    kwargs = {
        'arg1': 'val1',
    }

    c = ConnectClient('API_KEY', specs_location=None)

    c.delete(url, **kwargs)

    mocked.assert_called_once_with('delete', url, 204, **kwargs)


def test_execute(requests_mock):
    expected = [{'id': i} for i in range(10)]
    mock = requests_mock.request(
        'get',
        'https://localhost/resources',
        json=expected,
    )

    c = ConnectClient('API_KEY', specs_location=None)

    results = c.execute('get', 'https://localhost/resources', 200)

    assert mock.last_request.method == 'GET'
    headers = mock.last_request.headers

    assert 'Authorization' in headers and headers['Authorization'] == 'API_KEY'
    assert 'User-Agent' in headers and headers['User-Agent'].startswith('connect-fluent')

    assert results == expected


def test_execute_default_headers(requests_mock):
    mock = requests_mock.request(
        'get',
        'https://localhost/resources',
        json=[],
    )

    c = ConnectClient(
        'API_KEY',
        specs_location=None,
        default_headers={'X-Custom-Header': 'custom-header-value'},
    )

    c.execute('get', 'https://localhost/resources', 200)

    headers = mock.last_request.headers

    assert 'Authorization' in headers and headers['Authorization'] == 'API_KEY'
    assert 'User-Agent' in headers and headers['User-Agent'].startswith('connect-fluent')
    assert 'X-Custom-Header' in headers and headers['X-Custom-Header'] == 'custom-header-value'


def test_execute_with_kwargs(requests_mock):
    mock = requests_mock.request(
        'post',
        'https://localhost/resources',
        json=[],
        status_code=201,
    )

    c = ConnectClient('API_KEY', specs_location=None)
    kwargs = {
        'headers': {
            'X-Custom-Header': 'value',
        },
    }

    c.execute('post', 'https://localhost/resources', 201, **kwargs)

    assert mock.last_request.method == 'POST'

    headers = mock.last_request.headers

    assert 'Authorization' in headers and headers['Authorization'] == 'API_KEY'
    assert 'User-Agent' in headers and headers['User-Agent'].startswith('connect-fluent')
    assert 'X-Custom-Header' in headers and headers['X-Custom-Header'] == 'value'


def test_execute_connect_error(requests_mock):
    connect_error = {
        'error_code': 'code',
        'errors': ['first', 'second'],
    }

    requests_mock.request(
        'post',
        'https://localhost/resources',
        json=connect_error,
        status_code=400,
    )

    c = ConnectClient('API_KEY', specs_location=None)

    with pytest.raises(APIError) as cv:
        c.execute('post', 'https://localhost/resources', 201)

    assert cv.value.status_code == 400
    assert cv.value.error_code == 'code'
    assert cv.value.errors == ['first', 'second']


def test_execute_uparseable_connect_error(requests_mock):

    requests_mock.request(
        'post',
        'https://localhost/resources',
        text='error text',
        status_code=400,
    )

    c = ConnectClient('API_KEY', specs_location=None)

    with pytest.raises(HttpError):
        c.execute('post', 'https://localhost/resources', 201)


@pytest.mark.parametrize('encoding', ('utf-8', 'iso-8859-1'))
def test_execute_error_with_reason(requests_mock, encoding):

    requests_mock.request(
        'post',
        'https://localhost/resources',
        status_code=500,
        reason='Interñal Server Error'.encode(encoding),
    )

    c = ConnectClient('API_KEY', specs_location=None)

    with pytest.raises(HttpError):
        c.execute('post', 'https://localhost/resources', 201)


def test_execute_delete(requests_mock):

    requests_mock.request(
        'delete',
        'https://localhost/resources',
        text='error text',
        status_code=204,
    )

    c = ConnectClient('API_KEY', specs_location=None)

    results = c.execute('delete', 'https://localhost/resources', 204)

    assert results is None


def test_help(mocker, col_factory):
    print_help = mocker.patch.object(DefaultFormatter, 'print_help')
    c = ConnectClient('API_KEY', specs_location=None)
    c1 = c.help()

    assert print_help.called_once_with(None)
    assert c == c1
