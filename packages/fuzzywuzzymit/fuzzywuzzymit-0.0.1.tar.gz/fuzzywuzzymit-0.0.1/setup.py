#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014 SeatGeek

# This file is part of fuzzywuzzymit.

from fuzzywuzzymit import __version__
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def open_file(fname):
    return open(os.path.join(os.path.dirname(__file__), fname))

setup(
    name='fuzzywuzzymit',
    version=__version__,
    author='Adam Cohen',
    author_email='adam@seatgeek.com',
    packages=['fuzzywuzzymit'],
    url='https://github.com/graingert/fuzzywuzzymit',
    license="MIT",
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description='Fuzzy string matching in python',
    long_description=open_file('README.rst').read(),
    zip_safe=True,
)
