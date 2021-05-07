import pytest

from connect.client import AsyncConnectClient


@pytest.mark.asyncio
async def test_async_get(async_mocker):
    url = 'https://localhost'
    mocked = async_mocker.patch.object(AsyncConnectClient, 'execute')
    c = AsyncConnectClient('API_KEY', endpoint=url, use_specs=False)
    await c.get(url)
    mocked.assert_awaited_once_with('get', url)
