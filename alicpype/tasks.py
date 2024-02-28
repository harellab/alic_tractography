#!/usr/bin/env python3
# description: runs through all subject-specific processing steps

from pathlib import Path

# importing function from each script/submodules (ex. centroids.py)
from .externalio import import_hcp_subject, import_7T_hcp_subject, import_ocd_subject
from .tractography import generate_alic
from .splitracc import split_racc
from .subsegment import subsegment_alic
from .centroids import generate_centroid

def run_hcp_subject(subject, hcp_root, alicpype_root, selection=None ):
    """ 
    This function runs through all subject-specific processing steps for 3T HCP data. The available steps (in order of execution) are:
    import_hcp_subject:     copy inputs from 3T HCP dataset
    generate_alic:          generate whole ALIC tractogram
    split_racc:             split rACC into dorsal and ventral components
    subsegment_alic:        anatomically-based segmentation of the ALIC
    generate_centroid:      calculate centroids from each segmented ALIC density map

    :subject:               subject ID
    :hcp_root:              path to HCP-style dataset
    :alicpype_root:         path to processed dataset from ALIC_tractography pipeline
    """

    hcp_root = Path(hcp_root)

    # copy and paste data into input folders (externalio.py)
    alicpype_root = Path(alicpype_root) #convert datatype to path
    subject = str(subject)
    cwd = alicpype_root / subject / 'OCD_pipeline'
    import_hcp_subject(subject,hcp_root,cwd)

    # generate whole ALIC tractography (tractography.py)
    generate_alic(cwd)

    # generate split rACC ROI (divideracc.py)
    split_racc(cwd)

    # subsegment ALIC based on PFC ROIs (subsegment.py)
    subsegment_alic(cwd)

    # calculate centroids of each subsegmented ALIC heatmap (centroids.py)
    generate_centroid(cwd)

def run_7T_hcp_subject (subject, hcp_root, alicpype_root, selection=None):
    """ 
    This function runs through all subject-specific processing steps for 7T HCP data. The available steps (in order of execution) are:
    import_7T_hcp_subject:      copy inputs from 7T HCP dataset
    generate_alic:              generate whole ALIC tractogram
    split_racc:                 split rACC into dorsal and ventral components
    subsegment_alic:            anatomically-based segmentation of the ALIC
    generate_centroid:          calculate centroids from each segmented ALIC density map

    :subject:                   subject ID
    :hcp_root:                  path to HCP-style dataset
    :alicpype_root:             path to processed dataset from ALIC_tractography pipeline
    """
    
    # copy and paste data into input folders (externalio.py)
    alicpype_root = Path(alicpype_root) #convert datatype to path
    subject = str(subject)
    cwd = alicpype_root / subject / 'OCD_pipeline'
    import_7T_hcp_subject(subject,hcp_root,cwd)

    # generate whole ALIC tractography (tractography.py)
    generate_alic(cwd)

    # generate split rACC ROI (divideracc.py)
    split_racc(cwd)

    # subsegment ALIC based on PFC ROIs (subsegment.py)
    subsegment_alic(cwd)

    # calculate centroids from each segmented ALIC density map (centroids.py)
    generate_centroid(cwd)

def run_ocd_subject (subject, input_data_root, alicpype_root, selection=None):
    """ 
    This function runs through all subject-specific processing steps for 7T data from OCD patients. The available steps (in order of execution) are:
    import_ocd_subject:         copy inputs from 7T OCD dataset
    generate_alic:              generate whole ALIC tractogram
    split_racc:                 split rACC into dorsal and ventral components
    subsegment_alic:            anatomically-based segmentation of the ALIC
    generate_centroid:          calculate centroids from each segmented ALIC density map

    :subject:                   subject ID
    :input_data_root:           path to OCD patient dataset
    :alicpype_root:             path to processed dataset from ALIC_tractography pipeline
    """

    # copy and paste data into input folders (externalio.py)
    alicpype_root = Path(alicpype_root) #convert datatype to path
    subject = str(subject)
    cwd = alicpype_root / subject / 'OCD_pipeline'
    import_ocd_subject(subject,input_data_root,cwd)

    # generate whole ALIC tractography (tractography.py)
    generate_alic(cwd)

    # generate split rACC ROI (divideracc.py)
    split_racc(cwd)

    # subsegment ALIC based on PFC ROIs (subsegment.py)
    subsegment_alic(cwd)

    # calculate centroids of each subsegmented ALIC heatmap (centroids.py)
    generate_centroid(cwd)