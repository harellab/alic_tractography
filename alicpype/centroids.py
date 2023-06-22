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

#dipy
from dipy.tracking.utils import reduce_labels
from dipy.tracking import utils
import dipy.io.streamline
import dipy.align
from dipy.tracking.utils import density_map

#alicpype imports
from . import config
from .config import targetLabels

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
                out_file = saveFigDir / ('%s_%04d_%s_centerofmass_withinALIC' % (track_file.stem, iTarget, targetStr)) #output center of mass image
                centerofmass = np.zeros([num_slices,3]) #numerical array corresponding to x,y,z coordinates of centroid
                for iSlice in range(num_slices): #interating over total number of coronal slides of input image
                    img_slice = in_img[:,iSlice,:] #an individual slice
                    tmp = ndimage.center_of_mass(img_slice, labels=None, index=None) #step that calculates COM for each slice
                    centerofmass[iSlice,:] = [tmp[0],iSlice,tmp[1]] #adding iSlice at APaxis=1
                centerofmass = centerofmass[~np.any(np.isnan(centerofmass),axis=1)]
                nib.affines.apply_affine(in_nifti.affine, centerofmass, inplace=True)

                np.savetxt(out_file.with_suffix('.csv'), centerofmass, delimiter=",") #save output file as a .csv for all slices
                # make a Pandas dataframe of the location data and save it
                n_points = np.shape(centerofmass)[0]
                # point_labels = [f'{targetStr}_{i}' for i in range(n_points)]
                column_labels = ['label', 'r','a','s','defined','selected','visible','locked','description']
                # col_defined = np.ones(point_labels, dtype=np.int)
                # col_selected = np.zeros(point_labels, dtype=np.int)
                # col_visible = np.ones(point_labels, dtype=np.int)
                # col_locked = np.zeros(point_labels, dtype=np.int)
                # description = ['' for i in range(n_points)]
                table_data = {'label': [f'{targetStr}_{i}' for i in range(n_points)], 
                    'r': centerofmass[:,0],
                    'a': centerofmass[:,1],
                    's': centerofmass[:,2],
                    'defined': np.ones(n_points, dtype=np.int),
                    'selected': np.zeros(n_points, dtype=np.int),
                    'visible': np.ones(n_points, dtype=np.int),
                    'locked': np.zeros(n_points, dtype=np.int),
                    'description':['' for i in range(n_points)]}
                table = pd.DataFrame(table_data, columns=column_labels)
                table.set_index('label')
                table.to_csv(out_file.with_suffix('.csv'), index=False)

