# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 10:48:58 2021

@author: Ricardo Hopker
"""
from math import log
def digestor_stats(wIn,wComp):
    wInCattle = wIn*wComp[0]
    wInSwine = wIn*wComp[1]
    biogas_total = cattle_biogas(wInCattle)
    biogas_total += swine_biogas(wInSwine)
    V_d = (wInCattle+wInSwine)*30*1.3
    
    return biogas_total,V_d
    
def cattle_biogas(x):
    return 2.0037*log(x)+12.915
def swine_biogas(x):
    return 16.174*log(x)+41.355