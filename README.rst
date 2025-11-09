ASTEVAL
=======

.. image:: https://github.com/lmfit/asteval/actions/workflows/ubuntu_numpy.yml/badge.svg
   :target: https://github.com/lmfit/asteval/actions/workflows/ubuntu_numpy.yml

.. image:: https://github.com/lmfit/asteval/actions/workflows/ubuntu_nonumpy.yml/badge.svg
   :target: https://github.com/lmfit/asteval/actions/workflows/ubuntu_nonumpy.yml

.. image:: https://github.com/lmfit/asteval/actions/workflows/macos_numpy.yml/badge.svg
   :target: https://github.com/lmfit/asteval/actions/workflows/macos_numpy.yml

.. image:: https://github.com/lmfit/asteval/actions/workflows/windows_numpy.yml/badge.svg
   :target: https://github.com/lmfit/asteval/actions/workflows/windows_numpy.yml

.. image:: https://codecov.io/gh/lmfit/asteval/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/lmfit/asteval

.. image:: https://img.shields.io/pypi/v/asteval.svg
   :target: https://pypi.org/project/asteval

.. image:: https://img.shields.io/pypi/dm/asteval.svg
   :target: https://pypi.org/project/asteval

.. image:: https://img.shields.io/badge/docs-read-brightgreen
   :target: https://lmfit.github.io/asteval/

.. image:: https://zenodo.org/badge/4185/newville/asteval.svg
   :target: https://zenodo.org/badge/latestdoi/4185/newville/asteval


Links
-----

* Documentation: https://lmfit.github.io/asteval/
* PyPI installation: https://pypi.org/project/asteval/
* Development Code: https://github.com/lmfit/asteval
* Issue Tracker: https://github.com/lmfit/asteval/issues

Installation
------------

Use ``pip install asteval`` to install the asteval library.

Asteval supports Python 3.10 or higher. No modules outside of the
standard library are required, though if `NumPy` is installed, many
functions from it will be used by default.

About Asteval
--------------

Asteval is a safe(ish) evaluator of Python expressions and statements,
using Python's ast module. It provides a simple and robust restricted
Python interpreter that can safely handle user input.  The emphasis
here is on mathematical expressions so that many functions from
``NumPy`` are imported and used if available.

Asteval supports many Python language constructs by default. These
include conditionals (if-elif-else blocks and if expressions), flow
control (for loops, while loops, and try-except-finally blocks), list
comprehension, slicing, subscripting, f-strings, and more.  All data
are Python objects and built-in data structures (dictionaries, tuples,
lists, strings, and ``Numpy`` nd-arrays) are fully supported by
default.  It supports these language features by converting input into
Python's own abstract syntax tree (AST) representation and walking
through that tree.  This approach effectively guarantees that parsing
of input will be identical to that of Python.

Many of the standard built-in Python functions are available, as are
all mathematical functions from the ``math`` module.  If the ``NumPy``
is installed, many of its functions will also be available.  Users can
define and run their own functions within the confines of the
limitations of Asteval.

There are several absences and differences with Python, and Asteval is
by no means an attempt to reproduce Python with its own ``ast``
module.  Some of the most important differences and absences are:

 1. accessing many internal methods and classes of Python objects is
    forbidden. This strengthens Asteval against malicious user code.
 2. creating classes is not supported.
 3. function decorators, `yield`, `async`, `lambda`, `exec`, and
    `eval` are not supported.
 4. importing modules is not supported by default (it can be enabled).
 5. files will be opened in read-only mode by default.

Even with these restrictions, Asteval provides a pretty full-features
``mini-Python`` language that might be useful to expose to user input.


Matt Newville <newville@cars.uchicago.edu>
Last Update:  09-Nov-2025
