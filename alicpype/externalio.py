#!/usr/bin/env python3
# description: copy and pasting data to the appropriate input folders

import os
import shutil
from pathlib import Path
from . import config


def import_hcp_subject(subject, hcp_root, cwd): #defining function
    hcp_root = Path(hcp_root)
    subject = str(subject) 
    cwd = Path(cwd) 
    assert(cwd.is_dir())
    print(cwd)
    subject_hcp_dir = hcp_root / subject

# Dictionary of all images copied
    to_copy = {
        'T1w_acpc':[
            'T1w/T1w_acpc_dc_restore_1.25.nii.gz', #source path (source_file)
            config.refT1Path], #destination path (dest_file)
        'bvals':[
            'T1w/Diffusion/bvals',
            config.bvalsPath],
        'bvecs':[
            'T1w/Diffusion/bvecs',
            config.bvecsPath],
        'diffusion':[
            'T1w/Diffusion/data.nii.gz',
            config.diffPath],
        'segmentation':[
            'T1w/aparc+aseg.nii.gz',
            config.parcellationPath],
        'segmentation_fs':[ 
            # app-track_aLIC is hard coded to use this path 
            # so we must duplicate the segmentation here.
            'T1w/aparc+aseg.nii.gz',
            config.parcellationFsPath],
        'mni_to_acpc_xfm':[
            'MNINonLinear/xfms/standard2acpc_dc.nii.gz',
            config.mni_to_acpc_xfm], 
        'acpc_to_mni_xfm':['MNINonLinear/xfms/acpc_dc2standard.nii.gz',
            config.acpc_to_mni_xfm]}

            
# Copy over each image
    for source_file, dest_file in to_copy.values():
        print(f'copying {source_file} to {dest_file}...')
        os.makedirs(
            (cwd / dest_file).parent, 
            exist_ok=True)
        shutil.copy(
            subject_hcp_dir / source_file,
            cwd / dest_file)


