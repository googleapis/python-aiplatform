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

from collections import OrderedDict
from typing import Dict, Sequence, Tuple, Type, Union
import pkg_resources

import google.api_core.client_options as ClientOptions  # type: ignore
from google.api_core import exceptions  # type: ignore
from google.api_core import gapic_v1  # type: ignore
from google.api_core import retry as retries  # type: ignore
from google.auth import credentials  # type: ignore
from google.oauth2 import service_account  # type: ignore

from google.cloud.aiplatform_v1beta1.types import explanation
from google.cloud.aiplatform_v1beta1.types import prediction_service
from google.protobuf import struct_pb2 as struct  # type: ignore

from .transports.base import PredictionServiceTransport
from .transports.grpc import PredictionServiceGrpcTransport


class PredictionServiceClientMeta(type):
    """Metaclass for the PredictionService client.

    This provides class-level methods for building and retrieving
    support objects (e.g. transport) without polluting the client instance
    objects.
    """

    _transport_registry = (
        OrderedDict()
    )  # type: Dict[str, Type[PredictionServiceTransport]]
    _transport_registry["grpc"] = PredictionServiceGrpcTransport

    def get_transport_class(
        cls, label: str = None,
    ) -> Type[PredictionServiceTransport]:
        """Return an appropriate transport class.

        Args:
            label: The name of the desired transport. If none is
                provided, then the first transport in the registry is used.

        Returns:
            The transport class to use.
        """
        # If a specific transport is requested, return that one.
        if label:
            return cls._transport_registry[label]

        # No transport is requested; return the default (that is, the first one
        # in the dictionary).
        return next(iter(cls._transport_registry.values()))


class PredictionServiceClient(metaclass=PredictionServiceClientMeta):
    """A service for online predictions and explanations."""

    DEFAULT_OPTIONS = ClientOptions.ClientOptions(
        api_endpoint="aiplatform.googleapis.com"
    )

    @classmethod
    def from_service_account_file(cls, filename: str, *args, **kwargs):
        """Creates an instance of this client using the provided credentials
        file.

        Args:
            filename (str): The path to the service account private key json
                file.
            args: Additional arguments to pass to the constructor.
            kwargs: Additional arguments to pass to the constructor.

        Returns:
            {@api.name}: The constructed client.
        """
        credentials = service_account.Credentials.from_service_account_file(filename)
        kwargs["credentials"] = credentials
        return cls(*args, **kwargs)

    from_service_account_json = from_service_account_file

    def __init__(
        self,
        *,
        credentials: credentials.Credentials = None,
        transport: Union[str, PredictionServiceTransport] = None,
        client_options: ClientOptions.ClientOptions = DEFAULT_OPTIONS,
    ) -> None:
        """Instantiate the prediction service client.

        Args:
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            transport (Union[str, ~.PredictionServiceTransport]): The
                transport to use. If set to None, a transport is chosen
                automatically.
            client_options (ClientOptions): Custom options for the client.
        """
        if isinstance(client_options, dict):
            client_options = ClientOptions.from_dict(client_options)

        # Save or instantiate the transport.
        # Ordinarily, we provide the transport, but allowing a custom transport
        # instance provides an extensibility point for unusual situations.
        if isinstance(transport, PredictionServiceTransport):
            if credentials:
                raise ValueError(
                    "When providing a transport instance, "
                    "provide its credentials directly."
                )
            self._transport = transport
        else:
            Transport = type(self).get_transport_class(transport)
            self._transport = Transport(
                credentials=credentials,
                host=client_options.api_endpoint or "aiplatform.googleapis.com",
            )

    def predict(
        self,
        request: prediction_service.PredictRequest = None,
        *,
        endpoint: str = None,
        instances: Sequence[struct.Value] = None,
        parameters: struct.Value = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> prediction_service.PredictResponse:
        r"""Perform an online prediction.

        Args:
            request (:class:`~.prediction_service.PredictRequest`):
                The request object. Request message for
                [PredictionService.Predict][google.cloud.aiplatform.v1beta1.PredictionService.Predict].
            endpoint (:class:`str`):
                Required. The name of the Endpoint requested to serve
                the prediction. Format:
                ``projects/{project}/locations/{location}/endpoints/{endpoint}``
                This corresponds to the ``endpoint`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            instances (:class:`Sequence[~.struct.Value]`):
                Required. The instances that are the input to the
                prediction call. A DeployedModel may have an upper limit
                on the number of instances it supports per request, and
                when it is exceeded the prediction call errors in case
                of AutoML Models, or, in case of customer created
                Models, the behaviour is as documented by that Model.
                The schema of any single instance may be specified via
                Endpoint's DeployedModels'
                [Model's][google.cloud.aiplatform.v1beta1.DeployedModel.model]
                [PredictSchemata's][google.cloud.aiplatform.v1beta1.Model.predict_schemata]
                [instance_schema_uri][google.cloud.aiplatform.v1beta1.PredictSchemata.instance_schema_uri].
                This corresponds to the ``instances`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            parameters (:class:`~.struct.Value`):
                The parameters that govern the prediction. The schema of
                the parameters may be specified via Endpoint's
                DeployedModels' [Model's
                ][google.cloud.aiplatform.v1beta1.DeployedModel.model]
                [PredictSchemata's][google.cloud.aiplatform.v1beta1.Model.predict_schemata]
                [parameters_schema_uri][google.cloud.aiplatform.v1beta1.PredictSchemata.parameters_schema_uri].
                This corresponds to the ``parameters`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.

            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            ~.prediction_service.PredictResponse:
                Response message for
                [PredictionService.Predict][google.cloud.aiplatform.v1beta1.PredictionService.Predict].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        if request is not None and any([endpoint, instances, parameters]):
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = prediction_service.PredictRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.

        if endpoint is not None:
            request.endpoint = endpoint
        if instances is not None:
            request.instances = instances
        if parameters is not None:
            request.parameters = parameters

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method.wrap_method(
            self._transport.predict, default_timeout=None, client_info=_client_info,
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    def explain(
        self,
        request: prediction_service.ExplainRequest = None,
        *,
        endpoint: str = None,
        instances: Sequence[struct.Value] = None,
        parameters: struct.Value = None,
        deployed_model_id: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> prediction_service.ExplainResponse:
        r"""Perform an online explanation.

        If [ExplainRequest.deployed_model_id] is specified, the
        corresponding DeployModel must have
        [explanation_spec][google.cloud.aiplatform.v1beta1.DeployedModel.explanation_spec]
        populated. If [ExplainRequest.deployed_model_id] is not
        specified, all DeployedModels must have
        [explanation_spec][google.cloud.aiplatform.v1beta1.DeployedModel.explanation_spec]
        populated. Only deployed AutoML tabular Models have
        explanation_spec.

        Args:
            request (:class:`~.prediction_service.ExplainRequest`):
                The request object. Request message for
                [PredictionService.Explain][google.cloud.aiplatform.v1beta1.PredictionService.Explain].
            endpoint (:class:`str`):
                Required. The name of the Endpoint requested to serve
                the explanation. Format:
                ``projects/{project}/locations/{location}/endpoints/{endpoint}``
                This corresponds to the ``endpoint`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            instances (:class:`Sequence[~.struct.Value]`):
                Required. The instances that are the input to the
                explanation call. A DeployedModel may have an upper
                limit on the number of instances it supports per
                request, and when it is exceeded the explanation call
                errors in case of AutoML Models, or, in case of customer
                created Models, the behaviour is as documented by that
                Model. The schema of any single instance may be
                specified via Endpoint's DeployedModels'
                [Model's][google.cloud.aiplatform.v1beta1.DeployedModel.model]
                [PredictSchemata's][google.cloud.aiplatform.v1beta1.Model.predict_schemata]
                [instance_schema_uri][google.cloud.aiplatform.v1beta1.PredictSchemata.instance_schema_uri].
                This corresponds to the ``instances`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            parameters (:class:`~.struct.Value`):
                The parameters that govern the prediction. The schema of
                the parameters may be specified via Endpoint's
                DeployedModels' [Model's
                ][google.cloud.aiplatform.v1beta1.DeployedModel.model]
                [PredictSchemata's][google.cloud.aiplatform.v1beta1.Model.predict_schemata]
                [parameters_schema_uri][google.cloud.aiplatform.v1beta1.PredictSchemata.parameters_schema_uri].
                This corresponds to the ``parameters`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            deployed_model_id (:class:`str`):
                If specified, this ExplainRequest will be served by the
                chosen DeployedModel, overriding
                [Endpoint.traffic_split][google.cloud.aiplatform.v1beta1.Endpoint.traffic_split].
                This corresponds to the ``deployed_model_id`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.

            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            ~.prediction_service.ExplainResponse:
                Response message for
                [PredictionService.Explain][google.cloud.aiplatform.v1beta1.PredictionService.Explain].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        if request is not None and any(
            [endpoint, instances, parameters, deployed_model_id]
        ):
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = prediction_service.ExplainRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.

        if endpoint is not None:
            request.endpoint = endpoint
        if instances is not None:
            request.instances = instances
        if parameters is not None:
            request.parameters = parameters
        if deployed_model_id is not None:
            request.deployed_model_id = deployed_model_id

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method.wrap_method(
            self._transport.explain, default_timeout=None, client_info=_client_info,
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response


try:
    _client_info = gapic_v1.client_info.ClientInfo(
        gapic_version=pkg_resources.get_distribution(
            "google-cloud-aiplatform",
        ).version,
    )
except pkg_resources.DistributionNotFound:
    _client_info = gapic_v1.client_info.ClientInfo()


__all__ = ("PredictionServiceClient",)
