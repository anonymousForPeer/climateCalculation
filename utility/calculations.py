#!/usr/bin/python

import os
import numpy as np
import xclim as xc
import xarray as xr

def chunking(chunks, latrange, lonrange):
    '''
    For array chunking the dataset. Necessary since dask_jobquee not working on EVE
    and we need to shrink the datasize

    '''

    xsize = lonrange #1664
    x=[x.tolist() for x in np.array_split(range(xsize), chunks)]
    xextend = [[sublist[0],sublist[-1]+1] for sublist in x]
    ysize = latrange #1168
    y=[y.tolist() for y in np.array_split(range(ysize), chunks)]
    yextend = [[sublist[0],sublist[-1]+1] for sublist in y]

    return xextend,yextend


def writeOut(var, extraString, path, folder, iteration, zip=False):
    '''
    Depending on status write out netcdf file to either working output directory or final diectory.

    var = variable to write to netcdf file

    extraString = name of file

    path = ueses the defined path

    folder = safes files to defined

    '''
    pathName = path+folder

    if os.path.isdir(pathName)==False:
        os.mkdir(pathName)

    if zip==True:
        comp = dict(zlib=True, complevel=1, dtype='float32')
        encoding = {var: comp for var in var.data_vars}
        var.to_netcdf(pathName+extraString+str(iteration)+".nc", format="NETCDF4", encoding=encoding)
    if zip==False:
        encoding = {'latitude': {'zlib': True, "complevel": 1},'longitude': {"zlib": True, "complevel": 1}, 'time': {"zlib": True, "complevel": 1}}
        var.to_netcdf(pathName+extraString+str(iteration)+".nc", format="NETCDF4_CLASSIC", encoding=encoding)



def statValue(array1, timerange, stat):
    '''
    Calculating standard statistics of climatic variables.

    array1 = input variable

    timerange = defined frequency of calculation

    stat = statistical calculation

    '''
    if stat == 'mean':
        return array1.resample(time=timerange).mean('time', keep_attrs=True)
    if stat == 'max':
        return array1.resample(time=timerange).max('time', keep_attrs=True)
    if stat == 'min':
        return array1.resample(time=timerange).min('time', keep_attrs=True)
    if stat == 'std':
        return array1.resample(time=timerange).std('time', keep_attrs=True)
    if stat == 'sum':
        return array1.resample(time=timerange).sum('time', keep_attrs=True)
    else:
        return 'Please choose between "min", "max", "mean" or "std"'

def dateToTime(dataarray, freq):
    '''
    Grouping by years or seasons
    dataarray = input DataArray

    freq = frequency of resample

    '''
    if freq == 'YS':
        date2Time = dataarray.resample(time="1Y").mean("time", keep_attrs=True)
    if freq == 'QS-DEC':
        date2Time = dataarray.resample(time="QS-DEC").mean("time", keep_attrs=True)
    else:
        'please choose either years freq="YS" or seasons freq="QS-DEC"'
    return date2Time

def namedArray(dataarray, name, description, units='unitless'):
    '''
    Creates new DataArray from generated numpy array.

    dataarray = DataArray

    name = new name of DataArray

    description = additional description for DataArray

    units = default 'unitless'. Can be set accordingly and will be used if no attributes are available

    '''
    if bool(dataarray.attrs)==True:
        index = xr.DataArray(
            data=dataarray,
            dims=dataarray.dims,
            coords=dataarray.coords,
            attrs=dict(
                description=description,
                units=dataarray.attrs["units"],
                scaling="1.0"
            ))

    else:
        index = xr.DataArray(
            data=dataarray,
            dims=dataarray.dims,
            coords=dataarray.coords,
            attrs=dict(
                description=description,
                units=units,
                scaling="1.0"
            ))
    return index.rename(name)

def newArrayFromArray(input, dataarray, description, units, name):
    '''
    Creates new DataArray from generated numpy array.

    input = Numpy array to be transformed to DataArray

    dataarray = DataArray to use coordinates from

    name = new name of DataArray

    description = additional description for DataArray

    unit = set units accordingly

    '''

    index = xr.DataArray(
        data=input,
        dims=dataarray.dims,
        coords=dataarray.coords,
        attrs=dict(
            description=description,
            units=units,
            scaling="1.0"
        ))
    return namedArray(index, name, description)

def aridityIndex(dataarray, temp, prec, description='Index of aridity tmp July/annual pre', units='Index values', name='aridityIndex'):
    '''
    Aridity index. Based on Dividing annual Precipitation from July monthly Mean.
    Indicates the aridity of an area - the higher the value the more arid it is.
    Preventing Inf values by adding a slight amount to the annual precipitation

    dataarray = xarray.DataArray

    temp = monthly Temperature Mean

    prec = annual Precipitation sum

    '''

    aridity = []
    years = dateToTime(dataarray, freq='YS')

    for i in range(len(years)):
        m = 6+(i*12)
        values = temp[m]/(prec[i]+0.00000001)
        aridity.append(values/np.sqrt((values*values)+1))
    aridity = np.asarray(aridity)
    return newArrayFromArray(aridity, dateToTime(dataarray, freq='YS'), description, units, name)


def continentalityIndex(dataarray, outstring, tempRange, freq='YS', description='Conrads Continentality Index', units='Index values', name='ConradsContinentalityIndex'):
    '''
    Continentality index. Based on temperature range and latitude of location.
    Originally indicated by Johansson 1926 but further defined by Conrad 1946 and thus referred to as Conrads Index.
    Threthold between 0 - no continentality and 100 - absolute continentality.

    dataarray = xarray.DataArray

    tempRange = temporal range of temperature

    '''
    lat = np.array(dataarray.coords['latitude'])
    repetitions = len(dataarray.coords['longitude'])
    if outstring == 'eobs_':
        latitude = np.tile(lat, (repetitions, 1)).transpose()
    else: 
        latitude = np.tile(lat, (repetitions, 1))
    reducedDims = dataarray.to_dataset()
    reducedDims = reducedDims.drop_dims('time')
    continentality = newArrayFromArray(input=latitude, dataarray=reducedDims, units="degrees north", description="Latitude for continentality", name='lat')
    rads = np.radians(continentality+10)
    conti = []
    time = dateToTime(dataarray, freq=freq)

    for i in range(len(time)):
        idx = ((1.7*tempRange[i]) / np.sin(rads))-14
        idx = idx.where(idx >= 0)
        #idx = idx.where(idx <= 100)
        conti.append(idx)
    continental = np.asarray(conti)
    return newArrayFromArray(continental, dateToTime(dataarray, freq=freq), description, units, name)

