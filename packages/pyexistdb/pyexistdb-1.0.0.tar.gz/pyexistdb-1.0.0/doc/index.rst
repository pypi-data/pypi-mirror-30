Pyexistdb
==========

Pyexistdb is a library for accessing, querying, and updating an `eXist-db
<http://exist.sourceforge.net/>`_ XML database using idiomatic Python.
:class:`~pyexistdb.db.ExistDB` provides basic read-write access. pyexistdb
doesn't require `Django <http://www.djangoproject.com/>`_, but when they're
used together, developers can define :class:`~pyexistdb.models.XmlModel`
subclasses to automate `XQuery <http://www.w3.org/TR/xquery/>`_ searching of
the eXist database based on the model's `XPath
<http://www.w3.org/TR/xpath/>`_ fields. Even without Django configuration,
developers can utilize this automatic XQuery generation by constructing a
:class:`~pyexistdb.query.QuerySet` referencing an
:class:`~eulxml.xmlmap.XmlObject` subclass and a database.

Contents
--------

.. toctree::
   :maxdepth: 3
   
   existdb
   changelog

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
