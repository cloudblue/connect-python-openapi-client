## AsyncConnectClient

::: connect.client.AsyncConnectClient
    options:
        heading_level: 3

::: connect.client.fluent._ConnectClientBase
    options:
        heading_level: 3

::: connect.client.mixins.AsyncClientMixin
    options:
        heading_level: 3


## AsyncNS

A **namespace** groups together a set of  [**collections**](#asynccollection) of [**resources**](#asyncresource).

::: connect.client.models.AsyncNS
    options:
        heading_level: 3

::: connect.client.models.base._NSBase
    options:
        heading_level: 3


## AsyncCollection

A **collection** is a set of [**resources**](#asyncresource) of the same type.

::: connect.client.models.AsyncCollection
    options:
        heading_level: 3

::: connect.client.models.base._CollectionBase
    options:
        heading_level: 3

::: connect.client.models.mixins.AsyncCollectionMixin
    options:
        heading_level: 3


## AsyncResource

A **resource** is an object with a type, associated data, relationships to other resources
and [**actions**](#aasyncction) that can be performed on such resource.

::: connect.client.models.AsyncResource
    options:
        heading_level: 3

::: connect.client.models.base._ResourceBase
    options:
        heading_level: 3

::: connect.client.models.mixins.AsyncResourceMixin
    options:
        heading_level: 3


## AsyncAction

An **action** is an operation that can be performed on [**resources**](#asyncresource)
or [**collections**](#asynccollection).

::: connect.client.models.AsyncAction
    options:
        heading_level: 3

::: connect.client.models.mixins.AsyncActionMixin
    options:
        heading_level: 3


## AsyncResourceSet

A **ResourceSet** is a set of resources from one collection eventually filtered and ordered.

::: connect.client.models.AsyncResourceSet
    options:
        heading_level: 3

::: connect.client.models.resourceset._ResourceSetBase
    options:
        heading_level: 3
