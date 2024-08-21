#!/usr/bin/python

from time import process_time
t1= process_time()
import xarray as xr
import rioxarray
from rasterio.enums import Resampling
import utility.combine as co
import os, glob, sys
import shutil 
from resource import getrusage, RUSAGE_SELF
import numpy as np


path = os.environ['PATHNAME']
rcp = os.environ['RCP']
stat = os.environ['STAT']
folderNew=os.environ['FOLDERNEW']
name=os.environ['NAME']
minT=int(os.environ['MIN'])
maxT=int(os.environ['MAX'])
soil=os.environ['SOIL']
rcp=str(rcp).zfill(2)
####in combineScript you have to specify if reference period
### if so the years are set
## else you need to specify the min and max year
## also specify if all other variables or soilWaterContent
## they are kept separate since their processing differs a little
## this results in separate files

if minT==1971:
    print('ref')
    year1='1971'
    year2='2000'
    name=''
    folder='climateInterCalculations/climateAnnualCalculations_'+soil+'met_'
    folderNew=folderNew+'1971_2000/'
    outstring=str(rcp)+'_ref'
    print('reference modelling '+str(year1) + ' ' + str(year2), flush=True)
elif name=='eobs':
    year1='1971'
    year2='2000'
    folder='EOBS/climateInterCalculations/'
    outstring='eobs'
    folderNew=folderNew+'eobs/'
    name='climateAnnualCalculations_'
    print('eobs modelling '+str(year1) + ' ' + str(year2), flush=True)
elif name=='forcings' and minT!=1971:
    print(name)
    print(minT)
    name=''
    folderNew=folderNew+'forcings/'
    year1=str(minT)
    year2=str(maxT)
    folder='climateInterCalculations/climateAnnualCalculations_'+soil+'met_'
    outstring = ''+str(rcp)
    print('forcings ' + str(year1) + ' ' + str(year2), flush=True)
elif name=='projection' and minT!=1971:
    name=''
    folderNew=folderNew+str(minT)+'_'+str(maxT)+'/'
    year1=str(minT)
    year2=str(maxT)
    folder='rcp'+rcp+'/'+stat+'/'+soil
    outstring = 'rcp'+rcp+'_quantile'+stat 
    print('modelling '+str(year1) + ' ' + str(year2), flush=True)
else:
    print('Something is wrong, please check your input')
    sys.exit()
print(path+folder+name+outstring+'_*.nc', flush=True)
print(outstring)
print(path+folderNew)

co.combineYears(outstring, name, year1, year2, path, folder, folderNew)

t2= process_time()
print('Processing time in seconds: %f' % (t2-t1))

print(str(round((getrusage(RUSAGE_SELF).ru_maxrss)/1024, 2)) + ' MB RAM used')
