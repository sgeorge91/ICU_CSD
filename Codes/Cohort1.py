# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 15:47:13 2023

@author: SVG
"""


import os
import numpy as np
import zipfile
import pandas as pd
import datetime as dt
import pymannkendall as mk
import scipy.ndimage as ndimage
tarr=[]
ctr=0
t=0
tp=0
df=pd.read_csv('Cohort1_FailExtTimes.txt',sep='\t')
uid=df['ID'].to_list()
cohort2=[i.split('.')[0] for i in uid]
print(uid)
et=df['ActualExtTime'].to_list()
id_et=dict(zip(uid,et))
rit=df['ActualReintTime']
id_rit=dict(zip(uid,rit))
extsc=df['ExtScore'].to_list()
id_exsc=dict(zip(uid,extsc))

df0=pd.read_csv('patient_icu_ward_stay_list_deid.csv',sep=',')
ddate=df0['death_deid_date'].to_list()
ns=df0['Project ID'].to_list()
vn=df0['icu_visit'].to_list()
uid0=[i+'.'+str(j) for i,j in zip(ns,vn)]
dflag=[0 if pd.isnull(i) else 1 for i in ddate]
id_dflag=dict(zip(uid0,dflag))

arr=[]
def corrfun(t,x,l=1):#ACF(l)
    mx=np.mean(x)
    vx=np.var(x)	
    denom=0.
    rk=0.
    wsi=5
    dis=wsi*l#diatance. eg 10*1=> 10 day bins, 1
    ctr=0
    size=[]
    x=[p-mx for p in x]
    ctrg=0
    xp=[]
    for i in range(0,len(x)-l):
        if((t[i+l]-t[i]).total_seconds()<=dis+(wsi/2.)):
            rk=rk+((x[i])*(x[i+l]))
            ctr=ctr+1
            denom=denom+(x[i]*x[i])
        else:
            ctrg=ctrg+1
        xp.append(x[i])
    rk=rk/denom
    return rk,np.var(xp)

def ews(t_st, a,ws):
    #corr_mat=[]
    a=a[0:len(a)]
    yp=[]
    var=[]
    newlen=int((len(a)-ws)/12)
    for i in range (0,newlen):
        a0=pd.Series(a[i*12:(i*12)+ws])#corrfun(t_st[i+12:i+12+ws],
        yp.append(a0.autocorr())
        #yp.append(corr_mat[i][0])
        var.append(a0.std())
        #var.append(corr_mat[i][1])
    result=mk.hamed_rao_modification_test(yp)
    r1=result[2]
    r2=result[4]
    result=mk.hamed_rao_modification_test(var)
    r3=result[2]
    r4=result[4]
    return(r1,r2,r3,r4)

def outlier(a):
    std=np.std(a)
    m=np.mean(a)
    a=[i-m for i in a]
    for i in range(0,len(a)):
        if(abs(a[i])>3*std):
            a[i]=m
    return(a)
arr=[]
timearr=[]
larr=[]

def evensampling(time,x):
    tp=time[0]
    st=7.5
    tnew=[]
    xnew=[]
    flag=False
    for i in range(1,len(time)):
        gapl=(time[i]-tp).total_seconds()
        if(gapl<st):
            tnew.append(time[i])
            xnew.append(x[i])
            tp=t
        else:
            gapa=int(gapl/5)
            mv=(x[i-1]+x[i])/2
            if (gapa>10):
                flag=True
                continue
            for j in range (0,gapa):
                tnew.append(tp+dt.timedelta(seconds=5))
                xnew.append(mv)
                
            tp=time[i]
    return(tnew,xnew,flag)
            

# if((t-tp).total_seconds()<6):

with zipfile.ZipFile('DataExtraction.zip') as z:
    for filename in z.namelist():
        if not os.path.isdir(filename):
            #print(filename)
            temp=filename.split('_')
           
            if(len(temp)>=4)and(temp[0]!='patient'):
                ID=temp[1].split('/')[4]
                ID=ID+'.'+temp[2]
                #print(ID)
            else:
                continue
            if(ID in uid):
                if(temp[len(temp)-1]=='HR.csv'):#read the file
                    nid=ID
                    
                    ctr=0
                    text=dt.datetime.strptime(id_et[nid], '%d-%m-%Y %H:%M')
                    trit=dt.datetime.strptime(id_rit[nid], '%d-%m-%Y %H:%M')
                    exsc=id_exsc[nid]
                    
                    with z.open(filename) as f:
                        if((trit-text).total_seconds()>60*120 and (float(exsc)>2.5)):
                            print(filename)
                            for line in f:
                                ctr=ctr+1
                                if (ctr<2):
                                    continue
                               
                                temp2p=line.decode("utf-8")
                                temp2=temp2p.split(',')
                                t= dt.datetime.strptime(temp2[1], '%Y-%m-%d %H:%M:%S')
                    
                                if((t>text) and (t<trit) and (temp2[0]=='HR')):
                                    timearr.append(t)
                                    arr.append(float(temp2[2]))
                                if(t>trit):
                                    break
                            if(len(arr)*5<.75*(trit-text).total_seconds()):
                                print("Too Few")
                                arr=[]
                                timearr=[]
                                continue
                            if(len(arr)>2*720):
                                print(text,trit)
                                timearr,arr, flag=evensampling(timearr,arr)
                                if(flag==True):
                                    arr=[]
                                    timearr=[]
                                    continue
                                arr_smooth = ndimage.gaussian_filter1d(arr, sigma=100)
                                arr = arr - arr_smooth
                                arr= outlier(arr)
                                #print(len(arr))
                                res=ews(timearr,arr,720)
                                tarr.append([nid,res[0],res[1],res[2],res[3]])
                                larr.append(len(arr))
                                
                            arr=[]
                            timearr=[]
                        else:
                            continue
dflag_t=[id_dflag[i[0]] for i in tarr]
df2=pd.DataFrame(tarr, columns=['ID','ACF-p','ACF-Tau','Var-p','Var-Tau'])
df2['death_flag']=dflag_t
df2.to_csv('DT_HR_v2_Taus_Cohort1_60min.dat',sep='\t')
