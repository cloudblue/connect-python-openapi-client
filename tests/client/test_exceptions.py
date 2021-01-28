from cnct.client.exceptions import ClientError


def test_connect_error():
    c = ClientError(status_code=400, error_code='error_code', errors=['msg1', 'msg2'])

    assert repr(c) == '<ClientError 400: error_code>'
    assert str(c) == '400 Bad Request: error_code - msg1,msg2'

def test_connect_error_additional_info():
    additional_info = {
        'attr1': 'val1',
        'attr2': 'val2',
    }

    c = ClientError(status_code=400, error_code='error_code', errors=['msg1', 'msg2'], **additional_info)
    assert c.additional_info == additional_info
