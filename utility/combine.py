#!/usr/bin/python

import xarray as xr
import rioxarray
from rasterio.enums import Resampling
import os, glob, sys
import shutil
import numpy as np
import itertools

perc = ['5', '50', '95']#

def indexSet(filename_1, filename):

    command = "gdal_translate -of GTiff -co COMPRESS=LZW -co PREDICTOR=3 "+ filename_1 + " "+ filename
    os.system(command)
    os.remove(filename_1)



def combineYears(outstring, name, year1, year2, path, folder, folderNew):
    '''
    Calculates quantiles for epoches of 20 years. Maximum value to 95th percentile,
    minimum values to 5th percentile, all other to 50th percentile.
    Can be used for all variables including Soil and reference period. 

    '''
    
    data=[]
    with xr.open_mfdataset(path+folder+name+outstring+'_[0-9]*.nc').sel(time=slice(year1+'-12-31',year2+'-12-31')) as ds: #SoilWaterContent_
        data.append(ds)
    data=data[0]

    mask=[]
    with xr.open_dataset('mask.nc') as ds:
        for i in range(1,len(data.time)+1):
            mask.append(ds)

    
    mask = xr.concat(mask, dim='time')

    print(path+folder+name+outstring+'_*.nc', flush=True)

    annualIdx = np.array(data.coords['time'], dtype='datetime64')
    mask = mask.assign(time=annualIdx)
    for i in list(itertools.product(perc, data.data_vars)):
        print(i, flush=True)
        if data[i[1]].dtype=='timedelta64[ns]':
            print('timedelta')
            input = data[i[1]].dt.days.astype('int32')
            input = input.rename(i[1])
        else:
            input = data[i[1]]
        
        if 'lat' in input.dims:
             input=input.rename(dict(lon='longitude', lat='latitude'))
        input = input.where(mask['mask']==1)
        quan  = input.chunk(dict(time=-1)).quantile(int(i[0])/100, 'time')

        repro = quan.rio.write_crs('EPSG:4326')
        repro = repro.round(decimals=4)
        repro = repro.astype('float32')
        resample = repro.rio.reproject('EPSG:3035', resolution=(3000,-3000), resampling=Resampling.nearest) #resolution=(1000,-1000)
        filename_1 = path+folderNew+i[1]+'_'+outstring+'_'+year1+'_'+year2+i[0]+'_uncom.tif'
        filename = path+folderNew+i[1]+'_'+outstring+'_'+year1+'_'+year2+'_'+i[0]+'.tif'
        resample.rio.to_raster(filename_1)
        indexSet(filename_1, filename)
        resample=None