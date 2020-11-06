import pytest

import responses

from cnct.client.openapi import OpenAPISpecs

from tests.fixtures.client_models import (  # noqa
    action_factory,
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
