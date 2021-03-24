def biomethane(g_in):
    #constants
    ch4_comp = 0.6   #ch4 composition rate
    ch4_pur = 0.965  #ch4 density of biomethane
    v_bm = g_in * (ch4_comp / ch4_pur)  #biomethane produced
    
    print("Daily amount of effleunt gas: ",g_in, "scm/d")
    print("CH4 composition rate: ", ch4_comp)
    print("CH4 purity rate: ", ch4_pur)
    print("------------------------")
    print("Amount of Bio-methane produced: ", v_bm,"scm/d")
    
    return v_bm

def biofertilizer(kilos):
    vs_r = 0.43   #rate of volatile solid in the total manure
    vs = kilos * vs_r  #amount of volatile solid
    
    pdy = (kilos - vs) + (vs * 0.4)  #(non-volatile solid) + (remnants of volatile solid)
    
    print("Total manure processed per day: ", kilos, "kg/d")
    print("Amount of volatile solid: ", vs)
    print("------------------------")
    print("Amount of biofertilizer produced: ", pdy, 'kg/d')
    
    return pdy
    
def ghg(cattle, swine, poultry, g_in):
    #GHG release by manure type (unit: kg/head/yr)
    #CH4: cattle 39.5; swine 18; poultry 0.157
    #CO2: cattle 12; swine 5.47; poultry 0.048
    #NOx: cattle 0.02; swine 0.02; poultry 0.005
    #SOx: 0
    #unit conversion to g/tonne -> need the weight of manure by types
    
    ch4_r = cattle*39.5 + swine*18 + poultry*0.157
    co2_r = cattle*12 + swine*5.47 + poultry*0.048
    nox_r = cattle*0.02 + swine*0.02 + poultry*0.005
    sox_r = 0 #value is minimal
    
    ghg_r = [ch4_r,co2_r,nox_r,sox_r]
    
    #GHG captured during the biogas post-treatment process
    #tentatively measured based on the result from biomethane & biogas composition rate
    #gas composition rate: CH4 60%; CO2 38% (recovery rate 90%); NOX & SOX 1% each
    ch4_c = biomethane(g_in)
    co2_c = ch4_c*0.38*0.9
    nox_c = sox_c = ch4_c*0.01
    
    ghg_c = [ch4_c,co2_c,nox_c,sox_c]
    
    return ghg_r, ghg_c;
    