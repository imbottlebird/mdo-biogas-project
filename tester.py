# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 21:06:01 2021

@author: Ricardo Hopker
"""

# import integrating_modules
from cost_module_funcs2 import *

def tests(func,var,expected_value,err=0.01):
    x = func(*var)
    low = expected_value-expected_value*err
    high = expected_value+expected_value*err
    return (x<high) & (x>low)

all_tests = []
#test for NPV
all_tests.append([npv,[10,2,0.1],8.26])
all_tests.append([npv,[10,1,0],10])
all_tests.append([npv,[10,2,0],10])
all_tests.append([npv,[20,3],15.88])
all_tests.append([total_npv,[10],39.9])
result =[]
for test in all_tests:
    result.append(tests(*test))

df = pd.DataFrame(all_tests,columns=['function name','variables in','expected resuts'])
df['results'] = result
# test_vector = [tests(npv,[P,n],10),