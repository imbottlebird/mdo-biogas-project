def biomethane(G_in, G_comp):
    #G_comp=[ch4Out, co2Out, noxOut, soxOut]
    #constants
    ch4_pur = 0.965  #ch4 density of biomethane in Brazil
    v_bm = G_in * (G_comp[0] / ch4_pur)  #biomethane produced
    
    return v_bm

def scm_to_m3(scm):
    #biomethane storage temperature = 60C (scielo.br)
    #source: https://checalc.com/solved/volconv.html
    K = 273 #temp conversion to Kelvin
    P1 = P2 = 1 #pressure
    T1 = 15 #scm temp
    T2 = 50 #biomethane temp
    m3 = scm * (P1/P2) * ((T2+K)/(T1+K))
    return m3

def biofertilizer(kilos):
    vs_r = 0.43   #rate of volatile solid in the total manure
    vs = kilos * vs_r  #amount of volatile solid
    pdy = (kilos - vs) + (vs * 0.4)  #(non-volatile solid) + (remnants of volatile solid)
    
    return pdy
    
def ghg(kilos, wComp, G_in, G_comp):
    #GHG release by manure type (unit: kg/head/yr) -> g/tonne  (kilos kg/day)
    #CH4: cattle 39.5; swine 18; poultry 0.157
    #CO2: cattle 12; swine 5.47; poultry 0.048
    #NOx: cattle 0.02; swine 0.02; poultry 0.005
    #SOx: 0
    #unit conversion to g/tonne -> need the weight of manure by types
    tonne_conv = kilos * 0.001
    ch4_r = tonne_conv * (wComp[0] * (39.5/365) + wComp[1]* (18/365) + wComp[2] * (0.157/365))
    co2_r = tonne_conv * (wComp[0] * (12/365) + wComp[1] * (5.47/365) + wComp[2] * (0.048/365))
    nox_r = tonne_conv * (wComp[0] * (0.02/365) + wComp[1] * (0.02/365) + wComp[2] * (0.005/365))
    sox_r = 0 #value is minimal
    
    ghg_r = [ch4_r,co2_r,nox_r,sox_r]
    
    #GHG captured during the biogas post-treatment process
    #tentatively measured based on the result from biomethane & biogas composition rate
    ch4_c = tonne_conv * biomethane(G_in, G_comp)
    co2_c = tonne_conv * G_in * G_comp[1] * 0.9 #CO2 recovery rate 90%
    nox_c = tonne_conv * G_in * G_comp[2]
    sox_c = tonne_conv * G_in * G_comp[3]
    
    ghg_c = [ch4_c,co2_c,nox_c,sox_c]
    
    return ghg_r, ghg_c;
    