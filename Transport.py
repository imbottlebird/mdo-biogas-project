#/Users/niekjansenvanrensburg/Documents/MDO/Ass3_code/mdo-biogas-project
import numpy as np
from scipy import spatial
import matplotlib.pyplot as plt
import pandas as pd
import cvxpy as cp
from math import sin, cos, sqrt, atan2, radians, pi
from constants import *
#Run "pip install scikit-opt" to get the Simulated Annealing program @ https://scikit-opt.github.io/scikit-opt/#/en/README?id=install
from sko.SA import SA_TSP

file_name = 'location_data.csv'
transport_data = np.loadtxt(file_name, delimiter=',')
points_coordinate = np.zeros((len(transport_data),2))
volume = np.zeros((len(transport_data)))
solids = np.zeros((len(transport_data)))
cattle = np.zeros((len(transport_data)))
pigs = np.zeros((len(transport_data)))
chicken = np.zeros((len(transport_data)))

for n in range(0,len(transport_data)):
    points_coordinate[n][0:2]=transport_data[n][0:2]
    volume[n]     = transport_data[n][2]
    solids[n]     = transport_data[n][3]
    cattle[n]     = transport_data[n][4]
    pigs[n]       = transport_data[n][5]
    chicken[n]    = transport_data[n][6]

print(points_coordinate)
print(volume)
print(solids)

num_points = points_coordinate.shape[0]
distance_matrix = spatial.distance.cdist(points_coordinate, points_coordinate, metric='euclidean')
distance_matrix = distance_matrix * 111 # 1 degree of lat/lon ~ = 111km
print(distance_matrix)

max_vol = np.argmax(volume, axis=0)
digestor_loc = points_coordinate[max_vol]
print(digestor_loc)

def cal_total_distance(routine):
    '''The objective function. input routine, return total distance.
    cal_total_distance(np.arange(num_points))
    '''
    num_points, = routine.shape
    #print("_________")
    return sum([distance_matrix[routine[i % num_points], routine[(i + 1) % num_points]] for i in range(num_points)])

sa_tsp = SA_TSP(func=cal_total_distance, x0=range(num_points), T_max=100, T_min=1, L=10 * num_points)

best_points, best_distance = sa_tsp.run()
print(best_points, best_distance, cal_total_distance(best_points))

#Total volumes (m3) are the daily volumes of all the farms per day
def total_vol(v):
    return (sum(v))

total_volume = total_vol(volume)

def vol_breakdown(volume, per):
    return sum(volume*per)/sum(volume)

total_solids_perc = vol_breakdown(volume, solids)
total_cattle_perc = vol_breakdown(volume, cattle)
total_pig_perc = vol_breakdown(volume, pigs)
total_chicken_perc = vol_breakdown(volume, chicken)
manure_comp = [total_cattle_perc, total_pig_perc, total_chicken_perc]

print("Optimal location in radians for DIGESTOR is latitude: "+str(digestor_loc[0])+" and longitude: "+str(digestor_loc[1]))
print("Total daily distance from farms to digestor travelled is "+str(best_distance)+" km")
print("Total VOLUME manure supplied per day is "+str(total_volume)+" m3")
print("Weighted average solids percentage of the manure supplied is "+str(total_solids_perc*100)+" %")
print("Manure composition is CATTLE-PIGS-CHICKS is "+str(manure_comp))


