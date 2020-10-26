from json.decoder import JSONDecodeError
from keyword import iskeyword

import requests

from cnct.client.constants import CONNECT_ENDPOINT_URL, CONNECT_SPECS_URL
from cnct.client.exceptions import ConnectError, HttpError, NotFoundError
from cnct.client.models import Collection, NS
from cnct.client.utils import get_headers
from cnct.help import print_help
from cnct.specs.parser import parse


class ConnectFluent:
    def __init__(
        self,
        api_key,
        endpoint=CONNECT_ENDPOINT_URL,
        specs_location=CONNECT_SPECS_URL,
        default_headers={},
    ):
        self.endpoint = endpoint
        self.api_key = api_key
        self.default_headers = default_headers
        self.specs_location = specs_location
        self.specs = parse(self.specs_location) if self.specs_location else None
        self.response = None

    def __getattr__(self, name):
        if not self.specs:
            raise AttributeError(
                'No specs available. Use `ns` '
                'or `collection` methods instead.'
            )
        if name in self.specs.namespaces:
            return self.ns(name)
        if name in self.specs.collections:
            return self.collection(name)
        raise AttributeError('Unable to resolve {}.'.format(name))

    def __dir__(self):
        if not self.specs:
            return super().__dir__()
        ns = list(self.specs.namespaces.keys())
        cl = list(self.specs.collections.keys())
        additional_names = [
            name for name in cl + ns
            if name.isidentifier() and not iskeyword(name)
        ]
        return sorted(super().__dir__() + additional_names)

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

        return self.execute('put', url, 200, **kwargs)

    def delete(self, url, **kwargs):
        return self.execute('delete', url, 204, **kwargs)

    def execute(self, method, url, expected_status, **kwargs):
        kwargs = kwargs or {}
        if 'headers' in kwargs:
            kwargs['headers'].update(get_headers(self.api_key))
        else:
            kwargs['headers'] = get_headers(self.api_key)

        if self.default_headers:
            kwargs['headers'].update(self.default_headers)

        self.response = requests.request(
            method,
            url,
            **kwargs,
        )

        if self.response.status_code != expected_status:
            try:
                error = self.response.json()
                if 'error_code' in error and 'errors' in error:
                    raise ConnectError(
                        self.response.status_code,
                        error['error_code'],
                        error['errors'],
                    )
            except JSONDecodeError:
                pass

            self._raise_exception()

        if self.response.status_code == 204:
            return

        return self.response.json()

    def help(self):
        print_help(self.specs)
        return self

    def _raise_exception(self):
        message = ''
        if isinstance(self.response.reason, bytes):
            try:
                reason = self.response.reason.decode('utf-8')
            except UnicodeDecodeError:
                reason = self.response.reason.decode('iso-8859-1')
        else:
            reason = self.response.reason

        if 400 <= self.response.status_code < 500:
            message = f'{self.response.status_code} Client Error: {reason}'
        elif 500 <= self.response.status_code < 600:
            message = f'{self.response.status_code} Server Error: {reason}'

        raise HttpError(message, response=self.response)
