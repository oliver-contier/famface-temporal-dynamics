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

    with open(outfile, 'w') as f:
        wr = csv.writer(f)
        wr.writerows(transposed)


def extract_runs_famface_mnimask(base_dir, out_dir, mnimask, sub_id,
                                 labelcsv='/data/famface/openfmri/github/notebooks/roi_coord.csv'):
    """
    Calls extract_timeseries() for ALL runs of ONE subject.
    For use in TETRAD. base_dir contains pre-processed BOLD images in mni space.
    """

    subdir = os.path.join(base_dir, sub_id, 'bold')
    rundirs = os.listdir(subdir)

    labels = getlabels(labelcsv)
    header = [pair[1] for pair in labels]
    # load mask in pymvpa
    ms = fmri_dataset(mnimask)

    for run in rundirs:
        infile = os.path.join(base_dir, sub_id, 'bold', run, 'bold_mni.nii.gz')
        # load bold file in pymvpa
        bold = fmri_dataset(infile)
        if not os.path.exists(os.path.join(out_dir, 'csv')):
            os.makedirs(os.path.join(out_dir, 'csv'))
        outfile = os.path.join(out_dir, 'csv', '{}_{}.csv'.format(sub_id, run))
        # extract time series
        timeseries = extract_mean_timeseries(bold, ms)
        # write to csv
        transpose_and_write(timeseries, outfile, header)


if __name__ == '__main__':

    # get command line arguments
    import sys

    sub_id = sys.argv[1]
    mnimask = sys.argv[2]
    base_dir = sys.argv[3]
    out_dir = sys.argv[4]

    # run the function for famfaces
    extract_runs_famface_mnimask(base_dir, out_dir, mnimask, sub_id)