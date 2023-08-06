#!/usr/bin/env python
import os
from setuptools import setup, find_packages


# Dynamically calculate the version based on autoscan.__VERSION__
version = __import__('httplog').__VERSION__

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as fh:
    long_description = fh.read()

setup(
    name="http-log",
    version=version,
    description='httplog',
    long_description=long_description,
    packages=find_packages(),
    # metadata for upload to PyPI
    author="Joe Lei",
    author_email='thezero12@hotmail.com',
    license='Tencent license',
    keywords='httplog',
    url='https://github.com/ifooth/httplog',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
