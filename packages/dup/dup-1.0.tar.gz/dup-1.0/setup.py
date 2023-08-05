#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import os

from setuptools import find_packages, setup

VERSION = "1.0"

NAME = 'dup'
DESCRIPTION = """对Python unittest的功能进行了扩展
    原作者：jianbing
    git: 'https://github.com/jianbing/utx'
    EMAIL = '326333381@qq.com'    
"""

AUTHOR = 'lijian'
EMAIL = '389105015@imdada.cn'
# URL = 'git@git.corp.imdada.cn:qa/dup.git'

REQUIRED = [
    'colorama', 'enum34'
]

here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()


setup(
    name=NAME,
    version="1.0",
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    # url=URL,
    packages=find_packages(include=("dup",)),
    install_requires=REQUIRED,
    include_package_data=True,
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
