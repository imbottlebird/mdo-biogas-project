# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 11:34:16 2021

@author: Ricardo Hopker, Niek Jansen van Rensburg
"""
import pandas as pd
from scipy.integrate import odeint
import numpy as np
import matplotlib.pyplot as plt
from sko.GA import GA

from constants import *
from cost_module_funcs2 import do_all_list_cp,system_npv,JtokWh ,farmer_npv
from digesterModule import digester
import Transport as T
import biogas as B

# Variables we want to keep track in DOE
farm=[]
system=[]


# url=r'C:\Users\Ricardo Hopker\Massachusetts Institute of Technology\EM.428 MDO Biogas spring 2021 - General\Assignment A2'
# DOE = pd.read_csv(url+'\\DOE.csv')
DOE = pd.read_csv('DOE.csv')


# vector1 = [n_g,V_gburnP] #design variables
# DOE_vector = [vector1,vector2] #all design vectors for DOE
DOE_vector=[]
for i in range(0,18):
    vector =  DOE.loc[i].values.flatten().tolist()
    DOE_vector.append(vector[1:])
DOE_n = 0
def biodigestor(vector,printt=False,pen=True):
    #Use printt to print the text within your modules, when running the optimization it should be set to False
    #Use pen to penalize the function contraints being violated, when running the optimization it should be set to True
    # DOE_n = DOE_n+1
    # print('Design of experiment #%.0f' % (DOE_n))
    #Optimal latitude and longitude for Digestor
    Digest_lat = T.location_optimal(Farm1_lat, Farm2_lat, Farm3_lat, Farm4_lat, Farm5_lat)
    Digest_lon = T.location_optimal(Farm1_lon, Farm2_lon, Farm3_lon, Farm4_lon, Farm5_lon)
    
    #Total distance travelled per day in kms to deliver manure at digestor
    distance = T.total_distance(Farm1_lat, Farm1_lon, Farm2_lat, Farm2_lon, Farm3_lat, 
        Farm3_lon, Farm4_lat, Farm4_lon, Farm5_lat, Farm5_lon, Digest_lat, Digest_lon) 
    
    #Total volumes of manure (m3) per day transported to digestor
    # wIn = T.total_vol(man1, man2, man3, man4, man5)
    wIn = vector[3]
    
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
    #kilos = T.total_kg(wIn, vol_to_mass_conv)
    kilos = vector[4]
    #up to and including V_g are inputs
    #print(farmer_npv(V_d,typ,distance_total,f_p,h_needed,W_out,V_gburn,V_g,e_c,e_priceB,f_used,p_bf))
    
    # print("Optimal location for DIGESTOR is latitude: "+str(Digest_lat)+" and longitude: "+str(Digest_lon))
    # print("Total daily distance from farms to digestor travelled is "+str(distance)+" km")
    # print("Total VOLUME manure supplied per day is "+str(wIn)+" m3")
    # print("Weighted average solids percentage of the manure supplied is "+str(total_solids_perc*100)+" %")
    # print("Manure composition is CATTLE-PIGS-CHICKS is "+str(wComp))
    # print('----')
    
    #output from digester -- will return 9 values & print to console
    Tdig = vector[2]
    [W_a, typ, V_d, G_in, G_comp, digOut, digOut_comp, W_out, H_needed] = digester(wIn,wComp,Tdig)
    H_needed = JtokWh(H_needed*1000)
    # print('----')
    
    #biogas module
    V_g = B.biomethane(G_in, G_comp) #biomethane
    #bg = B.biomethane_validation(kilos, wComp)
    f_p = B.biofertilizer(digOut) 
    ghg_r, ghg_c = B.ghg(kilos, wComp, G_in, G_comp) #ghg_r: released gas, ghg_c: captured gas
    bgm_total = B.bgm_cost(G_comp, G_in, digOut)
    
    #print('Module biogas: ', G_in, 'Expected biogas: ', bg)
    # print("Produced biomethane: ", V_g)
    # print("Produced biofertilizer: ",f_p)
    # print("Released gas (g/tonne): ", ghg_r)
    # print("Captured gas (g/tonne): ", ghg_c)
    
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
    
    n_g = vector[1]
    V_gburn = vector[0]*V_g
    debt_level = vector[5]
    # print('----')
    # farm.append(farmer_npv(n_g,V_gburn,V_d,typ,distance,f_p,H_needed,W_out,V_g,debt_level,e_c,e_priceB,f_used,p_bf))
    # print('----')
    # system.append(system_npv(n_g,V_gburn,V_d,typ,distance,f_p,H_needed,W_out,V_g,debt_level,e_c,e_priceB,f_used,p_bf,list_ghg))
    # print('----')
    return -system_npv(n_g,V_gburn,V_d,typ,distance,f_p,H_needed,W_out,V_g,debt_level,e_c,e_priceB,f_used,p_bf,list_ghg,printt,pen)
# for vector in DOE_vector:
#     vector.extend([0.7])
#     system.append(biodigestor(vector))

# constraint_eq = []
# constraint_ueq = []
# ga = GA(func=biodigestor,n_dim=len(vector),size_pop=100,max_iter=50,lb=[0,1,20,0,0,0],ub=[1,3,30,10000,10000,0.8],precision=1)
# from sko.operators import ranking, selection, crossover, mutation
# ga.register(operator_name='ranking', operator=ranking.ranking). \
#     register(operator_name='crossover', operator=crossover.crossover_2point). \
#     register(operator_name='mutation', operator=mutation.mutation)  
# best_x, best_y = ga.run()
from geneticalgorithm import geneticalgorithm as ga # https://pypi.org/project/geneticalgorithm/
import timeit
def runGA():
    algorithm_param = {'max_num_iteration': 500,\
                    'population_size':100,\
                    'mutation_probability':.5,\
                    'elit_ratio': .01,\
                    'crossover_probability': .2,\
                    'parents_portion': .3,\
                    'crossover_type':'uniform',\
                    'max_iteration_without_improv':200}
    varbound =np.array([[0,1],[1,3],[20,30],[0,10000],[0,10000],[0,0.8]])
    start = timeit.default_timer()  
    var_type = np.array([['real'],['int'],['real'],['real'],['real'],['real']])   
    model2=ga(function=biodigestor,\
            dimension=len(vector),\
            variable_type_mixed=var_type,\
            variable_boundaries=varbound,\
            algorithm_parameters=algorithm_param)
    model2.run()
    stop = timeit.default_timer()
    print(stop-start)
    return model2
best = [6.26087460e-02, 1.00000000e+00, 2.80062435e+01, 9.99810434e+03,
       9.98127312e+03, 7.99307199e-01]
biodigestor(best,True)