#!/usr/bin/env bash

# execute the python script for extracting mean betas per run for rois

# takes sub ID as input argument from run_mean_betas.submit

# second argument: working directory from analysis of simulated data
# (contains registration and parameter estimate images)

# third argument: base directory for output

# source fsl
source /etc/fsl/fsl.sh

# execute script
python extract_pe_sim.py $1 \
    /data/famface/openfmri/oli/results/extract_betas/l1_workdir_betas_sim_realtrans/ \
    /data/famface/openfmri/oli/results/extract_betas/results_sim_realtrans/outdir_rois \
