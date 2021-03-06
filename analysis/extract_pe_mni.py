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


def pe2mni_ants(pe, mni2anat_hd5, affine_matrix, workdir, outfilename,
                standard='/usr/share/fsl/5.0/data/standard/MNI152_T1_2mm_brain.nii.gz'):
    """
    Transform a 3D statistical image to MNI space with ANTS given pre-existing transformation
    matrices (in our case, from GLM/nipype working directory).

    This is very much mimicking the behavior of the 'warpall' node in our analysis
    pipeline.
    """

    # apply both affine and non-linear transform to parameter estimate file
    # TODO: Not sure about the order in which ANTS wants these transformation files ...
    pe2mni = ants.ApplyTransforms(
        input_image=pe,
        reference_image=standard,
        output_image=outfilename,
        transforms=[mni2anat_hd5, affine_matrix],
        default_value=0, dimension=3, interpolation='Linear',
        terminal_output='file')
    pe2mni.run()

    # return path to resulting image
    return outfilename


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


def extract_runs_famface_betas(base_dir, out_dir, mnimask, subdir_template, stats_type, csvfilename, beta_filename):
    """
    Project the mni mask into subject space. Extract the mean
    parameter estimate (zstat, pe, cope, varcope) for each roi and run.
    For all runs of one subject (submit multiple subjects in parallel via PBS/Condor).
    """

    outfile_fullpath = join(out_dir, csvfilename)
    # Do nothing if csv file already exists
    if os.path.exists(outfile_fullpath):
        pass
    else:

        # this list will later be written to a csv file.
        betas = []

        # list of directory names for each run
        runs = ['_modelestimate%d' % i for i in range(11)]

        # create output directory
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        # create workdir
        workdir = join(out_dir, 'masktrans')
        if not os.path.exists(workdir):
            os.makedirs(workdir)

        # path to hd5 file and affine transformation matrix
        mni2anat_hd5 = join(base_dir, 'registration', subdir_template, 'antsRegister', 'output_Composite.h5')
        affine_matrix = join(base_dir, 'registration', subdir_template, 'convert2itk', 'affine.txt')

        """
        extract mean parameter estimate for each run
        """

        for run in runs:
            # get paths for parameter estimate files
            pe_file = join(base_dir, 'modelestimate', subdir_template, 'modelestimate',
                           'mapflow', run, 'results', beta_filename)

            # path of the to be transformed image
            outfilename = join(workdir, 'pe2mni_run%03d_%s.nii.gz' % ((runs.index(run)+1), stats_type))

            if not os.path.exists(outfilename):
                # do transformation, load result image in pymvpa
                pe_trans = pe2mni_ants(pe_file, mni2anat_hd5, affine_matrix, workdir, outfilename)
                pe_trans_img = fmri_dataset(pe_trans)
            else:
                pe_trans_img = fmri_dataset(outfilename)

            # extract mean parameter estimates
            run_betas = extract_mean_3d(pe_trans_img, mnimask)
            betas.append(run_betas)

        # write to csv file
        with open(outfile_fullpath, 'wb') as f:
            writer = csv.writer(f)
            for b in betas:
                writer.writerow(b)


if __name__ == '__main__':

    # pass arguments to this script
    import sys

    sub_id = sys.argv[1]
    out_base_dir = sys.argv[2]
    maskpath = sys.argv[3]
    mnimask = fmri_dataset(maskpath)

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

            extract_runs_famface_betas(base_dir, out_dir, mnimask, subdir_template, stats,
                                       csvfilename='%s_%s.csv' % (cond, sub_id),
                                       beta_filename=conds[cond])

#base_dir, out_dir, mnimask, subdir_template, stats_type, csvfilename, beta_filename)
