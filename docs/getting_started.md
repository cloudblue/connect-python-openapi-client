## Terminology

### Resource

A **resource** is an object with a type, associated data and relationships to other resources (example: `product`).

### Collection

A **collection** is a set of **resources** of the same type (example: `products`).

### Namespace

A **namespace** is a group of related **collections** (example: `localization`).

### Sub-namespace

A **sub-namespace** is a **namespace** nested under a parent **namespace**.

### Sub-collection

A **sub-collection** is a collection nested under a **resource** (example: `product items`).

### Action

An **action** is an operation that can be performed on a **collection** or a **resource** (example: `approve request`).


## Requirements

*connect-openapi-client* runs on python 3.7 or later.

## Install

*connect-openapi-client* is a small python package that can be installed
from the [pypi.org](https://pypi.org/project/connect-openapi-client/) repository.

```
$ pip install connect-openapi-client
```

## Create a client instance

To use *connect-openapi-client* first of all you have to create an instance of the `ConnectClient` object:

```python
from connect.client import ConnectClient

client = ConnectClient('ApiKey SU-000-000-000:xxxxxxxxxxxxxxxx')
```
