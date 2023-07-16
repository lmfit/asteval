#!/usr/bin/env python
"""
Safe(ish) evaluation of minimal Python code using Python's ast module.

This module provides an Interpreter class that compiles a restricted set of
Python expressions and statements to Python's AST representation, and then
executes that representation using values held in a symbol table.

The symbol table is a simple dictionary, giving a flat namespace.  This comes
pre-loaded with many functions from Python's builtin and math module.  If numpy
is installed, many numpy functions are also included.  Additional symbols can
be added when an Interpreter is created, but the user of that interpreter will
not be able to import additional modules.

Expressions, including loops, conditionals, and function definitions can be
compiled into ast node and then evaluated later, using the current values
in the symbol table.

The result is a restricted, simplified version of Python meant for numerical
calculations that is somewhat safer than 'eval' because many unsafe operations
(such as 'eval') are simply not allowed, and others (such as 'import') are
disabled by default, but can be explicitly enabled.

Many parts of Python syntax are supported, including:
     for loops, while loops, if-then-elif-else conditionals, with,
     try-except-finally
     function definitions with def
     advanced slicing:    a[::-1], array[-3:, :, ::2]
     if-expressions:      out = one_thing if TEST else other
     list, dict, and set comprehension

The following Python syntax elements are not supported:
     Import, Exec, Lambda, Class, Global, Generators,
     Yield, Decorators

In addition, while many builtin functions are supported, several builtin
functions that are considered unsafe are missing ('eval', 'exec', and
'getattr' for example) are missing.
"""
import ast
import sys
import copy
import inspect
import time
from sys import exc_info, stderr, stdout

from .astutils import (HAS_NUMPY, UNSAFE_ATTRS, ExceptionHolder, ReturnedNone, Empty,
                       make_symbol_table, numpy, op2func, valid_symbol_name,
                       Procedure)

ALL_NODES = ['arg', 'assert', 'assign', 'attribute', 'augassign', 'binop',
             'boolop', 'break', 'bytes', 'call', 'compare', 'constant',
             'continue', 'delete', 'dict', 'dictcomp', 'ellipsis',
             'excepthandler', 'expr', 'extslice', 'for', 'functiondef', 'if',
             'ifexp', 'import', 'importfrom', 'index', 'interrupt', 'list',
             'listcomp', 'module', 'name', 'nameconstant', 'num', 'pass',
             'raise', 'repr', 'return', 'set', 'setcomp', 'slice', 'str',
             'subscript', 'try', 'tuple', 'unaryop', 'while', 'with',
             'formattedvalue', 'joinedstr']


MINIMAL_CONFIG = {'import': False, 'importfrom': False}
DEFAULT_CONFIG = {'import': False, 'importfrom': False}

for _tnode in ('assert', 'augassign', 'delete', 'if', 'ifexp', 'for',
             'formattedvalue', 'functiondef', 'print', 'raise', 'listcomp',
             'dictcomp', 'setcomp', 'try', 'while', 'with'):
    MINIMAL_CONFIG[_tnode] = False
    DEFAULT_CONFIG[_tnode] = True

class Interpreter:
    """create an asteval Interpreter: a restricted, simplified interpreter
    of mathematical expressions using Python syntax.

    Parameters
    ----------
    symtable : dict or `None`
        dictionary or SymbolTable to use as symbol table (if `None`, one will be created).
    nested_symtable : bool, optional
        whether to use a new-style nested symbol table instead of a plain dict [False]
    user_symbols : dict or `None`
        dictionary of user-defined symbols to add to symbol table.
    writer : file-like or `None`
        callable file-like object where standard output will be sent.
    err_writer : file-like or `None`
        callable file-like object where standard error will be sent.
    use_numpy : bool
        whether to use functions from numpy.
    max_statement_length : int
        maximum length of expression allowed [50,000 characters]
    readonly_symbols : iterable or `None`
        symbols that the user can not assign to
    builtins_readonly : bool
        whether to blacklist all symbols that are in the initial symtable
    minimal : bool
        create a minimal interpreter: disable many nodes (see Note 1).
    config : dict
        dictionay listing which nodes to support (see note 2))

    Notes
    -----
    1. setting `minimal=True` is equivalent to setting a config with the following
       nodes disabled: ('import', 'importfrom', 'if', 'for', 'while', 'try', 'with',
       'functiondef', 'ifexp', 'listcomp', 'dictcomp', 'setcomp', 'augassign',
       'assert', 'delete', 'raise', 'print')
    2. by default 'import' and 'importfrom' are disabled, though they can be enabled.
    """
    def __init__(self, symtable=None, nested_symtable=False,
                 user_symbols=None, writer=None, err_writer=None,
                 use_numpy=True, max_statement_length=50000,
                 minimal=False, readonly_symbols=None,
                 builtins_readonly=False, config=None, **kws):

        self.config = copy.copy(MINIMAL_CONFIG if minimal else DEFAULT_CONFIG)
        if config is not None:
            self.config.update(config)
        self.config['nested_symtable'] = nested_symtable

        if user_symbols is None:
            user_symbols = {}
            if 'usersyms' in kws:
                user_symbols = kws.pop('usersyms') # back compat, changed July, 2023, v 0.9.4

        if len(kws) > 0:
            for key, val in kws.items():
                if key.startswith('no_'):
                    node = key[3:]
                    if node in ALL_NODES:
                        self.config[node] = not val
                elif key.startswith('with_'):
                    node = key[5:]
                    if node in ALL_NODES:
                        self.config[node] = val

        self.writer = writer or stdout
        self.err_writer = err_writer or stderr
        self.max_statement_length = max(1, min(1.e8, max_statement_length))

        self.use_numpy = HAS_NUMPY and use_numpy
        if symtable is None:
            symtable = make_symbol_table(nested=nested_symtable,
                                         use_numpy=self.use_numpy, **user_symbols)

        symtable['print'] = self._printer
        self.symtable = symtable
        self._interrupt = None
        self.error = []
        self.error_msg = None
        self.expr = None
        self.retval = None
        self._calldepth = 0
        self.lineno = 0
        self.start_time = time.time()

        self.node_handlers = {}
        for node in ALL_NODES:
            handler = self.unimplemented
            if self.config.get(node, True):
                handler = getattr(self, f"on_{node}", self.unimplemented)
            self.node_handlers[node] = handler

        # to rationalize try/except try/finally
        if 'try' in self.node_handlers:
            self.node_handlers['tryexcept'] = self.node_handlers['try']
            self.node_handlers['tryfinally'] = self.node_handlers['try']

        if readonly_symbols is None:
            self.readonly_symbols = set()
        else:
            self.readonly_symbols = set(readonly_symbols)

        if builtins_readonly:
            self.readonly_symbols |= set(self.symtable)

        self.no_deepcopy = [key for key, val in symtable.items()
                            if (callable(val)
                                or inspect.ismodule(val)
                                or 'numpy.lib.index_tricks' in repr(type(val)))]

    def remove_nodehandler(self, node):
        """remove support for a node
        returns current node handler, so that it
        might be re-added with add_nodehandler()
        """
        out = None
        if node in self.node_handlers:
            out = self.node_handlers.pop(node)
        return out

    def set_nodehandler(self, node, handler=None):
        """set node handler or use current built-in default"""
        if handler is None:
            handler = getattr(self, f"on_{node}", self.unimplemented)
        self.node_handlers[node] = handler
        return handler

    def user_defined_symbols(self):
        """Return a set of symbols that have been added to symtable after
        construction.

        I.e., the symbols from self.symtable that are not in
        self.no_deepcopy.

        Returns
        -------
        unique_symbols : set
            symbols in symtable that are not in self.no_deepcopy

        """
        sym_in_current = set(self.symtable.keys())
        sym_from_construction = set(self.no_deepcopy)
        unique_symbols = sym_in_current.difference(sym_from_construction)
        return unique_symbols

    def unimplemented(self, node):
        """Unimplemented nodes."""
        msg = f"{node.__class__.__name__} not supported"
        self.raise_exception(node, exc=NotImplementedError, msg=msg)

    def raise_exception(self, node, exc=None, msg='', expr=None,
                        lineno=None):
        """Add an exception."""
        if self.error is None:
            self.error = []
        if expr is None:
            expr = self.expr
        if len(self.error) > 0 and not isinstance(node, ast.Module):
            msg = f'{msg!s}'
        err = ExceptionHolder(node, exc=exc, msg=msg, expr=expr, lineno=lineno)
        self._interrupt = ast.Raise()
        self.error.append(err)
        if self.error_msg is None:
            self.error_msg = (' '.join([msg, f"at expr='{self.expr}'"])).strip()
        elif len(msg) > 0:
            self.error_msg = msg
        if exc is None:
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
        if len(text) > self.max_statement_length:
            msg = f'length of text exceeds {self.max_statement_length:d} characters'
            self.raise_exception(None, exc=RuntimeError, expr=msg)
        self.expr = text
        try:
            out = ast.parse(text)
        except SyntaxError:
            self.raise_exception(None, exc=SyntaxError, expr=text)
        except:
            self.raise_exception(None, exc=RuntimeError, expr=text)

        return out

    def run(self, node, expr=None, lineno=None, with_raise=True):
        """Execute parsed Ast representation for an expression."""
        # Note: keep the 'node is None' test: internal code here may run
        #    run(None) and expect a None in return.
        out = None
        if len(self.error) > 0:
            return out
        if self.retval is not None:
            return self.retval
        if isinstance(self._interrupt, (ast.Break, ast.Continue)):
            return self._interrupt
        if node is None:
            return out
        if isinstance(node, str):
            node = self.parse(node)
        if lineno is not None:
            self.lineno = lineno
        if expr is not None:
            self.expr = expr

        # get handler for this node:
        #   on_xxx with handle nodes of type 'xxx', etc
        try:
            handler = self.node_handlers[node.__class__.__name__.lower()]
        except KeyError:
            self.raise_exception(None, exc=NotImplementedError, expr=expr)

        # run the handler:  this will likely generate
        # recursive calls into this run method.
        try:
            ret = handler(node)
            if isinstance(ret, enumerate):
                ret = list(ret)
            return ret
        except:
            if with_raise:
                if len(self.error) == 0:
                    # Unhandled exception that didn't use raise_exception
                    self.raise_exception(node, expr=expr)
                raise
        return None

    def __call__(self, expr, **kw):
        """Call class instance as function."""
        return self.eval(expr, **kw)

    def eval(self, expr, lineno=0, show_errors=True, raise_errors=False):
        """Evaluate a single statement."""
        self.lineno = lineno
        self.error = []
        self.start_time = time.time()
        if isinstance(expr, str):
            try:
                node = self.parse(expr)
            except Exception:
                errmsg = exc_info()[1]
                if len(self.error) > 0:
                    errmsg = "\n".join(self.error[0].get_error())
                if raise_errors:
                    try:
                        exc = self.error[0].exc
                    except Exception:
                        exc = RuntimeError
                    raise exc(errmsg)
                if show_errors:
                    print(errmsg, file=self.err_writer)
                return None
        else:
            node = expr
        try:
            return self.run(node, expr=expr, lineno=lineno)
        except:
            errmsg = exc_info()[1]
            if len(self.error) > 0:
                errmsg = "\n".join(self.error[0].get_error())
            if raise_errors:
                try:
                    exc = self.error[0].exc
                except Exception:
                    exc = RuntimeError
                raise exc(errmsg)
            if show_errors:
                print(errmsg, file=self.err_writer)
        return None

    @staticmethod
    def dump(node, **kw):
        """Simple ast dumper."""
        return ast.dump(node, **kw)

    # handlers for ast components
    def on_expr(self, node):
        """Expression."""
        return self.run(node.value)  # ('value',)

    # imports
    def on_import(self, node):    # ('names',)
        "simple import"
        for tnode in node.names:
            self.import_module(tnode.name, tnode.asname)

    def on_importfrom(self, node):    # ('module', 'names', 'level')
        "import/from"
        fromlist, asname = [], []
        for tnode in node.names:
            fromlist.append(tnode.name)
            asname.append(tnode.asname)
        self.import_module(node.module, asname, fromlist=fromlist)

    def import_module(self, name, asname, fromlist=None):
        """import a python module, installing it into the symbol table.
        options:
          name       name of module to import 'foo' in 'import foo'
          asname     alias for imported name(s)
                          'bar' in 'import foo as bar'
                       or
                          ['s','t'] in 'from foo import x as s, y as t'
          fromlist   list of symbols to import with 'from-import'
                         ['x','y'] in 'from foo import x, y'
        """
        # find module in sys.modules or import to it
        if name in sys.modules:
            thismod = sys.modules[name]
        else:
            try:
                __import__(name)
                thismod = sys.modules[name]
            except:
                self.raise_exception(None, exc=ImportError, msg='Import Error')

        if fromlist is None:
            if asname is not None:
                self.symtable[asname] = sys.modules[name]
            else:
                mparts = []
                parts = name.split('.')
                while len(parts) > 0:
                    mparts.append(parts.pop(0))
                    modname = '.'.join(mparts)
                    inname = name if (len(parts) == 0) else modname
                    self.symtable[inname] = sys.modules[modname]
        else: #  import-from construct
            if asname is None:
                asname = [None]*len(fromlist)
            for sym, alias in zip(fromlist, asname):
                if alias is None:
                    alias = sym
                self.symtable[alias] = getattr(thismod, sym)

    def on_index(self, node):
        """Index."""
        return self.run(node.value)  # ('value',)

    def on_return(self, node):  # ('value',)
        """Return statement: look for None, return special sentinel."""
        if self._calldepth == 0:
            raise SyntaxError('cannot return at top level')
        self.retval = self.run(node.value)
        if self.retval is None:
            self.retval = ReturnedNone

    def on_repr(self, node):
        """Repr."""
        return repr(self.run(node.value))  # ('value',)

    def on_module(self, node):    # ():('body',)
        """Module def."""
        out = None
        for tnode in node.body:
            out = self.run(tnode)
        return out

    def on_expression(self, node):
        "basic expression"
        return self.on_module(node)  # ():('body',)

    def on_pass(self, node):
        """Pass statement."""
        return None  # ()

    def on_ellipsis(self, node):
        """Ellipses.  deprecated in 3.8"""
        return Ellipsis

    # for break and continue: set the instance variable _interrupt
    def on_interrupt(self, node):    # ()
        """Interrupt handler."""
        self._interrupt = node
        return node

    def on_break(self, node):
        """Break."""
        return self.on_interrupt(node)

    def on_continue(self, node):
        """Continue."""
        return self.on_interrupt(node)

    def on_assert(self, node):    # ('test', 'msg')
        """Assert statement."""
        if not self.run(node.test):
            #depraction warning: will become:
            #  msg = node.msg.value if node.msg else ""
            msg = node.msg.s if node.msg else ""
            self.raise_exception(node, exc=AssertionError, msg=msg)
        return True

    def on_list(self, node):    # ('elt', 'ctx')
        """List."""
        return [self.run(e) for e in node.elts]

    def on_tuple(self, node):    # ('elts', 'ctx')
        """Tuple."""
        return tuple(self.on_list(node))

    def on_set(self, node):    # ('elts')
        """Set."""
        return set([self.run(k) for k in node.elts])

    def on_dict(self, node):    # ('keys', 'values')
        """Dictionary."""
        return {self.run(k): self.run(v) for k, v in
                zip(node.keys, node.values)}

    def on_constant(self, node):   # ('value', 'kind')
        """Return constant value."""
        return node.value

    def on_num(self, node):   # ('n',)
        """Return number.  deprecated in 3.8"""
        return node.n

    def on_str(self, node):   # ('s',)
        """Return string.  deprecated in 3.8"""
        return node.s

    def on_bytes(self, node):
        """return bytes.  deprecated in 3.8"""
        return node.s  # ('s',)

    def on_joinedstr(self, node):  # ('values',)
        "join strings, used in f-strings"
        return ''.join([self.run(k) for k in node.values])

    def on_formattedvalue(self, node): # ('value', 'conversion', 'format_spec')
        "formatting used in f-strings"
        val = self.run(node.value)
        fstring_converters = {115: str, 114: repr, 97: ascii}
        if node.conversion in fstring_converters:
            val = fstring_converters[node.conversion](val)
        fmt = '{0}'
        if node.format_spec is not None:
            fmt = f'{{0:{self.run(node.format_spec)}}}'
        return fmt.format(val)

    def _getsym(self, node):
        val = self.symtable.get(node.id, ReturnedNone)
        if isinstance(val, Empty):
            msg = f"name '{node.id}' is not defined"
            self.raise_exception(node, exc=NameError, msg=msg)
        return val

    def on_name(self, node):    # ('id', 'ctx')
        """Name node."""
        ctx = node.ctx.__class__
        if ctx in (ast.Param, ast.Del):
            return str(node.id)
        return self._getsym(node)

    def on_nameconstant(self, node):
        """True, False, or None  deprecated in 3.8"""
        return node.value

    def node_assign(self, node, val):
        """Assign a value (not the node.value object) to a node.

        This is used by on_assign, but also by for, list comprehension,
        etc.

        """
        if node.__class__ == ast.Name:
            if (not valid_symbol_name(node.id) or
                    node.id in self.readonly_symbols):
                errmsg = f"invalid symbol name (reserved word?) {node.id}"
                self.raise_exception(node, exc=NameError, msg=errmsg)
            self.symtable[node.id] = val
            if node.id in self.no_deepcopy:
                self.no_deepcopy.remove(node.id)

        elif node.__class__ == ast.Attribute:
            if node.ctx.__class__ == ast.Load:
                msg = f"cannot assign to attribute {node.attr}"
                self.raise_exception(node, exc=AttributeError, msg=msg)

            setattr(self.run(node.value), node.attr, val)

        elif node.__class__ == ast.Subscript:
            self.run(node.value)[self.run(node.slice)] = val

        elif node.__class__ in (ast.Tuple, ast.List):
            if len(val) == len(node.elts):
                for telem, tval in zip(node.elts, val):
                    self.node_assign(telem, tval)
            else:
                raise ValueError('too many values to unpack')

    def on_attribute(self, node):    # ('value', 'attr', 'ctx')
        """Extract attribute."""
        ctx = node.ctx.__class__
        if ctx == ast.Store:
            msg = "attribute for storage: shouldn't be here!"
            self.raise_exception(node, exc=RuntimeError, msg=msg)

        sym = self.run(node.value)
        if ctx == ast.Del:
            return delattr(sym, node.attr)

        # ctx is ast.Load
        if not (node.attr in UNSAFE_ATTRS or
                (node.attr.startswith('__') and
                 node.attr.endswith('__'))):
            try:
                return getattr(sym, node.attr)
            except AttributeError:
                pass

        # AttributeError or accessed unsafe attribute
        msg = f"no attribute '{node.attr}' for {self.run(node.value)}"
        self.raise_exception(node, exc=AttributeError, msg=msg)
        return None

    def on_assign(self, node):    # ('targets', 'value')
        """Simple assignment."""
        val = self.run(node.value)
        for tnode in node.targets:
            self.node_assign(tnode, val)

    def on_augassign(self, node):    # ('target', 'op', 'value')
        """Augmented assign."""
        return self.on_assign(ast.Assign(targets=[node.target],
                                         value=ast.BinOp(left=node.target,
                                                         op=node.op,
                                                         right=node.value)))

    def on_slice(self, node):    # ():('lower', 'upper', 'step')
        """Simple slice."""
        return slice(self.run(node.lower),
                     self.run(node.upper),
                     self.run(node.step))

    def on_extslice(self, node):    # ():('dims',)
        """Extended slice."""
        return tuple([self.run(tnode) for tnode in node.dims])

    def on_subscript(self, node):    # ('value', 'slice', 'ctx')
        """Subscript handling -- one of the tricky parts."""
        val = self.run(node.value)
        nslice = self.run(node.slice)
        ctx = node.ctx.__class__
        if ctx in (ast.Load, ast.Store):
            return val[nslice]
        msg = "subscript with unknown context"
        self.raise_exception(node, msg=msg)
        return None

    def on_delete(self, node):    # ('targets',)
        """Delete statement."""
        for tnode in node.targets:
            if tnode.ctx.__class__ != ast.Del:
                break
            children = []
            while tnode.__class__ == ast.Attribute:
                children.append(tnode.attr)
                tnode = tnode.value
            if (tnode.__class__ == ast.Name and
                    tnode.id not in self.readonly_symbols):
                children.append(tnode.id)
                children.reverse()
                self.symtable.pop('.'.join(children))
            else:
                msg = "could not delete symbol"
                self.raise_exception(node, msg=msg)

    def on_unaryop(self, node):    # ('op', 'operand')
        """Unary operator."""
        return op2func(node.op)(self.run(node.operand))

    def on_binop(self, node):    # ('left', 'op', 'right')
        """Binary operator."""
        return op2func(node.op)(self.run(node.left),
                                self.run(node.right))

    def on_boolop(self, node):    # ('op', 'values')
        """Boolean operator."""
        val = self.run(node.values[0])
        is_and = ast.And == node.op.__class__
        if (is_and and val) or (not is_and and not val):
            for nodeval in node.values[1:]:
                val = op2func(node.op)(val, self.run(nodeval))
                if (is_and and not val) or (not is_and and val):
                    break
        return val

    def on_compare(self, node):  # ('left', 'ops', 'comparators')
        """comparison operators, including chained comparisons (a<b<c)"""
        lval = self.run(node.left)
        results = []
        for oper, rnode in zip(node.ops, node.comparators):
            rval = self.run(rnode)
            ret = op2func(oper)(lval, rval)
            results.append(ret)
            if ((self.use_numpy and not isinstance(ret, numpy.ndarray)) and
                    not ret):
                break
            lval = rval
        if len(results) == 1:
            return results[0]
        out = True
        for ret in results:
            out = out and ret
        return out

    def _printer(self, *out, **kws):
        """Generic print function."""
        if self.config.get('print', True):
            flush = kws.pop('flush', True)
            fileh = kws.pop('file', self.writer)
            sep = kws.pop('sep', ' ')
            end = kws.pop('sep', '\n')
            print(*out, file=fileh, sep=sep, end=end)
            if flush:
                fileh.flush()

    def on_if(self, node):    # ('test', 'body', 'orelse')
        """Regular if-then-else statement."""
        block = node.body
        if not self.run(node.test):
            block = node.orelse
        for tnode in block:
            self.run(tnode)

    def on_ifexp(self, node):    # ('test', 'body', 'orelse')
        """If expressions."""
        expr = node.orelse
        if self.run(node.test):
            expr = node.body
        return self.run(expr)

    def on_while(self, node):    # ('test', 'body', 'orelse')
        """While blocks."""
        while self.run(node.test):
            self._interrupt = None
            for tnode in node.body:
                self.run(tnode)
                if self._interrupt is not None:
                    break
            if isinstance(self._interrupt, ast.Break):
                break
        else:
            for tnode in node.orelse:
                self.run(tnode)
        self._interrupt = None

    def on_for(self, node):    # ('target', 'iter', 'body', 'orelse')
        """For blocks."""
        for val in self.run(node.iter):
            self.node_assign(node.target, val)
            self._interrupt = None
            for tnode in node.body:
                self.run(tnode)
                if self._interrupt is not None:
                    break
            if isinstance(self._interrupt, ast.Break):
                break
        else:
            for tnode in node.orelse:
                self.run(tnode)
        self._interrupt = None

    def on_with(self, node):    # ('items', 'body', 'type_comment')
        """with blocks."""
        contexts = []
        for item in node.items:
            ctx = self.run(item.context_expr)
            contexts.append(ctx)
            if hasattr(ctx, '__enter__'):
                result = ctx.__enter__()
                if item.optional_vars is not None:
                    self.node_assign(item.optional_vars, result)
            else:
                msg = "object does not support the context manager protocol"
                raise TypeError(f"'{type(ctx)}' {msg}")
        for bnode in node.body:
            self.run(bnode)
            if self._interrupt is not None:
                break

        for ctx in contexts:
            if hasattr(ctx, '__exit__'):
                ctx.__exit__()


    def comprehension_data(self, node):      # ('elt', 'generators')
        "data for comprehensions"
        mylocals = {}
        saved_syms = {}

        for tnode in node.generators:
            if tnode.__class__ == ast.comprehension:
                if tnode.target.__class__ == ast.Name:
                    if (not valid_symbol_name(tnode.target.id) or
                        tnode.target.id in self.readonly_symbols):
                        errmsg = f"invalid symbol name (reserved word?) {tnode.target.id}"
                        self.raise_exception(tnode.target, exc=NameError, msg=errmsg)
                    mylocals[tnode.target.id] = []
                    if tnode.target.id in self.symtable:
                        saved_syms[tnode.target.id] = copy.deepcopy(self._getsym(tnode.target))

                elif tnode.target.__class__ == ast.Tuple:
                    target = []
                    for tval in tnode.target.elts:
                        mylocals[tval.id] = []
                        if tval.id in self.symtable:
                            saved_syms[tval.id] = copy.deepcopy(self._getsym(tval))

        for tnode in node.generators:
            if tnode.__class__ == ast.comprehension:
                ttype = 'name'
                if tnode.target.__class__ == ast.Name:
                    if (not valid_symbol_name(tnode.target.id) or
                        tnode.target.id in self.readonly_symbols):
                        errmsg = f"invalid symbol name (reserved word?) {tnode.target.id}"
                        self.raise_exception(tnode.target, exc=NameError, msg=errmsg)
                    ttype, target = 'name', tnode.target.id
                elif tnode.target.__class__ == ast.Tuple:
                    ttype = 'tuple'
                    target =tuple([tval.id for tval in tnode.target.elts])

                for val in self.run(tnode.iter):
                    if ttype == 'name':
                        self.symtable[target] = val
                    else:
                        for telem, tval in zip(target, val):
                            self.symtable[target] = val

                    add = True
                    for cond in tnode.ifs:
                        add = add and self.run(cond)
                    if add:
                        if ttype == 'name':
                            mylocals[target].append(val)
                        else:
                            for telem, tval in zip(target, val):
                                mylocals[telem].append(tval)
        return mylocals, saved_syms

    def on_listcomp(self, node):
        """List comprehension"""
        mylocals, saved_syms = self.comprehension_data(node)

        names = list(mylocals.keys())
        data = list(mylocals.values())
        def listcomp_recurse(out, i, names, data):
            if i == len(names):
                out.append(self.run(node.elt))
                return

            for val in data[i]:
                self.symtable[names[i]] = val
                listcomp_recurse(out, i+1, names, data)

        out = []
        listcomp_recurse(out, 0, names, data)
        for name, val in saved_syms.items():
            self.symtable[name] = val
        return out

    def on_setcomp(self, node):
        """Set comprehension"""
        return set(self.on_listcomp(node))

    def on_dictcomp(self, node):
        """Dictionary comprehension"""
        mylocals, saved_syms = self.comprehension_data(node)

        names = list(mylocals.keys())
        data = list(mylocals.values())

        def dictcomp_recurse(out, i, names, data):
            if i == len(names):
                out[self.run(node.key)] = self.run(node.value)
                return

            for val in data[i]:
                self.symtable[names[i]] = val
                dictcomp_recurse(out, i+1, names, data)

        out = {}
        dictcomp_recurse(out, 0, names, data)
        for name, val in saved_syms.items():
            self.symtable[name] = val
        return out


    def on_excepthandler(self, node):  # ('type', 'name', 'body')
        """Exception handler..."""
        return (self.run(node.type), node.name, node.body)

    def on_try(self, node):    # ('body', 'handlers', 'orelse', 'finalbody')
        """Try/except/else/finally blocks."""
        no_errors = True
        for tnode in node.body:
            self.run(tnode, with_raise=False)
            no_errors = no_errors and len(self.error) == 0
            if len(self.error) > 0:
                e_type, e_value, _ = self.error[-1].exc_info
                for hnd in node.handlers:
                    htype = None
                    if hnd.type is not None:
                        htype = __builtins__.get(hnd.type.id, None)
                    if htype is None or isinstance(e_type(), htype):
                        self.error = []
                        if hnd.name is not None:
                            self.node_assign(hnd.name, e_value)
                        for tline in hnd.body:
                            self.run(tline)
                        break
                break
        if no_errors and hasattr(node, 'orelse'):
            for tnode in node.orelse:
                self.run(tnode)

        if hasattr(node, 'finalbody'):
            for tnode in node.finalbody:
                self.run(tnode)

    def on_raise(self, node):    # ('type', 'inst', 'tback')
        """Raise statement: note difference for python 2 and 3."""
        excnode = node.exc
        msgnode = node.cause
        out = self.run(excnode)
        msg = ' '.join(out.args)
        msg2 = self.run(msgnode)
        if msg2 not in (None, 'None'):
            msg = f"{msg:s}: {msg2:s}"
        self.raise_exception(None, exc=out.__class__, msg=msg, expr='')

    def on_call(self, node):
        """Function execution."""
        func = self.run(node.func)
        if not hasattr(func, '__call__') and not isinstance(func, type):
            msg = f"'{func}' is not callable!!"
            self.raise_exception(node, exc=TypeError, msg=msg)
        args = [self.run(targ) for targ in node.args]
        starargs = getattr(node, 'starargs', None)
        if starargs is not None:
            args = args + self.run(starargs)

        keywords = {}
        if func == print:
            keywords['file'] = self.writer
        for key in node.keywords:
            if not isinstance(key, ast.keyword):
                msg = f"keyword error in function call '{func}'"
                self.raise_exception(node, msg=msg)
            if key.arg is None:
                keywords.update(self.run(key.value))
            elif key.arg in keywords:
                self.raise_exception(node, exc=SyntaxError,
                                     msg=f"keyword argument repeated: {key.arg}")
            else:
                keywords[key.arg] = self.run(key.value)

        kwargs = getattr(node, 'kwargs', None)
        if kwargs is not None:
            keywords.update(self.run(kwargs))

        if isinstance(func, Procedure):
            self._calldepth += 1
        try:
            out = func(*args, **keywords)
        except Exception as ex:
            out = None
            func_name = getattr(func, '__name__', str(func))
            msg = f"Error running function '{func_name}' with args '{args}'"
            msg = f"{msg} and kwargs {keywords}: {ex}"
            self.raise_exception(node, msg=msg)
        finally:
            if isinstance(func, Procedure):
                self._calldepth -= 1
        return out

    def on_arg(self, node):    # ('test', 'msg')
        """Arg for function definitions."""
        return node.arg

    def on_functiondef(self, node):
        """Define procedures."""
        # ('name', 'args', 'body', 'decorator_list')
        if node.decorator_list:
            raise Warning("decorated procedures not supported!")
        kwargs = []

        if (not valid_symbol_name(node.name) or
                node.name in self.readonly_symbols):
            errmsg = f"invalid function name (reserved word?) {node.name}"
            self.raise_exception(node, exc=NameError, msg=errmsg)

        offset = len(node.args.args) - len(node.args.defaults)
        for idef, defnode in enumerate(node.args.defaults):
            defval = self.run(defnode)
            keyval = self.run(node.args.args[idef+offset])
            kwargs.append((keyval, defval))

        args = [tnode.arg for tnode in node.args.args[:offset]]
        doc = None
        nb0 = node.body[0]
        # deprecation warning: will become
        # if isinstance(nb0, ast.Expr) and isinstance(nb0.value, ast.Constant):
        if isinstance(nb0, ast.Expr) and isinstance(nb0.value, ast.Str):
            # deprecation warning: will become
            # doc = nb0.value
            doc = nb0.value.s
        varkws = node.args.kwarg
        vararg = node.args.vararg
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
            self.no_deepcopy.remove(node.name)
