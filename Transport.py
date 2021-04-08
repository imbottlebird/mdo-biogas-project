#cd /Users/niekjansenvanrensburg/Documents/MDO/Assignment_2  

import pandas as pd
import cvxpy as cp
from math import sin, cos, sqrt, atan2, radians, pi
from constants import *

#Total volumes (m3) are the daily volumes of all the farms per day
def total_vol(m1, m2, m3, m4, m5):
    return (m1+m2+m3+m4+m5)

volume = total_vol(man1, man2, man3, man4, man5)

def location_optimal(l1, l2, l3, l4, l5):
    return (l1+l2+l3+l4+l5)/5

def distance(Farm_lat, dlat, dlon):
    a = sin(dlat / 2)**2 + cos(Farm_lat) * cos(Farm_lat) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return c

Digest_lat = location_optimal(Farm1_lat, Farm2_lat, Farm3_lat, Farm4_lat, Farm5_lat)
Digest_lon = location_optimal(Farm1_lon, Farm2_lon, Farm3_lon, Farm4_lon, Farm5_lon)

print("Location of FARM1 in radians is latitude: "+str(Farm1_lat)+" and longitude: "+str(Farm2_lon))
print("Location of FARM2 in radians is latitude: "+str(Farm2_lat)+" and longitude: "+str(Farm2_lon))
print("Location of FARM3 in radians is latitude: "+str(Farm3_lat)+" and longitude: "+str(Farm3_lon))
print("Location of FARM4 in radians is latitude: "+str(Farm4_lat)+" and longitude: "+str(Farm4_lon))
print("Location of FARM5 in radians is latitude: "+str(Farm5_lat)+" and longitude: "+str(Farm5_lon))


#Total distance is the travelled distance from all 5 farms per day in km's - ENSURE CAPACITY OF TRUCKS IS ADDRESSED IN THIS CALC
def total_distance(lat1, lon1, lat2, lon2, lat3, lon3, lat4, lon4, lat5, lon5, dlat, dlon):
    dlon1 = lon1 - dlon
    dlat1 = lat1 - dlat
    dlon2 = lon2 - dlon 
    dlat2 = lat2 - dlat
    dlon3 = lon3 - dlon
    dlat3 = lat3 - dlat
    dlon4 = lon4 - dlon
    dlat4 = lat4 - dlat
    dlon5 = lon5 - dlon
    dlat5 = lat5 - dlat

    Farm1_c = distance(lat1, dlat1, dlon1)
    Farm2_c = distance(lat2, dlat2, dlon2)
    Farm3_c = distance(lat3, dlat3, dlon3)
    Farm4_c = distance(lat4, dlat4, dlon4)
    Farm5_c = distance(lat5, dlat5, dlon5)

    return R * (Farm1_c + Farm2_c + Farm3_c + Farm4_c + Farm5_c)


distance_total = total_distance(Farm1_lat, Farm1_lon, Farm2_lat, Farm2_lon, Farm3_lat, \
    Farm3_lon, Farm4_lat, Farm4_lon, Farm5_lat, Farm5_lon, Digest_lat, Digest_lon)



#Total kilograms are the daily volumes supplied (m3) converted into mass (kg)
def total_kg(vol,conv):
    return vol*conv

kilos = total_kg(volume, vol_to_mass_conv)

#Weighted average calculation
def vol_breakdown(m1, p1, m2, p2, m3, p3, m4, p4, m5, p5):
    return (m1*p1 + m2*p2 + m3*p3 + m4*p4 + m5*p5)/(m1+m2+m3+m4+m5)

#Calculate the weighted average % of Total Solids of all the material supplied
total_solids_perc = vol_breakdown(man1, exp_1["Farm 1 % TS"], man2, exp_1["Farm 2 % TS"], \
    man3, exp_1["Farm 3 % TS"], man4, exp_1["Farm 4 % TS"], man5, exp_1["Farm 5 % TS"] )


#Calculate the weighted average % of cattle manure of all the material supplied
total_cattle_perc = vol_breakdown(man1, exp_1["Farm 1 cattle"], man2, exp_1["Farm 2 cattle"], \
    man3, exp_1["Farm 3 cattle"], man4, exp_1["Farm 4 cattle"], man5, exp_1["Farm 5 cattle"] )


#Calculate the weighted average % of pig manure of all the material supplied
total_pigs_perc = vol_breakdown(man1, exp_1["Farm 1 pigs"], man2, exp_1["Farm 2 pigs"], \
    man3, exp_1["Farm 3 pigs"], man4, exp_1["Farm 4 pigs"], man5, exp_1["Farm 5 pigs"] )

#Calculate the weighted average % of chicken manure of all the material supplied
total_chicks_perc = vol_breakdown(man1, exp_1["Farm 1 chicks"], man2, exp_1["Farm 2 chicks"], \
    man3, exp_1["Farm 3 chicks"], man4, exp_1["Farm 4 chicks"], man5, exp_1["Farm 5 chicks"] )

manure_comp = [total_cattle_perc, total_pigs_perc, total_chicks_perc]

print("Optimal location in radians for DIGESTOR is latitude: "+str(Digest_lat)+" and longitude: "+str(Digest_lon))
print("Total daily distance from farms to digestor travelled is "+str(distance_total)+" km")
print("Total VOLUME manure supplied per day is "+str(volume)+" m3")
print("Weighted average solids percentage of the manure supplied is "+str(total_solids_perc*100)+" %")
print("Manure composition is CATTLE-PIGS-CHICKS is "+str(manure_comp))


#print("Total daily distance from farms to digestor travelled is "+str(distance_total)+" km")
#print("Total VOLUME manure supplied per day is "+str(volume)+" m3")
#print("Total MASS manure supplied per day is "+str(kilos)+" kg")
#print("Weighted average solids percentage of the manure supplied is "+str(total_solids_perc*100)+" %")
#print("Manure composition is CATTLE-PIGS-CHICKS is "+str(manure_comp))
