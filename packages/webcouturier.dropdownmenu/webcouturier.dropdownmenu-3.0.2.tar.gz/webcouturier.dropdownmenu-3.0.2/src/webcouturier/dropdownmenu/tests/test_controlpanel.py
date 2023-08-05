# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import logout
from plone.registry.interfaces import IRegistry
from webcouturier.dropdownmenu.browser.interfaces import IDropdownConfiguration
from webcouturier.dropdownmenu.testing import DROPDOWN_INTEGRATION_TESTING
from zope.component import getUtility

import unittest


class ControlPanelTestCase(unittest.TestCase):

    layer = DROPDOWN_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.controlpanel = self.portal['portal_controlpanel']

    def test_controlpanel_has_view(self):
        request = self.layer['request']
        view = api.content.get_view(
            u'dropdown-controlpanel',
            self.portal,
            request
        )
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_controlpanel_view_is_protected(self):
        from AccessControl import Unauthorized
        logout()
        with self.assertRaises(Unauthorized):
            self.portal.restrictedTraverse('@@dropdown-controlpanel')

    def test_controlpanel_installed(self):
        actions = [a.getAction(self)['id']
                   for a in self.controlpanel.listActions()]
        self.assertIn('DropdownConfiguration', actions)

    def test_controlpanel_removed_on_uninstall(self):
        setup_tool = self.portal['portal_setup']
        with api.env.adopt_roles(['Manager']):
            setup_tool.runAllImportStepsFromProfile(
                'profile-webcouturier.dropdownmenu:uninstall'
            )
        actions = [a.getAction(self)['id']
                   for a in self.controlpanel.listActions()]
        self.assertNotIn('DropdownConfiguration', actions)


class RegistryTestCase(unittest.TestCase):

    layer = DROPDOWN_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(  # noqa: P001
            IDropdownConfiguration
        )

    def test_css_class_blacklist_record_in_registry(self):
        self.assertTrue(hasattr(self.settings, 'dropdown_depth'))
        self.assertEqual(self.settings.dropdown_depth, 3)

    def test_records_removed_on_uninstall(self):
        setup_tool = self.portal['portal_setup']
        with api.env.adopt_roles(['Manager']):
            setup_tool.runAllImportStepsFromProfile(
                'profile-webcouturier.dropdownmenu:uninstall'
            )

        records = [
            IDropdownConfiguration.__identifier__ + '.dropdown_depth',
        ]

        for r in records:
            self.assertNotIn(r, self.registry)
