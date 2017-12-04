#!/usr/bin/env bash

# extract mean time series for our ROIs from the residual data, where button press is also included.
# add column for our contrast fam-unfam.

python meants_tetrad.py \
    $1 \
    /data/famface/openfmri/scripts/notebooks/rois_manual_r5_20170222_nooverlap.nii.gz \
    /data/famface/openfmri/oli/results/results_nuisance_button/l1ants_fwhm6_hp60_derivs_frac0.1_nuisance_button/model001/task001/ \
    /data/famface/openfmri/oli/results/extract_meants_nuisance_button_withcontrast \
    residuals \
    with_contrast
