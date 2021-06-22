"""
   ASTEVAL provides a numpy-aware, safe(ish) "eval" function

   Emphasis is on mathematical expressions, and so numpy ufuncs
   are used if available.  Symbols are held in the Interpreter
   symbol table 'symtable':  a simple dictionary supporting a
   simple, flat namespace.

   Expressions can be compiled into ast node for later evaluation,
   using the values in the symbol table current at evaluation time.

   version: 0.9.13
   last update: 2018-Sept-29
   License:  MIT
   Author:  Matthew Newville <newville@cars.uchicago.edu>
            Center for Advanced Radiation Sources,
            The University of Chicago
"""

from .asteval import Interpreter
from .astutils import (NameFinder, get_ast_names, make_symbol_table,
                       valid_symbol_name)

__all__ = ['Interpreter', 'NameFinder', 'valid_symbol_name',
           'make_symbol_table', 'get_ast_names']

from ._version import __version__
