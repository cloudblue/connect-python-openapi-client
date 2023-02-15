#
# This file is part of the Ingram Micro CloudBlue Connect Python OpenAPI Client.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
from connect.client.models.mixins import (
    ActionMixin,
    AsyncActionMixin,
    AsyncCollectionMixin,
    AsyncResourceMixin,
    CollectionMixin,
    ResourceMixin,
)
from connect.client.models.resourceset import AsyncResourceSet, ResourceSet
from connect.client.rql import R


class _NSBase:
    def __init__(self, client, path):
        self._client = client
        self._path = path

    @property
    def path(self) -> str:
        return self._path

    def __getattr__(self, name):
        if '_' in name:
            name = name.replace('_', '-')
        return self.collection(name)

    def __iter__(self):
        raise TypeError('A Namespace object is not iterable.')

    def __call__(self, name):
        return self.ns(name)

    def collection(self, name: str):
        """
        Returns a `[Async]Collection` object nested under this namespace object
        identified by its name.

        Usage:

        ```py3
        devops_ns = client.ns('devops')
        services = devops_ns.collection('products')
        ```

        Concise form:

        ```py3
        services = client('devops').services
        ```

        Args:
            name (str): The name of the collection to access.

        Returns:
            (Union[Collection, AsyncCollection]):  Returns an object nested under this namespace
                object identified by its name.
        """

        if not isinstance(name, str):
            raise TypeError('`name` must be a string.')

        if not name:
            raise ValueError('`name` must not be blank.')

        return self._get_collection_class()(
            self._client,
            f'{self._path}/{name}',
        )

    def ns(self, name: str):
        """
        Returns a `[Async]Namespace` object nested under this namespace
        identified by its name.

        Usage:

        ```py3
        subscriptions_ns = client.ns('subscriptions')
        nested_ns = subcriptions_ns.ns('nested')
        ```

        Concise form:

        ```py3
        nested_ns = client('subscriptions')('nested')
        ```

        Args:
            name (str): The name of the namespace to access.

        Returns:
            (Union[NS, AsyncNS]): Returns an object nested under this namespace
                identified by its name.
        """
        if not isinstance(name, str):
            raise TypeError('`name` must be a string.')

        if not name:
            raise ValueError('`name` must not be blank.')

        return self._get_namespace_class()(
            self._client,
            f'{self._path}/{name}',
        )

    def help(self):
        self._client.print_help(self)
        return self

    def _get_collection_class(self):
        raise NotImplementedError()

    def _get_namespace_class(self):
        raise NotImplementedError()


class NS(_NSBase):
    def _get_collection_class(self):
        return Collection

    def _get_namespace_class(self):
        return NS


class AsyncNS(_NSBase):
    def _get_collection_class(self):
        return AsyncCollection

    def _get_namespace_class(self):
        return AsyncNS


class _CollectionBase:
    def __init__(self, client, path):
        self._client = client
        self._path = path

    @property
    def path(self):
        return self._path

    def __iter__(self):
        raise TypeError('A Collection object is not iterable.')

    def __getitem__(self, resource_id):
        return self.resource(resource_id)

    def __call__(self, name):
        return self.action(name)

    def all(self):
        """
        Returns a `[Async]ResourceSet` object that that allow to access all the resources that
        belong to this collection.

        Returns:
            (Union[ResourceSet, AsyncResourceSet]): Returns an object that that allow to access
                all the resources that belong to this collection.
        """
        return self._get_resourceset_class()(
            self._client,
            self._path,
        )

    def filter(self, *args, **kwargs):
        """
        Returns a `[Async]ResourceSet` object.
        The returned ResourceSet object will be filtered based on
        the arguments and keyword arguments.

        Arguments can be RQL filter expressions as strings
        or R objects.

        Usage:

        ```py3
        rs = collection.filter('eq(field,value)', 'eq(another.field,value2)')
        rs = collection.filter(R().field.eq('value'), R().another.field.eq('value2'))
        ```

        All the arguments will be combined with logical **and**.

        Filters can be also specified as keyword argument using the **__** (double underscore)
        notation.

        Usage:

        ```py3
        rs = collection.filter(
            field=value,
            another__field=value,
            field2__in=('a', 'b'),
            field3__null=True,
        )
        ```

        Also keyword arguments will be combined with logical **and**.

        Returns:
            (Union[ResourceSet, AsyncResourceSet]): The returned ResourceSet object will be
                filtered based on the arguments and keyword arguments.
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

        return self._get_resourceset_class()(
            self._client,
            self._path,
            query=query,
        )

    def resource(self, resource_id: str):
        """
        Returns a `[Async]Resource` object that represent a resource that belong to
        this collection identified by its unique identifier.

        Usage:

        ```py3
        resource = client.collection('products').resource('PRD-000-111-222')
        ```

        Concise form:

        ```py3
        resource = client.products['PRD-000-111-222']
        ```

        Args:
            resource_id (str): The unique identifier of the resource.

        Returns:
            (Union[Resource, AsyncResource]): Returns an object that represent a resource that
                belong to this collection identified by its unique identifier.
        """
        if not isinstance(resource_id, (str, int)):
            raise TypeError('`resource_id` must be a string or int.')

        if not resource_id:
            raise ValueError('`resource_id` must not be blank.')

        return self._get_resource_class()(
            self._client,
            f'{self._path}/{resource_id}',
        )

    def action(self, name: str):
        """
        Returns an `[Async]Action` object that represent an action to perform
        on this collection identified by its name.

        Args:
            name (str): The name of the action to perform.

        Returns:
            (Union[Action, AsyncAction]): Returns an object that represent an action to perform
                on this collection identified by its name.
        """
        if not isinstance(name, str):
            raise TypeError('`name` must be a string.')

        if not name:
            raise ValueError('`name` must not be blank.')

        return self._get_action_class()(
            self._client,
            f'{self._path}/{name}',
        )

    def help(self):
        self._client.print_help(self)
        return self

    def _get_resource_class(self):
        return NotImplementedError()  # pragma: no cover

    def _get_resourceset_class(self):
        return NotImplementedError()  # pragma: no cover

    def _get_action_class(self):
        raise NotImplementedError()  # pragma: no cover


class Collection(_CollectionBase, CollectionMixin):
    def _get_resource_class(self):
        return Resource

    def _get_resourceset_class(self):
        return ResourceSet

    def _get_action_class(self):
        return Action


class AsyncCollection(_CollectionBase, AsyncCollectionMixin):
    def _get_resource_class(self):
        return AsyncResource

    def _get_resourceset_class(self):
        return AsyncResourceSet

    def _get_action_class(self):
        return AsyncAction


class _ResourceBase:
    def __init__(self, client, path):
        self._client = client
        self._path = path

    @property
    def path(self):
        return self._path

    def __getattr__(self, name):
        if '_' in name:
            name = name.replace('_', '-')
        return self.collection(name)

    def __call__(self, name):
        return self.action(name)

    def collection(self, name: str):
        """
        Returns a `[Async]Collection` object nested under this resource object
        identified by its name.

        Usage:

        ```py3
        environments = (
            client.ns("devops")
            .collection("services")
            .resource("SRVC-0000-1111")
            .collection("environments")
        )
        ```

        Concise form:

        ```py3
        services = client('devops').services['SRVC-0000-1111'].environments
        ```

        Args:
            name (str): The name of the collection to access.

        Returns:
            (Union[Collection, AsyncCollection]): Returns an object nested under this resource
                object identified by its name.
        """  # noqa: E501
        if not isinstance(name, str):
            raise TypeError('`name` must be a string.')

        if not name:
            raise ValueError('`name` must not be blank.')

        return self._get_collection_class()(
            self._client,
            f'{self._path}/{name}',
        )

    def action(self, name: str):
        """
        Returns an `[Async]Action` object that can be performed on this this resource object
        identified by its name.

        Usage:

        ```py3
        approve_action = (
            client.collection('requests')
            .resource('PR-000-111-222')
            .action('approve')
        )
        ```

        Concise form:

        ```py3
        approve_action = client.requests[''PR-000-111-222']('approve')
        ```

        Args:
            name (str): The name of the action to perform.

        Returns:
            (Union[Action, AsyncAction]): Returns an object that can be performed on this this
                resource object identified by its name.
        """
        if not isinstance(name, str):
            raise TypeError('`name` must be a string.')

        if not name:
            raise ValueError('`name` must not be blank.')

        return self._get_action_class()(
            self._client,
            f'{self._path}/{name}',
        )

    def help(self):
        self._client.print_help(self)
        return self

    def _get_collection_class(self):
        raise NotImplementedError()

    def _get_action_class(self):
        raise NotImplementedError()


class Resource(_ResourceBase, ResourceMixin):
    def _get_collection_class(self):
        return Collection

    def _get_action_class(self):
        return Action


class AsyncResource(_ResourceBase, AsyncResourceMixin):
    def _get_collection_class(self):
        return AsyncCollection

    def _get_action_class(self):
        return AsyncAction


class _ActionBase:
    def __init__(self, client, path):
        self._client = client
        self._path = path

    @property
    def path(self):
        return self._path

    def help(self):
        self._client.print_help(self)
        return self


class Action(_ActionBase, ActionMixin):
    pass


class AsyncAction(_ActionBase, AsyncActionMixin):
    pass
