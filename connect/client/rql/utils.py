#
# This file is part of the Ingram Micro CloudBlue Connect Python OpenAPI Client.
#
# Copyright (c) 2021 Ingram Micro. All Rights Reserved.
#
from datetime import date, datetime
from decimal import Decimal


COMP = ('eq', 'ne', 'lt', 'le', 'gt', 'ge')
SEARCH = ('like', 'ilike')
LIST = ('in', 'out')
NULL = 'null'
EMPTY = 'empty'

KEYWORDS = (*COMP, *SEARCH, *LIST, NULL, EMPTY)


def parse_kwargs(query_dict):
    query = []
    for lookup, value in query_dict.items():
        tokens = lookup.split('__')
        if len(tokens) == 1:
            #  field=value
            field = tokens[0]
            value = to_rql_value('eq', value)
            query.append(f'eq({field},{value})')
            continue
        op = tokens[-1]
        if op not in KEYWORDS:
            # field__nested=value
            field = '.'.join(tokens)
            value = to_rql_value('eq', value)
            query.append(f'eq({field},{value})')
            continue
        field = '.'.join(tokens[:-1])
        if op in COMP or op in SEARCH:
            value = to_rql_value(op, value)
            query.append(f'{op}({field},{value})')
            continue
        if op in LIST:
            value = to_rql_value(op, value)
            query.append(f'{op}({field},({value}))')
            continue

        cmpop = 'eq' if value is True else 'ne'
        expr = 'null()' if op == NULL else 'empty()'
        query.append(f'{cmpop}({field},{expr})')

    return query


def to_rql_value(op, value):
    if op not in LIST:
        if isinstance(value, str):
            return value
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if isinstance(value, (int, float, Decimal)):
            return str(value)
        if isinstance(value, (date, datetime)):
            return value.isoformat()
    if op in LIST and isinstance(value, (list, tuple)):
        return ','.join(value)
    raise TypeError(f"the `{op}` operator doesn't support the {type(value)} type.")
