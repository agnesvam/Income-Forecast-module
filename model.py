import itertools
import numpy as np
import pandas as pd
import ast 
import sys
import matplotlib.pyplot as plt
from pmdarima.arima import auto_arima
import statsmodels.api as sm
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error

pd.options.display.float_format = '{:.4f}'.format
def ARMA (df,timescale):
    orig_stdout = sys.stdout
    f = open('out.txt', 'w')
    sys.stdout = f 
    train_size = int(len(df) * 0.8)
    train = df[0:train_size]
    test=df[train_size:]
    model=auto_arima(train, start_p=1, start_q=1, max_p=10, max_q=10, m=get_m_value(timescale),
                            seasonal=False, d=None, 
                             stepwise=True , trace=True,error_action='ignore')
    sys.stdout = orig_stdout
    f.close()
    pred = model.predict(n_periods=test.shape[0]+5)
 
    f = open("demo.txt", "w")
    f.write(str(model.summary()))
    f.close()

    TestKeys=(pd.to_datetime(test.index.values , format='%Y-%m-%d')).astype(str).tolist()
    testVal = dict(map(lambda i,j : (i,j) , TestKeys,list(test['income'])))


    TrainKeys=(pd.to_datetime(train.index.values , format='%Y-%m-%d')).astype(str).tolist()
    trainVal = dict(map(lambda i,j : (i,j) , TrainKeys,list(train['income'])))

   
    PredKeys=(pd.to_datetime(pred.index.values , format='%Y-%m-%d')).astype(str).tolist()
    predVal = dict(map(lambda i,j : (i,j) , PredKeys,pred.values))

    return predVal,trainVal,testVal
    


def ARIMA(df,timescale):
    orig_stdout = sys.stdout
    f = open('out.txt', 'w')
    sys.stdout = f  
    train_size = int(len(df) * 0.8)
    train = df[0:train_size]
    test=df[train_size:]
    model=auto_arima(train, start_p=0, start_q=0, max_p=4, max_q=4, m=get_m_value(timescale), seasonal=True, d=None, D=1, stepwise=True ,trace=True,
                             error_action='ignore')

    sys.stdout = orig_stdout
    f.close()
    pred = model.predict(n_periods=test.shape[0]+5)
    
    print(model.summary())
    f = open("demo.txt", "w")
    f.write(str(model.summary()))
    f.close()
    TestKeys=(pd.to_datetime(test.index.values , format='%Y-%m-%d')).astype(str).tolist()
    testVal = dict(map(lambda i,j : (i,j) , TestKeys,list(test['income'])))


    TrainKeys=(pd.to_datetime(train.index.values , format='%Y-%m-%d')).astype(str).tolist()
    trainVal = dict(map(lambda i,j : (i,j) , TrainKeys,list(train['income'])))

   
    PredKeys=(pd.to_datetime(pred.index.values , format='%Y-%m-%d')).astype(str).tolist()
    predVal = dict(map(lambda i,j : (i,j) , PredKeys,pred.values))
    return predVal,trainVal,testVal


def SARIMA(df,timescale):
    orig_stdout = sys.stdout
    f = open('out.txt', 'w')
    sys.stdout = f 

    train_size = int(len(df) * 0.8)
    train = df[0:train_size]
    test=df[train_size:]
    model=auto_arima(train, start_p=0, start_q=0, max_p=10, max_q=10, m=get_m_value(timescale),
                             start_P=0, seasonal=True, d=1, D=2, trace=True,
                             error_action='ignore')
    sys.stdout = orig_stdout
    f.close()
    pred = model.predict(n_periods=test.shape[0]+5)
    f = open("demo.txt", "w")
    f.write(str(model.summary()))
    f.close()
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
   
def decomposition(df,df1,timescale):
    T=ast.literal_eval(df)
    P=ast.literal_eval(df1)
    df= {**T, **P}
    df= pd.DataFrame(df.items(),columns=['date', 'income'])
    
    df['date'] = (pd.to_datetime(df['date'], format='%Y-%m-%d'))
    df=df.resample(resampling(timescale),on='date').sum()
   
    decomp=sm.tsa.seasonal_decompose(df, model='additive',period=1)
    fig=decomp.plot()
    plt.savefig('web\static\plot.png')
    

def analyse_accuracy(df_test, df_pred,timescale):
    
    T=ast.literal_eval(df_test)
    P=ast.literal_eval(df_pred)
    test_size = int(len(T) )
    P = dict(itertools.islice(P.items(),test_size))


    df_test= pd.DataFrame(T.items(),columns=['date', 'income'])
    df_pred=pd.DataFrame(P.items(),columns=['date', 'income'])
    df_test['date'] = (pd.to_datetime(df_test['date'], format='%Y-%m-%d'))
    df_pred['date'] = (pd.to_datetime(df_pred['date'], format='%Y-%m-%d'))
    
    df_test=df_test.resample(resampling(timescale),on='date').sum()
    df_pred=df_pred.resample(resampling(timescale),on='date').sum()
   

    mae = mean_absolute_error(df_test, df_pred)
 #   mape = mean_absolute_percentage_error(df_test['income'], df_pred['income'])
    mape=np.mean(np.abs((df_test['income'] -  df_pred['income']) / df_test['income'])) * 100
    rmse = np.sqrt(mean_squared_error(df_test, df_pred))

    return mae,mape,rmse

