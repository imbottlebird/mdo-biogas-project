# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 21:06:01 2021

@author: Ricardo Hopker
"""

# import integrating_modules
from cost_module_funcs2 import *

def tests(func,var,expected_value,err=0.01):
    x = func(*var)
    l_h = [expected_value-expected_value*err,expected_value+expected_value*err]
    low = min(l_h)
    high = max(l_h)
    return (x<high) & (x>low)

all_tests = []
#test for NPV
all_tests.append([npv,[10,2,0.1],8.26])
all_tests.append([npv,[10,1,0],10])
all_tests.append([npv,[10,2,0],10])
all_tests.append([npv,[20,3],15.88])
#test for total_npv
all_tests.append([total_npv,[10],39.9])
all_tests.append([total_npv,[5],19.96])
#Test V_year function
all_tests.append([V_year,[10],3650])
all_tests.append([V_year,[5],1825])
#test D function
all_tests.append([D,[10],3650])
all_tests.append([D,[20],7300])
# test total cost of transport
all_tests.append([c_t,[20],87440])
all_tests.append([c_t,[2530],11061204])
# test investement
all_tests.append([i,[30,True,1],72139])
all_tests.append([i,[10,True,2],78311])
all_tests.append([i,[30,False,1],45049])
all_tests.append([i,[10,False,2],67515])
# test cost of maintenance per year
all_tests.append([i_m,[30,True,1],9570.96])
all_tests.append([i_m,[10,True,2],9246.76])
all_tests.append([i_m,[30,False,1],5507.35])
all_tests.append([i_m,[10,False,2],7627.25])
# test total cost of maintenance
all_tests.append([c_m,[30,True,1],38214])
all_tests.append([c_m,[10,True,2],36919])
all_tests.append([c_m,[30,False,1],21989])
all_tests.append([c_m,[10,False,2],30453])
# test total savings in electrical engergy
all_tests.append([c_e,[150,1],599])
all_tests.append([c_e,[250,1],998])
all_tests.append([c_e,[150,20],11978])
all_tests.append([c_e,[250,20],19963])
all_tests.append([c_e,[150,0.5],300])
all_tests.append([c_e,[250,0.5],499])
# test total savings in fertilizer
all_tests.append([f_s,[150,1],599])
all_tests.append([f_s,[250,1],998])
all_tests.append([f_s,[150,20],11978])
all_tests.append([f_s,[250,20],19963])
all_tests.append([f_s,[150,0.5],300])
all_tests.append([f_s,[250,0.5],499])
# test fertilizer used
all_tests.append([w_l,[2,1],1])
all_tests.append([w_l,[10,20],-10])
# test energy produced
all_tests.append([e_p,[1],30.24])
all_tests.append([e_p,[523],15815])
# test J to kwH
all_tests.append([JtokWh,[100000],0.0277])
all_tests.append([JtokWh,[36000],0.01])
# test energy sold
all_tests.append([e_s,[20,300,50,100],288.5])
all_tests.append([e_s,[5,300,100,250],-189.6])
#test revenue
# V_gburn,e_c,h_needed,W_out,f_p,f_used,V_g
all_tests.append([r,[20,300,50,100,100,20,30],1080])
all_tests.append([r,[5,300,100,250,30,2,6],347.6])
#farmer npv
# farmer_npv(n_g,V_gburn,V_d,typ,distance_total,f_p,h_needed,W_out,V_g,e_c,e_priceB,f_used,p_bf)
n_g =1
V_gburn = 20
V_d = 50
typ = False
distance_total = 30
f_p =20
h_needed=30
W_out = 100
V_g = 30
all_tests.append([farmer_npv,[n_g,V_gburn,V_d,typ,distance_total,f_p,h_needed,W_out,V_g,e_c,e_priceB,f_used,p_bf],-197933])
n_g =2
V_gburn = 10
V_d = 15
typ = True
distance_total = 20
f_p =500
h_needed=100
W_out = 100
V_g = 30
all_tests.append([farmer_npv,[n_g,V_gburn,V_d,typ,distance_total,f_p,h_needed,W_out,V_g,e_c,e_priceB,f_used,p_bf],-200005])


result =[]
name = []
function_result = []
for test in all_tests:
    result.append(tests(*test))
    name.append([test[0].__name__])
    function_result.append(test[0](*test[1]))
    print(test[0].__name__ + ' '+ str(result[-1]))

df = pd.DataFrame(all_tests,columns=['function name','variables in','expected resuts'])
df['results'] = result
df['name']=name
df['function result']=function_result
df.to_csv(r'C:\Users\Ricardo Hopker\Massachusetts Institute of Technology\EM.428 MDO Biogas spring 2021 - General\Assignment A2\cost test table.csv')
# test_vector = [tests(npv,[P,n],10),