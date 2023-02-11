====================================
Downloading and Installation
====================================

.. _numpy: http://docs.scipy.org/doc/numpy
.. _github:  http://github.com/newville/asteval
.. _PyPI:  http://pypi.python.org/pypi/asteval/

Requirements
~~~~~~~~~~~~~~~

Asteval is a pure Python module with very few dependencies.  For Python 3.8 and
higher, there are no required dependencies outside of the standard
library. Python 3.7 does require the `importlib_metadata` package.  If
available, Asteval will make use of the `numpy`_ module.  The test suite
requires the `pytest` and `coverage` modules, and building the documentation
requires the `sphinx`.

The latest stable version of asteval is |release|.

Versions 0.9.28 and later support and are automatically tested with Python 3.7
through 3.11.  Python versions have generally been supported by `asteval` until
they are well past the end of security fixes - there are no immediate plans to
drop support for Python 3.7.  Support for new versions of the Python 3 series
is not gauranteed until some time after the official release of that version,
as we may not start testing until late in the "beta" period of development.
Historically, the delay has not been too long, though `asteval` may not support
newly introduced language features.

The last version of asteval to support Python 2.7 was version 0.9.17.  It
should not be used and cannot be supported, but the code may be of historical
interest.

Download and Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The latest stable version of asteval is |release| and is available at
`PyPI`_ or as a conda package.  You should be able to install asteval
with::

   pip install asteval

It may also be available on some conda channels, including `conda-forge`,
but as it is a pure Python package with no dependencies or OS-specific
extensions, using `pip` should be the preferred method on all platforms and
environments.

Development Version
~~~~~~~~~~~~~~~~~~~~~~~~

The latest development version can be found at the `github`_ repository, and cloned with::

    git clone http://github.com/newville/asteval.git


Installation
~~~~~~~~~~~~~~~~~

Installation from source on any platform is::

   pip install .

License
~~~~~~~~~~~~~

The ASTEVAL code is distribution under the following license:

.. literalinclude:: ../LICENSE
