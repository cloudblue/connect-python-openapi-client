# -*- coding: utf-8 -*-

#
# This file is part of the Ingram Micro CloudBlue Connect Python OpenAPI Client.
#
# Copyright (c) 2021 Ingram Micro. All Rights Reserved.
#

from pkg_resources import DistributionNotFound, get_distribution


def get_version():
    try:
        return get_distribution('connect-openapi-client').version
    except DistributionNotFound:
        return '0.0.0'
