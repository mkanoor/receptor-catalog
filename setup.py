#!/usr/bin/env python

# Copyright (c) 2020 Red Hat, Inc.
# All Rights Reserved.

from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="receptor-catalog",
    version="1.0.0",
    author="Red Hat Insights",
    url="https://github.com/mkanoor/receptor-catalog",
    license="Apache",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[ "aiohttp" ],
    setup_requires=['pytest-runner'],
    tests_require=["aioresponses","pytest"],
    zip_safe=False,
    entry_points={"receptor.worker": "receptor_catalog = receptor_catalog.worker"},
    classifiers=["Programming Language :: Python :: 3"],
    extras_require={"dev": ["pytest", "flake8", "pylint", "black"]},
)
