#!/bin/bash

# define sequence from 001 to 033
subs=( $(seq -w 033) )

# only for a subset
#subs=( $(seq -w 009 018) )

# loop over subs, submitting one job each
#for sub in "${subs[@]}"; do
#qsub -v sub="sub$sub" -N "$sub_l1" pbssubmit_runl1_mc.pbs
#done

# submit just one subj
qsub -v sub="sub015"  pbssubmit_runl1_mc.pbs
