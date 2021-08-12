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
from google.cloud.aiplatform_v1beta1.services.metadata_service import (
    MetadataServiceAsyncClient,
)
from google.cloud.aiplatform_v1beta1.services.metadata_service import (
    MetadataServiceClient,
)
from google.cloud.aiplatform_v1beta1.services.metadata_service import pagers
from google.cloud.aiplatform_v1beta1.services.metadata_service import transports
from google.cloud.aiplatform_v1beta1.services.metadata_service.transports.base import (
    _GOOGLE_AUTH_VERSION,
)
from google.cloud.aiplatform_v1beta1.types import artifact
from google.cloud.aiplatform_v1beta1.types import artifact as gca_artifact
from google.cloud.aiplatform_v1beta1.types import context
from google.cloud.aiplatform_v1beta1.types import context as gca_context
from google.cloud.aiplatform_v1beta1.types import encryption_spec
from google.cloud.aiplatform_v1beta1.types import event
from google.cloud.aiplatform_v1beta1.types import execution
from google.cloud.aiplatform_v1beta1.types import execution as gca_execution
from google.cloud.aiplatform_v1beta1.types import lineage_subgraph
from google.cloud.aiplatform_v1beta1.types import metadata_schema
from google.cloud.aiplatform_v1beta1.types import metadata_schema as gca_metadata_schema
from google.cloud.aiplatform_v1beta1.types import metadata_service
from google.cloud.aiplatform_v1beta1.types import metadata_store
from google.cloud.aiplatform_v1beta1.types import metadata_store as gca_metadata_store
from google.cloud.aiplatform_v1beta1.types import operation as gca_operation
from google.longrunning import operations_pb2
from google.oauth2 import service_account
from google.protobuf import field_mask_pb2  # type: ignore
from google.protobuf import struct_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
import google.auth


# TODO(busunkim): Once google-auth >= 1.25.0 is required transitively
# through google-api-core:
# - Delete the auth "less than" test cases
# - Delete these pytest markers (Make the "greater than or equal to" tests the default).
requires_google_auth_lt_1_25_0 = pytest.mark.skipif(
    packaging.version.parse(_GOOGLE_AUTH_VERSION) >= packaging.version.parse("1.25.0"),
    reason="This test requires google-auth < 1.25.0",
)
requires_google_auth_gte_1_25_0 = pytest.mark.skipif(
    packaging.version.parse(_GOOGLE_AUTH_VERSION) < packaging.version.parse("1.25.0"),
    reason="This test requires google-auth >= 1.25.0",
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

    assert MetadataServiceClient._get_default_mtls_endpoint(None) is None
    assert (
        MetadataServiceClient._get_default_mtls_endpoint(api_endpoint)
        == api_mtls_endpoint
    )
    assert (
        MetadataServiceClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        MetadataServiceClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        MetadataServiceClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        MetadataServiceClient._get_default_mtls_endpoint(non_googleapi) == non_googleapi
    )


@pytest.mark.parametrize(
    "client_class", [MetadataServiceClient, MetadataServiceAsyncClient,]
)
def test_metadata_service_client_from_service_account_info(client_class):
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
    "transport_class,transport_name",
    [
        (transports.MetadataServiceGrpcTransport, "grpc"),
        (transports.MetadataServiceGrpcAsyncIOTransport, "grpc_asyncio"),
    ],
)
def test_metadata_service_client_service_account_always_use_jwt(
    transport_class, transport_name
):
    with mock.patch.object(
        service_account.Credentials, "with_always_use_jwt_access", create=True
    ) as use_jwt:
        creds = service_account.Credentials(None, None, None)
        transport = transport_class(credentials=creds, always_use_jwt_access=True)
        use_jwt.assert_called_once_with(True)

    with mock.patch.object(
        service_account.Credentials, "with_always_use_jwt_access", create=True
    ) as use_jwt:
        creds = service_account.Credentials(None, None, None)
        transport = transport_class(credentials=creds, always_use_jwt_access=False)
        use_jwt.assert_not_called()


@pytest.mark.parametrize(
    "client_class", [MetadataServiceClient, MetadataServiceAsyncClient,]
)
def test_metadata_service_client_from_service_account_file(client_class):
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


def test_metadata_service_client_get_transport_class():
    transport = MetadataServiceClient.get_transport_class()
    available_transports = [
        transports.MetadataServiceGrpcTransport,
    ]
    assert transport in available_transports

    transport = MetadataServiceClient.get_transport_class("grpc")
    assert transport == transports.MetadataServiceGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (MetadataServiceClient, transports.MetadataServiceGrpcTransport, "grpc"),
        (
            MetadataServiceAsyncClient,
            transports.MetadataServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
@mock.patch.object(
    MetadataServiceClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(MetadataServiceClient),
)
@mock.patch.object(
    MetadataServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(MetadataServiceAsyncClient),
)
def test_metadata_service_client_client_options(
    client_class, transport_class, transport_name
):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(MetadataServiceClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=ga_credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(MetadataServiceClient, "get_transport_class") as gtc:
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
            always_use_jwt_access=True,
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
                always_use_jwt_access=True,
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
                always_use_jwt_access=True,
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
            always_use_jwt_access=True,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name,use_client_cert_env",
    [
        (
            MetadataServiceClient,
            transports.MetadataServiceGrpcTransport,
            "grpc",
            "true",
        ),
        (
            MetadataServiceAsyncClient,
            transports.MetadataServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "true",
        ),
        (
            MetadataServiceClient,
            transports.MetadataServiceGrpcTransport,
            "grpc",
            "false",
        ),
        (
            MetadataServiceAsyncClient,
            transports.MetadataServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "false",
        ),
    ],
)
@mock.patch.object(
    MetadataServiceClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(MetadataServiceClient),
)
@mock.patch.object(
    MetadataServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(MetadataServiceAsyncClient),
)
@mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"})
def test_metadata_service_client_mtls_env_auto(
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
                always_use_jwt_access=True,
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
                        always_use_jwt_access=True,
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
                    always_use_jwt_access=True,
                )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (MetadataServiceClient, transports.MetadataServiceGrpcTransport, "grpc"),
        (
            MetadataServiceAsyncClient,
            transports.MetadataServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_metadata_service_client_client_options_scopes(
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
            always_use_jwt_access=True,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (MetadataServiceClient, transports.MetadataServiceGrpcTransport, "grpc"),
        (
            MetadataServiceAsyncClient,
            transports.MetadataServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_metadata_service_client_client_options_credentials_file(
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
            always_use_jwt_access=True,
        )


def test_metadata_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.metadata_service.transports.MetadataServiceGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = MetadataServiceClient(
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
            always_use_jwt_access=True,
        )


def test_create_metadata_store(
    transport: str = "grpc", request_type=metadata_service.CreateMetadataStoreRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_metadata_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.create_metadata_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.CreateMetadataStoreRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_create_metadata_store_from_dict():
    test_create_metadata_store(request_type=dict)


def test_create_metadata_store_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_metadata_store), "__call__"
    ) as call:
        client.create_metadata_store()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.CreateMetadataStoreRequest()


@pytest.mark.asyncio
async def test_create_metadata_store_async(
    transport: str = "grpc_asyncio",
    request_type=metadata_service.CreateMetadataStoreRequest,
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_metadata_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.create_metadata_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.CreateMetadataStoreRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_create_metadata_store_async_from_dict():
    await test_create_metadata_store_async(request_type=dict)


def test_create_metadata_store_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.CreateMetadataStoreRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_metadata_store), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.create_metadata_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_metadata_store_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.CreateMetadataStoreRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_metadata_store), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.create_metadata_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_metadata_store_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_metadata_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_metadata_store(
            parent="parent_value",
            metadata_store=gca_metadata_store.MetadataStore(name="name_value"),
            metadata_store_id="metadata_store_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].metadata_store == gca_metadata_store.MetadataStore(
            name="name_value"
        )
        assert args[0].metadata_store_id == "metadata_store_id_value"


def test_create_metadata_store_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_metadata_store(
            metadata_service.CreateMetadataStoreRequest(),
            parent="parent_value",
            metadata_store=gca_metadata_store.MetadataStore(name="name_value"),
            metadata_store_id="metadata_store_id_value",
        )


@pytest.mark.asyncio
async def test_create_metadata_store_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_metadata_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_metadata_store(
            parent="parent_value",
            metadata_store=gca_metadata_store.MetadataStore(name="name_value"),
            metadata_store_id="metadata_store_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].metadata_store == gca_metadata_store.MetadataStore(
            name="name_value"
        )
        assert args[0].metadata_store_id == "metadata_store_id_value"


@pytest.mark.asyncio
async def test_create_metadata_store_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_metadata_store(
            metadata_service.CreateMetadataStoreRequest(),
            parent="parent_value",
            metadata_store=gca_metadata_store.MetadataStore(name="name_value"),
            metadata_store_id="metadata_store_id_value",
        )


def test_get_metadata_store(
    transport: str = "grpc", request_type=metadata_service.GetMetadataStoreRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_metadata_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_store.MetadataStore(
            name="name_value", description="description_value",
        )
        response = client.get_metadata_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.GetMetadataStoreRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, metadata_store.MetadataStore)
    assert response.name == "name_value"
    assert response.description == "description_value"


def test_get_metadata_store_from_dict():
    test_get_metadata_store(request_type=dict)


def test_get_metadata_store_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_metadata_store), "__call__"
    ) as call:
        client.get_metadata_store()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.GetMetadataStoreRequest()


@pytest.mark.asyncio
async def test_get_metadata_store_async(
    transport: str = "grpc_asyncio",
    request_type=metadata_service.GetMetadataStoreRequest,
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_metadata_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_store.MetadataStore(
                name="name_value", description="description_value",
            )
        )
        response = await client.get_metadata_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.GetMetadataStoreRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, metadata_store.MetadataStore)
    assert response.name == "name_value"
    assert response.description == "description_value"


@pytest.mark.asyncio
async def test_get_metadata_store_async_from_dict():
    await test_get_metadata_store_async(request_type=dict)


def test_get_metadata_store_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.GetMetadataStoreRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_metadata_store), "__call__"
    ) as call:
        call.return_value = metadata_store.MetadataStore()
        client.get_metadata_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_metadata_store_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.GetMetadataStoreRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_metadata_store), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_store.MetadataStore()
        )
        await client.get_metadata_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_metadata_store_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_metadata_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_store.MetadataStore()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_metadata_store(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_metadata_store_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_metadata_store(
            metadata_service.GetMetadataStoreRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_metadata_store_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_metadata_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_store.MetadataStore()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_store.MetadataStore()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_metadata_store(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_metadata_store_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_metadata_store(
            metadata_service.GetMetadataStoreRequest(), name="name_value",
        )


def test_list_metadata_stores(
    transport: str = "grpc", request_type=metadata_service.ListMetadataStoresRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_metadata_stores), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.ListMetadataStoresResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_metadata_stores(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.ListMetadataStoresRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListMetadataStoresPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_metadata_stores_from_dict():
    test_list_metadata_stores(request_type=dict)


def test_list_metadata_stores_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_metadata_stores), "__call__"
    ) as call:
        client.list_metadata_stores()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.ListMetadataStoresRequest()


@pytest.mark.asyncio
async def test_list_metadata_stores_async(
    transport: str = "grpc_asyncio",
    request_type=metadata_service.ListMetadataStoresRequest,
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_metadata_stores), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.ListMetadataStoresResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_metadata_stores(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.ListMetadataStoresRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListMetadataStoresAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_metadata_stores_async_from_dict():
    await test_list_metadata_stores_async(request_type=dict)


def test_list_metadata_stores_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.ListMetadataStoresRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_metadata_stores), "__call__"
    ) as call:
        call.return_value = metadata_service.ListMetadataStoresResponse()
        client.list_metadata_stores(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_metadata_stores_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.ListMetadataStoresRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_metadata_stores), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.ListMetadataStoresResponse()
        )
        await client.list_metadata_stores(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_metadata_stores_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_metadata_stores), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.ListMetadataStoresResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_metadata_stores(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_metadata_stores_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_metadata_stores(
            metadata_service.ListMetadataStoresRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_metadata_stores_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_metadata_stores), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.ListMetadataStoresResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.ListMetadataStoresResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_metadata_stores(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_metadata_stores_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_metadata_stores(
            metadata_service.ListMetadataStoresRequest(), parent="parent_value",
        )


def test_list_metadata_stores_pager():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_metadata_stores), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metadata_service.ListMetadataStoresResponse(
                metadata_stores=[
                    metadata_store.MetadataStore(),
                    metadata_store.MetadataStore(),
                    metadata_store.MetadataStore(),
                ],
                next_page_token="abc",
            ),
            metadata_service.ListMetadataStoresResponse(
                metadata_stores=[], next_page_token="def",
            ),
            metadata_service.ListMetadataStoresResponse(
                metadata_stores=[metadata_store.MetadataStore(),],
                next_page_token="ghi",
            ),
            metadata_service.ListMetadataStoresResponse(
                metadata_stores=[
                    metadata_store.MetadataStore(),
                    metadata_store.MetadataStore(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_metadata_stores(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, metadata_store.MetadataStore) for i in results)


def test_list_metadata_stores_pages():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_metadata_stores), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metadata_service.ListMetadataStoresResponse(
                metadata_stores=[
                    metadata_store.MetadataStore(),
                    metadata_store.MetadataStore(),
                    metadata_store.MetadataStore(),
                ],
                next_page_token="abc",
            ),
            metadata_service.ListMetadataStoresResponse(
                metadata_stores=[], next_page_token="def",
            ),
            metadata_service.ListMetadataStoresResponse(
                metadata_stores=[metadata_store.MetadataStore(),],
                next_page_token="ghi",
            ),
            metadata_service.ListMetadataStoresResponse(
                metadata_stores=[
                    metadata_store.MetadataStore(),
                    metadata_store.MetadataStore(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_metadata_stores(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_metadata_stores_async_pager():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_metadata_stores),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metadata_service.ListMetadataStoresResponse(
                metadata_stores=[
                    metadata_store.MetadataStore(),
                    metadata_store.MetadataStore(),
                    metadata_store.MetadataStore(),
                ],
                next_page_token="abc",
            ),
            metadata_service.ListMetadataStoresResponse(
                metadata_stores=[], next_page_token="def",
            ),
            metadata_service.ListMetadataStoresResponse(
                metadata_stores=[metadata_store.MetadataStore(),],
                next_page_token="ghi",
            ),
            metadata_service.ListMetadataStoresResponse(
                metadata_stores=[
                    metadata_store.MetadataStore(),
                    metadata_store.MetadataStore(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_metadata_stores(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, metadata_store.MetadataStore) for i in responses)


@pytest.mark.asyncio
async def test_list_metadata_stores_async_pages():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_metadata_stores),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metadata_service.ListMetadataStoresResponse(
                metadata_stores=[
                    metadata_store.MetadataStore(),
                    metadata_store.MetadataStore(),
                    metadata_store.MetadataStore(),
                ],
                next_page_token="abc",
            ),
            metadata_service.ListMetadataStoresResponse(
                metadata_stores=[], next_page_token="def",
            ),
            metadata_service.ListMetadataStoresResponse(
                metadata_stores=[metadata_store.MetadataStore(),],
                next_page_token="ghi",
            ),
            metadata_service.ListMetadataStoresResponse(
                metadata_stores=[
                    metadata_store.MetadataStore(),
                    metadata_store.MetadataStore(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_metadata_stores(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_delete_metadata_store(
    transport: str = "grpc", request_type=metadata_service.DeleteMetadataStoreRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_metadata_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_metadata_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.DeleteMetadataStoreRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_metadata_store_from_dict():
    test_delete_metadata_store(request_type=dict)


def test_delete_metadata_store_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_metadata_store), "__call__"
    ) as call:
        client.delete_metadata_store()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.DeleteMetadataStoreRequest()


@pytest.mark.asyncio
async def test_delete_metadata_store_async(
    transport: str = "grpc_asyncio",
    request_type=metadata_service.DeleteMetadataStoreRequest,
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_metadata_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_metadata_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.DeleteMetadataStoreRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_metadata_store_async_from_dict():
    await test_delete_metadata_store_async(request_type=dict)


def test_delete_metadata_store_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.DeleteMetadataStoreRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_metadata_store), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_metadata_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_metadata_store_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.DeleteMetadataStoreRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_metadata_store), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_metadata_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_metadata_store_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_metadata_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_metadata_store(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_metadata_store_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_metadata_store(
            metadata_service.DeleteMetadataStoreRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_metadata_store_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_metadata_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_metadata_store(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_metadata_store_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_metadata_store(
            metadata_service.DeleteMetadataStoreRequest(), name="name_value",
        )


def test_create_artifact(
    transport: str = "grpc", request_type=metadata_service.CreateArtifactRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_artifact), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_artifact.Artifact(
            name="name_value",
            display_name="display_name_value",
            uri="uri_value",
            etag="etag_value",
            state=gca_artifact.Artifact.State.PENDING,
            schema_title="schema_title_value",
            schema_version="schema_version_value",
            description="description_value",
        )
        response = client.create_artifact(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.CreateArtifactRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_artifact.Artifact)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.uri == "uri_value"
    assert response.etag == "etag_value"
    assert response.state == gca_artifact.Artifact.State.PENDING
    assert response.schema_title == "schema_title_value"
    assert response.schema_version == "schema_version_value"
    assert response.description == "description_value"


def test_create_artifact_from_dict():
    test_create_artifact(request_type=dict)


def test_create_artifact_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_artifact), "__call__") as call:
        client.create_artifact()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.CreateArtifactRequest()


@pytest.mark.asyncio
async def test_create_artifact_async(
    transport: str = "grpc_asyncio", request_type=metadata_service.CreateArtifactRequest
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_artifact), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_artifact.Artifact(
                name="name_value",
                display_name="display_name_value",
                uri="uri_value",
                etag="etag_value",
                state=gca_artifact.Artifact.State.PENDING,
                schema_title="schema_title_value",
                schema_version="schema_version_value",
                description="description_value",
            )
        )
        response = await client.create_artifact(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.CreateArtifactRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_artifact.Artifact)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.uri == "uri_value"
    assert response.etag == "etag_value"
    assert response.state == gca_artifact.Artifact.State.PENDING
    assert response.schema_title == "schema_title_value"
    assert response.schema_version == "schema_version_value"
    assert response.description == "description_value"


@pytest.mark.asyncio
async def test_create_artifact_async_from_dict():
    await test_create_artifact_async(request_type=dict)


def test_create_artifact_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.CreateArtifactRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_artifact), "__call__") as call:
        call.return_value = gca_artifact.Artifact()
        client.create_artifact(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_artifact_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.CreateArtifactRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_artifact), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_artifact.Artifact()
        )
        await client.create_artifact(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_artifact_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_artifact), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_artifact.Artifact()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_artifact(
            parent="parent_value",
            artifact=gca_artifact.Artifact(name="name_value"),
            artifact_id="artifact_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].artifact == gca_artifact.Artifact(name="name_value")
        assert args[0].artifact_id == "artifact_id_value"


def test_create_artifact_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_artifact(
            metadata_service.CreateArtifactRequest(),
            parent="parent_value",
            artifact=gca_artifact.Artifact(name="name_value"),
            artifact_id="artifact_id_value",
        )


@pytest.mark.asyncio
async def test_create_artifact_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_artifact), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_artifact.Artifact()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_artifact.Artifact()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_artifact(
            parent="parent_value",
            artifact=gca_artifact.Artifact(name="name_value"),
            artifact_id="artifact_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].artifact == gca_artifact.Artifact(name="name_value")
        assert args[0].artifact_id == "artifact_id_value"


@pytest.mark.asyncio
async def test_create_artifact_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_artifact(
            metadata_service.CreateArtifactRequest(),
            parent="parent_value",
            artifact=gca_artifact.Artifact(name="name_value"),
            artifact_id="artifact_id_value",
        )


def test_get_artifact(
    transport: str = "grpc", request_type=metadata_service.GetArtifactRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_artifact), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = artifact.Artifact(
            name="name_value",
            display_name="display_name_value",
            uri="uri_value",
            etag="etag_value",
            state=artifact.Artifact.State.PENDING,
            schema_title="schema_title_value",
            schema_version="schema_version_value",
            description="description_value",
        )
        response = client.get_artifact(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.GetArtifactRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, artifact.Artifact)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.uri == "uri_value"
    assert response.etag == "etag_value"
    assert response.state == artifact.Artifact.State.PENDING
    assert response.schema_title == "schema_title_value"
    assert response.schema_version == "schema_version_value"
    assert response.description == "description_value"


def test_get_artifact_from_dict():
    test_get_artifact(request_type=dict)


def test_get_artifact_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_artifact), "__call__") as call:
        client.get_artifact()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.GetArtifactRequest()


@pytest.mark.asyncio
async def test_get_artifact_async(
    transport: str = "grpc_asyncio", request_type=metadata_service.GetArtifactRequest
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_artifact), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            artifact.Artifact(
                name="name_value",
                display_name="display_name_value",
                uri="uri_value",
                etag="etag_value",
                state=artifact.Artifact.State.PENDING,
                schema_title="schema_title_value",
                schema_version="schema_version_value",
                description="description_value",
            )
        )
        response = await client.get_artifact(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.GetArtifactRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, artifact.Artifact)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.uri == "uri_value"
    assert response.etag == "etag_value"
    assert response.state == artifact.Artifact.State.PENDING
    assert response.schema_title == "schema_title_value"
    assert response.schema_version == "schema_version_value"
    assert response.description == "description_value"


@pytest.mark.asyncio
async def test_get_artifact_async_from_dict():
    await test_get_artifact_async(request_type=dict)


def test_get_artifact_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.GetArtifactRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_artifact), "__call__") as call:
        call.return_value = artifact.Artifact()
        client.get_artifact(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_artifact_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.GetArtifactRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_artifact), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(artifact.Artifact())
        await client.get_artifact(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_artifact_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_artifact), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = artifact.Artifact()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_artifact(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_artifact_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_artifact(
            metadata_service.GetArtifactRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_artifact_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_artifact), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = artifact.Artifact()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(artifact.Artifact())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_artifact(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_artifact_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_artifact(
            metadata_service.GetArtifactRequest(), name="name_value",
        )


def test_list_artifacts(
    transport: str = "grpc", request_type=metadata_service.ListArtifactsRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_artifacts), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.ListArtifactsResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_artifacts(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.ListArtifactsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListArtifactsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_artifacts_from_dict():
    test_list_artifacts(request_type=dict)


def test_list_artifacts_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_artifacts), "__call__") as call:
        client.list_artifacts()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.ListArtifactsRequest()


@pytest.mark.asyncio
async def test_list_artifacts_async(
    transport: str = "grpc_asyncio", request_type=metadata_service.ListArtifactsRequest
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_artifacts), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.ListArtifactsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_artifacts(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.ListArtifactsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListArtifactsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_artifacts_async_from_dict():
    await test_list_artifacts_async(request_type=dict)


def test_list_artifacts_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.ListArtifactsRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_artifacts), "__call__") as call:
        call.return_value = metadata_service.ListArtifactsResponse()
        client.list_artifacts(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_artifacts_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.ListArtifactsRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_artifacts), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.ListArtifactsResponse()
        )
        await client.list_artifacts(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_artifacts_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_artifacts), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.ListArtifactsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_artifacts(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_artifacts_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_artifacts(
            metadata_service.ListArtifactsRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_artifacts_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_artifacts), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.ListArtifactsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.ListArtifactsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_artifacts(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_artifacts_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_artifacts(
            metadata_service.ListArtifactsRequest(), parent="parent_value",
        )


def test_list_artifacts_pager():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_artifacts), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metadata_service.ListArtifactsResponse(
                artifacts=[
                    artifact.Artifact(),
                    artifact.Artifact(),
                    artifact.Artifact(),
                ],
                next_page_token="abc",
            ),
            metadata_service.ListArtifactsResponse(
                artifacts=[], next_page_token="def",
            ),
            metadata_service.ListArtifactsResponse(
                artifacts=[artifact.Artifact(),], next_page_token="ghi",
            ),
            metadata_service.ListArtifactsResponse(
                artifacts=[artifact.Artifact(), artifact.Artifact(),],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_artifacts(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, artifact.Artifact) for i in results)


def test_list_artifacts_pages():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_artifacts), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metadata_service.ListArtifactsResponse(
                artifacts=[
                    artifact.Artifact(),
                    artifact.Artifact(),
                    artifact.Artifact(),
                ],
                next_page_token="abc",
            ),
            metadata_service.ListArtifactsResponse(
                artifacts=[], next_page_token="def",
            ),
            metadata_service.ListArtifactsResponse(
                artifacts=[artifact.Artifact(),], next_page_token="ghi",
            ),
            metadata_service.ListArtifactsResponse(
                artifacts=[artifact.Artifact(), artifact.Artifact(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_artifacts(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_artifacts_async_pager():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_artifacts), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metadata_service.ListArtifactsResponse(
                artifacts=[
                    artifact.Artifact(),
                    artifact.Artifact(),
                    artifact.Artifact(),
                ],
                next_page_token="abc",
            ),
            metadata_service.ListArtifactsResponse(
                artifacts=[], next_page_token="def",
            ),
            metadata_service.ListArtifactsResponse(
                artifacts=[artifact.Artifact(),], next_page_token="ghi",
            ),
            metadata_service.ListArtifactsResponse(
                artifacts=[artifact.Artifact(), artifact.Artifact(),],
            ),
            RuntimeError,
        )
        async_pager = await client.list_artifacts(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, artifact.Artifact) for i in responses)


@pytest.mark.asyncio
async def test_list_artifacts_async_pages():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_artifacts), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metadata_service.ListArtifactsResponse(
                artifacts=[
                    artifact.Artifact(),
                    artifact.Artifact(),
                    artifact.Artifact(),
                ],
                next_page_token="abc",
            ),
            metadata_service.ListArtifactsResponse(
                artifacts=[], next_page_token="def",
            ),
            metadata_service.ListArtifactsResponse(
                artifacts=[artifact.Artifact(),], next_page_token="ghi",
            ),
            metadata_service.ListArtifactsResponse(
                artifacts=[artifact.Artifact(), artifact.Artifact(),],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_artifacts(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_update_artifact(
    transport: str = "grpc", request_type=metadata_service.UpdateArtifactRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_artifact), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_artifact.Artifact(
            name="name_value",
            display_name="display_name_value",
            uri="uri_value",
            etag="etag_value",
            state=gca_artifact.Artifact.State.PENDING,
            schema_title="schema_title_value",
            schema_version="schema_version_value",
            description="description_value",
        )
        response = client.update_artifact(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.UpdateArtifactRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_artifact.Artifact)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.uri == "uri_value"
    assert response.etag == "etag_value"
    assert response.state == gca_artifact.Artifact.State.PENDING
    assert response.schema_title == "schema_title_value"
    assert response.schema_version == "schema_version_value"
    assert response.description == "description_value"


def test_update_artifact_from_dict():
    test_update_artifact(request_type=dict)


def test_update_artifact_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_artifact), "__call__") as call:
        client.update_artifact()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.UpdateArtifactRequest()


@pytest.mark.asyncio
async def test_update_artifact_async(
    transport: str = "grpc_asyncio", request_type=metadata_service.UpdateArtifactRequest
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_artifact), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_artifact.Artifact(
                name="name_value",
                display_name="display_name_value",
                uri="uri_value",
                etag="etag_value",
                state=gca_artifact.Artifact.State.PENDING,
                schema_title="schema_title_value",
                schema_version="schema_version_value",
                description="description_value",
            )
        )
        response = await client.update_artifact(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.UpdateArtifactRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_artifact.Artifact)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.uri == "uri_value"
    assert response.etag == "etag_value"
    assert response.state == gca_artifact.Artifact.State.PENDING
    assert response.schema_title == "schema_title_value"
    assert response.schema_version == "schema_version_value"
    assert response.description == "description_value"


@pytest.mark.asyncio
async def test_update_artifact_async_from_dict():
    await test_update_artifact_async(request_type=dict)


def test_update_artifact_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.UpdateArtifactRequest()

    request.artifact.name = "artifact.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_artifact), "__call__") as call:
        call.return_value = gca_artifact.Artifact()
        client.update_artifact(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "artifact.name=artifact.name/value",) in kw[
        "metadata"
    ]


@pytest.mark.asyncio
async def test_update_artifact_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.UpdateArtifactRequest()

    request.artifact.name = "artifact.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_artifact), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_artifact.Artifact()
        )
        await client.update_artifact(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "artifact.name=artifact.name/value",) in kw[
        "metadata"
    ]


def test_update_artifact_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_artifact), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_artifact.Artifact()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_artifact(
            artifact=gca_artifact.Artifact(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].artifact == gca_artifact.Artifact(name="name_value")
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


def test_update_artifact_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_artifact(
            metadata_service.UpdateArtifactRequest(),
            artifact=gca_artifact.Artifact(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_artifact_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_artifact), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_artifact.Artifact()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_artifact.Artifact()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_artifact(
            artifact=gca_artifact.Artifact(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].artifact == gca_artifact.Artifact(name="name_value")
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


@pytest.mark.asyncio
async def test_update_artifact_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_artifact(
            metadata_service.UpdateArtifactRequest(),
            artifact=gca_artifact.Artifact(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


def test_delete_artifact(
    transport: str = "grpc", request_type=metadata_service.DeleteArtifactRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_artifact), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_artifact(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.DeleteArtifactRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_artifact_from_dict():
    test_delete_artifact(request_type=dict)


def test_delete_artifact_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_artifact), "__call__") as call:
        client.delete_artifact()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.DeleteArtifactRequest()


@pytest.mark.asyncio
async def test_delete_artifact_async(
    transport: str = "grpc_asyncio", request_type=metadata_service.DeleteArtifactRequest
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_artifact), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_artifact(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.DeleteArtifactRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_artifact_async_from_dict():
    await test_delete_artifact_async(request_type=dict)


def test_delete_artifact_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.DeleteArtifactRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_artifact), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_artifact(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_artifact_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.DeleteArtifactRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_artifact), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_artifact(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_artifact_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_artifact), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_artifact(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_artifact_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_artifact(
            metadata_service.DeleteArtifactRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_artifact_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_artifact), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_artifact(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_artifact_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_artifact(
            metadata_service.DeleteArtifactRequest(), name="name_value",
        )


def test_purge_artifacts(
    transport: str = "grpc", request_type=metadata_service.PurgeArtifactsRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.purge_artifacts), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.purge_artifacts(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.PurgeArtifactsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_purge_artifacts_from_dict():
    test_purge_artifacts(request_type=dict)


def test_purge_artifacts_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.purge_artifacts), "__call__") as call:
        client.purge_artifacts()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.PurgeArtifactsRequest()


@pytest.mark.asyncio
async def test_purge_artifacts_async(
    transport: str = "grpc_asyncio", request_type=metadata_service.PurgeArtifactsRequest
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.purge_artifacts), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.purge_artifacts(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.PurgeArtifactsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_purge_artifacts_async_from_dict():
    await test_purge_artifacts_async(request_type=dict)


def test_purge_artifacts_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.PurgeArtifactsRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.purge_artifacts), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.purge_artifacts(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_purge_artifacts_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.PurgeArtifactsRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.purge_artifacts), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.purge_artifacts(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_purge_artifacts_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.purge_artifacts), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.purge_artifacts(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_purge_artifacts_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.purge_artifacts(
            metadata_service.PurgeArtifactsRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_purge_artifacts_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.purge_artifacts), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.purge_artifacts(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_purge_artifacts_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.purge_artifacts(
            metadata_service.PurgeArtifactsRequest(), parent="parent_value",
        )


def test_create_context(
    transport: str = "grpc", request_type=metadata_service.CreateContextRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_context), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_context.Context(
            name="name_value",
            display_name="display_name_value",
            etag="etag_value",
            parent_contexts=["parent_contexts_value"],
            schema_title="schema_title_value",
            schema_version="schema_version_value",
            description="description_value",
        )
        response = client.create_context(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.CreateContextRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_context.Context)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.etag == "etag_value"
    assert response.parent_contexts == ["parent_contexts_value"]
    assert response.schema_title == "schema_title_value"
    assert response.schema_version == "schema_version_value"
    assert response.description == "description_value"


def test_create_context_from_dict():
    test_create_context(request_type=dict)


def test_create_context_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_context), "__call__") as call:
        client.create_context()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.CreateContextRequest()


@pytest.mark.asyncio
async def test_create_context_async(
    transport: str = "grpc_asyncio", request_type=metadata_service.CreateContextRequest
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_context), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_context.Context(
                name="name_value",
                display_name="display_name_value",
                etag="etag_value",
                parent_contexts=["parent_contexts_value"],
                schema_title="schema_title_value",
                schema_version="schema_version_value",
                description="description_value",
            )
        )
        response = await client.create_context(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.CreateContextRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_context.Context)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.etag == "etag_value"
    assert response.parent_contexts == ["parent_contexts_value"]
    assert response.schema_title == "schema_title_value"
    assert response.schema_version == "schema_version_value"
    assert response.description == "description_value"


@pytest.mark.asyncio
async def test_create_context_async_from_dict():
    await test_create_context_async(request_type=dict)


def test_create_context_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.CreateContextRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_context), "__call__") as call:
        call.return_value = gca_context.Context()
        client.create_context(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_context_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.CreateContextRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_context), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gca_context.Context())
        await client.create_context(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_context_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_context), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_context.Context()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_context(
            parent="parent_value",
            context=gca_context.Context(name="name_value"),
            context_id="context_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].context == gca_context.Context(name="name_value")
        assert args[0].context_id == "context_id_value"


def test_create_context_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_context(
            metadata_service.CreateContextRequest(),
            parent="parent_value",
            context=gca_context.Context(name="name_value"),
            context_id="context_id_value",
        )


@pytest.mark.asyncio
async def test_create_context_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_context), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_context.Context()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gca_context.Context())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_context(
            parent="parent_value",
            context=gca_context.Context(name="name_value"),
            context_id="context_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].context == gca_context.Context(name="name_value")
        assert args[0].context_id == "context_id_value"


@pytest.mark.asyncio
async def test_create_context_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_context(
            metadata_service.CreateContextRequest(),
            parent="parent_value",
            context=gca_context.Context(name="name_value"),
            context_id="context_id_value",
        )


def test_get_context(
    transport: str = "grpc", request_type=metadata_service.GetContextRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_context), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = context.Context(
            name="name_value",
            display_name="display_name_value",
            etag="etag_value",
            parent_contexts=["parent_contexts_value"],
            schema_title="schema_title_value",
            schema_version="schema_version_value",
            description="description_value",
        )
        response = client.get_context(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.GetContextRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, context.Context)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.etag == "etag_value"
    assert response.parent_contexts == ["parent_contexts_value"]
    assert response.schema_title == "schema_title_value"
    assert response.schema_version == "schema_version_value"
    assert response.description == "description_value"


def test_get_context_from_dict():
    test_get_context(request_type=dict)


def test_get_context_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_context), "__call__") as call:
        client.get_context()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.GetContextRequest()


@pytest.mark.asyncio
async def test_get_context_async(
    transport: str = "grpc_asyncio", request_type=metadata_service.GetContextRequest
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_context), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            context.Context(
                name="name_value",
                display_name="display_name_value",
                etag="etag_value",
                parent_contexts=["parent_contexts_value"],
                schema_title="schema_title_value",
                schema_version="schema_version_value",
                description="description_value",
            )
        )
        response = await client.get_context(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.GetContextRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, context.Context)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.etag == "etag_value"
    assert response.parent_contexts == ["parent_contexts_value"]
    assert response.schema_title == "schema_title_value"
    assert response.schema_version == "schema_version_value"
    assert response.description == "description_value"


@pytest.mark.asyncio
async def test_get_context_async_from_dict():
    await test_get_context_async(request_type=dict)


def test_get_context_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.GetContextRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_context), "__call__") as call:
        call.return_value = context.Context()
        client.get_context(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_context_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.GetContextRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_context), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(context.Context())
        await client.get_context(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_context_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_context), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = context.Context()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_context(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_context_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_context(
            metadata_service.GetContextRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_context_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_context), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = context.Context()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(context.Context())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_context(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_context_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_context(
            metadata_service.GetContextRequest(), name="name_value",
        )


def test_list_contexts(
    transport: str = "grpc", request_type=metadata_service.ListContextsRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_contexts), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.ListContextsResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_contexts(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.ListContextsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListContextsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_contexts_from_dict():
    test_list_contexts(request_type=dict)


def test_list_contexts_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_contexts), "__call__") as call:
        client.list_contexts()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.ListContextsRequest()


@pytest.mark.asyncio
async def test_list_contexts_async(
    transport: str = "grpc_asyncio", request_type=metadata_service.ListContextsRequest
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_contexts), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.ListContextsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_contexts(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.ListContextsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListContextsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_contexts_async_from_dict():
    await test_list_contexts_async(request_type=dict)


def test_list_contexts_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.ListContextsRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_contexts), "__call__") as call:
        call.return_value = metadata_service.ListContextsResponse()
        client.list_contexts(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_contexts_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.ListContextsRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_contexts), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.ListContextsResponse()
        )
        await client.list_contexts(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_contexts_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_contexts), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.ListContextsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_contexts(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_contexts_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_contexts(
            metadata_service.ListContextsRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_contexts_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_contexts), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.ListContextsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.ListContextsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_contexts(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_contexts_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_contexts(
            metadata_service.ListContextsRequest(), parent="parent_value",
        )


def test_list_contexts_pager():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_contexts), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metadata_service.ListContextsResponse(
                contexts=[context.Context(), context.Context(), context.Context(),],
                next_page_token="abc",
            ),
            metadata_service.ListContextsResponse(contexts=[], next_page_token="def",),
            metadata_service.ListContextsResponse(
                contexts=[context.Context(),], next_page_token="ghi",
            ),
            metadata_service.ListContextsResponse(
                contexts=[context.Context(), context.Context(),],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_contexts(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, context.Context) for i in results)


def test_list_contexts_pages():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_contexts), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metadata_service.ListContextsResponse(
                contexts=[context.Context(), context.Context(), context.Context(),],
                next_page_token="abc",
            ),
            metadata_service.ListContextsResponse(contexts=[], next_page_token="def",),
            metadata_service.ListContextsResponse(
                contexts=[context.Context(),], next_page_token="ghi",
            ),
            metadata_service.ListContextsResponse(
                contexts=[context.Context(), context.Context(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_contexts(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_contexts_async_pager():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_contexts), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metadata_service.ListContextsResponse(
                contexts=[context.Context(), context.Context(), context.Context(),],
                next_page_token="abc",
            ),
            metadata_service.ListContextsResponse(contexts=[], next_page_token="def",),
            metadata_service.ListContextsResponse(
                contexts=[context.Context(),], next_page_token="ghi",
            ),
            metadata_service.ListContextsResponse(
                contexts=[context.Context(), context.Context(),],
            ),
            RuntimeError,
        )
        async_pager = await client.list_contexts(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, context.Context) for i in responses)


@pytest.mark.asyncio
async def test_list_contexts_async_pages():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_contexts), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metadata_service.ListContextsResponse(
                contexts=[context.Context(), context.Context(), context.Context(),],
                next_page_token="abc",
            ),
            metadata_service.ListContextsResponse(contexts=[], next_page_token="def",),
            metadata_service.ListContextsResponse(
                contexts=[context.Context(),], next_page_token="ghi",
            ),
            metadata_service.ListContextsResponse(
                contexts=[context.Context(), context.Context(),],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_contexts(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_update_context(
    transport: str = "grpc", request_type=metadata_service.UpdateContextRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_context), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_context.Context(
            name="name_value",
            display_name="display_name_value",
            etag="etag_value",
            parent_contexts=["parent_contexts_value"],
            schema_title="schema_title_value",
            schema_version="schema_version_value",
            description="description_value",
        )
        response = client.update_context(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.UpdateContextRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_context.Context)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.etag == "etag_value"
    assert response.parent_contexts == ["parent_contexts_value"]
    assert response.schema_title == "schema_title_value"
    assert response.schema_version == "schema_version_value"
    assert response.description == "description_value"


def test_update_context_from_dict():
    test_update_context(request_type=dict)


def test_update_context_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_context), "__call__") as call:
        client.update_context()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.UpdateContextRequest()


@pytest.mark.asyncio
async def test_update_context_async(
    transport: str = "grpc_asyncio", request_type=metadata_service.UpdateContextRequest
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_context), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_context.Context(
                name="name_value",
                display_name="display_name_value",
                etag="etag_value",
                parent_contexts=["parent_contexts_value"],
                schema_title="schema_title_value",
                schema_version="schema_version_value",
                description="description_value",
            )
        )
        response = await client.update_context(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.UpdateContextRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_context.Context)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.etag == "etag_value"
    assert response.parent_contexts == ["parent_contexts_value"]
    assert response.schema_title == "schema_title_value"
    assert response.schema_version == "schema_version_value"
    assert response.description == "description_value"


@pytest.mark.asyncio
async def test_update_context_async_from_dict():
    await test_update_context_async(request_type=dict)


def test_update_context_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.UpdateContextRequest()

    request.context.name = "context.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_context), "__call__") as call:
        call.return_value = gca_context.Context()
        client.update_context(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "context.name=context.name/value",) in kw[
        "metadata"
    ]


@pytest.mark.asyncio
async def test_update_context_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.UpdateContextRequest()

    request.context.name = "context.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_context), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gca_context.Context())
        await client.update_context(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "context.name=context.name/value",) in kw[
        "metadata"
    ]


def test_update_context_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_context), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_context.Context()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_context(
            context=gca_context.Context(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].context == gca_context.Context(name="name_value")
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


def test_update_context_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_context(
            metadata_service.UpdateContextRequest(),
            context=gca_context.Context(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_context_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_context), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_context.Context()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gca_context.Context())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_context(
            context=gca_context.Context(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].context == gca_context.Context(name="name_value")
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


@pytest.mark.asyncio
async def test_update_context_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_context(
            metadata_service.UpdateContextRequest(),
            context=gca_context.Context(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


def test_delete_context(
    transport: str = "grpc", request_type=metadata_service.DeleteContextRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_context), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_context(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.DeleteContextRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_context_from_dict():
    test_delete_context(request_type=dict)


def test_delete_context_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_context), "__call__") as call:
        client.delete_context()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.DeleteContextRequest()


@pytest.mark.asyncio
async def test_delete_context_async(
    transport: str = "grpc_asyncio", request_type=metadata_service.DeleteContextRequest
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_context), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_context(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.DeleteContextRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_context_async_from_dict():
    await test_delete_context_async(request_type=dict)


def test_delete_context_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.DeleteContextRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_context), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_context(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_context_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.DeleteContextRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_context), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_context(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_context_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_context), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_context(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_context_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_context(
            metadata_service.DeleteContextRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_context_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_context), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_context(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_context_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_context(
            metadata_service.DeleteContextRequest(), name="name_value",
        )


def test_purge_contexts(
    transport: str = "grpc", request_type=metadata_service.PurgeContextsRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.purge_contexts), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.purge_contexts(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.PurgeContextsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_purge_contexts_from_dict():
    test_purge_contexts(request_type=dict)


def test_purge_contexts_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.purge_contexts), "__call__") as call:
        client.purge_contexts()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.PurgeContextsRequest()


@pytest.mark.asyncio
async def test_purge_contexts_async(
    transport: str = "grpc_asyncio", request_type=metadata_service.PurgeContextsRequest
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.purge_contexts), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.purge_contexts(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.PurgeContextsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_purge_contexts_async_from_dict():
    await test_purge_contexts_async(request_type=dict)


def test_purge_contexts_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.PurgeContextsRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.purge_contexts), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.purge_contexts(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_purge_contexts_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.PurgeContextsRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.purge_contexts), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.purge_contexts(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_purge_contexts_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.purge_contexts), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.purge_contexts(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_purge_contexts_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.purge_contexts(
            metadata_service.PurgeContextsRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_purge_contexts_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.purge_contexts), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.purge_contexts(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_purge_contexts_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.purge_contexts(
            metadata_service.PurgeContextsRequest(), parent="parent_value",
        )


def test_add_context_artifacts_and_executions(
    transport: str = "grpc",
    request_type=metadata_service.AddContextArtifactsAndExecutionsRequest,
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.add_context_artifacts_and_executions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.AddContextArtifactsAndExecutionsResponse()
        response = client.add_context_artifacts_and_executions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.AddContextArtifactsAndExecutionsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, metadata_service.AddContextArtifactsAndExecutionsResponse
    )


def test_add_context_artifacts_and_executions_from_dict():
    test_add_context_artifacts_and_executions(request_type=dict)


def test_add_context_artifacts_and_executions_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.add_context_artifacts_and_executions), "__call__"
    ) as call:
        client.add_context_artifacts_and_executions()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.AddContextArtifactsAndExecutionsRequest()


@pytest.mark.asyncio
async def test_add_context_artifacts_and_executions_async(
    transport: str = "grpc_asyncio",
    request_type=metadata_service.AddContextArtifactsAndExecutionsRequest,
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.add_context_artifacts_and_executions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.AddContextArtifactsAndExecutionsResponse()
        )
        response = await client.add_context_artifacts_and_executions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.AddContextArtifactsAndExecutionsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, metadata_service.AddContextArtifactsAndExecutionsResponse
    )


@pytest.mark.asyncio
async def test_add_context_artifacts_and_executions_async_from_dict():
    await test_add_context_artifacts_and_executions_async(request_type=dict)


def test_add_context_artifacts_and_executions_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.AddContextArtifactsAndExecutionsRequest()

    request.context = "context/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.add_context_artifacts_and_executions), "__call__"
    ) as call:
        call.return_value = metadata_service.AddContextArtifactsAndExecutionsResponse()
        client.add_context_artifacts_and_executions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "context=context/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_add_context_artifacts_and_executions_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.AddContextArtifactsAndExecutionsRequest()

    request.context = "context/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.add_context_artifacts_and_executions), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.AddContextArtifactsAndExecutionsResponse()
        )
        await client.add_context_artifacts_and_executions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "context=context/value",) in kw["metadata"]


def test_add_context_artifacts_and_executions_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.add_context_artifacts_and_executions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.AddContextArtifactsAndExecutionsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.add_context_artifacts_and_executions(
            context="context_value",
            artifacts=["artifacts_value"],
            executions=["executions_value"],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].context == "context_value"
        assert args[0].artifacts == ["artifacts_value"]
        assert args[0].executions == ["executions_value"]


def test_add_context_artifacts_and_executions_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.add_context_artifacts_and_executions(
            metadata_service.AddContextArtifactsAndExecutionsRequest(),
            context="context_value",
            artifacts=["artifacts_value"],
            executions=["executions_value"],
        )


@pytest.mark.asyncio
async def test_add_context_artifacts_and_executions_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.add_context_artifacts_and_executions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.AddContextArtifactsAndExecutionsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.AddContextArtifactsAndExecutionsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.add_context_artifacts_and_executions(
            context="context_value",
            artifacts=["artifacts_value"],
            executions=["executions_value"],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].context == "context_value"
        assert args[0].artifacts == ["artifacts_value"]
        assert args[0].executions == ["executions_value"]


@pytest.mark.asyncio
async def test_add_context_artifacts_and_executions_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.add_context_artifacts_and_executions(
            metadata_service.AddContextArtifactsAndExecutionsRequest(),
            context="context_value",
            artifacts=["artifacts_value"],
            executions=["executions_value"],
        )


def test_add_context_children(
    transport: str = "grpc", request_type=metadata_service.AddContextChildrenRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.add_context_children), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.AddContextChildrenResponse()
        response = client.add_context_children(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.AddContextChildrenRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, metadata_service.AddContextChildrenResponse)


def test_add_context_children_from_dict():
    test_add_context_children(request_type=dict)


def test_add_context_children_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.add_context_children), "__call__"
    ) as call:
        client.add_context_children()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.AddContextChildrenRequest()


@pytest.mark.asyncio
async def test_add_context_children_async(
    transport: str = "grpc_asyncio",
    request_type=metadata_service.AddContextChildrenRequest,
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.add_context_children), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.AddContextChildrenResponse()
        )
        response = await client.add_context_children(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.AddContextChildrenRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, metadata_service.AddContextChildrenResponse)


@pytest.mark.asyncio
async def test_add_context_children_async_from_dict():
    await test_add_context_children_async(request_type=dict)


def test_add_context_children_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.AddContextChildrenRequest()

    request.context = "context/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.add_context_children), "__call__"
    ) as call:
        call.return_value = metadata_service.AddContextChildrenResponse()
        client.add_context_children(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "context=context/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_add_context_children_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.AddContextChildrenRequest()

    request.context = "context/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.add_context_children), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.AddContextChildrenResponse()
        )
        await client.add_context_children(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "context=context/value",) in kw["metadata"]


def test_add_context_children_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.add_context_children), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.AddContextChildrenResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.add_context_children(
            context="context_value", child_contexts=["child_contexts_value"],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].context == "context_value"
        assert args[0].child_contexts == ["child_contexts_value"]


def test_add_context_children_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.add_context_children(
            metadata_service.AddContextChildrenRequest(),
            context="context_value",
            child_contexts=["child_contexts_value"],
        )


@pytest.mark.asyncio
async def test_add_context_children_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.add_context_children), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.AddContextChildrenResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.AddContextChildrenResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.add_context_children(
            context="context_value", child_contexts=["child_contexts_value"],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].context == "context_value"
        assert args[0].child_contexts == ["child_contexts_value"]


@pytest.mark.asyncio
async def test_add_context_children_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.add_context_children(
            metadata_service.AddContextChildrenRequest(),
            context="context_value",
            child_contexts=["child_contexts_value"],
        )


def test_query_context_lineage_subgraph(
    transport: str = "grpc",
    request_type=metadata_service.QueryContextLineageSubgraphRequest,
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.query_context_lineage_subgraph), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = lineage_subgraph.LineageSubgraph()
        response = client.query_context_lineage_subgraph(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.QueryContextLineageSubgraphRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, lineage_subgraph.LineageSubgraph)


def test_query_context_lineage_subgraph_from_dict():
    test_query_context_lineage_subgraph(request_type=dict)


def test_query_context_lineage_subgraph_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.query_context_lineage_subgraph), "__call__"
    ) as call:
        client.query_context_lineage_subgraph()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.QueryContextLineageSubgraphRequest()


@pytest.mark.asyncio
async def test_query_context_lineage_subgraph_async(
    transport: str = "grpc_asyncio",
    request_type=metadata_service.QueryContextLineageSubgraphRequest,
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.query_context_lineage_subgraph), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            lineage_subgraph.LineageSubgraph()
        )
        response = await client.query_context_lineage_subgraph(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.QueryContextLineageSubgraphRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, lineage_subgraph.LineageSubgraph)


@pytest.mark.asyncio
async def test_query_context_lineage_subgraph_async_from_dict():
    await test_query_context_lineage_subgraph_async(request_type=dict)


def test_query_context_lineage_subgraph_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.QueryContextLineageSubgraphRequest()

    request.context = "context/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.query_context_lineage_subgraph), "__call__"
    ) as call:
        call.return_value = lineage_subgraph.LineageSubgraph()
        client.query_context_lineage_subgraph(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "context=context/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_query_context_lineage_subgraph_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.QueryContextLineageSubgraphRequest()

    request.context = "context/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.query_context_lineage_subgraph), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            lineage_subgraph.LineageSubgraph()
        )
        await client.query_context_lineage_subgraph(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "context=context/value",) in kw["metadata"]


def test_query_context_lineage_subgraph_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.query_context_lineage_subgraph), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = lineage_subgraph.LineageSubgraph()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.query_context_lineage_subgraph(context="context_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].context == "context_value"


def test_query_context_lineage_subgraph_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.query_context_lineage_subgraph(
            metadata_service.QueryContextLineageSubgraphRequest(),
            context="context_value",
        )


@pytest.mark.asyncio
async def test_query_context_lineage_subgraph_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.query_context_lineage_subgraph), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = lineage_subgraph.LineageSubgraph()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            lineage_subgraph.LineageSubgraph()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.query_context_lineage_subgraph(context="context_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].context == "context_value"


@pytest.mark.asyncio
async def test_query_context_lineage_subgraph_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.query_context_lineage_subgraph(
            metadata_service.QueryContextLineageSubgraphRequest(),
            context="context_value",
        )


def test_create_execution(
    transport: str = "grpc", request_type=metadata_service.CreateExecutionRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_execution), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_execution.Execution(
            name="name_value",
            display_name="display_name_value",
            state=gca_execution.Execution.State.NEW,
            etag="etag_value",
            schema_title="schema_title_value",
            schema_version="schema_version_value",
            description="description_value",
        )
        response = client.create_execution(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.CreateExecutionRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_execution.Execution)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.state == gca_execution.Execution.State.NEW
    assert response.etag == "etag_value"
    assert response.schema_title == "schema_title_value"
    assert response.schema_version == "schema_version_value"
    assert response.description == "description_value"


def test_create_execution_from_dict():
    test_create_execution(request_type=dict)


def test_create_execution_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_execution), "__call__") as call:
        client.create_execution()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.CreateExecutionRequest()


@pytest.mark.asyncio
async def test_create_execution_async(
    transport: str = "grpc_asyncio",
    request_type=metadata_service.CreateExecutionRequest,
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_execution), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_execution.Execution(
                name="name_value",
                display_name="display_name_value",
                state=gca_execution.Execution.State.NEW,
                etag="etag_value",
                schema_title="schema_title_value",
                schema_version="schema_version_value",
                description="description_value",
            )
        )
        response = await client.create_execution(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.CreateExecutionRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_execution.Execution)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.state == gca_execution.Execution.State.NEW
    assert response.etag == "etag_value"
    assert response.schema_title == "schema_title_value"
    assert response.schema_version == "schema_version_value"
    assert response.description == "description_value"


@pytest.mark.asyncio
async def test_create_execution_async_from_dict():
    await test_create_execution_async(request_type=dict)


def test_create_execution_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.CreateExecutionRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_execution), "__call__") as call:
        call.return_value = gca_execution.Execution()
        client.create_execution(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_execution_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.CreateExecutionRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_execution), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_execution.Execution()
        )
        await client.create_execution(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_execution_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_execution), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_execution.Execution()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_execution(
            parent="parent_value",
            execution=gca_execution.Execution(name="name_value"),
            execution_id="execution_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].execution == gca_execution.Execution(name="name_value")
        assert args[0].execution_id == "execution_id_value"


def test_create_execution_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_execution(
            metadata_service.CreateExecutionRequest(),
            parent="parent_value",
            execution=gca_execution.Execution(name="name_value"),
            execution_id="execution_id_value",
        )


@pytest.mark.asyncio
async def test_create_execution_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_execution), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_execution.Execution()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_execution.Execution()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_execution(
            parent="parent_value",
            execution=gca_execution.Execution(name="name_value"),
            execution_id="execution_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].execution == gca_execution.Execution(name="name_value")
        assert args[0].execution_id == "execution_id_value"


@pytest.mark.asyncio
async def test_create_execution_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_execution(
            metadata_service.CreateExecutionRequest(),
            parent="parent_value",
            execution=gca_execution.Execution(name="name_value"),
            execution_id="execution_id_value",
        )


def test_get_execution(
    transport: str = "grpc", request_type=metadata_service.GetExecutionRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_execution), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = execution.Execution(
            name="name_value",
            display_name="display_name_value",
            state=execution.Execution.State.NEW,
            etag="etag_value",
            schema_title="schema_title_value",
            schema_version="schema_version_value",
            description="description_value",
        )
        response = client.get_execution(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.GetExecutionRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, execution.Execution)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.state == execution.Execution.State.NEW
    assert response.etag == "etag_value"
    assert response.schema_title == "schema_title_value"
    assert response.schema_version == "schema_version_value"
    assert response.description == "description_value"


def test_get_execution_from_dict():
    test_get_execution(request_type=dict)


def test_get_execution_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_execution), "__call__") as call:
        client.get_execution()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.GetExecutionRequest()


@pytest.mark.asyncio
async def test_get_execution_async(
    transport: str = "grpc_asyncio", request_type=metadata_service.GetExecutionRequest
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_execution), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            execution.Execution(
                name="name_value",
                display_name="display_name_value",
                state=execution.Execution.State.NEW,
                etag="etag_value",
                schema_title="schema_title_value",
                schema_version="schema_version_value",
                description="description_value",
            )
        )
        response = await client.get_execution(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.GetExecutionRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, execution.Execution)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.state == execution.Execution.State.NEW
    assert response.etag == "etag_value"
    assert response.schema_title == "schema_title_value"
    assert response.schema_version == "schema_version_value"
    assert response.description == "description_value"


@pytest.mark.asyncio
async def test_get_execution_async_from_dict():
    await test_get_execution_async(request_type=dict)


def test_get_execution_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.GetExecutionRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_execution), "__call__") as call:
        call.return_value = execution.Execution()
        client.get_execution(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_execution_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.GetExecutionRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_execution), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(execution.Execution())
        await client.get_execution(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_execution_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_execution), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = execution.Execution()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_execution(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_execution_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_execution(
            metadata_service.GetExecutionRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_execution_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_execution), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = execution.Execution()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(execution.Execution())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_execution(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_execution_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_execution(
            metadata_service.GetExecutionRequest(), name="name_value",
        )


def test_list_executions(
    transport: str = "grpc", request_type=metadata_service.ListExecutionsRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_executions), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.ListExecutionsResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_executions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.ListExecutionsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListExecutionsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_executions_from_dict():
    test_list_executions(request_type=dict)


def test_list_executions_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_executions), "__call__") as call:
        client.list_executions()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.ListExecutionsRequest()


@pytest.mark.asyncio
async def test_list_executions_async(
    transport: str = "grpc_asyncio", request_type=metadata_service.ListExecutionsRequest
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_executions), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.ListExecutionsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_executions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.ListExecutionsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListExecutionsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_executions_async_from_dict():
    await test_list_executions_async(request_type=dict)


def test_list_executions_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.ListExecutionsRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_executions), "__call__") as call:
        call.return_value = metadata_service.ListExecutionsResponse()
        client.list_executions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_executions_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.ListExecutionsRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_executions), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.ListExecutionsResponse()
        )
        await client.list_executions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_executions_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_executions), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.ListExecutionsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_executions(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_executions_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_executions(
            metadata_service.ListExecutionsRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_executions_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_executions), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.ListExecutionsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.ListExecutionsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_executions(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_executions_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_executions(
            metadata_service.ListExecutionsRequest(), parent="parent_value",
        )


def test_list_executions_pager():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_executions), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metadata_service.ListExecutionsResponse(
                executions=[
                    execution.Execution(),
                    execution.Execution(),
                    execution.Execution(),
                ],
                next_page_token="abc",
            ),
            metadata_service.ListExecutionsResponse(
                executions=[], next_page_token="def",
            ),
            metadata_service.ListExecutionsResponse(
                executions=[execution.Execution(),], next_page_token="ghi",
            ),
            metadata_service.ListExecutionsResponse(
                executions=[execution.Execution(), execution.Execution(),],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_executions(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, execution.Execution) for i in results)


def test_list_executions_pages():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_executions), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metadata_service.ListExecutionsResponse(
                executions=[
                    execution.Execution(),
                    execution.Execution(),
                    execution.Execution(),
                ],
                next_page_token="abc",
            ),
            metadata_service.ListExecutionsResponse(
                executions=[], next_page_token="def",
            ),
            metadata_service.ListExecutionsResponse(
                executions=[execution.Execution(),], next_page_token="ghi",
            ),
            metadata_service.ListExecutionsResponse(
                executions=[execution.Execution(), execution.Execution(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_executions(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_executions_async_pager():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_executions), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metadata_service.ListExecutionsResponse(
                executions=[
                    execution.Execution(),
                    execution.Execution(),
                    execution.Execution(),
                ],
                next_page_token="abc",
            ),
            metadata_service.ListExecutionsResponse(
                executions=[], next_page_token="def",
            ),
            metadata_service.ListExecutionsResponse(
                executions=[execution.Execution(),], next_page_token="ghi",
            ),
            metadata_service.ListExecutionsResponse(
                executions=[execution.Execution(), execution.Execution(),],
            ),
            RuntimeError,
        )
        async_pager = await client.list_executions(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, execution.Execution) for i in responses)


@pytest.mark.asyncio
async def test_list_executions_async_pages():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_executions), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metadata_service.ListExecutionsResponse(
                executions=[
                    execution.Execution(),
                    execution.Execution(),
                    execution.Execution(),
                ],
                next_page_token="abc",
            ),
            metadata_service.ListExecutionsResponse(
                executions=[], next_page_token="def",
            ),
            metadata_service.ListExecutionsResponse(
                executions=[execution.Execution(),], next_page_token="ghi",
            ),
            metadata_service.ListExecutionsResponse(
                executions=[execution.Execution(), execution.Execution(),],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_executions(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_update_execution(
    transport: str = "grpc", request_type=metadata_service.UpdateExecutionRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_execution), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_execution.Execution(
            name="name_value",
            display_name="display_name_value",
            state=gca_execution.Execution.State.NEW,
            etag="etag_value",
            schema_title="schema_title_value",
            schema_version="schema_version_value",
            description="description_value",
        )
        response = client.update_execution(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.UpdateExecutionRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_execution.Execution)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.state == gca_execution.Execution.State.NEW
    assert response.etag == "etag_value"
    assert response.schema_title == "schema_title_value"
    assert response.schema_version == "schema_version_value"
    assert response.description == "description_value"


def test_update_execution_from_dict():
    test_update_execution(request_type=dict)


def test_update_execution_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_execution), "__call__") as call:
        client.update_execution()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.UpdateExecutionRequest()


@pytest.mark.asyncio
async def test_update_execution_async(
    transport: str = "grpc_asyncio",
    request_type=metadata_service.UpdateExecutionRequest,
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_execution), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_execution.Execution(
                name="name_value",
                display_name="display_name_value",
                state=gca_execution.Execution.State.NEW,
                etag="etag_value",
                schema_title="schema_title_value",
                schema_version="schema_version_value",
                description="description_value",
            )
        )
        response = await client.update_execution(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.UpdateExecutionRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_execution.Execution)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.state == gca_execution.Execution.State.NEW
    assert response.etag == "etag_value"
    assert response.schema_title == "schema_title_value"
    assert response.schema_version == "schema_version_value"
    assert response.description == "description_value"


@pytest.mark.asyncio
async def test_update_execution_async_from_dict():
    await test_update_execution_async(request_type=dict)


def test_update_execution_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.UpdateExecutionRequest()

    request.execution.name = "execution.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_execution), "__call__") as call:
        call.return_value = gca_execution.Execution()
        client.update_execution(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "execution.name=execution.name/value",) in kw[
        "metadata"
    ]


@pytest.mark.asyncio
async def test_update_execution_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.UpdateExecutionRequest()

    request.execution.name = "execution.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_execution), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_execution.Execution()
        )
        await client.update_execution(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "execution.name=execution.name/value",) in kw[
        "metadata"
    ]


def test_update_execution_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_execution), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_execution.Execution()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_execution(
            execution=gca_execution.Execution(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].execution == gca_execution.Execution(name="name_value")
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


def test_update_execution_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_execution(
            metadata_service.UpdateExecutionRequest(),
            execution=gca_execution.Execution(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_execution_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_execution), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_execution.Execution()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_execution.Execution()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_execution(
            execution=gca_execution.Execution(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].execution == gca_execution.Execution(name="name_value")
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


@pytest.mark.asyncio
async def test_update_execution_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_execution(
            metadata_service.UpdateExecutionRequest(),
            execution=gca_execution.Execution(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


def test_delete_execution(
    transport: str = "grpc", request_type=metadata_service.DeleteExecutionRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_execution), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_execution(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.DeleteExecutionRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_execution_from_dict():
    test_delete_execution(request_type=dict)


def test_delete_execution_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_execution), "__call__") as call:
        client.delete_execution()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.DeleteExecutionRequest()


@pytest.mark.asyncio
async def test_delete_execution_async(
    transport: str = "grpc_asyncio",
    request_type=metadata_service.DeleteExecutionRequest,
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_execution), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_execution(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.DeleteExecutionRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_execution_async_from_dict():
    await test_delete_execution_async(request_type=dict)


def test_delete_execution_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.DeleteExecutionRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_execution), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_execution(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_execution_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.DeleteExecutionRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_execution), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_execution(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_execution_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_execution), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_execution(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_execution_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_execution(
            metadata_service.DeleteExecutionRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_execution_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_execution), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_execution(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_execution_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_execution(
            metadata_service.DeleteExecutionRequest(), name="name_value",
        )


def test_purge_executions(
    transport: str = "grpc", request_type=metadata_service.PurgeExecutionsRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.purge_executions), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.purge_executions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.PurgeExecutionsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_purge_executions_from_dict():
    test_purge_executions(request_type=dict)


def test_purge_executions_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.purge_executions), "__call__") as call:
        client.purge_executions()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.PurgeExecutionsRequest()


@pytest.mark.asyncio
async def test_purge_executions_async(
    transport: str = "grpc_asyncio",
    request_type=metadata_service.PurgeExecutionsRequest,
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.purge_executions), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.purge_executions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.PurgeExecutionsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_purge_executions_async_from_dict():
    await test_purge_executions_async(request_type=dict)


def test_purge_executions_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.PurgeExecutionsRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.purge_executions), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.purge_executions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_purge_executions_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.PurgeExecutionsRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.purge_executions), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.purge_executions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_purge_executions_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.purge_executions), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.purge_executions(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_purge_executions_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.purge_executions(
            metadata_service.PurgeExecutionsRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_purge_executions_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.purge_executions), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.purge_executions(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_purge_executions_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.purge_executions(
            metadata_service.PurgeExecutionsRequest(), parent="parent_value",
        )


def test_add_execution_events(
    transport: str = "grpc", request_type=metadata_service.AddExecutionEventsRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.add_execution_events), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.AddExecutionEventsResponse()
        response = client.add_execution_events(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.AddExecutionEventsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, metadata_service.AddExecutionEventsResponse)


def test_add_execution_events_from_dict():
    test_add_execution_events(request_type=dict)


def test_add_execution_events_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.add_execution_events), "__call__"
    ) as call:
        client.add_execution_events()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.AddExecutionEventsRequest()


@pytest.mark.asyncio
async def test_add_execution_events_async(
    transport: str = "grpc_asyncio",
    request_type=metadata_service.AddExecutionEventsRequest,
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.add_execution_events), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.AddExecutionEventsResponse()
        )
        response = await client.add_execution_events(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.AddExecutionEventsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, metadata_service.AddExecutionEventsResponse)


@pytest.mark.asyncio
async def test_add_execution_events_async_from_dict():
    await test_add_execution_events_async(request_type=dict)


def test_add_execution_events_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.AddExecutionEventsRequest()

    request.execution = "execution/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.add_execution_events), "__call__"
    ) as call:
        call.return_value = metadata_service.AddExecutionEventsResponse()
        client.add_execution_events(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "execution=execution/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_add_execution_events_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.AddExecutionEventsRequest()

    request.execution = "execution/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.add_execution_events), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.AddExecutionEventsResponse()
        )
        await client.add_execution_events(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "execution=execution/value",) in kw["metadata"]


def test_add_execution_events_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.add_execution_events), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.AddExecutionEventsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.add_execution_events(
            execution="execution_value",
            events=[event.Event(artifact="artifact_value")],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].execution == "execution_value"
        assert args[0].events == [event.Event(artifact="artifact_value")]


def test_add_execution_events_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.add_execution_events(
            metadata_service.AddExecutionEventsRequest(),
            execution="execution_value",
            events=[event.Event(artifact="artifact_value")],
        )


@pytest.mark.asyncio
async def test_add_execution_events_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.add_execution_events), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.AddExecutionEventsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.AddExecutionEventsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.add_execution_events(
            execution="execution_value",
            events=[event.Event(artifact="artifact_value")],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].execution == "execution_value"
        assert args[0].events == [event.Event(artifact="artifact_value")]


@pytest.mark.asyncio
async def test_add_execution_events_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.add_execution_events(
            metadata_service.AddExecutionEventsRequest(),
            execution="execution_value",
            events=[event.Event(artifact="artifact_value")],
        )


def test_query_execution_inputs_and_outputs(
    transport: str = "grpc",
    request_type=metadata_service.QueryExecutionInputsAndOutputsRequest,
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.query_execution_inputs_and_outputs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = lineage_subgraph.LineageSubgraph()
        response = client.query_execution_inputs_and_outputs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.QueryExecutionInputsAndOutputsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, lineage_subgraph.LineageSubgraph)


def test_query_execution_inputs_and_outputs_from_dict():
    test_query_execution_inputs_and_outputs(request_type=dict)


def test_query_execution_inputs_and_outputs_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.query_execution_inputs_and_outputs), "__call__"
    ) as call:
        client.query_execution_inputs_and_outputs()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.QueryExecutionInputsAndOutputsRequest()


@pytest.mark.asyncio
async def test_query_execution_inputs_and_outputs_async(
    transport: str = "grpc_asyncio",
    request_type=metadata_service.QueryExecutionInputsAndOutputsRequest,
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.query_execution_inputs_and_outputs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            lineage_subgraph.LineageSubgraph()
        )
        response = await client.query_execution_inputs_and_outputs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.QueryExecutionInputsAndOutputsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, lineage_subgraph.LineageSubgraph)


@pytest.mark.asyncio
async def test_query_execution_inputs_and_outputs_async_from_dict():
    await test_query_execution_inputs_and_outputs_async(request_type=dict)


def test_query_execution_inputs_and_outputs_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.QueryExecutionInputsAndOutputsRequest()

    request.execution = "execution/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.query_execution_inputs_and_outputs), "__call__"
    ) as call:
        call.return_value = lineage_subgraph.LineageSubgraph()
        client.query_execution_inputs_and_outputs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "execution=execution/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_query_execution_inputs_and_outputs_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.QueryExecutionInputsAndOutputsRequest()

    request.execution = "execution/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.query_execution_inputs_and_outputs), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            lineage_subgraph.LineageSubgraph()
        )
        await client.query_execution_inputs_and_outputs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "execution=execution/value",) in kw["metadata"]


def test_query_execution_inputs_and_outputs_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.query_execution_inputs_and_outputs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = lineage_subgraph.LineageSubgraph()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.query_execution_inputs_and_outputs(execution="execution_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].execution == "execution_value"


def test_query_execution_inputs_and_outputs_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.query_execution_inputs_and_outputs(
            metadata_service.QueryExecutionInputsAndOutputsRequest(),
            execution="execution_value",
        )


@pytest.mark.asyncio
async def test_query_execution_inputs_and_outputs_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.query_execution_inputs_and_outputs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = lineage_subgraph.LineageSubgraph()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            lineage_subgraph.LineageSubgraph()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.query_execution_inputs_and_outputs(
            execution="execution_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].execution == "execution_value"


@pytest.mark.asyncio
async def test_query_execution_inputs_and_outputs_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.query_execution_inputs_and_outputs(
            metadata_service.QueryExecutionInputsAndOutputsRequest(),
            execution="execution_value",
        )


def test_create_metadata_schema(
    transport: str = "grpc", request_type=metadata_service.CreateMetadataSchemaRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_metadata_schema), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_metadata_schema.MetadataSchema(
            name="name_value",
            schema_version="schema_version_value",
            schema="schema_value",
            schema_type=gca_metadata_schema.MetadataSchema.MetadataSchemaType.ARTIFACT_TYPE,
            description="description_value",
        )
        response = client.create_metadata_schema(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.CreateMetadataSchemaRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_metadata_schema.MetadataSchema)
    assert response.name == "name_value"
    assert response.schema_version == "schema_version_value"
    assert response.schema == "schema_value"
    assert (
        response.schema_type
        == gca_metadata_schema.MetadataSchema.MetadataSchemaType.ARTIFACT_TYPE
    )
    assert response.description == "description_value"


def test_create_metadata_schema_from_dict():
    test_create_metadata_schema(request_type=dict)


def test_create_metadata_schema_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_metadata_schema), "__call__"
    ) as call:
        client.create_metadata_schema()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.CreateMetadataSchemaRequest()


@pytest.mark.asyncio
async def test_create_metadata_schema_async(
    transport: str = "grpc_asyncio",
    request_type=metadata_service.CreateMetadataSchemaRequest,
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_metadata_schema), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_metadata_schema.MetadataSchema(
                name="name_value",
                schema_version="schema_version_value",
                schema="schema_value",
                schema_type=gca_metadata_schema.MetadataSchema.MetadataSchemaType.ARTIFACT_TYPE,
                description="description_value",
            )
        )
        response = await client.create_metadata_schema(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.CreateMetadataSchemaRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_metadata_schema.MetadataSchema)
    assert response.name == "name_value"
    assert response.schema_version == "schema_version_value"
    assert response.schema == "schema_value"
    assert (
        response.schema_type
        == gca_metadata_schema.MetadataSchema.MetadataSchemaType.ARTIFACT_TYPE
    )
    assert response.description == "description_value"


@pytest.mark.asyncio
async def test_create_metadata_schema_async_from_dict():
    await test_create_metadata_schema_async(request_type=dict)


def test_create_metadata_schema_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.CreateMetadataSchemaRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_metadata_schema), "__call__"
    ) as call:
        call.return_value = gca_metadata_schema.MetadataSchema()
        client.create_metadata_schema(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_metadata_schema_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.CreateMetadataSchemaRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_metadata_schema), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_metadata_schema.MetadataSchema()
        )
        await client.create_metadata_schema(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_metadata_schema_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_metadata_schema), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_metadata_schema.MetadataSchema()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_metadata_schema(
            parent="parent_value",
            metadata_schema=gca_metadata_schema.MetadataSchema(name="name_value"),
            metadata_schema_id="metadata_schema_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].metadata_schema == gca_metadata_schema.MetadataSchema(
            name="name_value"
        )
        assert args[0].metadata_schema_id == "metadata_schema_id_value"


def test_create_metadata_schema_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_metadata_schema(
            metadata_service.CreateMetadataSchemaRequest(),
            parent="parent_value",
            metadata_schema=gca_metadata_schema.MetadataSchema(name="name_value"),
            metadata_schema_id="metadata_schema_id_value",
        )


@pytest.mark.asyncio
async def test_create_metadata_schema_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_metadata_schema), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_metadata_schema.MetadataSchema()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_metadata_schema.MetadataSchema()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_metadata_schema(
            parent="parent_value",
            metadata_schema=gca_metadata_schema.MetadataSchema(name="name_value"),
            metadata_schema_id="metadata_schema_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].metadata_schema == gca_metadata_schema.MetadataSchema(
            name="name_value"
        )
        assert args[0].metadata_schema_id == "metadata_schema_id_value"


@pytest.mark.asyncio
async def test_create_metadata_schema_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_metadata_schema(
            metadata_service.CreateMetadataSchemaRequest(),
            parent="parent_value",
            metadata_schema=gca_metadata_schema.MetadataSchema(name="name_value"),
            metadata_schema_id="metadata_schema_id_value",
        )


def test_get_metadata_schema(
    transport: str = "grpc", request_type=metadata_service.GetMetadataSchemaRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_metadata_schema), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_schema.MetadataSchema(
            name="name_value",
            schema_version="schema_version_value",
            schema="schema_value",
            schema_type=metadata_schema.MetadataSchema.MetadataSchemaType.ARTIFACT_TYPE,
            description="description_value",
        )
        response = client.get_metadata_schema(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.GetMetadataSchemaRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, metadata_schema.MetadataSchema)
    assert response.name == "name_value"
    assert response.schema_version == "schema_version_value"
    assert response.schema == "schema_value"
    assert (
        response.schema_type
        == metadata_schema.MetadataSchema.MetadataSchemaType.ARTIFACT_TYPE
    )
    assert response.description == "description_value"


def test_get_metadata_schema_from_dict():
    test_get_metadata_schema(request_type=dict)


def test_get_metadata_schema_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_metadata_schema), "__call__"
    ) as call:
        client.get_metadata_schema()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.GetMetadataSchemaRequest()


@pytest.mark.asyncio
async def test_get_metadata_schema_async(
    transport: str = "grpc_asyncio",
    request_type=metadata_service.GetMetadataSchemaRequest,
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_metadata_schema), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_schema.MetadataSchema(
                name="name_value",
                schema_version="schema_version_value",
                schema="schema_value",
                schema_type=metadata_schema.MetadataSchema.MetadataSchemaType.ARTIFACT_TYPE,
                description="description_value",
            )
        )
        response = await client.get_metadata_schema(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.GetMetadataSchemaRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, metadata_schema.MetadataSchema)
    assert response.name == "name_value"
    assert response.schema_version == "schema_version_value"
    assert response.schema == "schema_value"
    assert (
        response.schema_type
        == metadata_schema.MetadataSchema.MetadataSchemaType.ARTIFACT_TYPE
    )
    assert response.description == "description_value"


@pytest.mark.asyncio
async def test_get_metadata_schema_async_from_dict():
    await test_get_metadata_schema_async(request_type=dict)


def test_get_metadata_schema_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.GetMetadataSchemaRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_metadata_schema), "__call__"
    ) as call:
        call.return_value = metadata_schema.MetadataSchema()
        client.get_metadata_schema(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_metadata_schema_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.GetMetadataSchemaRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_metadata_schema), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_schema.MetadataSchema()
        )
        await client.get_metadata_schema(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_metadata_schema_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_metadata_schema), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_schema.MetadataSchema()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_metadata_schema(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_metadata_schema_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_metadata_schema(
            metadata_service.GetMetadataSchemaRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_metadata_schema_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_metadata_schema), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_schema.MetadataSchema()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_schema.MetadataSchema()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_metadata_schema(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_metadata_schema_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_metadata_schema(
            metadata_service.GetMetadataSchemaRequest(), name="name_value",
        )


def test_list_metadata_schemas(
    transport: str = "grpc", request_type=metadata_service.ListMetadataSchemasRequest
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_metadata_schemas), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.ListMetadataSchemasResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_metadata_schemas(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.ListMetadataSchemasRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListMetadataSchemasPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_metadata_schemas_from_dict():
    test_list_metadata_schemas(request_type=dict)


def test_list_metadata_schemas_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_metadata_schemas), "__call__"
    ) as call:
        client.list_metadata_schemas()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.ListMetadataSchemasRequest()


@pytest.mark.asyncio
async def test_list_metadata_schemas_async(
    transport: str = "grpc_asyncio",
    request_type=metadata_service.ListMetadataSchemasRequest,
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_metadata_schemas), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.ListMetadataSchemasResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_metadata_schemas(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.ListMetadataSchemasRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListMetadataSchemasAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_metadata_schemas_async_from_dict():
    await test_list_metadata_schemas_async(request_type=dict)


def test_list_metadata_schemas_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.ListMetadataSchemasRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_metadata_schemas), "__call__"
    ) as call:
        call.return_value = metadata_service.ListMetadataSchemasResponse()
        client.list_metadata_schemas(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_metadata_schemas_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.ListMetadataSchemasRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_metadata_schemas), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.ListMetadataSchemasResponse()
        )
        await client.list_metadata_schemas(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_metadata_schemas_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_metadata_schemas), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.ListMetadataSchemasResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_metadata_schemas(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_metadata_schemas_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_metadata_schemas(
            metadata_service.ListMetadataSchemasRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_metadata_schemas_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_metadata_schemas), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = metadata_service.ListMetadataSchemasResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            metadata_service.ListMetadataSchemasResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_metadata_schemas(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_metadata_schemas_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_metadata_schemas(
            metadata_service.ListMetadataSchemasRequest(), parent="parent_value",
        )


def test_list_metadata_schemas_pager():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_metadata_schemas), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metadata_service.ListMetadataSchemasResponse(
                metadata_schemas=[
                    metadata_schema.MetadataSchema(),
                    metadata_schema.MetadataSchema(),
                    metadata_schema.MetadataSchema(),
                ],
                next_page_token="abc",
            ),
            metadata_service.ListMetadataSchemasResponse(
                metadata_schemas=[], next_page_token="def",
            ),
            metadata_service.ListMetadataSchemasResponse(
                metadata_schemas=[metadata_schema.MetadataSchema(),],
                next_page_token="ghi",
            ),
            metadata_service.ListMetadataSchemasResponse(
                metadata_schemas=[
                    metadata_schema.MetadataSchema(),
                    metadata_schema.MetadataSchema(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_metadata_schemas(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, metadata_schema.MetadataSchema) for i in results)


def test_list_metadata_schemas_pages():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_metadata_schemas), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metadata_service.ListMetadataSchemasResponse(
                metadata_schemas=[
                    metadata_schema.MetadataSchema(),
                    metadata_schema.MetadataSchema(),
                    metadata_schema.MetadataSchema(),
                ],
                next_page_token="abc",
            ),
            metadata_service.ListMetadataSchemasResponse(
                metadata_schemas=[], next_page_token="def",
            ),
            metadata_service.ListMetadataSchemasResponse(
                metadata_schemas=[metadata_schema.MetadataSchema(),],
                next_page_token="ghi",
            ),
            metadata_service.ListMetadataSchemasResponse(
                metadata_schemas=[
                    metadata_schema.MetadataSchema(),
                    metadata_schema.MetadataSchema(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_metadata_schemas(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_metadata_schemas_async_pager():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_metadata_schemas),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metadata_service.ListMetadataSchemasResponse(
                metadata_schemas=[
                    metadata_schema.MetadataSchema(),
                    metadata_schema.MetadataSchema(),
                    metadata_schema.MetadataSchema(),
                ],
                next_page_token="abc",
            ),
            metadata_service.ListMetadataSchemasResponse(
                metadata_schemas=[], next_page_token="def",
            ),
            metadata_service.ListMetadataSchemasResponse(
                metadata_schemas=[metadata_schema.MetadataSchema(),],
                next_page_token="ghi",
            ),
            metadata_service.ListMetadataSchemasResponse(
                metadata_schemas=[
                    metadata_schema.MetadataSchema(),
                    metadata_schema.MetadataSchema(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_metadata_schemas(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, metadata_schema.MetadataSchema) for i in responses)


@pytest.mark.asyncio
async def test_list_metadata_schemas_async_pages():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_metadata_schemas),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            metadata_service.ListMetadataSchemasResponse(
                metadata_schemas=[
                    metadata_schema.MetadataSchema(),
                    metadata_schema.MetadataSchema(),
                    metadata_schema.MetadataSchema(),
                ],
                next_page_token="abc",
            ),
            metadata_service.ListMetadataSchemasResponse(
                metadata_schemas=[], next_page_token="def",
            ),
            metadata_service.ListMetadataSchemasResponse(
                metadata_schemas=[metadata_schema.MetadataSchema(),],
                next_page_token="ghi",
            ),
            metadata_service.ListMetadataSchemasResponse(
                metadata_schemas=[
                    metadata_schema.MetadataSchema(),
                    metadata_schema.MetadataSchema(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_metadata_schemas(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_query_artifact_lineage_subgraph(
    transport: str = "grpc",
    request_type=metadata_service.QueryArtifactLineageSubgraphRequest,
):
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.query_artifact_lineage_subgraph), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = lineage_subgraph.LineageSubgraph()
        response = client.query_artifact_lineage_subgraph(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.QueryArtifactLineageSubgraphRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, lineage_subgraph.LineageSubgraph)


def test_query_artifact_lineage_subgraph_from_dict():
    test_query_artifact_lineage_subgraph(request_type=dict)


def test_query_artifact_lineage_subgraph_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.query_artifact_lineage_subgraph), "__call__"
    ) as call:
        client.query_artifact_lineage_subgraph()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.QueryArtifactLineageSubgraphRequest()


@pytest.mark.asyncio
async def test_query_artifact_lineage_subgraph_async(
    transport: str = "grpc_asyncio",
    request_type=metadata_service.QueryArtifactLineageSubgraphRequest,
):
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.query_artifact_lineage_subgraph), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            lineage_subgraph.LineageSubgraph()
        )
        response = await client.query_artifact_lineage_subgraph(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == metadata_service.QueryArtifactLineageSubgraphRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, lineage_subgraph.LineageSubgraph)


@pytest.mark.asyncio
async def test_query_artifact_lineage_subgraph_async_from_dict():
    await test_query_artifact_lineage_subgraph_async(request_type=dict)


def test_query_artifact_lineage_subgraph_field_headers():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.QueryArtifactLineageSubgraphRequest()

    request.artifact = "artifact/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.query_artifact_lineage_subgraph), "__call__"
    ) as call:
        call.return_value = lineage_subgraph.LineageSubgraph()
        client.query_artifact_lineage_subgraph(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "artifact=artifact/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_query_artifact_lineage_subgraph_field_headers_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = metadata_service.QueryArtifactLineageSubgraphRequest()

    request.artifact = "artifact/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.query_artifact_lineage_subgraph), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            lineage_subgraph.LineageSubgraph()
        )
        await client.query_artifact_lineage_subgraph(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "artifact=artifact/value",) in kw["metadata"]


def test_query_artifact_lineage_subgraph_flattened():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.query_artifact_lineage_subgraph), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = lineage_subgraph.LineageSubgraph()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.query_artifact_lineage_subgraph(artifact="artifact_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].artifact == "artifact_value"


def test_query_artifact_lineage_subgraph_flattened_error():
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.query_artifact_lineage_subgraph(
            metadata_service.QueryArtifactLineageSubgraphRequest(),
            artifact="artifact_value",
        )


@pytest.mark.asyncio
async def test_query_artifact_lineage_subgraph_flattened_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.query_artifact_lineage_subgraph), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = lineage_subgraph.LineageSubgraph()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            lineage_subgraph.LineageSubgraph()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.query_artifact_lineage_subgraph(
            artifact="artifact_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].artifact == "artifact_value"


@pytest.mark.asyncio
async def test_query_artifact_lineage_subgraph_flattened_error_async():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.query_artifact_lineage_subgraph(
            metadata_service.QueryArtifactLineageSubgraphRequest(),
            artifact="artifact_value",
        )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.MetadataServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = MetadataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(), transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.MetadataServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = MetadataServiceClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.MetadataServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = MetadataServiceClient(
            client_options={"scopes": ["1", "2"]}, transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.MetadataServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    client = MetadataServiceClient(transport=transport)
    assert client.transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.MetadataServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.MetadataServiceGrpcAsyncIOTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.MetadataServiceGrpcTransport,
        transports.MetadataServiceGrpcAsyncIOTransport,
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
    client = MetadataServiceClient(credentials=ga_credentials.AnonymousCredentials(),)
    assert isinstance(client.transport, transports.MetadataServiceGrpcTransport,)


def test_metadata_service_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(core_exceptions.DuplicateCredentialArgs):
        transport = transports.MetadataServiceTransport(
            credentials=ga_credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_metadata_service_base_transport():
    # Instantiate the base transport.
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.metadata_service.transports.MetadataServiceTransport.__init__"
    ) as Transport:
        Transport.return_value = None
        transport = transports.MetadataServiceTransport(
            credentials=ga_credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "create_metadata_store",
        "get_metadata_store",
        "list_metadata_stores",
        "delete_metadata_store",
        "create_artifact",
        "get_artifact",
        "list_artifacts",
        "update_artifact",
        "delete_artifact",
        "purge_artifacts",
        "create_context",
        "get_context",
        "list_contexts",
        "update_context",
        "delete_context",
        "purge_contexts",
        "add_context_artifacts_and_executions",
        "add_context_children",
        "query_context_lineage_subgraph",
        "create_execution",
        "get_execution",
        "list_executions",
        "update_execution",
        "delete_execution",
        "purge_executions",
        "add_execution_events",
        "query_execution_inputs_and_outputs",
        "create_metadata_schema",
        "get_metadata_schema",
        "list_metadata_schemas",
        "query_artifact_lineage_subgraph",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    # Additionally, the LRO client (a property) should
    # also raise NotImplementedError
    with pytest.raises(NotImplementedError):
        transport.operations_client


@requires_google_auth_gte_1_25_0
def test_metadata_service_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        google.auth, "load_credentials_from_file", autospec=True
    ) as load_creds, mock.patch(
        "google.cloud.aiplatform_v1beta1.services.metadata_service.transports.MetadataServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.MetadataServiceTransport(
            credentials_file="credentials.json", quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=None,
            default_scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


@requires_google_auth_lt_1_25_0
def test_metadata_service_base_transport_with_credentials_file_old_google_auth():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        google.auth, "load_credentials_from_file", autospec=True
    ) as load_creds, mock.patch(
        "google.cloud.aiplatform_v1beta1.services.metadata_service.transports.MetadataServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.MetadataServiceTransport(
            credentials_file="credentials.json", quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


def test_metadata_service_base_transport_with_adc():
    # Test the default credentials are used if credentials and credentials_file are None.
    with mock.patch.object(google.auth, "default", autospec=True) as adc, mock.patch(
        "google.cloud.aiplatform_v1beta1.services.metadata_service.transports.MetadataServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.MetadataServiceTransport()
        adc.assert_called_once()


@requires_google_auth_gte_1_25_0
def test_metadata_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        MetadataServiceClient()
        adc.assert_called_once_with(
            scopes=None,
            default_scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id=None,
        )


@requires_google_auth_lt_1_25_0
def test_metadata_service_auth_adc_old_google_auth():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        MetadataServiceClient()
        adc.assert_called_once_with(
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id=None,
        )


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.MetadataServiceGrpcTransport,
        transports.MetadataServiceGrpcAsyncIOTransport,
    ],
)
@requires_google_auth_gte_1_25_0
def test_metadata_service_transport_auth_adc(transport_class):
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
        transports.MetadataServiceGrpcTransport,
        transports.MetadataServiceGrpcAsyncIOTransport,
    ],
)
@requires_google_auth_lt_1_25_0
def test_metadata_service_transport_auth_adc_old_google_auth(transport_class):
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
        (transports.MetadataServiceGrpcTransport, grpc_helpers),
        (transports.MetadataServiceGrpcAsyncIOTransport, grpc_helpers_async),
    ],
)
def test_metadata_service_transport_create_channel(transport_class, grpc_helpers):
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
    "transport_class",
    [
        transports.MetadataServiceGrpcTransport,
        transports.MetadataServiceGrpcAsyncIOTransport,
    ],
)
def test_metadata_service_grpc_transport_client_cert_source_for_mtls(transport_class):
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
            scopes=None,
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


def test_metadata_service_host_no_port():
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="aiplatform.googleapis.com"
        ),
    )
    assert client.transport._host == "aiplatform.googleapis.com:443"


def test_metadata_service_host_with_port():
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="aiplatform.googleapis.com:8000"
        ),
    )
    assert client.transport._host == "aiplatform.googleapis.com:8000"


def test_metadata_service_grpc_transport_channel():
    channel = grpc.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.MetadataServiceGrpcTransport(
        host="squid.clam.whelk", channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


def test_metadata_service_grpc_asyncio_transport_channel():
    channel = aio.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.MetadataServiceGrpcAsyncIOTransport(
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
        transports.MetadataServiceGrpcTransport,
        transports.MetadataServiceGrpcAsyncIOTransport,
    ],
)
def test_metadata_service_transport_channel_mtls_with_client_cert_source(
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
                scopes=None,
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
        transports.MetadataServiceGrpcTransport,
        transports.MetadataServiceGrpcAsyncIOTransport,
    ],
)
def test_metadata_service_transport_channel_mtls_with_adc(transport_class):
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
                scopes=None,
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )
            assert transport.grpc_channel == mock_grpc_channel


def test_metadata_service_grpc_lro_client():
    client = MetadataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )
    transport = client.transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_metadata_service_grpc_lro_async_client():
    client = MetadataServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc_asyncio",
    )
    transport = client.transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsAsyncClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_artifact_path():
    project = "squid"
    location = "clam"
    metadata_store = "whelk"
    artifact = "octopus"
    expected = "projects/{project}/locations/{location}/metadataStores/{metadata_store}/artifacts/{artifact}".format(
        project=project,
        location=location,
        metadata_store=metadata_store,
        artifact=artifact,
    )
    actual = MetadataServiceClient.artifact_path(
        project, location, metadata_store, artifact
    )
    assert expected == actual


def test_parse_artifact_path():
    expected = {
        "project": "oyster",
        "location": "nudibranch",
        "metadata_store": "cuttlefish",
        "artifact": "mussel",
    }
    path = MetadataServiceClient.artifact_path(**expected)

    # Check that the path construction is reversible.
    actual = MetadataServiceClient.parse_artifact_path(path)
    assert expected == actual


def test_context_path():
    project = "winkle"
    location = "nautilus"
    metadata_store = "scallop"
    context = "abalone"
    expected = "projects/{project}/locations/{location}/metadataStores/{metadata_store}/contexts/{context}".format(
        project=project,
        location=location,
        metadata_store=metadata_store,
        context=context,
    )
    actual = MetadataServiceClient.context_path(
        project, location, metadata_store, context
    )
    assert expected == actual


def test_parse_context_path():
    expected = {
        "project": "squid",
        "location": "clam",
        "metadata_store": "whelk",
        "context": "octopus",
    }
    path = MetadataServiceClient.context_path(**expected)

    # Check that the path construction is reversible.
    actual = MetadataServiceClient.parse_context_path(path)
    assert expected == actual


def test_execution_path():
    project = "oyster"
    location = "nudibranch"
    metadata_store = "cuttlefish"
    execution = "mussel"
    expected = "projects/{project}/locations/{location}/metadataStores/{metadata_store}/executions/{execution}".format(
        project=project,
        location=location,
        metadata_store=metadata_store,
        execution=execution,
    )
    actual = MetadataServiceClient.execution_path(
        project, location, metadata_store, execution
    )
    assert expected == actual


def test_parse_execution_path():
    expected = {
        "project": "winkle",
        "location": "nautilus",
        "metadata_store": "scallop",
        "execution": "abalone",
    }
    path = MetadataServiceClient.execution_path(**expected)

    # Check that the path construction is reversible.
    actual = MetadataServiceClient.parse_execution_path(path)
    assert expected == actual


def test_metadata_schema_path():
    project = "squid"
    location = "clam"
    metadata_store = "whelk"
    metadata_schema = "octopus"
    expected = "projects/{project}/locations/{location}/metadataStores/{metadata_store}/metadataSchemas/{metadata_schema}".format(
        project=project,
        location=location,
        metadata_store=metadata_store,
        metadata_schema=metadata_schema,
    )
    actual = MetadataServiceClient.metadata_schema_path(
        project, location, metadata_store, metadata_schema
    )
    assert expected == actual


def test_parse_metadata_schema_path():
    expected = {
        "project": "oyster",
        "location": "nudibranch",
        "metadata_store": "cuttlefish",
        "metadata_schema": "mussel",
    }
    path = MetadataServiceClient.metadata_schema_path(**expected)

    # Check that the path construction is reversible.
    actual = MetadataServiceClient.parse_metadata_schema_path(path)
    assert expected == actual


def test_metadata_store_path():
    project = "winkle"
    location = "nautilus"
    metadata_store = "scallop"
    expected = "projects/{project}/locations/{location}/metadataStores/{metadata_store}".format(
        project=project, location=location, metadata_store=metadata_store,
    )
    actual = MetadataServiceClient.metadata_store_path(
        project, location, metadata_store
    )
    assert expected == actual


def test_parse_metadata_store_path():
    expected = {
        "project": "abalone",
        "location": "squid",
        "metadata_store": "clam",
    }
    path = MetadataServiceClient.metadata_store_path(**expected)

    # Check that the path construction is reversible.
    actual = MetadataServiceClient.parse_metadata_store_path(path)
    assert expected == actual


def test_common_billing_account_path():
    billing_account = "whelk"
    expected = "billingAccounts/{billing_account}".format(
        billing_account=billing_account,
    )
    actual = MetadataServiceClient.common_billing_account_path(billing_account)
    assert expected == actual


def test_parse_common_billing_account_path():
    expected = {
        "billing_account": "octopus",
    }
    path = MetadataServiceClient.common_billing_account_path(**expected)

    # Check that the path construction is reversible.
    actual = MetadataServiceClient.parse_common_billing_account_path(path)
    assert expected == actual


def test_common_folder_path():
    folder = "oyster"
    expected = "folders/{folder}".format(folder=folder,)
    actual = MetadataServiceClient.common_folder_path(folder)
    assert expected == actual


def test_parse_common_folder_path():
    expected = {
        "folder": "nudibranch",
    }
    path = MetadataServiceClient.common_folder_path(**expected)

    # Check that the path construction is reversible.
    actual = MetadataServiceClient.parse_common_folder_path(path)
    assert expected == actual


def test_common_organization_path():
    organization = "cuttlefish"
    expected = "organizations/{organization}".format(organization=organization,)
    actual = MetadataServiceClient.common_organization_path(organization)
    assert expected == actual


def test_parse_common_organization_path():
    expected = {
        "organization": "mussel",
    }
    path = MetadataServiceClient.common_organization_path(**expected)

    # Check that the path construction is reversible.
    actual = MetadataServiceClient.parse_common_organization_path(path)
    assert expected == actual


def test_common_project_path():
    project = "winkle"
    expected = "projects/{project}".format(project=project,)
    actual = MetadataServiceClient.common_project_path(project)
    assert expected == actual


def test_parse_common_project_path():
    expected = {
        "project": "nautilus",
    }
    path = MetadataServiceClient.common_project_path(**expected)

    # Check that the path construction is reversible.
    actual = MetadataServiceClient.parse_common_project_path(path)
    assert expected == actual


def test_common_location_path():
    project = "scallop"
    location = "abalone"
    expected = "projects/{project}/locations/{location}".format(
        project=project, location=location,
    )
    actual = MetadataServiceClient.common_location_path(project, location)
    assert expected == actual


def test_parse_common_location_path():
    expected = {
        "project": "squid",
        "location": "clam",
    }
    path = MetadataServiceClient.common_location_path(**expected)

    # Check that the path construction is reversible.
    actual = MetadataServiceClient.parse_common_location_path(path)
    assert expected == actual


def test_client_withDEFAULT_CLIENT_INFO():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(
        transports.MetadataServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        client = MetadataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(
        transports.MetadataServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        transport_class = MetadataServiceClient.get_transport_class()
        transport = transport_class(
            credentials=ga_credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)
