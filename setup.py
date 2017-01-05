#!/usr/bin/env python

from setuptools import setup

import sys

if sys.version_info < (3, 2):
    install_requires = ["future"]
else:
    install_requires = ["future"]

setup(
    name='tb-ioc',
    version='0.3.3',
    packages=['tb_ioc'],

    author='Thong Dong',
    author_email='thongdong7@gmail.com',
    description='IOC (Inversion of control) for Python',
    url='https://github.com/thongdong7/tb-ioc',
    install_requires=[
        'pyyaml~=3.11',
        'six==1.10.0',
    ] + install_requires
)
