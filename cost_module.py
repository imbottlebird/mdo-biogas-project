# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 14:58:19 2021

@author: Ricardo Hopker
"""


import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import sklearn.metrics as metrics
import numpy as np

url = r'C:\Users\Ricardo Hopker\Massachusetts Institute of Technology\EM.428 MDO Biogas spring 2021 - General'
data = pd.read_csv(url+r'\data from felipe.csv')
inflation_month = pd.read_csv(url+r'\inflation.csv')
inflation_year=inflation_month.div(100)+1
inflation_year=inflation_year.product()
tot_infl = inflation_year.head(11).product()
data['Cost']=data['Cost'].mul(tot_infl)

data_upflow = data[data['Digester Type']=='Upflow System']
data_covered = data[data['Digester Type']=='Covered lagoon']

def linearFit(x,y):
    x_predict = np.linspace(min(x),max(x),100).reshape(-1,1)
    model = LinearRegression(fit_intercept=True)
    model.fit(x,y)
    y_predict =model.predict(x_predict)
    return x_predict,y_predict,model
def logFit(x,y):
    x_out = np.linspace(min(x),max(x),100).reshape(-1,1)
    model = LinearRegression(fit_intercept=True)
    xfit = np.array(x).reshape(-1,1)
    yfit= np.array(y).reshape(-1,1)
    model.fit(xfit,np.log(yfit))
    y_out =model.predict(x_out)
    return x_out,np.exp(y_out),model
def logLogFit(x,y):
    x_out = np.log(np.linspace(min(x),max(x),100).reshape(-1,1))
    model = LinearRegression(fit_intercept=True)
    xfit = np.array(x).reshape(-1,1)
    yfit= np.array(y).reshape(-1,1)
    model.fit(np.log(xfit),np.log(yfit))
    y_out =model.predict(x_out)
    return np.exp(x_out),np.exp(y_out),model
def logxFit(x,y):
    x_out = np.log(np.linspace(min(x),max(x),100).reshape(-1,1))
    model = LinearRegression(fit_intercept=True)
    xfit = np.array(x).reshape(-1,1)
    yfit= np.array(y).reshape(-1,1)
    model.fit(np.log(xfit),yfit)
    y_out =model.predict(x_out)
    return np.exp(x_out),y_out,model
def plot_data(xin,yin,xlabel='',ylabel='',title='',ftype=linearFit):
    x = np.array(xin).reshape(-1,1)
    y = np.array(yin).reshape(-1,1)
    x_predict,y_predict,model = ftype(x,y)
    fig,ax = plt.subplots()
    slope = model.coef_
    intercept = model.intercept_
    
    if ftype==linearFit:
        r2 = metrics.r2_score(y,model.predict(x))
        label='y={:.0f}x+{:.0f}, ($\ r^2 $ = {:.3f})'.format(slope[0][0],intercept[0],r2)
    elif ftype==logFit:
        r2 = metrics.r2_score(np.log(y),model.predict(x))
        label='y={:.3f}exp({:.3f}x), ($\ r^2 $ = {:.3f})'.format(intercept[0],slope[0][0],r2)
    elif ftype==logxFit:
        r2 = metrics.r2_score(y,model.predict(np.log(x)))
        label='y={:.3f}ln(x)+{:.3f}, ($\ r^2 $ = {:.3f})'.format(slope[0][0],intercept[0],r2)
    elif ftype==logLogFit:
        r2 = metrics.r2_score(np.log(y),model.predict(np.log(x)))
        label='ln(y)={:.3f}ln(x)+{:.3f}, ($\ r^2 $ = {:.3f})'.format(slope[0][0],intercept[0],r2)
    ax.plot(x_predict,y_predict,c='r',label=label)
    ax.scatter(x,y,c='b')
    ax.set(xlabel=xlabel,ylabel=ylabel,title=title)
    ax.legend()
    
    return fig,ax, model

xlabel = 'Digestor Volume ($\ m^3 $)'
ylabel = 'Cost (R$)'
title = 'Upflow System'
x = data_upflow['Digester Volume']
y = data_upflow['Cost']
figUp,axUp,modelUp1 = plot_data(x,y,xlabel,ylabel,title,linearFit)
figUp,axUp,modelUp = plot_data(x,y,xlabel,ylabel,title,logFit)
figUp,axUp,modelUp = plot_data(x,y,xlabel,ylabel,title,logxFit)
figUp,axUp,modelUp = plot_data(x,y,xlabel,ylabel,title,logLogFit)

title = 'Covered lagoon'
x = data_covered['Digester Volume']
y = data_covered['Cost']
figCov,axCov,modelCov = plot_data(x,y,xlabel,ylabel,title,linearFit)

title = 'NOx estimator (Euro 5)'
xlabel = 'Vehicle speed ($ km/h $)'
ylabel = 'NOx (g/km)'
x = range(10,110,10)
y=[11,8.3,5,3,2.7,2,1.5,2.2,1.8,1]
figUp,axUp,modelUp = plot_data(x,y,xlabel,ylabel,title,linearFit)
figUp,axUp,modelUp = plot_data(x,y,xlabel,ylabel,title,logFit)
figUp,axUp,modelUp = plot_data(x,y,xlabel,ylabel,title,logxFit)
figUp,axUp,modelUp = plot_data(x,y,xlabel,ylabel,title,logLogFit)