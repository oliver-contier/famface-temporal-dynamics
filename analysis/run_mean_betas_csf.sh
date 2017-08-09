#!/usr/bin/env bash

# execute the python script for extracting mean betas per run within the CSF
# takes sub ID as input argument from run_mean_betas.submit
# second argument: base directory for output

# source fsl
source /etc/fsl/fsl.sh

python extract_pe_csf.py $1 \
    /data/famface/openfmri/oli/results/extract_betas/l1_workdir_betas/ \
    /data/famface/openfmri/oli/results/extract_betas/results/outdir_csf \
