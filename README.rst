ASTEVAL
=======

.. image:: https://travis-ci.org/newville/asteval.png
   :target: https://travis-ci.org/newville/asteval

.. image:: https://codecov.io/gh/newville/asteval/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/newville/asteval

.. image:: https://zenodo.org/badge/4185/newville/asteval.svg
   :target: https://zenodo.org/badge/latestdoi/4185/newville/asteval


Links
-----

* Documentation: http://newville.github.com/asteval
* PyPI installation: http://pypi.python.org/pypi/asteval
* Development Code: http://github.com/newville/asteval
* Issue Tracker: http://github.com/newville/asteval/issues

What is it?
-----------

ASTEVAL is a safe(ish) evaluator of Python expressions and statements,
using Python's ast module.  The idea is to provide a simple, safe, and
robust miniature mathematical language that can handle user-input.  The
emphasis here is on mathematical expressions, and so many functions from
``numpy`` are imported and used if available.

Many Python lanquage constructs are supported by default, These include
slicing, subscripting, list comprehension, conditionals (if-elif-else
blocks and if expressions), flow control (for loops, while loops, and
try-except-finally blocks). All data are python objects, and built-in data
structures (dictionaries, tuple, lists, numpy arrays, strings) are fully
supported by default.

Many of the standard builtin python functions are available, as are all
mathemetical functions from the math module.  If the numpy module is
installed, many of its functions will also be available.  Users can define
and run their own functions within the confines of the limitations of
asteval.

There are several absences and differences with Python, and asteval is by
no means an attempt to reproduce Python with its own ast module.  Some of
the most important differences and absences are:

 1. Variable and function symbol names are held in a simple symbol
    table (a single dictionary), giving a flat namespace.
 2. creating classes is not supported.
 3. importing modules is not supported.
 4. function decorators, yield, lambda, exec, and eval are not supported.
 5. files can only be opened in read-only mode.

In addition, accessing many internal methods and classes of objects is
forbidden in order to strengthen asteval against malicious user code.
