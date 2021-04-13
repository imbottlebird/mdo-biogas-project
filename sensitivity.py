import pandas as pd
from scipy.integrate import odeint
import numpy as np
import matplotlib.pyplot as plt
from sko.GA import GA

from constants import *
from cost_module_funcs2 import do_all_list_cp,system_npv,JtokWh ,farmer_npv
from digesterModule import digester
import cost_module_funcs2 as C2
import Transport as T
import biogas as B
import pickle
from math import inf

# Variables we want to keep track in DOE
farm=[]
system=[]
# with open('data_transport.p', 'rb') as fp:
#     dict_T = pickle.load(fp)
with open('full_transp.p', 'rb') as fp:
    dict_T = pickle.load(fp)

# url=r'C:\Users\Ricardo Hopker\Massachusetts Institute of Technology\EM.428 MDO Biogas spring 2021 - General\Assignment A2'
# DOE = pd.read_csv(url+'\\DOE.csv')
DOE = pd.read_csv('DOE.csv')
 #Variables below are which farms should be activated

# vector1 = [n_g,V_gburnP] #design variables
# DOE_vector = [vector1,vector2] #all design vectors for DOE
# DOE_vector=[]
# for i in range(0,18):
#     vector =  DOE.loc[i].values.flatten().tolist()
#     DOE_vector.append(vector[1:])

# DOE_n = 0


import matplotlib.pyplot as plt
import autograd.numpy as np

# A0 = 1.0
# def A(t, k1, k_1):



def biodigestor(DV2_ng,printt=False,pen=True):
    #Use printt to print the text within your modules, when running the optimization it should be set to False
    #Use pen to penalize the function contraints being violated, when running the optimization it should be set to True
    # DOE_n = DOE_n+1
    # print('Design of experiment #%.0f' % (DOE_n))
    #Optimal latitude and longitude for Digestor
    #Digest_location = T.digestor_loc

    #This loads the respective farms - 1 is active, 0 is inactive. Total farms must be at least 3 active (required by annealing)
    #TOTAL_SOLIDS PERCENTAGE IS NOT USED
    vector = [4.83662871e-01, 1.00000000e+00, 2.62359775e+01, 
            1.11820675e-03, 1.00000000e+00, 0.00000000e+00,0.00000000e+00, 
            1.00000000e+00, 0.00000000e+00, 1.00000000e+00,0.00000000e+00]
    print('vector',vector)
    active_farms= vector[4:11] 
    active_farms = [0 if num<1 else 1 for num in active_farms ]
    # [distance, wIn, total_solids_perc, wComp] = T.load_data(1,1,1,1,1,1,1)
    # [distance, wIn, total_solids_perc, wComp] = T.load_data(*active_farms,printt)
    # if sum(active_farms)>2:
    if printt:
        [distance, wIn, total_solids_perc, wComp] = T.load_data(*active_farms,printt)
    else:
        [distance, wIn, total_solids_perc, wComp] = dict_T[tuple(active_farms)]
    
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
    
    #COST Module
    V_g =V_g*working_days
    ghg = pd.DataFrame()
    ghg['ghg_lf']=ghg_r
    ghg['ghg_tech']=ghg_c
    ghg['gas']= ['CH4','CO2','NOX','SOX']
    list_ghg = []
    for gas in ['CH4','CO2','NOX','SOX']:
        list_ghg.append(ghg[ghg['gas']==gas].values.flatten().tolist())
    list_ghg = do_all_list_cp(W_a,distance,list_ghg)
    
    n_g = DV2_ng
    #print("n_g",n_g)
    V_gburn = vector[0]*V_g
    #print('vector[0]',vector[0])
    debt_level = vector[3]
    
    return -farmer_npv(n_g,V_gburn,V_d,typ,distance,f_p,V_g,debt_level,e_c,e_priceB,f_used,p_bf,printt,pen)




# t = np.linspace(0, 0.5)
# k1 = 
# k_1 = 3.0

import numpy as np

ngs = np.linspace(1, 5,5)

returned_v = []
for ng in ngs:
    returned_v.append(biodigestor(ng))

print('return',returned_v)


plt.plot(ngs, returned_v)
plt.xlim([0, 0.5])
plt.ylim([0, 1])
plt.xlabel('t')
plt.ylabel('A')



# import autograd.numpy as np
# A0 = 1.0
# def A(t, k1, k_1):
#     return A0 / (k1 + k_1) * (k1 * np.exp(-(k1 + k_1) * t) + k_1)
# %matplotlib inline
# import matplotlib.pyplot as plt
# t = np.linspace(0, 0.5)
# k1 = 3.0
# k_1 = 3.0
# plt.plot(t, A(t, k1, k_1))
# plt.xlim([0, 0.5])
# plt.ylim([0, 1])
# plt.xlabel('t')
# plt.ylabel('A')