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
from google.auth import credentials  # type: ignore

import grpc  # type: ignore

from google.cloud.aiplatform_v1beta1.types import prediction_service

from .base import PredictionServiceTransport


class PredictionServiceGrpcTransport(PredictionServiceTransport):
    """gRPC backend transport for PredictionService.

    A service for online predictions and explanations.

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
    def predict(
        self,
    ) -> Callable[
        [prediction_service.PredictRequest], prediction_service.PredictResponse
    ]:
        r"""Return a callable for the predict method over gRPC.

        Perform an online prediction.

        Returns:
            Callable[[~.PredictRequest],
                    ~.PredictResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "predict" not in self._stubs:
            self._stubs["predict"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.PredictionService/Predict",
                request_serializer=prediction_service.PredictRequest.serialize,
                response_deserializer=prediction_service.PredictResponse.deserialize,
            )
        return self._stubs["predict"]

    @property
    def explain(
        self,
    ) -> Callable[
        [prediction_service.ExplainRequest], prediction_service.ExplainResponse
    ]:
        r"""Return a callable for the explain method over gRPC.

        Perform an online explanation.

        If [ExplainRequest.deployed_model_id] is specified, the
        corresponding DeployModel must have
        [explanation_spec][google.cloud.aiplatform.v1beta1.DeployedModel.explanation_spec]
        populated. If [ExplainRequest.deployed_model_id] is not
        specified, all DeployedModels must have
        [explanation_spec][google.cloud.aiplatform.v1beta1.DeployedModel.explanation_spec]
        populated. Only deployed AutoML tabular Models have
        explanation_spec.

        Returns:
            Callable[[~.ExplainRequest],
                    ~.ExplainResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "explain" not in self._stubs:
            self._stubs["explain"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.PredictionService/Explain",
                request_serializer=prediction_service.ExplainRequest.serialize,
                response_deserializer=prediction_service.ExplainResponse.deserialize,
            )
        return self._stubs["explain"]


__all__ = ("PredictionServiceGrpcTransport",)
