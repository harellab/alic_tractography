#!/usr/bin/env python3
# description: calculate pathway-specific centroid using ALIC mask and rACC split into ventral and dorsal components

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

# dipy
from dipy.tracking.utils import reduce_labels
from dipy.tracking import utils
import dipy.io.streamline
import dipy.align
from dipy.tracking.utils import density_map

# alicpype imports
from . import config
from .config import targetLabels

# convert ACPC_to_MNI xfm in fsl format to ANTS
# function inverts the 2nd axis (AP persumably)
def convertfslxfm_to_ANTS(acpc_to_mni_xfm_fsl,acpc_to_mni_xfm_ANTS, acpc_ref_image):
    """
    This function converts a transform file FSL format to ANTS.
    :add_dimensions:            insert extra dimensions to resample ANTS transform

    acpc_to_mni_xfm_fsl:        input tranform in FSL format
    acpc_to_mni_xfm_ANTS:       output transform in ANTS format
    acpc_ref_image:             reference image
    
    """
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

# insert extra dimensions (to resample ANTS transform)
def add_dimensions(nifti_in, nifti_out):
    """
    This function inserts an additional dimension to resample the ANTS transform.
    nifti_in:       input ANTS transform nifti
    nifti_out:      output resampled ANTS transform nifti
    """
    nifti = nib.load(nifti_in)
    affine = nifti.affine
    #print(header)
    voxels = nifti.get_fdata()
    voxels = np.squeeze(voxels)
    voxels = np.expand_dims(voxels, 3)

    #print(np.shape(voxels)) # should be (?, ?, ?, 1, 3)
    nifti_itk = nib.Nifti1Image(voxels, affine)
    nib.save(nifti_itk, nifti_out)

# transform centroid coordinates from ACPC to MNI space
def transform_centerofmass_to_mni(input_points, transform_file):
    """
    This function transforms centroid coordinates from original to transformed space.
    :input_points:      inputs centroid coordinates
    :transform_file:     transform file

    :return: transformed output centroid coordinates
    """
    n_points = np.shape(input_points)[0]
    if n_points > 0:
        with NamedTemporaryFile(suffix = '.csv') as input_points_file:
            with NamedTemporaryFile(suffix = '.csv') as output_points_file:
                np.savetxt(input_points_file.name, input_points, delimiter=",", header="r,a,s")
                p = run(
                    ['Slicer',
                        '--no-main-window',
                        '--python-script', str(config.slicer_apply_xfm_script),
                        '--output', str(output_points_file.name),
                        '--transform', str(transform_file),
                        str(input_points_file.name)],
                    check=True)
                output_points = np.loadtxt(output_points_file.name, delimiter=",", skiprows=1, ndmin=2)
                return output_points
    else: return input_points 


# transform fiber bundles from ACPC to DTI space
def transform_bundle_to_dti(input_bundle, transform, output_bundle):
    """
    This function transforms fiber bundles from native space to transformed space.
    :input_bundle:      input fiber bundle vtk
    :transform:         transform file

    :return: transformed output fiber bundle
    """

    p = run(
        ['Slicer',
            '--no-main-window',
            '--python-script', str(config.slicer_apply_xfm2bundle_script),
            '--output', str(output_bundle),
            '--transform', str(transform),
            str(input_bundle)],
        check=True)

# transform fiber bundle in vtk format from ACPC to DTI space (transform_bundle_to_dti)
def transform_bundles(cwd):
    """
    This function transforms fiber bundles from ACPC to DTI space
    cwd:    path to subject-specific processe data directory
    """
    for iSide in ['left','right']:
        for iTarget in config.targetLabels[iSide]:
            target = f'combined_aLIC_{iSide}_{iTarget}_{config.freesurfer_lookup_table.loc[iTarget, "LabelName:"]}.vtk'
            output_bundle = f'combined_aLIC_{iSide}_{iTarget}_{config.freesurfer_lookup_table.loc[iTarget, "LabelName:"]}_space-dti.vtk'
            transform_bundle_to_dti(cwd/config.saveFigDir/target, cwd/config.DTI_to_acpc_xfm, cwd/config.saveFigDir/output_bundle)

# generate coordinates of centroid based on streamline heatmap restricted to within the ALIC
def generate_centroid(cwd):
    """
    This function converts transform from FSL to ANTS format and passes through generate_centroid_from_mask to calculate centroids.
    cwd:    path to subject-specific processe data directory
    """
    cwd = Path(cwd)
    ALIC_mask_file = {'left': cwd/ 'app-track_aLIC/output/ROIS/fullCutIC_ROI11_left.nii.gz',
                    'right': cwd/ 'app-track_aLIC/output/ROIS/fullCutIC_ROI11_right.nii.gz'}
    #STN_mask_file = {'left': cwd/ config.STN_segmentation_left,
                    #'right': cwd/ config.STN_segmentation_right}

    #paths to input data
    track_files = {k: [cwd / i for i in v]
        for k, v in config.track_files.items()}

    convertfslxfm_to_ANTS(cwd/config.acpc_to_mni_xfm, cwd/config.acpc_to_mni_xfm_itk, 
        cwd/config.MNI_ref_image)
    for iSide in ['left','right']: #iterate over each hemisphere
        # for normal operation, only calculate centroids for the ALIC and skip the stn
        # for imask, imask_label in [[ALIC_mask_file, 'withinALIC'],[STN_mask_file, 'STN']]: #iterate over both ALIC and STN mask
        for imask, imask_label in [[ALIC_mask_file, 'withinALIC'],]: #iterate over ALIC mask only
        
            mask = nib.load(imask[iSide]) #loading mask 
            for track_file in track_files[iSide]: 
                for iTarget in targetLabels[iSide]: #iterate over each pathway
                     generate_centroid_from_mask(cwd, mask, iTarget, track_file, imask_label)

def generate_centroid_from_mask(cwd, in_mask, iTarget, track_file, mask_label):
    """
    This function generates 3D coordinates of centroids based of density map restricted to within a mask (ie. ALIC, STN).
    cwd:        path to subject-specific process directory
    in_mask:    input mask
    iTarget:    PFC subregion label
    track_file: PFC subregion track file
    mask_label: mask label (ex. ALIC, STN)
    """
    cwd = Path(cwd)
    APaxis = 1
        # load Freesurfer labelsfreesurfer_lookup_table
    lookupTable = config.freesurfer_lookup_table
    saveFigDir = cwd / config.saveFigDir
    targetStr = lookupTable.loc[iTarget, 'LabelName:'] #label corresponding to each pathway
    in_file = saveFigDir / ('%s_%04d_%s' % (track_file.stem, iTarget, targetStr)) #generate input file
    in_nifti = nib.load(in_file.with_suffix('.nii.gz')) #load nifti of a pathway
    in_img = in_nifti.get_fdata() #convert nifti into a voxel array
    resample_mask = dipy.align.resample(in_mask,in_nifti) #resample ALIC mask nifti into heatmap nifti dimensions
    in_img = in_img*resample_mask.get_fdata() #multiply ALIC density map voxel array by resampled ALIC mask array
    num_slices = np.shape(in_img)[APaxis]
    out_file = saveFigDir / ('%s_%04d_%s_centerofmass_%s' % (track_file.stem, iTarget, targetStr, mask_label)) #output center of mass image in acpc
    mni_out_file = saveFigDir / ('%s_%04d_%s_centerofmass_%s_mni' % (track_file.stem, iTarget, targetStr, mask_label)) #output centroids in mni space
    centerofmass = np.zeros([num_slices,3]) #numerical array corresponding to x,y,z coordinates of centroid in acpc
    
    for iSlice in range(num_slices): #interating over total number of coronal slides of input image
        img_slice = in_img[:,iSlice,:] #an individual slice
        tmp = ndimage.center_of_mass(img_slice, labels=None, index=None) #step that calculates COM for each slice
        centerofmass[iSlice,:] = [tmp[0],iSlice,tmp[1]] #adding iSlice at APaxis=1
    centerofmass = centerofmass[~np.any(np.isnan(centerofmass),axis=1)]
    nib.affines.apply_affine(in_nifti.affine, centerofmass, inplace=True)
    if centerofmass.size > 0:
        print(centerofmass.shape)
        centerofmass_mni = transform_centerofmass_to_mni(centerofmass, 
            cwd/config.acpc_to_mni_xfm_itk)
    else: 
        centerofmass_mni = centerofmass
        print("csv for this target is empty")

    # export centroids in ACPC (3dSlicer compatible)
    save_centroids(centerofmass, targetStr, out_file)

    # export centroids in MNI (3dSlicer compatible)
    save_centroids(centerofmass_mni, targetStr, mni_out_file)
    

# save out centroid coordinates into a csv
def save_centroids(centerofmass, target_label, out_file):
    """ 
    This function saves out slicer-compatible csv containing centroids 
    centerofmass:   3D coordinates of centroids
    target_label:   PFC subregion label
    out_file:       subject-specific csv containing 3D coordinates (rostral, anterior, superior) of centroids 
    """
    n_points = np.shape(centerofmass)[0]
    centerofmass = np.array(centerofmass, dtype=float)
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

# generate a summary csv which includes centroids across all targets and subjects for a single defined coronal slice
def make_centroids_summary(project_dir, subject_list):
    """
    This function generates a summary csv which includes centroids across all targets and subjects for a single defined coronal slice.
    project_dir:    path to general processed data directory 
    subject_list:   list of subjects
    """
    project_dir = Path(project_dir)
    out_dir = project_dir / 'output'
    os.makedirs(out_dir, exist_ok=True)
    for iSide in ['left', 'right']:
        for iTarget in targetLabels[iSide]:
            # load Freesurfer labels
            lookupTable=config.freesurfer_lookup_table
            targetStr = lookupTable.loc[iTarget, 'LabelName:'] 
            outfile = {k: out_dir / f'{iTarget}_{targetStr}_{k}mm_summary_centroids_mni.csv' for k in config.coronal_slices_displayed_mm}
            group_average_outfile = out_dir / f'{iTarget}_{targetStr}_average_summary_centroids_mni.csv'
            target_points = {k: [] for k in config.coronal_slices_displayed_mm}
            subject_target_label = []
            interpolated_centroids = [] 
            for iSubject in subject_list:
                subject_dir = project_dir / iSubject / 'OCD_pipeline'
                #load each csv containing centroids in mni space
                track_file = config.track_files[iSide][0]
                input_csv_path = subject_dir / 'output' / ('%s_%04d_%s_centerofmass_withinALIC_mni.csv' % (track_file.stem, iTarget, targetStr))
                input_csv = np.loadtxt(input_csv_path, delimiter=",", skiprows=1, usecols=[1,2,3])
                #extract centroid coordinates at a single defined slice
                if input_csv.size > 0: #if input_csv array is not empty
                    for displayed_slice in config.coronal_slices_displayed_mm:
                        target_point = [np.interp(displayed_slice, input_csv[:,1], input_csv[:,0]), #interpolate r and s coordinates for a specific displayed_slice
                            displayed_slice, 
                            np.interp(displayed_slice, input_csv[:,1], input_csv[:,2])]
                        #concatenate target_point from all subjects (target_points)
                        target_points[displayed_slice].append(target_point)
                    subject_target_label.append(f'{targetStr}_{iSubject}')
                
                    # generate 20 csvs (1 per pathway) containing group average coordinates from anterior slices -13 to 19
                    start = -13
                    stop = 20
                    anterior_slices = np.arange(start,stop)
                    target_point_interp = np.transpose([np.interp(anterior_slices, input_csv[:,1], input_csv[:,0]), # generates array per subject & per target of interpolated coronal slices 
                        anterior_slices,
                        np.interp(anterior_slices, input_csv[:,1], input_csv[:,2])])
                    # generate array containing interpolated RAS coordinates for all subjects, all anterior slices
                    interpolated_centroids.append(target_point_interp)
                else: print("csv for this target is empty")
            
            # average interpolated_centroids over subject and save out csv
            averaged_centroids = np.average(interpolated_centroids, axis = 0)
            save_centroids(averaged_centroids, targetStr, group_average_outfile)
                
            # save out target_points array in slicer formatted csv
            for displayed_slice in config.coronal_slices_displayed_mm:
                print(f'saving {outfile[displayed_slice]}...')
                save_centroids(target_points[displayed_slice], subject_target_label, outfile[displayed_slice])