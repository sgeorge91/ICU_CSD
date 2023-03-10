# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 15:47:13 2023

@author: SVG
"""


import os
import zipfile
import pandas as pd
import datetime as dt
tarr=[]
ctr=0
t=0
tp=0
df=pd.read_csv('patient_icu_ward_stay_list_deid.csv',sep=',')
ns=df['Project ID'].to_list()
vn=df['icu_visit'].to_list()
uid=[i+'.'+str(j) for i,j in zip(ns,vn)]
et=df['extubation_deid_date'].to_list()
id_et=dict(zip(uid,et))
feflag=df['failed_extubation_flag'].to_list()
print(feflag)
etime=df['extubation_deid_date'].to_list()

extscore=df['extubation_score'].to_list()
id_fe=dict(zip(uid,feflag))
id_et=dict(zip(uid,etime))
id_exsc=dict(zip(uid,extscore))


#df = pd.read_csv(zf.open('intfile.csv'))

with zipfile.ZipFile('DataExtraction.zip') as z:
    for filename in z.namelist():
        if not os.path.isdir(filename):
            #print(filename)
            temp=filename.split('_')
            try:
                if(temp[len(temp)-1]=='etCO2.csv'):#read the file
                    temp1=filename.split('/')
                    temp2=temp1[len(temp1)-1]
                    temp3=temp2.split('_')
                    tuid=temp3[0]+'.'+temp3[1]
                    print(id_fe[tuid]==1)
                    if(id_fe[tuid]==1):
                        continue
                    print(filename)
                    t0=dt.datetime.strptime(id_et[tuid],'%d/%m/%Y %H:%M')
                    
                    ctr=0
                    df=pd.read_csv(z.open(filename))
                    
                    etime=df['record_date_time'].iloc[-1]
                    print(etime)
                    t = dt.datetime.strptime(etime, '%Y-%m-%d %H:%M:%S')
                    diff=abs((t-t0).total_seconds())
                    tarr.append([tuid,etime,id_et[tuid],diff,id_exsc[tuid]])
            except:
                continue
print(tarr)
df=pd.DataFrame(tarr, columns=['PatientID','EtCO2endTime','ExtubationTime','Difference','ExtScore'])
df.to_csv('ExtubationTimes_EtCO2.dat', sep='\t')