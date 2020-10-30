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
            query.append(f'eq({field},{value})')
            continue
        op = tokens[-1]
        if op not in KEYWORDS:
            # field__nested=value
            field = '.'.join(tokens)
            query.append(f'eq({field},{value})')
            continue
        field = '.'.join(tokens[:-1])
        if op in COMP or op in SEARCH:
            query.append(f'{op}({field},{value})')
            continue
        if op in LIST:
            value = ','.join(value)
            query.append(f'{op}({field},({value}))')
            continue

        cmpop = 'eq' if value is True else 'ne'
        expr = 'null()' if op == NULL else 'empty()'
        query.append(f'{cmpop}({field},{expr})')

    return query
