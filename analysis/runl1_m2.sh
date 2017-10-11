# execute regular first level analysis using model002 (with just nuisance regressors)

#!/bin/bash
echo "Sourcing FSL"
source /etc/fsl/fsl.sh

# source c3d
PATH=$PATH:/opt/convert3d
export PATH

echo "Running script"
PATH=$PATH:/usr/lib/ants/:/apps/convert3d/ python /home/scripts/fmri_ants_openfmri_m2.py \
  --hpfilter 60.0 --derivatives \
  -d /home/data \
  -w /home/nobackup_l1ants_fwhm6_hp60_derivs_frac0.1_workdir_nuisance \
  -o /home/results/l1ants_fwhm6_hp60_derivs_frac0.1_nuisance \
  -p MultiProc \
  --plugin_args "{'n_procs': 16}" \
  -s $1  \
  --nuisance_only True
#  --write-graph /home/scripts/graph
