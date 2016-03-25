#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# Name: pyFlies
# Purpose: A DSL for modeling cognitive psychology experiments
# Author: Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2015 Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>
# License: GPLv3 License
###############################################################################

__author__ = "Igor R. Dejanović <igor DOT dejanovic AT gmail DOT com>"
__version__ = "0.2.post1"

import os
from setuptools import setup, find_packages

NAME = 'pyFlies'
VERSION = __version__
DESC = 'A DSL for modeling cognitive psychology experiments'
AUTHOR = 'Igor R. Dejanovic'
AUTHOR_EMAIL = 'igor DOT dejanovic AT gmail DOT com'
LICENSE = 'GPLv3'
URL = 'https://github.com/igordejanovic/pyFlies'
DOWNLOAD_URL = 'https://github.com/igordejanovic/pyFlies/archive/v%s.tar.gz'\
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
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'textX',
        'Jinja2'
        ],

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
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ],
    zip_safe=False,
    entry_points={
        'gui_scripts': [
            'pyfliesgui = pyflies.scripts.gui:pyfliesgui'
        ],
        'console_scripts': [
            'pyflies = pyflies.scripts.console:pyflies'
        ]
    }
)
