from datetime import date, datetime
from decimal import Decimal

import pytest

from cnct.rql.base import RQLQuery


def test_create():
    q = RQLQuery()
    assert q.op == RQLQuery.EXPR
    assert q.children == []
    assert q.negated is False


def test_create_single_kwarg():
    q = RQLQuery(id='ID')
    assert q.op == RQLQuery.EXPR
    assert str(q) == 'eq(id,ID)'
    assert q.children == []
    assert q.negated is False


def test_create_multiple_kwargs():
    q = RQLQuery(id='ID', status__in=('a', 'b'))
    assert q.op == RQLQuery.AND
    assert str(q) == 'and(eq(id,ID),in(status,(a,b)))'
    assert len(q.children) == 2
    assert q.children[0].op == RQLQuery.EXPR
    assert q.children[0].children == []
    assert str(q.children[0]) == 'eq(id,ID)'
    assert q.children[1].op == RQLQuery.EXPR
    assert q.children[1].children == []
    assert str(q.children[1]) == 'in(status,(a,b))'


def test_len():
    q = RQLQuery()
    assert len(q) == 0

    q = RQLQuery(id='ID')
    assert len(q) == 1

    q = RQLQuery(id='ID', status__in=('a', 'b'))
    assert len(q) == 2


def test_bool():
    assert bool(RQLQuery()) is False
    assert bool(RQLQuery(id='ID')) is True
    assert bool(RQLQuery(id='ID', status__in=('a', 'b'))) is True


def test_eq():
    r1 = RQLQuery()
    r2 = RQLQuery()

    assert r1 == r2

    r1 = RQLQuery(id='ID')
    r2 = RQLQuery(id='ID')

    assert r1 == r2

    r1 = ~RQLQuery(id='ID')
    r2 = ~RQLQuery(id='ID')

    assert r1 == r2

    r1 = RQLQuery(id='ID', status__in=('a', 'b'))
    r2 = RQLQuery(id='ID', status__in=('a', 'b'))

    assert r1 == r2

    r1 = RQLQuery()
    r2 = RQLQuery(id='ID', status__in=('a', 'b'))

    assert r1 != r2


def test_or():
    r1 = RQLQuery()
    r2 = RQLQuery()

    r3 = r1 | r2

    assert r3 == r1
    assert r3 == r2

    r1 = RQLQuery(id='ID')
    r2 = RQLQuery(id='ID')

    r3 = r1 | r2

    assert r3 == r1
    assert r3 == r2

    r1 = RQLQuery(id='ID')
    r2 = RQLQuery(name='name')

    r3 = r1 | r2

    assert r3 != r1
    assert r3 != r2

    assert r3.op == RQLQuery.OR
    assert r1 in r3.children
    assert r2 in r3.children

    r = RQLQuery(id='ID')
    assert r | RQLQuery() == r
    assert RQLQuery() | r == r


def test_or_merge():
    r1 = RQLQuery(id='ID')
    r2 = RQLQuery(name='name')

    r3 = RQLQuery(field='value')
    r4 = RQLQuery(field__in=('v1', 'v2'))

    or1 = r1 | r2

    or2 = r3 | r4

    or3 = or1 | or2

    assert or3.op == RQLQuery.OR
    assert len(or3.children) == 4
    assert [r1, r2, r3, r4] == or3.children

    r1 = RQLQuery(id='ID')
    r2 = RQLQuery(field='value')

    r3 = r1 | r2 | r2

    assert len(r3) == 2
    assert r3.op == RQLQuery.OR
    assert [r1, r2] == r3.children


def test_and():
    r1 = RQLQuery()
    r2 = RQLQuery()

    r3 = r1 & r2

    assert r3 == r1
    assert r3 == r2

    r1 = RQLQuery(id='ID')
    r2 = RQLQuery(id='ID')

    r3 = r1 & r2

    assert r3 == r1
    assert r3 == r2

    r1 = RQLQuery(id='ID')
    r2 = RQLQuery(name='name')

    r3 = r1 & r2

    assert r3 != r1
    assert r3 != r2

    assert r3.op == RQLQuery.AND
    assert r1 in r3.children
    assert r2 in r3.children

    r = RQLQuery(id='ID')
    assert r & RQLQuery() == r
    assert RQLQuery() & r == r

    r1 = RQLQuery(id='ID')
    r2 = RQLQuery(field='value')

    r3 = r1 & r2 & r2

    assert len(r3) == 2
    assert r3.op == RQLQuery.AND
    assert [r1, r2] == r3.children


def test_and_or():
    r1 = RQLQuery(id='ID')
    r2 = RQLQuery(field='value')

    r3 = RQLQuery(other='value2')
    r4 = RQLQuery(inop__in=('a', 'b'))

    r5 = r1 & r2 & (r3 | r4)

    assert r5.op == RQLQuery.AND
    assert str(r5) == 'and(eq(id,ID),eq(field,value),or(eq(other,value2),in(inop,(a,b))))'

    r5 = r1 & r2 | r3

    assert str(r5) == 'or(and(eq(id,ID),eq(field,value)),eq(other,value2))'

    r5 = r1 & (r2 | r3)

    assert str(r5) == 'and(eq(id,ID),or(eq(field,value),eq(other,value2)))'

    r5 = (r1 & r2) | (r3 & r4)

    assert str(r5) == 'or(and(eq(id,ID),eq(field,value)),and(eq(other,value2),in(inop,(a,b))))'

    r5 = (r1 & r2) | ~r3

    assert str(r5) == 'or(and(eq(id,ID),eq(field,value)),not(eq(other,value2)))'


def test_and_merge():
    r1 = RQLQuery(id='ID')
    r2 = RQLQuery(name='name')

    r3 = RQLQuery(field='value')
    r4 = RQLQuery(field__in=('v1', 'v2'))

    and1 = r1 & r2

    and2 = r3 & r4

    and3 = and1 & and2

    assert and3.op == RQLQuery.AND
    assert len(and3.children) == 4
    assert [r1, r2, r3, r4] == and3.children


@pytest.mark.parametrize('op', ('eq', 'ne', 'gt', 'ge', 'le', 'lt'))
def test_dotted_path_comp(op):
    R = RQLQuery
    assert str(getattr(R().asset.id, op)('value')) == f'{op}(asset.id,value)'
    assert str(getattr(R().asset.id, op)(True)) == f'{op}(asset.id,true)'
    assert str(getattr(R().asset.id, op)(False)) == f'{op}(asset.id,false)'
    assert str(getattr(R().asset.id, op)(10)) == f'{op}(asset.id,10)'
    assert str(getattr(R().asset.id, op)(10.678937)) == f'{op}(asset.id,10.678937)'

    d = Decimal('32983.328238273')
    assert str(getattr(R().asset.id, op)(d)) == f'{op}(asset.id,{str(d)})'

    d = date.today()
    assert str(getattr(R().asset.id, op)(d)) == f'{op}(asset.id,{d.isoformat()})'

    d = datetime.now()
    assert str(getattr(R().asset.id, op)(d)) == f'{op}(asset.id,{d.isoformat()})'

    class Test:
        pass

    test = Test()

    with pytest.raises(TypeError):
        getattr(R().asset.id, op)(test)


@pytest.mark.parametrize(
    ('method', 'op'),
    (
        ('in_', 'in'),
        ('oneof', 'in'),
        ('out', 'out'),
    ),
)
def test_dotted_path_list(method, op):
    R = RQLQuery

    assert str(getattr(R().asset.id, method)(('first', 'second'))) == f'{op}(asset.id,(first,second))'
    assert str(getattr(R().asset.id, method)(['first', 'second'])) == f'{op}(asset.id,(first,second))'

    with pytest.raises(TypeError):
        getattr(R().asset.id, method)('Test')


@pytest.mark.parametrize(
    ('expr', 'value', 'expected_op'),
    (
        ('null', True, 'eq'),
        ('null', False, 'ne'),
        ('empty', True, 'eq'),
        ('empty', False, 'ne'),
    ),
)
def test_dotted_path_bool(expr, value, expected_op):
    R = RQLQuery

    assert str(getattr(R().asset.id, expr)(value)) == f'{expected_op}(asset.id,{expr}())'


def test_dotted_path_already_evaluated():

    q = RQLQuery().first.second.eq('value')

    with pytest.raises(AttributeError):
        q.third


def test_str():
    assert str(RQLQuery(id='ID')) == 'eq(id,ID)'
    assert str(~RQLQuery(id='ID')) == 'not(eq(id,ID))'
    assert str(~RQLQuery(id='ID', field='value')) == 'not(and(eq(id,ID),eq(field,value)))'


def test_hash():
    s = set()

    r = RQLQuery(id='ID', field='value')

    s.add(r)
    s.add(r)

    assert len(s) == 1
