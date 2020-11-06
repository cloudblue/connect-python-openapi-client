import pytest

from cnct.client.openapi import OpenAPISpecs


def test_load_from_file():
    oa = OpenAPISpecs('tests/data/specs.yml')
    assert oa._specs is not None


def test_load_from_url(mocked_responses):
    mocked_responses.add(
        'GET',
        'https://localhost/specs.yml',
        body=open('tests/data/specs.yml', 'r').read())

    oa = OpenAPISpecs('https://localhost/specs.yml')
    assert oa._specs is not None


def test_get_title(openapi_specs):
    assert openapi_specs.title is not None


def test_get_description(openapi_specs):
    assert openapi_specs.description is not None


def test_get_version(openapi_specs):
    assert openapi_specs.version is not None


def test_get_tags(openapi_specs):
    assert openapi_specs.tags is not None
    assert isinstance(openapi_specs.tags, list)


@pytest.mark.parametrize(
    ('method', 'path', 'expected'),
    (
        ('get', 'products', True),
        ('get', 'products?eq(status,published)', True),
        ('put', 'products', False),
        ('get', 'products/PRD-000', True),
        ('get', 'products/PRD-000/items', True),
        ('post', 'products/PRD-000/endsale', True),
        ('get', 'subscriptions/assets', True),
        ('get', 'subscriptions/assets/AS-000', True),
        ('get', 'resources/assets/AS-000', False),
    ),
)
def test_exists(openapi_specs, method, path, expected):
    assert openapi_specs.exists(method, path) is expected


def test_get_namespaces(openapi_specs):
    namespaces = openapi_specs.get_namespaces()
    assert namespaces == ['subscriptions']


def test_get_collections(openapi_specs):
    cols = openapi_specs.get_collections()
    assert cols == ['products']


def test_get_namespaced_collections(openapi_specs):
    cols = openapi_specs.get_namespaced_collections('subscriptions')

    assert cols == ['assets', 'requests']


def test_get_collection(openapi_specs):
    col = openapi_specs.get_collection('products')
    assert col is not None

    col = openapi_specs.get_collection('subscriptions/assets')
    assert col is not None

    col = openapi_specs.get_collection('does-not-exists')
    assert col is None


def test_get_resource(openapi_specs):
    res = openapi_specs.get_resource('products/PRD-000')
    assert res is not None

    res = openapi_specs.get_resource('subscriptions/assets/AS-0000')
    assert res is not None

    res = openapi_specs.get_resource('does-not-exists/dne-id')
    assert res is None


def test_get_actions(openapi_specs):
    actions = openapi_specs.get_actions('products/PRD-000')
    assert ['endsale', 'resumesale'] == sorted([x[0] for x in actions])


def test_get_action(openapi_specs):
    action = openapi_specs.get_action('products/PRD-000/endsale')
    assert action is not None

    action = openapi_specs.get_action('products/PRD-000/does-not-exist')
    assert action is None


def test_get_nested_collections(openapi_specs):
    nested = openapi_specs.get_nested_collections('products/PRD-000')
    assert [
        'actions',
        'agreements',
        'configurations',
        'connections',
        'items',
        'localizations',
        'media',
        'parameters',
        'templates',
        'versions'
    ] == [x[0] for x in nested]
