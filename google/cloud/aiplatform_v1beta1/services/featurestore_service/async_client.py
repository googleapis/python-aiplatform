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
from google.cloud.aiplatform_v1beta1.services.featurestore_service import pagers
from google.cloud.aiplatform_v1beta1.types import entity_type
from google.cloud.aiplatform_v1beta1.types import entity_type as gca_entity_type
from google.cloud.aiplatform_v1beta1.types import feature
from google.cloud.aiplatform_v1beta1.types import feature as gca_feature
from google.cloud.aiplatform_v1beta1.types import feature_monitoring_stats
from google.cloud.aiplatform_v1beta1.types import featurestore
from google.cloud.aiplatform_v1beta1.types import featurestore as gca_featurestore
from google.cloud.aiplatform_v1beta1.types import featurestore_monitoring
from google.cloud.aiplatform_v1beta1.types import featurestore_service
from google.cloud.aiplatform_v1beta1.types import operation as gca_operation
from google.protobuf import empty_pb2  # type: ignore
from google.protobuf import field_mask_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
from .transports.base import FeaturestoreServiceTransport, DEFAULT_CLIENT_INFO
from .transports.grpc_asyncio import FeaturestoreServiceGrpcAsyncIOTransport
from .client import FeaturestoreServiceClient


class FeaturestoreServiceAsyncClient:
    """The service that handles CRUD and List for resources for
    Featurestore.
    """

    _client: FeaturestoreServiceClient

    DEFAULT_ENDPOINT = FeaturestoreServiceClient.DEFAULT_ENDPOINT
    DEFAULT_MTLS_ENDPOINT = FeaturestoreServiceClient.DEFAULT_MTLS_ENDPOINT

    entity_type_path = staticmethod(FeaturestoreServiceClient.entity_type_path)
    parse_entity_type_path = staticmethod(
        FeaturestoreServiceClient.parse_entity_type_path
    )
    feature_path = staticmethod(FeaturestoreServiceClient.feature_path)
    parse_feature_path = staticmethod(FeaturestoreServiceClient.parse_feature_path)
    featurestore_path = staticmethod(FeaturestoreServiceClient.featurestore_path)
    parse_featurestore_path = staticmethod(
        FeaturestoreServiceClient.parse_featurestore_path
    )
    common_billing_account_path = staticmethod(
        FeaturestoreServiceClient.common_billing_account_path
    )
    parse_common_billing_account_path = staticmethod(
        FeaturestoreServiceClient.parse_common_billing_account_path
    )
    common_folder_path = staticmethod(FeaturestoreServiceClient.common_folder_path)
    parse_common_folder_path = staticmethod(
        FeaturestoreServiceClient.parse_common_folder_path
    )
    common_organization_path = staticmethod(
        FeaturestoreServiceClient.common_organization_path
    )
    parse_common_organization_path = staticmethod(
        FeaturestoreServiceClient.parse_common_organization_path
    )
    common_project_path = staticmethod(FeaturestoreServiceClient.common_project_path)
    parse_common_project_path = staticmethod(
        FeaturestoreServiceClient.parse_common_project_path
    )
    common_location_path = staticmethod(FeaturestoreServiceClient.common_location_path)
    parse_common_location_path = staticmethod(
        FeaturestoreServiceClient.parse_common_location_path
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
            FeaturestoreServiceAsyncClient: The constructed client.
        """
        return FeaturestoreServiceClient.from_service_account_info.__func__(FeaturestoreServiceAsyncClient, info, *args, **kwargs)  # type: ignore

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
            FeaturestoreServiceAsyncClient: The constructed client.
        """
        return FeaturestoreServiceClient.from_service_account_file.__func__(FeaturestoreServiceAsyncClient, filename, *args, **kwargs)  # type: ignore

    from_service_account_json = from_service_account_file

    @property
    def transport(self) -> FeaturestoreServiceTransport:
        """Returns the transport used by the client instance.

        Returns:
            FeaturestoreServiceTransport: The transport used by the client instance.
        """
        return self._client.transport

    get_transport_class = functools.partial(
        type(FeaturestoreServiceClient).get_transport_class,
        type(FeaturestoreServiceClient),
    )

    def __init__(
        self,
        *,
        credentials: ga_credentials.Credentials = None,
        transport: Union[str, FeaturestoreServiceTransport] = "grpc_asyncio",
        client_options: ClientOptions = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
    ) -> None:
        """Instantiates the featurestore service client.

        Args:
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            transport (Union[str, ~.FeaturestoreServiceTransport]): The
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
        self._client = FeaturestoreServiceClient(
            credentials=credentials,
            transport=transport,
            client_options=client_options,
            client_info=client_info,
        )

    async def create_featurestore(
        self,
        request: featurestore_service.CreateFeaturestoreRequest = None,
        *,
        parent: str = None,
        featurestore: gca_featurestore.Featurestore = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Creates a new Featurestore in a given project and
        location.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.CreateFeaturestoreRequest`):
                The request object. Request message for
                [FeaturestoreService.CreateFeaturestore][google.cloud.aiplatform.v1beta1.FeaturestoreService.CreateFeaturestore].
            parent (:class:`str`):
                Required. The resource name of the Location to create
                Featurestores. Format:
                ``projects/{project}/locations/{location}'``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            featurestore (:class:`google.cloud.aiplatform_v1beta1.types.Featurestore`):
                Required. The Featurestore to create.
                This corresponds to the ``featurestore`` field
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
                :class:`google.cloud.aiplatform_v1beta1.types.Featurestore`
                Featurestore configuration information on how the
                Featurestore is configured.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, featurestore])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = featurestore_service.CreateFeaturestoreRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if featurestore is not None:
            request.featurestore = featurestore

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_featurestore,
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
            gca_featurestore.Featurestore,
            metadata_type=featurestore_service.CreateFeaturestoreOperationMetadata,
        )

        # Done; return the response.
        return response

    async def get_featurestore(
        self,
        request: featurestore_service.GetFeaturestoreRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> featurestore.Featurestore:
        r"""Gets details of a single Featurestore.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.GetFeaturestoreRequest`):
                The request object. Request message for
                [FeaturestoreService.GetFeaturestore][google.cloud.aiplatform.v1beta1.FeaturestoreService.GetFeaturestore].
            name (:class:`str`):
                Required. The name of the
                Featurestore resource.

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.Featurestore:
                Featurestore configuration
                information on how the Featurestore is
                configured.

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

        request = featurestore_service.GetFeaturestoreRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_featurestore,
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

    async def list_featurestores(
        self,
        request: featurestore_service.ListFeaturestoresRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListFeaturestoresAsyncPager:
        r"""Lists Featurestores in a given project and location.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.ListFeaturestoresRequest`):
                The request object. Request message for
                [FeaturestoreService.ListFeaturestores][google.cloud.aiplatform.v1beta1.FeaturestoreService.ListFeaturestores].
            parent (:class:`str`):
                Required. The resource name of the Location to list
                Featurestores. Format:
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
            google.cloud.aiplatform_v1beta1.services.featurestore_service.pagers.ListFeaturestoresAsyncPager:
                Response message for
                [FeaturestoreService.ListFeaturestores][google.cloud.aiplatform.v1beta1.FeaturestoreService.ListFeaturestores].

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

        request = featurestore_service.ListFeaturestoresRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_featurestores,
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
        response = pagers.ListFeaturestoresAsyncPager(
            method=rpc, request=request, response=response, metadata=metadata,
        )

        # Done; return the response.
        return response

    async def update_featurestore(
        self,
        request: featurestore_service.UpdateFeaturestoreRequest = None,
        *,
        featurestore: gca_featurestore.Featurestore = None,
        update_mask: field_mask_pb2.FieldMask = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Updates the parameters of a single Featurestore.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.UpdateFeaturestoreRequest`):
                The request object. Request message for
                [FeaturestoreService.UpdateFeaturestore][google.cloud.aiplatform.v1beta1.FeaturestoreService.UpdateFeaturestore].
            featurestore (:class:`google.cloud.aiplatform_v1beta1.types.Featurestore`):
                Required. The Featurestore's ``name`` field is used to
                identify the Featurestore to be updated. Format:
                ``projects/{project}/locations/{location}/featurestores/{featurestore}``

                This corresponds to the ``featurestore`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            update_mask (:class:`google.protobuf.field_mask_pb2.FieldMask`):
                Field mask is used to specify the fields to be
                overwritten in the Featurestore resource by the update.
                The fields specified in the update_mask are relative to
                the resource, not the full request. A field will be
                overwritten if it is in the mask. If the user does not
                provide a mask then only the non-empty fields present in
                the request will be overwritten. Set the update_mask to
                ``*`` to override all fields.

                Updatable fields:

                -  ``labels``
                -  ``online_serving_config.fixed_node_count``

                This corresponds to the ``update_mask`` field
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
                :class:`google.cloud.aiplatform_v1beta1.types.Featurestore`
                Featurestore configuration information on how the
                Featurestore is configured.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([featurestore, update_mask])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = featurestore_service.UpdateFeaturestoreRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if featurestore is not None:
            request.featurestore = featurestore
        if update_mask is not None:
            request.update_mask = update_mask

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.update_featurestore,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("featurestore.name", request.featurestore.name),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = operation_async.from_gapic(
            response,
            self._client._transport.operations_client,
            gca_featurestore.Featurestore,
            metadata_type=featurestore_service.UpdateFeaturestoreOperationMetadata,
        )

        # Done; return the response.
        return response

    async def delete_featurestore(
        self,
        request: featurestore_service.DeleteFeaturestoreRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Deletes a single Featurestore. The Featurestore must not contain
        any EntityTypes or ``force`` must be set to true for the request
        to succeed.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.DeleteFeaturestoreRequest`):
                The request object. Request message for
                [FeaturestoreService.DeleteFeaturestore][google.cloud.aiplatform.v1beta1.FeaturestoreService.DeleteFeaturestore].
            name (:class:`str`):
                Required. The name of the Featurestore to be deleted.
                Format:
                ``projects/{project}/locations/{location}/featurestores/{featurestore}``

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

        request = featurestore_service.DeleteFeaturestoreRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.delete_featurestore,
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

    async def create_entity_type(
        self,
        request: featurestore_service.CreateEntityTypeRequest = None,
        *,
        parent: str = None,
        entity_type: gca_entity_type.EntityType = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Creates a new EntityType in a given Featurestore.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.CreateEntityTypeRequest`):
                The request object. Request message for
                [FeaturestoreService.CreateEntityType][google.cloud.aiplatform.v1beta1.FeaturestoreService.CreateEntityType].
            parent (:class:`str`):
                Required. The resource name of the Featurestore to
                create EntityTypes. Format:
                ``projects/{project}/locations/{location}/featurestores/{featurestore}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            entity_type (:class:`google.cloud.aiplatform_v1beta1.types.EntityType`):
                The EntityType to create.
                This corresponds to the ``entity_type`` field
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

                The result type for the operation will be :class:`google.cloud.aiplatform_v1beta1.types.EntityType` An entity type is a type of object in a system that needs to be modeled and
                   have stored information about. For example, driver is
                   an entity type, and driver0 is an instance of an
                   entity type driver.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, entity_type])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = featurestore_service.CreateEntityTypeRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if entity_type is not None:
            request.entity_type = entity_type

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_entity_type,
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
            gca_entity_type.EntityType,
            metadata_type=featurestore_service.CreateEntityTypeOperationMetadata,
        )

        # Done; return the response.
        return response

    async def get_entity_type(
        self,
        request: featurestore_service.GetEntityTypeRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> entity_type.EntityType:
        r"""Gets details of a single EntityType.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.GetEntityTypeRequest`):
                The request object. Request message for
                [FeaturestoreService.GetEntityType][google.cloud.aiplatform.v1beta1.FeaturestoreService.GetEntityType].
            name (:class:`str`):
                Required. The name of the EntityType resource. Format:
                ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.EntityType:
                An entity type is a type of object in
                a system that needs to be modeled and
                have stored information about. For
                example, driver is an entity type, and
                driver0 is an instance of an entity type
                driver.

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

        request = featurestore_service.GetEntityTypeRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_entity_type,
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

    async def list_entity_types(
        self,
        request: featurestore_service.ListEntityTypesRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListEntityTypesAsyncPager:
        r"""Lists EntityTypes in a given Featurestore.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.ListEntityTypesRequest`):
                The request object. Request message for
                [FeaturestoreService.ListEntityTypes][google.cloud.aiplatform.v1beta1.FeaturestoreService.ListEntityTypes].
            parent (:class:`str`):
                Required. The resource name of the Featurestore to list
                EntityTypes. Format:
                ``projects/{project}/locations/{location}/featurestores/{featurestore}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.services.featurestore_service.pagers.ListEntityTypesAsyncPager:
                Response message for
                [FeaturestoreService.ListEntityTypes][google.cloud.aiplatform.v1beta1.FeaturestoreService.ListEntityTypes].

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

        request = featurestore_service.ListEntityTypesRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_entity_types,
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
        response = pagers.ListEntityTypesAsyncPager(
            method=rpc, request=request, response=response, metadata=metadata,
        )

        # Done; return the response.
        return response

    async def update_entity_type(
        self,
        request: featurestore_service.UpdateEntityTypeRequest = None,
        *,
        entity_type: gca_entity_type.EntityType = None,
        update_mask: field_mask_pb2.FieldMask = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_entity_type.EntityType:
        r"""Updates the parameters of a single EntityType.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.UpdateEntityTypeRequest`):
                The request object. Request message for
                [FeaturestoreService.UpdateEntityType][google.cloud.aiplatform.v1beta1.FeaturestoreService.UpdateEntityType].
            entity_type (:class:`google.cloud.aiplatform_v1beta1.types.EntityType`):
                Required. The EntityType's ``name`` field is used to
                identify the EntityType to be updated. Format:
                ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}``

                This corresponds to the ``entity_type`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            update_mask (:class:`google.protobuf.field_mask_pb2.FieldMask`):
                Field mask is used to specify the fields to be
                overwritten in the EntityType resource by the update.
                The fields specified in the update_mask are relative to
                the resource, not the full request. A field will be
                overwritten if it is in the mask. If the user does not
                provide a mask then only the non-empty fields present in
                the request will be overwritten. Set the update_mask to
                ``*`` to override all fields.

                Updatable fields:

                -  ``description``
                -  ``labels``
                -  ``monitoring_config.snapshot_analysis.disabled``
                -  ``monitoring_config.snapshot_analysis.monitoring_interval``

                This corresponds to the ``update_mask`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.EntityType:
                An entity type is a type of object in
                a system that needs to be modeled and
                have stored information about. For
                example, driver is an entity type, and
                driver0 is an instance of an entity type
                driver.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([entity_type, update_mask])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = featurestore_service.UpdateEntityTypeRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if entity_type is not None:
            request.entity_type = entity_type
        if update_mask is not None:
            request.update_mask = update_mask

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.update_entity_type,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("entity_type.name", request.entity_type.name),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def delete_entity_type(
        self,
        request: featurestore_service.DeleteEntityTypeRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Deletes a single EntityType. The EntityType must not have any
        Features or ``force`` must be set to true for the request to
        succeed.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.DeleteEntityTypeRequest`):
                The request object. Request message for
                [FeaturestoreService.DeleteEntityTypes][].
            name (:class:`str`):
                Required. The name of the EntityType to be deleted.
                Format:
                ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}``

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

        request = featurestore_service.DeleteEntityTypeRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.delete_entity_type,
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

    async def create_feature(
        self,
        request: featurestore_service.CreateFeatureRequest = None,
        *,
        parent: str = None,
        feature: gca_feature.Feature = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Creates a new Feature in a given EntityType.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.CreateFeatureRequest`):
                The request object. Request message for
                [FeaturestoreService.CreateFeature][google.cloud.aiplatform.v1beta1.FeaturestoreService.CreateFeature].
            parent (:class:`str`):
                Required. The resource name of the EntityType to create
                a Feature. Format:
                ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            feature (:class:`google.cloud.aiplatform_v1beta1.types.Feature`):
                Required. The Feature to create.
                This corresponds to the ``feature`` field
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

                The result type for the operation will be :class:`google.cloud.aiplatform_v1beta1.types.Feature` Feature Metadata information that describes an attribute of an entity type.
                   For example, apple is an entity type, and color is a
                   feature that describes apple.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, feature])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = featurestore_service.CreateFeatureRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if feature is not None:
            request.feature = feature

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_feature,
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
            gca_feature.Feature,
            metadata_type=featurestore_service.CreateFeatureOperationMetadata,
        )

        # Done; return the response.
        return response

    async def batch_create_features(
        self,
        request: featurestore_service.BatchCreateFeaturesRequest = None,
        *,
        parent: str = None,
        requests: Sequence[featurestore_service.CreateFeatureRequest] = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Creates a batch of Features in a given EntityType.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.BatchCreateFeaturesRequest`):
                The request object. Request message for
                [FeaturestoreService.BatchCreateFeatures][google.cloud.aiplatform.v1beta1.FeaturestoreService.BatchCreateFeatures].
            parent (:class:`str`):
                Required. The resource name of the EntityType to create
                the batch of Features under. Format:
                ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            requests (:class:`Sequence[google.cloud.aiplatform_v1beta1.types.CreateFeatureRequest]`):
                Required. The request message specifying the Features to
                create. All Features must be created under the same
                parent EntityType. The ``parent`` field in each child
                request message can be omitted. If ``parent`` is set in
                a child request, then the value must match the
                ``parent`` value in this request message.

                This corresponds to the ``requests`` field
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
                :class:`google.cloud.aiplatform_v1beta1.types.BatchCreateFeaturesResponse`
                Response message for
                [FeaturestoreService.BatchCreateFeatures][google.cloud.aiplatform.v1beta1.FeaturestoreService.BatchCreateFeatures].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, requests])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = featurestore_service.BatchCreateFeaturesRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if requests:
            request.requests.extend(requests)

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.batch_create_features,
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
            featurestore_service.BatchCreateFeaturesResponse,
            metadata_type=featurestore_service.BatchCreateFeaturesOperationMetadata,
        )

        # Done; return the response.
        return response

    async def get_feature(
        self,
        request: featurestore_service.GetFeatureRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> feature.Feature:
        r"""Gets details of a single Feature.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.GetFeatureRequest`):
                The request object. Request message for
                [FeaturestoreService.GetFeature][google.cloud.aiplatform.v1beta1.FeaturestoreService.GetFeature].
            name (:class:`str`):
                Required. The name of the Feature resource. Format:
                ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.Feature:
                Feature Metadata information that
                describes an attribute of an entity
                type. For example, apple is an entity
                type, and color is a feature that
                describes apple.

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

        request = featurestore_service.GetFeatureRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_feature,
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

    async def list_features(
        self,
        request: featurestore_service.ListFeaturesRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListFeaturesAsyncPager:
        r"""Lists Features in a given EntityType.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.ListFeaturesRequest`):
                The request object. Request message for
                [FeaturestoreService.ListFeatures][google.cloud.aiplatform.v1beta1.FeaturestoreService.ListFeatures].
            parent (:class:`str`):
                Required. The resource name of the Location to list
                Features. Format:
                ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.services.featurestore_service.pagers.ListFeaturesAsyncPager:
                Response message for
                [FeaturestoreService.ListFeatures][google.cloud.aiplatform.v1beta1.FeaturestoreService.ListFeatures].

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

        request = featurestore_service.ListFeaturesRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_features,
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
        response = pagers.ListFeaturesAsyncPager(
            method=rpc, request=request, response=response, metadata=metadata,
        )

        # Done; return the response.
        return response

    async def update_feature(
        self,
        request: featurestore_service.UpdateFeatureRequest = None,
        *,
        feature: gca_feature.Feature = None,
        update_mask: field_mask_pb2.FieldMask = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_feature.Feature:
        r"""Updates the parameters of a single Feature.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.UpdateFeatureRequest`):
                The request object. Request message for
                [FeaturestoreService.UpdateFeature][google.cloud.aiplatform.v1beta1.FeaturestoreService.UpdateFeature].
            feature (:class:`google.cloud.aiplatform_v1beta1.types.Feature`):
                Required. The Feature's ``name`` field is used to
                identify the Feature to be updated. Format:
                ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}/features/{feature}``

                This corresponds to the ``feature`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            update_mask (:class:`google.protobuf.field_mask_pb2.FieldMask`):
                Field mask is used to specify the fields to be
                overwritten in the Features resource by the update. The
                fields specified in the update_mask are relative to the
                resource, not the full request. A field will be
                overwritten if it is in the mask. If the user does not
                provide a mask then only the non-empty fields present in
                the request will be overwritten. Set the update_mask to
                ``*`` to override all fields.

                Updatable fields:

                -  ``description``
                -  ``labels``
                -  ``monitoring_config.snapshot_analysis.disabled``
                -  ``monitoring_config.snapshot_analysis.monitoring_interval``

                This corresponds to the ``update_mask`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.Feature:
                Feature Metadata information that
                describes an attribute of an entity
                type. For example, apple is an entity
                type, and color is a feature that
                describes apple.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([feature, update_mask])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = featurestore_service.UpdateFeatureRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if feature is not None:
            request.feature = feature
        if update_mask is not None:
            request.update_mask = update_mask

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.update_feature,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("feature.name", request.feature.name),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def delete_feature(
        self,
        request: featurestore_service.DeleteFeatureRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Deletes a single Feature.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.DeleteFeatureRequest`):
                The request object. Request message for
                [FeaturestoreService.DeleteFeature][google.cloud.aiplatform.v1beta1.FeaturestoreService.DeleteFeature].
            name (:class:`str`):
                Required. The name of the Features to be deleted.
                Format:
                ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}/features/{feature}``

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

        request = featurestore_service.DeleteFeatureRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.delete_feature,
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

    async def import_feature_values(
        self,
        request: featurestore_service.ImportFeatureValuesRequest = None,
        *,
        entity_type: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Imports Feature values into the Featurestore from a
        source storage.
        The progress of the import is tracked by the returned
        operation. The imported features are guaranteed to be
        visible to subsequent read operations after the
        operation is marked as successfully done.
        If an import operation fails, the Feature values
        returned from reads and exports may be inconsistent. If
        consistency is required, the caller must retry the same
        import request again and wait till the new operation
        returned is marked as successfully done.
        There are also scenarios where the caller can cause
        inconsistency.
         - Source data for import contains multiple distinct
        Feature values for    the same entity ID and timestamp.
         - Source is modified during an import. This includes
        adding, updating, or  removing source data and/or
        metadata. Examples of updating metadata  include but are
        not limited to changing storage location, storage class,
        or retention policy.
         - Online serving cluster is under-provisioned.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.ImportFeatureValuesRequest`):
                The request object. Request message for
                [FeaturestoreService.ImportFeatureValues][google.cloud.aiplatform.v1beta1.FeaturestoreService.ImportFeatureValues].
            entity_type (:class:`str`):
                Required. The resource name of the EntityType grouping
                the Features for which values are being imported.
                Format:
                ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entityType}``

                This corresponds to the ``entity_type`` field
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
                :class:`google.cloud.aiplatform_v1beta1.types.ImportFeatureValuesResponse`
                Response message for
                [FeaturestoreService.ImportFeatureValues][google.cloud.aiplatform.v1beta1.FeaturestoreService.ImportFeatureValues].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([entity_type])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = featurestore_service.ImportFeatureValuesRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if entity_type is not None:
            request.entity_type = entity_type

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.import_feature_values,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("entity_type", request.entity_type),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = operation_async.from_gapic(
            response,
            self._client._transport.operations_client,
            featurestore_service.ImportFeatureValuesResponse,
            metadata_type=featurestore_service.ImportFeatureValuesOperationMetadata,
        )

        # Done; return the response.
        return response

    async def batch_read_feature_values(
        self,
        request: featurestore_service.BatchReadFeatureValuesRequest = None,
        *,
        featurestore: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Batch reads Feature values from a Featurestore.
        This API enables batch reading Feature values, where
        each read instance in the batch may read Feature values
        of entities from one or more EntityTypes. Point-in-time
        correctness is guaranteed for Feature values of each
        read instance as of each instance's read timestamp.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.BatchReadFeatureValuesRequest`):
                The request object. Request message for
                [FeaturestoreService.BatchReadFeatureValues][google.cloud.aiplatform.v1beta1.FeaturestoreService.BatchReadFeatureValues].
                (- Next Id: 6 -)
            featurestore (:class:`str`):
                Required. The resource name of the Featurestore from
                which to query Feature values. Format:
                ``projects/{project}/locations/{location}/featurestores/{featurestore}``

                This corresponds to the ``featurestore`` field
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
                :class:`google.cloud.aiplatform_v1beta1.types.BatchReadFeatureValuesResponse`
                Response message for
                [FeaturestoreService.BatchReadFeatureValues][google.cloud.aiplatform.v1beta1.FeaturestoreService.BatchReadFeatureValues].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([featurestore])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = featurestore_service.BatchReadFeatureValuesRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if featurestore is not None:
            request.featurestore = featurestore

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.batch_read_feature_values,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("featurestore", request.featurestore),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = operation_async.from_gapic(
            response,
            self._client._transport.operations_client,
            featurestore_service.BatchReadFeatureValuesResponse,
            metadata_type=featurestore_service.BatchReadFeatureValuesOperationMetadata,
        )

        # Done; return the response.
        return response

    async def export_feature_values(
        self,
        request: featurestore_service.ExportFeatureValuesRequest = None,
        *,
        entity_type: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Exports Feature values from all the entities of a
        target EntityType.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.ExportFeatureValuesRequest`):
                The request object. Request message for
                [FeaturestoreService.ExportFeatureValues][google.cloud.aiplatform.v1beta1.FeaturestoreService.ExportFeatureValues].
            entity_type (:class:`str`):
                Required. The resource name of the EntityType from which
                to export Feature values. Format:
                ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}``

                This corresponds to the ``entity_type`` field
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
                :class:`google.cloud.aiplatform_v1beta1.types.ExportFeatureValuesResponse`
                Response message for
                [FeaturestoreService.ExportFeatureValues][google.cloud.aiplatform.v1beta1.FeaturestoreService.ExportFeatureValues].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([entity_type])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = featurestore_service.ExportFeatureValuesRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if entity_type is not None:
            request.entity_type = entity_type

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.export_feature_values,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("entity_type", request.entity_type),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = operation_async.from_gapic(
            response,
            self._client._transport.operations_client,
            featurestore_service.ExportFeatureValuesResponse,
            metadata_type=featurestore_service.ExportFeatureValuesOperationMetadata,
        )

        # Done; return the response.
        return response

    async def search_features(
        self,
        request: featurestore_service.SearchFeaturesRequest = None,
        *,
        location: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.SearchFeaturesAsyncPager:
        r"""Searches Features matching a query in a given
        project.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.SearchFeaturesRequest`):
                The request object. Request message for
                [FeaturestoreService.SearchFeatures][google.cloud.aiplatform.v1beta1.FeaturestoreService.SearchFeatures].
            location (:class:`str`):
                Required. The resource name of the Location to search
                Features. Format:
                ``projects/{project}/locations/{location}``

                This corresponds to the ``location`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.services.featurestore_service.pagers.SearchFeaturesAsyncPager:
                Response message for
                [FeaturestoreService.SearchFeatures][google.cloud.aiplatform.v1beta1.FeaturestoreService.SearchFeatures].

                Iterating over this object will yield results and
                resolve additional pages automatically.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([location])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = featurestore_service.SearchFeaturesRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if location is not None:
            request.location = location

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.search_features,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("location", request.location),)),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # This method is paged; wrap the response in a pager, which provides
        # an `__aiter__` convenience method.
        response = pagers.SearchFeaturesAsyncPager(
            method=rpc, request=request, response=response, metadata=metadata,
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


__all__ = ("FeaturestoreServiceAsyncClient",)
