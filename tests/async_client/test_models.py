import pytest

from connect.client.exceptions import ClientError
from connect.client.models import (
    AsyncAction,
    AsyncCollection,
    AsyncNS,
    AsyncResource,
    AsyncResourceSet,
    NotYetEvaluatedError,
)
from connect.client.utils import ContentRange
from connect.client.rql import R


def test_ns_ns_invalid_type(async_ns_factory):
    ns = async_ns_factory()
    with pytest.raises(TypeError) as cv:
        ns.ns(None)

    assert str(cv.value) == '`name` must be a string.'

    with pytest.raises(TypeError) as cv:
        ns.ns(3)

    assert str(cv.value) == '`name` must be a string.'


def test_ns_ns_invalid_value(async_ns_factory):
    ns = async_ns_factory()
    with pytest.raises(ValueError) as cv:
        ns.ns('')

    assert str(cv.value) == '`name` must not be blank.'


def test_ns_ns(async_ns_factory):
    ns = async_ns_factory()
    ns2 = ns.ns('ns2')

    assert isinstance(ns2, AsyncNS)
    assert ns2._client == ns._client
    assert ns2.path == f'{ns.path}/ns2'


def test_ns_ns_call(async_ns_factory):
    ns = async_ns_factory()
    ns2 = ns('ns2')

    assert isinstance(ns2, AsyncNS)
    assert ns2._client == ns._client
    assert ns2.path == f'{ns.path}/ns2'


def test_ns_collection_invalid_type(async_ns_factory):
    ns = async_ns_factory()
    with pytest.raises(TypeError) as cv:
        ns.collection(None)

    assert str(cv.value) == '`name` must be a string.'

    with pytest.raises(TypeError) as cv:
        ns.collection(3)

    assert str(cv.value) == '`name` must be a string.'


def test_ns_collection_invalid_value(async_ns_factory):
    ns = async_ns_factory()
    with pytest.raises(ValueError) as cv:
        ns.collection('')

    assert str(cv.value) == '`name` must not be blank.'


def test_ns_collection(async_ns_factory):
    ns = async_ns_factory()
    collection = ns.collection('resources')

    assert isinstance(collection, AsyncCollection)
    assert collection._client == ns._client
    assert collection.path == f'{ns.path}/resources'


def test_ns_getattr(async_ns_factory):
    ns = async_ns_factory()
    col = ns.resources

    assert isinstance(col, AsyncCollection)
    assert col._client == ns._client
    assert col.path == f'{ns.path}/resources'


def test_ns_getattr_with_dash(async_ns_factory):
    ns = async_ns_factory()
    col = ns.my_resources

    assert isinstance(col, AsyncCollection)
    assert col._client == ns._client
    assert col.path == f'{ns.path}/my-resources'


def test_ns_not_iterable(async_ns_factory):
    ns = async_ns_factory()

    with pytest.raises(TypeError) as cv:
        list(ns)

    assert str(cv.value) == 'A Namespace object is not iterable.'


def test_ns_help(mocker, async_ns_factory):
    ns = async_ns_factory()
    ns1 = ns.help()

    ns._client.print_help.assert_called_once_with(ns)
    assert ns == ns1


def test_collection_resource(async_col_factory):
    collection = async_col_factory(path='resource')
    resource = collection.resource('item_id')

    assert isinstance(resource, AsyncResource)
    assert resource.path == f'{collection.path}/item_id'


def test_collection_resource_invalid_type(async_col_factory):
    collection = async_col_factory(path='resource')

    with pytest.raises(TypeError) as cv:
        collection.resource(None)

    assert str(cv.value) == '`resource_id` must be a string or int.'

    with pytest.raises(TypeError) as cv:
        collection.resource(3.77)

    assert str(cv.value) == '`resource_id` must be a string or int.'


def test_collection_resource_invalid_value(async_col_factory):
    collection = async_col_factory(path='resource')

    with pytest.raises(ValueError) as cv:
        collection.resource('')

    assert str(cv.value) == '`resource_id` must not be blank.'


def test_collection_getitem(async_col_factory):
    collection = async_col_factory(path='resource')
    resource = collection['item_id']

    assert isinstance(resource, AsyncResource)
    assert resource.path == f'{collection.path}/item_id'


def test_collection_not_iterable(async_col_factory):
    collection = async_col_factory()

    with pytest.raises(TypeError) as cv:
        list(collection)

    assert str(cv.value) == 'A Collection object is not iterable.'


@pytest.mark.asyncio
async def test_collection_create(async_client_mock, async_col_factory):
    client = async_client_mock(methods=['create'])
    collection = async_col_factory(
        client=client,
        path='resource',
    )

    await collection.create({'name': 'test'})
    collection._client.create.assert_awaited_once_with(collection.path, payload={'name': 'test'})

    await collection.create({'name': 'test'}, headers={'Content-Type': 'application/json'})
    collection._client.create.assert_awaited_with(
        collection.path,
        payload={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )


def test_collection_filter(async_col_factory):
    collection = async_col_factory(path='resource')

    rs = collection.filter()

    assert isinstance(rs, AsyncResourceSet)
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


def test_collection_filter_invalid_arg(async_col_factory):
    collection = async_col_factory(path='resource')

    with pytest.raises(TypeError):
        collection.filter(1)


def test_collection_all(async_col_factory):
    collection = async_col_factory(path='resource')

    rs = collection.all()

    assert isinstance(rs, AsyncResourceSet)
    assert rs._client == collection._client
    assert rs.path == collection.path
    assert bool(rs.query) is False


def test_collection_help(async_col_factory):
    col = async_col_factory()
    col1 = col.help()

    col._client.print_help.assert_called_once_with(col)
    assert col1 == col


def test_resource_getattr(async_res_factory):
    res = async_res_factory()
    col = res.resources

    assert isinstance(col, AsyncCollection)
    assert col._client == res._client
    assert col.path == f'{res.path}/resources'


def test_resource_getattr_with_dash(async_res_factory):
    res = async_res_factory()
    col = res.my_resources

    assert isinstance(col, AsyncCollection)
    assert col._client == res._client
    assert col.path == f'{res.path}/my-resources'


def test_resource_collection_invalid_type(async_res_factory):
    resource = async_res_factory()
    with pytest.raises(TypeError) as cv:
        resource.collection(None)

    assert str(cv.value) == '`name` must be a string.'

    with pytest.raises(TypeError) as cv:
        resource.collection(3)

    assert str(cv.value) == '`name` must be a string.'


def test_resource_collection_invalid_value(async_res_factory):
    resource = async_res_factory()
    with pytest.raises(ValueError) as cv:
        resource.collection('')

    assert str(cv.value) == '`name` must not be blank.'


def test_resource_collection(async_res_factory):
    resource = async_res_factory()
    collection = resource.collection('resource')

    assert isinstance(collection, AsyncCollection)
    assert collection._client == resource._client
    assert collection.path == f'{resource.path}/resource'


def test_resource_action_invalid_type(async_res_factory):
    resource = async_res_factory()
    with pytest.raises(TypeError) as cv:
        resource.action(None)

    assert str(cv.value) == '`name` must be a string.'

    with pytest.raises(TypeError) as cv:
        resource.action(3)

    assert str(cv.value) == '`name` must be a string.'


def test_resource_action_invalid_value(async_res_factory):
    resource = async_res_factory()
    with pytest.raises(ValueError) as cv:
        resource.action('')

    assert str(cv.value) == '`name` must not be blank.'


def test_resource_action(async_res_factory):
    resource = async_res_factory()
    action = resource.action('action')

    assert isinstance(action, AsyncAction)
    assert action._client == resource._client
    assert action.path == f'{resource.path}/action'


def test_resource_action_call(async_res_factory):
    resource = async_res_factory()
    action = resource('action')

    assert isinstance(action, AsyncAction)
    assert action._client == resource._client
    assert action.path == f'{resource.path}/action'


@pytest.mark.asyncio
async def test_resource_exists(async_client_mock, async_res_factory):
    resource = async_res_factory(
        client=async_client_mock(methods=['get']),
    )
    resource._client.get.return_value = {'id': 'res_id'}

    assert await resource.exists() is True
    ce = ClientError(status_code=404)
    resource._client.get.side_effect = ce

    assert await resource.exists() is False


@pytest.mark.asyncio
async def test_resource_exists_exception(async_client_mock, async_res_factory):
    resource = async_res_factory(
        client=async_client_mock(methods=['get']),
    )
    resource._client.get.return_value = {'id': 'res_id'}

    assert await resource.exists() is True
    ce = ClientError(status_code=500)
    resource._client.get.side_effect = ce

    with pytest.raises(ClientError):
        await resource.exists()


@pytest.mark.asyncio
async def test_resource_get(async_client_mock, async_res_factory):
    resource = async_res_factory(
        client=async_client_mock(methods=['get']),
    )
    await resource.get()

    resource._client.get.assert_awaited_once()

    await resource.get(headers={'Content-Type': 'application/json'})
    resource._client.get.assert_awaited_with(
        resource.path,
        headers={'Content-Type': 'application/json'},
    )


@pytest.mark.asyncio
async def test_resource_update(async_client_mock, async_res_factory):
    resource = async_res_factory(
        client=async_client_mock(methods=['update']),
    )
    await resource.update({'name': 'test'})

    resource._client.update.assert_awaited_once_with(resource.path, payload={'name': 'test'})

    await resource.update({'name': 'test'}, headers={'Content-Type': 'application/json'})
    resource._client.update.assert_awaited_with(
        resource.path,
        payload={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )


@pytest.mark.asyncio
async def test_resource_delete(async_client_mock, async_res_factory):
    resource = async_res_factory(
        client=async_client_mock(methods=['delete']),
    )
    await resource.delete()

    resource._client.delete.assert_awaited_once()

    await resource.delete(headers={'Content-Type': 'application/json'})
    resource._client.delete.assert_awaited_with(
        resource.path,
        headers={'Content-Type': 'application/json'},
    )


@pytest.mark.asyncio
async def test_resource_values(async_mocker, async_client_mock, async_res_factory):
    resource = async_res_factory(
        client=async_client_mock(methods=['get']),
    )
    resource.get = async_mocker.AsyncMock()
    resource.get.return_value = {
        'id': 'ID',
        'not_choosen': 'value',
        'sub_object': {
            'name': 'ok',
        },
    }

    result = await resource.values('id', 'sub_object.name')
    assert isinstance(result, dict)
    assert 'not_choosen' not in result
    assert 'id' in result and result['id'] == 'ID'
    assert (
        'sub_object.name' in result
        and result['sub_object.name'] == 'ok'
    )


def test_resource_help(async_res_factory):
    res = async_res_factory()
    res1 = res.help()

    res._client.print_help.assert_called_once_with(res)
    assert res1 == res


@pytest.mark.asyncio
async def test_action_get(async_client_mock, async_action_factory):
    action = async_action_factory(
        client=async_client_mock(methods=['get']),
    )
    await action.get()

    action._client.get.assert_awaited_once()

    await action.get(headers={'Content-Type': 'application/json'})
    action._client.get.assert_awaited_with(
        action.path,
        headers={'Content-Type': 'application/json'},
    )


@pytest.mark.asyncio
async def test_action_post(async_action_factory):
    action = async_action_factory()
    await action.post({'name': 'test'})

    action._client.execute.assert_awaited_once_with(
        'post',
        action.path,
        json={'name': 'test'},
    )

    await action.post(
        {'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )
    action._client.execute.assert_awaited_with(
        'post',
        action.path,
        json={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )

    await action.post(
        json={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )
    action._client.execute.assert_awaited_with(
        'post',
        action.path,
        json={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )


@pytest.mark.asyncio
async def test_action_put(async_action_factory):
    action = async_action_factory()
    await action.put({'name': 'test'})

    action._client.execute.assert_awaited_once_with(
        'put',
        action.path,
        json={'name': 'test'},
    )

    await action.put(
        {'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )
    action._client.execute.assert_awaited_with(
        'put',
        action.path,
        json={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )

    await action.put(
        json={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )
    action._client.execute.assert_awaited_with(
        'put',
        action.path,
        json={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )


@pytest.mark.asyncio
async def test_action_delete(async_client_mock, async_action_factory):
    action = async_action_factory(
        client=async_client_mock(methods=['delete']),
    )
    await action.delete()

    action._client.delete.assert_awaited_once()

    await action.delete(headers={'Content-Type': 'application/json'})
    action._client.delete.assert_awaited_with(
        action.path,
        headers={'Content-Type': 'application/json'},
    )


def test_action_help(async_action_factory):
    action = async_action_factory()
    act2 = action.help()

    action._client.print_help.assert_called_once_with(action)
    assert act2 == action


@pytest.mark.asyncio
async def test_rs_iterate(mocker, async_client_mock, async_rs_factory):
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    rs = async_rs_factory(
        client=async_client_mock(methods=['get']),
    )
    rs._client.get.return_value = expected

    results = [resource async for resource in rs]
    assert results == expected


@pytest.mark.asyncio
async def test_rs_iterate_no_paging_endpoint(mocker, async_client_mock, async_rs_factory):
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        return_value=None,
    )
    expected = [{'id': i} for i in range(10)]
    rs = async_rs_factory(
        client=async_client_mock(methods=['get']),
    )
    rs._client.get.return_value = expected

    results = [resource async for resource in rs]
    assert results == expected


@pytest.mark.asyncio
async def test_rs_bool_truthy(mocker, async_client_mock, async_rs_factory):
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    rs = async_rs_factory(
        client=async_client_mock(methods=['get']),
    )
    rs._client.get.return_value = expected
    results = [item async for item in rs]
    assert results == expected
    assert bool(rs) is True


def test_rs_bool_not_evaluated(async_client_mock, async_rs_factory):
    rs = async_rs_factory(
        client=async_client_mock(methods=['get']),
    )
    with pytest.raises(NotYetEvaluatedError):
        bool(rs)


@pytest.mark.asyncio
async def test_rs_bool_falsy(mocker, async_client_mock, async_rs_factory):
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        return_value=ContentRange(0, 0, 0),
    )
    rs = async_rs_factory(
        client=async_client_mock(methods=['get']),
    )
    rs._client.get.return_value = []
    results = [item async for item in rs]
    assert results == []
    assert bool(rs) is False


@pytest.mark.asyncio
async def test_rs_getitem(mocker, async_client_mock, async_rs_factory):
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    rs = async_rs_factory(
        client=async_client_mock(methods=['get']),
    )
    rs._client.get.return_value = expected
    results = [item async for item in rs]
    assert results == expected
    assert rs[0] == expected[0]


@pytest.mark.asyncio
async def test_rs_getitem_not_evaluated(async_client_mock, async_rs_factory):
    rs = async_rs_factory(
        client=async_client_mock(methods=['get']),
    )
    with pytest.raises(NotYetEvaluatedError):
        rs[0]


def test_rs_getitem_slice(mocker, async_client_mock, async_rs_factory):
    mocker.patch(
        'connect.client.models.resourceset.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    rs = async_rs_factory(
        client=async_client_mock(methods=['get']),
    )
    rs._client.get.return_value = expected
    sliced = rs[2:4]
    assert isinstance(sliced, AsyncResourceSet)
    assert sliced._limit == 2
    assert sliced._offset == 2
    rs._client.get.assert_not_awaited()


def test_rs_getitem_slice_type(async_rs_factory):
    rs = async_rs_factory()
    with pytest.raises(TypeError) as cv:
        rs['invalid']

    assert str(cv.value) == 'ResourceSet indices must be integers or slices.'


def test_rs_getitem_slice_negative(async_rs_factory):
    rs = async_rs_factory()
    with pytest.raises(ValueError) as cv:
        rs[1:-1]

    assert str(cv.value) == 'Negative indexing is not supported.'


def test_rs_getitem_slice_step(async_rs_factory):
    rs = async_rs_factory()
    with pytest.raises(ValueError) as cv:
        rs[0:10:2]

    assert str(cv.value) == 'Indexing with step is not supported.'


@pytest.mark.asyncio
async def test_rs_count(mocker, async_client_mock, async_rs_factory):
    content_range = ContentRange(0, 9, 100)
    mocker.patch(
        'connect.client.models.resourceset.parse_content_range',
        return_value=content_range,
    )
    rs = async_rs_factory(
        client=async_client_mock(methods=['get']),
    )
    rs._client.get.return_value = []

    assert await rs.count() == 100
    assert rs.content_range == content_range


@pytest.mark.asyncio
async def test_rs_first(mocker, async_client_mock, async_rs_factory):
    content_range = ContentRange(0, 9, 10)
    mocker.patch(
        'connect.client.models.resourceset.parse_content_range',
        return_value=content_range,
    )
    expected = [{'id': i} for i in range(10)]
    rs = async_rs_factory(
        client=async_client_mock(methods=['get']),
    )
    rs._client.get.return_value = expected

    first = await rs.first()

    assert first == expected[0]

    rs = async_rs_factory(
        client=async_client_mock(methods=['get']),
    )
    rs._client.get.return_value = []

    first = await rs.first()

    assert first is None


def test_rs_all(async_rs_factory):
    rs = async_rs_factory()
    rs1 = rs.all()

    assert isinstance(rs1, AsyncResourceSet)
    assert rs1 != rs


def test_rs_limit(async_rs_factory):
    rs = async_rs_factory()
    rs1 = rs.limit(300)

    assert rs1._limit == 300
    assert rs1 != rs


def test_rs_limit_invalid(async_rs_factory):
    rs = async_rs_factory()
    with pytest.raises(TypeError):
        rs.limit('3')

    with pytest.raises(ValueError):
        rs.limit(-1)


@pytest.mark.asyncio
async def test_rs_request(mocker, async_client_mock, async_rs_factory):
    rs = async_rs_factory(
        client=async_client_mock(methods=['get']),
    )
    content_range = ContentRange(0, 0, 0)
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        return_value=content_range,
    )
    rs._client.get.return_value = []

    rs = (
        rs.filter(field='value', field2__in=('a', 'b'))
        .search('search term')
        .select('obj1', '-obj2')
        .order_by('field1', '-field2')
    )

    rs._client.get.assert_not_called()

    [item async for item in rs]

    rs._client.get.assert_awaited_once()

    assert rs._client.get.call_args[0][0] == (
        'resources?select(obj1,-obj2)'
        '&and(eq(field,value),in(field2,(a,b)))'
        '&ordering(field1,-field2)'
    )


@pytest.mark.asyncio
async def test_rs_values_list(mocker, async_client_mock, async_rs_factory):
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
    rs = async_rs_factory(
        client=async_client_mock(methods=['get']),
    )
    rs._client.get.return_value = return_value

    rs = rs.values_list('id', 'inner.title')

    assert isinstance(rs, AsyncResourceSet)
    assert [item async for item in rs] == expected


@pytest.mark.asyncio
async def test_rs_values_list_evaluated(mocker, async_client_mock, async_rs_factory):
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
    rs = async_rs_factory(
        client=async_client_mock(methods=['get']),
    )
    rs._client.get.return_value = return_value

    results = [item async for item in rs]
    assert results == return_value
    values = rs.values_list('id', 'inner.title')

    assert values == expected


@pytest.mark.asyncio
async def test_rs_pagination(mocker, async_client_mock, async_rs_factory):
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        side_effect=[
            ContentRange(0, 99, 200),
            ContentRange(100, 199, 200),
        ],
    )

    rs = async_rs_factory(
        client=async_client_mock(methods=['get']),
    )
    rs._client.get.side_effect = [
        [{'id': i} for i in range(100)],
        [{'id': i} for i in range(100, 200)],
    ]
    results = [item async for item in rs]
    assert results == [{'id': i} for i in range(200)]
    assert rs._limit == 100
    assert rs._offset == 0


@pytest.mark.asyncio
async def test_rs_values_list_pagination(mocker, async_client_mock, async_rs_factory):
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        side_effect=[
            ContentRange(0, 99, 200),
            ContentRange(100, 199, 200),
        ],
    )

    rs = async_rs_factory(
        client=async_client_mock(methods=['get']),
    )
    rs._client.get.side_effect = [
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
    ]

    expected = [
        {
            'id': i,
            'inner.title': f'title {i}',
        }
        for i in range(200)
    ]

    assert [item async for item in rs.values_list('id', 'inner.title')] == expected


@pytest.mark.asyncio
async def test_rs_with_queries(mocker, async_client_mock, async_rs_factory):
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        return_value=ContentRange(0, 0, 0),
    )
    rs = async_rs_factory(
        client=async_client_mock(methods=['get']),
        query='eq(status,approved)',
    )
    rs._client.get.return_value = []
    items = [item async for item in rs]
    assert items == []
    rs._client.get.assert_awaited_once_with(
        f'{rs.path}?{rs.query}', params={'limit': 100, 'offset': 0},
    )


def test_rs_configure(async_rs_factory):
    rs = async_rs_factory()
    kwargs = {'k': 'v'}
    s1 = rs.configure(**kwargs)

    assert s1._config == kwargs
    assert s1 != rs


def test_rs_order_by(async_rs_factory):
    rs = async_rs_factory()
    fields = ('field1', '-field2')
    s1 = rs.order_by(*fields)

    for field in fields:
        assert field in s1._ordering
    assert len(fields) == len(s1._ordering)
    assert s1 != rs


def test_rs_select(async_rs_factory):
    rs = async_rs_factory()
    fields = ('field1', '-field2')
    s1 = rs.select(*fields)

    for field in fields:
        assert field in s1._select
    assert len(fields) == len(s1._select)
    assert s1 != rs


def test_rs_filter(async_rs_factory):
    rs = async_rs_factory()

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


def test_rs_filter_invalid_arg(async_rs_factory):
    rs = async_rs_factory()

    with pytest.raises(TypeError):
        rs.filter(1)


def test_rs_help(async_rs_factory):
    rs = async_rs_factory()
    rs2 = rs.help()
    rs._client.print_help.assery_called_once_with(rs)
    assert rs2 == rs


@pytest.mark.asyncio
async def test_rs_bool_truthy_already_evaluated(mocker, async_client_mock, async_rs_factory):
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    rs = async_rs_factory(
        client=async_client_mock(methods=['get']),
    )
    rs._client.get.return_value = expected
    items = [item async for item in rs]
    assert items == expected
    assert bool(rs) is True


@pytest.mark.asyncio
async def test_rs_count_already_evaluated(mocker, async_client_mock, async_rs_factory):
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    rs = async_rs_factory(
        client=async_client_mock(methods=['get']),
    )
    rs._client.get.return_value = expected
    _ = [item async for item in rs]
    assert await rs.count() == 10


def test_rs_slice_single_bound(mocker, async_rs_factory):
    rs = async_rs_factory()
    with pytest.raises(ValueError) as cv:
        rs[1:]
    assert str(cv.value) == 'Both start and stop indexes must be specified.'

    with pytest.raises(ValueError) as cv:
        rs[:1]
    assert str(cv.value) == 'Both start and stop indexes must be specified.'


@pytest.mark.asyncio
async def test_rs_slice_already_evaluated(mocker, async_client_mock, async_rs_factory):
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    rs = async_rs_factory(
        client=async_client_mock(methods=['get']),
    )
    rs._client.get.return_value = expected
    items = [item async for item in rs]
    assert items == expected
    assert rs[0:2] == expected[0:2]


@pytest.mark.asyncio
async def test_rs_iterate_already_evaluated(mocker, async_client_mock, async_rs_factory):
    mocker.patch(
        'connect.client.models.iterators.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    rs = async_rs_factory(
        client=async_client_mock(methods=['get']),
    )
    rs._client.get.return_value = expected
    assert [item async for item in rs] == expected
    assert [item async for item in rs] == expected
