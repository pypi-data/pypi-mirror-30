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
    parser.add_argument('operation',
                        help='''to start/stop the terraform plugin server.\
                                Expected values are "start"/"stop"''')
    args = parser.parse_args()

    if args.operation == "start":
        pyvtf.start()
    elif args.operation == "stop":
        pyvtf.stop()
