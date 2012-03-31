#!/usr/bin/env python
""" Base Test Case """
import unittest
from unittest_utils import TestCase
import numpy as np

class TestEval(TestCase):
    '''testing of asteval'''

    def test_dict_index(self):
        '''dictionary indexing'''
        self.interp("a_dict = {'a': 1, 'b': 2, 'c': 3, 'd': 4}")
        self.istrue("a_dict['a'] == 1")
        self.istrue("a_dict['d'] == 4")

    def test_list_index(self):
        '''list indexing'''
        self.interp("a_list = ['a', 'b', 'c', 'd', 'o']")
        self.istrue("a_list[0] == 'a'")
        self.istrue("a_list[1] == 'b'")
        self.istrue("a_list[2] == 'c'")

    def test_tuple_index(self):
        '''tuple indexing'''
        self.interp("a_tuple = (5, 'a', 'x')")
        self.istrue("a_tuple[0] == 5")
        self.istrue("a_tuple[2] == 'x'")

    def test_string_index(self):
        '''string indexing'''
        self.interp("a_string = 'hello world'")
        self.istrue("a_string[0] == 'h'")
        self.istrue("a_string[6] == 'w'")
        self.istrue("a_string[-1] == 'd'")
        self.istrue("a_string[-2] == 'l'")

    def test_ndarray_index(self):
        '''nd array indexing'''
        self.interp("a_ndarray = 5*arange(20)")
        self.istrue("a_ndarray[2] == 10")
        self.istrue("a_ndarray[4] == 20")

    def test_ndarrayslice(self):
        '''array slicing'''
        self.interp("a_ndarray = arange(200).reshape(10, 20)")
        self.istrue("a_ndarray[1:3,5:7] == array([[25,26], [45,46]])")

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

    def test_ndarrays(self):
        '''simple ndarrays'''
        self.interp('n = array([11, 10, 9])')
        self.istrue("isinstance(n, ndarray)")
        self.istrue("len(n) == 3")
        self.isvalue("n", np.array([11, 10, 9]))

    def test_convenience_imports(self):
        '''builtin math functions'''
        self.interp('n = sqrt(4)')
        self.istrue('n == 2')
        self.istrue('abs(sin(pi/2) - 1) < 1.e-7')
        self.istrue('abs(cos(pi/2) - 0) < 1.e-7')
        self.istrue('exp(0) == 1')
        self.istrue('abs(exp(1) - e) < 1.e-7')

if __name__ == '__main__':  # pragma: no cover
    for suite in (TestEval,):
        suite = unittest.TestLoader().loadTestsFromTestCase(suite)
        unittest.TextTestRunner(verbosity=2).run(suite)
