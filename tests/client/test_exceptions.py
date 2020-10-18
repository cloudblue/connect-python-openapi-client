from cnct.client.exceptions import ConnectError


def test_connect_error():
    c = ConnectError(400, 'error_code', ['msg1', 'msg2'])

    assert repr(c) == '<ConnectError 400: error_code>'
    assert str(c) == 'error_code: msg1,msg2'
