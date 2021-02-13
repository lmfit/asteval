.. _lmfit: http://github.com/lmfit/lmfit-py
.. _xraylarch: http://github.com/xraypy/xraylarch

########################
Motivation for asteval
########################

The asteval module allows you to evaluate a large subset of the Python
language from within a python program, without using :py:func:`eval`.  It is,
in effect, a restricted version of Python's built-in :py:func:`eval`,
forbidding several actions, and using a simple dictionary as a flat namespace.
A completely fair question is: Why is this desirable?  That is, why not simply
use :py:func:`eval`, or just use Python itself?

The short answer is that sometimes you want to allow evaluation of user
input, or expose a simple or even scientific calculator inside a larger
application.  For this, :py:func:`eval` is pretty scary, as it exposes
*all* of Python, which makes user input difficult to trust.  Since asteval
does not support the **import** statement or many other constructs, user
code cannot access the :py:mod:`os` and :py:mod:`sys` modules or any
functions or classes outside those provided in the symbol table.

Many of the other missing features (modules, classes, lambda, yield,
generators) are similarly motivated by a desire for a safer version of
:py:func:`eval`.  The idea for asteval is to make a simple procedural,
mathematically-oriented language that can be embedded into larger
applications.

In fact, the asteval module grew out the the need for a simple expression
evaluator for scientific applications such as the `lmfit`_ and `xraylarch`_
modules.  An early attempt using the pyparsing module worked but was
error-prone and difficult to maintain.  While the simplest of calculators
or expressiona-evaluators is not hard with pyparsing, it turned out that
using the Python :py:mod:`ast` module makes it much easier to implement a
feature-rich scientific calculator, including slicing, complex numbers,
keyword arguments to functions, etc. In fact, this approach meant that
adding more complex programming constructs like conditionals, loops,
exception handling, and even user-defined functions was fairly simple.  An
important benefit of using the :py:mod:`ast` module is that whole
categories of implementation errors involving parsing, lexing, and defining a
grammar disappear.  Any valid python expression will be parsed correctly
and converted into an Abstract Syntax Tree.  Furthermore, the resulting AST
is easy to walk through, greatly simplifying the evaluation process.  What
started as a desire for a simple expression evaluator grew into a quite
useable procedural domain-specific language for mathematical applications.

Asteval makes no claims about speed. Evaluating the AST involves many
function calls, which is going to be slower than Python - often 4x slower
than Python.  That said, for certain use cases (see
https://stackoverflow.com/questions/34106484), use of asteval and numpy can
approach the speed of `eval` and the `numexpr` modules.

How Safe is asteval?
=======================

Asteval avoids all of the exploits we know about that make :py:func:`eval`
dangerous. For reference, see, `Eval is really dangerous
<http://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html>`_ and the
comments and links therein.  From this discussion it is apparent that not only
is :py:func:`eval` unsafe, but that it is a difficult prospect to make any
program that takes user input perfectly safe.  In particular, if a user can
cause Python to crash with a segmentation fault, safety cannot be guaranteed.
Asteval explicitly forbids the exploits described in the above link, and works
hard to prevent malicious code from crashing Python or accessing the
underlying operating system.  That said, we cannot guarantee that asteval is
completely safe from malicious code.  We claim only that it is safer than the
builtin :py:func:`eval`, and that you might find it useful.

Some of the things not allowed in the asteval interpreter for safety reasons include:

  * importing modules.  Neither 'import' nor '__import__' are supported.
  * create classes or modules.
  * access to Python's :py:func:`eval`, :py:func:`execfile`,
    :py:func:`getattr`, :py:func:`hasattr`, :py:func:`setattr`, and
    :py:func:`delattr`.
  * accessing object attributes that begin and end with `__`, the so-called
    ``dunder`` attributes.  This will include (but is not limited to
    `__globals__`, `__code__`, `__func__`, `__self__`, `__module__`,
    `__dict__`, `__class__`, `__call__`, and `__getattribute__`.  None of
    these can be accessed for any object.

In addition (and following the discussion in the link above), the following
attributes are blacklisted for all objects, and cannot be accessed:

   `func_globals`, `func_code`, `func_closure`, `im_class`, `im_func`, `im_self`,
   `gi_code`, `gi_frame`, `f_locals`

While this approach of making a blacklist cannot be guaranteed to be complete,
it does eliminate entire classes of attacks known to seg-fault the Python.

It should be noted that asteval will typically expose numpy ufuncs from the
numpy module, and several of these can seg-fault Python without too much
trouble.  If you're paranoid about safe user input that can never cause a
segmentation fault, you may want to consider disabling the use of numpy
entirely.

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
anyones threshold for an acceptable run-time.  There simply is not a good
way to predict how long any code will take to run from the text of the code
itself.  As a simple example, consider the expression `x**y**z`.  For
values `x=y=z=5`, the run time will be well under 0.001 seconds.  For
`x=y=z=8`, run time will still be under 1 sec.  Changing to `x=8, y=9,
z=9`, will cause the statement to take several seconds.  With `x=y=z=9`,
executing that statement may take more than 1 hour on some machines.  In
short, runtime cannot be determined lexically.

This double exponential example also demonstrates there is not a good way
to check for a long-running calculation within a single Python process.
That calculation is not stuck within the Python interpreter, in Python's C
C-code (no doubt calling the `pow()` function) called by the Python
interpreter itself.  That call will not return to the Python interpreter or
allow other threads to run until that call is done.  That means that from
within a single process, there is not a foolproof way to tell `asteval` (or
really, even Python) when a calculation has taken too long.  The most
reliable way to limit run time is to have a second process watching the
execution time of the asteval process and interrupt or kill it.

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
desirable, and you may want to remove some of these functions from the
symbol table, re-implement them, or ensure that your program cannot access
information on disk that should be kept private.

In summary, while asteval attempts to be safe and is definitely safer than
using :py:func:`eval`, there are many ways that asteval could be considered
part of an un-safe programming environment.  Recommendations for how to
improve this situation would be greatly appreciated.
