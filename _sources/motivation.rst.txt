.. _lmfit: https://github.com/lmfit/lmfit-py
.. _xraylarch: https://github.com/xraypy/xraylarch

====================================
Motivation
====================================

The asteval module allows you to evaluate a large subset of the Python language
from within a python program, without using :py:func:`eval`.  It is, in effect,
a restricted version of Python's built-in :py:func:`eval`, forbidding several
actions, and using (by default) a simple dictionary as a flat namespace.  A
completely fair question is: Why is this desirable?  That is, why not simply
use :py:func:`eval`, or just use Python itself?

The short answer is that sometimes you want to allow evaluation of user input,
or expose a simple or even scientific calculator inside a larger application.
For this, :py:func:`eval` is pretty scary, as it exposes *all* of Python, which
makes user input difficult to trust.  Since asteval does not support the
**import** statement (unless explicitly enabled) or many other constructs, user
code cannot access the :py:mod:`os` and :py:mod:`sys` modules or any functions
or classes outside those provided in the symbol table.

Many of the other missing features (modules, classes, yield,
generators) are similarly motivated by a desire for a safer version of
:py:func:`eval`.  The idea for asteval is to make a simple procedural,
mathematically-oriented language that can be embedded into larger applications.

In fact, the asteval module grew out of the need for a simple expression
evaluator for scientific applications such as the `lmfit`_ and `xraylarch`_
modules.  An early attempt using the `pyparsing` module worked but was
error-prone and difficult to maintain.  While the simplest of calculators or
expression-evaluators is not hard with pyparsing, it turned out that using the
Python :py:mod:`ast` module makes it much easier to implement a feature-rich
scientific calculator, including slicing, complex numbers, keyword arguments to
functions, etc. In fact, this approach meant that adding more complex
programming constructs like conditionals, loops, exception handling, and even
user-defined functions was fairly simple.  An important benefit of using the
:py:mod:`ast` module is that whole categories of implementation errors
involving parsing, lexing, and defining a grammar disappear.  Any valid python
expression will be parsed correctly and converted into an Abstract Syntax Tree.
Furthermore, the resulting AST is easy to walk through, greatly simplifying the
evaluation process.  What started as a desire for a simple expression evaluator
grew into a quite usable procedural domain-specific language for mathematical
applications.

Asteval makes no claims about speed. Evaluating the AST involves many
function calls, which is going to be slower than Python - often 4x slower
than Python.  That said, for certain use cases (see
https://stackoverflow.com/questions/34106484), use of asteval and numpy can
approach the speed of `eval` and the `numexpr` modules.
