# ALIC_tractography
## Overview Description: Tractography pipeline for generating white matter streamlines for the anterior limb of the internal capsule.
## Authors: Karianne Sretavan Wong & Henry Braun

## Installation

1. Clone this repository.

2. update all submodules:
 ```
 git submodule update --init --recursive # Execute from within the folder you just cloned
 ```
3. Build or activate the "subsegment" conda environment:

  *. On CMRR linux computers, the environment is already built and ready to be activated, assuming you have conda configured:
 ```
 conda activate /opt/local/dbs/bin/miniconda3/envs/subsegment
 ```
  *. If on a different machine, you can build the environment from the environment.yml file:
 ```
 conda env create -n subsegment -f environment.yml
 conda activate subsegment
 ```
 
  4. Open the Jupyter notebook `subsegment.ipynb` and follow its instructions to run the pipeline.

## Usage
### main_batch_subjects.py
inputs
wrapper for run_hcp_subject
outputs

### main_batch_subjects_retest.py
inputs
outputs

### main_batch_7T_subjects.py
inputs
outputs

### main_run_subject.py
inputs
outputs

##  

TODO: 
- write out descriptions within each script 
