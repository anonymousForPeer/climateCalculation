# climateCalculation

Calculation of the bio-climatic variables in three steps:

input are daily mean temperature (tavg), min temperature (tmin), max temperature (tmax), precipitation (pre), potential evapotranspiration (pet) and weekly soil water content (swc).

>> Remark: We use python package xarray. Unfortunately our HPC with slurm did not allow the parallel processing from dask we handled it to separate the large files in longitudinal chunks using .isel() 

Following Order of processing applies:

1. Calculation of bio-climatic variables in calculation/
    - 88 realisations exist - we calculated variables for each realisations but omitted 18 during the processing
    - ```orchestrateCalculation.sh``` calls ```startSequentialCalculation.sh``` calls ```readData.py``` calls ```utility/bioCalculation```
    - specifications in ```orchestrateCalculation.sh``` and ```utility/values.config```
2. Ensemble calculation into RCPs and their percentiles in ensemble/
    - ```orchestrateEnsemble.sh``` calls ```startSequentiellEnsemble.sh``` calls ```readEnsemble.py``` calls ```utility/ensemble.py```
    - specifications in ```orchestrateEnsemble.sh```
3. Combining the different longitudinal chunks in ```calculation/``` and calculation of temporal percentiles
    - ```orchestrateCombine.sh``` calls ```combineScript.sh``` calls ```combineIterations.py``` calls ```utility/combine.py```
    - specifications in ```orchestrateCombine.sh```

The folder ```utility/``` contains helper functions in ```calculations.py```, a mask file ```mask.nc``` for masking the data and ```rcp.py``` which states the realisations for RCP ensemble combination.

For publication purpose we combined all data variables according to their specifications including temporal percentiles. Here we utilise the folder ```biovars/```
1. ```start.sh``` is the sbatch script to start following processing:
    - ```stackAndRename.py``` - stacks all combined temporal percentiles according to realisations, RCPs and temporal percentiles
    - old and new variable names are in renameVars.csv
    - ```testStack.py``` checks, if this stacking was succesful by rastermath with single files


>> This code can not be run as the base variables can not be supplied - it rather is a verification of processing

Used packages are attached in requirements.txt