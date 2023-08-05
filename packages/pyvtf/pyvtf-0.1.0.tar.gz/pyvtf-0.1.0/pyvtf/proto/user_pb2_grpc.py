# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from ..proto import user_pb2 as proto_dot_user__pb2


class UserStub(object):
    # missing associated documentation comment in .proto file
    pass

    def __init__(self, channel):
        """Constructor.

    Args:
      channel: A grpc.Channel.
    """
        self.Create = channel.unary_unary(
            '/proto.User/Create',
            request_serializer=proto_dot_user__pb2.CreateUserInfo.
            SerializeToString,
            response_deserializer=proto_dot_user__pb2.CreateUserResult.
            FromString,
        )
        self.Delete = channel.unary_unary(
            '/proto.User/Delete',
            request_serializer=proto_dot_user__pb2.DeleteUserInfo.
            SerializeToString,
            response_deserializer=proto_dot_user__pb2.DeleteUserResult.
            FromString,
        )
        self.Read = channel.unary_unary(
            '/proto.User/Read',
            request_serializer=proto_dot_user__pb2.ReadUserInfo.
            SerializeToString,
            response_deserializer=proto_dot_user__pb2.ReadUserResult.
            FromString,
        )
        self.Update = channel.unary_unary(
            '/proto.User/Update',
            request_serializer=proto_dot_user__pb2.UpdateUserInfo.
            SerializeToString,
            response_deserializer=proto_dot_user__pb2.UpdateUserResult.
            FromString,
        )


class UserServicer(object):
    # missing associated documentation comment in .proto file
    pass

    def Create(self, request, context):
        """create a User
    """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Delete(self, request, context):
        """delete a User
    """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Read(self, request, context):
        """Read User
    """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Update(self, request, context):
        """Update User
    """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_UserServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'Create':
        grpc.unary_unary_rpc_method_handler(
            servicer.Create,
            request_deserializer=proto_dot_user__pb2.CreateUserInfo.FromString,
            response_serializer=proto_dot_user__pb2.CreateUserResult.
            SerializeToString,
        ),
        'Delete':
        grpc.unary_unary_rpc_method_handler(
            servicer.Delete,
            request_deserializer=proto_dot_user__pb2.DeleteUserInfo.FromString,
            response_serializer=proto_dot_user__pb2.DeleteUserResult.
            SerializeToString,
        ),
        'Read':
        grpc.unary_unary_rpc_method_handler(
            servicer.Read,
            request_deserializer=proto_dot_user__pb2.ReadUserInfo.FromString,
            response_serializer=proto_dot_user__pb2.ReadUserResult.
            SerializeToString,
        ),
        'Update':
        grpc.unary_unary_rpc_method_handler(
            servicer.Update,
            request_deserializer=proto_dot_user__pb2.UpdateUserInfo.FromString,
            response_serializer=proto_dot_user__pb2.UpdateUserResult.
            SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'proto.User', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler, ))
