# -*- coding: utf-8 -*-
"""
Created on Fri Apr 13 16:15:17 2018

@author: xingrongtech
"""

from distutils.core import setup

setup(name = 'rankedlist',
      version = '0.0.2',
      description='A Python library for data ranking, finding one value or a group of values by indexing absolutely or relatively.', 
      author = 'xingrongtech',
      author_email = 'wzv100@163.com',
      license='MIT License',
      install_requires = ['numpy', 'veryprettytable', 'matplotlib'],
      packages=['rankedlist'],
      keywords=['rank'],
      url='https://github.com/xingrongtech/rankedlist',
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
