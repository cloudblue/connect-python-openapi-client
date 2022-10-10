You can perform queries on a collection to retrieve a set of resources that
match the filters specified in the query.

The Connect ReST API use the [Resource Query Language](https://connect.cloudblue.com/community/api/rql/)
or RQL, to perform queries on a collection.

!!! note
    This guide assumes you are somewhat familiar with RQL.
    If not, take a look at the [RQL video tutorial here](https://connect.cloudblue.com/community/api/rql/#Video_Tutorial).


The `ResourceSet` object helps both to express RQL queries and to manipulate the resulting set of resources.

## Create a `ResourceSet` object

A `ResourceSet` object can be created through
the corresponding `Collection` object
using the `Collection.all()` method to access
all the resources of the collection:

```python
products = client.products.all()
```

Or applying filter using the `Collection.filter()` method:

```python
products = client.products.filter(status='published')
```

The `ResourceSet` will not be evaluated until you need the resources data,
i.e. it does not make any HTTP call until needed, to help express more complex queries
using method chaining like in the following example:

```python
products = client.products.filter(status='published').order_by('-created')
```

## Count results

To get the total number of resources represented by a `ResourceSet` you can use
the `ResourceSet.count()` method.

```python
no_of_published = client.products.filter(status='published').count()
```

or

```python
total = client.products.all().count()
```

## First result

To get the first resource represented by a `ResourceSet` you can use
the `ResourceSet.first()` method.

```python
first = client.products.all().first()
```

or

```python
first = client.products.filter(status='published').first()
```

## Filtering resources

The `ResourceSet` object offers three way to define
your RQL query filters:

### Using raw RQL filter expressions

You can express your filters using raw RQL expressions like in this example:

```python
products = client.products.filter('ilike(name,*awesome*)', 'in(status,(draft,published))')
```

Arguments will be joined using the `and` logical operator.

### Using kwargs and the `__` (double underscore) notation

You can use the `__` notation at the end of the name of the keyword argument
to specify which RQL operator to apply:

```python
products = client.products.filter(name__ilike='*awesome*', status__in=('draft', 'published'))
```

The lookups expressed through keyword arguments are `and`-ed togheter.

Chaning the filter method combine filters using `and`. Equivalent to the previous
expression is to write:

```python
products = client.products.filter(name__ilike='*awesome*').filter(status__in=('draft', 'published'))
```

The `__` notation allow also to specify nested fields for lookups like:

```python
products = client.products.filter(product__category__name__ilike='"*saas services*"')
```

### Using the `R` object

The `R` object allows to create complex RQL filter expression.

The `R` constructor allows to specify lookups as keyword arguments
the same way you do with the `filter()` method.

But it allows also to specify nested fields using the `.` notation:

```python
flt = R().product.category.name.ilike('"*saas services*"')

products = client.products.filter(flt)
```

So an expression like:

```python
flt = R().product.category.name.ilike('"*saas services*"')

products = client.products.filter(flt, status__in=('draft', 'published'))
```

will result in the following RQL query:

```
and(ilike(product.category.name,"*saas services*"),in(status,(draft,published)))
```

The `R` object also allows to join filter expressions using logical `and` and `or` and `not`
using the `&`, `|` and and `~` bitwise operators:

```python
query = (
    R(status='published') | R().category.name.ilike('*awesome*')
) & ~R(description__empty=True)
```

## Other RQL operators

### Searching

For endpoints that supports the RQL search operator you can specify
your search term has shown below:

```python
with_search = rs.search('term')
```

### Ordering

To apply ordering you can specify the fields that have to be used to order the results:

```python
ordered = rs.order_by('+field1', '-field2')
```

Any subsequent calls append other fields to the previous one.

So the previous statement can also be expressed with chaining:

```python
ordered = rs.order_by('+field1').order_by('-field2')
```

### RQL `select`

For collections that supports the `select` RQL operator you can
specify the object to be selected/unselected the following way:

```python
with_select = rs.select('+object1', '-object2')
```

Any subsequent calls append other select expression to the previous.

So the previous statement can also be expressed with chaining:

```python
with_select = rs.select('+object1').select('-object2')
```
