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
with zipfile.ZipFile('DataExtraction.zip') as z:
    for filename in z.namelist():
        if not os.path.isdir(filename):
           
            temp=filename.split('_')
            
            if(temp[len(temp)-1]=='etCO2.csv'):#read the file
                print(filename)
                ctr=0
                with z.open(filename) as f:
                    for line in f:
                        ctr=ctr+1
                        if (ctr<2):
                            continue
                        
                        temp2p=line.decode("utf-8")
                        temp2=temp2p.split(',')
                        if(ctr>=3):
                            tp=t
                        t= dt.datetime.strptime(temp2[1], '%Y-%m-%d %H:%M:%S')#temp2[0]+'T'+temp2[1]
                        if(ctr>=3):
                            if((t-tp).total_seconds()>600):
                                #print('ho')
                                tarr.append([temp[1].split('/')[4],temp[2],t.strftime('%Y-%m-%d %H:%M:%S'), tp.strftime('%Y-%m-%d %H:%M:%S')])
print(tarr)
df=pd.DataFrame(tarr, columns=['PatientID','VisitNo','GapMissingStart','GapMissingEnd'])
df.to_csv('MissingTimes.dat', sep='\t')