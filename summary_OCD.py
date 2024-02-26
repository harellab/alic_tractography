#!/usr/bin/env python3
from alicpype.centroids import make_centroids_summary
from pathlib import Path
import sys 
import numpy as np

#TODO: edit so not hard coded paths
TEST_ALIC_DIR =Path('/home/udall-raid7/DBS_OCD_Processing') # path to project-specific data processing directory
#TEST_HCP_DIR = Path('/home/udall-raid5/bids-data/OCD_data/') # path to raw data directory

def main():
    """
    TODO
    """

    subject_list_file = Path(sys.argv[1]).expanduser().resolve()
    subject_list = np.loadtxt(subject_list_file, delimiter=',', dtype=str)

    make_centroids_summary(TEST_ALIC_DIR, subject_list)

if __name__ == '__main__':
    main()