#!/usr/bin/env bash

# execute the python script for extracting mean betas per run for rois
# taking sub ID as input argument from run_mean_betas.submit

# source fsl
source /etc/fsl/fsl.sh

# execute python script
python extract_roi_timeseries.py $1
