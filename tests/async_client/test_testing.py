import re

import httpx
import pytest

from connect.client import AsyncConnectClient, ClientError
from connect.client.rql import R
from connect.client.testing.fluent import AsyncConnectClientMocker, _async_mocker, get_httpx_mocker


@pytest.mark.asyncio
async def test_create():
    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.create(return_value={'test': 'data'})
        client = AsyncConnectClient('api_key', endpoint='http://localhost')
        assert await client.products.create(payload={}) == {'test': 'data'}

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.create(return_value={'test': 'data'}, match_body={'match': 'body'})
        client = AsyncConnectClient('api_key', endpoint='http://localhost')
        assert await client.products.create(payload={'match': 'body'}) == {'test': 'data'}

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.create(return_value={'test': 'data'}, match_body=b'binary content')
        client = AsyncConnectClient('api_key', endpoint='http://localhost')
        assert await client.products.create(content=b'binary content') == {'test': 'data'}

    with pytest.raises(ClientError):
        with AsyncConnectClientMocker('http://localhost') as mocker:
            mocker.products.create(return_value={'test': 'data'}, match_body=b'another content')
            client = AsyncConnectClient('api_key', endpoint='http://localhost')
            assert await client.products.create(content=b'binary content') == {'test': 'data'}

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker('my_namespace').products.create(return_value={'test': 'data'})
        client = AsyncConnectClient('api_key', endpoint='http://localhost')
        assert await client('my_namespace').products.create(payload={}) == {'test': 'data'}

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker('my_namespace')('another_namespace').products.create(return_value={'test': 'data'})
        client = AsyncConnectClient('api_key', endpoint='http://localhost')
        assert await client('my_namespace')('another_namespace').products.create(
            payload={},
        ) == {'test': 'data'}

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products['product_id'].items.create(return_value={'test': 'data'})
        client = AsyncConnectClient('api_key', endpoint='http://localhost')
        assert await client.products['product_id'].items.create(payload={}) == {'test': 'data'}


@pytest.mark.asyncio
async def test_bulk_create():
    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.bulk_create(return_value=[{'test': 'data'}])
        client = AsyncConnectClient('api_key', endpoint='http://localhost')
        assert await client.products.bulk_create(payload=[]) == [{'test': 'data'}]


@pytest.mark.asyncio
async def test_retrieve():
    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products['product_id'].get(return_value={'test': 'data'})

        client = AsyncConnectClient('api_key', endpoint='http://localhost')

        assert await client.products['product_id'].get() == {'test': 'data'}


@pytest.mark.asyncio
async def test_update():
    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products['product_id'].update(return_value={'test': 'data'})

        client = AsyncConnectClient('api_key', endpoint='http://localhost')

        assert await client.products['product_id'].update(payload={}) == {'test': 'data'}


@pytest.mark.asyncio
async def test_bulk_update():
    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.bulk_update(return_value=[{'test': 'data'}])
        client = AsyncConnectClient('api_key', endpoint='http://localhost')
        assert await client.products.bulk_update(payload=[]) == [{'test': 'data'}]


@pytest.mark.asyncio
async def test_delete():
    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products['product_id'].delete()

        client = AsyncConnectClient('api_key', endpoint='http://localhost')
        assert await client.products['product_id'].delete() is None


@pytest.mark.asyncio
async def test_bulk_delete():
    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.bulk_delete()

        client = AsyncConnectClient('api_key', endpoint='http://localhost')
        assert await client.products.bulk_delete(payload=[]) is None


@pytest.mark.asyncio
async def test_action():
    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products['product_id']('my_action').get(return_value={'test': 'data'})

        client = AsyncConnectClient('api_key', endpoint='http://localhost')
        assert await client.products['product_id']('my_action').get() == {'test': 'data'}

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products['product_id']('my_action').post(return_value={'test': 'data'})

        client = AsyncConnectClient('api_key', endpoint='http://localhost')
        assert await client.products['product_id']('my_action').post(payload={}) == {'test': 'data'}

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products['product_id']('my_action').put(return_value={'test': 'data'})

        client = AsyncConnectClient('api_key', endpoint='http://localhost')
        assert await client.products['product_id']('my_action').put(payload={}) == {'test': 'data'}

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products['product_id']('my_action').delete()

        client = AsyncConnectClient('api_key', endpoint='http://localhost')
        assert await client.products['product_id']('my_action').delete() is None

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products('my_action').get(return_value={'test': 'data'})

        client = AsyncConnectClient('api_key', endpoint='http://localhost')
        assert await client.products('my_action').get() == {'test': 'data'}


@pytest.mark.asyncio
@pytest.mark.parametrize('exists', (True, False))
async def test_resource_exists(exists):
    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products['product_id'].exists(return_value=exists)
        client = AsyncConnectClient('api_key', endpoint='http://localhost')
        assert await client.products['product_id'].exists() is exists


@pytest.mark.asyncio
async def test_resource_values():
    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products['product_id'].values(return_value={'id': 'PRD-000', 'name': 'my_product'})
        client = AsyncConnectClient('api_key', endpoint='http://localhost')
        assert await client.products['product_id'].values('id') == {'id': 'PRD-000'}


@pytest.mark.asyncio
async def test_iterate():
    return_value = [
        {'id': f'OBJ-{i}'}
        for i in range(5)
    ]

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.all().limit(2).mock(return_value=return_value)

        client = AsyncConnectClient('api_key', endpoint='http://localhost')

        assert [item async for item in client.products.all().limit(2)] == return_value

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.all().mock(return_value=return_value, headers={'X-Custom-Header': 'value'})

        client = AsyncConnectClient('api_key', endpoint='http://localhost')

        assert [item async for item in client.products.all()] == return_value
        assert client.response.headers['X-Custom-Header'] == 'value'

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.all().mock(return_value=[])

        client = AsyncConnectClient('api_key', endpoint='http://localhost')

        assert [item async for item in client.products.all()] == []

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.all().mock(return_value=[], headers={'X-Custom-Header': 'value'})

        client = AsyncConnectClient('api_key', endpoint='http://localhost')

        assert [item async for item in client.products.all()] == []
        assert client.response.headers['X-Custom-Header'] == 'value'

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.all().mock(return_value=return_value)

        client = AsyncConnectClient('api_key', endpoint='http://localhost')

        assert [item async for item in client.products.all()] == return_value

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.filter(test='value').mock(return_value=return_value)

        client = AsyncConnectClient('api_key', endpoint='http://localhost')

        assert [item async for item in client.products.filter(test='value')] == return_value

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.all().filter('eq(id,PRD-000)').mock(return_value=return_value)

        client = AsyncConnectClient('api_key', endpoint='http://localhost')

        assert [item async for item in client.products.all().filter(
            'eq(id,PRD-000)',
        )] == return_value

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.all().filter(R().id.eq('PRD-000')).mock(return_value=return_value)

        client = AsyncConnectClient('api_key', endpoint='http://localhost')

        assert [item async for item in client.products.all().filter(
            R().id.eq('PRD-000'),
        )] == return_value

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.filter(test='value').search(
            'search_term',
        ).filter(
            another='value',
        ).all().select(
            '-field1', 'field2',
        ).order_by(
            'field3', '-field4',
        ).mock(return_value=return_value)

        client = AsyncConnectClient('api_key', endpoint='http://localhost')

        assert [item async for item in client.products.filter(test='value').search(
            'search_term',
        ).filter(
            another='value',
        ).all().select(
            '-field1', 'field2',
        ).order_by(
            'field3', '-field4',
        )] == return_value


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('total', 'start', 'stop'),
    (
        (5, 1, 3),
        (5, 1, 30),
        (200, 3, 115),
    ),
)
async def test_slicing(total, start, stop):
    return_value = [
        {'id': f'OBJ-{i}'}
        for i in range(total)
    ]

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.all()[start:stop].mock(return_value=return_value)

        client = AsyncConnectClient('api_key', endpoint='http://localhost')

        assert [
            item async for item in client.products.all()[start:stop]
        ] == return_value[start:stop]

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.all()[start:stop].mock(
            return_value=return_value, headers={'X-Custom-Header': 'value'},
        )

        client = AsyncConnectClient('api_key', endpoint='http://localhost')

        assert [
            item async for item in client.products.all()[start:stop]
        ] == return_value[start:stop]
        assert client.response.headers['X-Custom-Header'] == 'value'


@pytest.mark.asyncio
async def test_slicing_no_results():

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.all()[0:3].mock(return_value=[])

        client = AsyncConnectClient('api_key', endpoint='http://localhost')

        assert [
            item async for item in client.products.all()[0:3]
        ] == []

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.all()[0:3].mock(
            return_value=[], headers={'X-Custom-Header': 'value'},
        )

        client = AsyncConnectClient('api_key', endpoint='http://localhost')

        assert [
            item async for item in client.products.all()[0:3]
        ] == []
        assert client.response.headers['X-Custom-Header'] == 'value'


@pytest.mark.asyncio
async def test_count():
    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.all().count(return_value=123)

        client = AsyncConnectClient('api_key', endpoint='http://localhost')

        assert await client.products.all().count() == 123

    with AsyncConnectClientMocker('http://localhost') as mocker:
        return_value = [
            {'id': f'OBJ-{i}'}
            for i in range(5)
        ]

        mocker.products.all().mock(return_value=return_value)

        client = AsyncConnectClient('api_key', endpoint='http://localhost')
        all_products = client.products.all()

        assert [item async for item in all_products] == return_value
        assert await all_products.count() == 5


@pytest.mark.asyncio
async def test_iterate_error():
    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.all().mock(status_code=500)

        client = AsyncConnectClient('api_key', endpoint='http://localhost')
        with pytest.raises(ClientError) as cv:
            [item async for item in client.products.all()]

        assert cv.value.status_code == 500


@pytest.mark.asyncio
async def test_count_error():
    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.all().count(status_code=500)

        client = AsyncConnectClient('api_key', endpoint='http://localhost')
        with pytest.raises(ClientError) as cv:
            await client.products.all().count()

        assert cv.value.status_code == 500


def test_invalid_return_value():
    with pytest.raises(TypeError):
        with AsyncConnectClientMocker('http://localhost') as mocker:
            mocker.products.all().mock(return_value='hello')

    with pytest.raises(TypeError):
        with AsyncConnectClientMocker('http://localhost') as mocker:
            mocker.products.all().count(return_value='hello')


@pytest.mark.asyncio
async def test_inner_mockers():

    async def inner_mocking():
        with AsyncConnectClientMocker('http://localhost') as mocker:
            mocker.products.all().count(return_value=100)
            client = AsyncConnectClient('api_key', endpoint='http://localhost')
            assert await client.products.all().count() == 100
            assert [item async for item in client.products.all()] == [{'id': 'OBJ-0'}]

    with AsyncConnectClientMocker('http://localhost') as mocker:
        mocker.products.all().mock(return_value=[{'id': 'OBJ-0'}])

        await inner_mocking()


@pytest.mark.parametrize(
    'exclude',
    (
        'https://www.google.com',
        ['https://www.google.com', 'https://youtube.com'],
        re.compile(r'https://www.google.com(/\w*)?'),
        [re.compile(r'https://www.google.com(/\w*)?'), 'https://youtube.com'],
    ),
)
@pytest.mark.asyncio
async def test_exclude(mocker, exclude):
    with AsyncConnectClientMocker('http://localhost', exclude=exclude) as mocker:
        mocker.products.create(return_value={'test': 'data'})
        client = AsyncConnectClient('api_key', endpoint='http://localhost')
        assert await client.products.create(payload={}) == {'test': 'data'}
        async with httpx.AsyncClient() as client:
            r = await client.get('https://www.google.com')
            assert r.status_code == 200


def test_get_httpx_mocker():
    assert get_httpx_mocker() == _async_mocker
