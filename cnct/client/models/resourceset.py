import copy

from cnct.client.utils import get_values, parse_content_range, resolve_attribute
from cnct.rql import R


class AbstractIterable:
    def __init__(self, client, path, query, config, **kwargs):
        self._client = client
        self._path = path
        self._query = query
        self._config = config
        self._kwargs = kwargs

    def get_item(self, item):
        raise NotImplementedError('get_item must be implemented in subclasses.')

    def __iter__(self):
        cr = None
        results = None
        while cr is None or cr.last < cr.count - 1:
            try:
                results, cr = self._execute_request()
            except StopIteration:
                return

            if not (results and cr):
                return

            for item in results:
                yield self.get_item(item)
            self._config['params']['offset'] += self._config['params']['limit']

    def _execute_request(self):
        results = self._client.get(
            f'{self._path}?{self._query}',
            **self._config,
        )
        content_range = parse_content_range(
            self._client.response.headers.get('Content-Range'),
        )
        return results, content_range


class ResourceIterable(AbstractIterable):

    def get_item(self, item):
        return item


class ValuesListIterable(AbstractIterable):

    def get_item(self, item):
        return get_values(item, self._kwargs['fields'])


class ResourceSet:
    """
    Represent a set of resources.
    """
    def __init__(
        self,
        client,
        path,
        specs=None,
        query=None
    ):

        self._client = client
        self._path = path
        self._specs = specs
        self._query = query or R()
        self._results = None
        self._result_iterator = None
        self._limit = 100
        self._offset = 0
        self._slice = False
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

    def __iter__(self):
        """
        Returns an iterator to iterate over the set of resources.

        :return: A resources iterator.
        :rtype: ResourceSet
        """
        if self._results is None:
            return self._iterator()
        return iter(self._results)

    def __bool__(self):
        """
        Return True if the ResourceSet contains at least a resource
        otherwise return False.

        :return: True if contains a resource otherwise False.
        :rtype: bool
        """
        self._fetch_all()
        return bool(self._results)

    def __getitem__(self, key):
        """
        If called with and integer index, returns the item
        at index ``key``.

        If key is a slice, set the pagination limit and offset
        accordingly.

        :param key: index or slice.
        :type key: int, slice
        :raises TypeError: If ``key`` is neither an integer nor a slice.
        :return: The resource at index ``key`` or self if ``key`` is a slice.
        :rtype: dict, ResultSet
        """
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

        if self._results:
            return self._results[key]

        if isinstance(key, int):
            copy = self._copy()
            copy._limit = 1
            copy._offset = key
            copy._fetch_all()
            return copy._results[0] if copy._results else None

        copy = self._copy()
        copy._offset = key.start
        copy._limit = key.stop - key.start
        copy._slice = True
        return copy

    def configure(self, **kwargs):
        """
        Set the keyword arguments that needs to be forwarded to
        the underlying ``requests`` call.

        :return: This ResourceSet object.
        :rtype: ResourceSet
        """
        copy = self._copy()
        copy._config = kwargs or {}
        return copy

    def limit(self, limit):
        """
        Set the number of results to be fetched from the remote
        endpoint at once.

        :param limit: maximum number of results to fetch in a batch.
        :type limit: int
        :raises TypeError: if `limit` is not an integer.
        :raises ValueError: if `limit` is not positive non-zero.
        :return: A copy of this ResourceSet class with the new limit.
        :rtype: ResourceSet
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

        :return: This ResourceSet object.
        :rtype: ResourceSet
        """
        copy = self._copy()
        copy._ordering.extend(fields)
        return copy

    def select(self, *fields):
        """
        Apply the RQL ``select`` operator to
        this ResourceSet object.

        :return: This ResourceSet object.
        :rtype: ResourceSet
        """
        copy = self._copy()
        copy._select.extend(fields)
        return copy

    def filter(self, *args, **kwargs):
        """
        Applies filters to this ResourceSet object.

        Arguments can be RQL filter expressions as strings
        or R objects.

        Ex.

        .. code-block:: python

            rs = rs.filter('eq(field,value)', 'eq(another.field,value2)')
            rs = rs.filter(R().field.eq('value'), R().another.field.eq('value2'))

        All the arguments will be combined with logical ``and``.

        Filters can be also specified as keyword argument using the ``__`` (double underscore)
        notation.

        Ex.

        .. code-block:: python

            rs = rs.filter(
                field=value,
                another__field=value,
                field2__in=('a', 'b'),
                field3__null=True,
            )

        Also keyword arguments will be combined with logical ``and``.


        :raises TypeError: If arguments are neither strings nor R objects.
        :return: This ResourceSet object.
        :rtype: ResourceSet
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

    def count(self):
        """
        Returns the total number of resources within this ResourceSet object.

        :return: The total number of resources present.
        :rtype: int
        """
        if not self._content_range:
            url = self._get_request_url()
            kwargs = self._get_request_kwargs()
            kwargs['params']['limit'] = 0
            self._execute_request(url, kwargs)
        return self._content_range.count

    def first(self):
        """
        Returns the first resource that belongs to this ResourceSet object
        or None if the ResourceSet doesn't contains resources.

        :return: The first resource.
        :rtype: dict, None
        """
        self._fetch_all()
        return self._results[0] if self._results else None

    def all(self):
        """
        Returns a copy of the current ResourceSet.

        :return: A copy of this ResourceSet.
        :rtype: ResourceSet
        """
        return self._copy()

    def search(self, term):
        """
        Create a copy of the current ResourceSet with
        the search set to `term`.

        :param term: The term to search for.
        :type term: str
        :return: A copy of the current ResourceSet.
        :rtype: ResourceSet
        """
        copy = self._copy()
        copy._search = term
        return copy

    def values_list(self, *fields):
        """
        Returns a flat dictionary containing only the fields passed as arguments
        for each resource that belongs to this ResourceSet.

        Nested field can be specified using dot notation.

        Ex.

        .. code-block:: python

        values = rs.values_list('field', 'nested.field')

        :return: A list of dictionaries containing field,value pairs.
        :rtype: list
        """
        if self._results:
            self._fields = fields
            return [
                self._get_values(item)
                for item in self._results
            ]

        copy = self._copy()
        copy._fields = fields
        return copy

    def _get_values(self, item):
        return {
            field: resolve_attribute(field, item)
            for field in self._fields
        }

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

    def _iterator(self):
        args = (
            self._client,
            self._path,
            self._build_qs(),
            self._get_request_kwargs(),
        )
        iterable = (
            ValuesListIterable(*args, fields=self._fields)
            if self._fields else ResourceIterable(*args)
        )
        return iter(iterable)

    def _get_request_kwargs(self):
        config = copy.deepcopy(self._config)
        config.setdefault('params', {})

        config['params'].update({
            'limit': self._limit,
            'offset': self._offset,
        })

        if self._search:
            config['params']['search'] = self._search

        return config

    def _execute_request(self, url, kwargs):
        results = self._client.get(url, **kwargs)
        self._content_range = parse_content_range(
            self._client.response.headers.get('Content-Range'),
        )
        return results

    def _fetch_all(self):
        if self._results is None:
            self._results = list(self._iterator())

    def _copy(self):
        rs = ResourceSet(self._client, self._path, self._specs, self._query)
        rs._limit = self._limit
        rs._offset = self._offset
        rs._slice = self._slice
        rs._fields = self._fields
        rs._search = self._search
        rs._select = copy.copy(self._select)
        rs._ordering = copy.copy(self._ordering)
        rs._config = copy.deepcopy(self._config)

        return rs

    def help(self):
        """
        Output the ResourceSet documentation to the console.

        :return: self
        :rtype: ResourceSet
        """
        self._client._help_formatter.print_help(self._specs)
        return self
