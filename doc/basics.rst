================
Using asteval
================

The asteval module is very easy to use:

    >>> import asteval
    >>> interp = asteval.Interpreter()

and now you have an embedded interpreter for a procedural, mathematical
language that is very much like python in your application, all ready to
use::

    >>> interp('x = sqrt(3)')
    >>> interp('print x')
    1.73205080757

