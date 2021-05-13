API Reference
=============

Client
------

.. autoclass:: connect.client.fluent.ConnectClient
   :members:
   :inherited-members:
   :special-members: __getattr__, __call__



Models
------

.. autoclass:: connect.client.models.NS
   :members:
   :inherited-members:
   :special-members: __getattr__


.. autoclass:: connect.client.models.Collection
   :members:
   :inherited-members:
   :special-members: __getitem__


.. autoclass:: connect.client.models.Resource
   :members:
   :inherited-members:
   :special-members: __getattr__, __call__

.. autoclass:: connect.client.models.Action
   :members:
   :inherited-members:
   :special-members: __getattr__, __call__

.. autoclass:: connect.client.models.ResourceSet
   :members:
   :inherited-members:
   :special-members: __bool__, __iter__, __getitem__


RQL utility
-----------

.. autoclass:: connect.client.rql.base.R
   :members:
   :special-members: __and__, __bool__, __eq__, __getattr__, __invert__, __len__, __or__


.. autoclass:: connect.client.rql.base.RQLQuery
   :members:
   :special-members: __and__, __bool__, __eq__, __getattr__, __invert__, __len__, __or__


Exceptions
----------

.. autoclass:: connect.client.exceptions.ClientError
   :members:
