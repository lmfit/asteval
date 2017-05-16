from asteval.astutils import ReturnedNone
from .frame import Frame

# pylint: disable=too-many-instance-attributes, too-many-arguments


class Function:
    """Procedure: user-defined function for asteval

    This stores the parsed ast nodes as from the
    'functiondef' ast node for later evaluation.
    """

    def __init__(self, name, interp, mod, filename, doc=None, lineno=0, body=None, args=None,
                 kwargs=None, vararg=None, varkws=None):
        self.name = name
        self.__name__ = name
        self.__asteval__ = interp
        self.raise_exc = self.__asteval__.raise_exception
        self.__doc__ = doc
        self.body = body
        self.argnames = args
        self.kwargs = kwargs
        self.vararg = vararg
        self.varkws = varkws
        self.lineno = lineno
        self.filename = filename
        self.mod = mod

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

        return "<Function %s(%s)>" % (self.name, sig)

    def __str__(self):
        return repr(self)

    def __call__(self, *args, **kwargs):
        symlocals = {}
        args = list(args)
        n_args = len(args)
        n_names = len(self.argnames)

        # may need to move kwargs to args if names align!
        if n_args < n_names and kwargs:
            for name in self.argnames[n_args:]:
                if name in kwargs:
                    args.append(kwargs.pop(name))
            n_args = len(args)
            n_names = len(self.argnames)

        if self.argnames and kwargs is not None:
            msg = "multiple values for keyword argument `{}`"
            for targ in self.argnames:
                if targ in kwargs:
                    self.raise_exc(None, exc=TypeError,
                                   msg=msg.format(targ),
                                   lineno=self.lineno)

        msg = '[expected `{}`, got `{}`]'.format(n_names, n_args)
        if n_args < n_names:
            self.raise_exc(None, exc=TypeError, msg="not enough positional parameters {}".format(msg))

        elif n_args > n_names and not self.vararg:
            self.raise_exc(None, exc=TypeError, msg="too many positional parameters {}".format(msg))

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
                self.raise_exc(None, msg='extra keyword arguments (`{}`)'.format(','.join(list(kwargs.keys()))),
                               exc=TypeError, lineno=self.lineno)

        except (ValueError, LookupError, TypeError, NameError, AttributeError) as ex:
            self.raise_exc(None, exc=ex, msg='incorrect arguments', lineno=self.lineno)

        self.__asteval__.enter_module(self.mod)
        frame = Frame(self.name, symlocals, filename=self.filename)
        self.__asteval__.push_frame(frame)
        if self.__asteval__.trace:
            self.__asteval__.trace = self.__asteval__.trace(frame, 'call', self.name)

        retval = None

        try:

            # evaluate script of function
            for node in self.body:
                self.__asteval__.run(node, expr='<>')
                if self.__asteval__.error:
                    break

                __ret_val = self.__asteval__.get_current_frame().get_retval()
                if __ret_val is not None:
                    retval = None if __ret_val == ReturnedNone else __ret_val
                    break

        finally:
            self.__asteval__.pop_frame()
            self.__asteval__.leave_module()

        return retval
