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
from google.cloud.aiplatform_v1.services.pipeline_service import pagers
from google.cloud.aiplatform_v1.types import encryption_spec
from google.cloud.aiplatform_v1.types import model
from google.cloud.aiplatform_v1.types import operation as gca_operation
from google.cloud.aiplatform_v1.types import pipeline_job
from google.cloud.aiplatform_v1.types import pipeline_job as gca_pipeline_job
from google.cloud.aiplatform_v1.types import pipeline_service
from google.cloud.aiplatform_v1.types import pipeline_state
from google.cloud.aiplatform_v1.types import training_pipeline
from google.cloud.aiplatform_v1.types import training_pipeline as gca_training_pipeline
from google.protobuf import empty_pb2  # type: ignore
from google.protobuf import struct_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
from google.rpc import status_pb2  # type: ignore
from .transports.base import PipelineServiceTransport, DEFAULT_CLIENT_INFO
from .transports.grpc_asyncio import PipelineServiceGrpcAsyncIOTransport
from .client import PipelineServiceClient


class PipelineServiceAsyncClient:
    """A service for creating and managing Vertex AI's pipelines. This
    includes both ``TrainingPipeline`` resources (used for AutoML and
    custom training) and ``PipelineJob`` resources (used for Vertex
    Pipelines).
    """

    _client: PipelineServiceClient

    DEFAULT_ENDPOINT = PipelineServiceClient.DEFAULT_ENDPOINT
    DEFAULT_MTLS_ENDPOINT = PipelineServiceClient.DEFAULT_MTLS_ENDPOINT

    artifact_path = staticmethod(PipelineServiceClient.artifact_path)
    parse_artifact_path = staticmethod(PipelineServiceClient.parse_artifact_path)
    context_path = staticmethod(PipelineServiceClient.context_path)
    parse_context_path = staticmethod(PipelineServiceClient.parse_context_path)
    custom_job_path = staticmethod(PipelineServiceClient.custom_job_path)
    parse_custom_job_path = staticmethod(PipelineServiceClient.parse_custom_job_path)
    endpoint_path = staticmethod(PipelineServiceClient.endpoint_path)
    parse_endpoint_path = staticmethod(PipelineServiceClient.parse_endpoint_path)
    execution_path = staticmethod(PipelineServiceClient.execution_path)
    parse_execution_path = staticmethod(PipelineServiceClient.parse_execution_path)
    model_path = staticmethod(PipelineServiceClient.model_path)
    parse_model_path = staticmethod(PipelineServiceClient.parse_model_path)
    network_path = staticmethod(PipelineServiceClient.network_path)
    parse_network_path = staticmethod(PipelineServiceClient.parse_network_path)
    pipeline_job_path = staticmethod(PipelineServiceClient.pipeline_job_path)
    parse_pipeline_job_path = staticmethod(
        PipelineServiceClient.parse_pipeline_job_path
    )
    training_pipeline_path = staticmethod(PipelineServiceClient.training_pipeline_path)
    parse_training_pipeline_path = staticmethod(
        PipelineServiceClient.parse_training_pipeline_path
    )
    common_billing_account_path = staticmethod(
        PipelineServiceClient.common_billing_account_path
    )
    parse_common_billing_account_path = staticmethod(
        PipelineServiceClient.parse_common_billing_account_path
    )
    common_folder_path = staticmethod(PipelineServiceClient.common_folder_path)
    parse_common_folder_path = staticmethod(
        PipelineServiceClient.parse_common_folder_path
    )
    common_organization_path = staticmethod(
        PipelineServiceClient.common_organization_path
    )
    parse_common_organization_path = staticmethod(
        PipelineServiceClient.parse_common_organization_path
    )
    common_project_path = staticmethod(PipelineServiceClient.common_project_path)
    parse_common_project_path = staticmethod(
        PipelineServiceClient.parse_common_project_path
    )
    common_location_path = staticmethod(PipelineServiceClient.common_location_path)
    parse_common_location_path = staticmethod(
        PipelineServiceClient.parse_common_location_path
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
            PipelineServiceAsyncClient: The constructed client.
        """
        return PipelineServiceClient.from_service_account_info.__func__(PipelineServiceAsyncClient, info, *args, **kwargs)  # type: ignore

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
            PipelineServiceAsyncClient: The constructed client.
        """
        return PipelineServiceClient.from_service_account_file.__func__(PipelineServiceAsyncClient, filename, *args, **kwargs)  # type: ignore

    from_service_account_json = from_service_account_file

    @property
    def transport(self) -> PipelineServiceTransport:
        """Returns the transport used by the client instance.

        Returns:
            PipelineServiceTransport: The transport used by the client instance.
        """
        return self._client.transport

    get_transport_class = functools.partial(
        type(PipelineServiceClient).get_transport_class, type(PipelineServiceClient)
    )

    def __init__(
        self,
        *,
        credentials: ga_credentials.Credentials = None,
        transport: Union[str, PipelineServiceTransport] = "grpc_asyncio",
        client_options: ClientOptions = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
    ) -> None:
        """Instantiates the pipeline service client.

        Args:
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            transport (Union[str, ~.PipelineServiceTransport]): The
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
        self._client = PipelineServiceClient(
            credentials=credentials,
            transport=transport,
            client_options=client_options,
            client_info=client_info,
        )

    async def create_training_pipeline(
        self,
        request: pipeline_service.CreateTrainingPipelineRequest = None,
        *,
        parent: str = None,
        training_pipeline: gca_training_pipeline.TrainingPipeline = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_training_pipeline.TrainingPipeline:
        r"""Creates a TrainingPipeline. A created
        TrainingPipeline right away will be attempted to be run.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.CreateTrainingPipelineRequest`):
                The request object. Request message for
                [PipelineService.CreateTrainingPipeline][google.cloud.aiplatform.v1.PipelineService.CreateTrainingPipeline].
            parent (:class:`str`):
                Required. The resource name of the Location to create
                the TrainingPipeline in. Format:
                ``projects/{project}/locations/{location}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            training_pipeline (:class:`google.cloud.aiplatform_v1.types.TrainingPipeline`):
                Required. The TrainingPipeline to
                create.

                This corresponds to the ``training_pipeline`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.types.TrainingPipeline:
                The TrainingPipeline orchestrates tasks associated with training a Model. It
                   always executes the training task, and optionally may
                   also export data from Vertex AI's Dataset which
                   becomes the training input,
                   [upload][google.cloud.aiplatform.v1.ModelService.UploadModel]
                   the Model to Vertex AI, and evaluate the Model.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, training_pipeline])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = pipeline_service.CreateTrainingPipelineRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if training_pipeline is not None:
            request.training_pipeline = training_pipeline

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_training_pipeline,
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

    async def get_training_pipeline(
        self,
        request: pipeline_service.GetTrainingPipelineRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> training_pipeline.TrainingPipeline:
        r"""Gets a TrainingPipeline.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.GetTrainingPipelineRequest`):
                The request object. Request message for
                [PipelineService.GetTrainingPipeline][google.cloud.aiplatform.v1.PipelineService.GetTrainingPipeline].
            name (:class:`str`):
                Required. The name of the TrainingPipeline resource.
                Format:
                ``projects/{project}/locations/{location}/trainingPipelines/{training_pipeline}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.types.TrainingPipeline:
                The TrainingPipeline orchestrates tasks associated with training a Model. It
                   always executes the training task, and optionally may
                   also export data from Vertex AI's Dataset which
                   becomes the training input,
                   [upload][google.cloud.aiplatform.v1.ModelService.UploadModel]
                   the Model to Vertex AI, and evaluate the Model.

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

        request = pipeline_service.GetTrainingPipelineRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_training_pipeline,
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

    async def list_training_pipelines(
        self,
        request: pipeline_service.ListTrainingPipelinesRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListTrainingPipelinesAsyncPager:
        r"""Lists TrainingPipelines in a Location.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.ListTrainingPipelinesRequest`):
                The request object. Request message for
                [PipelineService.ListTrainingPipelines][google.cloud.aiplatform.v1.PipelineService.ListTrainingPipelines].
            parent (:class:`str`):
                Required. The resource name of the Location to list the
                TrainingPipelines from. Format:
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
            google.cloud.aiplatform_v1.services.pipeline_service.pagers.ListTrainingPipelinesAsyncPager:
                Response message for
                [PipelineService.ListTrainingPipelines][google.cloud.aiplatform.v1.PipelineService.ListTrainingPipelines]

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

        request = pipeline_service.ListTrainingPipelinesRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_training_pipelines,
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
        response = pagers.ListTrainingPipelinesAsyncPager(
            method=rpc, request=request, response=response, metadata=metadata,
        )

        # Done; return the response.
        return response

    async def delete_training_pipeline(
        self,
        request: pipeline_service.DeleteTrainingPipelineRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Deletes a TrainingPipeline.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.DeleteTrainingPipelineRequest`):
                The request object. Request message for
                [PipelineService.DeleteTrainingPipeline][google.cloud.aiplatform.v1.PipelineService.DeleteTrainingPipeline].
            name (:class:`str`):
                Required. The name of the TrainingPipeline resource to
                be deleted. Format:
                ``projects/{project}/locations/{location}/trainingPipelines/{training_pipeline}``

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

        request = pipeline_service.DeleteTrainingPipelineRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.delete_training_pipeline,
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

    async def cancel_training_pipeline(
        self,
        request: pipeline_service.CancelTrainingPipelineRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> None:
        r"""Cancels a TrainingPipeline. Starts asynchronous cancellation on
        the TrainingPipeline. The server makes a best effort to cancel
        the pipeline, but success is not guaranteed. Clients can use
        [PipelineService.GetTrainingPipeline][google.cloud.aiplatform.v1.PipelineService.GetTrainingPipeline]
        or other methods to check whether the cancellation succeeded or
        whether the pipeline completed despite cancellation. On
        successful cancellation, the TrainingPipeline is not deleted;
        instead it becomes a pipeline with a
        [TrainingPipeline.error][google.cloud.aiplatform.v1.TrainingPipeline.error]
        value with a [google.rpc.Status.code][google.rpc.Status.code] of
        1, corresponding to ``Code.CANCELLED``, and
        [TrainingPipeline.state][google.cloud.aiplatform.v1.TrainingPipeline.state]
        is set to ``CANCELLED``.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.CancelTrainingPipelineRequest`):
                The request object. Request message for
                [PipelineService.CancelTrainingPipeline][google.cloud.aiplatform.v1.PipelineService.CancelTrainingPipeline].
            name (:class:`str`):
                Required. The name of the TrainingPipeline to cancel.
                Format:
                ``projects/{project}/locations/{location}/trainingPipelines/{training_pipeline}``

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
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([name])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = pipeline_service.CancelTrainingPipelineRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.cancel_training_pipeline,
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
            request, retry=retry, timeout=timeout, metadata=metadata,
        )

    async def create_pipeline_job(
        self,
        request: pipeline_service.CreatePipelineJobRequest = None,
        *,
        parent: str = None,
        pipeline_job: gca_pipeline_job.PipelineJob = None,
        pipeline_job_id: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_pipeline_job.PipelineJob:
        r"""Creates a PipelineJob. A PipelineJob will run
        immediately when created.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.CreatePipelineJobRequest`):
                The request object. Request message for
                [PipelineService.CreatePipelineJob][google.cloud.aiplatform.v1.PipelineService.CreatePipelineJob].
            parent (:class:`str`):
                Required. The resource name of the Location to create
                the PipelineJob in. Format:
                ``projects/{project}/locations/{location}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            pipeline_job (:class:`google.cloud.aiplatform_v1.types.PipelineJob`):
                Required. The PipelineJob to create.
                This corresponds to the ``pipeline_job`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            pipeline_job_id (:class:`str`):
                The ID to use for the PipelineJob, which will become the
                final component of the PipelineJob name. If not
                provided, an ID will be automatically generated.

                This value should be less than 128 characters, and valid
                characters are /[a-z][0-9]-/.

                This corresponds to the ``pipeline_job_id`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.types.PipelineJob:
                An instance of a machine learning
                PipelineJob.

        """
        # Create or coerce a protobuf request object.
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, pipeline_job, pipeline_job_id])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = pipeline_service.CreatePipelineJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if pipeline_job is not None:
            request.pipeline_job = pipeline_job
        if pipeline_job_id is not None:
            request.pipeline_job_id = pipeline_job_id

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.create_pipeline_job,
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

    async def get_pipeline_job(
        self,
        request: pipeline_service.GetPipelineJobRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pipeline_job.PipelineJob:
        r"""Gets a PipelineJob.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.GetPipelineJobRequest`):
                The request object. Request message for
                [PipelineService.GetPipelineJob][google.cloud.aiplatform.v1.PipelineService.GetPipelineJob].
            name (:class:`str`):
                Required. The name of the PipelineJob resource. Format:
                ``projects/{project}/locations/{location}/pipelineJobs/{pipeline_job}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.types.PipelineJob:
                An instance of a machine learning
                PipelineJob.

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

        request = pipeline_service.GetPipelineJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_pipeline_job,
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

    async def list_pipeline_jobs(
        self,
        request: pipeline_service.ListPipelineJobsRequest = None,
        *,
        parent: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListPipelineJobsAsyncPager:
        r"""Lists PipelineJobs in a Location.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.ListPipelineJobsRequest`):
                The request object. Request message for
                [PipelineService.ListPipelineJobs][google.cloud.aiplatform.v1.PipelineService.ListPipelineJobs].
            parent (:class:`str`):
                Required. The resource name of the Location to list the
                PipelineJobs from. Format:
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
            google.cloud.aiplatform_v1.services.pipeline_service.pagers.ListPipelineJobsAsyncPager:
                Response message for
                [PipelineService.ListPipelineJobs][google.cloud.aiplatform.v1.PipelineService.ListPipelineJobs]

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

        request = pipeline_service.ListPipelineJobsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_pipeline_jobs,
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
        response = pagers.ListPipelineJobsAsyncPager(
            method=rpc, request=request, response=response, metadata=metadata,
        )

        # Done; return the response.
        return response

    async def delete_pipeline_job(
        self,
        request: pipeline_service.DeletePipelineJobRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Deletes a PipelineJob.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.DeletePipelineJobRequest`):
                The request object. Request message for
                [PipelineService.DeletePipelineJob][google.cloud.aiplatform.v1.PipelineService.DeletePipelineJob].
            name (:class:`str`):
                Required. The name of the PipelineJob resource to be
                deleted. Format:
                ``projects/{project}/locations/{location}/pipelineJobs/{pipeline_job}``

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

        request = pipeline_service.DeletePipelineJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.delete_pipeline_job,
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

    async def cancel_pipeline_job(
        self,
        request: pipeline_service.CancelPipelineJobRequest = None,
        *,
        name: str = None,
        retry: retries.Retry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> None:
        r"""Cancels a PipelineJob. Starts asynchronous cancellation on the
        PipelineJob. The server makes a best effort to cancel the
        pipeline, but success is not guaranteed. Clients can use
        [PipelineService.GetPipelineJob][google.cloud.aiplatform.v1.PipelineService.GetPipelineJob]
        or other methods to check whether the cancellation succeeded or
        whether the pipeline completed despite cancellation. On
        successful cancellation, the PipelineJob is not deleted; instead
        it becomes a pipeline with a
        [PipelineJob.error][google.cloud.aiplatform.v1.PipelineJob.error]
        value with a [google.rpc.Status.code][google.rpc.Status.code] of
        1, corresponding to ``Code.CANCELLED``, and
        [PipelineJob.state][google.cloud.aiplatform.v1.PipelineJob.state]
        is set to ``CANCELLED``.

        Args:
            request (:class:`google.cloud.aiplatform_v1.types.CancelPipelineJobRequest`):
                The request object. Request message for
                [PipelineService.CancelPipelineJob][google.cloud.aiplatform.v1.PipelineService.CancelPipelineJob].
            name (:class:`str`):
                Required. The name of the PipelineJob to cancel. Format:
                ``projects/{project}/locations/{location}/pipelineJobs/{pipeline_job}``

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
        # Sanity check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([name])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = pipeline_service.CancelPipelineJobRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.cancel_pipeline_job,
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
            request, retry=retry, timeout=timeout, metadata=metadata,
        )


try:
    DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo(
        gapic_version=pkg_resources.get_distribution(
            "google-cloud-aiplatform",
        ).version,
    )
except pkg_resources.DistributionNotFound:
    DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo()


__all__ = ("PipelineServiceAsyncClient",)
