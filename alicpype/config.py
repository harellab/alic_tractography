#!/usr/bin/env python3
# description: storing constants and configurations

import sys
from pathlib import Path
import os
import pandas as pd

##---Set up paths within OCD_Pipeline---
ALICPYPE_DIR = Path(__file__).resolve().parent
OCD_PIPELINE_DIR = ALICPYPE_DIR.parent

# setup wma_pyTools submodule installation
# make sure that wma_pyTools is right in the working directory, or that
# the package can otherwise be imported effectively
# TODO fix wma_pyTools installation
sys.path.append(str(OCD_PIPELINE_DIR / 'wma_pyTools'))

# setup connectome workbench installation 
os.environ['PATH'] = '/opt/local/dbs/bin/hcp-workbench-1.4.2/workbench/bin_rh_linux64:'+ os.environ['PATH']

# Script to transform points/fiducials using Slicer
slicer_apply_xfm_script = ALICPYPE_DIR / 'slicer_transform_points.py'

MNI_ref_image = OCD_PIPELINE_DIR / 'indata' / 'MNI152_T1_1mm_brain.nii.gz'
xfm_header_template = OCD_PIPELINE_DIR / 'indata' / 'xfm_header_template.hdr'
freesurfer_lookup_table =pd.read_csv(
        OCD_PIPELINE_DIR / 'indata/FreesurferLookup.csv',
        index_col='#No.')

#path to SCC mask to divide rACC
splitraccplane = OCD_PIPELINE_DIR / 'indata/subcallosal_cingulate_mni.nii.gz'

##---Set up subject-specific paths ---

# define expected inputs and check for them
data_dir = Path('indata')

parcellationPath = data_dir / 'aparc+aseg.nii.gz'
parcellationFsPath = data_dir / 'mri/aparc+aseg.nii.gz'
refT1Path = data_dir / 'T1w_acpc.nii.gz'
diffPath = data_dir / 'diffusion_acpc.nii.gz'
#diff_b0acpc_path = data_dir / 'eddy_wrapped_B0_image_space-acpc.nii.gz'
#diff_unreg_path = data_dir /'eddy_wrapped_avg_image.nii.gz'
bvalsPath = data_dir / 'bvals'
#bvalsPath_b9 = data_dir / 'bvals_b9'
bvecsPath = data_dir / 'bvecs'
#ParcellationFsPath = data_dir / 'mri/aparc+aseg.mgz'
acpc_ref_image = parcellationPath
rACC_mod_aparc_aseg = data_dir / 'rACC_mod_aparc_aseg.nii.gz'

# transform files
acpc_to_mni_xfm = data_dir / 'acpc_dc2standard.nii.gz'
mni_to_acpc_xfm = data_dir / 'standard2acpc_dc.nii.gz'

rACC_split_labels = {11026: data_dir / 'lh_rostralanteriorcingulate_ROI_acpc_ventral.nii.gz',
                     21026: data_dir / 'lh_rostralanteriorcingulate_ROI_acpc_dorsal.nii.gz',
                    12026: data_dir / 'rh_rostralanteriorcingulate_ROI_acpc_ventral.nii.gz',
                     22026: data_dir / 'rh_rostralanteriorcingulate_ROI_acpc_dorsal.nii.gz'}
# Targets of interest (Freesurfer label index)
targetLabels={'left':[1002,11026,21026,1012,1020,1028,1003,1014,1019,1027],
                'right':[2002,12026,22026,2012,2020,2028,2003,2014,2019,2027]}

track_files = {
        'left': [ Path('app-track_aLIC/output/combined_aLIC_left.tck'),],
        'right': [ Path('app-track_aLIC/output/combined_aLIC_right.tck'),]}

# Freesurfer lookup table, e.g. https://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/AnatomicalROI/FreeSurferColorLUT
lutPath = data_dir / 'FreesurferLookup.csv' #subject-specific path. TODO switch to config.freesurferLookupTable wherever used

#tckPath=Path('/home/naxos2-raid25/sreta001/DBS_for_sreta001/DBS-OCD/OCD004/Code/app-track_aLIC_harelpreproc/output/track.tck')
saveFigDir = Path( 'output' )

#acpc_to_MNI_xfm in ANTs format
mni_to_acpc_xfm_itk = data_dir / 'mni_to_acpc_xfm_itk.nii.gz'

#anterior communisure displayed slice (3mm anterior of the origin)
ac_displayed_slice_3mm = 3.0
posterior3mm_displayed_slice = -3.0
anterior9mm_displayed_slice = 9.0

#path to project-specific directory (ex. 3T_HCP_visit1)
project_dir = '/home/udall-raid7/HCP_data/Data_Processing/3T_HCP_visit1/'
