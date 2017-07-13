#!/usr/bin/env python

from mvpa2.datasets.mri import fmri_dataset
from nipype.interfaces import fsl, ants
from nipype.interfaces.fsl.utils import ConvertXFM
from nipype.interfaces.c3 import C3dAffineTool
import numpy as np
import csv
import os
from os.path import join

"""
Project statistical map to MNI space and extract mean parameter estimate for ROIs
specified in a mni-mask. 

Do this for all runs of one subject.
"""


def pe2mni_ants(pe, mni2anat_hd5, affine_matrix, workdir,
                standard='/usr/share/fsl/5.0/data/standard/MNI152_T1_2mm_brain.nii.gz'):
    """
    Transform a 3D statistical image to MNI space with ANTS given pre-existing transformation
    matrices (in our case, from GLM/nipype working directory).

    This is very much mimicking the behavior of the 'warpall' node in our analysis
    pipeline.
    """

    # path to output file
    outfile = join(workdir, 'pe2mni.nii.gz')

    # apply both affine and non-linear transform to parameter estimate file
    # TODO: Not sure about the order in which ANTS wants these transformation files ...
    mni2anat = ants.ApplyTransforms(
        input_image=pe,
        reference_image=standard,
        output_image=outfile,
        transforms=[mni2anat_hd5, affine_matrix],
        dimension=3, interpolation='Linear',
        terminal_output='file')
    mni2anat.run()

    # return path to resulting image
    return outfile


def extract_mean_3d(bold, mask):
    """
    extract mean value of rois given pymvpa datasets
    for a mask and a 3D map. the 3D map could be a statistical map with
    parameter or contrast estimates.
    """

    roi_timeseries = []

    # select first sample of mask dataset
    assert len(mask) == 1
    roi = mask.samples[0]

    # make a copy of bold dataset for safety
    assert len(bold) == 1
    bold_cp = bold.copy()

    bold_cp_sample = bold_cp.samples[0]

    for roi_value in range(1, int(max(roi)) + 1):
        # append mean of values in beta map that correspond to roi value index in roi mask
        roi_timeseries.append(np.mean(bold_cp_sample[roi == roi_value]))
    return roi_timeseries


def extract_runs_famface_betas(base_dir, out_dir, mnimask, subdir_template, outfilename, beta_filename):
    """
    Project the mni mask into subject space. Extract the mean
    parameter estimate (zstat, pe, cope, varcope) for each roi and run.
    For all runs of one subject (submit multiple subjects in parallel via PBS/Condor).
    """

    # this list will later be written to a csv file.
    betas = []

    # list of directory names for each run
    runs = ['_modelestimate%d' % i for i in range(11)]

    # create output directory
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    """
    transform parameter estimate to mni space
    """

    # create workdir
    workdir = join(out_dir, 'masktrans')
    if not os.path.exists(workdir):
        os.makedirs(workdir)

    # path to hd5 file and affine transformation matrix
    mni2anat_hd5 = join(base_dir, 'registration', subdir_template, 'antsRegister', 'output_Composite.h5')
    affine_matrix = join(base_dir, 'registration', subdir_template, 'mean2anatbbr', 'median_flirt.mat')

    """
    extract mean parameter estimate for each run
    """

    for run in runs:
        # get paths for beta files (or any statistical map really)
        pe_file = join(base_dir, 'modelestimate', subdir_template, 'modelestimate',
                       'mapflow', run, 'results', beta_filename)

        # do transformation, load result in pymvpa
        pe_mni = fmri_dataset(pe2mni_ants(pe_file, mni2anat_hd5, affine_matrix, workdir))

        # load stats map in pymvpa
        #stats_map = fmri_dataset(pe_mni)

        # extract mean parameter estimates
        run_betas = extract_mean_3d(pe_mni, mnimask)
        betas.append(run_betas)

    # write to csv file
    outfile_fullpath = join(out_dir, outfilename)
    with open(outfile_fullpath, 'wb') as f:
        writer = csv.writer(f)
        for b in betas:
            writer.writerow(b)


if __name__ == '__main__':

    # pass arguments to this script
    import sys

    sub_id = sys.argv[1]
    out_base_dir = sys.argv[2]
    mnimask = fmri_dataset(sys.argv[3])

    # path to base directory (working directory from nipype 1st lvl analysis)
    base_dir = '/data/famface/openfmri/oli/results/extract_betas/l1_workdir_betas/'

    # create one output directory for each subject
    out_dir = join(out_base_dir, sub_id)

    # make this part of the path names a variable. for ease of use and aesthetics (since it repeats a lot).
    subdir_template = '_model_id_1_subject_id_%s_task_id_1' % sub_id

    # iterate over different kinds of parameter estimates
    for stats in ['tstat', 'zstat', 'cope', 'varcope']:

        # dict with regressors and contrasts to extract
        conds = {
            # simple regressors
            'familiar_mean_%s' % stats: '%s1.nii.gz' % stats,
            'unfamiliar_mean_%s' % stats: '%s2.nii.gz' % stats,
            # contrasts
            'famvsunfam_mean_%s' % stats: '%s3.nii.gz' % stats,
            'unfamvsfam_mean_%s' % stats: '%s4.nii.gz' % stats,
        }

        # extract betas
        for cond in conds.keys():
            extract_runs_famface_betas(base_dir, out_dir, mnimask, subdir_template,
                                       outfilename='%s_%s.csv' % (cond, sub_id),
                                       beta_filename=conds[cond])
