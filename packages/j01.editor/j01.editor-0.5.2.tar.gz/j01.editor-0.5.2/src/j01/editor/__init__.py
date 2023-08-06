###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Widgt mixin classes shared in form and jsform

$Id: __init__.py 4669 2017-12-21 01:22:32Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

from xml.sax import saxutils


def escape(value):
    """Escape the given value"""
    if isinstance(value, basestring):
        value = saxutils.escape(value)
    return value
