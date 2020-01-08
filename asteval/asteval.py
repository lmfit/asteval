# coding=utf-8
"""
Safe(ish) evaluator of python scripts, using ast module.

"""

from __future__ import division, print_function

import ast
import math
from sys import stdout
from time import time

from .astutils import (FROM_PY, FROM_MATH, UNSAFE_ATTRS,LOCALFUNCS, op2func, MAX_EXEC_TIME,
                       ReturnedNone, valid_symbol_name, MAX_CYCLES, get_class_name, NoReturn, Empty, Return)
from .frame import Frame
from .function import Function
from .module import Module

builtins = __builtins__
if not isinstance(builtins, dict):
    builtins = builtins.__dict__


# pylint: disable=too-many-lines


class Interpreter:  # pylint: disable=too-many-instance-attributes, too-many-public-methods
    """
  This module compiles expressions and statements to AST representation,
  using python's ast module, and then executes the AST representation.

  This version of asteval has sep. frames of execution for builtins,
  globals, and funcs and supports hooking by a debugger. It also allows
  limited importing of "modules" into the global namespace using a modified
  `import` statement.

  The result is a restricted, simplified version of Python that is
  somewhat safer than 'eval' because some operations (such as 'exec' and 'eval')
  are simply not allowed.

  Many parts of Python syntax are supported, including:
     for loops, while loops, if-then-elif-else conditionals
     try-except (including 'finally')
     function definitions with def
     advanced slicing:    a[::-1], array[-3:, :, ::2]
     if-expressions:      out = one_thing if TEST else other
     list comprehension   out = [sqrt(i) for i in values]
     dict comprehensions

  The following Python syntax elements are not supported:
      Import*, Exec, Lambda, Class, Global**, Generators,
      Yield, Yield From, Decorators, NonLocal**, Async, Await,
      Generator Comprehensions, Raise From

      * modified from standard Python.
      ** planned to be supported in future.

  In addition, while many builtin functions are supported, several
  builtin functions are missing ('eval', 'exec', and 'getattr' for
  example) that can be considered unsafe.

  """

    supported_nodes = ('arg', 'assert', 'assign', 'attribute', 'augassign',
                       'binop', 'boolop', 'break', 'call', 'compare',
                       'continue', 'delete', 'dict', 'dictcomp', 'ellipsis',
                       'excepthandler', 'expr', 'extslice', 'for',
                       'functiondef', 'if', 'ifexp', 'index', 'interrupt',
                       'list', 'listcomp', 'module', 'name', 'nameconstant',
                       'num', 'pass', 'raise', 'repr', 'return',  # 'print'
                       'set', 'slice', 'starred', 'str', 'subscript', 'try', 'tuple',
                       'unaryop', 'while',
                       'import',      # used to support importing from other presets
                       'importfrom',  #  NOOP
                      )

    def __init__(self, filename='', writer=None, globals_=None, import_hook=None, max_time=MAX_EXEC_TIME,
                 max_cycles=MAX_CYCLES, truncate_traces=False):
        self.writer = writer or stdout
        self.filename = filename
        self.start = 0
        self.cycles = 0
        self.max_time = max_time
        self.max_cycles = max_cycles
        self.import_hook = import_hook
        self.ui_trace_enabled = True
        self.ui_trace = []
        self.trace = None   # à la sys.settrace()
        self._interrupt = None
        self.error = None
        self.expr = None
        self.prev_lineno = 0
        self.globals_ = globals_
        self.modules = {}
        self.mod_stack = []
        self.last_func = None
        self.prev_mod = None
        self.truncate_traces = truncate_traces  # False or int. for max length before truncation

        self.builtins = {}
        for sym in FROM_PY:
            if sym in builtins:
                self.builtins[sym] = builtins[sym]

        for symname, obj in LOCALFUNCS.items():
            self.builtins[symname] = obj

        for sym in FROM_MATH:
            if hasattr(math, sym):
                self.builtins[sym] = getattr(math, sym)

        self.builtins['print'] = self.print_
        self.builtins['vars'] = self.vars_
        self.mod_stack.append('__main__')
        self.add_module('__main__', filename, extras={'settrace': self.set_trace})
        self.node_handlers = dict(((node, getattr(self, "on_%s" % node)) for node in self.supported_nodes))

        # to rationalize try/except try/finally for Python2.6 through Python3.3
        self.node_handlers['tryexcept'] = self.node_handlers['try']
        self.node_handlers['tryfinally'] = self.node_handlers['try']

    def truncate(self, s):
        if self.truncate_traces and isinstance(s, str) and len(s) >= self.truncate_traces:
            return "{}...[truncated]".format(s[:self.truncate_traces])
        return s

    def code_wrap(self, s, lang=''):
        s = self.quote(s)
        multiline = '\n' in s
        ticks = '```' if multiline else '`'
        newlines = '\n' if multiline else ''
        lang = lang if multiline else ''
        return ''.join([newlines, ticks, lang, newlines, s, newlines, ticks, newlines])

    def quote(self, s):
        if isinstance(s, str):
            return "'{}'".format(self.truncate(s))
        return self.truncate(str(s))

    def add_module(self, name, filename, extras=None):
        mod = Module(name, self, filename)
        builtin_frame = Frame('Builtins', self.builtins)
        if extras is not None and isinstance(extras, dict):
            for k, v in extras.items():
                builtin_frame.set_symbol(k, v)
        mod.push_frame(builtin_frame)
        mod.push_frame(Frame('Globals', self.globals_, filename=filename))
        self.modules[name] = mod
        return mod

    def get_main_module(self):
        return self.modules['main']

    def get_module(self, name):
        try:
            return self.modules[name]
        except KeyError:
            return

    def get_current_module(self):
        return self.modules[self.mod_stack[-1]]

    def enter_module(self, name):
        self.mod_stack.append(name)

    def leave_module(self):
        self.mod_stack.pop()

    def push_frame(self, frame):
        self.get_current_module().frames.append(frame)

    def pop_frame(self):
        return self.get_current_module().frames.pop()

    def get_current_frame(self):
        return self.get_current_module().frames[-1]

    def find_frame(self, name):
        """
        Find the frame (if any) where the symbol is defined.
        :param name: Symbol name
        :return:  frame if found, None otherwise
        """
        for frame in reversed(self.get_current_module().frames):
            if frame.is_symbol(name):
                return frame

    def get_global_frame(self):
        return self.get_current_module().frames[1]

    def set_symbol(self, name, val):
        return self.get_current_frame().set_symbol(name, val)

    def set_trace(self, func):
        self.trace = func

    def get_trace(self):
        return self.trace

    def set_ui_trace(self, on_off):
        self.ui_trace_enabled = on_off

    def ui_tracer(self, s):
        if self.ui_trace_enabled:
            self.ui_trace.append("{}:{}".format(self.get_current_frame().get_filename() or '__main__', s))

    def get_ui_trace(self):
        return self.ui_trace

    def clear_ui_trace(self):
        self.ui_trace.clear()

    def get_errors(self):
        return self.error

    def add_function(self, func):
        if callable(func) and hasattr(func, '__name__'):
            self.set_symbol(func.__name__, func)

    def unimplemented(self, node):
        """unimplemented nodes"""
        self.raise_exception(node, exc=NotImplementedError, msg="`%s` not supported" % get_class_name(node))

    @staticmethod
    def get_lineno_label(node):
        if node is not None and hasattr(node, 'lineno'):
            return "{}: ".format(node.lineno)
        return ''

    @staticmethod
    def get_lineno(node):
        if node is not None and hasattr(node, 'lineno'):
            return node.lineno

    def raise_exception(self, node, exc=None, msg='', expr=None, lineno=None):  # pylint: disable=unused-argument
        """add an exception"""

        if lineno is None and node is not None:
            lineno = self.get_lineno_label(node)

        if exc is None:
            exc = RuntimeError

        if not isinstance(exc, type):
            exc = exc.__class__

        self.error = exc(msg)
        self.ui_tracer(" Exception `{}` raised: {}".format(get_class_name(exc), msg))
        raise exc(msg)

    def __call__(self, expr, **kw):
        return self.eval(expr, **kw)

    def eval(self, expr, **kw):  # pylint: disable=unused-argument
        """evaluates a single or block of statements or whole file"""
        self.error = None
        self.start = time()
        self.cycles = 0

        node = self.parse(expr)
        ret = self.run(node, expr=expr)
        if self.error is not None:
            self.ui_tracer(" Unhandled exception: {}".format(get_class_name(self.error.exc)))  # pylint: disable=no-member
        return ret

    def parse(self, text):
        """parse statement/expression to Ast representation"""
        self.expr = text
        return ast.parse(text)

    def run(self, node, expr=None):
        """executes parsed Ast representation for an expression"""
        # Note: keep the 'node is None' test: internal code here may run
        #    run(None) and expect a None in return.
        if self.max_time and time() - self.start > self.max_time:
            raise RuntimeError("Execution exceeded time limit, max runtime is {}s".format(self.max_time))

        self.cycles += 1
        if self.cycles > self.max_cycles:
            raise RuntimeError("Max cycles exceeded, max is {}.".format(self.max_cycles))

        if self.error is not None:
            # Skip over statements if there's a pending exception
            return

        if node is None:
            return

        if isinstance(node, str):
            node = self.parse(node)

        if expr is not None:
            self.expr = expr

        # set_trace() for lines
        new_line = False
        if hasattr(node, 'lineno') and node.lineno != self.prev_lineno:
            new_line = True
            self.get_current_frame().set_lineno(node.lineno)
            if self.trace:
                self.trace = self.trace(self.get_current_frame(), 'line', node.lineno)
            self.prev_lineno = node.lineno

        # get handler for this node:
        #   on_xxx with handle nodes of type 'xxx', etc
        try:
            handler = self.node_handlers[get_class_name(node).lower()]
        except KeyError:
            return self.unimplemented(node)

        # run the handler:  this will likely generate
        # recursive calls into this run method.
        try:
            ret = handler(node)
        except Exception as e:
            if self.trace and new_line:
                self.trace = self.trace(self.get_current_frame(), 'exception', node.lineno)
            raise e

        if isinstance(ret, enumerate):
            ret = list(ret)

        if isinstance(ret, Empty):
            ret = None

        return ret

    @staticmethod
    def dump(node, **kw):
        """simple ast dumper"""
        return ast.dump(node, **kw)

    # handlers for ast components
    def on_expr(self, node):
        """expression"""
        self.last_func = None
        val = self.run(node.value)
        return val  # ('value',)

    def on_index(self, node):
        """index"""
        return self.run(node.value)  # ('value',)

    def on_return(self, node):  # ('value',)
        """return statement: look for None, return special sentinel"""
        retval = self.run(node.value)

        if self.trace:
            self.trace = self.trace(self.get_current_frame(), 'return', retval)

        self.ui_tracer("{}Returning value: `{}`".format(self.get_lineno_label(node), self.quote(retval)))
        raise Return(retval if retval is not None else ReturnedNone)

    def on_repr(self, node):
        """repr """
        return repr(self.run(node.value))  # ('value',)

    def on_module(self, node):  # ():('body',)
        """module def"""
        for tnode in node.body:
            try:
                self.run(tnode)
            except Return as return_:
                return None if return_.value == ReturnedNone else return_.value

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def on_pass(self, _):  # pylint: disable=no-self-use
        """pass statement"""
        return NoReturn

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def on_ellipsis(self, _):  # pylint: disable=no-self-use
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
        if not self.run(node.test):
            self.raise_exception(node, exc=AssertionError, msg=node.msg)
        return True

    def on_list(self, node):  # ('elt', 'ctx')
        """list"""
        return [self.run(e) for e in node.elts]

    def on_tuple(self, node):  # ('elts', 'ctx')
        """tuple"""
        return tuple(self.on_list(node))

    def on_dict(self, node):  # ('keys', 'values')
        """dictionary"""
        return dict([(self.run(k), self.run(v)) for k, v in
                     zip(node.keys, node.values)])

    # noinspection PyMethodMayBeStatic
    # pylint: disable=no-self-use
    def on_num(self, node):  # ('n',)
        """return number"""
        return node.n

    # noinspection PyMethodMayBeStatic
    # pylint: disable=no-self-use
    def on_str(self, node):  # ('s',)
        """return string"""
        return node.s

    def on_starred(self, node):
        return node

    def on_name(self, node):  # ('id', 'ctx')
        """ Name node """
        ctx = node.ctx.__class__
        if ctx in (ast.Param, ast.Del):
            return str(node.id)
        else:
            frame = self.find_frame(node.id)
            if frame:
                val = frame.get_symbol_value(node.id)
                val_str = repr(val)
                if not val_str.startswith('<'):
                    if isinstance(val, str):
                        val = val.replace('`', '')

                    if frame.is_modified(node.id):
                        self.ui_tracer("{}Value of `{}` is {}."
                                       .format(self.get_lineno_label(node), node.id, self.code_wrap(val)))
                        frame.reset_modified(node.id)

                return val

            msg = "name `%s` is not defined" % node.id
            self.raise_exception(node, exc=NameError, msg=msg)

    # noinspection PyMethodMayBeStatic
    def on_nameconstant(self, node):  # pylint: disable=no-self-use
        """ True, False, None in python >= 3.4 """
        return node.value

    def __get_node_path(self, node):
        name = node
        path = []
        while True:
            try:
                name = name.id
                path.append(name)
                break
            except AttributeError:
                try:
                    path.append(name.slice.value.n)
                except AttributeError:
                    try:
                        path.append(name.slice.value.s)
                    except AttributeError:
                        try:
                            lower = name.slice.lower.n
                        except AttributeError:
                            lower = None
                        try:
                            upper = name.slice.upper.n
                        except AttributeError:
                            upper = None
                        try:
                            step = name.slice.step.n
                        except AttributeError:
                            step = None

                        slice_str = '{}:{}{}' \
                            .format(lower if lower else 0,
                                    upper if upper else -1,
                                    ':' + str(step) if step else '')

                        path.append(slice_str)

                name = name.value

        path.reverse()
        return name, path[0] + ''.join(['[{}]'.format(self.quote(i)) for i in path[1:-1]])

    def node_assign(self, node, val):  # pylint: disable=too-many-branches
        """here we assign a value (not the node.value object) to a node
        this is used by on_assign, but also by for, list comprehension, etc.
        """
        if node.__class__ == ast.Name:
            if not valid_symbol_name(node.id):
                errmsg = "invalid symbol name (reserved word?) `%s`" % node.id
                self.raise_exception(node, exc=NameError, msg=errmsg)

            if self.set_symbol(node.id, val):
                frame = self.find_frame(node.id)
                if frame:
                    frame.reset_modified(node.id)

                if val is None or isinstance(val, (str, bool, int, float, tuple, list, dict)):
                    self.ui_tracer("{}Assigned value of {} to `{}`."
                                   .format(self.get_lineno_label(node), self.code_wrap(val), node.id))

                else:
                    self.ui_tracer("{}Assigned value of {} to `{}`."
                                   .format(self.get_lineno_label(node), self.code_wrap(repr(val)), node.id))

        elif node.__class__ == ast.Attribute:
            if node.ctx.__class__ == ast.Load:
                msg = "cannot assign to attribute `%s`" % node.attr
                self.raise_exception(node, exc=AttributeError, msg=msg)

            setattr(self.run(node.value), node.attr, val)

        elif node.__class__ == ast.Subscript:
            sym = self.run(node.value)
            xslice = self.run(node.slice)
            if isinstance(node.slice, ast.Index):
                try:
                    prev_val = sym[xslice]
                except (IndexError, KeyError):
                    modified = True
                else:
                    modified = val != prev_val

                sym[xslice] = val

                name, path = self.__get_node_path(node)

                if name:
                    if modified:
                        self.ui_tracer("{}Assigned index/subscript `[{}]` of `{}` to {}."
                                       .format(self.get_lineno_label(node), self.quote(xslice),
                                               path, self.code_wrap(val)))

                        frame = self.find_frame(name)
                        if frame:
                            frame.set_modified(name)

            elif isinstance(node.slice, ast.Slice):
                # noinspection PyTypeChecker
                # pylint: disable=no-member
                try:
                    prev_val = sym[slice(xslice.start, xslice.stop, xslice.step)]
                except (IndexError, KeyError):
                    modified = True
                else:
                    modified = val != prev_val

                name, path = self.__get_node_path(node)

                sym[slice(xslice.start, xslice.stop, xslice.step)] = val

                if name:
                    if modified:
                        slice_str = '{}:{}{}' \
                            .format(xslice.start if xslice.start else 0,
                                    xslice.stop if xslice.stop else -1,
                                    ':' + str(xslice.step) if xslice.step else '')

                        self.ui_tracer("{}Assigned slice `[{}]` of `{}` to {}."
                                       .format(self.get_lineno_label(node), slice_str,
                                               path, self.code_wrap(val)))

                        frame = self.find_frame(name)
                        if frame:
                            frame.set_modified(name)

        elif node.__class__ in (ast.Tuple, ast.List):
            if len(val) == len(node.elts):
                for telem, tval in zip(node.elts, val):
                    self.node_assign(telem, tval)
            else:
                self.raise_exception(node, exc=ValueError, msg='too many values to unpack')

        else:
            raise ValueError("Invalid node assignment type!")

        return NoReturn

    def on_attribute(self, node):  # ('value', 'attr', 'ctx')
        """extract attribute"""
        ctx = node.ctx.__class__
        if ctx == ast.Store:
            msg = "attribute for storage: shouldn't be here!"
            self.raise_exception(node, exc=RuntimeError, msg=msg)

        sym = self.run(node.value)
        if ctx == ast.Del:
            return delattr(sym, node.attr)

        # ctx is ast.Load
        fmt = "cannot access attribute `%s` for `%s`"
        if node.attr not in UNSAFE_ATTRS:
            fmt = "no attribute `%s` for `%s`"
            try:
                return getattr(sym, node.attr)
            except AttributeError:
                pass

        # AttributeError or accessed unsafe attribute
        obj = self.run(node.value)
        msg = fmt % (node.attr, obj)
        self.raise_exception(node, exc=AttributeError, msg=msg)

    def on_assign(self, node):  # ('targets', 'value')
        """simple assignment"""
        val = self.run(node.value)
        for tnode in node.targets:
            self.node_assign(tnode, val)
        return NoReturn

    def on_augassign(self, node):  # ('target', 'op', 'value')
        """augmented assign"""
        return self.on_assign(ast.Assign(targets=[node.target],
                                         value=ast.BinOp(left=node.target,
                                                         op=node.op,
                                                         right=node.value)))

    def on_slice(self, node):  # ():('lower', 'upper', 'step')
        """simple slice"""
        return slice(self.run(node.lower),
                     self.run(node.upper),
                     self.run(node.step))

    def on_extslice(self, node):  # ():('dims',)
        """extended slice"""
        return tuple([self.run(tnode) for tnode in node.dims])

    def on_subscript(self, node):  # ('value', 'slice', 'ctx')
        """subscript handling -- one of the tricky parts"""
        val = self.run(node.value)
        nslice = self.run(node.slice)
        ctx = node.ctx.__class__
        if ctx in (ast.Load, ast.Store):
            if isinstance(node.slice, (ast.Index, ast.Slice, ast.Ellipsis)):
                try:
                    return val.__getitem__(nslice)
                except IndexError:
                    self.raise_exception(node, exc=IndexError, msg='index out of range')
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
                child = '.'.join(children)
                self.get_current_frame().remove_symbol(child)
                self.ui_tracer("{}Deleted `{}`.".format(self.get_lineno_label(node), child))

            elif tnode.__class__ == ast.Subscript:
                sym = self.run(tnode.value)
                xslice = self.run(tnode.slice)
                if isinstance(tnode.slice, ast.Index):
                    del sym[xslice]
                    self.ui_tracer("{}Deleted index/subscript {} of `{}`."
                                   .format(self.get_lineno_label(node), self.code_wrap(xslice), tnode.value.id))

                elif isinstance(tnode.slice, ast.Slice):
                    # noinspection PyTypeChecker
                    # pylint: disable=no-member
                    del sym[slice(xslice.start, xslice.stop, xslice.step)]

                    slice_str = '{}:{}{}' \
                        .format(xslice.start if xslice.start else 0,
                                xslice.stop if xslice.stop else -1,
                                ':' + str(xslice.step) if xslice.step else '')
                    self.ui_tracer("{}Deleted slice {} of `{}`."
                                   .format(self.get_lineno_label(node), slice_str, tnode.value.id))

                elif isinstance(tnode.slice, ast.ExtSlice):
                    del sym[xslice]
            else:
                msg = "could not delete symbol"
                self.raise_exception(node, msg=msg)

        return NoReturn

    def on_unaryop(self, node):  # ('op', 'operand')
        """unary operator"""
        func, _ = op2func(node.op)
        val = self.run(node.operand)
        ret = func(val)
        return ret

    def on_binop(self, node):  # ('left', 'op', 'right')
        """binary operator"""
        func, name = op2func(node.op)
        left, right = self.run(node.left), self.run(node.right)
        ret = func(left, right)
        self.ui_tracer("{}Operation `{} {} {}` returned `{}`."
                       .format(self.get_lineno_label(node), self.quote(left), name, self.quote(right), self.quote(ret)))
        return ret

    def on_boolop(self, node):  # ('op', 'values')
        """boolean operator"""
        val = self.run(node.values[0])
        is_and = ast.And == node.op.__class__
        if (is_and and val) or (not is_and and not val):
            for n in node.values[1:]:
                func, _ = op2func(node.op)
                val = func(val, self.run(n))
                if (is_and and not val) or (not is_and and val):
                    break
        self.ui_tracer("{}Boolean expression returned `{}`.".format(self.get_lineno_label(node), val))
        return val

    def on_compare(self, node):  # ('left', 'ops', 'comparators')
        """comparison operators"""
        lval = self.run(node.left)
        out = True
        for op, rnode in zip(node.ops, node.comparators):
            rval = self.run(rnode)
            func, name = op2func(op)
            out = func(lval, rval)
            self.ui_tracer("{}Comparison `{} {} {}` returned `{}`."
                           .format(self.get_lineno_label(node), self.quote(lval), name, self.quote(rval),
                                   self.quote(out)))
            lval = rval
            if not out:
                break
        return out

    def print_(self, *objects, sep=' ', end='\n'):
        """generic print function"""
        print(*objects, file=self.writer, sep=sep, end=end)
        return NoReturn

    def vars_(self, obj=None):
        var_dict = self.get_current_frame().get_symbols().copy()
        return {k: v for k, v in var_dict.items() if not repr(v).startswith(('<module', '<bound'))}

    def on_if(self, node):  # ('test', 'body', 'orelse')
        """regular if-then-else statement"""
        test = self.run(node.test)
        # self.ui_tracer("{}If statement evaluated as `{}`".format(self.get_lineno_label(node), bool(test)))
        if test:
            block = node.body
        else:
            block = node.orelse

        for tnode in block:
            self.run(tnode)

        return NoReturn

    def on_ifexp(self, node):  # ('test', 'body', 'orelse')
        """if expressions"""
        test = self.run(node.test)
        # self.ui_tracer("{}If else expression evaluated as `{}`".format(self.get_lineno_label(node), test))
        if test:
            expr = node.body
        else:
            expr = node.orelse

        return self.run(expr)

    def on_while(self, node):  # ('test', 'body', 'orelse')
        """while blocks"""
        self.ui_tracer("{}Executing `while` loop...".format(self.get_lineno_label(node)))
        while self.run(node.test):
            self._interrupt = None
            for tnode in node.body:
                self.run(tnode)
                if self._interrupt is not None:
                    break

            if isinstance(self._interrupt, ast.Break):
                self.ui_tracer("{}`break` hit in `while` loop, exiting loop...".format(self.get_lineno_label(node)))
                break

            elif isinstance(self._interrupt, ast.Continue):
                self.ui_tracer("{}`continue` hit in `while` loop, continuing loop..."
                               .format(self.get_lineno_label(node)))

        else:
            if hasattr(node, 'orelse') and node.orelse:
                self.ui_tracer("{}Executing `else` block for `while` loop.".format(self.get_lineno_label(node)))
                for tnode in node.orelse:
                    self.run(tnode)

        self._interrupt = None
        return NoReturn

    def on_for(self, node):  # ('target', 'iter', 'body', 'orelse')
        """for blocks"""
        self.ui_tracer("{}Executing `for` loop...".format(self.get_lineno_label(node)))
        for val in self.run(node.iter):
            self.node_assign(node.target, val)
            self._interrupt = None
            for tnode in node.body:
                self.run(tnode)
                if self._interrupt is not None:
                    break

            if isinstance(self._interrupt, ast.Break):
                self.ui_tracer("{}`break` hit in `for` loop, exiting loop...".format(self.get_lineno_label(node)))
                break

            elif isinstance(self._interrupt, ast.Continue):
                self.ui_tracer("{}`continue` hit in `for` loop, restarting loop...".format(self.get_lineno_label(node)))

        else:
            if hasattr(node, 'orelse') and node.orelse:
                self.ui_tracer("{}Executing `else` block for `for` loop.".format(self.get_lineno_label(node)))
                for tnode in node.orelse:
                    self.run(tnode)

        self._interrupt = None
        return NoReturn

    def on_excepthandler(self, node):  # ('type', 'name', 'body')
        """exception handler"""
        for ebody in node.body:  # run the statements in the handler body
            self.run(ebody)

        return NoReturn

    def on_try(self, node):  # ('body', 'handlers', 'orelse', 'finalbody')
        """try/except/else/finally blocks"""
        no_errors, found, exc, last_error = True, False, None, None
        self.ui_tracer('{}Executing `try` block...'.format(self.get_lineno_label(node)))
        for tnode in node.body:
            try:
                self.run(tnode)
            except Exception as ex:  # pylint: disable=broad-except
                exc = ex
                no_errors = False
                last_error = exc
                self.error = None
                found = False

                for hnd in node.handlers:
                    if hnd.type is not None:
                        if isinstance(hnd.type, ast.Name) and isinstance(exc, builtins.get(hnd.type.id)):
                            if hnd.name is not None:
                                self.node_assign(ast.Name(hnd.name, ast.Store(), lineno=node.lineno), last_error)
                            self.run(hnd)
                            found = True
                            break

                        elif isinstance(hnd.type, ast.Tuple):
                            for t in hnd.type.elts:
                                if isinstance(exc, builtins.get(t.id)):
                                    if hnd.name is not None:
                                        self.node_assign(ast.Name(hnd.name, ast.Store(),
                                                                  lineno=node.lineno), last_error)
                                    self.run(hnd)
                                    found = True
                                    break
                    if found:
                        break

                break

        if no_errors and hasattr(node, 'orelse') and node.orelse:
            self.ui_tracer('{}Executing `else` block...'.format(self.get_lineno_label(node.orelse)))
            for tnode in node.orelse:
                self.run(tnode)

        if not no_errors and not found and exc is not None:
            # Run a bare except if it exists
            for hnd in node.handlers:
                if hnd.type is None:
                    self.ui_tracer("{}Executing bare except... (Note: Poor coding practice)"
                                   .format(self.get_lineno_label(node)))
                    if hnd.name is not None:  # Not sure if this is possible?
                        self.node_assign(ast.Name(hnd.name, ast.Store(), lineno=node.lineno), last_error)
                    self.run(hnd)
                    found = True  # prevent unhandled exception
                    break

        if hasattr(node, 'finalbody') and node.finalbody:
            self.ui_tracer('{}Executing `finally` block...'.format(self.get_lineno_label(node)))
            for tnode in node.finalbody:
                self.run(tnode)

        if not no_errors and not found and exc is not None:
            self.ui_tracer("{}Unhandled exception, unrolling stack...".format(self.get_lineno_label(node)))
            self.error = last_error
            raise exc  # pylint: disable=raising-bad-type

        return NoReturn

    def on_raise(self, node):  # ('type', 'inst', 'tback')
        """raise statement: note difference for python 2 and 3"""
        excnode = node.exc
        msgnode = node.cause

        out = self.run(excnode)

        try:
            msg = ' '.join(out.args)  # pylint: disable=no-member
        except (TypeError, AttributeError):
            msg = ''

        msg2 = self.run(msgnode)

        if msg2 not in (None, 'None'):
            msg = "`%s: %s`" % (msg, msg2)

        self.raise_exception(node, exc=out, msg=msg, expr='')

    def on_call(self, node):
        """function execution"""
        #  ('func', 'args', 'keywords', and 'starargs', 'kwargs' in py < 3.5)
        func = self.run(node.func)

        name = ''
        if hasattr(func, '__name__'):
            name = func.__name__  # pylint: disable=no-member
        elif hasattr(func, 'name'):
            name = func.name  # pylint: disable=no-member

        self.last_func = name

        if hasattr(node.func, 'value') and hasattr(node.func.value, 'id'):
            # If func is a method call on a mutable, mark it as mutated/modified.
            # This may not always be correct (method might not mutate object),
            # but the majority of object.func() calls do mutate... so this
            # is an approximation of reality
            # TODO: Track the value of the symbol before/after for better accuracy
            if name not in ('items', 'keys', 'values', 'sorted', 'reversed', 'index', 'copy', 'count'):
                sym, _ = self.__get_node_path(node.func)
                frame = self.find_frame(sym)
                if frame:
                    frame.set_modified(sym)  # node.func.value.id

        if not hasattr(func, '__call__') and not isinstance(func, type):
            msg = "`%s` is not callable!!" % func
            self.raise_exception(node, exc=TypeError, msg=msg)

        tmpArgs = [self.run(targ) for targ in node.args]

        # expand Starred
        args = []
        for tmpArg in tmpArgs:
            if tmpArg.__class__.__name__ == 'Starred':
                args.extend(list(self.run(tmpArg.value)))
            else:
                args.append(tmpArg)

        starargs = getattr(node, 'starargs', None)
        if starargs is not None:
            args = args + self.run(starargs)

        keywords = {}
        for key in node.keywords:
            if not isinstance(key, ast.keyword):
                msg = "keyword error in function call `%s`" % func
                self.raise_exception(node, msg=msg)

            if key.arg is None:
                keywords.update(self.run(key.value))
            else:
                keywords[key.arg] = self.run(key.value)

        kwargs = getattr(node, 'kwargs', None)
        if kwargs is not None:
            keywords.update(self.run(kwargs))

        arg_list = []
        if args:
            arg_list.append(', '.join([self.quote(arg) for arg in args]))
        if keywords:
            arg_list.append(', '.join(['{}={}'.format(k, self.quote(v)) for (k, v) in keywords.items()]))

        arg_str = ', '.join(arg_list)

        if self.trace and not isinstance(func, Function):
            self.trace = self.trace(Frame(name), 'call', name)  # builtins, etc. (not user defined Functions)

        # noinspection PyBroadException
        try:
            ret = func(*args, **keywords)
        except Exception as e:  # pylint: disable=broad-except
            self.ui_tracer('{}Function `{}({})` raised on exception: {}.'
                           .format(self.get_lineno_label(node), name, self.truncate(arg_str), str(e)))

            self.error = e
            msg = "Error calling `%s()`: %s" % (name, str(e))
            self.ui_tracer(" Exception `{}` raised: {}".format(get_class_name(e), msg))
            raise

        if name not in ('pprint', 'print', 'jprint', 'print_'):
            self.ui_tracer('{}Function `{}({})` returned {}.'
                           .format(self.get_lineno_label(node), name, self.truncate(arg_str), self.code_wrap(ret)))

        return ret

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
            defval = self.run(defnode)
            keyval = self.run(node.args.args[idef + offset])
            kwargs.append((keyval, defval))

        args = [tnode.arg for tnode in node.args.args[:offset]]

        doc = None
        nb0 = node.body[0]
        if isinstance(nb0, ast.Expr) and isinstance(nb0.value, ast.Str):
            doc = nb0.value.s

        varkws = node.args.kwarg
        vararg = node.args.vararg

        if isinstance(vararg, ast.arg):
            vararg = vararg.arg
        if isinstance(varkws, ast.arg):
            varkws = varkws.arg

        self.set_symbol(node.name, Function(node.name,
                                            self,
                                            self.get_current_module().name,
                                            self.get_current_frame().get_filename(),
                                            doc=doc,
                                            lineno=node.lineno,
                                            body=node.body,
                                            args=args,
                                            kwargs=kwargs,
                                            vararg=vararg,
                                            varkws=varkws))

        return NoReturn

    def on_dictcomp(self, node):  # ('key', 'value', 'generators')
        """ Dictionary comprehension """
        out = {}
        self.push_frame(Frame('dict_comp', filename=self.get_current_frame().get_filename()))
        try:
            for tnode in node.generators:
                if tnode.__class__ == ast.comprehension:
                    for val in self.run(tnode.iter):
                        self.node_assign(tnode.target, val)
                        add = True
                        for cond in tnode.ifs:
                            add = add and self.run(cond)
                        if add:
                            out[self.run(node.key)] = self.run(node.value)
            return out

        finally:
            self.pop_frame()

    def on_listcomp(self, node):  # ('elt', 'generators')
        """list comprehension"""
        out = []
        self.push_frame(Frame('list_comp', filename=self.get_current_frame().get_filename()))
        try:
            for tnode in node.generators:
                if tnode.__class__ == ast.comprehension:
                    for val in self.run(tnode.iter):
                        self.node_assign(tnode.target, val)
                        add = True
                        for cond in tnode.ifs:
                            add = add and self.run(cond)
                        if add:
                            out.append(self.run(node.elt))
            return out
        finally:
            self.pop_frame()

    def on_set(self, node):  # ('elts',)
        """
        Set literals
        """
        result = set()
        [result.add(self.run(val)) for val in node.elts]  # pylint: disable=expression-not-assigned
        return result

    def on_import(self, node):  # ('names',)
        if self.import_hook is None:
            self.unimplemented(node)

        for name in node.names:
            import_name = name.name
            asname = name.asname
            if asname is not None:
                self.unimplemented(node)

            path, script = self.import_hook(import_name)
            if not script:
                self.raise_exception(node, ImportError, '{} not found.'.format(import_name))

            mod = self.add_module(import_name, path)
            self.get_current_frame().set_symbol(import_name, mod)
            self.enter_module(import_name)
            try:
                node = self.parse(script)
                self.run(node, expr=script)
            finally:
                self.leave_module()

        return NoReturn

    # noinspection PyMethodMayBeStatic
    def on_importfrom(self, _):  # NOOP (used for PyCharm IDE error quelling)
        return NoReturn
