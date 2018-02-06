#!/usr/bin/env python
"""
Pre-processing script for effective connectivity analysis.
Contains functions to read files containing info about motion parameters, artifacts, and noise estimates
from GLM preprocessing pipeline, construct regressors from them, apply a respective GLM with PyMVPA function
and save the residuals to nifti files.
"""

from mvpa2.datasets.eventrelated import fit_event_hrf_model
from mvpa2.datasets.mri import fmri_dataset, map2nifti
import numpy as np
from os.path import join as pjoin
import os


def get_nuisance_regressors(qa_dir, run_number, num_noise_comps=5):
    """
    For specified functional run,
    read the files containing motion parameters, artifacts (i.e. motion outliers), and noise components
    from the results directory.
    Return array containing these regressors to be used as input 'extra_regressors' for 'fit_event_hrf_model'.
    """
    # motion parameters
    motion_file = pjoin(qa_dir, 'art', 'run%02d_norm.bold_dtype_mcf.txt' % run_number)
    with open(motion_file, 'r') as f:
        motion_parameters = np.array([float(line) for line in f.readlines()])

    # artifacts / outliers
    artifact_file = pjoin(qa_dir, 'art', 'run%02d_art.bold_dtype_mcf_outliers.txt' % run_number)
    with open(artifact_file, 'r') as f:
        artifact_index = [int(line) - 1 for line in f.readlines()]  # get indices
    # create emtpy array and fill with outlier tags
    artifacts = np.zeros(motion_parameters.shape)
    artifacts[artifact_index] = 1

    # noise components
    noisecomp_file = pjoin(qa_dir, 'noisecomp', 'run%02d_noise_components.txt' % run_number)
    noisecomp_regressors = np.loadtxt(noisecomp_file)
    # only take specified number of noise components
    noisecomp_regressors = noisecomp_regressors[..., :num_noise_comps]

    # reshape depending on wether artifacts exist
    if np.sum(artifacts) == 0:
        extra_regressors = np.append(motion_parameters.reshape((-1, 1)), noisecomp_regressors, axis=1)
    else:
        extra_regressors = np.append(np.vstack((motion_parameters, artifacts)).T, noisecomp_regressors, axis=1)
    return extra_regressors


def preproc_run(boldfile, outfile, qa_dir, runnumber):
    """
    Use PyMVPA's function 'fit_event_hrf_model' to create and fit a nuisance GLM to the preprocessed bold data.
    Save the Residuals of that GLM as NIFTI files.
    """
    # load preprocessed and transformed bold file
    ds = fmri_dataset(boldfile)

    # create dummy event. 'events' should contain dicts with name, onset, duration.
    events = [{'condition': 'dummy',
               'onset': [308],  # chose last time point to nullify effect of regressor
               'duration': [0]}]

    # get nuisance regressors
    extra_regressors = get_nuisance_regressors(qa_dir, runnumber)

    # perform GLM
    hrf_estimates = fit_event_hrf_model(ds, events,
                                        design_kwargs=dict(hrf_model='canonical',
                                                           drift_model='blank',
                                                           add_regs=extra_regressors),
                                        return_model=True, time_attr='time_coords',
                                        condition_attr='condition', glmfit_kwargs=dict(model='ols'))

    # get residuals from model. replace data in existing pymvpa dataset to maintain mapper
    residuals4d_array = hrf_estimates.a.model.results_[0].resid
    ds.samples = residuals4d_array

    # save to nifti
    def _save_ds(d, fname):
        """
        Save pymvpa data set to nifti file
        Requires data set to have a mapper
        """
        image = map2nifti(d)
        image.to_filename(fname)

    _save_ds(ds, outfile)


if __name__ == '__main__':

    import sys
    sub_nr = int(sys.argv[1])    # subject number as integer

    # I/O paths
    results_basedir = '/data/famface/openfmri/oli/results/results_with_main_effects/' \
                      'l1ants_fwhm6_hp60_derivs_frac0.1/l1ants_fwhm6_hp60_derivs_frac0.1/' \
                      'model001/task001/'
    qadir = pjoin(results_basedir, 'sub%03d' % sub_nr, 'qa')
    out_dir = pjoin('/data/famface/openfmri/oli/results/ec_preproc/', 'sub%03d' % sub_nr, 'residual4d', 'mni')

    # check if out dir exists
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    else:
        print('Output directory: %s ' % out_dir)
        raise(OSError, 'Sorry Master. Output directory already exists.')

    # iterate over runs
    for run_nr in range(1, 12):
        # I/O files
        bold_file = pjoin(results_basedir, 'sub%03d' % sub_nr, 'bold', 'run%03d' % run_nr, 'bold_mni.nii.gz')
        out_file = pjoin(out_dir, 'res4d_%02d.nii.gz' % run_nr)
        # run preprocessing for given run and subject
        preproc_run(bold_file, out_file, qadir, run_nr)
        # report back to me
        print('finished run %03d subject %03d' % (run_nr, sub_nr))
