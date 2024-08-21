#!/usr/bin/python

import numpy as np
import xarray as xr
import xclim as xc
from xclim.core.units import convert_units_to
import utility.calculations as cl
import os, glob


    
def bioClimVar(tavg, tmax, tmin, pet, pre, tavgstring, tmaxstring, tminstring, petstring, prestring, outstring, k, output, calculations, path, timeDelta, allChunks):
    '''

    This function loads the desired input data - average temp, max temp, min temp, precipitation and potential evapotranspiration 
    for Europe 1971-2099. 
    As each dataset is too big to be processed in total they are chunked and calculated for a small subset.

    Each subset and each climate variable are mostly saved directly while calculated as this keeps the cpu usage low.
    After all climate variable calculation they are combined into one file per tile as following processing can handle this more nicely.    

    The climate variables were chosen accordingly to recent species distribution modelling research. 
    xclim package offers most of them as ready to use functions.

    '''
    
    folder = output
    folderCombined = calculations
    

    mask=[]
    with xr.open_dataset('mask.nc').isel(longitude=slice(min(allChunks[k]), max(allChunks[k]))) as ds:
        for i in range(1,timeDelta):
            mask.append(ds)


    mask = xr.concat(mask, dim='time').assign_coords(time=np.array(tavg.coords['time'], dtype='datetime64'))
    
    tavg = tavg.where(mask['mask']==1)
    tmin = tmin.where(mask['mask']==1)
    tmax = tmax.where(mask['mask']==1)
    pre = pre.where(mask['mask']==1)
    if outstring != 'eobs_':
        pet = pet.where(mask['mask']==1)

    print('######################################')
    print('Calculating annual indices')
    print('######################################')
    ##############################################################################################
    ########################################### ANNUAL ###########################################
    ##############################################################################################
        
    annualIndex = cl.dateToTime(tavg, freq='YS')
    annualIdx = np.array(annualIndex.coords['time'], dtype='datetime64')
        ##############################################
        ############ Stats annual Temperature #########
        ##############################################
        
    annualMean = cl.namedArray(cl.statValue(tavg[tavgstring], "1Y", 'mean'), 'meanTemp', 'annual Mean Temperature', 'C' )
    annualMean = convert_units_to(annualMean, "C")
    cl.writeOut(annualMean.assign_coords(time=annualIdx), 'annualMeanTemp'+outstring, path, folder, k)

    
        #########################################################
        ########### Mean Temperature of coldest month ###########
        #########################################################
        
    monthMean = cl.namedArray(cl.statValue(tavg[tavgstring], "1M", 'mean'), 'monthMean', 'monthly Mean Temperature' )
    monthMean = convert_units_to(monthMean, "C")
    monthMax = cl.namedArray(cl.statValue(tmax[tmaxstring], "1M", 'max'), 'monthMax', 'monthly Max Temperature', 'C')
    monthMax = convert_units_to(monthMax, "C")
    monthMin = cl.namedArray(cl.statValue(tmin[tminstring], "1M", 'min'), 'monthMin', 'monthly Min Temperature', 'C' )
    monthMin = convert_units_to(monthMin, "C")
        #########################################################
        ############ Min Temperature of coldest month ###########
        #########################################################
    #same as annual min     
    annualMinColdMonth = cl.namedArray(cl.statValue(monthMin, "1Y", 'min'), 'minColdMonth', 'annual min temperature of coldest month', 'C')
    cl.writeOut(annualMinColdMonth, 'annualMinColdMonth'+outstring, path, folder, k)

        #########################################################
        ########### Max Temperature of warmest month ###########
        #########################################################
    #same as annual max     
    annualMaxWarmMonth = cl.namedArray(cl.statValue(monthMax, "1Y", 'max'), 'maxWarmMonth', 'annual max temperature of warmest month')
    cl.writeOut(annualMaxWarmMonth, 'annualMaxWarmMonth'+outstring, path, folder, k)
        
        #########################################################
        ################ Temperature Seasonality ################
        #########################################################
        # the higher the value the more seasonal variations occur
        ##checked
    annualTempSeasonality = xc.indicators.anuclim.P4_TempSeasonality(tavg[tavgstring]).assign_coords(time=annualIdx)
    cl.writeOut(annualTempSeasonality.assign_coords(time=annualIdx), 'annualTempSeasonality'+outstring, path, folder, k)
        
        #########################################################
        ############### Annual Mean Diurnal Range ###############
        #########################################################

        #checked
    annualDiurnalRange = xc.indicators.atmos.daily_temperature_range(tmin[tminstring], tmax[tmaxstring], freq='YS')
    annualDiurnalRange.attrs['units'] = 'degC'
    cl.writeOut(annualDiurnalRange.assign_coords(time=annualIdx), 'annualDiurnalRange'+outstring, path, folder, k)
        
        #########################################################
        ############### Annual temperature range ###############
        #########################################################
        
        #checked
    annualTempRange = cl.namedArray(cl.statValue(monthMax, "1Y", 'max') - cl.statValue(monthMin, "1Y", 'min'),'tempRange', 'annual temperature range, range between min of coldest month and max of warmest month')
    annualTempRange.attrs['units'] = 'degC'
    cl.writeOut(annualTempRange.assign_coords(time=annualIdx), 'annualTempRange'+outstring, path, folder, k)

        #########################################################
        ############# Annual precipitation range ################
        #########################################################
        
    precMin = cl.namedArray(cl.statValue(pre[prestring], "1Y", 'min'), 'minPrec', 'annual min Precipitation' )
    precMax = cl.namedArray(cl.statValue(pre[prestring], "1Y", 'max'), 'maxPrec', 'annual max Precipitation' )
    annualPrecRange = cl.namedArray(precMax-precMin, 'precipRange', 'annual precipitation range', 'mm d-1')
    cl.writeOut(annualPrecRange.assign_coords(time=annualIdx), 'annualPrecRange'+outstring, path, folder, k)
        
        #########################################################
        ###### Mean Temperature of wettest/driest Season ########
        #########################################################
        
        #wettest season
    wetMeanTemp = xc.indicators.anuclim.P8_MeanTempWettestQuarter(tas=tavg[tavgstring], pr=pre[prestring])
    wetMeanTemp = convert_units_to(wetMeanTemp,'degC')
    cl.writeOut(wetMeanTemp.assign_coords(time=annualIdx), 'annualWetMeanTemp'+outstring, path, folder, k)

        #driest Season
    dryMeanTemp = xc.indicators.anuclim.P9_MeanTempDriestQuarter(tas=tavg[tavgstring], pr=pre[prestring])
    dryMeanTemp = convert_units_to(dryMeanTemp,'degC')
    cl.writeOut(dryMeanTemp.assign_coords(time=annualIdx), 'annualDryMeanTemp'+outstring, path, folder, k)

        #########################################################
        ###### Mean Temperature of warmest/coldest Season #######
        #########################################################
        
        #warmest season
    warmMeanTemp = xc.indicators.anuclim.P10_MeanTempWarmestQuarter(tas=tavg[tavgstring], freq='YS')
    warmMeanTemp = convert_units_to(warmMeanTemp,'degC')
    cl.writeOut(warmMeanTemp.assign_coords(time=annualIdx), 'annualWarmMeanTemp'+outstring, path, folder, k)
        
        #coldest season   
    coldMeanTemp = xc.indicators.anuclim.P11_MeanTempColdestQuarter(tas=tavg[tavgstring], freq='YS') 
    coldMeanTemp = convert_units_to(coldMeanTemp,'degC')
    cl.writeOut(coldMeanTemp.assign_coords(time=annualIdx), 'annualColdMeanTemp'+outstring, path, folder, k)
        #########################################################
        ################### Last spring frost ###################
        #########################################################
        # per default this uses tavg
        # threshold 0 degC
        # window default 1
    lastSpringFrost = xc.indicators.atmos.last_spring_frost(tasmin=tmin[tminstring], freq='YS')
    #keep all >0 else set to 0 - otherwise lot of NA values included
    lastSpringFrost = lastSpringFrost.where(lastSpringFrost > 0, 0)  
    cl.writeOut(lastSpringFrost.assign_coords(time=annualIdx).astype(dtype='float32'), 'annualLastSpringFrost'+outstring, path, folder, k)

        ########################################################
        ################ Annual precipitation ##################
        ########################################################
        
    annualPrec = cl.namedArray(cl.statValue(pre[prestring], "1Y", 'sum'),'precip', 'annual sum of precipitation')
    cl.writeOut(annualPrec.assign_coords(time=annualIdx), 'annualPrec'+outstring, path, folder, k)
        
        #########################################################
        ####### Precipitation of wettest/driest season ##########
        #########################################################
        
    cl.writeOut(xc.indicators.anuclim.P16_PrecipWettestQuarter(pr=pre[prestring], freq='YS').assign_coords(time=annualIdx), 'annualPrecWetSeason'+outstring, path, folder, k)
    
    cl.writeOut(xc.indicators.anuclim.P17_PrecipDriestQuarter(pr=pre[prestring], freq='YS').assign_coords(time=annualIdx), 'annualPrecDrySeason'+outstring, path, folder, k)
    
        #########################################################
        ############# Precipitation seasonality #################
        #########################################################

    cl.writeOut(xc.indicators.anuclim.P15_PrecipSeasonality(pre[prestring]).assign_coords(time=annualIdx), 'annualPrecSeasonality'+outstring, path, folder, k)

        #########################################################
        ####### Precipitation of warmest/coldest season #########
        #########################################################
        
    cl.writeOut(xc.indicators.anuclim.P18_PrecipWarmestQuarter(pr=pre[prestring], tas=tavg[tavgstring], freq='YS').assign_coords(time=annualIdx), 'annualPrecWarmSeason'+outstring, path, folder, k)
    
    cl.writeOut(xc.indicators.anuclim.P19_PrecipColdestQuarter(pr=pre[prestring], tas=tavg[tavgstring], freq='YS').assign_coords(time=annualIdx), 'annualPrecColdSeason'+outstring, path, folder, k)
    
        
        #########################################################
        ####################### Dry days #######################
        #########################################################
        
        ##threshold per default 0.2mm/d
    dryDays = xc.indicators.atmos.dry_days(pr=pre[prestring], freq='YS').assign_coords(time=annualIdx)
    cl.writeOut(dryDays, 'annualDryDays'+outstring, path, folder, k)
    

    cdd = xc.indicators.atmos.maximum_consecutive_dry_days(pr=pre[prestring], freq='YS').assign_coords(time=annualIdx)
    cl.writeOut(cdd, 'annualConsecutiveDryDays'+outstring, path, folder, k)
        
        #########################################################
        #################### Isothermality ######################
        #########################################################
        
    cl.writeOut(xc.indicators.anuclim.P3_Isothermality(tasmin=tmin[tminstring], tasmax=tmax[tmaxstring], freq='YS').assign_coords(time=annualIdx), 'annualIsothermality'+outstring, path, folder, k)
    
        #########################################################
        ######### Annual growing degree days above 5°C ##########
        #########################################################

    cl.writeOut(xc.indicators.atmos.growing_degree_days(tas=tavg[tavgstring], thresh='5.0 degC', freq='YS').assign_coords(time=annualIdx), 'annualGDD'+outstring, path, folder, k)    
        
        ########################################################
        ################## Index of aridity ####################
        ########################################################
        
    cl.writeOut(cl.aridityIndex(dataarray=tavg[tavgstring], temp=monthMean, prec=annualPrec).assign_coords(time=annualIdx), 'annualAridity'+outstring, path, folder, k)
        
    
        #########################################################
        ########### Conrads Continentality index ################
        #########################################################
    contiIndex = cl.continentalityIndex(tavg[tavgstring], outstring, annualTempRange, freq='YS').assign_coords(time=annualIdx)    
    cl.writeOut(contiIndex.astype(dtype='float32'), 'annualContinentality'+outstring, path, folder, k)

        #########################################################
        ################# Annual water deficit ##################
        #########################################################
        ## make to function
    
    if outstring != 'eobs_':
        monthlyPet = cl.statValue(pet[petstring], "1M", 'mean')
        monthlyPre = cl.statValue(pre[prestring], "1M", 'sum')
        waterDeficit = cl.namedArray(cl.statValue(monthlyPre-monthlyPet, '1Y', 'sum'), 'waterDeficit', 'annual water deficit - difference of mean potential evapotranspiration and total precipitation')
        cl.writeOut(waterDeficit.assign_coords(time=annualIdx), 'annualWaterDeficit'+outstring, path, folder, k)
                
    # here the single climate variables are combine together - only for the designated tile
    with xr.open_mfdataset(path+folder+'annual*'+outstring+str(k)+'.nc', chunks=-1, parallel=True, engine='h5netcdf', combine='nested',combine_attrs='drop') as ds:    
        ds['cdd']=ds['cdd'].dt.days.astype('float32')
        ds['dry_days']=ds['dry_days'].dt.days.astype('float32') 
        ds = ds.where(mask['mask']==1)
        cl.writeOut(ds, 'climateAnnualCalculations_'+outstring, path, folderCombined, k, zip=False)
        print('-----------------------------------')
        print('Annual output in ' + path+folderCombined)
        print('-----------------------------------')

    for f in glob.glob(path+folder+'annual*'+outstring+str(k)+'.nc'):
        os.remove(f)
        


def soilVar(soil, soilstring, outstring, k, output, path, calculations, timeDelta, allChunks):
    '''

    This function loads the desired input data - average temp, max temp, min temp, precipitation and potential evapotranspiration 
    for Europe 1971-2099. 
    As each dataset is too big to be processed in total they are chunked and calculated for a small subset.

    Each subset and each climate variable are mostly saved directly while calculated as this keeps the cpu usage low.
    After all climate variable calculation they are combined into one file per tile as following processing can handle this more nicely.    

    The climate variables were chosen accordingly to recent species distribution modelling research. 
    xclim package offers most of them as ready to use functions.

    '''
    
    folder = output
    folderCombined = calculations
    
    monthlyIndex = soil.resample(time="1M").mean("time", keep_attrs=True) #cl.dateToTime(soil, freq='M')            
    monthlyIdx = np.array(monthlyIndex.coords['time'], dtype='datetime64')
    
    annualIndex = cl.dateToTime(soil, freq='YS')            
    annualIdx = np.array(annualIndex.coords['time'], dtype='datetime64')
    
    soil = soil.assign_coords(time=monthlyIdx)

    mask=[]
    with xr.open_dataset('mask.nc').isel(longitude=slice(min(allChunks[k]), max(allChunks[k]))) as ds:
        for i in range(1,timeDelta):
            mask.append(ds)

    mask = xr.concat(mask, dim='time').assign_coords(time=monthlyIdx)

        ###############################################
        ############# Stats annual Temperature #########
        ###############################################
    annualMean = cl.namedArray(cl.statValue(soil[soilstring], "1Y", 'mean'), 'meanSoilWaterContent', 'annual Mean Soil Water Content')
    annualMean = annualMean.assign_coords(time=annualIdx)
    cl.writeOut(annualMean, 'soilWaterContentMean'+outstring, path, folder, k)

    ## here the single climate variables are combine together - only for the designated tile
    with xr.open_mfdataset(path+folder+'soilWaterContentMean*'+outstring+str(k)+'.nc', chunks=-1, parallel=True, engine='h5netcdf', combine='nested') as ds:    
        ds = ds.where(mask['mask']==1)
        cl.writeOut(ds, 'climateAnnualCalculations_SoilWaterContent_'+outstring, path, folderCombined, k)
        print('-----------------------------------')
        print('Annual output in ' + path+folderCombined)
        print('-----------------------------------')


    for f in glob.glob(path+folder+'soilWaterContent*'+outstring+str(k)+'.nc'):
        os.remove(f)