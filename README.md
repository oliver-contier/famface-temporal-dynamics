# Synopsis

Analysis scripts for the project *temporal dynamics of familiar face recognition* by Oliver Contier, Matteo Visconti di Oleggio Castello, M. Ida Gobbini and Yaroslav O. Halchenko. 

# Functionalities

## simulation

Contains scripts used to simulate data for validation of the pipeline.

- *famface_simulation_functions.py*: Underlying functions.
- *famface_simulation_main.py*: Execution on our data set.
- *run_simulation.sh*: Runs the main script with. flexible input argument (reflecting the individual subjects) to allow for splitting into jobs and effective use of HPC condor.
- *famface_simulation.submit*: Submission file for HPC Condor.

### glm
Contains scripts to execute our analysis pipeline on the simulated data. These scripts are essentially identical to the ones used for our main analysis, with the exception of input/output specification.

- *simulation_fmri_ants_openfmri.py*: 1st and 2nd level analysis pipeline implemented with nipype.
- *run_flow.py*: Additional specification of 2nd level model.
- *simulation_runl1*: Runs 1st and 2nd lvl pipeline.
- *pbssubmit_simulation_runl1.pbs*: Submission script for PBS cluster computing for 1st and 2nd level analysis.

- *group_multregress_openfmri.py*: Group level analysis pipeline implemented with nipype. 
- *simulation_runl2.sh*: Runs the group level analysis.
- *pbssubmit_simulation_runl2.pbs*: Submission script for PBS cluster computing for group level analysis. 