#!/bin/bash
PATH=/apps/palm-alpha86:$PATH
echo "Sourcing FSL"
source /etc/fsl/fsl.sh

echo "Running script"
python group_multregress_openfmri.py -m 1 -t 1 --nonparametric --norev\
  -o /data/famface/openfmri/oli/simulation/results/l2ants_fwhm6_hp60_derivs_frac0.1 \
  -d /data/famface/openfmri/data \
  -l1 /data/famface/openfmri/oli/simulation/results/l1ants_fwhm6_hp60_derivs_frac0.1 \
  -w /data/famface/openfmri/oli/simulation/nobackup_l2ants_fwhm6_hp60_derivs_frac0.1_workdir \

