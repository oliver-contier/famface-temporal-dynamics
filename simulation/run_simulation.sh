#!/usr/bin/env bash

echo "Sourcing FSL"
source /etc/fsl/fsl.sh

echo "Running script"
python famface_simulation_main.py $1
