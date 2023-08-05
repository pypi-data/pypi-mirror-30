#*****************************************************************
# terraform-provider-vcloud-director
# Copyright (c) 2017 VMware, Inc. All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
#*****************************************************************

import argparse
import pyvtf


def main():
    ''' main function '''
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', nargs='?', default='',
                        help='''to start/stop/status the terraform plugin server.\
                                Expected values are "start"/"stop"''')
    parser.add_argument('--version', action="store_true",
                        help='current version of pyvtf')

    args = parser.parse_args()

    if args.version:
        return pyvtf.__VERSION__

    if args.operation == "start":
        pyvtf.start()

    if args.operation == "stop":
        pyvtf.stop()

    if args.operation == "status":
        return pyvtf.get_status()
