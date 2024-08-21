#!/bin/bash

for minT in 1971 2021 2041 2061 2079 
do
  maxT=$(($minT+19))
  echo $minT
  echo $maxT

  for stat in 5 50 95 # if rcps then all percentiles, otherwise just use 5 as placeholder
     
  do
    #if reference period or realisations
    #sbatch -a 11,12,13,14,32,38,39,42,43,44,45,59,60,61,62,79,80,88,16,17,18,19,33,34,46,48,49,63,64,65,66,01,02,21,23,24,25,27,28,30,31,35,36,37,40,41,50,51,53,54,55,56,57,58,67,68,70,71,72,73,74,75,76,77,78,82,84,85,86,87 /home/$USER/Workspace/climatedata/calculation/combineScript.sh "${stat}" "${minT}" "${maxT}"
    #if rcps
    sbatch -a 26,45,85 /home/$USER/Workspace/climatedata/calculation/combineScript.sh "${stat}" "${minT}" "${maxT}"   
  done
done