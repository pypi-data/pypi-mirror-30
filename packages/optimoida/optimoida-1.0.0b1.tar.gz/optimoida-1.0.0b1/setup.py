#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages
from optimoida import __author__, __version__

description = "The optimoida is a command line application "
description += "to optimize image file (jpg, png only) by TinyPNG API"

with open("README.rst", "r") as fp:
    long_description = fp.read()

with open("requirements.txt", "r") as fp:
    requires = fp.read().strip().split("\n")

setup(
    name="optimoida",
    author=__author__,
    author_email="takemehighermore@gmail.com",
    url="https://github.com/alice1017/optimoida",
    description=description,
    long_description=long_description,
    version=__version__,
    license="MIT License",
    packages=find_packages(),
    install_requires=requires,
    entry_points={
        "console_scripts": [
            "optimoida=optimoida.__main__:main"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2 :: Only",
        "Topic :: Utilities"
    ]
)
