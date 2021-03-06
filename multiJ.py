# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 11:01:17 2021

@author: Ricardo Hopker
"""

import numpy as np
from pymoo.model.problem import Problem
from integrating_modules import biodigestor, cleanXopt
import matplotlib.pyplot as plt
from constants import dict_total
from pymoo.factory import get_sampling, get_crossover, get_mutation
from pymoo.operators.mixed_variable_operator import MixedVariableSampling, MixedVariableMutation, MixedVariableCrossover
from pymoo.algorithms.nsga2 import NSGA2
from pymoo.optimize import minimize
# from pymoo.visualization.scatter import Scatter
import pandas as pd
# from pymoo.util.misc import stack
import scipy.optimize as op
from pymoo.algorithms.so_genetic_algorithm import GA

class BiogasMultiJ(Problem):

    def __init__(self,args):
    # def __init__(self):
        super().__init__(n_var=11,
                         n_obj=2,
                         n_constr=0,
                         xl=np.array([0,1,0,0,
                                      0,0,0,0,0,0,0]),
                         xu=np.array([1,args['ng_max'],args['max_debt'],1,
                                      1,1,1,1,1,1,1]))
        self.args = args.copy()

    def _evaluate(self, X, out, *args, **kwargs):
        x1 =[]
        x2 =[]
        dict_t = self.args
        for i in range(len(X)):
            x = biodigestor(X[i,:],dict_t,1,True,True)
            # x = biodigestor(X[i,:],1,True,True)
            x1.append(x[1])
            x2.append(x[2])
        x1=np.array(x1)
        x2=np.array(x2)
        out["F"] = np.column_stack([x1, x2])
def run_multiJ(dict_t):
# def run_multiJ():
    mask = ["real","int","real","real",
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
    problem = BiogasMultiJ(dict_t)
    # problem = BiogasMultiJ()
    algorithm = NSGA2(pop_size=dict_t['NSGA_pop'],
                  sampling=sampling,
                  crossover=crossover,
                  n_offsprings=dict_t['NSGA_off'],
                  mutation=mutation,
                  eliminate_duplicates=True,
    )
    res = minimize(problem,
                   algorithm,
                   ("n_gen", dict_t['NSGA_gen']),
                   verbose=True,
                   seed=1,
                   save_history=True)
    return res
# run_multiJ()
# run_multiJ(dict_total)
def biodigestorLam1(x,dict_totalUser):
    return biodigestor(cleanXopt(x),dict_totalUser,1,True,False)
def biodigestorLam0(x,dict_totalUser):
    return biodigestor(cleanXopt(x),dict_totalUser,0,True,False)
def plotRes(res,plot,dict_totalUser):
    df = pd.DataFrame(-res.F,columns=['NPV','gwp'])
    dfX = pd.DataFrame(res.X)
    df = pd.concat([df,dfX],axis=1)
    df = df.sort_values(by=['NPV'])
    xAnnot = max(df['NPV'])
    yAnnot = max(df['gwp'])
    annot=[xAnnot, yAnnot]
    if plot:
        fig,ax = plt.subplots()
        ax.scatter(df['NPV'],df['gwp'],s=20,c='r')
        ax.set_xlabel('NPV')
        ax.set_ylabel('gwp')
        ax.plot(df['NPV'],df['gwp'],c='r',lw=1)
        
        ax.scatter(xAnnot,yAnnot,marker='*',c='y',s=120)
    
    n_evals = []    # corresponding number of function evaluations\
    F = []          # the objective space values in each generation
    cv = []         # constraint violation in each generation
    
    
    # iterate over the deepcopies of algorithms
    for algorithm in res.history:
    
        # store the number of function evaluations
        n_evals.append(algorithm.evaluator.n_eval)
    
        # retrieve the optimum from the algorithm
        opt = algorithm.opt
        pop = algorithm.pop
        # store the least contraint violation in this generation
        cv.append(opt.get("CV").min())
    
        # filter out only the feasible and append
        feas = np.where(opt.get("feasible"))[0]
        _F = opt.get("F")[feas]
        _F = pop.get("F")
        F.extend(list(-_F))
    F = pd.DataFrame(list(map(list, F)))
    if plot:
        ax.scatter(F[0],F[1],c='b',s=0.5,)
        ax.set_xlim([-3e6,0])
    return [df,F,annot]
# [df,F,annot] = plotRes(run_multiJ(dict_total),True,dict_total)
class BiogasSingleJ(Problem):

    def __init__(self,args):
    # def __init__(self):
        super().__init__(n_var=11,
                         n_obj=1,
                         n_constr=0,
                         xl=np.array([0,1,0,0,
                                      0,0,0,0,0,0,0]),
                         xu=np.array([1,args['ng_max'],args['max_debt'],1,
                                      1,1,1,1,1,1,1]))
        self.args = args.copy()

    def _evaluate(self, X, out, *args, **kwargs):
        x1 =[]
        # x2 =[]
        dict_t = self.args
        lam = dict_t['lam']
        for i in range(len(X)):
            x = biodigestor(X[i,:],dict_t,lam,True,True)
            # x = biodigestor(X[i,:],1,True,True)
            x1.append(x[0])
            # x2.append(x[2])
        x1=np.array(x1)
        # x2=np.array(x2)
        out["F"] = np.column_stack([x1])
def run_singleJ(dict_t):
# def run_multiJ():
    mask = ["real","int","real","real",
            "int","int","int","int","int","int","int"]
    sampling =  MixedVariableSampling(mask, {
        "real": get_sampling("real_random"),
        "int": get_sampling("int_random")
        })
    crossover = MixedVariableCrossover(mask, {
        "real": get_crossover("real_sbx", prob=0.2, eta=3.0),
        "int": get_crossover("int_sbx", prob=0.2, eta=3.0)
    })
    mutation = MixedVariableMutation(mask, {
        "real": get_mutation("real_pm", eta=3.0,prob=0.02),
        "int": get_mutation("int_pm", eta=3.0,prob=0.02)
    })
    #[V_gBurn,ng,Tdig,debt_level,V_cng_p,e_priceS,farm1,farm2,farm3,farm4,farm5,farm6,farm7]
    problem = BiogasSingleJ(dict_t)
    # problem = BiogasMultiJ()
    algorithm = GA(pop_size=dict_t['GA_pop'],
                  sampling=sampling,
                  crossover=crossover,
                  n_offsprings=dict_t['GA_off'],
                  mutation=mutation,
                  eliminate_duplicates=True,
    )
    res = minimize(problem,
                   algorithm,
                   ("n_gen", dict_t['GA_gen']),
                   verbose=True,
                   seed=1,
                   save_history=True)
    return res
def plotsingle(res):
    n_evals = []    # corresponding number of function evaluations\
    F = []          # the objective space values in each generation
    cv = []         # constraint violation in each generation
    optT=[]
    fig,ax = plt.subplots()
    Fx = []
    # iterate over the deepcopies of algorithms
    it = 0
    for algorithm in res.history:
    
        # store the number of function evaluations
        n_evals.append(algorithm.evaluator.n_eval)
    
        # retrieve the optimum from the algorithm
        opt = algorithm.opt
        pop = algorithm.pop
        # store the least contraint violation in this generation
        cv.append(opt.get("CV").min())
    
        # filter out only the feasible and append
        feas = np.where(opt.get("feasible"))[0]
        feasP = np.where(pop.get("feasible"))[0]
        _opt = opt.get("F")[feas]
        _F = pop.get("F")[feasP]
        F.extend(list(-_F))
        optT.extend(list(-_opt))
        Fx.extend(list(np.ones(len(_F))*it))
        it += 1
        
    # F = pd.DataFrame(list(map(list, F)))
    ax.scatter(Fx,F,c='g',s=0.5,label='Population')
    ax.plot(range(len(optT)),optT,c='r',label='Pareto')
    # ax.set_ylim([-2.5e6,0])
    ax.set_xlabel('Iteration')
    ax.set_ylabel('NPV (R$)')
    ax.legend()
    # fig,ax = plt.subplots()
    # ax.scatter(Fx[0:10000],F[0:10000],c='g',s=0.5,label='Population')
    # ax.plot(range(100),optT[0:100],c='r',label='Pareto')
    # ax.set_ylim([-1e6,0])
    # ax.set_xlabel('Iteration')
    # ax.set_ylabel('NPV (R$)')
    # ax.legend()
    
    
# dict_total['GA_gen'] = 500
# dict_total['GA_pop'] = 100
# res = run_singleJ(dict_total)
# plotsingle(res)