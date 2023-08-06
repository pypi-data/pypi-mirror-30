###############################################################################
#
# Copyright (c) 2017 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Tests
$Id: tests.py 4669 2017-12-21 01:22:32Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import unittest
import doctest


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('checker.txt'),
        doctest.DocFileSuite('util.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
