# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 20:42:13 2021
Last updated on Mon Apr 12 2021

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
    if mixTS > 5:
        upflowFlag = True
    else:
        upflowFlag = False
        
    # determine reactor volume and time steps
    if upflowFlag:
        rxVol = hrtRx['Upflow'] * wFR * 1.3 # 30% bigger than flow rate
        t = np.linspace(0,hrtRx['Lagoon'])
    else:
        rxVol = hrtRx['Lagoon'] * wFR * 1.3
        t = np.linspace(0,hrtRx['Lagoon'])
    
    # run reactor
    Tdig = Tdig + 273 # temp in Kelvin
    
    # mixMC = wasteData['MC'].dot(wComp) * wIn * 1000 # L water / day
    hM_in = 10**(-7) * 4 * 32 * 1000 # neutral pH in kg BOD / m3
    
    mixBOD = wasteData['BOD'].dot(wComp) * wIn / rxVol # kg BOD / m3
    bacIn = 0.001 # kg BOD / m3 of incoming bacteria
    z0 = [0,0,0,0,hM_in,0,0,mixBOD,0,0,bacIn,bacIn,bacIn,bacIn] # initial condition
    # t = np.linspace(0,10)
    z = odeint(rxns, z0, t, args=(Tdig,mixBOD,bacIn,hM_in,rxVol/1.3,wFR,))
    
    # retrieve reaction products
    sI = z[:,0] # soluble inerts = N2, H2S in kg BOD / m3
    sH2 = z[:,4] # H2
    sCH4 = z[:,5] # methane
    sCO2 = z[:,6] # co2
    sPM = [z[:,1], z[:,2], z[:,3]] # all unreacted particulate matter
    
    # check that reaction is to plan
    # plt.figure()
    # plt.plot(t,sI,'r-',linewidth=2,label='inert')
    # plt.plot(t,sH2,'b--',linewidth=2,label='H2')
    # plt.plot(t,sCH4,'g:',linewidth=2,label='CH4')
    # plt.plot(t,sCO2,'y-.',linewidth=2,label='CO2')
    # plt.plot(t,sum(sPM),'k-',linewidth=2,label='particulate matter')
    # plt.legend(loc='center right')
    # plt.xlabel('time (days)')
    # plt.ylabel('kg BOD/m^3')
    # plt.title('Reaction Kinetics in Digester')
    
    # just take the last time-step concentrations
    sI = sI[-1]
    sH2 = sH2[-1]
    sCH4 = sCH4[-1]
    sCO2 = sCO2[-1]
    sPM = [i[-1] for i in sPM]
    
    # determine flow rate & composition of effluent gas
    mixN2 = wasteData['N'].dot(wComp)
    noxOut = sI * mixN2 / 32 * 0.5 * 46 * wFR # kg NO2 / day ; o2 demand to no2
    soxOut = sI * (1 - mixN2) / 32 * 2/3 * 64 * wFR # kg SO2 / day; o2 demand to so2
    ch4Out = sCH4 / 32 * 0.5 * 16 * wFR # kg CH4 / day; o2 demand to ch4
    co2Out = sCO2 / 32 * (1/3) * 44 * wFR # kg CO2 / day; from h2, ch4
    gasInKg = [ch4Out, co2Out, noxOut*0.99, soxOut*0.99] # 99% nox, sox in vapor
    
    gasIn = [ch4Out/0.55, co2Out/1.53, gasInKg[2]/3.3, gasInKg[3]/2.619] # m3/day
    gasComp = [i/sum(gasIn) for i in gasIn] # fraction
    gasIn = sum(gasIn) # m3/day, one number
    
    # determine flow rate & composition of digestate (solid + liquid)
    sPM[0] = sPM[0] / 32 * 0.11 * 153 * wFR # kg soluble monomers by o2 demand
    sPM[1] = sPM[1] / 32 * 0.21 * 88 * wFR # kg organic acids by o2 demand 
    sPM[2] = sPM[2] / 32 * 0.5 * 60 * wFR # kg acetic acid by o2 demand
    inertKg = 0.6 * mixTS * wIn # kg inert / day; lignin & cellulose make up 50% dry mass
    waterKg = (1 - mixTS) * wIn # kg water / day 
    digOutKg = [sum(sPM), noxOut*0.01, soxOut*0.01, inertKg, waterKg]
    
    digOut = [(sPM[0]/1396 + sPM[1]/960 + sPM[2]/1050), # assume inert density = 1
              digOutKg[1]/3.3, digOutKg[2]/2.619, inertKg/1524,
              waterKg/997] # m3/day
    digComp = [i/sum(digOut) for i in digOut] # fraction
    digOut = sum(digOut) # m3/day, one number
    
    # assume heat leaves reactor and maybe gets used to warm up animals
    #
    # # calculate temp requirement
    # enthEff = (gasInKg[0]*cpCH4(Tdig)*Tdig/16 + gasInKg[1]*cpCO2(Tdig)*Tdig/44 +
    #               gasInKg[2]*cpNO2(Tdig)*Tdig/46 + gasInKg[3]*cpSO2(Tdig)*Tdig)/64
    # enthDig= (sPM[0]*196*Tdig/153 + sPM[1]*178*Tdig/88 + sPM[2]*125*Tdig/60 +
    #               digOutKg[1]*cpNO2(Tdig)*Tdig/46 + digOutKg[2]*cpSO2(Tdig)*Tdig/64
    #               + inertKg*cpInert(Tdig))*Tdig
    # # enthWout = wIn*196*Tamb
    # enthWin = wIn*196*Tamb
    
    # enthOut = (enthEff + enthDig - enthWin) / 1000 # kJ/day
    # # print("enthalpy from effluent is: ", enthEff / 1000)
    # # print("enthalpy from digestate is: ", enthDig / 1000)
    # # print("enthalpy from waste in is: ", enthWin / 1000)
    # # enthOut = enthWout - enthWin / 1000
    # h2oOut = abs(enthOut) * 1000 / cpH2O(Tdig) / (Tdig - Tw) # kg/day
    
    # print("Waste entering reactor in kg/day: ", wIn)
    # rxName = ["Covered Lagoon", "Upflow System"]
    # print("Reactor type is: ", rxName[upflowFlag])
    # print("Reactor volume in m^3: ", rxVol)
    # print("Effluent gas leaving reactor in m^3/day is: ", gasIn)
    # print("Effluent gas composition by CH4, CO2, NO2, SO2 is: ", gasComp)
    # print("Digestate leaving reactor in m^3/day is: ", digOut)
    # print("Digestate composition by PM, NO2, SO2, inert, water is: ", digComp)
    # print("Total water needed for reactor in kg/day is: ", h2oOut)
    # print("Total heat needed for reactor in kJ/day is: ", enthOut)
    
    return [wIn,upflowFlag,rxVol,gasIn,gasComp,digOut,digComp]

def rxns(z,t,T,BODin,bacIn,hIn,rVol,volFR):
    sI = z[0] # particulate concentrations in kg BOD / m3
    sSO = z[1]
    sOA = z[2]
    sAC = z[3]
    sH2 = z[4]
    sCH4 = z[5]
    sCO2 = z[6]
    xC = z[7] # bacteria concentrations in kg COD / m3
    xS = z[8]
    xI = z[9]
    xAcid = z[10]
    xAcet = z[11]
    xMetaAC = z[12]
    xMetaH2 = z[13]
    
    pH = sH2 / 4 / 32 / 1000
    
    kDis = 1e10 * np.log(6.07e4/8.314/T) # 1/day rates
    kHyd = 1e15 * np.log(8.84e4/8.314/T)
    
    vAcid = 150*bac(T,pH) # 1/day, relative to Acet rxn from Calise as baseline
    vAcet = 100*bac(T,pH)
    vMetaAC = 40*bac(T,pH)
    vMetaH2 = 175*bac(T,pH)
    
    kAcid = 0.5 # kg COD/day
    kAcet = 0.2
    kMetaAC = 0.15
    kMetaH2 = 7e-6
    
    kdAcid = 0.02 # 1/day
    kdAcet =  0.02
    kdMetaAC = 0.02
    kdMetaH2 = 0.02
    
    # rxns
    acidRxn = (vAcid * sSO * xAcid) / (kAcid + sSO)
    acetRxn = (vAcet * sOA * xAcet) / (kAcet + sOA)
    methACRxn = (vMetaAC * sAC * xMetaAC) / (kMetaAC + sAC)
    methH2Rxn = (vMetaH2 * sH2 * xMetaH2) / (kMetaH2 + sH2)
    
    # organic species
    dsIdt = 0.02*kDis*xC - sI*volFR/rVol
    dsSOdt = kHyd*xS - acidRxn - sSO*volFR/rVol
    dsOAdt = (1 - 0.1)*acidRxn - acetRxn - sOA*volFR/rVol
    dsACdt = 0.72*(1 - 0.06)*acetRxn - methACRxn - sAC*volFR/rVol
    dsH2dt = 0.28*(1 - 0.06)*acetRxn - methH2Rxn + hIn*volFR/rVol - sH2*volFR/rVol
    dsCH4dt = (1 - 0.05)*methACRxn + (1 - 0.06)*methH2Rxn
    dsCO2dt = dsCH4dt - (1/4)*dsH2dt # gain CO2 from AC to CH4, use from H2
    
    # bacteria growth & decay
    dxCdt = (-kDis*xC + kdAcid*xAcid + kdAcet*xAcet + kdMetaAC*xMetaAC + 
             kdMetaH2*xMetaH2 + BODin*volFR/rVol - xC*volFR/rVol)
    dxSdt = 0.8*kDis*xC - kHyd*xS - xS*volFR/rVol
    dxIdt = 0.15*kDis*xC - xI*volFR/rVol
    dxAciddt = 0.1*acidRxn - kdAcid*xAcid + bacIn*volFR/rVol - xAcid*volFR/rVol
    dxAcetdt = 0.06*acetRxn - kdAcet*xAcet + bacIn*volFR/rVol - xAcet*volFR/rVol
    dxMetaACdt = 0.05*methACRxn - kdMetaAC*xMetaAC + bacIn*volFR/rVol - xMetaAC*volFR/rVol
    dxMetaH2dt = 0.06*methH2Rxn - kdMetaH2*xMetaH2 + bacIn*volFR/rVol - xMetaH2*volFR/rVol
    
    
    return [dsIdt, dsSOdt, dsOAdt, dsACdt, dsH2dt, dsCH4dt, dsCO2dt, dxCdt, dxSdt,
            dxIdt, dxAciddt, dxAcetdt, dxMetaACdt, dxMetaH2dt]
    
def bac(T,pH): # bacteria model from Esener 1981 - Klebsiella pneumoniae
    # only 10% b/c it's very fast compared to mesophiles in Demirel (2008)
    uMax = 0.1 * 5.69e14 * np.exp(-86.4e3/8.314/T) / (1 + 1.38e48 * np.exp(-287.78e3/8.314/T))
    return uMax # don't currently do anything with pH, gotta find constants
    

def cpCO2(T):
    T = T / 1000
    return 24.997 + 55.187*T - 33.691*T**2 + 7.948*T**3 - 0.137/T**2

def cpNO2(T):
    T = T / 1000
    return 16.109 + 75.895*T - 54.387*T**2 + 14.308*T**3 + 0.239/T**2

def cpSO2(T):
    T = T / 1000
    return 21.430 + 74.351*T - 57.752*T**2 + 16.355*T**3 + 0.087/T**2

def cpCH4(T):
    T = T / 1000
    return -0.703 + 108.477*T - 47.522*T**2 + 5.863*T**3 + 0.679/T**2

def cpH2O(T):
    T = T / 1000
    return -0.703 + 108.477*T - 47.522*T**2 + 5.863*T**3 + 0.679/T**2

def cpInert(T): # include molecular weights of lignin & cellulose
    return ((0.7729*T + 11.412)/1514 + 1300) / 2