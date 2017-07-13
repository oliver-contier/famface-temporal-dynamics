#!/usr/bin/env bash

# execute the python script for extracting mean betas per run for rois
# takes sub ID as input argument from run_mean_betas.submit
# second argument: base directory for output
# third argument: roi-mask image

# source fsl
source /etc/fsl/fsl.sh

python extract_pe_mni.py $1 \
    /data/famface/openfmri/oli/results/extract_betas/results_pe2mni/outdir_rois \
    /data/famface/openfmri/oli/results/extract_betas/newrois_nooverlap_plusmatteos.nii.gz


# thresholded contrast for decrease in fam > unfam
# /data/famface/openfmri/oli/results/results_with_main_effects/l2ants_fwhm6_hp60_derivs_frac0.1/model001/task001/subjects_all/stats/contrast__l1-03-l2-02/zstat1_reversed_index.nii.gz

# mask with new rois and matteos, limited to the significant voxels from our decrease contrast.
# /data/famface/openfmri/oli/results/extract_betas/newrois_nooverlap_plusmatteos_masked.nii.gz

# mask with new rois and matteos, not masked additionally with our contrast.
# /data/famface/openfmri/oli/results/extract_betas/newrois_nooverlap_plusmatteos.nii.gz

# only my manually selected rois
# /data/famface/openfmri/oli/results/extract_betas/newrois_nooverlap.nii.gz