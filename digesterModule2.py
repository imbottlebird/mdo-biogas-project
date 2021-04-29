# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 20:42:13 2021
Last updated on Wed Apr 28 2021

Digester Module for Spring 2021 MDO Project

inputs: waste flow rate (m3/day)
        waste composition (%) by animal type (cattle, swine, chicken)
        operating temperature (degC)
        
outputs: waste flow rate (kg/day) into reactor in kg
         reactor type (binary 0 - covered lagoon, 1 - upflow system)
         reactor volume (m3)
         gas effluent (m3/day) leaving reactor
         effluent composition (%) leaving rx (CH4, CO2, NO2, SO2)
         digestate leaving rx (m3/day)
         digestate composition (%) leaving rx (PM, NO2, SO2, inert, H2O)

@author: Jacqueline Baidoo
"""
# import packages
import pandas as pd
from scipy.integrate import odeint
import numpy as np
import matplotlib.pyplot as plt

from constants import *


# # TEST inputs
# w1 = 1
# w2 = [0.2, 0.8, 0]
# T1 = 30

# # introduce constants
# wasteData = { # moisture content, total solids, volatile solids, etc by mass
    
#     "Density" : [989.32, 996.89, 992.63], # kg/m3
#     "MC": [0.86, 0.9, 0.74], # cattle, swine, poultry
#     "TS" : [0.13, 0.1, 0.26],
#     "VS" : [0.11, 0.09, 0.19],
#     "BOD" : [0.021, 0.034, 0.058],
#     "COD" : [0.066, 0.085, 0.29],
#     "N" : [0.0047, 0.0071, 0.013]
    
#     }
# wasteData = pd.DataFrame(wasteData, index=["Cattle", "Swine", "Poultry"])

# hrtRx = pd.Series([5, 60], index=['Upflow', 'Lagoon'], name='HRT')

# Tamb = 25 + 273 # K
# Tw = 0 # K water coming into reactor
# Pdig =  1 # atm

def digester(wFR, wComp, Tdig):
    # calculate waste in kg
    wIn = wasteData['Density'].dot(wComp) * wFR # kg/day waste
    
    # determine reactor type
    mixTS = wasteData['TS'].dot(wComp)
    upflowFlag = False
        
    # determine reactor volume and time steps
    rxVUp = 1 + rxVCap
    rxVol = hrtRx['Lagoon'] * wFR * rxVUp
    vol = rxVol / rxVUp # volume of reaction medium, not scaled up
    t = np.linspace(0,hrtRx['Lagoon'])
    
    # run reactor, get methane & unreactored particulate matter
    Tdig = Tdig + 273 # temp in Kelvin
    mixCOD = wasteData['COD'].dot(wComp) # wt% weighted avg, to be kg COD / day
    mixVS = wasteData['VS'].dot(wComp) # wt% weighted avg, to be kg VS / day
    
    [sPM, ch4Out, fCH4] = rxn(wFR, mixCOD*wIn/vol, mixVS*wIn/vol, t) # kg COD or VS / m3 / day
    co2Out = ch4Out / fCH4 * (1 - fCH4); # m3 / day
    
    # check that reaction is to plan
    # plt.figure()
    # # plt.plot(t,sPM,'r-',linewidth=2,label='particulate matter')
    # plt.plot(t,ch4Out,'g:',linewidth=2,label='CH4')
    # plt.plot(t,co2Out,'y-.',linewidth=2,label='CO2')
    # plt.legend(loc='center right')
    # plt.xlabel('time (days)')
    # plt.ylabel('scm^3/day')
    # plt.title('Reaction Kinetics in Digester')
    
    # just take the last time-step concentrations
    ch4Out = ch4Out[-1]
    co2Out = co2Out[-1]
    sPM = sPM[-1]
    
    # determine flow rate & composition of effluent gas
    mixN2 = wasteData['N'].dot(wComp)
    noxOut = mixN2 / 32 * 0.5 * 46 * wFR # kg NO2 / day ; o2 demand to no2
    soxOut = mixN2 / 32 * 2/3 * 64 * wFR # kg SO2 / day; o2 demand to so2

    gasInKg = [ch4Out*0.55, co2Out*1.53, noxOut*0.99, soxOut*0.99] # 99% nox, sox in vapor
    
    gasIn = [ch4Out, co2Out, gasInKg[2]/3.3, gasInKg[3]/2.619] # m3/day
    gasComp = [i/sum(gasIn) for i in gasIn] # fraction
    gasIn = sum(gasIn) # m3/day, one number
    
    # determine flow rate & composition of digestate (solid + liquid)
    sPM = sPM / 32 * wFR # inbetween COD, o2 demand
    sPM = (1/3)*sPM*0.11*153 + (1/3)*sPM*0.21*88 + (1/3)*sPM*0.5*60
        # assume remainder is split evenly between soluble monomers,
        #       organic acids, and acetic acid by o2 demand --> kg / day
    
    inertKg = 0.6 * (mixTS - mixVS) * wIn # kg inert / day; lignin & cellulose make up 50% dry mass
    
    mixMC = wasteData['MC'].dot(wComp) # weight % that's water
    waterKg = mixMC * wIn # kg water / day 
    
    digOutKg = [sPM, noxOut*0.01, soxOut*0.01, inertKg, waterKg]
    
    sPMm3 = (1/3)*sPM/1396 + (1/3)*sPM/960 + (1/3)*sPM/1050
    digOut = [sPMm3, digOutKg[1]/3.3, digOutKg[2]/2.619, inertKg/1524,
              waterKg/997] # m3/day
    print(digOut)
    digComp = [i/sum(digOut) for i in digOut] # fraction
    digOut = sum(digOut) # m3/day, one number
    
    
    return [wIn,upflowFlag,rxVol,gasIn,gasComp,digOut,digComp]

def rxn(Q,COD_in,TOC_all,t):
    COD_d = 0.81*(1 - np.exp(-0.28*t)) + 0.19*(1 - np.exp(-0.03*t))
    vCH4 = 0.35*Q*COD_d
    
    oxSt = 4 - 1.5*(COD_in/TOC_all)
    frac_CH4 = 100 - 12.5*(oxSt + 4) + 45
    
    return [COD_in*(1 - COD_d), vCH4, frac_CH4/100]

