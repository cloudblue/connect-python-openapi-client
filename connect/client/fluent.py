#
# This file is part of the Ingram Micro CloudBlue Connect Python OpenAPI Client.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
import contextvars
import threading
from functools import cache
from json.decoder import JSONDecodeError
from typing import Union

import httpx
import requests
from httpx._config import Proxy
from httpx._utils import get_environment_proxies
from requests.adapters import HTTPAdapter

from connect.client.constants import CONNECT_ENDPOINT_URL, CONNECT_SPECS_URL
from connect.client.help_formatter import DefaultFormatter
from connect.client.mixins import AsyncClientMixin, SyncClientMixin
from connect.client.models import (
    NS,
    AsyncCollection,
    AsyncNS,
    Collection,
)
from connect.client.openapi import OpenAPISpecs
from connect.client.utils import get_headers


_SYNC_TRANSPORTS = {}
_ASYNC_TRANSPORTS = {}


class _ConnectClientBase:
    def __init__(
        self,
        api_key,
        endpoint=None,
        use_specs=False,
        specs_location=None,
        validate_using_specs=True,
        default_headers=None,
        default_limit=100,
        max_retries=3,
        logger=None,
        timeout=(15.0, 180.0),
        resourceset_append=True,
    ):
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
        self.logger = logger
        self._help_formatter = DefaultFormatter(self.specs)
        self.timeout = timeout
        self.resourceset_append = resourceset_append

    def __getattr__(self, name):
        if name in ('session', 'response'):
            return self.__getattribute__(name)
        if '_' in name:
            name = name.replace('_', '-')
        return self.collection(name)

    def __call__(self, name):
        return self.ns(name)

    def ns(self, name: str) -> Union[NS, AsyncNS]:
        """
        Returns a `Namespace` object identified by its name.

        Usage:

        ```py3
        subscriptions = client.ns('subscriptions')
        ```

        Concise form:

        ```py3
        subscriptions = client('subscriptions')
        ```

        Args:
            name (str): The name of the namespace to access.
        """
        if not isinstance(name, str):
            raise TypeError('`name` must be a string.')

        if not name:
            raise ValueError('`name` must not be blank.')

        return self._get_namespace_class()(self, name)

    def collection(self, name: str) -> Union[Collection, AsyncCollection]:
        """
        Returns a `Collection` object identified by its name.

        Usage:

        ```py3
        products = client.collection('products')
        ```

        Concise form:

        ```py3
        products = client.products
        ```

        Args:
            name (str): The name of the collection to access.
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
    """
    Create a new instance of the ConnectClient.

    Usage:

    ```py3
    from connect.client import ConnectClient
    client = ConnectClient('ApiKey SU-000-000-000:xxxxxxxxxxxxxxxx')
    product = client.products['PRD-001-002-003'].get()
    ```

    Args:
        api_key (str): The API key used for authentication.
        endpoint (str): (Optional) The API endpoint, defaults to
            https://api.connect.cloudblue.com/public/v1.
        use_specs (bool): (Optional) Use Connect OpenAPI specifications.
        specs_location (str): (Optional) The Connect OpenAPI specification local path or URL.
        validate_using_specs (bool): (Optional) Use the Connect OpenAPI specification to validate
            the call.
        default_headers (dict): (Optional) HTTP headers to apply to each request.
        default_limit (int): (Optional) Default value for pagination limit parameter.
        max_retries (int): (Optional) Max number of retries for a request before raising an error.
        logger: (Optional) HTTP Request logger class.
        timeout (int): (Optional) Timeout parameter to pass to the underlying HTTP client.
        resourceset_append: (Optional) Append all the pages to the current resourceset.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._thread_locals = threading.local()

    @property
    def session(self):
        if not hasattr(self._thread_locals, 'session'):
            self._thread_locals.session = requests.Session()
            self._thread_locals.session.mount(
                self.endpoint,
                _SYNC_TRANSPORTS.setdefault(
                    self.endpoint,
                    HTTPAdapter(),
                ),
            )

        return self._thread_locals.session

    @property
    def response(self) -> requests.Response:
        """
        Returns the raw
        [`requests`](https://requests.readthedocs.io/en/latest/api/#requests.Response)
        response.
        """
        if not hasattr(self._thread_locals, 'response'):
            self._thread_locals.response = None
        return self._thread_locals.response

    @response.setter
    def response(self, value: requests.Response):
        self._thread_locals.response = value

    def _get_collection_class(self):
        return Collection

    def _get_namespace_class(self):
        return NS


_SSL_CONTEXT = httpx.create_ssl_context()


@cache
def _get_async_mounts():
    """
    This code based on how httpx.Client mounts proxies from environment.
    This is cached to allow reusing the created transport objects.
    """
    return {
        key: None
        if url is None
        else httpx.AsyncHTTPTransport(verify=_SSL_CONTEXT, proxy=Proxy(url=url))
        for key, url in get_environment_proxies().items()
    }


class AsyncConnectClient(_ConnectClientBase, AsyncClientMixin):
    """
    Create a new instance of the AsyncConnectClient.

    Usage:

    ```py3
    from connect.client import AsyncConnectClient
    client = AsyncConnectClient('ApiKey SU-000-000-000:xxxxxxxxxxxxxxxx')
    product = await client.products['PRD-001-002-003'].get()
    ```

    Args:
        api_key (str): The API key used for authentication.
        endpoint (str): (Optional) The API endpoint, defaults to
            https://api.connect.cloudblue.com/public/v1.
        use_specs (bool): (Optional) Use Connect OpenAPI specifications.
        specs_location: (Optional) The Connect OpenAPI specification local path or URL.
        validate_using_specs: (Optional) Use the Connect OpenAPI specification to validate
            the call.
        default_headers (dict): (Optional) HTTP headers to apply to each request.
        default_limit (int): (Optional) Default value for pagination limit parameter.
        max_retries (int): (Optional) Max number of retries for a request before raising an error.
        logger: (Optional) HTTP Request logger class.
        timeout (int): (Optional) Timeout parameter to pass to the underlying HTTP client.
        resourceset_append: (Optional) Append all the pages to the current resourceset.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._response = contextvars.ContextVar('response', default=None)
        self._session = contextvars.ContextVar('session', default=None)

    @property
    def session(self):
        value = self._session.get()
        if not value:
            transport = _ASYNC_TRANSPORTS.get(self.endpoint)
            if not transport:
                transport = _ASYNC_TRANSPORTS[self.endpoint] = httpx.AsyncHTTPTransport(
                    verify=_SSL_CONTEXT,
                )
            # When passing a transport to httpx a Client/AsyncClient, proxies defined in environment
            # (like HTTP_PROXY) are ignored, so let's pass them using mounts parameter.
            value = httpx.AsyncClient(transport=transport, mounts=_get_async_mounts())
            self._session.set(value)
        return value

    @property
    def response(self):
        """
        Returns the raw
        [`httpx`](https://www.python-httpx.org/api/#response)
        response.
        """
        return self._response.get()

    @response.setter
    def response(self, value):
        self._response.set(value)

    def _get_collection_class(self):
        return AsyncCollection

    def _get_namespace_class(self):
        return AsyncNS
