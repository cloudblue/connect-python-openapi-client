import platform
from collections import namedtuple

from cnct.client.version import get_version

ContentRange = namedtuple('ContentRange', ('first', 'last', 'count'))


def _get_user_agent():
    version = get_version()
    pimpl = platform.python_implementation()
    pver = platform.python_version()
    sysname = platform.system()
    sysver = platform.release()
    ua = f'connect-fluent/{version} {pimpl}/{pver} {sysname}/{sysver}'
    return {'User-Agent': ua}


def get_headers(api_key):
    headers = {'Authorization': api_key}
    headers.update(_get_user_agent())
    return headers


def parse_content_range(value):
    if not value:
        return
    _, info = value.split()
    first_last, count = info.split('/')
    first, last = first_last.split('-')
    return ContentRange(int(first), int(last), int(count))


def resolve_attribute(attr, data):
    try:
        for comp in attr.split('.'):
            data = data.get(comp)
        return data
    except:  # noqa
        pass


def get_values(item, fields):
    return {field: resolve_attribute(field, item) for field in fields}
