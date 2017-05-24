#!/bin/bash
echo "Sourcing FSL"
source /etc/fsl/fsl.sh

echo "Running script"
PATH=$PATH:/usr/lib/ants/:/apps/convert3d/ python simulation_fmri_ants_openfmri.py \
  --hpfilter 60.0 --derivatives \
  -d /data/famface/openfmri \
  -w /data/famface/openfmri/oli/simulation/nobackup_l1ants_fwhm6_hp60_derivs_frac0.1_workdir \
  -o /data/famface/openfmri/oli/simulation/results/l1ants_fwhm6_hp60_derivs_frac0.1 \
  -s sub002 \
  -p CondorDAGMan
  #--write-graph /data/famface/openfmri/oli/graph
