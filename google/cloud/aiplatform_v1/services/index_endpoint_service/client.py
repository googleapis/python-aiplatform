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
from typing import Dict, Optional, Sequence, Tuple, Type, Union
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
from google.cloud.aiplatform_v1.services.index_endpoint_service import pagers
from google.cloud.aiplatform_v1.types import index_endpoint
from google.cloud.aiplatform_v1.types import index_endpoint as gca_index_endpoint
from google.cloud.aiplatform_v1.types import index_endpoint_service
from google.cloud.aiplatform_v1.types import operation as gca_operation
from google.protobuf import empty_pb2  # type: ignore
from google.protobuf import field_mask_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
from .transports.base import IndexEndpointServiceTransport, DEFAULT_CLIENT_INFO
from .transports.grpc import IndexEndpointServiceGrpcTransport
from .transports.grpc_asyncio import IndexEndpointServiceGrpcAsyncIOTransport


class IndexEndpointServiceClientMeta(type):
    """Metaclass for the IndexEndpointService client.

    This provides class-level methods for building and retrieving
    support objects (e.g. transport) without polluting the client instance
    objects.
    """

    _transport_registry = (
        OrderedDict()
    )  # type: Dict[str, Type[IndexEndpointServiceTransport]]
    _transport_registry["grpc"] = IndexEndpointServiceGrpcTransport
    _transport_registry["grpc_asyncio"] = IndexEndpointServiceGrpcAsyncIOTransport

    def get_transport_class(
        cls, label: str = None,
    ) -> Type[IndexEndpointServiceTransport]:
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


class IndexEndpointServiceClient(metaclass=IndexEndpointServiceClientMeta):
    """A service for managing Vertex AI's IndexEndpoints."""

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
            IndexEndpointServiceClient: The constructed client.
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
            IndexEndpointServiceClient: The constructed client.
        """
        credentials = service_account.Credentials.from_service_account_file(filename)
        kwargs["credentials"] = credentials
        return cls(*args, **kwargs)

    from_service_account_json = from_service_account_file

    @property
    def transport(self) -> IndexEndpointServiceTransport:
        """Returns the transport used by the client instance.

        Returns:
            IndexEndpointServiceTransport: The transport used by the client
                instance.
        """
        return self._transport

    @staticmethod
    def index_path(project: str, location: str, index: str,) -> str:
        """Returns a fully-qualified index string."""
        return "projects/{project}/locations/{location}/indexes/{index}".format(
            project=project, location=location, index=index,
        )

    @staticmethod
    def parse_index_path(path: str) -> Dict[str, str]:
        """Parses a index path into its component segments."""
        m = re.match(
            r"^projects/(?P<project>.+?)/locations/(?P<location>.+?)/indexes/(?P<index>.+?)$",
            path,
        )
        return m.groupdict() if m else {}

    @staticmethod
    def index_endpoint_path(project: str, location: str, index_endpoint: str,) -> str:
        """Returns a fully-qualified index_endpoint string."""
        return "projects/{project}/locations/{location}/indexEndpoints/{index_endpoint}".format(
            project=project, location=location, index_endpoint=index_endpoint,
        )

    @staticmethod
    def parse_index_endpoint_path(path: str) -> Dict[str, str]:
        """Parses a index_endpoint path into its component segments."""
        m = re.match(
            r"^projects/(?P<project>.+?)/locations/(?P<location>.+?)/indexEndpoints/(?P<index_endpoint>.+?)$",
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
        transport: Union[str, IndexEndpointServiceTransport, None] = None,
        client_options: Optional[client_options_lib.ClientOptions] = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
    ) -> None:
        """Instantiates the index endpoint service client.

        Args:
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            transport (Union[str, IndexEndpointServiceTransport]): The
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
        if isinstance(transport, IndexEndpointServiceTransport):
            # transport is a IndexEndpointServiceTransport instance.
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
                always_use_jwt_access=(
                    Transport == type(self).get_transport_class("grpc")
                    or Transport == type(self).get_transport_class("grpc_asyncio")
                ),
            )

    def create_index_endpoint(
        self,
        request: Union[index_endpoint_service.CreateIndexEndpointRequest, dict] = None,
        *,
        parent: str = None,
        index_endpoint: gca_index_endpoint.IndexEndpoint = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gac_operation.Operation:
        r"""Creates an IndexEndpoint.

        Args:
            request (Union[google.cloud.aiplatform_v1.types.CreateIndexEndpointRequest, dict]):
                The request object. Request message for
                [IndexEndpointService.CreateIndexEndpoint][google.cloud.aiplatform.v1.IndexEndpointService.CreateIndexEndpoint].
            parent (str):
                Required. The resource name of the Location to create
                the IndexEndpoint in. Format:
                ``projects/{project}/locations/{location}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            index_endpoint (google.cloud.aiplatform_v1.types.IndexEndpoint):
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
            google.api_core.operation.Operation:
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

        # Minor optimization to avoid making a copy if the user passes
        # in a index_endpoint_service.CreateIndexEndpointRequest.
        # There's no risk of modifying the input as we've already verified
        # there are no flattened fields.
        if not isinstance(request, index_endpoint_service.CreateIndexEndpointRequest):
            request = index_endpoint_service.CreateIndexEndpointRequest(request)
            # If we have keyword arguments corresponding to fields on the
            # request, apply these.
            if parent is not None:
                request.parent = parent
            if index_endpoint is not None:
                request.index_endpoint = index_endpoint

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = self._transport._wrapped_methods[self._transport.create_index_endpoint]

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
            gca_index_endpoint.IndexEndpoint,
            metadata_type=index_endpoint_service.CreateIndexEndpointOperationMetadata,
        )

        # Done; return the response.
        return response

    def get_index_endpoint(
        self,
        request: Union[index_endpoint_service.GetIndexEndpointRequest, dict] = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> index_endpoint.IndexEndpoint:
        r"""Gets an IndexEndpoint.

        Args:
            request (Union[google.cloud.aiplatform_v1.types.GetIndexEndpointRequest, dict]):
                The request object. Request message for
                [IndexEndpointService.GetIndexEndpoint][google.cloud.aiplatform.v1.IndexEndpointService.GetIndexEndpoint]
            name (str):
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

        # Minor optimization to avoid making a copy if the user passes
        # in a index_endpoint_service.GetIndexEndpointRequest.
        # There's no risk of modifying the input as we've already verified
        # there are no flattened fields.
        if not isinstance(request, index_endpoint_service.GetIndexEndpointRequest):
            request = index_endpoint_service.GetIndexEndpointRequest(request)
            # If we have keyword arguments corresponding to fields on the
            # request, apply these.
            if name is not None:
                request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = self._transport._wrapped_methods[self._transport.get_index_endpoint]

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("name", request.name),)),
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    def list_index_endpoints(
        self,
        request: Union[index_endpoint_service.ListIndexEndpointsRequest, dict] = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListIndexEndpointsPager:
        r"""Lists IndexEndpoints in a Location.

        Args:
            request (Union[google.cloud.aiplatform_v1.types.ListIndexEndpointsRequest, dict]):
                The request object. Request message for
                [IndexEndpointService.ListIndexEndpoints][google.cloud.aiplatform.v1.IndexEndpointService.ListIndexEndpoints].
            parent (str):
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
            google.cloud.aiplatform_v1.services.index_endpoint_service.pagers.ListIndexEndpointsPager:
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

        # Minor optimization to avoid making a copy if the user passes
        # in a index_endpoint_service.ListIndexEndpointsRequest.
        # There's no risk of modifying the input as we've already verified
        # there are no flattened fields.
        if not isinstance(request, index_endpoint_service.ListIndexEndpointsRequest):
            request = index_endpoint_service.ListIndexEndpointsRequest(request)
            # If we have keyword arguments corresponding to fields on the
            # request, apply these.
            if parent is not None:
                request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = self._transport._wrapped_methods[self._transport.list_index_endpoints]

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", request.parent),)),
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # This method is paged; wrap the response in a pager, which provides
        # an `__iter__` convenience method.
        response = pagers.ListIndexEndpointsPager(
            method=rpc, request=request, response=response, metadata=metadata,
        )

        # Done; return the response.
        return response

    def update_index_endpoint(
        self,
        request: Union[index_endpoint_service.UpdateIndexEndpointRequest, dict] = None,
        *,
        index_endpoint: gca_index_endpoint.IndexEndpoint = None,
        update_mask: field_mask_pb2.FieldMask = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_index_endpoint.IndexEndpoint:
        r"""Updates an IndexEndpoint.

        Args:
            request (Union[google.cloud.aiplatform_v1.types.UpdateIndexEndpointRequest, dict]):
                The request object. Request message for
                [IndexEndpointService.UpdateIndexEndpoint][google.cloud.aiplatform.v1.IndexEndpointService.UpdateIndexEndpoint].
            index_endpoint (google.cloud.aiplatform_v1.types.IndexEndpoint):
                Required. The IndexEndpoint which
                replaces the resource on the server.

                This corresponds to the ``index_endpoint`` field
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

        # Minor optimization to avoid making a copy if the user passes
        # in a index_endpoint_service.UpdateIndexEndpointRequest.
        # There's no risk of modifying the input as we've already verified
        # there are no flattened fields.
        if not isinstance(request, index_endpoint_service.UpdateIndexEndpointRequest):
            request = index_endpoint_service.UpdateIndexEndpointRequest(request)
            # If we have keyword arguments corresponding to fields on the
            # request, apply these.
            if index_endpoint is not None:
                request.index_endpoint = index_endpoint
            if update_mask is not None:
                request.update_mask = update_mask

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = self._transport._wrapped_methods[self._transport.update_index_endpoint]

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("index_endpoint.name", request.index_endpoint.name),)
            ),
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Done; return the response.
        return response

    def delete_index_endpoint(
        self,
        request: Union[index_endpoint_service.DeleteIndexEndpointRequest, dict] = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gac_operation.Operation:
        r"""Deletes an IndexEndpoint.

        Args:
            request (Union[google.cloud.aiplatform_v1.types.DeleteIndexEndpointRequest, dict]):
                The request object. Request message for
                [IndexEndpointService.DeleteIndexEndpoint][google.cloud.aiplatform.v1.IndexEndpointService.DeleteIndexEndpoint].
            name (str):
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
        # in a index_endpoint_service.DeleteIndexEndpointRequest.
        # There's no risk of modifying the input as we've already verified
        # there are no flattened fields.
        if not isinstance(request, index_endpoint_service.DeleteIndexEndpointRequest):
            request = index_endpoint_service.DeleteIndexEndpointRequest(request)
            # If we have keyword arguments corresponding to fields on the
            # request, apply these.
            if name is not None:
                request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = self._transport._wrapped_methods[self._transport.delete_index_endpoint]

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

    def deploy_index(
        self,
        request: Union[index_endpoint_service.DeployIndexRequest, dict] = None,
        *,
        index_endpoint: str = None,
        deployed_index: gca_index_endpoint.DeployedIndex = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gac_operation.Operation:
        r"""Deploys an Index into this IndexEndpoint, creating a
        DeployedIndex within it.
        Only non-empty Indexes can be deployed.

        Args:
            request (Union[google.cloud.aiplatform_v1.types.DeployIndexRequest, dict]):
                The request object. Request message for
                [IndexEndpointService.DeployIndex][google.cloud.aiplatform.v1.IndexEndpointService.DeployIndex].
            index_endpoint (str):
                Required. The name of the IndexEndpoint resource into
                which to deploy an Index. Format:
                ``projects/{project}/locations/{location}/indexEndpoints/{index_endpoint}``

                This corresponds to the ``index_endpoint`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            deployed_index (google.cloud.aiplatform_v1.types.DeployedIndex):
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
            google.api_core.operation.Operation:
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

        # Minor optimization to avoid making a copy if the user passes
        # in a index_endpoint_service.DeployIndexRequest.
        # There's no risk of modifying the input as we've already verified
        # there are no flattened fields.
        if not isinstance(request, index_endpoint_service.DeployIndexRequest):
            request = index_endpoint_service.DeployIndexRequest(request)
            # If we have keyword arguments corresponding to fields on the
            # request, apply these.
            if index_endpoint is not None:
                request.index_endpoint = index_endpoint
            if deployed_index is not None:
                request.deployed_index = deployed_index

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = self._transport._wrapped_methods[self._transport.deploy_index]

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("index_endpoint", request.index_endpoint),)
            ),
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = gac_operation.from_gapic(
            response,
            self._transport.operations_client,
            index_endpoint_service.DeployIndexResponse,
            metadata_type=index_endpoint_service.DeployIndexOperationMetadata,
        )

        # Done; return the response.
        return response

    def undeploy_index(
        self,
        request: Union[index_endpoint_service.UndeployIndexRequest, dict] = None,
        *,
        index_endpoint: str = None,
        deployed_index_id: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gac_operation.Operation:
        r"""Undeploys an Index from an IndexEndpoint, removing a
        DeployedIndex from it, and freeing all resources it's
        using.

        Args:
            request (Union[google.cloud.aiplatform_v1.types.UndeployIndexRequest, dict]):
                The request object. Request message for
                [IndexEndpointService.UndeployIndex][google.cloud.aiplatform.v1.IndexEndpointService.UndeployIndex].
            index_endpoint (str):
                Required. The name of the IndexEndpoint resource from
                which to undeploy an Index. Format:
                ``projects/{project}/locations/{location}/indexEndpoints/{index_endpoint}``

                This corresponds to the ``index_endpoint`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            deployed_index_id (str):
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
            google.api_core.operation.Operation:
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

        # Minor optimization to avoid making a copy if the user passes
        # in a index_endpoint_service.UndeployIndexRequest.
        # There's no risk of modifying the input as we've already verified
        # there are no flattened fields.
        if not isinstance(request, index_endpoint_service.UndeployIndexRequest):
            request = index_endpoint_service.UndeployIndexRequest(request)
            # If we have keyword arguments corresponding to fields on the
            # request, apply these.
            if index_endpoint is not None:
                request.index_endpoint = index_endpoint
            if deployed_index_id is not None:
                request.deployed_index_id = deployed_index_id

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = self._transport._wrapped_methods[self._transport.undeploy_index]

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("index_endpoint", request.index_endpoint),)
            ),
        )

        # Send the request.
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

        # Wrap the response in an operation future.
        response = gac_operation.from_gapic(
            response,
            self._transport.operations_client,
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


__all__ = ("IndexEndpointServiceClient",)
