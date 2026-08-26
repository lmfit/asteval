.. asteval documentation master file,

ASTEVAL: Minimal Python AST Evaluator
================================================

.. _numpy: https://numpy.org/
.. _numpy_financial: https://numpy.org/numpy-financial/

:bdg-link-info:`GitHub <https://github.com/lmfit/asteval>`
:bdg-link-info:`PyPI <https://pypi.org/project/asteval>`


Asteval evaluates Python expressions and statements in a way that is
safer than Python's builtin :py:func:`eval` and more capable than
:py:func:`ast.literal_eval`.  Asteval provides an embedded interpreter
that uses Python's :py:mod:`ast` module to evaluates a subset of the
Python language. The emphasis is the evaluation of mathematical
expressions, and functions from Python's :py:mod:`math` module are
built-in to asteval. If `numpy`_ is available, a large number of
functions from `numpy`_ will be included too. For backward
compatibility, a few functions that were moved from `numpy`_ to
`numpy_financial`_ will also be imported, if that package is
installed.

In addition to mathematical expressions, many features and constructs
of the Python including array slicing and subscripting, if-then-else
conditionals, while loops, for loops, try-except blocks, list
comprehension, and user-defined functions are supported by default.
All objects in the asteval interpreter are Python objects, and most of
the basic built-in data structures (strings, dictionaries, tuple,
lists, sets, numpy arrays) are supported, including the built-in
methods for these objects.

However, asteval is not an attempt to write Python in its own
:py:mod:`ast` module.  There are important differences and missing
features compared to Python.  Many of these absences are intentional,
to try to make a safer version of :py:func:`eval`, while some are
simply due to the reduced requirements for an embedded mini-language.
These differences and absences include:

 1. All variable and function symbol names are held in a single symbol table
    that can be accessed from the calling program.  By default, this is a
    simple dictionary, giving a flat namespace. A more elaborate, still
    experimental, symbol table that allows both dictionary and attribute
    access can also be used.
 2. creating classes is not allowed.
 3. importing modules is not allowed, unless specifically enabled.
 4. decorators, generators, and type hints are not supported.
 5. ``yield``, ``await``,  and async programming are not supported.
 6. Many builtin functions (:py:func:`eval`, :py:func:`getattr`,
    :py:func:`hasattr`, :py:func:`setattr`, and :py:func:`delattr`) are not allowed.
 7. Accessing many object attributes that can provide access to
    the python interpreter are not allowed.

The resulting "asteval language" is then like miniature version of
Python, focused on mathematical calculations, and with noticeable
limitations.  It is the kind of programming language you might use to
introduce simple scientific programming concepts, but also includes
much of the standard Python syntax and features.  This makes Asteval
suitable as an embedded "macro language" in a larger application that
may want to provide some limited, controlled scripting capabilities.

Because asteval is designed for evaluating user-supplied input, safety
against malicious or incompetent user input is an important concern.
Asteval tries as hard as possible to prevent user-supplied input from
crashing the Python interpreter or from returning exploitable parts of the
Python interpreter.  In this sense asteval is certainly safer than using
:py:func:`eval`.  However, asteval is an open source project written by
volunteers, and we cannot guarantee that it is completely safe against
malicious attacks.

.. toctree::
   :maxdepth: 2

   installation
   basics
   api
   motivation
   safety
