#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 13 9:31:14 2018

@author: xingrongtech
"""

from .table import Table
from .ffloat import FFloat
import numpy as np
from veryprettytable import VeryPrettyTable
from math import ceil, floor
import matplotlib.pyplot as plt

class RankedList():
    '''排名列表'''
    
    def fromTxt(fName, splitter='\t', order=1):
        '''从Txt文件导入数据，创建RankedList排名列表
        【参数说明】
        1.fName(str)：文件地址，可以是绝对地址或相对地址。例如scores.txt。
        2.splitter(可选，str)：数据分隔符。例如数据为"35.3,34.1,37.9,34.8"时，splitter应为","。
        3.order(可选，int)：数据的排序方式。order=1时为升序，-1时为降序，0时为不排序。'''
        f = open(fName, 'r')
        texts = f.read()
        textArr = texts.split(splitter)
        isDecimal = texts.__contains__('.')
        if isDecimal:
            values = [FFloat(t) for t in textArr if t!='']
        else:
            values = [int(t) for t in textArr if t!='']
        return RankedList(values, order)
    
    def __init__(self, values, order=1):
        '''创建RankedList排名列表
        【参数说明】
        1.values(list或RankedList)：列表数值。例如[35.3,34.1,37.9,34.8]。
        2.order(可选，int)：数据的排序方式。order=1时为升序，-1时为降序，0时为不排序。'''
        if type(values) == RankedList:
            values = values.__values
        self.__isInt = type(values[0]) == int
        if order == 0:
            self.__values = values
        elif order == 1:
            self.__values = sorted(values)
        elif order == -1:
            self.__values = sorted(values, reverse=True)
        self.__n = len(self.__values)
    
    def __getitem__(self, index):
        '''获得排名列表中的某一项或者多项
        【参数列表】
        index：要找出的项的索引。以有序列表sc为例，index可以通过以下形式给出：
        当要找出一项时：
        (1)int：直接给出要要找出项的绝对位置，例如sc[5]表示找出sc中的第5项。
        (2)float或str：给出要找出项的float形式，或者字符串形式的相对位置。例如要找出sc中排40%的地方的值，可以通过sc[0.4]或sc['40%']找出。
        当要找出多项时：
        (3)str：通过:和绝对/相对位置，给定要找出的值所在的区间，例如':3'表示找出排第1、2、3名的数据，'10%:20%'表示排10%~20%之间的数据，'-3:'表示找出排倒数第3、2、1名的数据。
        (4)tuple：同时获得多项，每项的索引可以以(1)和(2)中的任意形式给出，例如sc[3,6,10]表示同时获得sc中的第2、5、9项；sc['10%','20%','30%']表示同时获得sc中10%、20%、30%处对应的项。'''
        if type(index) == tuple:
            return RankedList([self.__getitem__(subIndex) for subIndex in index], order=0)
        if type(index) == int:
            if index > 0:
                return self.__values[index-1]
            else:
                return self.__values[index]
        elif type(index) == float:
            id = int(self.__n*index)-1
            if id >= 0 and id < self.__n:
                return self.__values[id]
        elif type(index) == str:
            if index.find(':') != -1:
                iArr = index.split(':')
                down = iArr[0]
                up = iArr[1]
                if down == '':
                    down = 0
                elif down.find('%') != -1:
                    down = ceil(float(down[:-1])/100*self.__n)-1
                    if down < 0:
                        down = 0
                elif down.find('.') != -1:
                    down = ceil(self.__n*float(down))-1
                    if down < 0:
                        down = 0
                else:
                    down = int(down)
                    if down < 0:
                        down = self.__n+down
                    else:
                        down -= 1
                if up == '':
                    up = self.__n-1
                elif up.find('%') != -1:
                    up = floor(float(up[:-1])/100*self.__n)-1
                    if up < 0:
                        up = 0
                elif up.find('.') != -1:
                    up = floor(self.__n*float(up))-1
                    if up < 0:
                        up = 0
                else:
                    up = int(up)
                    if up < 0:
                        up = self.__n+up
                    else:
                        up -= 1
                return RankedList([self.__values[si] for si in range(down,up+1)], order=0)
            elif index[-1] == '%':
                id = int(float(index[:-1])/100*self.__n)-1
                if id >= 0 and id < self.__n:
                    return self.__values[id]
            
    def __str__(self):
        '''获得排名列表的字符串形式'''
        return str(self.__values)
    
    def __repr__(self):
        '''获得排名列表的字符串形式'''
        return repr(self.__values)
                
    def pos(self, value, method='%'):
        '''获得某项所在的位置（包括绝对位置和相对位置）
        【参数说明】
        1.value(float或int)：要查找的值。当value找得到时，会匹配value在排名列表中的位置；当value找不到时，会匹配排名列表中与value最接近的值的位置。
        2.method(str)：位置的输出方式，可以是以下值：
        (1)'d':value对应的索引，例如3表示第4项；
        (2)'f':value对应的小数形式的相对位置，例如0.4表明value对应的是排序列表中排40%处的值；
        (3)'%':value对应的百分数形式的相对位置，例如0.4表明value对应的是排序列表中排40%处的值；
        (4)'rat'：value与样本总量的比值，例如3/155表示总共155项中的第3项。'''
        if type(value) == tuple or type(value) == list:
            return [self.pos(subValue) for subValue in value]
        nearest = min(self.__values, key=lambda v: abs(v-value))
        id = self.__values.index(nearest)
        if method == '%':
            return '%.2f%%' % ((id+1)/self.__n*100)
        elif method == 'f':
            return '%.4f' % ((id+1)/self.__n)
        elif method == 'd':
            return id+1
        elif method == 'rat':
            return '%d/%d' % (id+1, self.__n)
        
    def countInRange(self, start, end):
        '''获得落在一个值区间内的样本数量
        【参数说明】
        1.start(int)：起始值。
        2.end(int)：结束值。
        start、end没有大小之分，即start>end、start<end均可满足要求。
        【返回值】
        int：落在值区间内的样本数量'''
        if start <= end:
            down, up = start, end
        else:
            down, up = end, start
        return len([vi for vi in self.__values if vi>=down and vi<=up])
    
    def toList(self):
        '''将RankedList转换为list'''
        return self.__values
    
    def rangeTable(self, step, rFormat, show='1111', name='区间|数量|比例|累计数量|累计比例', hist='0000'):
        '''展示区间分布表格
        【参数说明】
        1.step(int)：步进，即每两个区间之间的改变量是多少。例如0.1、-0.1。
        2.rFormat(str)：区间的字符串编码。例如'%.1f'。
        3.show(可选，str)：用于设定表格要展示哪些项的参数，由四个0或1组成的字符串，四个0或1依次表示“数量”、“比例”、“累计数量”、“累计比例”。例如'1111'表示“数量”、“比例”、“累计数量”、“累计比例”都显示；'1100'表示显示“数量”和“比例”，而不显示“累计数量”和“累计比例”。
        4.name(可选，str)：各项的名称，由“区间”和“数量”、“比例”、“累计数量”、“累计比例”四项，共计五项组成，格式为由“|”隔开的五项组成的字符串，即“区间|数量|比例|累计数量|累计比例”。当其中一部分项（比如“比例”、“累计比例”）不需要时，应写成“区间|数量||累计数量|”，即各项的值可以为空，但为空的项仍需使用“|”隔开。
        5.hist(可选，bool)：是否展示区间分布的直方图图表。'''
        show_count = show[0] == '1'
        show_rate = show[1] == '1'
        show_accuCount = show[2] == '1'
        show_accuRate = show[3] == '1'
        name = name.split('|')
        name_range = name[0]
        name_count = name[1]
        name_rate = name[2]
        name_accuCount = name[3]
        name_accuRate = name[4]
        table = VeryPrettyTable(format=True)
        rMax = ceil(max(self.__values) / abs(step)) * abs(step)
        rMin = floor(min(self.__values) / abs(step)) * abs(step)
        if step > 0:
            start, end = rMin, rMax
        else:
            start, end = rMax, rMin
        stepCount = round((end-start)/step)
        x = [float(xi) for xi in np.arange(start, end, step)]
        xRanges = [(rFormat + '-' + rFormat) % (xi, xi+step) for xi in x]
        table.add_column(name_range, xRanges)
        counts = [self.countInRange(xi, xi+step) for xi in x]
        if show_count:
            table.add_column(name_count, counts)
        if show_rate:
            percentages = ['%.2f%%' % (ci/self.__n*100) for ci in counts]
            table.add_column(name_rate, percentages)
        if show_accuCount or show_accuRate:
            accuCounts = [None] * len(x)
            accuCounts[0] = counts[0]
            for i in range(1, len(x)):
                accuCounts[i] = accuCounts[i-1] + counts[i]
            if show_accuCount:
                table.add_column(name_accuCount, accuCounts)
            if show_accuRate:
                accuPercentages = ['%.2f%%' % (aci/self.__n*100) for aci in accuCounts]
                table.add_column(name_accuRate, accuPercentages)
        n = hist.count('1')
        if n > 0:
            if n == 1:
                plt.figure(figsize=(6,4), dpi=80)
            elif n == 2:
                plt.figure(figsize=(5,6), dpi=80)
            elif n >= 3:
                plt.figure(figsize=(10,6), dpi=80)
            if type(self.__values[0]) == FFloat:
                vs = [vi._FFloat__num for vi in self.__values]
            else:
                vs = self.__values
            if step < 0:
                vs = [-vi for vi in vs]
            pId = [1]
            def checkPlot(id, cumu, dens, pId):
                if hist[id] == '1':
                    if n == 2:
                        plt.subplot(2,1,pId[0])
                    elif n == 3:
                        if pId[0] <= 2:
                            plt.subplot(2,2,pId[0])
                        else:
                            plt.subplot(2,1,2)
                    elif n == 4:
                        plt.subplot(2,2,pId[0])
                    if step > 0:
                        plt.hist(vs, stepCount, range=(start, end), cumulative=cumu, density=dens)
                    else:
                        plt.hist(vs, stepCount, range=(-start, -end), cumulative=cumu, density=dens)
                    pId[0] += 1
            checkPlot(0, False, False, pId)
            checkPlot(1, False, True, pId)
            checkPlot(2, True, False, pId)
            checkPlot(3, True, True, pId)
            plt.show()
        return Table(table)