#!/usr/bin/env python3
from alicpype.centroids import make_centroids_summary
from pathlib import Path
import sys 
import numpy as np

TEST_ALIC_DIR = '/home/udall-raid7/HCP_data/Data_Processing/3T_HCP_visit1'
TEST_HCP_DIR = '/home/udall-raid7/HCP_data/Data/3T_HCP_visit1'

def main():
    """
    TODO
    """

    subject_list_file = Path(sys.argv[1]).expanduser().resolve()
    subject_list = np.loadtxt(subject_list_file, delimiter=',', dtype=str)

    make_centroids_summary(TEST_ALIC_DIR, subject_list)

if __name__ == '__main__':
    main()