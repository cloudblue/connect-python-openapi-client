#
# This file is part of the Ingram Micro CloudBlue Connect Python OpenAPI Client.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#


class CollectionMixin:
    def create(
        self,
        status_code=201,
        return_value=None,
        headers=None,
        match_body=None,
    ):
        return self._client.create(
            self._path,
            status_code=status_code,
            return_value=return_value,
            headers=headers,
            match_body=match_body,
        )

    def bulk_create(
        self,
        status_code=201,
        return_value=None,
        headers=None,
        match_body=None,
    ):
        return self._client.create(
            self._path,
            status_code=status_code,
            return_value=return_value,
            headers=headers,
            match_body=match_body,
        )

    def bulk_update(
        self,
        status_code=200,
        return_value=None,
        headers=None,
        match_body=None,
    ):
        return self._client.update(
            self._path,
            status_code=status_code,
            return_value=return_value,
            headers=headers,
            match_body=match_body,
        )

    def bulk_delete(
        self,
        status_code=204,
        return_value=None,
        headers=None,
        match_body=None,
    ):
        return self._client.delete(
            self._path,
            status_code=status_code,
            return_value=return_value,
            headers=headers,
            match_body=match_body,
        )


class ResourceMixin:
    def exists(self, return_value):
        self.get(status_code=200 if return_value else 404)

    def get(
        self,
        status_code=200,
        return_value=None,
        headers=None,
    ):
        return self._client.get(
            self._path,
            status_code=status_code,
            return_value=return_value,
            headers=headers,
        )

    def update(
        self,
        status_code=200,
        return_value=None,
        headers=None,
        match_body=None,
    ):
        return self._client.update(
            self._path,
            status_code=status_code,
            return_value=return_value,
            headers=headers,
            match_body=match_body,
        )

    def delete(
        self,
        status_code=204,
        return_value=None,
        headers=None,
    ):
        return self._client.delete(
            self._path,
            status_code=status_code,
            return_value=return_value,
            headers=headers,
        )

    def values(
        self,
        status_code=200,
        return_value=None,
        headers=None,
    ):
        return self._client.get(
            self._path,
            status_code=status_code,
            return_value=return_value,
            headers=headers,
        )


class ActionMixin:
    def get(
        self,
        status_code=200,
        return_value=None,
        headers=None,
    ):
        return self._client.get(
            self._path,
            status_code=status_code,
            return_value=return_value,
            headers=headers,
        )

    def post(
        self,
        status_code=200,
        return_value=None,
        headers=None,
        match_body=None,
    ):
        return self._client.create(
            self._path,
            status_code=status_code,
            return_value=return_value,
            headers=headers,
            match_body=match_body,
        )

    def put(
        self,
        status_code=200,
        return_value=None,
        headers=None,
        match_body=None,
    ):
        return self._client.update(
            self._path,
            status_code=status_code,
            return_value=return_value,
            headers=headers,
            match_body=match_body,
        )

    def delete(
        self,
        status_code=204,
        return_value=None,
        headers=None,
    ):
        return self._client.delete(
            self._path,
            status_code=status_code,
            return_value=return_value,
            headers=headers,
        )
