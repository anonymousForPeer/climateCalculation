import os
from os import listdir
from os.path import isfile, join
import pandas as pd
import numpy as np
import xarray as xr
import itertools

inputRun='forcings' #'rcp' 'forcings'
perc=['5', '50', '95']

if inputRun=='rcp':
    periods=['2021_2040', '2041_2060', '2061_2080', '2079_2098']#'2021_2040',
    rcps=['26', '45', '85']
    c = list(itertools.product(periods, rcps, perc, perc)) 

elif inputRun=='forcings':
    periods=['1971_2000','2021_2040', '2041_2060', '2061_2080', '2079_2098']
    rcps=['11','12','13','14','32','38','39','42','43','44','45','59','60',
      '61','62','79','80','88','16','17','18','19','33','34','46','48',
      '49','63','64','65','66','01','02','21','23','24','25','27','28',
      '30','31','35','36','37','40','41','50','51','53','54','55','56',
      '57','58','67','68','70','71','72','73','74','75','76','77','78',
      '82','84','85','86','87'] 
    c = list(itertools.product(periods, rcps, perc)) 

mypath='/work/reichmut/ClimateData/'
renew=pd.read_csv(mypath+'renameVars.csv')
old=list(renew.iloc[:,0])

def runTest(iterList, inputRun):

    ident=[]
    result=[]
    rownames=[]
    for i in iterList:
        year=i[0].replace("_", "-")
        if inputRun=='rcp':
            locate = i[0]+'_rcp'+i[1]+'_perc'+i[2]+'_'+i[3]
            appendStr = '_rcp'+i[1]+'_quantile'+i[2]+'_'+i[0]+'_'+i[3]+'.tif'
            addit='calculationCombine/'+i[0]+'/'
            rcps=str(int(i[1])/10)
            filepattern=mypath+addit+'biovars_rcp'+rcps+'_'+i[2]+'perc_'+year+'_'+i[3]+'.tif'
            rowAdd='_'+year+'_'+i[1]+'_'+i[2]+'_'+i[3]
        elif inputRun=='forcings':
            locate=i[0] + '_met_'+i[1]+'_'+i[2]    
            if i[0]=='1971_2000':
                addit='calculationCombine/1971_2000/'
                appendStr = '_'+i[1]+'_ref_'+i[0]+'_'+i[2]+'.tif'
            else:
                addit='calculationCombine/forcings/'
                appendStr = '_'+i[1]+'_'+i[0]+'_'+i[2]+'.tif'
            rowAdd='_'+year+'_'+i[1]+'_'+i[2]
            filepattern=mypath+addit+'biovars_met'+i[1]+'_'+year+'_'+i[2]+'.tif'
            print(filepattern, flush=True)
        oldFiles=[mypath+addit+f+appendStr for f in old if isfile(mypath+addit+f+appendStr)==True]
        if isfile(filepattern)==True:
            print('True', flush=True)
            stacked = []
            with xr.open_dataset(filepattern).isel(x=slice(933,948), y=slice(933,955)) as ds:
                stacked.append(ds)
            stacked=stacked[0]
            print(stacked)
        if len(oldFiles) != 0:
            compare = []
        
            for j in range(0,len(oldFiles)):
                with xr.open_dataset(oldFiles[j]).isel(x=slice(933,948), y=slice(933,955)) as ds:
                    compare.append(ds)
                ident.append(locate)
                rownames.append(old[j]+rowAdd)
            [result.append(np.sum(stacked['band_data'].isel(band=f).values-compare[f]['band_data'].values)) for f in range(0,len(oldFiles))]#
        
    f=pd.concat([pd.Series(rownames), pd.Series(result)], axis=1)
    f.to_csv(mypath+'checkData_'+inputRun+'.csv', index=False)


runTest(c,inputRun)