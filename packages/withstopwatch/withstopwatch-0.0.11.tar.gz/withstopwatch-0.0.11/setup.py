#!/usr/bin/env python

from distutils.core import setup

setup(name='withstopwatch',
      version='0.0.11',
      description='Stopwatch as a context manager.',
      long_description=open('README.rst').read(),
      author='Kirill Bulygin',
      author_email='kirill.bulygin@gmail.com',
      packages=['withstopwatch'])
