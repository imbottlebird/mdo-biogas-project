import integrating_modules as I

args = (0.01,True,False,False,True)
x0 = [0.0006, 1, 36.90369, 0.00010,1, 1, 0, 0, 0, 0, 0, 0]
#[V_gBurn,ng,Tdig,debt_level,V_cng_p,farm1,farm2,farm3,farm4,farm5,farm6,farm7]

#change decision variables with detla
def update_s(dec_v,d,n): 
    x0_delta = dec_v.copy()
    x0_delta[n] = x0_delta[n]+d
    return x0_delta


#x0 = I.fminClean(xt, args) 
res_mid = I.cleanBiodigestor(x0, args)
#Initialize function vector f
f = {}

#run algorithm for each input vector and change to delta

for s in [0, 3, 4]:
    #git sprint(s)
    for d in range(7):
        delta = 10**(-d)
        pos_x0 = update_s(x0,delta,s)
        neg_x0 = update_s(x0,-delta,s)
        #print(d)
        #print(pos_x0)
        #print(x0)
        #print(neg_x0)
        res_pos = I.cleanBiodigestor(pos_x0,args)
        res_neg = I.cleanBiodigestor(neg_x0,args)
        f_fin = (res_pos - 2*res_mid + res_neg)/(delta**2) - d*2 
        #print('VARIABLE #'+str(s)+' ORDER-'+str(d)+': Delta is '+str(delta)+' & + finite is '+str(res_pos)+' \
        #- finite is '+str(res_neg)+' and the same is '+str(res_mid))
        f.update({(s,d):f_fin})

print(f)

#xNPV0 =I.cleanXoptNPV0(I.runNPV0())
#print(xNPV0)
#print(I.biodigestorNPV0(xNPV0))


