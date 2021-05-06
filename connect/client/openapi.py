#
# This file is part of the Ingram Micro CloudBlue Connect Python OpenAPI Client.
#
# Copyright (c) 2021 Ingram Micro. All Rights Reserved.
#
from io import StringIO
from functools import partial

import requests

import yaml


class OpenAPISpecs:

    def __init__(self, location):
        self._location = location
        self._specs = self._load()

    @property
    def title(self):
        return self._specs['info']['title'] if self._specs else None

    @property
    def description(self):
        return self._specs['info']['description'] if self._specs else None

    @property
    def version(self):
        return self._specs['info']['version'] if self._specs else None

    @property
    def tags(self):
        return self._specs.get('tags') if self._specs else None

    def exists(self, method, path):
        p = self._get_path(path)
        if not p:
            return False
        info = self._specs['paths'][p]
        return method.lower() in info

    def get_namespaces(self):
        def _is_namespace(path):
            comp = path[1:].split('/', 1)
            return len(comp) > 1 and not comp[1].startswith('{')
        return sorted(
            list(
                {
                    p[1:].split('/', 1)[0]
                    for p in filter(_is_namespace, self._specs['paths'].keys())
                },
            ),
        )

    def get_collections(self):
        namespaces = self.get_namespaces()
        cols = set()
        for p in self._specs['paths'].keys():
            name = p[1:].split('/', 1)[0]
            if name not in namespaces:
                cols.add(name)

        return sorted(cols)

    def get_namespaced_collections(self, path):
        nested = filter(lambda x: x[1:].startswith(path), self._specs['paths'].keys())
        collections = set()
        for p in nested:
            splitted = p[len(path) + 1:].split('/', 2)
            if self._is_collection(p) and len(splitted) == 2:
                collections.add(splitted[1])
        return list(sorted(collections))

    def get_collection(self, path):
        return self._get_info(path)

    def get_resource(self, path):
        return self._get_info(path)

    def get_action(self, path):
        return self._get_info(path)

    def get_actions(self, path):
        p = self._get_path(path)
        nested = filter(
            lambda x: x.startswith(p) and x != p,
            self._specs['paths'].keys(),
        )

        actions = set()
        descriptions = {}
        for np in nested:
            name = np[len(p) + 1:]
            actions.add(name)
            info = self._specs['paths'][np]
            summary = info['summary'] if 'summary' in info else ''
            if summary:
                descriptions[name] = summary
        return [
            (name, descriptions.get(name))
            for name in sorted(actions)
        ]

    def get_nested_namespaces(self, path):
        def _is_nested_namespace(base_path, path):
            if path[1:].startswith(base_path):
                comp = path[1:].split('/')
                return (
                    len(comp) > 1
                    and not comp[-1].startswith('{')
                )
            return False

        nested = filter(
            partial(_is_nested_namespace, path),
            self._specs['paths'].keys(),
        )
        current_level = len(path[1:].split('/'))
        nested_namespaces = []
        for ns in nested:
            name = ns[1:].split('/')[current_level]
            if not self._is_collection(f'/{path}/{name}'):
                nested_namespaces.append(name)
        return nested_namespaces

    def get_nested_collections(self, path):
        p = self._get_path(path)
        nested = filter(
            lambda x: x.startswith(p[0:p.rindex('{')]) and x != p,
            self._specs['paths'].keys(),
        )
        cut_pos = p.count('/')
        collections = set()
        descriptions = {}
        for np in nested:
            splitted = np[1:].split('/')
            name = splitted[cut_pos]
            info = self._specs['paths'][np]
            method_info = info['get'] if 'get' in info else info['post']
            operation_id = method_info['operationId']
            if self._is_action(operation_id):
                continue
            collections.add(name)
            summary = info['summary'] if 'summary' in info else ''
            if summary:
                descriptions[name] = summary
        return [
            (name, descriptions.get(name))
            for name in sorted(collections)
        ]

    def _load(self):
        if self._location.startswith('http'):
            return self._load_from_url()
        return self._load_from_fs()

    def _load_from_url(self):
        res = requests.get(self._location, stream=True)
        if res.status_code == 200:
            result = StringIO()
            for chunk in res.iter_content(chunk_size=8192):
                result.write(str(chunk, encoding='utf-8'))
            result.seek(0)
            return yaml.safe_load(result)
        res.raise_for_status()

    def _load_from_fs(self):
        with open(self._location, 'r') as f:
            return yaml.safe_load(f)

    def _get_path(self, path):
        if '?' in path:
            path, _ = path.split('?', 1)
        components = path.split('/')
        for p in self._specs['paths'].keys():
            cmps = p[1:].split('/')
            if len(cmps) != len(components):
                continue
            for idx, comp in enumerate(components):
                if cmps[idx].startswith('{'):
                    continue
                if cmps[idx] != comp:
                    break
            else:
                return p

    def _get_info(self, path):
        p = self._get_path(path)
        return self._specs['paths'][p] if p else None

    def _is_action(self, operation_id):
        op_id_cmps = operation_id.rsplit('_', 2)
        return op_id_cmps[-2] not in ('list', 'retrieve')

    def _is_collection(self, path):
        path_length = len(path[1:].split('/'))
        for p in self._specs['paths'].keys():
            comp = p[1:].split('/')
            if not p.startswith(path):
                continue
            if p == path:
                return True
            if len(comp) > path_length and comp[path_length].startswith('{'):
                return True
        return False
