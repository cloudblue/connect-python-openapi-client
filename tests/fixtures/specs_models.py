import pytest

from cnct.specs.models import NSInfo, CollectionInfo


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
