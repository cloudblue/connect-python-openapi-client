from cnct.specs.models import ApiInfo, CollectionInfo, NSInfo
from cnct.specs.parser import parse


def test_parser():
    specs = parse('tests/data/specs.yml')
    assert specs is not None
    assert isinstance(specs, ApiInfo)
    assert 'subscriptions' in specs.namespaces
    assert isinstance(specs.namespaces['subscriptions'], NSInfo)
    assert 'products' in specs.collections
    assert isinstance(specs.collections['products'], CollectionInfo)
    nsinfo = specs.namespaces['subscriptions']
    assert 'assets' in nsinfo.collections
    assert isinstance(nsinfo.collections['assets'], CollectionInfo)


def test_parser_from_url(requests_mock):
    requests_mock.get(
        'https://localhost/specs.yml',
        text=open('tests/data/specs.yml', 'r').read(),
    )
    specs = parse('https://localhost/specs.yml')
    assert specs is not None
