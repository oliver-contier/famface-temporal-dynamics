#!/bin/bash
PATH=/apps/palm-alpha86:$PATH
echo "Sourcing FSL"
source /etc/fsl/fsl.sh

echo "Running script"
python /home/simulation/scripts/glm/group_multregress_openfmri.py \
  -m 1 -t 1 --norev\
  -o /home/simulation/results/l2ants_fwhm6_hp60_derivs_frac0.1 \
  -d /home/data_oli \
  -l1 /home/simulation/results/l1ants_fwhm6_hp60_derivs_frac0.1 \
  -w /home/simulation/nobackup_l2ants_fwhm6_hp60_derivs_frac0.1_workdir \
  -p MultiProc \
  --plugin_args "{'n_procs': 16}"
  # --nonparametric
