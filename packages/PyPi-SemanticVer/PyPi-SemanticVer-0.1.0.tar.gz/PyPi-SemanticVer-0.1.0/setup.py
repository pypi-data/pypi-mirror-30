# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = ""

setup(
    name="PyPi-SemanticVer",
    version="0.1.0",
    description="A command line tool for incrementing semantic versioning ",
    license="MIT",
    author="John Brunelle",
    author_email="devjohnb@gmail.com",
    packages=find_packages(),
    install_requires=[],
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
    ],
    scripts=['bin/pip-sv']
)
