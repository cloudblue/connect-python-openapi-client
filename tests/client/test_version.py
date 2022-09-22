from connect.client.version import get_version


def test_version_ok(mocker):
    mocker.patch('connect.client.version.version', return_value='1.2.3')
    assert get_version() == '1.2.3'


def test_version_ko(mocker):
    mocker.patch('connect.client.version.version', side_effect=Exception)
    assert get_version() == '0.0.0'
