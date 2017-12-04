#!/usr/bin/env python

from mvpa2.datasets.mri import fmri_dataset
from mvpa2.misc.data_generators import simple_hrf_dataset
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


def add_contrast(timeseries, onsetpath, amplitudes=(1, 1)):
    """
    Based on the onsets for familiar and unfamiliar faces, construct a regressor
    that reflects the difference between the two conditions and add it to our
    time series.
    This way, we want to try to model the effect of experimental stimulation on
    our connectivity model in Py-Causal / TETRAD.
    """

    # import custom function, used also during simulation, to get the onsets

    sys.path.insert(0, '/data/famface/openfmri/oli/osf_prereg_code/simulation')
    from famface_simulation_functions import get_onsets_famface

    # get onsets
    spec = get_onsets_famface(onsetpath, amplitudes)

    # construct hrf model for familiar and unfamiliar faces
    # (in the form of dicts in a list)
    hrf_models = []
    for condition, amplitude in zip(spec, amplitudes):
        hrf_model = simple_hrf_dataset(events=condition['onset'],
                                       nsamples=154,
                                       tr=2,
                                       tres=2,
                                       baseline=0,
                                       signal_level=amplitude,
                                       noise_level=0)
        hrf_models.append(hrf_model)

    # subtract
    fam_vs_unfam = hrf_models[0].samples[:, 0] - hrf_models[1].samples[:, 0]

    # append to time series
    from copy import deepcopy
    ts_copy = deepcopy(timeseries)
    ts_copy.append(fam_vs_unfam)
    return ts_copy


def getlabels(csvpath):
    """
    get labels from a csv file listing them (in our case, Matteo's list of rois)
    """
    with open(csvpath, 'r') as f:
        rdr = csv.reader(f)
        content = [row for row in rdr]

    labelnames = [row[0] for row in content[1:]]
    labels = [(idx, l) for (idx, l) in enumerate(labelnames, 1)]
    return labels


def transpose_and_write(roi_timeseries, outfile, header):
    """
    Write roi_timeseries to csv file (with roi-indices as header) with rois as
    columns and time points as rows.
    For use in TETRAD.
    """
    transposed = map(list, zip(*roi_timeseries))
    assert len(header) == len(transposed[0])
    transposed.insert(0, header)

    # TODO: See if py-causal can deal with scientific notation for very small and large numbers.
    # if not, tell csv to write in regular floats
    with open(outfile, 'w') as f:
        wr = csv.writer(f)
        wr.writerows(transposed)


def extract_runs_famface_mnimask(base_dir, out_dir, mnimask, sub_id,
                                 with_contrast=False,
                                 labelcsv='/data/famface/openfmri/github/notebooks/roi_coord.csv'):
    """
    Given our famface data, extract time series for ALL runs of ONE subject.
    For use in TETRAD. base_dir contains pre-processed BOLD images in mni space.
    """

    runs = ['run%03d' % i for i in xrange(1, 12)]

    # enumerated label names from csv file
    labels = getlabels(labelcsv)

    # select label names and strip whitespaces for header
    # (because tetrad doesn't allow whitespaces)
    header = [pair[1].replace(' ', '') for pair in labels]
    if with_contrast:
        header.append('FAM-UNFAM')

    # load mask in pymvpa
    ms = fmri_dataset(mnimask)

    for run in runs:
        # create output dir
        if not os.path.exists(join(out_dir, 'csv', run)):
            os.makedirs(join(out_dir, 'csv', run))
        infile = join(base_dir, sub_id, 'bold', run, 'bold_mni.nii.gz')
        # load bold file in pymvpa
        bold = fmri_dataset(infile)
        # extract time series
        timeseries = extract_mean_timeseries(bold, ms)

        if with_contrast:
            # TODO: don't hardcode data directory
            data_dir = '/data/famface/openfmri/oli/simulation/data_oli'
            onsetpath = join(data_dir, sub_id, 'model', 'model001', 'onsets', 'task001_%s' % run)
            ts_with_contrast = add_contrast(timeseries, onsetpath)

            # write to csv
            outfile = join(out_dir, 'csv', run, '{}_{}.csv'.format(sub_id, run))
            transpose_and_write(ts_with_contrast, outfile, header)

        else:
            # write to csv
            outfile = join(out_dir, 'csv', run, '{}_{}.csv'.format(sub_id, run))
            transpose_and_write(timeseries, outfile, header)


def extract_runs_nuisancedata(base_dir, out_dir, mnimask, sub_id,
                              with_contrast=False,
                              labelcsv='/data/famface/openfmri/github/notebooks/roi_coord.csv'):
    """
    extract time series from the residuals of our nuisance model.
    This does essentially the same as extract_runs_famface_mnimask, only
    for different input path structure.
    """
    """
    Given our famface data, extract time series for ALL runs of ONE subject.
    For use in TETRAD. base_dir contains pre-processed BOLD images in mni space.
    """

    # enumerated label names from csv file
    labels = getlabels(labelcsv)

    # strip whitespaces for header
    # (because tetrad doesn't allow whitespaces)
    header = [pair[1].replace(' ', '') for pair in labels]
    if with_contrast:
        header.append('FAM-UNFAM')

    ms = fmri_dataset(mnimask)

    runs = ['run%02d' % i for i in xrange(1, 12)]
    for run in runs:
        # create output dir
        if not os.path.exists(join(out_dir, 'csv', run)):
            os.makedirs(join(out_dir, 'csv', run))

        infile = join(base_dir, sub_id, 'residual4d', 'mni', 'res4d_%s.nii.gz' % run)
        bold = fmri_dataset(infile)
        timeseries = extract_mean_timeseries(bold, ms)

        if with_contrast:
            # TODO: don't hardcode data directory
            data_dir = '/data/famface/openfmri/oli/simulation/data_oli'
            runstring = run[:3] + '0' + run[3:]
            onsetpath = join(data_dir, sub_id, 'model/model001/onsets', 'task001_%s' % runstring)

            ts_with_contrast = add_contrast(timeseries, onsetpath)

            # write to csv
            outfile = join(out_dir, 'csv', run, '{}_{}.csv'.format(sub_id, run))
            transpose_and_write(ts_with_contrast, outfile, header)

        else:
            # write to csv
            outfile = join(out_dir, 'csv', run, '{}_{}.csv'.format(sub_id, run))
            transpose_and_write(timeseries, outfile, header)


if __name__ == '__main__':

    """
    get command line arguments
    """
    import sys

    sub_id = sys.argv[1]
    mnimask = sys.argv[2]
    base_dir = sys.argv[3]

    # subject specific output directory
    out_base_dir = sys.argv[4]
    out_dir = join(out_base_dir, sub_id)

    # if residuals should be used, the run script gives the argument 'residuals'
    # at this position
    residual_string = sys.argv[5]

    # if the contrast between familiar and unfamiliar should be included,
    # this should be 'with_contrast'
    contrast_string = sys.argv[6]
    if contrast_string == 'with_contrast':
        contrast = True
    else:
        contrast = False

    """
    run the executing function
    """
    if residual_string == 'residuals':
        extract_runs_nuisancedata(base_dir, out_dir, mnimask, sub_id, with_contrast=contrast)
    else:
        extract_runs_famface_mnimask(base_dir, out_dir, mnimask, sub_id, with_contrast=contrast)
