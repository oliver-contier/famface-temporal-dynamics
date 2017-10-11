#!/bin/bash

# get singularity
module add singularity/2.3.1

# define sequence from 001 to 033
subs=( $(seq -w 033) )

# only for a subset
# subs=( $(seq -w 029 032) )

# loop over subs, submitting one job each
#for sub in "${subs[@]}"; do
#qsub -v sub="sub$sub" -N "$sub_l1" pbssubmit_runl1_m2.pbs
#done

# submit just one subj
qsub -v sub="sub001"  pbssubmit_runl1_m2.pbs
