# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 11:35:01 2021

@author: Ricardo Hopker
"""
import pandas as pd
import pickle
from math import sin, cos, sqrt, atan2, radians, pi
#Farm_name = [Longitude, Latitudem Volume_per_day, Solid_percentage, cattle_percentage, pig_percentage, poultry_percentrage]
Farm_data = {
    "Farm_1": [-25.46047176, -49.70418413, 2.18, 0.03, 1.0, 0.0, 0.0],
    "Farm_2": [-25.58610376,-49.77387713, 4.128, 0.05, 0.0, 1.0, 0.0],
    "Farm_3": [-25.49456176,-49.83134413, 11.04, 0.03, 0.0, 1.0, 0.0],  
    "Farm_4": [-25.42129176,-49.77551413, 3.576, 0.03, 0.0, 1.0, 0.0],
    "Farm_5": [-25.22145176,-49.89957413, 15.99, 0.03, 0.0, 1.0, 0.0],
    "Farm_6": [-25.52145176,-49.75957413, 8.04, 0.03, 0.0, 1.0, 0.0],
    "Farm_7": [-25.62145176,-49.71957413, 15.09, 0.03, 0.0, 1.0, 0.0]}
    
#Cost Constants
a_d = [126.7373687,941.38836117] #R$/m^3 [1] --> upflow [0]--> covered lagoon 
b_d = [16248.10090549,18897.67690485] #R$ [1] --> upflow [0]--> covered lagoon
p_f = 3.53 #R$/L
p_g = 3.05 #R$/kg
p_l = 3.0 #R$/kg
e_priceS = 0.35 #R$/kWh
p_bf = 14.5 #R$/kg
f_used = 8000*0.01 #kg/ha assume a farm of 0.5 ha
e_c = 121.500 #kWh/year it is actually 121.5MWh but its too big for our current production
e_priceB = 0.59 #R$/kWh
L = 10 # years
ke = 0.08 #interest, expected return
kd = 0.04 # interest on debt for clean energy, loan provided by BNDES
tax = 0.12
g_d = 25000.0 # R$/Generator (36kVa)
g_m = g_d*0.1 #R$/year (10% of maintenance cost)
ng_max = 20
# CF = 4.17 #kWh/km
max_debt = 0.8
p_nox = 4369 # $/ton (mean) [min, max] -> [345,14915]
p_sox = 3140 # $/ton (mean) [min, max] -> [1208,7379]
p_pm = 6751 # $/ton (mean) [min, max] -> [1491,25434]
p_ch4 = 810 # $/ton (mean) [min, max] -> [370,1100]
p_co2 = 43  # $/ton (mean) [min, max] -> [12,64]
USS_to_RS = 5.49 # R$ to 1 US$ 21st march 2021
V_per_truck = 18.0 #m^3/truck
c_km = 3 #R$/km
i_main_cost = 0.15
n_start = 1
CF = 38*39.5/360 #kWh/km
c_rskm = 3.0 #R$/km
working_days = 365 #days/year
working_hours =8 #h/day
g_eff = .42 #% generator efficiency
g_power = 36.0 #kW
e_densitygas = 20 #MJ/m^3 
g= 9.81 # m/s^2
h_water = 131.1 # m
eff_pump=0.80 #%
R = 6373.0 #earth radius factor
vol_to_mass_conv = 400 #10m3 is equal to 400kg - wwww.epa.gov 
T_m3_km_cng =1/2.56 # Truck consumption of CNG (m^3) per km
T_L_km_diesel =1/2.97601 # Truck consumption of Diesel (L) per km
P_diesel = 3.3 #R$/L of diesel
C_upgrade_cng = 0.78 # R$/m^3 to upgrade from biogas to CNG
C_V_gas = 0.16 #R$/m^3 to produce biogas
NSGA_pop = 100
NSGA_gen = 500
NSGA_off = 10
GA_pop = 100
GA_gen = 100
GA_off = 10
lam = 1

with open('full_transp.p', 'rb') as fp:
    dict_T = pickle.load(fp)

#Fixing units
p_nox = p_nox*USS_to_RS
p_sox = p_sox*USS_to_RS
p_pm = p_pm*USS_to_RS
p_ch4 = p_ch4*USS_to_RS
p_co2 = p_co2*USS_to_RS
e_densitygas = e_densitygas*3.6 


# Reactor constants
wasteData = { # moisture content, total solids, volatile solids, etc by mass %
    
    "Density" : [989.32, 996.89, 992.63], # kg/m3
    "MC": [0.86, 0.9, 0.74], # cattle, swine, poultry
    "TS" : [0.13, 0.1, 0.26],
    "VS" : [0.11, 0.09, 0.19],
    "BOD" : [0.021, 0.034, 0.058],
    "COD" : [0.066, 0.085, 0.29],
    "N" : [0.0047, 0.0071, 0.013]
    
    }
wasteData = pd.DataFrame(wasteData, index=["Cattle", "Swine", "Poultry"])
hrtRx = pd.Series([5, 60], index=['Upflow', 'Lagoon'], name='HRT')
rxVCap = 0.3 # reactor volume capacity increase (maybe range from 10% - 50%)
# Tamb = 25 + 273 # K
# Tw = 0 # K water temperature around reactor
# Pdig =  1 # atm


#Biogas/fertilizer upgrading constants
ch4_pur = 0.965 #methane purity rate
fer_conv_r = 0.9 #bio-fertilizer conversion rate



dict_total = {}
for i in dir():
    if i[0]!='_' and i!='dict_total' and not(callable(globals()[i])) and i!='pd' and i!='fp' and i!='pickle':
        dict_total[i] = globals()[i]