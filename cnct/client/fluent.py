from keyword import iskeyword

import requests

from cnct.client.constants import CONNECT_ENDPOINT_URL, CONNECT_SPECS_URL
from cnct.client.exceptions import NotFoundError
from cnct.client.models import Collection, NS
from cnct.client.utils import get_headers
from cnct.help import print_help
from cnct.specs.parser import parse


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
                'No specs available. Use `ns` '
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
        return default + [
            name for name in list(set(cl) ^ set(ns))
            if name.isidentifier() and not iskeyword(name)
        ]

    def ns(self, name):
        if not self.specs:
            return NS(self, name)
        if name in self.specs.namespaces:
            return NS(self, name, self.specs.namespaces[name])
        raise NotFoundError(f'The namespace {name} does not exist.')

    def collection(self, name):
        if not self.specs:
            return Collection(
                self,
                f'{self.endpoint}/{name}',
            )
        if name in self.specs.collections:
            return Collection(
                self,
                f'{self.endpoint}/{name}',
                self.specs.collections[name],
            )
        raise NotFoundError(f'The collection {name} does not exist.')

    def get(self, url, **kwargs):
        return self.execute('get', url, 200, **kwargs)

    def create(self, url, payload=None, **kwargs):
        kwargs = kwargs or {}

        if payload:
            kwargs['json'] = payload

        return self.execute('post', url, 201, **kwargs)

    def update(self, url, payload=None, **kwargs):
        kwargs = kwargs or {}

        if payload:
            kwargs['json'] = payload

        return self.execute('put', url, 201, **kwargs)

    def delete(self, url):
        return self.execute('delete', url, 204)

    def execute(self, method, url, expected_status, **kwargs):
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
