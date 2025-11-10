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
using Python's ast module.  It emphasizes mathematical expressions so
that many functions from ``NumPy`` are imported and used if available,
but also provides a pretty complete subset of the Python language.
Asteval provides a simple and robust restricted Python interpreter
that can safely handle user input, and can be used as an embedded
macro language within a large application.

Asteval supports many Python language constructs by default, including
conditionals (if-elif-else blocks and if expressions), flow control
(for loops, while loops, with blocks, and try-except-finally blocks),
list comprehension, slicing, subscripting, and f-strings.  All data
are Python objects and the standard built-in data structures
(dictionaries, tuples, lists, sets, strings, functions, and ``Numpy``
nd-arrays) are well supported, but with limited to look "under the
hood" and get private and unsafe methods.

Many of the standard built-in Python functions are available, as are
the functions from the ``math`` module.  Some of the built-in
operators and functions, such as `getattr`, and `setattr` are not
allowed, and some including `open` and `**` are replaced with versions
intended to make them safer for user input.  If the ``NumPy`` is
installed, many of its functions will also be available.  Programmers
can add custom functions and data into each Asteval session.  Users
can define and run their own functions within the confines of the
limitations of the Asteval language.

Asteval converts user input into Python's own abstract syntax tree
(AST) representation and determines the result by walking through that
tree.  This approach guarantees the parsing of input will be identical
to that of Python, eliminating many lexing and parsing challenges and
generating a result that is straightforward to interpret.  This makes
"correctness" easy to test and verify with high confidence, so that
the emphasis can be placed on balancing features with safety.

There are several absences and differences with Python, and Asteval is
by no means an attempt to reproduce Python with its own ``ast``
module.  While, it does support a large subset of Python, the
following features found in Python are not supported in Asteval:

 1. many internal methods and classes of Python objects,
    especially ``__dunder__`` methods cannot be accessed.
 2. creating classes is not supported
 3. `eval`, `exec`, `yield`, `async`, `match/case`, function
    decorators, generators, and type annotations are not supported.
 4. `f-strings` are supported, but `t-strings` are not supported.
 5. importing modules is not supported by default, though it can be
    enabled.

Most of these omissions and limitations are intentional, and aimed to
strengthen Asteval against dangerous user code. Some of these
omissions may simply be viewed as not particularly compelling for an
embedded interpreter exposed to user input.

Even with these
restrictions,



Matt Newville <newville@cars.uchicago.edu>
Last Update:  09-Nov-2025
