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

    from cnct import ConnectClient

    client = ConnectClient('ApiKey SU-000-000-000:xxxxxxxxxxxxxxxx')


Access to namespaces and collections
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``ConnectClient`` instance allows access to collections of resources using the 
:meth:`~cnct.client.fluent.ConnectClient.collection` method of the client:

.. code-block:: python

    products = client.collection('products')

The previous call to the :meth:`~cnct.client.fluent.ConnectClient.collection` method returns a 
:class:`~cnct.client.models.Collection` object that allows working with the resources that contain.

Some collections of the CloudBlue Connect ReST API are grouped within a namespace.

To access a namespace the client exposes the :meth:`~cnct.client.fluent.ConnectClient.ns` method:


.. code-block:: python

    subscriptions = client.ns('subscriptions')


Since *Connect Python OpenAPI Client* has been designed following the fluent interface design pattern,
you can chain methods:

.. code-block:: python

    assets = client.ns('subscriptions').collection('assets')


By default, the ``ConnectClient`` object, when instantiated, downloads and parse
the `CloudBlue Connect OpenAPI specifications <https://connect.cloudblue.com/community/api/openapi/>`_.

This allows you to write the previous expression in a more concise way:

.. code-block:: python

    assets = client.subscriptions.assets

.. caution::

    As long as the name of the namespace or the collection is a valid python 
    identifier, is not a language reserved word, and does not collide with other 
    symbols defined on the object, you can use the concise form.


.. note::

    For namespaces and/or collections that use a dash in their names, it is yet 
    possible to use the concise form by replacing the dash character with an underscore.


Working with resources
----------------------


Create a new resource
^^^^^^^^^^^^^^^^^^^^^

To create a new resource inside a collection you can invoke the 
:meth:`~cnct.client.models.Collection.create` method on the corresponding 
:class:`~cnct.client.models.Collection` instance:

.. code-block:: python

    payload = {
        'name': 'My Awesome Product',
        'category': {
            'id': 'CAT-00000',
        },
    }

    new_product = c.products.create(payload=payload)

This returns the newly created object json-decoded.

Access to a resource
^^^^^^^^^^^^^^^^^^^^

The indexing operator allows to work with a particular resource using 
its primary identifier as the index:

.. code-block:: python

    product = client.products['PRD-000-000-000']

The previous expression returns a :class:`~cnct.client.models.Resource` object.

.. caution::

    The ``Resource`` object returned by the indexing operator does not make 
    any HTTP calls to retrieve the resource identified by the index, to avoid 
    unnecessary traffic if what you want is to update it, delete it, perform 
    an action on it or access a nested collection of resources.

    This means that, if the resource does not exist, any operation on it or
    on its nested collection will fail.


Retrieve a resource
^^^^^^^^^^^^^^^^^^^

To retrieve a resource from within a collection you have to invoke 
the :meth:`~cnct.client.models.Resource.get` method of the 
:class:`~cnct.client.models.Resource` object as shown below:

.. code-block:: python

    product = client.products['PRD-000-000-000'].get()

This call returns the json-decoded object or raise an exception
if it does not exist.


Update a resource
^^^^^^^^^^^^^^^^^

To update a resource of the collection using its primary identifier,
you can invoke the :meth:`~cnct.client.models.Resource.update` method as shown below:

.. code-block:: python

    payload = {
        'short_description': 'This is the short description',
        'detailed_description': 'This is the detailed description',
    }

    product = client.products['PRD-000-000-000'].update(payload=payload)


Delete a resource
^^^^^^^^^^^^^^^^^

To delete a resource the :meth:`~cnct.client.models.Resource.delete` method is exposed:

.. code-block:: python

    client.products['PRD-000-000-000'].delete()

Access to an action
^^^^^^^^^^^^^^^^^^^

To access an action that can be performed on a resource you can use
the :meth:`~cnct.client.models.Resource.action` method of the 
:class:`~cnct.client.models.Resource` object or directly the name of the action.

.. code-block:: python

    endsale_action = client.products['PRD-000-000-000'].endsale

This returns an :class:`~cnct.client.models.Action` object.


Execute an action on a resource
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Depending on its nature, an action can be exposed using the HTTP method that 
best gives the sense of the action to perform.
The :class:`~cnct.client.models.Action` object exposes the 
:meth:`~cnct.client.models.Action.get`, :meth:`~cnct.client.models.Action.post`,
:meth:`~cnct.client.models.Action.put`, and :meth:`~cnct.client.models.Action.delete`
methods.

For example, supose you want to execute the **endsale** action:

.. code-block:: python

    payload = {
        'replacement': {
            'id': 'PRD-111-111-111'
        },
        'end_of_sale_notes': 'stopped manufacturing',
    }

    result = client.products['PRD-000-000-000'].endsale.post(payload=payload)


Access nested collections
^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to access a nested collection, you can do that both using the 
:meth:`~cnct.client.models.Resource.collection` method or the
name of the nested collection on the :class:`~cnct.client.models.Resource` object:

.. code-block:: python

    product_item = client.products['PRD-000-000-000'].items

As for root collections, you can use the :meth:`~cnct.client.models.Resource.create` 
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

A :class:`cnct.client.models.ResourceSet` object can be created through 
the corresponding o:class:`cnct.client.models.Collection` object
using the :meth:`cnct.client.models.Collection.all` method to access 
all the resources of the collection:

.. code-block:: python

    products = client.products.all()


Or applying filter using the :meth:`cnct.client.models.Collection.filter` method:


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
the :meth:`cnct.client.models.Collection.count` method. 

.. code-block:: python

    no_of_published = client.products.filter(status='published').count()

or

.. code-block:: python

    no_of_published = client.products.all().count()





First result
^^^^^^^^^^^^

To get the first resource represented by a ``ResourceSet`` you can use
the :meth:`cnct.client.models.Collection.first` method. 

.. code-block:: python

    first = client.products.all().first()

or

.. code-block:: python

    first = client.products.filter(status='published').first()


Filtering resources
^^^^^^^^^^^^^^^^^^^

The :class:`cnct.client.models.ResourceSet` object offers three way to define
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

The :class:`~cnct.rql.base.R` object allows to create complex RQL filter expression.

The :class:`~cnct.rql.base.R` constructor allows to specify lookups as keyword arguments
the same way you do with the :meth:`~cnct.client.models.ResourceSet.filter` method.

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

