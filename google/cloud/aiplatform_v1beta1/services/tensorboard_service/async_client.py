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
from typing import Dict, AsyncIterable, Awaitable, Sequence, Tuple, Type, Union
import pkg_resources

import google.api_core.client_options as ClientOptions  # type: ignore
from google.api_core import exceptions as core_exceptions  # type: ignore
from google.api_core import gapic_v1  # type: ignore
from google.api_core import retry as retries  # type: ignore
from google.auth import credentials as ga_credentials  # type: ignore
from google.oauth2 import service_account  # type: ignore

from google.api_core import operation as gac_operation  # type: ignore
from google.api_core import operation_async  # type: ignore
from google.cloud.aiplatform_v1beta1.services.tensorboard_service import pagers
from google.cloud.aiplatform_v1beta1.types import encryption_spec
from google.cloud.aiplatform_v1beta1.types import operation as gca_operation
from google.cloud.aiplatform_v1beta1.types import tensorboard
from google.cloud.aiplatform_v1beta1.types import tensorboard as gca_tensorboard
from google.cloud.aiplatform_v1beta1.types import tensorboard_data
from google.cloud.aiplatform_v1beta1.types import tensorboard_experiment
from google.cloud.aiplatform_v1beta1.types import (
    tensorboard_experiment as gca_tensorboard_experiment,
)
from google.cloud.aiplatform_v1beta1.types import tensorboard_run
from google.cloud.aiplatform_v1beta1.types import tensorboard_run as gca_tensorboard_run
from google.cloud.aiplatform_v1beta1.types import tensorboard_service
from google.cloud.aiplatform_v1beta1.types import tensorboard_time_series
from google.cloud.aiplatform_v1beta1.types import (
    tensorboard_time_series as gca_tensorboard_time_series,
)
from google.protobuf import empty_pb2  # type: ignore
from google.protobuf import field_mask_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
from .transports.base import TensorboardServiceTransport, DEFAULT_CLIENT_INFO
from .transports.grpc_asyncio import TensorboardServiceGrpcAsyncIOTransport
from .client import TensorboardServiceClient


class TensorboardServiceAsyncClient:
    """TensorboardService"""

    _client: TensorboardServiceClient

    DEFAULT_ENDPOINT = TensorboardServiceClient.DEFAULT_ENDPOINT
    DEFAULT_MTLS_ENDPOINT = TensorboardServiceClient.DEFAULT_MTLS_ENDPOINT

    tensorboard_path = staticmethod(TensorboardServiceClient.tensorboard_path)
    parse_tensorboard_path = staticmethod(
        TensorboardServiceClient.parse_tensorboard_path
    )
    tensorboard_experiment_path = staticmethod(
        TensorboardServiceClient.tensorboard_experiment_path
    )
    parse_tensorboard_experiment_path = staticmethod(
        TensorboardServiceClient.parse_tensorboard_experiment_path
    )
    tensorboard_run_path = staticmethod(TensorboardServiceClient.tensorboard_run_path)
    parse_tensorboard_run_path = staticmethod(
        TensorboardServiceClient.parse_tensorboard_run_path
    )
    tensorboard_time_series_path = staticmethod(
        TensorboardServiceClient.tensorboard_time_series_path
    )
    parse_tensorboard_time_series_path = staticmethod(
        TensorboardServiceClient.parse_tensorboard_time_series_path
    )
    common_billing_account_path = staticmethod(
        TensorboardServiceClient.common_billing_account_path
    )
    parse_common_billing_account_path = staticmethod(
        TensorboardServiceClient.parse_common_billing_account_path
    )
    common_folder_path = staticmethod(TensorboardServiceClient.common_folder_path)
    parse_common_folder_path = staticmethod(
        TensorboardServiceClient.parse_common_folder_path
    )
    common_organization_path = staticmethod(
        TensorboardServiceClient.common_organization_path
    )
    parse_common_organization_path = staticmethod(
        TensorboardServiceClient.parse_common_organization_path
    )
    common_project_path = staticmethod(TensorboardServiceClient.common_project_path)
    parse_common_project_path = staticmethod(
        TensorboardServiceClient.parse_common_project_path
    )
    common_location_path = staticmethod(TensorboardServiceClient.common_location_path)
    parse_common_location_path = staticmethod(
        TensorboardServiceClient.parse_common_location_path
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
            TensorboardServiceAsyncClient: The constructed client.
        """
        return TensorboardServiceClient.from_service_account_info.__func__(TensorboardServiceAsyncClient, info, *args, **kwargs)  # type: ignore

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
            TensorboardServiceAsyncClient: The constructed client.
        """
        return TensorboardServiceClient.from_service_account_file.__func__(TensorboardServiceAsyncClient, filename, *args, **kwargs)  # type: ignore

    from_service_account_json = from_service_account_file

    @property
    def transport(self) -> TensorboardServiceTransport:
        """Returns the transport used by the client instance.

        Returns:
            TensorboardServiceTransport: The transport used by the client instance.
        """
        return self._client.transport

    get_transport_class = functools.partial(
        type(TensorboardServiceClient).get_transport_class,
        type(TensorboardServiceClient),
    )

    def __init__(
        self,
        *,
        credentials: ga_credentials.Credentials = None,
        transport: Union[str, TensorboardServiceTransport] = "grpc_asyncio",
        client_options: ClientOptions = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
    ) -> None:
        """Instantiates the tensorboard service client.

        Args:
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            transport (Union[str, ~.TensorboardServiceTransport]): The
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
        self._client = TensorboardServiceClient(
            credentials=credentials,
            transport=transport,
            client_options=client_options,
            client_info=client_info,
        )

    async def create_tensorboard(
        self,
        request: tensorboard_service.CreateTensorboardRequest = None,
        *,
        parent: str = None,
        tensorboard: gca_tensorboard.Tensorboard = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Creates a Tensorboard.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.CreateTensorboardRequest`):
                The request object. Request message for
                [TensorboardService.CreateTensorboard][google.cloud.aiplatform.v1beta1.TensorboardService.CreateTensorboard].
            parent (:class:`str`):
                Required. The resource name of the Location to create
                the Tensorboard in. Format:
                ``projects/{project}/locations/{location}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            tensorboard (:class:`google.cloud.aiplatform_v1beta1.types.Tensorboard`):
                Required. The Tensorboard to create.
                This corresponds to the ``tensorboard`` field
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

                The result type for the operation will be :class:`google.cloud.aiplatform_v1beta1.types.Tensorboard` Tensorboard is a physical database that stores users' training metrics.
                   A default Tensorboard is provided in each region of a
                   GCP project. If needed users can also create extra
                   Tensorboards in their projects.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, tensorboard])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = tensorboard_service.CreateTensorboardRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if tensorboard is not None:
            request.tensorboard = tensorboard

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_tensorboard,
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
            gca_tensorboard.Tensorboard,
            metadata_type=tensorboard_service.CreateTensorboardOperationMetadata,
        )

        # Done; return the response.
        return response

    async def get_tensorboard(
        self,
        request: tensorboard_service.GetTensorboardRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> tensorboard.Tensorboard:
        r"""Gets a Tensorboard.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.GetTensorboardRequest`):
                The request object. Request message for
                [TensorboardService.GetTensorboard][google.cloud.aiplatform.v1beta1.TensorboardService.GetTensorboard].
            name (:class:`str`):
                Required. The name of the Tensorboard resource. Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.Tensorboard:
                Tensorboard is a physical database
                that stores users' training metrics. A
                default Tensorboard is provided in each
                region of a GCP project. If needed users
                can also create extra Tensorboards in
                their projects.

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

        request = tensorboard_service.GetTensorboardRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_tensorboard,
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

    async def update_tensorboard(
        self,
        request: tensorboard_service.UpdateTensorboardRequest = None,
        *,
        tensorboard: gca_tensorboard.Tensorboard = None,
        update_mask: field_mask_pb2.FieldMask = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Updates a Tensorboard.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.UpdateTensorboardRequest`):
                The request object. Request message for
                [TensorboardService.UpdateTensorboard][google.cloud.aiplatform.v1beta1.TensorboardService.UpdateTensorboard].
            tensorboard (:class:`google.cloud.aiplatform_v1beta1.types.Tensorboard`):
                Required. The Tensorboard's ``name`` field is used to
                identify the Tensorboard to be updated. Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}``

                This corresponds to the ``tensorboard`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            update_mask (:class:`google.protobuf.field_mask_pb2.FieldMask`):
                Required. Field mask is used to specify the fields to be
                overwritten in the Tensorboard resource by the update.
                The fields specified in the update_mask are relative to
                the resource, not the full request. A field will be
                overwritten if it is in the mask. If the user does not
                provide a mask then all fields will be overwritten if
                new values are specified.

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

                The result type for the operation will be :class:`google.cloud.aiplatform_v1beta1.types.Tensorboard` Tensorboard is a physical database that stores users' training metrics.
                   A default Tensorboard is provided in each region of a
                   GCP project. If needed users can also create extra
                   Tensorboards in their projects.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([tensorboard, update_mask])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = tensorboard_service.UpdateTensorboardRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if tensorboard is not None:
            request.tensorboard = tensorboard
        if update_mask is not None:
            request.update_mask = update_mask

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.update_tensorboard,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("tensorboard.name", request.tensorboard.name),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = operation_async.from_gapic(
            response,
            self._client._transport.operations_client,
            gca_tensorboard.Tensorboard,
            metadata_type=tensorboard_service.UpdateTensorboardOperationMetadata,
        )

        # Done; return the response.
        return response

    async def list_tensorboards(
        self,
        request: tensorboard_service.ListTensorboardsRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListTensorboardsAsyncPager:
        r"""Lists Tensorboards in a Location.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.ListTensorboardsRequest`):
                The request object. Request message for
                [TensorboardService.ListTensorboards][google.cloud.aiplatform.v1beta1.TensorboardService.ListTensorboards].
            parent (:class:`str`):
                Required. The resource name of the Location to list
                Tensorboards. Format:
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
            google.cloud.aiplatform_v1beta1.services.tensorboard_service.pagers.ListTensorboardsAsyncPager:
                Response message for
                [TensorboardService.ListTensorboards][google.cloud.aiplatform.v1beta1.TensorboardService.ListTensorboards].

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

        request = tensorboard_service.ListTensorboardsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_tensorboards,
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
        response = pagers.ListTensorboardsAsyncPager(
            method=rpc, request=request, response=response, metadata=metadata,
        )

        # Done; return the response.
        return response

    async def delete_tensorboard(
        self,
        request: tensorboard_service.DeleteTensorboardRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Deletes a Tensorboard.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.DeleteTensorboardRequest`):
                The request object. Request message for
                [TensorboardService.DeleteTensorboard][google.cloud.aiplatform.v1beta1.TensorboardService.DeleteTensorboard].
            name (:class:`str`):
                Required. The name of the Tensorboard to be deleted.
                Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}``

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

        request = tensorboard_service.DeleteTensorboardRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.delete_tensorboard,
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

    async def create_tensorboard_experiment(
        self,
        request: tensorboard_service.CreateTensorboardExperimentRequest = None,
        *,
        parent: str = None,
        tensorboard_experiment: gca_tensorboard_experiment.TensorboardExperiment = None,
        tensorboard_experiment_id: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_tensorboard_experiment.TensorboardExperiment:
        r"""Creates a TensorboardExperiment.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.CreateTensorboardExperimentRequest`):
                The request object. Request message for
                [TensorboardService.CreateTensorboardExperiment][google.cloud.aiplatform.v1beta1.TensorboardService.CreateTensorboardExperiment].
            parent (:class:`str`):
                Required. The resource name of the Tensorboard to create
                the TensorboardExperiment in. Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            tensorboard_experiment (:class:`google.cloud.aiplatform_v1beta1.types.TensorboardExperiment`):
                The TensorboardExperiment to create.
                This corresponds to the ``tensorboard_experiment`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            tensorboard_experiment_id (:class:`str`):
                Required. The ID to use for the Tensorboard experiment,
                which will become the final component of the Tensorboard
                experiment's resource name.

                This value should be 1-128 characters, and valid
                characters are /[a-z][0-9]-/.

                This corresponds to the ``tensorboard_experiment_id`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.TensorboardExperiment:
                A TensorboardExperiment is a group of
                TensorboardRuns, that are typically the
                results of a training job run, in a
                Tensorboard.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any(
            [parent, tensorboard_experiment, tensorboard_experiment_id]
        )
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = tensorboard_service.CreateTensorboardExperimentRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if tensorboard_experiment is not None:
            request.tensorboard_experiment = tensorboard_experiment
        if tensorboard_experiment_id is not None:
            request.tensorboard_experiment_id = tensorboard_experiment_id

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_tensorboard_experiment,
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

        # Done; return the response.
        return response

    async def get_tensorboard_experiment(
        self,
        request: tensorboard_service.GetTensorboardExperimentRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> tensorboard_experiment.TensorboardExperiment:
        r"""Gets a TensorboardExperiment.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.GetTensorboardExperimentRequest`):
                The request object. Request message for
                [TensorboardService.GetTensorboardExperiment][google.cloud.aiplatform.v1beta1.TensorboardService.GetTensorboardExperiment].
            name (:class:`str`):
                Required. The name of the TensorboardExperiment
                resource. Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.TensorboardExperiment:
                A TensorboardExperiment is a group of
                TensorboardRuns, that are typically the
                results of a training job run, in a
                Tensorboard.

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

        request = tensorboard_service.GetTensorboardExperimentRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_tensorboard_experiment,
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

    async def update_tensorboard_experiment(
        self,
        request: tensorboard_service.UpdateTensorboardExperimentRequest = None,
        *,
        tensorboard_experiment: gca_tensorboard_experiment.TensorboardExperiment = None,
        update_mask: field_mask_pb2.FieldMask = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_tensorboard_experiment.TensorboardExperiment:
        r"""Updates a TensorboardExperiment.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.UpdateTensorboardExperimentRequest`):
                The request object. Request message for
                [TensorboardService.UpdateTensorboardExperiment][google.cloud.aiplatform.v1beta1.TensorboardService.UpdateTensorboardExperiment].
            tensorboard_experiment (:class:`google.cloud.aiplatform_v1beta1.types.TensorboardExperiment`):
                Required. The TensorboardExperiment's ``name`` field is
                used to identify the TensorboardExperiment to be
                updated. Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}``

                This corresponds to the ``tensorboard_experiment`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            update_mask (:class:`google.protobuf.field_mask_pb2.FieldMask`):
                Required. Field mask is used to specify the fields to be
                overwritten in the TensorboardExperiment resource by the
                update. The fields specified in the update_mask are
                relative to the resource, not the full request. A field
                will be overwritten if it is in the mask. If the user
                does not provide a mask then all fields will be
                overwritten if new values are specified.

                This corresponds to the ``update_mask`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.TensorboardExperiment:
                A TensorboardExperiment is a group of
                TensorboardRuns, that are typically the
                results of a training job run, in a
                Tensorboard.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([tensorboard_experiment, update_mask])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = tensorboard_service.UpdateTensorboardExperimentRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if tensorboard_experiment is not None:
            request.tensorboard_experiment = tensorboard_experiment
        if update_mask is not None:
            request.update_mask = update_mask

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.update_tensorboard_experiment,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("tensorboard_experiment.name", request.tensorboard_experiment.name),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def list_tensorboard_experiments(
        self,
        request: tensorboard_service.ListTensorboardExperimentsRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListTensorboardExperimentsAsyncPager:
        r"""Lists TensorboardExperiments in a Location.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.ListTensorboardExperimentsRequest`):
                The request object. Request message for
                [TensorboardService.ListTensorboardExperiments][google.cloud.aiplatform.v1beta1.TensorboardService.ListTensorboardExperiments].
            parent (:class:`str`):
                Required. The resource name of the
                Tensorboard to list
                TensorboardExperiments. Format:
                'projects/{project}/locations/{location}/tensorboards/{tensorboard}'

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.services.tensorboard_service.pagers.ListTensorboardExperimentsAsyncPager:
                Response message for
                [TensorboardService.ListTensorboardExperiments][google.cloud.aiplatform.v1beta1.TensorboardService.ListTensorboardExperiments].

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

        request = tensorboard_service.ListTensorboardExperimentsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_tensorboard_experiments,
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
        response = pagers.ListTensorboardExperimentsAsyncPager(
            method=rpc, request=request, response=response, metadata=metadata,
        )

        # Done; return the response.
        return response

    async def delete_tensorboard_experiment(
        self,
        request: tensorboard_service.DeleteTensorboardExperimentRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Deletes a TensorboardExperiment.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.DeleteTensorboardExperimentRequest`):
                The request object. Request message for
                [TensorboardService.DeleteTensorboardExperiment][google.cloud.aiplatform.v1beta1.TensorboardService.DeleteTensorboardExperiment].
            name (:class:`str`):
                Required. The name of the TensorboardExperiment to be
                deleted. Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}``

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

        request = tensorboard_service.DeleteTensorboardExperimentRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.delete_tensorboard_experiment,
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

    async def create_tensorboard_run(
        self,
        request: tensorboard_service.CreateTensorboardRunRequest = None,
        *,
        parent: str = None,
        tensorboard_run: gca_tensorboard_run.TensorboardRun = None,
        tensorboard_run_id: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_tensorboard_run.TensorboardRun:
        r"""Creates a TensorboardRun.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.CreateTensorboardRunRequest`):
                The request object. Request message for
                [TensorboardService.CreateTensorboardRun][google.cloud.aiplatform.v1beta1.TensorboardService.CreateTensorboardRun].
            parent (:class:`str`):
                Required. The resource name of the TensorboardExperiment
                to create the TensorboardRun in. Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            tensorboard_run (:class:`google.cloud.aiplatform_v1beta1.types.TensorboardRun`):
                Required. The TensorboardRun to
                create.

                This corresponds to the ``tensorboard_run`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            tensorboard_run_id (:class:`str`):
                Required. The ID to use for the Tensorboard run, which
                will become the final component of the Tensorboard run's
                resource name.

                This value should be 1-128 characters, and valid
                characters are /[a-z][0-9]-/.

                This corresponds to the ``tensorboard_run_id`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.TensorboardRun:
                TensorboardRun maps to a specific
                execution of a training job with a given
                set of hyperparameter values, model
                definition, dataset, etc

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, tensorboard_run, tensorboard_run_id])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = tensorboard_service.CreateTensorboardRunRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if tensorboard_run is not None:
            request.tensorboard_run = tensorboard_run
        if tensorboard_run_id is not None:
            request.tensorboard_run_id = tensorboard_run_id

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_tensorboard_run,
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

        # Done; return the response.
        return response

    async def batch_create_tensorboard_runs(
        self,
        request: tensorboard_service.BatchCreateTensorboardRunsRequest = None,
        *,
        parent: str = None,
        requests: Sequence[tensorboard_service.CreateTensorboardRunRequest] = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> tensorboard_service.BatchCreateTensorboardRunsResponse:
        r"""Batch create TensorboardRuns.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.BatchCreateTensorboardRunsRequest`):
                The request object. Request message for
                [TensorboardService.BatchCreateTensorboardRuns][google.cloud.aiplatform.v1beta1.TensorboardService.BatchCreateTensorboardRuns].
            parent (:class:`str`):
                Required. The resource name of the TensorboardExperiment
                to create the TensorboardRuns in. Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}``
                The parent field in the CreateTensorboardRunRequest
                messages must match this field.

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            requests (:class:`Sequence[google.cloud.aiplatform_v1beta1.types.CreateTensorboardRunRequest]`):
                Required. The request message
                specifying the TensorboardRuns to
                create. A maximum of 1000
                TensorboardRuns can be created in a
                batch.

                This corresponds to the ``requests`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.BatchCreateTensorboardRunsResponse:
                Response message for
                [TensorboardService.BatchCreateTensorboardRuns][google.cloud.aiplatform.v1beta1.TensorboardService.BatchCreateTensorboardRuns].

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

        request = tensorboard_service.BatchCreateTensorboardRunsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if requests:
            request.requests.extend(requests)

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.batch_create_tensorboard_runs,
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

        # Done; return the response.
        return response

    async def get_tensorboard_run(
        self,
        request: tensorboard_service.GetTensorboardRunRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> tensorboard_run.TensorboardRun:
        r"""Gets a TensorboardRun.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.GetTensorboardRunRequest`):
                The request object. Request message for
                [TensorboardService.GetTensorboardRun][google.cloud.aiplatform.v1beta1.TensorboardService.GetTensorboardRun].
            name (:class:`str`):
                Required. The name of the TensorboardRun resource.
                Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}/runs/{run}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.TensorboardRun:
                TensorboardRun maps to a specific
                execution of a training job with a given
                set of hyperparameter values, model
                definition, dataset, etc

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

        request = tensorboard_service.GetTensorboardRunRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_tensorboard_run,
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

    async def update_tensorboard_run(
        self,
        request: tensorboard_service.UpdateTensorboardRunRequest = None,
        *,
        tensorboard_run: gca_tensorboard_run.TensorboardRun = None,
        update_mask: field_mask_pb2.FieldMask = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_tensorboard_run.TensorboardRun:
        r"""Updates a TensorboardRun.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.UpdateTensorboardRunRequest`):
                The request object. Request message for
                [TensorboardService.UpdateTensorboardRun][google.cloud.aiplatform.v1beta1.TensorboardService.UpdateTensorboardRun].
            tensorboard_run (:class:`google.cloud.aiplatform_v1beta1.types.TensorboardRun`):
                Required. The TensorboardRun's ``name`` field is used to
                identify the TensorboardRun to be updated. Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}/runs/{run}``

                This corresponds to the ``tensorboard_run`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            update_mask (:class:`google.protobuf.field_mask_pb2.FieldMask`):
                Required. Field mask is used to specify the fields to be
                overwritten in the TensorboardRun resource by the
                update. The fields specified in the update_mask are
                relative to the resource, not the full request. A field
                will be overwritten if it is in the mask. If the user
                does not provide a mask then all fields will be
                overwritten if new values are specified.

                This corresponds to the ``update_mask`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.TensorboardRun:
                TensorboardRun maps to a specific
                execution of a training job with a given
                set of hyperparameter values, model
                definition, dataset, etc

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([tensorboard_run, update_mask])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = tensorboard_service.UpdateTensorboardRunRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if tensorboard_run is not None:
            request.tensorboard_run = tensorboard_run
        if update_mask is not None:
            request.update_mask = update_mask

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.update_tensorboard_run,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("tensorboard_run.name", request.tensorboard_run.name),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def list_tensorboard_runs(
        self,
        request: tensorboard_service.ListTensorboardRunsRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListTensorboardRunsAsyncPager:
        r"""Lists TensorboardRuns in a Location.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.ListTensorboardRunsRequest`):
                The request object. Request message for
                [TensorboardService.ListTensorboardRuns][google.cloud.aiplatform.v1beta1.TensorboardService.ListTensorboardRuns].
            parent (:class:`str`):
                Required. The resource name of the
                TensorboardExperiment to list
                TensorboardRuns. Format:
                'projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}'

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.services.tensorboard_service.pagers.ListTensorboardRunsAsyncPager:
                Response message for
                [TensorboardService.ListTensorboardRuns][google.cloud.aiplatform.v1beta1.TensorboardService.ListTensorboardRuns].

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

        request = tensorboard_service.ListTensorboardRunsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_tensorboard_runs,
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
        response = pagers.ListTensorboardRunsAsyncPager(
            method=rpc, request=request, response=response, metadata=metadata,
        )

        # Done; return the response.
        return response

    async def delete_tensorboard_run(
        self,
        request: tensorboard_service.DeleteTensorboardRunRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Deletes a TensorboardRun.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.DeleteTensorboardRunRequest`):
                The request object. Request message for
                [TensorboardService.DeleteTensorboardRun][google.cloud.aiplatform.v1beta1.TensorboardService.DeleteTensorboardRun].
            name (:class:`str`):
                Required. The name of the TensorboardRun to be deleted.
                Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}/runs/{run}``

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

        request = tensorboard_service.DeleteTensorboardRunRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.delete_tensorboard_run,
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

    async def batch_create_tensorboard_time_series(
        self,
        request: tensorboard_service.BatchCreateTensorboardTimeSeriesRequest = None,
        *,
        parent: str = None,
        requests: Sequence[
            tensorboard_service.CreateTensorboardTimeSeriesRequest
        ] = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> tensorboard_service.BatchCreateTensorboardTimeSeriesResponse:
        r"""Batch create TensorboardTimeSeries that belong to a
        TensorboardExperiment.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.BatchCreateTensorboardTimeSeriesRequest`):
                The request object. Request message for
                [TensorboardService.BatchCreateTensorboardTimeSeries][google.cloud.aiplatform.v1beta1.TensorboardService.BatchCreateTensorboardTimeSeries].
            parent (:class:`str`):
                Required. The resource name of the TensorboardExperiment
                to create the TensorboardTimeSeries in. Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}``
                The TensorboardRuns referenced by the parent fields in
                the CreateTensorboardTimeSeriesRequest messages must be
                sub resources of this TensorboardExperiment.

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            requests (:class:`Sequence[google.cloud.aiplatform_v1beta1.types.CreateTensorboardTimeSeriesRequest]`):
                Required. The request message
                specifying the TensorboardTimeSeries to
                create. A maximum of 1000
                TensorboardTimeSeries can be created in
                a batch.

                This corresponds to the ``requests`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.BatchCreateTensorboardTimeSeriesResponse:
                Response message for
                [TensorboardService.BatchCreateTensorboardTimeSeries][google.cloud.aiplatform.v1beta1.TensorboardService.BatchCreateTensorboardTimeSeries].

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

        request = tensorboard_service.BatchCreateTensorboardTimeSeriesRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if requests:
            request.requests.extend(requests)

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.batch_create_tensorboard_time_series,
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

        # Done; return the response.
        return response

    async def create_tensorboard_time_series(
        self,
        request: tensorboard_service.CreateTensorboardTimeSeriesRequest = None,
        *,
        parent: str = None,
        tensorboard_time_series: gca_tensorboard_time_series.TensorboardTimeSeries = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_tensorboard_time_series.TensorboardTimeSeries:
        r"""Creates a TensorboardTimeSeries.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.CreateTensorboardTimeSeriesRequest`):
                The request object. Request message for
                [TensorboardService.CreateTensorboardTimeSeries][google.cloud.aiplatform.v1beta1.TensorboardService.CreateTensorboardTimeSeries].
            parent (:class:`str`):
                Required. The resource name of the TensorboardRun to
                create the TensorboardTimeSeries in. Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}/runs/{run}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            tensorboard_time_series (:class:`google.cloud.aiplatform_v1beta1.types.TensorboardTimeSeries`):
                Required. The TensorboardTimeSeries
                to create.

                This corresponds to the ``tensorboard_time_series`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.TensorboardTimeSeries:
                TensorboardTimeSeries maps to times
                series produced in training runs

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, tensorboard_time_series])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = tensorboard_service.CreateTensorboardTimeSeriesRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if tensorboard_time_series is not None:
            request.tensorboard_time_series = tensorboard_time_series

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_tensorboard_time_series,
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

        # Done; return the response.
        return response

    async def get_tensorboard_time_series(
        self,
        request: tensorboard_service.GetTensorboardTimeSeriesRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> tensorboard_time_series.TensorboardTimeSeries:
        r"""Gets a TensorboardTimeSeries.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.GetTensorboardTimeSeriesRequest`):
                The request object. Request message for
                [TensorboardService.GetTensorboardTimeSeries][google.cloud.aiplatform.v1beta1.TensorboardService.GetTensorboardTimeSeries].
            name (:class:`str`):
                Required. The name of the TensorboardTimeSeries
                resource. Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}/runs/{run}/timeSeries/{time_series}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.TensorboardTimeSeries:
                TensorboardTimeSeries maps to times
                series produced in training runs

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

        request = tensorboard_service.GetTensorboardTimeSeriesRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_tensorboard_time_series,
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

    async def update_tensorboard_time_series(
        self,
        request: tensorboard_service.UpdateTensorboardTimeSeriesRequest = None,
        *,
        tensorboard_time_series: gca_tensorboard_time_series.TensorboardTimeSeries = None,
        update_mask: field_mask_pb2.FieldMask = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_tensorboard_time_series.TensorboardTimeSeries:
        r"""Updates a TensorboardTimeSeries.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.UpdateTensorboardTimeSeriesRequest`):
                The request object. Request message for
                [TensorboardService.UpdateTensorboardTimeSeries][google.cloud.aiplatform.v1beta1.TensorboardService.UpdateTensorboardTimeSeries].
            tensorboard_time_series (:class:`google.cloud.aiplatform_v1beta1.types.TensorboardTimeSeries`):
                Required. The TensorboardTimeSeries' ``name`` field is
                used to identify the TensorboardTimeSeries to be
                updated. Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}/runs/{run}/timeSeries/{time_series}``

                This corresponds to the ``tensorboard_time_series`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            update_mask (:class:`google.protobuf.field_mask_pb2.FieldMask`):
                Required. Field mask is used to specify the fields to be
                overwritten in the TensorboardTimeSeries resource by the
                update. The fields specified in the update_mask are
                relative to the resource, not the full request. A field
                will be overwritten if it is in the mask. If the user
                does not provide a mask then all fields will be
                overwritten if new values are specified.

                This corresponds to the ``update_mask`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.TensorboardTimeSeries:
                TensorboardTimeSeries maps to times
                series produced in training runs

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([tensorboard_time_series, update_mask])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = tensorboard_service.UpdateTensorboardTimeSeriesRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if tensorboard_time_series is not None:
            request.tensorboard_time_series = tensorboard_time_series
        if update_mask is not None:
            request.update_mask = update_mask

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.update_tensorboard_time_series,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (
                    (
                        "tensorboard_time_series.name",
                        request.tensorboard_time_series.name,
                    ),
                )
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def list_tensorboard_time_series(
        self,
        request: tensorboard_service.ListTensorboardTimeSeriesRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListTensorboardTimeSeriesAsyncPager:
        r"""Lists TensorboardTimeSeries in a Location.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.ListTensorboardTimeSeriesRequest`):
                The request object. Request message for
                [TensorboardService.ListTensorboardTimeSeries][google.cloud.aiplatform.v1beta1.TensorboardService.ListTensorboardTimeSeries].
            parent (:class:`str`):
                Required. The resource name of the
                TensorboardRun to list
                TensorboardTimeSeries. Format:
                'projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}/runs/{run}'

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.services.tensorboard_service.pagers.ListTensorboardTimeSeriesAsyncPager:
                Response message for
                [TensorboardService.ListTensorboardTimeSeries][google.cloud.aiplatform.v1beta1.TensorboardService.ListTensorboardTimeSeries].

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

        request = tensorboard_service.ListTensorboardTimeSeriesRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_tensorboard_time_series,
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
        response = pagers.ListTensorboardTimeSeriesAsyncPager(
            method=rpc, request=request, response=response, metadata=metadata,
        )

        # Done; return the response.
        return response

    async def delete_tensorboard_time_series(
        self,
        request: tensorboard_service.DeleteTensorboardTimeSeriesRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Deletes a TensorboardTimeSeries.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.DeleteTensorboardTimeSeriesRequest`):
                The request object. Request message for
                [TensorboardService.DeleteTensorboardTimeSeries][google.cloud.aiplatform.v1beta1.TensorboardService.DeleteTensorboardTimeSeries].
            name (:class:`str`):
                Required. The name of the TensorboardTimeSeries to be
                deleted. Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}/runs/{run}/timeSeries/{time_series}``

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

        request = tensorboard_service.DeleteTensorboardTimeSeriesRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.delete_tensorboard_time_series,
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

    async def read_tensorboard_time_series_data(
        self,
        request: tensorboard_service.ReadTensorboardTimeSeriesDataRequest = None,
        *,
        tensorboard_time_series: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> tensorboard_service.ReadTensorboardTimeSeriesDataResponse:
        r"""Reads a TensorboardTimeSeries' data. Data is returned in
        paginated responses. By default, if the number of data points
        stored is less than 1000, all data will be returned. Otherwise,
        1000 data points will be randomly selected from this time series
        and returned. This value can be changed by changing
        max_data_points.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.ReadTensorboardTimeSeriesDataRequest`):
                The request object. Request message for
                [TensorboardService.ReadTensorboardTimeSeriesData][google.cloud.aiplatform.v1beta1.TensorboardService.ReadTensorboardTimeSeriesData].
            tensorboard_time_series (:class:`str`):
                Required. The resource name of the TensorboardTimeSeries
                to read data from. Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}/runs/{run}/timeSeries/{time_series}``

                This corresponds to the ``tensorboard_time_series`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.ReadTensorboardTimeSeriesDataResponse:
                Response message for
                [TensorboardService.ReadTensorboardTimeSeriesData][google.cloud.aiplatform.v1beta1.TensorboardService.ReadTensorboardTimeSeriesData].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([tensorboard_time_series])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = tensorboard_service.ReadTensorboardTimeSeriesDataRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if tensorboard_time_series is not None:
            request.tensorboard_time_series = tensorboard_time_series

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.read_tensorboard_time_series_data,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("tensorboard_time_series", request.tensorboard_time_series),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    def read_tensorboard_blob_data(
        self,
        request: tensorboard_service.ReadTensorboardBlobDataRequest = None,
        *,
        time_series: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> Awaitable[AsyncIterable[tensorboard_service.ReadTensorboardBlobDataResponse]]:
        r"""Gets bytes of TensorboardBlobs.
        This is to allow reading blob data stored in consumer
        project's Cloud Storage bucket without users having to
        obtain Cloud Storage access permission.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.ReadTensorboardBlobDataRequest`):
                The request object. Request message for
                [TensorboardService.ReadTensorboardBlobData][google.cloud.aiplatform.v1beta1.TensorboardService.ReadTensorboardBlobData].
            time_series (:class:`str`):
                Required. The resource name of the TensorboardTimeSeries
                to list Blobs. Format:
                'projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}/runs/{run}/timeSeries/{time_series}'

                This corresponds to the ``time_series`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            AsyncIterable[google.cloud.aiplatform_v1beta1.types.ReadTensorboardBlobDataResponse]:
                Response message for
                [TensorboardService.ReadTensorboardBlobData][google.cloud.aiplatform.v1beta1.TensorboardService.ReadTensorboardBlobData].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([time_series])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = tensorboard_service.ReadTensorboardBlobDataRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if time_series is not None:
            request.time_series = time_series

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.read_tensorboard_blob_data,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("time_series", request.time_series),)
            ),
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def write_tensorboard_experiment_data(
        self,
        request: tensorboard_service.WriteTensorboardExperimentDataRequest = None,
        *,
        tensorboard_experiment: str = None,
        write_run_data_requests: Sequence[
            tensorboard_service.WriteTensorboardRunDataRequest
        ] = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> tensorboard_service.WriteTensorboardExperimentDataResponse:
        r"""Write time series data points of multiple
        TensorboardTimeSeries in multiple TensorboardRun's. If
        any data fail to be ingested, an error will be returned.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.WriteTensorboardExperimentDataRequest`):
                The request object. Request message for
                [TensorboardService.WriteTensorboardExperimentData][google.cloud.aiplatform.v1beta1.TensorboardService.WriteTensorboardExperimentData].
            tensorboard_experiment (:class:`str`):
                Required. The resource name of the TensorboardExperiment
                to write data to. Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}``

                This corresponds to the ``tensorboard_experiment`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            write_run_data_requests (:class:`Sequence[google.cloud.aiplatform_v1beta1.types.WriteTensorboardRunDataRequest]`):
                Required. Requests containing per-run
                TensorboardTimeSeries data to write.

                This corresponds to the ``write_run_data_requests`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.WriteTensorboardExperimentDataResponse:
                Response message for
                [TensorboardService.WriteTensorboardExperimentData][google.cloud.aiplatform.v1beta1.TensorboardService.WriteTensorboardExperimentData].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([tensorboard_experiment, write_run_data_requests])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = tensorboard_service.WriteTensorboardExperimentDataRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if tensorboard_experiment is not None:
            request.tensorboard_experiment = tensorboard_experiment
        if write_run_data_requests:
            request.write_run_data_requests.extend(write_run_data_requests)

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.write_tensorboard_experiment_data,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("tensorboard_experiment", request.tensorboard_experiment),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def write_tensorboard_run_data(
        self,
        request: tensorboard_service.WriteTensorboardRunDataRequest = None,
        *,
        tensorboard_run: str = None,
        time_series_data: Sequence[tensorboard_data.TimeSeriesData] = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> tensorboard_service.WriteTensorboardRunDataResponse:
        r"""Write time series data points into multiple
        TensorboardTimeSeries under a TensorboardRun. If any
        data fail to be ingested, an error will be returned.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.WriteTensorboardRunDataRequest`):
                The request object. Request message for
                [TensorboardService.WriteTensorboardRunData][google.cloud.aiplatform.v1beta1.TensorboardService.WriteTensorboardRunData].
            tensorboard_run (:class:`str`):
                Required. The resource name of the TensorboardRun to
                write data to. Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}/runs/{run}``

                This corresponds to the ``tensorboard_run`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            time_series_data (:class:`Sequence[google.cloud.aiplatform_v1beta1.types.TimeSeriesData]`):
                Required. The TensorboardTimeSeries
                data to write. Values with in a time
                series are indexed by their step value.
                Repeated writes to the same step will
                overwrite the existing value for that
                step.
                The upper limit of data points per write
                request is 5000.

                This corresponds to the ``time_series_data`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.WriteTensorboardRunDataResponse:
                Response message for
                [TensorboardService.WriteTensorboardRunData][google.cloud.aiplatform.v1beta1.TensorboardService.WriteTensorboardRunData].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([tensorboard_run, time_series_data])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = tensorboard_service.WriteTensorboardRunDataRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if tensorboard_run is not None:
            request.tensorboard_run = tensorboard_run
        if time_series_data:
            request.time_series_data.extend(time_series_data)

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.write_tensorboard_run_data,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("tensorboard_run", request.tensorboard_run),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    async def export_tensorboard_time_series_data(
        self,
        request: tensorboard_service.ExportTensorboardTimeSeriesDataRequest = None,
        *,
        tensorboard_time_series: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ExportTensorboardTimeSeriesDataAsyncPager:
        r"""Exports a TensorboardTimeSeries' data. Data is
        returned in paginated responses.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.ExportTensorboardTimeSeriesDataRequest`):
                The request object. Request message for
                [TensorboardService.ExportTensorboardTimeSeriesData][google.cloud.aiplatform.v1beta1.TensorboardService.ExportTensorboardTimeSeriesData].
            tensorboard_time_series (:class:`str`):
                Required. The resource name of the TensorboardTimeSeries
                to export data from. Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}/runs/{run}/timeSeries/{time_series}``

                This corresponds to the ``tensorboard_time_series`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.services.tensorboard_service.pagers.ExportTensorboardTimeSeriesDataAsyncPager:
                Response message for
                [TensorboardService.ExportTensorboardTimeSeriesData][google.cloud.aiplatform.v1beta1.TensorboardService.ExportTensorboardTimeSeriesData].

                Iterating over this object will yield results and
                resolve additional pages automatically.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([tensorboard_time_series])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = tensorboard_service.ExportTensorboardTimeSeriesDataRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if tensorboard_time_series is not None:
            request.tensorboard_time_series = tensorboard_time_series

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.export_tensorboard_time_series_data,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("tensorboard_time_series", request.tensorboard_time_series),)
            ),
        )

        # Send the request.
        response = await rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # This method is paged; wrap the response in a pager, which provides
        # an `__aiter__` convenience method.
        response = pagers.ExportTensorboardTimeSeriesDataAsyncPager(
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


__all__ = ("TensorboardServiceAsyncClient",)
