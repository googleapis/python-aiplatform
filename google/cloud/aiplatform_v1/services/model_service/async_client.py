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
from google.cloud.aiplatform_v1.services.model_service import pagers
from google.cloud.aiplatform_v1.types import deployed_model_ref
from google.cloud.aiplatform_v1.types import encryption_spec
from google.cloud.aiplatform_v1.types import explanation
from google.cloud.aiplatform_v1.types import model
from google.cloud.aiplatform_v1.types import model as gca_model
from google.cloud.aiplatform_v1.types import model_evaluation
from google.cloud.aiplatform_v1.types import model_evaluation as gca_model_evaluation
from google.cloud.aiplatform_v1.types import model_evaluation_slice
from google.cloud.aiplatform_v1.types import model_service
from google.cloud.aiplatform_v1.types import operation as gca_operation
from google.protobuf import empty_pb2  # type: ignore
from google.protobuf import field_mask_pb2  # type: ignore
from google.protobuf import struct_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
from .transports.base import ModelServiceTransport, DEFAULT_CLIENT_INFO
from .transports.grpc_asyncio import ModelServiceGrpcAsyncIOTransport
from .client import ModelServiceClient


class ModelServiceAsyncClient:
    """A service for managing Vertex AI's machine learning Models."""

    _client: ModelServiceClient

    DEFAULT_ENDPOINT = ModelServiceClient.DEFAULT_ENDPOINT
    DEFAULT_MTLS_ENDPOINT = ModelServiceClient.DEFAULT_MTLS_ENDPOINT

    endpoint_path = staticmethod(ModelServiceClient.endpoint_path)
    parse_endpoint_path = staticmethod(ModelServiceClient.parse_endpoint_path)
    model_path = staticmethod(ModelServiceClient.model_path)
    parse_model_path = staticmethod(ModelServiceClient.parse_model_path)
    model_evaluation_path = staticmethod(ModelServiceClient.model_evaluation_path)
    parse_model_evaluation_path = staticmethod(
        ModelServiceClient.parse_model_evaluation_path
    )
    model_evaluation_slice_path = staticmethod(
        ModelServiceClient.model_evaluation_slice_path
    )
    parse_model_evaluation_slice_path = staticmethod(
        ModelServiceClient.parse_model_evaluation_slice_path
    )
    training_pipeline_path = staticmethod(ModelServiceClient.training_pipeline_path)
    parse_training_pipeline_path = staticmethod(
        ModelServiceClient.parse_training_pipeline_path
    )
    common_billing_account_path = staticmethod(
        ModelServiceClient.common_billing_account_path
    )
    parse_common_billing_account_path = staticmethod(
        ModelServiceClient.parse_common_billing_account_path
    )
    common_folder_path = staticmethod(ModelServiceClient.common_folder_path)
    parse_common_folder_path = staticmethod(ModelServiceClient.parse_common_folder_path)
    common_organization_path = staticmethod(ModelServiceClient.common_organization_path)
    parse_common_organization_path = staticmethod(
        ModelServiceClient.parse_common_organization_path
    )
    common_project_path = staticmethod(ModelServiceClient.common_project_path)
    parse_common_project_path = staticmethod(
        ModelServiceClient.parse_common_project_path
    )
    common_location_path = staticmethod(ModelServiceClient.common_location_path)
    parse_common_location_path = staticmethod(
        ModelServiceClient.parse_common_location_path
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
            ModelServiceAsyncClient: The constructed client.
        """
        return ModelServiceClient.from_service_account_info.__func__(ModelServiceAsyncClient, info, *args, **kwargs)  # type: ignore

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
            ModelServiceAsyncClient: The constructed client.
        """
        return ModelServiceClient.from_service_account_file.__func__(ModelServiceAsyncClient, filename, *args, **kwargs)  # type: ignore

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
        return ModelServiceClient.get_mtls_endpoint_and_cert_source(client_options)  # type: ignore

    @property
    def transport(self) -> ModelServiceTransport:
        """Returns the transport used by the client instance.

        Returns:
            ModelServiceTransport: The transport used by the client instance.
        """
        return self._client.transport

    get_transport_class = functools.partial(
        type(ModelServiceClient).get_transport_class, type(ModelServiceClient)
    )

    def __init__(
        self,
        *,
        credentials: ga_credentials.Credentials = None,
        transport: Union[str, ModelServiceTransport] = "grpc_asyncio",
        client_options: ClientOptions = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
    ) -> None:
        """Instantiates the model service client.

        Args:
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            transport (Union[str, ~.ModelServiceTransport]): The
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
        self._client = ModelServiceClient(
            credentials=credentials,
            transport=transport,
            client_options=client_options,
            client_info=client_info,
        )

    async def upload_model(
        self,
        request: Union[model_service.UploadModelRequest, dict] = None,
        *,
        parent: str = None,
        model: gca_model.Model = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Uploads a Model artifact into Vertex AI.

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_upload_model():
                # Create a client
                client = aiplatform_v1.ModelServiceAsyncClient()

                # Initialize request argument(s)
                model = aiplatform_v1.Model()
                model.display_name = "display_name_value"

                request = aiplatform_v1.UploadModelRequest(
                    parent="parent_value",
                    model=model,
                )

                # Make the request
                operation = client.upload_model(request=request)

                print("Waiting for operation to complete...")

                response = await operation.result()

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.UploadModelRequest, dict]):
                The request object. Request message for
                [ModelService.UploadModel][google.cloud.aiplatform.v1.ModelService.UploadModel].
            parent (:class:`str`):
                Required. The resource name of the Location into which
                to upload the Model. Format:
                ``projects/{project}/locations/{location}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            model (:class:`google.cloud.aiplatform_v1.types.Model`):
                Required. The Model to create.
                This corresponds to the ``model`` field
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

                The result type for the operation will be
                :class:`google.cloud.aiplatform_v1.types.UploadModelResponse`
                Response message of
                [ModelService.UploadModel][google.cloud.aiplatform.v1.ModelService.UploadModel]
                operation.

        """
        # Create or coerce a protobuf request object.
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, model])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = model_service.UploadModelRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if model is not None:
            request.model = model

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.upload_model,
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
            model_service.UploadModelResponse,
            metadata_type=model_service.UploadModelOperationMetadata,
        )

        # Done; return the response.
        return response

    async def get_model(
        self,
        request: Union[model_service.GetModelRequest, dict] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> model.Model:
        r"""Gets a Model.

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_get_model():
                # Create a client
                client = aiplatform_v1.ModelServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.GetModelRequest(
                    name="name_value",
                )

                # Make the request
                response = await client.get_model(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.GetModelRequest, dict]):
                The request object. Request message for
                [ModelService.GetModel][google.cloud.aiplatform.v1.ModelService.GetModel].
            name (:class:`str`):
                Required. The name of the Model resource. Format:
                ``projects/{project}/locations/{location}/models/{model}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.types.Model:
                A trained machine learning Model.
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

        request = model_service.GetModelRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_model,
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

    async def list_models(
        self,
        request: Union[model_service.ListModelsRequest, dict] = None,
        *,
        parent: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListModelsAsyncPager:
        r"""Lists Models in a Location.

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_list_models():
                # Create a client
                client = aiplatform_v1.ModelServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.ListModelsRequest(
                    parent="parent_value",
                )

                # Make the request
                page_result = client.list_models(request=request)

                # Handle the response
                async for response in page_result:
                    print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.ListModelsRequest, dict]):
                The request object. Request message for
                [ModelService.ListModels][google.cloud.aiplatform.v1.ModelService.ListModels].
            parent (:class:`str`):
                Required. The resource name of the Location to list the
                Models from. Format:
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
            google.cloud.aiplatform_v1.services.model_service.pagers.ListModelsAsyncPager:
                Response message for
                [ModelService.ListModels][google.cloud.aiplatform.v1.ModelService.ListModels]

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

        request = model_service.ListModelsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_models,
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
        response = pagers.ListModelsAsyncPager(
            method=rpc,
            request=request,
            response=response,
            metadata=metadata,
        )

        # Done; return the response.
        return response

    async def update_model(
        self,
        request: Union[model_service.UpdateModelRequest, dict] = None,
        *,
        model: gca_model.Model = None,
        update_mask: field_mask_pb2.FieldMask = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_model.Model:
        r"""Updates a Model.

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_update_model():
                # Create a client
                client = aiplatform_v1.ModelServiceAsyncClient()

                # Initialize request argument(s)
                model = aiplatform_v1.Model()
                model.display_name = "display_name_value"

                request = aiplatform_v1.UpdateModelRequest(
                    model=model,
                )

                # Make the request
                response = await client.update_model(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.UpdateModelRequest, dict]):
                The request object. Request message for
                [ModelService.UpdateModel][google.cloud.aiplatform.v1.ModelService.UpdateModel].
            model (:class:`google.cloud.aiplatform_v1.types.Model`):
                Required. The Model which replaces the resource on the
                server. When Model Versioning is enabled, the model.name
                will be used to determine whether to update the model or
                model version.

                1. model.name with the @ value, e.g. models/123@1,
                   refers to a version specific update.
                2. model.name without the @ value, e.g. models/123,
                   refers to a model update.
                3. model.name with @-, e.g. models/123@-, refers to a
                   model update.
                4. Supported model fields: display_name, description;
                   supported version-specific fields:
                   version_description. Labels are supported in both
                   scenarios. Both the model labels and the version
                   labels are merged when a model is returned. When
                   updating labels, if the request is for model-specific
                   update, model label gets updated. Otherwise, version
                   labels get updated.
                5. A model name or model version name fields update
                   mismatch will cause a precondition error.
                6. One request cannot update both the model and the
                   version fields. You must update them separately.

                This corresponds to the ``model`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            update_mask (:class:`google.protobuf.field_mask_pb2.FieldMask`):
                Required. The update mask applies to the resource. For
                the ``FieldMask`` definition, see
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
            google.cloud.aiplatform_v1.types.Model:
                A trained machine learning Model.
        """
        # Create or coerce a protobuf request object.
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([model, update_mask])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = model_service.UpdateModelRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if model is not None:
            request.model = model
        if update_mask is not None:
            request.update_mask = update_mask

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.update_model,
            default_timeout=None,
            client_info=DEFAULT_CLIENT_INFO,
        )

        # Certain fields should be provided within the metadata header;
        # add these here.
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("model.name", request.model.name),)
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

    async def delete_model(
        self,
        request: Union[model_service.DeleteModelRequest, dict] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Deletes a Model.

        A model cannot be deleted if any
        [Endpoint][google.cloud.aiplatform.v1.Endpoint] resource has a
        [DeployedModel][google.cloud.aiplatform.v1.DeployedModel] based
        on the model in its
        [deployed_models][google.cloud.aiplatform.v1.Endpoint.deployed_models]
        field.

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_delete_model():
                # Create a client
                client = aiplatform_v1.ModelServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.DeleteModelRequest(
                    name="name_value",
                )

                # Make the request
                operation = client.delete_model(request=request)

                print("Waiting for operation to complete...")

                response = await operation.result()

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.DeleteModelRequest, dict]):
                The request object. Request message for
                [ModelService.DeleteModel][google.cloud.aiplatform.v1.ModelService.DeleteModel].
            name (:class:`str`):
                Required. The name of the Model resource to be deleted.
                Format:
                ``projects/{project}/locations/{location}/models/{model}``

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

        request = model_service.DeleteModelRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.delete_model,
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

        # Wrap the response in an operation future.
        response = operation_async.from_gapic(
            response,
            self._client._transport.operations_client,
            empty_pb2.Empty,
            metadata_type=gca_operation.DeleteOperationMetadata,
        )

        # Done; return the response.
        return response

    async def export_model(
        self,
        request: Union[model_service.ExportModelRequest, dict] = None,
        *,
        name: str = None,
        output_config: model_service.ExportModelRequest.OutputConfig = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> operation_async.AsyncOperation:
        r"""Exports a trained, exportable Model to a location specified by
        the user. A Model is considered to be exportable if it has at
        least one [supported export
        format][google.cloud.aiplatform.v1.Model.supported_export_formats].

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_export_model():
                # Create a client
                client = aiplatform_v1.ModelServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.ExportModelRequest(
                    name="name_value",
                )

                # Make the request
                operation = client.export_model(request=request)

                print("Waiting for operation to complete...")

                response = await operation.result()

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.ExportModelRequest, dict]):
                The request object. Request message for
                [ModelService.ExportModel][google.cloud.aiplatform.v1.ModelService.ExportModel].
            name (:class:`str`):
                Required. The resource name of the
                Model to export.

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            output_config (:class:`google.cloud.aiplatform_v1.types.ExportModelRequest.OutputConfig`):
                Required. The desired output location
                and configuration.

                This corresponds to the ``output_config`` field
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

                The result type for the operation will be
                :class:`google.cloud.aiplatform_v1.types.ExportModelResponse`
                Response message of
                [ModelService.ExportModel][google.cloud.aiplatform.v1.ModelService.ExportModel]
                operation.

        """
        # Create or coerce a protobuf request object.
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([name, output_config])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = model_service.ExportModelRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name
        if output_config is not None:
            request.output_config = output_config

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.export_model,
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

        # Wrap the response in an operation future.
        response = operation_async.from_gapic(
            response,
            self._client._transport.operations_client,
            model_service.ExportModelResponse,
            metadata_type=model_service.ExportModelOperationMetadata,
        )

        # Done; return the response.
        return response

    async def import_model_evaluation(
        self,
        request: Union[model_service.ImportModelEvaluationRequest, dict] = None,
        *,
        parent: str = None,
        model_evaluation: gca_model_evaluation.ModelEvaluation = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> gca_model_evaluation.ModelEvaluation:
        r"""Imports an externally generated ModelEvaluation.

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_import_model_evaluation():
                # Create a client
                client = aiplatform_v1.ModelServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.ImportModelEvaluationRequest(
                    parent="parent_value",
                )

                # Make the request
                response = await client.import_model_evaluation(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.ImportModelEvaluationRequest, dict]):
                The request object. Request message for
                [ModelService.ImportModelEvaluation][google.cloud.aiplatform.v1.ModelService.ImportModelEvaluation]
            parent (:class:`str`):
                Required. The name of the parent model resource. Format:
                ``projects/{project}/locations/{location}/models/{model}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            model_evaluation (:class:`google.cloud.aiplatform_v1.types.ModelEvaluation`):
                Required. Model evaluation resource
                to be imported.

                This corresponds to the ``model_evaluation`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.types.ModelEvaluation:
                A collection of metrics calculated by
                comparing Model's predictions on all of
                the test data against annotations from
                the test data.

        """
        # Create or coerce a protobuf request object.
        # Quick check: If we got a request object, we should *not* have
        # gotten any keyword arguments that map to the request.
        has_flattened_params = any([parent, model_evaluation])
        if request is not None and has_flattened_params:
            raise ValueError(
                "If the `request` argument is set, then none of "
                "the individual field arguments should be set."
            )

        request = model_service.ImportModelEvaluationRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent
        if model_evaluation is not None:
            request.model_evaluation = model_evaluation

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.import_model_evaluation,
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

    async def get_model_evaluation(
        self,
        request: Union[model_service.GetModelEvaluationRequest, dict] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> model_evaluation.ModelEvaluation:
        r"""Gets a ModelEvaluation.

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_get_model_evaluation():
                # Create a client
                client = aiplatform_v1.ModelServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.GetModelEvaluationRequest(
                    name="name_value",
                )

                # Make the request
                response = await client.get_model_evaluation(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.GetModelEvaluationRequest, dict]):
                The request object. Request message for
                [ModelService.GetModelEvaluation][google.cloud.aiplatform.v1.ModelService.GetModelEvaluation].
            name (:class:`str`):
                Required. The name of the ModelEvaluation resource.
                Format:
                ``projects/{project}/locations/{location}/models/{model}/evaluations/{evaluation}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.types.ModelEvaluation:
                A collection of metrics calculated by
                comparing Model's predictions on all of
                the test data against annotations from
                the test data.

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

        request = model_service.GetModelEvaluationRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_model_evaluation,
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

    async def list_model_evaluations(
        self,
        request: Union[model_service.ListModelEvaluationsRequest, dict] = None,
        *,
        parent: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListModelEvaluationsAsyncPager:
        r"""Lists ModelEvaluations in a Model.

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_list_model_evaluations():
                # Create a client
                client = aiplatform_v1.ModelServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.ListModelEvaluationsRequest(
                    parent="parent_value",
                )

                # Make the request
                page_result = client.list_model_evaluations(request=request)

                # Handle the response
                async for response in page_result:
                    print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.ListModelEvaluationsRequest, dict]):
                The request object. Request message for
                [ModelService.ListModelEvaluations][google.cloud.aiplatform.v1.ModelService.ListModelEvaluations].
            parent (:class:`str`):
                Required. The resource name of the Model to list the
                ModelEvaluations from. Format:
                ``projects/{project}/locations/{location}/models/{model}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.services.model_service.pagers.ListModelEvaluationsAsyncPager:
                Response message for
                [ModelService.ListModelEvaluations][google.cloud.aiplatform.v1.ModelService.ListModelEvaluations].

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

        request = model_service.ListModelEvaluationsRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_model_evaluations,
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
        response = pagers.ListModelEvaluationsAsyncPager(
            method=rpc,
            request=request,
            response=response,
            metadata=metadata,
        )

        # Done; return the response.
        return response

    async def get_model_evaluation_slice(
        self,
        request: Union[model_service.GetModelEvaluationSliceRequest, dict] = None,
        *,
        name: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> model_evaluation_slice.ModelEvaluationSlice:
        r"""Gets a ModelEvaluationSlice.

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_get_model_evaluation_slice():
                # Create a client
                client = aiplatform_v1.ModelServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.GetModelEvaluationSliceRequest(
                    name="name_value",
                )

                # Make the request
                response = await client.get_model_evaluation_slice(request=request)

                # Handle the response
                print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.GetModelEvaluationSliceRequest, dict]):
                The request object. Request message for
                [ModelService.GetModelEvaluationSlice][google.cloud.aiplatform.v1.ModelService.GetModelEvaluationSlice].
            name (:class:`str`):
                Required. The name of the ModelEvaluationSlice resource.
                Format:
                ``projects/{project}/locations/{location}/models/{model}/evaluations/{evaluation}/slices/{slice}``

                This corresponds to the ``name`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.types.ModelEvaluationSlice:
                A collection of metrics calculated by
                comparing Model's predictions on a slice
                of the test data against ground truth
                annotations.

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

        request = model_service.GetModelEvaluationSliceRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if name is not None:
            request.name = name

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.get_model_evaluation_slice,
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

    async def list_model_evaluation_slices(
        self,
        request: Union[model_service.ListModelEvaluationSlicesRequest, dict] = None,
        *,
        parent: str = None,
        retry: OptionalRetry = gapic_v1.method.DEFAULT,
        timeout: float = None,
        metadata: Sequence[Tuple[str, str]] = (),
    ) -> pagers.ListModelEvaluationSlicesAsyncPager:
        r"""Lists ModelEvaluationSlices in a ModelEvaluation.

        .. code-block:: python

            from google.cloud import aiplatform_v1

            async def sample_list_model_evaluation_slices():
                # Create a client
                client = aiplatform_v1.ModelServiceAsyncClient()

                # Initialize request argument(s)
                request = aiplatform_v1.ListModelEvaluationSlicesRequest(
                    parent="parent_value",
                )

                # Make the request
                page_result = client.list_model_evaluation_slices(request=request)

                # Handle the response
                async for response in page_result:
                    print(response)

        Args:
            request (Union[google.cloud.aiplatform_v1.types.ListModelEvaluationSlicesRequest, dict]):
                The request object. Request message for
                [ModelService.ListModelEvaluationSlices][google.cloud.aiplatform.v1.ModelService.ListModelEvaluationSlices].
            parent (:class:`str`):
                Required. The resource name of the ModelEvaluation to
                list the ModelEvaluationSlices from. Format:
                ``projects/{project}/locations/{location}/models/{model}/evaluations/{evaluation}``

                This corresponds to the ``parent`` field
                on the ``request`` instance; if ``request`` is provided, this
                should not be set.
            retry (google.api_core.retry.Retry): Designation of what errors, if any,
                should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.

        Returns:
            google.cloud.aiplatform_v1.services.model_service.pagers.ListModelEvaluationSlicesAsyncPager:
                Response message for
                [ModelService.ListModelEvaluationSlices][google.cloud.aiplatform.v1.ModelService.ListModelEvaluationSlices].

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

        request = model_service.ListModelEvaluationSlicesRequest(request)

        # If we have keyword arguments corresponding to fields on the
        # request, apply these.
        if parent is not None:
            request.parent = parent

        # Wrap the RPC method; this adds retry and timeout information,
        # and friendly error handling.
        rpc = gapic_v1.method_async.wrap_method(
            self._client._transport.list_model_evaluation_slices,
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
        response = pagers.ListModelEvaluationSlicesAsyncPager(
            method=rpc,
            request=request,
            response=response,
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


__all__ = ("ModelServiceAsyncClient",)
