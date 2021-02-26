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


Versions 0.9.21 and later support and are tested with Python 3.6 through
3.9.  Python 3.6 will be supported until at least its official end of life
(December 2021).  No released version supports Python 3.10 yet.

Versions 0.9.18, 0.9.19, and 0.9.20 supported and were tested with Python
3.5 through 3.8.

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
