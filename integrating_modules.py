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
# DOE = pd.read_csv('DOE.csv')
#  #Variables below are which farms should be activated

# # vector1 = [n_g,V_gburnP] #design variables
# # DOE_vector = [vector1,vector2] #all design vectors for DOE
# DOE_vector=[]
# for i in range(0,18):
#     vector =  DOE.loc[i].values.flatten().tolist()
#     DOE_vector.append(vector[1:])
DOE_n = 0
def biodigestor(vector,printt=False,pen=True):
    #Use printt to print the text within your modules, when running the optimization it should be set to False
    #Use pen to penalize the function contraints being violated, when running the optimization it should be set to True
    # DOE_n = DOE_n+1
    # print('Design of experiment #%.0f' % (DOE_n))
    #Optimal latitude and longitude for Digestor
    #Digest_location = T.digestor_loc

    #This loads the respective farms - 1 is active, 0 is inactive. Total farms must be at least 3 active (required by annealing)
    #TOTAL_SOLIDS PERCENTAGE IS NOT USED
    active_farms= vector[5:12] 
    active_farms = [0 if num<1 or num==False  else 1 for num in active_farms ]
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
    for gas in ['CH4','CO2','NOX','SOX']:
        list_ghg.append(ghg[ghg['gas']==gas].values.flatten().tolist())
    list_ghg = do_all_list_cp(W_a,distance,list_ghg)
    
    n_g = vector[1]
    V_gburn = vector[0]*V_g
    debt_level = vector[3]
    V_cng_p = vector[4]
    return -farmer_npv(n_g,V_gburn,V_cng_p,V_d,typ,distance,f_p,V_g,debt_level,e_c,e_priceB,f_used,p_bf,printt,pen)
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
def runGA(vector):
    algorithm_param = {'max_num_iteration': 500,\
                    'population_size':100,\
                    'mutation_probability':.5,\
                    'elit_ratio': .01,\
                    'crossover_probability': .2,\
                    'parents_portion': .3,\
                    'crossover_type':'uniform',\
                    'max_iteration_without_improv':200}
    varbound =np.array([[0,1],[1,2],[20,40],[0,0.8],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1]])
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
    if xopt[3]>1: xopt[3]=1
    elif xopt[3]<0: xopt[3]=0
    if xopt[4]>1: xopt[4]=1
    elif xopt[4]<0: xopt[4]=0
    for i in range(5,12):
        if xopt[i]>1: xopt[i]=1
        elif xopt[i]<1: xopt[i]=0
    return xopt
best = [0.05, 1.00000000e+00, 3.69047e+01, 
            0, 0,1.00000000e+00, 0.00000000e+00,0.00000000e+00, 
            0, 0.00000000e+00, 1.00000000e+00,0.00000000e+00] #[V_gBurn,ng,Tdig,debt_level,V_cng_p,farm1,farm2,farm3,farm4,farm5,farm6,farm7]
biodigestor(best,True,True)
# mod = runGA(best)
# biodigestor(mod.best_variable,True,False)
mod_best = np.array([9.98093589e-01, 1.00000000e+00, 3.69458953e+01, 4.70171351e-03,
        2.12949571e-03, 1.00000000e+00, 0.00000000e+00, 0.00000000e+00,
        0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00])
import scipy.optimize as op
# xopt,fopt,ite,funccalls,warnflag,allvecs = op.fmin(func=biodigestor,x0=mod_best,full_output=1,disp=True,retall=True)
# xopt = cleanXopt(xopt)
xopt=np.array([1.00000000e+00, 1.00000000e+00, 3.69039048e+01, 0.00000000e+00,
       7.24157048e-05, 1.00000000e+00, 0.00000000e+00, 0.00000000e+00,
       0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00])
f = biodigestor(xopt,True,True)

def cleanXopt(xopt_in):
    xopt = xopt_in.copy()
    if xopt[0]>1: xopt[0]=1
    elif xopt[0]<0: xopt[0]=0
    xopt[1] = round(xopt[1],0)
    if xopt[3]>1: xopt[3]=1
    elif xopt[3]<0: xopt[3]=0
    if xopt[4]>1: xopt[4]=1
    elif xopt[4]<0: xopt[4]=0
    for i in range(5,12):
        if xopt[i]>1: xopt[i]=1
        elif xopt[i]<1: xopt[i]=0
    return xopt
    

# XOPT =[]
# FOPT=[]
# ITE =[]
# FUNCALLS = []
# WARN = []
# ALLVECT = []
# count = 0
# xDOE=[[0.05,1,20,0,1,1,1,1,1,1,1],
#       [.5,1,20,0,1,1,1,1,1,1,1],
#        [0.05,1,25,0,1,1,1,1,1,1,1],
#        [0.05,1,20,0.5,1,1,1,1,1,1,1],
#        [0.05,1,20,0,1,0,1,1,1,1,1],
#         [0.05,1,20,0,1,0,0,1,1,1,1],
#         [0.05,1,20,0,1,0,0,0,1,1,1],
#         [0.05,1,20,0,1,0,0,0,0,1,1],
#         [0.05,1,20,0,1,0,0,0,0,0,1],
#         [0.05,1,20,0,1,0,0,0,0,0,0],
#         [0.05,1,20,0,0,0,0,0,1,0,0]
#       ]
# for x0 in xDOE:
#     start = timeit.default_timer() 
#     xopt,fopt,ite,funccalls,warnflag,allvecs = op.fmin(func=biodigestor,x0=x0,full_output=1,disp=True,retall=True)
#     XOPT.append(xopt)
#     FOPT.append(fopt)
#     ITE.append(ite)
#     FUNCALLS.append(funccalls)
#     WARN.append(warnflag)
#     ALLVECT.append(allvecs)
#     count +=1
#     print(count/len(xDOE))
#     stop = timeit.default_timer()
#     print('Run time: '+str(stop-start)+' seconds')
# with open('XOPT.pkl', 'wb') as file:
#       file.write(pickle.dumps(XOPT))
# with open('FOPT.pkl', 'wb') as file:
#       file.write(pickle.dumps(FOPT))
# with open('ITE.pkl', 'wb') as file:
#       file.write(pickle.dumps(ITE))
# with open('FUNCALLS.pkl', 'wb') as file:
#       file.write(pickle.dumps(FUNCALLS))
# with open('WARN.pkl', 'wb') as file:
#       file.write(pickle.dumps(WARN))
# with open('ALLVECT.pkl', 'wb') as file:
#       file.write(pickle.dumps(ALLVECT))
# fallVect = []
# count = 0
# for vec in ALLVECT:
#     fvec=[]
#     print(count/len(ALLVECT))
#     count+=1
#     for xas in vec:
#         fvec.append(biodigestor(xas,False,False))
#     fallVect.append(fvec)
# df = pd.DataFrame(XOPT) 
# df=df.transpose()
# for i in fallVect:
#     plt.plot(i)
#     plt.show()
# with open('FALLVECT.pkl', 'wb') as file:
#       file.write(pickle.dumps(fallVect))
# xopt = [ 1, 1,  2.48427792e+01,  0,
#         1, 0, 0,  1,
#         0,  1,  0]
# xopt = [ 5.13617781e-01,  1,  3.70900619e+01, 0,
        # 1,  0,  0,  0,
        # 0, 0, 0]
# biodigestor(xopt,True,False)
# out = biodigestor(vec,False,False)
# def jacobian(expr,vec):
#     out = []
#     for exp in expr:
#         outJ = []
#         for var in vec:
#             if type(var) == sp.core.symbol.Symbol:
#                 outJ.append(exp.diff(var))
#         out.append(outJ)
#     return out
# def hessian(jacobian,vec):
#     out = []
#     for jac_vect in jacobian:
#             hesM = []
#             for var in vec:
#                 if type(var) == sp.core.symbol.Symbol:
#                     outH = []
#                     for exp in jac_vect:
#                         outH.append(exp.diff(var))
#                     hesM.append(outH)
#             out.append(hesM)
#     return out
# def sub_var(expr,var,value):
#     exprR = np.reshape(np.array(expr),(-1))
#     out = []
#     for exp in exprR:
#         out.append(exp.subs(var,value))
#     out=np.array(out)
#     return np.reshape(out,np.array(expr).shape)
# def sub_all_var(expr,vec,value):
#     vec_value = zip(vec,value)
#     out= expr
#     for var,val in vec_value:
#         if type(var) == sp.core.symbol.Symbol:
#             out = sub_var(out,var,val)
#     return out
# def newton_method(expr,x0,vec,it_max=200,err=10**-3):
#     jac = jacobian([expr],vec)
#     hes = hessian(jac,vec)
#     hes = np.array(hes[0])
#     it = 0
#     xi =x0
#     while it<=it_max:
#         Ji = np.array(sub_all_var(expr,vec,xi)).astype(np.float64)
#         jac_xi = np.array(sub_all_var(jac,vec,xi)).astype(np.float64)
#         hes_xi = np.array(sub_all_var(hes,vec,xi)).astype(np.float64)
#         dx = -np.linalg.inv(hes_xi)*jac_xi
#         xi_1 = xi+dx
#         Ji_1 = np.array(sub_all_var(expr,vec,xi_1)).astype(np.float64)
#         if Ji_1-Ji<err:
#             return Ji_1
#         xi = xi_1
#     return Ji_1
        
# xxx = newton_method(out,best,vec)
# jac = jacobian([out],vec)
# hes = hessian(jac,vec)
# hes = np.array(hes[0])
# hes1 = sub_var(hes,debt_l,0.8)
# hes2 = sub_var(hes1,w_in,100)
# hes3 = sub_var(hes2,kilos,100)
# hes4 = sub_var(hes3,Vg_burn,0.5)
# hes5 = sub_var(hes4,n_G,1)
# eigen = np.linalg.eig(np.array(hes5).astype(np.float64))

