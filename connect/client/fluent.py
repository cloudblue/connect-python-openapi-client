#
# This file is part of the Ingram Micro CloudBlue Connect Python OpenAPI Client.
#
# Copyright (c) 2021 Ingram Micro. All Rights Reserved.
#
import threading
from json.decoder import JSONDecodeError

from connect.client.constants import CONNECT_ENDPOINT_URL, CONNECT_SPECS_URL
from connect.client.mixins import AsyncClientMixin, SyncClientMixin
from connect.client.models import AsyncCollection, AsyncNS, Collection, NS
from connect.client.utils import get_headers
from connect.client.help_formatter import DefaultFormatter
from connect.client.openapi import OpenAPISpecs


class _ConnectClientBase(threading.local):

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
        max_retries=0,
        logger=None,
        timeout=(180.0, 180.0),
    ):
        """
        Create a new instance of the ConnectClient.

        :param api_key: The API key used for authentication.
        :type api_key: str
        :param endpoint: The API endpoint, defaults to CONNECT_ENDPOINT_URL
        :type endpoint: str, optional
        :param specs_location: The Connect OpenAPI specification local path or URL, defaults to
                               CONNECT_SPECS_URL
        :type specs_location: str, optional
        :param default_headers: Http headers to apply to each request, defaults to {}
        :type default_headers: dict, optional
        :param logger: HTTPP Request logger class, defaults to None
        :type logger: RequestLogger, optional
        """
        if default_headers and 'Authorization' in default_headers:
            raise ValueError('`default_headers` cannot contains `Authorization`')

        self.endpoint = endpoint or CONNECT_ENDPOINT_URL
        self.api_key = api_key
        self.default_headers = default_headers or {}
        self.default_limit = default_limit
        self.max_retries = max_retries
        self._use_specs = use_specs
        self._validate_using_specs = validate_using_specs
        self.specs_location = specs_location or CONNECT_SPECS_URL
        self.specs = None
        if self._use_specs:
            self.specs = OpenAPISpecs(self.specs_location)
        self.response = None
        self.logger = logger
        self._help_formatter = DefaultFormatter(self.specs)
        self.timeout = timeout

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

        return self._get_namespace_class()(self, name)

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

        return self._get_collection_class()(
            self,
            name,
        )

    def print_help(self, obj):
        print()
        print(self._help_formatter.format(obj))

    def help(self):
        self.print_help(None)
        return self

    def _get_collection_class(self):
        raise NotImplementedError()

    def _get_namespace_class(self):
        raise NotImplementedError()

    def _prepare_call_kwargs(self, kwargs):
        kwargs = kwargs or {}
        if 'headers' in kwargs:
            kwargs['headers'].update(get_headers(self.api_key))
        else:
            kwargs['headers'] = get_headers(self.api_key)
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        if self.default_headers:
            kwargs['headers'].update(self.default_headers)
        return kwargs

    def _get_api_error_details(self):
        if self.response is not None:
            try:
                error = self.response.json()
                if 'error_code' in error and 'errors' in error:
                    return error
            except JSONDecodeError:
                pass


class ConnectClient(_ConnectClientBase, SyncClientMixin):
    def _get_collection_class(self):
        return Collection

    def _get_namespace_class(self):
        return NS


class AsyncConnectClient(_ConnectClientBase, AsyncClientMixin):
    def _get_collection_class(self):
        return AsyncCollection

    def _get_namespace_class(self):
        return AsyncNS
