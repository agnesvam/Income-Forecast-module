import sys
import numpy as np
import pandas as pd
from datetime import datetime
from flask import Blueprint, flash, g,session,render_template, request, redirect,url_for
import cx_Oracle
import json
import plotly
import plotly.express as px
from pmdarima.arima import auto_arima

cx_Oracle.init_oracle_client(lib_dir=r"C:\Oracle\product\19.0.0\client_1\bin")
dsn_tns = cx_Oracle.makedsn('127.0.0.1', '4000', service_name='XE') 
conn = cx_Oracle.connect(user=r'alcs', password='alcs', dsn=dsn_tns)

auth = Blueprint('auth', __name__)

@auth.before_request
def before_request():
#   cur=conn.cursor()
#   cur.execute("""select 
#       regexp_replace(a.com_name,
#                       '[^\r -~]',
#                       '')
# from   als_companies a
# where   (a.com_status = 'VER' or a.com_status = 'ACT')""")
#   res=cur.fetchall()
#   ret= list(map(lambda x: x[0], res))
#   return render_template("login.html", companies=ret)

  if 'user_id' in session and 'com_id' in session:
    #check if user id exists in useers
    g.user=session['user_id']
    g.com= session['com_id']


@auth.route('/login', methods=['GET','POST'])
def login():
  
    if request.method=='POST':
        session.pop('user_id',None)
        company=request.form['comid']
        user_email=request.form['usremail']
        cur=conn.cursor()
        usr_id= get_user_id(user_email,cur)
        
        outVal=cur.var(int)
        sql="""
   begin
     :outVal := sys.diutil.bool_to_int(als_stat.can_run_report
     (:rep,:com,:usr));
   end;
  """
        cur.execute(sql,outVal=outVal,rep='INCOME', com=company,usr=usr_id)

        if outVal.getvalue()==1 :
           session['user_id']= usr_id
           session['com_id'] =company
           return redirect(url_for('auth.income'))
        else:

          #  cur.close()
          #  conn.close()
          return redirect(url_for('auth.login'))
       
    return render_template("login.html" )
        
@auth.route('/income' , methods=['GET','POST'])
def income():
  if not g.user:

    return redirect(url_for('auth.login'))
  if request.method=='POST':
    cust=request.form['cust']
    timescale= request.form.get('timescale')
    option = request.form['options']
    if request.form.get('all_cust'):
      all_cust=1
    else:
      all_cust=0


    #function to get previous income
    re=get_prev_income(g.com, timescale,all_cust,cust)
    idx = [x[0] for x in re]
    vals = [x[1] for x in re]
    df=pd.DataFrame({'date':idx, 'income':vals})
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
   #df['date'] = df['date']
   #resampling for quarter
    df = df.resample('Q',on='date').sum()
    #------train/test split. build model on train data. 
    train_size = int(len(df) * 0.8)
    train, test = df[0:train_size], df[train_size:]
    model=auto_arima(train, start_p=0, start_q=0, max_p=4, max_q=4, m=4,
                             start_P=0, seasonal=True, d=1, D=1, trace=True,
                             error_action='ignore')
    pred = model.predict(n_periods=test.shape[0]+5)
    dd=(pd.to_datetime(pred.index.values , format='%Y-%m-%d')).astype(str).tolist()
    
    d=list(pred.values)
    print('sssssss')
     
    print(pred.index)

    print('sssssss')  

    return render_template("forecast.html",lab= dd, val=d,
    all=all_cust,cust=cust, timescale=timescale, model=option, supp=g.com, res=df.to_html() ,len =len(pred) )

  return render_template('loged.html')


        
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

def get_prev_income(supp_id,timescale, all_cust, cust_name ):
  cur=conn.cursor()
  outVal=cur.var(cx_Oracle.CURSOR)

  sql="""
    declare
  -- Boolean parameters are translated from/to integers: 
  -- 0/1/null <--> false/true/null 
  p_all_customers boolean := sys.diutil.int_to_bool(:p_all_customers);
     begin
      als_stat.find_prev_income(p_label_timescale => :p_label_timescale,
                            p_supplier_id => :p_supplier_id,
                            p_all_customers => p_all_customers,
                            p_customer_name => :p_customer_name,
                            v_res_crs => :v_res_crs);
       end;
     """
  cur.execute(sql,p_label_timescale=timescale,p_supplier_id=supp_id,p_all_customers=all_cust,p_customer_name=cust_name,v_res_crs=outVal)
  res=outVal.getvalue().fetchall()
  return res