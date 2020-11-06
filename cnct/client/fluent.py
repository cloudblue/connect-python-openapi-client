from json.decoder import JSONDecodeError

import requests
from requests.exceptions import RequestException

from cnct.client.constants import CONNECT_ENDPOINT_URL, CONNECT_SPECS_URL
from cnct.client.exceptions import ClientError
from cnct.client.models import Collection, NS
from cnct.client.utils import get_headers
from cnct.client.help_formatter import DefaultFormatter
from cnct.client.openapi import OpenAPISpecs


class ConnectClient:
    """
    Connect ReST API client.
    """
    def __init__(
        self,
        api_key,
        endpoint=None,
        use_specs=True,
        specs_location=None,
        validate_using_specs=True,
        default_headers=None,
        default_limit=100,
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

        self.endpoint = endpoint or CONNECT_ENDPOINT_URL
        self.api_key = api_key
        self.default_headers = default_headers or {}
        self._use_specs = use_specs
        self._validate_using_specs = validate_using_specs
        self.specs_location = specs_location or CONNECT_SPECS_URL
        self.specs = None
        if self._use_specs:
            self.specs = OpenAPISpecs(self.specs_location)
        self.response = None
        self._help_formatter = DefaultFormatter(self.specs)

    def __getattr__(self, name):
        """
        Returns a collection object called ``name``.

        :param name: The name of the collection to retrieve.
        :type name: str
        :return: a collection called ``name``.
        :rtype: Collection
        """
        if '_' in name:
            name = name.replace('_', '-')
        return self.collection(name)

    def __call__(self, name):
        return self.ns(name)

    def ns(self, name):
        """
        Returns the namespace called ``name``.

        :param name: The name of the namespace to access.
        :type name: str
        :return: The namespace called ``name``.
        :rtype: NS
        """
        if not isinstance(name, str):
            raise TypeError('`name` must be a string.')

        if not name:
            raise ValueError('`name` must not be blank.')

        return NS(self, name)

    def collection(self, name):
        """
        Returns the collection called ``name``.

        :param name: The name of the collection to access.
        :type name: str
        :return: The collection called ``name``.
        :rtype: Collection
        """
        if not isinstance(name, str):
            raise TypeError('`name` must be a string.')

        if not name:
            raise ValueError('`name` must not be blank.')

        return Collection(
            self,
            name,
        )

    def get(self, url, **kwargs):
        return self.execute('get', url, **kwargs)

    def create(self, url, payload=None, **kwargs):
        kwargs = kwargs or {}

        if payload:
            kwargs['json'] = payload

        return self.execute('post', url, **kwargs)

    def update(self, url, payload=None, **kwargs):
        kwargs = kwargs or {}

        if payload:
            kwargs['json'] = payload

        return self.execute('put', url, **kwargs)

    def delete(self, url, **kwargs):
        return self.execute('delete', url, **kwargs)

    def execute(self, method, path, **kwargs):
        if (
            self._use_specs
            and self._validate_using_specs
            and not self.specs.exists(method, path)
        ):
            # TODO more info, specs version, method etc
            raise ClientError(f'The path `{path}` does not exist.')

        url = f'{self.endpoint}/{path}'

        kwargs = kwargs or {}
        if 'headers' in kwargs:
            kwargs['headers'].update(get_headers(self.api_key))
        else:
            kwargs['headers'] = get_headers(self.api_key)

        if self.default_headers:
            kwargs['headers'].update(self.default_headers)

        self.response = None

        try:
            self._execute_http_call(method, url, kwargs)
            if self.response.status_code == 204:
                return None
            if self.response.headers['Content-Type'] == 'application/json':
                return self.response.json()
            else:
                return self.response.content

        except RequestException as re:
            api_error = self._get_api_error_details() or {}
            status_code = self.response.status_code if self.response is not None else None
            raise ClientError(status_code=status_code, **api_error) from re

    def print_help(self, obj):
        print()
        print(self._help_formatter.format(obj))

    def help(self):
        self.print_help(None)
        return self

    def _execute_http_call(self, method, url, kwargs):
        self.response = requests.request(method, url, **kwargs)
        if self.response.status_code >= 400:
            self.response.raise_for_status()

    def _get_api_error_details(self):
        if self.response is not None:
            try:
                error = self.response.json()
                if 'error_code' in error and 'errors' in error:
                    return error
            except JSONDecodeError:
                pass
