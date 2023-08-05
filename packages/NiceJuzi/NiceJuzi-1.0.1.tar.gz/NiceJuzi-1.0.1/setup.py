#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
"""
@Time : 18/3/19 下午5:41 
@Author : nice、柠檬 
@File : setup.py 
@Software: PyCharm
"""
from setuptools import setup, find_packages

setup(
    name='NiceJuzi',
    version='1.0.1',
    description=(
        '<util function>'
    ),
    long_description=open('README.rst').read(),
    author='<nice>',
    author_email='<2233987442@qq.com>',
    maintainer='<juzi>',
    maintainer_email='2233987442@qq.com',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='https://gitee.com/juziweb/NiceJuzi.git',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries'
    ],
)
