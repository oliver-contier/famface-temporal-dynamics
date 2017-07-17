#!/usr/bin/env bash

echo "Sourcing FSL"
source /etc/fsl/fsl.sh

echo "Running script"
python famface_simulation_main.py $1 \
    /data/famface/openfmri/oli/simulation/data_oli \
    /data/famface/openfmri/scripts/notebooks/rois_manual_r5_20170222_nooverlap.nii.gz \
    /data/famface/openfmri/oli/simulation/mcfiles
