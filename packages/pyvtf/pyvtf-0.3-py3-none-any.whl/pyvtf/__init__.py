#*****************************************************************
# terraform-provider-vcloud-director
# Copyright (c) 2017 VMware, Inc. All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
#*****************************************************************

from .plugin import PyPluginServer
from .plugin_stop import PyPluginClient

__VERSION__ = '0.3'


def start():
    ''' Function to start pyvtfplugin server'''
    server = PyPluginServer()
    server.serve()


def stop():
    ''' Function to stop pyvtfplugin server'''
    server = PyPluginClient()
    server.stop()


def get_status():
    ''' Function to get status of pyvtfplugin server'''
    server = PyPluginClient()
    if server.isRunning():
        return 'pyvtf server is running.'
    return 'pyvtf server is not running.'
