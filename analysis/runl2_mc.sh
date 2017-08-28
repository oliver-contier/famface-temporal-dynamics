#!/bin/bash
PATH=/apps/palm-alpha86:$PATH
echo "Sourcing FSL"
source /etc/fsl/fsl.sh

echo "Running script"
python /home/global/scratch/oliver/scripts/group_multregress_openfmri.py \
  -m 1 -t 1 \
  -o /home/global/scratch/oliver/results/l2ants_fwhm6_hp60_derivs_frac0.1_mc \
  -d /home/dartfs-hpc/scratch/oliver/data \
  -l1 /home/global/scratch/oliver/results/l1ants_fwhm6_hp60_derivs_frac0.1_mc \
  -w /home/global/scratch/olivernobackup_l2ants_fwhm6_hp60_derivs_frac0.1_workdir_mc \
  -p MultiProc \
  --plugin_args "{'n_procs': 16}"
  # --nonparametric
  # --norev
