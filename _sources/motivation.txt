========================
Motivation for asteval
========================

The asteval module provides a means to evaluate a large subset of Python in
a python program, using a simple dictionary as a namespace and evaluating
strings of statements.  It is, in effect, a limited version of Python's
built-in :func:`eval`.  A completely fair question is: Why on earth would
anyone do this?  That is, why not simply use :func:`eval`, or just use
Python itself.

The short answer is that sometimes you want to allow evaluation of user
input, or expose a simple calculator inside a larger application.  For
this, :func:`eval` is pretty scary, as it exposes *all* of Python, which
can make user input difficult to trust.  Since asteval does not support the
**import** statement, user code cannot access the 'os' and 'sys' modules or
any functions or classes outside the provided symbol table.

Other missing features (modules, classes, lambda, yield, generators) are
similarly motivated.  The idea was to make a simple procedural,
mathematically-oriented language that could be embedded into larger
applications, not to write Python.

In fact, the asteval module grew out the the need for a simple expression
evaluator for scientific applications.  A first attempt using pyparsing,
but was error-prone and difficult to maintain.  It turned out that using
the Python ast module is so easy that adding more complex programming
constructs like conditionals, loops, exception handling, complex assignment
and slicing, and even function definition and running was fairly simple
implement.  Importantly, because parsing is done by the ast module, a whole
class of implementation errors disappears -- valid python expression will
be parsed correctly and converted into an Abstract Syntax Tree.
Furthermore, the resulting AST is fairly simple to walk through, greatly
simplifying evaluation over any other approach.  What started as a desire
for a simple expression evaluator grew into a quite useable procedural
domain-specific language for mathematical applications.

There is no claim of speed in asteval.  Clearly, evaluating the ast tree
involves a lot of function calls, and will likely be slower than Python.
In preliminary tests, it's about 4x slower than Python.

How Safe is asteval?
=======================

.. _eval_is_evil:  http://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html
.. _save_eval1: http://code.activestate.com/recipes/496746-restricted-safe-eval

The short answer is: Not very.  If you're looking for guarantees that
malicious code cannot ever cause damage, you're definitely looking in the
wrong place.  I don't suggest that asteval is completely safe, only that it
is safer than the builtin :func:`eval`, and that you might find it useful.
For further details, see, for example `eval_is_evil`_ and discussion and
links therein for a clear explanation of how difficult this prospect is.
Basically, if input can cause Python to core-dump, safety cannot be
guaranteed.

Still, asteval is meant to be safe relative to the builtin :func:`eval`,
especially from errors of benign stupidity.  To do this, the following
actions are not allowed from the asteval interpreter:
   
  * importing modules.  Neither 'import' nor '__import__' is supported.
  * create classes or modules.
  * access to Python's :func:`eval`.

In addition (and following the discussion in the link above), the following
attributes are blacklisted for all objects, and cannot be accessed:

   __class__, __subclasses__, __bases__, __globals__, __code__,
   __closure__, __func__, __self__,  __module__, __dict__, 

   func_globals, func_code, func_closure, 
   im_class, im_func, im_self, gi_code, gi_frame

Of course, this approach of making a blacklist cannot be guaranteed to be
complete, but it does eliminate a class of attacks to seg-fault the Python
interpreter.  Of course, asteval will typically expose ufuncs from the
numpy module, and several of these can seg-fault Python without too much
trouble.

There are important categories of safety that asteval does not even attempt
to address. The most important of these is resource hogging.  There is no
timeout on any calculation, and so reasonable looking calculuation such as

   >>> from asteval import Interpreter
   >>> aeval = Interpreter()
   >>> aeval.eval("""for i in range(100000000):
       x = sqrt(arange(1000)/(i*10.0)))
   """)

can take a noticeable amount of CPU time, ranging from seconds to hundreds
of years.  Your threshold for an acceptable run-time is probably somewhere
between these values.

In summary, there are many ways that asteval could be considered part of an
un-safe programming environment.  Recommendations for how to improve this
situation would be greatly appreciated.
