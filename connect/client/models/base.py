from connect.client.exceptions import ClientError
from connect.client.models.resourceset import ResourceSet
from connect.client.utils import resolve_attribute
from connect.client.rql import R


class NS:
    """
    A namespace is a group of related collections.
    """
    def __init__(self, client, path):
        """
        Create a new NS instance.

        :param client: the client instance
        :type client: ConnectClient
        :param path: path name of the namespace
        :type path: str
        """
        self._client = client
        self._path = path

    @property
    def path(self):
        return self._path

    def __getattr__(self, name):
        """
        Returns a collection object by its name.

        :param name: the name of the Collection object.
        :type name: str
        :return: The Collection named ``name``.
        :rtype: Collection
        """
        if '_' in name:
            name = name.replace('_', '-')
        return self.collection(name)

    def __iter__(self):
        raise TypeError('A Namespace object is not iterable.')

    def __call__(self, name):
        return self.ns(name)

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

        return Collection(
            self._client,
            f'{self._path}/{name}',
        )

    def ns(self, name):
        """
        Returns the namespace called ``name``.

        :param name: The name of the namespace.
        :type name: str
        :raises TypeError: if the ``name`` is not a string.
        :raises ValueError: if the ``name`` is blank.
        :return: The namespace called ``name``.
        :rtype: NS
        """
        if not isinstance(name, str):
            raise TypeError('`name` must be a string.')

        if not name:
            raise ValueError('`name` must not be blank.')

        return NS(
            self._client,
            f'{self._path}/{name}',
        )

    def help(self):
        """
        Output the namespace documentation to the console.

        :return: self
        :rtype: NS
        """
        self._client.print_help(self)
        return self


class Collection:
    """
    A collection is a group of operations on a resource.
    """
    def __init__(self, client, path):
        """
        Create a new Collection instance.

        :param client: the client instance
        :type client: ConnectClient
        :param path: path name of the collection
        :type path: str
        """
        self._client = client
        self._path = path

    @property
    def path(self):
        return self._path

    def __iter__(self):
        raise TypeError('A Collection object is not iterable.')

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
            self._client,
            self._path,
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
            self._client,
            self._path,
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
        return self._client.create(
            self._path,
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
        if not isinstance(resource_id, (str, int)):
            raise TypeError('`resource_id` must be a string or int.')

        if not resource_id:
            raise ValueError('`resource_id` must not be blank.')

        return Resource(
            self._client,
            f'{self._path}/{resource_id}',
        )

    def help(self):
        """
        Output the collection documentation to the console.

        :return: self
        :rtype: Collection
        """
        self._client.print_help(self)
        return self


class Resource:
    """Represent a generic resource."""
    def __init__(self, client, path):
        """
        Create a new Resource instance.

        :param client: the client instance
        :type client: ConnectClient
        :param path: path name of the resource
        :type path: str
        :param specs: OpenAPI specs, defaults to None
        :type specs: ResourceInfo, optional
        """
        self._client = client
        self._path = path

    @property
    def path(self):
        return self._path

    def __getattr__(self, name):
        """
        Returns a nested Collection object called ``name``.

        :param name: The name of the Collection to retrieve.
        :type name: str
        :return: a Collection called ``name``.
        :rtype: Collection
        """
        if '_' in name:
            name = name.replace('_', '-')
        return self.collection(name)

    def __call__(self, name):
        return self.action(name)

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

        return Collection(
            self._client,
            f'{self._path}/{name}',
        )

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

        return Action(
            self._client,
            f'{self._path}/{name}',
        )

    def exists(self):
        try:
            self.get()
            return True
        except ClientError as ce:
            if ce.status_code and ce.status_code == 404:
                return False
            raise

    def get(self, **kwargs):
        """
        Execute a http GET to retrieve this resource.
        The http GET can be customized passing kwargs that
        will be forwarded to the underlying GET of the ``requests``
        library.

        :return: The resource data.
        :rtype: dict
        """
        return self._client.get(self._path, **kwargs)

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
        return self._client.update(
            self._path,
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
        return self._client.delete(
            self._path,
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
        self._client.print_help(self)
        return self


class Action:
    """
    This class represent an action that can be executed on a resource.
    """
    def __init__(self, client, path):
        """
        Create a new Action instance.

        :param client: the client instance
        :type client: ConnectClient
        :param path: path name of the action
        :type path: str
        :param specs: OpenAPI specs, defaults to None
        :type specs: ActionInfo, optional
        """
        self._client = client
        self._path = path

    @property
    def path(self):
        return self._path

    def get(self, **kwargs):
        """
        Execute this action through a http GET.
        The http GET can be customized passing kwargs that
        will be forwarded to the underlying GET of the ``requests``
        library.

        :return: The action data.
        :rtype: dict, None
        """
        return self._client.get(self._path, **kwargs)

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
        return self._client.execute(
            'post',
            self._path,
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
        return self._client.execute(
            'put',
            self._path,
            **kwargs,
        )

    def delete(self, **kwargs):
        """
        Execute this action through a http DELETE.
        The http DELETE can be customized passing kwargs that
        will be forwarded to the underlying DELETE of the ``requests``
        library.
        """
        return self._client.delete(
            self._path,
            **kwargs,
        )

    def help(self):
        """
        Output the action documentation to the console.

        :return: self
        :rtype: Action
        """
        self._client.print_help(self)
        return self
