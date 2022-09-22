import pytest

from connect.client import AsyncConnectClient


@pytest.mark.asyncio
async def test_client_mocker_factory(async_client_mocker_factory):
    mocker = async_client_mocker_factory('http://example.com')
    mocker.products.create(return_value={'id': 'PRD-000'})

    client = AsyncConnectClient('api_key', endpoint='http://example.com')
    assert await client.products.create(payload={}) == {'id': 'PRD-000'}
