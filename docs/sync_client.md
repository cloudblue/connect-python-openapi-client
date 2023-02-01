# Synchronous client

## ConnectClient

::: connect.client.ConnectClient
    options:
        heading_level: 3

::: connect.client.fluent._ConnectClientBase
    options:
        heading_level: 3

::: connect.client.mixins.SyncClientMixin
    options:
        heading_level: 3

## NS

A **namespace** groups together a set of [**collections**](#collection) of [**resources**](#resource).

::: connect.client.models.base.NS
    options:
        heading_level: 3

::: connect.client.models.base._NSBase
    options:
        heading_level: 3

## Collection

A **collection** is a set of [**resources**](#resource) of the same type.


::: connect.client.models.Collection
    options:
        heading_level: 3

::: connect.client.models.base._CollectionBase
    options:
        heading_level: 3

::: connect.client.models.mixins.CollectionMixin
    options:
        heading_level: 3

## Resource

A **resource** is an object with a type, associated data, relationships to other resources
and [**actions**](#action) that can be performed on such resource.

::: connect.client.models.Resource
    options:
        heading_level: 3

::: connect.client.models.base._ResourceBase
    options:
        heading_level: 3

::: connect.client.models.mixins.ResourceMixin
    options:
        heading_level: 3

## Action

An **action** is an operation that can be performed on [**resources**](#resource)
or [**collections**](#collection).

::: connect.client.models.Action
    options:
        heading_level: 3

::: connect.client.models.mixins.ActionMixin
    options:
        heading_level: 3

## ResourceSet

A **ResourceSet** is a set of resources from one collection eventually filtered and ordered.

::: connect.client.models.ResourceSet
    options:
        heading_level: 3

::: connect.client.models.resourceset._ResourceSetBase
    options:
        heading_level: 3