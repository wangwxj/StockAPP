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

trade_date1 = pro.trade_cal(exchange='',start_date='20230101',end_date=datetime.today().strftime("%Y%m%d")).query('is_open==1').sort_values("cal_date")
i = list(trade_date1['cal_date'])
df1=pd.DataFrame()
for j in range(len(i)-1):
    df=pd.DataFrame()
    df=pro.daily(trade_date=i[j])
    hotcode=df.query('pct_chg>9.5').ts_code
    df2=pro.daily(ts_code=','.join(hotcode), start_date=i[j+1],end_date=i[j+1],fields='ts_code,trade_date,pct_chg')
    df1 = pd.concat([df1,df2])

df1['market']=df1.ts_code.str[0:2]
dfffzb=df1.query('market=="00"|market=="60"')
dfffcy=df1.query('market=="30"|market=="68"')

col1, col2 = st.columns(2)

with col1:
	Chartzb = alt.Chart(dfffzb).mark_bar(color="red").encode(
  	  x='trade_date',
   	 y='sum(pct_chg)'
    
	)
	Chartzb = Chartzb.configure_axis(title='')
	st.altair_chart(Chartzb,use_container_width=True)
	
	st.dataframe(dfffzb)
with col2:
	Chartcy = alt.Chart(dfffcy).mark_bar(color="red").encode(
   	 x='trade_date',
    	y='sum(pct_chg)'
    
	)
	Chartcy = Chartcy.configure_axis(title='')
	st.altair_chart(Chartcy,use_container_width=True)
	st.dataframe(dfffcy)
