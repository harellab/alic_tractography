# ALIC_tractography

## Overview description
### This repository contains a package of Python code tools that can be used to perform probabilistic tractography of the anterior limb of the internal capsule and analysis of outputs.

## Authors, fundings sources, references
### Authors
Karianne Sretavan (sreta001@umn.edu) & Henry Braun (hbraun@umn.edu)

### PI
Noam Harel (harel002@umn.edu)

### Funding sources
Karianne Sretavan's work is supported by the following sources: the University of Minnesota Informatics Institute MnDRIVE Graduate Assistantship and NIH R01 MH124687, S10 OD025256, and P50 NS123109.

### References


## Installation

1. Install connectome workbench [https://www.humanconnectome.org/software/connectome-workbench]

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

### Imaging data
T1w_acpc_dc_restore.nii.gz
bvals
bvecs
diffusion_data.nii.gz
acpc_to_mni_xfm.nii.gz 
mni_to_acpc_xfm.nii.gz

### main_batch_subjects.py to generate whole and segemented ALIC tractograms, run and anatomically plotting/data visualization (density heatmaps, centroids, streamline OCD response tract analysis) for a batch of subjects with 3T dMRI

#### inputs (per subject)
TEST_ALIC_DIR = [directory to where match_batch_subjects.py will be run analyzed data will be housed]
TEST_HCP_DIR = [directory to where imaging data is housed]

#### outputs (per subject)
#_OCD_response_tract_streams.csv - output values for streamline OCD response tract analysis at particular coronal slice
combined_aLIC_left.nii.gz &  combined_aLIC_right.nii.gz: 
combined_aLIC_left_[####]_ctx-lh-[PFCtarget].nii.gz - segmented ALIC fiber bundle (ex. 1002_ctx-lh-caudalanteriorcingulate)
combined_aLIC_left_[####]_ctx-lh-[PFCtarget].tck - segmented ALIC fiber bundle tractrogram
combined_aLIC_left_[####]_ctx-lh-[PFCtarget].vtk - segmented ALIC fibr bundle in vtk formate (3dSlicer compatible)
combined_aLIC_left_[####]_ctx-lh-[PFCtarget]_centerofmass_withinALIC.csv - ALIC centroid coordinates in subject-specific space
combined_aLIC_left_[####]_ctx-lh-[PFCtarget]_centerofmass_withinALIC_mni.csv - ALIC centroid coordinates in MNI space

#### functions
run_hcp_subject is a custom-built function which includes the following sub-functions:
generate_alic()
subsegment_alic()
generate_centroid()

#### terminal command
[directory to main_batch_subjects.py] [directory to subject list (subjects_list_test.csv)]

### main_batch_subjects_retest.py to generate whole and segemented ALIC tractograms, run and anatomically plotting/data visualization for a batch of subjects with 3T retest dMRI
Inputs and outputs are identical to main_batch_subjects.py except using retest data.
#### terminal command: [directory to main_batch_subjects_retest.py] [directory to subject list (subjects_list_retest.csv)]

### main_batch_7T_subjects.py to generate whole and segemented ALIC tractograms, run and anatomically plotting/data visualization for a batch of subjects with 7T dMRI
Inputs and outputs are identical to main_batch_subjects.py except using 7T data.
terminal command: [directory to main_batch_7T_subjects.py] [directory to subject list (subjects_list_7T.csv)]

### main_run_subject.py to generate whole and segemented ALIC tractograms, run and anatomically plotting/data visualization for an individual subject
Inputs and outputs are identical to main_batch_subjects.py.
#### terminal command: [directory to main_run_subject.py] [directory to subject-specific folder (subject_002)]

### summary.py to run group-level analyses (concatenate centroids results and streamline OCD response tract analysis) and must be run after main_batch_subjects.py or any of alternative iterations

#### inputs (group-level)
TEST_ALIC_DIR = [directory to where match_batch_subjects.py will be run analyzed data will be housed]
TEST_HCP_DIR = [directory to where imaging data is housed]

#### outputs (group-level)
[####]_ctx-lh-[PFCtarget]_[#]mm_summary_centroids_mni.csv - target-specific centroid coordinates at specific coronal slice across all subjects
[####]_ctx-lh-[PFCtarget]_average_summary_centroids.csv - target-specific group-averaged centroid coordinates across all coronal slices along the anterior-posterior axis of the ALIC

#### functions
make_centroids_summary()
run_streamline_analysis()

#### terminal command
[directory to summary.py] [directory to subject list (subject_list_test.csv)]

### summary_7T.py to run group-level analyses (concatenate centroids results and streamline OCD response tract analysis) on 7T dMRI
Inputs and outputs are identical to summary.py except using 7T data.

TODO: 
- specify packaged versions that were run
-
