webcouturier.dropdownmenu
=========================

.. image:: http://img.shields.io/pypi/v/webcouturier.dropdownmenu.svg
    :target: https://pypi.python.org/pypi/webcouturier.dropdownmenu

.. image:: https://img.shields.io/travis/collective/webcouturier.dropdownmenu/master.svg
    :target: http://travis-ci.org/collective/webcouturier.dropdownmenu

.. image:: https://img.shields.io/coveralls/collective/webcouturier.dropdownmenu/master.svg
    :target: https://coveralls.io/r/collective/webcouturier.dropdownmenu

Overview
--------

The dropdown solution for Plone since 2007.

You will get the dropdown menus for those items in global navigation that have the subitems.
Submenus are built based on the same policy as the Site Map,
it will show the same tree as you would get in the Site Map or navigation portlet being in appropriate section.


How it works
------------

Dropdown menus are build based on the same policy as the Site Map,
it will show the same tree as you would get in the Site Map or navigation portlet being in appropriate section.

This means - no **private** objects for anonymous; no objects, excluded from the navigation -
exactly the same behavior you would expect from Site Map or navigation portlet.


Installation
------------

As any add-ons, please follow the `official install documentation <https://docs.plone.org/manage/installing/installing_addons.html>`_.


Tips
----

While disabling clicking the links with children, one may want the links in the global navigation bar to be clickable nevertheless

What you need is to customize the ``browser/static/dropdown.js`` file like the following:

::

    jQuery(function ($) {
        $('#portal-globalnav ul .noClick').click(function (e) {
            e.preventDefault();
        });
    });

Note that we have added **ul** in the jQuery selector. This will stop
clickability of the links in the dropdowns only, but not the section's link
in the global navigation bar itself.

Contribute
----------

.. image:: https://travis-ci.org/collective/webcouturier.dropdownmenu.svg?branch=master
    :target: https://travis-ci.org/collective/webcouturier.dropdownmenu

.. image:: https://coveralls.io/repos/github/collective/webcouturier.dropdownmenu/badge.svg?branch=master
    :target: https://coveralls.io/github/collective/webcouturier.dropdownmenu?branch=master


- Issue Tracker: https://github.com/collective/webcouturier.dropdownmenu/issues
- Source Code: https://github.com/collective/webcouturier.dropdownmenu


We'd be happy to see many commits, forks and pull-requests to make webcouturier.dropdownmenu even better.

If you are having issues, please let us know.

`Open an issue <http://github.com/collective/webcouturier.dropdownmenu/issues>`_ or send us an e-mail to dev@bluedynamics.com.



Credits
-------

Authors:

- Denys Mishunov [mishunov] Twitter_ · `Google+`_

Contributors:

- Wichert Akkerman [wichert] `Simplon`_
- JeanMichel FRANCOIS [toutpt] `Makina-Corpus`_
- Thomas Desvarin [thomasdesvenain] `Ecréall`_
- Maurits van Rees [maurits]
- David Glick [davisagli]
- Matt Halstead [matthal]
- Leonardo J. Caballero G. [macagua]
- Florian Schulze [fschulze]
- Jens Klein [jensens] `BlueDynamics Alliance`_
- Peter Holzer [agitator] `BlueDynamics Alliance`_
- Johannes Raggam [thet] `BlueDynamics Alliance`_
- Sven Strack [svx]


.. _Makina-Corpus: http://www.makina-corpus.com
.. _Simplon: http://www.simplon.biz
.. _Twitter: http://twitter.com/#!/mishunov
.. _Google+: https://plus.google.com/102311957553961771735/posts
.. _toutpt: http://profiles.google.com/toutpt
.. _Ecréall: http://www.ecreall.com/
.. _BlueDynamics Alliance: http://bluedynamics.com/
