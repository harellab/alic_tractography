#!/usr/bin/env python3
# description: copy and pasting data to the appropriate input folders

import os
import shutil
from pathlib import Path
from . import config
import numpy as np

def import_subject_from_list(subject_hcp_dir, cwd, to_copy): #defining function
    subject_hcp_dir = Path(subject_hcp_dir) 
    cwd = Path(cwd) 
    print(cwd)
    assert(subject_hcp_dir.parent.is_dir())

    # Copy over each image
    for source_file, dest_file in to_copy.values():
        print(f'copying {source_file} to {dest_file}...')
        os.makedirs(
            (cwd / dest_file).parent, 
            exist_ok=True)
        shutil.copyfile(
            subject_hcp_dir / source_file,
            cwd / dest_file)

def import_hcp_subject(subject, hcp_root, cwd):
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
    import_subject_from_list(hcp_root / subject, cwd, to_copy)

            
def import_7T_hcp_subject(subject, hcp_root, cwd):
    # Dictionary of all images copied
    to_copy = {
        'T1w_acpc':[
            'T1w/T1w_acpc_dc_restore_1.05.nii.gz', #source path (source_file)
            config.refT1Path], #destination path (dest_file)
        'bvals':[
            'T1w/Diffusion_7T/bvals',
            config.bvalsPath_raw],
        'bvecs':[
            'T1w/Diffusion_7T/bvecs',
            config.bvecsPath],
        'diffusion':[
            'T1w/Diffusion_7T/data.nii.gz',
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
    import_subject_from_list(hcp_root / subject, cwd, to_copy)
    # TODO: call edit_bvals_b9 function, inputs are paths to inputs
    edit_bvals_b9(cwd/config.bvalsPath_raw, cwd/config.bvalsPath, config.b0_threshold) #call to edit_bvals_b9 function, inputs will be paths

def edit_bvals_b9(bvals_raw, bvals_b9, b0_threshold): # generate a copy of bvals file that applies a threshold to b0 volumes
    correct_b0 = 9 # corrected b0 value 
    input_bvals = np.expand_dims(np.loadtxt(bvals_raw), axis = 0) # load original bval folder
    input_bvals[input_bvals <= b0_threshold] = correct_b0 # change input_bvals that meet condition [input_bvals <= b0_threshold] and change value to correct_b0
    # for i in range(len(input_bvals)): 
    #     if input_bvals[1] <= b0_threshold:
    #         input_bvals[1] = correct_b0
    output_bvals = np.savetxt(bvals_b9, input_bvals, fmt = '%d') # save out the edit bvals to the bvals_b9 file (file name, data)

def apply_transform_to_nifti(input, ref_image, output, transform, input_dimensions = 4):
    from nipype.interfaces.ants import ApplyTransforms
    IMG_TYPE = {3:0, 4:3} #3D images are "scalar"(0), 4D images are "time series" (3)
    at = ApplyTransforms()
    at.inputs.input_image = str(input) 
    at.inputs.reference_image = str(ref_image)
    at.inputs.transforms = str(transform)
    at.inputs.output_image = str(output)
    at.inputs.input_image_type = IMG_TYPE[input_dimensions]
    print(at.cmdline)
    at.run()
    return at.cmdline

def import_ocd_subject(subject, input_data_root, cwd):
    # Dictionary of all images copied
    to_copy = {
        'T1w_acpc':[
            'ses-7T/T1_processing/Nifti/T1w/T1w_acpc_dc_restore.nii.gz', #source path (source_file)
            config.refT1Path], #destination path (dest_file)
        'bvals':[
            'ses-7T/diff_analyze/bedpostx/bvals',
            config.bvalsPath_raw],
        'bvecs':[
            'ses-7T/diff_analyze/bedpostx/bvecs',
            config.bvecsPath],
        'diffusion':[
            'ses-7T/diff_analyze/bedpostx/data.nii.gz',
            config.diffPath_unregistered],
        'segmentation':[
            'ses-7T/T1_processing/Nifti/T1w/aparc+aseg.nii.gz',
            config.parcellationPath],
        'segmentation_fs':[ 
            # app-track_aLIC is hard coded to use this path 
            # so we must duplicate the segmentation here.
            'ses-7T/T1_processing/Nifti/T1w/aparc+aseg.nii.gz',
            config.parcellationFsPath],
        'mni_to_acpc_xfm':[
            'ses-7T/T1_processing/Nifti/MNINonLinear/xfms/standard2acpc_dc.nii.gz',
            config.mni_to_acpc_xfm], 
        'acpc_to_mni_xfm':['ses-7T/T1_processing/Nifti/MNINonLinear/xfms/acpc_dc2standard.nii.gz',
            config.acpc_to_mni_xfm],
        'DTI_to_acpc_xfm':[f'ses-7T/xfm/sub-{subject}_ses-7T_from-DTI_to-acpc_xfm.txt', config.DTI_to_acpc_xfm]}
    import_subject_from_list(Path(input_data_root) / f'dbspype/sub-{subject}', cwd, to_copy)
    # TODO: call edit_bvals_b9 function, inputs are paths to inputs
    edit_bvals_b9(cwd/config.bvalsPath_raw, cwd/config.bvalsPath, config.b0_threshold)
    apply_transform_to_nifti(cwd/config.diffPath_unregistered, 
        cwd/config.refT1Path, 
        cwd/config.diffPath, 
        cwd/config.DTI_to_acpc_xfm)


