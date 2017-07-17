#!/usr/bin/env python
"""
Concatinate run-specific csv files
"""

import pandas as pd
import os
from os.path import join


def concat(base_dir):

    subs = ['sub%03d' % i for i in xrange(1, 34)]
    runs = ['run%03d' % i for i in xrange(1, 12)]

    # make an output directory
    if not os.path.exists(join(base_dir, 'concatinated')):
        os.makedirs(join(base_dir, 'concatinated'))

    for sub in subs:
        files = [join(base_dir, run, '%s_%s.csv' % (sub, run)) for run in runs]
        df_list = [pd.read_csv(f) for f in files]
        full_df = pd.concat(df_list)
        outfilename = '%s.csv' % sub

        if not os.path.exists(join(base_dir, 'concatinated', outfilename)):
            full_df.to_csv(join(base_dir, 'concatinated', outfilename),
                           index_label='idx')
            print('successfully written out file for %s' % sub)
        else:
            print('%s already exists and was not overwritten' % outfilename)


if __name__ == '__main__':

    concat('/data/famface/openfmri/oli/results/extract_meants/csv')