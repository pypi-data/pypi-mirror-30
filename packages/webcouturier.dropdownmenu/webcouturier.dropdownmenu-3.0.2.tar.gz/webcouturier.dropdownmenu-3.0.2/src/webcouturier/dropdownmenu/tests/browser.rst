Browser Tests
=============


Here we can test our website with a programmable browser. First we
need to define this browser::

    >>> from plone.testing.z2 import Browser
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from plone.app.testing import TEST_USER_NAME
    >>> browser = Browser(layer['app'])
    >>> user = TEST_USER_NAME
    >>> pwd = TEST_USER_PASSWORD
    >>> browser.addHeader('Authorization', 'Basic %s:%s' % (user, pwd))
    >>> browser.handleErrors = False
    >>> browser.addHeader('Accept-Language', 'en-US')
    >>> portal = layer['portal']
    >>> for fid in ['folder-0', 'folder-1']:
    ...     folder = portal[fid]
    ...     for j in range(2):
    ...         sub_id = 'sub-%s' % j
    ...         sid = folder.invokeFactory('Folder', sub_id)
    ...         sub = folder[sub_id]
    ...         sub.reindexObject()
    ...         if j == 0:
    ...             subsub_id = 'sub-sub-0'
    ...             ssid = sub.invokeFactory('Folder', subsub_id)
    ...             sub[ssid].reindexObject()
    >>> import transaction
    >>> transaction.commit()

Let us get the absolute url of our website and try to load that with
the testbrowser::

    >>> browser.open(portal.absolute_url())
    >>> '"documentFirstHeading">Plone site' in browser.contents or 'Welcome to Plone' in browser.contents
    True


Enable or disable clicking on parent folders.
---------------------------------------------

There are links to several folders::

    >>> browser.getLink(url='http://nohost/plone/folder-0').url
    'http://nohost/plone/folder-0'

    >>> browser.getLink(url='http://nohost/plone/folder-1').url
    'http://nohost/plone/folder-1'

    >>> browser.getLink(url='http://nohost/plone/folder-0/sub-0').url
    'http://nohost/plone/folder-0/sub-0'

    >>> browser.getLink(url='http://nohost/plone/folder-0/sub-1').url
    'http://nohost/plone/folder-0/sub-1'

    >>> browser.getLink(url='http://nohost/plone/folder-0/sub-0/sub-sub-0').url
    'http://nohost/plone/folder-0/sub-0/sub-sub-0'


Now change the enable_parent_clickable setting so parent folders with
children are not clickable anymore.  They are just hoverable, which
allows us to get to the children::

    >>> from webcouturier.dropdownmenu.browser.interfaces import IDropdownConfiguration
    >>> from plone import api
    >>> api.portal.get_registry_record(
    ...     'enable_parent_clickable',
    ...     interface=IDropdownConfiguration
    ... )
    True

    >>> api.portal.set_registry_record(
    ...     'enable_parent_clickable',
    ...     False,
    ...     interface=IDropdownConfiguration
    ... )
    >>> transaction.commit()
    >>> api.portal.get_registry_record(
    ...     'enable_parent_clickable',
    ...     interface=IDropdownConfiguration
    ... )
    False

Now we try again::

    >>> browser.open(portal.absolute_url())
    >>> '"documentFirstHeading">Plone site' in browser.contents or 'Welcome to Plone' in browser.contents
    True

This time, the link to the folder should have a special class 'noClick' in
order to be not-clickable - javascript handles the behavior of this class::

    >>> 'noClick' in browser.getLink(url='http://nohost/plone/folder-0').attrs['class']
    True

Now check all folders::

    >>> 'noClick' in browser.getLink(url='http://nohost/plone/folder-1').attrs['class']
    True

    >>> folder_url = 'http://nohost/plone/folder-0/sub-0'
    >>> 'noClick' in browser.getLink(url=folder_url).attrs['class']
    True

    >>> folder_url = 'http://nohost/plone/folder-0/sub-1'
    >>> 'noClick' in browser.getLink(url=folder_url).attrs['class']
    False

    >>> 'noClick' in browser.getLink(url='http://nohost/plone/folder-0/sub-0/sub-sub-0').attrs['class']
    False

    >>> 'noClick' in browser.getLink(url='http://nohost/plone/folder-0/sub-0/sub-sub-0').attrs['class']
    False

Let's undo our change to the enable_parent_clickable setting, in case
someone decided to add some tests below that expect the default.  You
might want to just add a new text file then (and probably rename this
one)::

    >>> api.portal.set_registry_record(
    ...     'enable_parent_clickable',
    ...     True,
    ...     interface=IDropdownConfiguration
    ... )
    >>> import transaction
    >>> transaction.commit()

