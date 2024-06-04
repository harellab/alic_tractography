# ALIC_tractography

## Overview description
This repository contains a package of Python code tools that can be used to perform probabilistic tractography of the anterior limb of the internal capsule and analysis of outputs.

## Installation

1. Install dependencies:
* connectome workbench [https://www.humanconnectome.org/software/connectome-workbench]
* apptainer [https://apptainer.org/]

2. Clone this repository.

3. Update all submodules:
 ```
 git submodule update --init --recursive # Execute from within the folder you just cloned
 ```
4. Build or activate the "subsegment" conda environment:

  * On CMRR linux computers, the environment is already built and ready to be activated, assuming you have conda configured:
 ```
 conda activate /opt/local/dbs/bin/miniconda3/envs/subsegment
 ```
  * If on a different machine, you can build the environment from the environment.yml file:
 ```
 conda env create -n subsegment -f environment.yml
 conda activate subsegment
 ```

## Usage

`main_batch_subjects.py` is used to generate whole and segemented ALIC tractograms, run and anatomically plotting/data visualization (density heatmaps, centroids, streamline OCD response tract analysis) for a batch of subjects with 3T dMRI stored in HCP dataset format.

### Imaging data inputs
`main_batch_subjects.py` accepts a single input argument, consisting of a path to a CSV file containing the subject IDs to run, with one subject ID per line. In addition to command-line arguments, the following variables are currently hardcoded in main_batch_subjects.py:
* `TEST_ALIC_DIR`: directory where match_batch_subjects.py will be run and analyzed data will be stored
* `TEST_HCP_DIR`: directory where imaging data is stored

The following files must be present as an input to the pipeline in `{TEST_HCP_DIR}/{SUBJECT_ID}`:
* `T1w/T1w_acpc_dc_restore.nii.gz`
* `T1w/Diffusion/bvals`
* `T1w/Diffusion/bvecs`
* `T1w/Diffusion/data.nii.gz`
* `MNINonLinear/xfms/acpc_dc2standard.nii.gz`
* `MNINonLinear/xfms/standard2acpc_dc.nii.gz`

### outputs (per subject)
* `{coronal_slice_coordinate_mm}_OCD_response_tract_streams.csv` - output values for streamline OCD response tract analysis (percentage of streamlines overlapping with OCD response tract [Li et al. 2020]) at a single coronal slice in MNI space (ex. `3_OCD_response_tract_streams.csv` for y = 3mm)
* `combined_aLIC_left.nii.gz` &  `combined_aLIC_right.nii.gz`: 
* `combined_aLIC_left_{PFC_target_id}_ctx-lh-{PFC_target_name}.nii.gz` - segmented ALIC fiber bundle (ex. `1002_ctx-lh-caudalanteriorcingulate.nii.gz`)
* `combined_aLIC_left_{PFC_target_id}_ctx-lh-{PFC_target_name}.tck` - segmented ALIC fiber bundle tractrogram
* `combined_aLIC_left_{PFC_target_id}_ctx-lh-{PFC_target_name}.vtk` - segmented ALIC fibr bundle in vtk formate (3dSlicer compatible)
* `combined_aLIC_left_{PFC_target_id}_ctx-lh-{PFC_target_name}_centerofmass_withinALIC.csv` - ALIC centroid coordinates in subject-specific space
* `combined_aLIC_left_{PFC_target_id}_ctx-lh-{PFC_target_name}_centerofmass_withinALIC_mni.csv` - ALIC centroid coordinates in MNI space

### functions
run_hcp_subject is a custom-built function which includes the following sub-functions:
generate_alic()
subsegment_alic()
generate_centroid()

### terminal command
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
- fill in references

## References
Li N, Baldermann JC, Kibleur A, Treu S, Akram H, Elias GJB, *et al.* (2020): A unified connectomic target for deep brain stimulation in obsessive-compulsive disorder [no. 1]. *Nat Commun* 11: 3364.

## Authors, fundings sources, references
### Authors
Karianne Sretavan (sreta001@umn.edu) & Henry Braun (hbraun@umn.edu)

### PI
Noam Harel (harel002@umn.edu)
Sarah R. Heilbronner (sarah.heilbronner@bcm.edu)

### Funding sources
Research work was supported by the University of Minnesota’s MnDRIVE (Minnesota’s Discovery, Research and Innovation Economy) initiative and NIH R01MH124687, S10OD025256, P50NS123109 and UH3NS100548. SRH was further supported by the NIH R01MH126923 and the Robert and Janice McNair Foundation.

