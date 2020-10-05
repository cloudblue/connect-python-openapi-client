import platform
from http import HTTPStatus


from cnct import get_version


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

