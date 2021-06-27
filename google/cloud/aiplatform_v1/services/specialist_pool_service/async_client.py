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
from google.cloud.aiplatform_v1.services.specialist_pool_service import pagers
from google.cloud.aiplatform_v1.types import operation as gca_operation
from google.cloud.aiplatform_v1.types import specialist_pool
from google.cloud.aiplatform_v1.types import specialist_pool as gca_specialist_pool
from google.cloud.aiplatform_v1.types import specialist_pool_service
from google.protobuf import empty_pb2  # type: ignore
from google.protobuf import field_mask_pb2  # type: ignore
from .transports.base import SpecialistPoolServiceTransport, DEFAULT_CLIENT_INFO
from .transports.grpc_asyncio import SpecialistPoolServiceGrpcAsyncIOTransport
from .client import SpecialistPoolServiceClient


class SpecialistPoolServiceAsyncClient:
    """A service for creating and managing Customer SpecialistPools.
    When customers start Data Labeling jobs, they can reuse/create
    Specialist Pools to bring their own Specialists to label the
    data. Customers can add/remove Managers for the Specialist Pool
    on Cloud console, then Managers will get email notifications to
    manage Specialists and tasks on CrowdCompute console.
    """

    _client: SpecialistPoolServiceClient

    DEFAULT_ENDPOINT = SpecialistPoolServiceClient.DEFAULT_ENDPOINT
    DEFAULT_MTLS_ENDPOINT = SpecialistPoolServiceClient.DEFAULT_MTLS_ENDPOINT

    specialist_pool_path = staticmethod(
        SpecialistPoolServiceClient.specialist_pool_path
    )
    parse_specialist_pool_path = staticmethod(
        SpecialistPoolServiceClient.parse_specialist_pool_path
    )
    common_billing_account_path = staticmethod(
        SpecialistPoolServiceClient.common_billing_account_path
    )
    parse_common_billing_account_path = staticmethod(
        SpecialistPoolServiceClient.parse_common_billing_account_path
    )
    common_folder_path = staticmethod(SpecialistPoolServiceClient.common_folder_path)
    parse_common_folder_path = staticmethod(
        SpecialistPoolServiceClient.parse_common_folder_path
    )
    common_organization_path = staticmethod(
        SpecialistPoolServiceClient.common_organization_path
    )
    parse_common_organization_path = staticmethod(
        SpecialistPoolServiceClient.parse_common_organization_path
    )
    common_project_path = staticmethod(SpecialistPoolServiceClient.common_project_path)
    parse_common_project_path = staticmethod(
        SpecialistPoolServiceClient.parse_common_project_path
    )
    common_location_path = staticmethod(
        SpecialistPoolServiceClient.common_location_path
    )
    parse_common_location_path = staticmethod(
        SpecialistPoolServiceClient.parse_common_location_path
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
            SpecialistPoolServiceAsyncClient: The constructed client.
        """
        return SpecialistPoolServiceClient.from_service_account_info.__func__(SpecialistPoolServiceAsyncClient, info, *args, **kwargs)  # type: ignore

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
            SpecialistPoolServiceAsyncClient: The constructed client.
        """
        return SpecialistPoolServiceClient.from_service_account_file.__func__(SpecialistPoolServiceAsyncClient, filename, *args, **kwargs)  # type: ignore

    from_service_account_json = from_service_account_file

    @property
    def transport(self) -> SpecialistPoolServiceTransport:
        """Returns the transport used by the client instance.

        Returns:
            SpecialistPoolServiceTransport: The transport used by the client instance.
        """
        return self._client.transport

    get_transport_class = functools.partial(
        type(SpecialistPoolServiceClient).get_transport_class,
        type(SpecialistPoolServiceClient),
    )

    def __init__(
        self,
        *,
        credentials: ga_credentials.Credentials = None,
        transport: Union[str, SpecialistPoolServiceTransport] = "grpc_asyncio",
        client_options: ClientOptions = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
    ) -> None:
        """Instantiates the specialist pool service client.

        Args:
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            transport (Union[str, ~.SpecialistPoolServiceTransport]): The
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
        self._client = SpecialistPoolServiceClient(
            credentials=credentials,
            transport=transport,
            client_options=client_options,
            client_info=client_info,
        )

    async def create_specialist_pool(
        self,
        request: specialist_pool_service.CreateSpecialistPoolRequest = None,
        *,
        parent: str = None,
        specialist_pool: gca_specialist_pool.SpecialistPool = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Creates a SpecialistPool.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.CreateSpecialistPoolRequest`):
                The request object. Request message for
                [SpecialistPoolService.CreateSpecialistPool][google.cloud.aiplatform.v1.SpecialistPoolService.CreateSpecialistPool].
            parent (:class:`str`):
                Required. The parent Project name for the new
                SpecialistPool. The form is
                ``projects/{project}/locations/{location}``.

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            specialist_pool (:class:`google.cloud.aiplatform_v1.types.SpecialistPool`):
                Required. The SpecialistPool to
                create.

                This corresponds to the ``specialist_pool`` field
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

                The result type for the operation will be :class:`google.cloud.aiplatform_v1.types.SpecialistPool` SpecialistPool represents customers' own workforce to work on their data
                   labeling jobs. It includes a group of specialist
                   managers who are responsible for managing the
                   labelers in this pool as well as customers' data
                   labeling jobs associated with this pool. Customers
                   create specialist pool as well as start data labeling
                   jobs on Cloud, managers and labelers work with the
                   jobs using CrowdCompute console.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, specialist_pool])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = specialist_pool_service.CreateSpecialistPoolRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if specialist_pool is not None:
            request.specialist_pool = specialist_pool

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_specialist_pool,
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
            gca_specialist_pool.SpecialistPool,
            metadata_type=specialist_pool_service.CreateSpecialistPoolOperationMetadata,
        )

        # Done; return the response.
        return response

    async def get_specialist_pool(
        self,
        request: specialist_pool_service.GetSpecialistPoolRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> specialist_pool.SpecialistPool:
        r"""Gets a SpecialistPool.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.GetSpecialistPoolRequest`):
                The request object. Request message for
                [SpecialistPoolService.GetSpecialistPool][google.cloud.aiplatform.v1.SpecialistPoolService.GetSpecialistPool].
            name (:class:`str`):
                Required. The name of the SpecialistPool resource. The
                form is
                ``projects/{project}/locations/{location}/specialistPools/{specialist_pool}``.

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.types.SpecialistPool:
                SpecialistPool represents customers'
                own workforce to work on their data
                labeling jobs. It includes a group of
                specialist managers who are responsible
                for managing the labelers in this pool
                as well as customers' data labeling jobs
                associated with this pool.
                Customers create specialist pool as well
                as start data labeling jobs on Cloud,
                managers and labelers work with the jobs
                using CrowdCompute console.

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

        request = specialist_pool_service.GetSpecialistPoolRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_specialist_pool,
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

    async def list_specialist_pools(
        self,
        request: specialist_pool_service.ListSpecialistPoolsRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListSpecialistPoolsAsyncPager:
        r"""Lists SpecialistPools in a Location.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.ListSpecialistPoolsRequest`):
                The request object. Request message for
                [SpecialistPoolService.ListSpecialistPools][google.cloud.aiplatform.v1.SpecialistPoolService.ListSpecialistPools].
            parent (:class:`str`):
                Required. The name of the SpecialistPool's parent
                resource. Format:
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
            google.cloud.aiplatform_v1.services.specialist_pool_service.pagers.ListSpecialistPoolsAsyncPager:
                Response message for
                [SpecialistPoolService.ListSpecialistPools][google.cloud.aiplatform.v1.SpecialistPoolService.ListSpecialistPools].

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

        request = specialist_pool_service.ListSpecialistPoolsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_specialist_pools,
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
        response = pagers.ListSpecialistPoolsAsyncPager(
            method=rpc, request=request, response=response, metadata=metadata,
        )

        # Done; return the response.
        return response

    async def delete_specialist_pool(
        self,
        request: specialist_pool_service.DeleteSpecialistPoolRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Deletes a SpecialistPool as well as all Specialists
        in the pool.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.DeleteSpecialistPoolRequest`):
                The request object. Request message for
                [SpecialistPoolService.DeleteSpecialistPool][google.cloud.aiplatform.v1.SpecialistPoolService.DeleteSpecialistPool].
            name (:class:`str`):
                Required. The resource name of the SpecialistPool to
                delete. Format:
                ``projects/{project}/locations/{location}/specialistPools/{specialist_pool}``

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

        request = specialist_pool_service.DeleteSpecialistPoolRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.delete_specialist_pool,
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

    async def update_specialist_pool(
        self,
        request: specialist_pool_service.UpdateSpecialistPoolRequest = None,
        *,
        specialist_pool: gca_specialist_pool.SpecialistPool = None,
        update_mask: field_mask_pb2.FieldMask = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Updates a SpecialistPool.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.UpdateSpecialistPoolRequest`):
                The request object. Request message for
                [SpecialistPoolService.UpdateSpecialistPool][google.cloud.aiplatform.v1.SpecialistPoolService.UpdateSpecialistPool].
            specialist_pool (:class:`google.cloud.aiplatform_v1.types.SpecialistPool`):
                Required. The SpecialistPool which
                replaces the resource on the server.

                This corresponds to the ``specialist_pool`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            update_mask (:class:`google.protobuf.field_mask_pb2.FieldMask`):
                Required. The update mask applies to
                the resource.

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

                The result type for the operation will be :class:`google.cloud.aiplatform_v1.types.SpecialistPool` SpecialistPool represents customers' own workforce to work on their data
                   labeling jobs. It includes a group of specialist
                   managers who are responsible for managing the
                   labelers in this pool as well as customers' data
                   labeling jobs associated with this pool. Customers
                   create specialist pool as well as start data labeling
                   jobs on Cloud, managers and labelers work with the
                   jobs using CrowdCompute console.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([specialist_pool, update_mask])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = specialist_pool_service.UpdateSpecialistPoolRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if specialist_pool is not None:
            request.specialist_pool = specialist_pool
        if update_mask is not None:
            request.update_mask = update_mask

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.update_specialist_pool,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("specialist_pool.name", request.specialist_pool.name),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = operation_async.from_gapic(
            response,
            self._client._transport.operations_client,
            gca_specialist_pool.SpecialistPool,
            metadata_type=specialist_pool_service.UpdateSpecialistPoolOperationMetadata,
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


__all__ = ("SpecialistPoolServiceAsyncClient",)
