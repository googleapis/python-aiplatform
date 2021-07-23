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
import packaging.version

import grpc
from grpc.experimental import aio
import math
import pytest
from proto.marshal.rules.dates import DurationRule, TimestampRule


from google.api_core import client_options
from google.api_core import exceptions as core_exceptions
from google.api_core import future
from google.api_core import gapic_v1
from google.api_core import grpc_helpers
from google.api_core import grpc_helpers_async
from google.api_core import operation_async  # type: ignore
from google.api_core import operations_v1
from google.auth import credentials as ga_credentials
from google.auth.exceptions import MutualTLSChannelError
from google.cloud.aiplatform_v1beta1.services.tensorboard_service import (
    TensorboardServiceAsyncClient,
)
from google.cloud.aiplatform_v1beta1.services.tensorboard_service import (
    TensorboardServiceClient,
)
from google.cloud.aiplatform_v1beta1.services.tensorboard_service import pagers
from google.cloud.aiplatform_v1beta1.services.tensorboard_service import transports
from google.cloud.aiplatform_v1beta1.services.tensorboard_service.transports.base import (
    _API_CORE_VERSION,
)
from google.cloud.aiplatform_v1beta1.services.tensorboard_service.transports.base import (
    _GOOGLE_AUTH_VERSION,
)
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
from google.longrunning import operations_pb2
from google.oauth2 import service_account
from google.protobuf import field_mask_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
import google.auth


# TODO(busunkim): Once google-api-core >= 1.26.0 is required:
# - Delete all the api-core and auth "less than" test cases
# - Delete these pytest markers (Make the "greater than or equal to" tests the default).
requires_google_auth_lt_1_25_0 = pytest.mark.skipif(
    packaging.version.parse(_GOOGLE_AUTH_VERSION) >= packaging.version.parse("1.25.0"),
    reason="This test requires google-auth < 1.25.0",
)
requires_google_auth_gte_1_25_0 = pytest.mark.skipif(
    packaging.version.parse(_GOOGLE_AUTH_VERSION) < packaging.version.parse("1.25.0"),
    reason="This test requires google-auth >= 1.25.0",
)

requires_api_core_lt_1_26_0 = pytest.mark.skipif(
    packaging.version.parse(_API_CORE_VERSION) >= packaging.version.parse("1.26.0"),
    reason="This test requires google-api-core < 1.26.0",
)

requires_api_core_gte_1_26_0 = pytest.mark.skipif(
    packaging.version.parse(_API_CORE_VERSION) < packaging.version.parse("1.26.0"),
    reason="This test requires google-api-core >= 1.26.0",
)


def client_cert_source_callback():
    return b"cert bytes", b"key bytes"


# If default endpoint is localhost, then default mtls endpoint will be the same.
# This method modifies the default endpoint so the client can produce a different
# mtls endpoint for endpoint testing purposes.
def modify_default_endpoint(client):
    return (
        "foo.googleapis.com"
        if ("localhost" in client.DEFAULT_ENDPOINT)
        else client.DEFAULT_ENDPOINT
    )


def test__get_default_mtls_endpoint():
    api_endpoint = "example.googleapis.com"
    api_mtls_endpoint = "example.mtls.googleapis.com"
    sandbox_endpoint = "example.sandbox.googleapis.com"
    sandbox_mtls_endpoint = "example.mtls.sandbox.googleapis.com"
    non_googleapi = "api.example.com"

    assert TensorboardServiceClient._get_default_mtls_endpoint(None) is None
    assert (
        TensorboardServiceClient._get_default_mtls_endpoint(api_endpoint)
        == api_mtls_endpoint
    )
    assert (
        TensorboardServiceClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        TensorboardServiceClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        TensorboardServiceClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        TensorboardServiceClient._get_default_mtls_endpoint(non_googleapi)
        == non_googleapi
    )


@pytest.mark.parametrize(
    "client_class", [TensorboardServiceClient, TensorboardServiceAsyncClient,]
)
def test_tensorboard_service_client_from_service_account_info(client_class):
    creds = ga_credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_info"
    ) as factory:
        factory.return_value = creds
        info = {"valid": True}
        client = client_class.from_service_account_info(info)
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        assert client.transport._host == "aiplatform.googleapis.com:443"


@pytest.mark.parametrize(
    "client_class", [TensorboardServiceClient, TensorboardServiceAsyncClient,]
)
def test_tensorboard_service_client_from_service_account_file(client_class):
    creds = ga_credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = client_class.from_service_account_file("dummy/file/path.json")
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        client = client_class.from_service_account_json("dummy/file/path.json")
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        assert client.transport._host == "aiplatform.googleapis.com:443"


def test_tensorboard_service_client_get_transport_class():
    transport = TensorboardServiceClient.get_transport_class()
    available_transports = [
        transports.TensorboardServiceGrpcTransport,
    ]
    assert transport in available_transports

    transport = TensorboardServiceClient.get_transport_class("grpc")
    assert transport == transports.TensorboardServiceGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (TensorboardServiceClient, transports.TensorboardServiceGrpcTransport, "grpc"),
        (
            TensorboardServiceAsyncClient,
            transports.TensorboardServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
@mock.patch.object(
    TensorboardServiceClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(TensorboardServiceClient),
)
@mock.patch.object(
    TensorboardServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(TensorboardServiceAsyncClient),
)
def test_tensorboard_service_client_client_options(
    client_class, transport_class, transport_name
):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(TensorboardServiceClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=ga_credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(TensorboardServiceClient, "get_transport_class") as gtc:
        client = client_class(transport=transport_name)
        gtc.assert_called()

    # Check the case api_endpoint is provided.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch.object(transport_class, "__init__") as patched:
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
        with mock.patch.object(transport_class, "__init__") as patched:
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
        with mock.patch.object(transport_class, "__init__") as patched:
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
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}
    ):
        with pytest.raises(ValueError):
            client = client_class()

    # Check the case quota_project_id is provided
    options = client_options.ClientOptions(quota_project_id="octopus")
    with mock.patch.object(transport_class, "__init__") as patched:
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


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name,use_client_cert_env",
    [
        (
            TensorboardServiceClient,
            transports.TensorboardServiceGrpcTransport,
            "grpc",
            "true",
        ),
        (
            TensorboardServiceAsyncClient,
            transports.TensorboardServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "true",
        ),
        (
            TensorboardServiceClient,
            transports.TensorboardServiceGrpcTransport,
            "grpc",
            "false",
        ),
        (
            TensorboardServiceAsyncClient,
            transports.TensorboardServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "false",
        ),
    ],
)
@mock.patch.object(
    TensorboardServiceClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(TensorboardServiceClient),
)
@mock.patch.object(
    TensorboardServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(TensorboardServiceAsyncClient),
)
@mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"})
def test_tensorboard_service_client_mtls_env_auto(
    client_class, transport_class, transport_name, use_client_cert_env
):
    # This tests the endpoint autoswitch behavior. Endpoint is autoswitched to the default
    # mtls endpoint, if GOOGLE_API_USE_CLIENT_CERTIFICATE is "true" and client cert exists.

    # Check the case client_cert_source is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        options = client_options.ClientOptions(
            client_cert_source=client_cert_source_callback
        )
        with mock.patch.object(transport_class, "__init__") as patched:
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
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.mtls.has_default_client_cert_source",
                return_value=True,
            ):
                with mock.patch(
                    "google.auth.transport.mtls.default_client_cert_source",
                    return_value=client_cert_source_callback,
                ):
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
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.mtls.has_default_client_cert_source",
                return_value=False,
            ):
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


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (TensorboardServiceClient, transports.TensorboardServiceGrpcTransport, "grpc"),
        (
            TensorboardServiceAsyncClient,
            transports.TensorboardServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_tensorboard_service_client_client_options_scopes(
    client_class, transport_class, transport_name
):
    # Check the case scopes are provided.
    options = client_options.ClientOptions(scopes=["1", "2"],)
    with mock.patch.object(transport_class, "__init__") as patched:
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


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (TensorboardServiceClient, transports.TensorboardServiceGrpcTransport, "grpc"),
        (
            TensorboardServiceAsyncClient,
            transports.TensorboardServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_tensorboard_service_client_client_options_credentials_file(
    client_class, transport_class, transport_name
):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(credentials_file="credentials.json")
    with mock.patch.object(transport_class, "__init__") as patched:
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


def test_tensorboard_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.tensorboard_service.transports.TensorboardServiceGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = TensorboardServiceClient(
            client_options={"api_endpoint": "squid.clam.whelk"}
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


def test_create_tensorboard(
    transport: str = "grpc", request_type=tensorboard_service.CreateTensorboardRequest
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.create_tensorboard(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.CreateTensorboardRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_create_tensorboard_from_dict():
    test_create_tensorboard(request_type=dict)


def test_create_tensorboard_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard), "__call__"
    ) as call:
        client.create_tensorboard()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.CreateTensorboardRequest()


@pytest.mark.asyncio
async def test_create_tensorboard_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.CreateTensorboardRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.create_tensorboard(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.CreateTensorboardRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_create_tensorboard_async_from_dict():
    await test_create_tensorboard_async(request_type=dict)


def test_create_tensorboard_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.CreateTensorboardRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.create_tensorboard(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_tensorboard_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.CreateTensorboardRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.create_tensorboard(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_tensorboard_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_tensorboard(
            parent="parent_value",
            tensorboard=gca_tensorboard.Tensorboard(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].tensorboard == gca_tensorboard.Tensorboard(name="name_value")


def test_create_tensorboard_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_tensorboard(
            tensorboard_service.CreateTensorboardRequest(),
            parent="parent_value",
            tensorboard=gca_tensorboard.Tensorboard(name="name_value"),
        )


@pytest.mark.asyncio
async def test_create_tensorboard_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_tensorboard(
            parent="parent_value",
            tensorboard=gca_tensorboard.Tensorboard(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].tensorboard == gca_tensorboard.Tensorboard(name="name_value")


@pytest.mark.asyncio
async def test_create_tensorboard_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_tensorboard(
            tensorboard_service.CreateTensorboardRequest(),
            parent="parent_value",
            tensorboard=gca_tensorboard.Tensorboard(name="name_value"),
        )


def test_get_tensorboard(
    transport: str = "grpc", request_type=tensorboard_service.GetTensorboardRequest
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_tensorboard), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard.Tensorboard(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            blob_storage_path_prefix="blob_storage_path_prefix_value",
            run_count=989,
            etag="etag_value",
        )
        response = client.get_tensorboard(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.GetTensorboardRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, tensorboard.Tensorboard)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.blob_storage_path_prefix == "blob_storage_path_prefix_value"
    assert response.run_count == 989
    assert response.etag == "etag_value"


def test_get_tensorboard_from_dict():
    test_get_tensorboard(request_type=dict)


def test_get_tensorboard_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_tensorboard), "__call__") as call:
        client.get_tensorboard()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.GetTensorboardRequest()


@pytest.mark.asyncio
async def test_get_tensorboard_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.GetTensorboardRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_tensorboard), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard.Tensorboard(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
                blob_storage_path_prefix="blob_storage_path_prefix_value",
                run_count=989,
                etag="etag_value",
            )
        )
        response = await client.get_tensorboard(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.GetTensorboardRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, tensorboard.Tensorboard)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.blob_storage_path_prefix == "blob_storage_path_prefix_value"
    assert response.run_count == 989
    assert response.etag == "etag_value"


@pytest.mark.asyncio
async def test_get_tensorboard_async_from_dict():
    await test_get_tensorboard_async(request_type=dict)


def test_get_tensorboard_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.GetTensorboardRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_tensorboard), "__call__") as call:
        call.return_value = tensorboard.Tensorboard()
        client.get_tensorboard(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_tensorboard_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.GetTensorboardRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_tensorboard), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard.Tensorboard()
        )
        await client.get_tensorboard(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_tensorboard_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_tensorboard), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard.Tensorboard()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_tensorboard(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_tensorboard_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_tensorboard(
            tensorboard_service.GetTensorboardRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_tensorboard_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_tensorboard), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard.Tensorboard()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard.Tensorboard()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_tensorboard(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_tensorboard_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_tensorboard(
            tensorboard_service.GetTensorboardRequest(), name="name_value",
        )


def test_update_tensorboard(
    transport: str = "grpc", request_type=tensorboard_service.UpdateTensorboardRequest
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.update_tensorboard(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.UpdateTensorboardRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_update_tensorboard_from_dict():
    test_update_tensorboard(request_type=dict)


def test_update_tensorboard_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard), "__call__"
    ) as call:
        client.update_tensorboard()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.UpdateTensorboardRequest()


@pytest.mark.asyncio
async def test_update_tensorboard_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.UpdateTensorboardRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.update_tensorboard(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.UpdateTensorboardRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_update_tensorboard_async_from_dict():
    await test_update_tensorboard_async(request_type=dict)


def test_update_tensorboard_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.UpdateTensorboardRequest()

    request.tensorboard.name = "tensorboard.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.update_tensorboard(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "tensorboard.name=tensorboard.name/value",) in kw[
        "metadata"
    ]


@pytest.mark.asyncio
async def test_update_tensorboard_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.UpdateTensorboardRequest()

    request.tensorboard.name = "tensorboard.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.update_tensorboard(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "tensorboard.name=tensorboard.name/value",) in kw[
        "metadata"
    ]


def test_update_tensorboard_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_tensorboard(
            tensorboard=gca_tensorboard.Tensorboard(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].tensorboard == gca_tensorboard.Tensorboard(name="name_value")
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


def test_update_tensorboard_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_tensorboard(
            tensorboard_service.UpdateTensorboardRequest(),
            tensorboard=gca_tensorboard.Tensorboard(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_tensorboard_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_tensorboard(
            tensorboard=gca_tensorboard.Tensorboard(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].tensorboard == gca_tensorboard.Tensorboard(name="name_value")
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


@pytest.mark.asyncio
async def test_update_tensorboard_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_tensorboard(
            tensorboard_service.UpdateTensorboardRequest(),
            tensorboard=gca_tensorboard.Tensorboard(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


def test_list_tensorboards(
    transport: str = "grpc", request_type=tensorboard_service.ListTensorboardsRequest
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboards), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.ListTensorboardsResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_tensorboards(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ListTensorboardsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListTensorboardsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_tensorboards_from_dict():
    test_list_tensorboards(request_type=dict)


def test_list_tensorboards_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboards), "__call__"
    ) as call:
        client.list_tensorboards()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ListTensorboardsRequest()


@pytest.mark.asyncio
async def test_list_tensorboards_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.ListTensorboardsRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboards), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ListTensorboardsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_tensorboards(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ListTensorboardsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListTensorboardsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_tensorboards_async_from_dict():
    await test_list_tensorboards_async(request_type=dict)


def test_list_tensorboards_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ListTensorboardsRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboards), "__call__"
    ) as call:
        call.return_value = tensorboard_service.ListTensorboardsResponse()
        client.list_tensorboards(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_tensorboards_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ListTensorboardsRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboards), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ListTensorboardsResponse()
        )
        await client.list_tensorboards(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_tensorboards_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboards), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.ListTensorboardsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_tensorboards(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_tensorboards_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_tensorboards(
            tensorboard_service.ListTensorboardsRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_tensorboards_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboards), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.ListTensorboardsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ListTensorboardsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_tensorboards(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_tensorboards_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_tensorboards(
            tensorboard_service.ListTensorboardsRequest(), parent="parent_value",
        )


def test_list_tensorboards_pager():
    client = TensorboardServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboards), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[
                    tensorboard.Tensorboard(),
                    tensorboard.Tensorboard(),
                    tensorboard.Tensorboard(),
                ],
                next_page_token="abc",
            ),
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[], next_page_token="def",
            ),
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[tensorboard.Tensorboard(),], next_page_token="ghi",
            ),
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[tensorboard.Tensorboard(), tensorboard.Tensorboard(),],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_tensorboards(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, tensorboard.Tensorboard) for i in results)


def test_list_tensorboards_pages():
    client = TensorboardServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboards), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[
                    tensorboard.Tensorboard(),
                    tensorboard.Tensorboard(),
                    tensorboard.Tensorboard(),
                ],
                next_page_token="abc",
            ),
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[], next_page_token="def",
            ),
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[tensorboard.Tensorboard(),], next_page_token="ghi",
            ),
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[tensorboard.Tensorboard(), tensorboard.Tensorboard(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_tensorboards(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_tensorboards_async_pager():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboards),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[
                    tensorboard.Tensorboard(),
                    tensorboard.Tensorboard(),
                    tensorboard.Tensorboard(),
                ],
                next_page_token="abc",
            ),
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[], next_page_token="def",
            ),
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[tensorboard.Tensorboard(),], next_page_token="ghi",
            ),
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[tensorboard.Tensorboard(), tensorboard.Tensorboard(),],
            ),
            RuntimeError,
        )
        async_pager = await client.list_tensorboards(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, tensorboard.Tensorboard) for i in responses)


@pytest.mark.asyncio
async def test_list_tensorboards_async_pages():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboards),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[
                    tensorboard.Tensorboard(),
                    tensorboard.Tensorboard(),
                    tensorboard.Tensorboard(),
                ],
                next_page_token="abc",
            ),
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[], next_page_token="def",
            ),
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[tensorboard.Tensorboard(),], next_page_token="ghi",
            ),
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[tensorboard.Tensorboard(), tensorboard.Tensorboard(),],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_tensorboards(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_delete_tensorboard(
    transport: str = "grpc", request_type=tensorboard_service.DeleteTensorboardRequest
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_tensorboard(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.DeleteTensorboardRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_tensorboard_from_dict():
    test_delete_tensorboard(request_type=dict)


def test_delete_tensorboard_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard), "__call__"
    ) as call:
        client.delete_tensorboard()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.DeleteTensorboardRequest()


@pytest.mark.asyncio
async def test_delete_tensorboard_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.DeleteTensorboardRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_tensorboard(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.DeleteTensorboardRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_tensorboard_async_from_dict():
    await test_delete_tensorboard_async(request_type=dict)


def test_delete_tensorboard_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.DeleteTensorboardRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_tensorboard(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_tensorboard_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.DeleteTensorboardRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_tensorboard(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_tensorboard_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_tensorboard(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_tensorboard_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_tensorboard(
            tensorboard_service.DeleteTensorboardRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_tensorboard_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_tensorboard(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_tensorboard_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_tensorboard(
            tensorboard_service.DeleteTensorboardRequest(), name="name_value",
        )


def test_create_tensorboard_experiment(
    transport: str = "grpc",
    request_type=tensorboard_service.CreateTensorboardExperimentRequest,
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard_experiment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_tensorboard_experiment.TensorboardExperiment(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            etag="etag_value",
            source="source_value",
        )
        response = client.create_tensorboard_experiment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.CreateTensorboardExperimentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_tensorboard_experiment.TensorboardExperiment)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.etag == "etag_value"
    assert response.source == "source_value"


def test_create_tensorboard_experiment_from_dict():
    test_create_tensorboard_experiment(request_type=dict)


def test_create_tensorboard_experiment_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard_experiment), "__call__"
    ) as call:
        client.create_tensorboard_experiment()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.CreateTensorboardExperimentRequest()


@pytest.mark.asyncio
async def test_create_tensorboard_experiment_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.CreateTensorboardExperimentRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard_experiment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_tensorboard_experiment.TensorboardExperiment(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
                etag="etag_value",
                source="source_value",
            )
        )
        response = await client.create_tensorboard_experiment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.CreateTensorboardExperimentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_tensorboard_experiment.TensorboardExperiment)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.etag == "etag_value"
    assert response.source == "source_value"


@pytest.mark.asyncio
async def test_create_tensorboard_experiment_async_from_dict():
    await test_create_tensorboard_experiment_async(request_type=dict)


def test_create_tensorboard_experiment_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.CreateTensorboardExperimentRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard_experiment), "__call__"
    ) as call:
        call.return_value = gca_tensorboard_experiment.TensorboardExperiment()
        client.create_tensorboard_experiment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_tensorboard_experiment_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.CreateTensorboardExperimentRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard_experiment), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_tensorboard_experiment.TensorboardExperiment()
        )
        await client.create_tensorboard_experiment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_tensorboard_experiment_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard_experiment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_tensorboard_experiment.TensorboardExperiment()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_tensorboard_experiment(
            parent="parent_value",
            tensorboard_experiment=gca_tensorboard_experiment.TensorboardExperiment(
                name="name_value"
            ),
            tensorboard_experiment_id="tensorboard_experiment_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[
            0
        ].tensorboard_experiment == gca_tensorboard_experiment.TensorboardExperiment(
            name="name_value"
        )
        assert args[0].tensorboard_experiment_id == "tensorboard_experiment_id_value"


def test_create_tensorboard_experiment_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_tensorboard_experiment(
            tensorboard_service.CreateTensorboardExperimentRequest(),
            parent="parent_value",
            tensorboard_experiment=gca_tensorboard_experiment.TensorboardExperiment(
                name="name_value"
            ),
            tensorboard_experiment_id="tensorboard_experiment_id_value",
        )


@pytest.mark.asyncio
async def test_create_tensorboard_experiment_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard_experiment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_tensorboard_experiment.TensorboardExperiment()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_tensorboard_experiment.TensorboardExperiment()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_tensorboard_experiment(
            parent="parent_value",
            tensorboard_experiment=gca_tensorboard_experiment.TensorboardExperiment(
                name="name_value"
            ),
            tensorboard_experiment_id="tensorboard_experiment_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[
            0
        ].tensorboard_experiment == gca_tensorboard_experiment.TensorboardExperiment(
            name="name_value"
        )
        assert args[0].tensorboard_experiment_id == "tensorboard_experiment_id_value"


@pytest.mark.asyncio
async def test_create_tensorboard_experiment_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_tensorboard_experiment(
            tensorboard_service.CreateTensorboardExperimentRequest(),
            parent="parent_value",
            tensorboard_experiment=gca_tensorboard_experiment.TensorboardExperiment(
                name="name_value"
            ),
            tensorboard_experiment_id="tensorboard_experiment_id_value",
        )


def test_get_tensorboard_experiment(
    transport: str = "grpc",
    request_type=tensorboard_service.GetTensorboardExperimentRequest,
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_tensorboard_experiment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_experiment.TensorboardExperiment(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            etag="etag_value",
            source="source_value",
        )
        response = client.get_tensorboard_experiment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.GetTensorboardExperimentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, tensorboard_experiment.TensorboardExperiment)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.etag == "etag_value"
    assert response.source == "source_value"


def test_get_tensorboard_experiment_from_dict():
    test_get_tensorboard_experiment(request_type=dict)


def test_get_tensorboard_experiment_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_tensorboard_experiment), "__call__"
    ) as call:
        client.get_tensorboard_experiment()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.GetTensorboardExperimentRequest()


@pytest.mark.asyncio
async def test_get_tensorboard_experiment_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.GetTensorboardExperimentRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_tensorboard_experiment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_experiment.TensorboardExperiment(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
                etag="etag_value",
                source="source_value",
            )
        )
        response = await client.get_tensorboard_experiment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.GetTensorboardExperimentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, tensorboard_experiment.TensorboardExperiment)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.etag == "etag_value"
    assert response.source == "source_value"


@pytest.mark.asyncio
async def test_get_tensorboard_experiment_async_from_dict():
    await test_get_tensorboard_experiment_async(request_type=dict)


def test_get_tensorboard_experiment_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.GetTensorboardExperimentRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_tensorboard_experiment), "__call__"
    ) as call:
        call.return_value = tensorboard_experiment.TensorboardExperiment()
        client.get_tensorboard_experiment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_tensorboard_experiment_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.GetTensorboardExperimentRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_tensorboard_experiment), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_experiment.TensorboardExperiment()
        )
        await client.get_tensorboard_experiment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_tensorboard_experiment_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_tensorboard_experiment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_experiment.TensorboardExperiment()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_tensorboard_experiment(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_tensorboard_experiment_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_tensorboard_experiment(
            tensorboard_service.GetTensorboardExperimentRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_tensorboard_experiment_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_tensorboard_experiment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_experiment.TensorboardExperiment()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_experiment.TensorboardExperiment()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_tensorboard_experiment(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_tensorboard_experiment_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_tensorboard_experiment(
            tensorboard_service.GetTensorboardExperimentRequest(), name="name_value",
        )


def test_update_tensorboard_experiment(
    transport: str = "grpc",
    request_type=tensorboard_service.UpdateTensorboardExperimentRequest,
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard_experiment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_tensorboard_experiment.TensorboardExperiment(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            etag="etag_value",
            source="source_value",
        )
        response = client.update_tensorboard_experiment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.UpdateTensorboardExperimentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_tensorboard_experiment.TensorboardExperiment)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.etag == "etag_value"
    assert response.source == "source_value"


def test_update_tensorboard_experiment_from_dict():
    test_update_tensorboard_experiment(request_type=dict)


def test_update_tensorboard_experiment_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard_experiment), "__call__"
    ) as call:
        client.update_tensorboard_experiment()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.UpdateTensorboardExperimentRequest()


@pytest.mark.asyncio
async def test_update_tensorboard_experiment_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.UpdateTensorboardExperimentRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard_experiment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_tensorboard_experiment.TensorboardExperiment(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
                etag="etag_value",
                source="source_value",
            )
        )
        response = await client.update_tensorboard_experiment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.UpdateTensorboardExperimentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_tensorboard_experiment.TensorboardExperiment)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.etag == "etag_value"
    assert response.source == "source_value"


@pytest.mark.asyncio
async def test_update_tensorboard_experiment_async_from_dict():
    await test_update_tensorboard_experiment_async(request_type=dict)


def test_update_tensorboard_experiment_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.UpdateTensorboardExperimentRequest()

    request.tensorboard_experiment.name = "tensorboard_experiment.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard_experiment), "__call__"
    ) as call:
        call.return_value = gca_tensorboard_experiment.TensorboardExperiment()
        client.update_tensorboard_experiment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "tensorboard_experiment.name=tensorboard_experiment.name/value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_tensorboard_experiment_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.UpdateTensorboardExperimentRequest()

    request.tensorboard_experiment.name = "tensorboard_experiment.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard_experiment), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_tensorboard_experiment.TensorboardExperiment()
        )
        await client.update_tensorboard_experiment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "tensorboard_experiment.name=tensorboard_experiment.name/value",
    ) in kw["metadata"]


def test_update_tensorboard_experiment_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard_experiment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_tensorboard_experiment.TensorboardExperiment()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_tensorboard_experiment(
            tensorboard_experiment=gca_tensorboard_experiment.TensorboardExperiment(
                name="name_value"
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[
            0
        ].tensorboard_experiment == gca_tensorboard_experiment.TensorboardExperiment(
            name="name_value"
        )
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


def test_update_tensorboard_experiment_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_tensorboard_experiment(
            tensorboard_service.UpdateTensorboardExperimentRequest(),
            tensorboard_experiment=gca_tensorboard_experiment.TensorboardExperiment(
                name="name_value"
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_tensorboard_experiment_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard_experiment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_tensorboard_experiment.TensorboardExperiment()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_tensorboard_experiment.TensorboardExperiment()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_tensorboard_experiment(
            tensorboard_experiment=gca_tensorboard_experiment.TensorboardExperiment(
                name="name_value"
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[
            0
        ].tensorboard_experiment == gca_tensorboard_experiment.TensorboardExperiment(
            name="name_value"
        )
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


@pytest.mark.asyncio
async def test_update_tensorboard_experiment_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_tensorboard_experiment(
            tensorboard_service.UpdateTensorboardExperimentRequest(),
            tensorboard_experiment=gca_tensorboard_experiment.TensorboardExperiment(
                name="name_value"
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


def test_list_tensorboard_experiments(
    transport: str = "grpc",
    request_type=tensorboard_service.ListTensorboardExperimentsRequest,
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_experiments), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.ListTensorboardExperimentsResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_tensorboard_experiments(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ListTensorboardExperimentsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListTensorboardExperimentsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_tensorboard_experiments_from_dict():
    test_list_tensorboard_experiments(request_type=dict)


def test_list_tensorboard_experiments_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_experiments), "__call__"
    ) as call:
        client.list_tensorboard_experiments()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ListTensorboardExperimentsRequest()


@pytest.mark.asyncio
async def test_list_tensorboard_experiments_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.ListTensorboardExperimentsRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_experiments), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ListTensorboardExperimentsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_tensorboard_experiments(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ListTensorboardExperimentsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListTensorboardExperimentsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_tensorboard_experiments_async_from_dict():
    await test_list_tensorboard_experiments_async(request_type=dict)


def test_list_tensorboard_experiments_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ListTensorboardExperimentsRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_experiments), "__call__"
    ) as call:
        call.return_value = tensorboard_service.ListTensorboardExperimentsResponse()
        client.list_tensorboard_experiments(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_tensorboard_experiments_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ListTensorboardExperimentsRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_experiments), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ListTensorboardExperimentsResponse()
        )
        await client.list_tensorboard_experiments(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_tensorboard_experiments_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_experiments), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.ListTensorboardExperimentsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_tensorboard_experiments(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_tensorboard_experiments_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_tensorboard_experiments(
            tensorboard_service.ListTensorboardExperimentsRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_tensorboard_experiments_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_experiments), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.ListTensorboardExperimentsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ListTensorboardExperimentsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_tensorboard_experiments(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_tensorboard_experiments_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_tensorboard_experiments(
            tensorboard_service.ListTensorboardExperimentsRequest(),
            parent="parent_value",
        )


def test_list_tensorboard_experiments_pager():
    client = TensorboardServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_experiments), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tensorboard_service.ListTensorboardExperimentsResponse(
                tensorboard_experiments=[
                    tensorboard_experiment.TensorboardExperiment(),
                    tensorboard_experiment.TensorboardExperiment(),
                    tensorboard_experiment.TensorboardExperiment(),
                ],
                next_page_token="abc",
            ),
            tensorboard_service.ListTensorboardExperimentsResponse(
                tensorboard_experiments=[], next_page_token="def",
            ),
            tensorboard_service.ListTensorboardExperimentsResponse(
                tensorboard_experiments=[
                    tensorboard_experiment.TensorboardExperiment(),
                ],
                next_page_token="ghi",
            ),
            tensorboard_service.ListTensorboardExperimentsResponse(
                tensorboard_experiments=[
                    tensorboard_experiment.TensorboardExperiment(),
                    tensorboard_experiment.TensorboardExperiment(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_tensorboard_experiments(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(
            isinstance(i, tensorboard_experiment.TensorboardExperiment) for i in results
        )


def test_list_tensorboard_experiments_pages():
    client = TensorboardServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_experiments), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tensorboard_service.ListTensorboardExperimentsResponse(
                tensorboard_experiments=[
                    tensorboard_experiment.TensorboardExperiment(),
                    tensorboard_experiment.TensorboardExperiment(),
                    tensorboard_experiment.TensorboardExperiment(),
                ],
                next_page_token="abc",
            ),
            tensorboard_service.ListTensorboardExperimentsResponse(
                tensorboard_experiments=[], next_page_token="def",
            ),
            tensorboard_service.ListTensorboardExperimentsResponse(
                tensorboard_experiments=[
                    tensorboard_experiment.TensorboardExperiment(),
                ],
                next_page_token="ghi",
            ),
            tensorboard_service.ListTensorboardExperimentsResponse(
                tensorboard_experiments=[
                    tensorboard_experiment.TensorboardExperiment(),
                    tensorboard_experiment.TensorboardExperiment(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_tensorboard_experiments(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_tensorboard_experiments_async_pager():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_experiments),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tensorboard_service.ListTensorboardExperimentsResponse(
                tensorboard_experiments=[
                    tensorboard_experiment.TensorboardExperiment(),
                    tensorboard_experiment.TensorboardExperiment(),
                    tensorboard_experiment.TensorboardExperiment(),
                ],
                next_page_token="abc",
            ),
            tensorboard_service.ListTensorboardExperimentsResponse(
                tensorboard_experiments=[], next_page_token="def",
            ),
            tensorboard_service.ListTensorboardExperimentsResponse(
                tensorboard_experiments=[
                    tensorboard_experiment.TensorboardExperiment(),
                ],
                next_page_token="ghi",
            ),
            tensorboard_service.ListTensorboardExperimentsResponse(
                tensorboard_experiments=[
                    tensorboard_experiment.TensorboardExperiment(),
                    tensorboard_experiment.TensorboardExperiment(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_tensorboard_experiments(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(
            isinstance(i, tensorboard_experiment.TensorboardExperiment)
            for i in responses
        )


@pytest.mark.asyncio
async def test_list_tensorboard_experiments_async_pages():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_experiments),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tensorboard_service.ListTensorboardExperimentsResponse(
                tensorboard_experiments=[
                    tensorboard_experiment.TensorboardExperiment(),
                    tensorboard_experiment.TensorboardExperiment(),
                    tensorboard_experiment.TensorboardExperiment(),
                ],
                next_page_token="abc",
            ),
            tensorboard_service.ListTensorboardExperimentsResponse(
                tensorboard_experiments=[], next_page_token="def",
            ),
            tensorboard_service.ListTensorboardExperimentsResponse(
                tensorboard_experiments=[
                    tensorboard_experiment.TensorboardExperiment(),
                ],
                next_page_token="ghi",
            ),
            tensorboard_service.ListTensorboardExperimentsResponse(
                tensorboard_experiments=[
                    tensorboard_experiment.TensorboardExperiment(),
                    tensorboard_experiment.TensorboardExperiment(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (
            await client.list_tensorboard_experiments(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_delete_tensorboard_experiment(
    transport: str = "grpc",
    request_type=tensorboard_service.DeleteTensorboardExperimentRequest,
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard_experiment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_tensorboard_experiment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.DeleteTensorboardExperimentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_tensorboard_experiment_from_dict():
    test_delete_tensorboard_experiment(request_type=dict)


def test_delete_tensorboard_experiment_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard_experiment), "__call__"
    ) as call:
        client.delete_tensorboard_experiment()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.DeleteTensorboardExperimentRequest()


@pytest.mark.asyncio
async def test_delete_tensorboard_experiment_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.DeleteTensorboardExperimentRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard_experiment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_tensorboard_experiment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.DeleteTensorboardExperimentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_tensorboard_experiment_async_from_dict():
    await test_delete_tensorboard_experiment_async(request_type=dict)


def test_delete_tensorboard_experiment_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.DeleteTensorboardExperimentRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard_experiment), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_tensorboard_experiment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_tensorboard_experiment_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.DeleteTensorboardExperimentRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard_experiment), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_tensorboard_experiment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_tensorboard_experiment_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard_experiment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_tensorboard_experiment(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_tensorboard_experiment_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_tensorboard_experiment(
            tensorboard_service.DeleteTensorboardExperimentRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_tensorboard_experiment_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard_experiment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_tensorboard_experiment(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_tensorboard_experiment_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_tensorboard_experiment(
            tensorboard_service.DeleteTensorboardExperimentRequest(), name="name_value",
        )


def test_create_tensorboard_run(
    transport: str = "grpc",
    request_type=tensorboard_service.CreateTensorboardRunRequest,
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard_run), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_tensorboard_run.TensorboardRun(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            etag="etag_value",
        )
        response = client.create_tensorboard_run(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.CreateTensorboardRunRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_tensorboard_run.TensorboardRun)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.etag == "etag_value"


def test_create_tensorboard_run_from_dict():
    test_create_tensorboard_run(request_type=dict)


def test_create_tensorboard_run_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard_run), "__call__"
    ) as call:
        client.create_tensorboard_run()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.CreateTensorboardRunRequest()


@pytest.mark.asyncio
async def test_create_tensorboard_run_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.CreateTensorboardRunRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard_run), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_tensorboard_run.TensorboardRun(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
                etag="etag_value",
            )
        )
        response = await client.create_tensorboard_run(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.CreateTensorboardRunRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_tensorboard_run.TensorboardRun)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.etag == "etag_value"


@pytest.mark.asyncio
async def test_create_tensorboard_run_async_from_dict():
    await test_create_tensorboard_run_async(request_type=dict)


def test_create_tensorboard_run_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.CreateTensorboardRunRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard_run), "__call__"
    ) as call:
        call.return_value = gca_tensorboard_run.TensorboardRun()
        client.create_tensorboard_run(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_tensorboard_run_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.CreateTensorboardRunRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard_run), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_tensorboard_run.TensorboardRun()
        )
        await client.create_tensorboard_run(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_tensorboard_run_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard_run), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_tensorboard_run.TensorboardRun()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_tensorboard_run(
            parent="parent_value",
            tensorboard_run=gca_tensorboard_run.TensorboardRun(name="name_value"),
            tensorboard_run_id="tensorboard_run_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].tensorboard_run == gca_tensorboard_run.TensorboardRun(
            name="name_value"
        )
        assert args[0].tensorboard_run_id == "tensorboard_run_id_value"


def test_create_tensorboard_run_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_tensorboard_run(
            tensorboard_service.CreateTensorboardRunRequest(),
            parent="parent_value",
            tensorboard_run=gca_tensorboard_run.TensorboardRun(name="name_value"),
            tensorboard_run_id="tensorboard_run_id_value",
        )


@pytest.mark.asyncio
async def test_create_tensorboard_run_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard_run), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_tensorboard_run.TensorboardRun()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_tensorboard_run.TensorboardRun()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_tensorboard_run(
            parent="parent_value",
            tensorboard_run=gca_tensorboard_run.TensorboardRun(name="name_value"),
            tensorboard_run_id="tensorboard_run_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].tensorboard_run == gca_tensorboard_run.TensorboardRun(
            name="name_value"
        )
        assert args[0].tensorboard_run_id == "tensorboard_run_id_value"


@pytest.mark.asyncio
async def test_create_tensorboard_run_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_tensorboard_run(
            tensorboard_service.CreateTensorboardRunRequest(),
            parent="parent_value",
            tensorboard_run=gca_tensorboard_run.TensorboardRun(name="name_value"),
            tensorboard_run_id="tensorboard_run_id_value",
        )


def test_get_tensorboard_run(
    transport: str = "grpc", request_type=tensorboard_service.GetTensorboardRunRequest
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_tensorboard_run), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_run.TensorboardRun(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            etag="etag_value",
        )
        response = client.get_tensorboard_run(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.GetTensorboardRunRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, tensorboard_run.TensorboardRun)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.etag == "etag_value"


def test_get_tensorboard_run_from_dict():
    test_get_tensorboard_run(request_type=dict)


def test_get_tensorboard_run_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_tensorboard_run), "__call__"
    ) as call:
        client.get_tensorboard_run()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.GetTensorboardRunRequest()


@pytest.mark.asyncio
async def test_get_tensorboard_run_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.GetTensorboardRunRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_tensorboard_run), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_run.TensorboardRun(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
                etag="etag_value",
            )
        )
        response = await client.get_tensorboard_run(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.GetTensorboardRunRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, tensorboard_run.TensorboardRun)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.etag == "etag_value"


@pytest.mark.asyncio
async def test_get_tensorboard_run_async_from_dict():
    await test_get_tensorboard_run_async(request_type=dict)


def test_get_tensorboard_run_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.GetTensorboardRunRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_tensorboard_run), "__call__"
    ) as call:
        call.return_value = tensorboard_run.TensorboardRun()
        client.get_tensorboard_run(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_tensorboard_run_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.GetTensorboardRunRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_tensorboard_run), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_run.TensorboardRun()
        )
        await client.get_tensorboard_run(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_tensorboard_run_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_tensorboard_run), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_run.TensorboardRun()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_tensorboard_run(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_tensorboard_run_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_tensorboard_run(
            tensorboard_service.GetTensorboardRunRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_tensorboard_run_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_tensorboard_run), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_run.TensorboardRun()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_run.TensorboardRun()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_tensorboard_run(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_tensorboard_run_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_tensorboard_run(
            tensorboard_service.GetTensorboardRunRequest(), name="name_value",
        )


def test_update_tensorboard_run(
    transport: str = "grpc",
    request_type=tensorboard_service.UpdateTensorboardRunRequest,
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard_run), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_tensorboard_run.TensorboardRun(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            etag="etag_value",
        )
        response = client.update_tensorboard_run(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.UpdateTensorboardRunRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_tensorboard_run.TensorboardRun)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.etag == "etag_value"


def test_update_tensorboard_run_from_dict():
    test_update_tensorboard_run(request_type=dict)


def test_update_tensorboard_run_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard_run), "__call__"
    ) as call:
        client.update_tensorboard_run()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.UpdateTensorboardRunRequest()


@pytest.mark.asyncio
async def test_update_tensorboard_run_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.UpdateTensorboardRunRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard_run), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_tensorboard_run.TensorboardRun(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
                etag="etag_value",
            )
        )
        response = await client.update_tensorboard_run(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.UpdateTensorboardRunRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_tensorboard_run.TensorboardRun)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.etag == "etag_value"


@pytest.mark.asyncio
async def test_update_tensorboard_run_async_from_dict():
    await test_update_tensorboard_run_async(request_type=dict)


def test_update_tensorboard_run_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.UpdateTensorboardRunRequest()

    request.tensorboard_run.name = "tensorboard_run.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard_run), "__call__"
    ) as call:
        call.return_value = gca_tensorboard_run.TensorboardRun()
        client.update_tensorboard_run(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "tensorboard_run.name=tensorboard_run.name/value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_tensorboard_run_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.UpdateTensorboardRunRequest()

    request.tensorboard_run.name = "tensorboard_run.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard_run), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_tensorboard_run.TensorboardRun()
        )
        await client.update_tensorboard_run(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "tensorboard_run.name=tensorboard_run.name/value",
    ) in kw["metadata"]


def test_update_tensorboard_run_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard_run), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_tensorboard_run.TensorboardRun()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_tensorboard_run(
            tensorboard_run=gca_tensorboard_run.TensorboardRun(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].tensorboard_run == gca_tensorboard_run.TensorboardRun(
            name="name_value"
        )
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


def test_update_tensorboard_run_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_tensorboard_run(
            tensorboard_service.UpdateTensorboardRunRequest(),
            tensorboard_run=gca_tensorboard_run.TensorboardRun(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_tensorboard_run_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard_run), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_tensorboard_run.TensorboardRun()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_tensorboard_run.TensorboardRun()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_tensorboard_run(
            tensorboard_run=gca_tensorboard_run.TensorboardRun(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].tensorboard_run == gca_tensorboard_run.TensorboardRun(
            name="name_value"
        )
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


@pytest.mark.asyncio
async def test_update_tensorboard_run_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_tensorboard_run(
            tensorboard_service.UpdateTensorboardRunRequest(),
            tensorboard_run=gca_tensorboard_run.TensorboardRun(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


def test_list_tensorboard_runs(
    transport: str = "grpc", request_type=tensorboard_service.ListTensorboardRunsRequest
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_runs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.ListTensorboardRunsResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_tensorboard_runs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ListTensorboardRunsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListTensorboardRunsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_tensorboard_runs_from_dict():
    test_list_tensorboard_runs(request_type=dict)


def test_list_tensorboard_runs_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_runs), "__call__"
    ) as call:
        client.list_tensorboard_runs()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ListTensorboardRunsRequest()


@pytest.mark.asyncio
async def test_list_tensorboard_runs_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.ListTensorboardRunsRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_runs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ListTensorboardRunsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_tensorboard_runs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ListTensorboardRunsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListTensorboardRunsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_tensorboard_runs_async_from_dict():
    await test_list_tensorboard_runs_async(request_type=dict)


def test_list_tensorboard_runs_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ListTensorboardRunsRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_runs), "__call__"
    ) as call:
        call.return_value = tensorboard_service.ListTensorboardRunsResponse()
        client.list_tensorboard_runs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_tensorboard_runs_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ListTensorboardRunsRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_runs), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ListTensorboardRunsResponse()
        )
        await client.list_tensorboard_runs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_tensorboard_runs_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_runs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.ListTensorboardRunsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_tensorboard_runs(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_tensorboard_runs_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_tensorboard_runs(
            tensorboard_service.ListTensorboardRunsRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_tensorboard_runs_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_runs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.ListTensorboardRunsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ListTensorboardRunsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_tensorboard_runs(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_tensorboard_runs_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_tensorboard_runs(
            tensorboard_service.ListTensorboardRunsRequest(), parent="parent_value",
        )


def test_list_tensorboard_runs_pager():
    client = TensorboardServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_runs), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tensorboard_service.ListTensorboardRunsResponse(
                tensorboard_runs=[
                    tensorboard_run.TensorboardRun(),
                    tensorboard_run.TensorboardRun(),
                    tensorboard_run.TensorboardRun(),
                ],
                next_page_token="abc",
            ),
            tensorboard_service.ListTensorboardRunsResponse(
                tensorboard_runs=[], next_page_token="def",
            ),
            tensorboard_service.ListTensorboardRunsResponse(
                tensorboard_runs=[tensorboard_run.TensorboardRun(),],
                next_page_token="ghi",
            ),
            tensorboard_service.ListTensorboardRunsResponse(
                tensorboard_runs=[
                    tensorboard_run.TensorboardRun(),
                    tensorboard_run.TensorboardRun(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_tensorboard_runs(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, tensorboard_run.TensorboardRun) for i in results)


def test_list_tensorboard_runs_pages():
    client = TensorboardServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_runs), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tensorboard_service.ListTensorboardRunsResponse(
                tensorboard_runs=[
                    tensorboard_run.TensorboardRun(),
                    tensorboard_run.TensorboardRun(),
                    tensorboard_run.TensorboardRun(),
                ],
                next_page_token="abc",
            ),
            tensorboard_service.ListTensorboardRunsResponse(
                tensorboard_runs=[], next_page_token="def",
            ),
            tensorboard_service.ListTensorboardRunsResponse(
                tensorboard_runs=[tensorboard_run.TensorboardRun(),],
                next_page_token="ghi",
            ),
            tensorboard_service.ListTensorboardRunsResponse(
                tensorboard_runs=[
                    tensorboard_run.TensorboardRun(),
                    tensorboard_run.TensorboardRun(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_tensorboard_runs(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_tensorboard_runs_async_pager():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_runs),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tensorboard_service.ListTensorboardRunsResponse(
                tensorboard_runs=[
                    tensorboard_run.TensorboardRun(),
                    tensorboard_run.TensorboardRun(),
                    tensorboard_run.TensorboardRun(),
                ],
                next_page_token="abc",
            ),
            tensorboard_service.ListTensorboardRunsResponse(
                tensorboard_runs=[], next_page_token="def",
            ),
            tensorboard_service.ListTensorboardRunsResponse(
                tensorboard_runs=[tensorboard_run.TensorboardRun(),],
                next_page_token="ghi",
            ),
            tensorboard_service.ListTensorboardRunsResponse(
                tensorboard_runs=[
                    tensorboard_run.TensorboardRun(),
                    tensorboard_run.TensorboardRun(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_tensorboard_runs(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, tensorboard_run.TensorboardRun) for i in responses)


@pytest.mark.asyncio
async def test_list_tensorboard_runs_async_pages():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_runs),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tensorboard_service.ListTensorboardRunsResponse(
                tensorboard_runs=[
                    tensorboard_run.TensorboardRun(),
                    tensorboard_run.TensorboardRun(),
                    tensorboard_run.TensorboardRun(),
                ],
                next_page_token="abc",
            ),
            tensorboard_service.ListTensorboardRunsResponse(
                tensorboard_runs=[], next_page_token="def",
            ),
            tensorboard_service.ListTensorboardRunsResponse(
                tensorboard_runs=[tensorboard_run.TensorboardRun(),],
                next_page_token="ghi",
            ),
            tensorboard_service.ListTensorboardRunsResponse(
                tensorboard_runs=[
                    tensorboard_run.TensorboardRun(),
                    tensorboard_run.TensorboardRun(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_tensorboard_runs(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_delete_tensorboard_run(
    transport: str = "grpc",
    request_type=tensorboard_service.DeleteTensorboardRunRequest,
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard_run), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_tensorboard_run(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.DeleteTensorboardRunRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_tensorboard_run_from_dict():
    test_delete_tensorboard_run(request_type=dict)


def test_delete_tensorboard_run_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard_run), "__call__"
    ) as call:
        client.delete_tensorboard_run()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.DeleteTensorboardRunRequest()


@pytest.mark.asyncio
async def test_delete_tensorboard_run_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.DeleteTensorboardRunRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard_run), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_tensorboard_run(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.DeleteTensorboardRunRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_tensorboard_run_async_from_dict():
    await test_delete_tensorboard_run_async(request_type=dict)


def test_delete_tensorboard_run_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.DeleteTensorboardRunRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard_run), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_tensorboard_run(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_tensorboard_run_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.DeleteTensorboardRunRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard_run), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_tensorboard_run(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_tensorboard_run_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard_run), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_tensorboard_run(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_tensorboard_run_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_tensorboard_run(
            tensorboard_service.DeleteTensorboardRunRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_tensorboard_run_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard_run), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_tensorboard_run(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_tensorboard_run_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_tensorboard_run(
            tensorboard_service.DeleteTensorboardRunRequest(), name="name_value",
        )


def test_create_tensorboard_time_series(
    transport: str = "grpc",
    request_type=tensorboard_service.CreateTensorboardTimeSeriesRequest,
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_tensorboard_time_series.TensorboardTimeSeries(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            value_type=gca_tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR,
            etag="etag_value",
            plugin_name="plugin_name_value",
            plugin_data=b"plugin_data_blob",
        )
        response = client.create_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.CreateTensorboardTimeSeriesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_tensorboard_time_series.TensorboardTimeSeries)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert (
        response.value_type
        == gca_tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR
    )
    assert response.etag == "etag_value"
    assert response.plugin_name == "plugin_name_value"
    assert response.plugin_data == b"plugin_data_blob"


def test_create_tensorboard_time_series_from_dict():
    test_create_tensorboard_time_series(request_type=dict)


def test_create_tensorboard_time_series_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard_time_series), "__call__"
    ) as call:
        client.create_tensorboard_time_series()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.CreateTensorboardTimeSeriesRequest()


@pytest.mark.asyncio
async def test_create_tensorboard_time_series_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.CreateTensorboardTimeSeriesRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_tensorboard_time_series.TensorboardTimeSeries(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
                value_type=gca_tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR,
                etag="etag_value",
                plugin_name="plugin_name_value",
                plugin_data=b"plugin_data_blob",
            )
        )
        response = await client.create_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.CreateTensorboardTimeSeriesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_tensorboard_time_series.TensorboardTimeSeries)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert (
        response.value_type
        == gca_tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR
    )
    assert response.etag == "etag_value"
    assert response.plugin_name == "plugin_name_value"
    assert response.plugin_data == b"plugin_data_blob"


@pytest.mark.asyncio
async def test_create_tensorboard_time_series_async_from_dict():
    await test_create_tensorboard_time_series_async(request_type=dict)


def test_create_tensorboard_time_series_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.CreateTensorboardTimeSeriesRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard_time_series), "__call__"
    ) as call:
        call.return_value = gca_tensorboard_time_series.TensorboardTimeSeries()
        client.create_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_tensorboard_time_series_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.CreateTensorboardTimeSeriesRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard_time_series), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_tensorboard_time_series.TensorboardTimeSeries()
        )
        await client.create_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_tensorboard_time_series_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_tensorboard_time_series.TensorboardTimeSeries()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_tensorboard_time_series(
            parent="parent_value",
            tensorboard_time_series=gca_tensorboard_time_series.TensorboardTimeSeries(
                name="name_value"
            ),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[
            0
        ].tensorboard_time_series == gca_tensorboard_time_series.TensorboardTimeSeries(
            name="name_value"
        )


def test_create_tensorboard_time_series_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_tensorboard_time_series(
            tensorboard_service.CreateTensorboardTimeSeriesRequest(),
            parent="parent_value",
            tensorboard_time_series=gca_tensorboard_time_series.TensorboardTimeSeries(
                name="name_value"
            ),
        )


@pytest.mark.asyncio
async def test_create_tensorboard_time_series_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_tensorboard_time_series.TensorboardTimeSeries()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_tensorboard_time_series.TensorboardTimeSeries()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_tensorboard_time_series(
            parent="parent_value",
            tensorboard_time_series=gca_tensorboard_time_series.TensorboardTimeSeries(
                name="name_value"
            ),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[
            0
        ].tensorboard_time_series == gca_tensorboard_time_series.TensorboardTimeSeries(
            name="name_value"
        )


@pytest.mark.asyncio
async def test_create_tensorboard_time_series_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_tensorboard_time_series(
            tensorboard_service.CreateTensorboardTimeSeriesRequest(),
            parent="parent_value",
            tensorboard_time_series=gca_tensorboard_time_series.TensorboardTimeSeries(
                name="name_value"
            ),
        )


def test_get_tensorboard_time_series(
    transport: str = "grpc",
    request_type=tensorboard_service.GetTensorboardTimeSeriesRequest,
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_time_series.TensorboardTimeSeries(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            value_type=tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR,
            etag="etag_value",
            plugin_name="plugin_name_value",
            plugin_data=b"plugin_data_blob",
        )
        response = client.get_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.GetTensorboardTimeSeriesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, tensorboard_time_series.TensorboardTimeSeries)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert (
        response.value_type
        == tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR
    )
    assert response.etag == "etag_value"
    assert response.plugin_name == "plugin_name_value"
    assert response.plugin_data == b"plugin_data_blob"


def test_get_tensorboard_time_series_from_dict():
    test_get_tensorboard_time_series(request_type=dict)


def test_get_tensorboard_time_series_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_tensorboard_time_series), "__call__"
    ) as call:
        client.get_tensorboard_time_series()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.GetTensorboardTimeSeriesRequest()


@pytest.mark.asyncio
async def test_get_tensorboard_time_series_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.GetTensorboardTimeSeriesRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_time_series.TensorboardTimeSeries(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
                value_type=tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR,
                etag="etag_value",
                plugin_name="plugin_name_value",
                plugin_data=b"plugin_data_blob",
            )
        )
        response = await client.get_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.GetTensorboardTimeSeriesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, tensorboard_time_series.TensorboardTimeSeries)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert (
        response.value_type
        == tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR
    )
    assert response.etag == "etag_value"
    assert response.plugin_name == "plugin_name_value"
    assert response.plugin_data == b"plugin_data_blob"


@pytest.mark.asyncio
async def test_get_tensorboard_time_series_async_from_dict():
    await test_get_tensorboard_time_series_async(request_type=dict)


def test_get_tensorboard_time_series_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.GetTensorboardTimeSeriesRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_tensorboard_time_series), "__call__"
    ) as call:
        call.return_value = tensorboard_time_series.TensorboardTimeSeries()
        client.get_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_tensorboard_time_series_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.GetTensorboardTimeSeriesRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_tensorboard_time_series), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_time_series.TensorboardTimeSeries()
        )
        await client.get_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_tensorboard_time_series_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_time_series.TensorboardTimeSeries()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_tensorboard_time_series(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_tensorboard_time_series_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_tensorboard_time_series(
            tensorboard_service.GetTensorboardTimeSeriesRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_tensorboard_time_series_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_time_series.TensorboardTimeSeries()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_time_series.TensorboardTimeSeries()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_tensorboard_time_series(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_tensorboard_time_series_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_tensorboard_time_series(
            tensorboard_service.GetTensorboardTimeSeriesRequest(), name="name_value",
        )


def test_update_tensorboard_time_series(
    transport: str = "grpc",
    request_type=tensorboard_service.UpdateTensorboardTimeSeriesRequest,
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_tensorboard_time_series.TensorboardTimeSeries(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            value_type=gca_tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR,
            etag="etag_value",
            plugin_name="plugin_name_value",
            plugin_data=b"plugin_data_blob",
        )
        response = client.update_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.UpdateTensorboardTimeSeriesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_tensorboard_time_series.TensorboardTimeSeries)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert (
        response.value_type
        == gca_tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR
    )
    assert response.etag == "etag_value"
    assert response.plugin_name == "plugin_name_value"
    assert response.plugin_data == b"plugin_data_blob"


def test_update_tensorboard_time_series_from_dict():
    test_update_tensorboard_time_series(request_type=dict)


def test_update_tensorboard_time_series_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard_time_series), "__call__"
    ) as call:
        client.update_tensorboard_time_series()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.UpdateTensorboardTimeSeriesRequest()


@pytest.mark.asyncio
async def test_update_tensorboard_time_series_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.UpdateTensorboardTimeSeriesRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_tensorboard_time_series.TensorboardTimeSeries(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
                value_type=gca_tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR,
                etag="etag_value",
                plugin_name="plugin_name_value",
                plugin_data=b"plugin_data_blob",
            )
        )
        response = await client.update_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.UpdateTensorboardTimeSeriesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_tensorboard_time_series.TensorboardTimeSeries)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert (
        response.value_type
        == gca_tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR
    )
    assert response.etag == "etag_value"
    assert response.plugin_name == "plugin_name_value"
    assert response.plugin_data == b"plugin_data_blob"


@pytest.mark.asyncio
async def test_update_tensorboard_time_series_async_from_dict():
    await test_update_tensorboard_time_series_async(request_type=dict)


def test_update_tensorboard_time_series_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.UpdateTensorboardTimeSeriesRequest()

    request.tensorboard_time_series.name = "tensorboard_time_series.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard_time_series), "__call__"
    ) as call:
        call.return_value = gca_tensorboard_time_series.TensorboardTimeSeries()
        client.update_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "tensorboard_time_series.name=tensorboard_time_series.name/value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_tensorboard_time_series_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.UpdateTensorboardTimeSeriesRequest()

    request.tensorboard_time_series.name = "tensorboard_time_series.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard_time_series), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_tensorboard_time_series.TensorboardTimeSeries()
        )
        await client.update_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "tensorboard_time_series.name=tensorboard_time_series.name/value",
    ) in kw["metadata"]


def test_update_tensorboard_time_series_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_tensorboard_time_series.TensorboardTimeSeries()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_tensorboard_time_series(
            tensorboard_time_series=gca_tensorboard_time_series.TensorboardTimeSeries(
                name="name_value"
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[
            0
        ].tensorboard_time_series == gca_tensorboard_time_series.TensorboardTimeSeries(
            name="name_value"
        )
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


def test_update_tensorboard_time_series_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_tensorboard_time_series(
            tensorboard_service.UpdateTensorboardTimeSeriesRequest(),
            tensorboard_time_series=gca_tensorboard_time_series.TensorboardTimeSeries(
                name="name_value"
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_tensorboard_time_series_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_tensorboard_time_series.TensorboardTimeSeries()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_tensorboard_time_series.TensorboardTimeSeries()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_tensorboard_time_series(
            tensorboard_time_series=gca_tensorboard_time_series.TensorboardTimeSeries(
                name="name_value"
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[
            0
        ].tensorboard_time_series == gca_tensorboard_time_series.TensorboardTimeSeries(
            name="name_value"
        )
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


@pytest.mark.asyncio
async def test_update_tensorboard_time_series_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_tensorboard_time_series(
            tensorboard_service.UpdateTensorboardTimeSeriesRequest(),
            tensorboard_time_series=gca_tensorboard_time_series.TensorboardTimeSeries(
                name="name_value"
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


def test_list_tensorboard_time_series(
    transport: str = "grpc",
    request_type=tensorboard_service.ListTensorboardTimeSeriesRequest,
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.ListTensorboardTimeSeriesResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ListTensorboardTimeSeriesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListTensorboardTimeSeriesPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_tensorboard_time_series_from_dict():
    test_list_tensorboard_time_series(request_type=dict)


def test_list_tensorboard_time_series_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_time_series), "__call__"
    ) as call:
        client.list_tensorboard_time_series()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ListTensorboardTimeSeriesRequest()


@pytest.mark.asyncio
async def test_list_tensorboard_time_series_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.ListTensorboardTimeSeriesRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ListTensorboardTimeSeriesResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ListTensorboardTimeSeriesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListTensorboardTimeSeriesAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_tensorboard_time_series_async_from_dict():
    await test_list_tensorboard_time_series_async(request_type=dict)


def test_list_tensorboard_time_series_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ListTensorboardTimeSeriesRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_time_series), "__call__"
    ) as call:
        call.return_value = tensorboard_service.ListTensorboardTimeSeriesResponse()
        client.list_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_tensorboard_time_series_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ListTensorboardTimeSeriesRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_time_series), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ListTensorboardTimeSeriesResponse()
        )
        await client.list_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_tensorboard_time_series_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.ListTensorboardTimeSeriesResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_tensorboard_time_series(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_tensorboard_time_series_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_tensorboard_time_series(
            tensorboard_service.ListTensorboardTimeSeriesRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_tensorboard_time_series_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.ListTensorboardTimeSeriesResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ListTensorboardTimeSeriesResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_tensorboard_time_series(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_tensorboard_time_series_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_tensorboard_time_series(
            tensorboard_service.ListTensorboardTimeSeriesRequest(),
            parent="parent_value",
        )


def test_list_tensorboard_time_series_pager():
    client = TensorboardServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_time_series), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tensorboard_service.ListTensorboardTimeSeriesResponse(
                tensorboard_time_series=[
                    tensorboard_time_series.TensorboardTimeSeries(),
                    tensorboard_time_series.TensorboardTimeSeries(),
                    tensorboard_time_series.TensorboardTimeSeries(),
                ],
                next_page_token="abc",
            ),
            tensorboard_service.ListTensorboardTimeSeriesResponse(
                tensorboard_time_series=[], next_page_token="def",
            ),
            tensorboard_service.ListTensorboardTimeSeriesResponse(
                tensorboard_time_series=[
                    tensorboard_time_series.TensorboardTimeSeries(),
                ],
                next_page_token="ghi",
            ),
            tensorboard_service.ListTensorboardTimeSeriesResponse(
                tensorboard_time_series=[
                    tensorboard_time_series.TensorboardTimeSeries(),
                    tensorboard_time_series.TensorboardTimeSeries(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_tensorboard_time_series(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(
            isinstance(i, tensorboard_time_series.TensorboardTimeSeries)
            for i in results
        )


def test_list_tensorboard_time_series_pages():
    client = TensorboardServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_time_series), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tensorboard_service.ListTensorboardTimeSeriesResponse(
                tensorboard_time_series=[
                    tensorboard_time_series.TensorboardTimeSeries(),
                    tensorboard_time_series.TensorboardTimeSeries(),
                    tensorboard_time_series.TensorboardTimeSeries(),
                ],
                next_page_token="abc",
            ),
            tensorboard_service.ListTensorboardTimeSeriesResponse(
                tensorboard_time_series=[], next_page_token="def",
            ),
            tensorboard_service.ListTensorboardTimeSeriesResponse(
                tensorboard_time_series=[
                    tensorboard_time_series.TensorboardTimeSeries(),
                ],
                next_page_token="ghi",
            ),
            tensorboard_service.ListTensorboardTimeSeriesResponse(
                tensorboard_time_series=[
                    tensorboard_time_series.TensorboardTimeSeries(),
                    tensorboard_time_series.TensorboardTimeSeries(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_tensorboard_time_series(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_tensorboard_time_series_async_pager():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_time_series),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tensorboard_service.ListTensorboardTimeSeriesResponse(
                tensorboard_time_series=[
                    tensorboard_time_series.TensorboardTimeSeries(),
                    tensorboard_time_series.TensorboardTimeSeries(),
                    tensorboard_time_series.TensorboardTimeSeries(),
                ],
                next_page_token="abc",
            ),
            tensorboard_service.ListTensorboardTimeSeriesResponse(
                tensorboard_time_series=[], next_page_token="def",
            ),
            tensorboard_service.ListTensorboardTimeSeriesResponse(
                tensorboard_time_series=[
                    tensorboard_time_series.TensorboardTimeSeries(),
                ],
                next_page_token="ghi",
            ),
            tensorboard_service.ListTensorboardTimeSeriesResponse(
                tensorboard_time_series=[
                    tensorboard_time_series.TensorboardTimeSeries(),
                    tensorboard_time_series.TensorboardTimeSeries(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_tensorboard_time_series(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(
            isinstance(i, tensorboard_time_series.TensorboardTimeSeries)
            for i in responses
        )


@pytest.mark.asyncio
async def test_list_tensorboard_time_series_async_pages():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_tensorboard_time_series),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tensorboard_service.ListTensorboardTimeSeriesResponse(
                tensorboard_time_series=[
                    tensorboard_time_series.TensorboardTimeSeries(),
                    tensorboard_time_series.TensorboardTimeSeries(),
                    tensorboard_time_series.TensorboardTimeSeries(),
                ],
                next_page_token="abc",
            ),
            tensorboard_service.ListTensorboardTimeSeriesResponse(
                tensorboard_time_series=[], next_page_token="def",
            ),
            tensorboard_service.ListTensorboardTimeSeriesResponse(
                tensorboard_time_series=[
                    tensorboard_time_series.TensorboardTimeSeries(),
                ],
                next_page_token="ghi",
            ),
            tensorboard_service.ListTensorboardTimeSeriesResponse(
                tensorboard_time_series=[
                    tensorboard_time_series.TensorboardTimeSeries(),
                    tensorboard_time_series.TensorboardTimeSeries(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (
            await client.list_tensorboard_time_series(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_delete_tensorboard_time_series(
    transport: str = "grpc",
    request_type=tensorboard_service.DeleteTensorboardTimeSeriesRequest,
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.DeleteTensorboardTimeSeriesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_tensorboard_time_series_from_dict():
    test_delete_tensorboard_time_series(request_type=dict)


def test_delete_tensorboard_time_series_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard_time_series), "__call__"
    ) as call:
        client.delete_tensorboard_time_series()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.DeleteTensorboardTimeSeriesRequest()


@pytest.mark.asyncio
async def test_delete_tensorboard_time_series_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.DeleteTensorboardTimeSeriesRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.DeleteTensorboardTimeSeriesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_tensorboard_time_series_async_from_dict():
    await test_delete_tensorboard_time_series_async(request_type=dict)


def test_delete_tensorboard_time_series_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.DeleteTensorboardTimeSeriesRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard_time_series), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_tensorboard_time_series_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.DeleteTensorboardTimeSeriesRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard_time_series), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_tensorboard_time_series_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_tensorboard_time_series(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_tensorboard_time_series_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_tensorboard_time_series(
            tensorboard_service.DeleteTensorboardTimeSeriesRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_tensorboard_time_series_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_tensorboard_time_series(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_tensorboard_time_series_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_tensorboard_time_series(
            tensorboard_service.DeleteTensorboardTimeSeriesRequest(), name="name_value",
        )


def test_read_tensorboard_time_series_data(
    transport: str = "grpc",
    request_type=tensorboard_service.ReadTensorboardTimeSeriesDataRequest,
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_time_series_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.ReadTensorboardTimeSeriesDataResponse()
        response = client.read_tensorboard_time_series_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ReadTensorboardTimeSeriesDataRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, tensorboard_service.ReadTensorboardTimeSeriesDataResponse
    )


def test_read_tensorboard_time_series_data_from_dict():
    test_read_tensorboard_time_series_data(request_type=dict)


def test_read_tensorboard_time_series_data_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_time_series_data), "__call__"
    ) as call:
        client.read_tensorboard_time_series_data()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ReadTensorboardTimeSeriesDataRequest()


@pytest.mark.asyncio
async def test_read_tensorboard_time_series_data_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.ReadTensorboardTimeSeriesDataRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_time_series_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ReadTensorboardTimeSeriesDataResponse()
        )
        response = await client.read_tensorboard_time_series_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ReadTensorboardTimeSeriesDataRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, tensorboard_service.ReadTensorboardTimeSeriesDataResponse
    )


@pytest.mark.asyncio
async def test_read_tensorboard_time_series_data_async_from_dict():
    await test_read_tensorboard_time_series_data_async(request_type=dict)


def test_read_tensorboard_time_series_data_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ReadTensorboardTimeSeriesDataRequest()

    request.tensorboard_time_series = "tensorboard_time_series/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_time_series_data), "__call__"
    ) as call:
        call.return_value = tensorboard_service.ReadTensorboardTimeSeriesDataResponse()
        client.read_tensorboard_time_series_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "tensorboard_time_series=tensorboard_time_series/value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_read_tensorboard_time_series_data_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ReadTensorboardTimeSeriesDataRequest()

    request.tensorboard_time_series = "tensorboard_time_series/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_time_series_data), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ReadTensorboardTimeSeriesDataResponse()
        )
        await client.read_tensorboard_time_series_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "tensorboard_time_series=tensorboard_time_series/value",
    ) in kw["metadata"]


def test_read_tensorboard_time_series_data_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_time_series_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.ReadTensorboardTimeSeriesDataResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.read_tensorboard_time_series_data(
            tensorboard_time_series="tensorboard_time_series_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].tensorboard_time_series == "tensorboard_time_series_value"


def test_read_tensorboard_time_series_data_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.read_tensorboard_time_series_data(
            tensorboard_service.ReadTensorboardTimeSeriesDataRequest(),
            tensorboard_time_series="tensorboard_time_series_value",
        )


@pytest.mark.asyncio
async def test_read_tensorboard_time_series_data_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_time_series_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.ReadTensorboardTimeSeriesDataResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ReadTensorboardTimeSeriesDataResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.read_tensorboard_time_series_data(
            tensorboard_time_series="tensorboard_time_series_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].tensorboard_time_series == "tensorboard_time_series_value"


@pytest.mark.asyncio
async def test_read_tensorboard_time_series_data_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.read_tensorboard_time_series_data(
            tensorboard_service.ReadTensorboardTimeSeriesDataRequest(),
            tensorboard_time_series="tensorboard_time_series_value",
        )


def test_read_tensorboard_blob_data(
    transport: str = "grpc",
    request_type=tensorboard_service.ReadTensorboardBlobDataRequest,
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_blob_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = iter(
            [tensorboard_service.ReadTensorboardBlobDataResponse()]
        )
        response = client.read_tensorboard_blob_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ReadTensorboardBlobDataRequest()

    # Establish that the response is the type that we expect.
    for message in response:
        assert isinstance(message, tensorboard_service.ReadTensorboardBlobDataResponse)


def test_read_tensorboard_blob_data_from_dict():
    test_read_tensorboard_blob_data(request_type=dict)


def test_read_tensorboard_blob_data_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_blob_data), "__call__"
    ) as call:
        client.read_tensorboard_blob_data()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ReadTensorboardBlobDataRequest()


@pytest.mark.asyncio
async def test_read_tensorboard_blob_data_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.ReadTensorboardBlobDataRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_blob_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = mock.Mock(aio.UnaryStreamCall, autospec=True)
        call.return_value.read = mock.AsyncMock(
            side_effect=[tensorboard_service.ReadTensorboardBlobDataResponse()]
        )
        response = await client.read_tensorboard_blob_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ReadTensorboardBlobDataRequest()

    # Establish that the response is the type that we expect.
    message = await response.read()
    assert isinstance(message, tensorboard_service.ReadTensorboardBlobDataResponse)


@pytest.mark.asyncio
async def test_read_tensorboard_blob_data_async_from_dict():
    await test_read_tensorboard_blob_data_async(request_type=dict)


def test_read_tensorboard_blob_data_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ReadTensorboardBlobDataRequest()

    request.time_series = "time_series/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_blob_data), "__call__"
    ) as call:
        call.return_value = iter(
            [tensorboard_service.ReadTensorboardBlobDataResponse()]
        )
        client.read_tensorboard_blob_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "time_series=time_series/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_read_tensorboard_blob_data_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ReadTensorboardBlobDataRequest()

    request.time_series = "time_series/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_blob_data), "__call__"
    ) as call:
        call.return_value = mock.Mock(aio.UnaryStreamCall, autospec=True)
        call.return_value.read = mock.AsyncMock(
            side_effect=[tensorboard_service.ReadTensorboardBlobDataResponse()]
        )
        await client.read_tensorboard_blob_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "time_series=time_series/value",) in kw["metadata"]


def test_read_tensorboard_blob_data_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_blob_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = iter(
            [tensorboard_service.ReadTensorboardBlobDataResponse()]
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.read_tensorboard_blob_data(time_series="time_series_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].time_series == "time_series_value"


def test_read_tensorboard_blob_data_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.read_tensorboard_blob_data(
            tensorboard_service.ReadTensorboardBlobDataRequest(),
            time_series="time_series_value",
        )


@pytest.mark.asyncio
async def test_read_tensorboard_blob_data_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_blob_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = iter(
            [tensorboard_service.ReadTensorboardBlobDataResponse()]
        )

        call.return_value = mock.Mock(aio.UnaryStreamCall, autospec=True)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.read_tensorboard_blob_data(
            time_series="time_series_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].time_series == "time_series_value"


@pytest.mark.asyncio
async def test_read_tensorboard_blob_data_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.read_tensorboard_blob_data(
            tensorboard_service.ReadTensorboardBlobDataRequest(),
            time_series="time_series_value",
        )


def test_write_tensorboard_run_data(
    transport: str = "grpc",
    request_type=tensorboard_service.WriteTensorboardRunDataRequest,
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.write_tensorboard_run_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.WriteTensorboardRunDataResponse()
        response = client.write_tensorboard_run_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.WriteTensorboardRunDataRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, tensorboard_service.WriteTensorboardRunDataResponse)


def test_write_tensorboard_run_data_from_dict():
    test_write_tensorboard_run_data(request_type=dict)


def test_write_tensorboard_run_data_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.write_tensorboard_run_data), "__call__"
    ) as call:
        client.write_tensorboard_run_data()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.WriteTensorboardRunDataRequest()


@pytest.mark.asyncio
async def test_write_tensorboard_run_data_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.WriteTensorboardRunDataRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.write_tensorboard_run_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.WriteTensorboardRunDataResponse()
        )
        response = await client.write_tensorboard_run_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.WriteTensorboardRunDataRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, tensorboard_service.WriteTensorboardRunDataResponse)


@pytest.mark.asyncio
async def test_write_tensorboard_run_data_async_from_dict():
    await test_write_tensorboard_run_data_async(request_type=dict)


def test_write_tensorboard_run_data_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.WriteTensorboardRunDataRequest()

    request.tensorboard_run = "tensorboard_run/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.write_tensorboard_run_data), "__call__"
    ) as call:
        call.return_value = tensorboard_service.WriteTensorboardRunDataResponse()
        client.write_tensorboard_run_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "tensorboard_run=tensorboard_run/value",) in kw[
        "metadata"
    ]


@pytest.mark.asyncio
async def test_write_tensorboard_run_data_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.WriteTensorboardRunDataRequest()

    request.tensorboard_run = "tensorboard_run/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.write_tensorboard_run_data), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.WriteTensorboardRunDataResponse()
        )
        await client.write_tensorboard_run_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "tensorboard_run=tensorboard_run/value",) in kw[
        "metadata"
    ]


def test_write_tensorboard_run_data_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.write_tensorboard_run_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.WriteTensorboardRunDataResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.write_tensorboard_run_data(
            tensorboard_run="tensorboard_run_value",
            time_series_data=[
                tensorboard_data.TimeSeriesData(
                    tensorboard_time_series_id="tensorboard_time_series_id_value"
                )
            ],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].tensorboard_run == "tensorboard_run_value"
        assert args[0].time_series_data == [
            tensorboard_data.TimeSeriesData(
                tensorboard_time_series_id="tensorboard_time_series_id_value"
            )
        ]


def test_write_tensorboard_run_data_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.write_tensorboard_run_data(
            tensorboard_service.WriteTensorboardRunDataRequest(),
            tensorboard_run="tensorboard_run_value",
            time_series_data=[
                tensorboard_data.TimeSeriesData(
                    tensorboard_time_series_id="tensorboard_time_series_id_value"
                )
            ],
        )


@pytest.mark.asyncio
async def test_write_tensorboard_run_data_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.write_tensorboard_run_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.WriteTensorboardRunDataResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.WriteTensorboardRunDataResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.write_tensorboard_run_data(
            tensorboard_run="tensorboard_run_value",
            time_series_data=[
                tensorboard_data.TimeSeriesData(
                    tensorboard_time_series_id="tensorboard_time_series_id_value"
                )
            ],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].tensorboard_run == "tensorboard_run_value"
        assert args[0].time_series_data == [
            tensorboard_data.TimeSeriesData(
                tensorboard_time_series_id="tensorboard_time_series_id_value"
            )
        ]


@pytest.mark.asyncio
async def test_write_tensorboard_run_data_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.write_tensorboard_run_data(
            tensorboard_service.WriteTensorboardRunDataRequest(),
            tensorboard_run="tensorboard_run_value",
            time_series_data=[
                tensorboard_data.TimeSeriesData(
                    tensorboard_time_series_id="tensorboard_time_series_id_value"
                )
            ],
        )


def test_export_tensorboard_time_series_data(
    transport: str = "grpc",
    request_type=tensorboard_service.ExportTensorboardTimeSeriesDataRequest,
):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.export_tensorboard_time_series_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.ExportTensorboardTimeSeriesDataResponse(
            next_page_token="next_page_token_value",
        )
        response = client.export_tensorboard_time_series_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ExportTensorboardTimeSeriesDataRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ExportTensorboardTimeSeriesDataPager)
    assert response.next_page_token == "next_page_token_value"


def test_export_tensorboard_time_series_data_from_dict():
    test_export_tensorboard_time_series_data(request_type=dict)


def test_export_tensorboard_time_series_data_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.export_tensorboard_time_series_data), "__call__"
    ) as call:
        client.export_tensorboard_time_series_data()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ExportTensorboardTimeSeriesDataRequest()


@pytest.mark.asyncio
async def test_export_tensorboard_time_series_data_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.ExportTensorboardTimeSeriesDataRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.export_tensorboard_time_series_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.export_tensorboard_time_series_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ExportTensorboardTimeSeriesDataRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ExportTensorboardTimeSeriesDataAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_export_tensorboard_time_series_data_async_from_dict():
    await test_export_tensorboard_time_series_data_async(request_type=dict)


def test_export_tensorboard_time_series_data_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ExportTensorboardTimeSeriesDataRequest()

    request.tensorboard_time_series = "tensorboard_time_series/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.export_tensorboard_time_series_data), "__call__"
    ) as call:
        call.return_value = (
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse()
        )
        client.export_tensorboard_time_series_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "tensorboard_time_series=tensorboard_time_series/value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_export_tensorboard_time_series_data_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ExportTensorboardTimeSeriesDataRequest()

    request.tensorboard_time_series = "tensorboard_time_series/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.export_tensorboard_time_series_data), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse()
        )
        await client.export_tensorboard_time_series_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "tensorboard_time_series=tensorboard_time_series/value",
    ) in kw["metadata"]


def test_export_tensorboard_time_series_data_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.export_tensorboard_time_series_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.export_tensorboard_time_series_data(
            tensorboard_time_series="tensorboard_time_series_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].tensorboard_time_series == "tensorboard_time_series_value"


def test_export_tensorboard_time_series_data_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.export_tensorboard_time_series_data(
            tensorboard_service.ExportTensorboardTimeSeriesDataRequest(),
            tensorboard_time_series="tensorboard_time_series_value",
        )


@pytest.mark.asyncio
async def test_export_tensorboard_time_series_data_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.export_tensorboard_time_series_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse()
        )

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.export_tensorboard_time_series_data(
            tensorboard_time_series="tensorboard_time_series_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].tensorboard_time_series == "tensorboard_time_series_value"


@pytest.mark.asyncio
async def test_export_tensorboard_time_series_data_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.export_tensorboard_time_series_data(
            tensorboard_service.ExportTensorboardTimeSeriesDataRequest(),
            tensorboard_time_series="tensorboard_time_series_value",
        )


def test_export_tensorboard_time_series_data_pager():
    client = TensorboardServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.export_tensorboard_time_series_data), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse(
                time_series_data_points=[
                    tensorboard_data.TimeSeriesDataPoint(),
                    tensorboard_data.TimeSeriesDataPoint(),
                    tensorboard_data.TimeSeriesDataPoint(),
                ],
                next_page_token="abc",
            ),
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse(
                time_series_data_points=[], next_page_token="def",
            ),
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse(
                time_series_data_points=[tensorboard_data.TimeSeriesDataPoint(),],
                next_page_token="ghi",
            ),
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse(
                time_series_data_points=[
                    tensorboard_data.TimeSeriesDataPoint(),
                    tensorboard_data.TimeSeriesDataPoint(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("tensorboard_time_series", ""),)
            ),
        )
        pager = client.export_tensorboard_time_series_data(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, tensorboard_data.TimeSeriesDataPoint) for i in results)


def test_export_tensorboard_time_series_data_pages():
    client = TensorboardServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.export_tensorboard_time_series_data), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse(
                time_series_data_points=[
                    tensorboard_data.TimeSeriesDataPoint(),
                    tensorboard_data.TimeSeriesDataPoint(),
                    tensorboard_data.TimeSeriesDataPoint(),
                ],
                next_page_token="abc",
            ),
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse(
                time_series_data_points=[], next_page_token="def",
            ),
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse(
                time_series_data_points=[tensorboard_data.TimeSeriesDataPoint(),],
                next_page_token="ghi",
            ),
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse(
                time_series_data_points=[
                    tensorboard_data.TimeSeriesDataPoint(),
                    tensorboard_data.TimeSeriesDataPoint(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.export_tensorboard_time_series_data(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_export_tensorboard_time_series_data_async_pager():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.export_tensorboard_time_series_data),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse(
                time_series_data_points=[
                    tensorboard_data.TimeSeriesDataPoint(),
                    tensorboard_data.TimeSeriesDataPoint(),
                    tensorboard_data.TimeSeriesDataPoint(),
                ],
                next_page_token="abc",
            ),
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse(
                time_series_data_points=[], next_page_token="def",
            ),
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse(
                time_series_data_points=[tensorboard_data.TimeSeriesDataPoint(),],
                next_page_token="ghi",
            ),
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse(
                time_series_data_points=[
                    tensorboard_data.TimeSeriesDataPoint(),
                    tensorboard_data.TimeSeriesDataPoint(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.export_tensorboard_time_series_data(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(
            isinstance(i, tensorboard_data.TimeSeriesDataPoint) for i in responses
        )


@pytest.mark.asyncio
async def test_export_tensorboard_time_series_data_async_pages():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.export_tensorboard_time_series_data),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse(
                time_series_data_points=[
                    tensorboard_data.TimeSeriesDataPoint(),
                    tensorboard_data.TimeSeriesDataPoint(),
                    tensorboard_data.TimeSeriesDataPoint(),
                ],
                next_page_token="abc",
            ),
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse(
                time_series_data_points=[], next_page_token="def",
            ),
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse(
                time_series_data_points=[tensorboard_data.TimeSeriesDataPoint(),],
                next_page_token="ghi",
            ),
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse(
                time_series_data_points=[
                    tensorboard_data.TimeSeriesDataPoint(),
                    tensorboard_data.TimeSeriesDataPoint(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (
            await client.export_tensorboard_time_series_data(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.TensorboardServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = TensorboardServiceClient(
            credentials=ga_credentials.AnonymousCredentials(), transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.TensorboardServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = TensorboardServiceClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.TensorboardServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = TensorboardServiceClient(
            client_options={"scopes": ["1", "2"]}, transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.TensorboardServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    client = TensorboardServiceClient(transport=transport)
    assert client.transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.TensorboardServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.TensorboardServiceGrpcAsyncIOTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.TensorboardServiceGrpcTransport,
        transports.TensorboardServiceGrpcAsyncIOTransport,
    ],
)
def test_transport_adc(transport_class):
    # Test default credentials are used if not provided.
    with mock.patch.object(google.auth, "default") as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport_class()
        adc.assert_called_once()


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    assert isinstance(client.transport, transports.TensorboardServiceGrpcTransport,)


def test_tensorboard_service_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(core_exceptions.DuplicateCredentialArgs):
        transport = transports.TensorboardServiceTransport(
            credentials=ga_credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_tensorboard_service_base_transport():
    # Instantiate the base transport.
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.tensorboard_service.transports.TensorboardServiceTransport.__init__"
    ) as Transport:
        Transport.return_value = None
        transport = transports.TensorboardServiceTransport(
            credentials=ga_credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "create_tensorboard",
        "get_tensorboard",
        "update_tensorboard",
        "list_tensorboards",
        "delete_tensorboard",
        "create_tensorboard_experiment",
        "get_tensorboard_experiment",
        "update_tensorboard_experiment",
        "list_tensorboard_experiments",
        "delete_tensorboard_experiment",
        "create_tensorboard_run",
        "get_tensorboard_run",
        "update_tensorboard_run",
        "list_tensorboard_runs",
        "delete_tensorboard_run",
        "create_tensorboard_time_series",
        "get_tensorboard_time_series",
        "update_tensorboard_time_series",
        "list_tensorboard_time_series",
        "delete_tensorboard_time_series",
        "read_tensorboard_time_series_data",
        "read_tensorboard_blob_data",
        "write_tensorboard_run_data",
        "export_tensorboard_time_series_data",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    # Additionally, the LRO client (a property) should
    # also raise NotImplementedError
    with pytest.raises(NotImplementedError):
        transport.operations_client


@requires_google_auth_gte_1_25_0
def test_tensorboard_service_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        google.auth, "load_credentials_from_file", autospec=True
    ) as load_creds, mock.patch(
        "google.cloud.aiplatform_v1beta1.services.tensorboard_service.transports.TensorboardServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.TensorboardServiceTransport(
            credentials_file="credentials.json", quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=None,
            default_scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


@requires_google_auth_lt_1_25_0
def test_tensorboard_service_base_transport_with_credentials_file_old_google_auth():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        google.auth, "load_credentials_from_file", autospec=True
    ) as load_creds, mock.patch(
        "google.cloud.aiplatform_v1beta1.services.tensorboard_service.transports.TensorboardServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.TensorboardServiceTransport(
            credentials_file="credentials.json", quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


def test_tensorboard_service_base_transport_with_adc():
    # Test the default credentials are used if credentials and credentials_file are None.
    with mock.patch.object(google.auth, "default", autospec=True) as adc, mock.patch(
        "google.cloud.aiplatform_v1beta1.services.tensorboard_service.transports.TensorboardServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.TensorboardServiceTransport()
        adc.assert_called_once()


@requires_google_auth_gte_1_25_0
def test_tensorboard_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        TensorboardServiceClient()
        adc.assert_called_once_with(
            scopes=None,
            default_scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id=None,
        )


@requires_google_auth_lt_1_25_0
def test_tensorboard_service_auth_adc_old_google_auth():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        TensorboardServiceClient()
        adc.assert_called_once_with(
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id=None,
        )


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.TensorboardServiceGrpcTransport,
        transports.TensorboardServiceGrpcAsyncIOTransport,
    ],
)
@requires_google_auth_gte_1_25_0
def test_tensorboard_service_transport_auth_adc(transport_class):
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport_class(quota_project_id="octopus", scopes=["1", "2"])
        adc.assert_called_once_with(
            scopes=["1", "2"],
            default_scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.TensorboardServiceGrpcTransport,
        transports.TensorboardServiceGrpcAsyncIOTransport,
    ],
)
@requires_google_auth_lt_1_25_0
def test_tensorboard_service_transport_auth_adc_old_google_auth(transport_class):
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport_class(quota_project_id="octopus")
        adc.assert_called_once_with(
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


@pytest.mark.parametrize(
    "transport_class,grpc_helpers",
    [
        (transports.TensorboardServiceGrpcTransport, grpc_helpers),
        (transports.TensorboardServiceGrpcAsyncIOTransport, grpc_helpers_async),
    ],
)
@requires_api_core_gte_1_26_0
def test_tensorboard_service_transport_create_channel(transport_class, grpc_helpers):
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(
        google.auth, "default", autospec=True
    ) as adc, mock.patch.object(
        grpc_helpers, "create_channel", autospec=True
    ) as create_channel:
        creds = ga_credentials.AnonymousCredentials()
        adc.return_value = (creds, None)
        transport_class(quota_project_id="octopus", scopes=["1", "2"])

        create_channel.assert_called_with(
            "aiplatform.googleapis.com:443",
            credentials=creds,
            credentials_file=None,
            quota_project_id="octopus",
            default_scopes=("https://www.googleapis.com/auth/cloud-platform",),
            scopes=["1", "2"],
            default_host="aiplatform.googleapis.com",
            ssl_credentials=None,
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
            ],
        )


@pytest.mark.parametrize(
    "transport_class,grpc_helpers",
    [
        (transports.TensorboardServiceGrpcTransport, grpc_helpers),
        (transports.TensorboardServiceGrpcAsyncIOTransport, grpc_helpers_async),
    ],
)
@requires_api_core_lt_1_26_0
def test_tensorboard_service_transport_create_channel_old_api_core(
    transport_class, grpc_helpers
):
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(
        google.auth, "default", autospec=True
    ) as adc, mock.patch.object(
        grpc_helpers, "create_channel", autospec=True
    ) as create_channel:
        creds = ga_credentials.AnonymousCredentials()
        adc.return_value = (creds, None)
        transport_class(quota_project_id="octopus")

        create_channel.assert_called_with(
            "aiplatform.googleapis.com:443",
            credentials=creds,
            credentials_file=None,
            quota_project_id="octopus",
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            ssl_credentials=None,
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
            ],
        )


@pytest.mark.parametrize(
    "transport_class,grpc_helpers",
    [
        (transports.TensorboardServiceGrpcTransport, grpc_helpers),
        (transports.TensorboardServiceGrpcAsyncIOTransport, grpc_helpers_async),
    ],
)
@requires_api_core_lt_1_26_0
def test_tensorboard_service_transport_create_channel_user_scopes(
    transport_class, grpc_helpers
):
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(
        google.auth, "default", autospec=True
    ) as adc, mock.patch.object(
        grpc_helpers, "create_channel", autospec=True
    ) as create_channel:
        creds = ga_credentials.AnonymousCredentials()
        adc.return_value = (creds, None)

        transport_class(quota_project_id="octopus", scopes=["1", "2"])

        create_channel.assert_called_with(
            "aiplatform.googleapis.com:443",
            credentials=creds,
            credentials_file=None,
            quota_project_id="octopus",
            scopes=["1", "2"],
            ssl_credentials=None,
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
            ],
        )


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.TensorboardServiceGrpcTransport,
        transports.TensorboardServiceGrpcAsyncIOTransport,
    ],
)
def test_tensorboard_service_grpc_transport_client_cert_source_for_mtls(
    transport_class,
):
    cred = ga_credentials.AnonymousCredentials()

    # Check ssl_channel_credentials is used if provided.
    with mock.patch.object(transport_class, "create_channel") as mock_create_channel:
        mock_ssl_channel_creds = mock.Mock()
        transport_class(
            host="squid.clam.whelk",
            credentials=cred,
            ssl_channel_credentials=mock_ssl_channel_creds,
        )
        mock_create_channel.assert_called_once_with(
            "squid.clam.whelk:443",
            credentials=cred,
            credentials_file=None,
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
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
                client_cert_source_for_mtls=client_cert_source_callback,
            )
            expected_cert, expected_key = client_cert_source_callback()
            mock_ssl_cred.assert_called_once_with(
                certificate_chain=expected_cert, private_key=expected_key
            )


def test_tensorboard_service_host_no_port():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="aiplatform.googleapis.com"
        ),
    )
    assert client.transport._host == "aiplatform.googleapis.com:443"


def test_tensorboard_service_host_with_port():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="aiplatform.googleapis.com:8000"
        ),
    )
    assert client.transport._host == "aiplatform.googleapis.com:8000"


def test_tensorboard_service_grpc_transport_channel():
    channel = grpc.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.TensorboardServiceGrpcTransport(
        host="squid.clam.whelk", channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


def test_tensorboard_service_grpc_asyncio_transport_channel():
    channel = aio.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.TensorboardServiceGrpcAsyncIOTransport(
        host="squid.clam.whelk", channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


# Remove this test when deprecated arguments (api_mtls_endpoint, client_cert_source) are
# removed from grpc/grpc_asyncio transport constructor.
@pytest.mark.parametrize(
    "transport_class",
    [
        transports.TensorboardServiceGrpcTransport,
        transports.TensorboardServiceGrpcAsyncIOTransport,
    ],
)
def test_tensorboard_service_transport_channel_mtls_with_client_cert_source(
    transport_class,
):
    with mock.patch(
        "grpc.ssl_channel_credentials", autospec=True
    ) as grpc_ssl_channel_cred:
        with mock.patch.object(
            transport_class, "create_channel"
        ) as grpc_create_channel:
            mock_ssl_cred = mock.Mock()
            grpc_ssl_channel_cred.return_value = mock_ssl_cred

            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel

            cred = ga_credentials.AnonymousCredentials()
            with pytest.warns(DeprecationWarning):
                with mock.patch.object(google.auth, "default") as adc:
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
                scopes=("https://www.googleapis.com/auth/cloud-platform",),
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
@pytest.mark.parametrize(
    "transport_class",
    [
        transports.TensorboardServiceGrpcTransport,
        transports.TensorboardServiceGrpcAsyncIOTransport,
    ],
)
def test_tensorboard_service_transport_channel_mtls_with_adc(transport_class):
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        with mock.patch.object(
            transport_class, "create_channel"
        ) as grpc_create_channel:
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
                scopes=("https://www.googleapis.com/auth/cloud-platform",),
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )
            assert transport.grpc_channel == mock_grpc_channel


def test_tensorboard_service_grpc_lro_client():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )
    transport = client.transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_tensorboard_service_grpc_lro_async_client():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc_asyncio",
    )
    transport = client.transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsAsyncClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_tensorboard_path():
    project = "squid"
    location = "clam"
    tensorboard = "whelk"
    expected = "projects/{project}/locations/{location}/tensorboards/{tensorboard}".format(
        project=project, location=location, tensorboard=tensorboard,
    )
    actual = TensorboardServiceClient.tensorboard_path(project, location, tensorboard)
    assert expected == actual


def test_parse_tensorboard_path():
    expected = {
        "project": "octopus",
        "location": "oyster",
        "tensorboard": "nudibranch",
    }
    path = TensorboardServiceClient.tensorboard_path(**expected)

    # Check that the path construction is reversible.
    actual = TensorboardServiceClient.parse_tensorboard_path(path)
    assert expected == actual


def test_tensorboard_experiment_path():
    project = "cuttlefish"
    location = "mussel"
    tensorboard = "winkle"
    experiment = "nautilus"
    expected = "projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}".format(
        project=project,
        location=location,
        tensorboard=tensorboard,
        experiment=experiment,
    )
    actual = TensorboardServiceClient.tensorboard_experiment_path(
        project, location, tensorboard, experiment
    )
    assert expected == actual


def test_parse_tensorboard_experiment_path():
    expected = {
        "project": "scallop",
        "location": "abalone",
        "tensorboard": "squid",
        "experiment": "clam",
    }
    path = TensorboardServiceClient.tensorboard_experiment_path(**expected)

    # Check that the path construction is reversible.
    actual = TensorboardServiceClient.parse_tensorboard_experiment_path(path)
    assert expected == actual


def test_tensorboard_run_path():
    project = "whelk"
    location = "octopus"
    tensorboard = "oyster"
    experiment = "nudibranch"
    run = "cuttlefish"
    expected = "projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}/runs/{run}".format(
        project=project,
        location=location,
        tensorboard=tensorboard,
        experiment=experiment,
        run=run,
    )
    actual = TensorboardServiceClient.tensorboard_run_path(
        project, location, tensorboard, experiment, run
    )
    assert expected == actual


def test_parse_tensorboard_run_path():
    expected = {
        "project": "mussel",
        "location": "winkle",
        "tensorboard": "nautilus",
        "experiment": "scallop",
        "run": "abalone",
    }
    path = TensorboardServiceClient.tensorboard_run_path(**expected)

    # Check that the path construction is reversible.
    actual = TensorboardServiceClient.parse_tensorboard_run_path(path)
    assert expected == actual


def test_tensorboard_time_series_path():
    project = "squid"
    location = "clam"
    tensorboard = "whelk"
    experiment = "octopus"
    run = "oyster"
    time_series = "nudibranch"
    expected = "projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}/runs/{run}/timeSeries/{time_series}".format(
        project=project,
        location=location,
        tensorboard=tensorboard,
        experiment=experiment,
        run=run,
        time_series=time_series,
    )
    actual = TensorboardServiceClient.tensorboard_time_series_path(
        project, location, tensorboard, experiment, run, time_series
    )
    assert expected == actual


def test_parse_tensorboard_time_series_path():
    expected = {
        "project": "cuttlefish",
        "location": "mussel",
        "tensorboard": "winkle",
        "experiment": "nautilus",
        "run": "scallop",
        "time_series": "abalone",
    }
    path = TensorboardServiceClient.tensorboard_time_series_path(**expected)

    # Check that the path construction is reversible.
    actual = TensorboardServiceClient.parse_tensorboard_time_series_path(path)
    assert expected == actual


def test_common_billing_account_path():
    billing_account = "squid"
    expected = "billingAccounts/{billing_account}".format(
        billing_account=billing_account,
    )
    actual = TensorboardServiceClient.common_billing_account_path(billing_account)
    assert expected == actual


def test_parse_common_billing_account_path():
    expected = {
        "billing_account": "clam",
    }
    path = TensorboardServiceClient.common_billing_account_path(**expected)

    # Check that the path construction is reversible.
    actual = TensorboardServiceClient.parse_common_billing_account_path(path)
    assert expected == actual


def test_common_folder_path():
    folder = "whelk"
    expected = "folders/{folder}".format(folder=folder,)
    actual = TensorboardServiceClient.common_folder_path(folder)
    assert expected == actual


def test_parse_common_folder_path():
    expected = {
        "folder": "octopus",
    }
    path = TensorboardServiceClient.common_folder_path(**expected)

    # Check that the path construction is reversible.
    actual = TensorboardServiceClient.parse_common_folder_path(path)
    assert expected == actual


def test_common_organization_path():
    organization = "oyster"
    expected = "organizations/{organization}".format(organization=organization,)
    actual = TensorboardServiceClient.common_organization_path(organization)
    assert expected == actual


def test_parse_common_organization_path():
    expected = {
        "organization": "nudibranch",
    }
    path = TensorboardServiceClient.common_organization_path(**expected)

    # Check that the path construction is reversible.
    actual = TensorboardServiceClient.parse_common_organization_path(path)
    assert expected == actual


def test_common_project_path():
    project = "cuttlefish"
    expected = "projects/{project}".format(project=project,)
    actual = TensorboardServiceClient.common_project_path(project)
    assert expected == actual


def test_parse_common_project_path():
    expected = {
        "project": "mussel",
    }
    path = TensorboardServiceClient.common_project_path(**expected)

    # Check that the path construction is reversible.
    actual = TensorboardServiceClient.parse_common_project_path(path)
    assert expected == actual


def test_common_location_path():
    project = "winkle"
    location = "nautilus"
    expected = "projects/{project}/locations/{location}".format(
        project=project, location=location,
    )
    actual = TensorboardServiceClient.common_location_path(project, location)
    assert expected == actual


def test_parse_common_location_path():
    expected = {
        "project": "scallop",
        "location": "abalone",
    }
    path = TensorboardServiceClient.common_location_path(**expected)

    # Check that the path construction is reversible.
    actual = TensorboardServiceClient.parse_common_location_path(path)
    assert expected == actual


def test_client_withDEFAULT_CLIENT_INFO():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(
        transports.TensorboardServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        client = TensorboardServiceClient(
            credentials=ga_credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(
        transports.TensorboardServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        transport_class = TensorboardServiceClient.get_transport_class()
        transport = transport_class(
            credentials=ga_credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)
