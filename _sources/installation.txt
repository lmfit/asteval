====================================
Downloading and Installation
====================================

Prerequisites
~~~~~~~~~~~~~~~

The asteval package requires Python 2.6 and higher.  Extensive test with
version compatibility has not been done yet.  Initial tests work with
Python 3.2.  No testing has been done with 64-bit architectures, but as
this package is pure Python, no significant troubles are expected.


Downloads
~~~~~~~~~~~~~

The latest stable version of asteval is 0.9.2, available either from PyPI or CARS (Univ of Chicago):


.. _asteval-0.9.2.tar.gz (CARS):   http://cars9.uchicago.edu/software/python/asteval/src/asteval-0.9.2.tar.gz
.. _asteval-0.9.2.win32-py2.6.exe (CARS): http://cars9.uchicago.edu/software/python/asteval/src/asteval-0.9.2.win32-py2.6.exe
.. _asteval-0.9.2.win32-py2.7.exe (CARS): http://cars9.uchicago.edu/software/python/asteval/src/asteval-0.9.2.win32-py2.7.exe
.. _asteval-0.9.2.win32-py3.2.exe (CARS): http://cars9.uchicago.edu/software/python/asteval/src/asteval-0.9.2.win32-py3.2.exe

.. _asteval-0.9.2.tar.gz (PyPI): http://pypi.python.org/packages/source/a/asteval/asteval-0.9.2.tar.gz
.. _asteval-0.9.2.win32-py2.6.exe (PyPI): http://pypi.python.org/packages/any/a/asteval/asteval-0.9.2.win32-py2.6.exe
.. _asteval-0.9.2.win32-py2.7.exe (PyPI): http://pypi.python.org/packages/any/a/asteval/asteval-0.9.2.win32-py2.7.exe
.. _asteval-0.9.2.win32-py3.2.exe (PyPI): http://pypi.python.org/packages/any/a/asteval/asteval-0.9.2.win32-py3.2.exe

.. _asteval github repository: http://github.com/newville/asteval
.. _asteval at pypi:           http://pypi.python.org/pypi/asteval/
.. _Python Setup Tools:        http://pypi.python.org/pypi/setuptools

+----------------------+------------------+------------------------------------------------+
|  Download Option     | Python Versions  |  Location                                      |
+======================+==================+================================================+
|  Source Kit          | 2.6, 2.7, 3.2    | -  `asteval-0.9.2.tar.gz (PyPI)`_              |
|                      |                  | -  `asteval-0.9.2.tar.gz (CARS)`_              |
+----------------------+------------------+------------------------------------------------+
|  Win32 Installer     |   2.6            | -  `asteval-0.9.2.win32-py2.6.exe (PyPI)`_     |
|                      |                  | -  `asteval-0.9.2.win32-py2.6.exe (CARS)`_     |
+----------------------+------------------+------------------------------------------------+
|  Win32 Installer     |   2.7            | -  `asteval-0.9.2.win32-py2.7.exe (PyPI)`_     |
|                      |                  | -  `asteval-0.9.2.win32-py2.7.exe (CARS)`_     |
+----------------------+------------------+------------------------------------------------+
|  Win32 Installer     |   3.2            | -  `asteval-0.9.2.win32-py3.2.exe (PyPI)`_     |
|                      |                  | -  `asteval-0.9.2.win32-py3.2.exe (CARS)`_     |
+----------------------+------------------+------------------------------------------------+
|  Development Version |   all            |  use `asteval github repository`_              |
+----------------------+------------------+------------------------------------------------+

if you have `Python Setup Tools`_  installed, you can download and install
the asteval Package simply with::

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

  Copyright (c) 2012 Matthew Newville, The University of Chicago

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


