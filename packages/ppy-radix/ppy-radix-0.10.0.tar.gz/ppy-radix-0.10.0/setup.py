#!/usr/bin/env python

import codecs
import sys
import os

from setuptools import setup, find_packages, Extension
from os.path import abspath, dirname, join

here = abspath(dirname(__file__))

# determine the python version
IS_PYPY = hasattr(sys, 'pypy_version_info')

with codecs.open(join(here, 'README.rst'), encoding='utf-8') as f:
    README = f.read()

# introduce some extra setup_args if Python 2.x
extra_kwargs = {}


tests_require = ['nose', 'coverage']
if sys.version_info < (2, 7):
    tests_require.append('unittest2')


setup(
    name='ppy-radix',
    version='0.10.0',
    maintainer='Agari Engineering',
    maintainer_email='eng-team@agari.com',
    url='https://github.com/agaridata/ppy-radix',
    description='Pure-Python radix tree implementation',
    long_description=README,
    license='BSD',
    keywords='radix tree trie python routing networking',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    tests_require=tests_require,
    packages=find_packages(exclude=['tests', 'tests.*']),
    test_suite='nose.collector',
    **extra_kwargs
)
