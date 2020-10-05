class ApiInfo:
    def __init__(self, title, description, version):
        self.title = title
        self.description = description
        self.version = version
        self.tags = None
        self.components = None
        self.namespaces = {}
        self.collections = {}

    def set_namespace(self, ns_name):
        return self.namespaces.setdefault(ns_name, NSInfo(ns_name))

    def set_collection(self, col_name):
        return self.collections.setdefault(col_name, CollectionInfo(col_name))



class OpInfo:
    def __init__(self, name, collection_name, path, method, info):
        self.path = path
        self.name = name
        self.collection_name = collection_name
        self.path = path
        self.method = method
        self.info = info

class NSInfo:
    def __init__(self, name):
        self.name = name
        self.collections = {}

    def set_collection(self, name):
        return self.collections.setdefault(name, CollectionInfo(name))


class ItemInfo:
    def __init__(self):
        self.actions = {}
        self.collections = {}
        self._help = None


    def set_action(self, method, name, info):
        self.actions[f'{method}_{name}'] = info

    def set_collection(self, name):
        return self.collections.setdefault(name, CollectionInfo(name))



class CollectionInfo:
    def __init__(self, name):
        self.name = name
        self.operations = {}
        self.item_specs = ItemInfo()
