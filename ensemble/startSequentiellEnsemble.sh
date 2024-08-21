#!/bin/bash
 
#SBATCH --job-name=ensemble_reduction_rcp26_
#SBATCH --chdir=/work/reichmut
#SBATCH --output=/work/%u/%x-%A-%a.out
#SBATCH --time=0-00:18:00 # days-hours:minutes:seconds # 25days
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=8G # ram request 3G soil, 8G reference, 15G all others

module load GCCcore/10.2.0 GCC/10.2.0 Python/3.8.6 OpenMPI/4.0.5 netCDF/4.7.4 GCC/12.2.0 SciPy-bundle/2023.02


. /home/$USER/Workspace/climatedata/utility/values.config

export K=$SLURM_ARRAY_TASK_ID  #$j # $SLURM_ARRAY_TASK_ID
export PATHNAME=$PATHNAME
export RCP=$1
export STAT=$2
export EXTRA=$3
export CLIMDATA=$PATHNAME$CALCULATIONS  #$INPUT


source /home/$USER/venv/clim/bin/activate

python /home/$USER/Workspace/climatedata/ensemble/readEnsemble.py
