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
        query.append(self, op)
        query.append(other, op)
        return query

    def __and__(self, other):
        return self._join(other, self.AND)

    def __or__(self, other):
        return self._join(other, self.OR)

    def __invert__(self):
        query = RQLQuery(_op=self.AND, _expr=self.expr, _negated=True)
        query.append(self, self.AND)
        return query

    def __getattr__(self, name):
        if self._field:
            raise AttributeError('Already evaluated')

        if name in KEYWORDS:
            self._field = '.'.join(self._path)
            if name in (*COMP, *SEARCH):
                return lambda value: self._bin(name, value)
            if name in LIST:
                return lambda value: self._list(name, value)
            if name in (NULL, EMPTY):
                return lambda value: self._bool(name, value)

        self._path.append(name)
        return self

    def __str__(self):
        return self._to_string(self)

    def append(self, other, op):
        if other in self.children:
            return other

        if self.op == op:
            if (other.op == op or len(other) == 1) and not other.negated:
                self.children.extend(other.children)
                return self

            self.children.append(other)
            return self

        rql = RQLQuery(
            _op=self.op,
            _children=self.children,
            _negated=self.negated,
        )

        self.op = op
        self.children = [rql, other]
        return other

    def _bin(self, op, value):
        self.expr = f'{op}({self._field},{value})'
        return self

    def _list(self, op, value):
        if op == 'in_':
            op = 'in'
        self.expr = f'{op}({self._field},({",".join(value)}))'
        return self

    def _bool(self, expr, value):
        if value is False:
            self.expr = f'ne({self._field}, {expr}())'
            return self
        self.expr = f'eq({self._field}, {expr}())'
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
        if len(tokens) == 1:
            if query.negated:
                return f'not({tokens[0]})'
            return tokens[0]
        if query.negated:
            return f'not({query.op}({",".join(tokens)}))'
        return f'{query.op}({",".join(tokens)})'
