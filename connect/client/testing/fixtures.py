import pytest

from connect.client.testing import AsyncConnectClientMocker, ConnectClientMocker


@pytest.fixture
def client_mocker_factory(request):
    """
    This fixture allows to instantiate a ConnectClient mocker
    to mock http calls made from the ConnectClient in an easy way.
    """
    mocker = None

    def _wrapper(base_url='https://example.org/public/v1', exclude=None):
        mocker = ConnectClientMocker(base_url, exclude=exclude)
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

    def _wrapper(base_url='https://example.org/public/v1', exclude=None):
        mocker = AsyncConnectClientMocker(base_url, exclude=exclude)
        mocker.start()
        return mocker

    def _finalizer():
        if mocker:  # pragma: no cover
            mocker.reset()

    request.addfinalizer(_finalizer)
    return _wrapper
