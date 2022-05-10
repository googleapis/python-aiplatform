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

from google.api_core import operation as gac_operation  # type: ignore
from google.api_core import operation_async  # type: ignore
from google.cloud.aiplatform_v1beta1.services.job_service import pagers
from google.cloud.aiplatform_v1beta1.types import batch_prediction_job
from google.cloud.aiplatform_v1beta1.types import (
    batch_prediction_job as gca_batch_prediction_job,
)
from google.cloud.aiplatform_v1beta1.types import completion_stats
from google.cloud.aiplatform_v1beta1.types import custom_job
from google.cloud.aiplatform_v1beta1.types import custom_job as gca_custom_job
from google.cloud.aiplatform_v1beta1.types import data_labeling_job
from google.cloud.aiplatform_v1beta1.types import (
    data_labeling_job as gca_data_labeling_job,
)
from google.cloud.aiplatform_v1beta1.types import encryption_spec
from google.cloud.aiplatform_v1beta1.types import explanation
from google.cloud.aiplatform_v1beta1.types import hyperparameter_tuning_job
from google.cloud.aiplatform_v1beta1.types import (
    hyperparameter_tuning_job as gca_hyperparameter_tuning_job,
)
from google.cloud.aiplatform_v1beta1.types import io
from google.cloud.aiplatform_v1beta1.types import job_service
from google.cloud.aiplatform_v1beta1.types import job_state
from google.cloud.aiplatform_v1beta1.types import machine_resources
from google.cloud.aiplatform_v1beta1.types import manual_batch_tuning_parameters
from google.cloud.aiplatform_v1beta1.types import model_deployment_monitoring_job
from google.cloud.aiplatform_v1beta1.types import (
    model_deployment_monitoring_job as gca_model_deployment_monitoring_job,
)
from google.cloud.aiplatform_v1beta1.types import model_monitoring
from google.cloud.aiplatform_v1beta1.types import operation as gca_operation
from google.cloud.aiplatform_v1beta1.types import study
from google.cloud.aiplatform_v1beta1.types import unmanaged_container_model
from google.protobuf import duration_pb2  # type: ignore
from google.protobuf import empty_pb2  # type: ignore
from google.protobuf import field_mask_pb2  # type: ignore
from google.protobuf import struct_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
from google.rpc import status_pb2  # type: ignore
from google.type import money_pb2  # type: ignore
from .transports.base import JobServiceTransport, DEFAULT_CLIENT_INFO
from .transports.grpc_asyncio import JobServiceGrpcAsyncIOTransport
from .client import JobServiceClient


class JobServiceAsyncClient:
    """A service for creating and managing Vertex AI's jobs."""

    _client: JobServiceClient

    DEFAULT_ENDPOINT = JobServiceClient.DEFAULT_ENDPOINT
    DEFAULT_MTLS_ENDPOINT = JobServiceClient.DEFAULT_MTLS_ENDPOINT

    batch_prediction_job_path = staticmethod(JobServiceClient.batch_prediction_job_path)
    parse_batch_prediction_job_path = staticmethod(
        JobServiceClient.parse_batch_prediction_job_path
    )
    custom_job_path = staticmethod(JobServiceClient.custom_job_path)
    parse_custom_job_path = staticmethod(JobServiceClient.parse_custom_job_path)
    data_labeling_job_path = staticmethod(JobServiceClient.data_labeling_job_path)
    parse_data_labeling_job_path = staticmethod(
        JobServiceClient.parse_data_labeling_job_path
    )
    dataset_path = staticmethod(JobServiceClient.dataset_path)
    parse_dataset_path = staticmethod(JobServiceClient.parse_dataset_path)
    endpoint_path = staticmethod(JobServiceClient.endpoint_path)
    parse_endpoint_path = staticmethod(JobServiceClient.parse_endpoint_path)
    hyperparameter_tuning_job_path = staticmethod(
        JobServiceClient.hyperparameter_tuning_job_path
    )
    parse_hyperparameter_tuning_job_path = staticmethod(
        JobServiceClient.parse_hyperparameter_tuning_job_path
    )
    model_path = staticmethod(JobServiceClient.model_path)
    parse_model_path = staticmethod(JobServiceClient.parse_model_path)
    model_deployment_monitoring_job_path = staticmethod(
        JobServiceClient.model_deployment_monitoring_job_path
    )
    parse_model_deployment_monitoring_job_path = staticmethod(
        JobServiceClient.parse_model_deployment_monitoring_job_path
    )
    network_path = staticmethod(JobServiceClient.network_path)
    parse_network_path = staticmethod(JobServiceClient.parse_network_path)
    tensorboard_path = staticmethod(JobServiceClient.tensorboard_path)
    parse_tensorboard_path = staticmethod(JobServiceClient.parse_tensorboard_path)
    trial_path = staticmethod(JobServiceClient.trial_path)
    parse_trial_path = staticmethod(JobServiceClient.parse_trial_path)
    common_billing_account_path = staticmethod(
        JobServiceClient.common_billing_account_path
    )
    parse_common_billing_account_path = staticmethod(
        JobServiceClient.parse_common_billing_account_path
    )
    common_folder_path = staticmethod(JobServiceClient.common_folder_path)
    parse_common_folder_path = staticmethod(JobServiceClient.parse_common_folder_path)
    common_organization_path = staticmethod(JobServiceClient.common_organization_path)
    parse_common_organization_path = staticmethod(
        JobServiceClient.parse_common_organization_path
    )
    common_project_path = staticmethod(JobServiceClient.common_project_path)
    parse_common_project_path = staticmethod(JobServiceClient.parse_common_project_path)
    common_location_path = staticmethod(JobServiceClient.common_location_path)
    parse_common_location_path = staticmethod(
        JobServiceClient.parse_common_location_path
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
            JobServiceAsyncClient: The constructed client.
        """
        return JobServiceClient.from_service_account_info.__func__(JobServiceAsyncClient, info, *args, **kwargs)  # type: ignore

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
            JobServiceAsyncClient: The constructed client.
        """
        return JobServiceClient.from_service_account_file.__func__(JobServiceAsyncClient, filename, *args, **kwargs)  # type: ignore

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
        return JobServiceClient.get_mtls_endpoint_and_cert_source(client_options)  # type: ignore

    @property
    def transport(self) -> JobServiceTransport:
        """Returns the transport used by the client instance.

        Returns:
            JobServiceTransport: The transport used by the client instance.
        """
        return self._client.transport

    get_transport_class = functools.partial(
        type(JobServiceClient).get_transport_class, type(JobServiceClient)
    )

    def __init__(
        self,
        *,
        credentials: ga_credentials.Credentials = None,
        transport: Union[str, JobServiceTransport] = "grpc_asyncio",
        client_options: ClientOptions = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
    ) -> None:
        """Instantiates the job service client.

        Args:
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            transport (Union[str, ~.JobServiceTransport]): The
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
        self._client = JobServiceClient(
            credentials=credentials,
            transport=transport,
            client_options=client_options,
            client_info=client_info,
        )

    async def create_custom_job(
        self,
        request: Union[job_service.CreateCustomJobRequest, dict] = None,
        *,
        parent: str = None,
        custom_job: gca_custom_job.CustomJob = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_custom_job.CustomJob:
        r"""Creates a CustomJob. A created CustomJob right away
        will be attempted to be run.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_create_custom_job():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                custom_job = aiplatform_v1beta1.CustomJob()
                custom_job.display_name = "display_name_value"
                custom_job.job_spec.worker_pool_specs.container_spec.image_uri = "image_uri_value"

                request = aiplatform_v1beta1.CreateCustomJobRequest(
                    parent="parent_value",
                    custom_job=custom_job,
                )

                # Make the request
                response = await client.create_custom_job(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.CreateCustomJobRequest, dict]):
                The request object. Request message for
                [JobService.CreateCustomJob][google.cloud.aiplatform.v1beta1.JobService.CreateCustomJob].
            parent (:class:`str`):
                Required. The resource name of the Location to create
                the CustomJob in. Format:
                ``projects/{project}/locations/{location}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            custom_job (:class:`google.cloud.aiplatform_v1beta1.types.CustomJob`):
                Required. The CustomJob to create.
                This corresponds to the ``custom_job`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.CustomJob:
                Represents a job that runs custom
                workloads such as a Docker container or
                a Python package. A CustomJob can have
                multiple worker pools and each worker
                pool can have its own machine and input
                spec. A CustomJob will be cleaned up
                once the job enters terminal state
                (failed or succeeded).

        """
        # Create or coerce a protobuf request object.
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, custom_job])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = job_service.CreateCustomJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if custom_job is not None:
            request.custom_job = custom_job

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_custom_job,
            default_timeout=5.0,
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

    async def get_custom_job(
        self,
        request: Union[job_service.GetCustomJobRequest, dict] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> custom_job.CustomJob:
        r"""Gets a CustomJob.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_get_custom_job():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1beta1.GetCustomJobRequest(
                    name="name_value",
                )

                # Make the request
                response = await client.get_custom_job(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.GetCustomJobRequest, dict]):
                The request object. Request message for
                [JobService.GetCustomJob][google.cloud.aiplatform.v1beta1.JobService.GetCustomJob].
            name (:class:`str`):
                Required. The name of the CustomJob resource. Format:
                ``projects/{project}/locations/{location}/customJobs/{custom_job}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.CustomJob:
                Represents a job that runs custom
                workloads such as a Docker container or
                a Python package. A CustomJob can have
                multiple worker pools and each worker
                pool can have its own machine and input
                spec. A CustomJob will be cleaned up
                once the job enters terminal state
                (failed or succeeded).

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

        request = job_service.GetCustomJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_custom_job,
            default_timeout=5.0,
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

    async def list_custom_jobs(
        self,
        request: Union[job_service.ListCustomJobsRequest, dict] = None,
        *,
        parent: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListCustomJobsAsyncPager:
        r"""Lists CustomJobs in a Location.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_list_custom_jobs():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1beta1.ListCustomJobsRequest(
                    parent="parent_value",
                )

                # Make the request
                page_result = client.list_custom_jobs(request=request)

                # Handle the response
                async for response in page_result:
                    print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.ListCustomJobsRequest, dict]):
                The request object. Request message for
                [JobService.ListCustomJobs][google.cloud.aiplatform.v1beta1.JobService.ListCustomJobs].
            parent (:class:`str`):
                Required. The resource name of the Location to list the
                CustomJobs from. Format:
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
            google.cloud.aiplatform_v1beta1.services.job_service.pagers.ListCustomJobsAsyncPager:
                Response message for
                [JobService.ListCustomJobs][google.cloud.aiplatform.v1beta1.JobService.ListCustomJobs]

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

        request = job_service.ListCustomJobsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_custom_jobs,
            default_timeout=5.0,
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
        response = pagers.ListCustomJobsAsyncPager(
            method=rpc,
            request=request,
            response=response,
            metadata=metadata,
        )

        # Done; return the response.
        return response

    async def delete_custom_job(
        self,
        request: Union[job_service.DeleteCustomJobRequest, dict] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Deletes a CustomJob.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_delete_custom_job():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1beta1.DeleteCustomJobRequest(
                    name="name_value",
                )

                # Make the request
                operation = client.delete_custom_job(request=request)

                print("Waiting for operation to complete...")

                response = await operation.result()

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.DeleteCustomJobRequest, dict]):
                The request object. Request message for
                [JobService.DeleteCustomJob][google.cloud.aiplatform.v1beta1.JobService.DeleteCustomJob].
            name (:class:`str`):
                Required. The name of the CustomJob resource to be
                deleted. Format:
                ``projects/{project}/locations/{location}/customJobs/{custom_job}``

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
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([name])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = job_service.DeleteCustomJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.delete_custom_job,
            default_timeout=5.0,
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

        # Wrap the response in an operation future.
        response = operation_async.from_gapic(
            response,
            self._client._transport.operations_client,
            empty_pb2.Empty,
            metadata_type=gca_operation.DeleteOperationMetadata,
        )

        # Done; return the response.
        return response

    async def cancel_custom_job(
        self,
        request: Union[job_service.CancelCustomJobRequest, dict] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> None:
        r"""Cancels a CustomJob. Starts asynchronous cancellation on the
        CustomJob. The server makes a best effort to cancel the job, but
        success is not guaranteed. Clients can use
        [JobService.GetCustomJob][google.cloud.aiplatform.v1beta1.JobService.GetCustomJob]
        or other methods to check whether the cancellation succeeded or
        whether the job completed despite cancellation. On successful
        cancellation, the CustomJob is not deleted; instead it becomes a
        job with a
        [CustomJob.error][google.cloud.aiplatform.v1beta1.CustomJob.error]
        value with a [google.rpc.Status.code][google.rpc.Status.code] of
        1, corresponding to ``Code.CANCELLED``, and
        [CustomJob.state][google.cloud.aiplatform.v1beta1.CustomJob.state]
        is set to ``CANCELLED``.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_cancel_custom_job():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1beta1.CancelCustomJobRequest(
                    name="name_value",
                )

                # Make the request
                await client.cancel_custom_job(request=request)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.CancelCustomJobRequest, dict]):
                The request object. Request message for
                [JobService.CancelCustomJob][google.cloud.aiplatform.v1beta1.JobService.CancelCustomJob].
            name (:class:`str`):
                Required. The name of the CustomJob to cancel. Format:
                ``projects/{project}/locations/{location}/customJobs/{custom_job}``

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

        request = job_service.CancelCustomJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.cancel_custom_job,
            default_timeout=5.0,
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

    async def create_data_labeling_job(
        self,
        request: Union[job_service.CreateDataLabelingJobRequest, dict] = None,
        *,
        parent: str = None,
        data_labeling_job: gca_data_labeling_job.DataLabelingJob = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_data_labeling_job.DataLabelingJob:
        r"""Creates a DataLabelingJob.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_create_data_labeling_job():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                data_labeling_job = aiplatform_v1beta1.DataLabelingJob()
                data_labeling_job.display_name = "display_name_value"
                data_labeling_job.datasets = ['datasets_value_1', 'datasets_value_2']
                data_labeling_job.labeler_count = 1375
                data_labeling_job.instruction_uri = "instruction_uri_value"
                data_labeling_job.inputs_schema_uri = "inputs_schema_uri_value"
                data_labeling_job.inputs.null_value = "NULL_VALUE"

                request = aiplatform_v1beta1.CreateDataLabelingJobRequest(
                    parent="parent_value",
                    data_labeling_job=data_labeling_job,
                )

                # Make the request
                response = await client.create_data_labeling_job(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.CreateDataLabelingJobRequest, dict]):
                The request object. Request message for
                [JobService.CreateDataLabelingJob][google.cloud.aiplatform.v1beta1.JobService.CreateDataLabelingJob].
            parent (:class:`str`):
                Required. The parent of the DataLabelingJob. Format:
                ``projects/{project}/locations/{location}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            data_labeling_job (:class:`google.cloud.aiplatform_v1beta1.types.DataLabelingJob`):
                Required. The DataLabelingJob to
                create.

                This corresponds to the ``data_labeling_job`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.DataLabelingJob:
                DataLabelingJob is used to trigger a
                human labeling job on unlabeled data
                from the following Dataset:

        """
        # Create or coerce a protobuf request object.
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, data_labeling_job])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = job_service.CreateDataLabelingJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if data_labeling_job is not None:
            request.data_labeling_job = data_labeling_job

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_data_labeling_job,
            default_timeout=5.0,
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

    async def get_data_labeling_job(
        self,
        request: Union[job_service.GetDataLabelingJobRequest, dict] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> data_labeling_job.DataLabelingJob:
        r"""Gets a DataLabelingJob.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_get_data_labeling_job():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1beta1.GetDataLabelingJobRequest(
                    name="name_value",
                )

                # Make the request
                response = await client.get_data_labeling_job(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.GetDataLabelingJobRequest, dict]):
                The request object. Request message for
                [JobService.GetDataLabelingJob][google.cloud.aiplatform.v1beta1.JobService.GetDataLabelingJob].
            name (:class:`str`):
                Required. The name of the DataLabelingJob. Format:
                ``projects/{project}/locations/{location}/dataLabelingJobs/{data_labeling_job}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.DataLabelingJob:
                DataLabelingJob is used to trigger a
                human labeling job on unlabeled data
                from the following Dataset:

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

        request = job_service.GetDataLabelingJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_data_labeling_job,
            default_timeout=5.0,
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

    async def list_data_labeling_jobs(
        self,
        request: Union[job_service.ListDataLabelingJobsRequest, dict] = None,
        *,
        parent: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListDataLabelingJobsAsyncPager:
        r"""Lists DataLabelingJobs in a Location.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_list_data_labeling_jobs():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1beta1.ListDataLabelingJobsRequest(
                    parent="parent_value",
                )

                # Make the request
                page_result = client.list_data_labeling_jobs(request=request)

                # Handle the response
                async for response in page_result:
                    print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.ListDataLabelingJobsRequest, dict]):
                The request object. Request message for
                [JobService.ListDataLabelingJobs][google.cloud.aiplatform.v1beta1.JobService.ListDataLabelingJobs].
            parent (:class:`str`):
                Required. The parent of the DataLabelingJob. Format:
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
            google.cloud.aiplatform_v1beta1.services.job_service.pagers.ListDataLabelingJobsAsyncPager:
                Response message for
                [JobService.ListDataLabelingJobs][google.cloud.aiplatform.v1beta1.JobService.ListDataLabelingJobs].

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

        request = job_service.ListDataLabelingJobsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_data_labeling_jobs,
            default_timeout=5.0,
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
        response = pagers.ListDataLabelingJobsAsyncPager(
            method=rpc,
            request=request,
            response=response,
            metadata=metadata,
        )

        # Done; return the response.
        return response

    async def delete_data_labeling_job(
        self,
        request: Union[job_service.DeleteDataLabelingJobRequest, dict] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Deletes a DataLabelingJob.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_delete_data_labeling_job():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1beta1.DeleteDataLabelingJobRequest(
                    name="name_value",
                )

                # Make the request
                operation = client.delete_data_labeling_job(request=request)

                print("Waiting for operation to complete...")

                response = await operation.result()

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.DeleteDataLabelingJobRequest, dict]):
                The request object. Request message for
                [JobService.DeleteDataLabelingJob][google.cloud.aiplatform.v1beta1.JobService.DeleteDataLabelingJob].
            name (:class:`str`):
                Required. The name of the DataLabelingJob to be deleted.
                Format:
                ``projects/{project}/locations/{location}/dataLabelingJobs/{data_labeling_job}``

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
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([name])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = job_service.DeleteDataLabelingJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.delete_data_labeling_job,
            default_timeout=5.0,
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

        # Wrap the response in an operation future.
        response = operation_async.from_gapic(
            response,
            self._client._transport.operations_client,
            empty_pb2.Empty,
            metadata_type=gca_operation.DeleteOperationMetadata,
        )

        # Done; return the response.
        return response

    async def cancel_data_labeling_job(
        self,
        request: Union[job_service.CancelDataLabelingJobRequest, dict] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> None:
        r"""Cancels a DataLabelingJob. Success of cancellation is
        not guaranteed.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_cancel_data_labeling_job():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1beta1.CancelDataLabelingJobRequest(
                    name="name_value",
                )

                # Make the request
                await client.cancel_data_labeling_job(request=request)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.CancelDataLabelingJobRequest, dict]):
                The request object. Request message for
                [JobService.CancelDataLabelingJob][google.cloud.aiplatform.v1beta1.JobService.CancelDataLabelingJob].
            name (:class:`str`):
                Required. The name of the DataLabelingJob. Format:
                ``projects/{project}/locations/{location}/dataLabelingJobs/{data_labeling_job}``

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

        request = job_service.CancelDataLabelingJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.cancel_data_labeling_job,
            default_timeout=5.0,
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

    async def create_hyperparameter_tuning_job(
        self,
        request: Union[job_service.CreateHyperparameterTuningJobRequest, dict] = None,
        *,
        parent: str = None,
        hyperparameter_tuning_job: gca_hyperparameter_tuning_job.HyperparameterTuningJob = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_hyperparameter_tuning_job.HyperparameterTuningJob:
        r"""Creates a HyperparameterTuningJob

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_create_hyperparameter_tuning_job():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                hyperparameter_tuning_job = aiplatform_v1beta1.HyperparameterTuningJob()
                hyperparameter_tuning_job.display_name = "display_name_value"
                hyperparameter_tuning_job.study_spec.metrics.metric_id = "metric_id_value"
                hyperparameter_tuning_job.study_spec.metrics.goal = "MINIMIZE"
                hyperparameter_tuning_job.study_spec.parameters.double_value_spec.min_value = 0.96
                hyperparameter_tuning_job.study_spec.parameters.double_value_spec.max_value = 0.962
                hyperparameter_tuning_job.study_spec.parameters.parameter_id = "parameter_id_value"
                hyperparameter_tuning_job.max_trial_count = 1609
                hyperparameter_tuning_job.parallel_trial_count = 2128
                hyperparameter_tuning_job.trial_job_spec.worker_pool_specs.container_spec.image_uri = "image_uri_value"

                request = aiplatform_v1beta1.CreateHyperparameterTuningJobRequest(
                    parent="parent_value",
                    hyperparameter_tuning_job=hyperparameter_tuning_job,
                )

                # Make the request
                response = await client.create_hyperparameter_tuning_job(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.CreateHyperparameterTuningJobRequest, dict]):
                The request object. Request message for
                [JobService.CreateHyperparameterTuningJob][google.cloud.aiplatform.v1beta1.JobService.CreateHyperparameterTuningJob].
            parent (:class:`str`):
                Required. The resource name of the Location to create
                the HyperparameterTuningJob in. Format:
                ``projects/{project}/locations/{location}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            hyperparameter_tuning_job (:class:`google.cloud.aiplatform_v1beta1.types.HyperparameterTuningJob`):
                Required. The HyperparameterTuningJob
                to create.

                This corresponds to the ``hyperparameter_tuning_job`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.HyperparameterTuningJob:
                Represents a HyperparameterTuningJob.
                A HyperparameterTuningJob has a Study
                specification and multiple CustomJobs
                with identical CustomJob specification.

        """
        # Create or coerce a protobuf request object.
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, hyperparameter_tuning_job])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = job_service.CreateHyperparameterTuningJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if hyperparameter_tuning_job is not None:
            request.hyperparameter_tuning_job = hyperparameter_tuning_job

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_hyperparameter_tuning_job,
            default_timeout=5.0,
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

    async def get_hyperparameter_tuning_job(
        self,
        request: Union[job_service.GetHyperparameterTuningJobRequest, dict] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> hyperparameter_tuning_job.HyperparameterTuningJob:
        r"""Gets a HyperparameterTuningJob

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_get_hyperparameter_tuning_job():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1beta1.GetHyperparameterTuningJobRequest(
                    name="name_value",
                )

                # Make the request
                response = await client.get_hyperparameter_tuning_job(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.GetHyperparameterTuningJobRequest, dict]):
                The request object. Request message for
                [JobService.GetHyperparameterTuningJob][google.cloud.aiplatform.v1beta1.JobService.GetHyperparameterTuningJob].
            name (:class:`str`):
                Required. The name of the HyperparameterTuningJob
                resource. Format:
                ``projects/{project}/locations/{location}/hyperparameterTuningJobs/{hyperparameter_tuning_job}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.HyperparameterTuningJob:
                Represents a HyperparameterTuningJob.
                A HyperparameterTuningJob has a Study
                specification and multiple CustomJobs
                with identical CustomJob specification.

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

        request = job_service.GetHyperparameterTuningJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_hyperparameter_tuning_job,
            default_timeout=5.0,
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

    async def list_hyperparameter_tuning_jobs(
        self,
        request: Union[job_service.ListHyperparameterTuningJobsRequest, dict] = None,
        *,
        parent: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListHyperparameterTuningJobsAsyncPager:
        r"""Lists HyperparameterTuningJobs in a Location.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_list_hyperparameter_tuning_jobs():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1beta1.ListHyperparameterTuningJobsRequest(
                    parent="parent_value",
                )

                # Make the request
                page_result = client.list_hyperparameter_tuning_jobs(request=request)

                # Handle the response
                async for response in page_result:
                    print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.ListHyperparameterTuningJobsRequest, dict]):
                The request object. Request message for
                [JobService.ListHyperparameterTuningJobs][google.cloud.aiplatform.v1beta1.JobService.ListHyperparameterTuningJobs].
            parent (:class:`str`):
                Required. The resource name of the Location to list the
                HyperparameterTuningJobs from. Format:
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
            google.cloud.aiplatform_v1beta1.services.job_service.pagers.ListHyperparameterTuningJobsAsyncPager:
                Response message for
                [JobService.ListHyperparameterTuningJobs][google.cloud.aiplatform.v1beta1.JobService.ListHyperparameterTuningJobs]

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

        request = job_service.ListHyperparameterTuningJobsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_hyperparameter_tuning_jobs,
            default_timeout=5.0,
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
        response = pagers.ListHyperparameterTuningJobsAsyncPager(
            method=rpc,
            request=request,
            response=response,
            metadata=metadata,
        )

        # Done; return the response.
        return response

    async def delete_hyperparameter_tuning_job(
        self,
        request: Union[job_service.DeleteHyperparameterTuningJobRequest, dict] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Deletes a HyperparameterTuningJob.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_delete_hyperparameter_tuning_job():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1beta1.DeleteHyperparameterTuningJobRequest(
                    name="name_value",
                )

                # Make the request
                operation = client.delete_hyperparameter_tuning_job(request=request)

                print("Waiting for operation to complete...")

                response = await operation.result()

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.DeleteHyperparameterTuningJobRequest, dict]):
                The request object. Request message for
                [JobService.DeleteHyperparameterTuningJob][google.cloud.aiplatform.v1beta1.JobService.DeleteHyperparameterTuningJob].
            name (:class:`str`):
                Required. The name of the HyperparameterTuningJob
                resource to be deleted. Format:
                ``projects/{project}/locations/{location}/hyperparameterTuningJobs/{hyperparameter_tuning_job}``

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
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([name])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = job_service.DeleteHyperparameterTuningJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.delete_hyperparameter_tuning_job,
            default_timeout=5.0,
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

        # Wrap the response in an operation future.
        response = operation_async.from_gapic(
            response,
            self._client._transport.operations_client,
            empty_pb2.Empty,
            metadata_type=gca_operation.DeleteOperationMetadata,
        )

        # Done; return the response.
        return response

    async def cancel_hyperparameter_tuning_job(
        self,
        request: Union[job_service.CancelHyperparameterTuningJobRequest, dict] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> None:
        r"""Cancels a HyperparameterTuningJob. Starts asynchronous
        cancellation on the HyperparameterTuningJob. The server makes a
        best effort to cancel the job, but success is not guaranteed.
        Clients can use
        [JobService.GetHyperparameterTuningJob][google.cloud.aiplatform.v1beta1.JobService.GetHyperparameterTuningJob]
        or other methods to check whether the cancellation succeeded or
        whether the job completed despite cancellation. On successful
        cancellation, the HyperparameterTuningJob is not deleted;
        instead it becomes a job with a
        [HyperparameterTuningJob.error][google.cloud.aiplatform.v1beta1.HyperparameterTuningJob.error]
        value with a [google.rpc.Status.code][google.rpc.Status.code] of
        1, corresponding to ``Code.CANCELLED``, and
        [HyperparameterTuningJob.state][google.cloud.aiplatform.v1beta1.HyperparameterTuningJob.state]
        is set to ``CANCELLED``.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_cancel_hyperparameter_tuning_job():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1beta1.CancelHyperparameterTuningJobRequest(
                    name="name_value",
                )

                # Make the request
                await client.cancel_hyperparameter_tuning_job(request=request)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.CancelHyperparameterTuningJobRequest, dict]):
                The request object. Request message for
                [JobService.CancelHyperparameterTuningJob][google.cloud.aiplatform.v1beta1.JobService.CancelHyperparameterTuningJob].
            name (:class:`str`):
                Required. The name of the HyperparameterTuningJob to
                cancel. Format:
                ``projects/{project}/locations/{location}/hyperparameterTuningJobs/{hyperparameter_tuning_job}``

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

        request = job_service.CancelHyperparameterTuningJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.cancel_hyperparameter_tuning_job,
            default_timeout=5.0,
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

    async def create_batch_prediction_job(
        self,
        request: Union[job_service.CreateBatchPredictionJobRequest, dict] = None,
        *,
        parent: str = None,
        batch_prediction_job: gca_batch_prediction_job.BatchPredictionJob = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_batch_prediction_job.BatchPredictionJob:
        r"""Creates a BatchPredictionJob. A BatchPredictionJob
        once created will right away be attempted to start.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_create_batch_prediction_job():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                batch_prediction_job = aiplatform_v1beta1.BatchPredictionJob()
                batch_prediction_job.display_name = "display_name_value"
                batch_prediction_job.input_config.gcs_source.uris = ['uris_value_1', 'uris_value_2']
                batch_prediction_job.input_config.instances_format = "instances_format_value"
                batch_prediction_job.output_config.gcs_destination.output_uri_prefix = "output_uri_prefix_value"
                batch_prediction_job.output_config.predictions_format = "predictions_format_value"

                request = aiplatform_v1beta1.CreateBatchPredictionJobRequest(
                    parent="parent_value",
                    batch_prediction_job=batch_prediction_job,
                )

                # Make the request
                response = await client.create_batch_prediction_job(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.CreateBatchPredictionJobRequest, dict]):
                The request object. Request message for
                [JobService.CreateBatchPredictionJob][google.cloud.aiplatform.v1beta1.JobService.CreateBatchPredictionJob].
            parent (:class:`str`):
                Required. The resource name of the Location to create
                the BatchPredictionJob in. Format:
                ``projects/{project}/locations/{location}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            batch_prediction_job (:class:`google.cloud.aiplatform_v1beta1.types.BatchPredictionJob`):
                Required. The BatchPredictionJob to
                create.

                This corresponds to the ``batch_prediction_job`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.BatchPredictionJob:
                A job that uses a [Model][google.cloud.aiplatform.v1beta1.BatchPredictionJob.model] to produce predictions
                   on multiple [input
                   instances][google.cloud.aiplatform.v1beta1.BatchPredictionJob.input_config].
                   If predictions for significant portion of the
                   instances fail, the job may finish without attempting
                   predictions for all remaining instances.

        """
        # Create or coerce a protobuf request object.
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, batch_prediction_job])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = job_service.CreateBatchPredictionJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if batch_prediction_job is not None:
            request.batch_prediction_job = batch_prediction_job

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_batch_prediction_job,
            default_timeout=5.0,
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

    async def get_batch_prediction_job(
        self,
        request: Union[job_service.GetBatchPredictionJobRequest, dict] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> batch_prediction_job.BatchPredictionJob:
        r"""Gets a BatchPredictionJob

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_get_batch_prediction_job():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1beta1.GetBatchPredictionJobRequest(
                    name="name_value",
                )

                # Make the request
                response = await client.get_batch_prediction_job(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.GetBatchPredictionJobRequest, dict]):
                The request object. Request message for
                [JobService.GetBatchPredictionJob][google.cloud.aiplatform.v1beta1.JobService.GetBatchPredictionJob].
            name (:class:`str`):
                Required. The name of the BatchPredictionJob resource.
                Format:
                ``projects/{project}/locations/{location}/batchPredictionJobs/{batch_prediction_job}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.BatchPredictionJob:
                A job that uses a [Model][google.cloud.aiplatform.v1beta1.BatchPredictionJob.model] to produce predictions
                   on multiple [input
                   instances][google.cloud.aiplatform.v1beta1.BatchPredictionJob.input_config].
                   If predictions for significant portion of the
                   instances fail, the job may finish without attempting
                   predictions for all remaining instances.

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

        request = job_service.GetBatchPredictionJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_batch_prediction_job,
            default_timeout=5.0,
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

    async def list_batch_prediction_jobs(
        self,
        request: Union[job_service.ListBatchPredictionJobsRequest, dict] = None,
        *,
        parent: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListBatchPredictionJobsAsyncPager:
        r"""Lists BatchPredictionJobs in a Location.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_list_batch_prediction_jobs():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1beta1.ListBatchPredictionJobsRequest(
                    parent="parent_value",
                )

                # Make the request
                page_result = client.list_batch_prediction_jobs(request=request)

                # Handle the response
                async for response in page_result:
                    print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.ListBatchPredictionJobsRequest, dict]):
                The request object. Request message for
                [JobService.ListBatchPredictionJobs][google.cloud.aiplatform.v1beta1.JobService.ListBatchPredictionJobs].
            parent (:class:`str`):
                Required. The resource name of the Location to list the
                BatchPredictionJobs from. Format:
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
            google.cloud.aiplatform_v1beta1.services.job_service.pagers.ListBatchPredictionJobsAsyncPager:
                Response message for
                [JobService.ListBatchPredictionJobs][google.cloud.aiplatform.v1beta1.JobService.ListBatchPredictionJobs]

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

        request = job_service.ListBatchPredictionJobsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_batch_prediction_jobs,
            default_timeout=5.0,
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
        response = pagers.ListBatchPredictionJobsAsyncPager(
            method=rpc,
            request=request,
            response=response,
            metadata=metadata,
        )

        # Done; return the response.
        return response

    async def delete_batch_prediction_job(
        self,
        request: Union[job_service.DeleteBatchPredictionJobRequest, dict] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Deletes a BatchPredictionJob. Can only be called on
        jobs that already finished.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_delete_batch_prediction_job():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1beta1.DeleteBatchPredictionJobRequest(
                    name="name_value",
                )

                # Make the request
                operation = client.delete_batch_prediction_job(request=request)

                print("Waiting for operation to complete...")

                response = await operation.result()

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.DeleteBatchPredictionJobRequest, dict]):
                The request object. Request message for
                [JobService.DeleteBatchPredictionJob][google.cloud.aiplatform.v1beta1.JobService.DeleteBatchPredictionJob].
            name (:class:`str`):
                Required. The name of the BatchPredictionJob resource to
                be deleted. Format:
                ``projects/{project}/locations/{location}/batchPredictionJobs/{batch_prediction_job}``

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
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([name])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = job_service.DeleteBatchPredictionJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.delete_batch_prediction_job,
            default_timeout=5.0,
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

        # Wrap the response in an operation future.
        response = operation_async.from_gapic(
            response,
            self._client._transport.operations_client,
            empty_pb2.Empty,
            metadata_type=gca_operation.DeleteOperationMetadata,
        )

        # Done; return the response.
        return response

    async def cancel_batch_prediction_job(
        self,
        request: Union[job_service.CancelBatchPredictionJobRequest, dict] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> None:
        r"""Cancels a BatchPredictionJob.

        Starts asynchronous cancellation on the BatchPredictionJob. The
        server makes the best effort to cancel the job, but success is
        not guaranteed. Clients can use
        [JobService.GetBatchPredictionJob][google.cloud.aiplatform.v1beta1.JobService.GetBatchPredictionJob]
        or other methods to check whether the cancellation succeeded or
        whether the job completed despite cancellation. On a successful
        cancellation, the BatchPredictionJob is not deleted;instead its
        [BatchPredictionJob.state][google.cloud.aiplatform.v1beta1.BatchPredictionJob.state]
        is set to ``CANCELLED``. Any files already outputted by the job
        are not deleted.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_cancel_batch_prediction_job():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1beta1.CancelBatchPredictionJobRequest(
                    name="name_value",
                )

                # Make the request
                await client.cancel_batch_prediction_job(request=request)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.CancelBatchPredictionJobRequest, dict]):
                The request object. Request message for
                [JobService.CancelBatchPredictionJob][google.cloud.aiplatform.v1beta1.JobService.CancelBatchPredictionJob].
            name (:class:`str`):
                Required. The name of the BatchPredictionJob to cancel.
                Format:
                ``projects/{project}/locations/{location}/batchPredictionJobs/{batch_prediction_job}``

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

        request = job_service.CancelBatchPredictionJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.cancel_batch_prediction_job,
            default_timeout=5.0,
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

    async def create_model_deployment_monitoring_job(
        self,
        request: Union[
            job_service.CreateModelDeploymentMonitoringJobRequest, dict
        ] = None,
        *,
        parent: str = None,
        model_deployment_monitoring_job: gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob:
        r"""Creates a ModelDeploymentMonitoringJob. It will run
        periodically on a configured interval.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_create_model_deployment_monitoring_job():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                model_deployment_monitoring_job = aiplatform_v1beta1.ModelDeploymentMonitoringJob()
                model_deployment_monitoring_job.display_name = "display_name_value"
                model_deployment_monitoring_job.endpoint = "endpoint_value"

                request = aiplatform_v1beta1.CreateModelDeploymentMonitoringJobRequest(
                    parent="parent_value",
                    model_deployment_monitoring_job=model_deployment_monitoring_job,
                )

                # Make the request
                response = await client.create_model_deployment_monitoring_job(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.CreateModelDeploymentMonitoringJobRequest, dict]):
                The request object. Request message for
                [JobService.CreateModelDeploymentMonitoringJob][google.cloud.aiplatform.v1beta1.JobService.CreateModelDeploymentMonitoringJob].
            parent (:class:`str`):
                Required. The parent of the
                ModelDeploymentMonitoringJob. Format:
                ``projects/{project}/locations/{location}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            model_deployment_monitoring_job (:class:`google.cloud.aiplatform_v1beta1.types.ModelDeploymentMonitoringJob`):
                Required. The
                ModelDeploymentMonitoringJob to create

                This corresponds to the ``model_deployment_monitoring_job`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.ModelDeploymentMonitoringJob:
                Represents a job that runs
                periodically to monitor the deployed
                models in an endpoint. It will analyze
                the logged training & prediction data to
                detect any abnormal behaviors.

        """
        # Create or coerce a protobuf request object.
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, model_deployment_monitoring_job])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = job_service.CreateModelDeploymentMonitoringJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if model_deployment_monitoring_job is not None:
            request.model_deployment_monitoring_job = model_deployment_monitoring_job

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_model_deployment_monitoring_job,
            default_timeout=60.0,
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

    async def search_model_deployment_monitoring_stats_anomalies(
        self,
        request: Union[
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest, dict
        ] = None,
        *,
        model_deployment_monitoring_job: str = None,
        deployed_model_id: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.SearchModelDeploymentMonitoringStatsAnomaliesAsyncPager:
        r"""Searches Model Monitoring Statistics generated within
        a given time window.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_search_model_deployment_monitoring_stats_anomalies():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1beta1.SearchModelDeploymentMonitoringStatsAnomaliesRequest(
                    model_deployment_monitoring_job="model_deployment_monitoring_job_value",
                    deployed_model_id="deployed_model_id_value",
                )

                # Make the request
                page_result = client.search_model_deployment_monitoring_stats_anomalies(request=request)

                # Handle the response
                async for response in page_result:
                    print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.SearchModelDeploymentMonitoringStatsAnomaliesRequest, dict]):
                The request object. Request message for
                [JobService.SearchModelDeploymentMonitoringStatsAnomalies][google.cloud.aiplatform.v1beta1.JobService.SearchModelDeploymentMonitoringStatsAnomalies].
            model_deployment_monitoring_job (:class:`str`):
                Required. ModelDeploymentMonitoring Job resource name.
                Format:
                ``projects/{project}/locations/{location}/modelDeploymentMonitoringJobs/{model_deployment_monitoring_job}``

                This corresponds to the ``model_deployment_monitoring_job`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            deployed_model_id (:class:`str`):
                Required. The DeployedModel ID of the
                [ModelDeploymentMonitoringObjectiveConfig.deployed_model_id].

                This corresponds to the ``deployed_model_id`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.services.job_service.pagers.SearchModelDeploymentMonitoringStatsAnomaliesAsyncPager:
                Response message for
                   [JobService.SearchModelDeploymentMonitoringStatsAnomalies][google.cloud.aiplatform.v1beta1.JobService.SearchModelDeploymentMonitoringStatsAnomalies].

                Iterating over this object will yield results and
                resolve additional pages automatically.

        """
        # Create or coerce a protobuf request object.
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([model_deployment_monitoring_job, deployed_model_id])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest(
            request
        )

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if model_deployment_monitoring_job is not None:
            request.model_deployment_monitoring_job = model_deployment_monitoring_job
        if deployed_model_id is not None:
            request.deployed_model_id = deployed_model_id

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.search_model_deployment_monitoring_stats_anomalies,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (
                    (
                        "model_deployment_monitoring_job",
                        request.model_deployment_monitoring_job,
                    ),
                )
            ),
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
        response = pagers.SearchModelDeploymentMonitoringStatsAnomaliesAsyncPager(
            method=rpc,
            request=request,
            response=response,
            metadata=metadata,
        )

        # Done; return the response.
        return response

    async def get_model_deployment_monitoring_job(
        self,
        request: Union[job_service.GetModelDeploymentMonitoringJobRequest, dict] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> model_deployment_monitoring_job.ModelDeploymentMonitoringJob:
        r"""Gets a ModelDeploymentMonitoringJob.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_get_model_deployment_monitoring_job():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1beta1.GetModelDeploymentMonitoringJobRequest(
                    name="name_value",
                )

                # Make the request
                response = await client.get_model_deployment_monitoring_job(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.GetModelDeploymentMonitoringJobRequest, dict]):
                The request object. Request message for
                [JobService.GetModelDeploymentMonitoringJob][google.cloud.aiplatform.v1beta1.JobService.GetModelDeploymentMonitoringJob].
            name (:class:`str`):
                Required. The resource name of the
                ModelDeploymentMonitoringJob. Format:
                ``projects/{project}/locations/{location}/modelDeploymentMonitoringJobs/{model_deployment_monitoring_job}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1beta1.types.ModelDeploymentMonitoringJob:
                Represents a job that runs
                periodically to monitor the deployed
                models in an endpoint. It will analyze
                the logged training & prediction data to
                detect any abnormal behaviors.

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

        request = job_service.GetModelDeploymentMonitoringJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_model_deployment_monitoring_job,
            default_timeout=5.0,
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

    async def list_model_deployment_monitoring_jobs(
        self,
        request: Union[
            job_service.ListModelDeploymentMonitoringJobsRequest, dict
        ] = None,
        *,
        parent: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListModelDeploymentMonitoringJobsAsyncPager:
        r"""Lists ModelDeploymentMonitoringJobs in a Location.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_list_model_deployment_monitoring_jobs():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1beta1.ListModelDeploymentMonitoringJobsRequest(
                    parent="parent_value",
                )

                # Make the request
                page_result = client.list_model_deployment_monitoring_jobs(request=request)

                # Handle the response
                async for response in page_result:
                    print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.ListModelDeploymentMonitoringJobsRequest, dict]):
                The request object. Request message for
                [JobService.ListModelDeploymentMonitoringJobs][google.cloud.aiplatform.v1beta1.JobService.ListModelDeploymentMonitoringJobs].
            parent (:class:`str`):
                Required. The parent of the
                ModelDeploymentMonitoringJob. Format:
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
            google.cloud.aiplatform_v1beta1.services.job_service.pagers.ListModelDeploymentMonitoringJobsAsyncPager:
                Response message for
                   [JobService.ListModelDeploymentMonitoringJobs][google.cloud.aiplatform.v1beta1.JobService.ListModelDeploymentMonitoringJobs].

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

        request = job_service.ListModelDeploymentMonitoringJobsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_model_deployment_monitoring_jobs,
            default_timeout=5.0,
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
        response = pagers.ListModelDeploymentMonitoringJobsAsyncPager(
            method=rpc,
            request=request,
            response=response,
            metadata=metadata,
        )

        # Done; return the response.
        return response

    async def update_model_deployment_monitoring_job(
        self,
        request: Union[
            job_service.UpdateModelDeploymentMonitoringJobRequest, dict
        ] = None,
        *,
        model_deployment_monitoring_job: gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob = None,
        update_mask: field_mask_pb2.FieldMask = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Updates a ModelDeploymentMonitoringJob.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_update_model_deployment_monitoring_job():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                model_deployment_monitoring_job = aiplatform_v1beta1.ModelDeploymentMonitoringJob()
                model_deployment_monitoring_job.display_name = "display_name_value"
                model_deployment_monitoring_job.endpoint = "endpoint_value"

                request = aiplatform_v1beta1.UpdateModelDeploymentMonitoringJobRequest(
                    model_deployment_monitoring_job=model_deployment_monitoring_job,
                )

                # Make the request
                operation = client.update_model_deployment_monitoring_job(request=request)

                print("Waiting for operation to complete...")

                response = await operation.result()

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.UpdateModelDeploymentMonitoringJobRequest, dict]):
                The request object. Request message for
                [JobService.UpdateModelDeploymentMonitoringJob][google.cloud.aiplatform.v1beta1.JobService.UpdateModelDeploymentMonitoringJob].
            model_deployment_monitoring_job (:class:`google.cloud.aiplatform_v1beta1.types.ModelDeploymentMonitoringJob`):
                Required. The model monitoring
                configuration which replaces the
                resource on the server.

                This corresponds to the ``model_deployment_monitoring_job`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            update_mask (:class:`google.protobuf.field_mask_pb2.FieldMask`):
                Required. The update mask is used to specify the fields
                to be overwritten in the ModelDeploymentMonitoringJob
                resource by the update. The fields specified in the
                update_mask are relative to the resource, not the full
                request. A field will be overwritten if it is in the
                mask. If the user does not provide a mask then only the
                non-empty fields present in the request will be
                overwritten. Set the update_mask to ``*`` to override
                all fields. For the objective config, the user can
                either provide the update mask for
                model_deployment_monitoring_objective_configs or any
                combination of its nested fields, such as:
                model_deployment_monitoring_objective_configs.objective_config.training_dataset.

                Updatable fields:

                -  ``display_name``
                -  ``model_deployment_monitoring_schedule_config``
                -  ``model_monitoring_alert_config``
                -  ``logging_sampling_strategy``
                -  ``labels``
                -  ``log_ttl``
                -  ``enable_monitoring_pipeline_logs`` . and
                -  ``model_deployment_monitoring_objective_configs`` .
                   or
                -  ``model_deployment_monitoring_objective_configs.objective_config.training_dataset``
                -  ``model_deployment_monitoring_objective_configs.objective_config.training_prediction_skew_detection_config``
                -  ``model_deployment_monitoring_objective_configs.objective_config.prediction_drift_detection_config``

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

                The result type for the operation will be :class:`google.cloud.aiplatform_v1beta1.types.ModelDeploymentMonitoringJob` Represents a job that runs periodically to monitor the deployed models in an
                   endpoint. It will analyze the logged training &
                   prediction data to detect any abnormal behaviors.

        """
        # Create or coerce a protobuf request object.
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([model_deployment_monitoring_job, update_mask])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = job_service.UpdateModelDeploymentMonitoringJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if model_deployment_monitoring_job is not None:
            request.model_deployment_monitoring_job = model_deployment_monitoring_job
        if update_mask is not None:
            request.update_mask = update_mask

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.update_model_deployment_monitoring_job,
            default_timeout=5.0,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (
                    (
                        "model_deployment_monitoring_job.name",
                        request.model_deployment_monitoring_job.name,
                    ),
                )
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
            gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob,
            metadata_type=job_service.UpdateModelDeploymentMonitoringJobOperationMetadata,
        )

        # Done; return the response.
        return response

    async def delete_model_deployment_monitoring_job(
        self,
        request: Union[
            job_service.DeleteModelDeploymentMonitoringJobRequest, dict
        ] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Deletes a ModelDeploymentMonitoringJob.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_delete_model_deployment_monitoring_job():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1beta1.DeleteModelDeploymentMonitoringJobRequest(
                    name="name_value",
                )

                # Make the request
                operation = client.delete_model_deployment_monitoring_job(request=request)

                print("Waiting for operation to complete...")

                response = await operation.result()

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.DeleteModelDeploymentMonitoringJobRequest, dict]):
                The request object. Request message for
                [JobService.DeleteModelDeploymentMonitoringJob][google.cloud.aiplatform.v1beta1.JobService.DeleteModelDeploymentMonitoringJob].
            name (:class:`str`):
                Required. The resource name of the model monitoring job
                to delete. Format:
                ``projects/{project}/locations/{location}/modelDeploymentMonitoringJobs/{model_deployment_monitoring_job}``

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
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([name])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = job_service.DeleteModelDeploymentMonitoringJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.delete_model_deployment_monitoring_job,
            default_timeout=5.0,
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

        # Wrap the response in an operation future.
        response = operation_async.from_gapic(
            response,
            self._client._transport.operations_client,
            empty_pb2.Empty,
            metadata_type=gca_operation.DeleteOperationMetadata,
        )

        # Done; return the response.
        return response

    async def pause_model_deployment_monitoring_job(
        self,
        request: Union[
            job_service.PauseModelDeploymentMonitoringJobRequest, dict
        ] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> None:
        r"""Pauses a ModelDeploymentMonitoringJob. If the job is running,
        the server makes a best effort to cancel the job. Will mark
        [ModelDeploymentMonitoringJob.state][google.cloud.aiplatform.v1beta1.ModelDeploymentMonitoringJob.state]
        to 'PAUSED'.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_pause_model_deployment_monitoring_job():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1beta1.PauseModelDeploymentMonitoringJobRequest(
                    name="name_value",
                )

                # Make the request
                await client.pause_model_deployment_monitoring_job(request=request)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.PauseModelDeploymentMonitoringJobRequest, dict]):
                The request object. Request message for
                [JobService.PauseModelDeploymentMonitoringJob][google.cloud.aiplatform.v1beta1.JobService.PauseModelDeploymentMonitoringJob].
            name (:class:`str`):
                Required. The resource name of the
                ModelDeploymentMonitoringJob to pause. Format:
                ``projects/{project}/locations/{location}/modelDeploymentMonitoringJobs/{model_deployment_monitoring_job}``

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

        request = job_service.PauseModelDeploymentMonitoringJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.pause_model_deployment_monitoring_job,
            default_timeout=5.0,
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

    async def resume_model_deployment_monitoring_job(
        self,
        request: Union[
            job_service.ResumeModelDeploymentMonitoringJobRequest, dict
        ] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> None:
        r"""Resumes a paused ModelDeploymentMonitoringJob. It
        will start to run from next scheduled time. A deleted
        ModelDeploymentMonitoringJob can't be resumed.

        .. code-block:: python

            from google.cloud import aiplatform_v1beta1

            async def sample_resume_model_deployment_monitoring_job():
                # Create a client
                client = aiplatform_v1beta1.JobServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1beta1.ResumeModelDeploymentMonitoringJobRequest(
                    name="name_value",
                )

                # Make the request
                await client.resume_model_deployment_monitoring_job(request=request)

        Args:
            request (Union[google.cloud.aiplatform_v1beta1.types.ResumeModelDeploymentMonitoringJobRequest, dict]):
                The request object. Request message for
                [JobService.ResumeModelDeploymentMonitoringJob][google.cloud.aiplatform.v1beta1.JobService.ResumeModelDeploymentMonitoringJob].
            name (:class:`str`):
                Required. The resource name of the
                ModelDeploymentMonitoringJob to resume. Format:
                ``projects/{project}/locations/{location}/modelDeploymentMonitoringJobs/{model_deployment_monitoring_job}``

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

        request = job_service.ResumeModelDeploymentMonitoringJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.resume_model_deployment_monitoring_job,
            default_timeout=5.0,
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


__all__ = ("JobServiceAsyncClient",)
