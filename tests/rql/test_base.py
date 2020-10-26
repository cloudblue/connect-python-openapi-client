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
