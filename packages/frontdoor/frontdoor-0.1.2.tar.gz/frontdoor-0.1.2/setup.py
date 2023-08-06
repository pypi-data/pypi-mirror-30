#!/usr/bin/env python
import os

import setuptools


ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)))
with open(os.path.join(ROOT, 'README.rst')) as file:
    description = file.read()


setuptools.setup(
    name='frontdoor',
    version='0.1.2',
    description='Aids the creation of "front door" scripts.',
    long_description=description,
    author='Tim Simpson',
    license='MIT',
    py_modules=['frontdoor'],
)
