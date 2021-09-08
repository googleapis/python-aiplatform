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
from google.cloud.aiplatform_v1.services.index_endpoint_service import pagers
from google.cloud.aiplatform_v1.types import index_endpoint
from google.cloud.aiplatform_v1.types import index_endpoint as gca_index_endpoint
from google.cloud.aiplatform_v1.types import index_endpoint_service
from google.cloud.aiplatform_v1.types import operation as gca_operation
from google.protobuf import empty_pb2  # type: ignore
from google.protobuf import field_mask_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
from .transports.base import IndexEndpointServiceTransport, DEFAULT_CLIENT_INFO
from .transports.grpc_asyncio import IndexEndpointServiceGrpcAsyncIOTransport
from .client import IndexEndpointServiceClient


class IndexEndpointServiceAsyncClient:
    """A service for managing Vertex AI's IndexEndpoints."""

    _client: IndexEndpointServiceClient

    DEFAULT_ENDPOINT = IndexEndpointServiceClient.DEFAULT_ENDPOINT
    DEFAULT_MTLS_ENDPOINT = IndexEndpointServiceClient.DEFAULT_MTLS_ENDPOINT

    index_path = staticmethod(IndexEndpointServiceClient.index_path)
    parse_index_path = staticmethod(IndexEndpointServiceClient.parse_index_path)
    index_endpoint_path = staticmethod(IndexEndpointServiceClient.index_endpoint_path)
    parse_index_endpoint_path = staticmethod(
        IndexEndpointServiceClient.parse_index_endpoint_path
    )
    common_billing_account_path = staticmethod(
        IndexEndpointServiceClient.common_billing_account_path
    )
    parse_common_billing_account_path = staticmethod(
        IndexEndpointServiceClient.parse_common_billing_account_path
    )
    common_folder_path = staticmethod(IndexEndpointServiceClient.common_folder_path)
    parse_common_folder_path = staticmethod(
        IndexEndpointServiceClient.parse_common_folder_path
    )
    common_organization_path = staticmethod(
        IndexEndpointServiceClient.common_organization_path
    )
    parse_common_organization_path = staticmethod(
        IndexEndpointServiceClient.parse_common_organization_path
    )
    common_project_path = staticmethod(IndexEndpointServiceClient.common_project_path)
    parse_common_project_path = staticmethod(
        IndexEndpointServiceClient.parse_common_project_path
    )
    common_location_path = staticmethod(IndexEndpointServiceClient.common_location_path)
    parse_common_location_path = staticmethod(
        IndexEndpointServiceClient.parse_common_location_path
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
            IndexEndpointServiceAsyncClient: The constructed client.
        """
        return IndexEndpointServiceClient.from_service_account_info.__func__(IndexEndpointServiceAsyncClient, info, *args, **kwargs)  # type: ignore

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
            IndexEndpointServiceAsyncClient: The constructed client.
        """
        return IndexEndpointServiceClient.from_service_account_file.__func__(IndexEndpointServiceAsyncClient, filename, *args, **kwargs)  # type: ignore

    from_service_account_json = from_service_account_file

    @property
    def transport(self) -> IndexEndpointServiceTransport:
        """Returns the transport used by the client instance.

        Returns:
            IndexEndpointServiceTransport: The transport used by the client instance.
        """
        return self._client.transport

    get_transport_class = functools.partial(
        type(IndexEndpointServiceClient).get_transport_class,
        type(IndexEndpointServiceClient),
    )

    def __init__(
        self,
        *,
        credentials: ga_credentials.Credentials = None,
        transport: Union[str, IndexEndpointServiceTransport] = "grpc_asyncio",
        client_options: ClientOptions = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
    ) -> None:
        """Instantiates the index endpoint service client.

        Args:
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            transport (Union[str, ~.IndexEndpointServiceTransport]): The
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
        self._client = IndexEndpointServiceClient(
            credentials=credentials,
            transport=transport,
            client_options=client_options,
            client_info=client_info,
        )

    async def create_index_endpoint(
        self,
        request: index_endpoint_service.CreateIndexEndpointRequest = None,
        *,
        parent: str = None,
        index_endpoint: gca_index_endpoint.IndexEndpoint = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Creates an IndexEndpoint.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.CreateIndexEndpointRequest`):
                The request object. Request message for
                [IndexEndpointService.CreateIndexEndpoint][google.cloud.aiplatform.v1.IndexEndpointService.CreateIndexEndpoint].
            parent (:class:`str`):
                Required. The resource name of the Location to create
                the IndexEndpoint in. Format:
                ``projects/{project}/locations/{location}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            index_endpoint (:class:`google.cloud.aiplatform_v1.types.IndexEndpoint`):
                Required. The IndexEndpoint to
                create.

                This corresponds to the ``index_endpoint`` field
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

                The result type for the operation will be :class:`google.cloud.aiplatform_v1.types.IndexEndpoint` Indexes are deployed into it. An IndexEndpoint can have multiple
                   DeployedIndexes.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, index_endpoint])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = index_endpoint_service.CreateIndexEndpointRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if index_endpoint is not None:
            request.index_endpoint = index_endpoint

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_index_endpoint,
            default_timeout=None,
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
            gca_index_endpoint.IndexEndpoint,
            metadata_type=index_endpoint_service.CreateIndexEndpointOperationMetadata,
        )

        # Done; return the response.
        return response

    async def get_index_endpoint(
        self,
        request: index_endpoint_service.GetIndexEndpointRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> index_endpoint.IndexEndpoint:
        r"""Gets an IndexEndpoint.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.GetIndexEndpointRequest`):
                The request object. Request message for
                [IndexEndpointService.GetIndexEndpoint][google.cloud.aiplatform.v1.IndexEndpointService.GetIndexEndpoint]
            name (:class:`str`):
                Required. The name of the IndexEndpoint resource.
                Format:
                ``projects/{project}/locations/{location}/indexEndpoints/{index_endpoint}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.types.IndexEndpoint:
                Indexes are deployed into it. An
                IndexEndpoint can have multiple
                DeployedIndexes.

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

        request = index_endpoint_service.GetIndexEndpointRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_index_endpoint,
            default_timeout=None,
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

    async def list_index_endpoints(
        self,
        request: index_endpoint_service.ListIndexEndpointsRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListIndexEndpointsAsyncPager:
        r"""Lists IndexEndpoints in a Location.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.ListIndexEndpointsRequest`):
                The request object. Request message for
                [IndexEndpointService.ListIndexEndpoints][google.cloud.aiplatform.v1.IndexEndpointService.ListIndexEndpoints].
            parent (:class:`str`):
                Required. The resource name of the Location from which
                to list the IndexEndpoints. Format:
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
            google.cloud.aiplatform_v1.services.index_endpoint_service.pagers.ListIndexEndpointsAsyncPager:
                Response message for
                [IndexEndpointService.ListIndexEndpoints][google.cloud.aiplatform.v1.IndexEndpointService.ListIndexEndpoints].

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

        request = index_endpoint_service.ListIndexEndpointsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_index_endpoints,
            default_timeout=None,
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
        response = pagers.ListIndexEndpointsAsyncPager(
            method=rpc, request=request, response=response, metadata=metadata,
        )

        # Done; return the response.
        return response

    async def update_index_endpoint(
        self,
        request: index_endpoint_service.UpdateIndexEndpointRequest = None,
        *,
        index_endpoint: gca_index_endpoint.IndexEndpoint = None,
        update_mask: field_mask_pb2.FieldMask = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_index_endpoint.IndexEndpoint:
        r"""Updates an IndexEndpoint.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.UpdateIndexEndpointRequest`):
                The request object. Request message for
                [IndexEndpointService.UpdateIndexEndpoint][google.cloud.aiplatform.v1.IndexEndpointService.UpdateIndexEndpoint].
            index_endpoint (:class:`google.cloud.aiplatform_v1.types.IndexEndpoint`):
                Required. The IndexEndpoint which
                replaces the resource on the server.

                This corresponds to the ``index_endpoint`` field
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
            google.cloud.aiplatform_v1.types.IndexEndpoint:
                Indexes are deployed into it. An
                IndexEndpoint can have multiple
                DeployedIndexes.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([index_endpoint, update_mask])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = index_endpoint_service.UpdateIndexEndpointRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if index_endpoint is not None:
            request.index_endpoint = index_endpoint
        if update_mask is not None:
            request.update_mask = update_mask

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.update_index_endpoint,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("index_endpoint.name", request.index_endpoint.name),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def delete_index_endpoint(
        self,
        request: index_endpoint_service.DeleteIndexEndpointRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Deletes an IndexEndpoint.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.DeleteIndexEndpointRequest`):
                The request object. Request message for
                [IndexEndpointService.DeleteIndexEndpoint][google.cloud.aiplatform.v1.IndexEndpointService.DeleteIndexEndpoint].
            name (:class:`str`):
                Required. The name of the IndexEndpoint resource to be
                deleted. Format:
                ``projects/{project}/locations/{location}/indexEndpoints/{index_endpoint}``

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

        request = index_endpoint_service.DeleteIndexEndpointRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.delete_index_endpoint,
            default_timeout=None,
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

    async def deploy_index(
        self,
        request: index_endpoint_service.DeployIndexRequest = None,
        *,
        index_endpoint: str = None,
        deployed_index: gca_index_endpoint.DeployedIndex = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Deploys an Index into this IndexEndpoint, creating a
        DeployedIndex within it.
        Only non-empty Indexes can be deployed.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.DeployIndexRequest`):
                The request object. Request message for
                [IndexEndpointService.DeployIndex][google.cloud.aiplatform.v1.IndexEndpointService.DeployIndex].
            index_endpoint (:class:`str`):
                Required. The name of the IndexEndpoint resource into
                which to deploy an Index. Format:
                ``projects/{project}/locations/{location}/indexEndpoints/{index_endpoint}``

                This corresponds to the ``index_endpoint`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            deployed_index (:class:`google.cloud.aiplatform_v1.types.DeployedIndex`):
                Required. The DeployedIndex to be
                created within the IndexEndpoint.

                This corresponds to the ``deployed_index`` field
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
                :class:`google.cloud.aiplatform_v1.types.DeployIndexResponse`
                Response message for
                [IndexEndpointService.DeployIndex][google.cloud.aiplatform.v1.IndexEndpointService.DeployIndex].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([index_endpoint, deployed_index])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = index_endpoint_service.DeployIndexRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if index_endpoint is not None:
            request.index_endpoint = index_endpoint
        if deployed_index is not None:
            request.deployed_index = deployed_index

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.deploy_index,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("index_endpoint", request.index_endpoint),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = operation_async.from_gapic(
            response,
            self._client._transport.operations_client,
            index_endpoint_service.DeployIndexResponse,
            metadata_type=index_endpoint_service.DeployIndexOperationMetadata,
        )

        # Done; return the response.
        return response

    async def undeploy_index(
        self,
        request: index_endpoint_service.UndeployIndexRequest = None,
        *,
        index_endpoint: str = None,
        deployed_index_id: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Undeploys an Index from an IndexEndpoint, removing a
        DeployedIndex from it, and freeing all resources it's
        using.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.UndeployIndexRequest`):
                The request object. Request message for
                [IndexEndpointService.UndeployIndex][google.cloud.aiplatform.v1.IndexEndpointService.UndeployIndex].
            index_endpoint (:class:`str`):
                Required. The name of the IndexEndpoint resource from
                which to undeploy an Index. Format:
                ``projects/{project}/locations/{location}/indexEndpoints/{index_endpoint}``

                This corresponds to the ``index_endpoint`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            deployed_index_id (:class:`str`):
                Required. The ID of the DeployedIndex
                to be undeployed from the IndexEndpoint.

                This corresponds to the ``deployed_index_id`` field
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
                :class:`google.cloud.aiplatform_v1.types.UndeployIndexResponse`
                Response message for
                [IndexEndpointService.UndeployIndex][google.cloud.aiplatform.v1.IndexEndpointService.UndeployIndex].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([index_endpoint, deployed_index_id])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = index_endpoint_service.UndeployIndexRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if index_endpoint is not None:
            request.index_endpoint = index_endpoint
        if deployed_index_id is not None:
            request.deployed_index_id = deployed_index_id

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.undeploy_index,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("index_endpoint", request.index_endpoint),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = operation_async.from_gapic(
            response,
            self._client._transport.operations_client,
            index_endpoint_service.UndeployIndexResponse,
            metadata_type=index_endpoint_service.UndeployIndexOperationMetadata,
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


__all__ = ("IndexEndpointServiceAsyncClient",)
