# API Reference

## Client


### class connect.client.fluent.ConnectClient(api_key, endpoint=None, use_specs=True, specs_location=None, validate_using_specs=True, default_headers=None, default_limit=100, max_retries=0)
Connect ReST API client.


#### \__getattr__(name)
Returns a collection object called `name`.


* **Parameters**

    **name** (*str*) – The name of the collection to retrieve.



* **Returns**

    a collection called `name`.



* **Return type**

    Collection



#### \__call__(name)
Call self as a function.


#### ns(name)
Returns the namespace called `name`.


* **Parameters**

    **name** (*str*) – The name of the namespace to access.



* **Returns**

    The namespace called `name`.



* **Return type**

    NS



#### collection(name)
Returns the collection called `name`.


* **Parameters**

    **name** (*str*) – The name of the collection to access.



* **Returns**

    The collection called `name`.



* **Return type**

    Collection


## Models


### class connect.client.models.NS(client, path)
A namespace is a group of related collections.


#### \__getattr__(name)
Returns a collection object by its name.


* **Parameters**

    **name** (*str*) – the name of the Collection object.



* **Returns**

    The Collection named `name`.



* **Return type**

    Collection



#### collection(name)
Returns the collection called `name`.


* **Parameters**

    **name** (*str*) – The name of the collection.



* **Raises**

    
    * **TypeError** – if the `name` is not a string.


    * **ValueError** – if the `name` is blank.


    * **NotFoundError** – if the `name` does not exist.



* **Returns**

    The collection called `name`.



* **Return type**

    Collection



#### ns(name)
Returns the namespace called `name`.


* **Parameters**

    **name** (*str*) – The name of the namespace.



* **Raises**

    
    * **TypeError** – if the `name` is not a string.


    * **ValueError** – if the `name` is blank.



* **Returns**

    The namespace called `name`.



* **Return type**

    NS



#### help()
Output the namespace documentation to the console.


* **Returns**

    self



* **Return type**

    NS



### class connect.client.models.Collection(client, path)
A collection is a group of operations on a resource.


#### \__getitem__(resource_id)
Return a Resource object representing the resource
identified by `resource_id`.


* **Parameters**

    **resource_id** (*str**, **int*) – The identifier of the resource



* **Returns**

    the Resource instance identified by `resource_id`.



* **Return type**

    Resource



#### all()
Return a ResourceSet instance.


* **Returns**

    a ResourceSet instance.



* **Return type**

    ResourceSet



#### filter(\*args, \*\*kwargs)
Returns a ResourceSet object.
The returned ResourceSet object will be filtered based on
the arguments and keyword arguments.

Arguments can be RQL filter expressions as strings
or R objects.

Ex.

```
rs = collection.filter('eq(field,value)', 'eq(another.field,value2)')
rs = collection.filter(R().field.eq('value'), R().another.field.eq('value2'))
```

All the arguments will be combined with logical `and`.

Filters can be also specified as keyword argument using the `__` (double underscore)
notation.

Ex.

```
rs = collection.filter(
    field=value,
    another__field=value,
    field2__in=('a', 'b'),
    field3__null=True,
)
```

Also keyword arguments will be combined with logical `and`.


* **Raises**

    **TypeError** – If arguments are neither strings nor R objects.



* **Returns**

    A ResourceSet with the filters applied.



* **Return type**

    ResourceSet



#### create(payload=None, \*\*kwargs)
Create a new resource within this collection.


* **Parameters**

    **payload** (*dict**, **optional*) – JSON payload of the resource to create, defaults to None.



* **Returns**

    The newly created resource.



* **Return type**

    dict



#### resource(resource_id)
Returns an Resource object.


* **Parameters**

    **resource_id** (*str**, **int*) – The resource identifier.



* **Returns**

    The Resource identified by `resource_id`.



* **Return type**

    Resource



#### help()
Output the collection documentation to the console.


* **Returns**

    self



* **Return type**

    Collection



### class connect.client.models.Resource(client, path)
Represent a generic resource.


#### \__getattr__(name)
Returns a nested Collection object called `name`.


* **Parameters**

    **name** (*str*) – The name of the Collection to retrieve.



* **Returns**

    a Collection called `name`.



* **Return type**

    Collection



#### \__call__(name)
Call self as a function.


#### collection(name)
Returns the collection called `name`.


* **Parameters**

    **name** (*str*) – The name of the collection.



* **Raises**

    
    * **TypeError** – if the `name` is not a string.


    * **ValueError** – if the `name` is blank.


    * **NotFoundError** – if the `name` does not exist.



* **Returns**

    The collection called `name`.



* **Return type**

    Collection



#### action(name)
Returns the action called `name`.


* **Parameters**

    **name** (*str*) – The name of the action.



* **Raises**

    
    * **TypeError** – if the `name` is not a string.


    * **ValueError** – if the `name` is blank.


    * **NotFoundError** – if the `name` does not exist.



* **Returns**

    The action called `name`.



* **Return type**

    Action



#### get(\*\*kwargs)
Execute a http GET to retrieve this resource.
The http GET can be customized passing kwargs that
will be forwarded to the underlying GET of the `requests`
library.


* **Returns**

    The resource data.



* **Return type**

    dict



#### update(payload=None, \*\*kwargs)
Execute a http PUT to update this resource.
The http PUT can be customized passing kwargs that
will be forwarded to the underlying PUT of the `requests`
library.


* **Parameters**

    **payload** (*dict**, **optional*) – the JSON payload of the update request, defaults to None



* **Returns**

    The updated resource.



* **Return type**

    dict



#### delete(\*\*kwargs)
Execute a http DELETE to delete this resource.
The http DELETE can be customized passing kwargs that
will be forwarded to the underlying DELETE of the `requests`
library.


#### values(\*fields)
Returns a flat dictionary containing only the fields passed as arguments.
Nested field can be specified using dot notation.

Ex.

```
```

values = resource.values(‘field’, ‘nested.field’)


* **Returns**

    A dictionary containing field,value pairs.



* **Return type**

    dict



#### help()
Output the resource documentation to the console.


* **Returns**

    self



* **Return type**

    Resource



### class connect.client.models.ResourceSet(client, path, query=None)
Represent a set of resources.


#### \__iter__()
Returns an iterator to iterate over the set of resources.


* **Returns**

    A resources iterator.



* **Return type**

    ResourceSet



#### \__bool__()
Return True if the ResourceSet contains at least a resource
otherwise return False.


* **Returns**

    True if contains a resource otherwise False.



* **Return type**

    bool



#### \__getitem__(key)
If called with and integer index, returns the item
at index `key`.

If key is a slice, set the pagination limit and offset
accordingly.


* **Parameters**

    **key** (*int**, **slice*) – index or slice.



* **Raises**

    **TypeError** – If `key` is neither an integer nor a slice.



* **Returns**

    The resource at index `key` or self if `key` is a slice.



* **Return type**

    dict, ResultSet



#### configure(\*\*kwargs)
Set the keyword arguments that needs to be forwarded to
the underlying `requests` call.


* **Returns**

    This ResourceSet object.



* **Return type**

    ResourceSet



#### limit(limit)
Set the number of results to be fetched from the remote
endpoint at once.


* **Parameters**

    **limit** (*int*) – maximum number of results to fetch in a batch.



* **Raises**

    
    * **TypeError** – if limit is not an integer.


    * **ValueError** – if limit is not positive non-zero.



* **Returns**

    A copy of this ResourceSet class with the new limit.



* **Return type**

    ResourceSet



#### order_by(\*fields)
Add fields for ordering.


* **Returns**

    This ResourceSet object.



* **Return type**

    ResourceSet



#### select(\*fields)
Apply the RQL `select` operator to
this ResourceSet object.


* **Returns**

    This ResourceSet object.



* **Return type**

    ResourceSet



#### filter(\*args, \*\*kwargs)
Applies filters to this ResourceSet object.

Arguments can be RQL filter expressions as strings
or R objects.

Ex.

```
rs = rs.filter('eq(field,value)', 'eq(another.field,value2)')
rs = rs.filter(R().field.eq('value'), R().another.field.eq('value2'))
```

All the arguments will be combined with logical `and`.

Filters can be also specified as keyword argument using the `__` (double underscore)
notation.

Ex.

```
rs = rs.filter(
    field=value,
    another__field=value,
    field2__in=('a', 'b'),
    field3__null=True,
)
```

Also keyword arguments will be combined with logical `and`.


* **Raises**

    **TypeError** – If arguments are neither strings nor R objects.



* **Returns**

    This ResourceSet object.



* **Return type**

    ResourceSet



#### count()
Returns the total number of resources within this ResourceSet object.


* **Returns**

    The total number of resources present.



* **Return type**

    int



#### first()
Returns the first resource that belongs to this ResourceSet object
or None if the ResourceSet doesn’t contains resources.


* **Returns**

    The first resource.



* **Return type**

    dict, None



#### all()
Returns a copy of the current ResourceSet.


* **Returns**

    A copy of this ResourceSet.



* **Return type**

    ResourceSet



#### search(term)
Create a copy of the current ResourceSet with
the search set to term.


* **Parameters**

    **term** (*str*) – The term to search for.



* **Returns**

    A copy of the current ResourceSet.



* **Return type**

    ResourceSet



#### values_list(\*fields)
Returns a flat dictionary containing only the fields passed as arguments
for each resource that belongs to this ResourceSet.

Nested field can be specified using dot notation.

Ex.

```
```

values = rs.values_list(‘field’, ‘nested.field’)


* **Returns**

    A list of dictionaries containing field,value pairs.



* **Return type**

    list



#### help()
Output the ResourceSet documentation to the console.


* **Returns**

    self



* **Return type**

    ResourceSet


## RQL utility


### connect.client.rql.base.R()
alias of `connect.client.rql.base.RQLQuery`


### class connect.client.rql.base.RQLQuery(\*, _op='expr', _children=None, _negated=False, _expr=None, \*\*kwargs)
Helper class to construct complex RQL queries.


#### \__len__()
Returns the length of this R object.
It will be 1 if represent a single RQL expression
or the number of expressions this logical operator (and, or)
applies to.


* **Returns**

    The length of this R object.



* **Return type**

    int



#### \__bool__()
Returns False if it is an empty R object otherwise True.


* **Returns**

    False if it is an empty R object otherwise True.



* **Return type**

    bool



#### \__eq__(other)
Returns True if self == other.


* **Parameters**

    **other** (*R*) – Another R object.



* **Returns**

    True if the `other` object is equal to self, False otherwise.



* **Return type**

    bool



#### \__and__(other)
Combine this R object with `other` using a logical `and`.


* **Parameters**

    **other** (*R*) – Another R object.



* **Returns**

    The R object representing a logical `and` between this and `other`.



* **Return type**

    R



#### \__or__(other)
Combine this R object with `other` using a logical `or`.


* **Parameters**

    **other** (*R*) – Another R object.



* **Returns**

    The R object representing a logical `or` between this and `other`.



* **Return type**

    R



#### \__invert__()
Apply the RQL `not` operator to this R object.


* **Returns**

    The R object representing this R object negated.



* **Return type**

    R



#### n(name)
Set the current field for this R object.


* **Parameters**

    **name** (*str*) – name of the field



* **Raises**

    **AttributeError** – if this R object has already been evaluated.



* **Returns**

    This R object.



* **Return type**

    R


## Exceptions


### class connect.client.exceptions.ClientError(message=None, status_code=None, error_code=None, errors=None, \*\*kwargs)
