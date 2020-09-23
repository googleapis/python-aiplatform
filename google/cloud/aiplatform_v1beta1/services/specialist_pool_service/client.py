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

from google.api_core import operation as ga_operation
from google.cloud.aiplatform_v1beta1.services.specialist_pool_service import pagers
from google.cloud.aiplatform_v1beta1.types import operation as gca_operation
from google.cloud.aiplatform_v1beta1.types import specialist_pool
from google.cloud.aiplatform_v1beta1.types import specialist_pool as gca_specialist_pool
from google.cloud.aiplatform_v1beta1.types import specialist_pool_service
from google.protobuf import empty_pb2 as empty  # type: ignore
from google.protobuf import field_mask_pb2 as field_mask  # type: ignore

from .transports.base import SpecialistPoolServiceTransport
from .transports.grpc import SpecialistPoolServiceGrpcTransport


class SpecialistPoolServiceClientMeta(type):
    """Metaclass for the SpecialistPoolService client.

    This provides class-level methods for building and retrieving
    support objects (e.g. transport) without polluting the client instance
    objects.
    """

    _transport_registry = (
        OrderedDict()
    )  # type: Dict[str, Type[SpecialistPoolServiceTransport]]
    _transport_registry["grpc"] = SpecialistPoolServiceGrpcTransport

    def get_transport_class(
        cls, label: str = None,
    ) -> Type[SpecialistPoolServiceTransport]:
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


class SpecialistPoolServiceClient(metaclass=SpecialistPoolServiceClientMeta):
    """A service for creating and managing Customer SpecialistPools.
    When customers start Data Labeling jobs, they can reuse/create
    Specialist Pools to bring their own Specialists to label the
    data. Customers can add/remove Managers for the Specialist Pool
    on Cloud console, then Managers will get email notifications to
    manage Specialists and tasks on CrowdCompute console.
    """

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

    @staticmethod
    def specialist_pool_path(project: str, location: str, specialist_pool: str,) -> str:
        """Return a fully-qualified specialist_pool string."""
        return "projects/{project}/locations/{location}/specialistPools/{specialist_pool}".format(
            project=project, location=location, specialist_pool=specialist_pool,
        )

    def __init__(
        self,
        *,
        credentials: credentials.Credentials = None,
        transport: Union[str, SpecialistPoolServiceTransport] = None,
        client_options: ClientOptions.ClientOptions = DEFAULT_OPTIONS,
    ) -> None:
        """Instantiate the specialist pool service client.

        Args:
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            transport (Union[str, ~.SpecialistPoolServiceTransport]): The
                transport to use. If set to None, a transport is chosen
                automatically.
            client_options (ClientOptions): Custom options for the client.
        """
        if isinstance(client_options, dict):
            client_options = ClientOptions.from_dict(client_options)

        # Save or instantiate the transport.
        # Ordinarily, we provide the transport, but allowing a custom transport
        # instance provides an extensibility point for unusual situations.
        if isinstance(transport, SpecialistPoolServiceTransport):
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

    def create_specialist_pool(
        self,
        request: specialist_pool_service.CreateSpecialistPoolRequest = None,
        *,
        parent: str = None,
        specialist_pool: gca_specialist_pool.SpecialistPool = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> ga_operation.Operation:
        r"""Creates a SpecialistPool.

        Args:
            request (:class:`~.specialist_pool_service.CreateSpecialistPoolRequest`):
                The request object. Request message for
                [SpecialistPoolService.CreateSpecialistPool][google.cloud.aiplatform.v1beta1.SpecialistPoolService.CreateSpecialistPool].
            parent (:class:`str`):
                Required. The parent Project name for the new
                SpecialistPool. The form is
                ``projects/{project}/locations/{location}``.
                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            specialist_pool (:class:`~.gca_specialist_pool.SpecialistPool`):
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
            ~.ga_operation.Operation:
                An object representing a long-running operation.

                The result type for the operation will be
                :class:``~.gca_specialist_pool.SpecialistPool``:
                SpecialistPool represents customers' own workforce to
                work on their data labeling jobs. It includes a group of
                specialist managers who are responsible for managing the
                labelers in this pool as well as customers' data
                labeling jobs associated with this pool. Customers
                create specialist pool as well as start data labeling
                jobs on Cloud, managers and labelers work with the jobs
                using CrowdCompute console.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        if request is not None and any([parent, specialist_pool]):
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
        rpc = gapic_v1.method.wrap_method(
            self._transport.create_specialist_pool,
            default_timeout=None,
            client_info=_client_info,
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = ga_operation.from_gapic(
            response,
            self._transport.operations_client,
            gca_specialist_pool.SpecialistPool,
            metadata_type=specialist_pool_service.CreateSpecialistPoolOperationMetadata,
        )

        # Done; return the response.
        return response

    def get_specialist_pool(
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
            request (:class:`~.specialist_pool_service.GetSpecialistPoolRequest`):
                The request object. Request message for
                [SpecialistPoolService.GetSpecialistPool][google.cloud.aiplatform.v1beta1.SpecialistPoolService.GetSpecialistPool].
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
            ~.specialist_pool.SpecialistPool:
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
        if request is not None and any([name]):
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
        rpc = gapic_v1.method.wrap_method(
            self._transport.get_specialist_pool,
            default_timeout=None,
            client_info=_client_info,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("name", request.name),)),
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    def list_specialist_pools(
        self,
        request: specialist_pool_service.ListSpecialistPoolsRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListSpecialistPoolsPager:
        r"""Lists SpecialistPools in a Location.

        Args:
            request (:class:`~.specialist_pool_service.ListSpecialistPoolsRequest`):
                The request object. Request message for
                [SpecialistPoolService.ListSpecialistPools][google.cloud.aiplatform.v1beta1.SpecialistPoolService.ListSpecialistPools].
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
            ~.pagers.ListSpecialistPoolsPager:
                Response message for
                [SpecialistPoolService.ListSpecialistPools][google.cloud.aiplatform.v1beta1.SpecialistPoolService.ListSpecialistPools].

                Iterating over this object will yield results and
                resolve additional pages automatically.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        if request is not None and any([parent]):
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
        rpc = gapic_v1.method.wrap_method(
            self._transport.list_specialist_pools,
            default_timeout=None,
            client_info=_client_info,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", request.parent),)),
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # This method is paged; wrap the response in a pager, which provides
        # an `__iter__` convenience method.
        response = pagers.ListSpecialistPoolsPager(
            method=rpc, request=request, response=response,
        )

        # Done; return the response.
        return response

    def delete_specialist_pool(
        self,
        request: specialist_pool_service.DeleteSpecialistPoolRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> ga_operation.Operation:
        r"""Deletes a SpecialistPool as well as all Specialists
        in the pool.

        Args:
            request (:class:`~.specialist_pool_service.DeleteSpecialistPoolRequest`):
                The request object. Request message for
                [SpecialistPoolService.DeleteSpecialistPool][google.cloud.aiplatform.v1beta1.SpecialistPoolService.DeleteSpecialistPool].
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
            ~.ga_operation.Operation:
                An object representing a long-running operation.

                The result type for the operation will be
                :class:``~.empty.Empty``: A generic empty message that
                you can re-use to avoid defining duplicated empty
                messages in your APIs. A typical example is to use it as
                the request or the response type of an API method. For
                instance:

                ::

                    service Foo {
                      rpc Bar(google.protobuf.Empty) returns (google.protobuf.Empty);
                    }

                The JSON representation for ``Empty`` is empty JSON
                object ``{}``.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        if request is not None and any([name]):
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
        rpc = gapic_v1.method.wrap_method(
            self._transport.delete_specialist_pool,
            default_timeout=None,
            client_info=_client_info,
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = ga_operation.from_gapic(
            response,
            self._transport.operations_client,
            empty.Empty,
            metadata_type=gca_operation.DeleteOperationMetadata,
        )

        # Done; return the response.
        return response

    def update_specialist_pool(
        self,
        request: specialist_pool_service.UpdateSpecialistPoolRequest = None,
        *,
        specialist_pool: gca_specialist_pool.SpecialistPool = None,
        update_mask: field_mask.FieldMask = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> ga_operation.Operation:
        r"""Updates a SpecialistPool.

        Args:
            request (:class:`~.specialist_pool_service.UpdateSpecialistPoolRequest`):
                The request object. Request message for
                [SpecialistPoolService.UpdateSpecialistPool][google.cloud.aiplatform.v1beta1.SpecialistPoolService.UpdateSpecialistPool].
            specialist_pool (:class:`~.gca_specialist_pool.SpecialistPool`):
                Required. The SpecialistPool which
                replaces the resource on the server.
                This corresponds to the ``specialist_pool`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            update_mask (:class:`~.field_mask.FieldMask`):
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
            ~.ga_operation.Operation:
                An object representing a long-running operation.

                The result type for the operation will be
                :class:``~.gca_specialist_pool.SpecialistPool``:
                SpecialistPool represents customers' own workforce to
                work on their data labeling jobs. It includes a group of
                specialist managers who are responsible for managing the
                labelers in this pool as well as customers' data
                labeling jobs associated with this pool. Customers
                create specialist pool as well as start data labeling
                jobs on Cloud, managers and labelers work with the jobs
                using CrowdCompute console.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        if request is not None and any([specialist_pool, update_mask]):
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
        rpc = gapic_v1.method.wrap_method(
            self._transport.update_specialist_pool,
            default_timeout=None,
            client_info=_client_info,
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = ga_operation.from_gapic(
            response,
            self._transport.operations_client,
            gca_specialist_pool.SpecialistPool,
            metadata_type=specialist_pool_service.UpdateSpecialistPoolOperationMetadata,
        )

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


__all__ = ("SpecialistPoolServiceClient",)
