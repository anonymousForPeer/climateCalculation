#!/bin/bash

. /home/$USER/Workspace/climatedata/utility/values.config
chunks=$CHUNKS

n=0
m=$((chunks-1))

reference='' #reference #reference #''
extra='eobs' #Swc #'' #'eobs'

for met in {01..88} # still we calculated bio-climatic variables for all realisations
do
  sbatch -a $n-$m%50 /home/$USER/Workspace/climatedata/calculation/startSequentiellCalculation.sh "${met}" "${reference}" "${extra}"
done