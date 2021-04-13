# -*- coding: utf-8 -*-
"""
Created on Tue Apr 13 13:33:30 2021

@author: Ricardo Hopker
"""
import pickle
import numpy as np
from integrating_modules import biodigestor
import matplotlib.pyplot as plt
with open('full_transp.p', 'rb') as fp:
    dict_T = pickle.load(fp)
with open('for_plot.pkl', 'rb') as fp:
    Z = pickle.load(fp)
f = lambda tup: int("".join(str(ele) for ele in tup), 2)
d = [f(tup) for tup in dict_T.keys()]
dlist = list(dict_T.keys())
VGb = np.linspace(0,0.5,100)
farm = range(128)
VGB,FARM = np.meshgrid(VGb,farm)
@np.vectorize
def get_bio(VGg,farm):
    vec = [VGg, 1,37,0]
    vec.extend(list(dlist[farm]))
    Z = -biodigestor(vec)
    return Z
# Z = get_bio(VGB,FARM)
fig,ax= plt.subplots()
ax.contourf(VGB,FARM,Z)