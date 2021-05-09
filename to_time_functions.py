# -*- coding: utf-8 -*-
"""
Created on Sat May  8 20:49:40 2021

@author: Ricardo Hopker
"""

import time
from integrating_modules import biodigestor
from multiJ import run_multiJ,run_singleJ
from constants import dict_total

start = time.time()
res = run_singleJ(dict_total)
end = time.time()
print(end-start)

start = time.time()
res = biodigestor(res.X,dict_total)
end = time.time()
print(end-start)

start = time.time()
res = run_multiJ(dict_total)
end = time.time()
print(end-start)



