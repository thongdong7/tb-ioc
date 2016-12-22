#!/usr/bin/env python

from setuptools import setup

setup(
    name='tb-ioc',
    version='0.3.1',
    packages=['tb_ioc'],

    author='Thong Dong',
    author_email='thongdong7@gmail.com',
    description='IOC (Inversion of control) for Python',
    url='https://github.com/thongdong7/tb-ioc',
    install_requires=[
        'pyyaml~=3.11',
        'six==1.10.0',
    ]
)
