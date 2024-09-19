#!/usr/bin/env python3
# description: Defining and storing constants and configurations

import sys
from pathlib import Path
import os
import pandas as pd

##---Set up paths within ALIC_tractography---
ALICPYPE_DIR = Path(__file__).resolve().parent
ALIC_TRACTOGRAPHY_DIR = ALICPYPE_DIR.parent

# setup wma_pyTools submodule installation
# make sure that wma_pyTools is right in the working directory, or that
# the package can otherwise be imported effectively
sys.path.append(str(ALIC_TRACTOGRAPHY_DIR / 'wma_pyTools'))

# setup connectome workbench installation 
# this is the path used on UMN-CMRR linux computers, on other environments install and configure connectome workbench yourself
os.environ['PATH'] = '/opt/local/dbs/bin/hcp-workbench-1.4.2/workbench/bin_rh_linux64:'+ os.environ['PATH']

# script to transform points/fiducials using Slicer
slicer_apply_xfm_script = ALICPYPE_DIR / 'slicer_transform_points.py'
xfm_header_template = ALIC_TRACTOGRAPHY_DIR / 'indata' / 'xfm_header_template.hdr'

# script to transform fiber bundles using Slicer
slicer_apply_xfm2bundle_script = ALICPYPE_DIR / 'slicer_transform_bundle.py'

# template MNI brain
MNI_ref_image = ALIC_TRACTOGRAPHY_DIR / 'indata' / 'MNI152_T1_1mm_brain.nii.gz'

# Freesurfer Desikan-Killiany (DK) atlas lookup table [https://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/AnatomicalROI/FreeSurferColorLUT]
freesurfer_lookup_table =pd.read_csv(
        ALIC_TRACTOGRAPHY_DIR / 'indata/FreesurferLookup.csv',
        index_col='#No.')

# targets of interest (Freesurfer label index)
targetLabels={'left':[1002,11026,21026,1012,1020,1028,1003,1014,1019,1027,1018],
                'right':[2002,12026,22026,2012,2020,2028,2003,2014,2019,2027,2018]}

# anterior communisure displayed slice (level of anterior commissure is 3mm, 9mm is anterior, 1mm is posterior)
coronal_slices_displayed_mm = [9, 6, 3, 1]

# path to subcallosal cingulate cortex (SCC) mask to divide the rostral anterior cingulate cortex (rACC)
splitraccplane = ALIC_TRACTOGRAPHY_DIR / 'indata/subcallosal_cingulate_mni.nii.gz'

# OCD response tract in MNI space (Li et al. 2020 'A unified connectomic target for deep brain stimulation in obsessive-compulsive disorder') 
ocd_response_tract_MNI = ALIC_TRACTOGRAPHY_DIR / 'indata' / 'Tract_Target_Li_2020_space-MNI.nii.gz'

##---Set up subject-specific paths ---

# define expected inputs and check for them
data_dir = Path('indata')
parcellationPath = data_dir / 'aparc+aseg.nii.gz'
parcellationFsPath = data_dir / 'mri/aparc+aseg.nii.gz'
refT1Path = data_dir / 'T1w_acpc.nii.gz'
diffPath = data_dir / 'diffusion_acpc.nii.gz'
diffPath_unregistered = data_dir / 'diffusion_space-DTI.nii.gz'
bvalsPath = data_dir / 'bvals'
bvalsPath_raw = data_dir / 'bvals_raw'
b0_threshold = 65 # bvalues below this threshold will be treated as b0
bvecsPath = data_dir / 'bvecs'
acpc_ref_image = parcellationPath
rACC_mod_aparc_aseg = data_dir / 'rACC_mod_aparc_aseg.nii.gz' # DK atlas-based segmentation of the rACC into dorsal and ventral components

# OCD response tract in ACPC space (Li et al. 2020)
ocd_response_tract_acpc = data_dir / 'ocd_response_tract_acpc.nii.gz'

# transform files in FSL format
acpc_to_mni_xfm = data_dir / 'acpc_dc2standard.nii.gz'
mni_to_acpc_xfm = data_dir / 'standard2acpc_dc.nii.gz'

# DTI to ACPC transform in ANTs format
DTI_to_acpc_xfm = data_dir / 'from-DTI_to-acpc_xfm.txt'

# MNI to ACPC transform in ANTs format
mni_to_acpc_xfm_itk = data_dir / 'mni_to_acpc_xfm_itk.nii.gz'

# ACPC to MNI transform in ANTs format
acpc_to_mni_xfm_itk = data_dir / 'acpc_to_mni_xfm_itk.nii.gz'

# labels for divded dorsal/ventral rACC ROI
rACC_split_labels = {11026: data_dir / 'lh_rostralanteriorcingulate_ROI_acpc_ventral.nii.gz',
                     21026: data_dir / 'lh_rostralanteriorcingulate_ROI_acpc_dorsal.nii.gz',
                    12026: data_dir / 'rh_rostralanteriorcingulate_ROI_acpc_ventral.nii.gz',
                     22026: data_dir / 'rh_rostralanteriorcingulate_ROI_acpc_dorsal.nii.gz'}

# labels for combined superior and inferior ALIC tractogram
track_files = {
        'left': [ Path('app-track_aLIC/output/combined_aLIC_left.tck'),],
        'right': [ Path('app-track_aLIC/output/combined_aLIC_right.tck'),]}

# output folder
saveFigDir = Path( 'output' )
