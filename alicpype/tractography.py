#!/usr/bin/env python3
# description: generate whole ALIC tractogram

# SETUP
import os
from warnings import warn
from pathlib import Path
from subprocess import run

def generate_alic(cwd):
    cwd = Path(cwd)
    to_check = [ parcellationPath, refT1Path, lutPath, diffPath, bvalsPath, bvecsPath]
    for i in to_check:
        print(i)
        if not i.is_file():
            warn('%s doesn''t exist!' % str(i))


    # link indata to app-track_aLIC/indata
    src = '../indata' 
    dst = cwd/'app-track_aLIC/indata'
    os.symlink(src, dst)

    # run "main" app-track_aLIC script (command to run, environment, select cwd)
    env = {**os.environ, "APPTAINER_BIND": '/home'}
    run( './main', env = env, cwd = cwd/'app-track_aLIC')





