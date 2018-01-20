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
fname_slp = '/data/famface/openfmri/oli/results/results_with_main_effects/l2ants_fwhm6_hp60_derivs_frac0.1/' \
            '/model001/task001/subjects_all/stats/contrast__l1-03-l2-02/zstat1_reversed_threshold.nii.gz'

# get standard image
fsaverage = datasets.fetch_surf_fsaverage5()  # fsaverage contains: pial_right, infl_right, sulc_righ

# initiate subplots
fig, axs = plt.subplots(nrows=2, ncols=3, subplot_kw={'projection': '3d'})

# iterate over subplots, hemispheres, and views
for row, average_surfs in zip(axs, [[fsaverage.pial_left, fsaverage.infl_left, fsaverage.sulc_left],
                                    [fsaverage.pial_right, fsaverage.infl_right, fsaverage.sulc_right]]):
    for field, perspective in zip(row, ['lateral', 'ventral', 'medial']):

        # project statsmap to surface
        texture = surface.vol_to_surf(fname_slp, average_surfs[0])  # worked with pial_right

        # actual plotting
        plotting.plot_surf_stat_map(average_surfs[1], texture, hemi='right',
                                    title='Surface right hemisphere',
                                    bg_map=average_surfs[2],
                                    cmap='viridis', colorbar=True,
                                    view=perspective,
                                    figure=fig, axes=field)

# save figure
fig.savefig('surf_slp.png', dpi=300)
