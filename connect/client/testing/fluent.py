#
# This file is part of the Ingram Micro CloudBlue Connect Python OpenAPI Client.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
import json
import re

import httpx
import responses
from pytest import MonkeyPatch
from pytest_httpx import HTTPXMock
from responses import matchers

from connect.client.fluent import _ConnectClientBase
from connect.client.testing.models import CollectionMock, NSMock


def body_matcher(body):
    def match(request):
        request_body = request.body
        valid = body is None if request_body is None else body == request_body
        if not valid:
            return False, "%s doesn't match %s" % (request_body, body)

        return valid, ''

    return match


_mocker = responses.RequestsMock()


class ConnectClientMocker(_ConnectClientBase):
    def __init__(self, base_url, exclude=None):
        super().__init__('api_key', endpoint=base_url)
        if exclude:
            if not isinstance(exclude, (list, tuple, set)):
                exclude = [exclude]
            for item in exclude:
                _mocker.add_passthru(item)

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

        _mocker.add(**kwargs)

    def start(self):
        _mocker.start()

    def reset(self, success=True):
        try:
            _mocker.stop(allow_assert=success)
        finally:
            _mocker.reset()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, value, traceback):
        self.reset(success=exc_type is None)

    def _get_collection_class(self):
        return CollectionMock

    def _get_namespace_class(self):
        return NSMock


_monkeypatch = MonkeyPatch()
_async_mocker = HTTPXMock()


class AsyncConnectClientMocker(ConnectClientMocker):
    def __init__(self, base_url, exclude=None):
        super().__init__(base_url)
        self.exclude = exclude or []

    def start(self):
        patterns = self.exclude if isinstance(self.exclude, (list, tuple, set)) else [self.exclude]
        real_handle_async_request = httpx.AsyncHTTPTransport.handle_async_request

        async def mocked_handle_async_request(
            transport: httpx.AsyncHTTPTransport, request: httpx.Request
        ) -> httpx.Response:
            for pattern in patterns:
                if (isinstance(pattern, re.Pattern) and pattern.match(str(request.url))) or (
                    isinstance(pattern, str) and str(request.url).startswith(pattern)
                ):
                    return await real_handle_async_request(transport, request)
            return await _async_mocker._handle_async_request(transport, request)

        _monkeypatch.setattr(
            httpx.AsyncHTTPTransport,
            "handle_async_request",
            mocked_handle_async_request,
        )

    def reset(self, success=True):
        _async_mocker.reset(success)
        _monkeypatch.undo()

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

        _async_mocker.add_response(**kwargs)


def get_requests_mocker():
    """
    Returns a mocker object to mock http calls made using the `requests` library
    when they are made in conjunction with calls made with the `ConnectClient`.
    The returned mocker is the one provided by the
    [responses](https://github.com/getsentry/responses) library.
    """
    return _mocker


def get_httpx_mocker():
    """
    Returns a mocker object to mock http calls made using the `httpx` library
    when they are made in conjunction with calls made with the `AsyncConnectClient`.
    The returned mocker is the one provided by the
    [pytest-httpx](https://colin-b.github.io/pytest_httpx/) library.
    """
    return _async_mocker
