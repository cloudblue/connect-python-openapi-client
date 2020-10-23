Tutorial
========

Create a client instance
------------------------ 

To use *connect-fluent-client* first of all you have to create an instance of the ``ConnectFluent`` object:

.. code-block:: python

    from cnct import ConnectFluent

    client = ConnectFluent('ApiKey SU-000-000-000:xxxxxxxxxxxxxxxx')


Access namespaces and collections
---------------------------------

*connect-fluent-client* allows access to collections of resources using the ``.collection`` method
of the client:

.. code-block:: python

    products = client.collection('products')

Some collections of the CloudBlue Connect REST API are grouped within a namespace.

To access a namespace the client exposes the ``.ns`` method:


.. code-block:: python

    subscriptions = client.ns('subscriptions')


Since *connect-fluent-client* has been designed following the fluent interface design pattern, you can chain methods:

.. code-block:: python

    assets = client.ns('subscriptions').collection('assets')


By default, the ``ConnectFluent`` object, when instantiated, downloads and parse
the `CloudBlue Connect OpenAPI specifications <https://connect.cloudblue.com/community/api/openapi/>`_.

This allows you to write the previous expression in a more concise way:

.. code-block:: python

    assets = client.subscriptions.assets

.. caution::

    As long as the name of the namespace or the collection is a valid python identifier, is not a language reserved word, 
    and does not collide with other symbols defined on the object, you can use the concise form.


Create a new resource
---------------------

To create a new resource inside a collection you can invoke the ``.create`` method on the corresponding collection:

.. code-block:: python

    payload = {
        'name': 'My Awesome Product',
        'category': {
            'id': 'CAT-00000',
        },
    }

    new_product = c.products.create(payload=payload)



Retrieve a resource
-------------------

To retrieve a resource from within a collection using its ID,
you can use the the indexing operator to specify the id followed by the ``.get`` method as shown below:

.. code-block:: python

    product = client.products['PRD-000-000-000'].get()


Update a resource
-----------------

To updaye a resource from within a collection using its ID,
you can invoke the ``.update`` method as shown below:

.. code-block:: python

    payload = {
        'short_description': 'This is the short description',
        'detailed_description': 'This is the detailed description',
    }

    product = client.products['PRD-000-000-000'].update(payload=payload)


Delete a resource
-----------------

To delete a resource the ``.delete`` method is exposed:

.. code-block:: python

    client.products['PRD-000-000-000'].delete()


Execute an action on a resource
-------------------------------

To execute an action on a resource you can use the ``.action`` method or directly the name of the action.

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
-------------------------

If you want to access a nested collection, you can do that both using the ``.collection`` method or the
name of the nested collection on the resource object:

.. code-block:: python

    product_item = client.products['PRD-000-000-000'].items

As for root collections, you can use the ``.create`` method to create new resources within the
nested collection or you can use the indexing operator to access a resource of the nested collection
by ID.


List/search resources
---------------------

To list resources belonging to a collection you can do:

.. code-block:: python

    for product in client.products.search():
        print(product)

You can filter the results passing a `RQL query <https://connect.cloudblue.com/community/api/rql/>`_ string to the ``.search`` method:

.. code-block:: python

    for product in client.products.search(query='eq(status,published)'):
        print(product)


