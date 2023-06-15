#!/usr/bin/env python3
# description: module runs through entire alicpype for a single subject

from pathlib import Path

# importing function from each script/submodules (ex. centroids.py)
from .externalio import import_hcp_subject
from .tractography import generate_alic
from .subsegment import subsegment_alic
from .heatmap import generate_heatmap
from .centroids import generate_centroid
from .slicer import generate_slicer

def run_hcp_subject(subject, hcp_root, alicpype_root, selection=None ):
    
    #TODO:modify as necessary
    """ 
    Run the pipeline steps "a la carte". Each step can be turned on or off.
    Available steps (in order of execution) are:
        '7T_convert':   Convert dicoms in Dicom/sub-{subject}/ses-7T to 
                        BIDS-compatible NIFTIs
        'CT_convert':   Convert dicoms in Dicom/sub-{subject}/ses-{CT_session}
                        to BIDS-compatible NIFTIS for each CT session.
        'Diffusion':    Run legacy DiffusionAnalysisTopup script
        'T1_proc':      Run legacy HCP-based T1 processing
        '7T_bet':       Run brain extraction on 7T T2 and T1
        'STN_segmentation'  Run automated STN segmentation
        'GP_segmentation'   Run automated GP segmentation
        '7T_T2_reg':    Register 7T T2s to 7T T1 and apply to any segmentations
                        in T2 spaces.
        'apply_7T_reg': Transform segmentations from 7T T2 
                        space(s) to 7T T1
        '7T_swi_reg':   (naming is slightly broken, do this manually) Register 7T SWIs to 7T T1
        'apply_swi_reg': Transform segmentations from 7T SWI space(s) to 7T T1
        '3T_bet':       Run brain extraction on 3T T1 #TODO add other 3T scans
        '7T_3T_reg':    (unavailable) Register 7T T1 to 3T T1
        'ct_preproc':   Run CT preprocessing (ctmask, hbins)
        'electrode':    Estimate electrode location
        '7T_ct_reg':    Register 7T T1 to CT session(s)
        'apply_7T_ct_reg': Transform images and segmentations from 7T to 
                        CT space.
        '3T_ct_reg':    Register 3T T1 to CT session(s)
        'full_scene':   Build full scene, with all available coregistered data
        'lite_scene':   (unavailable) Build 'lite' scene, with only 7T T1, 
                        electrodes, and target

    :param subject:     Subject ID to process.
    :type subject:      str
    :param dbs_root:    Path of DBS data folder containing Dicom, Nifti, 
                        and dbspype subfolders.
    :type dbs_root:     String or Path-like
    :param electrode:   Electrode model. Default is 'auto', but is not 
                        recommended as this takes much longer to run 
                        and sometimes guesses wrong.
    :type electrode:    string, Optional.
    :param selection:   Pieces of pipeline to run. if a dict is TODO
    """

    # copy and paste data into input folders (externalio.py)
    alicpype_root = Path(alicpype_root) #convert datatype to path
    subject = str(subject)
    cwd = alicpype_root / subject / 'OCD_pipeline'
    import_hcp_subject(subject,hcp_root,alicpype_root)

    # register images into acpc space (registration.py)
    # data already registered
    # register_acpc()

    # generate whole ALIC tractography (tractography.py)
    generate_alic(cwd)

    # generate split rACC ROI (divideracc.py)
    split_racc(subject, cwd)

    # subsegment ALIC based on PFC ROIs (subsegment.py)
    subsegment_alic(subject, cwd)

    # generate subsegmented heatmaps (heatmap.py)
    generate_heatmap(subject, cwd)

    # calculate centroids of each subsegmented ALIC heatmap (centoids.py)
    generate_centroid(subject, cwd)

    # generate a slicer scene containing heatmaps and centroids (slicer.py)
    generate_slicer(subject, cwd)
