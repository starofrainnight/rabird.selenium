#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst", encoding="utf-8") as readme_file, open(
    "HISTORY.rst", encoding="utf-8"
) as history_file:
    long_description = readme_file.read() + "\n\n" + history_file.read()

install_requires = [
    "click>=6.0",
    "rabird.core",
    "selenium",
    "selenium-requests",
    "six>=1.10.0",
    "whichcraft",
    "arrow",
    "Pillow",
    "docker",
    "lxml",
    "attrdict",
]

setup_requires = [
    "pytest-runner",
    # TODO(starofrainnight): put setup requirements (distutils extensions, etc.) here
]

tests_requires = [
    "pytest",
    # TODO: put package test requirements here
]

setup(
    name="rabird.selenium",
    version="0.12.5",
    description="An extension library for selenium",
    long_description=long_description,
    author="Hong-She Liang",
    author_email="starofrainnight@gmail.com",
    url="https://github.com/starofrainnight/rabird.selenium",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["rabird.selenium=rabird.selenium.__main__:main"]
    },
    include_package_data=True,
    install_requires=install_requires,
    license="Apache Software License",
    zip_safe=False,
    keywords="rabird.selenium,selenium",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    test_suite="tests",
    tests_require=tests_requires,
    setup_requires=setup_requires,
)
