#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys, os

version = '0.6'

setup(name='ysmtool',
      version=version,
      description=u'个人工具库，主要用于SEO，数据采集方面',
      long_description=open('readme.rst').read(),
      classifiers=[],
      author='simon',
      author_email='simon@yesiming.com',
      url='http://www.yesiming.com',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
        'beautifulsoup4',
        'demjson'
      ],
)
