import mdv

from cnct.specs.models import ApiInfo, CollectionInfo, ItemInfo, NSInfo, OpInfo


def _print_api(specs):
        lines = [
            f'# Welcome to {specs.title} {specs.version}',
            '',
            '',
            '## Introduction'
            '',
        ] + specs.description.splitlines()

        lines += [
            '',
            '',
            '## Available namespaces',
        ]
        for ns_name in specs.namespaces.keys():
            lines.append(f'* {ns_name}')

        lines += [
            '',
            '',
            '## Available collections',
        ]
        for col_name in specs.collections.keys():
            lines.append(f'* {col_name}')

        print(mdv.main('\n'.join(lines)))


def _print_namespace(specs):
    lines = [
        f'# {specs.name.title()} namespace',
        '',
        '## Available collections',
        '',
        '',
    ]
    lines += [f'- {res}' for res in specs.collections.keys()]
    print(mdv.main('\n'.join(lines)))


def _print_collection(specs):
    lines = [
        f'# {specs.name.title()} collection',
        '',
        '## Operations',
        '',
        '',
    ]
    lines += [f'- {res}' for res in specs.operations.keys()]
    print(mdv.main('\n'.join(lines)))


def _print_item(specs):
    lines = []
    if specs.actions:
        lines += ['', '', '## Actions', '', '']
        lines += [f'- {res}' for res in specs.actions.keys()]
    if specs.collections:
        lines += ['', '', '## Nested collections', '', '']
        lines += [f'- {res}' for res in specs.collections.keys()]
    
    if lines:
        print(mdv.main('\n'.join(lines)))


def _print_operation(specs):
        lines = [
            f'# {specs.name.title()} {specs.collection_name}',
            '',
        ]
        params = specs.info.get('parameters')
        if params:
            lines += [
                '',
                '## Parameters',
                '',
            ]

        if specs.name == 'search':
            for param in specs.info.get('parameters'):
                if '$ref' in param:
                    continue
                name = param['name']
                description = param['description'].splitlines()
                req = '(*)' if param.get('required') else ''
                lines.append(f'**{name}** {req}')
                lines += [
                    f'    {line}' for line in description
                ]

        if lines:
            print(mdv.main('\n'.join(lines)))




def print_help(specs):
    if isinstance(specs, ApiInfo):
        return _print_api(specs)
    if isinstance(specs, NSInfo):
        return _print_namespace(specs)
    if isinstance(specs, CollectionInfo):
        return _print_collection(specs)
    if isinstance(specs, ItemInfo):
        return _print_item(specs)
    if isinstance(specs, OpInfo):
        return _print_operation(specs)