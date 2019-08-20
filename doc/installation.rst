====================================
Downloading and Installation
====================================

.. _numpy: http://docs.scipy.org/doc/numpy
.. _github:  http://github.com/newville/asteval
.. _PyPI:  http://pypi.python.org/pypi/asteval/

Requirements
~~~~~~~~~~~~~~~

Asteval is a pure python module with no required dependencies outside of the
standard library.   Asteval will make use of the `numpy`_ module if available.

As of version 0.9.15, the asteval package supports Python 3.5 and higher.
Versions 0.9.14 and earlier supported Python 2.7 and 3.4.


Download and Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The latest stable version of asteval is |release| and is available at `PyPI`_ or as
a conda package.  That is, you should be able to install asteval with::

   pip install asteval

or::

   conda install -c GSECARS asteval

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
