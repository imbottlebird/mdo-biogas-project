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
tests(*all_tests[-1])

# test_vector = [tests(npv,[P,n],10),