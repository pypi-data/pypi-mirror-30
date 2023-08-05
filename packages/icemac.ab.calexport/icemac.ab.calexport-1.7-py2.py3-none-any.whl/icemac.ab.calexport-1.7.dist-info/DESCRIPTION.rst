This package provides a calendar HTML export feature for `icemac.ab.calendar`_.

*Caution:* This package might not be as customizable as needed for a general
HTML calendar export.

.. _`icemac.ab.calendar` : https://pypi.org/project/icemac.ab.calendar

Copyright (c) 2015 - 2018 Michael Howitz

All Rights Reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.

.. contents::

=========
 Hacking
=========

Source code
===========

Get the source code::

   $ hg clone https://bitbucket.org/icemac/icemac.ab.calexport

or fork me on: https://bitbucket.org/icemac/icemac.ab.calexport

Running the tests
=================

To run the tests yourself call::

  $ python2.7 bootstrap.py
  $ bin/buildout -n
  $ bin/py.test


===========
 Changelog
===========

1.7 (2018-03-16)
================

- Update to `icemac.ab.calendar >= 3.0`.


1.6 (2017-12-26)
================

- Add breadcrumbs.

- Also release as wheel.


1.5 (2017-04-08)
================

- Allow umlauts in month names.

- Update to changes in test infrastructure in `icemac.addressbook >= 4.0`.


Older versions
==============

See `OLD_CHANGES.rst`_.

.. _`OLD_CHANGES.rst` : https://bitbucket.org/icemac/icemac.ab.calexport/raw/tip/OLD_CHANGES.rst


