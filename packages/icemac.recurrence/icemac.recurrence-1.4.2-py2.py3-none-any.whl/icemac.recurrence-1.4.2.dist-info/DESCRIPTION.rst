This package provides helper functions to compute recurrences of events in a
environment using the Zope Component Architecture (ZCA).

Copyright (c) 2013-2018 Michael Howitz

All Rights Reserved.

This software is subject to the provisions of the Zope Public License,
Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE.

.. contents::

=====
Usage
=====

* Register the package at the ZCA via ZCML::

  <include package="icemac.recurrence" />

* Compute recurrences. The example computes the 2nd Tuesday each month.::

      >>> from icemac.recurrence import get_recurrences
      >>> get_recurrences(
      ...     datetime=datetime(2015, 10, 13, 11, 15),
      ...     period='nth weekday of month',
      ...     interval_start=datetime(2015, 1, 1),
      ...     interval_end=datetime(2015, 12, 31))
      [datetime(2015, 10, 13, 11, 15),
       datetime(2015, 11, 10, 11, 15),
       datetime(2015, 12, 8, 11, 15)]

* Supported recurrence periods:

  * ``daily``
  * ``weekly``
  * ``biweekly``
  * ``nth weekday of month``
  * ``nth weekday every other month``
  * ``nth weekday from end of month``
  * ``nth weekday from end of other month``
  * ``yearly``

=========
 Hacking
=========

Source code
===========

Get the source code::

   $ hg clone https://bitbucket.org/icemac/icemac.recurrence

or fork me on: https://bitbucket.org/icemac/icemac.recurrence

Running the tests
=================

To run the tests yourself call::

  $ python2.7 bootstrap.py
  $ bin/buildout -n
  $ bin/py.test


===========
 Changelog
===========

1.4.2 (2018-03-16)
==================

- Fix the computation of monthly recurrences not to return a date before the
  given `interval_start` date.


1.4.1.post1 (2017-12-26)
========================

- Also release as wheel.


1.4.1 (2017-04-11)
==================

- Fix a corner case in the computation of monthly recurrences: If the
  beginning of the interval for which recurrences should be computed was
  outside DST but the recurrence date was inside DST - it was incorrectly
  returned with a time zone object which did not have DST switched on.


1.4 (2017-04-08)
================

- No longer exclude tests from coverage report.


1.3.1 (2017-02-04)
==================

- Fix computation of biweekly recurrences: Previously the first recurrence with
  a matching weekday in the interval was used as the first result for the
  interval. This is only correct in half of the cases. Now the computation of
  the first recurrence in the interval takes into account that it has to be an
  even number of weeks after the recurrence start date and it handles DST
  differences correctly.


1.3 (2017-01-07)
================

- Add Manifest and clean up coverage configuration.


1.2 (2016-04-16)
================

- Fix handling for dates with a timezone which has a daylight saving time
  (DST): The local time of the recurrence does not change when switching DST
  though the UTC representation of the time will now change.


1.1 (2016-03-01)
================

- Shorten the import path of ``get_recurrences()`` from
  ``icemac.recurrence.recurrence`` to just ``icemac.recurrence``.

- Refactor tests to use ``py.test`` fixtures.

- Fix an off by one month error in the periods `nth weekday every other month`
  and `nth weekday from end of other month`.

- Bring the test coverage to 100 % even in branch coverage.


1.0.1 (2015-10-22)
==================

- Fix broken 1.0.0 release.


1.0.0 (2015-10-13)
==================

* Extract package from `icemac.ab.calendar` for reuse in other projects.


