#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 13 16:14:26 2018

@author: xingrongtech
"""

class Table():
    
    def __init__(self, vpTable):
        self.__vpTable = vpTable
        self.__vpTable.format = True
        
    def __repr__(self):
        return self.__vpTable.get_string()
    
    def _repr_html_(self):
        return self.__vpTable.get_html_string()