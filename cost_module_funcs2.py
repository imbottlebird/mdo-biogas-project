# -*- coding: utf-8 -*-
"""
Created on Sun Mar 21 19:38:02 2021

@author: Ricardo Hopker
"""
#inputs from other modules, my initial guesses
# V_d = 50
# # d = 50
# V_day = 500000/330
# e_p = 5000000
# f_p =50000
# #V_f = 1000000
# V_g = 600000
# W_a = 1000000
# typ = 0 #type of digestor [1] --> upflow [0]--> covered lagoon 
# distance_total = 1388888/330 #km
# h_needed = 10000
# W_out = 10000

# nox_lf = 1
# sox_lf = 1 
# pm_lf = 1 
# ch4_lf = 1 
# co2_lf = 1 
# nox_tech = 0.5
# sox_tech = 0.5
# pm_tech = 0.5 
# ch4_tech = 0.5 
# co2_tech = 0.5
# all_gas_list = [[10,2,5,3,5],[10,6,3,1,3]]
#Optimizable
# n_g = 1 #natural number, # of generators
# V_gburn = 1000


# #Constants
# a_d = 941 #R$/m^3
# b_d = 18900 #R$
# p_f = 3.53 #R$/L
# p_g = 3.05 #R$/kg
# pl
# e_priceS = 0 #R$/kWh
# p_bf = 14.5 #R$/kg
# f_used = 8000 #kg/ha
# e_c = 121200 #kWh/year
# e_priceB = 0.59 #R$/kWh
# L = 5 # years
# k = 0.08 #interest, expected return
# g_d = 25000 # R$/Generator (36kVa)
# g_m = g_d*0.1 #R$/year (10% of maintenance cost)
# CF = 4.17 #kWh/km
# p_nox = 4369 # $/ton (mean) [min, max] -> [345,14915]
# p_sox = 3140 # $/ton (mean) [min, max] -> [1208,7379]
# p_pm = 6751 # $/ton (mean) [min, max] -> [1491,25434]
# p_ch4 = 810 # $/ton (mean) [min, max] -> [370,1100]
# p_co2 = 43  # $/ton (mean) [min, max] -> [12,64]
# USS_to_RS = 5.49 # R$ to 1 US$ 21st march 2021
# V_per_truck = 18 #m^3/truck
# c_km = 3 #R$/km
# i_main_cost = 0.15
# n_start = 1
# #Fixing units
# p_nox = p_nox*USS_to_RS
# p_sox = p_sox*USS_to_RS
# p_pm = p_pm*USS_to_RS
# p_ch4 = p_ch4*USS_to_RS
# p_co2 = p_co2*USS_to_RS
from constants import *
#Functions
def WACC(D,tax,kd,ke):
    global max_debt
    if D<0:
        D=0
    if D>max_debt:
        D = max_debt
    return D*kd*(1-tax)+(1-D)*ke
def npv(P,n,i):
    return P/((1+i)**n)
def total_npv(x,k):
    global L, n_start
    s = 0
    if type(x)!=list:
        x=[x]
    if len(x)==1:
        for n in range(n_start,L+n_start):
            s = s + npv(x[0],n,k)
    else:
        n = n_start
        for x_i in x:
            s = s + npv(x_i,n,k)
            n=n+1
    return s
def V_year(V_day):
    global working_days
    return V_day*working_days
# def D(d,V_day): #total distance traveled
#     return d*V_year(V_day)/V_per_truck
def D(distance_total):
    return distance_total*working_days
# def c_t(d,V_day): #total cost of travel
#     return total_npv(3*D(d,V_day))
def c_t(distance_total,k): #total cost of travel
    global c_rskm
    return total_npv(c_rskm*D(distance_total),k)

def i(V_d,typ,n_g): #investment cost
    global a_d,b_d,g_d
    return a_d[typ]*V_d+b_d[typ]+n_g*g_d
def i_m(V_d,typ,n_g):
    global g_m,i_main_cost
    return n_g*g_m+i_main_cost*(a_d[typ]*V_d+b_d[typ])
def c_m(V_d,typ,n_g,k):
    return total_npv(i_m(V_d,typ,n_g),k)
def c_e(e_c,e_priceB,k):
    return total_npv([e_c*e_priceB],k)
def f_s(f_p,f_used,p_bf,k):
    if f_p>f_used:
        f = f_used
    else: f = f_p
    return total_npv([f*p_bf],k)
def w_l(f_p,f_used):
    return max(f_p-f_used,0)
def e_p(V_gburn):
    global e_densitygas, g_eff
    return V_gburn*e_densitygas*g_eff
def JtokWh(J):
    return J/3600000
# def e_process(h_needed,W_out):
#     global g,h_water,eff_pump,working_days
#     return (0*h_needed+JtokWh(g*h_water*W_out/eff_pump))*working_days
# def e_s(V_gburn,e_c,h_needed,W_out):
#     global g,h_water,eff_pump
#     return max(e_p(V_gburn)-e_c-e_process(h_needed,W_out),0)
def e_s(V_gburn,e_c):
    global g,h_water,eff_pump
    return max(e_p(V_gburn)-e_c,0)


def r(V_gburn,e_c,f_p,f_used,V_g,k):
    global e_priceS,p_g,p_l
    r_e = total_npv([e_s(V_gburn,e_c)*e_priceS],k)
    r_g = total_npv([(V_g-V_gburn)*p_g],k)
    r_l = total_npv([w_l(f_p,f_used)*p_l],k)
    return r_e+r_g+r_l
def polution_avoided_specific(list_in):
    #https://reader.elsevier.com/reader/sd/pii/S0959652619307929?token=BC8B4776075DBF71536EA5B07D0328D1D52E1A387C68CB7BB93F6A9E9128722F38F694886CFCE14349F189AE6D053962
    #equation (7)
    #Nox here is an example can be used for SOx,PM,CH4,CO2,
    #[W,NOX_lf,NOX_tech,NOX_ff,P_nox]
    W = list_in[0]/1000
    NOX_lf = list_in[1]
    NOX_tech = list_in[2]
    NOX_ff = list_in[3]
    P_nox = list_in[4]
    return W*(NOX_lf-NOX_tech)*P_nox + 0*W*(NOX_ff-NOX_tech)*P_nox
def c_p(all_gas_list,k):
    s = 0
    for list_in in all_gas_list:
        s = s+ total_npv([polution_avoided_specific(list_in)],k)
    return s

def do_list_cp(W,distance_total,X_lf,X_tech,gas):
    global p_nox,p_sox,p_pm,p_ch4,p_co2
    if gas =='NOX':
        to_add = [nox_ff(distance_total),p_nox]
    elif gas=='SOX':
        to_add = [sox_ff(distance_total),p_sox]
    elif gas=='PM':
        to_add = [pm_ff(distance_total),p_pm]
    elif gas=='CH4':
        to_add = [ch4_ff(distance_total),p_ch4]
    elif gas=='CO2':
        to_add = [co2_ff(distance_total),p_co2]
    else:
        raise NotImplementedError
    return [W,X_lf,X_tech]+to_add

def do_all_list_cp(W,distance_total,list_in):
    list_out =[]
    for lis in list_in:
        X_lf=lis[0]
        X_tech=lis[1]
        gas = lis[2]
        list_out.append(do_list_cp(W,distance_total,X_lf,X_tech,gas))
    return list_out
    
def nox_ff(distance_total):
    global CF
    return 0.46*CF*D(distance_total)/1000
def sox_ff(distance_total):
    global CF
    return 0.0*CF*D(distance_total)/1000
def pm_ff(distance_total):
    global CF
    return 0.01*CF*D(distance_total)/1000
def ch4_ff(distance_total):
    global CF
    return 0.5*CF*D(distance_total)/1000
def co2_ff(distance_total):
    global CF
    return 4*CF*D(distance_total)/1000
def g0(fused,fp):
    return fused-fp
def g1(Vgburn,Vg):
    return Vgburn-Vg
# def g2(ep,ec,eprocess):
#     return ec+eprocess-ep
def g2(ep,ec):
    return ec-ep
def g3(n_g,ep):
    global g_power,working_hours,g_eff
    capacity = n_g*g_power*working_days*working_hours*g_eff
    return ep-capacity
def farmer_npv(n_g,V_gburn,V_d,typ,distance_total,f_p,V_g,debt_level,e_c,e_priceB,f_used,p_bf,printt=False,pen=True):
    global tax, kd, ke,g_power,working_hours,g_eff
    k = WACC(debt_level,tax,kd,ke)
    n_g = int(round(n_g,0))
    if V_gburn > V_g:
        V_gburn = V_g
    if V_gburn < 0:
        V_gburn = 0
    if n_g<1:
        n_g=1
    i_r = i(V_d,typ,n_g)
    c_t_r = c_t(distance_total,k)
    c_m_r = c_m(V_d,typ,n_g,k)
    c_e_r= c_e(e_c,e_priceB,k)
    f_s_r = f_s(f_p,f_used,p_bf,k)
    r_r = r(V_gburn,e_c,f_p,f_used,V_g,k)
    penalty = 0
    if pen:
        # p0 = max(w_l(f_p,f_used),0)**2
        p1 = max(100*g1(V_gburn,V_g),0)**2
        p2 = max(g2(e_p(V_gburn),e_c),0)**2
        p3 = max(g3(n_g,e_p(V_gburn)),0)**2
        ro = 10
        penalty = pen*ro*(100*p1+p2*100+100*p3)
    
    capacity = n_g*g_power*working_days*working_hours*g_eff
    if printt:
        print('Farmer NPV R$ = %.2f' % (r_r-i_r-c_m_r-c_t_r+c_e_r+f_s_r))
        print('Energy produced kWh/year = %.2f' % (e_p(V_gburn)))
        # print('Energy required to pump water kWh/year = %.2f' % (JtokWh(g*h_water*W_out/eff_pump)*working_days))
        print('System power production capacity kWh/year = %.2f' % (capacity))
        print('Energy Sold kWh/year = %.2f' % (e_s(V_gburn,e_c)))
        # print('Digester heat needed kWh/year = %.2f' % (h_needed*working_days))
        print('Total revenue generated R$ %.2f' % (r_r))
        print('Total investment R$ %.2f' % (i_r))
        print('Total cost of transport R$ %.2f' % (c_t_r))
        print('Total cost of maintenance R$ %.2f' % (c_m_r))
        print('Total cost saved in electrical energy R$ %.2f' % (c_e_r))
        print('Total cost saved in fertilizer R$ %.2f' % (f_s_r))
        print('Total amount of biomethane sold m^3 %.2f /year' % (V_g-V_gburn))
        print('Total amount of electrical energy sold kWh %.2f /year' % (e_s(V_gburn,e_c)))
        print('Total amount of fertilizer sold kg %.2f /year' % (w_l(f_p,f_used)))
    
    
    
    
    
    return r_r-i_r-c_m_r-c_t_r+c_e_r+f_s_r-penalty
def system_npv(n_g,V_gburn,V_d,typ,distance_total,f_p,V_g,debt_level,e_c,e_priceB,f_used,p_bf,all_gas_list,printt=False,pen=True):
    f_npv = farmer_npv(n_g,V_gburn,V_d,typ,distance_total,f_p,V_g,debt_level,e_c,e_priceB,f_used,p_bf,printt,pen)
    global tax, kd, ke
    k = WACC(debt_level,tax,kd,ke)
    if printt:
        print('System NPV R$ %.2f' % (f_npv+c_p(all_gas_list,k)))
        print('Total ghg emissions saved R$ %.2f' % (c_p(all_gas_list,k)))
    return f_npv +c_p(all_gas_list,k)
# farmer_npv(V_d,typ,distance_total,f_p,h_needed,W_out,V_gburn,V_g,e_c,e_priceB,f_used,p_bf)
# def check_constraints():
#     fnpv = farmer_npv(V_d,typ,distance_total,f_p,h_needed,W_out,V_gburn,V_g,e_c,e_priceB,f_used,p_bf)
#     print('farmer NPV >0? --> %.2f' % (fnpv))
#     snpv = system_npv(V_d,typ,distance_total,f_p,h_needed,W_out,V_gburn,V_g,e_c,e_priceB,f_used,p_bf,all_gas_list)
#     print('system NPV >0? --> %.2f' % (snpv))
#     print('V_gburn %.2f < V_g %.2f?' % (V_gburn,V_g))
#     e_process = (h_needed+g*h_water*W_out/eff_pump)*working_days
#     print('e_p %.2f > e_c (%.2f) +e_process (%.2f) = (%.2f)?' % (e_p(V_gburn),e_c,e_process,e_c+e_process))
#     capacity = n_g*g_power*working_days*working_hours
#     print('system power production capacity %.2f > e_p? --> %.2f' % (capacity,e_p(V_gburn)))
    
  
    
    
    