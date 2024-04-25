#!/usr/bin/env python3
#!/usr/bin/env conda run -p /opt/local/dbs/bin/mambaforge/envs/DBSv1p4 python
# description: run ALIC_tractography pipeline on an individual subject with 3T dMRI

import alicpype as alic
from pathlib import Path
import sys 

#TODO: edit so paths are not hard coded
TEST_ALIC_DIR = '/home/udall-raid7/HCP_data/Data_Processing/3T_HCP_retest'
TEST_HCP_DIR = '/home/udall-raid7/HCP_data/Data/3T_HCP_retest'

def main():
    """
    Run OCD pipeline on a single subject. Syntax is 
        main_run_subject.py subject_id
    """
    subject_id = sys.argv[1]

    # call alicpype tasks run_subject
    alic.tasks.run_hcp_subject(
        subject_id, TEST_HCP_DIR, TEST_ALIC_DIR)

if __name__ == '__main__':
    main()