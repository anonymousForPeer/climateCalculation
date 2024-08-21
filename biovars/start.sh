#!/bin/bash

#SBATCH --job-name=plotPrepare_
#SBATCH --chdir=/work/reichmut
#SBATCH --output=/work/%u/%x-%A-%a.out
#SBATCH --time=0-00:50:00 #this time necessary for all other variables
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=15G ##ram request

module load GCCcore/10.2.0 GCC/10.2.0 Python/3.8.6 OpenMPI/4.0.5 netCDF/4.7.4 GCC/12.2.0 SciPy-bundle/2023.02 OpenMPI/4.1.4 GDAL/3.6.2

source /home/$USER/venv/clim/bin/activate

export K=$SLURM_ARRAY_TASK_ID
#python /home/$USER/Workspace/paperClimate/stackAndRename.py
python /home/$USER/Workspace/paperClimate/testStack.py
