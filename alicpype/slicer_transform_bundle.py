#!/usr/bin/env python3
# description: transform fiber bundles within 3D Slicer

import os
import sys
import shutil
import argparse
import numpy as np

def parse_args():
    """ 
    This function interprets terminal input and returns corresponding python variables.
    
    """
    parser = argparse.ArgumentParser(
        prog='slicer_transform_bundle.py',
        description='transforms fiber bundles within 3D Slicer')
    parser.add_argument(
        'infile',
        help='input fiber bundle in vtk format in native space')
    parser.add_argument(
        '-o', '--output',
        #default=None,
        help='output fiber bundle in vtk format in transformed space')
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

# transform fiber bundle from ACPC to DTI space
def transform_fiber_bundle(infile, transform, outfile):
    """ 
    This function transforms csv containing centroids to 3D coordinates

    :infile:                                               input fiber bundle in original space
    :transform:                                            transform file from original to transformed space
    :outfile:                                              output fiber bundle in transformed space
    """

    print(infile)
    print(transform)
    print(outfile)
    # load slicer transform (node) from file
    transform_node = slicer.util.loadTransform(transform)
    transform_node.Inverse()
    
    # load and get fiber bundle node
    fiber_node = slicer.util.loadFiberBundle(infile)
    print(fiber_node)
    #fiber_node = slicer.util.getNode(infile)

    # apply transform to fiber bundle
    fiber_node.SetAndObserveTransformNodeID(transform_node.GetID())

    # harden the transform
    fiber_node.HardenTransform()

    # uncompress node (convert from binary to ascii format)
    fiber_node.GetStorageNode().SetUseCompression(0)

    # save out fiber bundles in transformed space
    slicer.util.saveNode(fiber_node, outfile)

def main():
    """
    This function parses command line arguments and passes them to transform_fiber_bundle

    """
    exit_status = 0 # doesn't do anything yet. need to catch errors
    args = parse_args()

    transform_fiber_bundle(args.infile, args.transform, args.output)

    if not args.stayopen:
        exit(exit_status)

if __name__ == '__main__':
    main()