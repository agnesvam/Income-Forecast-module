import json
from datetime import datetime
from income import get_prev_income
import cx_Oracle
import numpy as np
import pandas as pd
import plotly
import plotly.express as px
from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from pmdarima.arima import auto_arima

import income
import model

cx_Oracle.init_oracle_client(lib_dir=r"C:\Oracle\product\19.0.0\client_1\bin")
dsn_tns = cx_Oracle.makedsn('127.0.0.1', '4000', service_name='XE') 
conn = cx_Oracle.connect(user=r'alcs', password='alcs', dsn=dsn_tns)

auth = Blueprint('auth', __name__)

@auth.before_request
def before_request():

  if 'user_id' in session and 'com_id' in session:
    #check if user id exists in useers
    g.user=session['user_id']
    g.com= session['com_id']


@auth.route('/login', methods=['GET','POST'])
def login():
  
    if request.method=='POST':
        session.pop('user_id',None)
        company=request.form.get('com_select')
        user_email=request.form['usremail']
        cur=conn.cursor()

        usr_id= get_user_id(user_email,cur)
        com_id=get_com_id( company,cur)

        outVal=cur.var(int)
        sql="""
   begin
     :outVal := sys.diutil.bool_to_int(als_stat.can_run_report
     (:rep,:com,:usr));
   end;
  """
        cur.execute(sql,outVal=outVal,rep='INCOME', com=com_id,usr=usr_id)

        if outVal.getvalue()==1 :
           session['user_id']= usr_id
           session['com_id'] =com_id
           return redirect(url_for('auth.income'))
        else:
          return redirect(url_for('auth.login'))
       
    coms=get_all_com()
    return render_template("login.html", com=coms )
        
@auth.route('/income' , methods=['GET','POST'])
def income():
  if not g.user:
    return redirect(url_for('auth.login'))

  if request.method=='POST':
    session['df']=None
    cust=request.form.get('com_select')
    timescale= request.form.get('timescale')
    option = request.form['options']
    #all companies for dropdown/
    coms=get_all_com()

    if request.form.get('all_cust'):
      all_cust=1
    else:
      all_cust=0

    if (all_cust==1) and (cust != ''):
      flash('If customer is chosen- total for customers checkbox should not be checked', 'info')
      return render_template('loged.html',com=coms)


    #function to get previous income
    re=get_prev_income(g.com, timescale,all_cust,cust,conn)
    idx = [x[0] for x in re]
    vals = [x[1] for x in re]
    df=pd.DataFrame({'date':idx, 'income':vals})

    if len(re) ==0:
        flash('Not enough info', 'info')
        return render_template('loged.html', com=coms)

    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df=df.resample(model.resampling(timescale),on='date').sum()
  
    if  df.shape[0] < 5:
        flash('Not enough info')
        return render_template('loged.html',com=coms)
      
    if option == 'arma':
     predVal,trainVal,testVal=model.ARMA(df,timescale)
     return redirect(url_for('auth.forecast',predD=predVal,trainD=trainVal,testD=testVal,all=all_cust,cust=cust,timescale=timescale,model=option))

    if option == 'arima':
     predVal,trainVal,testVal=model.ARIMA(df,timescale)
     return redirect(url_for('auth.forecast',predD=predVal,trainD=trainVal,testD=testVal,all=all_cust,cust=cust,timescale=timescale,model=option))

    if option == 'sarima':
     predVal,trainVal,testVal=model.SARIMA(df,timescale)
     return redirect(url_for('auth.forecast',predD=predVal,trainD=trainVal,testD=testVal,all=all_cust,cust=cust,timescale=timescale,model=option))
     

  coms=get_all_com()
  return render_template('loged.html', com=coms)


@auth.route('/forecast/model' , methods=['GET','POST'])
def forecast():

  if request.method=='GET':
    return render_template("forecast.html",  predD=request.args.get('predD') , trainD=request.args.get('trainD'),
  testD=request.args.get('testD'),
  all=request.args.get('all'),cust=request.args.get('cust'), 
  timescale=request.args.get('timescale'), model=request.args.get('model'), supp=g.com)

  if request.form['action'] == 'excel':
    model.to_csv(request.args.get('trainD'),request.args.get('predD'))
    flash('saved to CSV file')
    return render_template("forecast.html",  predD=request.args.get('predD') , trainD=request.args.get('trainD'),
    testD=request.args.get('testD'),
    all=request.args.get('all'),cust=request.args.get('cust'), 
    timescale=request.args.get('timescale'), model=request.args.get('model'), supp=g.com)

  if request.form['action'] == 'decomposition':
    model.decomposition(request.args.get('trainD'),request.args.get('testD'))
    return render_template('decompose.html', name = 'new_plot', url ='web\static\plot.png')
   
def get_user_id(email,cur):
  sql=""" select a.uem_usr_id
from   als_user_emails a
where  a.uem_email like :email
  """
  cur.execute(sql,email=str(email))
  res=cur.fetchone()

  if not res:
        return None
  else:
        ret= res[0]
        return ret

def get_com_id(com,cur):
  sql=""" select a.com_id
from   als_companies a
where  a.com_name like :com_name
  """
  cur.execute(sql,com_name=str(com))
  res=cur.fetchone()
      
  ret= res[0]
  return ret

def get_all_com():
  cur=conn.cursor()
  cur.execute("""select 
      regexp_replace(a.com_name,
                      '[^\r -~]',
                      '')
from   als_companies a
where   (a.com_status = 'VER' or a.com_status = 'ACT')""")
  res=cur.fetchall()
  ret= list(map(lambda x: x[0], res))
  return ret