#!/usr/bin/env python3
import alicpype as alic
from pathlib import Path
import sys 
import numpy as np

TEST_ALIC_DIR = '/home/udall-raid7/HCP_data/Data_Processing/3T_HCP_visit1'
TEST_HCP_DIR = '/home/udall-raid7/HCP_data/Data/3T_HCP_visit1'

def main():
    """
    Run OCD pipeline on a CSV-formatted list of subjects. Syntax is 
        main_batch_subjects.py subject_list.csv
    """
    subject_list_file = Path(sys.argv[1]).expanduser().resolve()
    subject_list = np.loadtxt(subject_list_file, delimiter=',', dtype=str)

    # call alicpype tasks run_subject on each subject in list
    for subject_id in subject_list:
        print(f'starting processing for subject {subject_id}')
        alic.tasks.run_hcp_subject(
            subject_id, TEST_HCP_DIR, TEST_ALIC_DIR)

if __name__ == '__main__':
    main()