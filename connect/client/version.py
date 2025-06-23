# -*- coding: utf-8 -*-

#
# This file is part of the CloudBlue Connect Python OpenAPI Client.
#
# Copyright (c) 2025 CloudBlue. All Rights Reserved.
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
