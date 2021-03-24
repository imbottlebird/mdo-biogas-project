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
    
#def ghg(g_in):
    #gas composition rate: CH4 60%, CO2 38%, NOX & SOX 1% each
    