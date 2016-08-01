#!/usr/bin/env python
"""
Base TestCase for asteval
"""
import ast
import inspect
import os
from sys import version_info
import sys
from tempfile import NamedTemporaryFile
import textwrap
import time
import unittest

from asteval import NameFinder, Interpreter, astutils
import ddt


try:
    from unittest import mock
except ImportError: # PY2
    import mock # @UnusedImport

PY3 = version_info[0] == 3
PY33Plus = PY3 and version_info[1] >= 3
PY35Plus = PY3 and version_info[1] >= 5

if PY3:
    # noinspection PyUnresolvedReferences
    from io import StringIO
else:
    # noinspection PyUnresolvedReferences
    from cStringIO import StringIO


HAS_NUMPY = False
try:
    # noinspection PyUnresolvedReferences
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    print("Warning: numpy not available... functionality will be limited.")
    pass


class TestCase(unittest.TestCase):
    """testing of asteval"""

    def setUp(self):
        self.interp = Interpreter()
        self.symtable = self.interp.symtable
        self.set_stdout()
        self.set_stderr()
        if not HAS_NUMPY:
            self.interp("arange = range")

    def set_stdout(self):
        self.stdout = NamedTemporaryFile('w', delete=False, prefix='astevaltest')
        self.interp.writer = self.stdout

    def read_stdout(self):
        self.stdout.close()
        time.sleep(0.1)
        fname = self.stdout.name
        with open(self.stdout.name) as inp:
            out = inp.read()
        self.set_stdout()
        os.unlink(fname)
        return out

    def set_stderr(self):
        self.stderr = NamedTemporaryFile('w', delete=False,
                                         prefix='astevaltest_stderr')
        self.interp.err_writer = self.stderr

    def read_stderr(self):
        self.stderr.close()
        time.sleep(0.1)
        fname = self.stderr.name
        with open(self.stderr.name) as inp:
            out = inp.read()
        self.set_stderr()
        os.unlink(fname)
        return out

    def tearDown(self):
        if not self.stdout.closed:
            self.stdout.close()
        if not self.stderr.closed:
            self.stderr.close()

        # noinspection PyBroadException
        try:
            os.unlink(self.stdout.name)
        except:
            pass
        try:
            os.unlink(self.stderr.name)
        except:
            pass

    # noinspection PyUnresolvedReferences
    def isvalue(self, sym, val):
        """assert that a symboltable symbol has a particular value"""
        if HAS_NUMPY and isinstance(val, np.ndarray):
            return self.assertTrue(np.all(self.interp.symtable[sym] == val))
        else:
            return self.assertTrue(self.interp.symtable[sym] == val)

    def isnear(self, expr, val, places=7):
        """assert that a symboltable symbol is near a particular value"""
        oval = self.interp(expr)
        if HAS_NUMPY and isinstance(val, np.ndarray):
            for x, y in zip(oval, val):
                self.assertAlmostEqual(x, y, places=places)
        else:
            return self.assertAlmostEqual(oval, val, places=places)

    # noinspection PyUnresolvedReferences
    def istrue(self, expr):
        """assert that an expression evaluates to True"""
        val = self.interp(expr)
        if HAS_NUMPY and isinstance(val, np.ndarray):
            val = np.all(val)
        return self.assertTrue(val)

    # noinspection PyUnresolvedReferences
    def isfalse(self, expr):
        """assert that an expression evaluates to False"""
        val = self.interp(expr)
        if HAS_NUMPY and isinstance(val, np.ndarray):
            val = np.all(val)
        return self.assertFalse(val)

    def check_output(self, chk_str, exact=False):
        self.interp.writer.flush()
        out = self.read_stdout().split('\n')
        if out:
            if exact:
                return chk_str == out[0]
            return chk_str in out[0]
        return False

    def check_error(self, chk_type='', chk_msg=''):
        try:
            errtype, errmsg = self.interp.error[0].get_error()
            self.assertEqual(errtype, chk_type)
            if chk_msg:
                self.assertTrue(chk_msg in errmsg)
        except IndexError:
            if chk_type:
                self.assertTrue(False)


class TestEval(TestCase):
    """testing of asteval"""

    def test_dict_index(self):
        """dictionary indexing"""
        self.interp("a_dict = {'a': 1, 'b': 2, 'c': 3, 'd': 4}")
        self.istrue("a_dict['a'] == 1")
        self.istrue("a_dict['d'] == 4")

    def test_list_index(self):
        """list indexing"""
        self.interp("a_list = ['a', 'b', 'c', 'd', 'o']")
        self.istrue("a_list[0] == 'a'")
        self.istrue("a_list[1] == 'b'")
        self.istrue("a_list[2] == 'c'")

    def test_tuple_index(self):
        """tuple indexing"""
        self.interp("a_tuple = (5, 'a', 'x')")
        self.istrue("a_tuple[0] == 5")
        self.istrue("a_tuple[2] == 'x'")

    def test_string_index(self):
        """string indexing"""
        self.interp("a_string = 'hello world'")
        self.istrue("a_string[0] == 'h'")
        self.istrue("a_string[6] == 'w'")
        self.istrue("a_string[-1] == 'd'")
        self.istrue("a_string[-2] == 'l'")

    def test_ndarray_index(self):
        """nd array indexing"""
        if HAS_NUMPY:
            self.interp("a_ndarray = 5*arange(20)")
            self.istrue("a_ndarray[2] == 10")
            self.istrue("a_ndarray[4] == 20")

    def test_ndarrayslice(self):
        """array slicing"""
        if HAS_NUMPY:
            self.interp("a_ndarray = arange(200).reshape(10, 20)")
            self.istrue("a_ndarray[1:3,5:7] == array([[25,26], [45,46]])")
            self.interp("y = arange(20).reshape(4, 5)")
            self.istrue("y[:,3]  == array([3, 8, 13, 18])")
            self.istrue("y[...,1]  == array([1, 6, 11, 16])")
            self.interp("y[...,1] = array([2, 2, 2, 2])")
            self.istrue("y[1,:] == array([5, 2, 7, 8, 9])")

    def test_while(self):
        """while loops"""
        self.interp(textwrap.dedent("""
            n=0
            while n < 8:
                n += 1
            """))
        self.isvalue('n', 8)

        self.interp(textwrap.dedent("""
            n=0
            while n < 8:
                n += 1
                if n > 3:
                    break
            else:
                n = -1
            """))
        self.isvalue('n', 4)

        self.interp(textwrap.dedent("""
            n=0
            while n < 8:
                n += 1
            else:
                n = -1
            """))
        self.isvalue('n', -1)

        self.interp(textwrap.dedent("""
            n, i = 0, 0
            while n < 10:
                n += 1
                if n % 2:
                    continue
                i += 1
            print( 'finish: n, i = ', n, i)
            """))
        self.isvalue('n', 10)
        self.isvalue('i', 5)

        self.interp(textwrap.dedent("""
            n=0
            while n < 10:
                n += 1
                print( ' n = ', n)
                if n > 5:
                    break
            print( 'finish: n = ', n)
            """))
        self.isvalue('n', 6)

    def test_while_continue(self):
        self.interp(textwrap.dedent("""
            n, i = 0, 0
            while n < 10:
                n += 1
                if n % 2:
                    continue
                i += 1
            print( 'finish: n, i = ', n, i)
            """))
        self.isvalue('n', 10)
        self.isvalue('i', 5)

    def test_while_break(self):
        self.interp(textwrap.dedent("""
            n = 0
            while n < 10:
                n += 1
                if n > 6:
                    break
            print( 'finish: n = ', n)
            """))
        self.isvalue('n', 7)

    # noinspection PyTypeChecker
    def test_assert(self):
        """test assert statements"""
        self.interp.error = []
        self.interp('n=6')
        self.interp('assert n==6')
        self.check_error(None)
        self.interp('assert n==7')
        self.check_error('AssertionError')

    def test_for(self):
        """for loops"""
        self.interp(textwrap.dedent("""
            n=0
            for i in arange(10):
                n += i
            """))
        self.isvalue('n', 45)

        self.interp(textwrap.dedent("""
            n=0
            for i in arange(10):
                n += i
            else:
                n = -1
            """))
        self.isvalue('n', -1)

    def test_for_break(self):
        self.interp(textwrap.dedent("""
            n=0
            for i in arange(10):
                n += i
                if n > 2:
                    break
            else:
                n = -1
            """))
        self.isvalue('n', 3)

    def test_if(self):
        """runtime errors test"""
        self.interp(textwrap.dedent("""
            zero = 0
            if zero == 0:
                x = 1
            if zero != 100:
                x = x+1
            if zero > 2:
                x = x + 1
            else:
                y = 33
            """))
        self.isvalue('x', 2)
        self.isvalue('y', 33)

    def test_print(self):
        """print (ints, str, ....)"""
        self.interp("print(31)")
        self.check_output('31\n', True)
        self.interp("print('%s = %.3f' % ('a', 1.2012345))")
        self.check_output('a = 1.201\n', True)
        self.interp("print('{0:s} = {1:.2f}'.format('a', 1.2012345))")
        self.check_output('a = 1.20\n', True)

    def test_repr(self):
        """repr of dict, list"""
        self.interp("x = {'a': 1, 'b': 2, 'c': 3}")
        self.interp("y = ['a', 'b', 'c']")
        self.interp("rep_x = repr(x['a'])")
        self.interp("rep_y = repr(y)")
        self.interp("rep_y , rep_x")
        self.interp("repr(None)")
        self.isvalue("rep_x", "1")
        self.isvalue("rep_y", "['a', 'b', 'c']")

    def test_cmp(self):
        """numeric comparisons"""
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
        """boolean logic"""
        self.interp(textwrap.dedent("""
            yes = True
            no = False
            nottrue = False
            a = arange(7)"""))

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
        """coercion to boolean"""
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

    # noinspection PyUnresolvedReferences
    def test_assignment(self):
        """variables assignment"""
        self.interp('n = 5')
        self.isvalue("n", 5)
        self.interp('s1 = "a string"')
        self.isvalue("s1", "a string")
        self.interp('b = (1,2,3)')
        self.isvalue("b", (1, 2, 3))
        if HAS_NUMPY:
            self.interp('a = 1.*arange(10)')
            self.isvalue("a", np.arange(10))
            self.interp('a[1:5] = 1 + 0.5 * arange(4)')
            self.isnear("a", np.array([0., 1., 1.5, 2., 2.5, 5., 6., 7., 8., 9.]))

    def test_names(self):
        """names test"""
        self.interp('nx = 1')
        self.interp('nx1 = 1')

    def test_syntaxerrors_1(self):
        """assignment syntax errors test"""
        for expr in ('class = 1', 'for = 1', 'if = 1', 'raise = 1',
                     '1x = 1', '1.x = 1', '1_x = 1'):
            failed = False
            # noinspection PyBroadException
            try:
                self.interp(expr, show_errors=False)
            except:
                failed = True

            self.assertTrue(failed)
            self.check_error('SyntaxError')

    def test_unsupportednodes(self):
        """unsupported nodes"""
        for expr in ('f = lambda x: x*x', 'yield 10'):
            failed = False
            # noinspection PyBroadException
            try:
                self.interp(expr, show_errors=False)
            except:
                failed = True
            self.assertTrue(failed)
            self.check_error('NotImplementedError')

    def test_syntaxerrors_2(self):
        """syntax errors test"""
        for expr in ('x = (1/*)', 'x = 1.A', 'x = A.2'):
            failed = False
            # noinspection PyBroadException
            try:
                self.interp(expr, show_errors=False)
            except:  # RuntimeError:
                failed = True
            self.assertTrue(failed)
            self.check_error('SyntaxError')

    def test_runtimeerrors_1(self):
        """runtime errors test"""
        self.interp("zero = 0")
        self.interp("astr ='a string'")
        self.interp("atup = ('a', 'b', 11021)")
        self.interp("arr  = arange(20)")
        for expr, errname in (('x = 1/zero', 'ZeroDivisionError'),
                              ('x = zero + nonexistent', 'NameError'),
                              ('x = zero + astr', 'TypeError'),
                              ('x = zero()', 'TypeError'),
                              ('x = astr * atup', 'TypeError'),
                              ('x = arr.shapx', 'AttributeError'),
                              ('arr.shapx = 4', 'AttributeError'),
                              ('del arr.shapx', 'KeyError')):
            failed, errtype, errmsg = False, None, None
            # noinspection PyBroadException
            try:
                self.interp(expr, show_errors=False)
            except:
                failed = True
            self.assertTrue(failed)
            self.check_error(errname)

    # noinspection PyUnresolvedReferences
    def test_ndarrays(self):
        """simple ndarrays"""
        if HAS_NUMPY:
            self.interp('n = array([11, 10, 9])')
            self.istrue("isinstance(n, ndarray)")
            self.istrue("len(n) == 3")
            self.isvalue("n", np.array([11, 10, 9]))
            self.interp('n = arange(20).reshape(5, 4)')
            self.istrue("isinstance(n, ndarray)")
            self.istrue("n.shape == (5, 4)")
            self.interp("myx = n.shape")
            self.interp("n.shape = (4, 5)")
            self.istrue("n.shape == (4, 5)")
            self.interp("a = arange(20)")
            self.interp("gg = a[1:13:3]")
            self.isvalue('gg', np.array([1, 4, 7, 10]))
            self.interp("gg[:2] = array([0,2])")
            self.isvalue('gg', np.array([0, 2, 7, 10]))
            self.interp('a, b, c, d = gg')
            self.isvalue('c', 7)
            self.istrue('(a, b, d) == (0, 2, 10)')

    def test_binop(self):
        """test binary ops"""
        self.interp('a = 10.0')
        self.interp('b = 6.0')
        self.istrue("a+b == 16.0")
        self.isnear("a-b", 4.0)
        self.istrue("a/(b-1) == 2.0")
        self.istrue("a*b     == 60.0")

    def test_unaryop(self):
        """test binary ops"""
        self.interp('a = -10.0')
        self.interp('b = -6.0')
        self.isnear("a", -10.0)
        self.isnear("b", -6.0)

    def test_del(self):
        """test del function"""
        self.interp('a = -10.0')
        self.interp('b = -6.0')
        self.assertTrue('a' in self.symtable)
        self.assertTrue('b' in self.symtable)
        self.interp("del a")
        self.interp("del b")
        self.assertFalse('a' in self.symtable)
        self.assertFalse('b' in self.symtable)

    # noinspection PyUnresolvedReferences
    def test_math1(self):
        """builtin math functions"""
        self.interp('n = sqrt(4)')
        self.istrue('n == 2')
        self.isnear('sin(pi/2)', 1)
        self.isnear('cos(pi/2)', 0)
        self.istrue('exp(0) == 1')
        if HAS_NUMPY:
            self.isnear('exp(1)', np.e)

    def test_namefinder(self):
        """test namefinder"""
        p = self.interp.parse('x+y+cos(z)')
        nf = NameFinder()
        nf.generic_visit(p)
        self.assertTrue('x' in nf.names)
        self.assertTrue('y' in nf.names)
        self.assertTrue('z' in nf.names)
        self.assertTrue('cos' in nf.names)

    def test_list_comprehension(self):
        """test list comprehension"""
        self.interp('x = [i*i for i in range(4)]')
        self.isvalue('x', [0, 1, 4, 9])
        self.interp('x = [i*i for i in range(6) if i > 1]')
        self.isvalue('x', [4, 9, 16, 25])

    def test_ifexp(self):
        """test if expressions"""
        self.interp('x = 2')
        self.interp('y = 4 if x > 0 else -1')
        self.interp('z = 4 if x > 3 else -1')
        self.isvalue('y', 4)
        self.isvalue('z', -1)

    # noinspection PyUnresolvedReferences
    def test_index_assignment(self):
        """test indexing / subscripting on assignment"""
        self.interp('x = arange(10)')
        self.interp('l = [1,2,3,4,5]')
        self.interp('l[0] = 0')
        self.interp('l[3] = -1')
        self.isvalue('l', [0, 2, 3, -1, 5])
        self.interp('l[0:2] = [-1, -2]')
        self.isvalue('l', [-1, -2, 3, -1, 5])
        self.interp('x[1] = 99')
        if HAS_NUMPY:
            self.isvalue('x', np.array([0, 99, 2, 3, 4, 5, 6, 7, 8, 9]))
            self.interp('x[0:2] = [9,-9]')
            self.isvalue('x', np.array([9, -9, 2, 3, 4, 5, 6, 7, 8, 9]))

    def test_reservedwords(self):
        """test reserved words"""
        for w in ('and', 'as', 'while', 'raise', 'else',
                  'class', 'del', 'def', 'import', 'None'):
            self.interp.error = []
            # noinspection PyBroadException
            try:
                self.interp("%s= 2" % w, show_errors=False)
            except:
                pass

            self.check_error('SyntaxError')

        for w in ('True', 'False'):
            self.interp.error = []
            self.interp("%s= 2" % w)
            self.check_error('SyntaxError' if PY3 else 'NameError')

        for w in ('eval', '__import__'):
            self.interp.error = []
            self.interp("%s= 2" % w)
            self.check_error('NameError')

    def test_raise(self):
        """test raise"""
        self.interp("raise NameError('bob')")
        self.check_error('NameError', 'bob')

    def test_tryexcept(self):
        """test try/except"""
        self.interp(textwrap.dedent("""
            x = 5
            try:
                x = x/0
            except ZeroDivisionError:
                print( 'Error Seen!')
                x = -999
            """))
        self.isvalue('x', -999)

        self.interp(textwrap.dedent("""
            x = -1
            try:
                x = x/0
            except ZeroDivisionError:
                pass
            """))
        self.isvalue('x', -1)

    def test_tryelsefinally(self):

        self.interp(textwrap.dedent("""
            def dotry(x, y):
                out, ok, clean = 0, False, False
                try:
                    out = x/y
                except ZeroDivisionError:
                    out = -1
                else:
                    ok = True
                finally:
                    clean = True
                return out, ok, clean
            """))
        self.interp("val, ok, clean = dotry(1, 2.0)")
        self.interp("print(ok, clean)")
        self.isnear("val", 0.5)
        self.isvalue("ok", True)
        self.isvalue("clean", True)

        self.interp("val, ok, clean = dotry(1, 0.0)")
        self.isvalue("val", -1)
        self.isvalue("ok", False)
        self.isvalue("clean", True)

    def test_function1(self):
        """test function definition and running"""
        self.interp(textwrap.dedent("""
            def fcn(x, scale=2):
                'test function'
                out = sqrt(x)
                if scale > 1:
                    out = out * scale
                return out
            """))
        self.interp("a = fcn(4, scale=9)")
        self.isvalue("a", 18)
        self.interp("a = fcn(9, scale=0)")
        self.isvalue("a", 3)
        self.interp("print(fcn)")
        self.check_output('<Procedure fcn(x, scale=')
        self.interp("a = fcn()")
        self.check_error('TypeError', 'not enough arg')
        self.interp("a = fcn(x, bogus=3)")
        self.check_error('NameError')

    def test_function_vararg(self):
        """test function with var args"""
        self.interp(textwrap.dedent("""
            def fcn(*args):
                'test varargs function'
                out = 0
                for i in args:
                    out = out + i*i
                return out
            """))
        self.interp("o = fcn(1,2,3)")
        self.isvalue('o', 14)
        self.interp("print(fcn)")
        self.check_output('<Procedure fcn(')

    def test_function_kwargs(self):
        """test function with kw args, no **kws"""
        self.interp(textwrap.dedent("""
            def fcn(square=False, x=0, y=0, z=0, t=0):
                'test varargs function'
                out = 0
                for i in (x, y, z, t):
                    if square:
                        out = out + i*i
                    else:
                        out = out + i
                return out
            """))
        self.interp("print(fcn)")
        self.check_output('<Procedure fcn(square')
        self.interp("o = fcn(x=1, y=2, z=3, square=False)")
        self.isvalue('o', 6)
        self.interp("o = fcn(x=1, y=2, z=3, square=True)")
        self.isvalue('o', 14)
        self.interp("o = fcn(x=1, y=2, z=3, t=-2)")
        self.isvalue('o', 4)
        self.interp("o = fcn(x=1, y=2, z=3, t=-12, s=1)")
        self.check_error('TypeError', 'extra keyword arg')

    def test_function_kwargs1(self):
        """test function with **kws arg"""
        self.interp(textwrap.dedent("""
            def fcn(square=False, **kws):
                'test varargs function'
                out = 0
                for i in kws.values():
                    if square:
                        out = out + i*i
                    else:
                        out = out + i
                return out
            """))
        self.interp("print(fcn)")
        self.check_output('<Procedure fcn(square')
        self.interp("o = fcn(x=1, y=2, z=3, square=False)")
        self.isvalue('o', 6)
        self.interp("o = fcn(x=1, y=2, z=3, square=True)")
        self.isvalue('o', 14)

    def test_function_kwargs2(self):
        """test function with positional and **kws args"""
        self.interp(textwrap.dedent("""
            def fcn(x, y):
                'test function'
                return x + y**2
            """))
        self.interp("print(fcn)")
        self.check_output('<Procedure fcn(x,')
        self.interp("o = -1")
        self.interp("o = fcn(2, 1)")
        self.isvalue('o', 3)
        self.interp("o = fcn(x=1, y=2)")
        self.isvalue('o', 5)
        self.interp("o = fcn(y=2, x=7)")
        self.isvalue('o', 11)
        self.interp("o = fcn(1, y=2)")
        self.isvalue('o', 5)
        self.interp("o = fcn(1, x=2)")
        self.check_error('TypeError')

    def test_astdump(self):
        """test ast parsing and dumping"""
        astnode = self.interp.parse('x = 1')
        self.assertTrue(isinstance(astnode, ast.Module))
        self.assertTrue(isinstance(astnode.body[0], ast.Assign))
        self.assertTrue(isinstance(astnode.body[0].targets[0], ast.Name))
        self.assertTrue(isinstance(astnode.body[0].value, ast.Num))
        self.assertTrue(astnode.body[0].targets[0].id == 'x')
        self.assertTrue(astnode.body[0].value.n == 1)
        dumped = self.interp.dump(astnode.body[0])
        self.assertTrue(dumped.startswith('Assign'))

    # noinspection PyTypeChecker
    def test_safe_funcs(self):
        self.interp("'*'*(2<<17)")
        self.check_error(None)
        self.interp("'*'*(1+2<<17)")
        self.check_error('RuntimeError')
        self.interp("'*'*(2<<17) + '*'")
        self.check_error('RuntimeError')
        self.interp("10**10000")
        self.check_error(None)
        self.interp("10**10001")
        self.check_error('RuntimeError')
        self.interp("1<<1000")
        self.check_error(None)
        self.interp("1<<1001")
        self.check_error('RuntimeError')

    def test_safe_open(self):
        self.interp('open("foo", "wb")')
        self.check_error('RuntimeError')
        self.interp('open("foo", "rb")')
        self.check_error('FileNotFoundError' if PY33Plus else 'IOError')
        self.interp('open("foo", "rb", 2<<18)')
        self.check_error('RuntimeError')

    def test_dos(self):
        self.interp("""for x in range(2<<21): pass""")
        self.check_error('RuntimeError', 'time limit')
        self.interp("""while True: pass""")
        self.check_error('RuntimeError', 'time limit')
        self.interp("""def foo(): return foo()\nfoo()""")
        self.check_error('RecursionError' if PY35Plus else 'RuntimeError')

    def test_kaboom(self):
        """ test Ned Batchelder's 'Eval really is dangerous' - Kaboom test (and related tests)"""
        self.interp("""(lambda fc=(lambda n: [c for c in ().__class__.__bases__[0].__subclasses__() if c.__name__ == n][0]):
    fc("function")(fc("code")(0,0,0,0,"KABOOM",(),(),(),"","",0,""),{})()
)()""")
        self.check_error('NotImplementedError', 'Lambda')  # Safe, lambda is not supported

        self.interp(
            """[print(c) for c in ().__class__.__bases__[0].__subclasses__()]""")  # Try a portion of the kaboom...
        if PY3:
            self.check_error('AttributeError', '__class__')  # Safe, unsafe dunders are not supported
        else:
            self.check_error('SyntaxError')
        self.interp("9**9**9**9**9**9**9**9")
        self.check_error('RuntimeError')  # Safe, safe_pow() catches this
        self.interp(
            "((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((1))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))")
        self.check_error('MemoryError')  # Hmmm, this is caught, but its still concerning...
        self.interp("compile('xxx')")
        self.check_error('NameError')  # Safe, compile() is not supported

    def test_exit_value(self):
        """test expression eval - last exp. is returned by interpreter"""
        z = self.interp("True")
        self.assertTrue(z)
        z = self.interp("x = 1\ny = 2\ny == x + x\n")
        self.assertTrue(z)
        z = self.interp("x = 42\nx")
        self.assertEqual(z, 42)
        self.isvalue('x', 42)
        z = self.interp("""def foo(): return 42\nfoo()""")
        self.assertEqual(z, 42)


class TestCase2(unittest.TestCase):
    def test_stringio(self):
        """ test using stringio for output/errors """
        out = StringIO()
        err = StringIO()
        interp = Interpreter(writer=out, err_writer=err)
        interp("print('out')")
        self.assertEqual(out.getvalue(), 'out\n')

@ddt.ddt
class TRecurse(unittest.TestCase):
    def setUp(self):
        self._original_recusion_limit = sys.getrecursionlimit()

    def test_recursion_limit__unlimited_by_default(self):
        interp = Interpreter()
        m = mock.MagicMock()
        with mock.patch('sys.setrecursionlimit', m):
            interp("pass")
            m.assert_not_called()
        self.assertEqual(sys.getrecursionlimit(), self._original_recusion_limit)

    @ddt.data(-1, -100)
    def test_recursion_limit__unlimited_when_negative(self, rlimit):
        interp = Interpreter(recursion_limit=rlimit)
        m = mock.MagicMock()
        with mock.patch('sys.setrecursionlimit', m):
            interp("pass")
            m.assert_not_called()
        self.assertEqual(sys.getrecursionlimit(), self._original_recusion_limit)

    @ddt.data(None, False, True, '', 'foo', object(), 3.14, '3', '-1', -1.0)
    def test_recursion_limit__fail_when_non_integer(self, rlimit):
        with self.assertRaises(ValueError):
            interp = Interpreter(recursion_limit=rlimit)

    @ddt.data(1, 10)
    def test_recursion_limit__positive(self, rlimit):
        interp = Interpreter(recursion_limit=rlimit)
        m = mock.MagicMock()
        with mock.patch('sys.setrecursionlimit', m):
            interp("pass")
            rlimit = len(inspect.stack()) + rlimit
            self.assertEqual(m.mock_calls, [
                    mock.call(rlimit + 4),
                    mock.call(self._original_recusion_limit),
                    ])
        self.assertEqual(sys.getrecursionlimit(), self._original_recusion_limit)


if __name__ == '__main__':  # pragma: no cover
    for suite in (TestEval,):
        suite = unittest.TestLoader().loadTestsFromTestCase(suite)
        unittest.TextTestRunner(verbosity=2).run(suite)
