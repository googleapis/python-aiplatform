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
from google.cloud.aiplatform_v1beta1.services.metadata_service import pagers
from google.cloud.aiplatform_v1beta1.types import artifact
from google.cloud.aiplatform_v1beta1.types import artifact as gca_artifact
from google.cloud.aiplatform_v1beta1.types import context
from google.cloud.aiplatform_v1beta1.types import context as gca_context
from google.cloud.aiplatform_v1beta1.types import encryption_spec
from google.cloud.aiplatform_v1beta1.types import event
from google.cloud.aiplatform_v1beta1.types import execution
from google.cloud.aiplatform_v1beta1.types import execution as gca_execution
from google.cloud.aiplatform_v1beta1.types import lineage_subgraph
from google.cloud.aiplatform_v1beta1.types import metadata_schema
from google.cloud.aiplatform_v1beta1.types import metadata_schema as gca_metadata_schema
from google.cloud.aiplatform_v1beta1.types import metadata_service
from google.cloud.aiplatform_v1beta1.types import metadata_store
from google.cloud.aiplatform_v1beta1.types import metadata_store as gca_metadata_store
from google.cloud.aiplatform_v1beta1.types import operation as gca_operation
from google.protobuf import empty_pb2  # type: ignore
from google.protobuf import field_mask_pb2  # type: ignore
from google.protobuf import struct_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
from .transports.base import MetadataServiceTransport, DEFAULT_CLIENT_INFO
from .transports.grpc_asyncio import MetadataServiceGrpcAsyncIOTransport
from .client import MetadataServiceClient


class MetadataServiceAsyncClient:
    """Service for reading and writing metadata entries."""

    _client: MetadataServiceClient

    DEFAULT_ENDPOINT = MetadataServiceClient.DEFAULT_ENDPOINT
    DEFAULT_MTLS_ENDPOINT = MetadataServiceClient.DEFAULT_MTLS_ENDPOINT

    artifact_path = staticmethod(MetadataServiceClient.artifact_path)
    parse_artifact_path = staticmethod(MetadataServiceClient.parse_artifact_path)
    context_path = staticmethod(MetadataServiceClient.context_path)
    parse_context_path = staticmethod(MetadataServiceClient.parse_context_path)
    execution_path = staticmethod(MetadataServiceClient.execution_path)
    parse_execution_path = staticmethod(MetadataServiceClient.parse_execution_path)
    metadata_schema_path = staticmethod(MetadataServiceClient.metadata_schema_path)
    parse_metadata_schema_path = staticmethod(
        MetadataServiceClient.parse_metadata_schema_path
    )
    metadata_store_path = staticmethod(MetadataServiceClient.metadata_store_path)
    parse_metadata_store_path = staticmethod(
        MetadataServiceClient.parse_metadata_store_path
    )
    common_billing_account_path = staticmethod(
        MetadataServiceClient.common_billing_account_path
    )
    parse_common_billing_account_path = staticmethod(
        MetadataServiceClient.parse_common_billing_account_path
    )
    common_folder_path = staticmethod(MetadataServiceClient.common_folder_path)
    parse_common_folder_path = staticmethod(
        MetadataServiceClient.parse_common_folder_path
    )
    common_organization_path = staticmethod(
        MetadataServiceClient.common_organization_path
    )
    parse_common_organization_path = staticmethod(
        MetadataServiceClient.parse_common_organization_path
    )
    common_project_path = staticmethod(MetadataServiceClient.common_project_path)
    parse_common_project_path = staticmethod(
        MetadataServiceClient.parse_common_project_path
    )
    common_location_path = staticmethod(MetadataServiceClient.common_location_path)
    parse_common_location_path = staticmethod(
        MetadataServiceClient.parse_common_location_path
    )

    @classmethod
    def from_service_account_info(cls, info: dict, *args, **kwargs):
        """Creates an instance of this client using the provided credentials info.

        Args:
            info (dict): The service account private key info.
            args: Additional arguments to pass to the constructor.
            kwargs: Additional arguments to pass to the constructor.

        Returns:
            MetadataServiceAsyncClient: The constructed client.
        """
        return MetadataServiceClient.from_service_account_info.__func__(MetadataServiceAsyncClient, info, *args, **kwargs)  # type: ignore

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
            MetadataServiceAsyncClient: The constructed client.
        """
        return MetadataServiceClient.from_service_account_file.__func__(MetadataServiceAsyncClient, filename, *args, **kwargs)  # type: ignore

    from_service_account_json = from_service_account_file

    @property
    def transport(self) -> MetadataServiceTransport:
        """Return the transport used by the client instance.

        Returns:
            MetadataServiceTransport: The transport used by the client instance.
        """
        return self._client.transport

    get_transport_class = functools.partial(
        type(MetadataServiceClient).get_transport_class, type(MetadataServiceClient)
    )

    def __init__(
        self,
        *,
        credentials: ga_credentials.Credentials = None,
        transport: Union[str, MetadataServiceTransport] = "grpc_asyncio",
        client_options: ClientOptions = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
    ) -> None:
        """Instantiate the metadata service client.

        Args:
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            transport (Union[str, ~.MetadataServiceTransport]): The
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
        self._client = MetadataServiceClient(
            credentials=credentials,
            transport=transport,
            client_options=client_options,
            client_info=client_info,
        )

    async def create_metadata_store(
        self,
        request: metadata_service.CreateMetadataStoreRequest = None,
        *,
        parent: str = None,
        metadata_store: gca_metadata_store.MetadataStore = None,
        metadata_store_id: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Initializes a MetadataStore, including allocation of
        resources.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.CreateMetadataStoreRequest`):
                The request object. Request message for
                [MetadataService.CreateMetadataStore][google.cloud.aiplatform.v1beta1.MetadataService.CreateMetadataStore].
            parent (:class:`str`):
                Required. The resource name of the
                Location where the MetadataStore should
                be created. Format:
                projects/{project}/locations/{location}/

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            metadata_store (:class:`google.cloud.aiplatform_v1beta1.types.MetadataStore`):
                Required. The MetadataStore to
                create.

                This corresponds to the ``metadata_store`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            metadata_store_id (:class:`str`):
                The {metadatastore} portion of the resource name with
                the format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}
                If not provided, the MetadataStore's ID will be a UUID
                generated by the service. Must be 4-128 characters in
                length. Valid characters are /[a-z][0-9]-/. Must be
                unique across all MetadataStores in the parent Location.
                (Otherwise the request will fail with ALREADY_EXISTS, or
                PERMISSION_DENIED if the caller can't view the
                preexisting MetadataStore.)

                This corresponds to the ``metadata_store_id`` field
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

                The result type for the operation will be :class:`google.cloud.aiplatform_v1beta1.types.MetadataStore` Instance of a metadata store. Contains a set of metadata that can be
                   queried.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, metadata_store, metadata_store_id])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = metadata_service.CreateMetadataStoreRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if metadata_store is not None:
            request.metadata_store = metadata_store
        if metadata_store_id is not None:
            request.metadata_store_id = metadata_store_id

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_metadata_store,
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
            gca_metadata_store.MetadataStore,
            metadata_type=metadata_service.CreateMetadataStoreOperationMetadata,
        )

        # Done; return the response.
        return response

    async def get_metadata_store(
        self,
        request: metadata_service.GetMetadataStoreRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> metadata_store.MetadataStore:
        r"""Retrieves a specific MetadataStore.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.GetMetadataStoreRequest`):
                The request object. Request message for
                [MetadataService.GetMetadataStore][google.cloud.aiplatform.v1beta1.MetadataService.GetMetadataStore].
            name (:class:`str`):
                Required. The resource name of the
                MetadataStore to retrieve. Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.MetadataStore:
                Instance of a metadata store.
                Contains a set of metadata that can be
                queried.

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

        request = metadata_service.GetMetadataStoreRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_metadata_store,
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

    async def list_metadata_stores(
        self,
        request: metadata_service.ListMetadataStoresRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListMetadataStoresAsyncPager:
        r"""Lists MetadataStores for a Location.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.ListMetadataStoresRequest`):
                The request object. Request message for
                [MetadataService.ListMetadataStores][google.cloud.aiplatform.v1beta1.MetadataService.ListMetadataStores].
            parent (:class:`str`):
                Required. The Location whose
                MetadataStores should be listed. Format:
                projects/{project}/locations/{location}

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.services.metadata_service.pagers.ListMetadataStoresAsyncPager:
                Response message for
                [MetadataService.ListMetadataStores][google.cloud.aiplatform.v1beta1.MetadataService.ListMetadataStores].

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

        request = metadata_service.ListMetadataStoresRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_metadata_stores,
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
        response = pagers.ListMetadataStoresAsyncPager(
            method=rpc, request=request, response=response, metadata=metadata,
        )

        # Done; return the response.
        return response

    async def delete_metadata_store(
        self,
        request: metadata_service.DeleteMetadataStoreRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Deletes a single MetadataStore.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.DeleteMetadataStoreRequest`):
                The request object. Request message for
                [MetadataService.DeleteMetadataStore][google.cloud.aiplatform.v1beta1.MetadataService.DeleteMetadataStore].
            name (:class:`str`):
                Required. The resource name of the
                MetadataStore to delete. Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}

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

        request = metadata_service.DeleteMetadataStoreRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.delete_metadata_store,
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
            metadata_type=metadata_service.DeleteMetadataStoreOperationMetadata,
        )

        # Done; return the response.
        return response

    async def create_artifact(
        self,
        request: metadata_service.CreateArtifactRequest = None,
        *,
        parent: str = None,
        artifact: gca_artifact.Artifact = None,
        artifact_id: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_artifact.Artifact:
        r"""Creates an Artifact associated with a MetadataStore.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.CreateArtifactRequest`):
                The request object. Request message for
                [MetadataService.CreateArtifact][google.cloud.aiplatform.v1beta1.MetadataService.CreateArtifact].
            parent (:class:`str`):
                Required. The resource name of the
                MetadataStore where the Artifact should
                be created. Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            artifact (:class:`google.cloud.aiplatform_v1beta1.types.Artifact`):
                Required. The Artifact to create.
                This corresponds to the ``artifact`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            artifact_id (:class:`str`):
                The {artifact} portion of the resource name with the
                format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}/artifacts/{artifact}
                If not provided, the Artifact's ID will be a UUID
                generated by the service. Must be 4-128 characters in
                length. Valid characters are /[a-z][0-9]-/. Must be
                unique across all Artifacts in the parent MetadataStore.
                (Otherwise the request will fail with ALREADY_EXISTS, or
                PERMISSION_DENIED if the caller can't view the
                preexisting Artifact.)

                This corresponds to the ``artifact_id`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.Artifact:
                Instance of a general artifact.
        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, artifact, artifact_id])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = metadata_service.CreateArtifactRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if artifact is not None:
            request.artifact = artifact
        if artifact_id is not None:
            request.artifact_id = artifact_id

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_artifact,
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

        # Done; return the response.
        return response

    async def get_artifact(
        self,
        request: metadata_service.GetArtifactRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> artifact.Artifact:
        r"""Retrieves a specific Artifact.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.GetArtifactRequest`):
                The request object. Request message for
                [MetadataService.GetArtifact][google.cloud.aiplatform.v1beta1.MetadataService.GetArtifact].
            name (:class:`str`):
                Required. The resource name of the
                Artifact to retrieve. Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}/artifacts/{artifact}

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.Artifact:
                Instance of a general artifact.
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

        request = metadata_service.GetArtifactRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_artifact,
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

    async def list_artifacts(
        self,
        request: metadata_service.ListArtifactsRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListArtifactsAsyncPager:
        r"""Lists Artifacts in the MetadataStore.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.ListArtifactsRequest`):
                The request object. Request message for
                [MetadataService.ListArtifacts][google.cloud.aiplatform.v1beta1.MetadataService.ListArtifacts].
            parent (:class:`str`):
                Required. The MetadataStore whose
                Artifacts should be listed. Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.services.metadata_service.pagers.ListArtifactsAsyncPager:
                Response message for
                [MetadataService.ListArtifacts][google.cloud.aiplatform.v1beta1.MetadataService.ListArtifacts].

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

        request = metadata_service.ListArtifactsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_artifacts,
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
        response = pagers.ListArtifactsAsyncPager(
            method=rpc, request=request, response=response, metadata=metadata,
        )

        # Done; return the response.
        return response

    async def update_artifact(
        self,
        request: metadata_service.UpdateArtifactRequest = None,
        *,
        artifact: gca_artifact.Artifact = None,
        update_mask: field_mask_pb2.FieldMask = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_artifact.Artifact:
        r"""Updates a stored Artifact.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.UpdateArtifactRequest`):
                The request object. Request message for
                [MetadataService.UpdateArtifact][google.cloud.aiplatform.v1beta1.MetadataService.UpdateArtifact].
            artifact (:class:`google.cloud.aiplatform_v1beta1.types.Artifact`):
                Required. The Artifact containing updates. The
                Artifact's
                [Artifact.name][google.cloud.aiplatform.v1beta1.Artifact.name]
                field is used to identify the Artifact to be updated.
                Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}/artifacts/{artifact}

                This corresponds to the ``artifact`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            update_mask (:class:`google.protobuf.field_mask_pb2.FieldMask`):
                Required. A FieldMask indicating
                which fields should be updated.

                This corresponds to the ``update_mask`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.Artifact:
                Instance of a general artifact.
        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([artifact, update_mask])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = metadata_service.UpdateArtifactRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if artifact is not None:
            request.artifact = artifact
        if update_mask is not None:
            request.update_mask = update_mask

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.update_artifact,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("artifact.name", request.artifact.name),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def create_context(
        self,
        request: metadata_service.CreateContextRequest = None,
        *,
        parent: str = None,
        context: gca_context.Context = None,
        context_id: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_context.Context:
        r"""Creates a Context associated with a MetadataStore.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.CreateContextRequest`):
                The request object. Request message for
                [MetadataService.CreateContext][google.cloud.aiplatform.v1beta1.MetadataService.CreateContext].
            parent (:class:`str`):
                Required. The resource name of the
                MetadataStore where the Context should
                be created. Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            context (:class:`google.cloud.aiplatform_v1beta1.types.Context`):
                Required. The Context to create.
                This corresponds to the ``context`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            context_id (:class:`str`):
                The {context} portion of the resource name with the
                format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}/contexts/{context}
                If not provided, the Context's ID will be a UUID
                generated by the service. Must be 4-128 characters in
                length. Valid characters are /[a-z][0-9]-/. Must be
                unique across all Contexts in the parent MetadataStore.
                (Otherwise the request will fail with ALREADY_EXISTS, or
                PERMISSION_DENIED if the caller can't view the
                preexisting Context.)

                This corresponds to the ``context_id`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.Context:
                Instance of a general context.
        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, context, context_id])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = metadata_service.CreateContextRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if context is not None:
            request.context = context
        if context_id is not None:
            request.context_id = context_id

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_context,
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

        # Done; return the response.
        return response

    async def get_context(
        self,
        request: metadata_service.GetContextRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> context.Context:
        r"""Retrieves a specific Context.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.GetContextRequest`):
                The request object. Request message for
                [MetadataService.GetContext][google.cloud.aiplatform.v1beta1.MetadataService.GetContext].
            name (:class:`str`):
                Required. The resource name of the
                Context to retrieve. Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}/contexts/{context}

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.Context:
                Instance of a general context.
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

        request = metadata_service.GetContextRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_context,
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

    async def list_contexts(
        self,
        request: metadata_service.ListContextsRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListContextsAsyncPager:
        r"""Lists Contexts on the MetadataStore.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.ListContextsRequest`):
                The request object. Request message for
                [MetadataService.ListContexts][google.cloud.aiplatform.v1beta1.MetadataService.ListContexts]
            parent (:class:`str`):
                Required. The MetadataStore whose
                Contexts should be listed. Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.services.metadata_service.pagers.ListContextsAsyncPager:
                Response message for
                [MetadataService.ListContexts][google.cloud.aiplatform.v1beta1.MetadataService.ListContexts].

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

        request = metadata_service.ListContextsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_contexts,
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
        response = pagers.ListContextsAsyncPager(
            method=rpc, request=request, response=response, metadata=metadata,
        )

        # Done; return the response.
        return response

    async def update_context(
        self,
        request: metadata_service.UpdateContextRequest = None,
        *,
        context: gca_context.Context = None,
        update_mask: field_mask_pb2.FieldMask = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_context.Context:
        r"""Updates a stored Context.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.UpdateContextRequest`):
                The request object. Request message for
                [MetadataService.UpdateContext][google.cloud.aiplatform.v1beta1.MetadataService.UpdateContext].
            context (:class:`google.cloud.aiplatform_v1beta1.types.Context`):
                Required. The Context containing updates. The Context's
                [Context.name][google.cloud.aiplatform.v1beta1.Context.name]
                field is used to identify the Context to be updated.
                Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}/contexts/{context}

                This corresponds to the ``context`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            update_mask (:class:`google.protobuf.field_mask_pb2.FieldMask`):
                Required. A FieldMask indicating
                which fields should be updated.

                This corresponds to the ``update_mask`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.Context:
                Instance of a general context.
        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([context, update_mask])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = metadata_service.UpdateContextRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if context is not None:
            request.context = context
        if update_mask is not None:
            request.update_mask = update_mask

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.update_context,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("context.name", request.context.name),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def delete_context(
        self,
        request: metadata_service.DeleteContextRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Deletes a stored Context.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.DeleteContextRequest`):
                The request object. Request message for
                [MetadataService.DeleteContext][google.cloud.aiplatform.v1beta1.MetadataService.DeleteContext].
            name (:class:`str`):
                Required. The resource name of the
                Context to retrieve. Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}/contexts/{context}

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

        request = metadata_service.DeleteContextRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.delete_context,
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

    async def add_context_artifacts_and_executions(
        self,
        request: metadata_service.AddContextArtifactsAndExecutionsRequest = None,
        *,
        context: str = None,
        artifacts: Sequence[str] = None,
        executions: Sequence[str] = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> metadata_service.AddContextArtifactsAndExecutionsResponse:
        r"""Adds a set of Artifacts and Executions to a Context.
        If any of the Artifacts or Executions have already been
        added to a Context, they are simply skipped.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.AddContextArtifactsAndExecutionsRequest`):
                The request object. Request message for
                [MetadataService.AddContextArtifactsAndExecutions][google.cloud.aiplatform.v1beta1.MetadataService.AddContextArtifactsAndExecutions].
            context (:class:`str`):
                Required. The resource name of the
                Context that the Artifacts and
                Executions belong to. Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}/contexts/{context}

                This corresponds to the ``context`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            artifacts (:class:`Sequence[str]`):
                The resource names of the Artifacts
                to attribute to the Context.

                This corresponds to the ``artifacts`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            executions (:class:`Sequence[str]`):
                The resource names of the Executions
                to associate with the Context.

                This corresponds to the ``executions`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.AddContextArtifactsAndExecutionsResponse:
                Response message for
                [MetadataService.AddContextArtifactsAndExecutions][google.cloud.aiplatform.v1beta1.MetadataService.AddContextArtifactsAndExecutions].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([context, artifacts, executions])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = metadata_service.AddContextArtifactsAndExecutionsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if context is not None:
            request.context = context
        if artifacts:
            request.artifacts.extend(artifacts)
        if executions:
            request.executions.extend(executions)

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.add_context_artifacts_and_executions,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("context", request.context),)),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def add_context_children(
        self,
        request: metadata_service.AddContextChildrenRequest = None,
        *,
        context: str = None,
        child_contexts: Sequence[str] = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> metadata_service.AddContextChildrenResponse:
        r"""Adds a set of Contexts as children to a parent Context. If any
        of the child Contexts have already been added to the parent
        Context, they are simply skipped. If this call would create a
        cycle or cause any Context to have more than 10 parents, the
        request will fail with INVALID_ARGUMENT error.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.AddContextChildrenRequest`):
                The request object. Request message for
                [MetadataService.AddContextChildren][google.cloud.aiplatform.v1beta1.MetadataService.AddContextChildren].
            context (:class:`str`):
                Required. The resource name of the
                parent Context. Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}/contexts/{context}

                This corresponds to the ``context`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            child_contexts (:class:`Sequence[str]`):
                The resource names of the child
                Contexts.

                This corresponds to the ``child_contexts`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.AddContextChildrenResponse:
                Response message for
                [MetadataService.AddContextChildren][google.cloud.aiplatform.v1beta1.MetadataService.AddContextChildren].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([context, child_contexts])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = metadata_service.AddContextChildrenRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if context is not None:
            request.context = context
        if child_contexts:
            request.child_contexts.extend(child_contexts)

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.add_context_children,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("context", request.context),)),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def query_context_lineage_subgraph(
        self,
        request: metadata_service.QueryContextLineageSubgraphRequest = None,
        *,
        context: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> lineage_subgraph.LineageSubgraph:
        r"""Retrieves Artifacts and Executions within the
        specified Context, connected by Event edges and returned
        as a LineageSubgraph.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.QueryContextLineageSubgraphRequest`):
                The request object. Request message for
                [MetadataService.QueryContextLineageSubgraph][google.cloud.aiplatform.v1beta1.MetadataService.QueryContextLineageSubgraph].
            context (:class:`str`):
                Required. The resource name of the Context whose
                Artifacts and Executions should be retrieved as a
                LineageSubgraph. Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}/contexts/{context}

                The request may error with FAILED_PRECONDITION if the
                number of Artifacts, the number of Executions, or the
                number of Events that would be returned for the Context
                exceeds 1000.

                This corresponds to the ``context`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.LineageSubgraph:
                A subgraph of the overall lineage
                graph. Event edges connect Artifact and
                Execution nodes.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([context])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = metadata_service.QueryContextLineageSubgraphRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if context is not None:
            request.context = context

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.query_context_lineage_subgraph,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("context", request.context),)),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def create_execution(
        self,
        request: metadata_service.CreateExecutionRequest = None,
        *,
        parent: str = None,
        execution: gca_execution.Execution = None,
        execution_id: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_execution.Execution:
        r"""Creates an Execution associated with a MetadataStore.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.CreateExecutionRequest`):
                The request object. Request message for
                [MetadataService.CreateExecution][google.cloud.aiplatform.v1beta1.MetadataService.CreateExecution].
            parent (:class:`str`):
                Required. The resource name of the
                MetadataStore where the Execution should
                be created. Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            execution (:class:`google.cloud.aiplatform_v1beta1.types.Execution`):
                Required. The Execution to create.
                This corresponds to the ``execution`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            execution_id (:class:`str`):
                The {execution} portion of the resource name with the
                format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}/executions/{execution}
                If not provided, the Execution's ID will be a UUID
                generated by the service. Must be 4-128 characters in
                length. Valid characters are /[a-z][0-9]-/. Must be
                unique across all Executions in the parent
                MetadataStore. (Otherwise the request will fail with
                ALREADY_EXISTS, or PERMISSION_DENIED if the caller can't
                view the preexisting Execution.)

                This corresponds to the ``execution_id`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.Execution:
                Instance of a general execution.
        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, execution, execution_id])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = metadata_service.CreateExecutionRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if execution is not None:
            request.execution = execution
        if execution_id is not None:
            request.execution_id = execution_id

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_execution,
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

        # Done; return the response.
        return response

    async def get_execution(
        self,
        request: metadata_service.GetExecutionRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> execution.Execution:
        r"""Retrieves a specific Execution.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.GetExecutionRequest`):
                The request object. Request message for
                [MetadataService.GetExecution][google.cloud.aiplatform.v1beta1.MetadataService.GetExecution].
            name (:class:`str`):
                Required. The resource name of the
                Execution to retrieve. Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}/executions/{execution}

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.Execution:
                Instance of a general execution.
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

        request = metadata_service.GetExecutionRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_execution,
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

    async def list_executions(
        self,
        request: metadata_service.ListExecutionsRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListExecutionsAsyncPager:
        r"""Lists Executions in the MetadataStore.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.ListExecutionsRequest`):
                The request object. Request message for
                [MetadataService.ListExecutions][google.cloud.aiplatform.v1beta1.MetadataService.ListExecutions].
            parent (:class:`str`):
                Required. The MetadataStore whose
                Executions should be listed. Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.services.metadata_service.pagers.ListExecutionsAsyncPager:
                Response message for
                [MetadataService.ListExecutions][google.cloud.aiplatform.v1beta1.MetadataService.ListExecutions].

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

        request = metadata_service.ListExecutionsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_executions,
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
        response = pagers.ListExecutionsAsyncPager(
            method=rpc, request=request, response=response, metadata=metadata,
        )

        # Done; return the response.
        return response

    async def update_execution(
        self,
        request: metadata_service.UpdateExecutionRequest = None,
        *,
        execution: gca_execution.Execution = None,
        update_mask: field_mask_pb2.FieldMask = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_execution.Execution:
        r"""Updates a stored Execution.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.UpdateExecutionRequest`):
                The request object. Request message for
                [MetadataService.UpdateExecution][google.cloud.aiplatform.v1beta1.MetadataService.UpdateExecution].
            execution (:class:`google.cloud.aiplatform_v1beta1.types.Execution`):
                Required. The Execution containing updates. The
                Execution's
                [Execution.name][google.cloud.aiplatform.v1beta1.Execution.name]
                field is used to identify the Execution to be updated.
                Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}/executions/{execution}

                This corresponds to the ``execution`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            update_mask (:class:`google.protobuf.field_mask_pb2.FieldMask`):
                Required. A FieldMask indicating
                which fields should be updated.

                This corresponds to the ``update_mask`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.Execution:
                Instance of a general execution.
        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([execution, update_mask])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = metadata_service.UpdateExecutionRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if execution is not None:
            request.execution = execution
        if update_mask is not None:
            request.update_mask = update_mask

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.update_execution,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("execution.name", request.execution.name),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def add_execution_events(
        self,
        request: metadata_service.AddExecutionEventsRequest = None,
        *,
        execution: str = None,
        events: Sequence[event.Event] = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> metadata_service.AddExecutionEventsResponse:
        r"""Adds Events for denoting whether each Artifact was an
        input or output for a given Execution. If any Events
        already exist between the Execution and any of the
        specified Artifacts they are simply skipped.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.AddExecutionEventsRequest`):
                The request object. Request message for
                [MetadataService.AddExecutionEvents][google.cloud.aiplatform.v1beta1.MetadataService.AddExecutionEvents].
            execution (:class:`str`):
                Required. The resource name of the
                Execution that the Events connect
                Artifacts with. Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}/executions/{execution}

                This corresponds to the ``execution`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            events (:class:`Sequence[google.cloud.aiplatform_v1beta1.types.Event]`):
                The Events to create and add.
                This corresponds to the ``events`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.AddExecutionEventsResponse:
                Response message for
                [MetadataService.AddExecutionEvents][google.cloud.aiplatform.v1beta1.MetadataService.AddExecutionEvents].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([execution, events])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = metadata_service.AddExecutionEventsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if execution is not None:
            request.execution = execution
        if events:
            request.events.extend(events)

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.add_execution_events,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("execution", request.execution),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def query_execution_inputs_and_outputs(
        self,
        request: metadata_service.QueryExecutionInputsAndOutputsRequest = None,
        *,
        execution: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> lineage_subgraph.LineageSubgraph:
        r"""Obtains the set of input and output Artifacts for
        this Execution, in the form of LineageSubgraph that also
        contains the Execution and connecting Events.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.QueryExecutionInputsAndOutputsRequest`):
                The request object. Request message for
                [MetadataService.QueryExecutionInputsAndOutputs][google.cloud.aiplatform.v1beta1.MetadataService.QueryExecutionInputsAndOutputs].
            execution (:class:`str`):
                Required. The resource name of the
                Execution whose input and output
                Artifacts should be retrieved as a
                LineageSubgraph. Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}/executions/{execution}

                This corresponds to the ``execution`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.LineageSubgraph:
                A subgraph of the overall lineage
                graph. Event edges connect Artifact and
                Execution nodes.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([execution])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = metadata_service.QueryExecutionInputsAndOutputsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if execution is not None:
            request.execution = execution

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.query_execution_inputs_and_outputs,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("execution", request.execution),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def create_metadata_schema(
        self,
        request: metadata_service.CreateMetadataSchemaRequest = None,
        *,
        parent: str = None,
        metadata_schema: gca_metadata_schema.MetadataSchema = None,
        metadata_schema_id: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_metadata_schema.MetadataSchema:
        r"""Creates an MetadataSchema.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.CreateMetadataSchemaRequest`):
                The request object. Request message for
                [MetadataService.CreateMetadataSchema][google.cloud.aiplatform.v1beta1.MetadataService.CreateMetadataSchema].
            parent (:class:`str`):
                Required. The resource name of the
                MetadataStore where the MetadataSchema
                should be created. Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            metadata_schema (:class:`google.cloud.aiplatform_v1beta1.types.MetadataSchema`):
                Required. The MetadataSchema to
                create.

                This corresponds to the ``metadata_schema`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            metadata_schema_id (:class:`str`):
                The {metadata_schema} portion of the resource name with
                the format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}/metadataSchemas/{metadataschema}
                If not provided, the MetadataStore's ID will be a UUID
                generated by the service. Must be 4-128 characters in
                length. Valid characters are /[a-z][0-9]-/. Must be
                unique across all MetadataSchemas in the parent
                Location. (Otherwise the request will fail with
                ALREADY_EXISTS, or PERMISSION_DENIED if the caller can't
                view the preexisting MetadataSchema.)

                This corresponds to the ``metadata_schema_id`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.MetadataSchema:
                Instance of a general MetadataSchema.
        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, metadata_schema, metadata_schema_id])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = metadata_service.CreateMetadataSchemaRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if metadata_schema is not None:
            request.metadata_schema = metadata_schema
        if metadata_schema_id is not None:
            request.metadata_schema_id = metadata_schema_id

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_metadata_schema,
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

        # Done; return the response.
        return response

    async def get_metadata_schema(
        self,
        request: metadata_service.GetMetadataSchemaRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> metadata_schema.MetadataSchema:
        r"""Retrieves a specific MetadataSchema.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.GetMetadataSchemaRequest`):
                The request object. Request message for
                [MetadataService.GetMetadataSchema][google.cloud.aiplatform.v1beta1.MetadataService.GetMetadataSchema].
            name (:class:`str`):
                Required. The resource name of the
                MetadataSchema to retrieve. Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}/metadataSchemas/{metadataschema}

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.MetadataSchema:
                Instance of a general MetadataSchema.
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

        request = metadata_service.GetMetadataSchemaRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_metadata_schema,
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

    async def list_metadata_schemas(
        self,
        request: metadata_service.ListMetadataSchemasRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListMetadataSchemasAsyncPager:
        r"""Lists MetadataSchemas.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.ListMetadataSchemasRequest`):
                The request object. Request message for
                [MetadataService.ListMetadataSchemas][google.cloud.aiplatform.v1beta1.MetadataService.ListMetadataSchemas].
            parent (:class:`str`):
                Required. The MetadataStore whose
                MetadataSchemas should be listed.
                Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.services.metadata_service.pagers.ListMetadataSchemasAsyncPager:
                Response message for
                [MetadataService.ListMetadataSchemas][google.cloud.aiplatform.v1beta1.MetadataService.ListMetadataSchemas].

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

        request = metadata_service.ListMetadataSchemasRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_metadata_schemas,
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
        response = pagers.ListMetadataSchemasAsyncPager(
            method=rpc, request=request, response=response, metadata=metadata,
        )

        # Done; return the response.
        return response

    async def query_artifact_lineage_subgraph(
        self,
        request: metadata_service.QueryArtifactLineageSubgraphRequest = None,
        *,
        artifact: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> lineage_subgraph.LineageSubgraph:
        r"""Retrieves lineage of an Artifact represented through
        Artifacts and Executions connected by Event edges and
        returned as a LineageSubgraph.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.QueryArtifactLineageSubgraphRequest`):
                The request object. Request message for
                [MetadataService.QueryArtifactLineageSubgraph][google.cloud.aiplatform.v1beta1.MetadataService.QueryArtifactLineageSubgraph].
            artifact (:class:`str`):
                Required. The resource name of the Artifact whose
                Lineage needs to be retrieved as a LineageSubgraph.
                Format:
                projects/{project}/locations/{location}/metadataStores/{metadatastore}/artifacts/{artifact}

                The request may error with FAILED_PRECONDITION if the
                number of Artifacts, the number of Executions, or the
                number of Events that would be returned for the Context
                exceeds 1000.

                This corresponds to the ``artifact`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.LineageSubgraph:
                A subgraph of the overall lineage
                graph. Event edges connect Artifact and
                Execution nodes.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([artifact])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = metadata_service.QueryArtifactLineageSubgraphRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if artifact is not None:
            request.artifact = artifact

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.query_artifact_lineage_subgraph,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("artifact", request.artifact),)),
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


__all__ = ("MetadataServiceAsyncClient",)
