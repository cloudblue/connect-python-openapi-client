import os
import platform

from connect.client.utils import (
    ContentRange,
    get_headers,
    get_proxy,
    parse_content_range,
    resolve_attribute,
)
from connect.client.version import get_version


def test_get_headers():
    headers = get_headers('MY API KEY')

    assert 'Authorization' in headers
    assert headers['Authorization'] == 'MY API KEY'
    assert 'User-Agent' in headers

    ua = headers['User-Agent']

    cli, python, system = ua.split()

    assert cli == f'connect-fluent/{get_version()}'
    assert python == f'{platform.python_implementation()}/{platform.python_version()}'
    assert system == f'{platform.system()}/{platform.release()}'


def test_parse_content_range():
    first = 0
    last = 99
    count = 100
    value = f'items {first}-{last}/{count}'

    content_range = parse_content_range(value)

    assert isinstance(content_range, ContentRange)

    assert content_range.first == first
    assert content_range.last == last
    assert content_range.count == count

    assert parse_content_range(None) is None


def test_resolve_attribute():
    data = {
        'first': {
            'second': {
                'third': {'a': 'b'},
            },
        },
    }

    assert resolve_attribute('first.second.third', data) == {'a': 'b'}


def test_resolve_attribute_not_found():
    data = {
        'first': {
            'second': {
                'third': {'a': 'b'},
            },
        },
    }

    assert resolve_attribute('a.b.c', data) is None


def test_get_proxy(mocker):
    assert get_proxy() is None

    mocker.patch.dict(os.environ, {'HTTP_PROXY': 'http://localhost:1234'})
    assert get_proxy() == {
        'http': 'http://localhost:1234',
        'https': None,
        'no_proxy': None,
    }
