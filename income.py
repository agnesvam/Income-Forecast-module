import datetime
import cx_Oracle
import pandas as pd


#here getting previous income from DB
def get_prev_income (supp_id,timescale, all_cust, cust_name,conn):
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



#evaluation of imported file
def evaluation(df):
    if  df.shape[0] < 5:
        return 0
    elif isinstance(df['date'], datetime):
        return 0
    elif  (df['income'].any() ==''):
      return 0
