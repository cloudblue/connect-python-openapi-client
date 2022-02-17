import json
import sys


class RequestLogger:
    def __init__(self, file=sys.stdout):
        self._file = file

    def obfuscate(self, value):
        if value.startswith('ApiKey SU-'):
            return value.split(':')[0] + '*' * 10
        else:
            return '*' * 20

    def log_request(self, method, url, kwargs):
        other_args = {k: v for k, v in kwargs.items() if k not in ('headers', 'json', 'params')}

        if 'params' in kwargs:
            url += '&' if '?' in url else '?'
            url += '&'.join([f'{k}={v}' for k, v in kwargs['params'].items()])

        lines = [
            '--- HTTP Request ---',
            f'{method.upper()} {url} {other_args if other_args else ""}',
        ]

        if 'headers' in kwargs:
            for k, v in kwargs['headers'].items():
                if k == 'Authorization':
                    v = self.obfuscate(v)
                lines.append(f'{k}: {v}')

        if 'json' in kwargs:
            lines.append(json.dumps(kwargs['json'], indent=4))

        lines.append('')

        print(*lines, sep='\n', file=self._file)

    def log_response(self, response):
        reason = response.raw.reason if getattr(response, 'raw', None) else response.reason_phrase
        lines = [
            '--- HTTP Response ---',
            f'{response.status_code} {reason}',
        ]

        for k, v in response.headers.items():
            lines.append(f'{k}: {v}')

        if response.headers.get('Content-Type', None) == 'application/json':
            lines.append(json.dumps(response.json(), indent=4))

        lines.append('')

        print(*lines, sep='\n', file=self._file)
