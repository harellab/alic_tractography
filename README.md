# OCD_pipeline
Imaging pipeline for supporting DBS surgeries for treatment of OCD

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
