import pytest

from cnct.client.models import Action, NS, Collection, Resource, ResourceSet


@pytest.fixture
def ns_factory(mocker):
    client = mocker.MagicMock()
    client._endpoint = 'https://example.com/api/v1'

    def _ns_factory(
        client=client,
        path='namespace',
        specs=None,
    ):
        ns = NS(client, path, specs)
        return ns
    return _ns_factory


@pytest.fixture
def col_factory(mocker):
    client = mocker.MagicMock()
    client._endpoint = 'https://example.com/api/v1'

    def _col_factory(
        client=client,
        path='namespace',
        specs=None,
    ):
        col = Collection(client, path, specs)
        return col
    return _col_factory


@pytest.fixture
def res_factory(mocker):
    client = mocker.MagicMock()
    client._endpoint = 'https://example.com/api/v1'

    def _res_factory(
        client=client,
        path='{item_id}',
        specs=None,
    ):
        resource = Resource(client, path, specs)
        return resource
    return _res_factory


@pytest.fixture
def action_factory(mocker):
    client = mocker.MagicMock()
    client._endpoint = 'https://example.com/api/v1'

    def _action_factory(
        client=client,
        path='{item_id}',
        specs=None,
    ):
        action = Action(client, path, specs)
        return action
    return _action_factory


@pytest.fixture
def rs_factory(mocker):
    client = mocker.MagicMock()
    client._endpoint = 'https://example.com/api/v1'

    def _rs_factory(
        client=client,
        path='resources',
        query=None,
        specs=None,
    ):
        rs = ResourceSet(client, path, query, specs)
        return rs
    return _rs_factory
