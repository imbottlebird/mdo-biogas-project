# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 11:35:01 2021

@author: Ricardo Hopker
"""
import pandas as pd

from math import sin, cos, sqrt, atan2, radians, pi

dec_mat = pd.read_excel("Decision_variables.xlsx") #Load Decision matrix
exp_1 = dec_mat.iloc[0] #Load first experiment from Decision matrix

Farm1_lat = radians(exp_1["Farm 1 Lat"])
Farm1_lon = radians(exp_1["Farm 1 Long"])
Farm2_lat = radians(exp_1["Farm 2 Lat"])
Farm2_lon = radians(exp_1["Farm 2 Long"])
Farm3_lat = radians(exp_1["Farm 3 Lat"])
Farm3_lon = radians(exp_1["Farm 3 Long"])
Farm4_lat = radians(exp_1["Farm 4 Lat"])
Farm4_lon = radians(exp_1["Farm 4 Long"])
Farm5_lat = radians(exp_1["Farm 5 Lat"])
Farm5_lon = radians(exp_1["Farm 5 Long"])

man1 = exp_1["Farm 1 manure"]
man2 = exp_1["Farm 2 manure"]
man3 = exp_1["Farm 3 manure"]
man4 = exp_1["Farm 4 manure"]
man5 = exp_1["Farm 5 manure"]

#Cost Constants
a_d = [126.7373687,941.38836117] #R$/m^3 [1] --> upflow [0]--> covered lagoon 
b_d = [16248.10090549,18897.67690485] #R$ [1] --> upflow [0]--> covered lagoon
p_f = 3.53 #R$/L
p_g = 3.05 #R$/kg
p_l = 3 #R$/kg
e_priceS = 0 #R$/kWh
p_bf = 14.5 #R$/kg
f_used = 8000*0.01 #kg/ha assume a farm of 0.5 ha
e_c = 121.200 #kWh/year it is actually 121.5MWh but its too big for our current production
e_priceB = 0.59 #R$/kWh
L = 5 # years
ke = 0.08 #interest, expected return
kd = 0.04 # interest on debt for clean energy, loan provided by BNDES
tax = 0.12
g_d = 25000 # R$/Generator (36kVa)
g_m = g_d*0.1 #R$/year (10% of maintenance cost)
# CF = 4.17 #kWh/km
max_debt = 0.8
p_nox = 4369 # $/ton (mean) [min, max] -> [345,14915]
p_sox = 3140 # $/ton (mean) [min, max] -> [1208,7379]
p_pm = 6751 # $/ton (mean) [min, max] -> [1491,25434]
p_ch4 = 810 # $/ton (mean) [min, max] -> [370,1100]
p_co2 = 43  # $/ton (mean) [min, max] -> [12,64]
USS_to_RS = 5.49 # R$ to 1 US$ 21st march 2021
V_per_truck = 18 #m^3/truck
c_km = 3 #R$/km
i_main_cost = 0.15
n_start = 1
CF = 38*39.5/360 #kWh/km
c_rskm = 3 #R$/km
working_days = 365 #days/year
working_hours =8 #h/day
g_eff = .42 #% generator efficiency
g_power = 36 #kW
e_densitygas = 20 #MJ/m^3 
g= 9.81 #m/s^2
h_water = 131.1 #m
eff_pump=0.80 #%
R = 6373.0 #earth radius factor
vol_to_mass_conv = 400 #10m3 is equal to 400kg - wwww.epa.gov 



#Fixing units
p_nox = p_nox*USS_to_RS
p_sox = p_sox*USS_to_RS
p_pm = p_pm*USS_to_RS
p_ch4 = p_ch4*USS_to_RS
p_co2 = p_co2*USS_to_RS
e_densitygas = e_densitygas*3.6 


# Reactor constants
wasteData = { # moisture content, total solids, volatile solids, etc by mass
    
    "Density" : [989.32, 996.89, 992.63], # kg/m3
    "MC": [0.86, 0.9, 0.74], # cattle, swine, poultry
    "TS" : [0.13, 0.1, 0.26],
    "VS" : [0.11, 0.09, 0.19],
    "BOD" : [0.021, 0.034, 0.058],
    "N" : [0.0047, 0.0071, 0.013]
    
    }
wasteData = pd.DataFrame(wasteData, index=["Cattle", "Swine", "Poultry"])

hrtRx = pd.Series([5, 60], index=['Upflow', 'Lagoon'], name='HRT')

Tamb = 25 + 273 # K
Tw = 0 # K water temperature around reactor
Pdig =  1 # atm
