import streamlit as st
import tushare as ts
import numpy as np
import pandas as pd
import altair as alt
import datetime
from datetime import *
from bs4 import BeautifulSoup
import re
import requests
import html5lib
from datetime import datetime
import jqdatasdk
from jqdatasdk import *
auth('15050410156','Ff787878789')

pd.set_option('display.max_rows',1000)
pd.set_option('display.max_columns',1000)

pro = ts.pro_api('7791917f1a82bfedc20a7cc06d557c046333a49c987ff8d81f2bc8f7')
end_date=datetime.today().strftime("%Y%m%d")
trade_date= pro.trade_cal(exchange='', end_date=end_date,is_open='1').sort_values('cal_date')
trade_date.cal_date=pd.to_datetime(trade_date.cal_date,format="%Y-%m-%d")
end_trade_date=list(trade_date.cal_date)[-1]    
start_trade_date=list(trade_date.cal_date)[-7]


def yesterday_data(stock,date):
    yestdf=pd.DataFrame()  
    dff=pd.DataFrame()  
    df=pd.DataFrame()  
    df=get_price(stock,count=1,end_date=date,panel=False,fields=['close','pre_close','high','low','open'])
    dff=df
    dff['code']=stock[0:6]
    yestdf=yestdf.append(dff)
    yestdf["攻击"]=(yestdf.high-yestdf.open)/yestdf.open*100
    yestdf["回头"]=(yestdf.low-yestdf.open)/yestdf.open*100
    yestdf=yestdf
    return yestdf

def get_stocklist(date):
    df=pd.DataFrame()
    url='https://www.xilimao.com/zhangting/'+date+".html"
    res=requests.get(url)
    res.encoding="utf-8"
    soup = BeautifulSoup(res.text, features="html5lib")

    pct_list=[]
    pct=soup.find_all('td',class_="font-num1 text-right up zhangfu cursor-default")
    for a in pct:
        pct_list.append(a.text)

    code_list=[]
    code=soup.find_all('td',class_="font-num1 text-right up zhangfu cursor-default")
    for a in pct:
        code_list.append(a['data-dm'])

    reason_list=[]
    reason=soup.find_all('td',class_="cursor-default reason")
    for a in reason:
        reason_list.append(a.text)

    ban_list=[] 
    ban=soup.select('.lianban span')
    for a in ban:
        ban_list.append(a.text)
        

    stock_list=[]
    stock= soup.findAll('span',class_="mr-2 text-info zt1")
    for a in stock:
         stock_list.append(a.text)

    time_list=[]
    time= soup.findAll(class_='font-num1 text-right fengdan')
    for a in time:
        time_list.append(a.find_next_sibling().find_next_sibling().text) 
    df=pd.DataFrame({"date":date,"code":code_list,"name":stock_list,
                         "pct":pct_list,"time":time_list,"reason":reason_list,"lianban":ban_list})
    df['code']=df['code'].astype(str)
 
    df.lianban= df.lianban.astype(int)
    return df
    
def get_code(val):

    if val[0:2]=="00":
        code=".XSHE"
    elif val[0:2]=="60":
        code=".XSHG"
    elif val[0:2]=="30":
        code=".XSHE"
    elif val[0:2]=="68":
        code=".XSHG"
    return val+code

def get_gongji(stocklist,date):
    df=pd.DataFrame()  
    df=get_price(security=stocklist,end_date=date,count=3,panel=False,fields=['close','high', 'low', 'pre_close','open'])
    df["攻击"]=(df.high-df.open)/df.open*100
    df=pd.pivot_table(df,index=["code"],columns=["time"],values=["攻击"],aggfunc=sum).T.sort_values(by = ['time'], ascending = [False]).T.fillna(0)
    
    df=df.reset_index().drop('index', axis=1, errors='ignore')
    head=[str(c[1]) for c in df.columns]
    df.columns=head
    
    head=[str(c[5:10]) for c in df.columns]
    df.columns=head

    head[0]="code"
    df.columns=head

    df["code"]=df.code.str[0:6]

    
    return df

def get_huitou(stocklist,date):
    
    df=pd.DataFrame()  
    df=get_price(security=stocklist,end_date=date,count=3,panel=False,fields=['close','high', 'low', 'pre_close','open'])
    df["回头"]=(df.low-df.open)/df.open*100
    df=pd.pivot_table(df,index=["code"],columns=["time"],values=["回头"],aggfunc=sum).T.sort_values(by = ['time'], ascending = [False]).T.fillna(0)
    
    df=df.reset_index().drop('index', axis=1, errors='ignore')
    head=[str(c[1]) for c in df.columns]
    df.columns=head
    
    head=[str(c[5:10]) for c in df.columns]
    df.columns=head

    head[0]="code"
    df.columns=head

    df["code"]=df.code.str[0:6]
    return df

def get_gante(stocklist,date):
    
    df=pd.DataFrame()  
    df=get_price(security=stocklist,end_date=date,count=7,panel=False,fields=['close','high', 'low', 'pre_close','open'])
    df["pct"]=(df.close-df.pre_close)/df.pre_close*100
    df=pd.pivot_table(df,index=["code"],columns=["time"],values=["pct"],aggfunc=sum).T.sort_values(by = ['time'], ascending = [False]).T.fillna(0)
    
    df=df.reset_index().drop('index', axis=1, errors='ignore')
    head=[str(c[1]) for c in df.columns]
    df.columns=head
    
    head=[str(c[5:10]) for c in df.columns]
    df.columns=head

    head[0]="code"
    df.columns=head

    df["code"]=df.code.str[0:6]


    return df

def my_code(val):

    if val[0:2]=="00":
        code=".XSHE"
    elif val[0:2]=="60":
        code=".XSHG"
    elif val[0:2]=="30":
        code=".XSHE"
    elif val[0:2]=="68":
        code=".XSHG"
    return val+code

def get_jja(stock,date):
    jjpool=pd.DataFrame()  
    dff=pd.DataFrame()
    df=pd.DataFrame()
    start=date +' 09:20:00'
    end=date+' 15:03:10'
    df=get_ticks(stock,start_dt=start,end_dt=end,fields=["time","current","money","b1_v","b1_p","a1_v","a1_p"],count=None,skip=False) 
    df=pd.DataFrame(df)
    df.time = pd.to_datetime(df.time.astype(int).astype(str))
    df["code"]=stock
    df["money"]=round(df.money/10000/10000,4)
    df["b1_v"]=round(df["b1_v"]/10000,4)
    df["a1_v"]=round(df["a1_v"]/10000,4)
    df["buy1"]=round(df.b1_p*df.b1_v/10000,4)
    df["sale1"]=round(df.a1_p*df.a1_v/10000,4)
    dff=pd.DataFrame({"code":[df.code.max()],"买最高":[df.buy1.max()],"买最新":[df.buy1.iloc[-1]],"卖最高":[df.sale1.max()]})
    dff=round(jjpool.append(dff),2)
    return dff

def block_data(blockdate):
    block_list=pd.DataFrame() 
    data_list=pd.DataFrame() 
    temp1=pd.DataFrame() 
    block_list=get_stocklist(blockdate)
    data_list=get_gante(list(block_list.code.apply(my_code)),blockdate)
    temp1=pd.merge(block_list,data_list,left_on="code",right_on="code",how="left")
    temp1=temp1.reset_index().drop('code2', axis=1, errors='ignore').iloc[:,1:]
    return temp1

def jj_yest(block):
    jj_list=pd.DataFrame()
    yestdf=pd.DataFrame()
    temp2=pd.DataFrame()
    
    for i in list(block):
        try:
            jj_list=jj_list.append(get_jj(i,end_trade_date))
            yestdf=yestdf.append(yesterday_data(i,end_trade_date))
        except:continue
    temp2=pd.merge(yestdf,jj_list,left_on="code",right_on="code",how="left")
    '''head=[str(c) for c in temp2.columns] 
    head[0]="pre_close"
    temp2.columns=head'''
    temp2=temp2
    return temp2

def get_jj(stock,date):
    
    jjpool=pd.DataFrame()  
    dff=pd.DataFrame()
    df=pd.DataFrame()
    start=date +' 09:20:00'
    end=date+' 15:00:10'
    jjpool=pd.DataFrame()  
    dff=pd.DataFrame()
    df=pd.DataFrame()
    df=get_ticks(stock,start_dt=start,end_dt=end,fields=["time","current","money","b1_v","b1_p","a1_v","a1_p","b2_v","b2_p","a2_v","a2_p"],count=None,skip=False) 
    df=pd.DataFrame(df)
    df.time = pd.to_datetime(df.time.astype(int).astype(str))
    df["code"]=stock
    df["money"]=round(df.money/10000/10000,2)
    df["b1_v"]=round(df["b1_v"]/10000,2)
    df["a1_v"]=round(df["a1_v"]/10000,2)
    df["buy1"]=round(df.b1_p*df.b1_v/10000,2)
    df["sale1"]=round(df.a1_p*df.a1_v/10000,2)
    df["b2_v"]=round(df["b2_v"]/10000,4)
    df["a2_v"]=round(df["a2_v"]/10000,4)
    df["buy2"]=round(df.b1_p*df.b2_v/10000,2)
    df["sale2"]=round(df.a1_p*df.a2_v/10000,2)
    dff=pd.DataFrame({"code":[df.code.max()],"开盘额":[df.money.max()],"竞开价":[df.b1_p.iloc[0]],"竞结价":[df.b1_p.iloc[-1]],"买开(亿)":[df.buy1.iloc[0]+df.buy2.iloc[0]],"买结(亿)":[df.buy1.iloc[-1]+df.buy2.iloc[-1]]})
    jjpool=round(jjpool.append(dff),2)
    jjpool['code']=jjpool.code.str[0:6] 
    return jjpool

def daterange(date):
    trade_date1=pro.trade_cal(exchange='', start_date='20200101',end_date=date,is_open='1').sort_values('cal_date')
    trade_date1.cal_date=pd.to_datetime(trade_date.cal_date,format="%Y-%m-%d")
    return trade_date1.cal_date

trade_date.cal_date=daterange(end_trade_date.strftime("%Y-%m-%d")) #end_trade_date.strftime("%Y%m%d")
ban3=[]
ban2=[]
ban1=[]
end_trade_date=list(trade_date.cal_date)[-1]    
start_trade_date=list(trade_date.cal_date)[-7]
stocklist=pd.DataFrame()

for i in trade_date.cal_date[-3:]:
    stocklist=stocklist.append(get_stocklist(i.strftime("%Y-%m-%d")))
    if stocklist.empty:
        continue
    ban3_list=stocklist.query('lianban>=1').code.apply(get_code).tolist()
    ban2_list=stocklist.query('lianban==2').code.apply(get_code).tolist()
    ban1_list=stocklist.query('lianban==1').code.apply(get_code).tolist()
    ban3=ban3+ban3_list
    ban2=ban2+ban2_list
    ban1=ban1+ban1_list
ban3=list(set(ban3))
ban2=list(set(ban2))
ban1=list(set(ban1))
data=ban3

stocklist.drop_duplicates(subset = ["name"],keep="last",inplace=True)
stocklist=stocklist.sort_values("lianban",ascending=False)
get_gongji_list=get_gongji(data,end_trade_date.strftime("%Y-%m-%d"))
get_huitou_list=get_huitou(data,end_trade_date.strftime("%Y-%m-%d"))
get_gante_list=get_gante(data,end_trade_date.strftime("%Y-%m-%d"))
get_gante_list["sum"]=get_gante_list.sum(axis=1)
get_gante_list.sort_values("sum",ascending=False)
get_gante_list=get_gante_list.sort_values("sum",ascending=False).iloc[:,0:-1]
gongjiana=pd.merge(stocklist,get_gongji_list,left_on="code",right_on="code").iloc[:,[1,2,5,6,7,8,9,]].set_index(["code","name","reason","lianban"])
huitouana=pd.merge(stocklist,get_huitou_list,left_on="code",right_on="code").iloc[:,[1,2,5,6,7,8,9,]].set_index(["code","name","reason","lianban"])
final=pd.concat([gongjiana,huitouana],axis=1)
final=final.reset_index().drop('index', axis=1, errors='ignore')
head=[str(c) for c in final.columns]
head[-1]="s "+head[-1]
head[-2]="s "+head[-2]
head[-3]="s "+head[-3]
head[-4]="b "+head[-4]
head[-5]="b "+head[-5]
head[-6]="b "+head[-6]
final.columns=head
final["▏"]="▏ "
my_gante=pd.merge(get_gante_list,final,right_on="code",left_on="code",how="left")
my_gante=my_gante.set_index(['code','name', 'reason', 'lianban', head[4], head[5], head[6], head[7],
       head[8], head[9], '▏']).reset_index()
my_gante.insert(7,'|',"▏ ")
my_gante.to_excel("./block.xlsx")

st.set_page_config(
    page_title="StockApp",
    layout="wide"
)

def my_color(val):
    if val>9:
        color="lightcoral"
    elif val<-9:
        color="green"
    elif 3.5<=val<9:    
        color="orange"
    elif -9<val<=-3.5:    
        color="palegreen"
    else:
        color="white"    
    return 'background-color: %s' % color

df = pd.read_excel("./block.xlsx")

ztri=[str(c) for c in df.columns]
today=ztri[13]

df=round(df.iloc[:,2:],1)

st.sidebar.header("请在这里筛选:")

reason1 = st.sidebar.multiselect(
    "板块:",
    options=df["reason"].unique(),
    default=df["reason"].unique()
)
 
lianban1 = st.sidebar.multiselect(
    "连板:",
    options=df["lianban"].unique(),
    default=df["lianban"].unique()
)


data = df.query(
    "reason == @reason1 & lianban ==@lianban1"
)

pct = st.sidebar.slider('pct', -20.0, 20.0,(-20.0,20.0))

data=data[(data[today]>=pct[0]) & (data[today]<=pct[1])]

data=data.sort_values("lianban",ascending=False)

head=[str(c) for c in data.columns]
source=data.groupby(["reason"])[head[3],head[4],head[5],head[7],head[8],head[9],].sum()
source=source.stack().reset_index()
source.columns=["reason","date","val"]

Chart=alt.Chart(source).mark_bar().encode(
    x='date',
    y='sum(val)',
    color="date",
    column='reason'
).properties(width=50).properties(
    width=alt.Step(10)
)

st.altair_chart(Chart,use_container_width=False)


final=data\
.style.applymap(my_color,subset=data.columns.tolist()[3:6]+data.columns.tolist()[7:10]+data.columns.tolist()[11:])\
.format("{:.1f}",subset=data.columns.tolist()[3:6]+data.columns.tolist()[7:10]+data.columns.tolist()[11:])
st.dataframe(final,height=50*len(data))
