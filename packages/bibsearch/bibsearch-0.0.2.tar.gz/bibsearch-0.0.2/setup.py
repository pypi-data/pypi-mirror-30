#!/usr/bin/env python3

# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not
# use this file except in compliance with the License. A copy of the License
# is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

"""
A setuptools based setup module.

    python3 setup.py sdist upload -r pypi

See:
- https://packaging.python.org/en/latest/distributing.html
- https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup
import re
import os

def get_version():
    VERSION_RE = re.compile(r'''VERSION\s+=\s+['"]([0-9.]+)['"]''')
    init = open(os.path.join(os.path.dirname(__file__), 'bibsearch.py'), encoding='utf-8').read()
    return VERSION_RE.search(init).group(1)

setup(
    name = 'bibsearch',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version = get_version(),

    description = 'Download, manage, and search a BibTeX database.',
    long_description = 'Download, manage, and search a BibTeX database.',

    # The project's main homepage.
    url = 'https://github.com/mjpost/bibsearch',

    author = 'Matt Post',
    author_email='post@cs.jhu.edu',
    maintainer_email='post@cs.jhu.edu',

    license = 'Apache License 2.0',

    python_requires = '>=3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Text Processing',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3 :: Only',
    ],

    # What does your project relate to?
    keywords = ['computer science, LaTeX, BibTeX'],

    # Alternatively, if you want to distribute just a my_module.py, uncomment this:
    py_modules = ["bibsearch"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires = ['typing', 'pybtex'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require = {},

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'bibsearch = bibsearch:main',
        ],
    },
)
