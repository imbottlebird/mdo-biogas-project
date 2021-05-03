# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 14:54:35 2021

@author: Ricardo Hopker
"""

import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
from constants import dict_total
import dill
import matplotlib.pyplot as plt
import pydeck as pdk
from integrating_modules import biodigestor, cleanXopt,cleanBiodigestor,fminClean,dict_T
from multiJ import run_multiJ,plotRes
import scipy.optimize as op
from Transport import load_data


data = pd.read_csv('location_data.csv', header=None)
data = data.rename(columns={0:'lat',1:'lon',2:'Volume',3:'something',4:'Cattle',5:'Swine',6:'Poultry'}) 
data['id'] = list(range(len(data)))
data['id+1'] = list(range(1,len(data)+1))

def runJ():
    return run_multiJ()

def plotMultiJ(res):
    var = plotRes(res,False)
    return var

st.title('Biodigestor 2021 EM.428 MIT')
st.write("Ricardo Hopker, Niek, Jaqueline and Jo")
st.write("inputs:")
#[V_gBurn,ng,Tdig,debt_level,V_cng_p,farm1,farm2,farm3,farm4,farm5,farm6,farm7]
V_gBurn = st.number_input('Volume of Gas burn as % of biogas produced',value = 1.0)
ng = st.number_input('Number of Eletricity Generators',value = 1)
Tdig = st.number_input('Temperature of the digestor (C°): ',value = 37)
debt_level = st.number_input('Debt level of the project',value = 0.8)
V_cng_p = st.number_input('Volume of Gas upgraded to biodiesel for manure transportation: ',value = 0)
farm1 = st.number_input('is farm 1 active: ',value = 1)
farm2 = st.number_input('is farm 2 active: ',value = 1)
farm3 = st.number_input('is farm 3 active: ',value = 1)
farm4 = st.number_input('is farm 4 active: ',value = 1)
farm5 = st.number_input('is farm 5 active: ',value = 1)
farm6 = st.number_input('is farm 6 active: ',value = 1)
farm7 = st.number_input('is farm 7 active: ',value = 1)
lam = st.number_input('Multi-objective (1 full NPV, 0 full emissions): ',value = 1.00)
x = [V_gBurn,ng,Tdig,debt_level,V_cng_p,farm1,farm2,farm3,farm4,farm5,farm6,farm7]
st.write('objective function value:')
st.write(-biodigestor(cleanXopt(x),lam,True,False))
active_farms= x[5:12] 
active_farms = [False if num<1 or num==False  else True for num in active_farms]
if st.checkbox('Optimize with X0 above and lambda'):
    st.write('Best X')
    args = (lam,True,False,False,True)
    # print(lam)
    # print(x)
    # print(cleanXopt(x))
    # xopt = op.fmin(func=cleanBiodigestor,x0=x,args=args)
    xopt = fminClean(x,args)
    xoptSer = pd.DataFrame(pd.Series(cleanXopt(xopt),index=['V_gBurn','ng','Tdig','debt_level','V_cng_p','farm1','farm2','farm3','farm4','farm5','farm6','farm7'])).transpose()
    st.write(xoptSer)
    # print(cleanXopt(xopt))
    st.write('Best Obj')
    st.write(-cleanBiodigestor(xopt,lam,True,False,False,True))

@st.cache()
def load_tradespace_func():
    df,F,annot = plotMultiJ(runJ())
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
        ax.set_xlim([-3e6,0])
    st.write(fig)

# wasteData
map_data = data[['lat','lon']]
# map_data
# st.map(map_data)




view_state = pdk.ViewState(
    longitude=map_data.mean()['lon'], latitude= map_data.mean()['lat'], zoom=8.5, min_zoom=5, max_zoom=15, pitch=0, bearing=-27.36)
@st.cache()
def active_farmsfun(tf,dig_id = None):
    active_farms1= x[5:12] 
    active_farms1 = [0 if num<1 or num==False  else 1 for num in active_farms1]
    active_farms= x[5:12] 
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
    active_farms1= x[5:12] 
    active_farms1 = [0 if num<1 or num==False  else 1 for num in active_farms1]
    active_farms= x[5:12] 
    active_farms = [False if num<1 or num==False  else True for num in active_farms]
    [distance, wIn, total_solids_perc, wComp,Tpath] = dict_T[tuple(active_farms1)]
    r = load_r_path(Tpath)
    st.write('Active farms: current truck location in red')
    curr_step = st.slider('Step',int(min(Tpath)),int(max(Tpath)),value =int(len(Tpath)-1), step = 1)
    
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
    active_farms1= x[5:12] 
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
# a_d[0] = st.number_input('insert number for fit line for digestor type 0',value = a_d[0])
# st.write(a_d[0])
# a_d[1] = st.number_input('insert number for fit line for digestor type 1',value = a_d[1])

