# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 01:19:36 2023

@author: SVG
"""
import random
import datetime as dt
import pandas as pd
df0=pd.read_csv('patient_icu_ward_stay_list_deid.csv',sep=',')
ns=df0['Project ID'].to_list()
vn=df0['icu_visit'].to_list()
uid=[i+'.'+str(j) for i,j in zip(ns,vn)]

dobs=df0['birth_deid_date']
dobs=[dt.datetime.strptime(i,'%d/%m/%Y').date() for i in dobs]

sd=df0['icu_start_deid_dttm'].to_list()
sd=[dt.datetime.strptime(i,'%d/%m/%Y %H:%M').date() for i in sd]

age=[(i-j).days for i,j in zip(sd,dobs)]
id_age=dict(zip(uid,age))

df=pd.read_csv('Cohort1_SuccessExtTimes.txt',sep='\t')
df2=pd.read_csv('Cohort2_FailExtTimes.txt',sep=',')
df2['age']=[id_age[i] for i in df2['ID']]
df['age']=[id_age[i] for i in df['PatientID']]



uid2=df2['ID'].to_list()
cohort2=[i.split('.')[0] for i in uid2]
print(uid2)
et2=df2['ActualExtTime'].to_list()
id_et2=dict(zip(uid2,et2))
rit2=df2['ActualReintTime'].to_list()
id_rit2=dict(zip(uid2,rit2))


###DURATION ARRAY
a123=[dt.datetime.strptime(i, '%d-%m-%Y %H:%M') for i in df2['ActualExtTime']]
a123p=[dt.datetime.strptime(i, '%d-%m-%Y %H:%M') for i in df2['ActualReintTime']]
dur=[(i-j).total_seconds() for i,j in zip(a123p,a123)]

def reint_dur():
    
    
    #df2['Duration']=df2['ActualExtTime']-df2['ActualReintTime']
    #df2p=df2.loc[df2['Duration']>7200]
    rid=0
    while (rid< 7200):
        rid=random.sample(dur,1)[0]
    #text=dt.datetime.strptime(id_et2[rid], '%d-%m-%Y %H:%M')
    #trit=dt.datetime.strptime(id_rit2[rid], '%d-%m-%Y %H:%M')
    delt=rid#(trit-text).total_seconds()

    return(delt)




#labels=[q1,q2,q3,q4, q5, q6, q7, q8, q9, q10]
#df['quantiles']=pd.qcut(df.age, q = 10, labels = labels)
qts=[.1, .2, .3, .4, .5, .6, .7, .8, .9, 1.]
qs=df2.quantile(qts,  interpolation="nearest").age
carr=[]
for i in qts:
    carr.append(len(df.loc[df['age']<qs[i]]))
print(carr)

for i in range (len(carr)-1,0,-1):
    carr[i]=carr[i]-carr[i-1]
minval=min(carr)

strat_arr=[]
dfn=df.loc[df['age']<qs[.1]].sample(minval)
strat_arr.append(dfn.values.tolist())
for i in range(1,len(qts)):
    #dfn=df.loc[df['age']<qs[i]].sample(minval)
    dfn=df.loc[(df['age'] >= qs[qts[i-1]]) & (df['age'] <= qs[qts[i]])].sample(minval)
    strat_arr.append(dfn.values.tolist())
strat_arr1=[]
ritimes=[]
for i in range(0,len(strat_arr)):
    for j in range(0, len(strat_arr[i])):
        strat_arr1.append(strat_arr[i][j])
        ritimes.append(reint_dur())
df3=pd.DataFrame(strat_arr1, columns=df.columns)
df3['Reint']=ritimes
df3.to_csv('v2_Stratified_Cohort1.dat',sep='\t')
