#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages


if sys.version_info < (3, 6):
    print("FogStone requires Python 3.6 or later.")
    sys.exit(1)

import fogstone


setup(
    name="fogstone",
    version=fogstone.__version__,
    description="Simple helpdesk system",
    long_description=open("README.md").read(),
    author="Andriy Kushnir (Orhideous)",
    author_email="me@orhideous.name",
    license="MIT",
    url="https://github.com/MC4EP/fogstone",
    platforms="any",
    packages=find_packages(),
    install_requires=open("requirements.txt").read().splitlines(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "fogstone=fogstone.scripts:cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Flask",
        "License :: OSI Approved",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
)
