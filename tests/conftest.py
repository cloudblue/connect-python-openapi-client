import sys

import pytest

import responses

from connect.client.openapi import OpenAPISpecs

from tests.fixtures.client_models import (  # noqa
    action_factory,
    async_action_factory,
    async_client_mock,
    async_col_factory,
    async_ns_factory,
    async_res_factory,
    async_rs_factory,
    col_factory,
    res_factory,
    ns_factory,
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
