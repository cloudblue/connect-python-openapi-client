import pytest

from cnct.specs.models import (
    ActionInfo,
    ApiInfo,
    NSInfo,
    CollectionInfo,
    ResourceInfo,
    OpInfo,
)


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
def resinfo_factory(mocker):
    def _resinfo_factory(
        summary='Resource',
        description='Resource description',
        collections=None,
        actions=None,
    ):
        iteminfo = ResourceInfo(summary, description)
        if collections:
            for col in collections:
                iteminfo.set_collection(col.name, col.summary, col.description)
        if actions:
            for action in actions:
                if action.methods:
                    for info in action.methods.values():
                        iteminfo.set_action(action.name, action.summary, action.description, info)
                else:
                    iteminfo.set_action(action.name, action.summary, action.description, None)
        return iteminfo
    return _resinfo_factory


@pytest.fixture
def opinfo_factory(mocker):
    def _opinfo_factory(
        name='operation',
        collection_name='resources',
        path='path',
        method='post',
        info=None,
    ):
        return OpInfo(
            name,
            collection_name,
            path,
            method,
            info,
        )
    return _opinfo_factory


@pytest.fixture
def actinfo_factory(mocker):
    def _actinfo_factory(
        name='action',
        summary='Action summary',
        description='Action description.',
        info=None,
    ):
        act_info = ActionInfo(name, summary, description)
        if info:
            for opinfo in info:
                act_info.add_info(opinfo)
        return act_info
    return _actinfo_factory


@pytest.fixture
def opdata_factory(mocker):
    def _opdata_factory(
        parameters=[{'name': 'param', 'description': 'param description', 'required': True}],
    ):
        return {
            'parameters': parameters,
        }
    return _opdata_factory
