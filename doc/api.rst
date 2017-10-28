.. _asteval_api:

========================
asteval reference
========================

.. _numpy: http://docs.scipy.org/doc/numpy

.. module:: asteval


The asteval module is pretty simple, providing an :class:`Interpreter`
class which creates an Interpreter of expressions and code.  There are a
few options available to control what language features to support, how to
deal with writing to standard output and standard error, and specifying the
symbol table.  There are also a few convenience functions that are useful
for tesing the validity of symbol names and creating custom symbol tables.


:func:`valid_symbol_name`
:func:`make_symbol_table`


The :class:`Interpreter` class
=========================================

.. autoclass:: Interpreter

The symbol table will be loaded with several built in functions, several
functions from the :py:mod:`math` module and, if available and requested,
several functions from `numpy`_.  This will happen even for a symbol table
explicitly provided.

The ``writer`` argument can be used to provide a place to send all output
that would normally go to :py:data:`sys.stdout`.  The default is, of
course, to send output to :py:data:`sys.stdout`.

The ``use_numpy`` argument can be used to control whether functions from
`numpy`_ are loaded into the symbol table.

.. method:: eval(expression[, lineno=0[, show_errors=True]])

   evaluate the expression, returning the result.


   :param expression: code to evaluate.
   :type expression: string
   :param lineno: line number (for error messages).
   :type lineno: int
   :param show_errors: whether to print error messages or leave them
                       in the :attr:`errors` list.
   :type show_errors:  bool

.. method:: __call__(expression[, lineno=0[, show_errors=True]])

   same as :meth:`eval`.  That is one can do::

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
