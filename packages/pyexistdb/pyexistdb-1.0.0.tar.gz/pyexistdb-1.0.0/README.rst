pyexistdb
==========


**package**
  .. image:: https://img.shields.io/pypi/v/pyexistdb.svg
    :target: https://pypi.python.org/pypi/pyexistdb
    :alt: PyPI

  .. image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
    :target: https://opensource.org/licenses/Apache-2.0
    :alt: Apache 2 License

  .. image:: https://img.shields.io/pypi/dm/pyexistdb.svg
    :alt: PyPI downloads

**documentation**
  .. image:: https://readthedocs.org/projects/pyexistdb/badge/?version=latest
    :target: http://pyexistdb.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status

..
    **code**
      .. image:: https://travis-ci.org/emory-libraries/eulexistdb.svg?branch=master
        :target: https://travis-ci.org/emory-libraries/eulexistdb
        :alt: travis-ci build

      .. image:: https://coveralls.io/repos/github/emory-libraries/eulexistdb/badge.svg?branch=master
        :target: https://coveralls.io/github/emory-libraries/eulexistdb?branch=master
        :alt: Code Coverage

      .. image:: https://codeclimate.com/github/emory-libraries/eulexistdb/badges/gpa.svg
        :target: https://codeclimate.com/github/emory-libraries/eulexistdb
        :alt: Code Climate

      .. image:: https://landscape.io/github/emory-libraries/eulexistdb/master/landscape.svg?style=flat
         :target: https://landscape.io/github/emory-libraries/eulexistdb/master
         :alt: Code Health

      .. image:: https://requires.io/github/emory-libraries/eulexistdb/requirements.svg?branch=master
        :target: https://requires.io/github/emory-libraries/eulexistdb/requirements/?branch=master
        :alt: Requirements Status


**pyexistdb** is a Python 3 module that
provides utilities and classes for interacting with the `eXist-db XML
Database <http://exist.sourceforge.net/>`_  in a
pythonic, object-oriented way, with optional `Django
<https://www.djangoproject.com/>`_ integration.

**pyexistdb** is a fork of `eulexistdb <https://eulexistdb.readthedocs.io/en/stable/>`_ which was originally
created by the Digital Programs and Systems Software Team of `Emory University Libraries
<http://web.library.emory.edu/>`_.

**pyexistdb.query** provides a **QuerySet** class modeled after
`Django QuerySet
<http://docs.djangoproject.com/en/1.3/ref/models/querysets/>`_ in
functionality.  This module provides **model** and **manager** classes
that can be used to connect an `eulxml
<https://github.com/emory-libraries/eulxml>`_ **XmlObject** with the
**QuerySet** class, in order to generate XQueries and return the
results as XmlObject instances.  However, configuring the XmlObject
XPaths to make efficent XQueries against eXist and take advantage of
the full-text index does require expertise and familiarity with eXist.

When used with `Django <https://www.djangoproject.com/>`_,
**pyexistdb** can pull the database connection configuration from
Django settings, provides a custom management command for working with
the collection index configuration index in the configured eXist
database, and also provides a custom template tag that can be used to
highlight full-text search matches.

**pyexistdb.db** provides access to an eXist-db instance through
eXist's `XML-RPC API
<http://exist.sourceforge.net/devguide_xmlrpc.html>`_.

Dependencies
------------

**pyexistdb** currently depends on
`eulxml <https://github.com/emory-libraries/eulxml>`_.

**pyexistdb** can be used without
`Django <https://www.djangoproject.com/>`_, but additional
functionality is available when used with Django.


Contact Information
-------------------
**pyexistdb** is maintained by `The Research Software Company <http://www.chelem.co.il>`_.

Please contact us at contact@chelem.co.il .

License
-------
**pyexistdb** is distributed under the Apache 2.0 License.


Developer notes
---------------

To install dependencies for your local check out of the code, run ``pip install``
in the ``pyexistdb`` directory (the use of `virtualenv`_ is recommended)::

    pip install -e .

.. _virtualenv: http://www.virtualenv.org/en/latest/

If you want to run unit tests or build sphinx documentation, you will also
need to install development dependencies::

    pip install -e . "pyexistdb[dev]"

Running the unit tests requires an eXist-DB database instance.  Before running tests, you will
need to copy ``test/localsettings.py.dist`` to ``test/localsettings.py`` and edit the
configuration for your test instance of eXist.

To run all unit tests::


    nosetests test/ # for normal development
    nosetests test/ --with-coverage --cover-package=pyexistdb --cover-xml --with-xunit   # for continuous integration

To run unit tests for a specific module, use syntax like this::

    nosetests test/test_existdb/test_db.py


To generate sphinx documentation::

    cd doc
    make html


