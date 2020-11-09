import pytest

from cnct.client.help_formatter import DefaultFormatter


def test_no_specs():
    formatter = DefaultFormatter(None)
    formatted = formatter.format(None)
    assert 'No OpenAPI specs available.' in formatted


def test_format_client(openapi_specs):
    formatter = DefaultFormatter(openapi_specs)
    formatted = formatter.format(None)
    assert openapi_specs.title in formatted
    assert openapi_specs.version in formatted


def test_format_ns(openapi_specs, ns_factory):
    formatter = DefaultFormatter(openapi_specs)
    ns = ns_factory(path='subscriptions')
    formatted = formatter.format(ns)
    assert 'Subscriptions namespace' in formatted
    assert 'path: /subscriptions' in formatted

    ns = ns_factory(path='does-not-exists')
    formatted = formatter.format(ns)
    assert 'does not exist' in formatted


@pytest.mark.parametrize(
    ('title', 'path'),
    (
        ('Products', 'products'),
        ('Assets', 'subscriptions/assets'),
        ('Items', 'products/PRD-000/items'),
    )
)
def test_format_collection(openapi_specs, col_factory, title, path):
    formatter = DefaultFormatter(openapi_specs)
    col = col_factory(path=path)
    formatted = formatter.format(col)
    assert f'{title} collection' in formatted
    assert f'path: /{path}' in formatted


def test_format_collection_not_exists(openapi_specs, col_factory):
    formatter = DefaultFormatter(openapi_specs)
    col = col_factory(path='does-not-exists')
    formatted = formatter.format(col)
    assert 'does not exist' in formatted


def test_format_resource(openapi_specs, res_factory):
    formatter = DefaultFormatter(openapi_specs)
    res = res_factory(path='products/PRD-000')
    formatted = formatter.format(res)
    assert 'Product resource' in formatted
    assert 'path: /products/PRD-000' in formatted

    res = res_factory(path='subscriptions/assets/AS-0000')
    formatted = formatter.format(res)
    assert 'Asset resource' in formatted
    assert 'path: /subscriptions/assets/AS-0000' in formatted

    res = res_factory(path='does-not-exists')
    formatted = formatter.format(res)
    assert 'does not exist' in formatted


def test_format_action(openapi_specs, action_factory):
    formatter = DefaultFormatter(openapi_specs)
    action = action_factory(path='products/PRD-000/endsale')
    formatted = formatter.format(action)
    assert 'Endsale action' in formatted
    assert 'path: /products/PRD-000/endsale' in formatted

    action = action_factory(path='does-not-exists')
    formatted = formatter.format(action)
    assert 'does not exist' in formatted


def test_format_ts(openapi_specs, rs_factory):
    formatter = DefaultFormatter(openapi_specs)
    rs = rs_factory(path='products')
    formatted = formatter.format(rs)
    assert 'Search the Products collection' in formatted
    assert 'path: /products' in formatted
    assert 'Available filters' in formatted

    rs = rs_factory(path='products/PRD-000/items')
    formatted = formatter.format(rs)
    assert 'Search the Items collection' in formatted
    assert 'path: /products/PRD-000/items' in formatted
    assert 'Available filters' in formatted

    rs = rs_factory(path='does-not-exists')
    formatted = formatter.format(rs)
    assert 'does not exist' in formatted
