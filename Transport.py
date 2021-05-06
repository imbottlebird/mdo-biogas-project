import numpy as np
from scipy import spatial
import matplotlib.pyplot as plt
import pandas as pd
import cvxpy as cp
from math import sin, cos, sqrt, atan2, radians, pi
from constants import *
#Run "pip install scikit-opt" to get the Simulated Annealing program @ https://scikit-opt.github.io/scikit-opt/#/en/README?id=install
from sko.SA import SA_TSP


def optimal_loc(locations, vol, m):
    if len(locations)==1:
        return [locations[m]]
    else: 
        l = locations.copy()
        #print(l)
        perc_vol = vol/sum(vol)
        #print(perc_vol)
        for s in range(len(l)):
            l[s]=l[s]*perc_vol[s]
        #print(locations)
        new_loc = [np.sum(l,axis=0)]
        #print(type(new_loc))
        #print(new_loc)
        distances = spatial.distance.cdist(locations, new_loc,  metric='euclidean')*111
        #print(distances)
        #print("++++++++++++++++++++")
        min_digest_dist = np.argmin(distances, axis=0)
        #print(min_digest_dist[0])
        #print([locations[min_dist]])
        return [locations[min_digest_dist[0]]]

def total_vol(v):
    return (sum(v))

def vol_breakdown(volume, per):
    return sum(volume*per)/sum(volume)

def load_data(f1=1,f2=1,f3=1,f4=1,f5=1,f6=1,f7=1,printt=False):
    file_name = 'location_data.csv'
    data = np.loadtxt(file_name, delimiter=',')
    transport_data = []
    if f1==1:
        transport_data.append(data[0])
    if f2==1:
        transport_data.append(data[1])
    if f3==1:
        transport_data.append(data[2])
    if f4==1:
        transport_data.append(data[3])
    if f5==1:
        transport_data.append(data[4])
    if f6==1:
        transport_data.append(data[5])
    if f7==1:
        transport_data.append(data[6])

    points_coordinate = np.zeros((len(transport_data),2))
    volume = np.zeros((len(transport_data)))
    solids = np.zeros((len(transport_data)))
    cattle = np.zeros((len(transport_data)))
    pigs = np.zeros((len(transport_data)))
    chicken = np.zeros((len(transport_data)))
    truck_vol = 18 #truck has capacity of 18m3 

    for n in range(0,len(transport_data)):
        points_coordinate[n][0:2]=transport_data[n][0:2]
        volume[n]     = transport_data[n][2]
        solids[n]     = transport_data[n][3]
        cattle[n]     = transport_data[n][4]
        pigs[n]       = transport_data[n][5]
        chicken[n]    = transport_data[n][6]

    max_vol = np.argmax(volume, axis=0)

    digestor_loc = optimal_loc(points_coordinate,volume,max_vol)
    #print(type(digestor_loc))
    
    num_points = points_coordinate.shape[0]

    distance_matrix = spatial.distance.cdist(points_coordinate, points_coordinate, metric='euclidean')
    distance_matrix = distance_matrix * 111 # 1 degree of lat/lon ~ = 111km
    #print(distance_matrix)

    distance_home = spatial.distance.cdist(points_coordinate, digestor_loc,  metric='euclidean')*111

    def cal_total_distance(routine):
        '''The objective function. input routine, return total distance.
        cal_total_distance(np.arange(num_points))
        '''
        num_points, = routine.shape
        trip_vol = 0
        dist = 0
        for i in range(num_points):
            trip_vol = trip_vol + volume[routine[i % num_points]]
            trips = 0
            dist_home = 0
            if trip_vol>truck_vol:
                trips = trip_vol // truck_vol
                trip_vol = trip_vol % truck_vol
                dist_home = dist_home + int(distance_home[routine[i % num_points]])
            dist += distance_matrix[routine[i % num_points], routine[(i + 1) % num_points]] + 2*dist_home
        return dist

    if f1+f2+f3+f4+f5+f6+f7 >2:
        sa_tsp = SA_TSP(func=cal_total_distance, x0=range(num_points), T_max=100, T_min=1, L=10 * num_points) 
        best_points, best_distance = sa_tsp.run()
    elif f1+f2+f3+f4+f5+f6+f7 ==2:
        best_points = np.array([0,1])
        best_distance = cal_total_distance(best_points)
    elif f1+f2+f3+f4+f5+f6+f7 ==1:
        best_points = np.array([0])
        best_distance = 0
            

    def best_points_route(best_points, start):
        '''The objective function. input routine, return total distance.
        cal_total_distance(np.arange(num_points))
        '''
        num_points, = best_points.shape
        new_route = [start]
        trip_vol = 0
        dist = 0
        for i in range(num_points):
            trip_vol = trip_vol + volume[best_points[i % num_points]]
            trips = 0
            dist_home = 0
            new_route.append(best_points[i])
            if best_points[i % num_points]==max_vol:
                trips = 0
                trip_vol = 0
            if (trip_vol>truck_vol) & (best_points[i % num_points]!=max_vol):
                trips = trip_vol // truck_vol
                trip_vol = trip_vol % truck_vol
                dist_home = dist_home + int(distance_home[best_points[i % num_points]])
                new_route.append(max_vol)
                new_route.append(best_points[i % num_points])
                trips = 0
            dist = dist + distance_matrix[best_points[i % num_points], best_points[(i + 1) % num_points]] + 2*dist_home
        return new_route

    final_best = best_points_route(best_points, max_vol)

    #Total volumes (m3) are the daily volumes of all the farms per day
    total_volume = total_vol(volume)
    total_solids_perc = vol_breakdown(volume, solids)
    total_cattle_perc = vol_breakdown(volume, cattle)
    total_pig_perc = vol_breakdown(volume, pigs)
    total_chicken_perc = vol_breakdown(volume, chicken)
    manure_comp = [total_cattle_perc, total_pig_perc, total_chicken_perc]

    from matplotlib.ticker import FormatStrFormatter

    if (final_best[-1])!=max_vol:
        final_best.append(max_vol)
    best_points_ = np.array(final_best)
    best_points_coordinate = points_coordinate[best_points_, :]
    if printt:
        print("The best route is: "+str(final_best)+" and the distance on this route is "+str(best_distance))
        print("Optimal location is area # "+str(max_vol)+" in radians for DIGESTOR is latitude: "+str(digestor_loc[0][0])+" and longitude: "+str(digestor_loc[0][1]))
        print("Total daily distance from farms to digestor travelled is "+str(best_distance)+" km")
        print("Total VOLUME manure supplied per day is "+str(total_volume)+" m3")
        print("Weighted average solids percentage of the manure supplied is "+str(total_solids_perc*100)+" %")
        print("Manure composition is CATTLE-PIGS-CHICKS is "+str(manure_comp))
   
        fig, ax = plt.subplots(1, 2)
        ax[0].plot(sa_tsp.best_y_history)
        ax[0].set_xlabel("Iteration")
        ax[0].set_ylabel("Distance")
        ax[1].plot(best_points_coordinate[:, 0], best_points_coordinate[:, 1],
          marker='o', markerfacecolor='b', color='c', linestyle='-')
        ax[1].xaxis.set_major_formatter(FormatStrFormatter('%.3f'))
        ax[1].yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
        ax[1].set_xlabel("Longitude")
        ax[1].set_ylabel("Latitude")
        plt.show()

    return [best_distance, total_volume, total_solids_perc, manure_comp]

[distance, wIn, total_solids_perc, wComp] = load_data(1,1,1,1,1,1,1, False)