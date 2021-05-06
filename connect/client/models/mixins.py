#
# This file is part of the Ingram Micro CloudBlue Connect Python OpenAPI Client.
#
# Copyright (c) 2021 Ingram Micro. All Rights Reserved.
#
from connect.client.exceptions import ClientError
from connect.client.utils import resolve_attribute


class CollectionMixin:
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


class AsyncCollectionMixin:
    async def create(self, payload=None, **kwargs):
        """
        Create a new resource within this collection.

        :param payload: JSON payload of the resource to create, defaults to None.
        :type payload: dict, optional
        :return: The newly created resource.
        :rtype: dict
        """
        return await self._client.create(
            self._path,
            payload=payload,
            **kwargs,
        )


class ResourceMixin:
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


class AsyncResourceMixin:
    async def exists(self):
        try:
            await self.get()
            return True
        except ClientError as ce:
            if ce.status_code and ce.status_code == 404:
                return False
            raise

    async def get(self, **kwargs):
        """
        Execute a http GET to retrieve this resource.
        The http GET can be customized passing kwargs that
        will be forwarded to the underlying GET of the ``requests``
        library.

        :return: The resource data.
        :rtype: dict
        """
        return await self._client.get(self._path, **kwargs)

    async def update(self, payload=None, **kwargs):
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
        return await self._client.update(
            self._path,
            payload=payload,
            **kwargs,
        )

    async def delete(self, **kwargs):
        """
        Execute a http DELETE to delete this resource.
        The http DELETE can be customized passing kwargs that
        will be forwarded to the underlying DELETE of the ``requests``
        library.
        """
        return await self._client.delete(
            self._path,
            **kwargs,
        )

    async def values(self, *fields):
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
        item = await self.get()
        for field in fields:
            results[field] = resolve_attribute(field, item)
        return results


class ActionMixin:
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


class AsyncActionMixin:
    async def get(self, **kwargs):
        """
        Execute this action through a http GET.
        The http GET can be customized passing kwargs that
        will be forwarded to the underlying GET of the ``requests``
        library.

        :return: The action data.
        :rtype: dict, None
        """
        return await self._client.get(self._path, **kwargs)

    async def post(self, payload=None, **kwargs):
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
        return await self._client.execute(
            'post',
            self._path,
            **kwargs,
        )

    async def put(self, payload=None, **kwargs):
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
        return await self._client.execute(
            'put',
            self._path,
            **kwargs,
        )

    async def delete(self, **kwargs):
        """
        Execute this action through a http DELETE.
        The http DELETE can be customized passing kwargs that
        will be forwarded to the underlying DELETE of the ``requests``
        library.
        """
        return await self._client.delete(
            self._path,
            **kwargs,
        )
