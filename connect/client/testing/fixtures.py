import pytest

from connect.client.testing import (
    AsyncConnectClientMocker,
    ConnectClientMocker,
    get_httpx_mocker,
    get_requests_mocker,
)


@pytest.fixture
def client_mocker_factory(request):
    """
    This fixture allows to instantiate a ConnectClient mocker
    to mock http calls made from the ConnectClient in an easy way.
    """
    mocker = None

    def _wrapper(base_url='https://example.org/public/v1', exclude=None):
        nonlocal mocker
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


@pytest.fixture
def requests_mocker():
    """
    This fixture allows you to mock http calls made using the `requests` library
    when they are made in conjunction with calls made with the `ConnectClient`.
    The returned mocker is the one provided by the
    [responses](https://github.com/getsentry/responses) library.
    """
    return get_requests_mocker()


@pytest.fixture
def httpx_mocker():
    """
    This fixture allows you to mock http calls made using the `httpx` library
    when they are made in conjunction with calls made with the `AsyncConnectClient`.
    The returned mocker is the one provided by the
    [pytest-httpx](https://colin-b.github.io/pytest_httpx/) library.
    """
    return get_httpx_mocker()
