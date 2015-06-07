====================================
Downloading and Installation
====================================

.. _numpy: http://docs.scipy.org/doc/numpy

Requirements
~~~~~~~~~~~~~~~

The asteval package requires Python 2.6 and higher.  Most testing has been
done with Python 2.7 and 3.2 through 3.4.  As this package is pure Python,
and depends on only packages from the standard library and `numpy`_, no
significant troubles are expected.


Downloads
~~~~~~~~~~~~~

The latest stable version of asteval is 0.9.5 and is available at PyPI:

.. _asteval-0.9.5.tar.gz:          http://pypi.python.org/packages/source/a/asteval/asteval-0.9.5.tar.gz
.. _asteval-0.9.5.win32-py2.7.exe: http://pypi.python.org/packages/any/a/asteval/asteval-0.9.5.win32-py2.7.exe
.. _asteval-0.9.5.win32-py3.4.exe: http://pypi.python.org/packages/any/a/asteval/asteval-0.9.5.win32-py3.4.exe
.. _asteval-0.9.5-py2-none-any.whl: http://pypi.python.org/packages/any/a/asteval/asteval-0.9.5-py2-none-any.whl
.. _asteval-0.9.5-py3-none-any.whl: http://pypi.python.org/packages/any/a/asteval/asteval-0.9.5-py3-none-any.whl
.. _github repository:             http://github.com/newville/asteval
.. _asteval at pypi:               http://pypi.python.org/pypi/asteval/
.. _Python Setup Tools:            http://pypi.python.org/pypi/setuptools
.. _pip:                           http://pypi.python.org/pypi/pip

+----------------------+------------------+---------------------------------------+
|  Download Option     | Python Versions  |  Location                             |
+======================+==================+=======================================+
|  Source Kit          |   2.6 and higher |  `asteval-0.9.5.tar.gz`_              |
+----------------------+------------------+---------------------------------------+
|  Win32 Installer     |   2.7            |  `asteval-0.9.5.win32-py2.7.exe`_     |
+----------------------+------------------+---------------------------------------+
|  Win32 Installer     |   3.4            |  `asteval-0.9.5.win32-py3.4.exe`_     |
+----------------------+------------------+---------------------------------------+
|  Wheel Installer     |   2.7            |  `asteval-0.9.5-py2-none-any.whl`_    |
+----------------------+------------------+---------------------------------------+
|  Wheel Installer     |   3.4            |  `asteval-0.9.5-py3-none-any.whl`_    |
+----------------------+------------------+---------------------------------------+
|  Development Version |   all            |  `github repository`_                 |
+----------------------+------------------+---------------------------------------+

If you have `pip`_, you can install asteval with::

   pip install asteval

If you have `Python Setup Tools`_ installed, you can use::

   easy_install -U asteval


Development Version
~~~~~~~~~~~~~~~~~~~~~~~~

To get the latest development version, use::

   git clone http://github.com/newville/asteval.git


Installation
~~~~~~~~~~~~~~~~~

Installation from source on any platform is::

   python setup.py install

License
~~~~~~~~~~~~~

The ASTEVAL code is distribution under the following license:

  Copyright (c) 2014 Matthew Newville, The University of Chicago

  Permission to use and redistribute the source code or binary forms of this
  software and its documentation, with or without modification is hereby
  granted provided that the above notice of copyright, these terms of use,
  and the disclaimer of warranty below appear in the source code and
  documentation, and that none of the names of The University of Chicago or
  the authors appear in advertising or endorsement of works derived from this
  software without specific prior written permission from all parties.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
  DEALINGS IN THIS SOFTWARE.
