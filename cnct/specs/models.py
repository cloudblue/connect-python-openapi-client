class ApiInfo:
    def __init__(self, title, description, version, tags):
        self.title = title
        self.description = description
        self.version = version
        self.tags = {t['name']: t['description'] for t in tags}
        self.namespaces = {}
        self.collections = {}

    def set_namespace(self, ns_name, tag):
        return self.namespaces.setdefault(ns_name, NSInfo(ns_name, tag))

    def set_collection(self, col_name, summary, description, tag):
        return self.collections.setdefault(col_name, CollectionInfo(col_name, summary, description, tag))


class OpInfo:
    def __init__(self, name, collection_name, path, method, info):
        self.path = path
        self.name = name
        self.collection_name = collection_name
        self.method = method
        self.info = info


class NSInfo:
    def __init__(self, name, tag):
        self.name = name
        self.tag = tag
        self.collections = {}

    def set_collection(self, name, summary, description, tag):
        return self.collections.setdefault(name, CollectionInfo(name, summary, description, tag))


class ActionInfo:
    def __init__(self, name, summary, description):
        self.name = name
        self.summary = summary
        self.description = description
        self.methods = {}

    def add_info(self, info):
        if info:
            self.methods[info.method] = info


class ResourceInfo:
    def __init__(self, summary='', description=''):
        self.summary = summary
        self.description = description
        self.actions = {}
        self.collections = {}

    def set_action(self, name, summary, description, info):
        action = self.actions.setdefault(name, ActionInfo(name, summary, description))
        action.add_info(info)
        return action

    def set_collection(self, name, summary, description):
        return self.collections.setdefault(name, CollectionInfo(name, summary, description))


class CollectionInfo:
    def __init__(self, name, summary, description, tag=None):
        self.name = name
        self.summary = summary
        self.description = description
        self.tag = tag
        self.operations = {}
        self.resource_specs = ResourceInfo()
