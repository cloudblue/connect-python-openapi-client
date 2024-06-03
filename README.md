# Connect Python OpenAPI Client

![pyversions](https://img.shields.io/pypi/pyversions/connect-openapi-client.svg) [![PyPi Status](https://img.shields.io/pypi/v/connect-openapi-client.svg)](https://pypi.org/project/connect-openapi-client/) [![Build Status](https://github.com/cloudblue/connect-python-openapi-client/workflows/Build%20Connect%20Python%20OpenAPI%20Client/badge.svg)](https://github.com/cloudblue/connect-python-openapi-client/actions) [![codecov](https://codecov.io/gh/cloudblue/connect-python-openapi-client/branch/master/graph/badge.svg)](https://codecov.io/gh/cloudblue/connect-python-openapi-client) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=connect-open-api-client&metric=alert_status)](https://sonarcloud.io/dashboard?id=connect-open-api-client)




## Introduction

`Connect Python OpenAPI Client` is the simple, concise, powerful and REPL-friendly CloudBlue Connect API client.

It has been designed following the [fluent interface design pattern](https://en.wikipedia.org/wiki/Fluent_interface).

Due to its REPL-friendly nature, using the CloudBlue Connect OpenAPI specifications it allows developers to learn and
play with the CloudBlue Connect API using a python REPL like [jupyter](https://jupyter.org/) or [ipython](https://ipython.org/).


## Install

`Connect Python OpenAPI Client` requires python 3.9 or later.


`Connect Python OpenAPI Client` can be installed from [pypi.org](https://pypi.org/project/connect-openapi-client/) using pip:

```
$ pip install connect-openapi-client
```


## Development
We use `isort` library to order and format our imports, and `black` - to format the code. 
We check it using `flake8-isort` and `flake8-black` libraries (automatically on `flake8` run).  
For convenience you may run `isort . && black .` to format the code.


## Documentation

[`Connect Python OpenAPI Client` documentation](https://connect-openapi-client.readthedocs.io/en/latest/) is hosted on the _Read the Docs_ service.


## License

``Connect Python OpenAPI Client`` is released under the [Apache License Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).
