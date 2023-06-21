#!/usr/bin/env python3
# description: generate subsegmented ALIC pathways

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
#import random

import pandas as pd
import wmaPyTools.roiTools
import wmaPyTools.analysisTools
import wmaPyTools.segmentationTools
import wmaPyTools.streamlineTools
import wmaPyTools.visTools

#dipy
from dipy.tracking.utils import reduce_labels
from dipy.tracking import utils
from dipy.tracking.utils import density_map

from .config import targetLabels

# Define function to convert tck to vtk
def tck2vtk(in_file, overwrite=True):
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

# SUBSEGMENT TRACKS
def subsegment_alic(cwd):
    cwd = Path(cwd)

    #paths to input data
    track_files = {k: cwd / v for k, v in config.track_files.items()}
    
    # sanity check inputs
    to_check = [ config.parcellationPath, config.refT1Path, config.lutPath]
    for side in ['left', 'right']:
        for tck in track_files[side]:
            to_check.append(tck)     
    for i in to_check:
        print(i)
        assert((cwd / i).is_file())

    # define functions to generate tck for target

    def get_streams_matching_target(streams, atlas, target):
        target_mask=wmaPyTools.roiTools.multiROIrequestToMask(atlas,target)
        # return boolean mask for stream selection
        return wmaPyTools.segmentationTools.segmentTractMultiROI(streams, 
                        [target_mask,], 
                        [True,], 
                        ['either_end',]) 
        
    def save_density_map(streams, ref_img, out_file):
        density=utils.density_map(streams, ref_img.affine, ref_img.shape)
        densityNifti = nib.nifti1.Nifti1Image(density, ref_img.affine, ref_img.header)
        nib.save(densityNifti, out_file)
        
    def save_streams_matching_target(streams, atlas, lookupTable, target, out_file):
        strTarget = lookupTable.loc[target, 'LabelName:']
        print('target label is: %s (%s)' % (target, strTarget))
        #out_file = Path(save_dir) / ('track_%04d_%s' % (target,strTarget)) #no file extension yet, add it later
        print(out_file)
        # get boolean vector of matching streams
        targetBool = get_streams_matching_target(streams, atlas, target)
        streams = streams[targetBool]
        
        #dipy quickbundles
        streams = streams[bundle(streams)]
        
        #save *.tck tractogram
        wmaPyTools.streamlineTools.stubbornSaveTractogram(streams,
            savePath=str(out_file.with_suffix('.tck')))
        # save nifti density map
        save_density_map(streams, atlas, out_file.with_suffix('.nii.gz'))

        # convert tcks to vtks
        tck2vtk(out_file.with_suffix('.tck'))
        return targetBool
        
    #targetBool = save_streams_matching_target(streams,inflatedAtlas, lookupTable, iTarget, saveFigDir)
    #wmaPyTools.streamlineTools.stubbornSaveTractogram(streams[targetBool], 
    #    savePath=str(saveFigDir / '1002_test.tck' )

    #apply the initial culling, to remove extraneous streamlines 
    #first requires doing a DIPY quickbundling
    def bundle(streams):
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

    # load atlas-based segmentation - modified rACC mask (Dan calls it a parcellation)
    parcellaton=nib.load( cwd / config.rACC_mod_aparc_aseg)

    # load Freesurfer labels
    lookupTable=pd.read_csv(cwd / config.lutPath,index_col='#No.')

    #perform inflate & deIsland of input parcellation
    inflated_atlas_file = cwd / config.saveFigDir / Path(Path(cwd / config.rACC_mod_aparc_aseg.stem).stem + '_inflated').with_suffix('.nii.gz')
    print(inflated_atlas_file)
    inflatedAtlas,deIslandReport,inflationReport= wmaPyTools.roiTools.preProcParc(parcellaton,deIslandBool=True,inflateIter=2,retainOrigBorders=False,maintainIslandsLabels=None,erodeLabels=[2,41])    
    nib.save(inflatedAtlas,filename=inflated_atlas_file)

    #Main cell, do all the hard work

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
                #streams = streams[bundle(streams)]
                # save oriented + bundled streams
                print('saving oriented tck %s' % tck_oriented_file)
                wmaPyTools.streamlineTools.stubbornSaveTractogram(streams,savePath=str(tck_oriented_file))
            
            parent_density_file = cwd / config.saveFigDir / Path(track_file.stem).with_suffix('.nii.gz')
            print('saving density map %s' % parent_density_file)
            save_density_map(streams, inflatedAtlas, parent_density_file)
            
            for iTarget in targetLabels[iSide]:
                targetStr = lookupTable.loc[iTarget, 'LabelName:']
                out_file = cwd / config.saveFigDir / ('%s_%04d_%s' % (track_file.stem, iTarget, targetStr))
                print('Starting processing for %s' % out_file.stem)
                
                # subsegment the streams and save the resulting density map and tck tractogram
                targetBool = save_streams_matching_target(streams, inflatedAtlas, lookupTable, iTarget, out_file,)

                    
