#!/usr/bin/env python
"""
Base TestCase for asteval
"""
import ast
import math
import os
import textwrap
import time
import unittest
from functools import partial
from io import StringIO
from sys import version_info
from tempfile import NamedTemporaryFile

import pytest

from asteval import Interpreter, NameFinder, make_symbol_table
from asteval.astutils import get_ast_names

HAS_NUMPY = False
try:
    import numpy as np
    from numpy.testing import assert_allclose
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


def make_interpreter(nested_symtable=True):
    interp = Interpreter(nested_symtable=nested_symtable)
    interp.writer = NamedTemporaryFile('w', delete=False, prefix='astevaltest')
    return interp

def read_stdout(interp):
    stdout = interp.writer
    stdout.flush()
    stdout.close()
    time.sleep(0.1)
    fname = stdout.name
    with open(stdout.name) as inp:
        out = inp.read()
    interp.writer =  NamedTemporaryFile('w', delete=False, prefix='astevaltest')
    os.unlink(fname)
    return out


def isvalue(interp, sym, val):
    tval = interp.symtable.get(sym)
    if HAS_NUMPY and isinstance(tval, np.ndarray):
        assert_allclose(tval, val, rtol=0.01)
    else:
        assert tval == val

def isnear(interp, expr, val):
    tval = interp(expr)
    if HAS_NUMPY:
        assert_allclose(tval, val, rtol=1.e-4, atol=1.e-4)

def istrue(interp, expr):
    """assert that an expression evaluates to True"""
    val = interp(expr)
    if HAS_NUMPY and isinstance(val, np.ndarray):
        val = np.all(val)
    return bool(val)

def isfalse(interp, expr):
    """assert that an expression evaluates to False"""
    val = interp(expr)
    if HAS_NUMPY and isinstance(val, np.ndarray):
        val = np.all(val)
    return not bool(val)

def check_output(interp, chk_str, exact=False):
    out = read_stdout(interp).split('\n')
    if out:
        if exact:
            return chk_str == out[0]
        return chk_str in out[0]
    return False

def check_error(interp, chk_type='', chk_msg=''):
    try:
        errtype, errmsg = interp.error[0].get_error()
        assert errtype == chk_type
        if chk_msg:
            assert chk_msg in errmsg
    except IndexError:
        if chk_type:
            assert False


def test_py3():
    assert version_info.major > 2

@pytest.mark.parametrize("nested", [False, True])
def test_dict_index(nested):
    """dictionary indexing"""
    interp = make_interpreter(nested_symtable=nested)
    interp("a_dict = {'a': 1, 'b': 2, 'c': 3, 'd': 4}")
    istrue(interp, "a_dict['a'] == 1")
    istrue(interp, "a_dict['d'] == 4")

@pytest.mark.parametrize("nested", [False, True])
def test_dict_set_index(nested):
    """dictionary indexing"""
    interp = make_interpreter(nested_symtable=nested)
    interp("a_dict = {'a': 1, 'b': 2, 'c': 3, 'd': 4}")
    interp("a_dict['a'] = -4")
    interp("a_dict['e'] = 73")

    istrue(interp, "a_dict['a'] == -4")
    istrue(interp, "a_dict['e'] == 73")

    interp("b_dict = {}")
    interp("keyname = 'a'")
    interp("b_dict[keyname] = (1, -1, 'x')")
    istrue(interp, "b_dict[keyname] ==  (1, -1, 'x')")

@pytest.mark.parametrize("nested", [False, True])
def test_list_index(nested):
    """list indexing"""
    interp = make_interpreter(nested_symtable=nested)
    interp("a_list = ['a', 'b', 'c', 'd', 'o']")
    istrue(interp, "a_list[0] == 'a'")
    istrue(interp, "a_list[1] == 'b'")
    istrue(interp, "a_list[2] == 'c'")

@pytest.mark.parametrize("nested", [False, True])
def test_tuple_index(nested):
    """tuple indexing"""
    interp = make_interpreter(nested_symtable=nested)
    interp("a_tuple = (5, 'a', 'x')")
    istrue(interp, "a_tuple[0] == 5")
    istrue(interp, "a_tuple[2] == 'x'")

@pytest.mark.parametrize("nested", [False, True])
def test_string_index(nested):
    """string indexing"""
    interp = make_interpreter(nested_symtable=nested)
    interp("a_string = 'hello world'")
    istrue(interp, "a_string[0] == 'h'")
    istrue(interp, "a_string[6] == 'w'")
    istrue(interp, "a_string[-1] == 'd'")
    istrue(interp, "a_string[-2] == 'l'")

@pytest.mark.parametrize("nested", [False, True])
def test_sets(nested):
    """build, use set"""
    interp = make_interpreter(nested_symtable=nested)
    interp("a_set = {'a', 'b', 'c', 'd', 'c'}")
    istrue(interp, "len(a_set) == 4")
    istrue(interp, "'b' in a_set")

    interp("c_major7 = {'c', 'e', 'g', 'b'}")
    interp("d_minor7 = {'d', 'f', 'a', 'c'}")
    interp("e_minor7 = {'e', 'g', 'b', 'd'}")
    interp("f_major7 = {'f', 'a', 'c', 'e'}")
    interp("g_dom7 = {'g', 'b', 'd', 'f'}")
    interp("a_minor7 = {'a', 'c', 'e', 'g'}")
    interp("b_halfdim = {'b', 'd', 'f', 'a'}")
    interp("c_diatonic = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}")

    interp("phrase = d_minor7 + g_dom7 + c_major7")
    check_error(interp, 'TypeError')
    istrue(interp, "c_major7 & d_minor7 == {'c'}")
    istrue(interp, "c_major7 & e_minor7 == {'b', 'g', 'e'}")
    istrue(interp, "c_major7 | d_minor7 == c_diatonic")

@pytest.mark.parametrize("nested", [False, True])
def test_basic(nested):
    """build, use set"""
    interp = make_interpreter(nested_symtable=nested)
    assert interp("4") == 4
    v = interp("'x'")
    assert v == 'x'
    v = interp("b'x'")
    assert v == b'x'
    v = interp("str(4)")
    assert v == '4'
    v = interp("repr(4)")
    assert v == '4'

    assert interp("...") == ...
    assert not interp("False")
    interp("x = 8")
    interp("x.foo = 3")
    check_error(interp, 'AttributeError')
    interp("del x")

@pytest.mark.parametrize("nested", [False, True])
def test_fstring(nested):
    "fstrings"
    interp = make_interpreter(nested_symtable=nested)
    interp("x = 2523.33/723")
    interp("s = f'{x:+.3f}'")
    istrue(interp, "s == '+3.490'")

    interp("chie = '\u03c7(E)'")
    interp("v_s = f'{chie!s}'")
    interp("v_r = f'{chie!r}'")
    interp("v_a = f'{chie!a}'")

    istrue(interp, "v_s == '\u03c7(E)'")
    istrue(interp, '''v_r == "'\u03c7(E)'"''')
    istrue(interp, '''v_a == "'\\\\u03c7(E)'"''')

@pytest.mark.parametrize("nested", [False, True])
def test_verylong_strings(nested):
    "test that long string raises an error"
    interp = make_interpreter(nested_symtable=nested)
    longstr = "statement_of_somesize" * 5000
    interp(longstr)
    check_error(interp, 'RuntimeError')

@pytest.mark.parametrize("nested", [False, True])
def test_ndarray_index(nested):
    """nd array indexing"""
    interp = make_interpreter(nested_symtable=nested)
    if HAS_NUMPY:
        interp("a_ndarray = 5*arange(20)")
        assert interp("a_ndarray[2]") == 10
        assert interp("a_ndarray[4]") == 20

@pytest.mark.parametrize("nested", [False, True])
def test_ndarrayslice(nested):
    """array slicing"""
    interp = make_interpreter(nested_symtable=nested)
    interp("xlist = lisr(range(12))")
    istrue(interp, "x[::3] == [0, 3, 6, 9]")
    if HAS_NUMPY:
        interp("a_ndarray = arange(200).reshape(10, 20)")
        istrue(interp, "a_ndarray[1:3,5:7] == array([[25,26], [45,46]])")
        interp("y = arange(20).reshape(4, 5)")
        istrue(interp, "y[:,3]  == array([3, 8, 13, 18])")
        istrue(interp, "y[...,1]  == array([1, 6, 11, 16])")
        istrue(interp, "y[1,:] == array([5, 6, 7, 8, 9])")
        interp("y[...,1] = array([2, 2, 2, 2])")
        istrue(interp, "y[1,:] == array([5, 2, 7, 8, 9])")
        interp("xarr = arange(12)")
        istrue(interp, "x[::3] == array([0, 3, 6, 9])")

@pytest.mark.parametrize("nested", [False, True])
def test_while(nested):
    """while loops"""
    interp = make_interpreter(nested_symtable=nested)
    interp(textwrap.dedent("""
            n=0
            while n < 8:
                n += 1
            """))
    isvalue(interp, 'n', 8)

    interp(textwrap.dedent("""
            n=0
            while n < 8:
                n += 1
                if n > 3:
                    break
            else:
                n = -1
            """))
    isvalue(interp, 'n', 4)

    interp(textwrap.dedent("""
            n=0
            while n < 8:
                n += 1
            else:
                n = -1
            """))
    isvalue(interp, 'n', -1)

    interp(textwrap.dedent("""
            n, i = 0, 0
            while n < 10:
                n += 1
                if n % 2:
                    continue
                i += 1
            print( 'finish: n, i = ', n, i)
            """))
    isvalue(interp, 'n', 10)
    isvalue(interp, 'i', 5)

    interp(textwrap.dedent("""
            n=0
            while n < 10:
                n += 1
                print( ' n = ', n)
                if n > 5:
                    break
            print( 'finish: n = ', n)
            """))
    isvalue(interp, 'n', 6)

@pytest.mark.parametrize("nested", [False, True])
def test_while_continue(nested):
    interp = make_interpreter(nested_symtable=nested)
    interp(textwrap.dedent("""
            n, i = 0, 0
            while n < 10:
                n += 1
                if n % 2:
                    continue
                i += 1
            print( 'finish: n, i = ', n, i)
            """))
    isvalue(interp, 'n', 10)
    isvalue(interp, 'i', 5)

@pytest.mark.parametrize("nested", [False, True])
def test_while_break(nested):
    interp = make_interpreter(nested_symtable=nested)
    interp(textwrap.dedent("""
            n = 0
            while n < 10:
                n += 1
                if n > 6:
                    break
            print( 'finish: n = ', n)
            """))
    isvalue(interp, 'n', 7)

@pytest.mark.parametrize("nested", [False, True])
def test_with(nested):
    "test with"
    interp = make_interpreter(nested_symtable=nested)
    tmpfile = NamedTemporaryFile('w', delete=False, prefix='asteval_test')
    tmpfile.write('hello world\nline 2\nline 3\n\n')
    tmpfile.close()
    time.sleep(0.25)
    fname = tmpfile.name.replace('\\', '/')
    interp(textwrap.dedent("""
    with open('{0}', 'r') as fh:
          lines = fh.readlines()
    """.format(fname)))
    lines = interp.symtable['lines']
    fh1 = interp.symtable['fh']
    assert fh1.closed
    assert len(lines) > 2
    assert lines[1].startswith('line')


@pytest.mark.parametrize("nested", [False, True])
def test_assert(nested):
    """test assert statements"""
    interp = make_interpreter(nested_symtable=nested)
    interp.error = []
    interp('n=6')
    interp('assert n==6')
    check_error(interp, None)
    interp('assert n==7')
    check_error(interp, 'AssertionError')
    interp('assert n==7, "no match"')
    check_error(interp, 'AssertionError', 'no match')

@pytest.mark.parametrize("nested", [False, True])
def test_for(nested):
    """for loops"""
    interp = make_interpreter(nested_symtable=nested)
    interp(textwrap.dedent("""
            n=0
            for i in range(10):
                n += i
            """))
    isvalue(interp, 'n', 45)

    interp(textwrap.dedent("""
            n=0
            for i in range(10):
                n += i
            else:
                n = -1
            """))
    isvalue(interp, 'n', -1)

    if HAS_NUMPY:
        interp(textwrap.dedent("""
                n=0
                for i in arange(10):
                    n += i
                """))
        isvalue(interp, 'n', 45)

        interp(textwrap.dedent("""
                n=0
                for i in arange(10):
                    n += i
                else:
                    n = -1
                """))
        isvalue(interp, 'n', -1)

@pytest.mark.parametrize("nested", [False, True])
def test_for_break(nested):
    interp = make_interpreter(nested_symtable=nested)
    interp(textwrap.dedent("""
            n=0
            for i in range(10):
                n += i
                if n > 2:
                    break
            else:
                n = -1
            """))
    isvalue(interp, 'n', 3)
    if HAS_NUMPY:
        interp(textwrap.dedent("""
                n=0
                for i in arange(10):
                    n += i
                    if n > 2:
                        break
                else:
                    n = -1
                """))
        isvalue(interp, 'n', 3)

@pytest.mark.parametrize("nested", [False, True])
def test_if(nested):
    """runtime errors test"""
    interp = make_interpreter(nested_symtable=nested)
    interp(textwrap.dedent("""
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
    isvalue(interp, 'x', 2)
    isvalue(interp, 'y', 33)

@pytest.mark.parametrize("nested", [False, True])
def test_print(nested):
    """print (ints, str, ....)"""
    interp = make_interpreter(nested_symtable=nested)
    interp("print(31)")
    check_output(interp, '31\n', True)
    interp("print('%s = %.3f' % ('a', 1.2012345))")
    check_output(interp, 'a = 1.201\n', True)
    interp("print('{0:s} = {1:.2f}'.format('a', 1.2012345))")
    check_output(interp, 'a = 1.20\n', True)

@pytest.mark.parametrize("nested", [False, True])
def test_repr(nested):
    """repr of dict, list"""
    interp = make_interpreter(nested_symtable=nested)
    interp("x = {'a': 1, 'b': 2, 'c': 3}")
    interp("y = ['a', 'b', 'c']")
    interp("rep_x = repr(x['a'])")
    interp("rep_y = repr(y)")
    interp("rep_y , rep_x")
    interp("repr(None)")
    isvalue(interp, "rep_x", "1")
    isvalue(interp, "rep_y", "['a', 'b', 'c']")

@pytest.mark.parametrize("nested", [False, True])
def test_cmp(nested):
    """numeric comparisons"""
    interp = make_interpreter(nested_symtable=nested)
    istrue(interp, "3 == 3")
    istrue(interp, "3.0 == 3")
    istrue(interp, "3.0 == 3.0")
    istrue(interp, "3 != 4")
    istrue(interp, "3.0 != 4")
    istrue(interp, "3 >= 1")
    istrue(interp, "3 >= 3")
    istrue(interp, "3 <= 3")
    istrue(interp, "3 <= 5")
    istrue(interp, "3 < 5")
    istrue(interp, "5 > 3")
    isfalse(interp, "3 == 4")
    isfalse(interp, "3 > 5")
    isfalse(interp, "5 < 3")

@pytest.mark.parametrize("nested", [False, True])
def test_comparisons_return(nested):
    """test comparisons that do not return a bool"""
    interp = make_interpreter(nested_symtable=nested)
    if HAS_NUMPY:

        x = np.arange(10)/1.2
        out = x > 2.3

        interp("x = arange(10)/1.2")
        interp("out = x > 2.3")

        assert all(interp.symtable['out'] == out)
        assert interp.symtable['out'].sum() == 7

        interp("out = (x > 2.3 < 6.2)")

        assert interp.error.pop().exc == ValueError


@pytest.mark.parametrize("nested", [False, True])
def test_bool(nested):
    """boolean logic"""
    interp = make_interpreter(nested_symtable=nested)
    interp(textwrap.dedent("""
            yes = True
            no = False
            nottrue = False
            a = range(7)"""))

    istrue(interp, "yes")
    isfalse(interp, "no")
    isfalse(interp, "nottrue")
    isfalse(interp, "yes and no or nottrue")
    isfalse(interp, "yes and (no or nottrue)")
    isfalse(interp, "(yes and no) or nottrue")
    istrue(interp, "yes or no and nottrue")
    istrue(interp, "yes or (no and nottrue)")
    isfalse(interp, "(yes or no) and nottrue")
    istrue(interp, "yes or not no")
    istrue(interp, "(yes or no)")
    isfalse(interp, "not (yes or yes)")
    isfalse(interp, "not (yes or no)")
    isfalse(interp, "not (no or yes)")
    istrue(interp, "not no or yes")
    isfalse(interp, "not yes")
    istrue(interp, "not no")

@pytest.mark.parametrize("nested", [False, True])
def test_bool_coerce(nested):
    """coercion to boolean"""
    interp = make_interpreter(nested_symtable=nested)
    istrue(interp, "1")
    isfalse(interp, "0")
    istrue(interp, "'1'")
    isfalse(interp, "''")
    istrue(interp, "[1]")
    isfalse(interp, "[]")
    istrue(interp, "(1)")
    istrue(interp, "(0,)")
    isfalse(interp, "()")
    istrue(interp, "dict(y=1)")
    isfalse(interp, "{}")

@pytest.mark.parametrize("nested", [False, True])
def test_assignment(nested):
    """variables assignment"""
    interp = make_interpreter(nested_symtable=nested)
    interp('n = 5')
    isvalue(interp, "n", 5)
    interp('s1 = "a string"')
    isvalue(interp, "s1", "a string")
    interp('b = (1,2,3)')
    isvalue(interp, "b", (1, 2, 3))
    if HAS_NUMPY:
        interp('a = 1.*arange(10)')
        isvalue(interp, "a", np.arange(10))
        interp('a[1:5] = 1 + 0.5 * arange(4)')
        isnear(interp, "a", np.array([0., 1., 1.5, 2., 2.5, 5., 6., 7., 8., 9.]))

@pytest.mark.parametrize("nested", [False, True])
def test_names(nested):
    """names test"""
    interp = make_interpreter(nested_symtable=nested)
    interp('nx = 1')
    interp('nx1 = 1')
        # use \u escape b/c python 2 complains about file encoding
    interp('\u03bb = 1')
    interp('\u03bb1 = 1')

@pytest.mark.parametrize("nested", [False, True])
def test_syntaxerrors_1(nested):
    """assignment syntax errors test"""
    interp = make_interpreter(nested_symtable=nested)
    for expr in ('class = 1', 'for = 1', 'if = 1', 'raise = 1',
                 '1x = 1', '1.x = 1', '1_x = 1',
                 'return 3', 'return False'):
        failed = False
        # noinspection PyBroadException
        try:
            interp(expr, show_errors=False, raise_errors=True)
        except:
            failed = True

        assert failed
        check_error(interp, 'SyntaxError')

@pytest.mark.parametrize("nested", [False, True])
def test_unsupportednodes(nested):
    """unsupported nodes"""
    interp = make_interpreter(nested_symtable=nested)
    for expr in ('f = lambda x: x*x', 'yield 10'):
        failed = False
        # noinspection PyBroadException
        try:
            interp(expr, show_errors=False, raise_errors=True)
        except:
            failed = True
    assert failed
    check_error(interp, 'NotImplementedError')

@pytest.mark.parametrize("nested", [False, True])
def test_syntaxerrors_2(nested):
    """syntax errors test"""
    interp = make_interpreter(nested_symtable=nested)
    for expr in ('x = (1/*)', 'x = 1.A', 'x = A.2'):
        failed = False
        # noinspection PyBroadException
        try:
            interp(expr, show_errors=False, raise_errors=True)
        except:  # RuntimeError:
            failed = True
    assert failed
    check_error(interp, 'SyntaxError')


@pytest.mark.parametrize("nested", [False, True])
def test_runtimeerrors_1(nested):
    """runtime errors test"""
    interp = make_interpreter(nested_symtable=nested)
    interp("zero = 0")
    interp("astr ='a string'")
    interp("atup = ('a', 'b', 11021)")
    interp("arr  = range(20)")
    for expr, errname in (('x = 1/zero', 'ZeroDivisionError'),
                          ('x = zero + nonexistent', 'NameError'),
                          ('x = zero + astr', 'TypeError'),
                          ('x = zero()', 'TypeError'),
                          ('x = astr * atup', 'TypeError'),
                          ('x = arr.shapx', 'AttributeError'),
                          ('arr.shapx = 4', 'AttributeError'),
                          ('del arr.shapx', 'KeyError'),
                          ('x, y = atup', 'ValueError')):
        failed, errtype, errmsg = False, None, None
        # noinspection PyBroadException
        try:
            interp(expr, show_errors=False, raise_errors=True)
        except:
            failed = True
    assert failed
    check_error(interp, errname)

@pytest.mark.parametrize("nested", [False, True])
def test_ndarrays(nested):
    """simple ndarrays"""
    if HAS_NUMPY:
        interp = make_interpreter(nested_symtable=nested)
        interp('n = array([11, 10, 9])')
        istrue(interp, "isinstance(n, ndarray)")
        istrue(interp, "len(n) == 3")
        isvalue(interp, "n", np.array([11, 10, 9]))
        interp('n = arange(20).reshape(5, 4)')
        istrue(interp, "isinstance(n, ndarray)")
        istrue(interp, "n.shape == (5, 4)")
        interp("myx = n.shape")
        interp("n.shape = (4, 5)")
        istrue(interp, "n.shape == (4, 5)")
        interp("a = arange(20)")
        interp("gg = a[1:13:3]")
        isvalue(interp, 'gg', np.array([1, 4, 7, 10]))
        interp("gg[:2] = array([0,2])")
        isvalue(interp, 'gg', np.array([0, 2, 7, 10]))
        interp('a, b, c, d = gg')
        isvalue(interp, 'c', 7)
        istrue(interp, '(a, b, d) == (0, 2, 10)')


@pytest.mark.parametrize("nested", [False, True])
def test_binop(nested):
    """test binary ops"""
    interp = make_interpreter(nested_symtable=nested)
    interp('a = 10.0')
    interp('b = 6.0')
    istrue(interp, "a+b == 16.0")
    isnear(interp, "a-b", 4.0)
    istrue(interp, "a/(b-1) == 2.0")
    istrue(interp, "a*b     == 60.0")

@pytest.mark.parametrize("nested", [False, True])
def test_unaryop(nested):
    """test binary ops"""
    interp = make_interpreter(nested_symtable=nested)
    interp('a = -10.0')
    interp('b = -6.0')
    isnear(interp, "a", -10.0)
    isnear(interp, "b", -6.0)

@pytest.mark.parametrize("nested", [False, True])
def test_del(nested):
    """test del function"""
    interp = make_interpreter(nested_symtable=nested)
    interp('a = -10.0')
    interp('b = -6.0')
    assert 'a' in interp.symtable
    assert 'b' in interp.symtable
    interp("del a")
    interp("del b")
    assert 'a' not in interp.symtable
    assert  'b' not in interp.symtable

@pytest.mark.parametrize("nested", [False, True])
def test_math1(nested):
    """builtin math functions"""
    interp = make_interpreter(nested_symtable=nested)
    interp('n = sqrt(4)')
    istrue(interp, 'n == 2')
    isnear(interp, 'sin(pi/2)', 1)
    isnear(interp, 'cos(pi/2)', 0)
    istrue(interp, 'exp(0) == 1')
    if HAS_NUMPY:
        isnear(interp, 'exp(1)', np.e)

@pytest.mark.parametrize("nested", [False, True])
def test_namefinder(nested):
    """test namefinder"""
    interp = make_interpreter(nested_symtable=nested)
    p = interp.parse('x+y+cos(z)')
    nf = NameFinder()
    nf.generic_visit(p)
    assert 'x' in nf.names
    assert  'y' in nf.names
    assert 'z' in nf.names
    assert 'cos' in nf.names


@pytest.mark.parametrize("nested", [False, True])
def test_list_comprehension(nested):
    """test list comprehension"""
    interp = make_interpreter(nested_symtable=nested)
    interp('x = [i*i for i in range(4)]')
    isvalue(interp, 'x', [0, 1, 4, 9])
    interp('x = [i*i for i in range(6) if i > 1]')
    isvalue(interp, 'x', [4, 9, 16, 25])
    interp('x = [(i, j*2) for i in range(6) for j in range(2)]')
    isvalue(interp, 'x', [(0, 0), (0, 2), (1, 0), (1, 2), (2, 0), (2, 2),
                          (3, 0), (3, 2), (4, 0), (4, 2), (5, 0), (5, 2)])

    interp.readonly_symbols = set('a')
    list_in = "x = [a*2 for a in range(5)]"
    interp(list_in)
    check_error(interp, 'NameError')


@pytest.mark.parametrize("nested", [False, True])
def test_list_comprehension_more(nested):
    """more tests of list comprehension"""
    interp = make_interpreter(nested_symtable=nested)
    odd = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    even = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

    interp('odd = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]')
    interp('even = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]')

    for expr in  ['[2.5*x for x in range(4)]',
                '[(i, 5*i+j) for i in range(6) for j in range(3)]',
                '[(i, j*2) for i in range(6) for j in range(2) if i*j < 8]',
                '[(x, y) for (x,y) in [(1,2), (3,4)]]',
                '[(2*x, x+y) for (x,y) in [(1,3), (5,9)]]',
                '[p*2.5 for p in odd]',
                '[n for p in zip(odd, even) for n in p]',
                '[(i*i + 0.5) for i in range(4)]',
                '[i*3.2 for i in odd if i > 6 and i < 18]',
                '[i-1.0 for i in odd if i > 4 and i*2 not in (26, 34)]',
                ]:

        interp(f"out = {expr}")
        result = interp.symtable.get('out')
        assert repr(result) == repr(eval(expr))


@pytest.mark.parametrize("nested", [False, True])
def test_set_comprehension(nested):
    """test set comprehension"""
    interp = make_interpreter(nested_symtable=nested)
    set_in = "x = {(a,2*b) for a in range(5) for b in range(4)}"
    set_out = {(4, 0), (3, 4), (4, 6), (0, 2), (2, 2), (1, 0), (1, 6),
               (4, 2), (3, 0), (3, 6), (2, 4), (1, 2), (0, 4), (3, 2),
               (4, 4), (0, 0), (2, 0), (1, 4), (0, 6), (2, 6)}
    interp(set_in)
    isvalue(interp, "x", set_out)

@pytest.mark.parametrize("nested", [False, True])
def test_dict_comprehension(nested):
    """test set comprehension"""
    interp = make_interpreter(nested_symtable=nested)
    dict_in = "x = {a:2*b for a in range(5) for b in range(4)}"
    dict_out = {0: 6, 1: 6, 2: 6, 3: 6, 4: 6}
    interp(dict_in)
    isvalue(interp, 'x', dict_out)

    dict_in = "x = {a:yield for a in range(5) for yield in range(4)}"
    interp(dict_in)
    check_error(interp, 'SyntaxError')


@pytest.mark.parametrize("nested", [False, True])
def test_set_comprehension(nested):
    """test set comprehension"""
    interp = make_interpreter(nested_symtable=nested)
    set_in = "x = {(a,2*b) for a in range(5) for b in range(4)}"
    set_out = {(4, 0), (3, 4), (4, 6), (0, 2), (2, 2), (1, 0), (1, 6),
               (4, 2), (3, 0), (3, 6), (2, 4), (1, 2), (0, 4), (3, 2),
               (4, 4), (0, 0), (2, 0), (1, 4), (0, 6), (2, 6)}
    interp(set_in)
    isvalue(interp, "x", set_out)

@pytest.mark.parametrize("nested", [False, True])
def test_dict_comprehension(nested):
    """test set comprehension"""
    interp = make_interpreter(nested_symtable=nested)
    dict_in = "x = {a:2*b for a in range(5) for b in range(4)}"
    dict_out = {0: 6, 1: 6, 2: 6, 3: 6, 4: 6}
    interp(dict_in)
    isvalue(interp, 'x', dict_out)

    dict_in = "x = {a:yield for a in range(5) for yield in range(4)}"
    interp(dict_in)
    check_error(interp, 'SyntaxError')

@pytest.mark.parametrize("nested", [False, True])
def test_ifexp(nested):
    """test if expressions"""
    interp = make_interpreter(nested_symtable=nested)
    interp('x = 2')
    interp('y = 4 if x > 0 else -1')
    interp('z = 4 if x > 3 else -1')
    isvalue(interp, 'y', 4)
    isvalue(interp, 'z', -1)

@pytest.mark.parametrize("nested", [False, True])
def test_ifexp(nested):
    """test if expressions"""
    interp = make_interpreter(nested_symtable=nested)
    interp('x = 2')
    interp('y = 4 if x > 0 else -1')
    interp('z = 4 if x > 3 else -1')
    isvalue(interp, 'y', 4)
    isvalue(interp, 'z', -1)


@pytest.mark.parametrize("nested", [False, True])
def test_index_assignment(nested):
    """test indexing / subscripting on assignment"""
    if HAS_NUMPY:
        interp = make_interpreter(nested_symtable=nested)
        interp('x = arange(10)')
        interp('l = [1,2,3,4,5]')
        interp('l[0] = 0')
        interp('l[3] = -1')
        isvalue(interp, 'l', [0, 2, 3, -1, 5])
        interp('l[0:2] = [-1, -2]')
        isvalue(interp, 'l', [-1, -2, 3, -1, 5])
        interp('x[1] = 99')
        isvalue(interp, 'x', np.array([0, 99, 2, 3, 4, 5, 6, 7, 8, 9]))
        interp('x[0:2] = [9,-9]')
        isvalue(interp, 'x', np.array([9, -9, 2, 3, 4, 5, 6, 7, 8, 9]))

@pytest.mark.parametrize("nested", [False, True])
def test_reservedwords(nested):
    """test reserved words"""
    interp = make_interpreter(nested_symtable=nested)
    for w in ('and', 'as', 'while', 'raise', 'else',
              'class', 'del', 'def', 'import', 'None'):
        interp.error = []
        # noinspection PyBroadException
        try:
            interp("%s= 2" % w, show_errors=False, raise_errors=True)
        except:
            pass

        check_error(interp, 'SyntaxError')

        for w in ('True', 'False'):
            interp.error = []
            interp("%s= 2" % w)
            check_error(interp, 'SyntaxError')

        for w in ('eval', '__import__'):
            interp.error = []
            interp("%s= 2" % w)
            check_error(interp, 'NameError')

@pytest.mark.parametrize("nested", [False, True])
def test_raise(nested):
    """test raise"""
    interp = make_interpreter(nested_symtable=nested)
    interp("raise NameError('bob')")
    check_error(interp, 'NameError', 'bob')

@pytest.mark.parametrize("nested", [False, True])
def test_tryexcept(nested):
    """test try/except"""
    interp = make_interpreter(nested_symtable=nested)
    interp(textwrap.dedent("""
            x = 5
            try:
                x = x/0
            except ZeroDivisionError:
                print( 'Error Seen!')
                x = -999
            """))
    isvalue(interp, 'x', -999)

    interp(textwrap.dedent("""
            x = -1
            try:
                x = x/0
            except ZeroDivisionError:
                pass
            """))
    isvalue(interp, 'x', -1)

    interp(textwrap.dedent("""
            x = 15
            try:
                raise Exception()
                x = 20
            except:
                pass
            """))
    isvalue(interp, 'x', 15)

@pytest.mark.parametrize("nested", [False, True])
def test_tryelsefinally(nested):
    interp = make_interpreter(nested_symtable=nested)
    interp(textwrap.dedent("""
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
    interp("val, ok, clean = dotry(1, 2.0)")
    interp("print(ok, clean)")
    isnear(interp, "val", 0.5)
    isvalue(interp, "ok", True)
    isvalue(interp, "clean", True)

    interp("val, ok, clean = dotry(1, 0.0)")
    isvalue(interp, "val", -1)
    isvalue(interp, "ok", False)
    isvalue(interp, "clean", True)

@pytest.mark.parametrize("nested", [False, True])
def test_function1(nested):
    """test function definition and running"""
    interp = make_interpreter(nested_symtable=nested)
    interp(textwrap.dedent("""
            def fcn(x, scale=2):
                'test function'
                out = sqrt(x)
                if scale > 1:
                    out = out * scale
                return out
            """))
    interp("a = fcn(4, scale=9)")
    isvalue(interp, "a", 18)
    interp("a = fcn(9, scale=0)")
    isvalue(interp, "a", 3)
    interp("print(fcn)")
    check_output(interp, '<Procedure fcn(x, scale=')
    interp("a = fcn()")
    check_error(interp, 'TypeError', 'takes at least 1 arguments, got 0')
    interp("a = fcn(3,4,5,6,7)")
    check_error(interp, 'TypeError', 'expected at most 2, got')
    interp("a = fcn(77.0, other='what?')")
    check_error(interp, 'TypeError', 'extra keyword arguments for')


@pytest.mark.parametrize("nested", [False, True])
def test_function_vararg(nested):
    """test function with var args"""
    interp = make_interpreter(nested_symtable=nested)
    interp(textwrap.dedent("""
            def fcn(*args):
                'test varargs function'
                out = 0
                for i in args:
                    out = out + i*i
                return out
            """))
    interp("o = fcn(1,2,3)")
    isvalue(interp, 'o', 14)
    interp("print(fcn)")
    check_output(interp, '<Procedure fcn(')


@pytest.mark.parametrize("nested", [False, True])
def test_function_kwargs(nested):
    """test function with kw args, no **kws"""
    interp = make_interpreter(nested_symtable=nested)
    interp(textwrap.dedent("""
            def fcn(x=0, y=0, z=0, t=0, square=False):
                'test kwargs function'
                out = 0
                for i in (x, y, z, t):
                    if square:
                        out = out + i*i
                    else:
                        out = out + i
                return out
            """))
    interp("print(fcn)")
    check_output(interp, '<Procedure fcn(square')
    interp("o = fcn(x=1, y=2, z=3, square=False)")
    isvalue(interp, 'o', 6)
    interp("o = fcn(x=1, y=2, z=3, square=True)")
    isvalue(interp, 'o', 14)
    interp("o = fcn(3, 4, 5)")
    isvalue(interp, 'o', 12)
    interp("o = fcn(0, -1, 1)")
    isvalue(interp, 'o', 0)
    interp("o = fcn(0, -1, 1, square=True)")
    isvalue(interp, 'o', 2)
    interp("o = fcn(1, -1, 1, 1, True)")
    isvalue(interp, 'o', 4)
    interp("o = fcn(x=1, y=2, z=3, t=-2)")
    isvalue(interp, 'o', 4)
    interp("o = fcn(x=1, y=2, z=3, t=-12, s=1)")
    check_error(interp, 'TypeError', 'extra keyword arg')
    interp("o = fcn(x=1, y=2, y=3)")
    check_error(interp, 'SyntaxError')
    interp("o = fcn(0, 1, 2, 3, 4, 5, 6, 7, True)")
    check_error(interp, 'TypeError', 'too many arguments')

@pytest.mark.parametrize("nested", [False, True])
def test_function_kwargs1(nested):
    """test function with **kws arg"""
    interp = make_interpreter(nested_symtable=nested)
    interp(textwrap.dedent("""
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
    interp("print(fcn)")
    check_output(interp, '<Procedure fcn(square')
    interp("o = fcn(x=1, y=2, z=3, square=False)")
    isvalue(interp, 'o', 6)
    interp("o = fcn(x=1, y=2, z=3, square=True)")
    isvalue(interp, 'o', 14)

@pytest.mark.parametrize("nested", [False, True])
def test_function_kwargs2(nested):
    """test function with positional and **kws args"""
    interp = make_interpreter(nested_symtable=nested)
    interp(textwrap.dedent("""
            def fcn(x, y):
                'test function'
                return x + y**2
            """))
    interp("print(fcn)")
    check_output(interp, '<Procedure fcn(x,')
    interp("o = -1")
    interp("o = fcn(2, 1)")
    isvalue(interp, 'o', 3)
    interp("o = fcn(x=1, y=2)")
    isvalue(interp, 'o', 5)
    interp("o = fcn(y=2, x=7)")
    isvalue(interp, 'o', 11)
    interp("o = fcn(1, y=2)")
    isvalue(interp, 'o', 5)
    interp("o = fcn(1, x=2)")
    check_error(interp, 'TypeError')

@pytest.mark.parametrize("nested", [False, True])
def test_kwargx(nested):
    """test passing and chaining in **kwargs"""
    interp = make_interpreter(nested_symtable=nested)
    interp(textwrap.dedent("""
    def inner(foo=None, bar=None):
        return (foo, bar)

    def outer(**kwargs):
        return inner(**kwargs)
    """))

    ret = interp("inner(foo='a', bar=2)")
    assert ret == ('a', 2)
    ret = interp("outer(foo='a', bar=7)")
    assert ret == ('a', 7)
    ret = interp("outer(**dict(foo='b', bar=3))")
    assert ret == ('b', 3)


@pytest.mark.parametrize("nested", [False, True])
def test_nested_functions(nested):
    interp = make_interpreter(nested_symtable=nested)
    setup = """
    def a(x=10):
            if x > 5:
                return 1
            return -1

    def b():
            return 2.5

    def c(x=10):
            x = a(x=x)
            y = b()
            return x + y
     """
    interp(textwrap.dedent(setup))
    interp("o1 = c()")
    interp("o2 = c(x=0)")
    isvalue(interp, 'o1', 3.5)
    isvalue(interp, 'o2', 1.5)

@pytest.mark.parametrize("nested", [False, True])
def test_astdump(nested):
    """test ast parsing and dumping"""
    interp = make_interpreter(nested_symtable=nested)
    astnode = interp.parse('x = 1')
    assert isinstance(astnode, ast.Module)
    assert isinstance(astnode.body[0], ast.Assign)
    assert isinstance(astnode.body[0].targets[0], ast.Name)
    assert isinstance(astnode.body[0].value, ast.Constant)
    assert astnode.body[0].targets[0].id == 'x'
    assert astnode.body[0].value.value == 1
    dumped = interp.dump(astnode.body[0])
    assert dumped.startswith('Assign')

@pytest.mark.parametrize("nested", [False, True])
def test_get_ast_names(nested):
    """test ast_names"""
    interp = make_interpreter(nested_symtable=nested)
    interp('x = 12')
    interp('y = 9.9')
    astnode = interp.parse('z = x + y/3')
    names = get_ast_names(astnode)
    assert 'x' in names
    assert 'y' in names
    assert 'z' in names


@pytest.mark.parametrize("nested", [False, True])
def test_safe_funcs(nested):
    interp = make_interpreter(nested_symtable=nested)
    interp("'*'*(2<<17)")
    check_error(interp, None)
    interp("'*'*(1+2<<17)")
    check_error(interp, 'RuntimeError')
    interp("'*'*(2<<17) + '*'")
    check_error(interp, 'RuntimeError')
    interp("1.01**10000")
    check_error(interp, None)
    interp("1.01**10001")
    check_error(interp, 'RuntimeError')
    interp("1.5**10000")
    check_error(interp, 'OverflowError')
    interp("1<<1000")
    check_error(interp, None)
    interp("1<<1001")
    check_error(interp, 'RuntimeError')

@pytest.mark.parametrize("nested", [False, True])
def test_safe__numpyfuncs(nested):
    if HAS_NUMPY:
        interp = make_interpreter(nested_symtable=nested)
        interp("arg = linspace(0, 20000, 21)")
        interp("a = 3**arg")
        check_error(interp, 'RuntimeError')
        interp("a = 100 << arg")
        check_error(interp, 'RuntimeError')


@pytest.mark.parametrize("nested", [False, True])
def test_safe_open(nested):
    interp = make_interpreter(nested_symtable=nested)
    interp('open("foo1", "wb")')
    check_error(interp, 'RuntimeError')
    interp('open("foo2", "rb")')
    check_error(interp, 'FileNotFoundError')
    interp('open("foo3", "rb", 2<<18)')
    check_error(interp, 'RuntimeError')

@pytest.mark.parametrize("nested", [False, True])
def test_recursionlimit(nested):
    interp = make_interpreter(nested_symtable=nested)
    interp("""def foo(): return foo()\nfoo()""")
    check_error(interp, 'RecursionError')

@pytest.mark.parametrize("nested", [False, True])
def test_kaboom(nested):
    """ test Ned Batchelder's 'Eval really is dangerous'
    - Kaboom test (and related tests)"""
    interp = make_interpreter(nested_symtable=nested)
    interp("""(lambda fc=(lambda n: [c for c in ().__class__.__bases__[0].__subclasses__() if c.__name__ == n][0]):
    fc("function")(fc("code")(0,0,0,0,"KABOOM",(),(),(),"","",0,""),{})()
)()""")
    check_error(interp, 'NotImplementedError')  # Safe, lambda is not supported

    interp("""[print(c) for c in ().__class__.__bases__[0].__subclasses__()]""")  # Try a portion of the kaboom...

    check_error(interp, 'AttributeError', '__class__')  # Safe, unsafe dunders are not supported
    interp("9**9**9**9**9**9**9**9")
    check_error(interp, 'RuntimeError')  # Safe, safe_pow() catches this
    s = 'x = ' + '('*100 + '1' + ')'*100
    interp(s)
    if version_info.minor > 8:
        isvalue(interp, 'x', 1)
        check_error(interp, None)
    else:
        check_error(interp, 'RuntimeError')  # Hmmm, this is caught, but its still concerning...
    interp("compile('xxx')")
    check_error(interp, 'NameError')  # Safe, compile() is not supported

@pytest.mark.parametrize("nested", [False, True])
def test_exit_value(nested):
    """test expression eval - last exp. is returned by interpreter"""
    interp = make_interpreter(nested_symtable=nested)
    z = interp("True")
    assert z
    z = interp("x = 1\ny = 2\ny == x + x\n")
    assert z
    z = interp("x = 42\nx")
    assert  z == 42
    isvalue(interp, 'x', 42)
    z = interp("""def foo(): return 42\nfoo()""")
    assert z == 42

@pytest.mark.parametrize("nested", [False, True])
def test_interpreter_run(nested):
    interp = make_interpreter(nested_symtable=nested)
    interp('a = 12')
    interp.run('b = a + 2')
    isvalue(interp, 'b', 14)

    node = interp.parse('c = b - 7')
    interp.eval(node)
    isvalue(interp, 'c', 7)



@pytest.mark.parametrize("nested", [False, True])
def test_removenodehandler(nested):
    interp = make_interpreter(nested_symtable=nested)
    handler = interp.remove_nodehandler('ifexp')
    interp('testval = 300')
    interp('bogus = 3 if testval > 100 else 1')
    check_error(interp, 'NotImplementedError')

    interp.set_nodehandler('ifexp', handler)
    interp('bogus = 3 if testval > 100 else 1')
    isvalue(interp, 'bogus', 3)

@pytest.mark.parametrize("nested", [False, True])
def test_set_default_nodehandler(nested):
    interp = make_interpreter(nested_symtable=nested)
    handler_import = interp.set_nodehandler('import')
    handler_importfrom = interp.set_nodehandler('importfrom')
    interp('import ast')
    check_error(interp, None)

    interp('import notavailable')
    check_error(interp, 'ImportError')

    interp('from time import ctime, strftime')
    check_error(interp, None)
    interp('from time import ctime as tclock, strftime as s')
    check_error(interp, None)
    interp('import ast as pyast')
    check_error(interp, None)
    interp('x = pyast.parse("a = 1.0  + 3.4")')
    check_error(interp, None)

    interp.remove_nodehandler('import')
    interp.remove_nodehandler('importfrom')
    interp('from time import ctime')
    check_error(interp, 'NotImplementedError')


@pytest.mark.parametrize("nested", [False, True])
def test_interpreter_opts(nested):
    i1 = Interpreter(no_ifexp=True, nested_symtable=nested)
    assert i1.node_handlers['ifexp'] == i1.unimplemented

    i1('y = 4 if x > 0 else -1')
    errtype, errmsg = i1.error[0].get_error()
    assert errtype == 'NotImplementedError'

    conf = {k: v for k, v in i1.config.items()}
    conf['ifexp'] = True

    imin = Interpreter(minimal=True, nested_symtable=nested)
    assert not imin.config['ifexp']
    assert not imin.config['importfrom']
    assert not imin.config['augassign']
    assert not imin.config['with']

    ix = Interpreter(with_import=True, with_importfrom=True, nested_symtable=nested)
    assert ix.node_handlers['ifexp'] != ix.unimplemented
    assert ix.node_handlers['import'] != ix.unimplemented
    assert ix.node_handlers['importfrom'] != ix.unimplemented

    i2 = Interpreter(config=conf, nested_symtable=nested)
    assert i2.node_handlers['ifexp'] != i2.unimplemented
    assert i2.node_handlers['import'] == i2.unimplemented


@pytest.mark.parametrize("nested", [False, True])
def test_get_user_symbols(nested):
    interp = make_interpreter(nested_symtable=nested)
    interp("x = 1.1\ny = 2.5\nz = 788\n")
    usersyms = interp.user_defined_symbols()
    assert 'x' in usersyms
    assert 'y' in usersyms
    assert 'z' in usersyms
    assert 'foo' not in usersyms

@pytest.mark.parametrize("nested", [False, True])
def test_custom_symtable(nested):
    "test making and using a custom symbol table"
    if HAS_NUMPY:
        def cosd(x):
            "cos with angle in degrees"
            return np.cos(np.radians(x))

        def sind(x):
            "sin with angle in degrees"
            return np.sin(np.radians(x))

        def tand(x):
            "tan with angle in degrees"
            return np.tan(np.radians(x))

        sym_table = make_symbol_table(cosd=cosd, sind=sind, tand=tand,
                                      nested=nested, name='mysymtable')
        aeval = Interpreter(symtable=sym_table)
        aeval("x1 = sind(30)")
        aeval("x2 = cosd(30)")
        aeval("x3 = tand(45)")

        x1 = aeval.symtable['x1']
        x2 = aeval.symtable['x2']
        x3 = aeval.symtable['x3']

        assert_allclose(x1, 0.50, rtol=0.001)
        assert_allclose(x2, 0.866025, rtol=0.001)
        assert_allclose(x3, 1.00, rtol=0.001)

        repr1 = repr(sym_table)
        if nested:
            repr2 = sym_table._repr_html_()
            assert 'Group' in repr1
            assert '<caption>Group' in repr2
        else:
            assert isinstance(repr1, str)


@pytest.mark.parametrize("nested", [False, True])
def test_numpy_renames_in_custom_symtable(nested):
    """test that numpy renamed functions are in symtable"""
    if HAS_NUMPY:
        sym_table = make_symbol_table(nested=nested)
        lnfunc = sym_table.get('ln', None)
        assert lnfunc is not None

@pytest.mark.parametrize("nested", [False, True])
def test_readonly_symbols(nested):
    def foo():
        return 31

    usersyms = {
        "a": 10,
        "b": 11,
        "c": 12,
        "d": 13,
        "foo": foo,
        "bar": foo,
        "x": 5,
        "y": 7
        }

    aeval = Interpreter(usersyms=usersyms, nested_symtable=nested,
                        readonly_symbols={"a", "b", "c", "d", "foo", "bar"})

    aeval("a = 20")
    aeval("def b(): return 100")
    aeval("c += 1")
    aeval("del d")
    aeval("def foo(): return 55")
    aeval("bar = None")
    aeval("x = 21")
    aeval("y += a")

    assert aeval("a") == 10
    assert aeval("b") == 11
    assert aeval("c") == 12
    assert aeval("d") == 13
    assert aeval("foo()") == 31
    assert aeval("bar()") == 31
    assert aeval("x") == 21
    assert aeval("y") == 17

    assert aeval("abs(8)") == 8
    assert aeval("abs(-8)") == 8
    aeval("def abs(x): return x*2")
    assert aeval("abs(8)") == 16
    assert aeval("abs(-8)") == -16

    aeval2 = Interpreter(builtins_readonly=True)

    assert aeval2("abs(8)") == 8
    assert aeval2("abs(-8)") == 8
    aeval2("def abs(x): return x*2")
    assert aeval2("abs(8)") == 8
    assert aeval2("abs(-8)") == 8

@pytest.mark.parametrize("nested", [False, True])
def test_chained_compparisons(nested):
    interp = make_interpreter(nested_symtable=nested)
    interp('a = 7')
    interp('b = 12')
    interp('c = 19')
    interp('d = 30')
    assert interp('a < b < c < d')
    assert not interp('a < b < c/88 < d')
    assert not interp('a < b < c < d/2')

@pytest.mark.parametrize("nested", [False, True])
def test_array_compparisons(nested):
    if HAS_NUMPY:
        interp = make_interpreter(nested_symtable=nested)
        interp("sarr = arange(8)")
        sarr = np.arange(8)
        ox1 = interp("sarr < 4.3")
        assert np.all(ox1 == (sarr < 4.3))
        ox1 = interp("sarr == 4")
        assert np.all(ox1 == (sarr == 4))

@pytest.mark.parametrize("nested", [False, True])
def test_minimal(nested):
    aeval = Interpreter(builtins_readonly=True, minimal=True)
    aeval("a_dict = {'a': 1, 'b': 2, 'c': 3, 'd': 4}")
    assert aeval("a_dict['a'] == 1")
    assert aeval("a_dict['c'] == 3")

@pytest.mark.parametrize("nested", [False, True])
def test_partial_exception(nested):
    sym_table = make_symbol_table(sqrt=partial(math.sqrt), nested=nested)
    aeval = Interpreter(symtable=sym_table)

    assert aeval("sqrt(4)") == 2

    # Calling sqrt(-1) should raise a ValueError. When the interpreter
    # encounters an exception, it attempts to form an error string that
    # uses the function's __name__ attribute. Partials don't have a
    # __name__ attribute, so we want to make sure that an AttributeError is
    # not raised.

    result = aeval("sqrt(-1)")
    assert aeval.error.pop().exc == ValueError

@pytest.mark.parametrize("nested", [False, True])
def test_inner_return(nested):
    interp = make_interpreter(nested_symtable=nested)
    interp(textwrap.dedent("""
    def func():
         loop_cnt = 0
         for i in range(5):
             for k in range(5):
                 loop_cnt += 1
             return (i, k, loop_cnt)
    """))
    out = interp("func()")
    assert out == (0, 4, 5)

@pytest.mark.parametrize("nested", [False, True])
def test_nested_break(nested):
    interp = make_interpreter(nested_symtable=nested)
    interp(textwrap.dedent("""
    def func_w():
        for k in range(5):
            if k == 4:
                break
            something = 100
        return k
    """))
    assert 4 == interp("func_w()")

@pytest.mark.parametrize("nested", [False, True])
def test_pow(nested):
    interp = make_interpreter(nested_symtable=nested)
    assert 2**-2 == interp("2**-2")

@pytest.mark.parametrize("nested", [False, True])
def test_stringio(nested):
    """ test using stringio for output/errors """
    interp = make_interpreter(nested_symtable=nested)
    out = StringIO()
    err = StringIO()
    intrep = Interpreter(writer=out, err_writer=err)
    intrep("print('out')")
    assert out.getvalue() == 'out\n'

@pytest.mark.parametrize("nested", [False, True])
def test_gh129(nested):
    """ test that errors are propagated correctly, GH #129
    """
    interp = make_interpreter(nested_symtable=nested)
    interp('one, two, default  = 1, 2, 3')
    interp(textwrap.dedent("""
    try:
        output = some_var
    except NameError:
        output = None
    foo = output or default
    """))
    assert len(interp.error) == 0
    assert interp('foo') == 3

@pytest.mark.parametrize("nested", [False, True])
def test_no_duplicate_exception(nested):
    """ test that errors are not repeated GH #132
    """
    interp = make_interpreter(nested_symtable=nested)
    interp.run("print(hi)", with_raise=False)
    assert len(interp.error) == 1
    assert interp.error[0].exc == NameError

    # with plain eval too
    interp.error = []
    interp("print(hi)", raise_errors=False)
    assert len(interp.error) == 1
    assert interp.error[0].exc == NameError

@pytest.mark.parametrize("nested", [False, True])
def test_raise_errors_unknown_symbol(nested):
    """ test that raise_error raises corret error type. GH #133
    """
    interp = make_interpreter(nested_symtable=nested)
    interp.error = []
    try:
        saw_exception = False
        interp.run("unknown_value", with_raise=True)
    except NameError:
        saw_exception = True
    assert saw_exception
    assert len(interp.error) == 1
    assert interp.error[0].exc == NameError


@pytest.mark.parametrize("nested", [False, True])
def test_delete_slice(nested):
    """ test that a slice can be deleted"""

    interp = make_interpreter(nested_symtable=nested)
    interp.run("dlist = [1,3,5,7,9,11,13,15,17,19,21]")
    interp.run("del dlist[4:7]")
    assert interp("dlist") == [1, 3, 5, 7, 15, 17, 19, 21]

    if nested:
        interp.run("g = Group()")
        interp.run("g.dlist = [1,3,5,7,9,11,13,15,17,19,21]")
        interp.run("del g.dlist[4:7]")
        assert interp("g.dlist") == [1, 3, 5, 7, 15, 17, 19, 21]


if __name__ == '__main__':
    pytest.main(['-v', '-x', '-s'])
