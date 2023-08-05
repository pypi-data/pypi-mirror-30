# -*- coding: utf-8 -*-
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import logging


logger = logging.getLogger('webcouturier.dropdownmenu.upgrades')


def upgrade_1012_to_1030(context):
    """Upgrade to version 3.0"""

    # PORTAL PROPERTIES
    pprops = api.portal.get_tool('portal_properties')
    if 'dropdown_properties' in pprops:
        pprops.manage_delObjects(['dropdown_properties'])  # noqa: P001
        logger.info(u'dropdown_properties removed from portal_properties')

    # PORTAL SKINS
    pskin = api.portal.get_tool('portal_skins')
    for name, layers in pskin.getSkinPaths():
        layers = layers.split(',')
        if 'dropdownmenu_sunburst' in layers:
            layers.remove('dropdownmenu_sunburst')
            logger.info(
                u'skin layer dropdownmenu_sunburst removed from {0}'.format(
                    name
                )
            )
        if 'dropdownmenu' in layers:
            layers.remove('dropdownmenu')
            logger.info(
                u'skin layer dropdownmenu removed from {0}'.format(name)
            )
        pskin._getSelections()[name] = ','.join(layers)

    if 'dropdownmenu' in pskin:
        pskin.manage_delObjects(['dropdownmenu'])  # noqa: P001
        logger.info(u'skin path dropdownmenu removed')
    if 'dropdownmenu_sunburst' in pskin:
        pskin.manage_delObjects(['dropdownmenu_sunburst'])  # noqa: P001
        logger.info(u'skin path dropdownmenu_sunburst removed')

    # REGISTRY
    # pre-release cleanup
    registry = getUtility(IRegistry)
    regkey_enable_thumbs = (
        'webcouturier.dropdownmenu.browser.interfaces.'
        'IDropdownConfiguration.enable_thumbs'
    )
    if regkey_enable_thumbs in registry.records:
        del registry.records[regkey_enable_thumbs]
        logger.info(u'registry entry {0} removed'.format(regkey_enable_thumbs))

    # IMPORT REGISTRY PROFILE
    profile_id = 'profile-webcouturier.dropdownmenu:default'
    step_id = 'plone.app.registry'
    setup = api.portal.get_tool('portal_setup')
    setup.runImportStepFromProfile(profile_id=profile_id, step_id=step_id)
    logger.info(
        u'profile {0} with step {1} imported'.format(profile_id, step_id)
    )


def upgrade_step_import_profile(context):
    """Upgrade to version 3.0"""

    # IMPORT REGISTRY PROFILE
    profile_id = 'profile-webcouturier.dropdownmenu:default'
    step_id = 'plone.app.registry'
    setup = api.portal.get_tool('portal_setup')
    setup.runImportStepFromProfile(profile_id=profile_id, step_id=step_id)
    logger.info(
        u'profile {0} with step {1} imported'.format(profile_id, step_id)
    )
