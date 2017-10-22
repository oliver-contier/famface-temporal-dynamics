#!/usr/bin/env bash

python meants_tetrad.py \
    $1 \
    /data/famface/openfmri/scripts/notebooks/rois_manual_r5_20170222_nooverlap.nii.gz \
    /data/famface/openfmri/oli/results/results_nuisance/l1ants_fwhm6_hp60_derivs_frac0.1_nuisance/model001/task001/ \
    /data/famface/openfmri/oli/results/extract_meants_nuisance \
    residuals