#!/usr/bin/env python3
# description: generate whole ALIC tractogram

# SETUP
import os
from warnings import warn
from pathlib import Path
from subprocess import run

from . import config

def generate_alic(cwd):
    cwd = Path(cwd)
    to_check = [ config.parcellationPath, config.refT1Path, config.lutPath, 
        config.diffPath, config.bvalsPath, config.bvecsPath]
    for i in to_check:
        abs_file = cwd / i
        if i.is_file():
            print(f'found {abs_file}')
        else:
            warn('%s doesn''t exist!' % str(abs_file))

    # link indata to app-track_aLIC/indata
    try:
        os.symlink('../indata' , cwd/'app-track_aLIC/indata')
    except FileExistsError:
        # if app-track_aLic/indata already exists, ignore the error
        pass

    # run "main" app-track_aLIC script (command to run, environment, select cwd)
    env = {**os.environ, "APPTAINER_BIND": '/home'}
    run( './main', env=env, cwd=cwd/'app-track_aLIC')
