#!/usr/bin/env python
""" Base Test Case """
import unittest
from unittest_utils import TestCase
import numpy as np

class TestEval(TestCase):
    '''testing of asteval'''

    def test_while(self):
        '''while loops'''
        self.interp("""
n=0
while n < 8:
    n += 1
""")
        self.isvalue('n',  8)

    def test_for(self):
        '''for loops'''
        self.interp('''
n=0
for i in arange(10):
    n += i
''')

        self.isvalue('n', 45)

    def test_print(self):
        '''print a string'''

        self.interp("print 1")

        self.stdout.close()

        with open(self.stdout.name) as inf:
            self.assert_(inf.read() == '1\n')

    def test_cmp(self):
        '''numeric comparisons'''

        self.istrue("3 == 3")
        self.istrue("3.0 == 3")
        self.istrue("3.0 == 3.0")
        self.istrue("3 != 4")
        self.istrue("3.0 != 4")
        self.istrue("3 >= 1")
        self.istrue("3 >= 3")
        self.istrue("3 <= 3")
        self.istrue("3 <= 5")
        self.istrue("3 < 5")
        self.istrue("5 > 3")

        self.isfalse("3 == 4")
        self.isfalse("3 > 5")
        self.isfalse("5 < 3")

    def test_bool(self):
        '''boolean logic'''

        self.interp('''
yes = True
no = False
nottrue = False
a = arange(7)''')

        self.istrue("yes")
        self.isfalse("no")
        self.isfalse("nottrue")
        self.isfalse("yes and no or nottrue")
        self.isfalse("yes and (no or nottrue)")
        self.isfalse("(yes and no) or nottrue")
        self.istrue("yes or no and nottrue")
        self.istrue("yes or (no and nottrue)")
        self.isfalse("(yes or no) and nottrue")
        self.istrue("yes or not no")
        self.istrue("(yes or no)")
        self.isfalse("not (yes or yes)")
        self.isfalse("not (yes or no)")
        self.isfalse("not (no or yes)")
        self.istrue("not no or yes")
        self.isfalse("not yes")
        self.istrue("not no")

    def test_bool_coerce(self):
        '''coercion to boolean'''

        self.istrue("1")
        self.isfalse("0")

        self.istrue("'1'")
        self.isfalse("''")

        self.istrue("[1]")
        self.isfalse("[]")

        self.istrue("(1)")
        self.istrue("(0,)")
        self.isfalse("()")

        self.istrue("dict(y=1)")
        self.isfalse("{}")

    def test_assign(self):
        '''variables assignment?'''
        self.interp('n = 5')
        self.isvalue("n",  5)

    def test_function_call(self):
        '''simple ndarrays'''
        self.interp('n = array([11, 10, 9])')

        self.istrue("isinstance(n, ndarray)")
        self.istrue("len(n) == 3")
        self.isvalue("n", np.array([11, 10, 9]))

    def test_convenience_imports(self):
        '''convenience imports

        imported functions like math.sqrt into the top level?'''

        self.interp('n = sqrt(4)')
        self.istrue('n == 2')

if __name__ == '__main__':  # pragma: no cover
    for suite in (TestEval,):
        suite = unittest.TestLoader().loadTestsFromTestCase(suite)
        unittest.TextTestRunner(verbosity=2).run(suite)
