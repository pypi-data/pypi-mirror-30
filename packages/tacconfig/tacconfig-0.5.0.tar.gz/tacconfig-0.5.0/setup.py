#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from setuptools import setup
import os

readme = open('README.rst').read()
HERE = os.path.dirname(os.path.abspath(__file__))


def get_version():
    version = '0.5.0'
    f = open(os.path.join(HERE, 'VERSION'), 'r')
    version = f.readline()
    f.close
    return version


setup(
    name='tacconfig',
    packages=['tacconfig'],
    version=get_version(),
    description='Hierarchical configuration package for containers, web apps, and services',
    author='Matthew W. Vaughn',
    author_email='vaughn@tacc.utexas.edu',
    url='https://github.com/TACC/tacconfig',
    package_dir={'tacc-config': 'tacconfig'},
    install_requires=['attrdict==2.0.0', 'PyYAML==3.12'],
    license="BSD",
    keywords='',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
        'Environment :: Other Environment',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
