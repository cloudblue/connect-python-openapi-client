from collections import OrderedDict
from cmr import render
from cnct.specs.models import (
    ActionInfo,
    ApiInfo,
    CollectionInfo,
    ResourceInfo,
    NSInfo,
    OpInfo,
)

_SPACE = ['', '']


class DefaultFormatter:
    def print_api(self, specs):
        lines = [
            *_SPACE,
            f'# Welcome to {specs.title} {specs.version}',
            '',
            '',
            '## Introduction'
            '',
        ] + specs.description.splitlines() + ['<br><br>']

        tagged = OrderedDict()
        for t in specs.tags.keys():
            collections = [
                name for name in specs.collections.keys()
                if specs.collections[name].tag == t
            ]
            namespaces = [
                name for name in specs.namespaces.keys()
                if specs.namespaces[name].tag == t
            ]
            if collections or namespaces:
                tagged[t] = {
                    'namespaces': namespaces,
                    'collections': collections,
                }

        lines += [
            '\n',
            '\n',
        ]

        for tag, children in tagged.items():
            lines.append(f'## {tag}')
            lines.append('\n\n')
            if specs.tags[tag]:
                lines += specs.tags[tag].splitlines()
                lines.append('\n\n')
            if children['namespaces']:
                lines.append('#### Namespaces')
                for nsname in children['namespaces']:
                    lines.append(f'* {nsname}')
                lines.append('\n\n')
            if children['collections']:
                lines.append('#### Collections')
                for colname in children['collections']:
                    lines.append(f'* {colname}')
                lines.append('\n\n')

        return render('\n'.join(lines))

    def print_namespace(self, specs):
        lines = [
            f'# {specs.name.title()} namespace',
            '',
            '## Available collections',
            '',
            '',
        ]
        lines += [f'- {res}' for res in specs.collections.keys()]
        return '\n' + render('\n'.join(lines))

    def print_collection(self, specs):
        lines = _SPACE + [
            f'# {specs.name.title()} collection',
            '',
        ]
        if specs.summary:
            lines += ['## Summary'] + _SPACE
            lines += specs.summary.splitlines() + _SPACE
        if specs.description:
            lines += ['## Description'] + _SPACE
            lines += specs.description.splitlines() + _SPACE

        if specs.operations:
            lines += ['## Operations']
            lines += [
                f'- {res}' for res in specs.operations.keys()
                if res not in ('get', 'update', 'delete')
            ] + _SPACE
        return render('\n'.join(lines))

    def print_resource(self, specs):
        lines = []
        if specs.summary:
            lines += ['## Summary'] + _SPACE
            lines += specs.summary.splitlines() + _SPACE
        if specs.description:
            lines += ['## Description'] + _SPACE
            lines += specs.description.splitlines() + _SPACE
        if specs.actions:
            lines += ['## Actions'] + _SPACE
            lines += [f'- {res}' for res in specs.actions.keys()] + _SPACE
        if specs.collections:
            lines += ['## Nested collections'] + _SPACE
            lines += [f'- {res}' for res in specs.collections.keys()] + _SPACE

        if lines:
            return '\n' + render('\n'.join(lines))
        return ''

    def print_operation(self, specs):
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

        return render('\n'.join(lines))

    def print_action(self, specs):
        lines = [
            *_SPACE,
            f'# {specs.name.title()} action',
            '',
        ]
        if specs.summary:
            lines += ['## Summary'] + _SPACE
            lines += specs.summary.splitlines() + _SPACE
        if specs.description:
            lines += ['## Description'] + _SPACE
            lines += specs.description.splitlines() + _SPACE

        lines += ['## Methods']
        lines += [f'- {res}' for res in specs.methods.keys()] + _SPACE
        return render('\n'.join(lines))

    def print_help(self, specs):
        if isinstance(specs, ApiInfo):
            print(self.print_api(specs))
        if isinstance(specs, NSInfo):
            print(self.print_namespace(specs))
        if isinstance(specs, CollectionInfo):
            print(self.print_collection(specs))
        if isinstance(specs, ResourceInfo):
            print(self.print_resource(specs))
        if isinstance(specs, ActionInfo):
            print(self.print_action(specs))
        if isinstance(specs, OpInfo):
            print(self.print_operation(specs))
