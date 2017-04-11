ASTEVAL
=======

.. image:: https://travis-ci.org/newville/asteval.png
   :target: https://travis-ci.org/newville/asteval

What is it?
-----------

ASTEVAL is a safe(ish) evaluator of Python expressions and statements,
using Python's ast module.  The idea is to provide a simple, safe, and
robust miniature mathematical language that can handle user-input.

While much of Python's constructs are supported, there are important
absences and differences, and this is by no means an attempt to reproduce
Python with its own ast module.  Important differences and absences are:

 1. creating classes is not supported.
 2. importing modules is not supported.
 3. function decorators, yield, lambda, and exec are not supported.

Many built-in python syntactical components (if-then-else, while loops, for
loops, try-except blocks, list comprehension, slicing, subscripting), and
built-in data structures (dictionaries, tuple, lists, numpy arrays,
strings) are fully supported.  In addition, many built-in functions are
supported, including the standard builtin python functions, and all
mathemetical functions from the math module.  Users can
define their own functions, but given the restrictions of not being able to
define classes or import modules, the language is decidedly limited.
