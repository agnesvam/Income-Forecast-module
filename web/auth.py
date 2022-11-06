import sys
from flask import Blueprint, flash, g,session,render_template, request, redirect,url_for
import cx_Oracle
cx_Oracle.init_oracle_client(lib_dir=r"C:\Oracle\product\19.0.0\client_1\bin")
dsn_tns = cx_Oracle.makedsn('127.0.0.1', '4000', service_name='XE') 
conn = cx_Oracle.connect(user=r'alcs', password='alcs', dsn=dsn_tns)

auth = Blueprint('auth', __name__)

@auth.before_request
def before_request():
  cur=conn.cursor()
  cur.execute("""select 
      regexp_replace(a.com_name,
                      '[^\r -~]',
                      '')
from   als_companies a
where   (a.com_status = 'VER' or a.com_status = 'ACT')""")
  res=cur.fetchall()
  ret= list(map(lambda x: x[0], res))
  return render_template("login.html", companies=ret)

  # if 'user_id' in session:
  #   #check if user id exists in useers
  #   g.user=session['user_id']


@auth.route('/login', methods=['GET','POST'])
def login():
  
    if request.method=='POST':
        session.pop('user_id',None)
       # company=request.form['comid']
        user_email=request.form['usremail']
        cur=conn.cursor()
        
        usr_id= get_user_id(user_email,cur)
        company= get_com_id(request.form.get('com'),cur)
  
       

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

           return redirect(url_for('auth.income'))
        else:

          #  cur.close()
          #  conn.close()

          return redirect(url_for('auth.login'))
       
    return render_template("login.html" )
        
@auth.route('/income')
def income():
  if not g.user:
    return redirect(url_for('auth.login'))
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
