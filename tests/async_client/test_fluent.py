import pytest

from connect.client import AsyncConnectClient


@pytest.mark.asyncio
async def test_async_get(mocker):
    url = 'https://localhost'
    kwargs = {
        'arg1': 'val1',
    }
    mocked = mocker.patch.object(AsyncConnectClient, 'execute')
    c = AsyncConnectClient('API_KEY', use_specs=False)
    await c.get(url, **kwargs)
    mocked.assert_awaited_once_with('get', url, **kwargs)
