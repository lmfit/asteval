#!/usr/bin/env python
from setuptools import setup
import asteval


setup(name='asteval',
      version=asteval.__version__,
      author='Matthew Newville',
      author_email='newville@cars.uchicago.edu',
      url='http://github.com/newville/asteval',
      license='BSD',
      description="Safe, minimalistic evaluator of python expression using ast module",
      long_description="""ASTEVAL provides a safe(ish) 'eval' function""",
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
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
      ],
      )
