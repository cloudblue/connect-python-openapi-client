#
# This file is part of the Ingram Micro CloudBlue Connect Python OpenAPI Client.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
import copy

from connect.client.models.exceptions import NotYetEvaluatedError
from connect.client.models.iterators import (
    AsyncResourceIterator,
    AsyncValuesListIterator,
    ResourceIterator,
    ValuesListIterator,
    aiter,
)
from connect.client.rql import R
from connect.client.utils import parse_content_range, resolve_attribute


class _ResourceSetBase:
    def __init__(
        self,
        client,
        path,
        query=None,
    ):
        self._client = client
        self._path = path
        self._query = query or R()
        self._results = None
        self._limit = self._client.default_limit or 100
        self._offset = 0
        self._slice = None
        self._content_range = None
        self._fields = None
        self._search = None
        self._select = []
        self._ordering = []
        self._config = {}

    @property
    def path(self):
        return self._path

    @property
    def query(self):
        return self._query

    @property
    def content_range(self):
        return self._content_range

    def configure(self, **kwargs):
        """
        Set the default keyword arguments that must be provided to the
        underlying GET call on each page fetch.
        """
        copy = self._copy()
        copy._config = kwargs or {}
        return copy

    def limit(self, limit: int):
        """
        Set the number of results that must be fetched on each
        HTTP call.

        Args:
            limit (int): Number of results to fetch in each HTTP call.

        Returns:
            (ResourceSet): Returns a copy of the current ResourceSet with the limit applied.
        """
        if not isinstance(limit, int):
            raise TypeError('`limit` must be an integer.')

        if limit <= 0:
            raise ValueError('`limit` must be a positive, non-zero integer.')

        copy = self._copy()
        copy._limit = limit
        return copy

    def order_by(self, *fields):
        """
        Add fields for ordering.

        Usage:

        ```py3
        purchases = client.requests.all().order_by(
            'asset.tiers.customer.name',
            '-created'
        )
        ```
        !!! note
            To sort results in descending order the name of the field must
            be prefixed with a `-` (minus) sign.

        Returns:
            (ResourceSet): Returns a copy of the current ResourceSet with the order applied.
        """
        copy = self._copy()
        copy._ordering.extend(fields)
        return copy

    def select(self, *fields):
        """
        Apply the RQL ``select`` operator to
        this ResourceSet object.

        Usage:

        ```py3
        purchases = client.requests.all().select(
            '-asset.items',
            '-asset.params',
            'activation_key',
        )
        ```
        !!! note
            To unselect a field it must
            be prefixed with a `-` (minus) sign.

        Returns:
            (ResourceSet): Returns a copy of the current ResourceSet with the select applied.
        """
        copy = self._copy()
        copy._select.extend(fields)
        return copy

    def filter(self, *args, **kwargs):
        """
        Applies filters to this ResourceSet object.

        Arguments can be RQL filter expressions as strings
        or R objects.

        Usage:

        ```py3
        rs = rs.filter('eq(field,value)', 'eq(another.field,value2)')
        rs = rs.filter(R().field.eq('value'), R().another.field.eq('value2'))
        ```

        All the arguments will be combined with logical `and`.

        Filters can be also specified as keyword argument using the `__` (double underscore)
        notation.

        ```py3
        rs = rs.filter(
            field=value,
            another__field=value,
            field2__in=('a', 'b'),
            field3__null=True,
        )
        ```

        Also keyword arguments will be combined with logical `and`.

        Returns:
            (ResourceSet): Returns a copy of the current ResourceSet with the filter applied.
        """
        copy = self._copy()
        for arg in args:
            if isinstance(arg, str):
                copy._query &= R(_expr=arg)
                continue
            if isinstance(arg, R):
                copy._query &= arg
                continue
            raise TypeError(f'arguments must be string or R not {type(arg)}')

        if kwargs:
            copy._query &= R(**kwargs)

        return copy

    def all(self):
        """
        Returns a copy of the current ResourceSet.

        Returns:
            (ResourceSet): Returns a copy of the current ResourceSet.
        """
        return self._copy()

    def search(self, term: str):
        """
        Create a copy of the current ResourceSet applying the `search` RQL
        operator equal to `term`.

        Args:
            term (str): The term to search for.

        Returns:
            (ResourceSet): Create a copy of the current ResourceSet applying the `search` RQL
                operator equal to `term`.
        """
        copy = self._copy()
        copy._search = term
        return copy

    def values_list(self, *fields):
        """
        Returns a flat dictionary containing only the fields passed as arguments
        for each resource that belongs to this ResourceSet.

        Nested field can be specified using dot notation.

        Usage:

        ```py3
        values = rs.values_list('field', 'nested.field')
        ```
        """
        if self._results:
            self._fields = fields
            return [self._get_values(item) for item in self._results]

        copy = self._copy()
        copy._fields = fields
        return copy

    def _get_values(self, item):
        return {field: resolve_attribute(field, item) for field in self._fields}

    def _build_qs(self):
        qs = ''
        if self._select:
            qs += f'&select({",".join(self._select)})'
        if self._query:
            qs += f'&{str(self._query)}'
        if self._ordering:
            qs += f'&ordering({",".join(self._ordering)})'
        return qs[1:] if qs else ''

    def _get_request_url(self):
        url = f'{self._path}'
        qs = self._build_qs()
        if qs:
            url = f'{url}?{qs}'

        return url

    def _get_request_kwargs(self):
        config = copy.deepcopy(self._config)
        config.setdefault('params', {})

        config['params'].update(
            {
                'limit': self._limit,
                'offset': self._offset,
            },
        )

        if self._search:
            config['params']['search'] = self._search

        return config

    def _copy(self):
        rs = self.__class__(self._client, self._path, self._query)
        rs._limit = self._limit
        rs._offset = self._offset
        rs._slice = self._slice
        rs._fields = self._fields
        rs._search = self._search
        rs._select = copy.copy(self._select)
        rs._ordering = copy.copy(self._ordering)
        rs._config = copy.deepcopy(self._config)

        return rs

    def _validate_key(self, key):
        if not isinstance(key, (int, slice)):
            raise TypeError('ResourceSet indices must be integers or slices.')

        if isinstance(key, slice) and (key.start is None or key.stop is None):
            raise ValueError('Both start and stop indexes must be specified.')

        if (not isinstance(key, slice) and (key < 0)) or (
            isinstance(key, slice) and (key.start < 0 or key.stop < 0)
        ):
            raise ValueError('Negative indexing is not supported.')

        if isinstance(key, slice) and not (key.step is None or key.step == 0):
            raise ValueError('Indexing with step is not supported.')

    def help(self):
        self._client.print_help(self)
        return self


class ResourceSet(_ResourceSetBase):
    """
    Represent a set of resources.

    Usage:

    ```py3
    for product in client.products.all().filter(
        R().status.eq('published')
    ).order_by('created'):
        ...
    ```
    """

    def __iter__(self):
        if self._results is None:
            return self._iterator()
        return iter(self._results)

    def __bool__(self):
        if self._results is not None:
            return bool(self._results)
        copy = self._copy()
        copy._fetch_all()
        return bool(copy._results)

    def __getitem__(self, key):  # noqa: CCR001
        self._validate_key(key)

        if self._results is not None:
            return self._results[key]

        if isinstance(key, int):
            copy = self._copy()
            copy._limit = 1
            copy._offset = key
            copy._fetch_all()
            return copy._results[0] if copy._results else None

        copy = self._copy()
        copy._offset = key.start
        copy._slice = key
        if copy._slice.stop - copy._slice.start < copy._limit:
            copy._limit = copy._slice.stop - copy._slice.start

        return copy

    def count(self) -> int:
        """
        Returns the total number of resources within this ResourceSet object.

        Usage:

        ```py3
        no_of_products = client.products.all().count()
        ```

        Returns:
            (int): Returns the total number of resources within this ResourceSet object.
        """
        if not self._content_range:
            copy = self._copy()
            url = copy._get_request_url()
            kwargs = copy._get_request_kwargs()
            kwargs['params']['limit'] = 0
            copy._execute_request(url, kwargs)
            return copy._content_range.count
        return self._content_range.count

    def first(self):
        """
        Returns the first resource that belongs to this ResourceSet object
        or None if the ResourceSet doesn't contains resources.

        Usage:

        ```py3
        latest_news = client.news.all().order_by('-updated').first()
        ```

        Returns:
            (Resource): Returns the first resource that belongs to this ResourceSet object
                or None.
        """
        copy = self._copy()
        copy._limit = 1
        copy._offset = 0
        copy._fetch_all()
        return copy._results[0] if copy._results else None

    def _iterator(self):
        args = (
            self,
            self._client,
            self._path,
            self._build_qs(),
            self._get_request_kwargs(),
        )
        iterator = (
            ValuesListIterator(*args, fields=self._fields)
            if self._fields
            else ResourceIterator(*args)
        )
        return iterator

    def _execute_request(self, url, kwargs):
        results = self._client.get(url, **kwargs)
        self._content_range = parse_content_range(
            self._client.response.headers.get('Content-Range'),
        )
        return results

    def _fetch_all(self):
        if self._results is None:
            self._results = self._execute_request(
                self._get_request_url(),
                self._get_request_kwargs(),
            )


class AsyncResourceSet(_ResourceSetBase):
    """
    Represent a set of resources.

    Usage:

    ```py3
    async for product in (
        client.products.all().filter(
            R().status.eq('published')
        ).order_by('created')
    ):
        ...
    ```
    """

    def __aiter__(self):
        if self._results is None:
            return self._iterator()
        return aiter(self._results)

    def __bool__(self):
        if self._results is None:
            raise NotYetEvaluatedError()
        return bool(self._results)

    def __getitem__(self, key):  # noqa: CCR001
        self._validate_key(key)

        if self._results is not None:
            return self._results[key]

        if isinstance(key, int):
            raise NotYetEvaluatedError()

        copy = self._copy()
        copy._offset = key.start
        copy._slice = key
        if copy._slice.stop - copy._slice.start < copy._limit:
            copy._limit = copy._slice.stop - copy._slice.start

        return copy

    async def count(self) -> int:
        """
        Returns the total number of resources within this ResourceSet object.

        Usage:

        ```py3
        no_of_products = await client.products.all().count()
        ```

        Returns:
            (int): Returns the total number of resources within this ResourceSet object.
        """
        if not self._content_range:
            url = self._get_request_url()
            kwargs = self._get_request_kwargs()
            kwargs['params']['limit'] = 0
            await self._execute_request(url, kwargs)
        return self._content_range.count

    async def first(self):
        """
        Returns the first resource that belongs to this ResourceSet object
        or None if the ResourceSet doesn't contains resources.

        Usage:

        ```py3
        latest_news = await client.news.all().order_by('-updated').first()
        ```

        Returns:
            (Resource): Returns the first resource that belongs to this ResourceSet object
                or None.
        """
        copy = self._copy()
        copy._limit = 1
        copy._offset = 0
        await copy._fetch_all()
        return copy._results[0] if copy._results else None

    def _iterator(self):
        args = (
            self,
            self._client,
            self._path,
            self._build_qs(),
            self._get_request_kwargs(),
        )

        iterator = (
            AsyncValuesListIterator(*args, fields=self._fields)
            if self._fields
            else AsyncResourceIterator(*args)
        )
        return iterator

    async def _execute_request(self, url, kwargs):
        results = await self._client.get(url, **kwargs)
        self._content_range = parse_content_range(
            self._client.response.headers.get('Content-Range'),
        )
        return results

    async def _fetch_all(self):
        if self._results is None:  # pragma: no branch
            self._results = await self._execute_request(
                self._get_request_url(),
                self._get_request_kwargs(),
            )
