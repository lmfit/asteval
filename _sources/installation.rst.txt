====================================
Downloading and Installation
====================================

.. _numpy: http://docs.scipy.org/doc/numpy
.. _github:  http://github.com/newville/asteval
.. _PyPI:  http://pypi.python.org/pypi/asteval/

Requirements
~~~~~~~~~~~~~~~

Asteval is a pure python module with no required dependencies outside of the
standard library.  Asteval will make use of the `numpy`_ module if
available.  The test suite requires the `pytest` module.

The latest stable version of asteval is |release|.


Version 0.9.21 supports and is tested with Python 3.6 through 3.9. Support
for Python 3.5 has not been deliberately broken, but testing for this
version has now stopped, and development going forward will assume
Python3.6+.  There is no expectation of dropping support for Python 3.6
before its end of life.

Version 0.9.19 and 0.9.20 supported and was tested with Python 3.5 through
3.8, and had provisional but incomplete support for 3.9.

Version 0.9.18 supported and was tested with Python 3.5 through 3.8.  This
was the last version to support Python 3.5.

Version 0.9.17 was the last version to support Python 2.7.


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

   python setup.py install

License
~~~~~~~~~~~~~

The ASTEVAL code is distribution under the following license:

.. literalinclude:: ../LICENSE
