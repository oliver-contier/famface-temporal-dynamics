#!/usr/bin/env bash

# execute the python script for extracting mean betas per run for rois
# takes sub ID as input argument from run_mean_betas.submit
# second argument: base directory for output
# third argument: roi-mask image

# source fsl
source /etc/fsl/fsl.sh

python extract_pe.py $1 \
    /data/famface/openfmri/oli/results/extract_betas/l1_workdir_betas_mclast/ \
    /data/famface/openfmri/oli/results/extract_betas/results/outdir_clusters_mclast \
    /data/famface/openfmri/oli/results/results_mclast/l2ants_fwhm6_hp60_derivs_frac0.1_mc/model001/task001/subjects_all/stats/contrast__l1-03-l2-02/zstat1_reversed_index.nii.gz

