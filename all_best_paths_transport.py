# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 01:04:06 2021

@author: Ricardo Hopker
"""

import Transport as T
import itertools
from constants import *
x =[[0,1]]*7
allx = list(itertools.product(*x))
allx=allx[1:]
dict_T ={}
count = 1
for x in allx:
    if count %4 ==0:
        print(count/128)
    if sum(x)>2:
        dict_T[x] = T.load_data(x[0],x[1],x[2],x[3],x[4],x[5],x[6])
    count = count +1
