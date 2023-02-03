# -*- coding: utf-8 -*-

#
# This file is part of the Ingram Micro CloudBlue Connect Python OpenAPI Client.
#
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.
#
try:
    from importlib.metadata import version
except Exception:
    from importlib_metadata import version


def get_version():
    try:
        return version('connect-openapi-client')
    except Exception:
        return '0.0.0'
