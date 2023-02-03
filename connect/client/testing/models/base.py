#
# This file is part of the Ingram Micro CloudBlue Connect Python OpenAPI Client.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
from connect.client.models.base import (
    _ActionBase,
    _CollectionBase,
    _NSBase,
    _ResourceBase,
)
from connect.client.testing.models.mixins import ActionMixin, CollectionMixin, ResourceMixin
from connect.client.testing.models.resourceset import ResourceSetMock


class NSMock(_NSBase):
    def _get_collection_class(self):
        return CollectionMock

    def _get_namespace_class(self):
        return NSMock


class CollectionMock(_CollectionBase, CollectionMixin):
    def _get_resource_class(self):
        return ResourceMock

    def _get_resourceset_class(self):
        return ResourceSetMock

    def _get_action_class(self):
        return ActionMock


class ResourceMock(_ResourceBase, ResourceMixin):
    def _get_collection_class(self):
        return CollectionMock

    def _get_action_class(self):
        return ActionMock


class ActionMock(_ActionBase, ActionMixin):
    pass
