#!/usr/bin/env python3
# description: use z-plane value to cut a ROI mask along the z-axis
#rACC ROI = "side_" + rostralanteriorcingulate_ROI.nii.gz

import os  # Importing the os module for working with the operating system
from os.path import join as pjoin  # Importing the `join` function from the `os.path` module
import numpy as np  # Importing the NumPy library for numerical operations
import nibabel as nib  # Importing the NiBabel library for working with neuroimaging data
from nipype.interfaces import fsl  # Importing the FSL interface from the NiPype library
from nipype.interfaces.fsl.maths import Threshold  # Importing the Threshold class from the FSL module
from pathlib import Path
from subprocess import run
from . import config

def split_racc(subject, cwd):
    subj= str(subject)
    cwd = Path(cwd)
    base_path = os.path.abspath(cwd)  # Setting the base path to DBS_OCD_Processing directory
    proj_path = pjoin(base_path, 'indata')  # Joining the base path with the project path
    mni_path = pjoin(base_path, 'indata')  # Joining the base path with the MNI path
    mni_fname = pjoin(mni_path, 'MNI152_T1_1mm_brain.nii.gz')  # Joining the MNI path with the MNI filename
    subject_path = cwd  # Joining the base path with the HCP path
    indata = pjoin(subject_path, 'indata')
    outdata = pjoin(subject_path, 'output')


    # Step 1: generate rACC ROI nifti from aparg+aseg
    cmd = ['fslmaths', 
        str(cwd / config.parcellationPath), 
        '-thr', str(1026), 
        '-uthr', str(1026), 
        str(cwd / 'output' / 'lh_rostralanteriorcingulate_ROI.nii.gz')]
    run(cmd)
    cmd = ['fslmaths', 
        str(cwd / config.parcellationPath), 
        '-thr', str(2026), 
        '-uthr', str(2026), 
        str(cwd / 'output' / 'rh_rostralanteriorcingulate_ROI.nii.gz')]
    run(cmd)

    # Step 2: Create binary divider mask in MNI space 
    ##divider_mni_fname=pjoin(proj_path, 'subcallosal_cingulate_mni.nii.gz')
    #mni = nib.load(mni_fname)
    #mni_header=mni.header 
    #mni_affine=mni.affine
    #mni_data=mni.get_fdata()
    #mask_arr=np.zeros(mni_data.shape)
    #mask_arr[:, :, 76]=1 #extract a single line of voxels at z=76 (axial slice)
    #mask_img=nib.Nifti1Image(mask_arr, affine=mni_affine, header=mni_header)
    #nib.save(mask_img, divider_mni_fname)

    # Step 3: invert acpc2MNI linear transform (xfm = transform)
    import nipype.interfaces.fsl as fsl
    invt = fsl.ConvertXFM()
    invt.inputs.in_file = pjoin(indata,'acpc2MNILinear.mat') # TO DO
    invt.inputs.invert_xfm = True
    MNI2acpcLinear_xfm = pjoin(indata,'MNI2acpcLinear.mat') # TO DO
    invt.inputs.out_file = MNI2acpcLinear_xfm #output located in indata folder
    invt.cmdline 
    invt.run()

    # Step 3: Register SCC mask from MNI space to acpc space
    #diff_path_acpc=pjoin(subject_path, 'OCD_pipeline_noSubcorticalGray/indata/')
    #diff_mask_path=pjoin(diff_path, "masks")
    #if not os.path.exists(diff_mask_path):
        #os.makedir(diff_mask_path

    import nipype.interfaces.fsl as fsl
    applyxfm = fsl.preprocess.ApplyXFM()
    applyxfm.inputs.in_file = divider_mni_fname #subcallosal_cing_mask as input
    applyxfm.inputs.in_matrix_file = MNI2acpcLinear_xfm
    subcallosal_cingulate_acpc = pjoin(indata, 'subcallosal_cingulate_acpc.nii.gz')
    applyxfm.inputs.out_file = subcallosal_cingulate_acpc
    applyxfm.inputs.reference = pjoin(cwd, config.refT1Path)
    applyxfm.inputs.apply_xfm = True
    applyxfm.inputs.interp = "nearestneighbour" #binarize subcallosal mask
    result = applyxfm.run() 

    # Step 4: Use the divided subcallosal mask to cut the rostral anterior cingulate ROI mask 
    # function to get the range of non-zero data of a 3d array 
    def shrinkarr(
    arr, # array as input data      
    ):
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

    # function to divide ROI mask by the mid point of a divider mask
    def cut_roi(
        in_roi_path, # path to the input roi nifti
        in_roi_fname, # name of the input roi nifti
        in_divider_path, # path to the divider roi nifti  
        in_divider_fname, # name to the divider roi nifti  
        out_path, #path to the output roi masks 
        out_fname, # prefix of the output roi masks 
        cut_axis="z", # choose which axis to cut the roi along: x, y, or z
    ):
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
        #print(d0, d1, d_point, r0, r1)
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
            nib.save(out_img1, pjoin(out_path, out_fname+"_1.nii.gz"))
            #img2 = dorsal rostral ACC
            out_img2=nib.Nifti1Image(out_arr2, affine=roi_affine, header=roi_header)
            nib.save(out_img2, pjoin(out_path, out_fname+"_2.nii.gz"))
        else:
            raise ValueError("mid point of divider out of range of roi")
        
    #in_fname=pjoin(indata, "")
    in_rois = [pjoin(indata,"rh_rostralanteriorcingulate_ROI_acpc.nii.gz"), pjoin(indata,"lh_rostralanteriorcingulate_ROI_acpc.nii.gz")]
    in_roi_fname = in_rois
    in_divider_fname = subcallosal_cingulate_acpc
    #in_divider_fname = subcallosal_cingulate_acpc
    #out_path=[pjoin(outdata,""
    out_rois = rois = [pjoin(indata,"rh_rostralanteriorcingulate_ROI_acpc"), pjoin(indata,"lh_rostralanteriorcingulate_ROI_acpc")]
    out_fname = out_rois
    cut_roi("", in_roi_fname[0], "", in_divider_fname, "", out_fname[0])
    cut_roi("", in_roi_fname[1], "", in_divider_fname, "", out_fname[1])

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
