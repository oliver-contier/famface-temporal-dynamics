#!/bin/bash
echo "Sourcing FSL"
source /etc/fsl/fsl.sh

# source c3d
PATH=$PATH:/opt/convert3d
export PATH

# source virtual environment with modded nipype
source /home/global/scratch/oliver/nipype_mod_env/bin/activate

# run script
echo "Running script"

PATH=$PATH:/usr/lib/ants/:/apps/convert3d/ \
python /home/global/scratch/oliver/scripts/fmri_ants_openfmri_mc.py \
  --hpfilter 60.0 --derivatives \
  -d /home/dartfs-hpc/scratch/oliver/data \
  -w /home/global/scratch/oliver/nobackup_l1ants_fwhm6_hp60_derivs_frac0.1_workdir_mc \
  -o /home/global/scratch/oliver/results/l1ants_fwhm6_hp60_derivs_frac0.1_mc \
  -p MultiProc \
  --plugin_args "{'n_procs': 16}" \
  -s $1 \
  --mcrefrun -1
