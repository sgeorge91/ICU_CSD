# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 18:07:54 2023

@author: SVG
"""


import pandas as pd
import numpy as np
import datetime as dt
df=pd.read_csv('patient_icu_ward_stay_list_deid.csv',sep=',')
ns=df['Project ID'].to_list()
vn=df['icu_visit'].to_list()
uid=[i+'.'+str(j) for i,j in zip(ns,vn)]
et=df['extubation_deid_date'].to_list()
id_et=dict(zip(uid,et))
feflag=df['failed_extubation_flag'].to_list()
fetime=df['failed_extubation_deid_date'].to_list()
ritime=df['re_intubation_deid_date'].to_list()
extscore=df['extubation_score'].to_list()
id_fe=dict(zip(uid,feflag))
id_fet=dict(zip(uid,fetime))
id_rit=dict(zip(uid,ritime))
id_exsc=dict(zip(uid,extscore))


df2=pd.read_csv('MissingTimes.dat',sep='\t')
ns2=df2['PatientID'].to_list()
vn2=df2['VisitNo'].to_list()
uid2=[i+'.'+str(j) for i,j in zip(ns2,vn2)]
ts2_1=df2['GapMissingStart'].to_list()
ts2_2=df2['GapMissingEnd'].to_list()
list1=[[a_ , b_ , c_] for a_, b_,c_ in zip(uid2, ts2_1,ts2_2)] 
times_dict = dict()
rinttime_dict=dict()
for line in list1:
    #print(line)
    if line[0] in times_dict:
        # append the new number to the existing array at this slot
        times_dict[line[0]].append(line[1])
        rinttime_dict[line[0]].append(line[2])
    else:
        # create a new array in this slot
        times_dict[line[0]] = [line[1]]
        rinttime_dict[line[0]]=[line[2]]

tarr=[]
exttime=[]
ext_t=[]
tmin=[]
reinttime=[]
reint_t=[]
uidarr=[]
#rec_time=[]
for i in uid:
    
    try:
        if(id_fe[i]==1):
            temp=times_dict[i]
            temp2=rinttime_dict[i]
            t0=dt.datetime.strptime(id_fet[i],'%d/%m/%Y %H:%M')
            for j in range(0,len(temp)):
                t= dt.datetime.strptime(temp[j], '%Y-%m-%d %H:%M:%S')
                tarr.append(abs((t-t0).total_seconds()))
                exttime.append(temp[j])
                reinttime.append(temp2[j])
            uidarr.append(i)
            tmin.append(min(tarr))
            print(i,tarr)
            ext_t.append(exttime[np.argmin(tarr)])
            reint_t.append(reinttime[np.argmin(tarr)])
            #rec_time.append(id_et[i])
            reinttime=[]
            tarr=[]
            exttime=[]
        else:
            continue
    except:
        continue
fout=open('FailExtTimes_EtCO2.dat','w')
fout.write('ID\tExtDuration\tExtTime\tReintTime\tRecordedExtTime\tRecordedReint\tExtFailFlag\n')
for i in range (0,len(tmin)):
    fout.write(str(uidarr[i])+'\t'+str(tmin[i])+'\t'+str(ext_t[i])+'\t'+str(reint_t[i])+'\t'+str(id_fet[uidarr[i]])+'\t'+str(id_rit[uidarr[i]])+'\t'+str(id_fe[uidarr[i]])+'\t'+str(id_exsc[uidarr[i]])+'\n')
fout.close()