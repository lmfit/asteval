====================================
Installing Asteval
====================================

.. _numpy: https://numpy.org/
.. _numpy_financial: https://numpy.org/numpy-financial/
.. _github:  https://github.com/lmfit/asteval
.. _PyPI:  https://pypi.org/project/asteval/

Requirements
~~~~~~~~~~~~~~~

Asteval is a pure Python module. The latest stable version is |release|, which
supports Python 3.8 through 3.12.

Installing `asteval` requires `setuptools` and `setuptools_scm`. No other
libraries outside of the standard library are required.  If `numpy`_ and
`numpy_financial`_ are available, `asteval` will make use of these libraries.
Running the test suite requires the `pytest`, `coverage`, and `pytest-cov`
modules, deployment uses `build` and `twine`, and building the documentation
requires `sphinx`.

Python 3.8 through 3.12 are tested on Windows, MacOS, and Linux, with and
without `numpy`_ installed.  Older Python versions have generally been
supported by `asteval` until they are well past the end of security fixes. That
is, while `asteval` is no longer tested with Python 3.7, the latest release may
continue to work with that version.

Support for new versions of the Python 3 series is not guaranteed until some
time after the official release of that version, as we may not start testing
until late in the "beta" period of development.  Historically, the delay has
not been too long, though `asteval` may not support newly introduced language
features.


Installing with `pip`
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The latest stable version of `asteval` is |release| and is available at
`PyPI`_ or as a conda package.  You should be able to install `asteval`
with::

   pip install asteval

It may also be available on some conda channels, including `conda-forge`,
but as it is a pure Python package with no dependencies or OS-specific
extensions, using `pip` should be the preferred method on all platforms and
environments.

Development Version
~~~~~~~~~~~~~~~~~~~~~~~~

The latest development version can be found at the `github`_ repository, and cloned with::

    git clone https://github.com/lmfit/asteval.git


Installation from the source tree on any platform is can then be done with::

   pip install .

License
~~~~~~~~~~~~~

The `asteval` code and documentation is distribution under the following
license:

.. literalinclude:: ../LICENSE
