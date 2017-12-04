#!/usr/bin/env bash

# extract mean time series for our ROIs from the merely preprocessed data.
# add column for our contrast fam-unfam.

python meants_tetrad.py \
    $1 \
    /data/famface/openfmri/scripts/notebooks/rois_manual_r5_20170222_nooverlap.nii.gz \
    /data/famface/openfmri/oli/results/results_with_main_effects/l1ants_fwhm6_hp60_derivs_frac0.1/l1ants_fwhm6_hp60_derivs_frac0.1/model001/task001/ \
    /data/famface/openfmri/oli/results/extract_meants_withcontrast \
    noresiduals \
    with_contrast
