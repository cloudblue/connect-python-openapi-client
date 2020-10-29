import pytest

from cnct.specs.models import (
    ApiInfo,
    NSInfo,
    CollectionInfo,
    ResourceInfo,
)


@pytest.fixture
def colinfo_factory(mocker):
    def _colinfo_factory(
        name='resources',
        summary='Collection summary',
        description='Collection description',
        tag='Tag',
        operations=None,
        resource_specs=None,
    ):
        colinfo = CollectionInfo(name, summary, description, tag)
        colinfo.resource_specs = resource_specs
        if operations:
            for op in operations:
                colinfo.operations[op.name] = op
        return colinfo
    return _colinfo_factory


@pytest.fixture
def nsinfo_factory(mocker):
    def _nsinfo_factory(
        name='namespace',
        tag='Tag',
        collections=None,
    ):
        nsinfo = NSInfo(name, tag)
        if collections:
            for col in collections:
                nsinfo.set_collection(col.name, col.summary, col.description, col.tag)
        return nsinfo
    return _nsinfo_factory


@pytest.fixture
def resinfo_factory(mocker):
    def _resinfo_factory(
        collections=None,
        actions=None,
    ):
        iteminfo = ResourceInfo()
        if collections:
            for col in collections:
                iteminfo.set_collection(col.name, col.summary, col.description)
        if actions:
            for action in actions:
                if isinstance(action, str):
                    iteminfo.set_action(action, 'summary', 'description', None)
                elif isinstance(action, (list, tuple)):
                    iteminfo.set_action(action[0], 'summary', 'description', action[1])
        return iteminfo
    return _resinfo_factory


@pytest.fixture
def apiinfo_factory(mocker):
    def _apiinfo_factory(
        title='Test Api',
        description='Api description',
        version='Api version',
        tags=[{'name': 'Tag', 'description': 'Tag description.'}],
        collections=None,
        namespaces=None,
    ):
        apiinfo = ApiInfo(title, description, version, tags)

        if collections:
            for col in collections:
                apiinfo.set_collection(col.name, col.summary, col.description, col.tag)
        if namespaces:
            for ns in namespaces:
                apiinfo.set_namespace(ns.name, ns.tag)

        return apiinfo
    return _apiinfo_factory
