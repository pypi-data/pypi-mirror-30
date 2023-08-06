#!/usr/bin/env python

'''
Cisco Copyright 2018
Author: Vamsi Kalapala <vakalapa@cisco.com>

FILENAME: RUN.PY


'''
import argparse
from csr_tvnet.csr_tvnet import csr_transit


def main(args):
    '''
    Main function involves taking care of:
             - Creating a local copy of the Custom Data file
            - Parsing the Custom data and creating data structure
    '''
    tvnet = csr_transit(customDataFileName=args.decoded)
    tvnet.configure_transit_vnet()


if __name__ == '__main__':  # pragma: no cover

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d',
        '--decoded',
        type=str,
        default="sampledecodedCustomData",
        help='File location for the decoded custom data')
    args = parser.parse_args()
    main(args)
