#!/usr/bin/env python3
# description: build a slicer scene which transforms centroids from acpc to mni space

import os
import sys
import shutil
import argparse
import numpy as np


def parse_args(): #TODO
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'infile',
        help='input CSV-format file to read. Must contain 3 columns of '
            + '(R,A,S) coordinates, with a single header line.')
    parser.add_argument(
        '-o', '--output',
        #default=None,
        help='Path of CSV-format output file to write. Will be overwritten ' 
            + 'if it already exists.')
    parser.add_argument(
        '-t', '--transform',
        #default=None,
        help='path of ITK-format transform file.'
    )
    parser.add_argument(
        '--stayopen',
        default=False,
        action='store_true',
        help='Keep Slicer open when finished. Default False.'
    )
    args = parser.parse_args()
    #if args.output is None:
        #args.output = os.path.splitext(args.output)[0] + '.mrb'

    return args

def transform_points_csv(infile, transform, outfile):
    print(infile)
    print(transform)
    print(outfile)
    # load slicer transform (node) from file
    transform_node = slicer.util.loadTransform(transform)
    
    # load input csvs in original space
    inputarray = np.loadtxt(str(infile), delimiter=",", skiprows=1)
    # turn numpy array into fiducial list
    fiducial_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode") #creates an empty fiducial list
    slicer.util.updateMarkupsControlPointsFromArray(fiducial_node, inputarray, world = False) #insert input csv content into fiducial list

    # apply transform to fiducials
    fiducial_node.SetAndObserveTransformNodeID(transform_node.GetID())

    # harden the transform
    fiducial_node.HardenTransform()

    # convert fiducial list back to an array
    outputarray = slicer.util.arrayFromMarkupsControlPoints(fiducial_node, world=False)

    # save transformed array (R,A,S)
    np.savetxt(str(outfile), outputarray, delimiter=",", header="r,a,s")

def main():
    exit_status = 0 #doesn't do anything yet. need to catch errors
    args = parse_args()

    transform_points_csv(args.infile, args.transform, args.output)

    if not args.stayopen:
        exit(exit_status)

if __name__ == '__main__':
    main()