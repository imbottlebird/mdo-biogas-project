# -*- coding: utf-8 -*-
"""
Created on Sun Mar 21 19:38:02 2021
@author: Ricardo Hopker
"""
# from constants import *
#Functions
# def WACC(D,tax,kd,ke,dict_total):
def WACC(D,tax,kd,ke,dict_total):
    max_debt = dict_total['max_debt']
    # global max_debt
    if D<0:
        D=0
    if D>max_debt:
        D = max_debt
    return D*kd*(1-tax)+(1-D)*ke
def npv(P,n,i):
    return P/((1+i)**n)
def total_npv(x,k,dict_total):
    # global L, n_start
    L = dict_total['L']
    n_start = dict_total['n_start']
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
def V_year(V_day,dict_total):
    working_days = dict_total['working_days']
    # global working_days
    return V_day*working_days
# def D(d,V_day): #total distance traveled
#     return d*V_year(V_day)/V_per_truck
def D(distance_total,dict_total):
    working_days = dict_total['working_days']
    return distance_total*working_days

# def c_t(d,V_day): #total cost of travel
#     return total_npv(3*D(d,V_day))
def c_t(D_cng,D_diesel,k,dict_total): #total cost of travel
    # global c_rskm
    c_rskm = dict_total['c_rskm']
    C_t_fixed, C_cng = C_cng_func(dict_total)
    return total_npv(c_rskm*D_diesel+(C_t_fixed+C_cng)*D_cng,k,dict_total)
def C_cng_func(dict_total):
    c_rskm = dict_total['c_rskm']
    P_diesel = dict_total['P_diesel']
    T_L_km_diesel = dict_total['T_L_km_diesel']
    T_m3_km_cng = dict_total['T_m3_km_cng']
    C_upgrade_cng = dict_total['C_upgrade_cng']
    # global c_rskm,P_diesel, T_L_km_diesel, T_m3_km_cng,C_upgrade_cng
    C_t_diesel = T_L_km_diesel*P_diesel
    C_t_fixed = c_rskm - C_t_diesel
    C_cng = T_m3_km_cng*(C_upgrade_cng)
    return C_t_fixed, C_cng
def C_prod(V_g,k,dict_total):
    # global C_V_gas
    C_V_gas = dict_total['C_V_gas']
    return total_npv(V_g*C_V_gas,k,dict_total)
    
    
def i(V_d,typ,n_g,dict_total): #investment cost
    # global a_d,b_d,g_d
    a_d = dict_total['a_d']
    b_d = dict_total['b_d']
    g_d = dict_total['g_d']
    return a_d[typ]*V_d+b_d[typ]+n_g*g_d
def i_m(V_d,typ,n_g,dict_total):
    # global g_m,i_main_cost
    a_d = dict_total['a_d']
    b_d = dict_total['b_d']
    g_m = dict_total['g_m']
    i_main_cost = dict_total['i_main_cost']
    return n_g*g_m+i_main_cost*(a_d[typ]*V_d+b_d[typ])
def c_m(V_d,typ,n_g,k,dict_total):
    return total_npv(i_m(V_d,typ,n_g,dict_total),k,dict_total)
def c_e(e_c,e_priceB,k,dict_total):
    return total_npv([e_c*e_priceB],k,dict_total)
def f_s(f_p,f_used,p_bf,k,dict_total):
    if f_p>f_used:
        f = f_used
    else: f = f_p
    return total_npv([f*p_bf],k,dict_total)
def w_l(f_p,f_used):
    return max(f_p-f_used,0)
def e_p(V_gburn,dict_total):
    e_densitygas = dict_total['e_densitygas']
    g_eff = dict_total['g_eff']
    # global e_densitygas, g_eff
    return V_gburn*e_densitygas*g_eff
def JtokWh(J):
    return J/3600000
# def e_process(h_needed,W_out):
#     global g,h_water,eff_pump,working_days
#     return (0*h_needed+JtokWh(g*h_water*W_out/eff_pump))*working_days
# def e_s(V_gburn,e_c,h_needed,W_out):
#     global g,h_water,eff_pump
#     return max(e_p(V_gburn)-e_c-e_process(h_needed,W_out),0)
def e_s(V_gburn,e_c,dict_total):
    # global g,h_water,eff_pump
    return max(e_p(V_gburn,dict_total)-e_c,0)


def r(V_gburn,e_c,f_p,f_used,V_g,k,e_priceS,V_cng_p,dict_total):
    # global p_g,p_l
    p_g = dict_total['p_g']
    p_l = dict_total['p_l']
    r_e = total_npv([e_s(V_gburn,e_c,dict_total)*e_priceS],k,dict_total)
    r_g = total_npv([(V_g-V_gburn-V_cng_p)*p_g],k,dict_total)
    r_l = total_npv([w_l(f_p,f_used)*p_l],k,dict_total)
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

def do_list_cp(W,distance_total,X_lf,X_tech,gas,dict_total):
    p_nox = dict_total['p_nox']
    p_sox = dict_total['p_sox']
    p_pm = dict_total['p_pm']
    p_ch4 = dict_total['p_ch4']
    p_co2 = dict_total['p_co2']
    # global p_nox,p_sox,p_pm,p_ch4,p_co2
    if gas =='NOX':
        to_add = [nox_ff(distance_total,dict_total),p_nox]
    elif gas=='SOX':
        to_add = [sox_ff(distance_total,dict_total),p_sox]
    elif gas=='PM':
        to_add = [pm_ff(distance_total,dict_total),p_pm]
    elif gas=='CH4':
        to_add = [ch4_ff(distance_total,dict_total),p_ch4]
    elif gas=='CO2':
        to_add = [co2_ff(distance_total,dict_total),p_co2]
    else:
        raise NotImplementedError
    return [W,X_lf,X_tech]+to_add

def do_all_list_cp(W,distance_total,list_in,dict_total):
    list_out =[]
    for lis in list_in:
        X_lf=lis[0]
        X_tech=lis[1]
        gas = lis[2]
        list_out.append(do_list_cp(W,distance_total,X_lf,X_tech,gas,dict_total))
    return list_out
    
def nox_ff(distance_total,dict_total):
    CF = dict_total['CF']
    # global CF
    return 0.46*CF*D(distance_total,dict_total)/1000
def sox_ff(distance_total,dict_total):
    CF = dict_total['CF']
    # global CF
    return 0.0*CF*D(distance_total,dict_total)/1000
def pm_ff(distance_total,dict_total):
    CF = dict_total['CF']
    # global CF
    return 0.01*CF*D(distance_total,dict_total)/1000
def ch4_ff(distance_total,dict_total):
    CF = dict_total['CF']
    # global CF
    return 0.5*CF*D(distance_total,dict_total)/1000
def co2_ff(distance_total,dict_total):
    CF = dict_total['CF']
    # global CF
    return 4*CF*D(distance_total,dict_total)/1000
def g0(fused,fp):
    return fused-fp
def g1(Vgburn,V_cng,Vg):
    return Vgburn+V_cng-Vg
# def g2(ep,ec,eprocess):
#     return ec+eprocess-ep
# def g2(ep,ec):
#     return ep - ec
def g3(n_g,ep,dict_total):
    # global g_power,working_hours,g_eff
    g_power = dict_total['g_power']
    working_hours = dict_total['working_hours']
    g_eff = dict_total['g_eff']
    working_days = dict_total['working_days']
    
    capacity = n_g*g_power*working_days*working_hours*g_eff
    return ep-capacity
def farmer_npv(n_g,V_gburn,V_cng_p,V_d,typ,distance_total,f_p,V_g,debt_level,e_c,e_priceB,e_priceS,f_used,p_bf,dict_total,printt=False,pen=True):
    tax = dict_total['tax']
    kd = dict_total['kd']
    ke = dict_total['ke']
    g_power = dict_total['g_power']
    working_hours = dict_total['working_hours']
    g_eff = dict_total['g_eff']
    T_m3_km_cng = dict_total['T_m3_km_cng']
    working_days = dict_total['working_days']
    k = WACC(debt_level,tax,kd,ke,dict_total)
    n_g = int(round(n_g,0))
    if V_gburn > V_g:
        V_gburn = V_g
    if V_gburn < 0:
        V_gburn = 0
    if V_cng_p > 1:
        V_cng_p = 1
    if V_cng_p < 0:
        V_cng_p = 0
    if n_g<1:
        n_g=1
    V_cng = V_cng_p*V_g
    D_cng = V_cng/T_m3_km_cng
    D_diesel = D(distance_total,dict_total)-D_cng
    i_r = i(V_d,typ,n_g,dict_total)
    c_t_r = c_t(D_cng,D_diesel,k,dict_total)
    c_m_r = c_m(V_d,typ,n_g,k,dict_total)
    c_e_r= c_e(min(e_c,e_p(V_gburn,dict_total)),e_priceB,k,dict_total)
    f_s_r = f_s(f_p,f_used,p_bf,k,dict_total)
    r_r = r(V_gburn,e_c,f_p,f_used,V_g,k,e_priceS,V_cng_p,dict_total)
    p_r = C_prod(V_g, k,dict_total)
    penalty = 0
    if pen:
        # p0 = max(w_l(f_p,f_used),0)**2
        p1 = max(g1(V_gburn,V_cng,V_g),0)**2
        # p2 = max(g2(e_p(V_gburn),e_c),0)**2
        p3 = max(g3(n_g,e_p(V_gburn,dict_total),dict_total),0)**2
        ro = 1000
        penalty = pen*ro*(1000000*p1+100*p3)
    
    capacity = n_g*g_power*working_days*working_hours*g_eff
    farmnpv= r_r-i_r-c_m_r-c_t_r-p_r+c_e_r+f_s_r
    if printt:
        print('Farmer NPV R$ = %.2f' % (farmnpv))
        print('Energy produced kWh/year = %.2f' % (e_p(V_gburn,dict_total)))
        # print('Energy required to pump water kWh/year = %.2f' % (JtokWh(g*h_water*W_out/eff_pump)*working_days))
        print('System power production capacity kWh/year = %.2f' % (capacity))
        print('Energy Sold kWh/year = %.2f' % (e_s(V_gburn,e_c,dict_total)))
        # print('Digester heat needed kWh/year = %.2f' % (h_needed*working_days))
        print('Total revenue generated R$ %.2f' % (r_r))
        print('Total investment R$ %.2f' % (i_r))
        print('Total cost of transport R$ %.2f' % (c_t_r))
        print('Total cost of maintenance R$ %.2f' % (c_m_r))
        print('Total cost saved in electrical energy R$ %.2f' % (c_e_r))
        print('Total cost saved in fertilizer R$ %.2f' % (f_s_r))
        print('Total amount of biomethane sold m^3 %.2f /year' % (V_g-V_gburn-V_cng_p))
        print('Total amount of electrical energy sold kWh %.2f /year' % (e_s(V_gburn,e_c)))
        print('Total amount of fertilizer sold kg %.2f /year' % (w_l(f_p,f_used)))
    
    
    
    
    
    return farmnpv-penalty
def system_npv(n_g,V_gburn,V_cng_p,V_d,typ,distance_total,f_p,V_g,debt_level,e_c,e_priceB,f_used,p_bf,all_gas_list,printt=False,pen=True):
    f_npv = farmer_npv(n_g,V_gburn,V_cng_p,V_d,typ,distance_total,f_p,V_g,debt_level,e_c,e_priceB,f_used,p_bf,printt,pen)
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
  
    
    
    