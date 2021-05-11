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
from google.cloud.aiplatform_v1beta1.services.featurestore_service import (
    FeaturestoreServiceAsyncClient,
)
from google.cloud.aiplatform_v1beta1.services.featurestore_service import (
    FeaturestoreServiceClient,
)
from google.cloud.aiplatform_v1beta1.services.featurestore_service import pagers
from google.cloud.aiplatform_v1beta1.services.featurestore_service import transports
from google.cloud.aiplatform_v1beta1.services.featurestore_service.transports.base import (
    _API_CORE_VERSION,
)
from google.cloud.aiplatform_v1beta1.services.featurestore_service.transports.base import (
    _GOOGLE_AUTH_VERSION,
)
from google.cloud.aiplatform_v1beta1.types import entity_type
from google.cloud.aiplatform_v1beta1.types import entity_type as gca_entity_type
from google.cloud.aiplatform_v1beta1.types import feature
from google.cloud.aiplatform_v1beta1.types import feature as gca_feature
from google.cloud.aiplatform_v1beta1.types import feature_monitoring_stats
from google.cloud.aiplatform_v1beta1.types import feature_selector
from google.cloud.aiplatform_v1beta1.types import featurestore
from google.cloud.aiplatform_v1beta1.types import featurestore as gca_featurestore
from google.cloud.aiplatform_v1beta1.types import featurestore_monitoring
from google.cloud.aiplatform_v1beta1.types import featurestore_service
from google.cloud.aiplatform_v1beta1.types import io
from google.cloud.aiplatform_v1beta1.types import operation as gca_operation
from google.longrunning import operations_pb2
from google.oauth2 import service_account
from google.protobuf import duration_pb2  # type: ignore
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

    assert FeaturestoreServiceClient._get_default_mtls_endpoint(None) is None
    assert (
        FeaturestoreServiceClient._get_default_mtls_endpoint(api_endpoint)
        == api_mtls_endpoint
    )
    assert (
        FeaturestoreServiceClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        FeaturestoreServiceClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        FeaturestoreServiceClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        FeaturestoreServiceClient._get_default_mtls_endpoint(non_googleapi)
        == non_googleapi
    )


@pytest.mark.parametrize(
    "client_class", [FeaturestoreServiceClient, FeaturestoreServiceAsyncClient,]
)
def test_featurestore_service_client_from_service_account_info(client_class):
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
    "client_class", [FeaturestoreServiceClient, FeaturestoreServiceAsyncClient,]
)
def test_featurestore_service_client_from_service_account_file(client_class):
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


def test_featurestore_service_client_get_transport_class():
    transport = FeaturestoreServiceClient.get_transport_class()
    available_transports = [
        transports.FeaturestoreServiceGrpcTransport,
    ]
    assert transport in available_transports

    transport = FeaturestoreServiceClient.get_transport_class("grpc")
    assert transport == transports.FeaturestoreServiceGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (
            FeaturestoreServiceClient,
            transports.FeaturestoreServiceGrpcTransport,
            "grpc",
        ),
        (
            FeaturestoreServiceAsyncClient,
            transports.FeaturestoreServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
@mock.patch.object(
    FeaturestoreServiceClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(FeaturestoreServiceClient),
)
@mock.patch.object(
    FeaturestoreServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(FeaturestoreServiceAsyncClient),
)
def test_featurestore_service_client_client_options(
    client_class, transport_class, transport_name
):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(FeaturestoreServiceClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=ga_credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(FeaturestoreServiceClient, "get_transport_class") as gtc:
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
            FeaturestoreServiceClient,
            transports.FeaturestoreServiceGrpcTransport,
            "grpc",
            "true",
        ),
        (
            FeaturestoreServiceAsyncClient,
            transports.FeaturestoreServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "true",
        ),
        (
            FeaturestoreServiceClient,
            transports.FeaturestoreServiceGrpcTransport,
            "grpc",
            "false",
        ),
        (
            FeaturestoreServiceAsyncClient,
            transports.FeaturestoreServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "false",
        ),
    ],
)
@mock.patch.object(
    FeaturestoreServiceClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(FeaturestoreServiceClient),
)
@mock.patch.object(
    FeaturestoreServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(FeaturestoreServiceAsyncClient),
)
@mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"})
def test_featurestore_service_client_mtls_env_auto(
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
        (
            FeaturestoreServiceClient,
            transports.FeaturestoreServiceGrpcTransport,
            "grpc",
        ),
        (
            FeaturestoreServiceAsyncClient,
            transports.FeaturestoreServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_featurestore_service_client_client_options_scopes(
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
        (
            FeaturestoreServiceClient,
            transports.FeaturestoreServiceGrpcTransport,
            "grpc",
        ),
        (
            FeaturestoreServiceAsyncClient,
            transports.FeaturestoreServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_featurestore_service_client_client_options_credentials_file(
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


def test_featurestore_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.featurestore_service.transports.FeaturestoreServiceGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = FeaturestoreServiceClient(
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


def test_create_featurestore(
    transport: str = "grpc", request_type=featurestore_service.CreateFeaturestoreRequest
):
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_featurestore), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.create_featurestore(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.CreateFeaturestoreRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_create_featurestore_from_dict():
    test_create_featurestore(request_type=dict)


def test_create_featurestore_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_featurestore), "__call__"
    ) as call:
        client.create_featurestore()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.CreateFeaturestoreRequest()


@pytest.mark.asyncio
async def test_create_featurestore_async(
    transport: str = "grpc_asyncio",
    request_type=featurestore_service.CreateFeaturestoreRequest,
):
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_featurestore), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.create_featurestore(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.CreateFeaturestoreRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_create_featurestore_async_from_dict():
    await test_create_featurestore_async(request_type=dict)


def test_create_featurestore_field_headers():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.CreateFeaturestoreRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_featurestore), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.create_featurestore(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_featurestore_field_headers_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.CreateFeaturestoreRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_featurestore), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.create_featurestore(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_featurestore_flattened():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_featurestore), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_featurestore(
            parent="parent_value",
            featurestore=gca_featurestore.Featurestore(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].featurestore == gca_featurestore.Featurestore(name="name_value")


def test_create_featurestore_flattened_error():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_featurestore(
            featurestore_service.CreateFeaturestoreRequest(),
            parent="parent_value",
            featurestore=gca_featurestore.Featurestore(name="name_value"),
        )


@pytest.mark.asyncio
async def test_create_featurestore_flattened_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_featurestore), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_featurestore(
            parent="parent_value",
            featurestore=gca_featurestore.Featurestore(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].featurestore == gca_featurestore.Featurestore(name="name_value")


@pytest.mark.asyncio
async def test_create_featurestore_flattened_error_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_featurestore(
            featurestore_service.CreateFeaturestoreRequest(),
            parent="parent_value",
            featurestore=gca_featurestore.Featurestore(name="name_value"),
        )


def test_get_featurestore(
    transport: str = "grpc", request_type=featurestore_service.GetFeaturestoreRequest
):
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_featurestore), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = featurestore.Featurestore(
            name="name_value",
            etag="etag_value",
            state=featurestore.Featurestore.State.STABLE,
        )
        response = client.get_featurestore(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.GetFeaturestoreRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, featurestore.Featurestore)
    assert response.name == "name_value"
    assert response.etag == "etag_value"
    assert response.state == featurestore.Featurestore.State.STABLE


def test_get_featurestore_from_dict():
    test_get_featurestore(request_type=dict)


def test_get_featurestore_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_featurestore), "__call__") as call:
        client.get_featurestore()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.GetFeaturestoreRequest()


@pytest.mark.asyncio
async def test_get_featurestore_async(
    transport: str = "grpc_asyncio",
    request_type=featurestore_service.GetFeaturestoreRequest,
):
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_featurestore), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            featurestore.Featurestore(
                name="name_value",
                etag="etag_value",
                state=featurestore.Featurestore.State.STABLE,
            )
        )
        response = await client.get_featurestore(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.GetFeaturestoreRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, featurestore.Featurestore)
    assert response.name == "name_value"
    assert response.etag == "etag_value"
    assert response.state == featurestore.Featurestore.State.STABLE


@pytest.mark.asyncio
async def test_get_featurestore_async_from_dict():
    await test_get_featurestore_async(request_type=dict)


def test_get_featurestore_field_headers():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.GetFeaturestoreRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_featurestore), "__call__") as call:
        call.return_value = featurestore.Featurestore()
        client.get_featurestore(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_featurestore_field_headers_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.GetFeaturestoreRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_featurestore), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            featurestore.Featurestore()
        )
        await client.get_featurestore(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_featurestore_flattened():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_featurestore), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = featurestore.Featurestore()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_featurestore(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_featurestore_flattened_error():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_featurestore(
            featurestore_service.GetFeaturestoreRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_featurestore_flattened_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_featurestore), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = featurestore.Featurestore()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            featurestore.Featurestore()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_featurestore(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_featurestore_flattened_error_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_featurestore(
            featurestore_service.GetFeaturestoreRequest(), name="name_value",
        )


def test_list_featurestores(
    transport: str = "grpc", request_type=featurestore_service.ListFeaturestoresRequest
):
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_featurestores), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = featurestore_service.ListFeaturestoresResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_featurestores(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.ListFeaturestoresRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListFeaturestoresPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_featurestores_from_dict():
    test_list_featurestores(request_type=dict)


def test_list_featurestores_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_featurestores), "__call__"
    ) as call:
        client.list_featurestores()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.ListFeaturestoresRequest()


@pytest.mark.asyncio
async def test_list_featurestores_async(
    transport: str = "grpc_asyncio",
    request_type=featurestore_service.ListFeaturestoresRequest,
):
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_featurestores), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            featurestore_service.ListFeaturestoresResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_featurestores(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.ListFeaturestoresRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListFeaturestoresAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_featurestores_async_from_dict():
    await test_list_featurestores_async(request_type=dict)


def test_list_featurestores_field_headers():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.ListFeaturestoresRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_featurestores), "__call__"
    ) as call:
        call.return_value = featurestore_service.ListFeaturestoresResponse()
        client.list_featurestores(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_featurestores_field_headers_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.ListFeaturestoresRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_featurestores), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            featurestore_service.ListFeaturestoresResponse()
        )
        await client.list_featurestores(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_featurestores_flattened():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_featurestores), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = featurestore_service.ListFeaturestoresResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_featurestores(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_featurestores_flattened_error():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_featurestores(
            featurestore_service.ListFeaturestoresRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_featurestores_flattened_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_featurestores), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = featurestore_service.ListFeaturestoresResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            featurestore_service.ListFeaturestoresResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_featurestores(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_featurestores_flattened_error_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_featurestores(
            featurestore_service.ListFeaturestoresRequest(), parent="parent_value",
        )


def test_list_featurestores_pager():
    client = FeaturestoreServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_featurestores), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            featurestore_service.ListFeaturestoresResponse(
                featurestores=[
                    featurestore.Featurestore(),
                    featurestore.Featurestore(),
                    featurestore.Featurestore(),
                ],
                next_page_token="abc",
            ),
            featurestore_service.ListFeaturestoresResponse(
                featurestores=[], next_page_token="def",
            ),
            featurestore_service.ListFeaturestoresResponse(
                featurestores=[featurestore.Featurestore(),], next_page_token="ghi",
            ),
            featurestore_service.ListFeaturestoresResponse(
                featurestores=[
                    featurestore.Featurestore(),
                    featurestore.Featurestore(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_featurestores(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, featurestore.Featurestore) for i in results)


def test_list_featurestores_pages():
    client = FeaturestoreServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_featurestores), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            featurestore_service.ListFeaturestoresResponse(
                featurestores=[
                    featurestore.Featurestore(),
                    featurestore.Featurestore(),
                    featurestore.Featurestore(),
                ],
                next_page_token="abc",
            ),
            featurestore_service.ListFeaturestoresResponse(
                featurestores=[], next_page_token="def",
            ),
            featurestore_service.ListFeaturestoresResponse(
                featurestores=[featurestore.Featurestore(),], next_page_token="ghi",
            ),
            featurestore_service.ListFeaturestoresResponse(
                featurestores=[
                    featurestore.Featurestore(),
                    featurestore.Featurestore(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_featurestores(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_featurestores_async_pager():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_featurestores),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            featurestore_service.ListFeaturestoresResponse(
                featurestores=[
                    featurestore.Featurestore(),
                    featurestore.Featurestore(),
                    featurestore.Featurestore(),
                ],
                next_page_token="abc",
            ),
            featurestore_service.ListFeaturestoresResponse(
                featurestores=[], next_page_token="def",
            ),
            featurestore_service.ListFeaturestoresResponse(
                featurestores=[featurestore.Featurestore(),], next_page_token="ghi",
            ),
            featurestore_service.ListFeaturestoresResponse(
                featurestores=[
                    featurestore.Featurestore(),
                    featurestore.Featurestore(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_featurestores(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, featurestore.Featurestore) for i in responses)


@pytest.mark.asyncio
async def test_list_featurestores_async_pages():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_featurestores),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            featurestore_service.ListFeaturestoresResponse(
                featurestores=[
                    featurestore.Featurestore(),
                    featurestore.Featurestore(),
                    featurestore.Featurestore(),
                ],
                next_page_token="abc",
            ),
            featurestore_service.ListFeaturestoresResponse(
                featurestores=[], next_page_token="def",
            ),
            featurestore_service.ListFeaturestoresResponse(
                featurestores=[featurestore.Featurestore(),], next_page_token="ghi",
            ),
            featurestore_service.ListFeaturestoresResponse(
                featurestores=[
                    featurestore.Featurestore(),
                    featurestore.Featurestore(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_featurestores(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_update_featurestore(
    transport: str = "grpc", request_type=featurestore_service.UpdateFeaturestoreRequest
):
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_featurestore), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.update_featurestore(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.UpdateFeaturestoreRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_update_featurestore_from_dict():
    test_update_featurestore(request_type=dict)


def test_update_featurestore_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_featurestore), "__call__"
    ) as call:
        client.update_featurestore()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.UpdateFeaturestoreRequest()


@pytest.mark.asyncio
async def test_update_featurestore_async(
    transport: str = "grpc_asyncio",
    request_type=featurestore_service.UpdateFeaturestoreRequest,
):
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_featurestore), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.update_featurestore(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.UpdateFeaturestoreRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_update_featurestore_async_from_dict():
    await test_update_featurestore_async(request_type=dict)


def test_update_featurestore_field_headers():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.UpdateFeaturestoreRequest()

    request.featurestore.name = "featurestore.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_featurestore), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.update_featurestore(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "featurestore.name=featurestore.name/value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_featurestore_field_headers_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.UpdateFeaturestoreRequest()

    request.featurestore.name = "featurestore.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_featurestore), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.update_featurestore(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "featurestore.name=featurestore.name/value",
    ) in kw["metadata"]


def test_update_featurestore_flattened():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_featurestore), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_featurestore(
            featurestore=gca_featurestore.Featurestore(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].featurestore == gca_featurestore.Featurestore(name="name_value")
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


def test_update_featurestore_flattened_error():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_featurestore(
            featurestore_service.UpdateFeaturestoreRequest(),
            featurestore=gca_featurestore.Featurestore(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_featurestore_flattened_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_featurestore), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_featurestore(
            featurestore=gca_featurestore.Featurestore(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].featurestore == gca_featurestore.Featurestore(name="name_value")
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


@pytest.mark.asyncio
async def test_update_featurestore_flattened_error_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_featurestore(
            featurestore_service.UpdateFeaturestoreRequest(),
            featurestore=gca_featurestore.Featurestore(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


def test_delete_featurestore(
    transport: str = "grpc", request_type=featurestore_service.DeleteFeaturestoreRequest
):
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_featurestore), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_featurestore(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.DeleteFeaturestoreRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_featurestore_from_dict():
    test_delete_featurestore(request_type=dict)


def test_delete_featurestore_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_featurestore), "__call__"
    ) as call:
        client.delete_featurestore()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.DeleteFeaturestoreRequest()


@pytest.mark.asyncio
async def test_delete_featurestore_async(
    transport: str = "grpc_asyncio",
    request_type=featurestore_service.DeleteFeaturestoreRequest,
):
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_featurestore), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_featurestore(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.DeleteFeaturestoreRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_featurestore_async_from_dict():
    await test_delete_featurestore_async(request_type=dict)


def test_delete_featurestore_field_headers():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.DeleteFeaturestoreRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_featurestore), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_featurestore(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_featurestore_field_headers_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.DeleteFeaturestoreRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_featurestore), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_featurestore(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_featurestore_flattened():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_featurestore), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_featurestore(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_featurestore_flattened_error():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_featurestore(
            featurestore_service.DeleteFeaturestoreRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_featurestore_flattened_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_featurestore), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_featurestore(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_featurestore_flattened_error_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_featurestore(
            featurestore_service.DeleteFeaturestoreRequest(), name="name_value",
        )


def test_create_entity_type(
    transport: str = "grpc", request_type=featurestore_service.CreateEntityTypeRequest
):
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_entity_type), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.create_entity_type(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.CreateEntityTypeRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_create_entity_type_from_dict():
    test_create_entity_type(request_type=dict)


def test_create_entity_type_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_entity_type), "__call__"
    ) as call:
        client.create_entity_type()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.CreateEntityTypeRequest()


@pytest.mark.asyncio
async def test_create_entity_type_async(
    transport: str = "grpc_asyncio",
    request_type=featurestore_service.CreateEntityTypeRequest,
):
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_entity_type), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.create_entity_type(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.CreateEntityTypeRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_create_entity_type_async_from_dict():
    await test_create_entity_type_async(request_type=dict)


def test_create_entity_type_field_headers():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.CreateEntityTypeRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_entity_type), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.create_entity_type(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_entity_type_field_headers_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.CreateEntityTypeRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_entity_type), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.create_entity_type(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_entity_type_flattened():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_entity_type), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_entity_type(
            parent="parent_value",
            entity_type=gca_entity_type.EntityType(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].entity_type == gca_entity_type.EntityType(name="name_value")


def test_create_entity_type_flattened_error():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_entity_type(
            featurestore_service.CreateEntityTypeRequest(),
            parent="parent_value",
            entity_type=gca_entity_type.EntityType(name="name_value"),
        )


@pytest.mark.asyncio
async def test_create_entity_type_flattened_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_entity_type), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_entity_type(
            parent="parent_value",
            entity_type=gca_entity_type.EntityType(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].entity_type == gca_entity_type.EntityType(name="name_value")


@pytest.mark.asyncio
async def test_create_entity_type_flattened_error_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_entity_type(
            featurestore_service.CreateEntityTypeRequest(),
            parent="parent_value",
            entity_type=gca_entity_type.EntityType(name="name_value"),
        )


def test_get_entity_type(
    transport: str = "grpc", request_type=featurestore_service.GetEntityTypeRequest
):
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_entity_type), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = entity_type.EntityType(
            name="name_value", description="description_value", etag="etag_value",
        )
        response = client.get_entity_type(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.GetEntityTypeRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, entity_type.EntityType)
    assert response.name == "name_value"
    assert response.description == "description_value"
    assert response.etag == "etag_value"


def test_get_entity_type_from_dict():
    test_get_entity_type(request_type=dict)


def test_get_entity_type_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_entity_type), "__call__") as call:
        client.get_entity_type()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.GetEntityTypeRequest()


@pytest.mark.asyncio
async def test_get_entity_type_async(
    transport: str = "grpc_asyncio",
    request_type=featurestore_service.GetEntityTypeRequest,
):
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_entity_type), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            entity_type.EntityType(
                name="name_value", description="description_value", etag="etag_value",
            )
        )
        response = await client.get_entity_type(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.GetEntityTypeRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, entity_type.EntityType)
    assert response.name == "name_value"
    assert response.description == "description_value"
    assert response.etag == "etag_value"


@pytest.mark.asyncio
async def test_get_entity_type_async_from_dict():
    await test_get_entity_type_async(request_type=dict)


def test_get_entity_type_field_headers():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.GetEntityTypeRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_entity_type), "__call__") as call:
        call.return_value = entity_type.EntityType()
        client.get_entity_type(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_entity_type_field_headers_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.GetEntityTypeRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_entity_type), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            entity_type.EntityType()
        )
        await client.get_entity_type(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_entity_type_flattened():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_entity_type), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = entity_type.EntityType()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_entity_type(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_entity_type_flattened_error():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_entity_type(
            featurestore_service.GetEntityTypeRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_entity_type_flattened_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_entity_type), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = entity_type.EntityType()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            entity_type.EntityType()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_entity_type(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_entity_type_flattened_error_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_entity_type(
            featurestore_service.GetEntityTypeRequest(), name="name_value",
        )


def test_list_entity_types(
    transport: str = "grpc", request_type=featurestore_service.ListEntityTypesRequest
):
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_entity_types), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = featurestore_service.ListEntityTypesResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_entity_types(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.ListEntityTypesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListEntityTypesPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_entity_types_from_dict():
    test_list_entity_types(request_type=dict)


def test_list_entity_types_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_entity_types), "__call__"
    ) as call:
        client.list_entity_types()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.ListEntityTypesRequest()


@pytest.mark.asyncio
async def test_list_entity_types_async(
    transport: str = "grpc_asyncio",
    request_type=featurestore_service.ListEntityTypesRequest,
):
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_entity_types), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            featurestore_service.ListEntityTypesResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_entity_types(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.ListEntityTypesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListEntityTypesAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_entity_types_async_from_dict():
    await test_list_entity_types_async(request_type=dict)


def test_list_entity_types_field_headers():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.ListEntityTypesRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_entity_types), "__call__"
    ) as call:
        call.return_value = featurestore_service.ListEntityTypesResponse()
        client.list_entity_types(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_entity_types_field_headers_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.ListEntityTypesRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_entity_types), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            featurestore_service.ListEntityTypesResponse()
        )
        await client.list_entity_types(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_entity_types_flattened():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_entity_types), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = featurestore_service.ListEntityTypesResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_entity_types(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_entity_types_flattened_error():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_entity_types(
            featurestore_service.ListEntityTypesRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_entity_types_flattened_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_entity_types), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = featurestore_service.ListEntityTypesResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            featurestore_service.ListEntityTypesResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_entity_types(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_entity_types_flattened_error_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_entity_types(
            featurestore_service.ListEntityTypesRequest(), parent="parent_value",
        )


def test_list_entity_types_pager():
    client = FeaturestoreServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_entity_types), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            featurestore_service.ListEntityTypesResponse(
                entity_types=[
                    entity_type.EntityType(),
                    entity_type.EntityType(),
                    entity_type.EntityType(),
                ],
                next_page_token="abc",
            ),
            featurestore_service.ListEntityTypesResponse(
                entity_types=[], next_page_token="def",
            ),
            featurestore_service.ListEntityTypesResponse(
                entity_types=[entity_type.EntityType(),], next_page_token="ghi",
            ),
            featurestore_service.ListEntityTypesResponse(
                entity_types=[entity_type.EntityType(), entity_type.EntityType(),],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_entity_types(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, entity_type.EntityType) for i in results)


def test_list_entity_types_pages():
    client = FeaturestoreServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_entity_types), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            featurestore_service.ListEntityTypesResponse(
                entity_types=[
                    entity_type.EntityType(),
                    entity_type.EntityType(),
                    entity_type.EntityType(),
                ],
                next_page_token="abc",
            ),
            featurestore_service.ListEntityTypesResponse(
                entity_types=[], next_page_token="def",
            ),
            featurestore_service.ListEntityTypesResponse(
                entity_types=[entity_type.EntityType(),], next_page_token="ghi",
            ),
            featurestore_service.ListEntityTypesResponse(
                entity_types=[entity_type.EntityType(), entity_type.EntityType(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_entity_types(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_entity_types_async_pager():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_entity_types),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            featurestore_service.ListEntityTypesResponse(
                entity_types=[
                    entity_type.EntityType(),
                    entity_type.EntityType(),
                    entity_type.EntityType(),
                ],
                next_page_token="abc",
            ),
            featurestore_service.ListEntityTypesResponse(
                entity_types=[], next_page_token="def",
            ),
            featurestore_service.ListEntityTypesResponse(
                entity_types=[entity_type.EntityType(),], next_page_token="ghi",
            ),
            featurestore_service.ListEntityTypesResponse(
                entity_types=[entity_type.EntityType(), entity_type.EntityType(),],
            ),
            RuntimeError,
        )
        async_pager = await client.list_entity_types(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, entity_type.EntityType) for i in responses)


@pytest.mark.asyncio
async def test_list_entity_types_async_pages():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_entity_types),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            featurestore_service.ListEntityTypesResponse(
                entity_types=[
                    entity_type.EntityType(),
                    entity_type.EntityType(),
                    entity_type.EntityType(),
                ],
                next_page_token="abc",
            ),
            featurestore_service.ListEntityTypesResponse(
                entity_types=[], next_page_token="def",
            ),
            featurestore_service.ListEntityTypesResponse(
                entity_types=[entity_type.EntityType(),], next_page_token="ghi",
            ),
            featurestore_service.ListEntityTypesResponse(
                entity_types=[entity_type.EntityType(), entity_type.EntityType(),],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_entity_types(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_update_entity_type(
    transport: str = "grpc", request_type=featurestore_service.UpdateEntityTypeRequest
):
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_entity_type), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_entity_type.EntityType(
            name="name_value", description="description_value", etag="etag_value",
        )
        response = client.update_entity_type(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.UpdateEntityTypeRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_entity_type.EntityType)
    assert response.name == "name_value"
    assert response.description == "description_value"
    assert response.etag == "etag_value"


def test_update_entity_type_from_dict():
    test_update_entity_type(request_type=dict)


def test_update_entity_type_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_entity_type), "__call__"
    ) as call:
        client.update_entity_type()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.UpdateEntityTypeRequest()


@pytest.mark.asyncio
async def test_update_entity_type_async(
    transport: str = "grpc_asyncio",
    request_type=featurestore_service.UpdateEntityTypeRequest,
):
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_entity_type), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_entity_type.EntityType(
                name="name_value", description="description_value", etag="etag_value",
            )
        )
        response = await client.update_entity_type(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.UpdateEntityTypeRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_entity_type.EntityType)
    assert response.name == "name_value"
    assert response.description == "description_value"
    assert response.etag == "etag_value"


@pytest.mark.asyncio
async def test_update_entity_type_async_from_dict():
    await test_update_entity_type_async(request_type=dict)


def test_update_entity_type_field_headers():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.UpdateEntityTypeRequest()

    request.entity_type.name = "entity_type.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_entity_type), "__call__"
    ) as call:
        call.return_value = gca_entity_type.EntityType()
        client.update_entity_type(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "entity_type.name=entity_type.name/value",) in kw[
        "metadata"
    ]


@pytest.mark.asyncio
async def test_update_entity_type_field_headers_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.UpdateEntityTypeRequest()

    request.entity_type.name = "entity_type.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_entity_type), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_entity_type.EntityType()
        )
        await client.update_entity_type(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "entity_type.name=entity_type.name/value",) in kw[
        "metadata"
    ]


def test_update_entity_type_flattened():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_entity_type), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_entity_type.EntityType()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_entity_type(
            entity_type=gca_entity_type.EntityType(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].entity_type == gca_entity_type.EntityType(name="name_value")
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


def test_update_entity_type_flattened_error():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_entity_type(
            featurestore_service.UpdateEntityTypeRequest(),
            entity_type=gca_entity_type.EntityType(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_entity_type_flattened_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_entity_type), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_entity_type.EntityType()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_entity_type.EntityType()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_entity_type(
            entity_type=gca_entity_type.EntityType(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].entity_type == gca_entity_type.EntityType(name="name_value")
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


@pytest.mark.asyncio
async def test_update_entity_type_flattened_error_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_entity_type(
            featurestore_service.UpdateEntityTypeRequest(),
            entity_type=gca_entity_type.EntityType(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


def test_delete_entity_type(
    transport: str = "grpc", request_type=featurestore_service.DeleteEntityTypeRequest
):
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_entity_type), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_entity_type(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.DeleteEntityTypeRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_entity_type_from_dict():
    test_delete_entity_type(request_type=dict)


def test_delete_entity_type_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_entity_type), "__call__"
    ) as call:
        client.delete_entity_type()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.DeleteEntityTypeRequest()


@pytest.mark.asyncio
async def test_delete_entity_type_async(
    transport: str = "grpc_asyncio",
    request_type=featurestore_service.DeleteEntityTypeRequest,
):
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_entity_type), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_entity_type(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.DeleteEntityTypeRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_entity_type_async_from_dict():
    await test_delete_entity_type_async(request_type=dict)


def test_delete_entity_type_field_headers():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.DeleteEntityTypeRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_entity_type), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_entity_type(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_entity_type_field_headers_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.DeleteEntityTypeRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_entity_type), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_entity_type(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_entity_type_flattened():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_entity_type), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_entity_type(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_entity_type_flattened_error():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_entity_type(
            featurestore_service.DeleteEntityTypeRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_entity_type_flattened_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_entity_type), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_entity_type(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_entity_type_flattened_error_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_entity_type(
            featurestore_service.DeleteEntityTypeRequest(), name="name_value",
        )


def test_create_feature(
    transport: str = "grpc", request_type=featurestore_service.CreateFeatureRequest
):
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_feature), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.create_feature(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.CreateFeatureRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_create_feature_from_dict():
    test_create_feature(request_type=dict)


def test_create_feature_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_feature), "__call__") as call:
        client.create_feature()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.CreateFeatureRequest()


@pytest.mark.asyncio
async def test_create_feature_async(
    transport: str = "grpc_asyncio",
    request_type=featurestore_service.CreateFeatureRequest,
):
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_feature), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.create_feature(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.CreateFeatureRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_create_feature_async_from_dict():
    await test_create_feature_async(request_type=dict)


def test_create_feature_field_headers():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.CreateFeatureRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_feature), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.create_feature(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_feature_field_headers_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.CreateFeatureRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_feature), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.create_feature(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_feature_flattened():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_feature), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_feature(
            parent="parent_value", feature=gca_feature.Feature(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].feature == gca_feature.Feature(name="name_value")


def test_create_feature_flattened_error():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_feature(
            featurestore_service.CreateFeatureRequest(),
            parent="parent_value",
            feature=gca_feature.Feature(name="name_value"),
        )


@pytest.mark.asyncio
async def test_create_feature_flattened_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_feature), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_feature(
            parent="parent_value", feature=gca_feature.Feature(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].feature == gca_feature.Feature(name="name_value")


@pytest.mark.asyncio
async def test_create_feature_flattened_error_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_feature(
            featurestore_service.CreateFeatureRequest(),
            parent="parent_value",
            feature=gca_feature.Feature(name="name_value"),
        )


def test_batch_create_features(
    transport: str = "grpc",
    request_type=featurestore_service.BatchCreateFeaturesRequest,
):
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_create_features), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.batch_create_features(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.BatchCreateFeaturesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_batch_create_features_from_dict():
    test_batch_create_features(request_type=dict)


def test_batch_create_features_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_create_features), "__call__"
    ) as call:
        client.batch_create_features()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.BatchCreateFeaturesRequest()


@pytest.mark.asyncio
async def test_batch_create_features_async(
    transport: str = "grpc_asyncio",
    request_type=featurestore_service.BatchCreateFeaturesRequest,
):
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_create_features), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.batch_create_features(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.BatchCreateFeaturesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_batch_create_features_async_from_dict():
    await test_batch_create_features_async(request_type=dict)


def test_batch_create_features_field_headers():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.BatchCreateFeaturesRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_create_features), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.batch_create_features(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_batch_create_features_field_headers_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.BatchCreateFeaturesRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_create_features), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.batch_create_features(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_batch_create_features_flattened():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_create_features), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.batch_create_features(
            parent="parent_value",
            requests=[featurestore_service.CreateFeatureRequest(parent="parent_value")],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].requests == [
            featurestore_service.CreateFeatureRequest(parent="parent_value")
        ]


def test_batch_create_features_flattened_error():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.batch_create_features(
            featurestore_service.BatchCreateFeaturesRequest(),
            parent="parent_value",
            requests=[featurestore_service.CreateFeatureRequest(parent="parent_value")],
        )


@pytest.mark.asyncio
async def test_batch_create_features_flattened_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_create_features), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.batch_create_features(
            parent="parent_value",
            requests=[featurestore_service.CreateFeatureRequest(parent="parent_value")],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].requests == [
            featurestore_service.CreateFeatureRequest(parent="parent_value")
        ]


@pytest.mark.asyncio
async def test_batch_create_features_flattened_error_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.batch_create_features(
            featurestore_service.BatchCreateFeaturesRequest(),
            parent="parent_value",
            requests=[featurestore_service.CreateFeatureRequest(parent="parent_value")],
        )


def test_get_feature(
    transport: str = "grpc", request_type=featurestore_service.GetFeatureRequest
):
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_feature), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = feature.Feature(
            name="name_value",
            description="description_value",
            value_type=feature.Feature.ValueType.BOOL,
            etag="etag_value",
        )
        response = client.get_feature(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.GetFeatureRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, feature.Feature)
    assert response.name == "name_value"
    assert response.description == "description_value"
    assert response.value_type == feature.Feature.ValueType.BOOL
    assert response.etag == "etag_value"


def test_get_feature_from_dict():
    test_get_feature(request_type=dict)


def test_get_feature_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_feature), "__call__") as call:
        client.get_feature()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.GetFeatureRequest()


@pytest.mark.asyncio
async def test_get_feature_async(
    transport: str = "grpc_asyncio", request_type=featurestore_service.GetFeatureRequest
):
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_feature), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature.Feature(
                name="name_value",
                description="description_value",
                value_type=feature.Feature.ValueType.BOOL,
                etag="etag_value",
            )
        )
        response = await client.get_feature(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.GetFeatureRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, feature.Feature)
    assert response.name == "name_value"
    assert response.description == "description_value"
    assert response.value_type == feature.Feature.ValueType.BOOL
    assert response.etag == "etag_value"


@pytest.mark.asyncio
async def test_get_feature_async_from_dict():
    await test_get_feature_async(request_type=dict)


def test_get_feature_field_headers():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.GetFeatureRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_feature), "__call__") as call:
        call.return_value = feature.Feature()
        client.get_feature(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_feature_field_headers_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.GetFeatureRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_feature), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(feature.Feature())
        await client.get_feature(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_feature_flattened():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_feature), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = feature.Feature()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_feature(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_feature_flattened_error():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_feature(
            featurestore_service.GetFeatureRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_feature_flattened_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_feature), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = feature.Feature()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(feature.Feature())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_feature(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_feature_flattened_error_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_feature(
            featurestore_service.GetFeatureRequest(), name="name_value",
        )


def test_list_features(
    transport: str = "grpc", request_type=featurestore_service.ListFeaturesRequest
):
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_features), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = featurestore_service.ListFeaturesResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_features(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.ListFeaturesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListFeaturesPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_features_from_dict():
    test_list_features(request_type=dict)


def test_list_features_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_features), "__call__") as call:
        client.list_features()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.ListFeaturesRequest()


@pytest.mark.asyncio
async def test_list_features_async(
    transport: str = "grpc_asyncio",
    request_type=featurestore_service.ListFeaturesRequest,
):
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_features), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            featurestore_service.ListFeaturesResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_features(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.ListFeaturesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListFeaturesAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_features_async_from_dict():
    await test_list_features_async(request_type=dict)


def test_list_features_field_headers():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.ListFeaturesRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_features), "__call__") as call:
        call.return_value = featurestore_service.ListFeaturesResponse()
        client.list_features(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_features_field_headers_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.ListFeaturesRequest()

    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_features), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            featurestore_service.ListFeaturesResponse()
        )
        await client.list_features(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_features_flattened():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_features), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = featurestore_service.ListFeaturesResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_features(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_features_flattened_error():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_features(
            featurestore_service.ListFeaturesRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_features_flattened_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_features), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = featurestore_service.ListFeaturesResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            featurestore_service.ListFeaturesResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_features(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_features_flattened_error_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_features(
            featurestore_service.ListFeaturesRequest(), parent="parent_value",
        )


def test_list_features_pager():
    client = FeaturestoreServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_features), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            featurestore_service.ListFeaturesResponse(
                features=[feature.Feature(), feature.Feature(), feature.Feature(),],
                next_page_token="abc",
            ),
            featurestore_service.ListFeaturesResponse(
                features=[], next_page_token="def",
            ),
            featurestore_service.ListFeaturesResponse(
                features=[feature.Feature(),], next_page_token="ghi",
            ),
            featurestore_service.ListFeaturesResponse(
                features=[feature.Feature(), feature.Feature(),],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_features(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, feature.Feature) for i in results)


def test_list_features_pages():
    client = FeaturestoreServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_features), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            featurestore_service.ListFeaturesResponse(
                features=[feature.Feature(), feature.Feature(), feature.Feature(),],
                next_page_token="abc",
            ),
            featurestore_service.ListFeaturesResponse(
                features=[], next_page_token="def",
            ),
            featurestore_service.ListFeaturesResponse(
                features=[feature.Feature(),], next_page_token="ghi",
            ),
            featurestore_service.ListFeaturesResponse(
                features=[feature.Feature(), feature.Feature(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_features(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_features_async_pager():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_features), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            featurestore_service.ListFeaturesResponse(
                features=[feature.Feature(), feature.Feature(), feature.Feature(),],
                next_page_token="abc",
            ),
            featurestore_service.ListFeaturesResponse(
                features=[], next_page_token="def",
            ),
            featurestore_service.ListFeaturesResponse(
                features=[feature.Feature(),], next_page_token="ghi",
            ),
            featurestore_service.ListFeaturesResponse(
                features=[feature.Feature(), feature.Feature(),],
            ),
            RuntimeError,
        )
        async_pager = await client.list_features(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, feature.Feature) for i in responses)


@pytest.mark.asyncio
async def test_list_features_async_pages():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_features), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            featurestore_service.ListFeaturesResponse(
                features=[feature.Feature(), feature.Feature(), feature.Feature(),],
                next_page_token="abc",
            ),
            featurestore_service.ListFeaturesResponse(
                features=[], next_page_token="def",
            ),
            featurestore_service.ListFeaturesResponse(
                features=[feature.Feature(),], next_page_token="ghi",
            ),
            featurestore_service.ListFeaturesResponse(
                features=[feature.Feature(), feature.Feature(),],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_features(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_update_feature(
    transport: str = "grpc", request_type=featurestore_service.UpdateFeatureRequest
):
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_feature), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_feature.Feature(
            name="name_value",
            description="description_value",
            value_type=gca_feature.Feature.ValueType.BOOL,
            etag="etag_value",
        )
        response = client.update_feature(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.UpdateFeatureRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_feature.Feature)
    assert response.name == "name_value"
    assert response.description == "description_value"
    assert response.value_type == gca_feature.Feature.ValueType.BOOL
    assert response.etag == "etag_value"


def test_update_feature_from_dict():
    test_update_feature(request_type=dict)


def test_update_feature_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_feature), "__call__") as call:
        client.update_feature()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.UpdateFeatureRequest()


@pytest.mark.asyncio
async def test_update_feature_async(
    transport: str = "grpc_asyncio",
    request_type=featurestore_service.UpdateFeatureRequest,
):
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_feature), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_feature.Feature(
                name="name_value",
                description="description_value",
                value_type=gca_feature.Feature.ValueType.BOOL,
                etag="etag_value",
            )
        )
        response = await client.update_feature(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.UpdateFeatureRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_feature.Feature)
    assert response.name == "name_value"
    assert response.description == "description_value"
    assert response.value_type == gca_feature.Feature.ValueType.BOOL
    assert response.etag == "etag_value"


@pytest.mark.asyncio
async def test_update_feature_async_from_dict():
    await test_update_feature_async(request_type=dict)


def test_update_feature_field_headers():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.UpdateFeatureRequest()

    request.feature.name = "feature.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_feature), "__call__") as call:
        call.return_value = gca_feature.Feature()
        client.update_feature(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "feature.name=feature.name/value",) in kw[
        "metadata"
    ]


@pytest.mark.asyncio
async def test_update_feature_field_headers_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.UpdateFeatureRequest()

    request.feature.name = "feature.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_feature), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gca_feature.Feature())
        await client.update_feature(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "feature.name=feature.name/value",) in kw[
        "metadata"
    ]


def test_update_feature_flattened():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_feature), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_feature.Feature()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_feature(
            feature=gca_feature.Feature(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].feature == gca_feature.Feature(name="name_value")
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


def test_update_feature_flattened_error():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_feature(
            featurestore_service.UpdateFeatureRequest(),
            feature=gca_feature.Feature(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_feature_flattened_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_feature), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_feature.Feature()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gca_feature.Feature())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_feature(
            feature=gca_feature.Feature(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].feature == gca_feature.Feature(name="name_value")
        assert args[0].update_mask == field_mask_pb2.FieldMask(paths=["paths_value"])


@pytest.mark.asyncio
async def test_update_feature_flattened_error_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_feature(
            featurestore_service.UpdateFeatureRequest(),
            feature=gca_feature.Feature(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


def test_delete_feature(
    transport: str = "grpc", request_type=featurestore_service.DeleteFeatureRequest
):
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_feature), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_feature(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.DeleteFeatureRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_feature_from_dict():
    test_delete_feature(request_type=dict)


def test_delete_feature_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_feature), "__call__") as call:
        client.delete_feature()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.DeleteFeatureRequest()


@pytest.mark.asyncio
async def test_delete_feature_async(
    transport: str = "grpc_asyncio",
    request_type=featurestore_service.DeleteFeatureRequest,
):
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_feature), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_feature(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.DeleteFeatureRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_feature_async_from_dict():
    await test_delete_feature_async(request_type=dict)


def test_delete_feature_field_headers():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.DeleteFeatureRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_feature), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_feature(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_feature_field_headers_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.DeleteFeatureRequest()

    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_feature), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_feature(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_feature_flattened():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_feature), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_feature(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_feature_flattened_error():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_feature(
            featurestore_service.DeleteFeatureRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_feature_flattened_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_feature), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_feature(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_feature_flattened_error_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_feature(
            featurestore_service.DeleteFeatureRequest(), name="name_value",
        )


def test_import_feature_values(
    transport: str = "grpc",
    request_type=featurestore_service.ImportFeatureValuesRequest,
):
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.import_feature_values), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.import_feature_values(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.ImportFeatureValuesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_import_feature_values_from_dict():
    test_import_feature_values(request_type=dict)


def test_import_feature_values_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.import_feature_values), "__call__"
    ) as call:
        client.import_feature_values()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.ImportFeatureValuesRequest()


@pytest.mark.asyncio
async def test_import_feature_values_async(
    transport: str = "grpc_asyncio",
    request_type=featurestore_service.ImportFeatureValuesRequest,
):
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.import_feature_values), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.import_feature_values(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.ImportFeatureValuesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_import_feature_values_async_from_dict():
    await test_import_feature_values_async(request_type=dict)


def test_import_feature_values_field_headers():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.ImportFeatureValuesRequest()

    request.entity_type = "entity_type/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.import_feature_values), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.import_feature_values(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "entity_type=entity_type/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_import_feature_values_field_headers_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.ImportFeatureValuesRequest()

    request.entity_type = "entity_type/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.import_feature_values), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.import_feature_values(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "entity_type=entity_type/value",) in kw["metadata"]


def test_import_feature_values_flattened():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.import_feature_values), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.import_feature_values(entity_type="entity_type_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].entity_type == "entity_type_value"


def test_import_feature_values_flattened_error():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.import_feature_values(
            featurestore_service.ImportFeatureValuesRequest(),
            entity_type="entity_type_value",
        )


@pytest.mark.asyncio
async def test_import_feature_values_flattened_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.import_feature_values), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.import_feature_values(entity_type="entity_type_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].entity_type == "entity_type_value"


@pytest.mark.asyncio
async def test_import_feature_values_flattened_error_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.import_feature_values(
            featurestore_service.ImportFeatureValuesRequest(),
            entity_type="entity_type_value",
        )


def test_batch_read_feature_values(
    transport: str = "grpc",
    request_type=featurestore_service.BatchReadFeatureValuesRequest,
):
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_read_feature_values), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.batch_read_feature_values(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.BatchReadFeatureValuesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_batch_read_feature_values_from_dict():
    test_batch_read_feature_values(request_type=dict)


def test_batch_read_feature_values_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_read_feature_values), "__call__"
    ) as call:
        client.batch_read_feature_values()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.BatchReadFeatureValuesRequest()


@pytest.mark.asyncio
async def test_batch_read_feature_values_async(
    transport: str = "grpc_asyncio",
    request_type=featurestore_service.BatchReadFeatureValuesRequest,
):
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_read_feature_values), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.batch_read_feature_values(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.BatchReadFeatureValuesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_batch_read_feature_values_async_from_dict():
    await test_batch_read_feature_values_async(request_type=dict)


def test_batch_read_feature_values_field_headers():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.BatchReadFeatureValuesRequest()

    request.featurestore = "featurestore/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_read_feature_values), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.batch_read_feature_values(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "featurestore=featurestore/value",) in kw[
        "metadata"
    ]


@pytest.mark.asyncio
async def test_batch_read_feature_values_field_headers_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.BatchReadFeatureValuesRequest()

    request.featurestore = "featurestore/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_read_feature_values), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.batch_read_feature_values(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "featurestore=featurestore/value",) in kw[
        "metadata"
    ]


def test_batch_read_feature_values_flattened():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_read_feature_values), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.batch_read_feature_values(featurestore="featurestore_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].featurestore == "featurestore_value"


def test_batch_read_feature_values_flattened_error():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.batch_read_feature_values(
            featurestore_service.BatchReadFeatureValuesRequest(),
            featurestore="featurestore_value",
        )


@pytest.mark.asyncio
async def test_batch_read_feature_values_flattened_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_read_feature_values), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.batch_read_feature_values(
            featurestore="featurestore_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].featurestore == "featurestore_value"


@pytest.mark.asyncio
async def test_batch_read_feature_values_flattened_error_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.batch_read_feature_values(
            featurestore_service.BatchReadFeatureValuesRequest(),
            featurestore="featurestore_value",
        )


def test_export_feature_values(
    transport: str = "grpc",
    request_type=featurestore_service.ExportFeatureValuesRequest,
):
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.export_feature_values), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.export_feature_values(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.ExportFeatureValuesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_export_feature_values_from_dict():
    test_export_feature_values(request_type=dict)


def test_export_feature_values_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.export_feature_values), "__call__"
    ) as call:
        client.export_feature_values()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.ExportFeatureValuesRequest()


@pytest.mark.asyncio
async def test_export_feature_values_async(
    transport: str = "grpc_asyncio",
    request_type=featurestore_service.ExportFeatureValuesRequest,
):
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.export_feature_values), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.export_feature_values(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.ExportFeatureValuesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_export_feature_values_async_from_dict():
    await test_export_feature_values_async(request_type=dict)


def test_export_feature_values_field_headers():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.ExportFeatureValuesRequest()

    request.entity_type = "entity_type/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.export_feature_values), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.export_feature_values(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "entity_type=entity_type/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_export_feature_values_field_headers_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.ExportFeatureValuesRequest()

    request.entity_type = "entity_type/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.export_feature_values), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.export_feature_values(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "entity_type=entity_type/value",) in kw["metadata"]


def test_export_feature_values_flattened():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.export_feature_values), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.export_feature_values(entity_type="entity_type_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].entity_type == "entity_type_value"


def test_export_feature_values_flattened_error():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.export_feature_values(
            featurestore_service.ExportFeatureValuesRequest(),
            entity_type="entity_type_value",
        )


@pytest.mark.asyncio
async def test_export_feature_values_flattened_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.export_feature_values), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.export_feature_values(entity_type="entity_type_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].entity_type == "entity_type_value"


@pytest.mark.asyncio
async def test_export_feature_values_flattened_error_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.export_feature_values(
            featurestore_service.ExportFeatureValuesRequest(),
            entity_type="entity_type_value",
        )


def test_search_features(
    transport: str = "grpc", request_type=featurestore_service.SearchFeaturesRequest
):
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.search_features), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = featurestore_service.SearchFeaturesResponse(
            next_page_token="next_page_token_value",
        )
        response = client.search_features(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.SearchFeaturesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.SearchFeaturesPager)
    assert response.next_page_token == "next_page_token_value"


def test_search_features_from_dict():
    test_search_features(request_type=dict)


def test_search_features_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.search_features), "__call__") as call:
        client.search_features()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.SearchFeaturesRequest()


@pytest.mark.asyncio
async def test_search_features_async(
    transport: str = "grpc_asyncio",
    request_type=featurestore_service.SearchFeaturesRequest,
):
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.search_features), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            featurestore_service.SearchFeaturesResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.search_features(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == featurestore_service.SearchFeaturesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.SearchFeaturesAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_search_features_async_from_dict():
    await test_search_features_async(request_type=dict)


def test_search_features_field_headers():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.SearchFeaturesRequest()

    request.location = "location/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.search_features), "__call__") as call:
        call.return_value = featurestore_service.SearchFeaturesResponse()
        client.search_features(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "location=location/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_search_features_field_headers_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = featurestore_service.SearchFeaturesRequest()

    request.location = "location/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.search_features), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            featurestore_service.SearchFeaturesResponse()
        )
        await client.search_features(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "location=location/value",) in kw["metadata"]


def test_search_features_flattened():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.search_features), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = featurestore_service.SearchFeaturesResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.search_features(location="location_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].location == "location_value"


def test_search_features_flattened_error():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.search_features(
            featurestore_service.SearchFeaturesRequest(), location="location_value",
        )


@pytest.mark.asyncio
async def test_search_features_flattened_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.search_features), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = featurestore_service.SearchFeaturesResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            featurestore_service.SearchFeaturesResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.search_features(location="location_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0].location == "location_value"


@pytest.mark.asyncio
async def test_search_features_flattened_error_async():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.search_features(
            featurestore_service.SearchFeaturesRequest(), location="location_value",
        )


def test_search_features_pager():
    client = FeaturestoreServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.search_features), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            featurestore_service.SearchFeaturesResponse(
                features=[feature.Feature(), feature.Feature(), feature.Feature(),],
                next_page_token="abc",
            ),
            featurestore_service.SearchFeaturesResponse(
                features=[], next_page_token="def",
            ),
            featurestore_service.SearchFeaturesResponse(
                features=[feature.Feature(),], next_page_token="ghi",
            ),
            featurestore_service.SearchFeaturesResponse(
                features=[feature.Feature(), feature.Feature(),],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("location", ""),)),
        )
        pager = client.search_features(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, feature.Feature) for i in results)


def test_search_features_pages():
    client = FeaturestoreServiceClient(credentials=ga_credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.search_features), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            featurestore_service.SearchFeaturesResponse(
                features=[feature.Feature(), feature.Feature(), feature.Feature(),],
                next_page_token="abc",
            ),
            featurestore_service.SearchFeaturesResponse(
                features=[], next_page_token="def",
            ),
            featurestore_service.SearchFeaturesResponse(
                features=[feature.Feature(),], next_page_token="ghi",
            ),
            featurestore_service.SearchFeaturesResponse(
                features=[feature.Feature(), feature.Feature(),],
            ),
            RuntimeError,
        )
        pages = list(client.search_features(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_search_features_async_pager():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_features), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            featurestore_service.SearchFeaturesResponse(
                features=[feature.Feature(), feature.Feature(), feature.Feature(),],
                next_page_token="abc",
            ),
            featurestore_service.SearchFeaturesResponse(
                features=[], next_page_token="def",
            ),
            featurestore_service.SearchFeaturesResponse(
                features=[feature.Feature(),], next_page_token="ghi",
            ),
            featurestore_service.SearchFeaturesResponse(
                features=[feature.Feature(), feature.Feature(),],
            ),
            RuntimeError,
        )
        async_pager = await client.search_features(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, feature.Feature) for i in responses)


@pytest.mark.asyncio
async def test_search_features_async_pages():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_features), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            featurestore_service.SearchFeaturesResponse(
                features=[feature.Feature(), feature.Feature(), feature.Feature(),],
                next_page_token="abc",
            ),
            featurestore_service.SearchFeaturesResponse(
                features=[], next_page_token="def",
            ),
            featurestore_service.SearchFeaturesResponse(
                features=[feature.Feature(),], next_page_token="ghi",
            ),
            featurestore_service.SearchFeaturesResponse(
                features=[feature.Feature(), feature.Feature(),],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.search_features(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.FeaturestoreServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = FeaturestoreServiceClient(
            credentials=ga_credentials.AnonymousCredentials(), transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.FeaturestoreServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = FeaturestoreServiceClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.FeaturestoreServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = FeaturestoreServiceClient(
            client_options={"scopes": ["1", "2"]}, transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.FeaturestoreServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    client = FeaturestoreServiceClient(transport=transport)
    assert client.transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.FeaturestoreServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.FeaturestoreServiceGrpcAsyncIOTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.FeaturestoreServiceGrpcTransport,
        transports.FeaturestoreServiceGrpcAsyncIOTransport,
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
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    assert isinstance(client.transport, transports.FeaturestoreServiceGrpcTransport,)


def test_featurestore_service_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(core_exceptions.DuplicateCredentialArgs):
        transport = transports.FeaturestoreServiceTransport(
            credentials=ga_credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_featurestore_service_base_transport():
    # Instantiate the base transport.
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.featurestore_service.transports.FeaturestoreServiceTransport.__init__"
    ) as Transport:
        Transport.return_value = None
        transport = transports.FeaturestoreServiceTransport(
            credentials=ga_credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "create_featurestore",
        "get_featurestore",
        "list_featurestores",
        "update_featurestore",
        "delete_featurestore",
        "create_entity_type",
        "get_entity_type",
        "list_entity_types",
        "update_entity_type",
        "delete_entity_type",
        "create_feature",
        "batch_create_features",
        "get_feature",
        "list_features",
        "update_feature",
        "delete_feature",
        "import_feature_values",
        "batch_read_feature_values",
        "export_feature_values",
        "search_features",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    # Additionally, the LRO client (a property) should
    # also raise NotImplementedError
    with pytest.raises(NotImplementedError):
        transport.operations_client


@requires_google_auth_gte_1_25_0
def test_featurestore_service_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        google.auth, "load_credentials_from_file", autospec=True
    ) as load_creds, mock.patch(
        "google.cloud.aiplatform_v1beta1.services.featurestore_service.transports.FeaturestoreServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.FeaturestoreServiceTransport(
            credentials_file="credentials.json", quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=None,
            default_scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


@requires_google_auth_lt_1_25_0
def test_featurestore_service_base_transport_with_credentials_file_old_google_auth():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        google.auth, "load_credentials_from_file", autospec=True
    ) as load_creds, mock.patch(
        "google.cloud.aiplatform_v1beta1.services.featurestore_service.transports.FeaturestoreServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.FeaturestoreServiceTransport(
            credentials_file="credentials.json", quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


def test_featurestore_service_base_transport_with_adc():
    # Test the default credentials are used if credentials and credentials_file are None.
    with mock.patch.object(google.auth, "default", autospec=True) as adc, mock.patch(
        "google.cloud.aiplatform_v1beta1.services.featurestore_service.transports.FeaturestoreServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.FeaturestoreServiceTransport()
        adc.assert_called_once()


@requires_google_auth_gte_1_25_0
def test_featurestore_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        FeaturestoreServiceClient()
        adc.assert_called_once_with(
            scopes=None,
            default_scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id=None,
        )


@requires_google_auth_lt_1_25_0
def test_featurestore_service_auth_adc_old_google_auth():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        FeaturestoreServiceClient()
        adc.assert_called_once_with(
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id=None,
        )


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.FeaturestoreServiceGrpcTransport,
        transports.FeaturestoreServiceGrpcAsyncIOTransport,
    ],
)
@requires_google_auth_gte_1_25_0
def test_featurestore_service_transport_auth_adc(transport_class):
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
        transports.FeaturestoreServiceGrpcTransport,
        transports.FeaturestoreServiceGrpcAsyncIOTransport,
    ],
)
@requires_google_auth_lt_1_25_0
def test_featurestore_service_transport_auth_adc_old_google_auth(transport_class):
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
        (transports.FeaturestoreServiceGrpcTransport, grpc_helpers),
        (transports.FeaturestoreServiceGrpcAsyncIOTransport, grpc_helpers_async),
    ],
)
@requires_api_core_gte_1_26_0
def test_featurestore_service_transport_create_channel(transport_class, grpc_helpers):
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
        (transports.FeaturestoreServiceGrpcTransport, grpc_helpers),
        (transports.FeaturestoreServiceGrpcAsyncIOTransport, grpc_helpers_async),
    ],
)
@requires_api_core_lt_1_26_0
def test_featurestore_service_transport_create_channel_old_api_core(
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
        (transports.FeaturestoreServiceGrpcTransport, grpc_helpers),
        (transports.FeaturestoreServiceGrpcAsyncIOTransport, grpc_helpers_async),
    ],
)
@requires_api_core_lt_1_26_0
def test_featurestore_service_transport_create_channel_user_scopes(
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
        transports.FeaturestoreServiceGrpcTransport,
        transports.FeaturestoreServiceGrpcAsyncIOTransport,
    ],
)
def test_featurestore_service_grpc_transport_client_cert_source_for_mtls(
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


def test_featurestore_service_host_no_port():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="aiplatform.googleapis.com"
        ),
    )
    assert client.transport._host == "aiplatform.googleapis.com:443"


def test_featurestore_service_host_with_port():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="aiplatform.googleapis.com:8000"
        ),
    )
    assert client.transport._host == "aiplatform.googleapis.com:8000"


def test_featurestore_service_grpc_transport_channel():
    channel = grpc.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.FeaturestoreServiceGrpcTransport(
        host="squid.clam.whelk", channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


def test_featurestore_service_grpc_asyncio_transport_channel():
    channel = aio.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.FeaturestoreServiceGrpcAsyncIOTransport(
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
        transports.FeaturestoreServiceGrpcTransport,
        transports.FeaturestoreServiceGrpcAsyncIOTransport,
    ],
)
def test_featurestore_service_transport_channel_mtls_with_client_cert_source(
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
        transports.FeaturestoreServiceGrpcTransport,
        transports.FeaturestoreServiceGrpcAsyncIOTransport,
    ],
)
def test_featurestore_service_transport_channel_mtls_with_adc(transport_class):
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


def test_featurestore_service_grpc_lro_client():
    client = FeaturestoreServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc",
    )
    transport = client.transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_featurestore_service_grpc_lro_async_client():
    client = FeaturestoreServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc_asyncio",
    )
    transport = client.transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsAsyncClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_entity_type_path():
    project = "squid"
    location = "clam"
    featurestore = "whelk"
    entity_type = "octopus"
    expected = "projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}".format(
        project=project,
        location=location,
        featurestore=featurestore,
        entity_type=entity_type,
    )
    actual = FeaturestoreServiceClient.entity_type_path(
        project, location, featurestore, entity_type
    )
    assert expected == actual


def test_parse_entity_type_path():
    expected = {
        "project": "oyster",
        "location": "nudibranch",
        "featurestore": "cuttlefish",
        "entity_type": "mussel",
    }
    path = FeaturestoreServiceClient.entity_type_path(**expected)

    # Check that the path construction is reversible.
    actual = FeaturestoreServiceClient.parse_entity_type_path(path)
    assert expected == actual


def test_feature_path():
    project = "winkle"
    location = "nautilus"
    featurestore = "scallop"
    entity_type = "abalone"
    feature = "squid"
    expected = "projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}/features/{feature}".format(
        project=project,
        location=location,
        featurestore=featurestore,
        entity_type=entity_type,
        feature=feature,
    )
    actual = FeaturestoreServiceClient.feature_path(
        project, location, featurestore, entity_type, feature
    )
    assert expected == actual


def test_parse_feature_path():
    expected = {
        "project": "clam",
        "location": "whelk",
        "featurestore": "octopus",
        "entity_type": "oyster",
        "feature": "nudibranch",
    }
    path = FeaturestoreServiceClient.feature_path(**expected)

    # Check that the path construction is reversible.
    actual = FeaturestoreServiceClient.parse_feature_path(path)
    assert expected == actual


def test_featurestore_path():
    project = "cuttlefish"
    location = "mussel"
    featurestore = "winkle"
    expected = "projects/{project}/locations/{location}/featurestores/{featurestore}".format(
        project=project, location=location, featurestore=featurestore,
    )
    actual = FeaturestoreServiceClient.featurestore_path(
        project, location, featurestore
    )
    assert expected == actual


def test_parse_featurestore_path():
    expected = {
        "project": "nautilus",
        "location": "scallop",
        "featurestore": "abalone",
    }
    path = FeaturestoreServiceClient.featurestore_path(**expected)

    # Check that the path construction is reversible.
    actual = FeaturestoreServiceClient.parse_featurestore_path(path)
    assert expected == actual


def test_common_billing_account_path():
    billing_account = "squid"
    expected = "billingAccounts/{billing_account}".format(
        billing_account=billing_account,
    )
    actual = FeaturestoreServiceClient.common_billing_account_path(billing_account)
    assert expected == actual


def test_parse_common_billing_account_path():
    expected = {
        "billing_account": "clam",
    }
    path = FeaturestoreServiceClient.common_billing_account_path(**expected)

    # Check that the path construction is reversible.
    actual = FeaturestoreServiceClient.parse_common_billing_account_path(path)
    assert expected == actual


def test_common_folder_path():
    folder = "whelk"
    expected = "folders/{folder}".format(folder=folder,)
    actual = FeaturestoreServiceClient.common_folder_path(folder)
    assert expected == actual


def test_parse_common_folder_path():
    expected = {
        "folder": "octopus",
    }
    path = FeaturestoreServiceClient.common_folder_path(**expected)

    # Check that the path construction is reversible.
    actual = FeaturestoreServiceClient.parse_common_folder_path(path)
    assert expected == actual


def test_common_organization_path():
    organization = "oyster"
    expected = "organizations/{organization}".format(organization=organization,)
    actual = FeaturestoreServiceClient.common_organization_path(organization)
    assert expected == actual


def test_parse_common_organization_path():
    expected = {
        "organization": "nudibranch",
    }
    path = FeaturestoreServiceClient.common_organization_path(**expected)

    # Check that the path construction is reversible.
    actual = FeaturestoreServiceClient.parse_common_organization_path(path)
    assert expected == actual


def test_common_project_path():
    project = "cuttlefish"
    expected = "projects/{project}".format(project=project,)
    actual = FeaturestoreServiceClient.common_project_path(project)
    assert expected == actual


def test_parse_common_project_path():
    expected = {
        "project": "mussel",
    }
    path = FeaturestoreServiceClient.common_project_path(**expected)

    # Check that the path construction is reversible.
    actual = FeaturestoreServiceClient.parse_common_project_path(path)
    assert expected == actual


def test_common_location_path():
    project = "winkle"
    location = "nautilus"
    expected = "projects/{project}/locations/{location}".format(
        project=project, location=location,
    )
    actual = FeaturestoreServiceClient.common_location_path(project, location)
    assert expected == actual


def test_parse_common_location_path():
    expected = {
        "project": "scallop",
        "location": "abalone",
    }
    path = FeaturestoreServiceClient.common_location_path(**expected)

    # Check that the path construction is reversible.
    actual = FeaturestoreServiceClient.parse_common_location_path(path)
    assert expected == actual


def test_client_withDEFAULT_CLIENT_INFO():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(
        transports.FeaturestoreServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        client = FeaturestoreServiceClient(
            credentials=ga_credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(
        transports.FeaturestoreServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        transport_class = FeaturestoreServiceClient.get_transport_class()
        transport = transport_class(
            credentials=ga_credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)
