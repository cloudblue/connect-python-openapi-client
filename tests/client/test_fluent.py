import pytest

from requests import HTTPError

from cnct.client.exceptions import ConnectError, NotFoundError
from cnct.client.fluent import ConnectFluent
from cnct.client.models import Collection, NS


def test_getattr(mocker):
    mocker.patch(
        'cnct.client.fluent.parse',
        return_value=None,
    )

    c = ConnectFluent('Api Key')

    with pytest.raises(AttributeError) as cv:
        c.resources

    assert str(cv.value) == (
        'No specs available. Use `ns` '
        'or `collection` methods instead.'
    )


def test_getattr_with_specs(mocker, apiinfo_factory):
    specs = apiinfo_factory(
        collections=['resources'],
        namespaces=['namespace'],
    )
    mocker.patch(
        'cnct.client.fluent.parse',
        return_value=specs,
    )

    c = ConnectFluent('Api Key')

    assert isinstance(c.resources, Collection)
    assert isinstance(c.namespace, NS)


def test_getattr_with_specs_unresolved(mocker, apiinfo_factory):
    specs = apiinfo_factory(
        collections=['resources'],
        namespaces=['namespace'],
    )
    mocker.patch(
        'cnct.client.fluent.parse',
        return_value=specs,
    )

    c = ConnectFluent('Api Key')

    with pytest.raises(NotFoundError) as cv:
        c.others

    assert str(cv.value) == 'Unable to resolve others.'


def test_ns(mocker):
    mocker.patch(
        'cnct.client.fluent.parse',
        return_value=None,
    )

    c = ConnectFluent('Api Key')

    assert isinstance(c.ns('namespace'), NS)


def test_ns_unresolved(mocker, apiinfo_factory):
    mocker.patch(
        'cnct.client.fluent.parse',
        return_value=apiinfo_factory(namespaces=['namespace']),
    )

    c = ConnectFluent('Api Key')

    with pytest.raises(NotFoundError) as cv:
        c.ns('invalid')

    assert str(cv.value) == 'The namespace invalid does not exist.'


def test_collection(mocker):
    mocker.patch(
        'cnct.client.fluent.parse',
        return_value=None,
    )

    c = ConnectFluent('Api Key')

    assert isinstance(c.collection('resources'), Collection)


def test_collection_unresolved(mocker, apiinfo_factory):
    mocker.patch(
        'cnct.client.fluent.parse',
        return_value=apiinfo_factory(collections=['resources']),
    )

    c = ConnectFluent('Api Key')

    with pytest.raises(NotFoundError) as cv:
        c.collection('invalid')

    assert str(cv.value) == 'The collection invalid does not exist.'


def test_dir_with_specs(mocker, apiinfo_factory):
    mocker.patch(
        'cnct.client.fluent.parse',
        return_value=apiinfo_factory(
            collections=['resources'],
            namespaces=['namespace']
        ),
    )

    c = ConnectFluent('Api Key')

    dir_ = dir(c)
    assert 'resources' in dir_
    assert 'namespace' in dir_


def test_dir_without_specs(mocker):
    mocker.patch(
        'cnct.client.fluent.parse',
        return_value=None,
    )

    c = ConnectFluent('Api Key')

    dir_ = dir(c)

    assert 'collection' in dir_
    assert 'ns' in dir_
    assert 'resource' not in dir_


def test_get(mocker):
    mocked = mocker.patch.object(ConnectFluent, 'execute')
    url = 'https://localhost'
    kwargs = {
        'arg1': 'val1',
    }

    c = ConnectFluent('API_KEY', specs_url=None)

    c.get(url, **kwargs)

    assert mocked.called_once_with('get', url, 200, **kwargs)


def test_create(mocker):
    mocked = mocker.patch.object(ConnectFluent, 'execute')
    url = 'https://localhost'
    payload = {
        'k1': 'v1',
    }
    kwargs = {
        'arg1': 'val1',
    }

    c = ConnectFluent('API_KEY', specs_url=None)

    c.create(url, payload=payload, **kwargs)

    mocked.assert_called_once_with('post', url, 201, **{
        'arg1': 'val1',
        'json': {
            'k1': 'v1',
        },
    })


def test_update(mocker):
    mocked = mocker.patch.object(ConnectFluent, 'execute')
    url = 'https://localhost'
    payload = {
        'k1': 'v1',
    }
    kwargs = {
        'arg1': 'val1',
    }

    c = ConnectFluent('API_KEY', specs_url=None)

    c.update(url, payload=payload, **kwargs)

    mocked.assert_called_once_with('put', url, 200, **{
        'arg1': 'val1',
        'json': {
            'k1': 'v1',
        },
    })


def test_delete(mocker):
    mocked = mocker.patch.object(ConnectFluent, 'execute')
    url = 'https://localhost'

    kwargs = {
        'arg1': 'val1',
    }

    c = ConnectFluent('API_KEY', specs_url=None)

    c.delete(url, **kwargs)

    mocked.assert_called_once_with('delete', url, 204, **kwargs)


def test_execute(requests_mock):
    expected = [{'id': i} for i in range(10)]
    mock = requests_mock.request(
        'get',
        'https://localhost/resources',
        json=expected,
    )

    c = ConnectFluent('API_KEY', specs_url=None)

    results = c.execute('get', 'https://localhost/resources', 200)

    assert mock.last_request.method == 'GET'
    headers = mock.last_request.headers

    assert 'Authorization' in headers and headers['Authorization'] == 'API_KEY'
    assert 'User-Agent' in headers and headers['User-Agent'].startswith('connect-fluent')

    assert results == expected


def test_execute_with_kwargs(requests_mock):
    mock = requests_mock.request(
        'post',
        'https://localhost/resources',
        json=[],
        status_code=201,
    )

    c = ConnectFluent('API_KEY', specs_url=None)
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

    c = ConnectFluent('API_KEY', specs_url=None)

    with pytest.raises(ConnectError) as cv:
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

    c = ConnectFluent('API_KEY', specs_url=None)

    with pytest.raises(HTTPError):
        c.execute('post', 'https://localhost/resources', 201)


def test_execute_delete(requests_mock):

    requests_mock.request(
        'delete',
        'https://localhost/resources',
        text='error text',
        status_code=204,
    )

    c = ConnectFluent('API_KEY', specs_url=None)

    results = c.execute('delete', 'https://localhost/resources', 204)

    assert results is None
