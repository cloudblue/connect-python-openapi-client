import pytest

import responses

from cnct.client.exceptions import ClientError
from cnct.client.fluent import ConnectClient
from cnct.client.models import Collection, NS


def test_default_headers():
    c = ConnectClient(
        'Api Key',
        use_specs=False,
        default_headers={'X-Custom-Header': 'value'},
    )

    assert c.default_headers == {'X-Custom-Header': 'value'}


def test_default_headers_invalid():
    with pytest.raises(ValueError):
        ConnectClient(
            'Api Key',
            use_specs=False,
            default_headers={'Authorization': 'value'},
        )


# def test_getattr(mocker):
#     c = ConnectClient('Api Key', use_specs=False)

#     with pytest.raises(AttributeError) as cv:
#         c.resources

#     assert str(cv.value) == (
#         'No specs available. Use `ns` '
#         'or `collection` methods instead.'
#     )


# def test_getattr_with_specs_dash(mocker, apiinfo_factory, nsinfo_factory, colinfo_factory):
#     specs = apiinfo_factory(
#         collections=[colinfo_factory(name='my-resources')],
#         namespaces=[nsinfo_factory(name='name-space')],
#     )
#     mocker.patch(
#         'cnct.client.fluent.parse',
#         return_value=specs,
#     )

#     c = ConnectClient('Api Key')

#     assert isinstance(c.my_resources, Collection)
#     assert isinstance(c.name_space, NS)

#     specs = apiinfo_factory(
#         collections=[colinfo_factory('resources')],
#         namespaces=[nsinfo_factory('namespace')],
#     )
#     mocker.patch(
#         'cnct.client.fluent.parse',
#         return_value=specs,
#     )

#     c = ConnectClient('Api Key')

#     assert isinstance(c.resources, Collection)
#     assert isinstance(c.namespace, NS)


# def test_getattr_with_specs_unresolved(mocker, apiinfo_factory, nsinfo_factory, colinfo_factory):
#     specs = apiinfo_factory(
#         collections=[colinfo_factory(name='resources')],
#         namespaces=[nsinfo_factory(name='namespace')],
#     )
#     mocker.patch(
#         'cnct.client.fluent.parse',
#         return_value=specs,
#     )

#     c = ConnectClient('Api Key')

#     with pytest.raises(AttributeError) as cv:
#         c.others

#     assert str(cv.value) == 'Unable to resolve others.'


def test_ns(mocker):
    # mocker.patch(
    #     'cnct.client.fluent.parse',
    #     return_value=None,
    # )

    c = ConnectClient('Api Key', use_specs=False)

    assert isinstance(c.ns('namespace'), NS)


def test_ns_invalid_type():
    c = ConnectClient('Api Key', use_specs=False)
    with pytest.raises(TypeError):
        c.ns(c)


def test_ns_invalid_value():
    c = ConnectClient('Api Key', use_specs=False)
    with pytest.raises(ValueError):
        c.ns('')


def test_collection(mocker):
    c = ConnectClient('Api Key', use_specs=False)

    assert isinstance(c.collection('resources'), Collection)


def test_collection_invalid_type():
    c = ConnectClient('Api Key', use_specs=False)
    with pytest.raises(TypeError):
        c.collection(c)


def test_collection_invalid_value():
    c = ConnectClient('Api Key', use_specs=False)
    with pytest.raises(ValueError):
        c.collection('')


def test_get(mocker):
    mocked = mocker.patch.object(ConnectClient, 'execute')
    url = 'https://localhost'
    kwargs = {
        'arg1': 'val1',
    }

    c = ConnectClient('API_KEY', use_specs=False)

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

    c = ConnectClient('API_KEY', use_specs=False)

    c.create(url, payload=payload, **kwargs)

    mocked.assert_called_once_with('post', url, **{
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

    c = ConnectClient('API_KEY', use_specs=False)

    c.update(url, payload=payload, **kwargs)

    mocked.assert_called_once_with('put', url, **{
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

    c = ConnectClient('API_KEY', use_specs=False)

    c.delete(url, **kwargs)

    mocked.assert_called_once_with('delete', url, **kwargs)


def test_execute(mocked_responses):
    expected = [{'id': i} for i in range(10)]
    mocked_responses.add(
        responses.GET,
        'https://localhost/resources',
        json=expected,
    )

    c = ConnectClient('API_KEY', endpoint='https://localhost', use_specs=False)

    results = c.execute('get', 'resources')

    assert mocked_responses.calls[0].request.method == 'GET'
    headers = mocked_responses.calls[0].request.headers

    assert 'Authorization' in headers and headers['Authorization'] == 'API_KEY'
    assert 'User-Agent' in headers and headers['User-Agent'].startswith('connect-fluent')

    assert results == expected


def test_execute_default_headers(mocked_responses):
    mocked_responses.add(
        responses.GET,
        'https://localhost/resources',
        json=[],
    )

    c = ConnectClient(
        'API_KEY',
        endpoint='https://localhost',
        use_specs=False,
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

    c = ConnectClient('API_KEY', endpoint='https://localhost', use_specs=False)
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

    c = ConnectClient('API_KEY', endpoint='https://localhost', use_specs=False)

    with pytest.raises(ClientError) as cv:
        c.execute('post', 'resources')

    assert cv.value.status_code == 400
    assert cv.value.error_code == 'code'
    assert cv.value.errors == ['first', 'second']


def test_execute_uparseable_connect_error(mocked_responses):

    mocked_responses.add(
        responses.POST,
        'https://localhost/resources',
        body='error text',
        status=400,
    )

    c = ConnectClient('API_KEY', endpoint='https://localhost', use_specs=False)

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

    c = ConnectClient('API_KEY', endpoint='https://localhost', use_specs=False)

    with pytest.raises(ClientError):
        c.execute('post', 'resources')


def test_execute_delete(mocked_responses):

    mocked_responses.add(
        responses.DELETE,
        'https://localhost/resources',
        body='error text',
        status=204,
    )

    c = ConnectClient('API_KEY', endpoint='https://localhost', use_specs=False)

    results = c.execute('delete', 'resources')

    assert results is None


# def test_help(mocker, col_factory):
#     print_help = mocker.patch.object(DefaultFormatter, 'print_help')
#     c = ConnectClient('API_KEY', use_specs=False)
#     c1 = c.help()

#     assert print_help.called_once_with(None)
#     assert c == c1
