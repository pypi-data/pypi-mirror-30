#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 24 00:06:51 2018

@author: NewType
"""

from setuptools import setup

setup(name='iaajon',
      version='0.1.1',
      description='Detects potential corrupt entries in a dataframe. ',
      url='https://github.com/lionely/iaa',
      author='Jonathan Scott',
      author_email='lionelscotty95@gmail.com',
      license='BSD',
      packages=['iaajon'],
      install_requires=['gmaps','numpy','pandas'],
      zip_safe=False)
