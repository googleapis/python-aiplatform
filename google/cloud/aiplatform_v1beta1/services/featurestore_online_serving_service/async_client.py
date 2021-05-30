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

from google.cloud.aiplatform_v1beta1.types import featurestore_online_service
from .transports.base import (
    FeaturestoreOnlineServingServiceTransport,
    DEFAULT_CLIENT_INFO,
)
from .transports.grpc_asyncio import (
    FeaturestoreOnlineServingServiceGrpcAsyncIOTransport,
)
from .client import FeaturestoreOnlineServingServiceClient


class FeaturestoreOnlineServingServiceAsyncClient:
    """A service for serving online feature values."""

    _client: FeaturestoreOnlineServingServiceClient

    DEFAULT_ENDPOINT = FeaturestoreOnlineServingServiceClient.DEFAULT_ENDPOINT
    DEFAULT_MTLS_ENDPOINT = FeaturestoreOnlineServingServiceClient.DEFAULT_MTLS_ENDPOINT

    entity_type_path = staticmethod(
        FeaturestoreOnlineServingServiceClient.entity_type_path
    )
    parse_entity_type_path = staticmethod(
        FeaturestoreOnlineServingServiceClient.parse_entity_type_path
    )
    common_billing_account_path = staticmethod(
        FeaturestoreOnlineServingServiceClient.common_billing_account_path
    )
    parse_common_billing_account_path = staticmethod(
        FeaturestoreOnlineServingServiceClient.parse_common_billing_account_path
    )
    common_folder_path = staticmethod(
        FeaturestoreOnlineServingServiceClient.common_folder_path
    )
    parse_common_folder_path = staticmethod(
        FeaturestoreOnlineServingServiceClient.parse_common_folder_path
    )
    common_organization_path = staticmethod(
        FeaturestoreOnlineServingServiceClient.common_organization_path
    )
    parse_common_organization_path = staticmethod(
        FeaturestoreOnlineServingServiceClient.parse_common_organization_path
    )
    common_project_path = staticmethod(
        FeaturestoreOnlineServingServiceClient.common_project_path
    )
    parse_common_project_path = staticmethod(
        FeaturestoreOnlineServingServiceClient.parse_common_project_path
    )
    common_location_path = staticmethod(
        FeaturestoreOnlineServingServiceClient.common_location_path
    )
    parse_common_location_path = staticmethod(
        FeaturestoreOnlineServingServiceClient.parse_common_location_path
    )

    @classmethod
    def from_service_account_info(cls, info: dict, *args, **kwargs):
        """Creates an instance of this client using the provided credentials info.

        Args:
            info (dict): The service account private key info.
            args: Additional arguments to pass to the constructor.
            kwargs: Additional arguments to pass to the constructor.

        Returns:
            FeaturestoreOnlineServingServiceAsyncClient: The constructed client.
        """
        return FeaturestoreOnlineServingServiceClient.from_service_account_info.__func__(FeaturestoreOnlineServingServiceAsyncClient, info, *args, **kwargs)  # type: ignore

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
            FeaturestoreOnlineServingServiceAsyncClient: The constructed client.
        """
        return FeaturestoreOnlineServingServiceClient.from_service_account_file.__func__(FeaturestoreOnlineServingServiceAsyncClient, filename, *args, **kwargs)  # type: ignore

    from_service_account_json = from_service_account_file

    @property
    def transport(self) -> FeaturestoreOnlineServingServiceTransport:
        """Return the transport used by the client instance.

        Returns:
            FeaturestoreOnlineServingServiceTransport: The transport used by the client instance.
        """
        return self._client.transport

    get_transport_class = functools.partial(
        type(FeaturestoreOnlineServingServiceClient).get_transport_class,
        type(FeaturestoreOnlineServingServiceClient),
    )

    def __init__(
        self,
        *,
        credentials: ga_credentials.Credentials = None,
        transport: Union[
            str, FeaturestoreOnlineServingServiceTransport
        ] = "grpc_asyncio",
        client_options: ClientOptions = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
    ) -> None:
        """Instantiate the featurestore online serving service client.

        Args:
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            transport (Union[str, ~.FeaturestoreOnlineServingServiceTransport]): The
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
        self._client = FeaturestoreOnlineServingServiceClient(
            credentials=credentials,
            transport=transport,
            client_options=client_options,
            client_info=client_info,
        )

    async def read_feature_values(
        self,
        request: featurestore_online_service.ReadFeatureValuesRequest = None,
        *,
        entity_type: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> featurestore_online_service.ReadFeatureValuesResponse:
        r"""Reads Feature values of a specific entity of an
        EntityType. For reading feature values of multiple
        entities of an EntityType, please use
        StreamingReadFeatureValues.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.ReadFeatureValuesRequest`):
                The request object. Request message for
                [FeaturestoreOnlineServingService.ReadFeatureValues][google.cloud.aiplatform.v1beta1.FeaturestoreOnlineServingService.ReadFeatureValues].
            entity_type (:class:`str`):
                Required. The resource name of the EntityType for the
                entity being read. Value format:
                ``projects/{project}/locations/{location}/featurestores/ {featurestore}/entityTypes/{entityType}``.
                For example, for a machine learning model predicting
                user clicks on a website, an EntityType ID could be
                "user".

                This corresponds to the ``entity_type`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.ReadFeatureValuesResponse:
                Response message for
                [FeaturestoreOnlineServingService.ReadFeatureValues][google.cloud.aiplatform.v1beta1.FeaturestoreOnlineServingService.ReadFeatureValues].

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

        request = featurestore_online_service.ReadFeatureValuesRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if entity_type is not None:
            request.entity_type = entity_type

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.read_feature_values,
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

        # Done; return the response.
        return response

    def streaming_read_feature_values(
        self,
        request: featurestore_online_service.StreamingReadFeatureValuesRequest = None,
        *,
        entity_type: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> Awaitable[
        AsyncIterable[featurestore_online_service.ReadFeatureValuesResponse]
    ]:
        r"""Reads Feature values for multiple entities. Depending
        on their size, data for different entities may be broken
        up across multiple responses.

        Args:
            request (:class:`google.cloud.aiplatform_v1beta1.types.StreamingReadFeatureValuesRequest`):
                The request object. Request message for
                [FeaturestoreOnlineServingService.StreamingFeatureValuesRead][].
            entity_type (:class:`str`):
                Required. The resource name of the entities' type. Value
                format:
                ``projects/{project}/locations/{location}/featurestores/ {featurestore}/entityTypes/{entityType}``.
                For example, for a machine learning model predicting
                user clicks on a website, an EntityType ID could be
                "user".

                This corresponds to the ``entity_type`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            AsyncIterable[google.cloud.aiplatform_v1beta1.types.ReadFeatureValuesResponse]:
                Response message for
                [FeaturestoreOnlineServingService.ReadFeatureValues][google.cloud.aiplatform.v1beta1.FeaturestoreOnlineServingService.ReadFeatureValues].

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

        request = featurestore_online_service.StreamingReadFeatureValuesRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if entity_type is not None:
            request.entity_type = entity_type

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.streaming_read_feature_values,
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
        response = rpc(request, retry=retry, timeout=timeout, metadata=metadata,)

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


__all__ = ("FeaturestoreOnlineServingServiceAsyncClient",)
