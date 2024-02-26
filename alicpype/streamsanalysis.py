#!/usr/bin/env python3
# description: concatenate all subject streamline OCD response tract data into 8 csvs (number of streamlines, perecent streamlines iterated over 4 coronal slices)


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

# load Freesurfer labels
lookupTable=config.freesurfer_lookup_table

def run_streamline_analysis(data_dir, subject_list):
    data_dir = Path(data_dir) #defines data_dir as a path
    #iterate over subjects and slices
    for iSlice in config.coronal_slices_displayed_mm: #iterate over slice
        #columns = ['subject', ]
        #for iSide in ['left', 'right']:
            #for iTarget in targetLabels[iSide]:
                #targetStr = lookupTable.loc[iTarget, 'LabelName:']
                #columns.append(str(iTarget)) #append each target label to column headers
        #table = pd.DataFrame(columns=columns, ) #generate an empty data frame
        #table.set_index('subject', inplace=True) #set subject column for indexing
        number_data = {lookupTable.loc[i, 'LabelName:']:{} for i in [*targetLabels['left'], *targetLabels['right']]}
        percent_data = number_data.copy()
        
        for iSubject in subject_list: #iterate over subjects
            inputcsvpath = data_dir / iSubject / 'OCD_pipeline' / 'output' / f'{iSlice}_OCD_response_tract_streams.csv'
            inputcsv = np.loadtxt(inputcsvpath, delimiter=",", skiprows=1, dtype=str)
            #table = table.append({'subject': iSubject}, ignore_index=True, ) #for iSubject append subjectID in subject columnn of table
            for iRow in inputcsv: 
                number_data[iRow[0]][iSubject] = iRow[1]
                percent_data[iRow[0]][iSubject] = iRow[2]
        number_table = pd.DataFrame(number_data) #generate table containing number of streamline data
        percent_table = pd.DataFrame(percent_data) #generate table containing percent streamline data

        #save out summary csvs (2 for each slice)
        number_table.to_csv(data_dir / 'output' / f'number_streamlines_summary_{iSlice}.csv', index=True)
        percent_table.to_csv(data_dir / 'output' / f'percent_streamlines_summary_{iSlice}.csv', index=True)



