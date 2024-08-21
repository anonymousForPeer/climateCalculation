import itertools
import xarray as xr
import os
import utility.calculations as cl
import utility.rcps as rcps



def filesToProcess(rcp, climdata, extra, iter):
    '''
    This function looks for the files that are given and appends them to a list for further processing.

    '''

    to_process=[]

    if rcp=='26':
        for i in rcps.rcp26:
            to_process.append(climdata+'climateAnnualCalculations_'+extra+str(i)+'_'+str(iter)+'.nc')
    elif rcp=='45':
        for i in rcps.rcp45:
            to_process.append(climdata+'climateAnnualCalculations_'+extra+str(i)+'_'+str(iter)+'.nc')
    elif rcp=='85':
        for i in rcps.rcp85:
            to_process.append(climdata+'climateAnnualCalculations_'+extra+str(i)+'_'+str(iter)+'.nc')
    else:
        print('no correct Representative Concentration Pathways chosen')
    

    datasetToProcess = []
    for item in to_process:
        with xr.open_dataset(item) as ds:
            datasetToProcess.append(ds)
    length = datasetToProcess[0].dims['time']

    return datasetToProcess, length


def filesToIterateThrough(datasetToProcess, iterValue, tim):
    '''
    We load each file to be processed and change timedelta64 datatype to integer as we can not process timedelta64.
    Additionally lon and lat are being renamed for further processing. There xarray needs same coordnate names.

    datasetToProcess = all files to be used for processing
    iterValue = iteration through the dataArray of those
    '''

    timeToProcess = []
    for item in datasetToProcess:
        if item[iterValue].dtype=='timedelta64[ns]':
            input = item[iterValue].dt.days.astype('int32')
            if 'lat' in input.coords:
                input=input.rename({'lon':'longitude', 'lat':'latitude'})
            timeToProcess.append(input.isel(time=slice(tim,tim+1)))
                
        else:
            if 'lat' in item.coords:
                input=item[iterValue].rename({'lon':'longitude', 'lat':'latitude'})  
                timeToProcess.append(input.isel(time=slice(tim,tim+1)))
            else:
                timeToProcess.append(item[iterValue].isel(time=slice(tim,tim+1)))

    return timeToProcess


def mergeAndMask(datasetToProcess, iterValue, tim, stat):
    '''
    Here we iterate through the files to be processed, clean the variable names as 
    they are all the same and append iteration number

    '''

    timeToProcess = filesToIterateThrough(datasetToProcess, iterValue, tim)
    t = []
    for i in range(len(timeToProcess)):
        for _ in itertools.repeat(timeToProcess[i].rename(iterValue+str(i)), 1):
            t.append(_)
    merge = xr.merge(t)
    res = [i for i in merge.data_vars]
    filterres = [i for i in res if not (iterValue in i)]
    ##drop variables that are not the data variables itself
    datasetMasked = merge.drop_vars(filterres)
    
    stat = str(stat)
    quantileValue = int(stat)/100  
    statVal = datasetMasked.to_array(dim='quantile', name=iterValue).quantile(quantileValue, 'quantile')
    datasetMasked.assign(e=statVal)
        
    return statVal
    
def iterateThroughFiles(stat, rcp, extra, iter, path, climdata):
    print(iter, flush=True)
    datasetToProcess, length = filesToProcess(rcp, climdata, extra, iter)
    
    quantileResult = []
    ## is faster to iterate 
    for iterValue in datasetToProcess[0].data_vars:

        perVar = []
        for tim in range(length):

            statValue=mergeAndMask(datasetToProcess, iterValue, tim, stat)
            perVar.append(statValue)
        quantileValue = xr.concat(perVar, dim='time')
        quantileResult.append(quantileValue)
    dataToWriteOut = xr.merge(quantileResult)
    
    cl.writeOut(dataToWriteOut, extra+'rcp'+rcp+'_quantile'+str(stat)+'_', path, 'rcp'+rcp+'/'+str(stat)+'/', iter, zip=True)

