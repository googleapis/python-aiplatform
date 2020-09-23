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
from google.cloud.aiplatform_v1beta1.services.endpoint_service import pagers
from google.cloud.aiplatform_v1beta1.types import endpoint
from google.cloud.aiplatform_v1beta1.types import endpoint as gca_endpoint
from google.cloud.aiplatform_v1beta1.types import endpoint_service
from google.cloud.aiplatform_v1beta1.types import operation as gca_operation
from google.protobuf import empty_pb2 as empty  # type: ignore
from google.protobuf import field_mask_pb2 as field_mask  # type: ignore
from google.protobuf import timestamp_pb2 as timestamp  # type: ignore

from .transports.base import EndpointServiceTransport
from .transports.grpc import EndpointServiceGrpcTransport


class EndpointServiceClientMeta(type):
    """Metaclass for the EndpointService client.

    This provides class-level methods for building and retrieving
    support objects (e.g. transport) without polluting the client instance
    objects.
    """

    _transport_registry = (
        OrderedDict()
    )  # type: Dict[str, Type[EndpointServiceTransport]]
    _transport_registry["grpc"] = EndpointServiceGrpcTransport

    def get_transport_class(cls, label: str = None,) -> Type[EndpointServiceTransport]:
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


class EndpointServiceClient(metaclass=EndpointServiceClientMeta):
    """"""

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
    def endpoint_path(project: str, location: str, endpoint: str,) -> str:
        """Return a fully-qualified endpoint string."""
        return "projects/{project}/locations/{location}/endpoints/{endpoint}".format(
            project=project, location=location, endpoint=endpoint,
        )

    def __init__(
        self,
        *,
        credentials: credentials.Credentials = None,
        transport: Union[str, EndpointServiceTransport] = None,
        client_options: ClientOptions.ClientOptions = DEFAULT_OPTIONS,
    ) -> None:
        """Instantiate the endpoint service client.

        Args:
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            transport (Union[str, ~.EndpointServiceTransport]): The
                transport to use. If set to None, a transport is chosen
                automatically.
            client_options (ClientOptions): Custom options for the client.
        """
        if isinstance(client_options, dict):
            client_options = ClientOptions.from_dict(client_options)

        # Save or instantiate the transport.
        # Ordinarily, we provide the transport, but allowing a custom transport
        # instance provides an extensibility point for unusual situations.
        if isinstance(transport, EndpointServiceTransport):
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

    def create_endpoint(
        self,
        request: endpoint_service.CreateEndpointRequest = None,
        *,
        parent: str = None,
        endpoint: gca_endpoint.Endpoint = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> ga_operation.Operation:
        r"""Creates an Endpoint.

        Args:
            request (:class:`~.endpoint_service.CreateEndpointRequest`):
                The request object. Request message for
                [EndpointService.CreateEndpoint][google.cloud.aiplatform.v1beta1.EndpointService.CreateEndpoint].
            parent (:class:`str`):
                Required. The resource name of the Location to create
                the Endpoint in. Format:
                ``projects/{project}/locations/{location}``
                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            endpoint (:class:`~.gca_endpoint.Endpoint`):
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
            ~.ga_operation.Operation:
                An object representing a long-running operation.

                The result type for the operation will be
                :class:``~.gca_endpoint.Endpoint``: Models are deployed
                into it, and afterwards Endpoint is called to obtain
                predictions and explanations.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        if request is not None and any([parent, endpoint]):
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
        rpc = gapic_v1.method.wrap_method(
            self._transport.create_endpoint,
            default_timeout=None,
            client_info=_client_info,
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = ga_operation.from_gapic(
            response,
            self._transport.operations_client,
            gca_endpoint.Endpoint,
            metadata_type=endpoint_service.CreateEndpointOperationMetadata,
        )

        # Done; return the response.
        return response

    def get_endpoint(
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
            request (:class:`~.endpoint_service.GetEndpointRequest`):
                The request object. Request message for
                [EndpointService.GetEndpoint][google.cloud.aiplatform.v1beta1.EndpointService.GetEndpoint]
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
            ~.endpoint.Endpoint:
                Models are deployed into it, and
                afterwards Endpoint is called to obtain
                predictions and explanations.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        if request is not None and any([name]):
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
        rpc = gapic_v1.method.wrap_method(
            self._transport.get_endpoint,
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

    def list_endpoints(
        self,
        request: endpoint_service.ListEndpointsRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListEndpointsPager:
        r"""Lists Endpoints in a Location.

        Args:
            request (:class:`~.endpoint_service.ListEndpointsRequest`):
                The request object. Request message for
                [EndpointService.ListEndpoints][google.cloud.aiplatform.v1beta1.EndpointService.ListEndpoints].
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
            ~.pagers.ListEndpointsPager:
                Response message for
                [EndpointService.ListEndpoints][google.cloud.aiplatform.v1beta1.EndpointService.ListEndpoints].

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

        request = endpoint_service.ListEndpointsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.

        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method.wrap_method(
            self._transport.list_endpoints,
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
        response = pagers.ListEndpointsPager(
            method=rpc, request=request, response=response,
        )

        # Done; return the response.
        return response

    def update_endpoint(
        self,
        request: endpoint_service.UpdateEndpointRequest = None,
        *,
        endpoint: gca_endpoint.Endpoint = None,
        update_mask: field_mask.FieldMask = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_endpoint.Endpoint:
        r"""Updates an Endpoint.

        Args:
            request (:class:`~.endpoint_service.UpdateEndpointRequest`):
                The request object. Request message for
                [EndpointService.UpdateEndpoint][google.cloud.aiplatform.v1beta1.EndpointService.UpdateEndpoint].
            endpoint (:class:`~.gca_endpoint.Endpoint`):
                Required. The Endpoint which replaces
                the resource on the server.
                This corresponds to the ``endpoint`` field
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
            ~.gca_endpoint.Endpoint:
                Models are deployed into it, and
                afterwards Endpoint is called to obtain
                predictions and explanations.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        if request is not None and any([endpoint, update_mask]):
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
        rpc = gapic_v1.method.wrap_method(
            self._transport.update_endpoint,
            default_timeout=None,
            client_info=_client_info,
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    def delete_endpoint(
        self,
        request: endpoint_service.DeleteEndpointRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> ga_operation.Operation:
        r"""Deletes an Endpoint.

        Args:
            request (:class:`~.endpoint_service.DeleteEndpointRequest`):
                The request object. Request message for
                [EndpointService.DeleteEndpoint][google.cloud.aiplatform.v1beta1.EndpointService.DeleteEndpoint].
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

        request = endpoint_service.DeleteEndpointRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.

        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method.wrap_method(
            self._transport.delete_endpoint,
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

    def deploy_model(
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
    ) -> ga_operation.Operation:
        r"""Deploys a Model into this Endpoint, creating a
        DeployedModel within it.

        Args:
            request (:class:`~.endpoint_service.DeployModelRequest`):
                The request object. Request message for
                [EndpointService.DeployModel][google.cloud.aiplatform.v1beta1.EndpointService.DeployModel].
            endpoint (:class:`str`):
                Required. The name of the Endpoint resource into which
                to deploy a Model. Format:
                ``projects/{project}/locations/{location}/endpoints/{endpoint}``
                This corresponds to the ``endpoint`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            deployed_model (:class:`~.gca_endpoint.DeployedModel`):
                Required. The DeployedModel to be created within the
                Endpoint. Note that
                [Endpoint.traffic_split][google.cloud.aiplatform.v1beta1.Endpoint.traffic_split]
                must be updated for the DeployedModel to start receiving
                traffic, either as part of this call, or via
                [EndpointService.UpdateEndpoint][google.cloud.aiplatform.v1beta1.EndpointService.UpdateEndpoint].
                This corresponds to the ``deployed_model`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            traffic_split (:class:`Sequence[~.endpoint_service.DeployModelRequest.TrafficSplitEntry]`):
                A map from a DeployedModel's ID to the percentage of
                this Endpoint's traffic that should be forwarded to that
                DeployedModel.

                If this field is non-empty, then the Endpoint's
                [traffic_split][google.cloud.aiplatform.v1beta1.Endpoint.traffic_split]
                will be overwritten with it. To refer to the ID of the
                just being deployed Model, a "0" should be used, and the
                actual ID of the new DeployedModel will be filled in its
                place by this method. The traffic percentage values must
                add up to 100.

                If this field is empty, then the Endpoint's
                [traffic_split][google.cloud.aiplatform.v1beta1.Endpoint.traffic_split]
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
            ~.ga_operation.Operation:
                An object representing a long-running operation.

                The result type for the operation will be
                :class:``~.endpoint_service.DeployModelResponse``:
                Response message for
                [EndpointService.DeployModel][google.cloud.aiplatform.v1beta1.EndpointService.DeployModel].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        if request is not None and any([endpoint, deployed_model, traffic_split]):
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
        if traffic_split is not None:
            request.traffic_split = traffic_split

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method.wrap_method(
            self._transport.deploy_model,
            default_timeout=None,
            client_info=_client_info,
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = ga_operation.from_gapic(
            response,
            self._transport.operations_client,
            endpoint_service.DeployModelResponse,
            metadata_type=endpoint_service.DeployModelOperationMetadata,
        )

        # Done; return the response.
        return response

    def undeploy_model(
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
    ) -> ga_operation.Operation:
        r"""Undeploys a Model from an Endpoint, removing a
        DeployedModel from it, and freeing all resources it's
        using.

        Args:
            request (:class:`~.endpoint_service.UndeployModelRequest`):
                The request object. Request message for
                [EndpointService.UndeployModel][google.cloud.aiplatform.v1beta1.EndpointService.UndeployModel].
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
            traffic_split (:class:`Sequence[~.endpoint_service.UndeployModelRequest.TrafficSplitEntry]`):
                If this field is provided, then the Endpoint's
                [traffic_split][google.cloud.aiplatform.v1beta1.Endpoint.traffic_split]
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
            ~.ga_operation.Operation:
                An object representing a long-running operation.

                The result type for the operation will be
                :class:``~.endpoint_service.UndeployModelResponse``:
                Response message for
                [EndpointService.UndeployModel][google.cloud.aiplatform.v1beta1.EndpointService.UndeployModel].

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        if request is not None and any([endpoint, deployed_model_id, traffic_split]):
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
        if traffic_split is not None:
            request.traffic_split = traffic_split

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method.wrap_method(
            self._transport.undeploy_model,
            default_timeout=None,
            client_info=_client_info,
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = ga_operation.from_gapic(
            response,
            self._transport.operations_client,
            endpoint_service.UndeployModelResponse,
            metadata_type=endpoint_service.UndeployModelOperationMetadata,
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


__all__ = ("EndpointServiceClient",)
