import os, sys
from os import listdir
from os.path import isfile, join
import pandas as pd
import rasterio
import itertools

inputRun='rcp' #'rcp' 'forcings' 'reference'
k = os.environ['K']
rcps=[str(k).zfill(2)]
periods=['2021_2040', '2041_2060', '2061_2080', '2079_2098']
perc=['5', '50', '95']

mypath='/work/reichmut/ClimateData/'
renew=pd.read_csv(mypath+'renameVars.csv')

old=list(renew.iloc[:,0])
new=list(renew.iloc[:,1])


def indexSet(inputName, indexNames):
    with rasterio.open(inputName, 'r+') as scr:
        scr.descriptions = indexNames



def combineFiles(listToIter, appendStr, filename=None, addit=None, *args):
    if addit==None:
        year=listToIter[0].replace("_", "-")
        if inputRun=='forcings':
            filename='biovars_met'+listToIter[1]+'_'+year+'_'+listToIter[2]+'.tif'
            addit='calculationCombine/forcings/'
        elif inputRun=='reference':
            filename='biovars_met'+listToIter[1]+'_1971-2000_'+listToIter[2]+'.tif'
            addit='calculationCombine/1971_2000/'
        else:
            rcpDec=int(listToIter[1])/10
            addit='calculationCombine/'+listToIter[0]+'/'
            filename='biovars_rcp'+str(rcpDec)+'_'+listToIter[2]+'perc_'+year+'_'+listToIter[3]+'.tif'
    print(filename)
    print(appendStr)
    oldFiles=[mypath+addit+f+appendStr for f in old if isfile(mypath+addit+f+appendStr)==True]
    print(oldFiles)
    if len(oldFiles) != 0:
        name=mypath+addit+listToIter[1]+'_'+listToIter[0]+listToIter[2]     
        command1="gdalbuildvrt -a_srs EPSG:3035 -separate " + name+"Inter.vrt " +' '.join(oldFiles)
        command2="gdal_translate -of GTiff -co COMPRESS=LZW -co PREDICTOR=3 " + name+"Inter.vrt " + mypath+addit+filename
        os.system(command1)
        os.system(command2)
        indexSet(mypath+addit+filename, new)
        os.remove(name+"Inter.vrt")



if inputRun=='forcings':
    c = list(itertools.product(periods, rcps, perc)) 
    addit='calculationCombine/forcings/'
    appendStr = ['_'+i[1]+'_'+i[0]+'_'+i[2]+'.tif' for i in c]
    listToIter=c
    [combineFiles(listToIter[i], appendStr[i]) for i in range(0,len(c))]
elif inputRun=='rcp':
    c = list(itertools.product(periods, rcps, perc, perc)) 
    appendStr = ['_rcp'+i[1]+'_quantile'+i[2]+'_'+i[0]+'_'+i[3]+'.tif' for i in c]
    listToIter=c
    [combineFiles(listToIter[i], appendStr[i]) for i in range(0,len(c))]
elif inputRun == 'reference':
    c = list(itertools.product(['1971_2000'], rcps, perc)) 
    appendStr = ['_'+i[1]+'_ref_1971_2000_'+i[2]+'.tif' for i in c]
    listToIter=c
    [combineFiles(listToIter[i], appendStr[i]) for i in range(0,len(c))]