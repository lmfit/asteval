"""
utility functions for asteval

   Matthew Newville <newville@cars.uchicago.edu>,
   The University of Chicago
"""
from __future__ import division, print_function
import re
import ast

MAX_EXPONENT = 10000
MAX_STR_LEN = 2 << 17  # 256KiB
MAX_SHIFT = 1000
MAX_OPEN_BUFFER = 2 << 17
MAX_CYCLES = 5000

RESERVED_WORDS = ('and', 'as', 'assert', 'break', 'class', 'continue',
                  'def', 'del', 'elif', 'else', 'except', 'exec',
                  'finally', 'for', 'from', 'global', 'if', 'import',
                  'in', 'is', 'lambda', 'not', 'or', 'pass', 'print',
                  'raise', 'return', 'try', 'while', 'with', 'True',
                  'False', 'None', 'eval', 'execfile', '__import__',
                  '__package__')

NAME_MATCH = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*$").match

UNSAFE_ATTRS = ('__subclasses__', '__bases__', '__globals__', '__code__',
                '__closure__', '__func__', '__self__', '__module__',
                '__dict__', '__class__', '__call__', '__get__',
                '__getattribute__', '__subclasshook__', '__new__',
                '__init__', 'func_globals', 'func_code', 'func_closure',
                'im_class', 'im_func', 'im_self', 'gi_code', 'gi_frame',
                '__asteval__', 'f_locals')

# inherit these from python's __builtins__
FROM_PY = ('ArithmeticError', 'AssertionError', 'AttributeError',
           'BaseException', 'BufferError', 'BytesWarning',
           'DeprecationWarning', 'EOFError', 'EnvironmentError',
           'Exception', 'False', 'FloatingPointError', 'GeneratorExit',
           'IOError', 'ImportError', 'ImportWarning', 'IndentationError',
           'IndexError', 'KeyError', 'KeyboardInterrupt', 'LookupError',
           'MemoryError', 'NameError', 'None',
           'NotImplementedError', 'OSError', 'OverflowError',
           'ReferenceError', 'RuntimeError', 'RuntimeWarning',
           'StopIteration', 'SyntaxError', 'SyntaxWarning', 'SystemError',
           'SystemExit', 'True', 'TypeError', 'UnboundLocalError',
           'UnicodeDecodeError', 'UnicodeEncodeError', 'UnicodeError',
           'UnicodeTranslateError', 'UnicodeWarning', 'ValueError',
           'Warning', 'ZeroDivisionError', 'abs', 'all', 'any', 'bin',
           'bool', 'bytearray', 'bytes', 'chr', 'complex', 'dict', 'dir',
           'divmod', 'enumerate', 'filter', 'float', 'format', 'frozenset',
           'hash', 'hex', 'id', 'int', 'isinstance', 'len', 'list', 'map',
           'max', 'min', 'oct', 'ord', 'pow', 'range', 'repr',
           'reversed', 'round', 'set', 'slice', 'sorted', 'str', 'sum',
           'tuple', 'type', 'zip')

# inherit these from python's math
FROM_MATH = ('ceil', 'floor', 'sqrt', 'trunc')


def get_class_name(obj):
    try:
        return obj.__name__
    except:
        try:
            return obj.__class__.__name__
        except:
            return str(obj)

LOCALFUNCS = {}


# Safe versions of functions to prevent denial of service issues

def safe_pow(base, exp):
    if exp > MAX_EXPONENT:
        raise RuntimeError("Invalid exponent, max exponent is {}".format(MAX_EXPONENT))
    return base ** exp


def safe_mult(a, b):
    if isinstance(a, str) and isinstance(b, int) and len(a) * b > MAX_STR_LEN:
        raise RuntimeError("String length exceeded, max string length is {}".format(MAX_STR_LEN))
    return a * b


def safe_add(a, b):
    if isinstance(a, str) and isinstance(b, str) and len(a) + len(b) > MAX_STR_LEN:
        raise RuntimeError("String length exceeded, max string length is {}".format(MAX_STR_LEN))
    return a + b


def safe_lshift(a, b):
    if b > MAX_SHIFT:
        raise RuntimeError("Invalid left shift, max left shift is {}".format(MAX_SHIFT))
    return a << b


OPERATORS = {ast.Is: (lambda a, b: a is b, 'is'),
             ast.IsNot: (lambda a, b: a is not b, 'is not'),
             ast.In: (lambda a, b: a in b, 'in'),
             ast.NotIn: (lambda a, b: a not in b, 'not in'),
             ast.Add: (safe_add, '+'),
             ast.BitAnd: (lambda a, b: a & b, '&'),
             ast.BitOr: (lambda a, b: a | b, '|'),
             ast.BitXor: (lambda a, b: a ^ b, '^'),
             ast.Div: (lambda a, b: a / b, '/'),
             ast.FloorDiv: (lambda a, b: a // b, '//'),
             ast.LShift: (safe_lshift, '<<'),
             ast.RShift: (lambda a, b: a >> b, '>>'),
             ast.Mult: (safe_mult, '*'),
             ast.Pow: (safe_pow, '**'),
             ast.Sub: (lambda a, b: a - b, '-'),
             ast.Mod: (lambda a, b: a % b, '%'),
             ast.And: (lambda a, b: a and b, 'and'),
             ast.Or: (lambda a, b: a or b, 'or'),
             ast.Eq: (lambda a, b: a == b, '=='),
             ast.Gt: (lambda a, b: a > b, '>'),
             ast.GtE: (lambda a, b: a >= b, '>='),
             ast.Lt: (lambda a, b: a < b, '<'),
             ast.LtE: (lambda a, b: a <= b, '<='),
             ast.NotEq: (lambda a, b: a != b, '!='),
             ast.Invert: (lambda a: ~a, '~'),
             ast.Not: (lambda a: not a, 'not'),
             ast.UAdd: (lambda a: +a, '+'),
             ast.USub: (lambda a: -a, '-')
             }


def valid_symbol_name(name):
    """determines whether the input symbol name is a valid name

    This checks for reserved words, and that the name matches the
    regular expression ``[a-zA-Z_][a-zA-Z0-9_]``
    :param name: symbol name to test
    :return True if valid, False otherwise
    """
    if name in RESERVED_WORDS:
        return False
    return NAME_MATCH(name) is not None


def op2func(op):
    """return function for operator nodes
    :param op:
    """
    return OPERATORS[op.__class__]


class Empty:
    """empty class"""

    def __init__(self):
        pass

    # noinspection PyMethodMayBeStatic
    def __nonzero__(self):
        return False


ReturnedNone = Empty()


class NameFinder(ast.NodeVisitor):
    """find all symbol names used by a parsed node"""

    def __init__(self):
        self.names = []
        ast.NodeVisitor.__init__(self)

    def generic_visit(self, node):
        if node.__class__.__name__ == 'Name':
            if node.ctx.__class__ == ast.Load and node.id not in self.names:
                self.names.append(node.id)
        ast.NodeVisitor.generic_visit(self, node)


def get_ast_names(astnode):
    """returns symbol Names from an AST node
    :param astnode:
    """
    finder = NameFinder()
    finder.generic_visit(astnode)
    return finder.names


# Markdown helpers


def quote(s):
    is_str = isinstance(s, str)
    ret = "'{}'".format(s) if is_str else str(s)
    if is_str and len(ret) > 100:
        return ret[:100] + "...(truncated)'"
    return ret


def code_wrap(s, lang=''):
    s = quote(s)
    multiline = '\n' in s
    ticks = '```' if multiline else '`'
    newlines = '\n' if multiline else ''
    lang = lang if multiline else ''
    return ''.join([newlines, ticks, lang, newlines, s, newlines, ticks, newlines])
