# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 14:54:35 2021

@author: Ricardo Hopker
"""

import streamlit as st
import streamlit.components.v1 as components
import base64
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
# import numpy as np
import pandas as pd
from constants import dict_total
# import dill
import matplotlib.pyplot as plt
import pydeck as pdk
from integrating_modules import biodigestor, cleanXopt,cleanBiodigestor,fminClean
from multiJ import run_multiJ,plotRes,run_singleJ
from all_best_paths_transport import createTransportSurrogateModel
# import scipy.optimize as op
# from Transport import load_data
import copy
import SessionState
# import json
def load_session():
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
            g_power = dict_total['g_power'],
            V_gBurn = 0.7,
            ng = 1,
            debt_level = 0.5,
            V_cng_p =0.20,
            farm1 = 1,farm2 = 0,farm3 =0,farm4 = 0,farm5 = 0,farm6 = 0,farm7 = 0,
            ng_max = dict_total['ng_max'],
            NSGA_pop = dict_total['NSGA_pop'],
            NSGA_gen = dict_total['NSGA_gen'],
            NSGA_off = dict_total['NSGA_off'],
            dict_T = dict_total['dict_T'],
            Farm_data = dict_total['Farm_data'],
            GA_pop = dict_total['GA_pop'],
            GA_gen = dict_total['GA_gen'],
            GA_off = dict_total['GA_off'],
            truck_gwp_emmited = dict_total['truck_gwp_emmited'],
            lam = float(dict_total['lam'])
                                     )
    return session_state
def update_user_dict():
    dict_totalUser = copy.deepcopy(dict_total)
    session_state = load_session()
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
    dict_totalUser['ng_max'] = session_state.ng_max
    dict_totalUser['NSGA_pop'] = session_state.NSGA_pop
    dict_totalUser['NSGA_gen'] = session_state.NSGA_gen
    dict_totalUser['NSGA_off'] = session_state.NSGA_off
    dict_totalUser['dict_T'] = session_state.dict_T
    dict_totalUser['Farm_data'] = session_state.Farm_data
    dict_totalUser['GA_pop'] = session_state.GA_pop
    dict_totalUser['GA_gen'] = session_state.GA_gen
    dict_totalUser['GA_off'] = session_state.GA_off
    dict_totalUser['lam'] = session_state.lam
    dict_total['truck_gwp_emmited'] = session_state.truck_gwp_emmited
    return dict_totalUser
    
def main():
    pages ={"Main":page1,"Parameters":page2,'Transportation':pageTransport,"Model Explanation":page3}
    page = st.sidebar.selectbox("Select your page", tuple(pages.keys()))
    # session_state = load_session()
    pages[page]()
def page1():
    session_state = load_session()
    # data = pd.read_csv('location_data.csv', header=None)
    # data = data.rename(columns={0:'lat',1:'lon',2:'Volume',3:'Solid Percentage',4:'Cattle',5:'Swine',6:'Poultry'}) 
    # data['id'] = list(range(len(data)))
    # data['id+1'] = list(range(1,len(data)+1))

    def plotMultiJ(res,dict_totalUser):
        var = plotRes(res,False,dict_totalUser)
        return var
    
    
    dict_totalUser = update_user_dict()
    dict_T = dict_totalUser['dict_T']
    Farm_data = dict_totalUser['Farm_data']
    data = pd.DataFrame(Farm_data)
    data = data.transpose()
    data = data.rename(columns={0:'lat',1:'lon',2:'Volume',3:'Solid Percentage',4:'Cattle',5:'Swine',6:'Poultry'})
    data['id'] = list(range(len(data)))
    data['id+1'] = list(range(1,len(data)+1))
    st.title('Biodigestor 2021 EM.428 MIT')
    st.header('Ricardo Hopker, Niek van Rensburg, Jacqueline Baidoo and ByeongJo Kong')
    st.write("")
    st.subheader("Inputs:")
    #[V_gBurn,ng,Tdig,debt_level,V_cng_p,farm1,farm2,farm3,farm4,farm5,farm6,farm7]
    session_state.V_gBurn = st.number_input('Volume of Gas burn as % of biogas produced',0.0,1.0,value = session_state.V_gBurn)
    session_state.ng = st.number_input('Number of Eletricity Generators',1,value = session_state.ng)
    # Tdig = st.number_input('Temperature of the digestor (C°): ',value = 37)
    session_state.debt_level = st.number_input('Debt level of the project',0.0,1.0,value = session_state.debt_level)
    session_state.V_cng_p = st.number_input('Volume of Gas upgraded to biodiesel for manure transportation: ',0.0,1.0,value = session_state.V_cng_p)
    session_state.farm1 = st.number_input('is farm 1 active: ',0,1,value = session_state.farm1)
    session_state.farm2 = st.number_input('is farm 2 active: ',0,1,value = session_state.farm2)
    session_state.farm3 = st.number_input('is farm 3 active: ',0,1,value = session_state.farm3)
    session_state.farm4 = st.number_input('is farm 4 active: ',0,1,value = session_state.farm4)
    session_state.farm5 = st.number_input('is farm 5 active: ',0,1,value = session_state.farm5)
    session_state.farm6 = st.number_input('is farm 6 active: ',0,1,value = session_state.farm6)
    session_state.farm7 = st.number_input('is farm 7 active: ',0,1,value = session_state.farm7)
    session_state.lam = st.number_input('Multi-objective (1 full NPV, 0 full emissions): ',0.0,1.0,value = float(session_state.lam))
    dict_totalUser['lam'] = session_state.lam
    x = [session_state.V_gBurn,session_state.ng,session_state.debt_level,
         session_state.V_cng_p,session_state.farm1,session_state.farm2,
         session_state.farm3,session_state.farm4,session_state.farm5,
         session_state.farm6,session_state.farm7]
    st.write('objective function value:')
    st.write(-biodigestor(cleanXopt(x,dict_totalUser),dict_totalUser,session_state.lam,True,False))
    active_farms= x[4:11] 
    active_farms = [False if num<1 or num==False  else True for num in active_farms]
    if st.checkbox('Optimize with lamda above'):
        
        # print(dict_totalUser['e_priceS'])
        
        args = (dict_totalUser,session_state.lam,True,False,False,True)
        # xopt = fminClean(x,args)
        res = run_singleJ(dict_totalUser)
        xopt = res.X
        xoptSer = pd.DataFrame(pd.Series(cleanXopt(xopt,dict_totalUser),index=['V_gBurn','ng','debt_level','V_cng_p','farm1','farm2','farm3','farm4','farm5','farm6','farm7'])).transpose()
        st.write('Best X')
        st.write(xoptSer.style.format({'V_gBurn':"{:.2}",'debt_level':"{:.2}",'V_cng_p':"{:.2}"}))
        # print(cleanXopt(xopt))
        st.write('Best Obj')
        st.write(-cleanBiodigestor(xopt,dict_totalUser,session_state.lam,True,False,False,True))
    
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
        st.write('Pareto front vectors: ',df.style.format({'V_gBurn':"{:.2}",'debt_level':"{:.2}",'V_cng_p':"{:.2}"}))
         
    
    # wasteData
    map_data = data[['lat','lon']]
    # map_data
    # st.map(map_data)
    
    
    
    
    view_state = pdk.ViewState(
        longitude=map_data.mean()['lon'], latitude= map_data.mean()['lat'], zoom=8.5, min_zoom=5, max_zoom=15, pitch=0, bearing=-27.36)
    @st.cache()
    def active_farmsfun(tf,compare = None):
        active_farms1= x[4:11] 
        active_farms1 = [0 if num<1 or num==False  else 1 for num in active_farms1]
        active_farms= x[4:11] 
        active_farms = [False if num<1 or num==False  else True for num in active_farms]
        [distance, wIn, total_solids_perc, wComp,Tpath] = dict_T[tuple(active_farms1)]
        count = 0
        count_id =0
        if tf:
            compare = Tpath[0]
        for i in active_farms1:
            if i ==1:
                if count == compare:
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
def page2():
    session_state = load_session()
    st.title('Parameters: ')
    st.write('Electrical Energy: ')
    session_state.e_priceS = st.number_input('Price of electrical energy sold (R$/kWh): ',0.0,value = session_state.e_priceS)
    session_state.e_c = st.number_input('Electrical energy consumed in the farms (kWh/year): ',0.0,value = session_state.e_c)
    session_state.e_priceB = st.number_input('Price of electrical energy bought (R$/kWh): ',0.0,value = session_state.e_priceB)
    st.write('Fertilizer: ')
    session_state.f_used = st.number_input('Quantity of fertilizer used in the farms (kg/year): ',0.0,value = session_state.f_used)
    session_state.p_bf = st.number_input('Price of buying fertilizer used in the farms (R$/kg): ',0.0,value = session_state.p_bf)
    session_state.p_l = st.number_input('Selling price of fertilizer surplus (R$/kg): ',0.0,value = session_state.p_l)
    st.write('Transportation: ')
    session_state.c_rskm = st.number_input('Cost to transport manure (R$/km): ',0.0,value = session_state.c_rskm )
    session_state.c_km = session_state.c_rskm
    session_state.T_m3_km_cng = st.number_input('Truck average CNG consumption (m^3/km): ',0.0,value = session_state.T_m3_km_cng)
    session_state.T_L_km_diesel = st.number_input('Truck average diesel consumption (L/km): ',0.0,value = session_state.T_L_km_diesel)
    session_state.V_per_truck = st.number_input('Truck maximum capacity (m^3): ',0.0,value = session_state.V_per_truck)
    session_state.truck_gwp_emmited = st.number_input('Truck emission CO2 (kgCO2/km): ',0.0,value = session_state.truck_gwp_emmited)
    st.write('Biogas: ')
    session_state.C_V_gas = st.number_input('Cost to produce biogas (R$/m^3): ',0.0,value = session_state.C_V_gas)
    session_state.p_g = st.number_input('Selling price of biogas (R$/m^3): ',0.0,value = session_state.p_g)
    session_state.C_upgrade_cng = st.number_input('Cost to upgrade biogas to CNG (R$/m^3): ',0.0,value = session_state.C_upgrade_cng)
    st.write('Generator: ')
    session_state.g_d = st.number_input('Cost purchase eletricity generator (R$/unit): ',0.0,value = session_state.g_d)
    session_state.g_eff = st.number_input('Eletricity generator efficiency with biogas (%): ',0.0,1.0,value = session_state.g_eff)
    session_state.g_power = st.number_input('Eletricity generator power capacity (kW): ',0.0,value = session_state.g_power)
    session_state.g_m = st.number_input('Yealy cost of maintenance of eletricity generator (R$/(unit*year)): ',0.0,value = session_state.g_m)
    session_state.ng_max = st.number_input('Maximum number of generators (units): ',0,value = session_state.ng_max)
    st.write('Biodigestor: ')
    session_state.i_main_cost = st.number_input('Yealy cost of maintenance of biodigestor (% of investment/year): ',0.0,1.0,value = session_state.i_main_cost)
    session_state.L = st.number_input('Biodigestor life (years): ',0,value = session_state.L)
    st.write('Financial: ')
    session_state.kd = st.number_input('Cost of debt (%): ',0.0,value = session_state.kd)
    session_state.max_debt = st.number_input('Maximum debt allowed (%): ',0.0,1.0,value = session_state.max_debt)
    session_state.ke = st.number_input('Cost of equity (%): ',0.0,value = session_state.ke)
    session_state.tax = st.number_input('Tax on profits (%): ',0.0,1.0,value = session_state.tax)
    session_state.USS_to_RS = st.number_input('Corversion of US$ to R$ (R$/US$): ',0.0,value = session_state.USS_to_RS)
    session_state.working_days = st.number_input('Working days per year (days/year): ',0,365,value = session_state.working_days)
    session_state.working_hours = st.number_input('Working hours per day (hours/day): ',0,24,value = session_state.working_hours)
    st.write('Tradespace GA settings: ')
    session_state.NSGA_pop = st.number_input('GA population size (#): ',0,value = session_state.NSGA_pop)
    session_state.NSGA_gen = st.number_input('GA number of generations (#): ',0,value = session_state.NSGA_gen)
    session_state.NSGA_off = st.number_input('GA population offsprings (#/iteration): ',0,value = session_state.NSGA_off)
    st.write('Optimizer GA settings: ')
    session_state.GA_pop = st.number_input('Single objective GA population size (#): ',0,value = session_state.GA_pop)
    session_state.GA_gen = st.number_input('Single objective GA number of generations (#): ',0,value = session_state.GA_gen)
    session_state.GA_off = st.number_input('Single objective GA population offsprings (#/iteration): ',0,value = session_state.GA_off)


def pageTransport():
    session_state = load_session()
    st.title('Transportation Module: ')
    st.subheader('Do not forget to save your changes in the end of the page')
    # dict_T = session_state.dict_T
    Farm_data = copy.deepcopy(session_state.Farm_data)
    st.write('Farm 1: ')
    Farm_data['Farm_1'][0] = st.number_input('Farm 1 Latitude : ',-90.0,90.0,value = Farm_data['Farm_1'][0],format='%f')
    Farm_data['Farm_1'][1] = st.number_input('Farm 1 Longitude : ',-180.0,180.0,value = Farm_data['Farm_1'][1],format='%f')
    Farm_data['Farm_1'][2] = st.number_input('Farm 1 Manure volume (m^3): ',-180.0,180.0,value = Farm_data['Farm_1'][2])
    Farm_data['Farm_1'][3] = st.number_input('Farm 1 Manure Solid percentage (%): ',0.0,1.0,value = Farm_data['Farm_1'][3])
    Farm_data['Farm_1'][4] = st.number_input('Farm 1 Cattle Manure percentage (%): ',0.0,1.0,value = Farm_data['Farm_1'][4])
    Farm_data['Farm_1'][5] = st.number_input('Farm 1 Swine Manure percentage (%): ',0.0,1.0,value = Farm_data['Farm_1'][5])
    Farm_data['Farm_1'][6] = st.number_input('Farm 1 Poultry Manure percentage (%): ',0.0,1.0,value = Farm_data['Farm_1'][6])
    
    st.write('Farm 2: ')
    Farm_data['Farm_2'][0] = st.number_input('Farm 2 Latitude : ',-90.0,90.0,value = Farm_data['Farm_2'][0],format='%f')
    Farm_data['Farm_2'][1] = st.number_input('Farm 2 Longitude : ',-180.0,180.0,value = Farm_data['Farm_2'][1],format='%f')
    Farm_data['Farm_2'][2] = st.number_input('Farm 2 Manure volume (m^3): ',-180.0,180.0,value = Farm_data['Farm_2'][2])
    Farm_data['Farm_2'][3] = st.number_input('Farm 2 Manure Solid percentage (%): ',0.0,1.0,value = Farm_data['Farm_2'][3])
    Farm_data['Farm_2'][4] = st.number_input('Farm 2 Cattle Manure percentage (%): ',0.0,1.0,value = Farm_data['Farm_2'][4])
    Farm_data['Farm_2'][5] = st.number_input('Farm 2 Swine Manure percentage (%): ',0.0,1.0,value = Farm_data['Farm_2'][5])
    Farm_data['Farm_2'][6] = st.number_input('Farm 2 Poultry Manure percentage (%): ',0.0,1.0,value = Farm_data['Farm_2'][6])
    
    st.write('Farm 3: ')
    Farm_data['Farm_3'][0] = st.number_input('Farm 3 Latitude : ',-90.0,90.0,value = Farm_data['Farm_3'][0],format='%f')
    Farm_data['Farm_3'][1] = st.number_input('Farm 3 Longitude : ',-180.0,180.0,value = Farm_data['Farm_3'][1],format='%f')
    Farm_data['Farm_3'][2] = st.number_input('Farm 3 Manure volume (m^3): ',-180.0,180.0,value = Farm_data['Farm_3'][2])
    Farm_data['Farm_3'][3] = st.number_input('Farm 3 Manure Solid percentage (%): ',0.0,1.0,value = Farm_data['Farm_3'][3])
    Farm_data['Farm_3'][4] = st.number_input('Farm 3 Cattle Manure percentage (%): ',0.0,1.0,value = Farm_data['Farm_3'][4])
    Farm_data['Farm_3'][5] = st.number_input('Farm 3 Swine Manure percentage (%): ',0.0,1.0,value = Farm_data['Farm_3'][5])
    Farm_data['Farm_3'][6] = st.number_input('Farm 3 Poultry Manure percentage (%): ',0.0,1.0,value = Farm_data['Farm_3'][6])
    
    st.write('Farm 4: ')
    Farm_data['Farm_4'][0] = st.number_input('Farm 4 Latitude : ',-90.0,90.0,value = Farm_data['Farm_4'][0],format='%f')
    Farm_data['Farm_4'][1] = st.number_input('Farm 4 Longitude : ',-180.0,180.0,value = Farm_data['Farm_4'][1],format='%f')
    Farm_data['Farm_4'][2] = st.number_input('Farm 4 Manure volume (m^3): ',-180.0,180.0,value = Farm_data['Farm_4'][2])
    Farm_data['Farm_4'][3] = st.number_input('Farm 4 Manure Solid percentage (%): ',0.0,1.0,value = Farm_data['Farm_4'][3])
    Farm_data['Farm_4'][4] = st.number_input('Farm 4 Cattle Manure percentage (%): ',0.0,1.0,value = Farm_data['Farm_4'][4])
    Farm_data['Farm_4'][5] = st.number_input('Farm 4 Swine Manure percentage (%): ',0.0,1.0,value = Farm_data['Farm_4'][5])
    Farm_data['Farm_4'][6] = st.number_input('Farm 4 Poultry Manure percentage (%): ',0.0,1.0,value = Farm_data['Farm_4'][6])
    
    st.write('Farm 5: ')
    Farm_data['Farm_5'][0] = st.number_input('Farm 5 Latitude : ',-90.0,90.0,value = Farm_data['Farm_5'][0],format='%f')
    Farm_data['Farm_5'][1] = st.number_input('Farm 5 Longitude : ',-180.0,180.0,value = Farm_data['Farm_5'][1],format='%f')
    Farm_data['Farm_5'][2] = st.number_input('Farm 5 Manure volume (m^3): ',-180.0,180.0,value = Farm_data['Farm_5'][2])
    Farm_data['Farm_5'][3] = st.number_input('Farm 5 Manure Solid percentage (%): ',0.0,1.0,value = Farm_data['Farm_5'][3])
    Farm_data['Farm_5'][4] = st.number_input('Farm 5 Cattle Manure percentage (%): ',0.0,1.0,value = Farm_data['Farm_5'][4])
    Farm_data['Farm_5'][5] = st.number_input('Farm 5 Swine Manure percentage (%): ',0.0,1.0,value = Farm_data['Farm_5'][5])
    Farm_data['Farm_5'][3] = st.number_input('Farm 5 Poultry Manure percentage (%): ',0.0,1.0,value = Farm_data['Farm_5'][6])
    
    st.write('Farm 6: ')
    Farm_data['Farm_6'][0] = st.number_input('Farm 6 Latitude : ',-90.0,90.0,value = Farm_data['Farm_6'][0],format='%f')
    Farm_data['Farm_6'][1] = st.number_input('Farm 6 Longitude : ',-180.0,180.0,value = Farm_data['Farm_6'][1],format='%f')
    Farm_data['Farm_6'][2] = st.number_input('Farm 6 Manure volume (m^3): ',-180.0,180.0,value = Farm_data['Farm_6'][2])
    Farm_data['Farm_6'][3] = st.number_input('Farm 6 Manure Solid percentage (%): ',0.0,1.0,value = Farm_data['Farm_6'][3])
    Farm_data['Farm_6'][4] = st.number_input('Farm 6 Cattle Manure percentage (%): ',0.0,1.0,value = Farm_data['Farm_6'][4])
    Farm_data['Farm_6'][5] = st.number_input('Farm 6 Swine Manure percentage (%): ',0.0,1.0,value = Farm_data['Farm_6'][5])
    Farm_data['Farm_6'][6] = st.number_input('Farm 6 Poultry Manure percentage (%): ',0.0,1.0,value = Farm_data['Farm_6'][6])
    
    st.write('Farm 7: ')
    Farm_data['Farm_7'][0] = st.number_input('Farm 7 Latitude : ',-90.0,90.0,value = Farm_data['Farm_7'][0],format='%f')
    Farm_data['Farm_7'][1] = st.number_input('Farm 7 Longitude : ',-180.0,180.0,value = Farm_data['Farm_7'][1],format='%f')
    Farm_data['Farm_7'][2] = st.number_input('Farm 7 Manure volume (m^3): ',-180.0,180.0,value = Farm_data['Farm_7'][2])
    Farm_data['Farm_7'][3] = st.number_input('Farm 7 Manure Solid percentage (%): ',0.0,1.0,value = Farm_data['Farm_7'][3])
    Farm_data['Farm_7'][4] = st.number_input('Farm 7 Cattle Manure percentage (%): ',0.0,1.0,value = Farm_data['Farm_7'][4])
    Farm_data['Farm_7'][5] = st.number_input('Farm 7 Swine Manure percentage (%): ',0.0,1.0,value = Farm_data['Farm_7'][5])
    Farm_data['Farm_7'][6] = st.number_input('Farm 7 Poultry Manure percentage (%): ',0.0,1.0,value = Farm_data['Farm_7'][6])
    
    if st.button('Update Transportation model with new farm information'):
        st.write('Please wait a little while we update the model')
        session_state.Farm_data = copy.deepcopy(Farm_data)
        session_state.dict_T = createTransportSurrogateModel(update_user_dict())
        st.write('Done')
def page3():
    st.title('Model explanation and final report: ')
    st.header('This is an optimization model for biodigestors created for the MIT EM.428 class of Spring 2021')
    st.subheader('By: Ricardo Hopker, Niek van Rensburg, Jacqueline Baidoo and ByeongJo Kong')
    st.subheader('')
    pdf = 'Pset 4 Ricardo Hopker.pdf'
    pdf_file = open(pdf, 'rb')
    base64_pdf = base64.b64encode(pdf_file.read()).decode('Latin-1')
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="800" type="application/pdf">' 
    st.markdown(pdf_display, unsafe_allow_html=True)


main()