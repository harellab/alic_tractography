#!/usr/bin/env python3
"""
For each agrument, attempt to convert to vtk with the same base name
"""

import sys
from subprocess import check_call
from warnings import warn
from pathlib import Path

OVERWRITE = False

def tck2vtk(in_file):
    in_file = Path(in_file)
    assert(in_file.is_file())
    assert(in_file.suffix.lower() == '.tck')
    
    out_file = in_file.with_suffix('.vtk')

    cmd = ['apptainer', 'exec', 'docker://brainlife/mrtrix3:3.0.0',
		'tckconvert', str(in_file), str(out_file)]
    if OVERWRITE:
        cmd.append('-f')
    print(cmd)
    check_call(cmd)

def main():
    # parse args
    for arg in sys.argv:
        try:
            tck2vtk(arg)
        except Exception as e:
            warn(str(e))

if __name__ == '__main__':
    main()
