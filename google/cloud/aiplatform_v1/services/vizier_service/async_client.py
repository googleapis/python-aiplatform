# -*- coding: utf-8 -*-
# Copyright 2022 Google LLC
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
from typing import Dict, Mapping, Optional, Sequence, Tuple, Type, Union
import pkg_resources

from google.api_core.client_options import ClientOptions
from google.api_core import exceptions as core_exceptions
from google.api_core import gapic_v1
from google.api_core import retry as retries
from google.auth import credentials as ga_credentials  # type: ignore
from google.oauth2 import service_account  # type: ignore

try:
    OptionalRetry = Union[retries.Retry, gapic_v1.method._MethodDefault]
except AttributeError:  # pragma: NO COVER
    OptionalRetry = Union[retries.Retry, object]  # type: ignore

from google.api_core import operation  # type: ignore
from google.api_core import operation_async  # type: ignore
from google.cloud.aiplatform_v1.services.vizier_service import pagers
from google.cloud.aiplatform_v1.types import study
from google.cloud.aiplatform_v1.types import study as gca_study
from google.cloud.aiplatform_v1.types import vizier_service
from google.protobuf import timestamp_pb2  # type: ignore
from .transports.base import VizierServiceTransport, DEFAULT_CLIENT_INFO
from .transports.grpc_asyncio import VizierServiceGrpcAsyncIOTransport
from .client import VizierServiceClient


class VizierServiceAsyncClient:
    """Vertex AI Vizier API.
    Vertex AI Vizier is a service to solve blackbox optimization
    problems, such as tuning machine learning hyperparameters and
    searching over deep learning architectures.
    """

    _client: VizierServiceClient

    DEFAULT_ENDPOINT = VizierServiceClient.DEFAULT_ENDPOINT
    DEFAULT_MTLS_ENDPOINT = VizierServiceClient.DEFAULT_MTLS_ENDPOINT

    custom_job_path = staticmethod(VizierServiceClient.custom_job_path)
    parse_custom_job_path = staticmethod(VizierServiceClient.parse_custom_job_path)
    study_path = staticmethod(VizierServiceClient.study_path)
    parse_study_path = staticmethod(VizierServiceClient.parse_study_path)
    trial_path = staticmethod(VizierServiceClient.trial_path)
    parse_trial_path = staticmethod(VizierServiceClient.parse_trial_path)
    common_billing_account_path = staticmethod(
        VizierServiceClient.common_billing_account_path
    )
    parse_common_billing_account_path = staticmethod(
        VizierServiceClient.parse_common_billing_account_path
    )
    common_folder_path = staticmethod(VizierServiceClient.common_folder_path)
    parse_common_folder_path = staticmethod(
        VizierServiceClient.parse_common_folder_path
    )
    common_organization_path = staticmethod(
        VizierServiceClient.common_organization_path
    )
    parse_common_organization_path = staticmethod(
        VizierServiceClient.parse_common_organization_path
    )
    common_project_path = staticmethod(VizierServiceClient.common_project_path)
    parse_common_project_path = staticmethod(
        VizierServiceClient.parse_common_project_path
    )
    common_location_path = staticmethod(VizierServiceClient.common_location_path)
    parse_common_location_path = staticmethod(
        VizierServiceClient.parse_common_location_path
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
            VizierServiceAsyncClient: The constructed client.
        """
        return VizierServiceClient.from_service_account_info.__func__(VizierServiceAsyncClient, info, *args, **kwargs)  # type: ignore

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
            VizierServiceAsyncClient: The constructed client.
        """
        return VizierServiceClient.from_service_account_file.__func__(VizierServiceAsyncClient, filename, *args, **kwargs)  # type: ignore

    from_service_account_json = from_service_account_file

    @classmethod
    def get_mtls_endpoint_and_cert_source(
        cls, client_options: Optional[ClientOptions] = None
    ):
        """Return the API endpoint and client cert source for mutual TLS.

        The client cert source is determined in the following order:
        (1) if `GOOGLE_API_USE_CLIENT_CERTIFICATE` environment variable is not "true", the
        client cert source is None.
        (2) if `client_options.client_cert_source` is provided, use the provided one; if the
        default client cert source exists, use the default one; otherwise the client cert
        source is None.

        The API endpoint is determined in the following order:
        (1) if `client_options.api_endpoint` if provided, use the provided one.
        (2) if `GOOGLE_API_USE_CLIENT_CERTIFICATE` environment variable is "always", use the
        default mTLS endpoint; if the environment variabel is "never", use the default API
        endpoint; otherwise if client cert source exists, use the default mTLS endpoint, otherwise
        use the default API endpoint.

        More details can be found at https://google.aip.dev/auth/4114.

        Args:
            client_options (google.api_core.client_options.ClientOptions): Custom options for the
                client. Only the `api_endpoint` and `client_cert_source` properties may be used
                in this method.

        Returns:
            Tuple[str, Callable[[], Tuple[bytes, bytes]]]: returns the API endpoint and the
                client cert source to use.

        Raises:
            google.auth.exceptions.MutualTLSChannelError: If any errors happen.
        """
        return VizierServiceClient.get_mtls_endpoint_and_cert_source(client_options)  # type: ignore

    @property
    def transport(self) -> VizierServiceTransport:
        """Returns the transport used by the client instance.

        Returns:
            VizierServiceTransport: The transport used by the client instance.
        """
        return self._client.transport

    get_transport_class = functools.partial(
        type(VizierServiceClient).get_transport_class, type(VizierServiceClient)
    )

    def __init__(
        self,
        *,
        credentials: ga_credentials.Credentials = None,
        transport: Union[str, VizierServiceTransport] = "grpc_asyncio",
        client_options: ClientOptions = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
    ) -> None:
        """Instantiates the vizier service client.

        Args:
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            transport (Union[str, ~.VizierServiceTransport]): The
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
        self._client = VizierServiceClient(
            credentials=credentials,
            transport=transport,
            client_options=client_options,
            client_info=client_info,
        )

    async def create_study(
        self,
        request: Union[vizier_service.CreateStudyRequest, dict] = None,
        *,
        parent: str = None,
        study: gca_study.Study = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_study.Study:
        r"""Creates a Study. A resource name will be generated
        after creation of the Study.

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_create_study():
                # Create a client
                client = aiplatform_v1.VizierServiceAsyncClient()

                # Initialize request argument(s)
                study = aiplatform_v1.Study()
                study.display_name = "display_name_value"
                study.study_spec.metrics.metric_id = "metric_id_value"
                study.study_spec.metrics.goal = "MINIMIZE"
                study.study_spec.parameters.double_value_spec.min_value = 0.96
                study.study_spec.parameters.double_value_spec.max_value = 0.962
                study.study_spec.parameters.parameter_id = "parameter_id_value"

                request = aiplatform_v1.CreateStudyRequest(
                    parent="parent_value",
                    study=study,
                )

                # Make the request
                response = await client.create_study(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.CreateStudyRequest, dict]):
                The request object. Request message for
                [VizierService.CreateStudy][google.cloud.aiplatform.v1.VizierService.CreateStudy].
            parent (:class:`str`):
                Required. The resource name of the Location to create
                the CustomJob in. Format:
                ``projects/{project}/locations/{location}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            study (:class:`google.cloud.aiplatform_v1.types.Study`):
                Required. The Study configuration
                used to create the Study.

                This corresponds to the ``study`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.types.Study:
                A message representing a Study.
        """
        # Create or coerce a protobuf request object.
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, study])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = vizier_service.CreateStudyRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if study is not None:
            request.study = study

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_study,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", request.parent),)),
        )

        # Send the request.
        response = await rpc(
            request,
            retry=retry,
            timeout=timeout,
            metadata=metadata,
        )

        # Done; return the response.
        return response

    async def get_study(
        self,
        request: Union[vizier_service.GetStudyRequest, dict] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> study.Study:
        r"""Gets a Study by name.

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_get_study():
                # Create a client
                client = aiplatform_v1.VizierServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.GetStudyRequest(
                    name="name_value",
                )

                # Make the request
                response = await client.get_study(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.GetStudyRequest, dict]):
                The request object. Request message for
                [VizierService.GetStudy][google.cloud.aiplatform.v1.VizierService.GetStudy].
            name (:class:`str`):
                Required. The name of the Study resource. Format:
                ``projects/{project}/locations/{location}/studies/{study}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.types.Study:
                A message representing a Study.
        """
        # Create or coerce a protobuf request object.
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([name])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = vizier_service.GetStudyRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_study,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("name", request.name),)),
        )

        # Send the request.
        response = await rpc(
            request,
            retry=retry,
            timeout=timeout,
            metadata=metadata,
        )

        # Done; return the response.
        return response

    async def list_studies(
        self,
        request: Union[vizier_service.ListStudiesRequest, dict] = None,
        *,
        parent: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListStudiesAsyncPager:
        r"""Lists all the studies in a region for an associated
        project.

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_list_studies():
                # Create a client
                client = aiplatform_v1.VizierServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.ListStudiesRequest(
                    parent="parent_value",
                )

                # Make the request
                page_result = client.list_studies(request=request)

                # Handle the response
                async for response in page_result:
                    print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.ListStudiesRequest, dict]):
                The request object. Request message for
                [VizierService.ListStudies][google.cloud.aiplatform.v1.VizierService.ListStudies].
            parent (:class:`str`):
                Required. The resource name of the Location to list the
                Study from. Format:
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
            google.cloud.aiplatform_v1.services.vizier_service.pagers.ListStudiesAsyncPager:
                Response message for
                [VizierService.ListStudies][google.cloud.aiplatform.v1.VizierService.ListStudies].

                Iterating over this object will yield results and
                resolve additional pages automatically.

        """
        # Create or coerce a protobuf request object.
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = vizier_service.ListStudiesRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_studies,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", request.parent),)),
        )

        # Send the request.
        response = await rpc(
            request,
            retry=retry,
            timeout=timeout,
            metadata=metadata,
        )

        # This method is paged; wrap the response in a pager, which provides
        # an `__aiter__` convenience method.
        response = pagers.ListStudiesAsyncPager(
            method=rpc,
            request=request,
            response=response,
            metadata=metadata,
        )

        # Done; return the response.
        return response

    async def delete_study(
        self,
        request: Union[vizier_service.DeleteStudyRequest, dict] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> None:
        r"""Deletes a Study.

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_delete_study():
                # Create a client
                client = aiplatform_v1.VizierServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.DeleteStudyRequest(
                    name="name_value",
                )

                # Make the request
                await client.delete_study(request=request)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.DeleteStudyRequest, dict]):
                The request object. Request message for
                [VizierService.DeleteStudy][google.cloud.aiplatform.v1.VizierService.DeleteStudy].
            name (:class:`str`):
                Required. The name of the Study resource to be deleted.
                Format:
                ``projects/{project}/locations/{location}/studies/{study}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        # Create or coerce a protobuf request object.
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([name])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = vizier_service.DeleteStudyRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.delete_study,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("name", request.name),)),
        )

        # Send the request.
        await rpc(
            request,
            retry=retry,
            timeout=timeout,
            metadata=metadata,
        )

    async def lookup_study(
        self,
        request: Union[vizier_service.LookupStudyRequest, dict] = None,
        *,
        parent: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> study.Study:
        r"""Looks a study up using the user-defined display_name field
        instead of the fully qualified resource name.

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_lookup_study():
                # Create a client
                client = aiplatform_v1.VizierServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.LookupStudyRequest(
                    parent="parent_value",
                    display_name="display_name_value",
                )

                # Make the request
                response = await client.lookup_study(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.LookupStudyRequest, dict]):
                The request object. Request message for
                [VizierService.LookupStudy][google.cloud.aiplatform.v1.VizierService.LookupStudy].
            parent (:class:`str`):
                Required. The resource name of the Location to get the
                Study from. Format:
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
            google.cloud.aiplatform_v1.types.Study:
                A message representing a Study.
        """
        # Create or coerce a protobuf request object.
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = vizier_service.LookupStudyRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.lookup_study,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", request.parent),)),
        )

        # Send the request.
        response = await rpc(
            request,
            retry=retry,
            timeout=timeout,
            metadata=metadata,
        )

        # Done; return the response.
        return response

    async def suggest_trials(
        self,
        request: Union[vizier_service.SuggestTrialsRequest, dict] = None,
        *,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Adds one or more Trials to a Study, with parameter values
        suggested by Vertex AI Vizier. Returns a long-running operation
        associated with the generation of Trial suggestions. When this
        long-running operation succeeds, it will contain a
        [SuggestTrialsResponse][google.cloud.ml.v1.SuggestTrialsResponse].

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_suggest_trials():
                # Create a client
                client = aiplatform_v1.VizierServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.SuggestTrialsRequest(
                    parent="parent_value",
                    suggestion_count=1744,
                    client_id="client_id_value",
                )

                # Make the request
                operation = client.suggest_trials(request=request)

                print("Waiting for operation to complete...")

                response = await operation.result()

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.SuggestTrialsRequest, dict]):
                The request object. Request message for
                [VizierService.SuggestTrials][google.cloud.aiplatform.v1.VizierService.SuggestTrials].
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.api_core.operation_async.AsyncOperation:
                An object representing a long-running operation.

                The result type for the operation will be
                :class:`google.cloud.aiplatform_v1.types.SuggestTrialsResponse`
                Response message for
                [VizierService.SuggestTrials][google.cloud.aiplatform.v1.VizierService.SuggestTrials].

        """
        # Create or coerce a protobuf request object.
        request = vizier_service.SuggestTrialsRequest(request)

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.suggest_trials,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", request.parent),)),
        )

        # Send the request.
        response = await rpc(
            request,
            retry=retry,
            timeout=timeout,
            metadata=metadata,
        )

        # Wrap the response in an operation future.
        response = operation_async.from_gapic(
            response,
            self._client._transport.operations_client,
            vizier_service.SuggestTrialsResponse,
            metadata_type=vizier_service.SuggestTrialsMetadata,
        )

        # Done; return the response.
        return response

    async def create_trial(
        self,
        request: Union[vizier_service.CreateTrialRequest, dict] = None,
        *,
        parent: str = None,
        trial: study.Trial = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> study.Trial:
        r"""Adds a user provided Trial to a Study.

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_create_trial():
                # Create a client
                client = aiplatform_v1.VizierServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.CreateTrialRequest(
                    parent="parent_value",
                )

                # Make the request
                response = await client.create_trial(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.CreateTrialRequest, dict]):
                The request object. Request message for
                [VizierService.CreateTrial][google.cloud.aiplatform.v1.VizierService.CreateTrial].
            parent (:class:`str`):
                Required. The resource name of the Study to create the
                Trial in. Format:
                ``projects/{project}/locations/{location}/studies/{study}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            trial (:class:`google.cloud.aiplatform_v1.types.Trial`):
                Required. The Trial to create.
                This corresponds to the ``trial`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.types.Trial:
                A message representing a Trial. A
                Trial contains a unique set of
                Parameters that has been or will be
                evaluated, along with the objective
                metrics got by running the Trial.

        """
        # Create or coerce a protobuf request object.
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, trial])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = vizier_service.CreateTrialRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if trial is not None:
            request.trial = trial

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_trial,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", request.parent),)),
        )

        # Send the request.
        response = await rpc(
            request,
            retry=retry,
            timeout=timeout,
            metadata=metadata,
        )

        # Done; return the response.
        return response

    async def get_trial(
        self,
        request: Union[vizier_service.GetTrialRequest, dict] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> study.Trial:
        r"""Gets a Trial.

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_get_trial():
                # Create a client
                client = aiplatform_v1.VizierServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.GetTrialRequest(
                    name="name_value",
                )

                # Make the request
                response = await client.get_trial(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.GetTrialRequest, dict]):
                The request object. Request message for
                [VizierService.GetTrial][google.cloud.aiplatform.v1.VizierService.GetTrial].
            name (:class:`str`):
                Required. The name of the Trial resource. Format:
                ``projects/{project}/locations/{location}/studies/{study}/trials/{trial}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.types.Trial:
                A message representing a Trial. A
                Trial contains a unique set of
                Parameters that has been or will be
                evaluated, along with the objective
                metrics got by running the Trial.

        """
        # Create or coerce a protobuf request object.
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([name])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = vizier_service.GetTrialRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_trial,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("name", request.name),)),
        )

        # Send the request.
        response = await rpc(
            request,
            retry=retry,
            timeout=timeout,
            metadata=metadata,
        )

        # Done; return the response.
        return response

    async def list_trials(
        self,
        request: Union[vizier_service.ListTrialsRequest, dict] = None,
        *,
        parent: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListTrialsAsyncPager:
        r"""Lists the Trials associated with a Study.

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_list_trials():
                # Create a client
                client = aiplatform_v1.VizierServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.ListTrialsRequest(
                    parent="parent_value",
                )

                # Make the request
                page_result = client.list_trials(request=request)

                # Handle the response
                async for response in page_result:
                    print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.ListTrialsRequest, dict]):
                The request object. Request message for
                [VizierService.ListTrials][google.cloud.aiplatform.v1.VizierService.ListTrials].
            parent (:class:`str`):
                Required. The resource name of the Study to list the
                Trial from. Format:
                ``projects/{project}/locations/{location}/studies/{study}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.services.vizier_service.pagers.ListTrialsAsyncPager:
                Response message for
                [VizierService.ListTrials][google.cloud.aiplatform.v1.VizierService.ListTrials].

                Iterating over this object will yield results and
                resolve additional pages automatically.

        """
        # Create or coerce a protobuf request object.
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = vizier_service.ListTrialsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_trials,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", request.parent),)),
        )

        # Send the request.
        response = await rpc(
            request,
            retry=retry,
            timeout=timeout,
            metadata=metadata,
        )

        # This method is paged; wrap the response in a pager, which provides
        # an `__aiter__` convenience method.
        response = pagers.ListTrialsAsyncPager(
            method=rpc,
            request=request,
            response=response,
            metadata=metadata,
        )

        # Done; return the response.
        return response

    async def add_trial_measurement(
        self,
        request: Union[vizier_service.AddTrialMeasurementRequest, dict] = None,
        *,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> study.Trial:
        r"""Adds a measurement of the objective metrics to a
        Trial. This measurement is assumed to have been taken
        before the Trial is complete.

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_add_trial_measurement():
                # Create a client
                client = aiplatform_v1.VizierServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.AddTrialMeasurementRequest(
                    trial_name="trial_name_value",
                )

                # Make the request
                response = await client.add_trial_measurement(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.AddTrialMeasurementRequest, dict]):
                The request object. Request message for
                [VizierService.AddTrialMeasurement][google.cloud.aiplatform.v1.VizierService.AddTrialMeasurement].
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.types.Trial:
                A message representing a Trial. A
                Trial contains a unique set of
                Parameters that has been or will be
                evaluated, along with the objective
                metrics got by running the Trial.

        """
        # Create or coerce a protobuf request object.
        request = vizier_service.AddTrialMeasurementRequest(request)

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.add_trial_measurement,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("trial_name", request.trial_name),)
            ),
        )

        # Send the request.
        response = await rpc(
            request,
            retry=retry,
            timeout=timeout,
            metadata=metadata,
        )

        # Done; return the response.
        return response

    async def complete_trial(
        self,
        request: Union[vizier_service.CompleteTrialRequest, dict] = None,
        *,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> study.Trial:
        r"""Marks a Trial as complete.

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_complete_trial():
                # Create a client
                client = aiplatform_v1.VizierServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.CompleteTrialRequest(
                    name="name_value",
                )

                # Make the request
                response = await client.complete_trial(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.CompleteTrialRequest, dict]):
                The request object. Request message for
                [VizierService.CompleteTrial][google.cloud.aiplatform.v1.VizierService.CompleteTrial].
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.types.Trial:
                A message representing a Trial. A
                Trial contains a unique set of
                Parameters that has been or will be
                evaluated, along with the objective
                metrics got by running the Trial.

        """
        # Create or coerce a protobuf request object.
        request = vizier_service.CompleteTrialRequest(request)

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.complete_trial,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("name", request.name),)),
        )

        # Send the request.
        response = await rpc(
            request,
            retry=retry,
            timeout=timeout,
            metadata=metadata,
        )

        # Done; return the response.
        return response

    async def delete_trial(
        self,
        request: Union[vizier_service.DeleteTrialRequest, dict] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> None:
        r"""Deletes a Trial.

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_delete_trial():
                # Create a client
                client = aiplatform_v1.VizierServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.DeleteTrialRequest(
                    name="name_value",
                )

                # Make the request
                await client.delete_trial(request=request)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.DeleteTrialRequest, dict]):
                The request object. Request message for
                [VizierService.DeleteTrial][google.cloud.aiplatform.v1.VizierService.DeleteTrial].
            name (:class:`str`):
                Required. The Trial's name. Format:
                ``projects/{project}/locations/{location}/studies/{study}/trials/{trial}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        # Create or coerce a protobuf request object.
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([name])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = vizier_service.DeleteTrialRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.delete_trial,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("name", request.name),)),
        )

        # Send the request.
        await rpc(
            request,
            retry=retry,
            timeout=timeout,
            metadata=metadata,
        )

    async def check_trial_early_stopping_state(
        self,
        request: Union[vizier_service.CheckTrialEarlyStoppingStateRequest, dict] = None,
        *,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Checks whether a Trial should stop or not. Returns a
        long-running operation. When the operation is successful, it
        will contain a
        [CheckTrialEarlyStoppingStateResponse][google.cloud.ml.v1.CheckTrialEarlyStoppingStateResponse].

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_check_trial_early_stopping_state():
                # Create a client
                client = aiplatform_v1.VizierServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.CheckTrialEarlyStoppingStateRequest(
                    trial_name="trial_name_value",
                )

                # Make the request
                operation = client.check_trial_early_stopping_state(request=request)

                print("Waiting for operation to complete...")

                response = await operation.result()

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.CheckTrialEarlyStoppingStateRequest, dict]):
                The request object. Request message for
                [VizierService.CheckTrialEarlyStoppingState][google.cloud.aiplatform.v1.VizierService.CheckTrialEarlyStoppingState].
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.api_core.operation_async.AsyncOperation:
                An object representing a long-running operation.

                The result type for the operation will be
                :class:`google.cloud.aiplatform_v1.types.CheckTrialEarlyStoppingStateResponse`
                Response message for
                [VizierService.CheckTrialEarlyStoppingState][google.cloud.aiplatform.v1.VizierService.CheckTrialEarlyStoppingState].

        """
        # Create or coerce a protobuf request object.
        request = vizier_service.CheckTrialEarlyStoppingStateRequest(request)

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.check_trial_early_stopping_state,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("trial_name", request.trial_name),)
            ),
        )

        # Send the request.
        response = await rpc(
            request,
            retry=retry,
            timeout=timeout,
            metadata=metadata,
        )

        # Wrap the response in an operation future.
        response = operation_async.from_gapic(
            response,
            self._client._transport.operations_client,
            vizier_service.CheckTrialEarlyStoppingStateResponse,
            metadata_type=vizier_service.CheckTrialEarlyStoppingStateMetatdata,
        )

        # Done; return the response.
        return response

    async def stop_trial(
        self,
        request: Union[vizier_service.StopTrialRequest, dict] = None,
        *,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> study.Trial:
        r"""Stops a Trial.

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_stop_trial():
                # Create a client
                client = aiplatform_v1.VizierServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.StopTrialRequest(
                    name="name_value",
                )

                # Make the request
                response = await client.stop_trial(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.StopTrialRequest, dict]):
                The request object. Request message for
                [VizierService.StopTrial][google.cloud.aiplatform.v1.VizierService.StopTrial].
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.types.Trial:
                A message representing a Trial. A
                Trial contains a unique set of
                Parameters that has been or will be
                evaluated, along with the objective
                metrics got by running the Trial.

        """
        # Create or coerce a protobuf request object.
        request = vizier_service.StopTrialRequest(request)

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.stop_trial,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("name", request.name),)),
        )

        # Send the request.
        response = await rpc(
            request,
            retry=retry,
            timeout=timeout,
            metadata=metadata,
        )

        # Done; return the response.
        return response

    async def list_optimal_trials(
        self,
        request: Union[vizier_service.ListOptimalTrialsRequest, dict] = None,
        *,
        parent: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> vizier_service.ListOptimalTrialsResponse:
        r"""Lists the pareto-optimal Trials for multi-objective Study or the
        optimal Trials for single-objective Study. The definition of
        pareto-optimal can be checked in wiki page.
        https://en.wikipedia.org/wiki/Pareto_efficiency

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_list_optimal_trials():
                # Create a client
                client = aiplatform_v1.VizierServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.ListOptimalTrialsRequest(
                    parent="parent_value",
                )

                # Make the request
                response = await client.list_optimal_trials(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.ListOptimalTrialsRequest, dict]):
                The request object. Request message for
                [VizierService.ListOptimalTrials][google.cloud.aiplatform.v1.VizierService.ListOptimalTrials].
            parent (:class:`str`):
                Required. The name of the Study that
                the optimal Trial belongs to.

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.types.ListOptimalTrialsResponse:
                Response message for
                [VizierService.ListOptimalTrials][google.cloud.aiplatform.v1.VizierService.ListOptimalTrials].

        """
        # Create or coerce a protobuf request object.
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = vizier_service.ListOptimalTrialsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_optimal_trials,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", request.parent),)),
        )

        # Send the request.
        response = await rpc(
            request,
            retry=retry,
            timeout=timeout,
            metadata=metadata,
        )

        # Done; return the response.
        return response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.transport.close()


try:
    DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo(
        gapic_version=pkg_resources.get_distribution(
            "google-cloud-aiplatform",
        ).version,
    )
except pkg_resources.DistributionNotFound:
    DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo()


__all__ = ("VizierServiceAsyncClient",)
