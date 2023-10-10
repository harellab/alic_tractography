#!/usr/bin/env python3

import unittest
from pathlib import Path

from alicpype import config

class TestSlicerTransformPoints(unittest.TestCase):
    def test_ouptuts_passed(self):
        SLICER_CMD = Path('/Applications/Slicer.app/Contents/MacOS/Slicer')#TODO change to linux location
        assert(SLICER_CMD.is_file())
        cmd = [str(SLICER_CMD),
                        '--no-main-window',
                        '--python-script', str(config.slicer_apply_xfm_script),
                        '--output', 'out.csv',
                        '--transform', 'transform.nii.gz',
                        'input.csv'],