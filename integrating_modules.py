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
from digesterModule2 import digester
import Transport as T
import biogas as B
import pickle
from math import inf
import scipy.optimize as op

# Variables we want to keep track in DOE
# farm=[]
# system=[]
# with open('data_transport.p', 'rb') as fp:
#     dict_T = pickle.load(fp)
with open('full_transp.p', 'rb') as fp:
    dict_T = pickle.load(fp)


# DOE = pd.read_csv('DOE.csv')
#  #Variables below are which farms should be activated

# DOE_vector=[]
# for i in range(0,18):
#     vector =  DOE.loc[i].values.flatten().tolist()
#     DOE_vector.append(vector[1:])
# DOE_n = 0
def biodigestor(vector,lam = 1,multiJ =False,full=False,printt=False,pen=True):
    #Use printt to print the text within your modules, when running the optimization it should be set to False
    #Use pen to penalize the function contraints being violated, when running the optimization it should be set to True
    # DOE_n = DOE_n+1
    # print('Design of experiment #%.0f' % (DOE_n))
    #Optimal latitude and longitude for Digestor
    #Digest_location = T.digestor_loc

    #This loads the respective farms - 1 is active, 0 is inactive. Total farms must be at least 3 active (required by annealing)
    #TOTAL_SOLIDS PERCENTAGE IS NOT USED
    active_farms= vector[5:12] 
    active_farms = [0 if num<1 or num==False  else 1 for num in active_farms]
    # [distance, wIn, total_solids_perc, wComp] = T.load_data(1,1,1,1,1,1,1)
    # [distance, wIn, total_solids_perc, wComp] = T.load_data(*active_farms,printt)
    # if sum(active_farms)>2:
    if printt:
        [distance, wIn, total_solids_perc, wComp] = T.load_data(*active_farms,printt)
    else:
        [distance, wIn, total_solids_perc, wComp] = dict_T[tuple(active_farms)]
    # else:
    #     [distance, wIn, total_solids_perc, wComp] = [inf,0,0,[1,0,0]]
    # [distance, wIn, total_solids_perc, wComp] = T.load_data(vector[6],vector[7],vector[8],
    #                                                         vector[9],vector[10],vector[11],vector[12])

    

    #kilos = T.total_kg(wIn, vol_to_mass_conv)
    #up to and including V_g are inputs

    
    #output from digester -- will return 9 values & print to console
    Tdig = vector[2]
    [W_a, typ, V_d, G_in, G_comp, digOut, digOut_comp] = digester(wIn,wComp,Tdig)
    # H_needed = JtokWh(H_needed*1000)
    # print('----')
    
    #biogas module
    V_g = B.biomethane(G_in, G_comp) #biomethane
    #bg = B.biomethane_validation(kilos, wComp)
    f_p = B.biofertilizer(digOut) 
    ghg_r, ghg_c = B.ghg(W_a, wComp, G_in, G_comp) #ghg_r: released gas, ghg_c: captured gas
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
    gwpS =0
    for gas in ['CH4','CO2','NOX','SOX']:
        list_ghg.append(ghg[ghg['gas']==gas].values.flatten().tolist())
        gwpS = gwpS + gwp(ghg[ghg['gas']==gas]['ghg_lf'].values,gas)
    list_ghg = do_all_list_cp(W_a,distance,list_ghg)
    
    n_g = vector[1]
    V_gburn = vector[0]*V_g
    debt_level = vector[3]
    # print('----')
    # farm.append(farmer_npv(n_g,V_gburn,V_d,typ,distance,f_p,H_needed,W_out,V_g,debt_level,e_c,e_priceB,f_used,p_bf))
    # print('----')
    # system.append(system_npv(n_g,V_gburn,V_d,typ,distance,f_p,H_needed,W_out,V_g,debt_level,e_c,e_priceB,f_used,p_bf,list_ghg))
    # print('----')
    # return -system_npv(n_g,V_gburn,V_d,typ,distance,f_p,H_needed,W_out,V_g,debt_level,e_c,e_priceB,f_used,p_bf,list_ghg,printt,pen)
    V_cng_p = vector[4]
    farmerNPV = farmer_npv(n_g,V_gburn,V_cng_p,V_d,typ,distance,f_p,V_g,debt_level,e_c,e_priceB,e_priceS,f_used,p_bf,printt,pen)
    if multiJ:
        if full:
            return [-farmerNPV*lam-(1-lam)*gwpS,-farmerNPV,-gwpS]
        else: return -farmerNPV*lam-(1-lam)*gwpS
    else: return -farmerNPV
    # return -farmerNPV*lam-(1-lam)*gwpS
# for vector in DOE_vector:
#     vector.extend([0.7])
#     system.append(biodigestor(vector))
def gwp(x,gas): # https://www.epa.gov/ghgemissions/understanding-global-warming-potentials
    if gas == 'CH4':
        return x*32
    elif gas == 'CO2':
        return x
    elif gas =='NOX':
        return x*281.5
    elif gas =='SOX':
        return x*281.5
    else:
        raise NotImplementedError
# GA from scikit-optimize

# constraint_eq = []
# constraint_ueq = []
# ga = GA(func=biodigestor,n_dim=len(vector),size_pop=100,max_iter=50,lb=[0,1,20,0,0,0],ub=[1,3,30,10000,10000,0.8],precision=1)
# from sko.operators import ranking, selection, crossover, mutation
# ga.register(operator_name='ranking', operator=ranking.ranking). \
#     register(operator_name='crossover', operator=crossover.crossover_2point). \
#     register(operator_name='mutation', operator=mutation.mutation)  
# best_x, best_y = ga.run()

# GA that we us

from geneticalgorithm import geneticalgorithm as ga # https://pypi.org/project/geneticalgorithm/
import timeit
def runGA(vector):
    algorithm_param = {'max_num_iteration': 100,\
                    'population_size': 500,\
                    'mutation_probability': .6,\
                    'elit_ratio': .02,\
                    'crossover_probability': .1,\
                    'parents_portion': .4,\
                    'crossover_type':'uniform',\
                    'max_iteration_without_improv':50}
    varbound =np.array([[0,1],[1,2],[20,40],[0,0.8],[0,1],
                        [0,1],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1]])
    #[V_gBurn,ng,Tdig,debt_level,V_cng_p,farm1,farm2,farm3,farm4,farm5,farm6,farm7]
    start = timeit.default_timer()  
    var_type = np.array([['real'],['int'],['real'],['real'],['real'],
                          ['int'],['int'],['int'],['int'],['int'],['int'],['int']])   
    model2=ga(function=biodigestor,\
            dimension=len(vector),\
            variable_type_mixed=var_type,\
            variable_boundaries=varbound,\
            function_timeout =600,\
            algorithm_parameters=algorithm_param)
    model2.run()
    stop = timeit.default_timer()
    print('Run time: '+str(stop-start)+' second')
    return model2
def cleanXopt(xopt_in):
    xopt = xopt_in.copy()
    if xopt[0]>1: xopt[0]=1
    elif xopt[0]<0: xopt[0]=0
    xopt[1] = round(xopt[1],0)
    if xopt[1]<1: xopt[1]=1
    if xopt[3]>1: xopt[3]=1
    elif xopt[3]<0: xopt[3]=0
    if xopt[4]>1: xopt[4]=1
    elif xopt[4]<0: xopt[4]=0
    for i in range(5,12):
        if xopt[i]>1: xopt[i]=1
        elif xopt[i]<1: xopt[i]=0
    return xopt
def cleanBiodigestor(x,lam = 1,multiJ =False,full=False,printt=False,pen=True):
    X = cleanXopt(x)
    return biodigestor(X,lam,multiJ,full,printt,pen)
def fminClean(x0,args):
    xopt = op.fmin(func=cleanBiodigestor,x0=best,args=args)
    return xopt
# best = [4.83662871e-01, 1.00000000e+00, 2.62359775e+01, 
#             1.11820675e-03, 1.00000000e+00, 0.00000000e+00,0.00000000e+00, 
#             1.00000000e+00, 0.00000000e+00, 1.00000000e+00,0.00000000e+00]
# biodigestor(best,True,False)
# args = (0.01,True,False,False,True)
# mod = runGA(best)
# biodigestor(mod.best_variable,True,False)
# mod_best = [1.72039083e-01, 1.00000000e+00, 3.84795466e+01, 3.21167571e-03,
#         1.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
#         0.00000000e+00, 0.00000000e+00, 0.00000000e+00]

# fminsearch but Python
best = [1.72039083e-01, 1.00000000e+00, 3.84795466e+01, 3.21167571e-03,0.16,
        1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
        1.00000000e+00, 0.00000000e+00, 0.00000000e+00]
# args = (1,True,False,False,True)
# # mod = runGA(best)
# cleanBiodigestor(best,*args)
# xopt = fminClean(best,args)
# # xopt = op.fmin(func=cleanBiodigestor,x0=best,args=args)
# # # xopt = op.fmin(func=cleanBiodigestor,x0=best)
# xopt = cleanXopt(xopt)
# print(xopt)
# biodigestor(xopt,0.5,True)

def biodigestorNPV0(vector,printt=False,pen=True):
    active_farms= vector[6:13] 
    active_farms = [0 if num<1 or num==False  else 1 for num in active_farms]
    if printt:
        [distance, wIn, total_solids_perc, wComp] = T.load_data(*active_farms,printt)
    else:
        [distance, wIn, total_solids_perc, wComp] = dict_T[tuple(active_farms)]

    Tdig = vector[2]
    [W_a, typ, V_d, G_in, G_comp, digOut, digOut_comp] = digester(wIn,wComp,Tdig)

    V_g = B.biomethane(G_in, G_comp) #biomethane
    #bg = B.biomethane_validation(kilos, wComp)
    f_p = B.biofertilizer(digOut) 
    ghg_r, ghg_c = B.ghg(W_a, wComp, G_in, G_comp) #ghg_r: released gas, ghg_c: captured gas
    bgm_total = B.bgm_cost(G_comp, G_in, digOut)
    
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
    debt_level = vector[3]

    V_cng_p = vector[4]
    e_priceSS = vector[5]
    # farmer_npv(n_g,V_gburn,V_d,typ,distance_total,f_p,V_g,debt_level,e_c,e_priceB,e_priceS,f_used,p_bf)
    return -farmer_npv(n_g,V_gburn,V_cng_p,V_d,typ,distance,f_p,V_g,debt_level,e_c,e_priceB,e_priceSS,f_used,p_bf,printt,pen)
def cleanXoptNPV0(xopt_in):
    xopt = xopt_in.copy()
    if xopt[0]>1: xopt[0]=1
    elif xopt[0]<0: xopt[0]=0
    xopt[1] = round(xopt[1],0)
    if xopt[3]>1: xopt[3]=1
    elif xopt[3]<0: xopt[3]=0
    if xopt[4]>1: xopt[4]=1
    elif xopt[4]<0: xopt[4]=0
    if xopt[5]<0: xopt[5]=0
    for i in range(6,13):
        if xopt[i]>1: xopt[i]=1
        elif xopt[i]<1: xopt[i]=0
    return xopt
def NPV0goal(x):
    X = cleanXoptNPV0(x)
    return biodigestorNPV0(X)**2
def runNPV0():
    x0 = [1, 1.00000000e+00, 3.84795466e+01, 3.21167571e-03, 0,0.35,
        1.00000000e+00, 1.00000000e+00, 1.00000000e+00,1.00000000e+00,
        0.00000000e+00, 0.00000000e+00, 0.00000000e+00]
    xopt = op.fmin(func=NPV0goal,x0=x0)
    return xopt
# xNPV0 =cleanXoptNPV0(runNPV0())
# print(xNPV0)
# print(biodigestorNPV0(xNPV0))
# biodigestorNPV0([ 1.        ,  1.        , 49.23933306,  0.        ,  0.        ,
#        20,  1.        ,  0.        ,  0.        ,  0.        ,
#         0.        ,  0.        ,  0.        ])
    #[V_gBurn,ng,Tdig,debt_level,V_cng_p,e_priceS,farm1,farm2,farm3,farm4,farm5,farm6,farm7]
# xopt = runNPV0()
# xopt = [ 1, 1,  2.48427792e+01,  0,
#         1, 0, 0,  1,
#         0,  1,  0]
# xopt = [ 5.13617781e-01,  1,  3.70900619e+01, 0,
        # 1,  0,  0,  0,
        # 0, 0, 0]
# biodigestor(xopt,True,False)
# out = biodigestor(vec,False,False)


