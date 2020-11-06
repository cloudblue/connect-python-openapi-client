import pytest

from cnct.client.exceptions import ClientError
from cnct.client.models import Action, Collection, Resource, ResourceSet
from cnct.client.utils import ContentRange
from cnct.rql import R


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

    assert collection._client.create.called_once_with(payload={'name': 'test'})

    collection.create({'name': 'test'}, headers={'Content-Type': 'application/json'})
    assert collection._client.create.called_once_with(
        payload={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )


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

    assert resource._client.get.called_once()

    resource.get(headers={'Content-Type': 'application/json'})
    assert resource._client.create.called_once_with(
        headers={'Content-Type': 'application/json'},
    )


def test_resource_update(res_factory):
    resource = res_factory()
    resource.update({'name': 'test'})

    assert resource._client.update.called_once_with(payload={'name': 'test'})

    resource.update({'name': 'test'}, headers={'Content-Type': 'application/json'})
    assert resource._client.update.called_once_with(
        payload={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )


def test_resource_delete(res_factory):
    resource = res_factory()
    resource.delete()

    assert resource._client.delete.called_once()

    resource.delete(headers={'Content-Type': 'application/json'})
    assert resource._client.delete.called_once_with(
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
                'name': 'ok'
            },
        },
    )

    resource = res_factory()
    result = resource.values('id', 'sub_object.name')
    assert isinstance(result, dict)
    assert 'not_choosen' not in result
    assert 'id' in result and result['id'] == 'ID'
    assert 'sub_object.name' in result \
        and result['sub_object.name'] == 'ok'


def test_resource_help(res_factory):
    res = res_factory()
    res1 = res.help()

    res._client.print_help.assert_called_once_with(res)
    assert res1 == res


def test_action_get(action_factory):
    action = action_factory()
    action.get()

    assert action._client.get.called_once()

    action.get(headers={'Content-Type': 'application/json'})
    assert action._client.get.called_once_with(
        headers={'Content-Type': 'application/json'},
    )


def test_action_post(action_factory):
    action = action_factory()
    action.post({'name': 'test'})

    assert action._client.execute.called_once_with(
        'post',
        action.path,
        json={'name': 'test'},
    )

    action.post(
        {'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )
    assert action._client.execute.called_once_with(
        'post',
        action.path,
        json={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )

    action.post(
        json={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )
    assert action._client.execute.called_once_with(
        'post',
        action.path,
        json={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )


def test_action_put(action_factory):
    action = action_factory()
    action.put({'name': 'test'})

    assert action._client.execute.called_once_with(
        'put',
        action.path,
        json={'name': 'test'},
    )

    action.put(
        {'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )
    assert action._client.execute.called_once_with(
        'put',
        action.path,
        json={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )

    action.put(
        json={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )
    assert action._client.execute.called_once_with(
        'put',
        action.path,
        json={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )


def test_action_delete(action_factory):
    action = action_factory()
    action.delete()

    assert action._client.delete.called_once()

    action.delete(headers={'Content-Type': 'application/json'})
    assert action._client.delete.called_once_with(
        headers={'Content-Type': 'application/json'},
    )


def test_action_help(action_factory):
    action = action_factory()
    act2 = action.help()

    action._client.print_help.assert_called_once_with(action)
    assert act2 == action


def test_rs_iterate(mocker, rs_factory):
    mocker.patch(
        'cnct.client.models.resourceset.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=expected)

    results = [resource for resource in rs]
    assert results == expected


def test_rs_iterate_no_paging_endpoint(mocker, rs_factory):
    mocker.patch(
        'cnct.client.models.resourceset.parse_content_range',
        return_value=None,
    )
    expected = [{'id': i} for i in range(10)]
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=expected)

    results = [resource for resource in rs]
    assert results == expected


def test_rs_bool_truthy(mocker, rs_factory):
    mocker.patch(
        'cnct.client.models.resourceset.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=expected)
    assert bool(rs) is True


def test_rs_bool_falsy(mocker, rs_factory):
    mocker.patch(
        'cnct.client.models.resourceset.parse_content_range',
        return_value=ContentRange(0, 0, 0),
    )
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=[])
    assert bool(rs) is False


def test_rs_getitem(mocker, rs_factory):
    mocker.patch(
        'cnct.client.models.resourceset.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=expected)
    assert rs[0] == expected[0]


def test_rs_getitem_slice(mocker, rs_factory):
    mocker.patch(
        'cnct.client.models.resourceset.parse_content_range',
        return_value=ContentRange(0, 9, 10),
    )
    expected = [{'id': i} for i in range(10)]
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=expected)
    sliced = rs[2:4]
    assert isinstance(sliced, ResourceSet)
    assert sliced._limit == 2
    assert sliced._offset == 2


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
        'cnct.client.models.resourceset.parse_content_range',
        return_value=content_range,
    )
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=[])

    assert rs.count() == 100
    assert rs.content_range == content_range


def test_rs_first(mocker, rs_factory):
    content_range = ContentRange(0, 9, 10)
    mocker.patch(
        'cnct.client.models.resourceset.parse_content_range',
        return_value=content_range,
    )
    expected = [{'id': i} for i in range(10)]
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=expected)

    first = rs.first()

    assert first == expected[0]

    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=[])

    first = rs.first()

    assert first is None


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
        'cnct.client.models.resourceset.parse_content_range',
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
        'cnct.client.models.resourceset.parse_content_range',
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
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=return_value)

    rs = rs.values_list('id', 'inner.title')

    assert isinstance(rs, ResourceSet)
    assert list(rs) == expected


def test_rs_values_list_evaluated(mocker, rs_factory):
    mocker.patch(
        'cnct.client.models.resourceset.parse_content_range',
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
    rs = rs_factory()
    rs._client.get = mocker.MagicMock(return_value=return_value)

    bool(rs)
    values = rs.values_list('id', 'inner.title')

    assert values == expected


def test_rs_pagination(mocker, rs_factory):
    mocker.patch(
        'cnct.client.models.resourceset.parse_content_range',
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


def test_rs_values_list_pagination(mocker, rs_factory):
    mocker.patch(
        'cnct.client.models.resourceset.parse_content_range',
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

    assert list(rs.values_list('id', 'inner.title')) == expected


def test_rs_with_queries(mocker, rs_factory):
    mocker.patch(
        'cnct.client.models.resourceset.parse_content_range',
        return_value=ContentRange(0, 0, 0),
    )
    rs = rs_factory(query='eq(status,approved)')
    get_mock = mocker.MagicMock(return_value=[])
    rs._client.get = get_mock
    bool(rs)

    assert rs._client.get.called_once_with(f'{rs.path}?{rs.query}')


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
