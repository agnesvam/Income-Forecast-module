from flask import Blueprint, render_template, request, redirect,url_for
import cx_Oracle

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['comid']
        password=request.form['usrid']
        conn=None

        try:
         cx_Oracle.init_oracle_client(lib_dir=r"C:\Oracle\product\19.0.0\client_1\bin")
         dsn_tns = cx_Oracle.makedsn('127.0.0.1', '4000', service_name='XE') 
         conn = cx_Oracle.connect(user=r'alcs', password='alcs', dsn=dsn_tns)
         cur=conn.cursor()

         outVal=cur.var(int)
         sql="""
   begin
     :outVal := sys.diutil.bool_to_int(als_stat.can_run_report
     (:rep,:com,:usr));
   end;
  """
         cur.execute(sql,outVal=outVal,rep='INCOME', com=username,usr=password)

         if outVal.getvalue()==1 :
           return render_template("loged.html" )
         else:
           return render_template("login.html" )
        finally:
            if conn is not None:
             conn.close()


    return render_template("login.html" )
        



        



