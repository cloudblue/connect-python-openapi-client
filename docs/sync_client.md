## ConnectClient

::: connect.client.ConnectClient
    :docstring:
    :members: response ns collection

## NS

A **namespace** groups together a set of [**collections**](#collection) of [**resources**](#resource).

::: connect.client.models.NS
    :docstring:
    :members: ns collection

## Collection

A **collection** is a set of [**resources**](#resource) of the same type.


::: connect.client.models.Collection
    :docstring:
    :members: resource action filter all create bulk_create bulk_update bulk_delete


## Resource

A **resource** is an object with a type, associated data, relationships to other resources
and [**actions**](#action) that can be performed on such resource.

::: connect.client.models.Resource
    :docstring:
    :members: collection action get update delete exists values


## Action

An **action** is an operation that can be performed on [**resources**](#resource)
or [**collections**](#collection).

::: connect.client.models.Action
    :docstring:
    :members: get post put delete


## ResourceSet

A **ResourceSet** is a set of resources from one collection eventually filtered and ordered.

::: connect.client.models.ResourceSet
    :docstring:
    :members: all filter first count values_list search order_by select limit configure

