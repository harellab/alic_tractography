#!/usr/bin/env python3
#!/usr/bin/env conda run -p /opt/local/dbs/bin/mambaforge/envs/DBSv1p4 python
# description: run ALIC_tractography pipeline for a batch of subjects with 7T dMRI from OCD subjects

import alicpype as alic
from pathlib import Path
import sys 
import numpy as np
from traceback import print_exc

TEST_ALIC_DIR = Path('/home/udall-raid7/DBS_OCD_Processing')
TEST_HCP_DIR = Path('/home/udall-raid5/bids-data/OCD_data/')

def main():
    """
    Run OCD pipeline on a CSV-formatted list of subjects. Syntax is 
        main_batch_subjects.py subject_list.csv
    """
    subject_list_file = Path(sys.argv[1]).expanduser().resolve()
    subject_list = np.loadtxt(subject_list_file, delimiter=',', dtype=str)
    print(subject_list)

    # call alicpype tasks run_subject on each subject in list
    for subject_id in subject_list:
        print(f'starting processing for subject {subject_id}')
        #skip subject if error out
        try:
            alic.tasks.run_ocd_subject(
                subject_id, TEST_HCP_DIR, TEST_ALIC_DIR)
        except Exception as e:
            print(f'encountered an error when running {subject_id}')
            print_exc()

if __name__ == '__main__':
    main()
