import csv
from income import get_prev_income
import cx_Oracle
import pandas as pd
from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)

from income import evaluation
import model

cx_Oracle.init_oracle_client(lib_dir=r"C:\Oracle\product\19.0.0\client_1\bin")
dsn_tns = cx_Oracle.makedsn('127.0.0.1', '4000', service_name='XE') 
conn = cx_Oracle.connect(user=r'x', password='x', dsn=dsn_tns)

auth = Blueprint('auth', __name__)

@auth.before_request
def before_request():
  if 'user_id' in session and 'com_id' in session:
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
        outVal=cur.var(str)
        sql="""
   begin
     :outVal := als_usr.user_roles_str (:usr,:com);
   end;
  """
        cur.execute(sql,outVal=outVal,com=com_id,usr=usr_id)
        roles=outVal.getvalue()
        li= ['Administrator', 'General director', 'Financial manager', 'Director']
        if roles is not None: 
         if any(word in roles for word in li):
        # outVal.getvalue()==1 :
           session['user_id']= usr_id
           session['com_id'] =com_id
           return redirect(url_for('auth.income'))
         else:
          return redirect(url_for('auth.login'))
    coms=get_all_com()
    return render_template("login.html", com=coms)
        
@auth.route('/income' , methods=['GET','POST'])
def income():
  if not g.user:
    return redirect(url_for('auth.login'))

  if request.form.get('action') == "Forecast":
   
    cust=request.form.get('com_select')
    timescale= request.form.get('timescale')
    option = request.form['options']
    coms=get_all_com()

    if request.form.get('all_cust'):
      all_cust=1
    else:
      all_cust=0

    if (all_cust==1) and (cust != ''):
      flash('If customer is chosen- total for customers checkbox should not be checked', 'info')
      return render_template('logged.html',com=coms)


    #function to get previous income
    re=get_prev_income(g.com, timescale,all_cust,cust,conn)
    idx = [x[0] for x in re]
    vals = [x[1] for x in re]
    df=pd.DataFrame({'date':idx, 'income':vals})
    if len(re) ==0:
        flash('Not enough info', 'info')
        return render_template('logged.html', com=coms)

    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df=df.resample(model.resampling(timescale),on='date').sum()
  
    if  df.shape[0] < 5:
        flash('Not enough info')
        return render_template('logged.html',com=coms)
      
    if option == 'arma':
     predVal,trainVal,testVal=model.ARMA(df,timescale)
     return redirect(url_for('auth.forecast',predD=predVal,trainD=trainVal,testD=testVal,all=all_cust,cust=cust,timescale=timescale,model=option))

    if option == 'arima':
     predVal,trainVal,testVal=model.ARIMA(df,timescale)
     return redirect(url_for('auth.forecast',predD=predVal,trainD=trainVal,testD=testVal,all=all_cust,cust=cust,timescale=timescale,model=option))

    if option == 'sarima':
     predVal,trainVal,testVal=model.SARIMA(df,timescale)
     return redirect(url_for('auth.forecast',predD=predVal,trainD=trainVal,testD=testVal,all=all_cust,cust=cust,timescale=timescale,model=option))
    
  if request.form.get('action') == "Import":
    return redirect(url_for('auth.imported'))


  coms=get_all_com()
  return render_template('logged.html', com=coms)

@auth.route('/import' , methods=['GET','POST'])
def imported():
  if request.form.get('action') == "Forecast":
    uploaded= request.form['csvfile']
    timescale= request.form.get('timescale')
    option = request.form['options']
    data=[]
    with open(uploaded) as file:
      csvfile=csv.reader(file)
      for row in csvfile:
        data.append(row)
       
    data=pd.DataFrame(data,columns=['date', 'income'])
    evaluated=evaluation(data)
    if evaluated==0:
      flash('Imported file can not be used', 'info')
      return render_template('import.html')
      
    data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')
    data=data.resample(model.resampling(timescale),on='date').sum()
    
    if option == 'arma':
     predVal,trainVal,testVal=model.ARMA(data,timescale)
     return redirect(url_for('auth.forecast',predD=predVal,trainD=trainVal,testD=testVal,timescale=timescale,model=option,data=data.to_html()))

    if option == 'arima':
     predVal,trainVal,testVal=model.ARIMA(data,timescale)
     return redirect(url_for('auth.forecast',predD=predVal,trainD=trainVal,testD=testVal,timescale=timescale,model=option,data=data.to_html()))

    if option == 'sarima':
     predVal,trainVal,testVal=model.SARIMA(data,timescale)
     return redirect(url_for('auth.forecast',predD=predVal,trainD=trainVal,testD=testVal,timescale=timescale,model=option,data=data.to_html()))
    
  return render_template('import.html')


def format_c(content,model):
  content=content.replace('ARIMA', model)
  return content
  

@auth.route('/forecast' , methods=['GET','POST'])
def forecast():
  if request.method=='GET':
    with open("out.txt", "r") as f:
     content = f.read()
    content= format_c(content,request.args.get('model'))

    return render_template("forecast.html",  predD=request.args.get('predD') , trainD=request.args.get('trainD'),
    testD=request.args.get('testD'),
    all=request.args.get('all'),cust=request.args.get('cust'), 
    timescale=request.args.get('timescale'), model=request.args.get('model'), supp=g.com,content=content)

  if request.form['action'] == 'excel':
    model.to_csv(request.args.get('trainD'),request.args.get('predD'))
    flash('saved to CSV file')
    return render_template("forecast.html",  predD=request.args.get('predD') , trainD=request.args.get('trainD'),
    testD=request.args.get('testD'),
    all=request.args.get('all'),cust=request.args.get('cust'), 
    timescale=request.args.get('timescale'), model=request.args.get('model'), supp=g.com)

  if request.form['action'] == 'decomposition':
    model.decomposition(request.args.get('trainD'),request.args.get('testD'),request.args.get('timescale'))
    return render_template('decompose.html')

  if request.form['action'] == 'analysis':
    mae,mape,rmse= model.analyse_accuracy(request.args.get('testD'),request.args.get('predD'),request.args.get('timescale'))

    with open("demo.txt", "a") as f:
      f.write("\n mean absolute error (MAE) : " + str(mae))
      f.write("\n mean absolute percentage error (MAPE) : " + str(mape))
      f.write("\n mean squared error (RMSE) : " + str(rmse))
    with open("demo.txt", "r") as f:
      cont = f.read()
    return render_template("forecast.html",  predD=request.args.get('predD') , trainD=request.args.get('trainD'),
    testD=request.args.get('testD'),
    all=request.args.get('all'),cust=request.args.get('cust'), 
    timescale=request.args.get('timescale'), model=request.args.get('model'), supp=g.com,summary=cont)
    

   
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
  cur.execute("""select regexp_replace(a.com_name, '[^\r -~]','')
from als_companies a
where (a.com_status = 'VER' or a.com_status = 'ACT')""")
  res=cur.fetchall()
  ret= list(map(lambda x: x[0], res))
  ret.insert(0, "")
  return ret


  
@auth.route('/sign_out')
def sign_out():
    session.clear()
    return redirect(url_for('auth.login'))

     
