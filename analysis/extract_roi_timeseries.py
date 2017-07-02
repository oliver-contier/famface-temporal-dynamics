#!/usr/bin/env python

from mvpa2.datasets.mri import fmri_dataset
from nipype.interfaces import fsl
from nipype.interfaces.fsl.utils import ConvertXFM
import numpy as np
import csv
import os
from os.path import join

"""
Tools to extract mean timeseries or beta values from 4D or 3D statistical images
given ROI masks in standard space. 
"""


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
    # TODO: think about what would be a good interpolation method!
    # nearest neighbour should definitly used for the final transformation
    # (otherwise, we don't get discrete values for the roi indices in the resulting mask.
    # But here, we could use nonlinear shit to make it more precise.
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


def mask2anat(anat, mnimask, workdir,
              standard='/usr/share/fsl/5.0/data/standard/MNI152_T1_2mm_brain.nii.gz'):
    """
    Project mask in MNI space into individual anatomical space.
    Here, we use it to extract mean betas from individual statistical maps,
    which are in the anatomical space of the subject.
    ROIs are defined on a group level.
    """

    # create transformation matrix from mni to anatomical
    mni2anat = fsl.FLIRT(
        dof=12, interp='nearestneighbour',
        in_file=standard,
        reference=anat,
        out_file=join(workdir, 'mni2anat.nii.gz'),
        out_matrix_file=join(workdir, 'mni2anat.txt'))
    mni2anat.run()

    # set path to output file
    outfile = join(workdir, 'mask2anat.nii.gz')

    # apply transformation to mask image
    mni2bold = fsl.FLIRT(
        interp='nearestneighbour',
        apply_xfm=True,
        in_matrix_file=join(workdir, 'mni2anat.txt'),
        out_matrix_file=join(workdir, 'mask2anat.txt'),
        in_file=mnimask,
        reference=anat,
        out_file=outfile)
    mni2bold.run()

    return outfile


def extract_mean_timeseries(bold, mask):
    """
    extract mean time series of rois given pymvpa datasets
    for a mask and a bold time-series
    """

    roi_timeseries = []

    # select first sample of mask dataset
    roi = mask.samples[0]

    # make a copy of bold dataset for safety
    bold_cp = bold.copy()

    for roi_value in range(1, max(roi) + 1):
        roi_timeseries.append(
            [np.mean(sample[roi == roi_value]) for sample in bold_cp.samples]
        )

    return roi_timeseries


def extract_mean_3d(bold, mask):
    """
    extract mean value of rois given pymvpa datasets
    for a mask and a 3D map. the 3D map could be a statistical map with
    parameter  or contrast estimates.
    """

    roi_timeseries = []

    # select first sample of mask dataset
    roi = mask.samples[0]
    # make a copy of bold dataset for safety
    bold_cp = bold.copy()

    bold_cp_sample = bold_cp.samples[0]

    for roi_value in range(1, max(roi) + 1):
        # append mean of values in beta map that correspond to roi value index in roi mask
        roi_timeseries.append(np.mean(bold_cp_sample[roi == roi_value]))
    return roi_timeseries


def transpose_and_write(roi_timeseries, outfile):
    """
    Write roi_timeseries to csv file (with roi-indices as header).
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
    For use in TETRAD
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


def extract_runs_famface_betas(base_dir, out_dir, mnimask, outfilename, beta_filename):
    """
    Project the mni mask into subject space for each run. Extract the mean
    z-value value for familiar and unfamiliar faces within each roi.

    For all runs of one subject (submit multiple subjects in parallel via PBS).
    """

    betas = []

    # get run directories
    runs = [i for i in sorted(os.listdir(base_dir)) if i.startswith('_modelestimate')]
    runs += [runs.pop(2)]

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for run in runs:
        # get paths for beta files for familiar and unfamiliar
        stats_map_fam = join(base_dir, run, 'results', beta_filename)

        # make workdir for subject (within out_dir)

        workdir = join(out_dir, 'workdir', 'run_%d' % runs.index(run))
        if not os.path.exists(workdir):
            os.makedirs(workdir)

        # project mask into subject space, store in workdir, store path in variable
        mask_subspace_path = mask2anat(stats_map_fam, mnimask, workdir)

        # load mask and stats map in pymvpa
        ms = fmri_dataset(mask_subspace_path)
        stats_map = fmri_dataset(stats_map_fam)

        # get betas
        run_betas = extract_mean_3d(stats_map, ms)
        betas.append(run_betas)

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

    """
    For extracting mean betas on discovery
    """

    # pass sub0XX as argument to this script
    import sys

    sub_id = sys.argv[1]

    # point to path on hydra
    base_dir = '/data/famface/openfmri/oli/results/extract_betas/l1_workdir_betas/' \
               '_model_id_1_subject_id_%s_task_id_1/modelestimate/mapflow/' % sub_id

    out_dir = '/data/famface/openfmri/oli/results/extract_betas/outdir/%s' % sub_id

    # set path to mnimask
    mnimask = '/data/famface/openfmri/oli/results/results_with_main_effects/l2ants_fwhm6_hp60_derivs_frac0.1/' \
              'model001/task001/subjects_all/stats/contrast__l1-03-l2-02/' \
              'zstat1_reversed_index.nii.gz'

    # dict with conditions and pe images to extract
    conds = {'familiar': 'pe20.nii.gz',
             'unfamiliar': 'pe21.nii.gz'}

    # extract betas
    for cond in conds.keys():
        extract_runs_famface_betas(base_dir, out_dir, mnimask,
                                   outfilename='%s_mean_betas_%s.csv' % (cond, sub_id),
                                   beta_filename=conds[cond])
