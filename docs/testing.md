Testing tools
=============

To make it easier to write unit tests for functions that use the
ConnectClient, two utility classes are available in the
connect.client.testing module:

-   `ConnectClientMocker` to mock http calls for the `ConnectClient`
-   `AsyncConnectClientMocker` to mock http calls for the
    `AsyncConnectClient`

Usage example
-------------

The `ConnectClientMocker` (or the `AsyncConnectClientMocker` for the
`AsyncConnectClient`) folow the same fluent interface as the
`ConnectClient`:

``` {.python}
from connect.client import ConnectClient
from connect.client.testing import ConnectClientMocker

def test_get_all_products():
    client = ConnectClient('ApiKey SU-000-000-000:xxxxxxxxxxxxxxxx')

    expected_response = [{'id': 'PRD-000'}]

    with ConnectClientMocker(client.endpoint) as mocker:
        mocker.products.all().mock(return_value=expected_response)

        assert list(client.products.all()) == expected_response
```

or if you use the `AsyncConnectClient`:

``` {.python}
from connect.client import AsyncConnectClient
from connect.client.testing import AsyncConnectClientMocker

async def test_get_all_products():
    client = AsyncConnectClient('ApiKey SU-000-000-000:xxxxxxxxxxxxxxxx')

    expected_response = [{'id': 'PRD-000'}]

    with AsyncConnectClientMocker(client.endpoint) as mocker:
        mocker.products.all().mock(return_value=expected_response)

        assert [item async for item in client.products.all()] == expected_response
```

Both the `ConnectClientMocker` and the `AsyncConnectClientMocker` constructors
accept an extra keywork argument `exclude` to exclude urls from mocking.
the exclude argument can be a string, a `re.Pattern` object or a list, tuple or set which elements
can be strings or `re.Pattern`.

Both mockers are also available as pytest fixtures:

``` {.python}
def test_get_all_products(client_mocker_factory):
    client = ConnectClient('ApiKey SU-000-000-000:xxxxxxxxxxxxxxxx')

    expected_response = [{'id': 'PRD-000'}]

    mocker = client_mocker_factory(base_url=client.endpoint)
    mocker.products.all().mock(return_value=expected_response)

    assert list(client.products.all()) == expected_response
```

Also the fixtures accept an extra keyword argument `exclude` that is passed
to the underlying mocker constructor.

For more example on how to use the client mocker see the
`tests/client/test_testing.py` file in the github repository.
