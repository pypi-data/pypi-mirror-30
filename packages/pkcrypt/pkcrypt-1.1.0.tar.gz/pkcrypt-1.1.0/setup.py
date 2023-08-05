#!/usr/bin/env python
import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
setup(name='pkcrypt',
      version='1.1.0',
      description='public key cryptography',
      author='Joel Ward',
      author_email='jmward@gmail.com',
      license='MIT',
      platforms='any',
      url='https://github.com/val-labs/pkcrypt/tree/master/pkcrypt',
      packages=['pkcrypt'],
      scripts=['bin/pkcrypt','bin/pkdcrypt','bin/pkecrypt'],
      install_requires=['fastecdsa','pyaml','cryptography'],
     )
