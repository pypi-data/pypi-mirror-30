#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


pkg = {}
exec (read('aapippackage/__pkg__.py'), pkg)

setup(
    name=pkg['__package_name__'],
    version=pkg['__version__'],
    description=pkg['__description__'],
    url='',
    author=pkg['__author__'],
    author_email=pkg['__email__'],
    license=pkg['__license__'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    tests_require=['nose']
)