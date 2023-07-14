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
    if HAS_NUMPY:
        interp("a_ndarray = arange(200).reshape(10, 20)")
        istrue(interp, "a_ndarray[1:3,5:7] == array([[25,26], [45,46]])")
        interp("y = arange(20).reshape(4, 5)")
        istrue(interp, "y[:,3]  == array([3, 8, 13, 18])")
        istrue(interp, "y[...,1]  == array([1, 6, 11, 16])")
        istrue(interp, "y[1,:] == array([5, 6, 7, 8, 9])")
        interp("y[...,1] = array([2, 2, 2, 2])")
        istrue(interp, "y[1,:] == array([5, 2, 7, 8, 9])")

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


if __name__ == '__main__':
    pytest.main(['-v', '-x', '-s'])
