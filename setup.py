#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import, print_function

import io
import re
from glob import glob
from os.path import basename, dirname, join, splitext

from setuptools import find_packages, setup


def read(*names, **kwargs):
    return io.open(join(dirname(__file__), *names), encoding=kwargs.get('encoding', 'utf8')).read()


setup(
    name='checklisting',
    version='0.1.0',
    license='MIT license',
    description='Service checklisting made easy and automated',
    long_description='%s\n%s' % (re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub(
        '', read('README.rst')), re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))),
    author='Micha\u0142 Bachowski',
    author_email='michal@bachowski.pl',
    url='https://github.com/michalbachowski/python-checklisting',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=True,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        # uncomment if you test on these interpreters:
        # 'Programming Language :: Python :: Implementation :: IronPython',
        # 'Programming Language :: Python :: Implementation :: Jython',
        # 'Programming Language :: Python :: Implementation :: Stackless',
        'Topic :: Utilities',
    ],
    install_requires=[
        'pyyaml==3.11',
        'logging_utils==0.0.1',
        'PySimplePluginsDiscovery==0.1.0',
    ],
    extras_require={
        'web': [
            'aiohttp==3.3.2',
        ],
    },
    entry_points={
        'console_scripts': [
            'checklisting = checklisting.cli:main',
        ],
    },
)
