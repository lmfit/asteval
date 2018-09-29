.. _lmfit: http://github.com/lmfit/lmfit-py
.. _xraylarch: http://github.com/xraypy/xraylarch

########################
Motivation for asteval
########################

The asteval module allows you to evaluate a large subset of the Python
language from within a python program, without using :py:func:`eval`.  It
is, in effect, a restricted version of Python's built-in :py:func:`eval`,
forbidding several actions, and using using a simple dictionary as a flat
namespace.  A completely fair question is: Why is this desirable?  That
is, why not simply use :py:func:`eval`, or just use Python itself?

The short answer is that sometimes you want to allow evaluation of user
input, or expose a simple calculator inside a larger application.  For
this, :py:func:`eval` is pretty scary, as it exposes *all* of Python, which
makes user input difficult to trust.  Since asteval does not support the
**import** statement (or many other constructs), user code cannot access
the :py:mod:`os` and :py:mod:`sys` modules or any functions or classes
outside the provided symbol table.

Other missing features (modules, classes, lambda, yield, generators) are
similarly motivated by a desire for a safer version of :py:func:`eval`.
The idea for asteval is to make a simple procedural, mathematically
oriented language that can be embedded into larger applications.

In fact, the asteval module grew out the the need for a simple expression
evaluator for scientific applications such as the `lmfit`_ and `xraylarch`_
modules.  A first attempt using the pyparsing module worked but was
error-prone and difficult to maintain.  It turned out that using the Python
:py:mod:`ast` module is so easy that adding more complex programming
constructs like conditionals, loops, exception handling, complex assignment
and slicing, and even user-defined functions was fairly simple to
implement.  Importantly, because parsing is done by the :py:mod:`ast`
module, whole classes of implementation errors disappear.  Valid python
expression will be parsed correctly and converted into an Abstract Syntax
Tree.  Furthermore, the resulting AST is easy to walk through, greatly
simplifying evaluation over any other approach.  What started as a desire
for a simple expression evaluator grew into a quite useable procedural
domain-specific language for mathematical applications.

Asteval makes no claims about speed. Obviously,  evaluating the ast tree
involves a lot of function calls, and will likely be slower than Python.
In preliminary tests, it's about 4x slower than Python.  For certain use
cases (see https://stackoverflow.com/questions/34106484), use of asteval
and numpy can approach the speed of `eval` and the `numexpr` modules.

How Safe is asteval?
=======================

Asteval avoids the known exploits that make :py:func:`eval` dangerous. For
reference, see, `Eval is really dangerous
<http://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html>`_ and
the comments and links therein.  From this discussion it is apparent that
not only is :py:func:`eval` unsafe, but that it is a difficult prospect to
make any program that takes user input perfectly safe.  In particular, if a
user can cause Python to crash with a segmentation fault, safety cannot be
guaranteed.  Asteval explicitly forbids the exploits described in the above
link, and works hard to prevent malicious code from crashing Python or
accessing the underlying operating system.  That said, we cannot guarantee
that asteval is completely safe from malicious code.  We claim only that it
is safer than the builtin :py:func:`eval`, and that you might find it
useful.

Some of the things not allowed in the asteval interpreter for safety reasons include:

  * importing modules.  Neither 'import' nor '__import__' are supported.
  * create classes or modules.
  * access to Python's :py:func:`eval`, :py:func:`execfile`,
    :py:func:`getattr`, :py:func:`hasattr`, :py:func:`setattr`, and
    :py:func:`delattr`.

In addition (and following the discussion in the link above), the following
attributes are blacklisted for all objects, and cannot be accessed:

   __subclasses__, __bases__, __globals__, __code__, __closure__, __func__,
   __self__, __module__, __dict__, __class__, __call__, __get__,
   __getattribute__, __subclasshook__, __new__, __init__, func_globals,
   func_code, func_closure, im_class, im_func, im_self, gi_code, gi_frame
   f_locals, __mro__

This approach of making a blacklist cannot be guaranteed to be complete,
but it does eliminate classes of attacks known to seg-fault the Python.  On
the other hand, asteval will typically expose numpy ufuncs from the numpy
module, and several of these can seg-fault Python without too much trouble.
If you're paranoid about safe user input that can never cause a
segmentation fault, you'll want to disable the use of numpy.

There are important categories of safety that asteval does not even attempt
to address. The most important of these is resource hogging, which might be
used for a denial-of-service attack.  There is no guaranteed timeout on any
calculation, and so a reasonable looking calculation such as::

   from asteval import Interpreter
   aeval = Interpreter()
   txt = """nmax = 1e8
   a = sqrt(arange(nmax))
   """
   aeval.eval(txt)

can take a noticeable amount of CPU time.  It is not hard to come up with
short program that would run for hundreds of years, which probably exceeds
anyones threshold for an acceptable run-time.  As a very simple example, it
is very hard to predict how long the expression `x**y**z` will take to run
without knowing the values of `x`, `y`, and `z`.   In short, runtime cannot
be determined lexically.

Unfortunately, there is not a good way to check for a long-running
calculation within a single Python process.  For example, the double
exponential example above will be stuck deep inside C-code evaluated by the
Python interpreter itself, and will not return or allow other threads to
run until that calculation is done.  That is, from within a single process,
there is not a foolproof way to tell `asteval` when a calculation has taken
too long.  The most reliable way to limit run time is to have a second
process watching the execution time of the asteval process and interrupt
or kill it.

For a limited range of problems, you can try to avoid asteval taking too
long.  For example, you may try to limit the *recursion limit* when
executing expressions, with a code like this::

    import contextlib

    @contextlib.contextmanager
    def limited_recursion(recursion_limit):
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(recursion_limit)
        try:
            yield
        finally:
            sys.setrecursionlimit(old_limit)

    with limited_recursion(100):
        Interpreter().eval(...)

As an addition security concern, the default list of supported functions
does include Python's `open()` which will allow disk access to the
untrusted user.  If `numpy` is supported, its `load()` and `loadtxt()`
functions will also be supported.  This doesn't really elevate permissions,
but it does allow the user of the `asteval` interpreter to read files with
the privileges of the calling program.  In some cases, this may not be
desireable, and you may want to remove some of these functions from the
symbol table, re-implement them, or ensure that your program cannot access
information on disk that should be kept private.

In summary, while asteval attempts to be safe and is definitely safer than
using :py:func:`eval`, there are many ways that asteval could be considered
part of an un-safe programming environment.  Recommendations for how to
improve this situation would be greatly appreciated.
