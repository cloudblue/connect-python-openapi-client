from datetime import date, datetime
from decimal import Decimal

from cnct.rql.utils import parse_kwargs


COMP = ('eq', 'ne', 'lt', 'le', 'gt', 'ge')
SEARCH = ('like', 'ilike')
LIST = ('in_', 'out')
NULL = 'null'
EMPTY = 'empty'

KEYWORDS = (*COMP, *SEARCH, *LIST, NULL, EMPTY)


class RQLQuery:

    AND = 'and'
    OR = 'or'
    EXPR = 'expr'

    def __init__(self, *, _op=EXPR, _children=None, _negated=False, _expr=None, **kwargs):
        self.op = _op
        self.children = _children or []
        self.negated = _negated
        self.expr = _expr
        self._path = []
        self._field = None
        if len(kwargs) == 1:
            self.op = self.EXPR
            self.expr = parse_kwargs(kwargs)[0]
        if len(kwargs) > 1:
            self.op = self.AND
            for token in parse_kwargs(kwargs):
                self.children.append(RQLQuery(_expr=token))

    def __len__(self):
        if self.op == self.EXPR:
            if self.expr:
                return 1
            return 0
        return len(self.children)

    def __bool__(self):
        return bool(self.children) or bool(self.expr)

    def __eq__(self, other):
        return (
            self.op == other.op
            and self.children == other.children
            and self.negated == other.negated
            and self.expr == other.expr
        )

    def __hash__(self):
        return hash(
            (self.op, self.expr, self.negated, *(hash(value) for value in self.children))
        )

    def __repr__(self):
        if self.op == self.EXPR:
            return f'<R({self.op}) {self.expr}>'
        return f'<R({self.op})>'

    def __and__(self, other):
        return self._join(other, self.AND)

    def __or__(self, other):
        return self._join(other, self.OR)

    def __invert__(self):
        query = RQLQuery(_op=self.AND, _expr=self.expr, _negated=True)
        query._append(self)
        return query

    def __getattr__(self, name):
        if self._field:
            raise AttributeError('Already evaluated')

        self._path.append(name)
        return self

    def __str__(self):
        return self._to_string(self)

    def ne(self, value):
        return self._bin('ne', value)

    def eq(self, value):
        return self._bin('eq', value)

    def lt(self, value):
        return self._bin('lt', value)

    def le(self, value):
        return self._bin('le', value)

    def gt(self, value):
        return self._bin('gt', value)

    def ge(self, value):
        return self._bin('ge', value)

    def out(self, value):
        return self._list('out', value)

    def in_(self, value):
        return self._list('in', value)

    def oneof(self, value):
        return self._list('in', value)

    def null(self, value):
        return self._bool('null', value)

    def empty(self, value):
        return self._bool('empty', value)

    def _bin(self, op, value):
        self._field = '.'.join(self._path)
        actual_value = None
        if isinstance(value, str):
            actual_value = value
        elif isinstance(value, bool):
            actual_value = 'true' if value else 'false'
            print(actual_value)
        elif isinstance(value, (int, float, Decimal)):
            actual_value = str(value)
        elif isinstance(value, (date, datetime)):
            actual_value = value.isoformat()
        else:
            raise TypeError(f"the `{op}` operator doesn't support the {type(value)} type.")

        self.expr = f'{op}({self._field},{actual_value})'
        return self

    def _list(self, op, value):
        self._field = '.'.join(self._path)
        actual_value = None
        if isinstance(value, (list, tuple)):
            actual_value = ','.join(value)
        if actual_value:
            self.expr = f'{op}({self._field},({actual_value}))'
            return self

        raise TypeError(f"the `{op}` operator doesn't support the {type(value)} type.")

    def _bool(self, expr, value):
        self._field = '.'.join(self._path)
        if bool(value) is False:
            self.expr = f'ne({self._field},{expr}())'
            return self
        self.expr = f'eq({self._field},{expr}())'
        return self

    def _to_string(self, query):
        tokens = []
        if query.expr:
            if query.negated:
                return f'not({query.expr})'
            return query.expr
        for c in query.children:
            if c.expr:
                if c.negated:
                    tokens.append(f'not({c.expr})')
                else:
                    tokens.append(c.expr)
                continue
            tokens.append(self._to_string(c))

        if not tokens:
            return ''

        if query.negated:
            return f'not({query.op}({",".join(tokens)}))'
        return f'{query.op}({",".join(tokens)})'

    def _copy(self, other):
        return RQLQuery(
            _op=other.op,
            _children=other.children[:],
            _expr=other.expr,
        )

    def _join(self, other, op):
        if self == other:
            return self._copy(self)
        if not other:
            return self._copy(self)
        if not self:
            return self._copy(other)

        query = RQLQuery(_op=op)
        query._append(self)
        query._append(other)
        return query

    def _append(self, other):
        if other in self.children:
            return other

        if (other.op == self.op or (len(other) == 1 and other.op != self.EXPR)) and not other.negated:
            self.children.extend(other.children)
            return self

        self.children.append(other)
        return self
