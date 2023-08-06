# -*- coding: utf-8 -*-
"""
Created on Fri Apr 13 16:15:17 2018

@author: xingrongtech
"""

from distutils.core import setup

setup(name = 'rankedlist',
      version = '0.0.1',
      description='A library for data to ranking.', 
      author = 'xingrongtech',
      author_email = 'wzv100@163.com',
      license='MIT License',
      install_requires = ['numpy', 'veryprettytable'],
      packages=['rankedlist'],
      keywords=['rank'],
      classifiers=[
              'Development Status :: 4 - Beta',
              'Operating System :: OS Independent',
              'Intended Audience :: Developers',
              'License :: OSI Approved :: BSD License',
              'Programming Language :: Python',
              'Programming Language :: Python :: Implementation',
              'Programming Language :: Python :: 3.4',
              'Programming Language :: Python :: 3.5',
              'Programming Language :: Python :: 3.6',
              'Topic :: Software Development :: Libraries'
      ],
      )
