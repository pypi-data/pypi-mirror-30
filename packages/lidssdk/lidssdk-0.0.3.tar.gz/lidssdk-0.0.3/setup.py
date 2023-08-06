#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: xingming
# Mail: huoxingming@gmail.com
# Created Time:  2015-12-11 01:25:34 AM
#############################################


from setuptools import setup, find_packages

setup(
    name = "lidssdk",
    version = "0.0.3",
    keywords = ("pip", "lids", "liyi"),
    description = "lidi",
    long_description = "test project for python",
    license = "MIT Licence",

   # url = "http://xiaoh.me",
    author = "liyi",
    author_email = "lisc1991@163.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ['numpy'],
    entry_points={
        'console_scripts': ['lidssdk = lidssdk.help:main']
    }
)
