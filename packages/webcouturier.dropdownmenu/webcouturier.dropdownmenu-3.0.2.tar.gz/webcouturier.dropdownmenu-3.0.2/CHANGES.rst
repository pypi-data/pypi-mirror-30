Changelog
=========


3.0.2 (2018-03-22)
------------------

- made last childs sub sub items float left instead of right (outside of screen width)
  [iham]

- Mobile navigation with expandable/collapsable submenu levels.
  Resource registration cleanup
  [agitator]

- To set global section active tab, use ``selected_portal_tab`` instead simple url comparison.
  Fixes the ``Home`` tab always set active.
  Fixes: #31.
  [thet]

- Fix AttributeError during upgrade.
  [abosio]

- Improve README
  [svx]

3.0.1 (2016-11-24)
------------------

- Merge resources with default bundle
  [agitator]


3.0.0 (2016-11-14)
------------------

- Remove ``utils``, move its methods into the dropdown browser view and eliminate the need to call a module from the page template.
  [thet]

- Avoid waking up all objects in this navigation structure.
  [thet]

- Add selected class also to submenu items.
  [thet]

- Add ``review_state`` to tab-links.
  [thet]

- Add upgrade steps for 3.0 upgrade and remove obsolete ones.
  [thet]

- Move ``webcouturier.dropdownmenu.configlet`` to ``webcouturier.dropdownmenu.browser.controlpanel``.
  [thet]

- Add uninstall profile.
  [thet]

- Rename resource and bundle names to not contain a dot, because that's not supported by the less toolchain.
  [thet]

- Make images work within dropdownmenus, cleanup of settings and conditions
  [agitator]

- Make main menu items with subitems clickable by removing ``data-toggle`` from ``<a>`` element.
  See: http://stackoverflow.com/questions/19935480/bootstrap-3-how-to-make-head-of-dropdown-link-clickable-in-navbar
  [thet]

- More Twitter Bootstrap alignments.
  Use Twitter Bootstrap classes along with ``plone-`` prefixed ones.
  Makes sure, it will work in Bootstrap-less and Bootstrap based themes.
  [thet]

- Plone 5 compatibility
  [davilima6, fulv, jensens, lewecki]

- Add some css classes to make styling easier.
  [jensens]

- Default value none (not None) for enable_thumbs setting
  [jensens]

- Add Brazilian Portuguese translation.
  [hvelarde]

- Fix package dependencies and metadata; explicitly drop support for Plone 4.0.
  [hvelarde]

- Added option to show image and description in dropdownmenu [espen]

- Codebase cleanup.
  [thet]

- Add markup and a profile to support Twitter Bootstrap dropdowns.
  [rpatterson]

- Handle Unauthorized exceptions when rendered in context of unauthorized
  objects. Can happen with standard_error_pages
  [do3cc]

- First iteration to port codebase to be compatible with Plone 5
  [lewicki]

- Update buildout to Plone 5
  [davilima6]

- Register resource directory to enable csscompilation entry in registry.xml
  [davilima6]


2.3.1 (2012-07-26)
------------------

- move css from import to link
  [toutpt]

2.3 (2012-01-23)
----------------

- Moved the plone.app.testing and unittest2 dependencies to a test extra.
  [Maurits]

- Only load the CMF permissions when on Plone 4.1 or higher.
  [maurits]

- fix unkown version in quickinstaller.
  [toutpt]

- fix typo in skins.xml provide wrong install on sunburst
  [toutpt]

- rename dropdown css from dtml to static css
  [toutpt]

2.2 (August 17, 2011)
---------------------

- Javascript simplification using jQuery.
  [spliter]

- Fixed the INavigationRoot treatment by the dropdown menus.
  Fixes
  https://github.com/mishunov/webcouturier.dropdownmenu/pull/3 and
  https://github.com/mishunov/webcouturier.dropdownmenu/issues/1
  [spliter]

- Add dropdowmenu layer to all themes.
  [thomasdesvenain]

- Added enable_parent_clickable option in config panel.  The default
  of True corresponds with standard behaviour until now.  When
  False, menu items that have children are not clickable.
  [maurits]

- Fix Plone4.1 startup issue: http://dev.plone.org/plone/ticket/11837
  [toutpt]

2.1 (2010-09-23)
----------------

- Add z3c.autoinclude entry point so ZCML is loaded automatically in Plone.
  [davisagli]

- Fix icons for compatibility with Plone 4.
  [matthal]

- Added support for i18n
  [macagua]

- Added Spanish translation
  [macagua]

2.0 (2009-05-26)
----------------

- Updated README.txt with the whole bunch of information that
  users need about the package.
  [spliter]

- Icon for the package's configlet link.
  [spliter]

- Added configlet for managing dropdown settings rom Plone
  Control panel.
  [spliter]

- Added caching feature for output xhtml.
  [spliter]

- Fixed an IE Javascript error when dropdown.js was loaded on
  templates without a #portal-globalnav.
  [davisagli]

1.1.5 (2008-04-19)
------------------

- Made the package work in both Plone 3.0.x and Plone 3.1
  [spliter]

- Got rid of buggy default skin's resetting in package's profile
  [spliter]

- Look for 'path' in the global tabs data, if it's available then
  it's used to get the object instead of trying to reconstruct it
  from the url which fails in many cases.
  [fschulze]

- Got rid of hardcoded version of plone.browserlayer. It's up to
  users now to decide what version of plone.browserlayer to use.
  [spliter]

1.1.4 (2008-04-11)
------------------

- Fixed the bug when you have could get the error in case your navigation
  root differs from site root. In this case you could get
  "'NoneType' object has no attribute 'endswith'" error
  [spliter]

1.1.3 (2008-04-09)
------------------

- Switched the package from using browser resource for the main
  stylesheet. It's now in skins/ to follow main theme's colors
  better
  [spliter]

- Added a workaround for objects that contain spaces in their ID's
  [spliter]

- Fixed the problem with images in the site's root
  [spliter]

- Only override the depth for navtree queries for the dropdown menus.
  The override for the path was a nop for the common case but would
  break for sites with a different navigation root.
  [wichert]

- Call constructor for base class in our DropdownMenuViewlet class. This
  removes some boilerplate code and makes sure everything is initialised
  properly.
  [wichert]

1.1 (2007-10-29)
----------------

- Dropdownmenu uses it's own builder now (instead of sharing the same one
  with site map). Implemented new property ``dropdownDepth`` to contain
  depth property for dropdown menu separately from ``sitemapDepth``.
  [spliter]

- Fixed the problem with installation in Plone 3.0.2 because of relations
  with webstats.js file
  [spliter]


1.0 (2007-10-05)
----------------

- Initial release. Tested in all modern browsers, incl. Safari, IE6, IE7
  and so on.
  [spliter]
