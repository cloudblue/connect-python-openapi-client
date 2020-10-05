import requests

from cnct.constants import CONNECT_ENDPOINT_URL, CONNECT_SPECS_URL
from cnct.help import print_help
from cnct.specs.parser import parse
from cnct.utils import get_headers


class _Namespace:
    """A namespace groups logically a set of collections."""
    def __init__(self, client, path, specs=None):
        self.client = client
        self.path = path
        self.specs = specs

    def __getattr__(self, name):
        if not self.specs:
            raise AttributeError(
                'No specs available. Use the '
                '`collection` method instead.'
            )
        if name in self.specs.collections:
            return self.collection(name)
        raise AttributeError('Unable to resolve {}.'.format(name))

    def collection(self, name):
        if not self.specs:
            return _Collection(
                self.client,
                f'{self.path}/{name}',
            )
        if name in self.specs.collections:
            return _Collection(
                self.client,
                f'{self.path}/{name}',
                self.specs.collections.get(name),
            )
        raise Exception(f'The collection {name} does not exist.')

    def help(self):
        print_help(self.specs)
        return self


class _Collection:
    """A collection is a set of operation on a particular entity."""
    def __init__(self, client, path, specs=None):
        self.client = client
        self.path = path
        self.specs = specs

    def __getitem__(self, item_id):
        return self.item(item_id)

    def search(self, query=None):
        """Search/list items within the collection."""
        return Search(
            self.client,
            self.path,
            query,
            self.specs.operations.get('search') if self.specs else None,
        )

    def create(self, payload=None, **kwargs):
        """Create a new collection item.""" 
        return self.client.create(
            self.path,
            payload=payload,
            **kwargs,
        )

    def item(self, item_id):
        """Retrieve an item from the collection."""
        return _Item(
            self.client,
            f'{self.path}/{item_id}',
            self.specs.item_specs if self.specs else None,
        )

    def help(self):
        print_help(self.specs)
        return self


class _Item:
    """Represent a generic item."""
    def __init__(self, client, path, specs):
        self.client = client
        self.path = path
        self.specs = specs

    def __getattr__(self, name):
        if not self.specs:
            raise AttributeError(
                'No specs available. Use the `collection` '
                'or `action` methods instead.'
            )
        if name in self.specs.collections and \
            name in self.specs.actions:
                raise AttributeError(
                f'{name} is ambiguous. Use the `collection` '
                'or `action` methods instead.'
            )
        if name in self.specs.collections:
            return self.collection(name)
        if name in self.specs.actions:
            return self.action(name)
        raise AttributeError('Unable to resolve {}.'.format(name))

    def __dir__(self):
        default = sorted(super().__dir__() + list(self.__dict__.keys()))
        if not self.specs:
            return default
        cl = self.specs.collection.keys()
        ac = self.specs.actions.keys()
        return default + list(set(cl) ^ set(ac))

    def collection(self, name):
        """Get a collection of objects related to this item."""
        return _Collection(
            self.client,
            f'{self.path}/{name}',
            self.specs.collections.get(name),
        )

    def action(self, name):
        """Get an action for the current item."""
        return _Action(self.client, f'{self.path}/{name}')

    def help(self):
        print_help(self.specs)
        return self


class _Action:
    def __init__(self, client, path):
        self.client = client
        self.path = path


class Search:
    def __init__(self, client, path, query, specs):
        self.client = client
        self.path = path
        self.query = query or ''
        self.specs = specs
        self.results = None

    def __len__(self):
        if not self.results:
            self._perform()
        # get count from header
        return len(self.results)

    def __iter__(self):
        # Custom iterator to handle pagination
        if not self.results:
            self._perform()
        return iter(self.results)

    def __getitem__(self, key):
        """handle item and slice, return self"""
        pass

    def _perform(self):
        url = f'{self.path}?{self.query}'
        self.results = self.client.get(url)

    def help(self):
        print_help(self.specs)
        return self


class ConnectFluent:
    def __init__(
        self,
        api_key,
        endpoint=CONNECT_ENDPOINT_URL,
        specs_url=CONNECT_SPECS_URL,
    ):
        self.endpoint = endpoint
        self.api_key = api_key
        self.specs_url = specs_url
        self.specs = parse(self.specs_url) if self.specs_url else None
        self.response = None

    def __getattr__(self, name):
        if not self.specs:
            raise AttributeError(
                'No specs available. Use `namespace` '
                'or `collection` methods instead.'
            )
        if name in self.specs.namespaces and \
            name in self.specs.collections:
                raise AttributeError(
                f'{name} is ambiguous. Use `namespace` '
                'or `collection` methods instead.'
            )
        if name in self.specs.namespaces:
            return self.namespace(name)
        if name in self.specs.collections:
            return self.collection(name)
        raise AttributeError('Unable to resolve {}.'.format(name))

    def __dir__(self):
        default = sorted(super().__dir__() + list(self.__dict__.keys()))
        if not self.specs:
            return default
        ns = self.specs.namespaces.keys()
        cl = self.specs.collections.keys()
        return default + list(set(ns) ^ set(cl))

    def namespace(self, name):
        if not self.specs:
            return _Namespace(self, name)
        if name in self.specs.namespaces:
            return _Namespace(self, name, self.specs.namespaces[name])
        raise Exception(f'The namespace {name} does not exist.')

    def collection(self, name):
        if not self.specs:
            return _Collection(
                self, 
                f'{self.endpoint}/{name}',
            )
        if name in self.specs.collections:
            return _Collection(
                self,
                f'{self.endpoint}/{name}',
                self.specs.collections[name],
            )
        raise Exception(f'The collection {name} does not exist.')

    def get(self, url, **kwargs):
        return self._execute('get', url, 200, **kwargs)

    def create(self, url, payload=None, **kwargs):
        kwargs = kwargs or {}

        if payload:
            kwargs['json'] = payload

        return self._execute('post', url, 201, **kwargs)

    def update(self, url, payload=None, **kwargs):
        kwargs = kwargs or {}

        if payload:
            kwargs['json'] = payload

        return self._execute('put', url, 201, **kwargs)

    def delete(self, url):
        return self._execute('delete', url, 204)

    def _execute(self, method, url, expected_status, **kwargs):
        kwargs = kwargs or {}
        kwargs['headers'] = get_headers(self.api_key)
        self.response = requests.request(
            method,
            url,
            **kwargs,
        )

        if self.response.status_code != expected_status:
            self.response.raise_for_status()

        if self.response.status_code == 204:
            return

        return self.response.json()

    def help(self):
        print_help(self.specs)
        return self
