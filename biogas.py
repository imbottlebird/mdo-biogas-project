def biomethane(G_in, G_comp, dict_total):
    #G_comp=[ch4Out, co2Out, noxOut, soxOut]
    #constants
    ch4_pur = dict_total['ch4_pur']  #ch4 density of biomethane in Brazil
    v_bm = G_in * (G_comp[0] / ch4_pur)  #biomethane produced

    return v_bm


def scm_to_m3(scm):
    #biomethane storage temperature = 50C
    #source: https://checalc.com/solved/volconv.html
    K = 273 #temp conversion to Kelvin
    P1 = P2 = 1 #pressure
    T1 = 15 #scm temp
    T2 = 50 #biomethane temp
    m3 = scm * (P1/P2) * ((T2+K)/(T1+K))
    
    return m3

def biofertilizer(digOut, dict_total):
    # vs_r = 0.43   #rate of volatile solid in the total manure
    # vs = kilos * vs_r  #amount of volatile solid
    
    #pdy = (kilos - vs) + (vs * 0.4)  #(non-volatile solid) + (remnants of volatile solid)
    fer_conv_r = dict_total['fer_conv_r']
    pdy = digOut * fer_conv_r #rate of digestate conversion to biofertilizer
    
    return pdy
    
def ghg(kilos, wComp, G_in, G_comp):
    #GHG release by manure type (unit: g/head/yr) -> g/tonne  (kilos kg/day)
    #CH4: cattle 39.5; swine 18; poultry 0.157
    #CO2: cattle 12; swine 5.47; poultry 0.048
    #NOx: cattle 0.02; swine 0.02; poultry 0.005
    #SOx: 0
    ch4_ghg = [39500, 18000, 157]
    co2_ghg = [12000, 5470, 48]
    nox_ghg = [20, 20, 5]
    
    #unit conversion to g/tonne -> need the weight of manure by types
    # manure amount (tonne_conv) * SUM (composition of manure type by animal (wComp) * GHG emission per day by animal (ch4_ghg/365))
    tonne_conv = kilos * 0.001
    ch4_r = tonne_conv * (wComp[0] * (ch4_ghg[0]/365) + wComp[1]* (ch4_ghg[1]/365) + wComp[2] * (ch4_ghg[2]/365))
    co2_r = tonne_conv * (wComp[0] * (co2_ghg[0]/365) + wComp[1] * (co2_ghg[1]/365) + wComp[2] * (co2_ghg[2]/365))
    nox_r = tonne_conv * (wComp[0] * (nox_ghg[0]/365) + wComp[1] * (nox_ghg[1]/365) + wComp[2] * (nox_ghg[2]/365))
    sox_r = 0 #value is minimal
    
    ghg_r = [ch4_r,co2_r,nox_r,sox_r]
    
    #GHG captured during the biogas post-treatment process
    #tentatively measured based on the result from biomethane & biogas composition rate
    ch4_c = 0.001 * biomethane(G_in, G_comp)
    co2_c = 0.001 * G_in * G_comp[1] * 0.9 #CO2 recovery rate 90%
    nox_c = 0.001 * G_in * G_comp[2]
    sox_c = 0.001 * G_in * G_comp[3]
    
    ghg_c = [ch4_c,co2_c,nox_c,sox_c]
    
    return ghg_r, ghg_c

def bgm_cost(G_comp, G_in, digOut):
    #wComp, G_in are used for biogas cost
    #digOut is used for biofertilizer cost

    #BIOGAS COST
    #parameters:
    #energy consumtion (ec) = 0.2534 kWh/kg_co2
    #electricity cost = 0.07 USD/kWh
    #area of polymeric membrane required (pma)= 67.7m2/kg_co2
    #polymeric membrane cost = 20 USD/m2
    # 1 m3 (CO2) = 1.836 kg
    ec = 0.2534 * G_in * G_comp[1]*1.836
    pma = 67.7 * G_in * G_comp[1]*1.836
    tc_bg = (ec * 0.07) + (pma * 20)/2738

    #BIOFERTILIZER COST
    #parameters:
    #Treatment cost of raw digestate = 275 USD/tonne
    tc_bf = 275 * digOut * 0.001

    #LABOUR COST
    #assumption: one person is needed to maintain 
    #both biogas upgrading & biofertilizer processing
    #Direct labour cost based on 8h/day; 15$/h
    lc = 8 * 15

    # print("Cost of biogas upgrading:", tc_bg)
    # print("Cost of digesate treatment:",tc_bf)
    # print("Cost of labour:", lc)
    # print("Total operating cost of Biogas Module:", tc_bg + tc_bf + lc)

    return tc_bg + tc_bf + lc



    
