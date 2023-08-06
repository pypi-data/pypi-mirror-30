#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()
# with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as requirements:
#     requirement = requirements.readlines()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="flytrap-comments",
    version="0.0.1",
    author="flytrap",
    author_email="hiddenstat@gmial.com",
    description="A simple Django app to comment",
    long_description=README,
    url="https://github.com/flytrap/flytrap-comments",
    install_requires=[
        "Django>=2.0",
        "djangorestframework==3.7.3",
        "django-filter==1.1.0",
        "flytrap-base==0.0.5"
    ],
    packages=find_packages(),
    test_suite="runtests.runtests",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
