import pytest

from connect.client import AsyncConnectClient


@pytest.mark.asyncio
async def test_async_get(async_mocker):
    url = 'https://localhost'
    c = AsyncConnectClient('API_KEY', endpoint=url, use_specs=False)
    mocked = async_mocker.AsyncMock()
    c.execute = mocked
    await c.get(url)
    mocked.assert_awaited_once_with('get', url)
