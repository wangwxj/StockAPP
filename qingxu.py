import pandas as pd 
import datetime
import tushare as ts
import datetime
from datetime import *
import streamlit as st
import altair as alt

pro = ts.pro_api('7791917f1a82bfedc20a7cc06d557c046333a49c987ff8d81f2bc8f7')
st.set_page_config(
    page_title="StockApp",
    layout="wide"
)

trade_date1 = pro.trade_cal(exchange='',start_date='20230223',end_date=datetime.today().strftime("%Y%m%d")).query('is_open==1').sort_values("cal_date")
i = list(trade_date1['cal_date'])
df1=pd.DataFrame()
for j in range(len(i)-1):
    df=pd.DataFrame()
    df=pro.daily(trade_date=i[j])
    hotcode=df.query('pct_chg>9.5').ts_code
    df2=pro.daily(ts_code=','.join(hotcode), start_date=i[j+1],end_date=i[j+1],fields='ts_code,trade_date,pct_chg')
    df1 = pd.concat([df1,df2])
df1['market']=df1.ts_code.str[0:2]
df1.ts_code=df1.ts_code.str[0:6]
df1.trade_date=pd.to_datetime(df1.trade_date,format="%Y-%m-%d")

df1.to_csv("./qingxi.csv",index=0,header=0,mode="a")
df2=pd.read_csv("./qingxi.csv",dtype={'ts_code':str})
df2['trade_date'] = pd.to_datetime(df2['trade_date'],format="%Y-%m-%d")
df2=df2.sort_values("trade_date",ascending=True)
df2=df2.drop_duplicates(subset=['trade_date','ts_code'],keep='last')
df2.to_csv("./qingxi.csv",index=0)

name= pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,name,industry')
name.ts_code=name.ts_code.str[0:6]
df2=pd.merge(df2,name,left_on="ts_code",right_on="ts_code")
dfffzb=df2.query('market==0|market==60')
dfffzb=dfffzb.reset_index().drop('index', axis=1, errors='ignore')
#dfffcy=df2.query('market==30|market==68')
#dfffcy=dfffcy.reset_index().drop('index', axis=1, errors='ignore')
dfffzb["year"]=dfffzb["trade_date"].dt.year
dfffzb["month"]=dfffzb["trade_date"].dt.month

import datetime
now_date = datetime.date(2022, 12, 26)

trade_year=st.sidebar.date_input("Start date",now_date)

data = dfffzb.query(
    "trade_date>= @trade_year"
)


Chartzb = alt.Chart(data).mark_bar(color="red").encode(x=['year','month','date(trade_date):T'],y='sum(pct_chg)')
Chartzb = Chartzb.configure_axis(title='')
st.altair_chart(Chartzb,use_container_width=True)
st.dataframe(data)
