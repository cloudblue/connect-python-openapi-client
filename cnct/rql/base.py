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
    """
    Helper class to construct complex RQL queries.
    """
    AND = 'and'
    OR = 'or'
    EXPR = 'expr'

    def __init__(self, *, _op=EXPR, _children=None, _negated=False, _expr=None, **kwargs):
        """
        Create a new R object.

        Query filters can be expressed through keyword arguments or using methods.

        Ex.

        .. code-block:: python

            rql = R(field='value', field2__in=('v1', 'v2'), field3__empty=True)

        All the lookups expressed as keyword arguments are combined together with a logical ``and``.

        Using the ``n`` method:

        .. code-block:: python

            rql = R().n('field').eq('value') & R().n('field2').in_(('v1', 'v2')) & R().n('field3').empty(True)

        The previous query can be expressed in a more concise form like:

        .. code-block:: python

            rql = R().field.eq('value') & R().field2.in_(('v1', 'v2')) & r.field3.empty(True)

        The R object support the bitwise operators ``&``, ``|`` and ``~``.

        Nested fields can be expressed using dot notation:

        .. code-block:: python

            rql = R().n('nested.field').eq('value')

        or

        .. code-block:: python

            rql = R().nested.field.eq('value')
        """
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
        """
        Returns the length of this R object.
        It will be 1 if represent a single RQL expression
        or the number of expressions this logical operator (and, or)
        applies to.

        :return: The length of this R object.
        :rtype: int
        """
        if self.op == self.EXPR:
            if self.expr:
                return 1
            return 0
        return len(self.children)

    def __bool__(self):
        """
        Returns False if it is an empty R object otherwise True.

        :return: False if it is an empty R object otherwise True.
        :rtype: bool
        """
        return bool(self.children) or bool(self.expr)

    def __eq__(self, other):
        """
        Returns True if self == other.

        :param other: Another R object.
        :type other: R
        :return: True if the ``other`` object is equal to self, False otherwise.
        :rtype: bool
        """
        return (
            self.op == other.op
            and self.children == other.children
            and self.negated == other.negated
            and self.expr == other.expr
        )

    def __hash__(self):
        """
        Calculate a hash that identifies uniquely this R object.

        :return: The hash of this object.
        :rtype: int
        """
        return hash(
            (self.op, self.expr, self.negated, *(hash(value) for value in self.children))
        )

    def __repr__(self):
        if self.op == self.EXPR:
            return f'<R({self.op}) {self.expr}>'
        return f'<R({self.op})>'

    def __and__(self, other):
        """
        Combine this R object with ``other`` using a logical ``and``.

        :param other: Another R object.
        :type other: R
        :return: The R object representing a logical ``and`` between this and ``other``.
        :rtype: R
        """
        return self._join(other, self.AND)

    def __or__(self, other):
        """
        Combine this R object with ``other`` using a logical ``or``.

        :param other: Another R object.
        :type other: R
        :return: The R object representing a logical ``or`` between this and ``other``.
        :rtype: R
        """
        return self._join(other, self.OR)

    def __invert__(self):
        """
        Apply the RQL ``not`` operator to this R object.

        :return: The R object representing this R object negated.
        :rtype: R
        """
        query = RQLQuery(_op=self.AND, _expr=self.expr, _negated=True)
        query._append(self)
        return query

    def __getattr__(self, name):
        if self._field:
            raise AttributeError('Already evaluated')

        return self.n(name)

    def __str__(self):
        return self._to_string(self)

    def n(self, name):
        """
        Set the current field for this R object.

        :param name: name of the field
        :type name: str
        :raises AttributeError: if this R object has already been evaluated.
        :return: This R object.
        :rtype: R
        """
        if self._field:
            raise AttributeError('Already evaluated')

        self._path.extend(name.split('.'))
        return self

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


R = RQLQuery
