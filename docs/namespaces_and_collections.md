# Namespaces and collections

The `ConnectClient` instance allows access to collections of resources using the
`collection()` method of the client:

```python
products = client.collection('products')
```

The previous call to the `collection()` method returns a
`Collection` object that allows working with the resources that contain.

Some collections of the CloudBlue Connect ReST API are grouped within a namespace.

To access a namespace the client exposes the `ns()` method:

```python
subscriptions = client.ns('subscriptions')
```

Since *Connect Python OpenAPI Client* has been designed following the fluent interface design pattern,
you can chain methods:

```python
assets = client.ns('subscriptions').collection('assets')
```

This previous previous expression can be written in a more concise way:

```python
assets = client('subscriptions').assets
```

!!! note
    For collections that use a dash in their names, it is yet
    possible to use the concise form by replacing the dash character with an underscore.

