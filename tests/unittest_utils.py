#!/usr/bin/env python
"""
Base TestCase for asteval
"""
import unittest
import numpy as np
import os
import tempfile

from asteval import Interpreter

class TestCase(unittest.TestCase):
    '''testing of asteval'''
    def setUp(self):
        self.stdout = tempfile.NamedTemporaryFile(delete=False,
                                                  prefix='asteval')
        self.interp = Interpreter(writer=self.stdout)
        self.symtable = self.interp.symtable

    def tearDown(self):
        if not self.stdout.closed:
            self.stdout.close()
        os.unlink(self.stdout.name)

    def isvalue(self, sym, val):
        '''assert that a symboltable symbol has a particular value'''
        if isinstance(val, np.ndarray):
            return self.assertTrue(np.all(self.interp.symtable[sym]==val))
        else:
            return self.assertTrue(self.interp.symtable[sym]==val)

    def istrue(self, expr):
        '''assert that an expression evaluates to True'''
        val = self.interp(expr)
        if isinstance(val, np.ndarray):
            val = np.all(val)
        return self.assertTrue(val)

    def isfalse(self, expr):
        '''assert that an expression evaluates to False'''
        val = self.interp(expr)
        if isinstance(val, np.ndarray):
            val = np.all(val)
        return self.assertFalse(val)
