====================================
Downloading and Installation
====================================

.. _numpy: http://docs.scipy.org/doc/numpy
.. _github:  http://github.com/newville/asteval
.. _PyPI:  http://pypi.python.org/pypi/asteval/

Requirements
~~~~~~~~~~~~~~~

Asteval is a pure Python module.  For Python 3.8 and higher, there are no
required dependencies outside of the standard library.  If `numpy`_ is
available, Asteval will make use of it.  The test suite requires the `pytest`
and `coverage` modules, and building the documentation requires `sphinx`.

The latest stable version of asteval is |release|.

Versions 0.9.30 and later support and are automatically tested with Python 3.8
through 3.11.  Python versions have generally been supported by `asteval` until
they are well past the end of security fixes - there are no immediate plans to
drop support for Python 3.7, though we are no longer testing with it.  Support
for new versions of the Python 3 series is not guaranteed until some time after
the official release of that version, as we may not start testing until late in
the "beta" period of development.  Historically, the delay has not been too
long, though `asteval` may not support newly introduced language features.

At this writing (Asteval 0.9.30, June, 2023), minimal testing has been done
with Python 3.12-beta2, but all tests pass.

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
