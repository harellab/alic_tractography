#!/usr/bin/env python3
# description: use z-plane value (subcallosal cingulate) to cut the rACC mask along the z-axis to split the rACC into dorsal and ventral components as defined by the SCC

import os  # Importing the os module for working with the operating system
from os.path import join as pjoin  # Importing the `join` function from the `os.path` module
import numpy as np  # Importing the NumPy library for numerical operations
import nibabel as nib  # Importing the NiBabel library for working with neuroimaging data
from nipype.interfaces import fsl  # Importing the FSL interface from the NiPype library
from nipype.interfaces.fsl.maths import Threshold  # Importing the Threshold class from the FSL module
from pathlib import Path
from subprocess import run
from . import config

# function to divide ROI mask by the mid point of a divider mask
def cut_roi(
    in_roi_path, 
    in_roi_fname, 
    in_divider_path, 
    in_divider_fname,  
    out_path, 
    out_fname, 
    cut_axis="z", 
):
    """
    This function divides input ROI by the midpoint of divider mask.
    :in_roi_path:        path to the input roi nifti
    :in_roi_fname:       name of the input roi nifti
    :in_divider_path:    path to the divider roi nifti  
    :in_divider_fname:   name to the divider roi nifti  
    :out_path:           path to the output roi masks 
    :out_fname:          prefix of the output roi masks 
    :cut_axis="z":       choose which axis to cut the roi along: x, y, or z
    """

    from os.path import join as pjoin
    import numpy as np
    import scipy.special as sc
    import nibabel as nib
        
    roi_file=pjoin(in_roi_path, in_roi_fname)
    divider_file=pjoin(in_divider_path, in_divider_fname)

    roi_raw=nib.load(roi_file)
    roi_header=roi_raw.header 
    roi_affine=roi_raw.affine
    roi_data=roi_raw.get_fdata()

    out_arr1=np.zeros(roi_data.shape)
    out_arr2=np.zeros(roi_data.shape)

    divider_raw=nib.load(divider_file)
    divider_data=divider_raw.get_fdata()

    div_x_r, div_y_r, div_z_r=shrinkarr(divider_data)
    roi_x_r, roi_y_r, roi_z_r=shrinkarr(roi_data)

    if cut_axis=="z":
        d0, d1=div_z_r
        r0, r1=roi_z_r
    elif cut_axis=="y":
        d0, d1=div_y_r
        r0, r1=roi_y_r
    elif cut_axis=="x":
        d0, d1=div_x_r
        r0, r1=roi_x_r
    d_point=int(sc.round((d0+d1)/2))
    if (d_point<=r1) & (d_point>=r0):
        if cut_axis=="z":
            out_arr1[:, :, :d_point]=roi_data[:, :, :d_point]
            out_arr2[:, :, d_point:]=roi_data[:, :, d_point:]        
        elif cut_axis=="y":
            out_arr1[:, :d_point, :]=roi_data[:, :d_point, :]
            out_arr2[:, d_point:, :]=roi_data[:, d_point:, :] 
        elif cut_axis=="x":
            out_arr1[:d_point, :, :]=roi_data[:d_point, :, :]
            out_arr2[d_point:, :, :]=roi_data[d_point:, :, :]        
        out_img1=nib.Nifti1Image(out_arr1, affine=roi_affine, header=roi_header)
        #img1 = ventral rostral ACC
        nib.save(out_img1, pjoin(out_path, out_fname+"_ventral.nii.gz"))
        #img2 = dorsal rostral ACC
        out_img2=nib.Nifti1Image(out_arr2, affine=roi_affine, header=roi_header)
        nib.save(out_img2, pjoin(out_path, out_fname+"_dorsal.nii.gz"))
    else:
        raise ValueError("mid point of divider out of range of roi") 

def shrinkarr(arr):  
    """
    This function gets the range of non-zero data of a 3d array
    :arr:    numpy array to be shrunk

    :return: summary of support of arr (]min x, max x], [min y, max y], [min z, max z]) 
    """  
    import numpy as np
    ax, ay, az=arr.shape

    # Flatten the array on 3 axis and sum to find where non-zero data exist
    arr_x_sum=[sum(arr[i,:,:].flatten()) for i in range(ax)]
    arr_y_sum=[sum(arr[:,i,:].flatten()) for i in range(ay)]
    arr_z_sum=[sum(arr[:,:,i].flatten()) for i in range(az)]
    # Find range of non-zero data on 3 axis
    arr_x_nonzero = np.nonzero(arr_x_sum)
    arr_x_r=[arr_x_nonzero[0][0], arr_x_nonzero[0][-1]]
    arr_y_nonzero = np.nonzero(arr_y_sum)
    arr_y_r=[arr_y_nonzero[0][0], arr_y_nonzero[0][-1]]
    arr_z_nonzero = np.nonzero(arr_z_sum)
    arr_z_r=[arr_z_nonzero[0][0], arr_z_nonzero[0][-1]]
    return (arr_x_r, arr_y_r, arr_z_r) 

# split rACC ROI
def split_racc(cwd):
    """
    This function generates an rostral anterior cingulate ROI and registers the subcallosal cingualte mask from original to transformed space.
    :cwd:    path to subject-specific processed data directory
    """
    print('running split_racc')
    cwd = Path(cwd)
    subject_path = cwd  # Joining the base path with the HCP path
    indata = subject_path / 'indata'
    divider_mni_fname = config.splitraccplane
    
    # generate rACC ROI nifti from aparg+aseg
    print('Generate rACC ROI nifti from aparg+aseg..')
    cmd = ['fslmaths', 
        str(cwd / config.parcellationPath), 
        '-thr', str(1026), 
        '-uthr', str(1026), 
        str(indata / 'lh_rostralanteriorcingulate_ROI_acpc.nii.gz')]
    run(cmd)
    cmd = ['fslmaths', 
        str(cwd / config.parcellationPath), 
        '-thr', str(2026), 
        '-uthr', str(2026), 
        str(indata / 'rh_rostralanteriorcingulate_ROI_acpc.nii.gz')]
    run(cmd)

    # register SCC mask from MNI space to acpc space
    print('Register SCC mask from MNI space to acpc space...')
    import nipype.interfaces.fsl as fsl
    applyxfm = fsl.preprocess.ApplyWarp()
    applyxfm.inputs.in_file = divider_mni_fname #subcallosal_cing_mask as input
    applyxfm.inputs.field_file = cwd/config.mni_to_acpc_xfm
    subcallosal_cingulate_acpc = pjoin(indata, 'subcallosal_cingulate_acpc.nii.gz')
    applyxfm.inputs.out_file = subcallosal_cingulate_acpc
    applyxfm.inputs.ref_file = pjoin(cwd, config.parcellationPath)
    #applyxfm.inputs.apply_xfm = True
    applyxfm.inputs.interp = 'nn' # "nearestneighbour" #binarize subcallosal mask
    result = applyxfm.run() 

    #in_fname=pjoin(indata, "")
    in_rois = [pjoin(indata,"rh_rostralanteriorcingulate_ROI_acpc.nii.gz"), 
        pjoin(indata,"lh_rostralanteriorcingulate_ROI_acpc.nii.gz")]
    #TODO move rACC pathnames to config.py
    in_divider_fname = subcallosal_cingulate_acpc
    out_rois = [pjoin(indata,"rh_rostralanteriorcingulate_ROI_acpc"), 
        pjoin(indata,"lh_rostralanteriorcingulate_ROI_acpc")]
    #TODO move rACC pathnames to config.py
    cut_roi("", in_rois[0], "", in_divider_fname, "", out_rois[0])
    cut_roi("", in_rois[1], "", in_divider_fname, "", out_rois[1])

    # MODIFY APARC+ASEG WITH DIVIDED rACC ROI
    # load aparc+aseg in acpc
    aparc_aseg = nib.load(cwd / config.parcellationPath)
    aparc_aseg_voxel_grid = aparc_aseg.get_fdata()

    # load rACC masks and voxel grid
    for key, value in config.rACC_split_labels.items():
        rACC_ROI = nib.load(cwd / value)
        rACC_ROI_voxel_grid = rACC_ROI.get_fdata() #values either 0 and 1 because it's a mask
        aparc_aseg_voxel_grid[rACC_ROI_voxel_grid>0.5] = key #selecting aparc_aseg voxels within rACC mask and output corresponding key

    # save out modified aparc+aseg
    aparc_aseg_nifti = nib.Nifti1Image(aparc_aseg_voxel_grid,aparc_aseg.affine) #convert to nifti image
    nib.save(aparc_aseg_nifti,filename=cwd / config.rACC_mod_aparc_aseg)
