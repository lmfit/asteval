.. _asteval_api:

========================
Asteval Reference
========================

.. _numpy: https://numpy.org

.. module:: asteval

The asteval module has a pretty simple interface, providing an
:class:`Interpreter` class which creates an Interpreter of expressions and
code.  There are a few options available to control what language features
to support, how to deal with writing to standard output and standard error,
and specifying the symbol table.  There are also a few convenience
functions: :func:`valid_symbol_name` is useful for testing the validity of
symbol names, and :func:`make_symbol_table` is useful for creating symbol
tables that may be pre-loaded with custom symbols and functions.


The :class:`Interpreter` class
=========================================

.. autoclass:: Interpreter


If not provided, a symbol table will be created with :func:`make_symbol_table`
that will include several standard python builtin functions, several functions
from the :py:mod:`math` module and (if available and not turned off) several
functions from `numpy`_.

The ``writer`` argument can be used to provide a place to send all output
that would normally go to :py:data:`sys.stdout`.  The default is, of
course, to send output to :py:data:`sys.stdout`.  Similarly, ``err_writer``
will be used for output that will otherwise be sent to
:py:data:`sys.stderr`.

The ``use_numpy`` argument can be used to control whether functions from
`numpy`_ are loaded into the symbol table.

Whether the user-code is able to overwrite the entries in the symbol table can
be controlled with the ``readonly_symbols`` and ``builtins_readonly`` keywords.

Configuring which features the Interpreter recognizes
========================================================

The interpreter can be configured to enable or disable many language
constructs, named according to the AST node in the Python language definition.

.. _node_table:

**Table of optional Python AST nodes used asteval.** The minimal configuration
excludes all of the nodes listed, to give a bare-bones mathematical language
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


The ``minimal`` configuration for the Interpreter will support many basic
Python language constructs including all basic data types, operators, slicing.
The ``default`` configuration adds many language constructs, including

  *  if-elif-else conditionals
  *  for loops, with ``else``
  *  while loops, with ``else``
  *  try-except-finally blocks
  *  with blocks
  *  augmented assignments:  ``x += 1``
  *  if-expressions:      ``x = a if TEST else b``
  *  list comprehension:  ``out = [sqrt(i) for i in values]``
  *  set and dict comprehension, too.
  *  print formatting with ``%``, ``str.format()``, or f-strings.
  *  function definitions

The nodes listed in Table :ref:`Table of optional Python AST nodes used asteval
<node_table>` can be enabled and disabled individually with the appropriate
``no_NODE`` or ``with_NODE`` argument when creating the interpreter, or
specifying a ``config`` dictionary.

That is, you might construct an Interpreter as::

    >>> from asteval import Interpreter
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
module import method`` can be enabled, but is disabled by default.  To enable
these, use ``with_import=True`` and ``with_importfrom=True``, as ::

    >>> from asteval import Interpreter
    >>> aeval_max = Interpreter(with_import=True, with_importfrom=True)

or by setting the config dictionary as described above:

Interpreter methods and attributes
====================================

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
   :param raise_errors: whether to re-raise exceptions or leave them
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

   the symbol table where all data and functions for the Interpreter are stored
   and looked up. By default, this is a simple dictionary with symbol names as
   keys, and values of data and functions. If the ``nested_symtable``
   option is used, the symbol tables will be a subclass of a dictionary with
   more features, as discussed in :ref:`symtable_section`.

   In either case, the symbol table can be accessed from the calling program
   using the  :attr:`symtable` attribute of the Interpreter.  This allows the
   calling program to read, insert, replace, or remove symbols to
   alter what symbols are known to your interpreter.


.. attribute:: error

   a list of error information, filled on exceptions. You can test this
   after each call of the interpreter. It will be empty if the last
   execution was successful.  If an error occurs, this will contain a liste
   of Exceptions raised.

.. attribute:: error_msg

   the most recent error message.

.. _symtable_section:

Symbol Tables used in asteval
====================================

The symbol table holds all of the data used by the Interpreter.  That is, when
you execute ``a = b * cos(pi/3)``, the Interpreter sees that it needs to lookup
values for ``b``, ``cos``, and ``pi`` (it already knows ``=``, ``*``, ``/``,
``(``, and ``)`` mean), and then set the value for ``a``.  The place where it
looks up and then sets those values for these assigned variables is the symbol
table.

Historically, and by default, the symbol table in Asteval is a simple
dictionary with variable names as the keys, and their values as the
corresponding values.  This is slightly simpler than in Python or roughly
equivalent to everything being "global".  This isn't exactly true, and what
happens inside an Asteval Procedure (basically, a function) is a little
different as a special local symbol table (or Frame) is created for that
function, but it is mostly true.

Symbol names are limited to being valid Python object names, and must match
``[a-zA-Z_][a-zA-Z0-9_]*`` and not be a reserved word.  The symbol table is held
in the :attr:`symtable` attribute of the Interpreter, and can be accessed and
manipulated from the containing Python program.  This allows the calling
program to read, insert, replace, or remove symbols to alter what symbols are
known to your interpreter.  That is, it is perfectly valid to do something like
this::

      >>> from asteval import Interpreter
      >>> aeval = Interpreter()
      >>> aeval.symtable['x'] = 10
      >>> aeval('sqrt(x)')
      3.1622776601683795


By default, the symbol table will be pre-loaded with many Python builtins,
functions from the ``math`` module, and functions from ``numpy`` if available.
You can control some of these settings or add symbols into the symbol table
with the ``use_numpy`` and ``user_symbols`` arguments when creating an Interpreter.
You can also build your own symbol table and pass that it, and use the
``readonly_symbols`` and ``builtins_readonly`` options to prevent some symbols to
be writeable from within the Interpreter.  You can also create your own symbol
table, either as a plain dict, or with the :func:`make_symbol_table` function,
and alter that to use as the ``symtable`` option when creating an Interpreter.
That is, the calling program can fully control the symbol table, either
pre-loading custom variables and functions or removing default functions.

.. versionadded:: 0.9.31


New Style Symbol Table
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Beginning with version 0.9.31, there is an option to use a more complex and
nested symbol table. This symbol table uses a ``"Group"`` object which is a
subclass of a Python dict that can also be used with ``object.attribute`` syntax::

      >>> from asteval import Interpreter
      >>> aeval = Interpreter(nested_symtable=True)
      >>> aeval('x = 3')
      >>> aeval.symtable['x']  # as with default dictionary
      3
      >>> aeval.symtable.x     # new
      3
      >>> aeval.symtable.y = 7  # new
      >>> aeval('print(x+y)')
      10

As with the plain-dictionary symbol table, all symbols must be valid Python
identifiers, and cannot be reserved words.

In addition, this symbol table can be nested -- not flat -- and may have a
special attribute called ``_searchgroups`` that give the name of sub-Groups to
search for symbols.  By default, when using this new-style symbol table, the
mathematical functions imported from the ``math`` and ``numpy`` modules) are
placed in a subgroup named ``math`` (with about 300 named functions and
variables), and the ``_searchgroups`` variable is set to the tuple
``('math',)``.  When looking for the a symbol in an expression like ``a = b *
cos( pi /3)``, the Interpreter will have to find and use the symbols names for
``b``, ``cos`` and ``pi``.  With the old-style symbol table, all of these must
be in the flat dictionary, which makes it difficult to browse through the
symbol table.  With the new, nested symbol table, the names ``b``, ``cos`` and
``pi`` are first looked for in the top-level Group. If not found there, they
are looked for in the subgroups named in ``_searchgroups``, in order and
returned as soon as one is found.  That is the expectation is that `b` would be
found in the "top-level user Group", while ``cos`` and ``pi`` would be found in
the ``math`` Group, and that::

      >>> aeval('a = b * cos( pi /3)')
      >>> aeval('a = b * math.cos(math.pi /3)')

would be equivalent, as if you had imported a module that would automatically
be searched: something between ``import math`` and ``from math import *``.  Though
different from how Python works, if using Asteval as a domain-specific
language, this nesting and automated searching can be quite useful.


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
