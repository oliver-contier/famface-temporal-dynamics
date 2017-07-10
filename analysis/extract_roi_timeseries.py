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
Tools to extract mean timeseries or beta values from 4D or 3D statistical images
given ROI masks in standard space. 
"""


# standard_mymachine = '/usr/local/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'
# mask_subspace_path = mask2bold(bold, anat, roi_mask, workdir, standard=standard_mymachine)


def mask2bold(bold, anat, roi_mask, workdir,
              standard='/usr/share/fsl/5.0/data/standard/MNI152_T1_2mm_brain.nii.gz'):
    """
    Project a mask image to individual subject space. anatomical image must
    be defined for registration. workdir is needed to dump temporary files
    created by fsl. output is a nifti image.
    """

    from os.path import join
    import os

    # create workdir
    if not os.path.exists(workdir):
        print('working directory did not exist and is created now.')
        os.makedirs(workdir)

    # produce matrix for bold2anat
    bold2anat = fsl.FLIRT(
        dof=6, interp='trilinear',
        in_file=bold,
        reference=anat,
        out_file=join(workdir, 'bold2anat.nii.gz'),
        out_matrix_file=join(workdir, 'bold2anat.txt'))
    bold2anat.run()

    # anat to mni
    anat2mni = fsl.FLIRT(
        dof=12, interp='trilinear',
        in_file=anat,
        reference=standard,
        out_file=join(workdir, 'anat2mni.nii.gz'),
        out_matrix_file=join(workdir, 'anat2mni.txt'))
    anat2mni.run()

    # concatinate matrices
    concat = ConvertXFM(
        concat_xfm=True,
        in_file2=join(workdir, 'bold2anat.txt'),
        in_file=join(workdir, 'anat2mni.txt'),
        out_file=join(workdir, 'bold2mni.txt'))
    concat.run()

    # inverse transmatrix
    inverse = ConvertXFM(
        in_file=join(workdir, 'bold2mni.txt'),
        out_file=join(workdir, 'mni2bold.txt'),
        invert_xfm=True)
    inverse.run()

    # apply to mask
    mni2bold = fsl.FLIRT(
        interp='nearestneighbour',
        apply_xfm=True,
        in_matrix_file=join(workdir, 'mni2bold.txt'),
        out_matrix_file=join(workdir, 'roimask.txt'),
        in_file=roi_mask,
        reference=bold,
        out_file=join(workdir, 'roimask.nii.gz'))
    mni2bold.run()

    mask_subspace_path = join(workdir, 'roimask.nii.gz')

    # TODO: registration fails pretty much ...

    return mask_subspace_path


def mask2pe(pe, anat, mnimask, workdir,
            standard='/usr/share/fsl/5.0/data/standard/MNI152_T1_2mm_brain.nii.gz'):
    """
    Compute new 2-step projection for a masn from mni to 3D parameter space (and apply it).
    """

    # create transformation matrix from mni to anatomical
    mni2anat = fsl.FLIRT(
        dof=12, interp='trilinear',
        in_file=standard,
        reference=anat,
        out_file=join(workdir, 'mni2anat.nii.gz'),
        out_matrix_file=join(workdir, 'mni2anat.txt'))
    mni2anat.run()

    # anat to parameter estimate map (3D statistical volume)
    anat2pe = fsl.FLIRT(
        dof=6, interp='trilinear',
        in_file=anat,
        reference=pe,
        out_file=join(workdir, 'anat2pe.nii.gz'),
        out_matrix_file=join(workdir, 'anat2pe.txt'))
    anat2pe.run()

    # concatinate matrices
    concat = ConvertXFM(
        concat_xfm=True,
        in_file2=join(workdir, 'mni2anat.txt'),
        in_file=join(workdir, 'anat2pe.txt'),
        out_file=join(workdir, 'mni2pe.txt'))
    concat.run()

    # set path to output file
    outfile = join(workdir, 'mask2pe.nii.gz')

    # apply transformation to mask image
    mni2pe = fsl.FLIRT(
        interp='nearestneighbour',
        apply_xfm=True,
        in_matrix_file=join(workdir, 'mni2pe.txt'),
        out_matrix_file=join(workdir, 'mask2pe.txt'),
        in_file=mnimask,
        reference=pe,
        out_file=outfile)
    mni2pe.run()

    # return path to transformed result
    return outfile


def mask2pe_ants(mnimask, anat, pe, mni2anat_hd5, affine_matrix, workdir):
    """
    Use existing Transformation Matrices with Ants and FSL to project a mask from
    mni to parameter space.
    """

    """
    paths for temporary files and output file
    """

    # temporary nifti file
    mni2anat_out_name = join(workdir, 'mnimask2anat.nii.gz')
    # inverse affine transform
    affine_matrix_inverse = join(workdir, 'anat2pe.txt')
    # path to output file
    outfile = join(workdir, 'mask2pe.nii.gz')

    """
    Invert affine and apply both transforms
    """

    # invert affine transmatrix (output from glm analysis)
    inverse = ConvertXFM(
        in_file=affine_matrix,
        out_file=affine_matrix_inverse,
        invert_xfm=True)
    inverse.run()

    # apply inverse transform from mni to anat space
    # (output from glm analysis)
    mni2anat = ants.ApplyTransforms(
        input_image=mnimask,
        reference_image=anat,
        output_image=mni2anat_out_name,
        transforms=[mni2anat_hd5],
        dimension=3, interpolation='NearestNeighbor',
        terminal_output='file')
    mni2anat.run()

    # apply inverse affine transform from anat to pe estimate space
    mni2pe = fsl.FLIRT(
        interp='nearestneighbour',
        apply_xfm=True,
        in_matrix_file=affine_matrix_inverse,
        in_file=mni2anat_out_name,
        reference=pe,
        out_file=outfile)
    mni2pe.run()

    # return path to projected mask
    return outfile


def extract_mean_timeseries(bold, mask):
    """
    extract mean time series of rois given pymvpa datasets
    for a mask and a bold time-series. Used for TETRAD.
    """

    roi_timeseries = []

    # select first sample of mask dataset
    roi = mask.samples[0]

    # make a copy of bold dataset for safety
    bold_cp = bold.copy()

    for roi_value in range(1, int(max(roi)) + 1):
        roi_timeseries.append(
            [np.mean(sample[roi == roi_value]) for sample in bold_cp.samples]
        )

    return roi_timeseries


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


def transpose_and_write(roi_timeseries, outfile):
    """
    Write roi_timeseries to csv file (with roi-indices as header) with rois as
    columns and time points as rows.
    For use in TETRAD.
    """
    transposed = map(list, zip(*roi_timeseries))
    transposed.insert(0, range(1, len(roi_timeseries) + 1))

    with open(outfile, 'w') as f:
        wr = csv.writer(f)
        wr.writerows(transposed)


def extract_runs_famface_mnimask(base_dir, out_dir, mnimask, sub_id):
    """
    Calls extract_timeseries() for ALL runs of ONE subject.
    For use in TETRAD. base_dir contains pre-processed BOLD images in mni space.
    """

    subdir = os.path.join(base_dir, sub_id, 'bold')
    rundirs = os.listdir(subdir)

    for run in rundirs:
        infile = os.path.join(base_dir, sub_id, 'bold', run, 'bold_mni.nii.gz')
        outfile = os.path.join(out_dir, '{}_{}_roimean.csv'.format(sub_id, run))

        print('extracting run {}'.format(run))
        timeseries = extract_timeseries(infile, mnimask)
        print('writing csv for run {}'.format(run))
        transpose_and_write(timeseries, outfile)
        print('run {} extracted!'.format(run))


def extract_runs_famface_betas(base_dir, out_dir, mnimask, anat, subdir_template, outfilename, beta_filename):
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
    project mask into subject space
    """

    # create workdir to save transform files
    workdir = join(out_dir, 'masktrans')
    if not os.path.exists(workdir):
        os.makedirs(workdir)

    # path to hd5 file and affine transformation matrix
    mni2anat_hd5 = join(base_dir, 'registration', subdir_template, 'antsRegister', 'output_InverseComposite.h5')
    affine_matrix = join(base_dir, 'registration', subdir_template, 'mean2anatbbr', 'median_flirt.mat')

    # pick first stats map as template for co-registration.
    pe_template = join(base_dir, 'modelestimate', subdir_template, 'modelestimate',
                              'mapflow', '_modelestimate0', 'results', beta_filename)

    # do transformation, load result in pymvpa
    mask_subspace_path = mask2pe_ants(mnimask, anat, pe_template, mni2anat_hd5, affine_matrix, workdir)
    ms = fmri_dataset(mask_subspace_path)

    """
    extract mean parameter estimate for each run
    """

    for run in runs:
        # get paths for beta files (or any statistical map really)
        pe_file = join(base_dir, 'modelestimate', subdir_template, 'modelestimate',
                             'mapflow', run, 'results', beta_filename)

        # load stats map in pymvpa
        stats_map = fmri_dataset(pe_file)

        # extract mean parameter estimates
        run_betas = extract_mean_3d(stats_map, ms)
        betas.append(run_betas)

    # write to a csv file
    outfile_fullpath = join(out_dir, outfilename)
    with open(outfile_fullpath, 'wb') as f:
        writer = csv.writer(f)
        for b in betas:
            writer.writerow(b)


if __name__ == '__main__':
    """
    ### For use with Tetrad (i.e. mask and data in standard space) ###

    # get command line arguments
    import sys

    sub_id = sys.argv[1]
    mnimask = sys.argv[2]
    base_dir = sys.argv[3]
    out_dir = sys.argv[4]

    # run the function for famfaces
    extract_runs_famface_mnimask(base_dir, out_dir, mnimask, sub_id)
    """

    # pass sub_id as argument to this script
    import sys

    sub_id = sys.argv[1]
    out_base_dir = sys.argv[2]
    mnimask = sys.argv[3]

    # path to base directory (working directory from nipype 1st lvl analysis)
    base_dir = '/data/famface/openfmri/oli/results/extract_betas/l1_workdir_betas/'

    # create one output directory for each subject
    out_dir = join(out_base_dir, sub_id)

    # make this part of the path names a variable. for ease of use and aesthetics (since it repeats a lot).
    subdir_template = '_model_id_1_subject_id_%s_task_id_1' % sub_id

    # path to brain extracted anatomical image
    anat_brain = join(base_dir, 'registration', subdir_template, 'stripper', 'highres001_brain.nii.gz')

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
            extract_runs_famface_betas(base_dir, out_dir, mnimask, anat_brain, subdir_template,
                                       outfilename='%s_%s.csv' % (cond, sub_id),
                                       beta_filename=conds[cond])
