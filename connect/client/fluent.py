#
# This file is part of the Ingram Micro CloudBlue Connect Python OpenAPI Client.
#
# Copyright (c) 2021 Ingram Micro. All Rights Reserved.
#
import contextvars
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
        use_specs=False,
        specs_location=None,
        validate_using_specs=True,
        default_headers=None,
        default_limit=100,
        max_retries=0,
        logger=None,
        timeout=(180.0, 180.0),
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
        self._response = None
        self.logger = logger
        self._help_formatter = DefaultFormatter(self.specs)
        self.timeout = timeout
        self.resourceset_append = resourceset_append

    @property
    def response(self):
        """
        Returns the raw
        [`requests`](https://requests.readthedocs.io/en/latest/api/#requests.Response)
        response.
        """
        return self._response

    @response.setter
    def response(self, value):
        self._response = value

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
        Returns a `Namespace` object identified by its name.

        Usage:

        ```python
        subscriptions = client.ns('subscriptions')
        ```

        Concise form:

        ```python
        subscriptions = client('subscriptions')
        ```

        **Parameters**

        * **name** - The name of the namespace to access.
        """
        if not isinstance(name, str):
            raise TypeError('`name` must be a string.')

        if not name:
            raise ValueError('`name` must not be blank.')

        return self._get_namespace_class()(self, name)

    def collection(self, name):
        """
        Returns a `Collection` object identified by its name.

        Usage:

        ```python
        products = client.collection('products')
        ```

        Concise form:

        ```python
        products = client.products
        ```

        **Parameters**

        * **name** - The name of the collection to access.
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


class ConnectClient(_ConnectClientBase, threading.local, SyncClientMixin):
    """
    Create a new instance of the ConnectClient.

    Usage:

    ```python
    client = ConnectClient('ApiKey SU-000-000-000:xxxxxxxxxxxxxxxx')
    product = client.products['PRD-001-002-003'].get()
    ```

    **Parameters:**

    * **api_key** - The API key used for authentication.
    * **endpoint** *(optional)* - The API endpoint, defaults to
    https://api.connect.cloudblue.com/public/v1.
    * **use_specs**  *(optional)* - Use Connect OpenAPI specifications.
    * **specs_location**  *(optional)* - The Connect OpenAPI specification local path or URL.
    * **validate_using_specs**  *(optional)* - Use the Connect OpenAPI specification to validate
    the call.
    * **default_headers**  *(optional)* - HTTP headers to apply to each request.
    * **default_limit**  *(optional)* - Default value for pagination limit parameter.
    * **max_retries**  *(optional)* - Max number of retries for a request before raising an error.
    * **logger**  *(optional)* - HTTP Request logger class.
    * **timeout**  *(optional)* - Timeout parameter to pass to the underlying HTTP client.
    * **resourceset_append**  *(optional)* - Append all the pages to the current resourceset.
    """
    def _get_collection_class(self):
        return Collection

    def _get_namespace_class(self):
        return NS


class AsyncConnectClient(_ConnectClientBase, AsyncClientMixin):
    """
    Create a new instance of the AsyncConnectClient.

    Usage:

    ```python
    client = AsyncConnectClient('ApiKey SU-000-000-000:xxxxxxxxxxxxxxxx')
    product = await client.products['PRD-001-002-003'].get()
    ```

    **Parameters:**

    * **api_key** - The API key used for authentication.
    * **endpoint** *(optional)* - The API endpoint, defaults to
    https://api.connect.cloudblue.com/public/v1.
    * **use_specs**  *(optional)* - Use Connect OpenAPI specifications.
    * **specs_location**  *(optional)* - The Connect OpenAPI specification local path or URL.
    * **validate_using_specs**  *(optional)* - Use the Connect OpenAPI specification to validate
    the call.
    * **default_headers**  *(optional)* - HTTP headers to apply to each request.
    * **default_limit**  *(optional)* - Default value for pagination limit parameter.
    * **max_retries**  *(optional)* - Max number of retries for a request before raising an error.
    * **logger**  *(optional)* - HTTP Request logger class.
    * **timeout**  *(optional)* - Timeout parameter to pass to the underlying HTTP client.
    * **resourceset_append**  *(optional)* - Append all the pages to the current resourceset.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._response = contextvars.ContextVar('response', default=None)

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
