import pytest

from connect.client.testing import AsyncConnectClientMocker, ConnectClientMocker


@pytest.fixture
def client_mocker_factory(request):
    mocker = None

    def _wrapper(base_url='http://localhost'):
        mocker = ConnectClientMocker(base_url)
        mocker.start()
        return mocker

    def _finalizer():
        if mocker:  # pragma: no cover
            mocker.reset()

    request.addfinalizer(_finalizer)
    return _wrapper


@pytest.fixture
def async_client_mocker_factory(request):
    mocker = None

    def _wrapper(base_url='http://localhost'):
        mocker = AsyncConnectClientMocker(base_url)
        mocker.start()
        return mocker

    def _finalizer():
        if mocker:  # pragma: no cover
            mocker.reset()

    request.addfinalizer(_finalizer)
    return _wrapper
