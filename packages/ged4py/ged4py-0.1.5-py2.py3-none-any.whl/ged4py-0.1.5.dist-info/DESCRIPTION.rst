========================
GEDCOM parser for Python
========================


.. image:: https://img.shields.io/pypi/v/ged4py.svg
        :target: https://pypi.python.org/pypi/ged4py

.. image:: https://img.shields.io/travis/andy-z/ged4py.svg
        :target: https://travis-ci.org/andy-z/ged4py

.. image:: https://readthedocs.org/projects/ged4py/badge/?version=latest
        :target: https://ged4py.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

Implementation of the GEDCOM parser in Python


* Free software: MIT license
* Documentation: https://ged4py.readthedocs.io.


Features
--------

* Parsing of GEDCOM files as defined by 5.5.1 version of GEDCOM standard
* Supported file encodings are UTF-8 (with or without BOM), ASCII or ANSEL
* Designed to parse large files efficiently
* Supports Python 2.7 and 3.3+

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage


=======
History
=======

0.1.4 (2018-01-31)
------------------

* Improve name parsing for ALTREE dialect

0.1.3 (2018-01-16)
------------------

* improve Py3 compatibility

0.1.2 (2017-11-26)
------------------

* Get rid of name formatting options, too complicated for this package.
* Describe name parsing for different dialects.

0.1.1 (2017-11-20)
------------------

* Fix for missing modules.

0.1.0 (2017-07-17)
------------------

* First release on PyPI.


