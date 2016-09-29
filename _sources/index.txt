.. asteval documentation master file,

ASTEVAL: Minimal Python AST Evaluator
================================================

.. _numpy: http://docs.scipy.org/doc/numpy

ASTEVAL is a safe(ish) evaluator of Python expressions and statements,
using Python's ast module.  The idea is to provide a simple, robust
miniature mathematical language that is more complete than
:py:func:`ast.literal_eval` and can handle user-input more safely than
:py:func:`eval`.  The emphasis here is on mathematical calculations, so
mathematical functions from Python's :py:mod:`math` module are available,
and a large number of functions from `numpy`_ will be available if it is
installed on your system.

Many parts of the Python language are supported, including if-then-else
conditionals, while loops, for loops, try-except blocks, list
comprehension, slicing, subscripting, and writing user-defined functions.
All objects are true python objects, and many built-in data structures
(strings, dictionaries, tuple, lists, numpy arrays), are supported.  Still,
there are important absences and differences, and asteval is by no means an
attempt to reproduce Python with its own ast module.  Some of the
differences and absences include:

 1. Variable and function symbol names are held in a simple symbol
    table - a single dictionary - giving a flat namespace.
 2. creating classes is not allowed.
 3. importing modules is not allowed.
 4. function decorators, generators, yield, and lambda are not supported.
 5. several builtins (:py:func:`eval`, :py:func:`execfile`,
    :py:func:`getattr`, :py:func:`hasattr`, :py:func:`setattr`, and
    :py:func:`delattr`) are not allowed.
 6. Accessing several private object attributes that can provide access to
    the python interpreter are not allowed.

The result of this makes asteval a decidedly restricted and limited language
that is focused on mathematical calculations.

.. toctree::
   :maxdepth: 2

   installation
   motivation
   basics
   api
