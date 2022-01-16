#!/usr/bin/env python
from setuptools import setup

long_description = """ASTEVAL provides a numpy-aware, safe(ish) 'eval' function

Emphasis is on mathematical expressions, and so numpy ufuncs
are used if available.  Symbols are held in the Interpreter
symbol table 'symtable':  a simple dictionary supporting a
simple, flat namespace.

Expressions can be compiled into ast node for later evaluation,
using the values in the symbol table current at evaluation time.
"""
setup(name='asteval',
      use_scm_version=True,
      setup_requires=['setuptools_scm'],
      install_requires=['importlib_metadata ; python_version < "3.8"'],
      author='Matthew Newville',
      author_email='newville@cars.uchicago.edu',
      url='http://github.com/newville/asteval',
      license='OSI Approved :: MIT License',
      python_requires='>=3.6',
      description="Safe, minimalistic evaluator of python expression using ast module",
      long_description=long_description,

      packages=['asteval'],
      tests_require=['pytest'],
      classifiers=['Intended Audience :: End Users/Desktop',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Science/Research',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   ],
      )
