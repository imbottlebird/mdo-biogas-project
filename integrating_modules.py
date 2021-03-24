# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 11:34:16 2021

@author: Ricardo Hopker, Niek Jansen van Rensburg
"""
import pandas as pd
from scipy.integrate import odeint
import numpy as np
import matplotlib.pyplot as plt

from constants import *
from cost_module_funcs2 import *
from digesterModule import digester
import Transport as T

#Optimal latitude and longitude for Digestor
Digest_lat = T.location_optimal(Farm1_lat, Farm2_lat, Farm3_lat, Farm4_lat, Farm5_lat)
Digest_lon = T.location_optimal(Farm1_lon, Farm2_lon, Farm3_lon, Farm4_lon, Farm5_lon)

#Total distance travelled per day in kms to deliver manure at digestor
distance = T.total_distance(Farm1_lat, Farm1_lon, Farm2_lat, Farm2_lon, Farm3_lat, \
    Farm3_lon, Farm4_lat, Farm4_lon, Farm5_lat, Farm5_lon, Digest_lat, Digest_lon) 

#Total volumes of manure (m3) per day transported to digestor
wIn = T.total_vol(man1, man2, man3, man4, man5)

#Weighted average % of Total Solids of all the material supplied
total_solids_perc = T.vol_breakdown(man1, exp_1["Farm 1 % TS"], man2, exp_1["Farm 2 % TS"], \
    man3, exp_1["Farm 3 % TS"], man4, exp_1["Farm 4 % TS"], man5, exp_1["Farm 5 % TS"] )

#Weighted average % of cattle manure of all the material supplied
total_cattle_perc = T.vol_breakdown(man1, exp_1["Farm 1 cattle"], man2, exp_1["Farm 2 cattle"], \
    man3, exp_1["Farm 3 cattle"], man4, exp_1["Farm 4 cattle"], man5, exp_1["Farm 5 cattle"] )

#Weighted average % of pig manure of all the material supplied
total_pigs_perc = T.vol_breakdown(man1, exp_1["Farm 1 pigs"], man2, exp_1["Farm 2 pigs"], \
    man3, exp_1["Farm 3 pigs"], man4, exp_1["Farm 4 pigs"], man5, exp_1["Farm 5 pigs"] )

#Weighted average % of chicken manure of all the material supplied
total_chicks_perc = T.vol_breakdown(man1, exp_1["Farm 1 chicks"], man2, exp_1["Farm 2 chicks"], \
    man3, exp_1["Farm 3 chicks"], man4, exp_1["Farm 4 chicks"], man5, exp_1["Farm 5 chicks"] )

wComp = [total_cattle_perc, total_pigs_perc, total_chicks_perc]

#up to and including V_g are inputs
#print(farmer_npv(V_d,typ,distance_total,f_p,h_needed,W_out,V_gburn,V_g,e_c,e_priceB,f_used,p_bf))

print("Optimal location for DIGESTOR is latitude: "+str(Digest_lat)+" and longitude: "+str(Digest_lon))
print("Total daily distance from farms to digestor travelled is "+str(distance_total)+" km")
print("Total VOLUME manure supplied per day is "+str(wIn)+" m3")
print("Weighted average solids percentage of the manure supplied is "+str(total_solids_perc*100)+" %")
print("Manure composition is CATTLE-PIGS-CHICKS is "+str(wComp))

#output from digester -- will return 9 values & print to console
Tdig = 30
[W_a, typ, V_d, G_in, G_comp, digOut, digOut_comp, W_out, H_needed] = digester(wIn,wComp,Tdig)
