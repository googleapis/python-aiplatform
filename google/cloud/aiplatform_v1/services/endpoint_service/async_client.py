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

from google.api_core import operation as gac_operation  # type: ignore
from google.api_core import operation_async  # type: ignore
from google.cloud.aiplatform_v1.services.endpoint_service import pagers
from google.cloud.aiplatform_v1.types import encryption_spec
from google.cloud.aiplatform_v1.types import endpoint
from google.cloud.aiplatform_v1.types import endpoint as gca_endpoint
from google.cloud.aiplatform_v1.types import endpoint_service
from google.cloud.aiplatform_v1.types import operation as gca_operation
from google.protobuf import empty_pb2  # type: ignore
from google.protobuf import field_mask_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
from .transports.base import EndpointServiceTransport, DEFAULT_CLIENT_INFO
from .transports.grpc_asyncio import EndpointServiceGrpcAsyncIOTransport
from .client import EndpointServiceClient


class EndpointServiceAsyncClient:
    """"""

    _client: EndpointServiceClient

    DEFAULT_ENDPOINT = EndpointServiceClient.DEFAULT_ENDPOINT
    DEFAULT_MTLS_ENDPOINT = EndpointServiceClient.DEFAULT_MTLS_ENDPOINT

    endpoint_path = staticmethod(EndpointServiceClient.endpoint_path)
    parse_endpoint_path = staticmethod(EndpointServiceClient.parse_endpoint_path)
    model_path = staticmethod(EndpointServiceClient.model_path)
    parse_model_path = staticmethod(EndpointServiceClient.parse_model_path)
    common_billing_account_path = staticmethod(
        EndpointServiceClient.common_billing_account_path
    )
    parse_common_billing_account_path = staticmethod(
        EndpointServiceClient.parse_common_billing_account_path
    )
    common_folder_path = staticmethod(EndpointServiceClient.common_folder_path)
    parse_common_folder_path = staticmethod(
        EndpointServiceClient.parse_common_folder_path
    )
    common_organization_path = staticmethod(
        EndpointServiceClient.common_organization_path
    )
    parse_common_organization_path = staticmethod(
        EndpointServiceClient.parse_common_organization_path
    )
    common_project_path = staticmethod(EndpointServiceClient.common_project_path)
    parse_common_project_path = staticmethod(
        EndpointServiceClient.parse_common_project_path
    )
    common_location_path = staticmethod(EndpointServiceClient.common_location_path)
    parse_common_location_path = staticmethod(
        EndpointServiceClient.parse_common_location_path
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
            EndpointServiceAsyncClient: The constructed client.
        """
        return EndpointServiceClient.from_service_account_info.__func__(EndpointServiceAsyncClient, info, *args, **kwargs)  # type: ignore

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
            EndpointServiceAsyncClient: The constructed client.
        """
        return EndpointServiceClient.from_service_account_file.__func__(EndpointServiceAsyncClient, filename, *args, **kwargs)  # type: ignore

    from_service_account_json = from_service_account_file

    @property
    def transport(self) -> EndpointServiceTransport:
        """Returns the transport used by the client instance.

        Returns:
            EndpointServiceTransport: The transport used by the client instance.
        """
        return self._client.transport

    get_transport_class = functools.partial(
        type(EndpointServiceClient).get_transport_class, type(EndpointServiceClient)
    )

    def __init__(
        self,
        *,
        credentials: ga_credentials.Credentials = None,
        transport: Union[str, EndpointServiceTransport] = "grpc_asyncio",
        client_options: ClientOptions = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
    ) -> None:
        """Instantiates the endpoint service client.

        Args:
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            transport (Union[str, ~.EndpointServiceTransport]): The
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
        self._client = EndpointServiceClient(
            credentials=credentials,
            transport=transport,
            client_options=client_options,
            client_info=client_info,
        )

    async def create_endpoint(
        self,
        request: endpoint_service.CreateEndpointRequest = None,
        *,
        parent: str = None,
        endpoint: gca_endpoint.Endpoint = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Creates an Endpoint.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.CreateEndpointRequest`):
                The request object. Request message for
                [EndpointService.CreateEndpoint][google.cloud.aiplatform.v1.EndpointService.CreateEndpoint].
            parent (:class:`str`):
                Required. The resource name of the Location to create
                the Endpoint in. Format:
                ``projects/{project}/locations/{location}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            endpoint (:class:`google.cloud.aiplatform_v1.types.Endpoint`):
                Required. The Endpoint to create.
                This corresponds to the ``endpoint`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.api_core.operation_async.AsyncOperation:
                An object representing a long-running operation.

                The result type for the operation will be :class:`google.cloud.aiplatform_v1.types.Endpoint` Models are deployed into it, and afterwards Endpoint is called to obtain
                   predictions and explanations.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, endpoint])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = endpoint_service.CreateEndpointRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if endpoint is not None:
            request.endpoint = endpoint

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_endpoint,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", request.parent),)),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = operation_async.from_gapic(
            response,
            self._client._transport.operations_client,
            gca_endpoint.Endpoint,
            metadata_type=endpoint_service.CreateEndpointOperationMetadata,
        )

        # Done; return the response.
        return response

    async def get_endpoint(
        self,
        request: endpoint_service.GetEndpointRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> endpoint.Endpoint:
        r"""Gets an Endpoint.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.GetEndpointRequest`):
                The request object. Request message for
                [EndpointService.GetEndpoint][google.cloud.aiplatform.v1.EndpointService.GetEndpoint]
            name (:class:`str`):
                Required. The name of the Endpoint resource. Format:
                ``projects/{project}/locations/{location}/endpoints/{endpoint}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.types.Endpoint:
                Models are deployed into it, and
                afterwards Endpoint is called to obtain
                predictions and explanations.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([name])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = endpoint_service.GetEndpointRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_endpoint,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("name", request.name),)),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def list_endpoints(
        self,
        request: endpoint_service.ListEndpointsRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListEndpointsAsyncPager:
        r"""Lists Endpoints in a Location.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.ListEndpointsRequest`):
                The request object. Request message for
                [EndpointService.ListEndpoints][google.cloud.aiplatform.v1.EndpointService.ListEndpoints].
            parent (:class:`str`):
                Required. The resource name of the Location from which
                to list the Endpoints. Format:
                ``projects/{project}/locations/{location}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.services.endpoint_service.pagers.ListEndpointsAsyncPager:
                Response message for
                [EndpointService.ListEndpoints][google.cloud.aiplatform.v1.EndpointService.ListEndpoints].

                Iterating over this object will yield results and
                resolve additional pages automatically.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = endpoint_service.ListEndpointsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_endpoints,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", request.parent),)),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # This method is paged; wrap the response in a pager, which provides
        # an `__aiter__` convenience method.
        response = pagers.ListEndpointsAsyncPager(
            method=rpc, request=request, response=response, metadata=metadata,
        )

        # Done; return the response.
        return response

    async def update_endpoint(
        self,
        request: endpoint_service.UpdateEndpointRequest = None,
        *,
        endpoint: gca_endpoint.Endpoint = None,
        update_mask: field_mask_pb2.FieldMask = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_endpoint.Endpoint:
        r"""Updates an Endpoint.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.UpdateEndpointRequest`):
                The request object. Request message for
                [EndpointService.UpdateEndpoint][google.cloud.aiplatform.v1.EndpointService.UpdateEndpoint].
            endpoint (:class:`google.cloud.aiplatform_v1.types.Endpoint`):
                Required. The Endpoint which replaces
                the resource on the server.

                This corresponds to the ``endpoint`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            update_mask (:class:`google.protobuf.field_mask_pb2.FieldMask`):
                Required. The update mask applies to the resource. See
                [google.protobuf.FieldMask][google.protobuf.FieldMask].

                This corresponds to the ``update_mask`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.types.Endpoint:
                Models are deployed into it, and
                afterwards Endpoint is called to obtain
                predictions and explanations.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([endpoint, update_mask])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = endpoint_service.UpdateEndpointRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if endpoint is not None:
            request.endpoint = endpoint
        if update_mask is not None:
            request.update_mask = update_mask

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.update_endpoint,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("endpoint.name", request.endpoint.name),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def delete_endpoint(
        self,
        request: endpoint_service.DeleteEndpointRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Deletes an Endpoint.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.DeleteEndpointRequest`):
                The request object. Request message for
                [EndpointService.DeleteEndpoint][google.cloud.aiplatform.v1.EndpointService.DeleteEndpoint].
            name (:class:`str`):
                Required. The name of the Endpoint resource to be
                deleted. Format:
                ``projects/{project}/locations/{location}/endpoints/{endpoint}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.api_core.operation_async.AsyncOperation:
                An object representing a long-running operation.

                The result type for the operation will be :class:`google.protobuf.empty_pb2.Empty` A generic empty message that you can re-use to avoid defining duplicated
                   empty messages in your APIs. A typical example is to
                   use it as the request or the response type of an API
                   method. For instance:

                      service Foo {
                         rpc Bar(google.protobuf.Empty) returns
                         (google.protobuf.Empty);

                      }

                   The JSON representation for Empty is empty JSON
                   object {}.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([name])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = endpoint_service.DeleteEndpointRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.delete_endpoint,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("name", request.name),)),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = operation_async.from_gapic(
            response,
            self._client._transport.operations_client,
            empty_pb2.Empty,
            metadata_type=gca_operation.DeleteOperationMetadata,
        )

        # Done; return the response.
        return response

    async def deploy_model(
        self,
        request: endpoint_service.DeployModelRequest = None,
        *,
        endpoint: str = None,
        deployed_model: gca_endpoint.DeployedModel = None,
        traffic_split: Sequence[
            endpoint_service.DeployModelRequest.TrafficSplitEntry
        ] = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Deploys a Model into this Endpoint, creating a
        DeployedModel within it.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.DeployModelRequest`):
                The request object. Request message for
                [EndpointService.DeployModel][google.cloud.aiplatform.v1.EndpointService.DeployModel].
            endpoint (:class:`str`):
                Required. The name of the Endpoint resource into which
                to deploy a Model. Format:
                ``projects/{project}/locations/{location}/endpoints/{endpoint}``

                This corresponds to the ``endpoint`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            deployed_model (:class:`google.cloud.aiplatform_v1.types.DeployedModel`):
                Required. The DeployedModel to be created within the
                Endpoint. Note that
                [Endpoint.traffic_split][google.cloud.aiplatform.v1.Endpoint.traffic_split]
                must be updated for the DeployedModel to start receiving
                traffic, either as part of this call, or via
                [EndpointService.UpdateEndpoint][google.cloud.aiplatform.v1.EndpointService.UpdateEndpoint].

                This corresponds to the ``deployed_model`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            traffic_split (:class:`Sequence[google.cloud.aiplatform_v1.types.DeployModelRequest.TrafficSplitEntry]`):
                A map from a DeployedModel's ID to the percentage of
                this Endpoint's traffic that should be forwarded to that
                DeployedModel.

                If this field is non-empty, then the Endpoint's
                [traffic_split][google.cloud.aiplatform.v1.Endpoint.traffic_split]
                will be overwritten with it. To refer to the ID of the
                just being deployed Model, a "0" should be used, and the
                actual ID of the new DeployedModel will be filled in its
                place by this method. The traffic percentage values must
                add up to 100.

                If this field is empty, then the Endpoint's
                [traffic_split][google.cloud.aiplatform.v1.Endpoint.traffic_split]
                is not updated.

                This corresponds to the ``traffic_split`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.api_core.operation_async.AsyncOperation:
                An object representing a long-running operation.

                The result type for the operation will be
                :class:`google.cloud.aiplatform_v1.types.DeployModelResponse`
                Response message for
                [EndpointService.DeployModel][google.cloud.aiplatform.v1.EndpointService.DeployModel].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([endpoint, deployed_model, traffic_split])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = endpoint_service.DeployModelRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if endpoint is not None:
            request.endpoint = endpoint
        if deployed_model is not None:
            request.deployed_model = deployed_model

        if traffic_split:
            request.traffic_split.update(traffic_split)

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.deploy_model,
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

        # Wrap the response in an operation future.
        response = operation_async.from_gapic(
            response,
            self._client._transport.operations_client,
            endpoint_service.DeployModelResponse,
            metadata_type=endpoint_service.DeployModelOperationMetadata,
        )

        # Done; return the response.
        return response

    async def undeploy_model(
        self,
        request: endpoint_service.UndeployModelRequest = None,
        *,
        endpoint: str = None,
        deployed_model_id: str = None,
        traffic_split: Sequence[
            endpoint_service.UndeployModelRequest.TrafficSplitEntry
        ] = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Undeploys a Model from an Endpoint, removing a
        DeployedModel from it, and freeing all resources it's
        using.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.UndeployModelRequest`):
                The request object. Request message for
                [EndpointService.UndeployModel][google.cloud.aiplatform.v1.EndpointService.UndeployModel].
            endpoint (:class:`str`):
                Required. The name of the Endpoint resource from which
                to undeploy a Model. Format:
                ``projects/{project}/locations/{location}/endpoints/{endpoint}``

                This corresponds to the ``endpoint`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            deployed_model_id (:class:`str`):
                Required. The ID of the DeployedModel
                to be undeployed from the Endpoint.

                This corresponds to the ``deployed_model_id`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            traffic_split (:class:`Sequence[google.cloud.aiplatform_v1.types.UndeployModelRequest.TrafficSplitEntry]`):
                If this field is provided, then the Endpoint's
                [traffic_split][google.cloud.aiplatform.v1.Endpoint.traffic_split]
                will be overwritten with it. If last DeployedModel is
                being undeployed from the Endpoint, the
                [Endpoint.traffic_split] will always end up empty when
                this call returns. A DeployedModel will be successfully
                undeployed only if it doesn't have any traffic assigned
                to it when this method executes, or if this field
                unassigns any traffic to it.

                This corresponds to the ``traffic_split`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.api_core.operation_async.AsyncOperation:
                An object representing a long-running operation.

                The result type for the operation will be
                :class:`google.cloud.aiplatform_v1.types.UndeployModelResponse`
                Response message for
                [EndpointService.UndeployModel][google.cloud.aiplatform.v1.EndpointService.UndeployModel].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([endpoint, deployed_model_id, traffic_split])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = endpoint_service.UndeployModelRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if endpoint is not None:
            request.endpoint = endpoint
        if deployed_model_id is not None:
            request.deployed_model_id = deployed_model_id

        if traffic_split:
            request.traffic_split.update(traffic_split)

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.undeploy_model,
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

        # Wrap the response in an operation future.
        response = operation_async.from_gapic(
            response,
            self._client._transport.operations_client,
            endpoint_service.UndeployModelResponse,
            metadata_type=endpoint_service.UndeployModelOperationMetadata,
        )

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


__all__ = ("EndpointServiceAsyncClient",)
