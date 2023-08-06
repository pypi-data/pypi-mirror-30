# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 18:10:53 2018

@author: Peng
"""

from setuptools import setup

setup(
      name = 'shipy',
      version = '0.01',
      description = 'Multivariate Shannon Information',
      author = 'Matthew Graham',
      author_email = 'mlwgraham1992@gmail.com',
      url = 'https://github.com/ThePengwyn/shipy',
      download_url = 'https://github.com/ThePengwyn/shipy/archive/0.01.tar.gz',
      packages = ['shipy'],
      install_requires = [
              'numpy',
              'scipy'
              ],
      classifiers=[ 
              'Development Status :: 3 - Alpha', 
              'Intended Audience :: Science/Research', 
              'License :: OSI Approved :: Apache Software License',
              'Programming Language :: Python :: 3'
              ]   
      )