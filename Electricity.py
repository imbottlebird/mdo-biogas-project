#cd /Users/niekjansenvanrensburg/Documents/MDO/Assignment_2     

import pandas as pd
import cvxpy as cp
from math import sin, cos, sqrt, atan2, radians, pi

#Parameters
CH4_conv = 0.4

def electricity(CH4):
    elec = CH4*CH4_conv
    if elec >= 10:
        return elec
    else:
        return 0

elec = electricity(60)

print("Amount of electricity produced is "+str(elec)+" kWh")