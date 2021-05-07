# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 01:04:06 2021

@author: Ricardo Hopker
"""

import Transport as T
import itertools
from constants import dict_total
from math import inf
import pickle
# def createTransportSurrogateModel(dict_total=dict_total):
#     x =[[0,1]]*7
#     allx = list(itertools.product(*x))
#     dict_T ={}
#     count = 1
#     for x in allx:
#         if count %4 ==0:
#             print(count/128)
#         if sum(x)>0:
#             dict_T[x] = T.load_data(x[0],x[1],x[2],x[3],x[4],x[5],x[6],dict_total)
#         else:
#             dict_T[x] = [inf,0,0,[1,0,0],0]
#         count = count +1
#     return dict_T
# dict_T = createTransportSurrogateModel()
# with open('full_transp.p', 'wb') as file:
#       file.write(pickle.dumps(dict_T))

def createTransportSurrogateModel(dict_total=dict_total):
    x =[[0,1]]*7
    allx = list(itertools.product(*x))
    dict_T2 ={}
    count = 1
    for x in allx:
        if count %4 ==0:
            print(count/128)
        if sum(x)>0:
            dict_T2[x] = T.transportDFS(x[0],x[1],x[2],x[3],x[4],x[5],x[6],dict_total)
        else:
            dict_T2[x] = [inf,0,0,[1,0,0],0]
        count = count +1
    return dict_T2
# dict_T = createTransportSurrogateModel()
# with open('full_transp.p', 'wb') as file:
#       file.write(pickle.dumps(dict_T))