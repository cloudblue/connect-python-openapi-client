import pytest

from connect.client import ClientError, ConnectClient
from connect.client.rql import R
from connect.client.testing.fluent import ConnectClientMocker


def test_create():
    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.create(return_value={'test': 'data'})
        client = ConnectClient('api_key', endpoint='http://localhost')
        assert client.products.create(payload={}) == {'test': 'data'}

    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.create(return_value={'test': 'data'}, match_body={'match': 'body'})
        client = ConnectClient('api_key', endpoint='http://localhost')
        assert client.products.create(payload={'match': 'body'}) == {'test': 'data'}

    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.create(return_value={'test': 'data'}, match_body=b'binary content')
        client = ConnectClient('api_key', endpoint='http://localhost')
        assert client.products.create(data=b'binary content') == {'test': 'data'}

    with pytest.raises(ClientError):
        with ConnectClientMocker('http://localhost') as mocker:
            mocker.products.create(return_value={'test': 'data'}, match_body=b'another content')
            client = ConnectClient('api_key', endpoint='http://localhost')
            assert client.products.create(data=b'binary content') == {'test': 'data'}

    with ConnectClientMocker('http://localhost') as mocker:
        mocker('my_namespace').products.create(return_value={'test': 'data'})
        client = ConnectClient('api_key', endpoint='http://localhost')
        assert client('my_namespace').products.create(payload={}) == {'test': 'data'}

    with ConnectClientMocker('http://localhost') as mocker:
        mocker('my_namespace')('another_namespace').products.create(return_value={'test': 'data'})
        client = ConnectClient('api_key', endpoint='http://localhost')
        assert client('my_namespace')('another_namespace').products.create(
            payload={},
        ) == {'test': 'data'}

    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products['product_id'].items.create(return_value={'test': 'data'})
        client = ConnectClient('api_key', endpoint='http://localhost')
        assert client.products['product_id'].items.create(payload={}) == {'test': 'data'}


def test_bulk_create():
    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.bulk_create(return_value=[{'test': 'data'}])
        client = ConnectClient('api_key', endpoint='http://localhost')
        assert client.products.bulk_create(payload=[]) == [{'test': 'data'}]


def test_retrieve():
    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products['product_id'].get(return_value={'test': 'data'})

        client = ConnectClient('api_key', endpoint='http://localhost')

        assert client.products['product_id'].get() == {'test': 'data'}


def test_update():
    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products['product_id'].update(return_value={'test': 'data'})

        client = ConnectClient('api_key', endpoint='http://localhost')

        assert client.products['product_id'].update(payload={}) == {'test': 'data'}


def test_bulk_update():
    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.bulk_update(return_value=[{'test': 'data'}])
        client = ConnectClient('api_key', endpoint='http://localhost')
        assert client.products.bulk_update(payload=[]) == [{'test': 'data'}]


def test_delete():
    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products['product_id'].delete()

        client = ConnectClient('api_key', endpoint='http://localhost')
        assert client.products['product_id'].delete() is None


def test_bulk_delete():
    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.bulk_delete()

        client = ConnectClient('api_key', endpoint='http://localhost')
        assert client.products.bulk_delete(payload=[]) is None


def test_action():
    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products['product_id']('my_action').get(return_value={'test': 'data'})

        client = ConnectClient('api_key', endpoint='http://localhost')
        assert client.products['product_id']('my_action').get() == {'test': 'data'}

    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products['product_id']('my_action').post(return_value={'test': 'data'})

        client = ConnectClient('api_key', endpoint='http://localhost')
        assert client.products['product_id']('my_action').post(payload={}) == {'test': 'data'}

    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products['product_id']('my_action').put(return_value={'test': 'data'})

        client = ConnectClient('api_key', endpoint='http://localhost')
        assert client.products['product_id']('my_action').put(payload={}) == {'test': 'data'}

    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products['product_id']('my_action').delete()

        client = ConnectClient('api_key', endpoint='http://localhost')
        assert client.products['product_id']('my_action').delete() is None

    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products('my_action').get(return_value={'test': 'data'})

        client = ConnectClient('api_key', endpoint='http://localhost')
        assert client.products('my_action').get() == {'test': 'data'}


@pytest.mark.parametrize('exists', (True, False))
def test_resource_exists(exists):
    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products['product_id'].exists(return_value=exists)
        client = ConnectClient('api_key', endpoint='http://localhost')
        assert client.products['product_id'].exists() is exists


def test_resource_values():
    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products['product_id'].values(return_value={'id': 'PRD-000', 'name': 'my_product'})
        client = ConnectClient('api_key', endpoint='http://localhost')
        assert client.products['product_id'].values('id') == {'id': 'PRD-000'}


def test_iterate():
    return_value = [
        {'id': f'OBJ-{i}'}
        for i in range(5)
    ]

    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.all().limit(2).mock(return_value=return_value)

        client = ConnectClient('api_key', endpoint='http://localhost')

        assert list(client.products.all().limit(2)) == return_value

    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.all().mock(return_value=return_value, headers={'X-Custom-Header': 'value'})

        client = ConnectClient('api_key', endpoint='http://localhost')

        assert list(client.products.all()) == return_value
        assert client.response.headers['X-Custom-Header'] == 'value'

    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.all().mock(return_value=[])

        client = ConnectClient('api_key', endpoint='http://localhost')

        assert list(client.products.all()) == []

    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.all().mock(return_value=[], headers={'X-Custom-Header': 'value'})

        client = ConnectClient('api_key', endpoint='http://localhost')

        assert list(client.products.all()) == []
        assert client.response.headers['X-Custom-Header'] == 'value'

    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.all().mock(return_value=return_value)

        client = ConnectClient('api_key', endpoint='http://localhost')

        assert list(client.products.all()) == return_value

    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.filter(test='value').mock(return_value=return_value)

        client = ConnectClient('api_key', endpoint='http://localhost')

        assert list(client.products.filter(test='value')) == return_value

    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.all().filter('eq(id,PRD-000)').mock(return_value=return_value)

        client = ConnectClient('api_key', endpoint='http://localhost')

        assert list(client.products.all().filter('eq(id,PRD-000)')) == return_value

    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.all().filter(R().id.eq('PRD-000')).mock(return_value=return_value)

        client = ConnectClient('api_key', endpoint='http://localhost')

        assert list(client.products.all().filter(R().id.eq('PRD-000'))) == return_value

    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.filter(test='value').search(
            'search_term',
        ).filter(
            another='value',
        ).all().select(
            '-field1', 'field2',
        ).order_by(
            'field3', '-field4',
        ).mock(return_value=return_value)

        client = ConnectClient('api_key', endpoint='http://localhost')

        assert list(client.products.filter(test='value').search(
            'search_term',
        ).filter(
            another='value',
        ).all().select(
            '-field1', 'field2',
        ).order_by(
            'field3', '-field4',
        )) == return_value


def test_first():
    return_value = [{'id': 'OBJ-0'}]

    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.all().first().mock(return_value=return_value)

        client = ConnectClient('api_key', endpoint='http://localhost')

        assert client.products.all().first() == return_value[0]


def test_indexing():
    return_value = [{'id': 'OBJ-0'}]

    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.all()[0].mock(return_value=return_value)

        client = ConnectClient('api_key', endpoint='http://localhost')

        assert client.products.all()[0] == return_value[0]


@pytest.mark.parametrize(
    ('total', 'start', 'stop'),
    (
        (5, 1, 3),
        (5, 1, 30),
        (200, 3, 115),
    ),
)
def test_slicing(total, start, stop):
    return_value = [
        {'id': f'OBJ-{i}'}
        for i in range(total)
    ]

    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.all()[start:stop].mock(return_value=return_value)

        client = ConnectClient('api_key', endpoint='http://localhost')

        assert list(client.products.all()[start:stop]) == return_value[start:stop]

    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.all()[start:stop].mock(
            return_value=return_value, headers={'X-Custom-Header': 'value'},
        )

        client = ConnectClient('api_key', endpoint='http://localhost')

        assert list(client.products.all()[start:stop]) == return_value[start:stop]
        assert client.response.headers['X-Custom-Header'] == 'value'


def test_slicing_no_results():

    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.all()[0:3].mock(return_value=[])

        client = ConnectClient('api_key', endpoint='http://localhost')

        assert list(client.products.all()[0:3]) == []

    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.all()[0:3].mock(
            return_value=[], headers={'X-Custom-Header': 'value'},
        )

        client = ConnectClient('api_key', endpoint='http://localhost')

        assert list(client.products.all()[0:3]) == []
        assert client.response.headers['X-Custom-Header'] == 'value'


def test_count():
    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.all().count(return_value=123)

        client = ConnectClient('api_key', endpoint='http://localhost')

        assert client.products.all().count() == 123

    with ConnectClientMocker('http://localhost') as mocker:
        return_value = [
            {'id': f'OBJ-{i}'}
            for i in range(5)
        ]

        mocker.products.all().mock(return_value=return_value)

        client = ConnectClient('api_key', endpoint='http://localhost')
        all_products = client.products.all()

        assert list(all_products) == return_value
        assert all_products.count() == 5


def test_iterate_error():
    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.all().mock(status_code=500)

        client = ConnectClient('api_key', endpoint='http://localhost')
        with pytest.raises(ClientError) as cv:
            list(client.products.all())

        assert cv.value.status_code == 500


def test_count_error():
    with ConnectClientMocker('http://localhost') as mocker:
        mocker.products.all().count(status_code=500)

        client = ConnectClient('api_key', endpoint='http://localhost')
        with pytest.raises(ClientError) as cv:
            client.products.all().count()

        assert cv.value.status_code == 500


def test_invalid_return_value():
    with pytest.raises(TypeError):
        with ConnectClientMocker('http://localhost') as mocker:
            mocker.products.all().mock(return_value='hello')

    with pytest.raises(TypeError):
        with ConnectClientMocker('http://localhost') as mocker:
            mocker.products.all().count(return_value='hello')
