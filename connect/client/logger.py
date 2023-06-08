import json
import sys


class RequestLogger:
    def __init__(self, file=sys.stdout):
        self._file = file

    def obfuscate(self, key: str, value: str) -> str:
        if key in ('authorization', 'authentication'):
            if value.startswith('ApiKey '):
                return value.split(':')[0] + '*' * 10
            else:
                return '*' * 20
        if key in ('cookie', 'set-cookie'):
            if 'api_key="' in value:
                start_idx = value.index('api_key="') + len('api_key="')
                end_idx = value.index('"', start_idx)
                return f'{value[0:start_idx + 2]}******{value[end_idx - 2:]}'
        return value

    def log_request(self, method: str, url: str, kwargs):
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
                if k.lower() in ('authorization', 'authentication', 'cookie'):
                    v = self.obfuscate(k.lower(), v)
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
            if k.lower() == 'set-cookie':
                v = self.obfuscate(k.lower(), v)
            lines.append(f'{k}: {v}')

        if response.headers.get('Content-Type', None) == 'application/json':
            lines.append(json.dumps(response.json(), indent=4))

        lines.append('')

        print(*lines, sep='\n', file=self._file)
