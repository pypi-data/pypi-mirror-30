#!/usr/bin/env python

""" File setup.py

Copyright 2018 Aris Xanthos & John Goldsmith

This file is part of the lxa5-crab python package.

lxa5-crab is free software: you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free Software 
Foundation, either version 3 of the License, or (at your option) any later 
version.

lxa5-crab is distributed in the hope that it will be useful, but WITHOUT ANY 
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 
lxa5-crab. If not, see http://www.gnu.org/licenses
"""

from os import path
from setuptools import setup

__version__ = "0.1"   # file version

NAME = 'lxa5-crab'

VERSION = '0.1'  # package version
DESCRIPTION = 'Linguistica - Crab Nebula, py 2+3 standalone implementation.'
LONG_DESCRIPTION = open(
    path.join(path.dirname(__file__), 'README.md')
).read()
AUTHOR = 'Aris Xanthos and John Goldsmith'
AUTHOR_EMAIL = 'aris.xanthos@unil.ch'
URL = 'https://github.com/axanthos/lxa5-crab'
DOWNLOAD_URL = 'https://github.com/axanthos/lxa5-crab/archive/master.zip'
LICENSE = 'GPLv3'

KEYWORDS = (
    "unsupervised learning"
    "morphological analysis",
    "linguistica",
)

CLASSIFIERS = (
    'Development Status :: 3 - Alpha',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Operating System :: OS Independent',
    'Topic :: Scientific/Engineering :: Information Analysis',
    'Topic :: Text Processing :: General',
    'Topic :: Text Processing :: Linguistic',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
)

PACKAGES = ["lxa5-crab"]

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    license=LICENSE,
    packages=PACKAGES,
    keywords=KEYWORDS,
)
