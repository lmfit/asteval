"""
   ASTEVAL provides a safe(ish) "eval" function.

   Expressions can be compiled into ast node for later evaluation,
   using the values in the symbol table current at evaluation time.

   Uses python's ast module to parse a python expression.

   version: 0.9.9
   last update: 11-Apr-2017
   License:  BSD
   Author:  Matthew Newville <newville@cars.uchicago.edu>
            Center for Advanced Radiation Sources,
            The University of Chicago

            Don Welch <dwelch91@gmail.com>
            SDVI Corp.
"""

from .asteval import Interpreter

__version__ = '0.9.9'
__all__ = ['Interpreter']
