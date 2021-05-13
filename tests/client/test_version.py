from pkg_resources import DistributionNotFound

from connect.client.version import get_version


def test_version_ok(mocker):
    ver = mocker.MagicMock()
    ver.version = '1.2.3'
    mocker.patch('connect.client.version.get_distribution', return_value=ver)
    assert get_version() == '1.2.3'


def test_version_ko(mocker):
    mocker.patch('connect.client.version.get_distribution', side_effect=DistributionNotFound())
    assert get_version() == '0.0.0'
