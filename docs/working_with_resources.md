## Create a new resource

To create a new resource inside a collection you can invoke the
`create()` method on the corresponding
`Collection` instance:

```python
payload = {
    'name': 'My Awesome Product',
    'category': {
        'id': 'CAT-00000',
    },
}

new_product = c.products.create(payload=payload)
```

This returns the newly created object json-decoded.

## Access to a resource

To access a resource within a collection you can use the
`resource()` method on the corresponding
`Collection` instance:

```python
product = client.products.resource('PRD-000-000-000')
```

The indexing operator allows to write the previous expression the following way:

```python
product = client.products['PRD-000-000-000']
```

The previous expression returns a `Resource` object.

## Retrieve a resource

To retrieve a resource from within a collection you have to invoke
the `get()` method of the
`Resource` object as shown below:

```python
product = client.products['PRD-000-000-000'].get()
```

This call returns the json-decoded object or raise an exception
if it does not exist.

## Update a resource

To update a resource of the collection using its primary identifier,
you can invoke the `update()` method as shown below:

```python
payload = {
    'short_description': 'This is the short description',
    'detailed_description': 'This is the detailed description',
}

product = client.products['PRD-000-000-000'].update(payload=payload)
```

## Delete a resource

To delete a resource the `delete()` method is exposed:

```python
client.products['PRD-000-000-000'].delete()
```

## Access to an action

To access an action that can be performed on a resource you can use
the `action()` method of the
`Resource` object:

```python
endsale_action = client.products['PRD-000-000-000'].action('endsale')
```

or directly using the call operator
on the `Resource` class passing the name of the action:

```python
endsale_action = client.products['PRD-000-000-000']('endsale')
```

This returns an `Action` object.

## Execute an action on a resource

Depending on its nature, an action can be exposed using the HTTP method that
best gives the sense of the action to perform.
The `Action` object exposes the
`get()`, `post()`,
`put()`, and `delete()`
methods.

For example, supose you want to execute the **endsale** action:

```python
payload = {
    'replacement': {
        'id': 'PRD-111-111-111'
    },
    'end_of_sale_notes': 'stopped manufacturing',
}

result = client.products['PRD-000-000-000']('endsale').post(payload=payload)
```