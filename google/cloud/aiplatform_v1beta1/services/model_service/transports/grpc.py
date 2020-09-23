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

from google.cloud.aiplatform_v1beta1.types import model
from google.cloud.aiplatform_v1beta1.types import model as gca_model
from google.cloud.aiplatform_v1beta1.types import model_evaluation
from google.cloud.aiplatform_v1beta1.types import model_evaluation_slice
from google.cloud.aiplatform_v1beta1.types import model_service
from google.longrunning import operations_pb2 as operations  # type: ignore

from .base import ModelServiceTransport


class ModelServiceGrpcTransport(ModelServiceTransport):
    """gRPC backend transport for ModelService.

    A service for managing AI Platform's machine learning Models.

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
    def upload_model(
        self,
    ) -> Callable[[model_service.UploadModelRequest], operations.Operation]:
        r"""Return a callable for the upload model method over gRPC.

        Uploads a Model artifact into AI Platform.

        Returns:
            Callable[[~.UploadModelRequest],
                    ~.Operation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "upload_model" not in self._stubs:
            self._stubs["upload_model"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.ModelService/UploadModel",
                request_serializer=model_service.UploadModelRequest.serialize,
                response_deserializer=operations.Operation.FromString,
            )
        return self._stubs["upload_model"]

    @property
    def get_model(self) -> Callable[[model_service.GetModelRequest], model.Model]:
        r"""Return a callable for the get model method over gRPC.

        Gets a Model.

        Returns:
            Callable[[~.GetModelRequest],
                    ~.Model]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_model" not in self._stubs:
            self._stubs["get_model"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.ModelService/GetModel",
                request_serializer=model_service.GetModelRequest.serialize,
                response_deserializer=model.Model.deserialize,
            )
        return self._stubs["get_model"]

    @property
    def list_models(
        self,
    ) -> Callable[[model_service.ListModelsRequest], model_service.ListModelsResponse]:
        r"""Return a callable for the list models method over gRPC.

        Lists Models in a Location.

        Returns:
            Callable[[~.ListModelsRequest],
                    ~.ListModelsResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_models" not in self._stubs:
            self._stubs["list_models"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.ModelService/ListModels",
                request_serializer=model_service.ListModelsRequest.serialize,
                response_deserializer=model_service.ListModelsResponse.deserialize,
            )
        return self._stubs["list_models"]

    @property
    def update_model(
        self,
    ) -> Callable[[model_service.UpdateModelRequest], gca_model.Model]:
        r"""Return a callable for the update model method over gRPC.

        Updates a Model.

        Returns:
            Callable[[~.UpdateModelRequest],
                    ~.Model]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "update_model" not in self._stubs:
            self._stubs["update_model"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.ModelService/UpdateModel",
                request_serializer=model_service.UpdateModelRequest.serialize,
                response_deserializer=gca_model.Model.deserialize,
            )
        return self._stubs["update_model"]

    @property
    def delete_model(
        self,
    ) -> Callable[[model_service.DeleteModelRequest], operations.Operation]:
        r"""Return a callable for the delete model method over gRPC.

        Deletes a Model.
        Note: Model can only be deleted if there are no
        DeployedModels created from it.

        Returns:
            Callable[[~.DeleteModelRequest],
                    ~.Operation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "delete_model" not in self._stubs:
            self._stubs["delete_model"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.ModelService/DeleteModel",
                request_serializer=model_service.DeleteModelRequest.serialize,
                response_deserializer=operations.Operation.FromString,
            )
        return self._stubs["delete_model"]

    @property
    def export_model(
        self,
    ) -> Callable[[model_service.ExportModelRequest], operations.Operation]:
        r"""Return a callable for the export model method over gRPC.

        Exports a trained, exportable, Model to a location specified by
        the user. A Model is considered to be exportable if it has at
        least one [supported export
        format][google.cloud.aiplatform.v1beta1.Model.supported_export_formats].

        Returns:
            Callable[[~.ExportModelRequest],
                    ~.Operation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "export_model" not in self._stubs:
            self._stubs["export_model"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.ModelService/ExportModel",
                request_serializer=model_service.ExportModelRequest.serialize,
                response_deserializer=operations.Operation.FromString,
            )
        return self._stubs["export_model"]

    @property
    def get_model_evaluation(
        self,
    ) -> Callable[
        [model_service.GetModelEvaluationRequest], model_evaluation.ModelEvaluation
    ]:
        r"""Return a callable for the get model evaluation method over gRPC.

        Gets a ModelEvaluation.

        Returns:
            Callable[[~.GetModelEvaluationRequest],
                    ~.ModelEvaluation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_model_evaluation" not in self._stubs:
            self._stubs["get_model_evaluation"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.ModelService/GetModelEvaluation",
                request_serializer=model_service.GetModelEvaluationRequest.serialize,
                response_deserializer=model_evaluation.ModelEvaluation.deserialize,
            )
        return self._stubs["get_model_evaluation"]

    @property
    def list_model_evaluations(
        self,
    ) -> Callable[
        [model_service.ListModelEvaluationsRequest],
        model_service.ListModelEvaluationsResponse,
    ]:
        r"""Return a callable for the list model evaluations method over gRPC.

        Lists ModelEvaluations in a Model.

        Returns:
            Callable[[~.ListModelEvaluationsRequest],
                    ~.ListModelEvaluationsResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_model_evaluations" not in self._stubs:
            self._stubs["list_model_evaluations"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.ModelService/ListModelEvaluations",
                request_serializer=model_service.ListModelEvaluationsRequest.serialize,
                response_deserializer=model_service.ListModelEvaluationsResponse.deserialize,
            )
        return self._stubs["list_model_evaluations"]

    @property
    def get_model_evaluation_slice(
        self,
    ) -> Callable[
        [model_service.GetModelEvaluationSliceRequest],
        model_evaluation_slice.ModelEvaluationSlice,
    ]:
        r"""Return a callable for the get model evaluation slice method over gRPC.

        Gets a ModelEvaluationSlice.

        Returns:
            Callable[[~.GetModelEvaluationSliceRequest],
                    ~.ModelEvaluationSlice]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_model_evaluation_slice" not in self._stubs:
            self._stubs["get_model_evaluation_slice"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.ModelService/GetModelEvaluationSlice",
                request_serializer=model_service.GetModelEvaluationSliceRequest.serialize,
                response_deserializer=model_evaluation_slice.ModelEvaluationSlice.deserialize,
            )
        return self._stubs["get_model_evaluation_slice"]

    @property
    def list_model_evaluation_slices(
        self,
    ) -> Callable[
        [model_service.ListModelEvaluationSlicesRequest],
        model_service.ListModelEvaluationSlicesResponse,
    ]:
        r"""Return a callable for the list model evaluation slices method over gRPC.

        Lists ModelEvaluationSlices in a ModelEvaluation.

        Returns:
            Callable[[~.ListModelEvaluationSlicesRequest],
                    ~.ListModelEvaluationSlicesResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_model_evaluation_slices" not in self._stubs:
            self._stubs["list_model_evaluation_slices"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.ModelService/ListModelEvaluationSlices",
                request_serializer=model_service.ListModelEvaluationSlicesRequest.serialize,
                response_deserializer=model_service.ListModelEvaluationSlicesResponse.deserialize,
            )
        return self._stubs["list_model_evaluation_slices"]


__all__ = ("ModelServiceGrpcTransport",)
