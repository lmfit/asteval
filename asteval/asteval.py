"""
Safe(ish) evaluator of python expressions, using ast module.
The emphasis here is on mathematical expressions, and so
numpy functions are imported if available and used.

Symbols are held in the Interpreter symtable -- a simple
dictionary supporting a simple, flat namespace.

Expressions can be compiled into ast node and then evaluated
later, using the current values in the
"""

from __future__ import division, print_function

import ast
import contextlib
import inspect
import math
from sys import exc_info, stdout, stderr, version_info
import sys
from time import time

from .astutils import (FROM_PY, FROM_MATH, FROM_NUMPY, UNSAFE_ATTRS,
                       LOCALFUNCS, NUMPY_RENAMES, op2func,
                       ExceptionHolder, ReturnedNone, valid_symbol_name)


HAS_NUMPY = False
try:
    # noinspection PyUnresolvedReferences
    import numpy

    HAS_NUMPY = True
except ImportError:
    # print("Warning: numpy not available... functionality will be limited.")
    pass

builtins = __builtins__
if not isinstance(builtins, dict):
    builtins = builtins.__dict__


# noinspection PyIncorrectDocstring
class Interpreter:
    """mathematical expression compiler and interpreter.

  This module compiles expressions and statements to AST representation,
  using python's ast module, and then executes the AST representation
  using a dictionary of named object (variable, functions).

  The result is a restricted, simplified version of Python meant for
  numerical caclulations that is somewhat safer than 'eval' because some
  operations (such as 'import' and 'eval') are simply not allowed.  The
  resulting language uses a flat namespace that works on Python objects,
  but does not allow new classes to be defined.

  Many parts of Python syntax are supported, including:
     for loops, while loops, if-then-elif-else conditionals
     try-except (including 'finally')
     function definitions with def
     advanced slicing:    a[::-1], array[-3:, :, ::2]
     if-expressions:      out = one_thing if TEST else other
     list comprehension   out = [sqrt(i) for i in values]

  The following Python syntax elements are not supported:
      Import, Exec, Lambda, Class, Global, Generators,
      Yield, Decorators

  In addition, while many builtin functions are supported, several
  builtin functions are missing ('eval', 'exec', and 'getattr' for
  example) that can be considered unsafe.

  If numpy is installed, many numpy functions are also imported.

  :param int recursion_limit:
      Enforce a limit on the depth of function-calls *in addition* to
      the current stack, by invoking :func:`sys.setrecursionlimit()`.
      (affect python-interpreter globally!);
      if negative(-1 by default), no limit enforced.

      .. Warning::
         If limit too low (i.e. 10), :func:`eval()` may silently fail!
  """

    supported_nodes = ('arg', 'assert', 'assign', 'attribute', 'augassign',
                       'binop', 'boolop', 'break', 'call', 'compare',
                       'continue', 'delete', 'dict', 'ellipsis',
                       'excepthandler', 'expr', 'extslice', 'for',
                       'functiondef', 'if', 'ifexp', 'index', 'interrupt',
                       'list', 'listcomp', 'module', 'name', 'nameconstant',
                       'num', 'pass', 'print', 'raise', 'repr', 'return',
                       'slice', 'str', 'subscript', 'try', 'tuple', 'unaryop',
                       'while')

    def __init__(self, symtable=None, writer=None, use_numpy=True,
                 err_writer=None, max_time=5, recursion_limit=-1):
        self.writer = writer or stdout
        self.err_writer = err_writer or stderr
        self.start = 0
        self.max_time = max_time
        if isinstance(recursion_limit, bool) or not isinstance(recursion_limit, int):
            ## Dissallow True/False to be assumed as integers.
            msg = "The recursion_limit(%s) must be an integer!"
            raise ValueError(msg % recursion_limit)
        self.recursion_limit = recursion_limit

        if symtable is None:
            symtable = {}
        self.symtable = symtable
        self._interrupt = None
        self.error = []
        self.error_msg = None
        self.expr = None
        self.retval = None
        self.lineno = 0
        self.use_numpy = HAS_NUMPY and use_numpy

        symtable['print'] = self._printer
        for sym in FROM_PY:
            if sym in builtins:
                symtable[sym] = builtins[sym]

        for symname, obj in LOCALFUNCS.items():
            symtable[symname] = obj

        for sym in FROM_MATH:
            if hasattr(math, sym):
                symtable[sym] = getattr(math, sym)

        if self.use_numpy:
            for sym in FROM_NUMPY:
                if hasattr(numpy, sym):
                    symtable[sym] = getattr(numpy, sym)
            for name, sym in NUMPY_RENAMES.items():
                if hasattr(numpy, sym):
                    symtable[name] = getattr(numpy, sym)

        self.node_handlers = dict(((node, getattr(self, "on_%s" % node))
                                   for node in self.supported_nodes))

        # to rationalize try/except try/finally for Python2.6 through Python3.3
        self.node_handlers['tryexcept'] = self.node_handlers['try']
        self.node_handlers['tryfinally'] = self.node_handlers['try']

        self.no_deepcopy = []
        for key, val in symtable.items():
            if callable(val) or 'numpy.lib.index_tricks' in repr(val):
                self.no_deepcopy.append(key)

    @contextlib.contextmanager
    def limited_recursion(self):
        if self.recursion_limit >= 0:
            old_recursion_limit = sys.getrecursionlimit()
            sys.setrecursionlimit(len(inspect.stack()) + self.recursion_limit)
            try:
                yield
            finally:
                sys.setrecursionlimit(old_recursion_limit)
        else:
            yield

    def unimplemented(self, node):
        """unimplemented nodes"""
        self.raise_exception(node, exc=NotImplementedError,
                             msg="'%s' not supported" % node.__class__.__name__)

    def raise_exception(self, node, exc=None, msg='', expr=None, lineno=None):
        """add an exception"""
        if self.error is None:
            self.error = []
        if expr is None:
            expr = self.expr
        if self.error and not isinstance(node, ast.Module):
            msg = '%s' % msg
        err = ExceptionHolder(node, exc=exc, msg=msg, expr=expr, lineno=lineno)
        self._interrupt = ast.Break()
        self.error.append(err)
        if self.error_msg is None:
            self.error_msg = "%s in expr='%s'" % (msg, self.expr)
        elif msg:
            self.error_msg = "%s\n %s" % (self.error_msg, msg)
        if exc is None:
            # noinspection PyBroadException
            try:
                exc = self.error[0].exc
            except:
                exc = RuntimeError
        raise exc(self.error_msg)

    # main entry point for Ast node evaluation
    #  parse:  text of statements -> ast
    #  run:    ast -> result
    #  eval:   string statement -> result = run(parse(statement))
    def parse(self, text):
        """Parse statement/expression to Ast representation."""
        with self.limited_recursion():
            return self._parse(text)

    def _parse(self, text):
        """Parse statement/expression to Ast representation WITHOUT recursion-limit."""
        self.expr = text

        # noinspection PyBroadException
        try:
            return ast.parse(text)
        except SyntaxError:
            self.raise_exception(None, msg='Syntax Error', expr=text)
        except:
            self.raise_exception(None, msg='Runtime Error', expr=text)

    def run(self, node, expr=None, lineno=None, with_raise=True):
        """Executes parsed Ast representation for an expression."""
        with self.limited_recursion():
            return self._run(node, expr, lineno, with_raise)

    def _run(self, node, expr=None, lineno=None, with_raise=True):
        """Executes parsed Ast representation for an expression WITHOUT recursion-limit."""
        # Note: keep the 'node is None' test: internal code here may run
        #    run(None) and expect a None in return.
        if time() - self.start > self.max_time:
            raise RuntimeError("Execution exceeded time limit, max runtime is {}s".format(self.max_time))
        if self.error:
            return
        if node is None:
            return
        if isinstance(node, str):
            node = self._parse(node)
        if lineno is not None:
            self.lineno = lineno
        if expr is not None:
            self.expr = expr

        # get handler for this node:
        #   on_xxx with handle nodes of type 'xxx', etc
        try:
            handler = self.node_handlers[node.__class__.__name__.lower()]
        except KeyError:
            return self.unimplemented(node)

        # run the handler:  this will likely generate
        # recursive calls into this run method.
        # noinspection PyBroadException
        try:
            ret = handler(node)
            if isinstance(ret, enumerate):
                ret = list(ret)
            return ret
        except:
            if with_raise:
                self.raise_exception(node, expr=expr)

    def __call__(self, expr, **kw):
        return self.eval(expr, **kw)

    def eval(self, expr, lineno=0, show_errors=True):
        """Evaluates a single statement."""
        with self.limited_recursion():
            return self._eval(expr, lineno, show_errors)

    def _eval(self, expr, lineno=0, show_errors=True):
        """Evaluates a single statement WITHOUT recursion-limit."""
        self.lineno = lineno
        self.error = []
        self.start = time()

        try:
            node = self._parse(expr)
        except:
            errmsg = exc_info()[1]
            if self.error:
                errmsg = "\n".join(self.error[0].get_error())
            if not show_errors:
                # noinspection PyBroadException
                try:
                    exc = self.error[0].exc
                except:
                    exc = RuntimeError
                raise exc(errmsg)
            print(errmsg, file=self.err_writer)
            return
        # noinspection PyBroadException
        try:
            return self._run(node, expr=expr, lineno=lineno)
        except:
            errmsg = exc_info()[1]
            if self.error:
                errmsg = "\n".join(self.error[0].get_error())
            if not show_errors:
                # noinspection PyBroadException
                try:
                    exc = self.error[0].exc
                except:
                    exc = RuntimeError
                raise exc(errmsg)
            print(errmsg, file=self.err_writer)

    @staticmethod
    def dump(node, **kw):
        """simple ast dumper"""
        return ast.dump(node, **kw)

    # handlers for ast components
    def on_expr(self, node):
        """expression"""
        return self._run(node.value)  # ('value',)

    def on_index(self, node):
        """index"""
        return self._run(node.value)  # ('value',)

    def on_return(self, node):  # ('value',)
        """return statement: look for None, return special sentinal"""
        self.retval = self._run(node.value)
        if self.retval is None:
            self.retval = ReturnedNone
        return

    def on_repr(self, node):
        """repr """
        return repr(self._run(node.value))  # ('value',)

    def on_module(self, node):  # ():('body',)
        """module def"""
        out = None
        for tnode in node.body:
            out = self._run(tnode)
        return out

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def on_pass(self, node):
        """pass statement"""
        return None  # ()

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def on_ellipsis(self, node):
        """ellipses"""
        return Ellipsis

    # for break and continue: set the instance variable _interrupt
    def on_interrupt(self, node):  # ()
        """interrupt handler"""
        self._interrupt = node
        return node

    def on_break(self, node):
        """break"""
        return self.on_interrupt(node)

    def on_continue(self, node):
        """continue"""
        return self.on_interrupt(node)

    def on_assert(self, node):  # ('test', 'msg')
        """assert statement"""
        if not self._run(node.test):
            self.raise_exception(node, exc=AssertionError, msg=node.msg)
        return True

    def on_list(self, node):  # ('elt', 'ctx')
        """list"""
        return [self._run(e) for e in node.elts]

    def on_tuple(self, node):  # ('elts', 'ctx')
        """tuple"""
        return tuple(self.on_list(node))

    def on_dict(self, node):  # ('keys', 'values')
        """dictionary"""
        return dict([(self._run(k), self._run(v)) for k, v in
                     zip(node.keys, node.values)])

    # noinspection PyMethodMayBeStatic
    def on_num(self, node):  # ('n',)
        """return number"""
        return node.n

    # noinspection PyMethodMayBeStatic
    def on_str(self, node):  # ('s',)
        """return string"""
        return node.s

    def on_name(self, node):  # ('id', 'ctx')
        """ Name node """
        ctx = node.ctx.__class__
        if ctx in (ast.Param, ast.Del):
            return str(node.id)
        else:
            if node.id in self.symtable:
                return self.symtable[node.id]
            else:
                msg = "name '%s' is not defined" % node.id
                self.raise_exception(node, exc=NameError, msg=msg)

    # noinspection PyMethodMayBeStatic
    def on_nameconstant(self, node):
        """ True, False, None in python >= 3.4 """
        return node.value

    def node_assign(self, node, val):
        """here we assign a value (not the node.value object) to a node
        this is used by on_assign, but also by for, list comprehension, etc.
        """
        if node.__class__ == ast.Name:
            if not valid_symbol_name(node.id):
                errmsg = "invalid symbol name (reserved word?) %s" % node.id
                self.raise_exception(node, exc=NameError, msg=errmsg)
            self.symtable[node.id] = val
            if node.id in self.no_deepcopy:
                self.no_deepcopy.remove(node.id)

        elif node.__class__ == ast.Attribute:
            if node.ctx.__class__ == ast.Load:
                msg = "cannot assign to attribute %s" % node.attr
                self.raise_exception(node, exc=AttributeError, msg=msg)

            setattr(self._run(node.value), node.attr, val)

        elif node.__class__ == ast.Subscript:
            sym = self._run(node.value)
            xslice = self._run(node.slice)
            if isinstance(node.slice, ast.Index):
                sym[xslice] = val
            elif isinstance(node.slice, ast.Slice):
                # noinspection PyTypeChecker
                sym[slice(xslice.start, xslice.stop)] = val
            elif isinstance(node.slice, ast.ExtSlice):
                sym[xslice] = val
        elif node.__class__ in (ast.Tuple, ast.List):
            if len(val) == len(node.elts):
                for telem, tval in zip(node.elts, val):
                    self.node_assign(telem, tval)
            else:
                raise ValueError('too many values to unpack')

    def on_attribute(self, node):  # ('value', 'attr', 'ctx')
        """extract attribute"""
        ctx = node.ctx.__class__
        if ctx == ast.Store:
            msg = "attribute for storage: shouldn't be here!"
            self.raise_exception(node, exc=RuntimeError, msg=msg)

        sym = self._run(node.value)
        if ctx == ast.Del:
            return delattr(sym, node.attr)

        # ctx is ast.Load
        fmt = "cannnot access attribute '%s' for %s"
        if node.attr not in UNSAFE_ATTRS:
            fmt = "no attribute '%s' for %s"
            try:
                return getattr(sym, node.attr)
            except AttributeError:
                pass

        # AttributeError or accessed unsafe attribute
        obj = self._run(node.value)
        msg = fmt % (node.attr, obj)
        self.raise_exception(node, exc=AttributeError, msg=msg)

    def on_assign(self, node):  # ('targets', 'value')
        """simple assignment"""
        val = self._run(node.value)
        for tnode in node.targets:
            self.node_assign(tnode, val)
        return

    def on_augassign(self, node):  # ('target', 'op', 'value')
        """augmented assign"""
        return self.on_assign(ast.Assign(targets=[node.target],
                                         value=ast.BinOp(left=node.target,
                                                         op=node.op,
                                                         right=node.value)))

    def on_slice(self, node):  # ():('lower', 'upper', 'step')
        """simple slice"""
        return slice(self._run(node.lower),
                     self._run(node.upper),
                     self._run(node.step))

    def on_extslice(self, node):  # ():('dims',)
        """extended slice"""
        return tuple([self._run(tnode) for tnode in node.dims])

    def on_subscript(self, node):  # ('value', 'slice', 'ctx')
        """subscript handling -- one of the tricky parts"""
        val = self._run(node.value)
        nslice = self._run(node.slice)
        ctx = node.ctx.__class__
        if ctx in (ast.Load, ast.Store):
            if isinstance(node.slice, (ast.Index, ast.Slice, ast.Ellipsis)):
                return val.__getitem__(nslice)
            elif isinstance(node.slice, ast.ExtSlice):
                return val[nslice]
        else:
            msg = "subscript with unknown context"
            self.raise_exception(node, msg=msg)

    def on_delete(self, node):  # ('targets',)
        """delete statement"""
        for tnode in node.targets:
            if tnode.ctx.__class__ != ast.Del:
                break
            children = []
            while tnode.__class__ == ast.Attribute:
                children.append(tnode.attr)
                tnode = tnode.value

            if tnode.__class__ == ast.Name:
                children.append(tnode.id)
                children.reverse()
                self.symtable.pop('.'.join(children))
            else:
                msg = "could not delete symbol"
                self.raise_exception(node, msg=msg)

    def on_unaryop(self, node):  # ('op', 'operand')
        """unary operator"""
        return op2func(node.op)(self._run(node.operand))

    def on_binop(self, node):  # ('left', 'op', 'right')
        """binary operator"""
        return op2func(node.op)(self._run(node.left),
                                self._run(node.right))

    def on_boolop(self, node):  # ('op', 'values')
        """boolean operator"""
        val = self._run(node.values[0])
        is_and = ast.And == node.op.__class__
        if (is_and and val) or (not is_and and not val):
            for n in node.values[1:]:
                val = op2func(node.op)(val, self._run(n))
                if (is_and and not val) or (not is_and and val):
                    break
        return val

    def on_compare(self, node):  # ('left', 'ops', 'comparators')
        """comparison operators"""
        lval = self._run(node.left)
        out = True
        for op, rnode in zip(node.ops, node.comparators):
            rval = self._run(rnode)
            out = op2func(op)(lval, rval)
            lval = rval
            if self.use_numpy and isinstance(out, numpy.ndarray) and out.any():
                break
            elif not out:
                break
        return out

    def on_print(self, node):  # ('dest', 'values', 'nl')
        """ note: implements Python2 style print statement, not
        print() function.  May need improvement...."""
        dest = self._run(node.dest) or self.writer
        end = ''
        if node.nl:
            end = '\n'
        out = [self._run(tnode) for tnode in node.values]
        if out and not self.error:
            self._printer(*out, file=dest, end=end)

    def _printer(self, *out, **kws):
        """generic print function"""
        flush = kws.pop('flush', True)
        fileh = kws.pop('file', self.writer)
        sep = kws.pop('sep', ' ')
        end = kws.pop('sep', '\n')

        print(*out, file=fileh, sep=sep, end=end)
        if flush:
            fileh.flush()

    def on_if(self, node):  # ('test', 'body', 'orelse')
        """regular if-then-else statement"""
        block = node.body
        if not self._run(node.test):
            block = node.orelse
        for tnode in block:
            self._run(tnode)

    def on_ifexp(self, node):  # ('test', 'body', 'orelse')
        """if expressions"""
        expr = node.orelse
        if self._run(node.test):
            expr = node.body
        return self._run(expr)

    def on_while(self, node):  # ('test', 'body', 'orelse')
        """while blocks"""
        while self._run(node.test):
            self._interrupt = None
            for tnode in node.body:
                self._run(tnode)
                if self._interrupt is not None:
                    break
            if isinstance(self._interrupt, ast.Break):
                break
        else:
            for tnode in node.orelse:
                self._run(tnode)
        self._interrupt = None

    def on_for(self, node):  # ('target', 'iter', 'body', 'orelse')
        """for blocks"""
        for val in self._run(node.iter):
            self.node_assign(node.target, val)
            self._interrupt = None
            for tnode in node.body:
                self._run(tnode)
                if self._interrupt is not None:
                    break
            if isinstance(self._interrupt, ast.Break):
                break
        else:
            for tnode in node.orelse:
                self._run(tnode)
        self._interrupt = None

    def on_listcomp(self, node):  # ('elt', 'generators')
        """list comprehension"""
        out = []
        for tnode in node.generators:
            if tnode.__class__ == ast.comprehension:
                for val in self._run(tnode.iter):
                    self.node_assign(tnode.target, val)
                    add = True
                    for cond in tnode.ifs:
                        add = add and self._run(cond)
                    if add:
                        out.append(self._run(node.elt))
        return out

    def on_excepthandler(self, node):  # ('type', 'name', 'body')
        """exception handler..."""
        return self._run(node.type), node.name, node.body

    def on_try(self, node):  # ('body', 'handlers', 'orelse', 'finalbody')
        """try/except/else/finally blocks"""
        no_errors = True
        for tnode in node.body:
            self._run(tnode, with_raise=False)
            no_errors = no_errors and not self.error
            if self.error:
                e_type, e_value, e_tback = self.error[-1].exc_info
                for hnd in node.handlers:
                    htype = None
                    if hnd.type is not None:
                        htype = builtins.get(hnd.type.id, None)
                    if htype is None or isinstance(e_type(), htype):
                        self.error = []
                        if hnd.name is not None:
                            self.node_assign(hnd.name, e_value)
                        for tline in hnd.body:
                            self._run(tline)
                        break
        if no_errors and hasattr(node, 'orelse'):
            for tnode in node.orelse:
                self._run(tnode)

        if hasattr(node, 'finalbody'):
            for tnode in node.finalbody:
                self._run(tnode)

    def on_raise(self, node):  # ('type', 'inst', 'tback')
        """raise statement: note difference for python 2 and 3"""
        if version_info[0] == 3:
            excnode = node.exc
            msgnode = node.cause
        else:
            excnode = node.type
            msgnode = node.inst
        out = self._run(excnode)
        msg = ' '.join(out.args)
        msg2 = self._run(msgnode)
        if msg2 not in (None, 'None'):
            msg = "%s: %s" % (msg, msg2)
        self.raise_exception(None, exc=out.__class__, msg=msg, expr='')

    def on_call(self, node):
        """function execution"""
        #  ('func', 'args', 'keywords', and 'starargs', 'kwargs' in py < 3.5)
        func = self._run(node.func)
        if not hasattr(func, '__call__') and not isinstance(func, type):
            msg = "'%s' is not callable!!" % func
            self.raise_exception(node, exc=TypeError, msg=msg)

        args = [self._run(targ) for targ in node.args]
        starargs = getattr(node, 'starargs', None)
        if starargs is not None:
            args = args + self._run(starargs)

        keywords = {}
        for key in node.keywords:
            if not isinstance(key, ast.keyword):
                msg = "keyword error in function call '%s'" % func
                self.raise_exception(node, msg=msg)
            keywords[key.arg] = self._run(key.value)

        kwargs = getattr(node, 'kwargs', None)
        if kwargs is not None:
            keywords.update(self._run(kwargs))

        # noinspection PyBroadException
        try:
            return func(*args, **keywords)
        except:
            self.raise_exception(node, msg="Error running %s" % func)

    # noinspection PyMethodMayBeStatic
    def on_arg(self, node):  # ('test', 'msg')
        """arg for function definitions"""
        return node.arg

    def on_functiondef(self, node):
        """define procedures"""
        # ('name', 'args', 'body', 'decorator_list')
        if node.decorator_list:
            raise Warning("decorated procedures not supported!")
        kwargs = []

        offset = len(node.args.args) - len(node.args.defaults)
        for idef, defnode in enumerate(node.args.defaults):
            defval = self._run(defnode)
            keyval = self._run(node.args.args[idef + offset])
            kwargs.append((keyval, defval))

        if version_info[0] == 3:
            args = [tnode.arg for tnode in node.args.args[:offset]]
        else:
            args = [tnode.id for tnode in node.args.args[:offset]]

        doc = None
        nb0 = node.body[0]
        if isinstance(nb0, ast.Expr) and isinstance(nb0.value, ast.Str):
            doc = nb0.value.s

        varkws = node.args.kwarg
        vararg = node.args.vararg
        if version_info[0] == 3:
            if isinstance(vararg, ast.arg):
                vararg = vararg.arg
            if isinstance(varkws, ast.arg):
                varkws = varkws.arg

        self.symtable[node.name] = Procedure(node.name, self, doc=doc,
                                             lineno=self.lineno,
                                             body=node.body,
                                             args=args, kwargs=kwargs,
                                             vararg=vararg, varkws=varkws)
        if node.name in self.no_deepcopy:
            self.no_deepcopy.pop(node.name)


class Procedure(object):
    """Procedure: user-defined function for asteval

    This stores the parsed ast nodes as from the
    'functiondef' ast node for later evaluation.
    """

    def __init__(self, name, interp, doc=None, lineno=0,
                 body=None, args=None, kwargs=None,
                 vararg=None, varkws=None):
        self.name = name
        self.__asteval__ = interp
        self.raise_exc = self.__asteval__.raise_exception
        self.__doc__ = doc
        self.body = body
        self.argnames = args
        self.kwargs = kwargs
        self.vararg = vararg
        self.varkws = varkws
        self.lineno = lineno

    def __repr__(self):
        sig = ""
        if self.argnames:
            sig = "%s%s" % (sig, ', '.join(self.argnames))
        if self.vararg is not None:
            sig = "%s, *%s" % (sig, self.vararg)
        if self.kwargs:
            if sig:
                sig = "%s, " % sig
            _kw = ["%s=%s" % (k, v) for k, v in self.kwargs]
            sig = "%s%s" % (sig, ', '.join(_kw))

        if self.varkws is not None:
            sig = "%s, **%s" % (sig, self.varkws)
        sig = "<Procedure %s(%s)>" % (self.name, sig)
        if self.__doc__ is not None:
            sig = "%s\n  %s" % (sig, self.__doc__)
        return sig

    def __call__(self, *args, **kwargs):
        symlocals = {}
        args = list(args)
        n_args = len(args)
        n_names = len(self.argnames)

        # may need to move kwargs to args if names align!
        if (n_args < n_names) and kwargs:
            for name in self.argnames[n_args:]:
                if name in kwargs:
                    args.append(kwargs.pop(name))
            n_args = len(args)
            n_names = len(self.argnames)

        if self.argnames and kwargs is not None:
            msg = "multiple values for keyword argument '%s' in Procedure %s"
            for targ in self.argnames:
                if targ in kwargs:
                    self.raise_exc(None, exc=TypeError,
                                   msg=msg % (targ, self.name),
                                   lineno=self.lineno)

        if n_args != n_names:
            if n_args < n_names:
                msg = 'not enough arguments for Procedure %s()' % self.name
                msg = '%s (expected %i, got %i)' % (msg, n_names, n_args)
                self.raise_exc(None, exc=TypeError, msg=msg)

        for argname in self.argnames:
            symlocals[argname] = args.pop(0)

        try:
            if self.vararg is not None:
                symlocals[self.vararg] = tuple(args)

            for key, val in self.kwargs:
                if key in kwargs:
                    val = kwargs.pop(key)
                symlocals[key] = val

            if self.varkws is not None:
                symlocals[self.varkws] = kwargs

            elif kwargs:
                msg = 'extra keyword arguments for Procedure %s (%s)'
                msg = msg % (self.name, ','.join(list(kwargs.keys())))
                self.raise_exc(None, msg=msg, exc=TypeError,
                               lineno=self.lineno)

        except (ValueError, LookupError, TypeError,
                NameError, AttributeError):
            msg = 'incorrect arguments for Procedure %s' % self.name
            self.raise_exc(None, msg=msg, lineno=self.lineno)

        save_symtable = self.__asteval__.symtable.copy()
        self.__asteval__.symtable.update(symlocals)
        self.__asteval__.retval = None
        retval = None

        # evaluate script of function
        for node in self.body:
            self.__asteval__.run(node, expr='<>', lineno=self.lineno)
            if self.__asteval__.error:
                break
            if self.__asteval__.retval is not None:
                retval = self.__asteval__.retval
                if retval is ReturnedNone:
                    retval = None
                break

        self.__asteval__.symtable = save_symtable
        return retval
