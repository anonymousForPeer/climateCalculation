#!/bin/bash

. /home/$USER/Workspace/climatedata/utility/values.config
chunks=$CHUNKS

extra='SoilWaterContent_' #'' #SoilWaterContent_ #'' #for all other variables 

n=0
m=$((chunks-1))

rcpList=("26" "45" "85")
statList=("5" "50" "95")

for rcp in ${rcpList[*]}
do
  for stat in ${statList[*]}
  do
    sbatch -a $n-$m%50 /home/$USER/Workspace/climatedata/ensemble/startSequentiellEnsemble.sh "${rcp}" "${stat}" "${extra}"
  done
done
