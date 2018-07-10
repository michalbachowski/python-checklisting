========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - |
        |
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/python-checklisting/badge/?style=flat
    :target: https://readthedocs.org/projects/python-checklisting
    :alt: Documentation Status

.. |version| image:: https://img.shields.io/pypi/v/checklisting.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/checklisting

.. |commits-since| image:: https://img.shields.io/github/commits-since/michalbachowski/python-checklisting/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/michalbachowski/python-checklisting/compare/v0.1.0...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/checklisting.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/checklisting

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/checklisting.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/checklisting

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/checklisting.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/checklisting


.. end-badges

Service checklisting made easy and automated

* Free software: MIT license

Installation
============

::

    pip install checklisting

Documentation
=============

https://python-checklisting.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
