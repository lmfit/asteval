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

Whether the user-code is able to overwrite the entries in the symbol table can
be controlled with the ``readonly_symbols`` and ``builtins_readonly`` keywords.

Configuring what features the Interpreter support
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The interpreter can be configured to enable or disable many language
constructs, named according to the AST node in the Python language definition.

.. _node_table:

**Table of optional Python AST nodes used asteval.** The minimal configuration
excludes all of the nodes listed, to give a bare-bones mathemetical language
but will full support for Python data types and array slicing.

  +----------------+----------------------+-------------------+-------------------+
  | node name      | description          | in default config | in minimal config |
  +================+======================+===================+===================+
  | import         | import statements    |  False            | False             |
  +----------------+----------------------+-------------------+-------------------+
  | importfrom     | from x import y      |  False            | False             |
  +----------------+----------------------+-------------------+-------------------+
  | assert         | assert statements    |  True             | False             |
  +----------------+----------------------+-------------------+-------------------+
  | augassign      | x += 1               |  True             | False             |
  +----------------+----------------------+-------------------+-------------------+
  | delete         | delete statements    |  True             | False             |
  +----------------+----------------------+-------------------+-------------------+
  | if             | if/then blocks       |  True             | False             |
  +----------------+----------------------+-------------------+-------------------+
  | ifexp          | a = b if c else d    |  True             | False             |
  +----------------+----------------------+-------------------+-------------------+
  | for            | for loops            |  True             | False             |
  +----------------+----------------------+-------------------+-------------------+
  | formattedvalue | f-strings            |  True             | False             |
  +----------------+----------------------+-------------------+-------------------+
  | functiondef    | define functions     |  True             | False             |
  +----------------+----------------------+-------------------+-------------------+
  | print          | print function       |  True             | False             |
  +----------------+----------------------+-------------------+-------------------+
  | raise          | raise statements     |  True             | False             |
  +----------------+----------------------+-------------------+-------------------+
  | listcomp       | list comprehension   |  True             | False             |
  +----------------+----------------------+-------------------+-------------------+
  | dictcomp       | dict comprehension   |  True             | False             |
  +----------------+----------------------+-------------------+-------------------+
  | setcomp        | set comprehension    |  True             | False             |
  +----------------+----------------------+-------------------+-------------------+
  | try            | try/except blocks    |  True             | False             |
  +----------------+----------------------+-------------------+-------------------+
  | while          | while blocks         |  True             | False             |
  +----------------+----------------------+-------------------+-------------------+
  | with           | with blocks          |  True             | False             |
  +----------------+----------------------+-------------------+-------------------+


To be clear, the ``minimal`` configuration for the Interpreter will support
many basic Python language constructs including all basic data types,
operators, slicing.  The ``default`` configuration adds many language
constructs, including

  *  if-elif-else conditionals
  *  for loops, with ``else``
  *  while loops, with ``else``
  *  try-except-finally blocks
  *  with blocks
  *  augmented assignments:  ``x += 1``
  *  if-expressions:      ``x = a if TEST else b``
  *  list comprehension:  ``out = [sqrt(i) for i in values]``
  *  set and dict comphrension, too.
  *  print formatting with `%`, `str.format()`, or f-strings.
  *  function definitions

The nodes listed in Table :ref:`Table of optional Python AST nodes used asteval
<node_table>`
can be enabled and disabled individually with the appropriate
``no_NODE`` or ``with_NODE`` argument when creating the interpreter, or
specifying a ``config`` dictionary.

That is, you might construct an Interpreter as::

    >>> from asteval import Interpreter
    >>>
    >>> aeval_all = Interpreter(with_import=True, with_importfrom=True)
    >>>
    >>> aeval_nowhile = Interpreter(no_while=True)
    >>>
    >>> config = {'while': False, 'if': False, 'try': False,
                 'for': False, 'with': False}
    >>> aveal_noblocks = Interpreter(config=config)


Passing, ``minimal=True`` will turn off all the nodes listed in Table
:ref:`Table of optional Python AST nodes used asteval <node_table>`::

    >>> from asteval import Interpreter
    >>>
    >>> aeval_min = Interpreter(minimal=True)
    >>> aeval_min.config
    {'import': False, 'importfrom': False, 'assert': False, 'augassign': False,
    'delete': False, 'if': False, 'ifexp': False, 'for': False,
    'formattedvalue': False, 'functiondef': False, 'print': False,
    'raise': False, 'listcomp': False, 'dictcomp': False, 'setcomp': False,
    'try': False, 'while': False, 'with': False}

As shown above, importing Python modules with ``import module`` or ``from
module import method`` can be supported, but is not supported by default, but
can be enabled with ``with_import=True`` and ``with_importfrom=True``, or by
setting the config dictionary as described above.


Interpreter methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
