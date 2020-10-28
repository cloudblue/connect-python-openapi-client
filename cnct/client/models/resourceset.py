import copy

from cnct.client.utils import parse_content_range, resolve_attribute
from cnct.help import print_help
from cnct.rql import R


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

    def __len__(self):
        """
        Returns the length of the result cache.

        :return: the length of the result cache.
        :rtype: int
        """
        if not self._results:
            self._perform()
        return len(self._results)

    def __iter__(self):
        """
        Returns an iterator to iterate over the set of resources.

        :return: A resources iterator.
        :rtype: ResourceSet
        """
        if not self._results:
            self._perform()
        return self

    def __next__(self):
        """
        Returns the next element from the results iterator.
        The ResourceSet handles pagination automatically.

        :return: The next resource belonging to this ResourceSet.
        :rtype: dict
        """
        try:
            item = next(self._result_iterator)
            if self._fields:
                return self._get_values(item)
            return item
        except StopIteration:
            if self._slice:
                self._offset = 0
                raise
            if self._content_range.last == self._content_range.count - 1:
                self._offset = 0
                raise
            self._offset += self._limit
            self._perform()
            item = next(self._result_iterator)
            if self._fields:
                return self._get_values(item)
            return item

    def __bool__(self):
        """
        Return True if the ResourceSet contains at least a resource
        otherwise return False.

        :return: True if contains a resource otherwise False.
        :rtype: bool
        """
        self._perform()
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

        assert (not isinstance(key, slice) and (key >= 0)) or (
            isinstance(key, slice)
            and (key.start is None or key.start >= 0)
            and (key.stop is None or key.stop >= 0)
        ), "Negative indexing is not supported."

        assert (not isinstance(key, slice) and (key >= 0)) or (
            isinstance(key, slice)
            and (key.step is None or key.step == 0)
        ), "Indexing with step is not supported."

        if self._results:
            return self._results[key]

        if isinstance(key, int):
            copy = self._copy()
            copy._limit = 1
            copy._offset = key
            copy._perform()
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
        if not self._results:
            self._perform()
        return self._content_range.count

    def first(self):
        """
        Returns the first resource that belongs to this ResourceSet object
        or None if the ResourceSet doesn't contains resources.

        :return: The first resource.
        :rtype: dict, None
        """
        if not self._results:
            self._perform()
        return self._results[0] if self._results else None

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

    def _perform(self):
        url = f'{self._path}'
        qs = self._build_qs()
        if qs:
            url = f'{url}?{qs}'

        self._config.setdefault('params', {})

        self._config['params'].update({
            'limit': self._limit,
            'offset': self._offset,
        })

        if self._search:
            self._config['params']['search'] = self._search

        self._results = self._client.get(url, **self._config)
        self._content_range = parse_content_range(
            self._client.response.headers['Content-Range'],
        )
        self._result_iterator = iter(self._results)

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
        print_help(self._specs)
        return self
