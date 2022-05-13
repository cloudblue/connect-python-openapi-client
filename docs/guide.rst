User guide
==========


Getting started
---------------


Requirements
^^^^^^^^^^^^

*connect-openapi-client* runs on python 3.6 or later and has the following dependencies:

* `connect-markdown-renderer <https://github.com/cloudblue/connect-markdown-renderer>`_ 1.*
* requests 2.*
* pyyaml 5.*


Install
^^^^^^^

*connect-openapi-client* is a small python package that can be installed
from the `pypi.org <https://pypi.org/project/connect-openapi-client/>`_ repository.


.. code-block:: sh

    $ pip install connect-openapi-client



First steps with Connect Python OpenAPI Client
----------------------------------------------

Create a client instance
^^^^^^^^^^^^^^^^^^^^^^^^ 

To use *connect-openapi-client* first of all you have to create an instance of the ``ConnectClient`` object:

.. code-block:: python

    from connect.client import ConnectClient

    client = ConnectClient('ApiKey SU-000-000-000:xxxxxxxxxxxxxxxx')


Access to namespaces and collections
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``ConnectClient`` instance allows access to collections of resources using the 
:meth:`~connect.client.fluent.ConnectClient.collection` method of the client:

.. code-block:: python

    products = client.collection('products')

The previous call to the :meth:`~connect.client.fluent.ConnectClient.collection` method returns a 
:class:`~connect.client.models.Collection` object that allows working with the resources that contain.

Some collections of the CloudBlue Connect ReST API are grouped within a namespace.

To access a namespace the client exposes the :meth:`~connect.client.fluent.ConnectClient.ns` method:


.. code-block:: python

    subscriptions = client.ns('subscriptions')


Since *Connect Python OpenAPI Client* has been designed following the fluent interface design pattern,
you can chain methods:

.. code-block:: python

    assets = client.ns('subscriptions').collection('assets')


This previous previous expression can be written in a more concise way:

.. code-block:: python

    assets = client('subscriptions').assets

.. note::

    For collections that use a dash in their names, it is yet 
    possible to use the concise form by replacing the dash character with an underscore.


Working with resources
----------------------


Create new resources
^^^^^^^^^^^^^^^^^^^^

To create a new resource inside a collection you can invoke the 
:meth:`~connect.client.models.Collection.create` method on the corresponding 
:class:`~connect.client.models.Collection` instance:

.. code-block:: python

    payload = {
        'name': 'My Awesome Product',
        'category': {
            'id': 'CAT-00000',
        },
    }

    new_product = c.products.create(payload=payload)

This returns the newly created object json-decoded.

If the collection supports bulk creation of resources, you can use 
:meth:`~connect.client.models.Collection.bulk_create` and pass a list of
resources to be created:

.. code-block:: python

    payload = [
        {
            'name': 'An Awesome Product',
            'category': {
                'id': 'CAT-00000',
            },
        },
        {
            'name': 'Another Awesome Product',
            'category': {
                'id': 'CAT-00000',
            },
        },
    ]

    new_products = c.products.bulk_create(payload=payload)

In this case, this returns a list of the newly created objects json-decoded.

Access to a resource
^^^^^^^^^^^^^^^^^^^^

To access a resource within a collection you can use the
:meth:`~connect.client.models.Collection.resource` method on the corresponding 
:class:`~connect.client.models.Collection` instance:

.. code-block:: python

    product = client.products.resource('PRD-000-000-000')


The indexing operator allows to write the previous expression the following way:

.. code-block:: python

    product = client.products['PRD-000-000-000']

The previous expression returns a :class:`~connect.client.models.Resource` object.

.. caution::

    The ``Resource`` object does not make 
    any HTTP calls to retrieve the resource identified by the index, to avoid 
    unnecessary traffic if what you want is to update it, delete it, perform 
    an action on it or access a nested collection of resources.
    This means that, if the resource does not exist, any operation on it or
    on its nested collection will fail.


Retrieve a resource
^^^^^^^^^^^^^^^^^^^

To retrieve a resource from within a collection you have to invoke 
the :meth:`~connect.client.models.Resource.get` method of the 
:class:`~connect.client.models.Resource` object as shown below:

.. code-block:: python

    product = client.products['PRD-000-000-000'].get()

This call returns the json-decoded object or raise an exception
if it does not exist.


Update resources
^^^^^^^^^^^^^^^^

To update a resource of the collection using its primary identifier,
you can invoke the :meth:`~connect.client.models.Resource.update` method as shown below:

.. code-block:: python

    payload = {
        'short_description': 'This is the short description',
        'detailed_description': 'This is the detailed description',
    }

    updated_product = client.products['PRD-000-000-000'].update(payload=payload)

If the collection supports bulk update of resources you can use the
:meth:`~connect.client.models.Collection.bulk_update` method, passing the list of resources
to be updated:

.. code-block:: python

    payload = [
        {
            'id': 'PRD-000-000-000',
            'short_description': 'This is the short description for 0',
        },
        {
            'id': 'PRD-000-000-001',
            'short_description': 'This is the short description for 1',
        },
    ]

    updated_products = c.products.bulk_update(payload=payload)


Delete resources
^^^^^^^^^^^^^^^^

To delete a resource the :meth:`~connect.client.models.Resource.delete` method is exposed:

.. code-block:: python

    client.products['PRD-000-000-000'].delete()

Similarly to the update operation, if the collection supports bulk deletion of resources
you can use the :meth:`~connect.client.models.Collection.bulk_delete` method, passing the list
of resource identifiers to be deleted:

.. code-block:: python

    payload = [
        {
            'id': 'PRD-000-000-000',
        },
        {
            'id': 'PRD-000-000-001',
        },
    ]

    c.products.bulk_delete(payload=payload)

Access to an action
^^^^^^^^^^^^^^^^^^^

To access an action that can be performed on a resource you can use
the :meth:`~connect.client.models.Resource.action` method of the 
:class:`~connect.client.models.Resource` object:

.. code-block:: python

    endsale_action = client.products['PRD-000-000-000'].action('endsale')

or directly using the call operator
on the :class:`~connect.client.models.Resource` class passing the name of the action:

.. code-block:: python

    endsale_action = client.products['PRD-000-000-000']('endsale')

This returns an :class:`~connect.client.models.Action` object.



Execute an action on a resource
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Depending on its nature, an action can be exposed using the HTTP method that 
best gives the sense of the action to perform.
The :class:`~connect.client.models.Action` object exposes the 
:meth:`~connect.client.models.Action.get`, :meth:`~connect.client.models.Action.post`,
:meth:`~connect.client.models.Action.put`, and :meth:`~connect.client.models.Action.delete`
methods.

For example, supose you want to execute the **endsale** action:

.. code-block:: python

    payload = {
        'replacement': {
            'id': 'PRD-111-111-111'
        },
        'end_of_sale_notes': 'stopped manufacturing',
    }

    result = client.products['PRD-000-000-000']('endsale').post(payload=payload)


Access nested namespaces
^^^^^^^^^^^^^^^^^^^^^^^^

Nested namespaces can be accessed chaining calls of the `ns` method:

.. code-block:: python

    nested_namespace = client.ns('root_ns').ns('child_ns')

or shortly:

.. code-block:: python

    nested_namespace = client('root_ns')('child_ns')


Access nested collections
^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to access a nested collection, you can do that both using the 
:meth:`~connect.client.models.Resource.collection` method or the
name of the nested collection on the :class:`~connect.client.models.Resource` object:

.. code-block:: python

    product_item = client.products['PRD-000-000-000'].items

As for root collections, you can use the :meth:`~connect.client.models.Resource.create` 
method to create new resources within the nested collection or you can use the 
indexing operator to access a resource of the nested collection by ID.


Querying collections
--------------------

You can perform queries on a collection to retrieve a set of resources that
match the filters specified in the query.

The Connect ReST API use the `Resource Query Language <https://connect.cloudblue.com/community/api/rql/>`_
or RQL, to perform queries on a collection.

.. note::

    This guide assumes you are somewhat familiar with RQL.
    If not, take a look at the `RQL video tutorial here <https://connect.cloudblue.com/community/api/rql/#Video_Tutorial>`_.

The ``ResourceSet`` object helps both to express RQL queries and to manipulate the resulting set of resources.


Create a ``ResourceSet`` object
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A :class:`connect.client.models.ResourceSet` object can be created through 
the corresponding :class:`connect.client.models.Collection` object
using the :meth:`connect.client.models.Collection.all` method to access 
all the resources of the collection:

.. code-block:: python

    products = client.products.all()


Or applying filter using the :meth:`connect.client.models.Collection.filter` method:


.. code-block:: python

    products = client.products.filter(status='published')


The ``ResourceSet`` will not be evaluated until you need the resources data, 
i.e. it does not make any HTTP call until needed, to help express more complex queries
using method chaining like in the following example:


.. code-block:: python

    products = client.products.filter(status='published').order_by('-created')


Count results
^^^^^^^^^^^^^

To get the total number of resources represented by a ``ResourceSet`` you can use
the :meth:`connect.client.models.Collection.count` method. 

.. code-block:: python

    no_of_published = client.products.filter(status='published').count()

or

.. code-block:: python

    no_of_published = client.products.all().count()



First result
^^^^^^^^^^^^

To get the first resource represented by a ``ResourceSet`` you can use
the :meth:`connect.client.models.Collection.first` method. 

.. code-block:: python

    first = client.products.all().first()

or

.. code-block:: python

    first = client.products.filter(status='published').first()


Filtering resources
^^^^^^^^^^^^^^^^^^^

The :class:`connect.client.models.ResourceSet` object offers three way to define
your RQL query filters:


Using raw RQL filter expressions
""""""""""""""""""""""""""""""""

You can express your filters using raw RQL expressions like in this example:

.. code-block:: python

    products = client.products.filter('ilike(name,*awesome*)', 'in(status,(draft,published))')

Arguments will be joined using the ``and`` logical operator.


Using kwargs and the ``__`` (double underscore) notation
""""""""""""""""""""""""""""""""""""""""""""""""""""""""

You can use the ``__`` notation at the end of the name of the keyword argument
to specify which RQL operator to apply:

.. code-block:: python

    products = client.products.filter(name__ilike='*awesome*', status__in=('draft', 'published'))


The lookups expressed through keyword arguments are ``and``-ed togheter.

Chaning the filter method combine filters using ``and``. Equivalent to the previous
expression is to write:

.. code-block:: python

    products = client.products.filter(name__ilike='*awesome*').filter(status__in=('draft', 'published'))


The ``__`` notation allow also to specify nested fields for lookups like:

.. code-block:: python

    products = client.products.filter(product__category__name__ilike='"*saas services*"')


Using the ``R`` object
""""""""""""""""""""""

The :class:`~connect.client.rql.base.R` object allows to create complex RQL filter expression.

The :class:`~connect.client.rql.base.R` constructor allows to specify lookups as keyword arguments
the same way you do with the :meth:`~connect.client.models.ResourceSet.filter` method.

But it allows also to specify nested fields using the ``.`` notation:

.. code-block:: python

    flt = R().product.category.name.ilike('"*saas services*"')

    products = client.products.filter(flt)


So an expression like:

.. code-block:: python

    flt = R().product.category.name.ilike('"*saas services*"')

    products = client.products.filter(flt, status__in=('draft', 'published'))

will result in the following RQL query:

.. code-block:: sh

    and(ilike(product.category.name,"*saas services*"),in(status,(draft,published)))

The ``R`` object also allows to join filter expressions using logical ``and`` and ``or`` and ``not``
using the ``&``, ``|`` and and ``~`` bitwise operators:

.. code-block:: python

    query = (
        R(status='published') | R().category.name.ilike('*awesome*')
    ) & ~R(description__empty=True)


Other RQL operators
-------------------

Searching
^^^^^^^^^

For endpoints that supports the RQL search operator you can specify
your search term has shown below:

.. code-block::python

    with_search = rs.search('term')



Ordering
^^^^^^^^

To apply ordering you can specify the fields that have to be used to order the results:


.. code-block:: python

    ordered = rs.order_by('+field1', '-field2')


Any subsequent calls append other fields to the previous one.

So the previous statement can also be expressed with chaining:

.. code-block:: python

    ordered = rs.order_by('+field1').order_by('-field2')


Apply RQL ``select``
^^^^^^^^^^^^^^^^^^^^

For collections that supports the ``select`` RQL operator you can
specify the object to be selected/unselected the following way:

.. code-block:: python

    with_select = rs.select('+object1', '-object2')


Any subsequent calls append other select expression to the previous.

So the previous statement can also be expressed with chaining:

.. code-block:: python

    with_select = rs.select('+object1').select('-object2')

