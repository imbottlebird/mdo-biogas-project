# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 11:01:17 2021

@author: Ricardo Hopker
"""

import numpy as np
from pymoo.model.problem import Problem
from integrating_modules import biodigestor, cleanXopt
import matplotlib.pyplot as plt
from pymoo.factory import get_sampling, get_crossover, get_mutation
from pymoo.operators.mixed_variable_operator import MixedVariableSampling, MixedVariableMutation, MixedVariableCrossover
from pymoo.algorithms.nsga2 import NSGA2
from pymoo.optimize import minimize
# from pymoo.visualization.scatter import Scatter
import pandas as pd
# from pymoo.util.misc import stack
import scipy.optimize as op

class BiogasMultiJ(Problem):

    def __init__(self):
        super().__init__(n_var=12,
                         n_obj=2,
                         n_constr=0,
                         xl=np.array([0,1,30,0,0,
                                      0,0,0,0,0,0,0]),
                         xu=np.array([1,3,40,0.8,1,
                                      1,1,1,1,1,1,1]))

    def _evaluate(self, X, out, *args, **kwargs):
        x1 =[]
        x2 =[]
        for i in range(len(X)):
            x = biodigestor(X[i,:],1,True)
            x1.append(x[1])
            x2.append(x[2])
        x1=np.array(x1)
        x2=np.array(x2)
        out["F"] = np.column_stack([x1, x2])

mask = ["real","int","real","real","real",
        "int","int","int","int","int","int","int"]
sampling =  MixedVariableSampling(mask, {
    "real": get_sampling("real_random"),
    "int": get_sampling("int_random")
    })
crossover = MixedVariableCrossover(mask, {
    "real": get_crossover("real_sbx", prob=1.0, eta=3.0),
    "int": get_crossover("int_sbx", prob=1.0, eta=3.0)
})
mutation = MixedVariableMutation(mask, {
    "real": get_mutation("real_pm", eta=3.0),
    "int": get_mutation("int_pm", eta=3.0)
})
#[V_gBurn,ng,Tdig,debt_level,V_cng_p,e_priceS,farm1,farm2,farm3,farm4,farm5,farm6,farm7]
problem = BiogasMultiJ()
algorithm = NSGA2(pop_size=100,
              sampling=sampling,
              crossover=crossover,
              n_offsprings=10,
              mutation=mutation,
              eliminate_duplicates=True,
)
res = minimize(problem,
               algorithm,
               ("n_gen", 100),
               verbose=True,
               seed=1,
               save_history=True)
df = pd.DataFrame(-res.F,columns=['NPV','gwp'])
df = df.sort_values(by=['NPV'])
fig,ax = plt.subplots()
ax.scatter(df['NPV'],df['gwp'],s=7)
ax.set_xlabel('NPV')
ax.set_ylabel('gwp')
ax.plot(df['NPV'],df['gwp'],c='r',lw=0.5)
xAnnot = max(df['NPV'])
yAnnot = max(df['gwp'])
ax.scatter(xAnnot,yAnnot,marker='*',c='y',s=120)

# ps = problem.pareto_set(use_cache=False, flatten=False)
# pf = problem.pareto_front(use_cache=False, flatten=False)

# # Design Space
# plot = Scatter(title = "Design Space", axis_labels="x")
# plot.add(res.X, s=30, facecolors='none', edgecolors='r')
# if ps is not None:
#     plot.add(ps, plot_type="line", color="black", alpha=0.7)
# plot.show()

# # Objective Space
# plot = Scatter(title = "Objective Space")
# plot.add(res.F)
# if pf is not None:
#     plot.add(pf, plot_type="line", color="black", alpha=0.7)
# plot.show()