import pytest

from connect.client.models import (
    NS,
    Action,
    AsyncAction,
    AsyncCollection,
    AsyncNS,
    AsyncResource,
    AsyncResourceSet,
    Collection,
    Resource,
    ResourceSet,
)


@pytest.fixture
def async_client_mock(async_mocker):
    def _async_client_mock(methods=None):
        methods = methods or ['execute']
        client = async_mocker.MagicMock()
        client.default_limit = 100
        for method in methods:
            setattr(client, method, async_mocker.AsyncMock())
        return client
    return _async_client_mock


@pytest.fixture
def ns_factory(mocker):
    client = mocker.MagicMock()
    client._endpoint = 'https://example.com/api/v1'

    def _ns_factory(
        client=client,
        path='namespace',
    ):
        ns = NS(client, path)
        return ns
    return _ns_factory


@pytest.fixture
def async_ns_factory(async_client_mock):
    client = async_client_mock()
    client._endpoint = 'https://example.com/api/v1'

    def _ns_factory(
        client=client,
        path='namespace',
    ):
        ns = AsyncNS(client, path)
        return ns
    return _ns_factory


@pytest.fixture
def col_factory(mocker):
    client = mocker.MagicMock()
    client._endpoint = 'https://example.com/api/v1'

    def _col_factory(
        client=client,
        path='namespace',
    ):
        col = Collection(client, path)
        return col
    return _col_factory


@pytest.fixture
def async_col_factory(async_client_mock):
    client = async_client_mock()
    client._endpoint = 'https://example.com/api/v1'

    def _col_factory(
        client=client,
        path='namespace',
    ):
        col = AsyncCollection(client, path)
        return col
    return _col_factory


@pytest.fixture
def res_factory(mocker):
    client = mocker.MagicMock()
    client._endpoint = 'https://example.com/api/v1'

    def _res_factory(
        client=client,
        path='{item_id}',
    ):
        resource = Resource(client, path)
        return resource
    return _res_factory


@pytest.fixture
def async_res_factory(async_client_mock):
    client = async_client_mock()
    client._endpoint = 'https://example.com/api/v1'

    def _res_factory(
        client=client,
        path='{item_id}',
    ):
        resource = AsyncResource(client, path)
        return resource
    return _res_factory


@pytest.fixture
def action_factory(mocker):
    client = mocker.MagicMock()
    client._endpoint = 'https://example.com/api/v1'

    def _action_factory(
        client=client,
        path='{item_id}',
    ):
        action = Action(client, path)
        return action
    return _action_factory


@pytest.fixture
def async_action_factory(async_client_mock):
    client = async_client_mock()
    client._endpoint = 'https://example.com/api/v1'

    def _action_factory(
        client=client,
        path='{item_id}',
    ):
        action = AsyncAction(client, path)
        return action
    return _action_factory


@pytest.fixture
def rs_factory(mocker):
    client = mocker.MagicMock()
    client._endpoint = 'https://example.com/api/v1'
    client.default_limit = None

    def _rs_factory(
        client=client,
        path='resources',
        query=None,
    ):
        rs = ResourceSet(client, path, query)
        return rs
    return _rs_factory


@pytest.fixture
def async_rs_factory(async_client_mock):
    client = async_client_mock()
    client._endpoint = 'https://example.com/api/v1'
    client.default_limit = None

    def _rs_factory(
        client=client,
        path='resources',
        query=None,
    ):
        rs = AsyncResourceSet(client, path, query)
        return rs
    return _rs_factory
