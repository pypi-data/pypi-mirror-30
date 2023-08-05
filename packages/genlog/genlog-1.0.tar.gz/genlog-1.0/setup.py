#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author  : ilpan
@contact : pna.dev@outlook.com
@file    : setup.py
@desc    :
@time    : 18-3-18 下午12:07
"""

from setuptools import setup, find_packages
import genlog

setup(
    name='genlog',
    version=genlog.__version__,
    description=genlog.__description__,
    author=genlog.__author__,
    author_email='pna.dev@outlook.com',
    license=genlog.__license__,
    url='http://github.com/ilpan/GenerateLog',
    packages=find_packages(),

    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: Log Analysis',
        'Topic :: Utilities'
    ],
    keywords='genlog python3',

    entry_points={
        'console_scripts': [
          'genlog = genlog.main:main'
        ],
    }
)
