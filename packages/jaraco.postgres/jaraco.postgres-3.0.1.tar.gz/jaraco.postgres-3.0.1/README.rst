.. image:: https://img.shields.io/pypi/v/jaraco.postgres.svg
   :target: https://pypi.org/project/jaraco.postgres

.. image:: https://img.shields.io/pypi/pyversions/jaraco.postgres.svg

.. image:: https://img.shields.io/travis/jaraco/jaraco.postgres/master.svg
   :target: https://travis-ci.org/jaraco/jaraco.postgres

.. .. image:: https://img.shields.io/appveyor/ci/jaraco/skeleton/master.svg
..    :target: https://ci.appveyor.com/project/jaraco/skeleton/branch/master

.. image:: https://readthedocs.org/projects/jaracopostgres/badge/?version=latest
   :target: https://jaracopostgres.readthedocs.io/en/latest/?badge=latest

Routines and fixtures for launching and managing
`PostgreSQL <https://postgresql.org>`_ instances.

Pytest Plugin
=============

This library includes a pytest plugin. To enable it, simply
include this library in your test requirements.

Then, in your tests, simply add a ``postgresql_instance``
parameter to your functions.

Instance
--------

The ``postgresql_instance`` is a ``jaraco.postgres.PostgresServer``
instance with ``host`` and ``port`` properties.
