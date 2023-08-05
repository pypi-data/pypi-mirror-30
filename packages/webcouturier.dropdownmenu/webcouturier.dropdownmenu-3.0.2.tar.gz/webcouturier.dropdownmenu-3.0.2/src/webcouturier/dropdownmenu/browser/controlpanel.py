# -*- coding: utf-8 -*-
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from Products.CMFPlone import PloneMessageFactory as _
from webcouturier.dropdownmenu.browser.interfaces import IDropdownConfiguration


class DropdownControlPanelForm(RegistryEditForm):

    id = 'DropdownControlPanel'
    schema = IDropdownConfiguration
    schema_prefix = (
        'webcouturier.dropdownmenu.browser.interfaces.IDropdownConfiguration'
    )

    label = _(
        u'A dropdown menu configuration.',
        default=u'A dropdown menu configuration.'
    )
    description = _(
        u'Settings to configure dropdown menus for global navigation.',
        default=u'Settings to configure dropdown menus for global navigation.'
    )


class DropdownControlPanel(ControlPanelFormWrapper):
    form = DropdownControlPanelForm
