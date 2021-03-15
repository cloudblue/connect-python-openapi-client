import inflect

from cmr import render

from connect.client.models import Action, Collection, NS, Resource, ResourceSet


_COL_HTTP_METHOD_TO_METHOD = {
    'get': '.all(), .filter(), .first(), .last()',
    'post': '.create()',
}


class DefaultFormatter:

    def __init__(self, specs):
        self._specs = specs
        self._p = inflect.engine()

    def format_client(self):
        lines = [
            f'# Welcome to {self._specs.title} {self._specs.version}',
            '## Introduction',
        ] + self._specs.description.splitlines()

        lines += [
            '',
            '## Namespaces',
        ]
        for ns in self._specs.get_namespaces():
            lines.append(f'* {ns}')

        lines += [
            '',
            '## Collections',
        ]
        for col in self._specs.get_collections():
            lines.append(f'* {col}')

        return render('\n'.join(lines))

    def format_ns(self, ns):
        namespaces = self._specs.get_nested_namespaces(ns.path)
        collections = self._specs.get_namespaced_collections(ns.path)

        if not (collections or namespaces):
            return render(f'~~{ns.path}~~ **does not exists.**')

        lines = [
            f'# {ns.path.title()} namespace',
            f'**path: /{ns.path}**',
        ]
        if namespaces:
            lines.append('## Available namespaces')
            for namespace in namespaces:
                lines.append(f'* {namespace}')

        if collections:
            lines.append('## Available collections')
            for collection in collections:
                lines.append(f'* {collection}')

        return render('\n'.join(lines))

    def format_collection(self, collection):
        col_info = self._specs.get_collection(collection.path)
        if not col_info:
            return render(f'~~{collection.path}~~ **does not exists.**')

        if '/' in collection.path:
            _, collection_name = collection.path.rsplit('/', 1)
        else:
            collection_name = collection.path

        lines = [
            f'# {collection_name.title()} collection',
            f'**path: /{collection.path}**',
        ]

        lines.extend(self._format_heading(col_info))
        lines.append('### Available operations')
        if 'get' in col_info:
            lines.append(f'* GET: {_COL_HTTP_METHOD_TO_METHOD["get"]}')

        if 'post' in col_info:
            lines.append(f'* POST: {_COL_HTTP_METHOD_TO_METHOD["post"]}')

        return render('\n'.join(lines))

    def format_resource(self, resource):
        res_info = self._specs.get_resource(resource.path)
        if not res_info:
            return render(f'~~{resource.path}~~ **does not exists.**')

        resource_name = resource.path.split('/')[-2]
        resource_name = self._p.singular_noun(resource_name)
        lines = [
            f'# {resource_name.title()} resource',
            f'**path: /{resource.path}**',
        ]

        lines.extend(self._format_heading(res_info))

        actions = self._specs.get_actions(resource.path)
        if actions:
            lines.append('### Available actions')
            for name, summary in actions:
                if summary:
                    lines.append(f'* {name} - {summary}')
                else:
                    lines.append(f'* {name}')
            lines.append('')

        nested = self._specs.get_nested_collections(resource.path)
        if nested:
            lines.append('### Available nested collections')
            for name, summary in nested:
                if summary:
                    lines.append(f'* {name} - {summary}')
                else:
                    lines.append(f'* {name}')

        return render('\n'.join(lines))

    def format_action(self, action):
        action_info = self._specs.get_action(action.path)
        if not action_info:
            return render(f'~~{action.path}~~ **does not exists.**')

        _, action_name = action.path.rsplit('/', 1)

        lines = [
            f'# {action_name.title()} action',
            f'**path: /{action.path}**',
        ]
        lines.extend(self._format_heading(action_info))
        lines.append('## Available methods')
        for method in ('get', 'post', 'put', 'delete'):
            if method in action_info:
                lines.append(f'* {method.upper()}: .{method}()')

        return render('\n'.join(lines))

    def format_resource_set(self, rs):
        col_info = self._specs.get_collection(rs.path)
        if not col_info:
            return render(f'~~{rs.path}~~ **does not exists.**')

        if '/' in rs.path:
            _, collection_name = rs.path.rsplit('/', 1)
        else:
            collection_name = rs.path

        lines = [
            f'# Search the {collection_name.title()} collection',
            f'**path: /{rs.path}**',
        ]
        lines.extend(self._format_heading(col_info))
        get_info = col_info['get']
        params = get_info.get('parameters')
        if not params:
            return render('\n'.join(lines))
        filters = list(sorted(filter(lambda x: '$ref' not in x, params), key=lambda x: x['name']))
        lines.append(f'Support pagination: *{len(params) > len(filters)}*')
        if not filters:
            return render('\n'.join(lines))

        lines.append('## Available filters')
        for filter_ in filters:
            lines.append(f'*{filter_["name"]}*')
            description = filter_['description'].splitlines()
            for line in description:
                line = line.strip()
                if line:
                    lines.append(f'   {line}')
            lines.append('')

        return render('\n'.join(lines))

    def format(self, obj):
        if not self._specs:
            return render('**No OpenAPI specs available.**')

        if isinstance(obj, NS):
            return self.format_ns(obj)

        if isinstance(obj, Collection):
            return self.format_collection(obj)

        if isinstance(obj, Resource):
            return self.format_resource(obj)

        if isinstance(obj, Action):
            return self.format_action(obj)

        if isinstance(obj, ResourceSet):
            return self.format_resource_set(obj)

        return self.format_client()

    def _format_heading(self, info):
        lines = []
        for section in ('summary', 'description'):
            if section in info:
                lines.append(f'### {section.title()}')
                lines.append(info[section])
        return lines
