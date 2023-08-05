#!/usr/bin/env python
import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
setup(name='p2p-addons',
      version='1.0.0',
      description='peer2peer add ons',
      py_modules=['addons'],
      license='MIT',
      platforms='any',
      install_requires=['peer2peer']
      )
