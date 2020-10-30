import pytest

from cnct.client.exceptions import NotFoundError
from cnct.client.models import Action, Collection, Resource, ResourceSet
from cnct.client.utils import ContentRange
from cnct.help import DefaultFormatter
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
    collection = ns.collection('resource')

    assert isinstance(collection, Collection)
    assert collection._client == ns._client
    assert collection.path == f'{ns.path}/resource'
    assert collection._specs is None


def test_ns_collection_with_specs(ns_factory, nsinfo_factory, colinfo_factory):
    specs = nsinfo_factory(collections=[colinfo_factory(name='resource')])
    ns = ns_factory(specs=specs)
    collection = ns.collection('resource')

    assert isinstance(collection, Collection)
    assert collection._client == ns._client
    assert collection.path == f'{ns.path}/resource'
    assert collection._specs == specs.collections['resource']


def test_ns_collection_with_specs_unresolved(ns_factory, nsinfo_factory, colinfo_factory):
    specs = nsinfo_factory(collections=[colinfo_factory(name='resource')])
    ns = ns_factory(specs=specs)

    with pytest.raises(NotFoundError) as cv:
        ns.collection('other')

    assert str(cv.value) == 'The collection other does not exist.'


def test_ns_getattr(ns_factory):
    ns = ns_factory()
    with pytest.raises(AttributeError):
        ns.resource


def test_ns_getattr_with_specs(ns_factory, nsinfo_factory, colinfo_factory):
    specs = nsinfo_factory(collections=[colinfo_factory(name='resource')])
    ns = ns_factory(specs=specs)

    collection = ns.resource

    assert isinstance(collection, Collection)
    assert collection._client == ns._client
    assert collection.path == f'{ns.path}/resource'
    assert collection._specs == specs.collections['resource']


def test_ns_getattr_with_specs_unresolved(ns_factory, nsinfo_factory, colinfo_factory):
    specs = nsinfo_factory(collections=[colinfo_factory(name='resource')])
    ns = ns_factory(specs=specs)

    with pytest.raises(AttributeError) as cv:
        ns.other

    assert str(cv.value) == 'Unable to resolve other.'


def test_ns_dir_with_specs(ns_factory, nsinfo_factory, colinfo_factory):
    specs = nsinfo_factory(collections=[colinfo_factory(name='resource')])
    ns = ns_factory(specs=specs)

    dir_ = dir(ns)
    assert 'resource' in dir_
    assert 'collection' in dir_


def test_ns_dir_without_specs(ns_factory):
    ns = ns_factory()

    dir_ = dir(ns)

    assert 'collection' in dir_
    assert 'resource' not in dir_


def test_ns_help(mocker, ns_factory, nsinfo_factory, colinfo_factory):
    specs = nsinfo_factory(collections=[colinfo_factory(name='resource')])
    ns = ns_factory(specs=specs)

    print_help = mocker.patch.object(DefaultFormatter, 'print_help')

    ns2 = ns.help()

    assert print_help.called_once_with(specs)
    assert ns2 == ns


def test_collection_resource(col_factory):
    collection = col_factory(path='resource')
    resource = collection.resource('item_id')

    assert isinstance(resource, Resource)
    assert resource.path == f'{collection.path}/item_id'
    assert resource._specs is None


def test_collection_getitem(col_factory):
    collection = col_factory(path='resource')
    resource = collection['item_id']

    assert isinstance(resource, Resource)
    assert resource.path == f'{collection.path}/item_id'
    assert resource._specs is None


def test_collection_not_iterable(col_factory):
    collection = col_factory()

    with pytest.raises(TypeError) as cv:
        list(collection)

    assert str(cv.value) == 'A collection object is not iterable.'


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
    assert rs._specs is None

    rs = collection.filter('eq(field,value)')

    assert rs._client == collection._client
    assert rs.path == collection.path
    assert str(rs.query) == 'eq(field,value)'
    assert rs._specs is None

    rs = collection.filter(R().field.eq('value'))

    assert rs._client == collection._client
    assert rs.path == collection.path
    assert str(rs.query) == 'eq(field,value)'
    assert rs._specs is None

    rs = collection.filter(status__in=('status1', 'status2'))

    assert rs._client == collection._client
    assert rs.path == collection.path
    assert str(rs.query) == 'in(status,(status1,status2))'
    assert rs._specs is None


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
    assert rs._specs is None


def test_collection_help(mocker, col_factory):
    collection = col_factory(path='resource')
    print_help = mocker.patch.object(DefaultFormatter, 'print_help')

    col2 = collection.help()

    assert print_help.called_once_with(None)
    assert col2 == collection


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
    assert collection._specs is None


def test_resource_collection_with_specs(res_factory, colinfo_factory, resinfo_factory):
    specs = resinfo_factory(collections=[colinfo_factory(name='resource')])
    resource = res_factory(specs=specs)
    collection = resource.collection('resource')

    assert isinstance(collection, Collection)
    assert collection._client == resource._client
    assert collection.path == f'{resource.path}/resource'
    assert collection._specs == specs.collections['resource']


def test_resource_collection_with_specs_unresolved(res_factory, colinfo_factory, resinfo_factory):
    specs = resinfo_factory(collections=[colinfo_factory(name='resource')])
    resource = res_factory(specs=specs)

    with pytest.raises(NotFoundError) as cv:
        resource.collection('other')

    assert str(cv.value) == 'The collection other does not exist.'


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
    assert action._specs is None


def test_resource_action_with_specs(res_factory, resinfo_factory, actinfo_factory):
    specs = resinfo_factory(actions=[actinfo_factory(name='action')])
    resource = res_factory(specs=specs)
    action = resource.action('action')

    assert isinstance(action, Action)
    assert action._client == resource._client
    assert action.path == f'{resource.path}/action'
    assert action._specs == specs.actions['action']


def test_resource_action_with_specs_unresolved(res_factory, resinfo_factory, actinfo_factory):
    specs = resinfo_factory(actions=[actinfo_factory(name='action')])
    resource = res_factory(specs=specs)

    with pytest.raises(NotFoundError) as cv:
        resource.action('other')

    assert str(cv.value) == 'The action other does not exist.'


def test_resource_getattr_no_specs(res_factory):
    resource = res_factory()

    with pytest.raises(AttributeError) as cv:
        resource.resource

    assert str(cv.value) == (
        'No specs available. Use the `collection` '
        'or `action` methods instead.'
    )


def test_resource_getattr_with_specs(res_factory, colinfo_factory, resinfo_factory, actinfo_factory):
    specs = resinfo_factory(
        collections=[colinfo_factory(name='resource')],
        actions=[actinfo_factory(name='myaction')],
    )
    resource = res_factory(specs=specs)

    collection = resource.resource

    assert isinstance(collection, Collection)
    assert collection._client == resource._client
    assert collection.path == f'{resource.path}/resource'
    assert collection._specs == specs.collections['resource']

    action = resource.myaction

    assert isinstance(action, Action)
    assert action._client == resource._client
    assert action.path == f'{resource.path}/myaction'


def test_resource_getattr_with_specs_unresolved(res_factory, resinfo_factory, colinfo_factory):
    specs = resinfo_factory(collections=[colinfo_factory(name='resource')])
    resource = res_factory(specs=specs)

    with pytest.raises(AttributeError) as cv:
        resource.other

    assert str(cv.value) == 'Unable to resolve other.'


def test_resource_dir_with_specs(res_factory, colinfo_factory, resinfo_factory):
    specs = resinfo_factory(collections=[colinfo_factory(name='resource')])
    resource = res_factory(specs=specs)

    dir_ = dir(resource)
    assert 'resource' in dir_
    assert 'collection' in dir_


def test_resource_dir_without_specs(res_factory):
    resource = res_factory()

    dir_ = dir(resource)

    assert 'collection' in dir_
    assert 'resource' not in dir_


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


def test_resource_help(mocker, res_factory, colinfo_factory, resinfo_factory):
    specs = resinfo_factory(collections=[colinfo_factory(name='resource')])
    resource = res_factory(specs=specs)

    print_help = mocker.patch.object(DefaultFormatter, 'print_help')

    resource2 = resource.help()

    assert print_help.called_once_with(specs)
    assert resource2 == resource


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
        200,
        json={'name': 'test'},
    )

    action.post(
        {'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )
    assert action._client.execute.called_once_with(
        'post',
        action.path,
        200,
        json={'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )


def test_action_put(action_factory):
    action = action_factory()
    action.put({'name': 'test'})

    assert action._client.execute.called_once_with(
        'put',
        action.path,
        200,
        json={'name': 'test'},
    )

    action.put(
        {'name': 'test'},
        headers={'Content-Type': 'application/json'},
    )
    assert action._client.execute.called_once_with(
        'put',
        action.path,
        200,
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


def test_action_help(mocker, action_factory):
    action = action_factory(path='action')
    print_help = mocker.patch.object(DefaultFormatter, 'print_help')

    act2 = action.help()

    assert print_help.called_once_with(None)
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


def test_rs_help(mocker, rs_factory):
    rs = rs_factory(specs='this is a spec')
    print_help = mocker.patch.object(DefaultFormatter, 'print_help')
    rs2 = rs.help()
    assert print_help.called_once_with('this is a spec')
    assert rs2 == rs
