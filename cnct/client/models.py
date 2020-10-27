from keyword import iskeyword

from cnct.client.exceptions import NotFoundError
from cnct.client.utils import parse_content_range, resolve_attribute
from cnct.help import print_help
from cnct.rql import R


class NS:
    """
    A namespace is a group of related collections.
    """
    def __init__(self, client, path, specs=None):
        """
        Create a new NS instance.

        :param client: the client instance
        :type client: ConnectClient
        :param path: path name of the namespace
        :type path: str
        :param specs: OpenAPI specs, defaults to None
        :type specs: NSInfo, optional
        """
        self.client = client
        self.path = path
        self.specs = specs

    def __getattr__(self, name):
        """
        Returns a collection object by its name.

        :param name: the name of the Collection object.
        :type name: str
        :raises AttributeError: if the name does not exist.
        :return: The Collection named ``name``.
        :rtype: Collection
        """
        if not self.specs:
            return self.collection(name)
        if name in self.specs.collections:
            return self.collection(name)
        raise AttributeError(f'Unable to resolve {name}.')

    def __dir__(self):
        """
        Return a list of attributes defined for this NS instance.
        The returned list includes the names of the collections
        that belong to this namespace.

        :return: List of attributes.
        :rtype: list
        """
        default = sorted(super().__dir__() + list(self.__dict__.keys()))
        if not self.specs:
            return default
        cl = self.specs.collections.keys()
        return default + [
            name for name in cl
            if name.isidentifier() and not iskeyword(name)
        ]

    def collection(self, name):
        """
        Returns the collection called ``name``.

        :param name: The name of the collection.
        :type name: str
        :raises TypeError: if the ``name`` is not a string.
        :raises ValueError: if the ``name`` is blank.
        :raises NotFoundError: if the ``name`` does not exist.
        :return: The collection called ``name``.
        :rtype: Collection
        """
        if not isinstance(name, str):
            raise TypeError('`name` must be a string.')

        if not name:
            raise ValueError('`name` must not be blank.')

        if not self.specs:
            return Collection(
                self.client,
                f'{self.path}/{name}',
            )
        if name in self.specs.collections:
            return Collection(
                self.client,
                f'{self.path}/{name}',
                self.specs.collections.get(name),
            )
        raise NotFoundError(f'The collection {name} does not exist.')

    def help(self):
        """
        Output the namespace documentation to the console.

        :return: self
        :rtype: NS
        """
        print_help(self.specs)
        return self


class Collection:
    """
    A collection is a group of operations on a resource.
    """
    def __init__(self, client, path, specs=None):
        """
        Create a new Collection instance.

        :param client: the client instance
        :type client: ConnectClient
        :param path: path name of the namespace
        :type path: str
        :param specs: OpenAPI specs, defaults to None
        :type specs: CollectionInfo, optional
        """
        self.client = client
        self.path = path
        self.specs = specs

    def __iter__(self):
        raise TypeError('A collection object is not iterable.')

    def __getitem__(self, resource_id):
        """
        Return a Resource object representing the resource
        identified by ``resource_id``.

        :param resource_id: The identifier of the resource
        :type resource_id: str, int
        :return: the Resource instance identified by ``resource_id``.
        :rtype: Resource
        """
        return self.resource(resource_id)

    def all(self):
        """
        Return a ResourceSet instance.

        :return: a ResourceSet instance.
        :rtype: ResourceSet
        """
        return ResourceSet(
            self.client,
            self.path,
            specs=self.specs.operations.get('search') if self.specs else None,
        )

    def filter(self, *args, **kwargs):
        """
        Returns a ResourceSet object.
        The returned ResourceSet object will be filtered based on
        the arguments and keyword arguments.

        Arguments can be RQL filter expressions as strings
        or R objects.

        Ex.

        .. code-block:: python

            rs = collection.filter('eq(field,value)', 'eq(another.field,value2)')
            rs = collection.filter(R().field.eq('value'), R().another.field.eq('value2'))

        All the arguments will be combined with logical ``and``.

        Filters can be also specified as keyword argument using the ``__`` (double underscore)
        notation.

        Ex.

        .. code-block:: python

            rs = collection.filter(
                field=value,
                another__field=value,
                field2__in=('a', 'b'),
                field3__null=True,
            )

        Also keyword arguments will be combined with logical ``and``.


        :raises TypeError: If arguments are neither strings nor R objects.
        :return: A ResourceSet with the filters applied.
        :rtype: ResourceSet
        """
        query = R()
        for arg in args:
            if isinstance(arg, str):
                query &= R(_expr=arg)
                continue
            if isinstance(arg, R):
                query &= arg
                continue
            raise TypeError(f'arguments must be string or R not {type(arg)}')

        if kwargs:
            query &= R(**kwargs)

        return ResourceSet(
            self.client,
            self.path,
            specs=self.specs.operations.get('search') if self.specs else None,
            query=query,
        )

    def create(self, payload=None, **kwargs):
        """
        Create a new resource within this collection.

        :param payload: JSON payload of the resource to create, defaults to None.
        :type payload: dict, optional
        :return: The newly created resource.
        :rtype: dict
        """
        return self.client.create(
            self.path,
            payload=payload,
            **kwargs,
        )

    def resource(self, resource_id):
        """
        Returns an Resource object.

        :param resource_id: The resource identifier.
        :type resource_id: str, int
        :return: The Resource identified by ``resource_id``.
        :rtype: Resource
        """
        return Resource(
            self.client,
            f'{self.path}/{resource_id}',
            self.specs.resource_specs if self.specs else None,
        )

    def help(self):
        """
        Output the collection documentation to the console.

        :return: self
        :rtype: Collection
        """
        print_help(self.specs)
        return self


class Resource:
    """Represent a generic resource."""
    def __init__(self, client, path, specs=None):
        """
        Create a new Resource instance.

        :param client: the client instance
        :type client: ConnectClient
        :param path: path name of the resource
        :type path: str
        :param specs: OpenAPI specs, defaults to None
        :type specs: ResourceInfo, optional
        """
        self.client = client
        self.path = path
        self.specs = specs

    def __getattr__(self, name):
        """
        Returns an Action or a nested Collection object called ``name``.

        :param name: The name of the Action or Collection to retrieve.
        :type name: str
        :raises AttributeError: If OpenAPI specs are not avaliable.
        :raises AttributeError: If the name does not exist.
        :return: a Collection or an Action called ``name``.
        :rtype: Action, Collection
        """
        if not self.specs:
            raise AttributeError(
                'No specs available. Use the `collection` '
                'or `action` methods instead.'
            )
        if name in self.specs.collections:
            return self.collection(name)
        if name in self.specs.actions:
            return self.action(name)
        raise AttributeError('Unable to resolve {}.'.format(name))

    def __dir__(self):
        """
        Return a list of attributes defined for this Resource instance.
        The returned list includes the names of the nested collections
        and actions that belong to this resource.

        :return: List of attributes.
        :rtype: list
        """
        if not self.specs:
            return super().__dir__()
        ac = list(self.specs.actions.keys())
        cl = list(self.specs.collections.keys())
        additional_names = [
            name for name in cl + ac
            if name.isidentifier() and not iskeyword(name)
        ]
        return sorted(super().__dir__() + additional_names)

    def collection(self, name):
        """
        Returns the collection called ``name``.

        :param name: The name of the collection.
        :type name: str
        :raises TypeError: if the ``name`` is not a string.
        :raises ValueError: if the ``name`` is blank.
        :raises NotFoundError: if the ``name`` does not exist.
        :return: The collection called ``name``.
        :rtype: Collection
        """
        if not isinstance(name, str):
            raise TypeError('`name` must be a string.')

        if not name:
            raise ValueError('`name` must not be blank.')

        if not self.specs:
            return Collection(
                self.client,
                f'{self.path}/{name}',
            )
        if name in self.specs.collections:
            return Collection(
                self.client,
                f'{self.path}/{name}',
                self.specs.collections.get(name),
            )
        raise NotFoundError(f'The collection {name} does not exist.')

    def action(self, name):
        """
        Returns the action called ``name``.

        :param name: The name of the action.
        :type name: str
        :raises TypeError: if the ``name`` is not a string.
        :raises ValueError: if the ``name`` is blank.
        :raises NotFoundError: if the ``name`` does not exist.
        :return: The action called ``name``.
        :rtype: Action
        """
        if not isinstance(name, str):
            raise TypeError('`name` must be a string.')

        if not name:
            raise ValueError('`name` must not be blank.')

        if not self.specs:
            return Action(
                self.client,
                f'{self.path}/{name}',
            )
        if name in self.specs.actions:
            return Action(
                self.client,
                f'{self.path}/{name}',
                self.specs.actions.get(name),
            )
        raise NotFoundError(f'The action {name} does not exist.')

    def get(self, **kwargs):
        """
        Execute a http GET to retrieve this resource.
        The http GET can be customized passing kwargs that
        will be forwarded to the underlying GET of the ``requests``
        library.

        :return: The resource data.
        :rtype: dict
        """
        return self.client.get(self.path, **kwargs)

    def update(self, payload=None, **kwargs):
        """
        Execute a http PUT to update this resource.
        The http PUT can be customized passing kwargs that
        will be forwarded to the underlying PUT of the ``requests``
        library.

        :param payload: the JSON payload of the update request, defaults to None
        :type payload: dict, optional
        :return: The updated resource.
        :rtype: dict
        """
        return self.client.update(
            self.path,
            payload=payload,
            **kwargs,
        )

    def delete(self, **kwargs):
        """
        Execute a http DELETE to delete this resource.
        The http DELETE can be customized passing kwargs that
        will be forwarded to the underlying DELETE of the ``requests``
        library.
        """
        return self.client.delete(
            self.path,
            **kwargs,
        )

    def values(self, *fields):
        """
        Returns a flat dictionary containing only the fields passed as arguments.
        Nested field can be specified using dot notation.

        Ex.

        .. code-block:: python

        values = resource.values('field', 'nested.field')

        :return: A dictionary containing field,value pairs.
        :rtype: dict
        """
        results = {}
        item = self.get()
        for field in fields:
            results[field] = resolve_attribute(field, item)
        return results

    def help(self):
        """
        Output the resource documentation to the console.

        :return: self
        :rtype: Resource
        """
        print_help(self.specs)
        return self


class Action:
    """
    This class represent an action that can be executed on a resource.
    """
    def __init__(self, client, path, specs=None):
        """
        Create a new Action instance.

        :param client: the client instance
        :type client: ConnectClient
        :param path: path name of the action
        :type path: str
        :param specs: OpenAPI specs, defaults to None
        :type specs: ActionInfo, optional
        """
        self.client = client
        self.path = path
        self.specs = specs

    def get(self, **kwargs):
        """
        Execute this action through a http GET.
        The http GET can be customized passing kwargs that
        will be forwarded to the underlying GET of the ``requests``
        library.

        :return: The action data.
        :rtype: dict, None
        """
        return self.client.get(self.path, **kwargs)

    def post(self, payload=None, **kwargs):
        """
        Execute this action through a http POST.
        The http POST can be customized passing kwargs that
        will be forwarded to the underlying PUT of the ``requests``
        library.

        :param payload: the JSON payload for this action, defaults to None
        :type payload: dict, optional
        :return: The result of this action.
        :rtype: dict, None
        """
        if payload:
            kwargs['json'] = payload
        return self.client.execute(
            'post',
            self.path,
            200,
            **kwargs,
        )

    def put(self, payload=None, **kwargs):
        """
        Execute this action through a http PUT.
        The http PUT can be customized passing kwargs that
        will be forwarded to the underlying PUT of the ``requests``
        library.

        :param payload: the JSON payload for this action, defaults to None
        :type payload: dict, optional
        :return: The result of this action.
        :rtype: dict, None
        """
        if payload:
            kwargs['json'] = payload
        return self.client.execute(
            'put',
            self.path,
            200,
            **kwargs,
        )

    def delete(self, **kwargs):
        """
        Execute this action through a http DELETE.
        The http DELETE can be customized passing kwargs that
        will be forwarded to the underlying DELETE of the ``requests``
        library.
        """
        return self.client.delete(
            self.path,
            **kwargs,
        )

    def help(self):
        """
        Output the action documentation to the console.

        :return: self
        :rtype: Action
        """
        print_help(self.specs)
        return self


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

        self.client = client
        self.path = path
        self.specs = specs
        self.query = query or R()
        self.results = None
        self._result_iterator = None
        self._limit = 100
        self._offset = 0
        self._slice = False
        self.content_range = None
        self._fields = None
        self._search = None
        self._select = []
        self._ordering = []
        self._config = {}

    def __len__(self):
        """
        Returns the length of the result cache.

        :return: the length of the result cache.
        :rtype: int
        """
        if not self.results:
            self._perform()
        return len(self.results)

    def __iter__(self):
        """
        Returns an iterator to iterate over the set of resources.

        :return: A resources iterator.
        :rtype: ResourceSet
        """
        if not self.results:
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
            if self.content_range.last == self.content_range.count - 1:
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
        return bool(self.results)

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

        if self.results:
            return self.results[key]
        if isinstance(key, int):
            self._perform()
            return self.results[key]

        self._offset = key.start
        self._limit = key.stop - key.start
        self._slice = True
        return self

    def configure(self, **kwargs):
        """
        Set the keyword arguments that needs to be forwarded to
        the underlying ``requests`` call.

        :return: This ResourceSet object.
        :rtype: ResourceSet
        """
        self._config = kwargs or {}
        return self

    def order_by(self, *fields):
        """
        Add fields for ordering.

        :return: This ResourceSet object.
        :rtype: ResourceSet
        """
        self._ordering.extend(fields)
        return self

    def select(self, *fields):
        """
        Apply the RQL ``select`` operator to
        this ResourceSet object.

        :return: This ResourceSet object.
        :rtype: ResourceSet
        """
        self._select.extend(fields)
        return self

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
        for arg in args:
            if isinstance(arg, str):
                self.query &= R(_expr=arg)
                continue
            if isinstance(arg, R):
                self.query &= arg
                continue
            raise TypeError(f'arguments must be string or R not {type(arg)}')

        if kwargs:
            self.query &= R(**kwargs)

        return self

    def count(self):
        """
        Returns the total number of resources within this ResourceSet object.

        :return: The total number of resources present.
        :rtype: int
        """
        if not self.results:
            self._perform()
        return self.content_range.count

    def first(self):
        """
        Returns the first resource that belongs to this ResourceSet object
        or None if the ResourceSet doesn't contains resources.

        :return: The first resource.
        :rtype: dict, None
        """
        if not self.results:
            self._perform()
        return self.results[0] if self.results else None

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
        self._fields = fields
        if self.results:
            return [
                self._get_values(item)
                for item in self.results
            ]
        return self

    def _get_values(self, item):
        return {
            field: resolve_attribute(field, item)
            for field in self._fields
        }

    def _build_qs(self):
        qs = ''
        if self._select:
            qs += f'&select({",".join(self._select)})'
        if self.query:
            qs += f'&{str(self.query)}'
        if self._ordering:
            qs += f'&ordering({",".join(self._ordering)})'
        return qs[1:] if qs else ''

    def _perform(self):
        url = f'{self.path}'
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

        self.results = self.client.get(url, **self._config)
        self.content_range = parse_content_range(
            self.client.response.headers['Content-Range'],
        )
        self._result_iterator = iter(self.results)

    def help(self):
        """
        Output the ResourceSet documentation to the console.

        :return: self
        :rtype: ResourceSet
        """
        print_help(self.specs)
        return self
