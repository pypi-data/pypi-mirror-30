.. contents:: Table of Contents

Introduction
============

This package is an addon for `ftw.simplelayout`_.
Please make sure you already installed `ftw.simplelayout`_
on your plone site before installing this addon.

``ftw.iframeblock`` privides a block for `ftw.simplelayout`_,
which renders a iframe using `iframe-resizer`_.
Read the setup instructions of iframeresizer carefully:
you need an implementation on both domains.


Linking to sub pages
--------------------

When integrating other websites in iframes and indexing those
contents in the search, we want to be able to link from the search
to a specific iframed sub-page.

In order to make this possible we need to be able to pass the requested
sub-page as GET request param.

For security reason, the origin of both URLs must be the same, otherwise the configured startpage is loaded.

**Examples:**

- ``http://localhost:8080/Plone/the-page?i=http://foo.ch/bar/baz.php``
- ``http://localhost:8080/Plone/the-page?i_iframeblock2=http://foo.ch/bar/baz.php``


Compatibility
-------------

Runs with `Plone <http://www.plone.org/>`_ `4.3.x`.


Installation local development-environment
------------------------------------------

.. code:: bash

    $ git clone git@github.com:4teamwork/ftw.iframeblock.git
    $ cd ftw.iframeblock
    $ ln -s development.cfg buildout.cfg
    $ python2.7 bootstrap.py
    $ bin/buildout
    $ bin/instance fg



Links
-----

- Github: https://github.com/4teamwork/ftw.iframeblock
- Issues: https://github.com/4teamwork/ftw.iframeblock/issues
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.iframeblock

Copyright
---------

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.iframeblock`` is licensed under GNU General Public License, version 2.

.. _ftw.simplelayout: http://github.com/4teamwork/ftw.simplelayout
.. _iframe-resizer: https://github.com/davidjbradshaw/iframe-resizer
