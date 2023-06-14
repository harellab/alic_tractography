#!/usr/bin/env python3
# description: copy and pasting data to the appropriate input folders

import shutil
from pathlib import Path

def import_hcp_subject(subject, hcp_root, cwd): #defining function
    hcp_root = Path(hcp_root)
    subject = str(subject) 
    cwd = Path(cwd) 
    subject_hcp_dir = hcp_root / subject

# Dictionary of all images copied
    to_copy = {
        'T1w_acpc':[
            'T1w/T1w_acpc_dc_restore_1.25.nii.gz', #source path (source_file)
            'indata/T1w_acpc.nii.gz'], #destination path (dest_file)
        'bvals':[
            'T1w/Diffusion/bvals',
            'indata/bvals'],
        'bvecs':[
            'T1w/Diffusion/bvecs',
            'indata/bvecs'],
        'diffusion':[
            'T1w/Diffusion/data.nii.gz',
            'indata/diffusion.nii.gz'],
        'segmentation':[
            'T1w/Diffusion/data.nii.gz',
            'indata/aparc+aseg.nii.gz'],}
            
# Copy over each image
    for source_file, dest_file in to_copy.values():
        shutil.copy(
            subject_hcp_dir / source_file,
            cwd / dest_file)


