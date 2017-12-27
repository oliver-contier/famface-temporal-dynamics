#!/usr/bin/env python

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from nilearn import datasets
from nilearn import surface
from nilearn import plotting


import seaborn as sns
sns.set_context('paper')

fname_slp = '/data/famface/openfmri/oli/results/results_with_main_effects/l2ants_fwhm6_hp60_derivs_frac0.1/model001/task001/subjects_all/stats/contrast__l1-03-l2-02/zstat1_reversed_threshold.nii.gz'

fsaverage = datasets.fetch_surf_fsaverage5()

texture = surface.vol_to_surf(fname_slp, fsaverage.pial_right)

surf_slp = plotting.plot_surf_stat_map(fsaverage.infl_right, texture, hemi='right',
                            title='Surface right hemisphere',
                            bg_map=fsaverage.sulc_right,
                            cmap='viridis',
                            output_file='surf_slp.png')
