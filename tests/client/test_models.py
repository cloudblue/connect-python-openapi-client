import pytest

from cnct.client.exceptions import NotFoundError
from cnct.client.models import Collection, Item, Search


def test_ns_collection_invalid_type(ns_factory):
    ns = ns_factory()
    with pytest.raises(TypeError) as cv:
        ns.collection(None)

    assert str(cv.value) == '`name` must be a string.'

    with pytest.raises(TypeError) as cv:
        ns.collection(3)

    assert str(cv.value) == '`name` must be a string.'


def test_ns_collection_invalid_value(ns_factory):
    ns = ns_factory()
    with pytest.raises(ValueError) as cv:
        ns.collection('')

    assert str(cv.value) == '`name` must not be blank.'


def test_ns_collection(ns_factory):
    ns = ns_factory()
    collection = ns.collection('resource')

    assert isinstance(collection, Collection)
    assert collection.client == ns.client
    assert collection.path == f'{ns.path}/resource'
    assert collection.specs is None


def test_ns_collection_with_specs(ns_factory, nsinfo_factory):
    specs = nsinfo_factory(collections=['resource'])
    ns = ns_factory(specs=specs)
    collection = ns.collection('resource')

    assert isinstance(collection, Collection)
    assert collection.client == ns.client
    assert collection.path == f'{ns.path}/resource'
    assert collection.specs == specs.collections['resource']


def test_ns_collection_with_specs_unresolved(ns_factory, nsinfo_factory):
    specs = nsinfo_factory(collections=['resource'])
    ns = ns_factory(specs=specs)

    with pytest.raises(NotFoundError) as cv:
        ns.collection('other')

    assert str(cv.value) == 'The collection other does not exist.'


def test_ns_getattr(ns_factory):
    ns = ns_factory()
    collection = ns.resource

    assert isinstance(collection, Collection)
    assert collection.client == ns.client
    assert collection.path == f'{ns.path}/resource'
    assert collection.specs is None


def test_ns_getattr_with_specs(ns_factory, nsinfo_factory):
    specs = nsinfo_factory(collections=['resource'])
    ns = ns_factory(specs=specs)

    collection = ns.resource

    assert isinstance(collection, Collection)
    assert collection.client == ns.client
    assert collection.path == f'{ns.path}/resource'
    assert collection.specs == specs.collections['resource']


def test_ns_getattr_with_specs_unresolved(ns_factory, nsinfo_factory):
    specs = nsinfo_factory(collections=['resource'])
    ns = ns_factory(specs=specs)

    with pytest.raises(AttributeError) as cv:
        ns.other

    assert str(cv.value) == 'Unable to resolve other.'


def test_ns_help(mocker, ns_factory, nsinfo_factory):
    specs = nsinfo_factory(collections=['resource'])
    ns = ns_factory(specs=specs)

    print_help = mocker.patch('cnct.client.models.print_help')

    ns2 = ns.help()

    assert print_help.called_once_with(specs)
    assert ns2 == ns


def test_collection_item(col_factory):
    collection = col_factory(path='resource')
    item = collection.item('item_id')

    assert isinstance(item, Item)
    assert item.path == f'{collection.path}/item_id'
    assert item.specs is None


def test_collection_getitem(col_factory):
    collection = col_factory(path='resource')
    item = collection['item_id']

    assert isinstance(item, Item)
    assert item.path == f'{collection.path}/item_id'
    assert item.specs is None


def test_collection_create(col_factory):
    collection = col_factory(path='resource')
    collection.create({'name': 'test'})

    assert collection.client.create.called_once_with(payload={'name': 'test'})

    collection.create({'name': 'test'}, headers={'Content-Type': 'application/json'})
    assert collection.client.create.called_once_with(
        payload={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )


def test_collection_search(col_factory):
    collection = col_factory(path='resource')

    search = collection.search()

    assert isinstance(search, Search)
    assert search.client == collection.client
    assert search.path == collection.path
    assert search.query == ''
    assert search.specs is None

    search = collection.search(query='eq(field,value)')

    assert search.client == collection.client
    assert search.path == collection.path
    assert search.query == 'eq(field,value)'
    assert search.specs is None


def test_collection_help(mocker, col_factory):
    collection = col_factory(path='resource')
    print_help = mocker.patch('cnct.client.models.print_help')

    col2 = collection.help()

    assert print_help.called_once_with(None)
    assert col2 == collection
