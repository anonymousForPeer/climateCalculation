#!/bin/bash

#SBATCH --job-name=combine_calculations_
#SBATCH --chdir=/work/reichmut
#SBATCH --output=/work/%u/%x-%j-%a.log
#SBATCH --time=0-02:30:00 #this time necessary for all other variables
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=16G ##ram request

module load GCCcore/10.2.0 GCC/10.2.0 Python/3.8.6 OpenMPI/4.0.5 netCDF/4.7.4 GCC/12.2.0 SciPy-bundle/2023.02 OpenMPI/4.1.4 GDAL/3.6.2

source /home/$USER/venv/clim/bin/activate

. /home/$USER/Workspace/climatedata/utility/values.config

export PATHNAME=$PATHNAME
export RCP=$SLURM_ARRAY_TASK_ID    
export STAT=$1 
export CALCULATIONS=$CALCULATIONS
export NAME='projection' #'projection' #'forcings' 'eobs' #'' for all other variables
export SOIL='SoilWaterContent_' #'SoilWaterContent_' ''
export MIN=$2 
export MAX=$3 
export FOLDERNEW=calculationCombine/

if [ ! -d "${PATHNAME}""${processWay}""Combine" ]; then
  mkdir -p "${PATHNAME}""${processWay}""Combine";
fi


python /home/$USER/Workspace/climatedata/calculation/combineIterations.py 
#python /home/$USER/Workspace/climatedata/utility/combineEobsHicam.py