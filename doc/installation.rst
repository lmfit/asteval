====================================
Downloading and Installation
====================================

.. _numpy: http://docs.scipy.org/doc/numpy
.. _github:  http://github.com/newville/asteval
.. _PyPI:  http://pypi.python.org/pypi/asteval/

Requirements
~~~~~~~~~~~~~~~

The asteval package is supported for use with Python 2.7, 3.5, and 3.6.
The package may work for Python 2.6, and Python 3.4 or earlier, but no testing
is done for these out-dated versions.  Asteval will make use of the `numpy`_
module if available.


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
