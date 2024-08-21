#!/bin/bash

#SBATCH --job-name=climate_calculation_met_
#SBATCH --chdir=/work/reichmut
#SBATCH --output=/work/%u/%x-%A-%a.out
#SBATCH --time=0-05:30:00 # days-hours:minutes:seconds # 25days
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=18G # ram request 14G

module load GCCcore/10.2.0 GCC/10.2.0 Python/3.8.6 OpenMPI/4.0.5 netCDF/4.7.4 GCC/12.2.0 SciPy-bundle/2023.02

source /home/$USER/venv/clim/bin/activate

. /home/$USER/Workspace/climatedata/utility/values.config

export K=$SLURM_ARRAY_TASK_ID  
export MET=$1
export PATHNAME=$PATHNAME
export CLIMDATA=$INPUT
export SOILDATA=$SOILDATA
export LONRANGE=$LONRANGE
export LATRANGE=$LATRANGE
export CHUNKS=$CHUNKS
export MINDATA=$MININPUT
export ENSEMBLEDATA=$ENSEMBLE
export OUTPUT=$OUTPUT
export CALCULATIONS=$CALCULATIONS
export REFERENCE=$2
export EXTRA=$3

if [ ! -d "${PATHNAME}""${OUTPUT}" ]; then #/work/$USER/ClimateData/output
  mkdir -p "${PATHNAME}""${OUTPUT}";
fi

if [ ! -d "${PATHNAME}""${CALCULATIONS}" ]; then #/work/$USER/ClimateData/climateInterCalculations
  mkdir -p "${PATHNAME}""${CALCULATIONS}";
fi

python /home/$USER/Workspace/climatedata/calculation/readData.py