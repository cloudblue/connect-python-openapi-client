## AsyncConnectClient

::: connect.client.AsyncConnectClient
    :docstring:
    :members: response ns collection


## AsyncNS

A **namespace** groups together a set of  [**collections**](#asynccollection) of [**resources**](#asyncresource).

::: connect.client.models.AsyncNS
    :docstring:
    :members: ns collection


## AsyncCollection

A **collection** is a set of [**resources**](#asyncresource) of the same type.


::: connect.client.models.AsyncCollection
    :docstring:
    :members: resource action filter all create bulk_create bulk_update bulk_delete


## AsyncResource

A **resource** is an object with a type, associated data, relationships to other resources
and [**actions**](#aasyncction) that can be performed on such resource.

::: connect.client.models.AsyncResource
    :docstring:
    :members: collection action get update delete exists values


## AsyncAction

An **action** is an operation that can be performed on [**resources**](#asyncresource)
or [**collections**](#asynccollection).

::: connect.client.models.AsyncAction
    :docstring:
    :members: get post put delete


## AsyncResourceSet

A **ResourceSet** is a set of resources from one collection eventually filtered and ordered.

::: connect.client.models.AsyncResourceSet
    :docstring:
    :members: all filter first count values_list search order_by select limit configure
