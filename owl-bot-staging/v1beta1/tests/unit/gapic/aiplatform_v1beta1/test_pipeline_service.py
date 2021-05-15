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

import os
import mock

import grpc
from grpc.experimental import aio
import math
import pytest
from proto.marshal.rules.dates import DurationRule, TimestampRule

from google import auth
from google.api_core import client_options
from google.api_core import exceptions
from google.api_core import future
from google.api_core import gapic_v1
from google.api_core import grpc_helpers
from google.api_core import grpc_helpers_async
from google.api_core import operation_async  # type: ignore
from google.api_core import operations_v1
from google.auth import credentials
from google.auth.exceptions import MutualTLSChannelError
from google.cloud.aiplatform_v1beta1.services.pipeline_service import PipelineServiceAsyncClient
from google.cloud.aiplatform_v1beta1.services.pipeline_service import PipelineServiceClient
from google.cloud.aiplatform_v1beta1.services.pipeline_service import pagers
from google.cloud.aiplatform_v1beta1.services.pipeline_service import transports
from google.cloud.aiplatform_v1beta1.types import deployed_model_ref
from google.cloud.aiplatform_v1beta1.types import encryption_spec
from google.cloud.aiplatform_v1beta1.types import env_var
from google.cloud.aiplatform_v1beta1.types import explanation
from google.cloud.aiplatform_v1beta1.types import explanation_metadata
from google.cloud.aiplatform_v1beta1.types import io
from google.cloud.aiplatform_v1beta1.types import model
from google.cloud.aiplatform_v1beta1.types import operation as gca_operation
from google.cloud.aiplatform_v1beta1.types import pipeline_service
from google.cloud.aiplatform_v1beta1.types import pipeline_state
from google.cloud.aiplatform_v1beta1.types import training_pipeline
from google.cloud.aiplatform_v1beta1.types import training_pipeline as gca_training_pipeline
from google.longrunning import operations_pb2
from google.oauth2 import service_account
from google.protobuf import any_pb2 as gp_any  # type: ignore
from google.protobuf import field_mask_pb2 as field_mask  # type: ignore
from google.protobuf import struct_pb2 as struct  # type: ignore
from google.protobuf import timestamp_pb2 as timestamp  # type: ignore
from google.rpc import status_pb2 as status  # type: ignore


def client_cert_source_callback():
    return b"cert bytes", b"key bytes"


# If default endpoint is localhost, then default mtls endpoint will be the same.
# This method modifies the default endpoint so the client can produce a different
# mtls endpoint for endpoint testing purposes.
def modify_default_endpoint(client):
    return "foo.googleapis.com" if ("localhost" in client.DEFAULT_ENDPOINT) else client.DEFAULT_ENDPOINT


def test__get_default_mtls_endpoint():
    api_endpoint = "example.googleapis.com"
    api_mtls_endpoint = "example.mtls.googleapis.com"
    sandbox_endpoint = "example.sandbox.googleapis.com"
    sandbox_mtls_endpoint = "example.mtls.sandbox.googleapis.com"
    non_googleapi = "api.example.com"

    assert PipelineServiceClient._get_default_mtls_endpoint(None) is None
    assert PipelineServiceClient._get_default_mtls_endpoint(api_endpoint) == api_mtls_endpoint
    assert PipelineServiceClient._get_default_mtls_endpoint(api_mtls_endpoint) == api_mtls_endpoint
    assert PipelineServiceClient._get_default_mtls_endpoint(sandbox_endpoint) == sandbox_mtls_endpoint
    assert PipelineServiceClient._get_default_mtls_endpoint(sandbox_mtls_endpoint) == sandbox_mtls_endpoint
    assert PipelineServiceClient._get_default_mtls_endpoint(non_googleapi) == non_googleapi


def test_pipeline_service_client_from_service_account_info():
    creds = credentials.AnonymousCredentials()
    with mock.patch.object(service_account.Credentials, 'from_service_account_info') as factory:
        factory.return_value = creds
        info = {"valid": True}
        client = PipelineServiceClient.from_service_account_info(info)
        assert client.transport._credentials == creds

        assert client.transport._host == 'aiplatform.googleapis.com:443'


@pytest.mark.parametrize("client_class", [
    PipelineServiceClient,
    PipelineServiceAsyncClient,
])
def test_pipeline_service_client_from_service_account_file(client_class):
    creds = credentials.AnonymousCredentials()
    with mock.patch.object(service_account.Credentials, 'from_service_account_file') as factory:
        factory.return_value = creds
        client = client_class.from_service_account_file("dummy/file/path.json")
        assert client.transport._credentials == creds

        client = client_class.from_service_account_json("dummy/file/path.json")
        assert client.transport._credentials == creds

        assert client.transport._host == 'aiplatform.googleapis.com:443'


def test_pipeline_service_client_get_transport_class():
    transport = PipelineServiceClient.get_transport_class()
    available_transports = [
        transports.PipelineServiceGrpcTransport,
    ]
    assert transport in available_transports

    transport = PipelineServiceClient.get_transport_class("grpc")
    assert transport == transports.PipelineServiceGrpcTransport


@pytest.mark.parametrize("client_class,transport_class,transport_name", [
    (PipelineServiceClient, transports.PipelineServiceGrpcTransport, "grpc"),
    (PipelineServiceAsyncClient, transports.PipelineServiceGrpcAsyncIOTransport, "grpc_asyncio"),
])
@mock.patch.object(PipelineServiceClient, "DEFAULT_ENDPOINT", modify_default_endpoint(PipelineServiceClient))
@mock.patch.object(PipelineServiceAsyncClient, "DEFAULT_ENDPOINT", modify_default_endpoint(PipelineServiceAsyncClient))
def test_pipeline_service_client_client_options(client_class, transport_class, transport_name):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(PipelineServiceClient, 'get_transport_class') as gtc:
        transport = transport_class(
            credentials=credentials.AnonymousCredentials()
        )
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(PipelineServiceClient, 'get_transport_class') as gtc:
        client = client_class(transport=transport_name)
        gtc.assert_called()

    # Check the case api_endpoint is provided.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch.object(transport_class, '__init__') as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "never".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        with mock.patch.object(transport_class, '__init__') as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_ENDPOINT,
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "always".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        with mock.patch.object(transport_class, '__init__') as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT has
    # unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError):
            client = client_class()

    # Check the case GOOGLE_API_USE_CLIENT_CERTIFICATE has unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}):
        with pytest.raises(ValueError):
            client = client_class()

    # Check the case quota_project_id is provided
    options = client_options.ClientOptions(quota_project_id="octopus")
    with mock.patch.object(transport_class, '__init__') as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id="octopus",
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )

@pytest.mark.parametrize("client_class,transport_class,transport_name,use_client_cert_env", [

    (PipelineServiceClient, transports.PipelineServiceGrpcTransport, "grpc", "true"),
    (PipelineServiceAsyncClient, transports.PipelineServiceGrpcAsyncIOTransport, "grpc_asyncio", "true"),
    (PipelineServiceClient, transports.PipelineServiceGrpcTransport, "grpc", "false"),
    (PipelineServiceAsyncClient, transports.PipelineServiceGrpcAsyncIOTransport, "grpc_asyncio", "false"),

])
@mock.patch.object(PipelineServiceClient, "DEFAULT_ENDPOINT", modify_default_endpoint(PipelineServiceClient))
@mock.patch.object(PipelineServiceAsyncClient, "DEFAULT_ENDPOINT", modify_default_endpoint(PipelineServiceAsyncClient))
@mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"})
def test_pipeline_service_client_mtls_env_auto(client_class, transport_class, transport_name, use_client_cert_env):
    # This tests the endpoint autoswitch behavior. Endpoint is autoswitched to the default
    # mtls endpoint, if GOOGLE_API_USE_CLIENT_CERTIFICATE is "true" and client cert exists.

    # Check the case client_cert_source is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}):
        options = client_options.ClientOptions(client_cert_source=client_cert_source_callback)
        with mock.patch.object(transport_class, '__init__') as patched:
            patched.return_value = None
            client = client_class(client_options=options)

            if use_client_cert_env == "false":
                expected_client_cert_source = None
                expected_host = client.DEFAULT_ENDPOINT
            else:
                expected_client_cert_source = client_cert_source_callback
                expected_host = client.DEFAULT_MTLS_ENDPOINT

            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=expected_host,
                scopes=None,
                client_cert_source_for_mtls=expected_client_cert_source,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case ADC client cert is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}):
        with mock.patch.object(transport_class, '__init__') as patched:
            with mock.patch('google.auth.transport.mtls.has_default_client_cert_source', return_value=True):
                with mock.patch('google.auth.transport.mtls.default_client_cert_source', return_value=client_cert_source_callback):
                    if use_client_cert_env == "false":
                        expected_host = client.DEFAULT_ENDPOINT
                        expected_client_cert_source = None
                    else:
                        expected_host = client.DEFAULT_MTLS_ENDPOINT
                        expected_client_cert_source = client_cert_source_callback

                    patched.return_value = None
                    client = client_class()
                    patched.assert_called_once_with(
                        credentials=None,
                        credentials_file=None,
                        host=expected_host,
                        scopes=None,
                        client_cert_source_for_mtls=expected_client_cert_source,
                        quota_project_id=None,
                        client_info=transports.base.DEFAULT_CLIENT_INFO,
                    )

    # Check the case client_cert_source and ADC client cert are not provided.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}):
        with mock.patch.object(transport_class, '__init__') as patched:
            with mock.patch("google.auth.transport.mtls.has_default_client_cert_source", return_value=False):
                patched.return_value = None
                client = client_class()
                patched.assert_called_once_with(
                    credentials=None,
                    credentials_file=None,
                    host=client.DEFAULT_ENDPOINT,
                    scopes=None,
                    client_cert_source_for_mtls=None,
                    quota_project_id=None,
                    client_info=transports.base.DEFAULT_CLIENT_INFO,
                )


@pytest.mark.parametrize("client_class,transport_class,transport_name", [
    (PipelineServiceClient, transports.PipelineServiceGrpcTransport, "grpc"),
    (PipelineServiceAsyncClient, transports.PipelineServiceGrpcAsyncIOTransport, "grpc_asyncio"),
])
def test_pipeline_service_client_client_options_scopes(client_class, transport_class, transport_name):
    # Check the case scopes are provided.
    options = client_options.ClientOptions(
        scopes=["1", "2"],
    )
    with mock.patch.object(transport_class, '__init__') as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=["1", "2"],
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )

@pytest.mark.parametrize("client_class,transport_class,transport_name", [
    (PipelineServiceClient, transports.PipelineServiceGrpcTransport, "grpc"),
    (PipelineServiceAsyncClient, transports.PipelineServiceGrpcAsyncIOTransport, "grpc_asyncio"),
])
def test_pipeline_service_client_client_options_credentials_file(client_class, transport_class, transport_name):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(
        credentials_file="credentials.json"
    )
    with mock.patch.object(transport_class, '__init__') as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


def test_pipeline_service_client_client_options_from_dict():
    with mock.patch('google.cloud.aiplatform_v1beta1.services.pipeline_service.transports.PipelineServiceGrpcTransport.__init__') as grpc_transport:
        grpc_transport.return_value = None
        client = PipelineServiceClient(
            client_options={'api_endpoint': 'squid.clam.whelk'}
        )
        grpc_transport.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


def test_create_training_pipeline(transport: str = 'grpc', request_type=pipeline_service.CreateTrainingPipelineRequest):
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_training_pipeline),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_training_pipeline.TrainingPipeline(
            name='name_value',

            display_name='display_name_value',

            training_task_definition='training_task_definition_value',

            state=pipeline_state.PipelineState.PIPELINE_STATE_QUEUED,

        )

        response = client.create_training_pipeline(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == pipeline_service.CreateTrainingPipelineRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, gca_training_pipeline.TrainingPipeline)

    assert response.name == 'name_value'

    assert response.display_name == 'display_name_value'

    assert response.training_task_definition == 'training_task_definition_value'

    assert response.state == pipeline_state.PipelineState.PIPELINE_STATE_QUEUED


def test_create_training_pipeline_from_dict():
    test_create_training_pipeline(request_type=dict)


@pytest.mark.asyncio
async def test_create_training_pipeline_async(transport: str = 'grpc_asyncio', request_type=pipeline_service.CreateTrainingPipelineRequest):
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_training_pipeline),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gca_training_pipeline.TrainingPipeline(
            name='name_value',
            display_name='display_name_value',
            training_task_definition='training_task_definition_value',
            state=pipeline_state.PipelineState.PIPELINE_STATE_QUEUED,
        ))

        response = await client.create_training_pipeline(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == pipeline_service.CreateTrainingPipelineRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_training_pipeline.TrainingPipeline)

    assert response.name == 'name_value'

    assert response.display_name == 'display_name_value'

    assert response.training_task_definition == 'training_task_definition_value'

    assert response.state == pipeline_state.PipelineState.PIPELINE_STATE_QUEUED


@pytest.mark.asyncio
async def test_create_training_pipeline_async_from_dict():
    await test_create_training_pipeline_async(request_type=dict)


def test_create_training_pipeline_field_headers():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = pipeline_service.CreateTrainingPipelineRequest()
    request.parent = 'parent/value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_training_pipeline),
            '__call__') as call:
        call.return_value = gca_training_pipeline.TrainingPipeline()

        client.create_training_pipeline(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent/value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_create_training_pipeline_field_headers_async():
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = pipeline_service.CreateTrainingPipelineRequest()
    request.parent = 'parent/value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_training_pipeline),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gca_training_pipeline.TrainingPipeline())

        await client.create_training_pipeline(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent/value',
    ) in kw['metadata']


def test_create_training_pipeline_flattened():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_training_pipeline),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_training_pipeline.TrainingPipeline()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_training_pipeline(
            parent='parent_value',
            training_pipeline=gca_training_pipeline.TrainingPipeline(name='name_value'),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == 'parent_value'

        assert args[0].training_pipeline == gca_training_pipeline.TrainingPipeline(name='name_value')


def test_create_training_pipeline_flattened_error():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_training_pipeline(
            pipeline_service.CreateTrainingPipelineRequest(),
            parent='parent_value',
            training_pipeline=gca_training_pipeline.TrainingPipeline(name='name_value'),
        )


@pytest.mark.asyncio
async def test_create_training_pipeline_flattened_async():
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_training_pipeline),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_training_pipeline.TrainingPipeline()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gca_training_pipeline.TrainingPipeline())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_training_pipeline(
            parent='parent_value',
            training_pipeline=gca_training_pipeline.TrainingPipeline(name='name_value'),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == 'parent_value'

        assert args[0].training_pipeline == gca_training_pipeline.TrainingPipeline(name='name_value')


@pytest.mark.asyncio
async def test_create_training_pipeline_flattened_error_async():
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_training_pipeline(
            pipeline_service.CreateTrainingPipelineRequest(),
            parent='parent_value',
            training_pipeline=gca_training_pipeline.TrainingPipeline(name='name_value'),
        )


def test_get_training_pipeline(transport: str = 'grpc', request_type=pipeline_service.GetTrainingPipelineRequest):
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_training_pipeline),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = training_pipeline.TrainingPipeline(
            name='name_value',

            display_name='display_name_value',

            training_task_definition='training_task_definition_value',

            state=pipeline_state.PipelineState.PIPELINE_STATE_QUEUED,

        )

        response = client.get_training_pipeline(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == pipeline_service.GetTrainingPipelineRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, training_pipeline.TrainingPipeline)

    assert response.name == 'name_value'

    assert response.display_name == 'display_name_value'

    assert response.training_task_definition == 'training_task_definition_value'

    assert response.state == pipeline_state.PipelineState.PIPELINE_STATE_QUEUED


def test_get_training_pipeline_from_dict():
    test_get_training_pipeline(request_type=dict)


@pytest.mark.asyncio
async def test_get_training_pipeline_async(transport: str = 'grpc_asyncio', request_type=pipeline_service.GetTrainingPipelineRequest):
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_training_pipeline),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(training_pipeline.TrainingPipeline(
            name='name_value',
            display_name='display_name_value',
            training_task_definition='training_task_definition_value',
            state=pipeline_state.PipelineState.PIPELINE_STATE_QUEUED,
        ))

        response = await client.get_training_pipeline(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == pipeline_service.GetTrainingPipelineRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, training_pipeline.TrainingPipeline)

    assert response.name == 'name_value'

    assert response.display_name == 'display_name_value'

    assert response.training_task_definition == 'training_task_definition_value'

    assert response.state == pipeline_state.PipelineState.PIPELINE_STATE_QUEUED


@pytest.mark.asyncio
async def test_get_training_pipeline_async_from_dict():
    await test_get_training_pipeline_async(request_type=dict)


def test_get_training_pipeline_field_headers():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = pipeline_service.GetTrainingPipelineRequest()
    request.name = 'name/value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_training_pipeline),
            '__call__') as call:
        call.return_value = training_pipeline.TrainingPipeline()

        client.get_training_pipeline(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name/value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_get_training_pipeline_field_headers_async():
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = pipeline_service.GetTrainingPipelineRequest()
    request.name = 'name/value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_training_pipeline),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(training_pipeline.TrainingPipeline())

        await client.get_training_pipeline(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name/value',
    ) in kw['metadata']


def test_get_training_pipeline_flattened():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_training_pipeline),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = training_pipeline.TrainingPipeline()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_training_pipeline(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == 'name_value'


def test_get_training_pipeline_flattened_error():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_training_pipeline(
            pipeline_service.GetTrainingPipelineRequest(),
            name='name_value',
        )


@pytest.mark.asyncio
async def test_get_training_pipeline_flattened_async():
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_training_pipeline),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = training_pipeline.TrainingPipeline()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(training_pipeline.TrainingPipeline())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_training_pipeline(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == 'name_value'


@pytest.mark.asyncio
async def test_get_training_pipeline_flattened_error_async():
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_training_pipeline(
            pipeline_service.GetTrainingPipelineRequest(),
            name='name_value',
        )


def test_list_training_pipelines(transport: str = 'grpc', request_type=pipeline_service.ListTrainingPipelinesRequest):
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_training_pipelines),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = pipeline_service.ListTrainingPipelinesResponse(
            next_page_token='next_page_token_value',

        )

        response = client.list_training_pipelines(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == pipeline_service.ListTrainingPipelinesRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, pagers.ListTrainingPipelinesPager)

    assert response.next_page_token == 'next_page_token_value'


def test_list_training_pipelines_from_dict():
    test_list_training_pipelines(request_type=dict)


@pytest.mark.asyncio
async def test_list_training_pipelines_async(transport: str = 'grpc_asyncio', request_type=pipeline_service.ListTrainingPipelinesRequest):
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_training_pipelines),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(pipeline_service.ListTrainingPipelinesResponse(
            next_page_token='next_page_token_value',
        ))

        response = await client.list_training_pipelines(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == pipeline_service.ListTrainingPipelinesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListTrainingPipelinesAsyncPager)

    assert response.next_page_token == 'next_page_token_value'


@pytest.mark.asyncio
async def test_list_training_pipelines_async_from_dict():
    await test_list_training_pipelines_async(request_type=dict)


def test_list_training_pipelines_field_headers():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = pipeline_service.ListTrainingPipelinesRequest()
    request.parent = 'parent/value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_training_pipelines),
            '__call__') as call:
        call.return_value = pipeline_service.ListTrainingPipelinesResponse()

        client.list_training_pipelines(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent/value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_list_training_pipelines_field_headers_async():
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = pipeline_service.ListTrainingPipelinesRequest()
    request.parent = 'parent/value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_training_pipelines),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(pipeline_service.ListTrainingPipelinesResponse())

        await client.list_training_pipelines(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent/value',
    ) in kw['metadata']


def test_list_training_pipelines_flattened():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_training_pipelines),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = pipeline_service.ListTrainingPipelinesResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_training_pipelines(
            parent='parent_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == 'parent_value'


def test_list_training_pipelines_flattened_error():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_training_pipelines(
            pipeline_service.ListTrainingPipelinesRequest(),
            parent='parent_value',
        )


@pytest.mark.asyncio
async def test_list_training_pipelines_flattened_async():
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_training_pipelines),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = pipeline_service.ListTrainingPipelinesResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(pipeline_service.ListTrainingPipelinesResponse())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_training_pipelines(
            parent='parent_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == 'parent_value'


@pytest.mark.asyncio
async def test_list_training_pipelines_flattened_error_async():
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_training_pipelines(
            pipeline_service.ListTrainingPipelinesRequest(),
            parent='parent_value',
        )


def test_list_training_pipelines_pager():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_training_pipelines),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[
                    training_pipeline.TrainingPipeline(),
                    training_pipeline.TrainingPipeline(),
                    training_pipeline.TrainingPipeline(),
                ],
                next_page_token='abc',
            ),
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[],
                next_page_token='def',
            ),
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[
                    training_pipeline.TrainingPipeline(),
                ],
                next_page_token='ghi',
            ),
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[
                    training_pipeline.TrainingPipeline(),
                    training_pipeline.TrainingPipeline(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((
                ('parent', ''),
            )),
        )
        pager = client.list_training_pipelines(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, training_pipeline.TrainingPipeline)
                   for i in results)

def test_list_training_pipelines_pages():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_training_pipelines),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[
                    training_pipeline.TrainingPipeline(),
                    training_pipeline.TrainingPipeline(),
                    training_pipeline.TrainingPipeline(),
                ],
                next_page_token='abc',
            ),
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[],
                next_page_token='def',
            ),
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[
                    training_pipeline.TrainingPipeline(),
                ],
                next_page_token='ghi',
            ),
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[
                    training_pipeline.TrainingPipeline(),
                    training_pipeline.TrainingPipeline(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_training_pipelines(request={}).pages)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token

@pytest.mark.asyncio
async def test_list_training_pipelines_async_pager():
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_training_pipelines),
            '__call__', new_callable=mock.AsyncMock) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[
                    training_pipeline.TrainingPipeline(),
                    training_pipeline.TrainingPipeline(),
                    training_pipeline.TrainingPipeline(),
                ],
                next_page_token='abc',
            ),
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[],
                next_page_token='def',
            ),
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[
                    training_pipeline.TrainingPipeline(),
                ],
                next_page_token='ghi',
            ),
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[
                    training_pipeline.TrainingPipeline(),
                    training_pipeline.TrainingPipeline(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_training_pipelines(request={},)
        assert async_pager.next_page_token == 'abc'
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, training_pipeline.TrainingPipeline)
                   for i in responses)

@pytest.mark.asyncio
async def test_list_training_pipelines_async_pages():
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_training_pipelines),
            '__call__', new_callable=mock.AsyncMock) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[
                    training_pipeline.TrainingPipeline(),
                    training_pipeline.TrainingPipeline(),
                    training_pipeline.TrainingPipeline(),
                ],
                next_page_token='abc',
            ),
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[],
                next_page_token='def',
            ),
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[
                    training_pipeline.TrainingPipeline(),
                ],
                next_page_token='ghi',
            ),
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[
                    training_pipeline.TrainingPipeline(),
                    training_pipeline.TrainingPipeline(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_training_pipelines(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token


def test_delete_training_pipeline(transport: str = 'grpc', request_type=pipeline_service.DeleteTrainingPipelineRequest):
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_training_pipeline),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/spam')

        response = client.delete_training_pipeline(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == pipeline_service.DeleteTrainingPipelineRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_training_pipeline_from_dict():
    test_delete_training_pipeline(request_type=dict)


@pytest.mark.asyncio
async def test_delete_training_pipeline_async(transport: str = 'grpc_asyncio', request_type=pipeline_service.DeleteTrainingPipelineRequest):
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_training_pipeline),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name='operations/spam')
        )

        response = await client.delete_training_pipeline(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == pipeline_service.DeleteTrainingPipelineRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_training_pipeline_async_from_dict():
    await test_delete_training_pipeline_async(request_type=dict)


def test_delete_training_pipeline_field_headers():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = pipeline_service.DeleteTrainingPipelineRequest()
    request.name = 'name/value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_training_pipeline),
            '__call__') as call:
        call.return_value = operations_pb2.Operation(name='operations/op')

        client.delete_training_pipeline(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name/value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_delete_training_pipeline_field_headers_async():
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = pipeline_service.DeleteTrainingPipelineRequest()
    request.name = 'name/value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_training_pipeline),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(operations_pb2.Operation(name='operations/op'))

        await client.delete_training_pipeline(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name/value',
    ) in kw['metadata']


def test_delete_training_pipeline_flattened():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_training_pipeline),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/op')

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_training_pipeline(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == 'name_value'


def test_delete_training_pipeline_flattened_error():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_training_pipeline(
            pipeline_service.DeleteTrainingPipelineRequest(),
            name='name_value',
        )


@pytest.mark.asyncio
async def test_delete_training_pipeline_flattened_async():
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_training_pipeline),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/op')

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name='operations/spam')
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_training_pipeline(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == 'name_value'


@pytest.mark.asyncio
async def test_delete_training_pipeline_flattened_error_async():
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_training_pipeline(
            pipeline_service.DeleteTrainingPipelineRequest(),
            name='name_value',
        )


def test_cancel_training_pipeline(transport: str = 'grpc', request_type=pipeline_service.CancelTrainingPipelineRequest):
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.cancel_training_pipeline),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.cancel_training_pipeline(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == pipeline_service.CancelTrainingPipelineRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_cancel_training_pipeline_from_dict():
    test_cancel_training_pipeline(request_type=dict)


@pytest.mark.asyncio
async def test_cancel_training_pipeline_async(transport: str = 'grpc_asyncio', request_type=pipeline_service.CancelTrainingPipelineRequest):
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.cancel_training_pipeline),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        response = await client.cancel_training_pipeline(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == pipeline_service.CancelTrainingPipelineRequest()

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_cancel_training_pipeline_async_from_dict():
    await test_cancel_training_pipeline_async(request_type=dict)


def test_cancel_training_pipeline_field_headers():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = pipeline_service.CancelTrainingPipelineRequest()
    request.name = 'name/value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.cancel_training_pipeline),
            '__call__') as call:
        call.return_value = None

        client.cancel_training_pipeline(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name/value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_cancel_training_pipeline_field_headers_async():
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = pipeline_service.CancelTrainingPipelineRequest()
    request.name = 'name/value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.cancel_training_pipeline),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        await client.cancel_training_pipeline(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name/value',
    ) in kw['metadata']


def test_cancel_training_pipeline_flattened():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.cancel_training_pipeline),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.cancel_training_pipeline(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == 'name_value'


def test_cancel_training_pipeline_flattened_error():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.cancel_training_pipeline(
            pipeline_service.CancelTrainingPipelineRequest(),
            name='name_value',
        )


@pytest.mark.asyncio
async def test_cancel_training_pipeline_flattened_async():
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.cancel_training_pipeline),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.cancel_training_pipeline(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == 'name_value'


@pytest.mark.asyncio
async def test_cancel_training_pipeline_flattened_error_async():
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.cancel_training_pipeline(
            pipeline_service.CancelTrainingPipelineRequest(),
            name='name_value',
        )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.PipelineServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = PipelineServiceClient(
            credentials=credentials.AnonymousCredentials(),
            transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.PipelineServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = PipelineServiceClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.PipelineServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = PipelineServiceClient(
            client_options={"scopes": ["1", "2"]},
            transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.PipelineServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    client = PipelineServiceClient(transport=transport)
    assert client.transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.PipelineServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.PipelineServiceGrpcAsyncIOTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


@pytest.mark.parametrize("transport_class", [
    transports.PipelineServiceGrpcTransport,
    transports.PipelineServiceGrpcAsyncIOTransport,
])
def test_transport_adc(transport_class):
    # Test default credentials are used if not provided.
    with mock.patch.object(auth, 'default') as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transport_class()
        adc.assert_called_once()


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )
    assert isinstance(
        client.transport,
        transports.PipelineServiceGrpcTransport,
    )


def test_pipeline_service_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(exceptions.DuplicateCredentialArgs):
        transport = transports.PipelineServiceTransport(
            credentials=credentials.AnonymousCredentials(),
            credentials_file="credentials.json"
        )


def test_pipeline_service_base_transport():
    # Instantiate the base transport.
    with mock.patch('google.cloud.aiplatform_v1beta1.services.pipeline_service.transports.PipelineServiceTransport.__init__') as Transport:
        Transport.return_value = None
        transport = transports.PipelineServiceTransport(
            credentials=credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        'create_training_pipeline',
        'get_training_pipeline',
        'list_training_pipelines',
        'delete_training_pipeline',
        'cancel_training_pipeline',
        )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    # Additionally, the LRO client (a property) should
    # also raise NotImplementedError
    with pytest.raises(NotImplementedError):
        transport.operations_client


def test_pipeline_service_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(auth, 'load_credentials_from_file') as load_creds, mock.patch('google.cloud.aiplatform_v1beta1.services.pipeline_service.transports.PipelineServiceTransport._prep_wrapped_messages') as Transport:
        Transport.return_value = None
        load_creds.return_value = (credentials.AnonymousCredentials(), None)
        transport = transports.PipelineServiceTransport(
            credentials_file="credentials.json",
            quota_project_id="octopus",
        )
        load_creds.assert_called_once_with("credentials.json", scopes=(
            'https://www.googleapis.com/auth/cloud-platform',
            ),
            quota_project_id="octopus",
        )


def test_pipeline_service_base_transport_with_adc():
    # Test the default credentials are used if credentials and credentials_file are None.
    with mock.patch.object(auth, 'default') as adc, mock.patch('google.cloud.aiplatform_v1beta1.services.pipeline_service.transports.PipelineServiceTransport._prep_wrapped_messages') as Transport:
        Transport.return_value = None
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transport = transports.PipelineServiceTransport()
        adc.assert_called_once()


def test_pipeline_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(auth, 'default') as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        PipelineServiceClient()
        adc.assert_called_once_with(scopes=(
            'https://www.googleapis.com/auth/cloud-platform',),
            quota_project_id=None,
        )


def test_pipeline_service_transport_auth_adc():
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(auth, 'default') as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transports.PipelineServiceGrpcTransport(host="squid.clam.whelk", quota_project_id="octopus")
        adc.assert_called_once_with(scopes=(
            'https://www.googleapis.com/auth/cloud-platform',),
            quota_project_id="octopus",
        )


@pytest.mark.parametrize("transport_class", [transports.PipelineServiceGrpcTransport, transports.PipelineServiceGrpcAsyncIOTransport])
def test_pipeline_service_grpc_transport_client_cert_source_for_mtls(
    transport_class
):
    cred = credentials.AnonymousCredentials()

    # Check ssl_channel_credentials is used if provided.
    with mock.patch.object(transport_class, "create_channel") as mock_create_channel:
        mock_ssl_channel_creds = mock.Mock()
        transport_class(
            host="squid.clam.whelk",
            credentials=cred,
            ssl_channel_credentials=mock_ssl_channel_creds
        )
        mock_create_channel.assert_called_once_with(
            "squid.clam.whelk:443",
            credentials=cred,
            credentials_file=None,
            scopes=(
                'https://www.googleapis.com/auth/cloud-platform',
            ),
            ssl_credentials=mock_ssl_channel_creds,
            quota_project_id=None,
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
            ],
        )

    # Check if ssl_channel_credentials is not provided, then client_cert_source_for_mtls
    # is used.
    with mock.patch.object(transport_class, "create_channel", return_value=mock.Mock()):
        with mock.patch("grpc.ssl_channel_credentials") as mock_ssl_cred:
            transport_class(
                credentials=cred,
                client_cert_source_for_mtls=client_cert_source_callback
            )
            expected_cert, expected_key = client_cert_source_callback()
            mock_ssl_cred.assert_called_once_with(
                certificate_chain=expected_cert,
                private_key=expected_key
            )


def test_pipeline_service_host_no_port():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(api_endpoint='aiplatform.googleapis.com'),
    )
    assert client.transport._host == 'aiplatform.googleapis.com:443'


def test_pipeline_service_host_with_port():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(api_endpoint='aiplatform.googleapis.com:8000'),
    )
    assert client.transport._host == 'aiplatform.googleapis.com:8000'


def test_pipeline_service_grpc_transport_channel():
    channel = grpc.secure_channel('http://localhost/', grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.PipelineServiceGrpcTransport(
        host="squid.clam.whelk",
        channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


def test_pipeline_service_grpc_asyncio_transport_channel():
    channel = aio.secure_channel('http://localhost/', grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.PipelineServiceGrpcAsyncIOTransport(
        host="squid.clam.whelk",
        channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


# Remove this test when deprecated arguments (api_mtls_endpoint, client_cert_source) are
# removed from grpc/grpc_asyncio transport constructor.
@pytest.mark.parametrize("transport_class", [transports.PipelineServiceGrpcTransport, transports.PipelineServiceGrpcAsyncIOTransport])
def test_pipeline_service_transport_channel_mtls_with_client_cert_source(
    transport_class
):
    with mock.patch("grpc.ssl_channel_credentials", autospec=True) as grpc_ssl_channel_cred:
        with mock.patch.object(transport_class, "create_channel") as grpc_create_channel:
            mock_ssl_cred = mock.Mock()
            grpc_ssl_channel_cred.return_value = mock_ssl_cred

            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel

            cred = credentials.AnonymousCredentials()
            with pytest.warns(DeprecationWarning):
                with mock.patch.object(auth, 'default') as adc:
                    adc.return_value = (cred, None)
                    transport = transport_class(
                        host="squid.clam.whelk",
                        api_mtls_endpoint="mtls.squid.clam.whelk",
                        client_cert_source=client_cert_source_callback,
                    )
                    adc.assert_called_once()

            grpc_ssl_channel_cred.assert_called_once_with(
                certificate_chain=b"cert bytes", private_key=b"key bytes"
            )
            grpc_create_channel.assert_called_once_with(
                "mtls.squid.clam.whelk:443",
                credentials=cred,
                credentials_file=None,
                scopes=(
                    'https://www.googleapis.com/auth/cloud-platform',
                ),
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )
            assert transport.grpc_channel == mock_grpc_channel
            assert transport._ssl_channel_credentials == mock_ssl_cred


# Remove this test when deprecated arguments (api_mtls_endpoint, client_cert_source) are
# removed from grpc/grpc_asyncio transport constructor.
@pytest.mark.parametrize("transport_class", [transports.PipelineServiceGrpcTransport, transports.PipelineServiceGrpcAsyncIOTransport])
def test_pipeline_service_transport_channel_mtls_with_adc(
    transport_class
):
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        with mock.patch.object(transport_class, "create_channel") as grpc_create_channel:
            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel
            mock_cred = mock.Mock()

            with pytest.warns(DeprecationWarning):
                transport = transport_class(
                    host="squid.clam.whelk",
                    credentials=mock_cred,
                    api_mtls_endpoint="mtls.squid.clam.whelk",
                    client_cert_source=None,
                )

            grpc_create_channel.assert_called_once_with(
                "mtls.squid.clam.whelk:443",
                credentials=mock_cred,
                credentials_file=None,
                scopes=(
                    'https://www.googleapis.com/auth/cloud-platform',
                ),
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )
            assert transport.grpc_channel == mock_grpc_channel


def test_pipeline_service_grpc_lro_client():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
        transport='grpc',
    )
    transport = client.transport

    # Ensure that we have a api-core operations client.
    assert isinstance(
        transport.operations_client,
        operations_v1.OperationsClient,
    )

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_pipeline_service_grpc_lro_async_client():
    client = PipelineServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
        transport='grpc_asyncio',
    )
    transport = client.transport

    # Ensure that we have a api-core operations client.
    assert isinstance(
        transport.operations_client,
        operations_v1.OperationsAsyncClient,
    )

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_endpoint_path():
    project = "squid"
    location = "clam"
    endpoint = "whelk"

    expected = "projects/{project}/locations/{location}/endpoints/{endpoint}".format(project=project, location=location, endpoint=endpoint, )
    actual = PipelineServiceClient.endpoint_path(project, location, endpoint)
    assert expected == actual


def test_parse_endpoint_path():
    expected = {
    "project": "octopus",
    "location": "oyster",
    "endpoint": "nudibranch",

    }
    path = PipelineServiceClient.endpoint_path(**expected)

    # Check that the path construction is reversible.
    actual = PipelineServiceClient.parse_endpoint_path(path)
    assert expected == actual

def test_model_path():
    project = "cuttlefish"
    location = "mussel"
    model = "winkle"

    expected = "projects/{project}/locations/{location}/models/{model}".format(project=project, location=location, model=model, )
    actual = PipelineServiceClient.model_path(project, location, model)
    assert expected == actual


def test_parse_model_path():
    expected = {
    "project": "nautilus",
    "location": "scallop",
    "model": "abalone",

    }
    path = PipelineServiceClient.model_path(**expected)

    # Check that the path construction is reversible.
    actual = PipelineServiceClient.parse_model_path(path)
    assert expected == actual

def test_training_pipeline_path():
    project = "squid"
    location = "clam"
    training_pipeline = "whelk"

    expected = "projects/{project}/locations/{location}/trainingPipelines/{training_pipeline}".format(project=project, location=location, training_pipeline=training_pipeline, )
    actual = PipelineServiceClient.training_pipeline_path(project, location, training_pipeline)
    assert expected == actual


def test_parse_training_pipeline_path():
    expected = {
    "project": "octopus",
    "location": "oyster",
    "training_pipeline": "nudibranch",

    }
    path = PipelineServiceClient.training_pipeline_path(**expected)

    # Check that the path construction is reversible.
    actual = PipelineServiceClient.parse_training_pipeline_path(path)
    assert expected == actual

def test_common_billing_account_path():
    billing_account = "cuttlefish"

    expected = "billingAccounts/{billing_account}".format(billing_account=billing_account, )
    actual = PipelineServiceClient.common_billing_account_path(billing_account)
    assert expected == actual


def test_parse_common_billing_account_path():
    expected = {
    "billing_account": "mussel",

    }
    path = PipelineServiceClient.common_billing_account_path(**expected)

    # Check that the path construction is reversible.
    actual = PipelineServiceClient.parse_common_billing_account_path(path)
    assert expected == actual

def test_common_folder_path():
    folder = "winkle"

    expected = "folders/{folder}".format(folder=folder, )
    actual = PipelineServiceClient.common_folder_path(folder)
    assert expected == actual


def test_parse_common_folder_path():
    expected = {
    "folder": "nautilus",

    }
    path = PipelineServiceClient.common_folder_path(**expected)

    # Check that the path construction is reversible.
    actual = PipelineServiceClient.parse_common_folder_path(path)
    assert expected == actual

def test_common_organization_path():
    organization = "scallop"

    expected = "organizations/{organization}".format(organization=organization, )
    actual = PipelineServiceClient.common_organization_path(organization)
    assert expected == actual


def test_parse_common_organization_path():
    expected = {
    "organization": "abalone",

    }
    path = PipelineServiceClient.common_organization_path(**expected)

    # Check that the path construction is reversible.
    actual = PipelineServiceClient.parse_common_organization_path(path)
    assert expected == actual

def test_common_project_path():
    project = "squid"

    expected = "projects/{project}".format(project=project, )
    actual = PipelineServiceClient.common_project_path(project)
    assert expected == actual


def test_parse_common_project_path():
    expected = {
    "project": "clam",

    }
    path = PipelineServiceClient.common_project_path(**expected)

    # Check that the path construction is reversible.
    actual = PipelineServiceClient.parse_common_project_path(path)
    assert expected == actual

def test_common_location_path():
    project = "whelk"
    location = "octopus"

    expected = "projects/{project}/locations/{location}".format(project=project, location=location, )
    actual = PipelineServiceClient.common_location_path(project, location)
    assert expected == actual


def test_parse_common_location_path():
    expected = {
    "project": "oyster",
    "location": "nudibranch",

    }
    path = PipelineServiceClient.common_location_path(**expected)

    # Check that the path construction is reversible.
    actual = PipelineServiceClient.parse_common_location_path(path)
    assert expected == actual


def test_client_withDEFAULT_CLIENT_INFO():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(transports.PipelineServiceTransport, '_prep_wrapped_messages') as prep:
        client = PipelineServiceClient(
            credentials=credentials.AnonymousCredentials(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(transports.PipelineServiceTransport, '_prep_wrapped_messages') as prep:
        transport_class = PipelineServiceClient.get_transport_class()
        transport = transport_class(
            credentials=credentials.AnonymousCredentials(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)
