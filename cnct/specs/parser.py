import logging

from io import StringIO

import requests
import yaml

from cnct.specs.models import ApiInfo, OpInfo


logger = logging.getLogger('connect-fluent')


def _get_operation_type(operation_id):
    _, token = operation_id.rsplit('_', 1)
    if token.startswith('list'):
        return 'search'
    elif token.startswith('retrieve'):
        return 'get'
    elif token.startswith('update'):
        return 'update'
    elif token.startswith('destroy'):
        return 'delete'
    return 'create'


def _get_action_name(operation_id):
    op_id_cmps = operation_id.rsplit('_', 2)
    return op_id_cmps[-2]


def _is_variable(component):
    return component[0] == '{' and component[-1] == '}'


def _load(url):
    res = requests.get(url, stream=True)
    if res.status_code == 200:
        result = StringIO()
        for chunk in res.iter_content(chunk_size=8192):
            result.write(str(chunk, encoding='utf-8'))
        result.seek(0)
        return yaml.safe_load(result)
    res.raise_for_status()


def parse(url):
    if url.startswith('http'):
        specs = _load(url)
    else:
        specs = yaml.safe_load(open(url, 'r'))

    apihelp = ApiInfo(
        specs['info']['title'],
        specs['info']['description'],
        specs['info']['version'],
        specs['tags'],
    )
    paths = sorted(specs['paths'].keys(), key=len)
    for path in paths:
        summary = specs['paths'][path].get('summary', '')
        description = specs['paths'][path].get('description', '')
        for method, opinfo in specs['paths'][path].items():
            if method in ('summary', 'description'):
                continue
            operation_id = opinfo['operationId']
            tag = opinfo['tags'][0] if 'tags' in opinfo and opinfo['tags'] else None
            components = path[1:].split('/')
            # check if the first component is a namespace or a collection
            ns_name = None
            if len(components) > 1 and not _is_variable(components[1]):
                # namespace found: get name and right-shift components
                ns_name = components[0] if not _is_variable(components[1]) else None
                components = components[1:]

            logger.debug('path components %s', components)

            collection_name = components[0]
            if ns_name:
                # collection in under a namespace
                logger.debug('namespace -> %s', ns_name)
                ns = apihelp.set_namespace(ns_name, tag)
                collection = ns.set_collection(collection_name, summary, description, tag)
            else:
                # collection is a root collection
                collection = apihelp.set_collection(collection_name, summary, description, tag)

            components = components[1:]
            if not components:
                # List operation
                logger.debug('root collection list operation')
                op_type = _get_operation_type(operation_id)
                collection.operations[op_type] = OpInfo(
                    op_type,
                    collection.name,
                    path,
                    method,
                    opinfo,
                )
                continue
            last_idx = len(components) - 1
            for idx, comp in enumerate(components):
                if _is_variable(comp) and idx < last_idx:
                    # {id}/<name>
                    logger.debug('skip variable -> %s', comp)
                    continue
                if idx < last_idx:
                    # <name>/.... (not an action since not latest token)
                    logger.debug('subcollection retrieve/update/delete operation')
                    collection = collection.resource_specs.set_collection(comp, summary, description)
                    continue
                if _is_variable(comp):
                    # <name>/{id}
                    op_type = _get_operation_type(operation_id)
                    collection.resource_specs.summary = summary
                    collection.resource_specs.description = description
                    collection.operations[op_type] = OpInfo(
                        op_type,
                        collection.name,
                        path,
                        method,
                        opinfo,
                    )
                    continue
                action_name = _get_action_name(operation_id)
                if action_name in ('list', 'detail'):
                    collection = collection.resource_specs.set_collection(comp, summary, description)
                    op_type = _get_operation_type(operation_id)
                    collection.operations[op_type] = OpInfo(
                        op_type,
                        collection.name,
                        path,
                        method,
                        opinfo,
                    )
                    continue
                else:
                    collection.resource_specs.set_action(
                        action_name,
                        summary,
                        description,
                        OpInfo(
                            action_name,
                            collection.name,
                            path,
                            method,
                            opinfo,
                        ),
                    )

    return apihelp
