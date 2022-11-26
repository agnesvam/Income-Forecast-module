import pandas as pd
import ast 
import sys
import matplotlib.pyplot as plt
from pmdarima.arima import auto_arima
import statsmodels.api as sm



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
    #print(model.summary())
    #print('model seasonal order', model.seasonal_order)
    pred = model.predict(n_periods=test.shape[0]+5)

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
    
    #print(model.summary())
    #print('model seasonal order', model.seasonal_order)
    pred = model.predict(n_periods=test.shape[0]+5)

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
 
    # print(model.summary())
    # print('model seasonal order', model.seasonal_order)
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
   
def decomposition(df,df1,timescale):
    T=ast.literal_eval(df)
    P=ast.literal_eval(df1)
    df= {**T, **P}
    df= pd.DataFrame(df.items(),columns=['date', 'income'])
    
    df['date'] = (pd.to_datetime(df['date'], format='%Y-%m-%d'))
    df=df.resample(resampling(timescale),on='date').sum()
    #print(df)
    decomp=sm.tsa.seasonal_decompose(df, model='additive',period=1)
    fig=decomp.plot()
    plt.savefig('web\static\plot.png')
    