import pytest

from connect.client.exceptions import ClientError
from connect.client.models import (
    NS,
    Action,
    Collection,
    Resource,
    ResourceSet,
)
from connect.client.rql import R
from connect.client.utils import ContentRange


def test_ns_ns_invalid_type(ns_factory):
    ns = ns_factory()
    with pytest.raises(TypeError) as cv:
        ns.ns(None)

    assert str(cv.value) == '`name` must be a string.'

    with pytest.raises(TypeError) as cv:
        ns.ns(3)

    assert str(cv.value) == '`name` must be a string.'


def test_ns_ns_invalid_value(ns_factory):
    ns = ns_factory()
    with pytest.raises(ValueError) as cv:
        ns.ns('')

    assert str(cv.value) == '`name` must not be blank.'


def test_ns_ns(ns_factory):
    ns = ns_factory()
    ns2 = ns.ns('ns2')

    assert isinstance(ns2, NS)
    assert ns2._client == ns._client
    assert ns2.path == f'{ns.path}/ns2'


def test_ns_ns_call(ns_factory):
    ns = ns_factory()
    ns2 = ns('ns2')

    assert isinstance(ns2, NS)
    assert ns2._client == ns._client
    assert ns2.path == f'{ns.path}/ns2'


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
    collection = ns.collection('resources')

    assert isinstance(collection, Collection)
    assert collection._client == ns._client
    assert collection.path == f'{ns.path}/resources'


def test_ns_getattr(ns_factory):
    ns = ns_factory()
    col = ns.resources

    assert isinstance(col, Collection)
    assert col._client == ns._client
    assert col.path == f'{ns.path}/resources'


def test_ns_getattr_with_dash(ns_factory):
    ns = ns_factory()
    col = ns.my_resources

    assert isinstance(col, Collection)
    assert col._client == ns._client
    assert col.path == f'{ns.path}/my-resources'


def test_ns_not_iterable(ns_factory):
    ns = ns_factory()

    with pytest.raises(TypeError) as cv:
        list(ns)

    assert str(cv.value) == 'A Namespace object is not iterable.'


def test_ns_help(mocker, ns_factory):
    ns = ns_factory()
    ns1 = ns.help()

    ns._client.print_help.assert_called_once_with(ns)
    assert ns == ns1


def test_collection_resource(col_factory):
    collection = col_factory(path='resource')
    resource = collection.resource('item_id')

    assert isinstance(resource, Resource)
    assert resource.path == f'{collection.path}/item_id'


def test_collection_resource_invalid_type(col_factory):
    collection = col_factory(path='resource')

    with pytest.raises(TypeError) as cv:
        collection.resource(None)

    assert str(cv.value) == '`resource_id` must be a string or int.'

    with pytest.raises(TypeError) as cv:
        collection.resource(3.77)

    assert str(cv.value) == '`resource_id` must be a string or int.'


def test_collection_resource_invalid_value(col_factory):
    collection = col_factory(path='resource')

    with pytest.raises(ValueError) as cv:
        collection.resource('')

    assert str(cv.value) == '`resource_id` must not be blank.'


def test_collection_getitem(col_factory):
    collection = col_factory(path='resource')
    resource = collection['item_id']

    assert isinstance(resource, Resource)
    assert resource.path == f'{collection.path}/item_id'


def test_collection_not_iterable(col_factory):
    collection = col_factory()

    with pytest.raises(TypeError) as cv:
        list(collection)

    assert str(cv.value) == 'A Collection object is not iterable.'


def test_collection_create(col_factory):
    collection = col_factory(path='resource')
    collection.create({'name': 'test'})

    collection._client.create.assert_called_once_with('resource', payload={'name': 'test'})

    collection.create({'name': 'test'}, headers={'Content-Type': 'application/json'})
    collection._client.create.assert_called_with(
        'resource',
        payload={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )


def test_collection_create_invalid_type(col_factory):
    collection = col_factory(path='resource')

    with pytest.raises(TypeError) as excinfo:
        collection.create([{'name': 'test A'}, {'name': 'test B'}])

    assert str(excinfo.value) == '`payload` must be a dict.'


def test_collection_create_no_args(col_factory):
    collection = col_factory(path='resource')
    collection.create()
    collection._client.create.assert_called_once_with('resource', payload=None)


def test_collection_bulk_create(col_factory):
    collection = col_factory(path='resource')

    collection.bulk_create([{'name': 'test A'}, {'name': 'test B'}])
    collection._client.create.assert_called_once_with(
        'resource',
        payload=[{'name': 'test A'}, {'name': 'test B'}],
    )


def test_collection_bulk_create_invalid_type(col_factory):
    collection = col_factory(path='resource')

    with pytest.raises(TypeError) as excinfo:
        collection.bulk_create({'name': 'test A'})

    assert str(excinfo.value) == '`payload` must be a list or tuple.'


def test_collection_bulk_update(col_factory):
    collection = col_factory(path='resource')

    collection.bulk_update([{'id': 1, 'name': 'test A'}, {'id': 2, 'name': 'test B'}])
    collection._client.update.assert_called_once_with(
        'resource',
        payload=[{'id': 1, 'name': 'test A'}, {'id': 2, 'name': 'test B'}],
    )


def test_collection_bulk_update_invalid_type(col_factory):
    collection = col_factory(path='resource')

    with pytest.raises(TypeError) as excinfo:
        collection.bulk_update({'id': 1, 'name': 'test'})

    assert str(excinfo.value) == '`payload` must be a list or tuple.'


def test_collection_bulk_delete(col_factory):
    collection = col_factory(path='resource')

    collection.bulk_delete([{'id': 1}, {'id': 2}])
    collection._client.delete.assert_called_once_with('resource', payload=[{'id': 1}, {'id': 2}])


def test_collection_bulk_delete_invalid_type(col_factory):
    collection = col_factory(path='resource')

    with pytest.raises(TypeError) as excinfo:
        collection.bulk_delete({'id': 1})

    assert str(excinfo.value) == '`payload` must be a list or tuple.'


def test_collection_filter(col_factory):
    collection = col_factory(path='resource')

    rs = collection.filter()

    assert isinstance(rs, ResourceSet)
    assert rs._client == collection._client
    assert rs.path == collection.path
    assert bool(rs.query) is False

    rs = collection.filter('eq(field,value)')

    assert rs._client == collection._client
    assert rs.path == collection.path
    assert str(rs.query) == 'eq(field,value)'

    rs = collection.filter(R().field.eq('value'))

    assert rs._client == collection._client
    assert rs.path == collection.path
    assert str(rs.query) == 'eq(field,value)'

    rs = collection.filter(status__in=('status1', 'status2'))

    assert rs._client == collection._client
    assert rs.path == collection.path
    assert str(rs.query) == 'in(status,(status1,status2))'


def test_collection_filter_invalid_arg(col_factory):
    collection = col_factory(path='resource')

    with pytest.raises(TypeError):
        collection.filter(1)


def test_collection_all(col_factory):
    collection = col_factory(path='resource')

    rs = collection.all()

    assert isinstance(rs, ResourceSet)
    assert rs._client == collection._client
    assert rs.path == collection.path
    assert bool(rs.query) is False


def test_collection_help(col_factory):
    col = col_factory()
    col1 = col.help()

    col._client.print_help.assert_called_once_with(col)
    assert col1 == col


def test_collection_action_invalid_type(col_factory):
    collection = col_factory()
    with pytest.raises(TypeError) as cv:
        collection.action(None)

    assert str(cv.value) == '`name` must be a string.'

    with pytest.raises(TypeError) as cv:
        collection.action(3)

    assert str(cv.value) == '`name` must be a string.'


def test_collection_action_invalid_value(col_factory):
    collection = col_factory()
    with pytest.raises(ValueError) as cv:
        collection.action('')

    assert str(cv.value) == '`name` must not be blank.'


def test_collection_action(col_factory):
    collection = col_factory()
    action = collection.action('action')

    assert isinstance(action, Action)
    assert action._client == collection._client
    assert action.path == f'{collection.path}/action'


def test_collection_action_call(col_factory):
    collection = col_factory()
    action = collection('action')

    assert isinstance(action, Action)
    assert action._client == collection._client
    assert action.path == f'{collection.path}/action'


def test_resource_getattr(res_factory):
    res = res_factory()
    col = res.resources

    assert isinstance(col, Collection)
    assert col._client == res._client
    assert col.path == f'{res.path}/resources'


def test_resource_getattr_with_dash(res_factory):
    res = res_factory()
    col = res.my_resources

    assert isinstance(col, Collection)
    assert col._client == res._client
    assert col.path == f'{res.path}/my-resources'


def test_resource_collection_invalid_type(res_factory):
    resource = res_factory()
    with pytest.raises(TypeError) as cv:
        resource.collection(None)

    assert str(cv.value) == '`name` must be a string.'

    with pytest.raises(TypeError) as cv:
        resource.collection(3)

    assert str(cv.value) == '`name` must be a string.'


def test_resource_collection_invalid_value(res_factory):
    resource = res_factory()
    with pytest.raises(ValueError) as cv:
        resource.collection('')

    assert str(cv.value) == '`name` must not be blank.'


def test_resource_collection(res_factory):
    resource = res_factory()
    collection = resource.collection('resource')

    assert isinstance(collection, Collection)
    assert collection._client == resource._client
    assert collection.path == f'{resource.path}/resource'


def test_resource_action_invalid_type(res_factory):
    resource = res_factory()
    with pytest.raises(TypeError) as cv:
        resource.action(None)

    assert str(cv.value) == '`name` must be a string.'

    with pytest.raises(TypeError) as cv:
        resource.action(3)

    assert str(cv.value) == '`name` must be a string.'


def test_resource_action_invalid_value(res_factory):
    resource = res_factory()
    with pytest.raises(ValueError) as cv:
        resource.action('')

    assert str(cv.value) == '`name` must not be blank.'


def test_resource_action(res_factory):
    resource = res_factory()
    action = resource.action('action')

    assert isinstance(action, Action)
    assert action._client == resource._client
    assert action.path == f'{resource.path}/action'


def test_resource_action_call(res_factory):
    resource = res_factory()
    action = resource('action')

    assert isinstance(action, Action)
    assert action._client == resource._client
    assert action.path == f'{resource.path}/action'


def test_resource_exists(res_factory):
    resource = res_factory()
    resource._client.get.return_value = {'id': 'res_id'}

    assert resource.exists() is True
    ce = ClientError(status_code=404)
    resource._client.get.side_effect = ce

    assert resource.exists() is False


def test_resource_exists_exception(res_factory):
    resource = res_factory()
    resource._client.get.return_value = {'id': 'res_id'}

    assert resource.exists() is True
    ce = ClientError(status_code=500)
    resource._client.get.side_effect = ce

    with pytest.raises(ClientError):
        resource.exists()


def test_resource_get(res_factory):
    resource = res_factory()
    resource.get()

    resource._client.get.assert_called_once()

    resource.get(headers={'Content-Type': 'application/json'})
    resource._client.get.assert_called_with(
        resource.path,
        headers={'Content-Type': 'application/json'},
    )


def test_resource_update(res_factory):
    resource = res_factory()
    resource.update({'name': 'test'})

    resource._client.update.assert_called_once_with(resource.path, payload={'name': 'test'})

    resource.update({'name': 'test'}, headers={'Content-Type': 'application/json'})
    resource._client.update.assert_called_with(
        resource.path,
        payload={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )


def test_resource_delete(res_factory):
    resource = res_factory()
    resource.delete()

    resource._client.delete.assert_called_once()

    resource.delete(headers={'Content-Type': 'application/json'})
    resource._client.delete.assert_called_with(
        resource.path,
        headers={'Content-Type': 'application/json'},
    )


def test_resource_values(mocker, res_factory):
    mocker.patch.object(
        Resource,
        'get',
        return_value={
            'id': 'ID',
            'not_choosen': 'value',
            'sub_object': {
                'name': 'ok',
            },
        },
    )

    resource = res_factory()
    result = resource.values('id', 'sub_object.name')
    assert isinstance(result, dict)
    assert 'not_choosen' not in result
    assert 'id' in result and result['id'] == 'ID'
    assert (
        'sub_object.name' in result
        and result['sub_object.name'] == 'ok'
    )


def test_resource_help(res_factory):
    res = res_factory()
    res1 = res.help()

    res._client.print_help.assert_called_once_with(res)
    assert res1 == res


def test_action_get(action_factory):
    action = action_factory()
    action.get()

    action._client.get.assert_called_once()

    action.get(headers={'Content-Type': 'application/json'})
    action._client.get.assert_called_with(
        action.path,
        headers={'Content-Type': 'application/json'},
    )


def test_action_post(action_factory):
    action = action_factory()
    action.post({'name': 'test'})

    action._client.execute.assert_called_once_with(
        'post',
        action.path,
        json={'name': 'test'},
    )

    action.post(
        {'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )
    action._client.execute.assert_called_with(
        'post',
        action.path,
        json={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )

    action.post(
        json={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )
    action._client.execute.assert_called_with(
        'post',
        action.path,
        json={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )


def test_action_put(action_factory):
    action = action_factory()
    action.put({'name': 'test'})

    action._client.execute.assert_called_once_with(
        'put',
        action.path,
        json={'name': 'test'},
    )

    action.put(
        {'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )
    action._client.execute.assert_called_with(
        'put',
        action.path,
        json={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )

    action.put(
        json={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )
    action._client.execute.assert_called_with(
        'put',
        action.path,
        json={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )


def test_action_delete(action_factory):
    action = action_factory()
    action.delete()

    action._client.delete.assert_called_once()

    action.delete(headers={'Content-Type': 'application/json'})
    action._client.delete.assert_called_with(
        action.path,
        headers={'Content-Type': 'application/json'},
    )


def test_action_help(action_factory):
    action = action_factory()
    act2 = action.help()

    action._client.print_help.assert_called_once_with(action)
    assert act2 == action


def test_rs_iterate(mocker, rs_factory):
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=expected)

    results = [resource for resource in rs]
    assert results == expected


def test_rs_iterate_no_paging_endpoint(mocker, rs_factory):
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        return_value=None,
    )
    expected = [{'id': i} for i in range(10)]
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=expected)

    results = [resource for resource in rs]
    assert results == expected


def test_rs_iterate_page_no_results(mocker, rs_factory):
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        side_effect=[
            ContentRange(0, 9, 100),
            ContentRange(10, 19, 100),
        ],
    )
    first_page = [{'id': i} for i in range(10)]
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(
        side_effect=[
            first_page,
            [],
        ],
    )

    results = [resource for resource in rs]
    assert results == first_page


def test_rs_bool_truthy(mocker, rs_factory):
    mocker.patch(
        'connect.client.models.resourceset.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=expected)
    assert bool(rs) is True


def test_rs_bool_falsy(mocker, rs_factory):
    mocker.patch(
        'connect.client.models.resourceset.parse_content_range',
        return_value=ContentRange(0, 0, 0),
    )
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=[])
    assert bool(rs) is False


def test_rs_getitem(mocker, rs_factory):
    mocker.patch(
        'connect.client.models.resourceset.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=expected)
    assert rs[0] == expected[0]


def test_rs_getitem_slice(mocker, rs_factory):
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        return_value=ContentRange(2, 3, 10),
    )
    expected = [{'id': 2}, {'id': 3}]
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=expected)
    sliced = rs[2:4]
    results = [resource for resource in sliced]
    assert results == expected


def test_rs_getitem_slice_more_than_limit(mocker, rs_factory):
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        side_effect=[
            ContentRange(1, 100, 257),
            ContentRange(101, 101, 257),
        ],
    )
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(side_effect=[
        [{'id': i + 1} for i in range(100)],
        [{'id': 101}],
    ])
    sliced = rs[1:102]
    results = [resource for resource in sliced]
    assert results == [{'id': i + 1} for i in range(101)]


def test_rs_getitem_slice_more_than_limit_no_append(mocker, rs_factory):
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        side_effect=[
            ContentRange(0, 9, 25),
            ContentRange(10, 19, 25),
            ContentRange(20, 21, 25),
        ],
    )
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(side_effect=[
        [{'id': i} for i in range(10)],
        [{'id': i + 10} for i in range(10)],
        [{'id': 20}, {'id': 21}],
    ])
    rs._limit = 10
    rs._client.resourceset_append = False
    sliced = rs[0:22]
    results = [resource for resource in sliced]
    assert results == [{'id': i} for i in range(22)]


def test_rs_getitem_slice_type(mocker, rs_factory):
    rs = rs_factory()
    with pytest.raises(TypeError) as cv:
        rs['invalid']

    assert str(cv.value) == 'ResourceSet indices must be integers or slices.'


def test_rs_getitem_slice_negative(mocker, rs_factory):
    rs = rs_factory()
    with pytest.raises(ValueError) as cv:
        rs[1:-1]

    assert str(cv.value) == 'Negative indexing is not supported.'


def test_rs_getitem_slice_step(mocker, rs_factory):
    rs = rs_factory()
    with pytest.raises(ValueError) as cv:
        rs[0:10:2]

    assert str(cv.value) == 'Indexing with step is not supported.'


def test_rs_count(mocker, rs_factory):
    content_range = ContentRange(0, 9, 100)
    mocker.patch(
        'connect.client.models.resourceset.parse_content_range',
        return_value=content_range,
    )
    rs_copy = rs_factory()
    mocker.patch.object(ResourceSet, '_copy', return_value=rs_copy)
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=[])
    assert rs.count() == 100
    assert rs_copy.content_range == content_range


def test_rs_first(mocker, rs_factory):
    content_range = ContentRange(0, 9, 10)
    mocker.patch(
        'connect.client.models.resourceset.parse_content_range',
        return_value=content_range,
    )
    expected = [{'id': i} for i in range(10)]
    rs = rs_factory()

    rs_copy = rs_factory()

    mocker.patch.object(ResourceSet, '_copy', return_value=rs_copy)

    rs_copy._client.get = mocker.MagicMock(return_value=expected)

    first = rs.first()

    assert first == expected[0]
    assert rs._results is None
    assert rs_copy._results == expected
    assert rs_copy._limit == 1
    assert rs_copy._offset == 0

    rs = rs_factory()
    rs_copy = rs_factory()

    mocker.patch.object(ResourceSet, '_copy', return_value=rs_copy)
    rs._client.get = mocker.MagicMock(return_value=[])

    first = rs.first()

    assert first is None
    assert rs._results is None
    assert rs_copy._results == []
    assert rs_copy._limit == 1
    assert rs_copy._offset == 0


def test_rs_all(rs_factory):
    rs = rs_factory()
    rs1 = rs.all()

    assert isinstance(rs1, ResourceSet)
    assert rs1 != rs


def test_rs_limit(rs_factory):
    rs = rs_factory()
    rs1 = rs.limit(300)

    assert rs1._limit == 300
    assert rs1 != rs


def test_rs_limit_invalid(rs_factory):
    rs = rs_factory()
    with pytest.raises(TypeError):
        rs.limit('3')

    with pytest.raises(ValueError):
        rs.limit(-1)


def test_rs_request(mocker, rs_factory):
    rs = rs_factory()
    content_range = ContentRange(0, 0, 0)
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        return_value=content_range,
    )
    rs._client.get = mocker.MagicMock(return_value=[])

    rs = (
        rs.filter(field='value', field2__in=('a', 'b'))
        .search('search term')
        .select('obj1', '-obj2')
        .order_by('field1', '-field2')
    )

    rs._client.get.assert_not_called()

    list(rs)

    rs._client.get.assert_called_once()

    assert rs._client.get.call_args[0][0] == (
        'resources?select(obj1,-obj2)'
        '&and(eq(field,value),in(field2,(a,b)))'
        '&ordering(field1,-field2)'
    )


def test_rs_values_list(mocker, rs_factory):
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    return_value = [
        {
            'id': i,
            'name': f'name {i}',
            'inner': {
                'title': f'title {i}',
            },
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
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=return_value)

    rs = rs.values_list('id', 'inner.title')

    assert isinstance(rs, ResourceSet)
    assert list(rs) == expected


def test_rs_values_list_evaluated(mocker, rs_factory):
    mocker.patch(
        'connect.client.models.resourceset.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    return_value = [
        {
            'id': i,
            'name': f'name {i}',
            'inner': {
                'title': f'title {i}',
            },
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
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=return_value)

    bool(rs)
    values = rs.values_list('id', 'inner.title')

    assert values == expected


def test_rs_pagination(mocker, rs_factory):
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        side_effect=[
            ContentRange(0, 99, 200),
            ContentRange(100, 199, 200),
        ],
    )

    rs = rs_factory()
    rs._client.get = mocker.MagicMock(side_effect=[
        [{'id': i} for i in range(100)],
        [{'id': i} for i in range(100, 200)],
    ])
    results = list(rs)
    assert results == [{'id': i} for i in range(200)]
    assert rs._limit == 100
    assert rs._offset == 0
    assert len(rs._results) == 200


def test_rs_pagination_no_append(mocker, rs_factory):
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        side_effect=[
            ContentRange(0, 99, 200),
            ContentRange(100, 199, 200),
        ],
    )

    rs = rs_factory()
    rs._client.get = mocker.MagicMock(side_effect=[
        [{'id': i} for i in range(100)],
        [{'id': i} for i in range(100, 200)],
    ])
    rs._client.resourceset_append = False
    results = list(rs)
    assert results == [{'id': i} for i in range(200)]
    assert rs._limit == 100
    assert rs._offset == 0
    assert len(rs._results) == 100


def test_rs_values_list_pagination(mocker, rs_factory):
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        side_effect=[
            ContentRange(0, 99, 200),
            ContentRange(100, 199, 200),
        ],
    )

    rs = rs_factory()
    rs._client.get = mocker.MagicMock(side_effect=[
        [
            {
                'id': i,
                'name': f'name {i}',
                'inner': {
                    'title': f'title {i}',
                },
            }
            for i in range(100)
        ],
        [
            {
                'id': i,
                'name': f'name {i}',
                'inner': {
                    'title': f'title {i}',
                },
            }
            for i in range(100, 200)
        ],
    ])

    expected = [
        {
            'id': i,
            'inner.title': f'title {i}',
        }
        for i in range(200)
    ]

    assert list(rs.values_list('id', 'inner.title')) == expected


def test_rs_with_queries(mocker, rs_factory):
    mocker.patch(
        'connect.client.models.resourceset.parse_content_range',
        return_value=ContentRange(0, 0, 0),
    )
    rs = rs_factory(query='eq(status,approved)')
    get_mock = mocker.MagicMock(return_value=[])
    rs._client.get = get_mock
    bool(rs)

    rs._client.get.assert_called_once_with(
        f'{rs.path}?{rs.query}',
        **{'params': {'limit': 100, 'offset': 0}},
    )


def test_rs_configure(rs_factory):
    rs = rs_factory()
    kwargs = {'k': 'v'}
    s1 = rs.configure(**kwargs)

    assert s1._config == kwargs
    assert s1 != rs


def test_rs_order_by(rs_factory):
    rs = rs_factory()
    fields = ('field1', '-field2')
    s1 = rs.order_by(*fields)

    for field in fields:
        assert field in s1._ordering
    assert len(fields) == len(s1._ordering)
    assert s1 != rs


def test_rs_select(rs_factory):
    rs = rs_factory()
    fields = ('field1', '-field2')
    s1 = rs.select(*fields)

    for field in fields:
        assert field in s1._select
    assert len(fields) == len(s1._select)
    assert s1 != rs


def test_rs_filter(rs_factory):
    rs = rs_factory()

    assert rs.query is not None

    s1 = rs.filter()

    assert s1 != rs
    assert bool(s1.query) is False

    s1 = rs.filter('eq(field,value)')

    assert str(s1.query) == 'eq(field,value)'

    s1 = rs.filter(R().field.eq('value'))

    assert str(s1.query) == 'eq(field,value)'

    s2 = s1.filter(status__in=('status1', 'status2'))

    assert s1 != s2

    assert str(s2.query) == 'and(eq(field,value),in(status,(status1,status2)))'


def test_rs_filter_invalid_arg(rs_factory):
    rs = rs_factory()

    with pytest.raises(TypeError):
        rs.filter(1)


def test_rs_help(rs_factory):
    rs = rs_factory()
    rs2 = rs.help()
    rs._client.print_help.assery_called_once_with(rs)
    assert rs2 == rs


def test_rs_bool_truthy_already_evaluated(mocker, rs_factory):
    mocker.patch(
        'connect.client.models.resourceset.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    rs = rs_factory()
    mocked = mocker.patch.object(ResourceSet, '_execute_request', wraps=rs._execute_request)
    rs._client.get = mocker.MagicMock(return_value=expected)
    assert bool(rs) is True
    assert bool(rs) is True
    mocked.assert_called_once()


def test_rs_count_already_evaluated(mocker, rs_factory):
    mocker.patch(
        'connect.client.models.resourceset.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=expected)
    assert bool(rs) is True
    assert rs.count() == 10


def test_rs_slice_single_bound(mocker, rs_factory):
    rs = rs_factory()
    with pytest.raises(ValueError) as cv:
        rs[1:]
    assert str(cv.value) == 'Both start and stop indexes must be specified.'

    with pytest.raises(ValueError) as cv:
        rs[:1]
    assert str(cv.value) == 'Both start and stop indexes must be specified.'


def test_rs_slice_already_evaluated(mocker, rs_factory):
    mocker.patch(
        'connect.client.models.resourceset.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=expected)
    assert bool(rs) is True
    assert rs[0:2] == expected[0:2]


def test_rs_iterate_already_evaluated(mocker, rs_factory):
    mocker.patch(
        'connect.client.models.resourceset.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=expected)
    assert bool(rs) is True
    assert [item for item in rs] == expected
