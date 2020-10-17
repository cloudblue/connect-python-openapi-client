import pytest

from cnct.client.exceptions import NotFoundError
from cnct.client.models import Action, Collection, Item, Search
from cnct.client.utils import ContentRange


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


def test_ns_dir_with_specs(ns_factory, nsinfo_factory):
    specs = nsinfo_factory(collections=['resource'])
    ns = ns_factory(specs=specs)

    dir_ = dir(ns)
    assert 'resource' in dir_
    assert 'collection' in dir_


def test_ns_dir_without_specs(ns_factory):
    ns = ns_factory()

    dir_ = dir(ns)

    assert 'collection' in dir_
    assert 'resource' not in dir_


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


def test_collection_not_iterable(col_factory):
    collection = col_factory()

    with pytest.raises(TypeError) as cv:
        list(collection)

    assert str(cv.value) == 'A collection object is not iterable.'


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


def test_item_collection_invalid_type(item_factory):
    item = item_factory()
    with pytest.raises(TypeError) as cv:
        item.collection(None)

    assert str(cv.value) == '`name` must be a string.'

    with pytest.raises(TypeError) as cv:
        item.collection(3)

    assert str(cv.value) == '`name` must be a string.'


def test_item_collection_invalid_value(item_factory):
    item = item_factory()
    with pytest.raises(ValueError) as cv:
        item.collection('')

    assert str(cv.value) == '`name` must not be blank.'


def test_item_collection(item_factory):
    item = item_factory()
    collection = item.collection('resource')

    assert isinstance(collection, Collection)
    assert collection.client == item.client
    assert collection.path == f'{item.path}/resource'
    assert collection.specs is None


def test_item_collection_with_specs(item_factory, iteminfo_factory):
    specs = iteminfo_factory(collections=['resource'])
    item = item_factory(specs=specs)
    collection = item.collection('resource')

    assert isinstance(collection, Collection)
    assert collection.client == item.client
    assert collection.path == f'{item.path}/resource'
    assert collection.specs == specs.collections['resource']


def test_item_collection_with_specs_unresolved(item_factory, iteminfo_factory):
    specs = iteminfo_factory(collections=['resource'])
    item = item_factory(specs=specs)

    with pytest.raises(NotFoundError) as cv:
        item.collection('other')

    assert str(cv.value) == 'The collection other does not exist.'


def test_item_getattr_no_specs(item_factory):
    item = item_factory()

    with pytest.raises(AttributeError) as cv:
        item.resource

    assert str(cv.value) == (
        'No specs available. Use the `collection` '
        'or `action` methods instead.'
    )


def test_item_getattr_with_specs(item_factory, iteminfo_factory):
    specs = iteminfo_factory(collections=['resource'], actions=['myaction'])
    item = item_factory(specs=specs)

    collection = item.resource

    assert isinstance(collection, Collection)
    assert collection.client == item.client
    assert collection.path == f'{item.path}/resource'
    assert collection.specs == specs.collections['resource']

    action = item.myaction

    assert isinstance(action, Action)
    assert action.client == item.client
    assert action.path == f'{item.path}/myaction'


def test_item_getattr_with_specs_unresolved(item_factory, iteminfo_factory):
    specs = iteminfo_factory(collections=['resource'])
    item = item_factory(specs=specs)

    with pytest.raises(AttributeError) as cv:
        item.other

    assert str(cv.value) == 'Unable to resolve other.'


def test_item_dir_with_specs(item_factory, iteminfo_factory):
    specs = iteminfo_factory(collections=['resource'])
    item = item_factory(specs=specs)

    dir_ = dir(item)
    assert 'resource' in dir_
    assert 'collection' in dir_


def test_item_dir_without_specs(item_factory):
    item = item_factory()

    dir_ = dir(item)

    assert 'collection' in dir_
    assert 'resource' not in dir_


def test_item_get(item_factory):
    item = item_factory()
    item.get()

    assert item.client.get.called_once()

    item.get(headers={'Content-Type': 'application/json'})
    assert item.client.create.called_once_with(
        headers={'Content-Type': 'application/json'},
    )


def test_item_update(item_factory):
    item = item_factory()
    item.update({'name': 'test'})

    assert item.client.update.called_once_with(payload={'name': 'test'})

    item.update({'name': 'test'}, headers={'Content-Type': 'application/json'})
    assert item.client.update.called_once_with(
        payload={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )


def test_item_delete(item_factory):
    item = item_factory()
    item.delete()

    assert item.client.delete.called_once()

    item.delete(headers={'Content-Type': 'application/json'})
    assert item.client.delete.called_once_with(
        headers={'Content-Type': 'application/json'},
    )


def test_item_values(mocker, item_factory):
    mocker.patch.object(
        Item,
        'get',
        return_value={
            'id': 'ID',
            'not_choosen': 'value',
            'sub_object': {
                'name': 'ok'
            },
        },
    )

    item = item_factory()
    result = item.values('id', 'sub_object.name')
    assert isinstance(result, dict)
    assert 'not_choosen' not in result
    assert 'id' in result and result['id'] == 'ID'
    assert 'sub_object.name' in result \
        and result['sub_object.name'] == 'ok'


def test_item_help(mocker, item_factory, iteminfo_factory):
    specs = iteminfo_factory(collections=['resource'])
    item = item_factory(specs=specs)

    print_help = mocker.patch('cnct.client.models.print_help')

    item2 = item.help()

    assert print_help.called_once_with(specs)
    assert item2 == item


def test_action_get(action_factory):
    action = action_factory()
    action.get()

    assert action.client.get.called_once()

    action.get(headers={'Content-Type': 'application/json'})
    assert action.client.get.called_once_with(
        headers={'Content-Type': 'application/json'},
    )


def test_action_post(action_factory):
    action = action_factory()
    action.post({'name': 'test'})

    assert action.client.execute.called_once_with(
        'post',
        action.path,
        200,
        json={'name': 'test'},
    )

    action.post(
        {'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )
    assert action.client.execute.called_once_with(
        'post',
        action.path,
        200,
        json={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )


def test_action_put(action_factory):
    action = action_factory()
    action.put({'name': 'test'})

    assert action.client.execute.called_once_with(
        'put',
        action.path,
        200,
        json={'name': 'test'},
    )

    action.put(
        {'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )
    assert action.client.execute.called_once_with(
        'put',
        action.path,
        200,
        json={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )


def test_action_delete(action_factory):
    action = action_factory()
    action.delete()

    assert action.client.delete.called_once()

    action.delete(headers={'Content-Type': 'application/json'})
    assert action.client.delete.called_once_with(
        headers={'Content-Type': 'application/json'},
    )


def test_search_len(mocker, search_factory):
    mocker.patch(
        'cnct.client.models.parse_content_range',
        return_value=ContentRange(0, 9, 100),
    )
    results = [{'id': i} for i in range(10)]
    search = search_factory()
    search.client.get = mocker.MagicMock(return_value=results)

    assert len(search) == 10


def test_search_iterate(mocker, search_factory):
    mocker.patch(
        'cnct.client.models.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    search = search_factory()
    search.client.get = mocker.MagicMock(return_value=expected)

    results = [item for item in search]
    assert results == expected


def test_search_bool_truthy(mocker, search_factory):
    mocker.patch(
        'cnct.client.models.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    search = search_factory()
    search.client.get = mocker.MagicMock(return_value=expected)
    assert bool(search) is True


def test_search_bool_falsy(mocker, search_factory):
    mocker.patch(
        'cnct.client.models.parse_content_range',
        return_value=ContentRange(0, 0, 0),
    )
    search = search_factory()
    search.client.get = mocker.MagicMock(return_value=[])
    assert bool(search) is False


def test_search_getitem(mocker, search_factory):
    mocker.patch(
        'cnct.client.models.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    search = search_factory()
    search.client.get = mocker.MagicMock(return_value=expected)
    for i in range(10):
        assert search[i] == expected[i]


def test_search_getitem_slice(mocker, search_factory):
    mocker.patch(
        'cnct.client.models.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    search = search_factory()
    search.client.get = mocker.MagicMock(return_value=expected)
    sliced = search[2:4]
    assert isinstance(sliced, Search)
    assert search._limit == 2
    assert search._offset == 2


def test_search_getitem_slice_type(mocker, search_factory):
    search = search_factory()
    with pytest.raises(TypeError) as cv:
        search['invalid']

    assert str(cv.value) == 'Search indices must be integers or slices.'


def test_search_getitem_slice_negative(mocker, search_factory):
    search = search_factory()
    with pytest.raises(AssertionError) as cv:
        search[1:-1]

    assert str(cv.value) == 'Negative indexing is not supported.'


def test_search_getitem_slice_step(mocker, search_factory):
    search = search_factory()
    with pytest.raises(AssertionError) as cv:
        search[0:10:2]

    assert str(cv.value) == 'Indexing with step is not supported.'


def test_search_count(mocker, search_factory):
    mocker.patch(
        'cnct.client.models.parse_content_range',
        return_value=ContentRange(0, 9, 100),
    )
    expected = [{'id': i} for i in range(10)]
    search = search_factory()
    search.client.get = mocker.MagicMock(return_value=expected)

    assert search.count() == 100


def test_search_values_list(mocker, search_factory):
    mocker.patch(
        'cnct.client.models.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    return_value = [
        {
            'id': i,
            'name': f'name {i}',
            'inner': {
                'title': f'title {i}',
            }
        }
        for i in range(10)
    ]
    expected = [
        {
            'id': i,
            'inner.title': f'title {i}',
        }
        for i in range(10)
    ]
    search = search_factory()
    search.client.get = mocker.MagicMock(return_value=return_value)

    search = search.values_list('id', 'inner.title')

    assert isinstance(search, Search)
    assert list(search) == expected


def test_search_values_list_evaluated(mocker, search_factory):
    mocker.patch(
        'cnct.client.models.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    return_value = [
        {
            'id': i,
            'name': f'name {i}',
            'inner': {
                'title': f'title {i}',
            }
        }
        for i in range(10)
    ]
    expected = [
        {
            'id': i,
            'inner.title': f'title {i}',
        }
        for i in range(10)
    ]
    search = search_factory()
    search.client.get = mocker.MagicMock(return_value=return_value)

    bool(search)
    values = search.values_list('id', 'inner.title')

    assert values == expected


def test_search_pagination(mocker, search_factory):
    mocker.patch(
        'cnct.client.models.parse_content_range',
        side_effect=[
            ContentRange(0, 99, 200),
            ContentRange(100, 199, 200),
        ],
    )

    search = search_factory()
    search.client.get = mocker.MagicMock(side_effect=[
        [{'id': i} for i in range(100)],
        [{'id': i} for i in range(100, 200)],
    ])

    assert list(search) == [{'id': i} for i in range(200)]


def test_search_values_list_pagination(mocker, search_factory):
    mocker.patch(
        'cnct.client.models.parse_content_range',
        side_effect=[
            ContentRange(0, 99, 200),
            ContentRange(100, 199, 200),
        ],
    )

    search = search_factory()
    search.client.get = mocker.MagicMock(side_effect=[
        [
            {
                'id': i,
                'name': f'name {i}',
                'inner': {
                    'title': f'title {i}',
                }
            }
            for i in range(100)
        ],
        [
            {
                'id': i,
                'name': f'name {i}',
                'inner': {
                    'title': f'title {i}',
                }
            }
            for i in range(100, 200)
        ]
    ])

    expected = [
        {
            'id': i,
            'inner.title': f'title {i}',
        }
        for i in range(200)
    ]

    assert list(search.values_list('id', 'inner.title')) == expected


def test_search_with_queries(mocker, search_factory):
    mocker.patch(
        'cnct.client.models.parse_content_range',
        return_value=ContentRange(0, 0, 0),
    )
    search = search_factory(query='eq(status,approved)')
    get_mock = mocker.MagicMock(return_value=[])
    search.client.get = get_mock
    bool(search)

    assert search.client.get.called_once_with(f'{search.path}?{search.query}')


def test_search_help(mocker, search_factory):
    search = search_factory(specs='this is a spec')
    print_help = mocker.patch('cnct.client.models.print_help')
    search2 = search.help()
    assert print_help.called_once_with('this is a spec')
    assert search2 == search
