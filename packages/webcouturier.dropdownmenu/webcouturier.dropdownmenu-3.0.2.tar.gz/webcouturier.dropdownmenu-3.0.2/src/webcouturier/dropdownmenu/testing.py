# -*- coding: utf-8 -*-
from plone import api
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.testing import z2
from Products.CMFCore.utils import getToolByName

import webcouturier.dropdownmenu


class WebcouturierDropdownmenuLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=webcouturier.dropdownmenu)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'webcouturier.dropdownmenu:default')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        workflowTool = getToolByName(portal, 'portal_workflow')   # noqa: P001
        workflowTool.setDefaultChain('simple_publication_workflow')
        for i in range(2):
            folder_id = 'folder-{0}'.format(i)
            api.content.create(container=portal,
                               type='Folder', id=folder_id)
        setRoles(portal, TEST_USER_ID, ['Member'])


DROPDOWN_FIXTURE = WebcouturierDropdownmenuLayer()


DROPDOWN_INTEGRATION_TESTING = IntegrationTesting(
    bases=(DROPDOWN_FIXTURE,),
    name='WebcouturierDropdownmenuLayer:IntegrationTesting'
)


DROPDOWN_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(DROPDOWN_FIXTURE,),
    name='WebcouturierDropdownmenuLayer:FunctionalTesting'
)


DROPDOWN_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        DROPDOWN_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='WebcouturierDropdownmenuLayer:AcceptanceTesting'
)
