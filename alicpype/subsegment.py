#!/usr/bin/env python3
# description: generate subsegmented ALIC fiber bundles

# SETUP
import os
import sys
import itertools
import numpy as np
from warnings import warn
from pathlib import Path
import nibabel as nib
from scipy import ndimage
from . import config
from subprocess import run
from tempfile import NamedTemporaryFile
#import random

import pandas as pd
import wmaPyTools.roiTools
import wmaPyTools.analysisTools
import wmaPyTools.segmentationTools
import wmaPyTools.streamlineTools
import wmaPyTools.visTools

# dipy
from dipy.tracking.utils import reduce_labels
from dipy.tracking import utils
from dipy.tracking.utils import density_map

from .config import targetLabels
import nipype.interfaces.fsl as fsl

# Convert tck to vtk
def tck2vtk(in_file, overwrite=True):
    """ 
    This function converts a tck file to a vtk
    :in_file:   input tck file
    """
    in_file = Path(in_file)
    assert(in_file.is_file())
    assert(in_file.suffix.lower() == '.tck')
    
    out_file = in_file.with_suffix('.vtk')

    # make sure to set $APPTAINER_BIND before running. for instance:
    # export APPTAINER_BIND=/home,${APPTAINER_BIND}
    cmd = ['apptainer', 'exec', 'docker://brainlife/mrtrix3:3.0.0',
		'tckconvert', str(in_file), str(out_file)]

    if overwrite:
        cmd.append('-f')
    print(cmd)
    run(cmd, check = True)


# convert transform from FSL format to MRtrix format
def convert_xfm_fsl_to_mrtrix(input_xfm, output_xfm, ref_image):
    """ 
    This function converts a transform in FSL format to MRtrix format
    :input_xfm:      input transform in FSL format
    :output_xfm:     output transform in MRtrix format
    :ref_image:      reference image
    """
    # generate a warpfield
    with NamedTemporaryFile(suffix = '.nii.gz') as x:
        cmd = ['warpinit', '-force', str(ref_image), str(x.name)]
        run(cmd, check = True)

    # apply the fsl-format transform (input_xfm) to the warpfield/mrtrix non-linear transform format
        applyxfm = fsl.preprocess.ApplyWarp()
        applyxfm.inputs.in_file = str(x.name)
        applyxfm.inputs.field_file = str(input_xfm) #original format xfm
        applyxfm.inputs.out_file = str(output_xfm) 
        applyxfm.inputs.ref_file = str(ref_image)
        applyxfm.run()
    
# apply MRtrix format transform to tck
def apply_mrtrix_xfm(input_tck, output_tck, mrtrix_xfm):
    """ 
    This function applies an MRtrix format transform to a tck file
    :input_tck:      input tck file
    :output_tck:     output transformed tck file
    :mrtrix_xfm:     MRtrix-format transform
    """
    cmd = ['tcktransform', str(input_tck), str(mrtrix_xfm), str(output_tck), '-force']
    run(cmd, check = True)
    return nib.streamlines.load(output_tck).streamlines

# generate OCD response tract ROIs based on coronal slices of interest 
def ocd_response_tract_roi(input_roi, coronal_slice, dimension = 'y', threshold = 1):
    """ 
    This function generates a planar ROI image at a single coronal slice from an input ROI image
    :input_roi:         input ROI image
    :coronal_slice:     single coronal slice mask image from input ROI image
    """
    input_roi_nifti = nib.load(input_roi)
    planar_roi = wmaPyTools.roiTools.makePlanarROI(input_roi_nifti, coronal_slice, dimension)
    planar_data = planar_roi.get_fdata()
    target_data = input_roi_nifti.get_fdata() >= threshold #binarizes mask for ocd response tract
    planar_data = planar_data * target_data
    return nib.Nifti1Image(planar_data, input_roi_nifti.affine, input_roi_nifti.header)

# calculate the number of streamlines and percent streamlines overlapping with OCD response tract ROI
def calculate_streams_ocd_response(input_streams, planar_roi):
    """ 
    This function calculates the number and percentage of streamlines from each segmented ALIC pathway that overlaps with a planar ROI image
    :input_streams:     input tck file containing streamlines
    :planar_roi:        single coronal slice mask image from input ROI image
    """
    ocd_response_streams = wmaPyTools.segmentationTools.segmentTractMultiROI(input_streams, 
                        [planar_roi,], 
                        [True,], 
                        ['any',]) 
    ocd_response_streams_perecent = np.sum(ocd_response_streams) / len(input_streams) * 100
    return (np.sum(ocd_response_streams), ocd_response_streams_perecent)

# get streamlines for prefrontal cortical target
def get_streams_matching_target(streams, atlas, target):
    """ 
    This function gets the streamlines for each prefrontal cortical target
    :streams:   output streamlines from PFC target
    :atlas:     DK atlas
    :target:    PFC target label
    """
    target_mask=wmaPyTools.roiTools.multiROIrequestToMask(atlas,target)
    # return boolean mask for stream selection
    return wmaPyTools.segmentationTools.segmentTractMultiROI(streams, 
                    [target_mask,], 
                    [True,], 
                    ['either_end',]) 

# save out density map
def save_density_map(streams, ref_img, out_file):
    """
    This function saves out density map for each PFC target
    streams:    streamlines from PFC target
    ref_img:    reference image (e.g. T1)
    out_file:   density map nifti for PFC target
    """
    density=utils.density_map(streams, ref_img.affine, ref_img.shape)
    densityNifti = nib.nifti1.Nifti1Image(density, ref_img.affine, ref_img.header)
    nib.save(densityNifti, out_file)
    
# save out streamlines for each prefrontal cortical target
def save_streams_matching_target(streams, atlas, lookupTable, target, out_file):
    """
    This function saves streamlines for each PFC target in tck and vtk format and pass through save_density_map.
    streams:        input streamlines from PFC target
    atlas:          DK atlas
    lookupTable:    freesurfer lookup table
    target:         PFC target label
    out_file:       tck and vtk of streamlines from PFC target
    """
    strTarget = lookupTable.loc[target, 'LabelName:']
    print('target label is: %s (%s)' % (target, strTarget))
    print(out_file)
    # get boolean vector of matching streams
    targetBool = get_streams_matching_target(streams, atlas, target)
    streams = streams[targetBool]
        
    #dipy quickbundles, will only run if > 0 streamlines present
    if len(streams) > 0:
        streams = streams[bundle(streams)]
        
    #save *.tck tractogram
    wmaPyTools.streamlineTools.stubbornSaveTractogram(streams,
        savePath=str(out_file.with_suffix('.tck')))
    # save nifti density map
    save_density_map(streams, atlas, out_file.with_suffix('.nii.gz'))

    # convert tcks to vtks
    tck2vtk(out_file.with_suffix('.tck'))
    return targetBool

# apply the initial culling, to remove extraneous streamlines 
# first requires doing a DIPY quickbundling
def bundle(streams):
    """
    This function applies DIPY QuickBundles for removal of extraneous streamlines
    streams: streamlines from PFC target to be culled
    return: boolean array showing surviving streamlines followin QuickBundles culling
    """
    print("DIPY quickbundle")
    clusters=wmaPyTools.streamlineTools.quickbundlesClusters(streams, thresholds = [30,20,10], nb_pts=100)

    #use those clusters to identify the streamlines to be culled
    print("identify streamlines to remove")
    survivingStreamsIndices, culledStreamIndicies=wmaPyTools.streamlineTools.cullViaClusters(clusters,streams,3)
    #convert survivingStreamsIndicies into a bool vec
    survivingStreamsBoolVec=np.zeros(len(streams),dtype=bool)
    survivingStreamsBoolVec[survivingStreamsIndices]=True
        
    print('%d of %d streams survived' % (len(survivingStreamsIndices), len(survivingStreamsBoolVec)))
        
    return survivingStreamsBoolVec

# SUBSEGMENT TRACKS

def subsegment_alic(cwd):
    """ 
    This function runs anatomical-based segmentation on the whole ALIC tractogram
    :cwd:   path to subject-specific processed data
    """
    cwd = Path(cwd)

    # paths to input data
    track_files = {k: [cwd / i for i in v]
        for k, v in config.track_files.items()}
        
    # sanity check inputs
    to_check = [ config.parcellationPath, config.refT1Path]
    for side in ['left', 'right']:
        for tck in track_files[side]:
            to_check.append(tck)     
    for i in to_check:
        print(i)
        assert((cwd / i).is_file())
    
    # create output folder in ALIC_tractography
    os.makedirs(cwd / 'output', exist_ok=True)

    # load atlas-based segmentation - modified rACC mask
    parcellaton=nib.load( cwd / config.rACC_mod_aparc_aseg)

    # load Freesurfer labels
    lookupTable=config.freesurfer_lookup_table

    # perform inflate & deIsland of input parcellation
    inflated_atlas_file = cwd / config.saveFigDir / Path(Path(cwd / config.rACC_mod_aparc_aseg.stem).stem + '_inflated').with_suffix('.nii.gz')
    print(inflated_atlas_file)
    inflatedAtlas,deIslandReport,inflationReport= wmaPyTools.roiTools.preProcParc(parcellaton,deIslandBool=True,inflateIter=2,retainOrigBorders=False,maintainIslandsLabels=None,erodeLabels=[2,41])    
    nib.save(inflatedAtlas,filename=inflated_atlas_file)

    # convert fsl-format acpc to MNI xfm to mrtrix format
    acpc_to_mni_xfm_mrtrix = cwd / config.data_dir / 'acpc_to_mni_xfm_mrtrix.nii.gz'
    mni_to_acpc_xfm_mrtrix = cwd / config.data_dir / 'mni_to_acpc_xfm_mrtrix.nii.gz'
    convert_xfm_fsl_to_mrtrix(cwd / config.acpc_to_mni_xfm, acpc_to_mni_xfm_mrtrix, cwd / config.MNI_ref_image) #use original xfm (acpc_to_mni_xfm) to transform images from acpc to mni
    convert_xfm_fsl_to_mrtrix(cwd / config.mni_to_acpc_xfm, mni_to_acpc_xfm_mrtrix, cwd / config.parcellationPath) #use inverse xfm (mni_to_acpc_xfm) to transform centroids or tcks from acpc to mni

    # generate OCD response tract ROI
    ROI_list = {}
    for iSlice in config.coronal_slices_displayed_mm:
        ROI_list[iSlice] = ocd_response_tract_roi(cwd / config.ocd_response_tract_MNI, iSlice, dimension = "y")

    # create an table for streamline data
    column_labels = ['target', 'number_of_streamlines', 'percent_streamlines']
    tables = {key: pd.DataFrame(columns=column_labels) for key in ROI_list.keys()}

    # Main cell, do all the hard work
    for iSide in ['left', 'right']:
        for track_file in track_files[iSide]:

            # load & orient streamlines
                
            tck_oriented_file = cwd / config.saveFigDir / Path(track_file.stem + '_oriented').with_suffix('.tck')
            if tck_oriented_file.exists():
                print('oriented tck already exists. loading %s' % tck_oriented_file)
                tckIn=nib.streamlines.load(tck_oriented_file)
                streams = tckIn.streamlines
            else:
                print('Load tck %s' % track_file)
                tckIn=nib.streamlines.load(track_file)
                print("orienting streamlines")
                streams=wmaPyTools.streamlineTools.orientAllStreamlines(tckIn.streamlines)
                # do quickbundles (never mind, takes too long)
                # save oriented + bundled streams
                print('saving oriented tck %s' % tck_oriented_file)
                wmaPyTools.streamlineTools.stubbornSaveTractogram(streams,savePath=str(tck_oriented_file))
                
            parent_density_file = cwd / config.saveFigDir / Path(track_file.stem).with_suffix('.nii.gz')
            print('saving density map %s' % parent_density_file)
            save_density_map(streams, inflatedAtlas, parent_density_file)

            # calculate whole ALIC streamlines that overlap with OCD response tract
            #response_tract = nib.load(cwd / config.ocd_response_tract_acpc)

            for iTarget in targetLabels[iSide]:
                targetStr = lookupTable.loc[iTarget, 'LabelName:']
                out_file = cwd / config.saveFigDir / ('%s_%04d_%s' % (track_file.stem, iTarget, targetStr))
                print('Starting processing for %s' % out_file.stem)
                    
                # subsegment the streams and save the resulting density map and tck tractogram
                targetBool = save_streams_matching_target(streams, inflatedAtlas, lookupTable, iTarget, out_file,)

                # transform tck from acpc to MNI space
                output_tck_mni_path = cwd / config.saveFigDir / f'{out_file.stem}_mni.tck'
                tck_mni = apply_mrtrix_xfm(out_file.with_suffix('.tck'), output_tck_mni_path, mni_to_acpc_xfm_mrtrix) #we must use the inverse xfm for transfomring points and tcks

                # calculate the number of streamlines and percent streamlines for each target that overlap with OCD response tract
                for (iROI, value) in ROI_list.items(): #iROI is the mm slice, value is the nifti at that specific mm slice
                    tables[iROI].loc[targetStr] = [targetStr, *calculate_streams_ocd_response(tck_mni, value)]
        
    # save out streamline csv containging all targets for a particularly slice for a single subject 
    for (iROI, value) in tables.items():
        outfile = cwd / config.saveFigDir / f'{iROI}_OCD_response_tract_streams.csv'
        value.to_csv(outfile, index=False)


