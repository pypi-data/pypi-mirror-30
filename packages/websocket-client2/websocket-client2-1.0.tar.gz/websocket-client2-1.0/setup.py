#!/usr/bin/env python

import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='websocket-client2',
      version='1.0',
      py_modules=['websocket2'],
      install_requires=('websocket-client'),
      url='https://github.com/val-labs/websocket-client2.git',
      author='Joel Ward',
      author_email='jmward@gmail.com',
      license='MIT',
      #scripts=['websocket2.py'],
      platforms='any',
      )
