#!/usr/bin/python

from time import process_time
t1= process_time()
import xarray as xr
import utility.bioCalculation as bc
import utility.calculations as cl
import os
from resource import getrusage, RUSAGE_SELF
import xclim as xc

path = os.environ['PATHNAME']
climdata = os.environ['CLIMDATA']
soildata = os.environ['SOILDATA']
k = int(os.environ['K'])
lonrange = int(os.environ['LONRANGE'])
latrange = int(os.environ['LATRANGE'])
chunks = int(os.environ['CHUNKS'])
mindata = os.environ['MINDATA']
met = os.environ['MET']
output=os.environ['OUTPUT']
calculations=os.environ['CALCULATIONS']
reference=os.environ['REFERENCE']
extra=os.environ['EXTRA']

xextend, yextend = cl.chunking(chunks, latrange, lonrange)
allChunks = [x for x in xextend]
print(allChunks[k], flush=True)
print(met + ' ' + str(k), flush=True)
print(reference, flush=True)


if extra.lower()=='swc':
    if reference=='reference':
        #soil water content is in weekly tempm resolution and thus less time ranges
        y1=0 
        y2=360
        print('reference', flush=True)
        outstring = 'met_'+met+'_ref_'

    else:
        y1=480
        y2=1536
        print('modelled', flush=True)
        outstring = 'met_'+met+'_'

    soilstring = 'SWC_All'
    timeDelta=(y2-y1)+1
    dataToProcess = []
    with xr.open_dataset(soildata+'met_0'+met+'/output/mHM_Fluxes_States.nc').isel(lon=slice(min(allChunks[k]), max(allChunks[k])),time=slice(y1,y2)) as ds:
        ds=ds.rename({'lon':'longitude', 'lat':'latitude'})
        dataToProcess.append(ds)
    filterres = [i for i in dataToProcess[0] if not ('SWC_L0' in i)]
    ds_masked = dataToProcess[0].drop_vars(filterres)
    #here we calculate the water content sum of all soil layers
    swc = ds_masked.to_array(name='SWC_All').sum("variable").to_dataset()

    soil=swc
    soil[soilstring].attrs = {'units': 'mm', 'project': 'mHM hi_cam entire domain', 'setup_description': 'model run for the hi_cam domain, forced with ...',
                        'simulation_type': 'historical simulation', 'Conventions': 'XXX', 'contact': 'mHM developers (email:mhm-developers@ufz.de)',
                        'mHM_details': 'Helmholtz Center for Environmental Research - UFZ, Department Computational Hydrosystems, Stochastic Hydrology Group, release mHMv5.11.2-dev0'}

    bc.soilVar(soil, soilstring, outstring, k, output, path, calculations, timeDelta, allChunks)
     
elif extra=='': # here we have daily temp resolution
    #tavgtring etc. makes it easy to address the data arrays later on
    tavgstring = 'tavg'
    tmaxstring = 'tmax'
    tminstring = 'tmin'
    petstring = 'pet'
    prestring = 'pre'

    if reference=='reference':
        y1=0 
        y2=10958
        print('reference', flush=True)
        outstring = 'met_'+met+'_ref_'
    else: #reference and projections are not calculated at once - we omitted years 2001-2010
        y1=14245
        y2=46752
        print('modelled', flush=True)
        outstring = 'met_'+met+'_'

    dataToProcess = []

    with xr.open_dataset(climdata+'met_0'+met+'/tavg.nc').isel(longitude=slice(min(allChunks[k]), max(allChunks[k])),time=slice(y1,y2)) as ds:        
        dataToProcess.append(ds)

    with xr.open_dataset(climdata+'met_0'+met+'/tmax.nc').isel(longitude=slice(min(allChunks[k]), max(allChunks[k])),time=slice(y1,y2)) as ds:        
        dataToProcess.append(ds)

    with xr.open_dataset(mindata+'met_0'+met+'/tmin.nc').isel(longitude=slice(min(allChunks[k]), max(allChunks[k])),time=slice(y1,y2)) as ds:
        dataToProcess.append(ds)

    with xr.open_dataset(climdata+'met_0'+met+'/pet.nc').isel(longitude=slice(min(allChunks[k]), max(allChunks[k])),time=slice(y1,y2)) as ds:        
        dataToProcess.append(ds)

    with xr.open_dataset(climdata+'met_0'+met+'/pre.nc').isel(longitude=slice(min(allChunks[k]), max(allChunks[k])),time=slice(y1,y2)) as ds:        
        dataToProcess.append(ds)

    tavg=dataToProcess[0]
    tmax=dataToProcess[1]
    tmin=dataToProcess[2]
    pet=dataToProcess[3]
    pre=dataToProcess[4]
    #units are set from deg C to degC for xclim to understand
    tavg[tavgstring].attrs['units'] = 'degC'
    tmin[tminstring].attrs['units'] = 'degC'
    tmax[tmaxstring].attrs['units'] = 'degC'

    timeDelta=(y2-y1)+1
    bc.bioClimVar(tavg, tmax, tmin, pet, pre, tavgstring, tmaxstring, tminstring, petstring, prestring, outstring, k, output, calculations, path, timeDelta, allChunks)

print(str(round((getrusage(RUSAGE_SELF).ru_maxrss)/1024, 2)) + ' MB RAM used')
t2= process_time()
print('Processing time in seconds: %f' % (t2-t1))