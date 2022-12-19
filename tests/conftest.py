import sys

import pytest
import responses

from connect.client.openapi import OpenAPISpecs
from connect.client.testing.fixtures import (  # noqa
    async_client_mocker_factory,
    client_mocker_factory,
)
from tests.fixtures.client_models import (  # noqa
    action_factory,
    async_action_factory,
    async_client_mock,
    async_col_factory,
    async_ns_factory,
    async_res_factory,
    async_rs_factory,
    col_factory,
    ns_factory,
    res_factory,
    rs_factory,
)


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture(scope='session')
def openapi_specs():
    return OpenAPISpecs('tests/data/specs.yml')


@pytest.fixture
def async_mocker(mocker):
    if sys.version_info >= (3, 8):
        return mocker

    import mock
    return mock
