#!/usr/bin/env python  
from __future__ import print_function  
from setuptools import setup, find_packages  
import sys  
  
setup(  
    name="net163",  
    version="1.1.1",  
    author="liu",  
    author_email="langdao5@aol.com",  
    description="html text parser,get the content form html page",  
    long_description=open("README.rst").read(),  
    license="MIT",  
    url="https://pypi.python.org/pypi",  
    packages=['net163'],  
    install_requires=[  
        "pymongo","scrapy","time"  
        ],  
    classifiers=[  
        "Environment :: Web Environment",  
        "Intended Audience :: Developers",  
        "Operating System :: OS Independent",  
        "Topic :: Text Processing :: Indexing",  
        "Topic :: Utilities",  
        "Topic :: Internet",  
        "Topic :: Software Development :: Libraries :: Python Modules",  
        "Programming Language :: Python",  
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",  
    ],  
)  