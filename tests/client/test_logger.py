import io

from requests.models import Response

from urllib3.response import HTTPResponse

from connect.client.logger import RequestLogger


def test_log_request():
    LOG_REQUEST_HEADER = '--- HTTP Request ---\n'
    PATH1 = 'https://some.host.name/some/path'
    PATH2 = 'https://some.host.name/some/path?a=b'

    ios = io.StringIO()
    rl = RequestLogger(file=ios)

    rl.log_request('get', PATH1, {})
    assert ios.getvalue() == LOG_REQUEST_HEADER + 'GET ' + PATH1 + ' \n\n'

    ios.truncate(0)
    ios.seek(0, 0)
    rl.log_request(
        'get',
        PATH1,
        {'headers': {'Auth': 'None', 'Cookie': 'XXX', 'Authorization': 'ApiKey SU-XXXX:YYYYY'}},
    )
    assert ios.getvalue() == LOG_REQUEST_HEADER + 'GET ' + PATH1 + ' \n' + """Auth: None
Cookie: XXX
Authorization: ApiKey SU-XXXX**********

"""

    ios.truncate(0)
    ios.seek(0, 0)
    rl.log_request(
        'get',
        PATH1,
        {'headers': {'Auth': 'None', 'Cookie': 'XXX', 'Authorization': 'SecretToken'}},
    )
    assert ios.getvalue() == LOG_REQUEST_HEADER + 'GET ' + PATH1 + ' \n' + """Auth: None
Cookie: XXX
Authorization: ********************

"""

    ios.truncate(0)
    ios.seek(0, 0)
    rl.log_request('post', PATH1, {'json': {'id': 'XX-1234', 'name': 'XXX'}})
    assert ios.getvalue() == LOG_REQUEST_HEADER + 'POST ' + PATH1 + ' \n' + """{
    "id": "XX-1234",
    "name": "XXX"
}

"""

    ios.truncate(0)
    ios.seek(0, 0)
    rl.log_request('get', PATH1, {'params': {'limit': 10, 'offset': 0}})
    assert ios.getvalue() == LOG_REQUEST_HEADER + 'GET ' + PATH1 + '?limit=10&offset=0 \n\n'

    ios.truncate(0)
    ios.seek(0, 0)
    rl.log_request('get', PATH2, {})
    assert ios.getvalue() == LOG_REQUEST_HEADER + 'GET ' + PATH2 + ' \n\n'

    ios.truncate(0)
    ios.seek(0, 0)
    rl.log_request('get', PATH2, {'params': {'limit': 10, 'offset': 0}})
    assert ios.getvalue() == LOG_REQUEST_HEADER + 'GET ' + PATH2 + '&limit=10&offset=0 \n\n'


def test_log_response(mocker):
    LOG_RESPONSE_HEADER = '--- HTTP Response ---\n'

    ios = io.StringIO()
    rl = RequestLogger(file=ios)

    rsp = Response()
    rsp.raw = HTTPResponse()

    rsp.status_code = 200
    rsp.raw.reason = 'OK'
    rl.log_response(rsp)
    assert ios.getvalue() == LOG_RESPONSE_HEADER + '200 OK\n\n'

    ios.truncate(0)
    ios.seek(0, 0)

    rsp = Response()
    rsp.status_code = 200
    rsp.reason_phrase = 'OK'
    rl.log_response(rsp)
    assert ios.getvalue() == LOG_RESPONSE_HEADER + '200 OK\n\n'

    ios.truncate(0)
    ios.seek(0, 0)

    json = {'id': 'XX-1234', 'name': 'XXX'}
    mocker.patch('requests.models.Response.json', return_value=json)
    rsp = Response()
    rsp.raw = HTTPResponse()
    rsp.headers = {'Content-Type': 'application/json'}
    rsp.status_code = 200
    rsp.raw.reason = 'OK'
    rl.log_response(rsp)
    assert ios.getvalue() == LOG_RESPONSE_HEADER + """200 OK
Content-Type: application/json
{
    "id": "XX-1234",
    "name": "XXX"
}

"""
