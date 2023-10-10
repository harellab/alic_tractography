#!/usr/bin/env python3
# description: build a slicer scene which transforms centroids from acpc to mni space

import os
import sys
import shutil
from pathlib import Path
import argparse

def parse_args(): #TODO
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'infile',
        help='input CSV-format file to read. Must contain 3 columns of '
            + '(R,A,S) coordinates, with a single header line.')
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='Path of CSV-format output file to write. Will be overwritten ' 
            + 'if it already exists.')
    parser.add_argument(
        '-t', '--transform',
        default=None,
        help='path of ITK-format transform file.'
    )
    parser.add_argument(
        '--stayopen',
        default=False,
        action='store_true',
        help='Keep Slicer open when finished. Default False.'
    )
    args = parser.parse_args()
    if args.output is None:
        args.output = os.path.splitext(args.output)[0] + '.mrb'

    return args

def transform_points_csv(infile, transform, outfile):
    print(infile)
    print(transform)
    print(outfile)
    pass #TODO

def main():
    exit_status = 0 #doesn't do anything yet. need to catch errors
    args = parse_args()

    transform_points_csv(args.infile, args.transform, args.output)

    if not args.stayopen:
        exit(exit_status)

if __name__ == '__main__':
    main()