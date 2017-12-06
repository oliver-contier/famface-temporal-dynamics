# Synopsis

Analysis scripts for the project *temporal dynamics of familiar face recognition* by Oliver Contier, Matteo Visconti di Oleggio Castello, M. Ida Gobbini and Yaroslav O. Halchenko.

This project is pre-registered on the Open Science Framework under [osf.io/f7dqp](https://osf.io/f7dqp/).

# Structure

## /simulation
Contains scripts used to simulate data for a priori validation of the pipeline.

### /simulation/glm
Contains scripts to perform the planned GLM analysis on the simulated data. These scripts are essentially identical to the ones used for our main analysis, with the exception of input/output specification.

## /analysis
Scripts to execute the GLM analysis on the actual data. Additionally, there are scripts to extract the mean parameter estimates for each run within certain ROIs.

## /tetrad
These scripts extract mean time series from within the selected ROIs, which are then being used as input for an effective connectivity analysis with the IMaGES search algorithm (as implemented in the python package 'py-causal'). The results of this can be found in /notebooks/pycausal-analysis.ipynb.

## /notebooks
Different notebooks for visualization of results.

- plot.results.ipynb : statistical maps resulting from GLM analysis.

- activation_table.ipynb : activation table describing the found clusters.

- plot_mean_betas.ipynb : several plots describing the progression of mean parameter estimates within ROIs across runs

- pycausal_analysis.ipynb : Results of effective connectivity analysis using IMaGES as implemented in the 'py-causal' package.
