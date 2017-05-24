#!/usr/bin/env bash

echo "sourcing fsl"
source /etc/fsl/fsl.sh
#source /usr/share/fsl/5.0/fsl.sh

#echo "running famface_simulation.py for" $1
python famface_simulation.py $1
