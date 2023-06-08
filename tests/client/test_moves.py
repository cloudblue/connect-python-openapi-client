from connect.client import ClientError, ConnectClient, R


def test_import_client():
    from cnct import ConnectClient as MovedConnectClient

    assert MovedConnectClient == ConnectClient


def test_import_error():
    from cnct import ClientError as MovedClientError

    assert MovedClientError == ClientError


def test_import_r():
    from cnct import R as MovedR

    assert MovedR == R
