from json.decoder import JSONDecodeError
from keyword import iskeyword

import requests

from cnct.client.constants import CONNECT_ENDPOINT_URL, CONNECT_SPECS_URL
from cnct.client.exceptions import APIError, HttpError, NotFoundError
from cnct.client.models import Collection, NS
from cnct.client.utils import get_headers
from cnct.help import DefaultFormatter
from cnct.specs.parser import parse


class ConnectClient:
    """
    Connect ReST API client.
    """
    def __init__(
        self,
        api_key,
        endpoint=CONNECT_ENDPOINT_URL,
        specs_location=CONNECT_SPECS_URL,
        default_headers={},
        default_limit=100,
        help_formatter=DefaultFormatter(),
    ):
        """
        Create a new instance of the ConnectClient.

        :param api_key: The API key used for authentication.
        :type api_key: str
        :param endpoint: The API endpoint, defaults to CONNECT_ENDPOINT_URL
        :type endpoint: str, optional
        :param specs_location: The Connect OpenAPI specification local path or URL, defaults to CONNECT_SPECS_URL
        :type specs_location: str, optional
        :param default_headers: Http headers to apply to each request, defaults to {}
        :type default_headers: dict, optional
        """
        if default_headers and 'Authorization' in default_headers:
            raise ValueError('`default_headers` cannot contains `Authorization`')

        self.endpoint = endpoint
        self.api_key = api_key
        self.default_headers = default_headers
        self.specs_location = specs_location
        self.specs = parse(self.specs_location) if self.specs_location else None
        self.response = None
        self._help_formatter = help_formatter

    def __getattr__(self, name):
        """
        Returns a NS or a Collection object called ``name``.

        :param name: The name of the NS or Collection to retrieve.
        :type name: str
        :raises AttributeError: If OpenAPI specs are not avaliable.
        :raises AttributeError: If the name does not exist.
        :return: a Collection or a NS called ``name``.
        :rtype: Collection, NS
        """
        if not self.specs:
            raise AttributeError(
                'No specs available. Use `ns` '
                'or `collection` methods instead.'
            )
        if '_' in name:
            name = name.replace('_', '-')
        if name in self.specs.namespaces:
            return self.ns(name)
        if name in self.specs.collections:
            return self.collection(name)
        raise AttributeError('Unable to resolve {}.'.format(name))

    def __dir__(self):
        """
        Return a list of attributes defined for this ConnectClient instance.
        The returned list includes the names of the root namespaces and collections.

        :return: List of attributes.
        :rtype: list
        """
        if not self.specs:
            return super().__dir__()
        ns = list(self.specs.namespaces.keys())
        cl = list(self.specs.collections.keys())
        additional_names = []
        for name in cl + ns:
            if '-' in name:
                name = name.replace('-', '_')
            if name.isidentifier() and not iskeyword(name):
                additional_names.append(name)
        return sorted(super().__dir__() + additional_names)

    def ns(self, name):
        """
        Returns the namespace called ``name``.

        :param name: The name of the namespace to access.
        :type name: str
        :raises NotFoundError: If a namespace with name ``name`` does not exist.
        :return: The namespace called ``name``.
        :rtype: NS
        """
        if not isinstance(name, str):
            raise TypeError('`name` must be a string.')

        if not name:
            raise ValueError('`name` must not be blank.')

        if not self.specs:
            return NS(self, f'{self.endpoint}/{name}',)
        if name in self.specs.namespaces:
            return NS(self, f'{self.endpoint}/{name}', self.specs.namespaces[name])
        raise NotFoundError(f'The namespace {name} does not exist.')

    def collection(self, name):
        """
        Returns the collection called ``name``.

        :param name: The name of the collection to access.
        :type name: str
        :raises NotFoundError: If a collection with name ``name`` does not exist.
        :return: The collection called ``name``.
        :rtype: Collection
        """
        if not isinstance(name, str):
            raise TypeError('`name` must be a string.')

        if not name:
            raise ValueError('`name` must not be blank.')

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
                    raise APIError(
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
        self._help_formatter.print_help(self.specs)
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
