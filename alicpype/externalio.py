#!/usr/bin/env python3
# description: copy and pasting imaging data to the appropriate input folders

import os
import shutil
from pathlib import Path
from . import config
import numpy as np

# import data from a list of subjects
def import_subject_from_list(subject_hcp_dir, cwd, to_copy): 
    """ 
    This function copies over HCP-style data from a list of subjects
    :subject_hcp_dir:     path to subject-specific directory where data will be copied from
    :cwd:                 path to subject-specific directory where data will be copied to
    :to_copy:             list of files to copy
    """

    subject_hcp_dir = Path(subject_hcp_dir) 
    cwd = Path(cwd) 
    print(cwd)
    assert(subject_hcp_dir.parent.is_dir())

    # copy over each image
    for source_file, dest_file in to_copy.values():
        print(f'copying {source_file} to {dest_file}...')
        os.makedirs(
            (cwd / dest_file).parent, 
            exist_ok=True)
        shutil.copyfile(
            subject_hcp_dir / source_file,
            cwd / dest_file)

# import 3T HCP data
def import_hcp_subject(subject, hcp_root, cwd):
    """ 
    This function imports 3T HCP-style data from a single subject.
    :subject:              subject ID
    :hcp_root:             path to HCP-style dataset
    :cwd:                  path to subject-specific directory where data will be copied to
    """
    # dict of all images copied
    to_copy = {
        'T1w_acpc':[
            'T1w/T1w_acpc_dc_restore_1.25.nii.gz', # source path (source_file)
            config.refT1Path], # destination path (dest_file)
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

# import 7T HCP data    
def import_7T_hcp_subject(subject, hcp_root, cwd):
    """ 
    This function imports 7T HCP-style data from a single subject and edits the bvals file.
    edit_bvals_b9:              edit bvalues below defined threshold to be treated as b0

    :subject:                   subject ID
    :hcp_root:                  path to HCP-style dataset
    :cwd:                       path to subject-specific directory where data will be copied to
    """

    # dict of all images copied
    to_copy = {
        'T1w_acpc':[
            'T1w/T1w_acpc_dc_restore_1.05.nii.gz', # source path (source_file)
            config.refT1Path], # destination path (dest_file)
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
    edit_bvals_b9(cwd/config.bvalsPath_raw, cwd/config.bvalsPath, config.b0_threshold) #call to edit_bvals_b9 function

# edit bvals file if mets condition of defined b0_threshold
def edit_bvals_b9(bvals_raw, bvals_b9, b0_threshold):
    """ 
    This function generates a copy of bvals file that applies a threshold to b0 volumes.
    :bvals_raw:         original bvals file
    :bvals_b9:          edited bvals files
    :b0_threshold:      defined b0 threshold, bvals greater than 9 and less than or equal to the threshold will be reduced to 9
    """

    correct_b0 = 9 # corrected b0 value 
    input_bvals = np.expand_dims(np.loadtxt(bvals_raw), axis = 0) # load original bval file
    input_bvals[input_bvals <= b0_threshold] = correct_b0 # change input_bvals that meet condition [input_bvals <= b0_threshold] and change value to correct_b0
    output_bvals = np.savetxt(bvals_b9, input_bvals, fmt = '%d') # save out the edited bvals to the bvals_b9 file (file name, data)

# applying transform to a nifti file
def apply_transform_to_nifti(input, ref_image, output, transform, input_dimensions = 4):
    """ 
    This function applies a transform to a nifti image
    :input:         input nifti image
    :ref_image:     reference image 
    :output:        output nifti image
    :transform:     transform file
    """

    from nipype.interfaces.ants import ApplyTransforms
    IMG_TYPE = {3:0, 4:3} # 3D images are "scalar"(0), 4D images are "time series" (3)
    at = ApplyTransforms()
    at.inputs.input_image = str(input) 
    at.inputs.reference_image = str(ref_image)
    at.inputs.transforms = str(transform)
    at.inputs.output_image = str(output)
    at.inputs.input_image_type = IMG_TYPE[input_dimensions]
    print(at.cmdline)
    at.run()
    return at.cmdline

# import 7T OCD subject data
def import_ocd_subject(subject, input_data_root, cwd):
    """ 
    This function imports 7T data from an individual OCD subject, edits the bvals file, and transform DTI to ACPC space.
    import_subject_from_list:   import data from from a list of subjects
    edit_bvals_b9:              edit bvalues below defined threshold to be treated as b0
    apply_transform_to_nifti:   transform diffusion nifti image to ACPC space

    :subject:                   subject ID
    :input_data_root:           path to dataset where data will be copied from
    :cwd:                       path to subject-specific directory where data will be copied to
    """

    # dict of all images copied
    to_copy = {
        'T1w_acpc':[
            'ses-7T/T1_processing/Nifti/T1w/T1w_acpc_dc_restore.nii.gz', # source path (source_file)
            config.refT1Path], # destination path (dest_file)
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
    edit_bvals_b9(cwd/config.bvalsPath_raw, cwd/config.bvalsPath, config.b0_threshold)
    apply_transform_to_nifti(cwd/config.diffPath_unregistered, 
        cwd/config.refT1Path, 
        cwd/config.diffPath, 
        cwd/config.DTI_to_acpc_xfm)


