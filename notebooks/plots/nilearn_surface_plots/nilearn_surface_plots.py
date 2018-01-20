#!/usr/bin/env python

import matplotlib

matplotlib.use('Agg')  # suppress rendering of plots
import matplotlib.pyplot as plt
import numpy as np
from nilearn import datasets
from nilearn import surface
from nilearn import plotting

# import seaborn as sns
# sns.set_context('paper')

# path to stats map
fname_slp = '/data/famface/openfmri/oli/results/results_with_main_effects/l2ants_fwhm6_hp60_derivs_frac0.1/model001/task001/subjects_all/stats/contrast__l1-03-l2-02/zstat1_reversed_threshold.nii.gz'

# get standard image
fsaverage = datasets.fetch_surf_fsaverage5()
# fsaverage contains: pial_right, infl_right, sulc_righ (also for left, of course)

# project statsmap to surface
texture = surface.vol_to_surf(fname_slp, fsaverage.pial_right)  # worked with pial_right

surf_slp = plotting.plot_surf_stat_map(fsaverage.infl_right, texture, hemi='right',
                                       title='Surface right hemisphere',
                                       bg_map=fsaverage.sulc_right,
                                       cmap='viridis', colorbar=True,
                                       view='lateral')

surf_slp.savefig('surf_slp.png')
