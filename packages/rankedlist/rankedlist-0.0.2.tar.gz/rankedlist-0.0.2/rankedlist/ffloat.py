#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 13 11:01:14 2018

@author: xingrongtech
"""

class FFloat():
    
    def __init__(self, numStr):
        self.__str = numStr
        self.__num = float(numStr)
        
    def __abs__(self):
        return abs(self.__num)
        
    def __gt__(self, obj):
        if type(obj) == int or type(obj) == float:
            return self.__num > obj
        else:
            return self.__num > obj.__num
    
    def __lt__(self, obj):
        if type(obj) == int or type(obj) == float:
            return self.__num < obj
        else:
            return self.__num < obj.__num
    
    def __ge__(self, obj):
        if type(obj) == int or type(obj) == float:
            return self.__num >= obj
        else:
            return self.__num >= obj.__num
    
    def __le__(self, obj):
        if type(obj) == int or type(obj) == float:
            return self.__num <= obj
        else:
            return self.__num <= obj.__num
        
    def __add__(self, obj):
        if type(obj) == int or type(obj) == float:
            return self.__num + obj
        else:
            return self.__num + obj.__num
        
    def __radd__(self, obj):
        if type(obj) == int or type(obj) == float:
            return obj + self.__num
        else:
            return obj.__num + self.__num
        
    def __sub__(self, obj):
        if type(obj) == int or type(obj) == float:
            return self.__num - obj
        else:
            return self.__num - obj.__num
        
    def __rsub__(self, obj):
        if type(obj) == int or type(obj) == float:
            return obj - self.__num
        else:
            return obj.__num - self.__num
        
    def __mul__(self, obj):
        if type(obj) == int or type(obj) == float:
            return self.__num * obj
        else:
            return self.__num * obj.__num
        
    def __rmul__(self, obj):
        if type(obj) == int or type(obj) == float:
            return obj * self.__num
        else:
            return obj.__num * self.__num
        
    def __truediv__(self, obj):
        if type(obj) == int or type(obj) == float:
            return self.__num / obj
        else:
            return self.__num / obj.__num
        
    def __rtruediv__(self, obj):
        if type(obj) == int or type(obj) == float:
            return obj / self.__num
        else:
            return obj.__num / self.__num
    
    def __str__(self):
        return self.__str
        
    def __repr__(self):
        return self.__str
    
    def toFloat(self):
        return self.__num