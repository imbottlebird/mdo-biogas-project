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
import biogas as B

#Optimal latitude and longitude for Digestor
Digest_lat = T.location_optimal(Farm1_lat, Farm2_lat, Farm3_lat, Farm4_lat, Farm5_lat)
Digest_lon = T.location_optimal(Farm1_lon, Farm2_lon, Farm3_lon, Farm4_lon, Farm5_lon)

#Total distance travelled per day in kms to deliver manure at digestor
distance = T.total_distance(Farm1_lat, Farm1_lon, Farm2_lat, Farm2_lon, Farm3_lat, 
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

#Weighted average % of chicken manure of all the material supplied

wComp = [total_cattle_perc, total_pigs_perc, total_chicks_perc]
kilos = T.total_kg(wIn, vol_to_mass_conv)
#up to and including V_g are inputs
#print(farmer_npv(V_d,typ,distance_total,f_p,h_needed,W_out,V_gburn,V_g,e_c,e_priceB,f_used,p_bf))

print("Optimal location for DIGESTOR is latitude: "+str(Digest_lat)+" and longitude: "+str(Digest_lon))
print("Total daily distance from farms to digestor travelled is "+str(distance)+" km")
print("Total VOLUME manure supplied per day is "+str(wIn)+" m3")
print("Weighted average solids percentage of the manure supplied is "+str(total_solids_perc*100)+" %")
print("Manure composition is CATTLE-PIGS-CHICKS is "+str(wComp))
print('----')

#output from digester -- will return 9 values & print to console
Tdig = 30
[W_a, typ, V_d, G_in, G_comp, digOut, digOut_comp, W_out, H_needed] = digester(wIn,wComp,Tdig)
H_needed = JtokWh(H_needed*1000)
print('----')

#biogas module
V_g = B.scm_to_m3(B.biomethane(G_in, G_comp)) #biomethane
f_p = B.biofertilizer(kilos) 
ghg_r, ghg_c = B.ghg(kilos, wComp, G_in, G_comp) #ghg_r: released gas, ghg_c: captured gas

print("Produced biomethane: ", V_g)
print("Produced biofertilizer: ",f_p)
print("Released gas (g/tonne): ", ghg_r)
print("Captured gas (g/tonne): ", ghg_c)

#issues for discussion
#1. released gas - amount for how many days? put per day for now. --> thats fine I just multiplied in the next line by working days
#2. G_in - is this already purified? methane's rate is already 0.9665, which meets the biomethane requirement
#          in general composition of biogas, methane is expected around 0.6
#3. digOut - digestate amount is 18.7. expected around 80%-90% of kilos (7963) --> how about 18.7 kg/day *330 days/year ~6200

V_g =V_g*working_days
ghg = pd.DataFrame()
ghg['ghg_lf']=ghg_r
ghg['ghg_tech']=ghg_c
ghg['gas']= ['CH4','CO2','NOX','SOX']
list_ghg = []
for gas in ['CH4','CO2','NOX','SOX']:
    list_ghg.append(ghg[ghg['gas']==gas].values.flatten().tolist())
list_ghg = do_all_list_cp(W_a,distance,list_ghg)

n_g = 1
V_gburn = 1*V_g
print('----')
farmer_npv(n_g,V_gburn,V_d,typ,distance,f_p,H_needed,W_out,V_g,e_c,e_priceB,f_used,p_bf)
print('----')
system_npv(n_g,V_gburn,V_d,typ,distance,f_p,H_needed,W_out,V_g,e_c,e_priceB,f_used,p_bf,list_ghg)