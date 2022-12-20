import time

from locust import HttpUser
from requests import RequestException

from connect.client import ConnectClient


class _LocustConnectClient(ConnectClient):
    def __init__(self, base_url, request_event, user, *args, **kwargs):
        self.base_url = base_url
        self.request_event = request_event
        self.user = user

        super().__init__(
            kwargs['connect_api_key'],
            self.base_url,
            use_specs=False,
            max_retries=0,
            timeout=(5, 120),
        )

    def _execute_http_call(self, method, url, kwargs):
        start_time = time.perf_counter()
        exc = None
        try:
            super()._execute_http_call(method, url, kwargs)
        except RequestException as e:
            exc = e

        response = self.response.history and self.response.history[0] or self.response
        request_meta = {
            'request_type': method,
            'response_time': (time.perf_counter() - start_time) * 1000,
            'name': response.request.path_url,
            'context': {},
            'response': self.response,
            'exception': exc,
            'response_length': len(self.response.content or b''),
        }

        self.request_event.fire(**request_meta)


class ConnectHttpUser(HttpUser):
    abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.client = _LocustConnectClient(
            self.host,
            request_event=self.environment.events.request,
            user=self,
            connect_api_key=self.environment.parsed_options.connect_api_key,
        )
