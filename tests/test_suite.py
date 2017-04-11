#!/usr/bin/env python
"""
Base TestCase for asteval
"""
import ast
import contextlib
import os
import re
import time
import unittest
from sys import version_info
from tempfile import NamedTemporaryFile
from textwrap import dedent

import sys

from math import sqrt

PY3 = version_info[0] == 3
PY33Plus = PY3 and version_info[1] >= 3

if PY3:
    # noinspection PyUnresolvedReferences
    from io import StringIO
else:
    # noinspection PyUnresolvedReferences
    from cStringIO import StringIO

from asteval.asteval import Interpreter #, NameFinder


@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


class TestCase(unittest.TestCase):
    """testing of asteval"""

    def setUp(self):
        self.interp = Interpreter(max_time=3)
        self.interp.set_symbol('print', self.interp.print_)
        self.set_stdout()

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

    def tearDown(self):
        if not self.stdout.closed:
            self.stdout.close()

        # noinspection PyBroadException
        try:
            os.unlink(self.stdout.name)
        except:
            pass

    # noinspection PyUnresolvedReferences
    def isvalue(self, sym, val):
        """assert that a symboltable symbol has a particular value"""
        #return self.assertEquals(self.interp.symtable[sym], val)
        return self.assertEquals(self.interp.get_global_frame().get_symbol_value(sym), val)

    def isnear(self, expr, val, places=7):
        """assert that a symboltable symbol is near a particular value"""
        oval = self.interp(expr)
        return self.assertAlmostEqual(oval, val, places=places)

    # noinspection PyUnresolvedReferences
    def istrue(self, expr):
        """assert that an expression evaluates to True"""
        val = self.interp(expr)
        return self.assertTrue(val)

    # noinspection PyUnresolvedReferences
    def isfalse(self, expr):
        """assert that an expression evaluates to False"""
        val = self.interp(expr)
        return self.assertFalse(val)

    def check_output(self, chk_str, exact=False):
        self.interp.writer.flush()
        out = self.read_stdout().split('\n')
        if out:
            if exact:
                return chk_str == out[0]
            return chk_str in out[0]
        return False


class TestEval(TestCase):
    """testing of asteval"""

    # noinspection PyTypeChecker
    def test_assert(self):
        """test assert statements"""
        self.interp.error = []
        self.interp('n=6')
        self.interp('assert n==6')
        with self.assertRaises(AssertionError):
            self.interp('assert n==7')

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
            with self.assertRaises(SyntaxError):
                self.interp(expr, show_errors=False)

    def test_unsupportednodes(self):
        """unsupported nodes"""
        for expr in ('f = lambda x: x*x', 'yield 10'):
            failed = False
            # noinspection PyBroadException
            with self.assertRaises(NotImplementedError):
                self.interp(expr, show_errors=False)


    def test_syntaxerrors_2(self):
        """syntax errors test"""
        for expr in ('x = (1/*)', 'x = 1.A', 'x = A.2'):
            failed = False
            # noinspection PyBroadException
            with self.assertRaises(SyntaxError):
                self.interp(expr, show_errors=False)

    def test_runtimeerrors_1(self):
        """runtime errors test"""
        self.interp("zero = 0")
        self.interp("astr ='a string'")
        self.interp("atup = ('a', 'b', 11021)")
        self.interp("arr  = range(20)")
        for expr, err in (('x = 1/zero', ZeroDivisionError),
                              ('x = zero + nonexistent', NameError),
                              ('x = zero + astr', TypeError),
                              ('x = zero()', TypeError),
                              ('x = astr * atup', TypeError),
                              ('x = arr.shapx', AttributeError),
                              ('arr.shapx = 4', AttributeError),
                              ('del arr.shapx', KeyError)):

            with self.assertRaises(err):
                # print(expr, repr(err))
                self.interp(expr)


    # def test_namefinder(self):
    #     """test namefinder"""
    #     p = self.interp.parse('x+y+cos(z)')
    #     nf = NameFinder()
    #     nf.generic_visit(p)
    #     self.assertTrue('x' in nf.names)
    #     self.assertTrue('y' in nf.names)
    #     self.assertTrue('z' in nf.names)
    #     self.assertTrue('cos' in nf.names)


    def test_import_noops(self):
        # From import is accepted but is a NOOP
        #self.interp("import sys")
        self.interp("from sys import getcwd")
        self.interp("from sys import getcwd as GetCwd")


    def test_reservedwords(self):
        """test reserved words"""
        for w in ('and', 'as', 'while', 'raise', 'else',
                  'class', 'del', 'def', 'import', 'None'):
            self.interp.error = []
            # noinspection PyBroadException
            expr = "%s= 2" % w
            with self.assertRaises(SyntaxError):
                self.interp(expr, show_errors=False)

        for w in ('True', 'False'):
            self.interp.error = []
            with self.assertRaises(SyntaxError):
                self.interp("%s= 2" % w)

        for w in ('eval', '__import__'):
            self.interp.error = []
            with self.assertRaises(NameError):
                self.interp("%s= 2" % w)


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
        with self.assertRaises(RuntimeError):
            self.interp("'*'*(1+2<<17)")

        with self.assertRaises(RuntimeError):
            self.interp("'*'*(2<<17) + '*'")

        self.interp("10**10000")

        with self.assertRaises(RuntimeError):
            self.interp("10**10001")

        self.interp("1<<1000")

        with self.assertRaises(RuntimeError):
            self.interp("1<<1001")

#     def test_dos(self):
#         self.interp("""for x in range(2<<21): pass""")
#         self.check_error('RuntimeError', 'Max cycles')
#         self.interp("""while True:\n    pass""")
#         self.check_error('RuntimeError', 'Max cycles')
#         # self.interp("""while 1: pass""")
#         # self.check_error('RuntimeError', 'time limit')
#         self.interp("""def foo(): return foo()\nfoo()""")
#         self.check_error('RuntimeError')  # Stack overflow... is caught, but with MemoryError. A bit concerning...
#
#     def test_kaboom(self):
#         """ test Ned Batchelder's 'Eval really is dangerous' - Kaboom test (and related tests)"""
#         self.interp("""(lambda fc=(lambda n: [c for c in ().__class__.__bases__[0].__subclasses__() if c.__name__ == n][0]):
#     fc("function")(fc("code")(0,0,0,0,"KABOOM",(),(),(),"","",0,""),{})()
# )()""")
#         self.check_error('NotImplementedError', 'Lambda')  # Safe, lambda is not supported
#
#         self.interp(
#             """[print(c) for c in ().__class__.__bases__[0].__subclasses__()]""")  # Try a portion of the kaboom...
#         if PY3:
#             self.check_error('AttributeError', '__class__')  # Safe, unsafe dunders are not supported
#         else:
#             self.check_error('SyntaxError')
#         self.interp("9**9**9**9**9**9**9**9")
#         self.check_error('RuntimeError')  # Safe, safe_pow() catches this
#         self.interp(
#             "((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((1))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))")
#         self.check_error('MemoryError')  # Hmmm, this is caught, but its still concerning...
#         self.interp("compile('xxx')")
#         self.check_error('NameError')  # Safe, compile() is not supported

    def test_exit_value(self):
        """
        Return value of this version of asteval is only set by a top-level `return`... 
        the last eval. expression does NOT set this value. This is because this version
        of asteval is script-centric where-as the original asteval was expression-centric.
        """
        z = self.interp("return True")
        self.assertTrue(z)

        z = self.interp("True")  # No return, so None
        self.assertIsNone(z)

        z = self.interp("x = 1\ny = 2\ny == x + x\n")  # No return, so None
        self.assertIsNone(z)

        z = self.interp("x = 1\ny = 2\ny == x + x\nreturn y\n")
        self.assertEqual(2, z)

        z = self.interp("x = 42\nx")  # No return, so None
        self.assertIsNone(z)

        z = self.interp("""def foo(): return 42\nfoo()""")  # No return, so None
        self.assertIsNone(z)

        z = self.interp("""def foo(): return 42\nreturn foo()""")
        self.assertEqual(42, z)

    def test_errors(self):
        with self.assertRaises(SyntaxError):
            self.interp("x=1\ny=1\nz=56%$#%@$#%@#$...")

    def test_tracer(self):
        def tracer(frame, event, args):
            print(frame.get_name(), frame.get_symbols(), event, args)

        self.interp.set_trace(tracer)

        self.interp(dedent("""
            z = 42
            def foo(x):
                def bar(x):
                    return x * x
                return bar(x)

            for y in range(10):
                print(foo(y))

            z = [foo(x) for x in range(3)]
            print("ok!")
        """))


EXPECTED_PAT = re.compile("""^#\s*(?:"([^"]+)"|'([^']+)')""")


class TestCaseRunner(unittest.TestCase):
    def test_case_runner(self):
        def print_out(*args):
            out.write([str(a) for a in args])

        def importer(name):
            scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
            import_name = os.path.join(scripts_dir, name + '.py')
            with open(import_name, 'rb') as f:
                return import_name, f.read()

        this_dir = os.path.dirname(__file__)
        testcases = os.path.abspath(os.path.join(this_dir, "scripts"))
        for f in os.listdir(testcases):
            if not f.startswith('__'):
                print("*"*20)
                print(f)
                with open(os.path.join(testcases, f), 'r') as fobj:
                    script = fobj.read()

                out = StringIO()
                interp = Interpreter(f, writer=out, import_hook=importer)
                interp.set_symbol('print', interp.print_)
                try:
                    interp(script)
                except Exception as e:
                    trace = '\n'.join(interp.ui_trace)
                    print(trace)
                    self.fail("Unhandled exception! {}".format(e))

                actual = out.getvalue()
                trace = '\n'.join(interp.ui_trace)
                print(trace)

                with stdoutIO() as s:
                    exec(script, dict())

                expected = s.getvalue()
                self.assertEqual(expected, actual, msg="AstEval {!r} != CPython {!r} in {}".format(actual, expected, f))
                print("Fingerprint: {!r}".format(actual.replace('\n', '|')))



if __name__ == '__main__':  # pragma: no cover
    for suite in (TestEval, TestCaseRunner):
        suite = unittest.TestLoader().loadTestsFromTestCase(suite)
        unittest.TextTestRunner(verbosity=2).run(suite)
