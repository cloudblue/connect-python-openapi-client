#
# This file is part of the Ingram Micro CloudBlue Connect Python OpenAPI Client.
#
# Copyright (c) 2021 Ingram Micro. All Rights Reserved.
#
import time

import httpx

import requests

from httpx import HTTPError

from requests.exceptions import RequestException, Timeout

from connect.client.exceptions import ClientError


class SyncClientMixin:

    def get(self, url, **kwargs):
        return self.execute('get', url, **kwargs)

    def create(self, url, payload=None, **kwargs):
        kwargs = kwargs or {}

        if payload:
            kwargs['json'] = payload

        return self.execute('post', url, **kwargs)

    def update(self, url, payload=None, **kwargs):
        kwargs = kwargs or {}

        if payload:
            kwargs['json'] = payload

        return self.execute('put', url, **kwargs)

    def delete(self, url, **kwargs):
        return self.execute('delete', url, **kwargs)

    def execute(self, method, path, **kwargs):
        if (
            self._use_specs
            and self._validate_using_specs
            and not self.specs.exists(method, path)
        ):
            # TODO more info, specs version, method etc
            raise ClientError(f'The path `{path}` does not exist.')

        url = f'{self.endpoint}/{path}'

        kwargs = self._prepare_call_kwargs(kwargs)

        self.response = None

        try:
            self._execute_http_call(method, url, kwargs)

            if self.response.status_code == 204:
                return None
            if self.response.headers.get('Content-Type', '').startswith('application/json'):
                return self.response.json()
            else:
                return self.response.content

        except RequestException as re:
            api_error = self._get_api_error_details() or {}
            status_code = self.response.status_code if self.response is not None else None
            raise ClientError(status_code=status_code, **api_error) from re

    def _execute_http_call(self, method, url, kwargs):  # noqa: CCR001
        retry_count = 0
        while True:
            if self.logger:
                self.logger.log_request(method, url, kwargs)
            try:
                self.response = requests.request(method, url, **kwargs)
                if self.logger:
                    self.logger.log_response(self.response)
            except Timeout:
                if retry_count < self.max_retries:
                    retry_count += 1
                    time.sleep(1)
                    continue
                raise

            if (  # pragma: no branch
                self.response.status_code >= 500
                and retry_count < self.max_retries
            ):
                retry_count += 1
                time.sleep(1)
                continue
            break  # pragma: no cover
        if self.response.status_code >= 400:
            self.response.raise_for_status()


class AsyncClientMixin:

    async def get(self, url, **kwargs):
        return await self.execute('get', url, **kwargs)

    async def create(self, url, payload=None, **kwargs):
        kwargs = kwargs or {}

        if payload:
            kwargs['json'] = payload

        return await self.execute('post', url, **kwargs)

    async def update(self, url, payload=None, **kwargs):
        kwargs = kwargs or {}

        if payload:
            kwargs['json'] = payload

        return await self.execute('put', url, **kwargs)

    async def delete(self, url, **kwargs):
        return await self.execute('delete', url, **kwargs)

    async def execute(self, method, path, **kwargs):
        if (
            self._use_specs
            and self._validate_using_specs
            and not self.specs.exists(method, path)
        ):
            # TODO more info, specs version, method etc
            raise ClientError(f'The path `{path}` does not exist.')

        url = f'{self.endpoint}/{path}'

        kwargs = self._prepare_call_kwargs(kwargs)

        url, kwargs = self._fix_url_params(url, kwargs)

        self.response = None

        try:
            await self._execute_http_call(method, url, kwargs)
            if self.response.status_code == 204:
                return None
            if self.response.headers.get('Content-Type', '').startswith('application/json'):
                return self.response.json()
            else:
                return self.response.content

        except HTTPError as re:
            api_error = self._get_api_error_details() or {}
            status_code = self.response.status_code if self.response is not None else None
            raise ClientError(status_code=status_code, **api_error) from re

    async def _execute_http_call(self, method, url, kwargs):
        retry_count = 0
        while True:
            if self.logger:
                self.logger.log_request(method, url, kwargs)

            async with httpx.AsyncClient() as client:
                self.response = await client.request(method, url, **kwargs)

            if self.logger:
                self.logger.log_response(self.response)

            if (  # pragma: no branch
                self.response.status_code >= 500
                and retry_count < self.max_retries
            ):
                retry_count += 1
                time.sleep(1)
                continue
            break  # pragma: no cover
        if self.response.status_code >= 400:
            self.response.raise_for_status()

    def _fix_url_params(self, url, kwargs):
        if 'params' in kwargs:
            params = kwargs.pop('params')
            qs_fragment = '&'.join([f'{k}={v}' for k, v in params.items()])
            join = '?' if '?' not in url else '&'
            url = f'{url}{join}{qs_fragment}'
        return url, kwargs
