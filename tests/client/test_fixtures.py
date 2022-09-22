from connect.client import ConnectClient


def test_client_mocker_factory(client_mocker_factory):
    mocker = client_mocker_factory('http://example.com')
    mocker.products.create(return_value={'id': 'PRD-000'})

    client = ConnectClient('api_key', endpoint='http://example.com')
    assert client.products.create(payload={}) == {'id': 'PRD-000'}
