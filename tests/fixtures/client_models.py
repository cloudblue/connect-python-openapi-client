import pytest

from cnct.client.models import Action, NS, Collection, Item, Search


@pytest.fixture
def ns_factory(mocker):
    client = mocker.MagicMock()
    client.endpoint = 'https://example.com/api/v1'

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
    client.endpoint = 'https://example.com/api/v1'

    def _col_factory(
        client=client,
        path='namespace',
        specs=None,
    ):
        col = Collection(client, path, specs)
        return col
    return _col_factory


@pytest.fixture
def item_factory(mocker):
    client = mocker.MagicMock()
    client.endpoint = 'https://example.com/api/v1'

    def _item_factory(
        client=client,
        path='{item_id}',
        specs=None,
    ):
        item = Item(client, path, specs)
        return item
    return _item_factory


@pytest.fixture
def action_factory(mocker):
    client = mocker.MagicMock()
    client.endpoint = 'https://example.com/api/v1'

    def _action_factory(
        client=client,
        path='{item_id}',
        specs=None,
    ):
        action = Action(client, path, specs)
        return action
    return _action_factory


@pytest.fixture
def search_factory(mocker):
    client = mocker.MagicMock()
    client.endpoint = 'https://example.com/api/v1'

    def _search_factory(
        client=client,
        path='resources',
        query=None,
        specs=None,
    ):
        search = Search(client, path, query, specs)
        return search
    return _search_factory
