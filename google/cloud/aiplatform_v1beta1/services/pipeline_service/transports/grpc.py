# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
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

from typing import Callable, Dict

from google.api_core import grpc_helpers  # type: ignore
from google.api_core import operations_v1  # type: ignore
from google.auth import credentials  # type: ignore

import grpc  # type: ignore

from google.cloud.aiplatform_v1beta1.types import pipeline_service
from google.cloud.aiplatform_v1beta1.types import training_pipeline
from google.cloud.aiplatform_v1beta1.types import (
    training_pipeline as gca_training_pipeline,
)
from google.longrunning import operations_pb2 as operations  # type: ignore
from google.protobuf import empty_pb2 as empty  # type: ignore

from .base import PipelineServiceTransport


class PipelineServiceGrpcTransport(PipelineServiceTransport):
    """gRPC backend transport for PipelineService.

    A service for creating and managing AI Platform's pipelines.

    This class defines the same methods as the primary client, so the
    primary client can load the underlying transport implementation
    and call it.

    It sends protocol buffers over the wire using gRPC (which is built on
    top of HTTP/2); the ``grpcio`` package must be installed.
    """

    def __init__(
        self,
        *,
        host: str = "aiplatform.googleapis.com",
        credentials: credentials.Credentials = None,
        channel: grpc.Channel = None
    ) -> None:
        """Instantiate the transport.

        Args:
            host (Optional[str]): The hostname to connect to.
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
                This argument is ignored if ``channel`` is provided.
            channel (Optional[grpc.Channel]): A ``Channel`` instance through
                which to make calls.
        """
        # Sanity check: Ensure that channel and credentials are not both
        # provided.
        if channel:
            credentials = False

        # Run the base constructor.
        super().__init__(host=host, credentials=credentials)
        self._stubs = {}  # type: Dict[str, Callable]

        # If a channel was explicitly provided, set it.
        if channel:
            self._grpc_channel = channel

    @classmethod
    def create_channel(
        cls,
        host: str = "aiplatform.googleapis.com",
        credentials: credentials.Credentials = None,
        **kwargs
    ) -> grpc.Channel:
        """Create and return a gRPC channel object.
        Args:
            address (Optionsl[str]): The host for the channel to use.
            credentials (Optional[~.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify this application to the service. If
                none are specified, the client will attempt to ascertain
                the credentials from the environment.
            kwargs (Optional[dict]): Keyword arguments, which are passed to the
                channel creation.
        Returns:
            grpc.Channel: A gRPC channel object.
        """
        return grpc_helpers.create_channel(
            host, credentials=credentials, scopes=cls.AUTH_SCOPES, **kwargs
        )

    @property
    def grpc_channel(self) -> grpc.Channel:
        """Create the channel designed to connect to this service.

        This property caches on the instance; repeated calls return
        the same channel.
        """
        # Sanity check: Only create a new channel if we do not already
        # have one.
        if not hasattr(self, "_grpc_channel"):
            self._grpc_channel = self.create_channel(
                self._host, credentials=self._credentials,
            )

        # Return the channel from cache.
        return self._grpc_channel

    @property
    def operations_client(self) -> operations_v1.OperationsClient:
        """Create the client designed to process long-running operations.

        This property caches on the instance; repeated calls return the same
        client.
        """
        # Sanity check: Only create a new client if we do not already have one.
        if "operations_client" not in self.__dict__:
            self.__dict__["operations_client"] = operations_v1.OperationsClient(
                self.grpc_channel
            )

        # Return the client from cache.
        return self.__dict__["operations_client"]

    @property
    def create_training_pipeline(
        self,
    ) -> Callable[
        [pipeline_service.CreateTrainingPipelineRequest],
        gca_training_pipeline.TrainingPipeline,
    ]:
        r"""Return a callable for the create training pipeline method over gRPC.

        Creates a TrainingPipeline. A created
        TrainingPipeline right away will be attempted to be run.

        Returns:
            Callable[[~.CreateTrainingPipelineRequest],
                    ~.TrainingPipeline]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "create_training_pipeline" not in self._stubs:
            self._stubs["create_training_pipeline"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.PipelineService/CreateTrainingPipeline",
                request_serializer=pipeline_service.CreateTrainingPipelineRequest.serialize,
                response_deserializer=gca_training_pipeline.TrainingPipeline.deserialize,
            )
        return self._stubs["create_training_pipeline"]

    @property
    def get_training_pipeline(
        self,
    ) -> Callable[
        [pipeline_service.GetTrainingPipelineRequest],
        training_pipeline.TrainingPipeline,
    ]:
        r"""Return a callable for the get training pipeline method over gRPC.

        Gets a TrainingPipeline.

        Returns:
            Callable[[~.GetTrainingPipelineRequest],
                    ~.TrainingPipeline]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_training_pipeline" not in self._stubs:
            self._stubs["get_training_pipeline"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.PipelineService/GetTrainingPipeline",
                request_serializer=pipeline_service.GetTrainingPipelineRequest.serialize,
                response_deserializer=training_pipeline.TrainingPipeline.deserialize,
            )
        return self._stubs["get_training_pipeline"]

    @property
    def list_training_pipelines(
        self,
    ) -> Callable[
        [pipeline_service.ListTrainingPipelinesRequest],
        pipeline_service.ListTrainingPipelinesResponse,
    ]:
        r"""Return a callable for the list training pipelines method over gRPC.

        Lists TrainingPipelines in a Location.

        Returns:
            Callable[[~.ListTrainingPipelinesRequest],
                    ~.ListTrainingPipelinesResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_training_pipelines" not in self._stubs:
            self._stubs["list_training_pipelines"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.PipelineService/ListTrainingPipelines",
                request_serializer=pipeline_service.ListTrainingPipelinesRequest.serialize,
                response_deserializer=pipeline_service.ListTrainingPipelinesResponse.deserialize,
            )
        return self._stubs["list_training_pipelines"]

    @property
    def delete_training_pipeline(
        self,
    ) -> Callable[
        [pipeline_service.DeleteTrainingPipelineRequest], operations.Operation
    ]:
        r"""Return a callable for the delete training pipeline method over gRPC.

        Deletes a TrainingPipeline.

        Returns:
            Callable[[~.DeleteTrainingPipelineRequest],
                    ~.Operation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "delete_training_pipeline" not in self._stubs:
            self._stubs["delete_training_pipeline"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.PipelineService/DeleteTrainingPipeline",
                request_serializer=pipeline_service.DeleteTrainingPipelineRequest.serialize,
                response_deserializer=operations.Operation.FromString,
            )
        return self._stubs["delete_training_pipeline"]

    @property
    def cancel_training_pipeline(
        self,
    ) -> Callable[[pipeline_service.CancelTrainingPipelineRequest], empty.Empty]:
        r"""Return a callable for the cancel training pipeline method over gRPC.

        Cancels a TrainingPipeline. Starts asynchronous cancellation on
        the TrainingPipeline. The server makes a best effort to cancel
        the pipeline, but success is not guaranteed. Clients can use
        ``PipelineService.GetTrainingPipeline``
        or other methods to check whether the cancellation succeeded or
        whether the pipeline completed despite cancellation. On
        successful cancellation, the TrainingPipeline is not deleted;
        instead it becomes a pipeline with a
        ``TrainingPipeline.error``
        value with a ``google.rpc.Status.code`` of
        1, corresponding to ``Code.CANCELLED``, and
        ``TrainingPipeline.state``
        is set to ``CANCELLED``.

        Returns:
            Callable[[~.CancelTrainingPipelineRequest],
                    ~.Empty]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "cancel_training_pipeline" not in self._stubs:
            self._stubs["cancel_training_pipeline"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.PipelineService/CancelTrainingPipeline",
                request_serializer=pipeline_service.CancelTrainingPipelineRequest.serialize,
                response_deserializer=empty.Empty.FromString,
            )
        return self._stubs["cancel_training_pipeline"]


__all__ = ("PipelineServiceGrpcTransport",)
