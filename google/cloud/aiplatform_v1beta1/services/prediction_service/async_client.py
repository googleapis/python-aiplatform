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
import functools
import re
from typing import Dict, Sequence, Tuple, Type, Union
import pkg_resources

import google.api_core.client_options as ClientOptions  # type: ignore
from google.api_core import exceptions as core_exceptions  # type: ignore
from google.api_core import gapic_v1  # type: ignore
from google.api_core import retry as retries  # type: ignore
from google.auth import credentials as ga_credentials  # type: ignore
from google.oauth2 import service_account  # type: ignore

from google.api import httpbody_pb2  # type: ignore
from google.cloud.aiplatform_v1beta1.types import explanation
from google.cloud.aiplatform_v1beta1.types import prediction_service
from google.protobuf import any_pb2  # type: ignore
from google.protobuf import struct_pb2  # type: ignore
from .transports.base import PredictionServiceTransport, DEFAULT_CLIENT_INFO
from .transports.grpc_asyncio import PredictionServiceGrpcAsyncIOTransport
from .client import PredictionServiceClient


class PredictionServiceAsyncClient:
    """A service for online predictions and explanations."""

    _client: PredictionServiceClient

    DEFAULT_ENDPOINT = PredictionServiceClient.DEFAULT_ENDPOINT
    DEFAULT_MTLS_ENDPOINT = PredictionServiceClient.DEFAULT_MTLS_ENDPOINT

    endpoint_path = staticmethod(PredictionServiceClient.endpoint_path)
    parse_endpoint_path = staticmethod(PredictionServiceClient.parse_endpoint_path)
    common_billing_account_path = staticmethod(
        PredictionServiceClient.common_billing_account_path
    )
    parse_common_billing_account_path = staticmethod(
        PredictionServiceClient.parse_common_billing_account_path
    )
    common_folder_path = staticmethod(PredictionServiceClient.common_folder_path)
    parse_common_folder_path = staticmethod(
        PredictionServiceClient.parse_common_folder_path
    )
    common_organization_path = staticmethod(
        PredictionServiceClient.common_organization_path
    )
    parse_common_organization_path = staticmethod(
        PredictionServiceClient.parse_common_organization_path
    )
    common_project_path = staticmethod(PredictionServiceClient.common_project_path)
    parse_common_project_path = staticmethod(
        PredictionServiceClient.parse_common_project_path
    )
    common_location_path = staticmethod(PredictionServiceClient.common_location_path)
    parse_common_location_path = staticmethod(
        PredictionServiceClient.parse_common_location_path
    )

    @classmethod
    def from_service_account_info(cls, info: dict, *args, **kwargs):
        """Creates an instance of this client using the provided credentials
            info.

        Args:
            info (dict): The service account private key info.
            args: Additional arguments to pass to the constructor.
            kwargs: Additional arguments to pass to the constructor.

        Returns:
            PredictionServiceAsyncClient: The constructed client.
        """
        return PredictionServiceClient.from_service_account_info.__func__(PredictionServiceAsyncClient, info, *args, **kwargs)  # type: ignore

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
            PredictionServiceAsyncClient: The constructed client.
        """
        return PredictionServiceClient.from_service_account_file.__func__(PredictionServiceAsyncClient, filename, *args, **kwargs)  # type: ignore

    from_service_account_json = from_service_account_file

    @property
    def transport(self) -> PredictionServiceTransport:
        """Returns the transport used by the client instance.

        Returns:
            PredictionServiceTransport: The transport used by the client instance.
        """
        return self._client.transport

    get_transport_class = functools.partial(
        type(PredictionServiceClient).get_transport_class, type(PredictionServiceClient)
    )

    def __init__(
        self,
        *,
        credentials: ga_credentials.Credentials = None,
        transport: Union[str, PredictionServiceTransport] = "grpc_asyncio",
        client_options: ClientOptions = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
    ) -> None:
        """Instantiates the prediction service client.

        Args:
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            transport (Union[str, ~.PredictionServiceTransport]): The
                transport to use. If set to None, a transport is chosen
                automatically.
            client_options (ClientOptions): Custom options for the client. It
                won't take effect if a ``transport`` instance is provided.
                (1) The ``api_endpoint`` property can be used to override the
                default endpoint provided by the client. GOOGLE_API_USE_MTLS_ENDPOINT
                environment variable can also be used to override the endpoint:
                "always" (always use the default mTLS endpoint), "never" (always
                use the default regular endpoint) and "auto" (auto switch to the
                default mTLS endpoint if client certificate is present, this is
                the default value). However, the ``api_endpoint`` property takes
                precedence if provided.
                (2) If GOOGLE_API_USE_CLIENT_CERTIFICATE environment variable
                is "true", then the ``client_cert_source`` property can be used
                to provide client certificate for mutual TLS transport. If
                not provided, the default SSL client certificate will be used if
                present. If GOOGLE_API_USE_CLIENT_CERTIFICATE is "false" or not
                set, no client certificate will be used.

        Raises:
            google.auth.exceptions.MutualTlsChannelError: If mutual TLS transport
                creation failed for any reason.
        """
        self._client = PredictionServiceClient(
            credentials=credentials,
            transport=transport,
            client_options=client_options,
            client_info=client_info,
        )

    async def predict(
        self,
        request: prediction_service.PredictRequest = None,
        *,
        endpoint: str = None,
        instances: Sequence[struct_pb2.Value] = None,
        parameters: struct_pb2.Value = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> prediction_service.PredictResponse:
        r"""Perform an online prediction.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.PredictRequest`):
                The request object. Request message for
                [PredictionService.Predict][google.cloud.aiplatform.v1beta1.PredictionService.Predict].
            endpoint (:class:`str`):
                Required. The name of the Endpoint requested to serve
                the prediction. Format:
                ``projects/{project}/locations/{location}/endpoints/{endpoint}``

                This corresponds to the ``endpoint`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            instances (:class:`Sequence[google.protobuf.struct_pb2.Value]`):
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
            parameters (:class:`google.protobuf.struct_pb2.Value`):
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
            google.cloud.aiplatform_v1beta1.types.PredictResponse:
                Response message for
                [PredictionService.Predict][google.cloud.aiplatform.v1beta1.PredictionService.Predict].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([endpoint, instances, parameters])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = prediction_service.PredictRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if endpoint is not None:
            request.endpoint = endpoint
        if parameters is not None:
            request.parameters = parameters
        if instances:
            request.instances.extend(instances)

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.predict,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("endpoint", request.endpoint),)),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def raw_predict(
        self,
        request: prediction_service.RawPredictRequest = None,
        *,
        endpoint: str = None,
        http_body: httpbody_pb2.HttpBody = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> httpbody_pb2.HttpBody:
        r"""Perform an online prediction with arbitrary http
        payload.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.RawPredictRequest`):
                The request object. Request message for
                [PredictionService.RawPredict][google.cloud.aiplatform.v1beta1.PredictionService.RawPredict].
            endpoint (:class:`str`):
                Required. The name of the Endpoint requested to serve
                the prediction. Format:
                ``projects/{project}/locations/{location}/endpoints/{endpoint}``

                This corresponds to the ``endpoint`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            http_body (:class:`google.api.httpbody_pb2.HttpBody`):
                The prediction input. Supports HTTP headers and
                arbitrary data payload.

                A
                [DeployedModel][google.cloud.aiplatform.v1beta1.DeployedModel]
                may have an upper limit on the number of instances it
                supports per request. When this limit it is exceeded for
                an AutoML model, the
                [RawPredict][google.cloud.aiplatform.v1beta1.PredictionService.RawPredict]
                method returns an error. When this limit is exceeded for
                a custom-trained model, the behavior varies depending on
                the model.

                You can specify the schema for each instance in the
                [predict_schemata.instance_schema_uri][google.cloud.aiplatform.v1beta1.PredictSchemata.instance_schema_uri]
                field when you create a
                [Model][google.cloud.aiplatform.v1beta1.Model]. This
                schema applies when you deploy the ``Model`` as a
                ``DeployedModel`` to an
                [Endpoint][google.cloud.aiplatform.v1beta1.Endpoint] and
                use the ``RawPredict`` method.

                This corresponds to the ``http_body`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.api.httpbody_pb2.HttpBody:
                Message that represents an arbitrary HTTP body. It should only be used for
                   payload formats that can't be represented as JSON,
                   such as raw binary or an HTML page.

                   This message can be used both in streaming and
                   non-streaming API methods in the request as well as
                   the response.

                   It can be used as a top-level request field, which is
                   convenient if one wants to extract parameters from
                   either the URL or HTTP template into the request
                   fields and also want access to the raw HTTP body.

                   Example:

                      message GetResourceRequest {
                         // A unique request id. string request_id = 1;

                         // The raw HTTP body is bound to this field.
                         google.api.HttpBody http_body = 2;

                      }

                      service ResourceService {
                         rpc GetResource(GetResourceRequest) returns
                         (google.api.HttpBody); rpc
                         UpdateResource(google.api.HttpBody) returns
                         (google.protobuf.Empty);

                      }

                   Example with streaming methods:

                      service CaldavService {
                         rpc GetCalendar(stream google.api.HttpBody)
                            returns (stream google.api.HttpBody);

                         rpc UpdateCalendar(stream google.api.HttpBody)
                            returns (stream google.api.HttpBody);

                      }

                   Use of this type only changes how the request and
                   response bodies are handled, all other features will
                   continue to work unchanged.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([endpoint, http_body])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = prediction_service.RawPredictRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if endpoint is not None:
            request.endpoint = endpoint
        if http_body is not None:
            request.http_body = http_body

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.raw_predict,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("endpoint", request.endpoint),)),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def explain(
        self,
        request: prediction_service.ExplainRequest = None,
        *,
        endpoint: str = None,
        instances: Sequence[struct_pb2.Value] = None,
        parameters: struct_pb2.Value = None,
        deployed_model_id: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> prediction_service.ExplainResponse:
        r"""Perform an online explanation.

        If
        [deployed_model_id][google.cloud.aiplatform.v1beta1.ExplainRequest.deployed_model_id]
        is specified, the corresponding DeployModel must have
        [explanation_spec][google.cloud.aiplatform.v1beta1.DeployedModel.explanation_spec]
        populated. If
        [deployed_model_id][google.cloud.aiplatform.v1beta1.ExplainRequest.deployed_model_id]
        is not specified, all DeployedModels must have
        [explanation_spec][google.cloud.aiplatform.v1beta1.DeployedModel.explanation_spec]
        populated. Only deployed AutoML tabular Models have
        explanation_spec.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.ExplainRequest`):
                The request object. Request message for
                [PredictionService.Explain][google.cloud.aiplatform.v1beta1.PredictionService.Explain].
            endpoint (:class:`str`):
                Required. The name of the Endpoint requested to serve
                the explanation. Format:
                ``projects/{project}/locations/{location}/endpoints/{endpoint}``

                This corresponds to the ``endpoint`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            instances (:class:`Sequence[google.protobuf.struct_pb2.Value]`):
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
            parameters (:class:`google.protobuf.struct_pb2.Value`):
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
            google.cloud.aiplatform_v1beta1.types.ExplainResponse:
                Response message for
                [PredictionService.Explain][google.cloud.aiplatform.v1beta1.PredictionService.Explain].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([endpoint, instances, parameters, deployed_model_id])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = prediction_service.ExplainRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if endpoint is not None:
            request.endpoint = endpoint
        if parameters is not None:
            request.parameters = parameters
        if deployed_model_id is not None:
            request.deployed_model_id = deployed_model_id
        if instances:
            request.instances.extend(instances)

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.explain,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("endpoint", request.endpoint),)),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response


try:
    DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo(
        gapic_version=pkg_resources.get_distribution(
            "google-cloud-aiplatform",
        ).version,
    )
except pkg_resources.DistributionNotFound:
    DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo()


__all__ = ("PredictionServiceAsyncClient",)
