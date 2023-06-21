#!/usr/bin/env python3
# description: storing constants and configurations

import sys
from pathlib import Path

ALICPYPE_DIR = Path(__file__).resolve().parent
OCD_PIPELINE_DIR = ALICPYPE_DIR.parent

# setup wma_pyTools submodule installation
# make sure that wma_pyTools is right in the working directory, or that
# the package can otherwise be imported effectively
# TODO fix wma_pyTools installation
sys.path.append(str(OCD_PIPELINE_DIR / 'wma_pyTools'))

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
rACC_mod_aparc_aseg = data_dir / 'rACC_mod_aparc_aseg.nii.gz'
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

# transform files
acpc_to_mni_xfm = data_dir / 'acpc_dc2standard.nii.gz'
mni_to_acpc_xfm = data_dir / 'standard2acpc_dc.nii.gz'


# Freesurfer lookup table, e.g. https://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/AnatomicalROI/FreeSurferColorLUT
lutPath = data_dir / 'FreesurferLookup.csv'

#tckPath=Path('/home/naxos2-raid25/sreta001/DBS_for_sreta001/DBS-OCD/OCD004/Code/app-track_aLIC_harelpreproc/output/track.tck')
saveFigDir = Path( 'output' )
