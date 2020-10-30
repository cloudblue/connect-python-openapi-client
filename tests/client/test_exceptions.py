from cnct.client.exceptions import APIError


def test_connect_error():
    c = APIError(400, 'error_code', ['msg1', 'msg2'])

    assert repr(c) == '<APIError 400: error_code>'
    assert str(c) == 'error_code: msg1,msg2'
