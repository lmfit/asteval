#!/usr/bin/env python
from distutils.core import setup
import lib as asteval

setup(name = 'asteval',
      version = asteval.__version__,
      author = 'Matthew Newville',
      author_email = 'newville@cars.uchicago.edu',
      url  = 'http://github.com/newville/asteval',
      license = 'BSD',
      description = "Safe, minimalistic evaluator of python expression using ast module",
      package_dir = {'asteval': 'lib'},
      packages = ['asteval'],
      )

