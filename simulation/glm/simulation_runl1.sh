#!/bin/bash
echo "Sourcing FSL"
source /etc/fsl/fsl.sh

# source c3d
PATH=$PATH:/opt/convert3d
export PATH

sub=$1

echo "Running script"
PATH=$PATH:/usr/lib/ants/:/apps/convert3d/ python /home/simulation/scripts/glm/simulation_fmri_ants_openfmri.py \
  --hpfilter 60.0 --derivatives \
  -d /home/data_oli \
  -w /home/simulation/nobackup_l1ants_fwhm6_hp60_derivs_frac0.1_workdir \
  -o /home/simulation/results/l1ants_fwhm6_hp60_derivs_frac0.1 \
  -p MultiProc \
  --plugin_args "{'n_procs': 16}" \
  -s $sub
  #--write-graph /data/famface/openfmri/oli/graph
