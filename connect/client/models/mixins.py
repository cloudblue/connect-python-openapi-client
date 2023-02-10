#
# This file is part of the Ingram Micro CloudBlue Connect Python OpenAPI Client.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
from typing import (
    Any,
    Dict,
    List,
    Tuple,
    Union,
)

from connect.client.exceptions import ClientError
from connect.client.utils import resolve_attribute


class CollectionMixin:
    def create(self, payload: Dict = None, **kwargs) -> Any:
        """
        Create a new resource within this collection.

        Usage:

        ```py3
        case = client.ns('helpdesk').collection('cases').create(
            payload={
                'subject': 'I have a question / problem',
                'description': 'Need help with contracts management.',
                'priority': 0,
                'state': 'pending',
                'type': 'business',
                'issuer': {
                    'recipients': [
                        {
                            'id': 'UR-012-345-678'
                        }
                    ]
                },
                'receiver': {
                    'account': {
                        'id': 'PA-111-222'
                    }
                }
            }
        )
        ```

        Concise form:

        ```py3
        case = client('helpdesk').cases.create(
            payload={
                'subject': 'I have a question / problem',
                'description': 'Need help with contracts management.',
                'priority': 0,
                'state': 'pending',
                'type': 'business',
                'issuer': {
                    'recipients': [
                        {
                            'id': 'UR-012-345-678'
                        }
                    ]
                },
                'receiver': {
                    'account': {
                        'id': 'PA-111-222'
                    }
                }
            }
        )
        ```

        Args:
            payload (dict): The payload of the resource to create.
        """
        if payload is not None and not isinstance(payload, dict):
            raise TypeError('`payload` must be a dict.')

        return self._client.create(
            self._path,
            payload=payload,
            **kwargs,
        )

    def bulk_create(self, payload: Union[List, Tuple], **kwargs):
        """
        Create a set of resources within this collection in a single call.

        Usage:

        ```py3
        translations = client.ns('localization').collection('translations').bulk_create(
            payload=[
                {
                    'context': {
                        'id': 'LCX-1234-1234-123'
                    },
                    'locale': {
                        'id': 'ES-MX'
                    },
                    'description': 'Awesome Mexican Spanish locale',
                    'auto': {
                        'enabled': True
                    }
                },
                {
                    'context': {
                        'id': 'LCX-1234-1234-123'
                    },
                    'locale': {
                        'id': 'ES'
                    },
                    'description': 'Awesome Spanish locale',
                    'auto': {
                        'enabled': False
                    }
                }
            ]
        )
        ```

        Concise form:

        ```py3
        translations = client('localization').translations.bulk_create(
            payload=[
                {
                    'context': {
                        'id': 'LCX-1234-1234-123'
                    },
                    'locale': {
                        'id': 'ES-MX'
                    },
                    'description': 'Awesome Mexican Spanish locale',
                    'auto': {
                        'enabled': True
                    }
                },
                {
                    'context': {
                        'id': 'LCX-1234-1234-123'
                    },
                    'locale': {
                        'id': 'ES'
                    },
                    'description': 'Awesome Spanish locale',
                    'auto': {
                        'enabled': False
                    }
                }
            ]
        )
        ```

        Args:
            payload (list|tuple): The list of objects to create.
        """
        if not isinstance(payload, (list, tuple)):
            raise TypeError('`payload` must be a list or tuple.')

        return self._client.create(
            self._path,
            payload=payload,
            **kwargs,
        )

    def bulk_update(self, payload: Union[List, Tuple], **kwargs):
        """
        Update a set of resources that belong to this collection in a single call.

        Usage:

        ```py3
        translations = client.ns('localization').collection('translations').bulk_update(
            payload=[
                {
                    'id': 'TRN-6783-3216-8782',
                    'description': 'Awesome English locale',
                    'auto': {
                        'enabled': True
                    }
                },
                {
                    'id': 'TRN-6783-0001-8782',
                    'description': 'Awesome Spanish locale'
                }
            ]
        )
        ```

        Concise form:

        ```py3
        translations = client('localization').translations.bulk_update(
            payload=[
                {
                    'id': 'TRN-6783-3216-8782',
                    'description': 'Awesome English locale',
                    'auto': {
                        'enabled': True
                    }
                },
                {
                    'id': 'TRN-6783-0001-8782',
                    'description': 'Awesome Spanish locale'
                }
            ]
        )
        ```

        Args:
            payload (list|tuple): The list of objects to update.
        """
        if not isinstance(payload, (list, tuple)):
            raise TypeError('`payload` must be a list or tuple.')

        return self._client.update(
            self._path,
            payload=payload,
            **kwargs,
        )

    def bulk_delete(self, payload: Union[List, Tuple], **kwargs):
        """
        Delete a set of resources from within this collection in a single call.

        Usage:

        ```py3
        client.ns('localization').collection('translations').bulk_delete(
            payload=[
                {
                    'id': 'TRN-6783-3216-8782'
                },
                {
                    'id': 'TRN-6783-0001-8782'
                }
            ]
        )
        ```

        Concise form:

        ```py3
        client('localization').translations.bulk_delete(
            payload=[
                {
                    'id': 'TRN-6783-3216-8782',
                },
                {
                    'id': 'TRN-6783-0001-8782',
                }
            ]
        )
        ```

        Args:
            payload (list|tuple): The list of objects to update.
        """
        if not isinstance(payload, (list, tuple)):
            raise TypeError('`payload` must be a list or tuple.')

        self._client.delete(
            self._path,
            payload=payload,
            **kwargs,
        )


class AsyncCollectionMixin:
    async def create(self, payload: Dict = None, **kwargs):
        """
        Create a new resource within this collection.

        Usage:

        ```py3
        case = await client.ns('helpdesk').collection('cases').create(
            payload={
                'subject': 'I have a question / problem',
                'description': 'Need help with contracts management.',
                'priority': 0,
                'state': 'pending',
                'type': 'business',
                'issuer': {
                    'recipients': [
                        {
                            'id': 'UR-012-345-678'
                        }
                    ]
                },
                'receiver': {
                    'account': {
                        'id': 'PA-111-222'
                    }
                }
            }
        )
        ```

        Concise form:

        ```py3
        case = await client('helpdesk').cases.create(
            payload={
                'subject': 'I have a question / problem',
                'description': 'Need help with contracts management.',
                'priority': 0,
                'state': 'pending',
                'type': 'business',
                'issuer': {
                    'recipients': [
                        {
                            'id': 'UR-012-345-678'
                        }
                    ]
                },
                'receiver': {
                    'account': {
                        'id': 'PA-111-222'
                    }
                }
            }
        )
        ```

        Args:
            payload (dict): The payload of the resource to create.
        """
        if payload is not None and not isinstance(payload, dict):
            raise TypeError('`payload` must be a dict.')

        return await self._client.create(
            self._path,
            payload=payload,
            **kwargs,
        )

    async def bulk_create(self, payload: Union[List, Tuple], **kwargs):
        """
        Create a set of resources within this collection in a single call.

        Usage:

        ```py3
        translations = await client.ns('localization').collection('translations').bulk_create(
            payload=[
                {
                    'context': {
                        'id': 'LCX-1234-1234-123'
                    },
                    'locale': {
                        'id': 'ES-MX'
                    },
                    'description': 'Awesome Mexican Spanish locale',
                    'auto': {
                        'enabled': True
                    }
                },
                {
                    'context': {
                        'id': 'LCX-1234-1234-123'
                    },
                    'locale': {
                        'id': 'ES'
                    },
                    'description': 'Awesome Spanish locale',
                    'auto': {
                        'enabled': False
                    }
                }
            ]
        )
        ```

        Concise form:

        ```py3
        translations = await client('localization').translations.bulk_create(
            payload=[
                {
                    'context': {
                        'id': 'LCX-1234-1234-123'
                    },
                    'locale': {
                        'id': 'ES-MX'
                    },
                    'description': 'Awesome Mexican Spanish locale',
                    'auto': {
                        'enabled': True
                    }
                },
                {
                    'context': {
                        'id': 'LCX-1234-1234-123'
                    },
                    'locale': {
                        'id': 'ES'
                    },
                    'description': 'Awesome Spanish locale',
                    'auto': {
                        'enabled': False
                    }
                }
            ]
        )
        ```

        Args:
            payload (list|tuple): The list of objects to create.
        """
        if not isinstance(payload, (list, tuple)):
            raise TypeError('`payload` must be a list or tuple.')

        return await self._client.create(
            self._path,
            payload=payload,
            **kwargs,
        )

    async def bulk_update(self, payload: Union[List, Tuple], **kwargs):
        """
        Update a set of resources that belong to this collection in a single call.

        Usage:

        ```py3
        translations = await client.ns('localization').collection('translations').bulk_update(
            payload=[
                {
                    'id': 'TRN-6783-3216-8782',
                    'description': 'Awesome English locale',
                    'auto': {
                        'enabled': True
                    }
                },
                {
                    'id': 'TRN-6783-0001-8782',
                    'description': 'Awesome Spanish locale'
                }
            ]
        )
        ```

        Concise form:

        ```py3
        translations = await client('localization').translations.bulk_update(
            payload=[
                {
                    'id': 'TRN-6783-3216-8782',
                    'description': 'Awesome English locale',
                    'auto': {
                        'enabled': True
                    }
                },
                {
                    'id': 'TRN-6783-0001-8782',
                    'description': 'Awesome Spanish locale'
                }
            ]
        )
        ```

        Args:
            payload (list|tuple): The list of objects to update.
        """
        if not isinstance(payload, (list, tuple)):
            raise TypeError('`payload` must be a list or tuple.')

        return await self._client.update(
            self._path,
            payload=payload,
            **kwargs,
        )

    async def bulk_delete(self, payload: Union[List, Tuple], **kwargs):
        """
        Delete a set of resources from within this collection in a single call.

        Usage:

        ```py3
        await client.ns('localization').collection('translations').bulk_delete(
            payload=[
                {
                    'id': 'TRN-6783-3216-8782'
                },
                {
                    'id': 'TRN-6783-0001-8782'
                }
            ]
        )
        ```

        Concise form:

        ```py3
        await client('localization').translations.bulk_delete(
            payload=[
                {
                    'id': 'TRN-6783-3216-8782',
                },
                {
                    'id': 'TRN-6783-0001-8782',
                }
            ]
        )
        ```

        Args:
            payload (list|tuple): The list of objects to update.
        """
        if not isinstance(payload, (list, tuple)):
            raise TypeError('`payload` must be a list or tuple.')

        return await self._client.delete(
            self._path,
            payload=payload,
            **kwargs,
        )


class ResourceMixin:
    def exists(self) -> bool:
        """
        Return True if the resource this `Resource` object refers to exists.

        Usage:

        ```py3
        if client.collection('products').resource('PRD-000-111-222').exits():
            ...
        ```

        Concise form:

        ```py3
        if client.products['PRD-000-111-222'].exists():
            ...
        ```

        Returns:
            (bool): Return True if the resource this `Resource` object refers to exists.
        """
        try:
            self.get()
            return True
        except ClientError as ce:
            if ce.status_code and ce.status_code == 404:
                return False
            raise

    def get(self, **kwargs) -> Dict:
        """
        Retrieve the resource this `Resource` object refers to.

        Usage:

        ```py3
        product = client.collection('products').resource('PRD-000-111-222').get()
        ```

        Concise form:

        ```py3
        product = client.products['PRD-000-111-222'].get()
        ```
        """
        return self._client.get(self._path, **kwargs)

    def update(self, payload: Dict = None, **kwargs) -> Dict:
        """
        Update the resource this `Resource` object refers to.

        Usage:

        ```py3
        product = client.collection('products').resource('PRD-000-111-222').update(
            payload={
                'name': 'Cool product'
            }
        )
        ```

        Concise form:

        ```py3
        product = client.products['PRD-000-111-222'].update(
            payload={
                'name': 'Cool product'
            }
        )
        ```

        Args:
            payload (dict): The payload of the update operations.
        """
        return self._client.update(
            self._path,
            payload=payload,
            **kwargs,
        )

    def delete(self, **kwargs):
        """
        Delete the resource this `Resource` object refers to.

        Usage:

        ```py3
        client.collection('products').resource('PRD-000-111-222').delete()
        ```

        Concise form:

        ```py3
        client.products['PRD-000-111-222'].delete()
        ```
        """
        return self._client.delete(
            self._path,
            **kwargs,
        )

    def values(self, *fields) -> Dict:
        """
        Returns a flat dictionary containing only the fields of this resource
        passed as arguments.

        !!! note
            Nested field can be specified using dot notation.

        Usage:

        ```py3
        values = resource.values('field', 'nested.field')
        ```

        Returns:
            (dict): Returns a flat dictionary containing only the fields of this resource
                passed as arguments.
        """
        results = {}
        item = self.get()
        for field in fields:
            results[field] = resolve_attribute(field, item)
        return results


class AsyncResourceMixin:
    async def exists(self) -> bool:
        """
        Return True if the resource this `Resource` object refers to exists.

        Usage:

        ```py3
        if await client.collection('products').resource('PRD-000-111-222').exits():
            ...
        ```

        Concise form:

        ```py3
        if await client.products['PRD-000-111-222'].exists():
            ...
        ```

        Returns:
            (bool): Return True if the resource this `Resource` object refers to exists.
        """
        try:
            await self.get()
            return True
        except ClientError as ce:
            if ce.status_code and ce.status_code == 404:
                return False
            raise

    async def get(self, **kwargs) -> Dict:
        """
        Retrieve the resource this `Resource` object refers to.

        Usage:

        ```py3
        product = await client.collection('products').resource('PRD-000-111-222').get()
        ```

        Concise form:

        ```py3
        product = await client.products['PRD-000-111-222'].get()
        ```

        Returns:
            (dict): Returns the resource this `Resource` object refers to.
        """
        return await self._client.get(self._path, **kwargs)

    async def update(self, payload=None, **kwargs) -> Dict:
        """
        Update the resource this `Resource` object refers to.

        Usage:

        ```py3
        product = await client.collection('products').resource('PRD-000-111-222').update(
            payload={
                'name': 'Cool product'
            }
        )
        ```

        Concise form:

        ```py3
        product = await client.products['PRD-000-111-222'].update(
            payload={
                'name': 'Cool product'
            }
        )
        ```

        Args:
            payload (dict): The payload of the update operations.

        Returns:
            (dict): Returns the updated object.
        """
        return await self._client.update(
            self._path,
            payload=payload,
            **kwargs,
        )

    async def delete(self, **kwargs):
        """
        Delete the resource this `Resource` object refers to.

        Usage:

        ```py3
        await client.collection('products').resource('PRD-000-111-222').delete()
        ```

        Concise form:

        ```py3
        await client.products['PRD-000-111-222'].delete()
        ```
        """
        return await self._client.delete(
            self._path,
            **kwargs,
        )

    async def values(self, *fields) -> Dict:
        """
        Returns a flat dictionary containing only the fields of this resource
        passed as arguments.

        !!! note
            Nested field can be specified using dot notation.

        Usage:

        ```py3
        values = await resource.values('field', 'nested.field')
        ```

        Returns:
            (dict): Returns a flat dictionary containing only the fields of this resource
                passed as arguments.
        """
        results = {}
        item = await self.get()
        for field in fields:
            results[field] = resolve_attribute(field, item)
        return results


class ActionMixin:
    def get(self, **kwargs):
        """
        Execute the action this `Action` object refers to using the
        `GET` HTTP verb.

        Usage:

        ```py3
        xlsx = (
            client.ns('devops')
            .collection('services')
            .resource('SRVC-0000-1111')
            .collection('environments')
            .resource('ENV-0000-1111-01')
            .collection('variables')
            .action('export')
            .get()
        )
        ```

        Concise form:

        ```py3
        xlsx = (
            client('devops')
            .services['SRVC-0000-1111']
            .environments['ENV-0000-1111-01']
            .variables('export').get()
        )
        ```
        """
        return self._client.get(self._path, **kwargs)

    def post(self, payload: Dict = None, **kwargs):
        """
        Execute the action this `Action` object refers to using the
        `POST` HTTP verb.

        Usage:

        ```py3
        product = (
            client.collection('products')
            .resource('PRD-000-111-222')
            .action('endsale')
            .post(
                payload={
                    'replacement': {'id': 'PRD-333-444-555'},
                    'end_of_sale_notes': 'Obsolete product'
                }
            )
        )
        ```

        Concise form:

        ```py3
        product = client.products['PRD-000-111-222']('endsale').post(
            payload={
                'replacement': {'id': 'PRD-333-444-555'},
                'end_of_sale_notes': 'Obsolete product'
            }
        )
        ```

        Args:
            payload (dict): The payload needed to perform this action.
        """
        if payload:
            kwargs['json'] = payload
        return self._client.execute(
            'post',
            self._path,
            **kwargs,
        )

    def put(self, payload: Dict = None, **kwargs):
        """
        Execute the action this `Action` object refers to using the
        `PUT` HTTP verb.

        Args:
            payload (dict): The payload needed to perform this action.
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
        Execute the action this `Action` object refers to using the
        `DELETE` HTTP verb.
        """
        return self._client.delete(
            self._path,
            **kwargs,
        )


class AsyncActionMixin:
    async def get(self, **kwargs):
        """
        Execute the action this `Action` object refers to using the
        `GET` HTTP verb.

        Usage:

        ```py3
        xlsx = await (
            client.ns('devops')
            .collection('services')
            .resource('SRVC-0000-1111')
            .collection('environments')
            .resource('ENV-0000-1111-01')
            .collection('variables')
            .action('export')
            .get()
        )
        ```

        Concise form:

        ```py3
        xlsx = await (
            client('devops')
            .services['SRVC-0000-1111']
            .environments['ENV-0000-1111-01']
            .variables('export').get()
        )
        ```
        """
        return await self._client.get(self._path, **kwargs)

    async def post(self, payload: Dict = None, **kwargs):
        """
        Execute the action this `Action` object refers to using the
        `POST` HTTP verb.

        Usage:

        ```py3
        product = await (
            client.collection('products')
            .resource('PRD-000-111-222')
            .action('endsale')
            .post(
                payload={
                    'replacement': {'id': 'PRD-333-444-555'},
                    'end_of_sale_notes': 'Obsolete product'
                }
            )
        )
        ```

        Concise form:

        ```py3
        product = await client.products['PRD-000-111-222']('endsale').post(
            payload={
                'replacement': {'id': 'PRD-333-444-555'},
                'end_of_sale_notes': 'Obsolete product'
            }
        )
        ```

        Args:
            payload (dict): The payload needed to perform this action.
        """
        if payload:
            kwargs['json'] = payload
        return await self._client.execute(
            'post',
            self._path,
            **kwargs,
        )

    async def put(self, payload: Dict = None, **kwargs):
        """
        Execute the action this `Action` object refers to using the
        `PUT` HTTP verb.

        Args:
            payload (dict): The payload needed to perform this action.
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
        Execute the action this `Action` object refers to using the
        `DELETE` HTTP verb.
        """
        return await self._client.delete(
            self._path,
            **kwargs,
        )
