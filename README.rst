ASTEVAL
=======

.. image:: https://travis-ci.org/newville/asteval.png
   :target: https://travis-ci.org/newville/asteval

Links
-----

* Documentation: http://newville.github.com/asteval
* PyPI: http://pypi.python.org/pypi/asteval
* Code: http://github.com/newville/asteval
* Issues: http://github.com/newville/asteval/issues

What is it?
-----------

ASTEVAL is a safe(ish) evaluator of Python expressions and statements,
using Python's ast module.  The idea is to provide a simple, safe, and
robust miniature mathematical language that can handle user-input.  The
emphasis here is on mathematical expressions, and so numpy functions are
imported and used if available.

While much of Python's constructs are supported, there are important
absences and differences, and this is by no means an attempt to reproduce
Python with its own ast module.  Important differences and absences are:

 1. Variable and function symbol names are held in a simple symbol
    table (a single dictionary), giving a flat namespace.
 2. creating classes is not supported.
 3. importing modules is not supported.
 4. function decorators, yield, lambda, and exec are not supported.

Many built-in python syntactical components (if-then-else, while loops, for
loops, try-except blocks, list comprehension, slicing, subscripting), and
built-in data structures (dictionaries, tuple, lists, numpy arrays,
strings) are fully supported.  In addition, many built-in functions are
supported, including the standard builtin python functions, and all
mathemetical functions from the math module.  As mentioned above, if numpy
is available, many of its functions will also be available.  Users can
define their own functions, but given the restrictions of not being able to
define classes or import modules, the language is decidedly limited.
