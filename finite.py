import integrating_modules as I

#change decision variables with detla
def update_s(dec_v,d): 
    x0_delta = dec_v.copy()
    x0_delta[2] = x0_delta[2]+d
    x0_delta[3] = x0_delta[3]+d
    x0_delta[5] = x0_delta[5]+d
    return x0_delta

x0 = [1, 1, 3.84795466e+01, 3.21167571e-03, 0,0.35, 1, 1, 1,1, 0, 0, 0.0]
res_mid = I.biodigestorNPV0(x0)
#Initialize function vector f
f = {}

#run algorithm for each input vector and change to delta

for d in range(7):
    delta = 10**(-d)
    pos_x0 = update_s(x0,delta)
    neg_x0 = update_s(x0,-delta)
    res_pos = I.biodigestorNPV0(pos_x0)
    res_neg = I.biodigestorNPV0(neg_x0)
    f_fin = (res_pos - 2*res_mid + res_neg)/(delta**2) - d**2 #Order magnitude is negative
    f.update({d:f_fin})

print(f)

#xNPV0 =I.cleanXoptNPV0(I.runNPV0())
#print(xNPV0)
#print(I.biodigestorNPV0(xNPV0))


