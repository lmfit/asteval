"""
   ASTEVAL provides a numpy-aware, safe(ish) "eval" function

   Emphasis is on mathematical expressions, and so numpy ufuncs
   are used if available.  Symbols are held in the Interpreter
   symbol table 'symtable':  a simple dictionary supporting a
   simple, flat namespace.

   Expressions can be compiled into ast node for later evaluation,
   using the values in the symbol table current at evaluation time.

   version: 0.9.10
   last update: 28-Oct-2017
   License:  MIT
   Author:  Matthew Newville <newville@cars.uchicago.edu>
            Center for Advanced Radiation Sources,
            The University of Chicago
"""

from .asteval import Interpreter
from .astutils import NameFinder, valid_symbol_name, make_symbol_table

__version__ = '0.9.10'
__all__ = ['Interpreter', 'NameFinder', 'valid_symbol_name', 'make_symbol_table']
