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
from distutils import util
import os
import re
from typing import Callable, Dict, Optional, Sequence, Tuple, Type, Union
import pkg_resources

from google.api_core import client_options as client_options_lib  # type: ignore
from google.api_core import exceptions as core_exceptions  # type: ignore
from google.api_core import gapic_v1  # type: ignore
from google.api_core import retry as retries  # type: ignore
from google.auth import credentials as ga_credentials  # type: ignore
from google.auth.transport import mtls  # type: ignore
from google.auth.transport.grpc import SslCredentials  # type: ignore
from google.auth.exceptions import MutualTLSChannelError  # type: ignore
from google.oauth2 import service_account  # type: ignore

from google.api_core import operation as gac_operation  # type: ignore
from google.api_core import operation_async  # type: ignore
from google.cloud.aiplatform_v1beta1.services.endpoint_service import pagers
from google.cloud.aiplatform_v1beta1.types import encryption_spec
from google.cloud.aiplatform_v1beta1.types import endpoint
from google.cloud.aiplatform_v1beta1.types import endpoint as gca_endpoint
from google.cloud.aiplatform_v1beta1.types import endpoint_service
from google.cloud.aiplatform_v1beta1.types import operation as gca_operation
from google.protobuf import empty_pb2  # type: ignore
from google.protobuf import field_mask_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
from .transports.base import EndpointServiceTransport, DEFAULT_CLIENT_INFO
from .transports.grpc import EndpointServiceGrpcTransport
from .transports.grpc_asyncio import EndpointServiceGrpcAsyncIOTransport


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
    _transport_registry["grpc_asyncio"] = EndpointServiceGrpcAsyncIOTransport

    def get_transport_class(cls, label: str = None,) -> Type[EndpointServiceTransport]:
        """Returns an appropriate transport class.

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

    @staticmethod
    def _get_default_mtls_endpoint(api_endpoint):
        """Converts api endpoint to mTLS endpoint.

        Convert "*.sandbox.googleapis.com" and "*.googleapis.com" to
        "*.mtls.sandbox.googleapis.com" and "*.mtls.googleapis.com" respectively.
        Args:
            api_endpoint (Optional[str]): the api endpoint to convert.
        Returns:
            str: converted mTLS api endpoint.
        """
        if not api_endpoint:
            return api_endpoint

        mtls_endpoint_re = re.compile(
            r"(?P<name>[^.]+)(?P<mtls>\.mtls)?(?P<sandbox>\.sandbox)?(?P<googledomain>\.googleapis\.com)?"
        )

        m = mtls_endpoint_re.match(api_endpoint)
        name, mtls, sandbox, googledomain = m.groups()
        if mtls or not googledomain:
            return api_endpoint

        if sandbox:
            return api_endpoint.replace(
                "sandbox.googleapis.com", "mtls.sandbox.googleapis.com"
            )

        return api_endpoint.replace(".googleapis.com", ".mtls.googleapis.com")

    DEFAULT_ENDPOINT = "aiplatform.googleapis.com"
    DEFAULT_MTLS_ENDPOINT = _get_default_mtls_endpoint.__func__(  # type: ignore
        DEFAULT_ENDPOINT
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
            EndpointServiceClient: The constructed client.
        """
        credentials = service_account.Credentials.from_service_account_info(info)
        kwargs["credentials"] = credentials
        return cls(*args, **kwargs)

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
            EndpointServiceClient: The constructed client.
        """
        credentials = service_account.Credentials.from_service_account_file(filename)
        kwargs["credentials"] = credentials
        return cls(*args, **kwargs)

    from_service_account_json = from_service_account_file

    @property
    def transport(self) -> EndpointServiceTransport:
        """Returns the transport used by the client instance.

        Returns:
            EndpointServiceTransport: The transport used by the client
                instance.
        """
        return self._transport

    @staticmethod
    def endpoint_path(project: str, location: str, endpoint: str,) -> str:
        """Returns a fully-qualified endpoint string."""
        return "projects/{project}/locations/{location}/endpoints/{endpoint}".format(
            project=project, location=location, endpoint=endpoint,
        )

    @staticmethod
    def parse_endpoint_path(path: str) -> Dict[str, str]:
        """Parses a endpoint path into its component segments."""
        m = re.match(
            r"^projects/(?P<project>.+?)/locations/(?P<location>.+?)/endpoints/(?P<endpoint>.+?)$",
            path,
        )
        return m.groupdict() if m else {}

    @staticmethod
    def model_path(project: str, location: str, model: str,) -> str:
        """Returns a fully-qualified model string."""
        return "projects/{project}/locations/{location}/models/{model}".format(
            project=project, location=location, model=model,
        )

    @staticmethod
    def parse_model_path(path: str) -> Dict[str, str]:
        """Parses a model path into its component segments."""
        m = re.match(
            r"^projects/(?P<project>.+?)/locations/(?P<location>.+?)/models/(?P<model>.+?)$",
            path,
        )
        return m.groupdict() if m else {}

    @staticmethod
    def common_billing_account_path(billing_account: str,) -> str:
        """Returns a fully-qualified billing_account string."""
        return "billingAccounts/{billing_account}".format(
            billing_account=billing_account,
        )

    @staticmethod
    def parse_common_billing_account_path(path: str) -> Dict[str, str]:
        """Parse a billing_account path into its component segments."""
        m = re.match(r"^billingAccounts/(?P<billing_account>.+?)$", path)
        return m.groupdict() if m else {}

    @staticmethod
    def common_folder_path(folder: str,) -> str:
        """Returns a fully-qualified folder string."""
        return "folders/{folder}".format(folder=folder,)

    @staticmethod
    def parse_common_folder_path(path: str) -> Dict[str, str]:
        """Parse a folder path into its component segments."""
        m = re.match(r"^folders/(?P<folder>.+?)$", path)
        return m.groupdict() if m else {}

    @staticmethod
    def common_organization_path(organization: str,) -> str:
        """Returns a fully-qualified organization string."""
        return "organizations/{organization}".format(organization=organization,)

    @staticmethod
    def parse_common_organization_path(path: str) -> Dict[str, str]:
        """Parse a organization path into its component segments."""
        m = re.match(r"^organizations/(?P<organization>.+?)$", path)
        return m.groupdict() if m else {}

    @staticmethod
    def common_project_path(project: str,) -> str:
        """Returns a fully-qualified project string."""
        return "projects/{project}".format(project=project,)

    @staticmethod
    def parse_common_project_path(path: str) -> Dict[str, str]:
        """Parse a project path into its component segments."""
        m = re.match(r"^projects/(?P<project>.+?)$", path)
        return m.groupdict() if m else {}

    @staticmethod
    def common_location_path(project: str, location: str,) -> str:
        """Returns a fully-qualified location string."""
        return "projects/{project}/locations/{location}".format(
            project=project, location=location,
        )

    @staticmethod
    def parse_common_location_path(path: str) -> Dict[str, str]:
        """Parse a location path into its component segments."""
        m = re.match(r"^projects/(?P<project>.+?)/locations/(?P<location>.+?)$", path)
        return m.groupdict() if m else {}

    def __init__(
        self,
        *,
        credentials: Optional[ga_credentials.Credentials] = None,
        transport: Union[str, EndpointServiceTransport, None] = None,
        client_options: Optional[client_options_lib.ClientOptions] = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
    ) -> None:
        """Instantiates the endpoint service client.

        Args:
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            transport (Union[str, EndpointServiceTransport]): The
                transport to use. If set to None, a transport is chosen
                automatically.
            client_options (google.api_core.client_options.ClientOptions): Custom options for the
                client. It won't take effect if a ``transport`` instance is provided.
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
            client_info (google.api_core.gapic_v1.client_info.ClientInfo):
                The client info used to send a user-agent string along with
                API requests. If ``None``, then default info will be used.
                Generally, you only need to set this if you're developing
                your own client library.

        Raises:
            google.auth.exceptions.MutualTLSChannelError: If mutual TLS transport
                creation failed for any reason.
        """
        if isinstance(client_options, dict):
            client_options = client_options_lib.from_dict(client_options)
        if client_options is None:
            client_options = client_options_lib.ClientOptions()

        # Create SSL credentials for mutual TLS if needed.
        use_client_cert = bool(
            util.strtobool(os.getenv("GOOGLE_API_USE_CLIENT_CERTIFICATE", "false"))
        )

        client_cert_source_func = None
        is_mtls = False
        if use_client_cert:
            if client_options.client_cert_source:
                is_mtls = True
                client_cert_source_func = client_options.client_cert_source
            else:
                is_mtls = mtls.has_default_client_cert_source()
                if is_mtls:
                    client_cert_source_func = mtls.default_client_cert_source()
                else:
                    client_cert_source_func = None

        # Figure out which api endpoint to use.
        if client_options.api_endpoint is not None:
            api_endpoint = client_options.api_endpoint
        else:
            use_mtls_env = os.getenv("GOOGLE_API_USE_MTLS_ENDPOINT", "auto")
            if use_mtls_env == "never":
                api_endpoint = self.DEFAULT_ENDPOINT
            elif use_mtls_env == "always":
                api_endpoint = self.DEFAULT_MTLS_ENDPOINT
            elif use_mtls_env == "auto":
                if is_mtls:
                    api_endpoint = self.DEFAULT_MTLS_ENDPOINT
                else:
                    api_endpoint = self.DEFAULT_ENDPOINT
            else:
                raise MutualTLSChannelError(
                    "Unsupported GOOGLE_API_USE_MTLS_ENDPOINT value. Accepted "
                    "values: never, auto, always"
                )

        # Save or instantiate the transport.
        # Ordinarily, we provide the transport, but allowing a custom transport
        # instance provides an extensibility point for unusual situations.
        if isinstance(transport, EndpointServiceTransport):
            # transport is a EndpointServiceTransport instance.
            if credentials or client_options.credentials_file:
                raise ValueError(
                    "When providing a transport instance, "
                    "provide its credentials directly."
                )
            if client_options.scopes:
                raise ValueError(
                    "When providing a transport instance, provide its scopes "
                    "directly."
                )
            self._transport = transport
        else:
            Transport = type(self).get_transport_class(transport)
            self._transport = Transport(
                credentials=credentials,
                credentials_file=client_options.credentials_file,
                host=api_endpoint,
                scopes=client_options.scopes,
                client_cert_source_for_mtls=client_cert_source_func,
                quota_project_id=client_options.quota_project_id,
                client_info=client_info,
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
    ) -> gac_operation.Operation:
        r"""Creates an Endpoint.

        Args:
            request (google.cloud.aiplatform_v1beta1.types.CreateEndpointRequest):
                The request object. Request message for
                [EndpointService.CreateEndpoint][google.cloud.aiplatform.v1beta1.EndpointService.CreateEndpoint].
            parent (str):
                Required. The resource name of the Location to create
                the Endpoint in. Format:
                ``projects/{project}/locations/{location}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            endpoint (google.cloud.aiplatform_v1beta1.types.Endpoint):
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
            google.api_core.operation.Operation:
                An object representing a long-running operation.

                The result type for the operation will be :class:`google.cloud.aiplatform_v1beta1.types.Endpoint` Models are deployed into it, and afterwards Endpoint is called to obtain
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

        # Minor optimization to avoid making a copy if the user passes
        # in a endpoint_service.CreateEndpointRequest.
        # There's no risk of modifying the input as we've already verified
        # there are no flattened fields.
        if not isinstance(request, endpoint_service.CreateEndpointRequest):
            request = endpoint_service.CreateEndpointRequest(request)
            # If we have keyword arguments corresponding to fields on the
            # request, apply these.
            if parent is not None:
                request.parent = parent
            if endpoint is not None:
                request.endpoint = endpoint

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = self._transport._wrapped_methods[self._transport.create_endpoint]

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", request.parent),)),
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = gac_operation.from_gapic(
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
            request (google.cloud.aiplatform_v1beta1.types.GetEndpointRequest):
                The request object. Request message for
                [EndpointService.GetEndpoint][google.cloud.aiplatform.v1beta1.EndpointService.GetEndpoint]
            name (str):
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
            google.cloud.aiplatform_v1beta1.types.Endpoint:
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

        # Minor optimization to avoid making a copy if the user passes
        # in a endpoint_service.GetEndpointRequest.
        # There's no risk of modifying the input as we've already verified
        # there are no flattened fields.
        if not isinstance(request, endpoint_service.GetEndpointRequest):
            request = endpoint_service.GetEndpointRequest(request)
            # If we have keyword arguments corresponding to fields on the
            # request, apply these.
            if name is not None:
                request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = self._transport._wrapped_methods[self._transport.get_endpoint]

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
            request (google.cloud.aiplatform_v1beta1.types.ListEndpointsRequest):
                The request object. Request message for
                [EndpointService.ListEndpoints][google.cloud.aiplatform.v1beta1.EndpointService.ListEndpoints].
            parent (str):
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
            google.cloud.aiplatform_v1beta1.services.endpoint_service.pagers.ListEndpointsPager:
                Response message for
                [EndpointService.ListEndpoints][google.cloud.aiplatform.v1beta1.EndpointService.ListEndpoints].

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

        # Minor optimization to avoid making a copy if the user passes
        # in a endpoint_service.ListEndpointsRequest.
        # There's no risk of modifying the input as we've already verified
        # there are no flattened fields.
        if not isinstance(request, endpoint_service.ListEndpointsRequest):
            request = endpoint_service.ListEndpointsRequest(request)
            # If we have keyword arguments corresponding to fields on the
            # request, apply these.
            if parent is not None:
                request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = self._transport._wrapped_methods[self._transport.list_endpoints]

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
            method=rpc, request=request, response=response, metadata=metadata,
        )

        # Done; return the response.
        return response

    def update_endpoint(
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
            request (google.cloud.aiplatform_v1beta1.types.UpdateEndpointRequest):
                The request object. Request message for
                [EndpointService.UpdateEndpoint][google.cloud.aiplatform.v1beta1.EndpointService.UpdateEndpoint].
            endpoint (google.cloud.aiplatform_v1beta1.types.Endpoint):
                Required. The Endpoint which replaces
                the resource on the server.

                This corresponds to the ``endpoint`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            update_mask (google.protobuf.field_mask_pb2.FieldMask):
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
            google.cloud.aiplatform_v1beta1.types.Endpoint:
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

        # Minor optimization to avoid making a copy if the user passes
        # in a endpoint_service.UpdateEndpointRequest.
        # There's no risk of modifying the input as we've already verified
        # there are no flattened fields.
        if not isinstance(request, endpoint_service.UpdateEndpointRequest):
            request = endpoint_service.UpdateEndpointRequest(request)
            # If we have keyword arguments corresponding to fields on the
            # request, apply these.
            if endpoint is not None:
                request.endpoint = endpoint
            if update_mask is not None:
                request.update_mask = update_mask

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = self._transport._wrapped_methods[self._transport.update_endpoint]

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("endpoint.name", request.endpoint.name),)
            ),
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
    ) -> gac_operation.Operation:
        r"""Deletes an Endpoint.

        Args:
            request (google.cloud.aiplatform_v1beta1.types.DeleteEndpointRequest):
                The request object. Request message for
                [EndpointService.DeleteEndpoint][google.cloud.aiplatform.v1beta1.EndpointService.DeleteEndpoint].
            name (str):
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
            google.api_core.operation.Operation:
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

        # Minor optimization to avoid making a copy if the user passes
        # in a endpoint_service.DeleteEndpointRequest.
        # There's no risk of modifying the input as we've already verified
        # there are no flattened fields.
        if not isinstance(request, endpoint_service.DeleteEndpointRequest):
            request = endpoint_service.DeleteEndpointRequest(request)
            # If we have keyword arguments corresponding to fields on the
            # request, apply these.
            if name is not None:
                request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = self._transport._wrapped_methods[self._transport.delete_endpoint]

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("name", request.name),)),
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = gac_operation.from_gapic(
            response,
            self._transport.operations_client,
            empty_pb2.Empty,
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
    ) -> gac_operation.Operation:
        r"""Deploys a Model into this Endpoint, creating a
        DeployedModel within it.

        Args:
            request (google.cloud.aiplatform_v1beta1.types.DeployModelRequest):
                The request object. Request message for
                [EndpointService.DeployModel][google.cloud.aiplatform.v1beta1.EndpointService.DeployModel].
            endpoint (str):
                Required. The name of the Endpoint resource into which
                to deploy a Model. Format:
                ``projects/{project}/locations/{location}/endpoints/{endpoint}``

                This corresponds to the ``endpoint`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            deployed_model (google.cloud.aiplatform_v1beta1.types.DeployedModel):
                Required. The DeployedModel to be created within the
                Endpoint. Note that
                [Endpoint.traffic_split][google.cloud.aiplatform.v1beta1.Endpoint.traffic_split]
                must be updated for the DeployedModel to start receiving
                traffic, either as part of this call, or via
                [EndpointService.UpdateEndpoint][google.cloud.aiplatform.v1beta1.EndpointService.UpdateEndpoint].

                This corresponds to the ``deployed_model`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            traffic_split (Sequence[google.cloud.aiplatform_v1beta1.types.DeployModelRequest.TrafficSplitEntry]):
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
            google.api_core.operation.Operation:
                An object representing a long-running operation.

                The result type for the operation will be
                :class:`google.cloud.aiplatform_v1beta1.types.DeployModelResponse`
                Response message for
                [EndpointService.DeployModel][google.cloud.aiplatform.v1beta1.EndpointService.DeployModel].

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

        # Minor optimization to avoid making a copy if the user passes
        # in a endpoint_service.DeployModelRequest.
        # There's no risk of modifying the input as we've already verified
        # there are no flattened fields.
        if not isinstance(request, endpoint_service.DeployModelRequest):
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
        rpc = self._transport._wrapped_methods[self._transport.deploy_model]

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("endpoint", request.endpoint),)),
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = gac_operation.from_gapic(
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
    ) -> gac_operation.Operation:
        r"""Undeploys a Model from an Endpoint, removing a
        DeployedModel from it, and freeing all resources it's
        using.

        Args:
            request (google.cloud.aiplatform_v1beta1.types.UndeployModelRequest):
                The request object. Request message for
                [EndpointService.UndeployModel][google.cloud.aiplatform.v1beta1.EndpointService.UndeployModel].
            endpoint (str):
                Required. The name of the Endpoint resource from which
                to undeploy a Model. Format:
                ``projects/{project}/locations/{location}/endpoints/{endpoint}``

                This corresponds to the ``endpoint`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            deployed_model_id (str):
                Required. The ID of the DeployedModel
                to be undeployed from the Endpoint.

                This corresponds to the ``deployed_model_id`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            traffic_split (Sequence[google.cloud.aiplatform_v1beta1.types.UndeployModelRequest.TrafficSplitEntry]):
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
            google.api_core.operation.Operation:
                An object representing a long-running operation.

                The result type for the operation will be
                :class:`google.cloud.aiplatform_v1beta1.types.UndeployModelResponse`
                Response message for
                [EndpointService.UndeployModel][google.cloud.aiplatform.v1beta1.EndpointService.UndeployModel].

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

        # Minor optimization to avoid making a copy if the user passes
        # in a endpoint_service.UndeployModelRequest.
        # There's no risk of modifying the input as we've already verified
        # there are no flattened fields.
        if not isinstance(request, endpoint_service.UndeployModelRequest):
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
        rpc = self._transport._wrapped_methods[self._transport.undeploy_model]

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("endpoint", request.endpoint),)),
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = gac_operation.from_gapic(
            response,
            self._transport.operations_client,
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


__all__ = ("EndpointServiceClient",)
