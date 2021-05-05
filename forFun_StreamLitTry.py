# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 14:54:35 2021

@author: Ricardo Hopker
"""

import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
# import numpy as np
import pandas as pd
from constants import dict_total
# import dill
import matplotlib.pyplot as plt
import pydeck as pdk
from integrating_modules import biodigestor, cleanXopt,cleanBiodigestor,fminClean,dict_T
from multiJ import run_multiJ,plotRes
# import scipy.optimize as op
# from Transport import load_data
import copy
import SessionState
# import json

data = pd.read_csv('location_data.csv', header=None)
data = data.rename(columns={0:'lat',1:'lon',2:'Volume',3:'something',4:'Cattle',5:'Swine',6:'Poultry'}) 
data['id'] = list(range(len(data)))
data['id+1'] = list(range(1,len(data)+1))
session_state = SessionState.get(e_priceS=dict_total['e_priceS'],
        e_c=dict_total['e_c'],
        e_priceB=dict_total['e_priceB'],
        f_used=dict_total['f_used'],
        p_bf = dict_total['p_bf'],
        p_l = dict_total['p_l'],
        c_rskm = dict_total['c_rskm'],
        C_V_gas = dict_total['C_V_gas'],
        p_g = dict_total['p_g'],
        C_upgrade_cng = dict_total['C_upgrade_cng'],
        g_d = dict_total['g_d'],
        g_eff = dict_total['g_eff'],
        g_m = dict_total['g_m'],
        i_main_cost = dict_total['i_main_cost'],
        kd = dict_total['kd'],
        max_debt = dict_total['max_debt'],
        ke = dict_total['ke'],
        L = dict_total['L'],
        T_m3_km_cng = dict_total['T_m3_km_cng'],
        T_L_km_diesel = dict_total['T_L_km_diesel'],
        V_per_truck = dict_total['V_per_truck'],
        tax = dict_total['tax'],
        USS_to_RS = dict_total['USS_to_RS'],
        working_days = dict_total['working_days'],
        working_hours = dict_total['working_hours'],
        g_power = dict_total['g_power']
                                 )

def plotMultiJ(res,dict_totalUser):
    var = plotRes(res,False,dict_totalUser)
    return var

dict_totalUser = copy.deepcopy(dict_total)
dict_totalUser['e_priceS'] = session_state.e_priceS
dict_totalUser['e_c'] = session_state.e_c
dict_totalUser['e_priceB'] = session_state.e_priceB
dict_totalUser['f_used'] = session_state.f_used
dict_totalUser['p_bf'] = session_state.p_bf
dict_totalUser['p_l'] = session_state.p_l
dict_totalUser['c_rskm'] = session_state.c_rskm
session_state.c_km = session_state.c_rskm
dict_totalUser['C_V_gas'] = session_state.C_V_gas
dict_totalUser['p_g'] = session_state.p_g
dict_totalUser['C_upgrade_cng'] = session_state.C_upgrade_cng
dict_totalUser['g_d'] = session_state.g_d
dict_totalUser['g_eff'] = session_state.g_eff
dict_totalUser['g_m']= session_state.g_m
dict_totalUser['i_main_cost'] = session_state.i_main_cost
dict_totalUser['kd'] = session_state.kd
dict_totalUser['max_debt'] = session_state.max_debt
dict_totalUser['ke'] = session_state.ke
dict_totalUser['L'] = session_state.L
dict_totalUser['T_m3_km_cng'] = session_state.T_m3_km_cng
dict_totalUser['T_L_km_diesel'] = session_state.T_L_km_diesel
dict_totalUser['V_per_truck'] = session_state.V_per_truck
dict_totalUser['tax'] = session_state.tax
dict_totalUser['USS_to_RS'] = session_state.USS_to_RS
dict_totalUser['working_days'] = session_state.working_days
dict_totalUser['working_hours'] = session_state.working_hours
dict_totalUser['g_power'] = session_state.g_power

st.title('Biodigestor 2021 EM.428 MIT')
st.write("Ricardo Hopker, Niek, Jaqueline and Jo")
st.write("inputs:")
#[V_gBurn,ng,Tdig,debt_level,V_cng_p,farm1,farm2,farm3,farm4,farm5,farm6,farm7]
V_gBurn = st.number_input('Volume of Gas burn as % of biogas produced',value = 1.00)
ng = st.number_input('Number of Eletricity Generators',value = 1)
# Tdig = st.number_input('Temperature of the digestor (C°): ',value = 37)
debt_level = st.number_input('Debt level of the project',value = 0.8)
V_cng_p = st.number_input('Volume of Gas upgraded to biodiesel for manure transportation: ',value = 0.00)
farm1 = st.number_input('is farm 1 active: ',value = 1)
farm2 = st.number_input('is farm 2 active: ',value = 1)
farm3 = st.number_input('is farm 3 active: ',value = 1)
farm4 = st.number_input('is farm 4 active: ',value = 1)
farm5 = st.number_input('is farm 5 active: ',value = 1)
farm6 = st.number_input('is farm 6 active: ',value = 1)
farm7 = st.number_input('is farm 7 active: ',value = 1)
lam = st.number_input('Multi-objective (1 full NPV, 0 full emissions): ',value = 1.00)
x = [V_gBurn,ng,debt_level,V_cng_p,farm1,farm2,farm3,farm4,farm5,farm6,farm7]
st.write('objective function value:')
st.write(-biodigestor(cleanXopt(x),dict_totalUser,lam,True,False))
active_farms= x[4:11] 
active_farms = [False if num<1 or num==False  else True for num in active_farms]
if st.checkbox('Optimize with X0 above and lambda'):
    
    # print(dict_totalUser['e_priceS'])
    args = (dict_totalUser,lam,True,False,False,True)
    xopt = fminClean(x,args)
    xoptSer = pd.DataFrame(pd.Series(cleanXopt(xopt),index=['V_gBurn','ng','debt_level','V_cng_p','farm1','farm2','farm3','farm4','farm5','farm6','farm7'])).transpose()
    st.write('Best X')
    st.write(xoptSer)
    # print(cleanXopt(xopt))
    st.write('Best Obj')
    st.write(-cleanBiodigestor(xopt,dict_totalUser,lam,True,False,False,True))

@st.cache()
def load_tradespace_func():
    df,F,annot = plotMultiJ(run_multiJ(dict_totalUser),dict_totalUser)
    return df,F,annot

if st.checkbox('View multiobjective tradespace'):
    st.write('multiobjective tradespace:')
    df,F,annot = load_tradespace_func()
    fig,ax = plt.subplots()
    ax.scatter(df['NPV'],df['gwp'],s=20,c='r')
    ax.set_xlabel('NPV')
    ax.set_ylabel('gwp')
    ax.plot(df['NPV'],df['gwp'],c='r',lw=1)
    
    ax.scatter(annot[0],annot[1],marker='*',c='y',s=120)
    ax.scatter(F[0],F[1],c='b',s=0.5,)
    if ax.get_xlim()[0]<-3e6:
        
        ax.set_xlim([min(df['NPV'])-1000,annot[0]+1000])
    colDict = {}
    colnames = ['V_gBurn','ng','debt_level','V_cng_p','farm1','farm2','farm3','farm4','farm5','farm6','farm7']    
    for j in range(11):
        colDict[j]=colnames[j]
    df = df.rename(columns=colDict)
    st.write(fig)
    st.write('Pareto front vectors: ',df)
     

# wasteData
map_data = data[['lat','lon']]
# map_data
# st.map(map_data)




view_state = pdk.ViewState(
    longitude=map_data.mean()['lon'], latitude= map_data.mean()['lat'], zoom=8.5, min_zoom=5, max_zoom=15, pitch=0, bearing=-27.36)
@st.cache()
def active_farmsfun(tf,dig_id = None):
    active_farms1= x[4:11] 
    active_farms1 = [0 if num<1 or num==False  else 1 for num in active_farms1]
    active_farms= x[4:11] 
    active_farms = [False if num<1 or num==False  else True for num in active_farms]
    [distance, wIn, total_solids_perc, wComp,Tpath] = dict_T[tuple(active_farms1)]
    count = 0
    count_id =0
    if tf:
        for i in active_farms1:
            if i ==1:
                if count == Tpath[0]:
                    dig_id=count_id
                count = count +1
            count_id = count_id+1
    
    
    layer_active = pdk.Layer(
        "ScatterplotLayer",
        data[active_farms],
        get_position=['lon', 'lat'],
        auto_highlight=True,
        get_radius=1000,
        get_fill_color=['id == ' + str(dig_id)+' ? 255 : 0', 0, 0, 255],
        # get_fill_color=[0, 0, 0, 255],
        # elevation_scale=50,
        pickable=True,
        get_weight = 'Volume > 0 ? Volume : 0',
        extruded=True,
        coverage=1,
)
    r_active = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        layers=[layer_active],
        initial_view_state=view_state,
        tooltip={"html": "<b>Manure Volume:</b> {Volume}  <br> <b>Farm:</b> {id+1}", "style": {"color": "white"}},
)
    
    return r_active,Tpath
@st.cache()
def load_r_path(Tpath):
    r = []
    for i in Tpath:
        r_new,Tpath2 = active_farmsfun(False,i)
        r.append(r_new)
    return r
if st.checkbox('View active farms'):
    st.write('Active farms: in red digestor location')
    r_active,Tpath = active_farmsfun(True)
    # print(Tpath)
    st.pydeck_chart(r_active)
if st.checkbox('View manure transport path for active farms'):
    active_farms1= x[4:11] 
    active_farms1 = [0 if num<1 or num==False  else 1 for num in active_farms1]
    active_farms= x[4:11] 
    active_farms = [False if num<1 or num==False  else True for num in active_farms]
    [distance, wIn, total_solids_perc, wComp,Tpath] = dict_T[tuple(active_farms1)]
    r = load_r_path(Tpath)
    st.write('Active farms: current truck location in red')
    curr_step = st.slider('Step',0,int(len(Tpath)-1),value =0, step = 1)
    
    # r_active,Tpath = active_farmsfun(False,Tpath[curr_step])
    # print(Tpath)
    st.pydeck_chart(r[curr_step])
@st.cache()
def show_farmsfun():
    layer_farms = pdk.Layer(
    "ScatterplotLayer",
    data,
    get_position=['lon', 'lat'],
    auto_highlight=True,
    get_radius=1000,
    get_fill_color=['id * 42.5', 'id * 42.5', 0, 255],
    # get_fill_color=[0, 0, 0, 255],
    # elevation_scale=50,
    pickable=True,
    # elevation_range=[0, 3000],
    extruded=True,
    coverage=1,
)
    r = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        layers=[layer_farms],
        initial_view_state=view_state,
        tooltip={"html": "<b>Manure Volume:</b> {Volume}  <br> <b>Farm:</b> {id+1}", "style": {"color": "white"}},
)
    return r
if st.checkbox('Show farm locations'):
    st.write('Farms:')
    r = show_farmsfun()
    st.pydeck_chart(r)

@st.cache()   
def farm_heatmapFunc():
    active_farms1= x[4:11] 
    active_farms1 = [0 if num<1 or num==False  else 1 for num in active_farms]
    [distance, wIn, total_solids_perc, wComp,Tpath] = dict_T[tuple(active_farms1)]
    dig_id=Tpath[0]
    layer_heat = pdk.Layer(
        "HeatmapLayer",
        data,
        get_position=['lon', 'lat'],
        auto_highlight=True,
        get_radius=1000,
        get_fill_color=['lon==' + str(map_data['lon'].iloc[dig_id])+' ? 255 : 0', 0, 0, 255],
        # elevation_scale=50,
        pickable=True,
        elevation_range=[0, 3000],
        get_weight = 'Volume > 0 ? Volume : 0',
        extruded=True,
        coverage=1,
)
    r = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        layers=[layer_heat],
        initial_view_state=view_state,
        tooltip={"html": "<b>Manure Volume:</b> {Volume}  <br> <b>Farm:</b> {id+1}", "style": {"color": "white"}},
)
    return r
    
if st.checkbox('Show farm heatmaps'):
    st.write('Manure volume heatmap:')
    r = farm_heatmapFunc()
    st.pydeck_chart(r)
st.header('Parameters: ')
st.write('Electrical Energy: ')
session_state.e_priceS = st.number_input('Price of electrical energy sold (R$/kWh): ',value = dict_totalUser['e_priceS'])
session_state.e_c = st.number_input('Electrical energy consumed in the farms (kWh/year): ',value = dict_totalUser['e_c'])
session_state.e_priceB = st.number_input('Price of electrical energy bought (R$/kWh): ',value = dict_totalUser['e_priceB'])
st.write('Fertilizer: ')
session_state.f_used = st.number_input('Quantity of fertilizer used in the farms (kg/year): ',value = dict_totalUser['f_used'])
session_state.p_bf = st.number_input('Price of buying fertilizer used in the farms (R$/kg): ',value = dict_totalUser['p_bf'])
session_state.p_l = st.number_input('Selling price of fertilizer surplus (R$/kg): ',value = dict_totalUser['p_l'])
st.write('Transportation: ')
session_state.c_rskm = st.number_input('Cost to transport manure (R$/km): ',value = dict_totalUser['c_rskm'])
session_state.c_km = session_state.c_rskm
session_state.T_m3_km_cng = st.number_input('Truck average CNG consumption (m^3/km): ',value = dict_totalUser['T_m3_km_cng'])
session_state.T_L_km_diesel = st.number_input('Truck average diesel consumption (L/km): ',value = dict_totalUser['T_L_km_diesel'])
session_state.V_per_truck = st.number_input('Truck maximum capacity (m^3): ',value = dict_totalUser['V_per_truck'])
st.write('Biogas: ')
session_state.C_V_gas = st.number_input('Cost to produce biogas (R$/m^3): ',value = dict_totalUser['C_V_gas'])
session_state.p_g = st.number_input('Selling price of biogas (R$/m^3): ',value = dict_totalUser['p_g'])
session_state.C_upgrade_cng = st.number_input('Cost to upgrade biogas to CNG (R$/m^3): ',value = dict_totalUser['C_upgrade_cng'])
st.write('Generator: ')
session_state.g_d = st.number_input('Cost purchase eletricity generator (R$/unit): ',value = dict_totalUser['g_d'])
session_state.g_eff = st.number_input('Eletricity generator efficiency with biogas (%): ',value = dict_totalUser['g_eff'])
session_state.g_power = st.number_input('Eletricity generator power capacity (kW): ',value = dict_totalUser['g_power'])
session_state.g_m = st.number_input('Yealy cost of maintenance of eletricity generator (R$/(unit*year)): ',value = dict_totalUser['g_m'])
st.write('Biodigestor: ')
session_state.i_main_cost = st.number_input('Yealy cost of maintenance of biodigestor (% of investment/year): ',value = dict_totalUser['i_main_cost'])
session_state.L = st.number_input('Biodigestor life (years): ',value = dict_totalUser['L'])
st.write('Financial: ')
session_state.kd = st.number_input('Cost of debt (%): ',value = dict_totalUser['kd'])
session_state.max_debt = st.number_input('Maximum debt allowed (%): ',value = dict_totalUser['max_debt'])
session_state.ke = st.number_input('Cost of equity (%): ',value = dict_totalUser['ke'])
session_state.tax = st.number_input('Tax on profits (%): ',value = dict_totalUser['tax'])
session_state.USS_to_RS = st.number_input('Corversion of US$ to R$ (R$/US$): ',value = dict_totalUser['USS_to_RS'])
session_state.working_days = st.number_input('Working days per year (days/year): ',value = dict_totalUser['working_days'])
session_state.working_hours = st.number_input('Working hours per day (hours/day): ',value = dict_totalUser['working_hours'])

# print(dict_totalUser['e_priceS'])
# a_d[0] = st.number_input('insert number for fit line for digestor type 0',value = a_d[0])
# st.write(a_d[0])
# a_d[1] = st.number_input('insert number for fit line for digestor type 1',value = a_d[1])

