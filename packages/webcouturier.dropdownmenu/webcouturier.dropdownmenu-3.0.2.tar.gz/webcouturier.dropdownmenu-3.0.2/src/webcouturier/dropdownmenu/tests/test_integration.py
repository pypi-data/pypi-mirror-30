# -*- coding: utf-8 -*-
from plone import api
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from webcouturier.dropdownmenu.testing import DROPDOWN_INTEGRATION_TESTING

import unittest2 as unittest
import zope.interface


class TestDropdownmenu(unittest.TestCase):

    layer = DROPDOWN_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        request = self.layer['request']
        from webcouturier.dropdownmenu.browser.dropdown import DropdownMenuViewlet  # noqa
        viewlet = DropdownMenuViewlet(portal, request, None, None)
        setRoles(portal, TEST_USER_ID, ['Manager'])

        # we have 2 folders created on the layer right away
        self.root_folders_ids = ['folder-0', 'folder-1']

        # update the dropdownmenu viewlet
        viewlet.update()

        for folder_id in self.root_folders_ids:
            self.assertIn(
                folder_id,
                [tab['id'] for tab in viewlet.portal_tabs]
            )

        setRoles(portal, TEST_USER_ID, ['Member'])
        self.portal = portal
        self.viewlet = viewlet

    def addSubFolders(self):
        # add some subfolders to one of the folders
        rf = getattr(self.portal, 'folder-0')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        for i in range(2):
            api.content.create(container=rf,
                               type='Folder', id='sub-{0}'.format(i))
        setRoles(self.portal, TEST_USER_ID, ['Member'])

        return rf.absolute_url()

    def test_no_subfolders_without_content(self):
        # since we don't have subfolders yet, we should not have dropdowns
        for tab_url in [getattr(self.portal, folder_id).absolute_url()
                        for folder_id in self.root_folders_ids]:
            self.assertEqual(self.viewlet.getTabObject(tab_url), '')

    def test_dropdownmenus_available(self):
        rf_url = self.addSubFolders()
        self.assertNotEqual(
            self.viewlet.getTabObject(rf_url),
            '',
            'We don\'t have the sub-folders available in the global navigation'
        )

    def test_subfolders_in_dropdownmenus(self):
        rf_url = self.addSubFolders()
        self.viewlet.update()
        self.assertIn(
            'href="http://nohost/plone/folder-0/sub-0"',
            self.viewlet.getTabObject(rf_url),
            'The sub-folder\'s URL is not available in the global navigation'
        )

    def test_leaks_in_dropdownmenus(self):
        rf_url = self.addSubFolders()
        self.viewlet.update()
        self.assertNotIn(
            'href="http://nohost/plone/folder-0"',
            self.viewlet.getTabObject(rf_url),
            'We have the leakage of the top level folders in the dropdownmenus'
        )


class TestINavigationRootDropdownmenu(unittest.TestCase):
    """ Test that the dropdownmenus play nice with different INavigationRoot.
    """

    layer = DROPDOWN_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        request = self.layer['request']
        # we should have 2 folders in the site's root from the layer. Lets
        # mark one of it's sub-folders ('sub-0') as a navigation root
        self.f1 = portal['folder-0']
        zope.interface.alsoProvides(self.f1, INavigationRoot)
        from webcouturier.dropdownmenu.browser.dropdown import DropdownMenuViewlet  # noqa
        viewlet = DropdownMenuViewlet(portal, request, None, None)
        viewlet.update()

        self.root_folders_ids = ['sub-0', 'sub-1']
        self.subfolders = ['sub-sub-0', 'sub-sub-1']
        self.portal = portal
        self.request = request
        self.viewlet = viewlet
        self.rf_url = self.f1.absolute_url()

    def test_no_root_folder(self):
        self.assertNotIn(
            '<a href="http://nohost/plone/folder-0"',
            self.viewlet.getTabObject(self.rf_url),
            'The root folder itself is in the globalnavigation'
        )

    def test_dropdownmenus_content(self):
        # Tests the tree builder to aply nice with the INavigationRoot
        self.assertNotIn(
            '<a href="http://nohost/plone/folder-1"',
            self.viewlet.getTabObject(self.rf_url),
            'The dropdown menus don\'t respect the iNavigationRoot.'
        )
