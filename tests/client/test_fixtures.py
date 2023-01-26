import requests

from connect.client import ConnectClient


def test_client_mocker_factory(client_mocker_factory):
    mocker = client_mocker_factory('http://example.com')
    mocker.products.create(return_value={'id': 'PRD-000'})

    client = ConnectClient('api_key', endpoint='http://example.com')
    assert client.products.create(payload={}) == {'id': 'PRD-000'}


def test_client_mocker_factory_default_base_url(client_mocker_factory):
    mocker = client_mocker_factory()
    mocker.products.create(return_value={'id': 'PRD-000'})

    client = ConnectClient('api_key', endpoint='https://example.org/public/v1')
    assert client.products.create(payload={}) == {'id': 'PRD-000'}


def test_requests_mocker(client_mocker_factory, requests_mocker):
    mocker = client_mocker_factory('http://example.com')
    mocker.products.create(return_value={'id': 'PRD-000'})
    requests_mocker.get('https://test.com', json={'a': 'b'})

    client = ConnectClient('api_key', endpoint='http://example.com')
    assert client.products.create(payload={}) == {'id': 'PRD-000'}
    assert requests.get('https://test.com').json() == {'a': 'b'}
