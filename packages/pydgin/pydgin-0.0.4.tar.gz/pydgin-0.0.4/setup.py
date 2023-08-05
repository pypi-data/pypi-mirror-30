#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


packages = [
    'pydgin',
]

package_data = {
}

requires = [
    'numpy', 'numba',
]

extra_requires = {
    'ipy': ['ipywidgets'],
}

classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
]

setup(
    name='pydgin',
    version='0.0.4',
    description='',
    long_description='',
    packages=packages,
    package_data=package_data,
    install_requires=requires,
    extra_requires=extra_requires,
    url='', # TODO: input here
    license='MIT',
    classifiers=classifiers,
    author='Kit Barnes',
    author_email='kit@ninjalith.com',
)
