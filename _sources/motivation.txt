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
