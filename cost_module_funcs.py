# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 00:09:10 2021

@author: Ricardo Hopker
"""
i=0.08 #8% is the expected return on agriculture in Brazil

def investment(volume,upOrCover='Upflow System'):
    # return in real 2021 value, digestor volume in m^3
    if upOrCover == 'Upflow System':
        return 941.38836117*volume+18897.67690485
    elif upOrCover == 'Covered lagoon':
        return 126.7373687*volume+16248.10090549
    raise NotImplementedError
def transportation(volume_per_year,km):
     # return in real 2021 value, volume of manure in m^3 
     return 3*km*volume_per_year/18.0
def energy_cost(kWh,category=1):
    #energy cost in parana: There are 4 cost depending on water level on dams
    #cost in real 2021
    #https://www.copel.com/hpcopel/root/nivel2.jsp?endereco=%2Fhpcopel%2Froot%2Fpagcopel2.nsf%2Fdocs%2F23BF37E67261209C03257488005939EB
    icms=.29
    pis=0.0111
    cofins=0.0509
    tax_total = icms+pis+cofins
    b2=0.36698
    yellow=0.015
    red = 0.04
    superred=0.06
    if category ==0:
        return kWh*b2/(1-tax_total)
    if category ==1:
        return kWh*(b2+yellow)/(1-tax_total)
    if category ==2:
        return kWh*(b2+red)/(1-tax_total)
    if category ==3:
        return kWh*(b2+superred)/(1-tax_total)
def biogas_cost():
    raise NotImplementedError
    
def maintenance_cost():
    raise NotImplementedError

def npv(P,n,i=i):
    return P/(1+i)**n
def polution_avoided_specific(list_in):
    #https://reader.elsevier.com/reader/sd/pii/S0959652619307929?token=BC8B4776075DBF71536EA5B07D0328D1D52E1A387C68CB7BB93F6A9E9128722F38F694886CFCE14349F189AE6D053962
    #equation (7)
    #Nox here is an example can be used for SOx,PM,CH4,CO2,
    W = list_in[0]
    NOX_lf = list_in[1]
    NOX_tech = list_in[2]
    NOX_ff = list_in[3]
    P_nox = list_in[4]
    return W*(NOX_lf-NOX_tech)*P_nox + W*(NOX_ff-NOX_tech)*P_nox
def polution_avoided(list_of_gas):
    s = 0
    for i in list_of_gas:
        s=s+polution_avoided_specific(i)
    return s
list_of_gas = [[1,2,1.5,2,5],[1,2,1.5,2,5]]
polution_avoided(list_of_gas)