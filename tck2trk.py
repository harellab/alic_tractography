#!/usr/bin/env python3
"""
For each agrument, attempt to convert to vtk with the same base name
"""

import sys
import json
import shutil
from subprocess import check_call
from warnings import warn
from pathlib import Path

OVERWRITE = False
app_tck_to_trk_dir = Path('/opt/local/dbs/bin/app-convert-tck-to-trk')
config_json_file = app_tck_to_trk_dir/'config.json'
main_file = app_tck_to_trk_dir/'main'

def tck2trk(in_file, dwi_file):
    in_file = Path(in_file)
    dwi_file = Path(dwi_file)
    assert(in_file.is_file())
    assert(in_file.suffix.lower() == '.tck')
    assert(dwi_file.is_file())
    
    out_file = in_file.with_suffix('.trk')

    write_config(in_file, dwi_file)
    #TODO: write the correct config function

    # make sure to set $APPTAINER_BIND before running. for instance:
    # export APPTAINER_BIND=/home,${APPTAINER_BIND}
    cmd = [str(main_file)]

    print(cmd)
    check_call(cmd, cwd = app_tck_to_trk_dir)
    shutil.move(app_tck_to_trk_dir/'trk/track.trk',out_file)

def write_config(tck_file, dwi_file):
    in_files = {'tck': str(tck_file),
                'dwi': str(dwi_file)}
    with open(config_json_file, 'w') as f:
        json.dump(in_files, f)

def main():
    # parse args
    dwi_file = sys.argv[1]
    for arg in sys.argv[2:]:
        try:
            tck2trk(arg,dwi_file)
        except Exception as e:
            warn(str(e))

if __name__ == '__main__':
    main()
