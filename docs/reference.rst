API Reference
=============

Client
------

.. autoclass:: cnct.client.fluent.ConnectClient
   :members:
   :special-members: __getattr__, __call__



Models
------

.. autoclass:: cnct.client.models.NS
   :members:
   :special-members: __getattr__


.. autoclass:: cnct.client.models.Collection
   :members:
   :special-members: __getitem__


.. autoclass:: cnct.client.models.Resource
   :members:
   :special-members: __getattr__, __call__


.. autoclass:: cnct.client.models.ResourceSet
   :members:
   :special-members: __bool__, __iter__, __getitem__


RQL utility
-----------

.. autoclass:: cnct.rql.base.R
   :members:
   :special-members: __and__, __bool__, __eq__, __getattr__, __invert__, __len__, __or__


.. autoclass:: cnct.rql.base.RQLQuery
   :members:
   :special-members: __and__, __bool__, __eq__, __getattr__, __invert__, __len__, __or__


Exceptions
----------

.. autoclass:: cnct.client.exceptions.ClientError
   :members:
