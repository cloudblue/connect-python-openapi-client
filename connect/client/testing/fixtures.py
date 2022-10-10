import pytest

from connect.client.testing import AsyncConnectClientMocker, ConnectClientMocker


@pytest.fixture
def client_mocker_factory(request):
    """
    This fixture allows to instantiate a ConnectClient mocker
    to mock http calls made from the ConnectClient in an easy way.
    """
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
    """
    This fixture allows to instantiate a AsyncConnectClient mocker
    to mock http calls made from the AsyncConnectClient in an easy way.
    """
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
