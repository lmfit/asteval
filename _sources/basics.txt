================
Using asteval
================

The asteval module is very easy to use. Import the module and create an Interpreter:

    >>> from asteval import Interpreter
    >>> aeval = Interpreter()

you have an embedded interpreter for a procedural, mathematical language
that is very much like python in your application, all ready to use::

    >>> aeval('x = sqrt(3)')
    >>> aeval('print x')
    1.73205080757
    >>> aeval('''for i in range(10):
    print i, sqrt(i), log(1+1)
    ''')
    0 0.0 0.0
    1 1.0 0.69314718056
    2 1.41421356237 1.09861228867
    3 1.73205080757 1.38629436112
    4 2.0 1.60943791243
    5 2.2360679775 1.79175946923
    6 2.44948974278 1.94591014906
    7 2.64575131106 2.07944154168
    8 2.82842712475 2.19722457734
    9 3.0 2.30258509299



accessing the symbol table
===========================

The symbol table (that is, the mapping between variable and
function names and the underlying objects) is a simple dictionary
held in the :attr:`symtable` attribute of the interpreter.  Of
course, this can be read or written to by the python program:

    >>> aeval('x = sqrt(3)')
    >>> aeval.symtable['x']
    1.73205080757
    >>> aeval.symtable['y'] = 100
    >>> aeval('print y/8')
    12.5

(Note the use of true division even though the operands are integers).

Certain names are reserved in Python, and cannot be used within
the asteval interpreter.  These reserved words are:

    and, as, assert, break, class, continue, def, del, elif, else,
    except, exec, finally, for, from, global, if, import, in, is,
    lambda, not, or, pass, print, raise, return, try, while, with,
    True, False, None, eval, execfile, __import__, __package__

Valid symbol names must match the basic regular expression pattern::

   valid_name = [a-zA-Z_][a-zA-Z0-9_]*


built-in functions
=======================

At startup, 130 symbols are loaded into the symbol table from
Python's builtins and the **math** module.   The builtins include
several basic Python functions:

    abs, all, any, bin, bool, bytearray, bytes, chr, complex,
    delattr, dict, dir, divmod, enumerate, filter, float, format,
    frozenset, getattr, hasattr, hash, hex, id, int, isinstance,
    len, list, map, max, min, oct, open, ord, pow, property,
    range, repr, reversed, round, set, setattr, slice, sorted,
    str, sum, tuple, type, zip

and a large number of named exceptions:

    ArithmeticError, AssertionError, AttributeError,
    BaseException, BufferError, BytesWarning, DeprecationWarning,
    EOFError, EnvironmentError, Exception, False,
    FloatingPointError, GeneratorExit, IOError, ImportError,
    ImportWarning, IndentationError, IndexError, KeyError,
    KeyboardInterrupt, LookupError, MemoryError, NameError, None,
    NotImplemented, NotImplementedError, OSError, OverflowError,
    ReferenceError, RuntimeError, RuntimeWarning, StopIteration,
    SyntaxError, SyntaxWarning, SystemError, SystemExit, True,
    TypeError, UnboundLocalError, UnicodeDecodeError,
    UnicodeEncodeError, UnicodeError, UnicodeTranslateError,
    UnicodeWarning, ValueError, Warning, ZeroDivisionError


The symbols imported from Python's *math* module include:

    acos, acosh, asin, asinh, atan, atan2, atanh, ceil, copysign,
    cos, cosh, degrees, e, exp, fabs, factorial, floor, fmod,
    frexp, fsum, hypot, isinf, isnan, ldexp, log, log10, log1p,
    modf, pi, pow, radians, sin, sinh, sqrt, tan, tanh, trunc

If available, a very large number (~400) additional symbols are
imported from numpy.

conditionals and loops
==========================

If-then-else blocks, for-loops (including the optional *else* block) and
while loops (also including optional *else* block) are supported, and work
exactly as they do in python.  Thus:

    >>> code = """
    sum = 0
    for i in range(10):
        sum += i*sqrt(*1.0)
        if i % 4 == 0:
            sum = sum + 1
    print "sum = ", sum
    """
    >>> aeval(code)
    sum =  114.049534067


printing
===============

For printing, asteval emulates Python's native :func:`print` function and
:data:`print` statement (for python 2).  That is, the behavior mimics the
version of python used.


writing functions
===================

User-defined functions can be written and executed, as in python with a
*def* block, for example::

   >>> from asteval import Interpreter
   >>> aeval = Interpreter()
   >>> code = """def func(a, b, norm=1.0):
   ... return (a + b)/norm
   ... """
   >>> aeval.eval(code)
   >>> aeval.eval("func(1, 3, norm=10.0)")
   0.4




exceptions
===============

asteval monitors and caches exceptions in the evaluated code.  Brief error
messages are printed (with Python's print statement or function, and so
using standard output by default), and the full set of exceptions is kept
in the :attr:`error` attribute of the :class:`Interpreter` instance.  This
:attr:`error` attribute is a list of instances of the asteval
:class:`ExceptionHolder` class, which is accessed throught the
:meth:`get_error` method.  The :attr:`error` attribute is reset to an empty
list at the beginning of each :meth:`eval`, so that errors are from only
the most recent :meth:`eval`.  

Thus, to handle and re-raise exceptions from your Python code in a simple
REPL loop, you'd want to do something similar to
    
   >>> from asteval import Interpreter
   >>> aeval = Interpreter()
   >>> while True:
   >>>     inp_string = raw_input('dsl:>')
   >>>     result = aeval.eval(inp_string)
   >>>     if len(aeval.error)>0:
   >>>         for err in aeval.error:
   >>>             print(err.get_error())
   >>>     else:
   >>>         print(result)

