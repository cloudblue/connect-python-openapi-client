import pytest

from cnct.specs.models import (
    ApiInfo,
    NSInfo,
    # CollectionInfo,
    ResourceInfo,
)


# @pytest.fixture
# def colinfo_factory(mocker):
#     def _colinfo_factory(
#         name='resource',
#         specs=None,
#         operations=None,
#         client_specs=None,
#     ):
#         colinfo = CollectionInfo(name)
#         if collections:
#             for col in collections:
#                 nsinfo.set_collection(col.name)
#         return nsinfo
#     return _nsinfo_factory


@pytest.fixture
def nsinfo_factory(mocker):
    def _nsinfo_factory(
        name='namespace',
        tag='Tag',
        specs=None,
        collections=None,
    ):
        nsinfo = NSInfo(name, tag)
        if collections:
            for col in collections:
                nsinfo.set_collection(col, 'summary', 'description', 'tag')
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
                iteminfo.set_collection(col, 'summary', 'description')
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
        tags=[],
        collections=None,
        namespaces=None,
    ):
        apiinfo = ApiInfo(title, description, version, tags)

        if collections:
            for col in collections:
                apiinfo.set_collection(col, 'summary', 'description', 'tag')
        if namespaces:
            for ns in namespaces:
                apiinfo.set_namespace(ns, 'tag')

        return apiinfo
    return _apiinfo_factory
