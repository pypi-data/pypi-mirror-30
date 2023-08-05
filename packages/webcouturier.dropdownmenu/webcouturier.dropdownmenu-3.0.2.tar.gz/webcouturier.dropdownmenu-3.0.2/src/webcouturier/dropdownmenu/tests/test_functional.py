# -*- coding: utf-8 -*-
from plone.testing import layered
from webcouturier.dropdownmenu.testing import DROPDOWN_FUNCTIONAL_TESTING

import doctest
import unittest2 as unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(
        [
            layered(
                doctest.DocFileSuite(
                    'browser.rst',
                ),
                layer=DROPDOWN_FUNCTIONAL_TESTING
            ),
        ]
    )
    return suite
