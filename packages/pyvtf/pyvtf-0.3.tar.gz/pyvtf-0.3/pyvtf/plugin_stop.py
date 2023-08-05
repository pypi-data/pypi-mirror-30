#*****************************************************************
# terraform-provider-vcloud-director
# Copyright (c) 2017 VMware, Inc. All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
#*****************************************************************

import grpc
from .proto import pyvcloudprovider_pb2 as pyvcloudprovider_pb2
from .proto import pyvcloudprovider_pb2_grpc as pyvcloudprovider_pb2_grpc


class PyPluginClient:
    def stop(self):
        # We need to build a health service to work with go-plugin
        print("stopRemote")
        try:
            channel = grpc.insecure_channel('127.0.0.1:1234')
            stub = pyvcloudprovider_pb2_grpc.PyVcloudProviderStub(channel)
            si = pyvcloudprovider_pb2.StopInfo()

            print("stopping")

            stub.StopPlugin(si)
            print("stop Remote OK")
        except grpc._channel._Rendezvous:
            print('grpc server is not running.')
        except Exception:
            print("Error occured")
            raise
