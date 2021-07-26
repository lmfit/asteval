.. _asteval_api:

========================
asteval reference
========================

.. _numpy: http://docs.scipy.org/doc/numpy

.. module:: asteval

The asteval module has a pretty simple interface, providing an
:class:`Interpreter` class which creates an Interpreter of expressions and
code.  There are a few options available to control what language features
to support, how to deal with writing to standard output and standard error,
and specifying the symbol table.  There are also a few convenience
functions: :func:`valid_symbol_name` is useful for tesing the validity of
symbol names, and :func:`make_symbol_table` is useful for creating symbol
tables that may be pre-loaded with custom symbols and functions.


The :class:`Interpreter` class
=========================================

.. autoclass:: Interpreter


By default, the symbol table will be created with :func:`make_symbol_table`
that will include several standard python builtin functions, several
functions from the :py:mod:`math` module and (if available and not turned off)
several functions from `numpy`_.

The ``writer`` argument can be used to provide a place to send all output
that would normally go to :py:data:`sys.stdout`.  The default is, of
course, to send output to :py:data:`sys.stdout`.  Similarly, ``err_writer``
will be used for output that will otherwise be sent to
:py:data:`sys.stderr`.

The ``use_numpy`` argument can be used to control whether functions from
`numpy`_ are loaded into the symbol table.

By default, the interpreter will support many Python language constructs,
including

  *  advanced slicing:    ``a[::-1], array[-3:, :, ::2]``
  *  if-elif-else conditionals
  *  for loops, with ``else``
  *  while loops, with ``else``
  *  try-except-finally blocks
  *  function definitions
  *  augmented assignments:  ``x += 1``
  *  if-expressions:      ``x = a if TEST else b``
  *  list comprehension:  ``out = [sqrt(i) for i in values]``

with the exception of slicing, each of these features can be turned off
with the appropriate ``no_XXX`` option.  To turn off all these optional
constructs, and create a simple expression calculator, use
``minimal=True``.


Many Python syntax elements are not supported at all, including:

   Import, Exec, Lambda, Class, Global, Generators, Yield, Decorators

In addition, many actions that are known to be unsafe (such as inspecting
objects to get at their base classes) are also not allowed.


An Interpreter instance has many methods, but most of them are
implementation details for how to handle particular AST nodes, and should
not be considered as part of the usable API.  The methods described be low,
and the examples elsewhere in this documentation should be used as the
stable API.

.. method:: eval(expression[, lineno=0[, show_errors=True[, raise_errors=False]]])

   evaluate the expression, returning the result.


   :param expression: code to evaluate.
   :type expression: string
   :param lineno: line number (for error messages).
   :type lineno: int
   :param show_errors: whether to print error messages or leave them
                       in the :attr:`errors` list.
   :type show_errors:  bool
   :param raise_errors: whether to reraise exceptions or leave them
                       in the :attr:`errors` list.
   :type raise_errors:  bool

.. method:: __call__(expression[, lineno=0[, show_errors=True[, raise_errors=False]]])

   same as :meth:`eval`.  That is::

      >>> from asteval import Interpreter
      >>> a = Interpreter()
      >>> a('x = 1')

   instead of::

      >>> a.eval('x = 1')

.. attribute:: symtable

   the symbol table. A dictionary with symbol names as keys, and object
   values (data and functions).

   For full control of the symbol table, you can simply access the
   :attr:`symtable` object, inserting, replacing, or removing symbols to
   alter what symbols are known to your interpreter.  You can also access
   the :attr:`symtable` to retrieve results.

.. attribute:: error

   a list of error information, filled on exceptions. You can test this
   after each call of the interpreter. It will be empty if the last
   execution was successful.  If an error occurs, this will contain a liste
   of Exceptions raised.

.. attribute:: error_msg

   the most recent error message.



Utility Functions
====================

.. autofunction:: valid_symbol_name



.. autofunction:: make_symbol_table


To make and use a custom symbol table, one might do this::

    from asteval import Interpreter, make_symbol_table
    import numpy as np
    def cosd(x):
        "cos with angle in degrees"
        return np.cos(np.radians(x))

    def sind(x):
        "sin with angle in degrees"
        return np.sin(np.radians(x))

    def tand(x):
        "tan with angle in degrees"
        return np.tan(np.radians(x))

    syms = make_symbol_table(use_numpy=True, cosd=cosd, sind=sind, tand=tand)

    aeval = Interpreter(symtable=syms)
    print(aeval("sind(30)")))

which will print ``0.5``.
