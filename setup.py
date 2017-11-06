#!/usr/bin/env python
from setuptools import setup
import versioneer

long_description = """ASTEVAL provides a numpy-aware, safe(ish) 'eval' function

Emphasis is on mathematical expressions, and so numpy ufuncs
are used if available.  Symbols are held in the Interpreter
symbol table 'symtable':  a simple dictionary supporting a
simple, flat namespace.

Expressions can be compiled into ast node for later evaluation,
using the values in the symbol table current at evaluation time.
"""

setup(name='asteval',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      author='Matthew Newville',
      author_email='newville@cars.uchicago.edu',
      url='http://github.com/newville/asteval',
      license='MIT',
      description="Safe, minimalistic evaluator of python expression using ast module",
      long_description=long_description,
      packages=['asteval'],
      classifiers=[
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
      ],
      install_requires=[
            'numpy>=1.6',
            'six'
      ],
      )
