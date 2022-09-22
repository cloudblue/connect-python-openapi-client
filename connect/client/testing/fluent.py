#
# This file is part of the Ingram Micro CloudBlue Connect Python OpenAPI Client.
#
# Copyright (c) 2021 Ingram Micro. All Rights Reserved.
#
import httpx

import responses

from pytest import MonkeyPatch

from pytest_httpx import HTTPXMock
from pytest_httpx._httpx_mock import _PytestAsyncTransport

from connect.client.fluent import _ConnectClientBase
from connect.client.testing.models import CollectionMock, NSMock


class ConnectClientMocker(_ConnectClientBase):
    def __init__(self, base_url):
        super().__init__('api_key', endpoint=base_url)
        self._mocker = responses.RequestsMock()

    def get(
        self,
        url,
        status_code=200,
        return_value=None,
        headers=None,
    ):
        return self.mock(
            'get',
            url,
            status_code=status_code,
            return_value=return_value,
            headers=headers,
        )

    def create(
        self,
        url,
        status_code=201,
        return_value=None,
        headers=None,
    ):

        return self.mock(
            'post',
            url,
            status_code=status_code,
            return_value=return_value,
            headers=headers,
        )

    def update(
        self,
        url,
        status_code=201,
        return_value=None,
        headers=None,
    ):

        return self.mock(
            'put',
            url,
            status_code=status_code,
            return_value=return_value,
            headers=headers,
        )

    def delete(
        self,
        url,
        status_code=204,
        return_value=None,
        headers=None,
    ):

        return self.mock(
            'delete',
            url,
            status_code=status_code,
            return_value=return_value,
            headers=headers,
        )

    def mock(
        self,
        method,
        path,
        status_code=200,
        return_value=None,
        headers=None,
    ):
        url = f'{self.endpoint}/{path}'

        kwargs = {
            'method': method.upper(),
            'url': url,
            'status': status_code,
            'headers': headers,
        }

        if isinstance(return_value, (dict, list, tuple)):
            kwargs['json'] = return_value
        else:
            kwargs['body'] = return_value

        self._mocker.add(**kwargs)

    def start(self):
        self._mocker.start()

    def reset(self, success=True):
        self._mocker.stop(allow_assert=success)
        self._mocker.reset()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, value, traceback):
        self.reset(success=exc_type is None)

    def _get_collection_class(self):
        return CollectionMock

    def _get_namespace_class(self):
        return NSMock


class AsyncConnectClientMocker(ConnectClientMocker):
    def __init__(self, base_url):
        super().__init__(base_url)
        self._monkeypatch = None
        self._mocker = None

    def start(self):
        self._monkeypatch = MonkeyPatch()
        self._mocker = HTTPXMock()

        mocker = self._mocker

        self._monkeypatch.setattr(
            httpx.AsyncClient,
            '_transport_for_url',
            lambda self, url: _PytestAsyncTransport(mocker),
        )

    def reset(self, success=True):
        self._mocker.reset(success)
        self._monkeypatch.undo()
        self._mocker = None
        self._monkeypatch = None

    def mock(
        self,
        method,
        path,
        status_code=200,
        return_value=None,
        headers=None,
    ):
        url = f'{self.endpoint}/{path}'

        kwargs = {
            'method': method.upper(),
            'url': url,
            'status_code': status_code,
            'headers': headers,
        }

        if isinstance(return_value, (dict, list, tuple)):
            kwargs['json'] = return_value
        else:
            kwargs['content'] = return_value.encode() if return_value else None

        self._mocker.add_response(**kwargs)
