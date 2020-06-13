#!/usr/bin/env python

# Copyright (c) 2020 Red Hat, Inc.
# All Rights Reserved.

from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="receptor-catalog",
    version="0.6.3",
    author="Red Hat Insights",
    author_email="support@redhat.com",
    url="https://github.com/mkanoor/receptor-catalog",
    license="Apache",
    packages=find_packages(),
    description="Receptor plugin to communicate with Ansible Tower API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[ "aiohttp", "jmespath"],
    setup_requires=['pytest-runner'],
    tests_require=["aioresponses","pytest"],
    zip_safe=False,
    entry_points={"receptor.worker": "receptor_catalog = receptor_catalog.worker"},
    classifiers=["Programming Language :: Python :: 3"],
    extras_require={"dev": ["pytest", "flake8", "pylint", "black"]},
)
