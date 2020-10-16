import pytest

from cnct.specs.models import NSInfo, CollectionInfo, ItemInfo


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
        specs=None,
        collections=None,
    ):
        nsinfo = NSInfo(name)
        if collections:
            for col in collections:
                nsinfo.set_collection(col)
        return nsinfo
    return _nsinfo_factory


@pytest.fixture
def iteminfo_factory(mocker):
    def _iteminfo_factory(
        collections=None,
        actions=None,
    ):
        iteminfo = ItemInfo()
        if collections:
            for col in collections:
                iteminfo.set_collection(col)
        if actions:
            for action in actions:
                if isinstance(action, str):
                    iteminfo.set_action(action, None)
                elif isinstance(action, (list, tuple)):
                    iteminfo.set_action(action[0], action[1])
        return iteminfo
    return _iteminfo_factory
