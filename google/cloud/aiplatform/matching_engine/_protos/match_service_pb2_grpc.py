# -*- coding: utf-8 -*-

# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
from google.cloud.aiplatform.matching_engine._protos import match_service_pb2

import grpc


class MatchServiceStub(object):
  """MatchService is a Google managed service for efficient vector similarity

    search at scale.
    """

  def __init__(self, channel):
    """Constructor.

        Args:
            channel: A grpc.Channel.
    """
    self.Match = channel.unary_unary(
        "/google.cloud.aiplatform.container.v1beta1.MatchService/Match",
        request_serializer=match_service_pb2.MatchRequest.SerializeToString,
        response_deserializer=match_service_pb2.MatchResponse.FromString,
    )
    self.BatchMatch = channel.unary_unary(
        "/google.cloud.aiplatform.container.v1beta1.MatchService/BatchMatch",
        request_serializer=match_service_pb2.BatchMatchRequest
        .SerializeToString,
        response_deserializer=match_service_pb2.BatchMatchResponse.FromString,
    )


class MatchServiceServicer(object):
  """MatchService is a Google managed service for efficient vector similarity

    search at scale.
    """

  def Match(self, request, context):
    """Returns the nearest neighbors for the query.

    If it is a sharded
        deployment, calls the other shards and aggregates the responses.
        """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details("Method not implemented!")
    raise NotImplementedError("Method not implemented!")

  def BatchMatch(self, request, context):
    """Returns the nearest neighbors for batch queries.

    If it is a sharded
        deployment, calls the other shards and aggregates the responses.
        """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details("Method not implemented!")
    raise NotImplementedError("Method not implemented!")


def add_MatchServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      "Match":
          grpc.unary_unary_rpc_method_handler(
              servicer.Match,
              request_deserializer=match_service_pb2.MatchRequest.FromString,
              response_serializer=match_service_pb2.MatchResponse
              .SerializeToString,
          ),
      "BatchMatch":
          grpc.unary_unary_rpc_method_handler(
              servicer.BatchMatch,
              request_deserializer=match_service_pb2.BatchMatchRequest
              .FromString,
              response_serializer=match_service_pb2.BatchMatchResponse
              .SerializeToString,
          ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      "google.cloud.aiplatform.container.v1beta1.MatchService",
      rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class MatchService(object):
  """MatchService is a Google managed service for efficient vector similarity

    search at scale.
    """

  @staticmethod
  def Match(
      request,
      target,
      options=(),
      channel_credentials=None,
      call_credentials=None,
      insecure=False,
      compression=None,
      wait_for_ready=None,
      timeout=None,
      metadata=None,
  ):
    return grpc.experimental.unary_unary(
        request,
        target,
        "/google.cloud.aiplatform.container.v1beta1.MatchService/Match",
        match_service_pb2.MatchRequest.SerializeToString,
        match_service_pb2.MatchResponse.FromString,
        options,
        channel_credentials,
        insecure,
        call_credentials,
        compression,
        wait_for_ready,
        timeout,
        metadata,
    )

  @staticmethod
  def BatchMatch(
      request,
      target,
      options=(),
      channel_credentials=None,
      call_credentials=None,
      insecure=False,
      compression=None,
      wait_for_ready=None,
      timeout=None,
      metadata=None,
  ):
    return grpc.experimental.unary_unary(
        request,
        target,
        "/google.cloud.aiplatform.container.v1beta1.MatchService/BatchMatch",
        match_service_pb2.BatchMatchRequest.SerializeToString,
        match_service_pb2.BatchMatchResponse.FromString,
        options,
        channel_credentials,
        insecure,
        call_credentials,
        compression,
        wait_for_ready,
        timeout,
        metadata,
    )
