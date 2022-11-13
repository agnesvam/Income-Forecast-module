from pmdarima.arima import auto_arima
import pandas as pd
from flask import Blueprint, flash, g,session,render_template, request, redirect,url_for

def ARMA (df, train, test):
    model=auto_arima(train, start_p=0, start_q=0, max_p=4, max_q=4, m=4,
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
    


def ARIMA(df,train,test):
    model=auto_arima(train, start_p=0, start_q=0, max_p=4, max_q=4, m=4, start_P=0, seasonal=False, d=1, D=1,  stepwise=True ,trace=True,
                             error_action='ignore')

    pred = model.predict(n_periods=test.shape[0]+5)
    model=auto_arima(train, start_p=0, start_q=0, max_p=4, max_q=4, m=4, start_P=0, seasonal=False, d=0, stepwise=True , trace=True,  error_action='ignore')
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


def SARIMA(df,train,test):
    model=auto_arima(train, start_p=0, start_q=0, max_p=4, max_q=4, m=4,
                             start_P=0, seasonal=True, d=1, D=1, trace=True,
                             error_action='ignore')

 
    pred = model.predict(n_periods=test.shape[0]+5)
 
  
    model=auto_arima(train, start_p=0, start_q=0, max_p=4, max_q=4, m=4, start_P=0, seasonal=False, d=0, stepwise=True , trace=True,  error_action='ignore')
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

