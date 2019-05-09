#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import CameraSequencer
from setuptools import setup, find_packages

if sys.argv[-1] == "pypi":
    os.system("python setup.py sdist bdist_wheel upload")
    sys.exit()

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

setup(
    name=CameraSequencer.__title__,
    version=CameraSequencer.__version__,
    description=CameraSequencer.__description__,
    long_description=readme,
    author=CameraSequencer.__author__,
    author_email=CameraSequencer.__email__,
    url=CameraSequencer.__url__,
    license=CameraSequencer.__license__,
    packages=find_packages(exclude=["tests"]),
    package_data={
        "": ["LICENSE", "README.rst", "HISTORY.rst"],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2',
    ],
)
