import pandas as pd
import ast
from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from pmdarima.arima import auto_arima


def ARMA (df,timescale):
    train_size = int(len(df) * 0.8)
    train = df[0:train_size]
    test=df[train_size:]
    model=auto_arima(train, start_p=0, start_q=0, max_p=4, max_q=4, m=get_m_value(timescale),
                             start_P=0, seasonal=False, d=0, 
                             stepwise=True , trace=True,error_action='ignore')
    print(model.summary())
    print('model seasonal order', model.seasonal_order)
    pred = model.predict(n_periods=test.shape[0]+5)

    TestKeys=(pd.to_datetime(test.index.values , format='%Y-%m-%d')).astype(str).tolist()
    testVal = dict(map(lambda i,j : (i,j) , TestKeys,list(test['income'])))


    TrainKeys=(pd.to_datetime(train.index.values , format='%Y-%m-%d')).astype(str).tolist()
    trainVal = dict(map(lambda i,j : (i,j) , TrainKeys,list(train['income'])))

   
    PredKeys=(pd.to_datetime(pred.index.values , format='%Y-%m-%d')).astype(str).tolist()
    predVal = dict(map(lambda i,j : (i,j) , PredKeys,pred.values))

    return predVal,trainVal,testVal
    


def ARIMA(df,timescale):
    train_size = int(len(df) * 0.8)
    train = df[0:train_size]
    test=df[train_size:]
    model=auto_arima(train, start_p=0, start_q=0, max_p=4, max_q=4, m=get_m_value(timescale), start_P=0, seasonal=False, d=1, D=1,  stepwise=True ,trace=True,
                             error_action='ignore')

    pred = model.predict(n_periods=test.shape[0]+5)
    print(model.summary())
    print('model seasonal order', model.seasonal_order)
    pred = model.predict(n_periods=test.shape[0]+5)

    TestKeys=(pd.to_datetime(test.index.values , format='%Y-%m-%d')).astype(str).tolist()
    testVal = dict(map(lambda i,j : (i,j) , TestKeys,list(test['income'])))


    TrainKeys=(pd.to_datetime(train.index.values , format='%Y-%m-%d')).astype(str).tolist()
    trainVal = dict(map(lambda i,j : (i,j) , TrainKeys,list(train['income'])))

   
    PredKeys=(pd.to_datetime(pred.index.values , format='%Y-%m-%d')).astype(str).tolist()
    predVal = dict(map(lambda i,j : (i,j) , PredKeys,pred.values))
    return predVal,trainVal,testVal


def SARIMA(df,timescale):
    train_size = int(len(df) * 0.8)
    train = df[0:train_size]
    test=df[train_size:]
    model=auto_arima(train, start_p=0, start_q=0, max_p=4, max_q=4, m=get_m_value(timescale),
                             start_P=0, seasonal=True, d=1, D=1, trace=True,
                             error_action='ignore')

 
    pred = model.predict(n_periods=test.shape[0]+5)
 
    print(model.summary())
    print('model seasonal order', model.seasonal_order)
    pred = model.predict(n_periods=test.shape[0]+5)

    TestKeys=(pd.to_datetime(test.index.values , format='%Y-%m-%d')).astype(str).tolist()
    testVal = dict(map(lambda i,j : (i,j) , TestKeys,list(test['income'])))

    TrainKeys=(pd.to_datetime(train.index.values , format='%Y-%m-%d')).astype(str).tolist()
    trainVal = dict(map(lambda i,j : (i,j) , TrainKeys,list(train['income'])))

   
    PredKeys=(pd.to_datetime(pred.index.values , format='%Y-%m-%d')).astype(str).tolist()
    predVal = dict(map(lambda i,j : (i,j) , PredKeys,pred.values))
    return predVal,trainVal,testVal


def resampling(scale):
    if scale =='year':
        return 'A'
    elif scale == 'quarter':
        return 'Q'
    elif scale == 'month':
        return 'M'
    elif scale == 'week':
        return 'W'
    else:
        return 0

def get_m_value(scale):
    if scale =='year':
        return 1
    elif scale == 'quarter':
        return 4
    elif scale == 'month':
        return 12
    elif scale == 'week':
        return 52
    else:
        return 0

def to_csv(df,df1):

    T=ast.literal_eval(df)
    P=ast.literal_eval(df1)
    df= {**T, **P}
    with open("prediction.csv", 'w') as file:
     for key, value in df.items():
        file.write(f"{key},{value}\n")
   