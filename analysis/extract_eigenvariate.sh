#!/usr/bin/env bash

# source FSL and execute python script to extract eigenvariates.
# pass on subject-ID argument (e.g. sub001)

# source fsl
source /etc/fsl/fsl.sh

python extract_eigenvariate.py $1
