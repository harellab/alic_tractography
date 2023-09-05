#!/usr/bin/env python3
# description: calculate (within ALIC) a centroid for each pathway using ALIC mask and rACC split into ventral and dorsal

# SETUP
import os
import sys
import itertools
import numpy as np
from warnings import warn
from pathlib import Path
import nibabel as nib
from scipy import ndimage
from subprocess import run

import pandas as pd
import wmaPyTools.roiTools
import wmaPyTools.analysisTools
import wmaPyTools.segmentationTools
import wmaPyTools.streamlineTools
import wmaPyTools.visTools
from tempfile import NamedTemporaryFile

#dipy
from dipy.tracking.utils import reduce_labels
from dipy.tracking import utils
import dipy.io.streamline
import dipy.align
from dipy.tracking.utils import density_map

#alicpype imports
from . import config
from .config import targetLabels

# Convert ACPC_to_MNI xfm in fsl format to ANTS
# Function inverts the 2nd axis (AP persumably)
def convertfslxfm_to_ANTS(acpc_to_mni_xfm_fsl,acpc_to_mni_xfm_ANTS, acpc_ref_image):
    if acpc_to_mni_xfm_ANTS.is_file():
        os.remove(acpc_to_mni_xfm_ANTS)
    cmd = ['3dresample', '-master', str(acpc_ref_image),
        '-prefix', str(acpc_to_mni_xfm_ANTS),
        '-input', str(acpc_to_mni_xfm_fsl)]
    run(cmd, check=True)
    
    add_dimensions(acpc_to_mni_xfm_ANTS, acpc_to_mni_xfm_ANTS)
    invert_axis = 1
    nifti = nib.load(acpc_to_mni_xfm_ANTS)
    voxels = nifti.get_fdata()
    voxels[:,:,:,:,invert_axis] = -1 * voxels[:,:,:,:,invert_axis]
    xfm_hdr_template = nib.load(config.xfm_header_template).header
    nifti_out = nib.Nifti1Image(voxels, nifti.affine, header=xfm_hdr_template)
    nib.save(nifti_out, acpc_to_mni_xfm_ANTS)

# insert extra dimensions (to resamples ANTS transform)
def add_dimensions(nifti_in, nifti_out):
    nifti = nib.load(nifti_in)
    affine = nifti.affine
    #print(header)
    voxels = nifti.get_fdata()
    voxels = np.squeeze(voxels)
    voxels = np.expand_dims(voxels, 3)

    #print(np.shape(voxels)) # should be (?, ?, ?, 1, 3)
    nifti_itk = nib.Nifti1Image(voxels, affine)
    nib.save(nifti_itk, nifti_out)

#Transform centroid coordinates from ACPC to MNI space
# Need to use the inverse fsl xfm (mni to acpc, NOT acpc to mni), transforming points in the inverse of images
def transform_centerofmass_to_mni(acpc_centerofmass, mni_to_acpc_xfm_itk):
    with NamedTemporaryFile(suffix = '.csv') as centerofmasstemp:
        with NamedTemporaryFile(suffix = '.csv') as centerofmasstemp_mni:
            np.savetxt(centerofmasstemp.name, acpc_centerofmass, delimiter=",", header="r,a,s")
            cmd = ['antsApplyTransformsToPoints', 
                '-d', '3',
                '-i', centerofmasstemp.name, 
                '-o', str(centerofmasstemp_mni.name),
                '-t', f'[{str(mni_to_acpc_xfm_itk)},0]']
            run(cmd, check=True)
            mni_centerofmass = np.loadtxt(centerofmasstemp_mni.name, delimiter=",", skiprows=1)
            return mni_centerofmass

def generate_centroid(cwd):
    cwd = Path(cwd)
    ALIC_mask_dir = {'left': config.OCD_PIPELINE_DIR / 'app-track_aLIC/output/ROIS/fullCutIC_ROI11_left.nii.gz',
                    'right': config.OCD_PIPELINE_DIR / 'app-track_aLIC/output/ROIS/fullCutIC_ROI11_right.nii.gz'}
    #TODO, not a dir, change to "file"

    #paths to input data
    track_files = {k: [cwd / i for i in v]
        for k, v in config.track_files.items()}
    # load Freesurfer labels
    lookupTable=pd.read_csv(cwd / config.lutPath,index_col='#No.')
    saveFigDir = cwd / config.saveFigDir

    APaxis = 1
    convertfslxfm_to_ANTS(cwd/config.mni_to_acpc_xfm, cwd/config.mni_to_acpc_xfm_itk, 
        cwd/config.acpc_ref_image)
    for iSide in ['left', 'right']: #iterate over each hemisphere
        ALIC_mask = nib.load(ALIC_mask_dir[iSide])#loading ALIC mask
        for track_file in track_files[iSide]: 
            for iTarget in targetLabels[iSide]: #iterate over each pathway
                targetStr = lookupTable.loc[iTarget, 'LabelName:'] #label corresponding to each pathway
                in_file = saveFigDir / ('%s_%04d_%s' % (track_file.stem, iTarget, targetStr)) #generate input file
                in_nifti = nib.load(in_file.with_suffix('.nii.gz')) #load nifti of a pathway
                in_img = in_nifti.get_fdata() #convert nifti into a voxel array
                resample_ALIC_mask = dipy.align.resample(ALIC_mask,in_nifti) #resample ALIC mask nifti into heatmap nifti dimensions
                in_img = in_img*resample_ALIC_mask.get_fdata() #multiply ALIC density map voxel array by resampled ALIC mask array
                num_slices = np.shape(in_img)[APaxis]
                out_file = saveFigDir / ('%s_%04d_%s_centerofmass_withinALIC' % (track_file.stem, iTarget, targetStr)) #output center of mass image in acpc
                mni_out_file = saveFigDir / ('%s_%04d_%s_centerofmass_withinALIC_mni' % (track_file.stem, iTarget, targetStr)) #output centroids in mni space
                centerofmass = np.zeros([num_slices,3]) #numerical array corresponding to x,y,z coordinates of centroid in acpc
                for iSlice in range(num_slices): #interating over total number of coronal slides of input image
                    img_slice = in_img[:,iSlice,:] #an individual slice
                    tmp = ndimage.center_of_mass(img_slice, labels=None, index=None) #step that calculates COM for each slice
                    centerofmass[iSlice,:] = [tmp[0],iSlice,tmp[1]] #adding iSlice at APaxis=1
                centerofmass = centerofmass[~np.any(np.isnan(centerofmass),axis=1)]
                nib.affines.apply_affine(in_nifti.affine, centerofmass, inplace=True)
                centerofmass_mni = transform_centerofmass_to_mni(centerofmass, 
                    cwd/config.mni_to_acpc_xfm_itk)

                #export centroids in acpc (slicer compatible)
                save_centroids(centerofmass, targetStr, out_file)

                #export centroids in mni (slicer compatible)
                save_centroids(centerofmass_mni, targetStr, mni_out_file)
    
    
def save_centroids(centerofmass, target_label, out_file):
    """ Generate and save slicer-compatible csv containing centroids """
    n_points = np.shape(centerofmass)[0]
    column_labels = ['label', 'r','a','s','defined','selected','visible','locked','description']
    if isinstance(target_label, str):
        label_list = [f'{target_label}_{i}' for i in range(n_points)]
    else:
        label_list = target_label
        #case when target_label list is given
    table_data = {'label': label_list, 
        'r': centerofmass[:,0],
        'a': centerofmass[:,1],
        's': centerofmass[:,2],
        'defined': np.ones(n_points, dtype=int),
        'selected': np.zeros(n_points, dtype=int),
        'visible': np.ones(n_points, dtype=int),
        'locked': np.zeros(n_points, dtype=int),
        'description':['' for i in range(n_points)]}
    table = pd.DataFrame(table_data, columns=column_labels)
    table.set_index('label')
    table.to_csv(out_file.with_suffix('.csv'), index=False)


def make_centroids_summary(project_dir, subject_list):
    """generate a summary csv which includes centroids across all targets and subjects for a single defined coronal slice"""
    project_dir = Path(project_dir)
    out_dir = project_dir / 'output'
    os.makedirs(out_dir, exist_ok=True)
    for iSide in ['left', 'right']:
        for iTarget in targetLabels[iSide]:
            # load Freesurfer labels
            lookupTable=config.freesurfer_lookup_table
            targetStr = lookupTable.loc[iTarget, 'LabelName:'] 
            outfile = out_dir / f'{iTarget}_{targetStr}_summary_centroids_mni.csv' 
            print(outfile) #TODO delete me
            target_points = []
            subject_target_label = []
            for iSubject in subject_list:
                subject_dir = project_dir / iSubject / 'OCD_pipeline'
                #load each csv containing centroids in mni space
                track_file = config.track_files[iSide][0]
                input_csv_path = subject_dir / 'output' / ('%s_%04d_%s_centerofmass_withinALIC_mni.csv' % (track_file.stem, iTarget, targetStr))
                input_csv = np.loadtxt(input_csv_path, delimiter=",", skiprows=1, usecols=[1,2,3])
                #extract centroid coordinates at a single defined slice (ac_displayed_slice)
                target_point = [np.interp(config.ac_displayed_slice, input_csv[:,1], input_csv[:,0]),
                    config.ac_displayed_slice, 
                    np.interp(config.ac_displayed_slice, input_csv[:,1], input_csv[:,2])]
                #concatenate target_point from all subjects (target_points)
                target_points.append(target_point)
                subject_target_label.append(f'{targetStr}_{iSubject}')
            #save out target_points array in slicer formatted csv
            save_centroids(target_points, subject_target_label, outfile)
