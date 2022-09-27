#
# This file is part of the Ingram Micro CloudBlue Connect Python OpenAPI Client.
#
# Copyright (c) 2021 Ingram Micro. All Rights Reserved.
#
import json

import httpx

import responses
from responses import matchers

from pytest import MonkeyPatch

from pytest_httpx import HTTPXMock
from pytest_httpx._httpx_mock import _PytestAsyncTransport

from connect.client.fluent import _ConnectClientBase
from connect.client.testing.models import CollectionMock, NSMock


def body_matcher(body):
    def match(request):
        request_body = request.body
        valid = (
            body is None
            if request_body is None
            else body == request_body
        )
        if not valid:
            return False, "%s doesn't match %s" % (request_body, body)

        return valid, ""

    return match


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
        match_body=None,
    ):

        return self.mock(
            'post',
            url,
            status_code=status_code,
            return_value=return_value,
            headers=headers,
            match_body=match_body,
        )

    def update(
        self,
        url,
        status_code=201,
        return_value=None,
        headers=None,
        match_body=None,
    ):

        return self.mock(
            'put',
            url,
            status_code=status_code,
            return_value=return_value,
            headers=headers,
            match_body=match_body,
        )

    def delete(
        self,
        url,
        status_code=204,
        return_value=None,
        headers=None,
        match_body=None,
    ):

        return self.mock(
            'delete',
            url,
            status_code=status_code,
            return_value=return_value,
            headers=headers,
            match_body=match_body,
        )

    def mock(
        self,
        method,
        path,
        status_code=200,
        return_value=None,
        headers=None,
        match_body=None,
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

        if match_body:
            if isinstance(match_body, (dict, list, tuple)):
                kwargs['match'] = [
                    matchers.json_params_matcher(match_body),
                ]
            else:
                kwargs['match'] = [
                    body_matcher(match_body),
                ]

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
        match_body=None,
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

        if match_body:
            if isinstance(match_body, (dict, list, tuple)):
                kwargs['match_content'] = json.dumps(match_body).encode('utf-8')
            else:
                kwargs['match_content'] = match_body

        self._mocker.add_response(**kwargs)
