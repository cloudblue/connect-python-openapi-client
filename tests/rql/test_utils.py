import pytest

from cnct.rql.utils import parse_kwargs


def test_simple():
    expressions = parse_kwargs({'field': 'value'})
    assert isinstance(expressions, list)
    assert len(expressions) == 1
    assert expressions[0] == 'eq(field,value)'


def test_comparison():
    for op in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
        expressions = parse_kwargs({f'field__{op}': 'value'})
        assert isinstance(expressions, list)
        assert len(expressions) == 1
        assert expressions[0] == f'{op}(field,value)'


def test_list():
    for op in ('out', 'in'):
        expressions = parse_kwargs({f'field__{op}': ('value1', 'value2')})
        assert isinstance(expressions, list)
        assert len(expressions) == 1
        assert expressions[0] == f'{op}(field,(value1,value2))'


def test_nested_fields():
    expressions = parse_kwargs({'field__nested': 'value'})
    assert isinstance(expressions, list)
    assert len(expressions) == 1
    assert expressions[0] == 'eq(field.nested,value)'


@pytest.mark.parametrize(
    ('expr', 'value', 'expected_op'),
    (
        ('null', True, 'eq'),
        ('null', False, 'ne'),
        ('empty', True, 'eq'),
        ('empty', False, 'ne'),
    )
)
def test_null(expr, value, expected_op):
    expressions = parse_kwargs({f'field__{expr}': value})
    assert isinstance(expressions, list)
    assert len(expressions) == 1
    assert expressions[0] == f'{expected_op}(field,{expr}())'
