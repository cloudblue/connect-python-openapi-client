import httpx
import pytest

from connect.client import AsyncConnectClient


@pytest.mark.asyncio
async def test_client_mocker_factory(async_client_mocker_factory):
    mocker = async_client_mocker_factory('http://example.com')
    mocker.products.create(return_value={'id': 'PRD-000'})

    client = AsyncConnectClient('api_key', endpoint='http://example.com')
    assert await client.products.create(payload={}) == {'id': 'PRD-000'}


@pytest.mark.asyncio
async def test_httpx_mocker(async_client_mocker_factory, httpx_mocker):
    mocker = async_client_mocker_factory('http://example.com')
    mocker.products.create(return_value={'id': 'PRD-000'})
    httpx_mocker.add_response(
        method='GET',
        url='https://test.com',
        json=[{"key1": "value1", "key2": "value2"}],
    )

    client = AsyncConnectClient('api_key', endpoint='http://example.com')
    assert await client.products.create(payload={}) == {'id': 'PRD-000'}

    async with httpx.AsyncClient() as client:
        response = await client.get('https://test.com')
        assert response.json() == [{"key1": "value1", "key2": "value2"}]
