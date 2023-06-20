#!/usr/bin/env python3
import alicpype as alic
from pathlib import Path

TEST_SUBJ = '103818'
TEST_ALIC_DIR = f'/home/udall-raid7/HCP_data/Data_Processing/3T_HCP_visit1'
TEST_HCP_DIR = '/home/udall-raid7/HCP_data/Data/3T_HCP_visit1'

def main():
    # call alicpype tasks run_subject
    alic.tasks.run_hcp_subject(
        TEST_SUBJ, TEST_HCP_DIR, TEST_ALIC_DIR)

if __name__ == '__main__':
    main()