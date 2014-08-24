#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# Name: pyFlies
# Purpose: A language for behaviour experiment modeling
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
###############################################################################

__author__ = "Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>"
__version__ = "0.1-dev"

import os
from setuptools import setup

NAME = 'pyFlies'
VERSION = __version__
DESC = 'Behaviour modeling textual language'
AUTHOR = 'Igor R. Dejanovic'
AUTHOR_EMAIL = 'igor DOT dejanovic AT gmail DOT com'
LICENSE = 'MIT'
URL = 'https://github.com/igordejanovic/pyFlies'
DOWNLOAD_URL = 'https://github.com/igordejanovic/textX/archive/v%s.tar.gz'\
    % VERSION
README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name=NAME,
    version=VERSION,
    description=DESC,
    long_description=README,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    license=LICENSE,
    url=URL,
    download_url=DOWNLOAD_URL,
    packages=["pyflies"],
    keywords="language behaviour experiment",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Healthcare Industry',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ],

    entry_points={
        'gui_scripts': [
            'pyflies = pyflies.gui:main',
        ]
    }
)
