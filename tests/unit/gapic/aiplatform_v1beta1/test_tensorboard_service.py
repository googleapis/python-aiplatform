# -*- coding: utf-8 -*-
# Copyright 2023 Google LLC
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

# try/except added for compatibility with python < 3.8
try:
    from unittest import mock
    from unittest.mock import AsyncMock  # pragma: NO COVER
except ImportError:  # pragma: NO COVER
    import mock

import grpc
from grpc.experimental import aio
import math
import pytest
from proto.marshal.rules.dates import DurationRule, TimestampRule
from proto.marshal.rules import wrappers

from google.api_core import client_options
from google.api_core import exceptions as core_exceptions
from google.api_core import future
from google.api_core import gapic_v1
from google.api_core import grpc_helpers
from google.api_core import grpc_helpers_async
from google.api_core import operation
from google.api_core import operation_async  # type: ignore
from google.api_core import operations_v1
from google.api_core import path_template
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
from google.cloud.location import locations_pb2
from google.iam.v1 import iam_policy_pb2  # type: ignore
from google.iam.v1 import options_pb2  # type: ignore
from google.iam.v1 import policy_pb2  # type: ignore
from google.longrunning import operations_pb2  # type: ignore
from google.oauth2 import service_account
from google.protobuf import empty_pb2  # type: ignore
from google.protobuf import field_mask_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
import google.auth


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
    "client_class,transport_name",
    [
        (TensorboardServiceClient, "grpc"),
        (TensorboardServiceAsyncClient, "grpc_asyncio"),
    ],
)
def test_tensorboard_service_client_from_service_account_info(
    client_class, transport_name
):
    creds = ga_credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_info"
    ) as factory:
        factory.return_value = creds
        info = {"valid": True}
        client = client_class.from_service_account_info(info, transport=transport_name)
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        assert client.transport._host == ("aiplatform.googleapis.com:443")


@pytest.mark.parametrize(
    "transport_class,transport_name",
    [
        (transports.TensorboardServiceGrpcTransport, "grpc"),
        (transports.TensorboardServiceGrpcAsyncIOTransport, "grpc_asyncio"),
    ],
)
def test_tensorboard_service_client_service_account_always_use_jwt(
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
    "client_class,transport_name",
    [
        (TensorboardServiceClient, "grpc"),
        (TensorboardServiceAsyncClient, "grpc_asyncio"),
    ],
)
def test_tensorboard_service_client_from_service_account_file(
    client_class, transport_name
):
    creds = ga_credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = client_class.from_service_account_file(
            "dummy/file/path.json", transport=transport_name
        )
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        client = client_class.from_service_account_json(
            "dummy/file/path.json", transport=transport_name
        )
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        assert client.transport._host == ("aiplatform.googleapis.com:443")


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
        client = client_class(transport=transport_name, client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "never".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class(transport=transport_name)
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_ENDPOINT,
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
                always_use_jwt_access=True,
                api_audience=None,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "always".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class(transport=transport_name)
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
                always_use_jwt_access=True,
                api_audience=None,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT has
    # unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError):
            client = client_class(transport=transport_name)

    # Check the case GOOGLE_API_USE_CLIENT_CERTIFICATE has unsupported value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}
    ):
        with pytest.raises(ValueError):
            client = client_class(transport=transport_name)

    # Check the case quota_project_id is provided
    options = client_options.ClientOptions(quota_project_id="octopus")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id="octopus",
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )
    # Check the case api_endpoint is provided
    options = client_options.ClientOptions(
        api_audience="https://language.googleapis.com"
    )
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience="https://language.googleapis.com",
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
            client = client_class(client_options=options, transport=transport_name)

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
                api_audience=None,
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
                    client = client_class(transport=transport_name)
                    patched.assert_called_once_with(
                        credentials=None,
                        credentials_file=None,
                        host=expected_host,
                        scopes=None,
                        client_cert_source_for_mtls=expected_client_cert_source,
                        quota_project_id=None,
                        client_info=transports.base.DEFAULT_CLIENT_INFO,
                        always_use_jwt_access=True,
                        api_audience=None,
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
                client = client_class(transport=transport_name)
                patched.assert_called_once_with(
                    credentials=None,
                    credentials_file=None,
                    host=client.DEFAULT_ENDPOINT,
                    scopes=None,
                    client_cert_source_for_mtls=None,
                    quota_project_id=None,
                    client_info=transports.base.DEFAULT_CLIENT_INFO,
                    always_use_jwt_access=True,
                    api_audience=None,
                )


@pytest.mark.parametrize(
    "client_class", [TensorboardServiceClient, TensorboardServiceAsyncClient]
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
def test_tensorboard_service_client_get_mtls_endpoint_and_cert_source(client_class):
    mock_client_cert_source = mock.Mock()

    # Test the case GOOGLE_API_USE_CLIENT_CERTIFICATE is "true".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        mock_api_endpoint = "foo"
        options = client_options.ClientOptions(
            client_cert_source=mock_client_cert_source, api_endpoint=mock_api_endpoint
        )
        api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source(
            options
        )
        assert api_endpoint == mock_api_endpoint
        assert cert_source == mock_client_cert_source

    # Test the case GOOGLE_API_USE_CLIENT_CERTIFICATE is "false".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "false"}):
        mock_client_cert_source = mock.Mock()
        mock_api_endpoint = "foo"
        options = client_options.ClientOptions(
            client_cert_source=mock_client_cert_source, api_endpoint=mock_api_endpoint
        )
        api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source(
            options
        )
        assert api_endpoint == mock_api_endpoint
        assert cert_source is None

    # Test the case GOOGLE_API_USE_MTLS_ENDPOINT is "never".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source()
        assert api_endpoint == client_class.DEFAULT_ENDPOINT
        assert cert_source is None

    # Test the case GOOGLE_API_USE_MTLS_ENDPOINT is "always".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source()
        assert api_endpoint == client_class.DEFAULT_MTLS_ENDPOINT
        assert cert_source is None

    # Test the case GOOGLE_API_USE_MTLS_ENDPOINT is "auto" and default cert doesn't exist.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        with mock.patch(
            "google.auth.transport.mtls.has_default_client_cert_source",
            return_value=False,
        ):
            api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source()
            assert api_endpoint == client_class.DEFAULT_ENDPOINT
            assert cert_source is None

    # Test the case GOOGLE_API_USE_MTLS_ENDPOINT is "auto" and default cert exists.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        with mock.patch(
            "google.auth.transport.mtls.has_default_client_cert_source",
            return_value=True,
        ):
            with mock.patch(
                "google.auth.transport.mtls.default_client_cert_source",
                return_value=mock_client_cert_source,
            ):
                (
                    api_endpoint,
                    cert_source,
                ) = client_class.get_mtls_endpoint_and_cert_source()
                assert api_endpoint == client_class.DEFAULT_MTLS_ENDPOINT
                assert cert_source == mock_client_cert_source


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
    options = client_options.ClientOptions(
        scopes=["1", "2"],
    )
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=["1", "2"],
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name,grpc_helpers",
    [
        (
            TensorboardServiceClient,
            transports.TensorboardServiceGrpcTransport,
            "grpc",
            grpc_helpers,
        ),
        (
            TensorboardServiceAsyncClient,
            transports.TensorboardServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            grpc_helpers_async,
        ),
    ],
)
def test_tensorboard_service_client_client_options_credentials_file(
    client_class, transport_class, transport_name, grpc_helpers
):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(credentials_file="credentials.json")

    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
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
            always_use_jwt_access=True,
            api_audience=None,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name,grpc_helpers",
    [
        (
            TensorboardServiceClient,
            transports.TensorboardServiceGrpcTransport,
            "grpc",
            grpc_helpers,
        ),
        (
            TensorboardServiceAsyncClient,
            transports.TensorboardServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            grpc_helpers_async,
        ),
    ],
)
def test_tensorboard_service_client_create_channel_credentials_file(
    client_class, transport_class, transport_name, grpc_helpers
):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(credentials_file="credentials.json")

    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )

    # test that the credentials from file are saved and used as the credentials.
    with mock.patch.object(
        google.auth, "load_credentials_from_file", autospec=True
    ) as load_creds, mock.patch.object(
        google.auth, "default", autospec=True
    ) as adc, mock.patch.object(
        grpc_helpers, "create_channel"
    ) as create_channel:
        creds = ga_credentials.AnonymousCredentials()
        file_creds = ga_credentials.AnonymousCredentials()
        load_creds.return_value = (file_creds, None)
        adc.return_value = (creds, None)
        client = client_class(client_options=options, transport=transport_name)
        create_channel.assert_called_with(
            "aiplatform.googleapis.com:443",
            credentials=file_creds,
            credentials_file=None,
            quota_project_id=None,
            default_scopes=("https://www.googleapis.com/auth/cloud-platform",),
            scopes=None,
            default_host="aiplatform.googleapis.com",
            ssl_credentials=None,
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
            ],
        )


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.CreateTensorboardRequest,
        dict,
    ],
)
def test_create_tensorboard(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_create_tensorboard_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.parent = "parent_value"

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
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_tensorboard_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.CreateTensorboardRequest()

    request.parent = "parent_value"

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
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


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
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].tensorboard
        mock_val = gca_tensorboard.Tensorboard(name="name_value")
        assert arg == mock_val


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
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].tensorboard
        mock_val = gca_tensorboard.Tensorboard(name="name_value")
        assert arg == mock_val


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


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.GetTensorboardRequest,
        dict,
    ],
)
def test_get_tensorboard(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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
            is_default=True,
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
    assert response.is_default is True


def test_get_tensorboard_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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
                is_default=True,
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
    assert response.is_default is True


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

    request.name = "name_value"

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
    assert (
        "x-goog-request-params",
        "name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_tensorboard_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.GetTensorboardRequest()

    request.name = "name_value"

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
    assert (
        "x-goog-request-params",
        "name=name_value",
    ) in kw["metadata"]


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
        client.get_tensorboard(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_get_tensorboard_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_tensorboard(
            tensorboard_service.GetTensorboardRequest(),
            name="name_value",
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
        response = await client.get_tensorboard(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_get_tensorboard_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_tensorboard(
            tensorboard_service.GetTensorboardRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.UpdateTensorboardRequest,
        dict,
    ],
)
def test_update_tensorboard(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_update_tensorboard_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.tensorboard.name = "name_value"

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
    assert (
        "x-goog-request-params",
        "tensorboard.name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_tensorboard_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.UpdateTensorboardRequest()

    request.tensorboard.name = "name_value"

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
    assert (
        "x-goog-request-params",
        "tensorboard.name=name_value",
    ) in kw["metadata"]


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
        arg = args[0].tensorboard
        mock_val = gca_tensorboard.Tensorboard(name="name_value")
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=["paths_value"])
        assert arg == mock_val


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
        arg = args[0].tensorboard
        mock_val = gca_tensorboard.Tensorboard(name="name_value")
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=["paths_value"])
        assert arg == mock_val


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


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.ListTensorboardsRequest,
        dict,
    ],
)
def test_list_tensorboards(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_list_tensorboards_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.parent = "parent_value"

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
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_tensorboards_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ListTensorboardsRequest()

    request.parent = "parent_value"

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
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


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
        client.list_tensorboards(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_list_tensorboards_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_tensorboards(
            tensorboard_service.ListTensorboardsRequest(),
            parent="parent_value",
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
        response = await client.list_tensorboards(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_list_tensorboards_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_tensorboards(
            tensorboard_service.ListTensorboardsRequest(),
            parent="parent_value",
        )


def test_list_tensorboards_pager(transport_name: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials,
        transport=transport_name,
    )

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
                tensorboards=[],
                next_page_token="def",
            ),
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[
                    tensorboard.Tensorboard(),
                ],
                next_page_token="ghi",
            ),
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[
                    tensorboard.Tensorboard(),
                    tensorboard.Tensorboard(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_tensorboards(request={})

        assert pager._metadata == metadata

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, tensorboard.Tensorboard) for i in results)


def test_list_tensorboards_pages(transport_name: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials,
        transport=transport_name,
    )

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
                tensorboards=[],
                next_page_token="def",
            ),
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[
                    tensorboard.Tensorboard(),
                ],
                next_page_token="ghi",
            ),
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[
                    tensorboard.Tensorboard(),
                    tensorboard.Tensorboard(),
                ],
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
                tensorboards=[],
                next_page_token="def",
            ),
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[
                    tensorboard.Tensorboard(),
                ],
                next_page_token="ghi",
            ),
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[
                    tensorboard.Tensorboard(),
                    tensorboard.Tensorboard(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_tensorboards(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
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
                tensorboards=[],
                next_page_token="def",
            ),
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[
                    tensorboard.Tensorboard(),
                ],
                next_page_token="ghi",
            ),
            tensorboard_service.ListTensorboardsResponse(
                tensorboards=[
                    tensorboard.Tensorboard(),
                    tensorboard.Tensorboard(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.list_tensorboards(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.DeleteTensorboardRequest,
        dict,
    ],
)
def test_delete_tensorboard(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_delete_tensorboard_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.name = "name_value"

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
    assert (
        "x-goog-request-params",
        "name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_tensorboard_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.DeleteTensorboardRequest()

    request.name = "name_value"

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
    assert (
        "x-goog-request-params",
        "name=name_value",
    ) in kw["metadata"]


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
        client.delete_tensorboard(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_delete_tensorboard_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_tensorboard(
            tensorboard_service.DeleteTensorboardRequest(),
            name="name_value",
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
        response = await client.delete_tensorboard(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_delete_tensorboard_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_tensorboard(
            tensorboard_service.DeleteTensorboardRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.ReadTensorboardUsageRequest,
        dict,
    ],
)
def test_read_tensorboard_usage(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_usage), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.ReadTensorboardUsageResponse()
        response = client.read_tensorboard_usage(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ReadTensorboardUsageRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, tensorboard_service.ReadTensorboardUsageResponse)


def test_read_tensorboard_usage_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_usage), "__call__"
    ) as call:
        client.read_tensorboard_usage()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ReadTensorboardUsageRequest()


@pytest.mark.asyncio
async def test_read_tensorboard_usage_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.ReadTensorboardUsageRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_usage), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ReadTensorboardUsageResponse()
        )
        response = await client.read_tensorboard_usage(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ReadTensorboardUsageRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, tensorboard_service.ReadTensorboardUsageResponse)


@pytest.mark.asyncio
async def test_read_tensorboard_usage_async_from_dict():
    await test_read_tensorboard_usage_async(request_type=dict)


def test_read_tensorboard_usage_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ReadTensorboardUsageRequest()

    request.tensorboard = "tensorboard_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_usage), "__call__"
    ) as call:
        call.return_value = tensorboard_service.ReadTensorboardUsageResponse()
        client.read_tensorboard_usage(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "tensorboard=tensorboard_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_read_tensorboard_usage_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ReadTensorboardUsageRequest()

    request.tensorboard = "tensorboard_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_usage), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ReadTensorboardUsageResponse()
        )
        await client.read_tensorboard_usage(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "tensorboard=tensorboard_value",
    ) in kw["metadata"]


def test_read_tensorboard_usage_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_usage), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.ReadTensorboardUsageResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.read_tensorboard_usage(
            tensorboard="tensorboard_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].tensorboard
        mock_val = "tensorboard_value"
        assert arg == mock_val


def test_read_tensorboard_usage_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.read_tensorboard_usage(
            tensorboard_service.ReadTensorboardUsageRequest(),
            tensorboard="tensorboard_value",
        )


@pytest.mark.asyncio
async def test_read_tensorboard_usage_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_usage), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.ReadTensorboardUsageResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ReadTensorboardUsageResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.read_tensorboard_usage(
            tensorboard="tensorboard_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].tensorboard
        mock_val = "tensorboard_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_read_tensorboard_usage_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.read_tensorboard_usage(
            tensorboard_service.ReadTensorboardUsageRequest(),
            tensorboard="tensorboard_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.ReadTensorboardSizeRequest,
        dict,
    ],
)
def test_read_tensorboard_size(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_size), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.ReadTensorboardSizeResponse(
            storage_size_byte=1826,
        )
        response = client.read_tensorboard_size(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ReadTensorboardSizeRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, tensorboard_service.ReadTensorboardSizeResponse)
    assert response.storage_size_byte == 1826


def test_read_tensorboard_size_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_size), "__call__"
    ) as call:
        client.read_tensorboard_size()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ReadTensorboardSizeRequest()


@pytest.mark.asyncio
async def test_read_tensorboard_size_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.ReadTensorboardSizeRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_size), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ReadTensorboardSizeResponse(
                storage_size_byte=1826,
            )
        )
        response = await client.read_tensorboard_size(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.ReadTensorboardSizeRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, tensorboard_service.ReadTensorboardSizeResponse)
    assert response.storage_size_byte == 1826


@pytest.mark.asyncio
async def test_read_tensorboard_size_async_from_dict():
    await test_read_tensorboard_size_async(request_type=dict)


def test_read_tensorboard_size_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ReadTensorboardSizeRequest()

    request.tensorboard = "tensorboard_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_size), "__call__"
    ) as call:
        call.return_value = tensorboard_service.ReadTensorboardSizeResponse()
        client.read_tensorboard_size(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "tensorboard=tensorboard_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_read_tensorboard_size_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ReadTensorboardSizeRequest()

    request.tensorboard = "tensorboard_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_size), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ReadTensorboardSizeResponse()
        )
        await client.read_tensorboard_size(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "tensorboard=tensorboard_value",
    ) in kw["metadata"]


def test_read_tensorboard_size_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_size), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.ReadTensorboardSizeResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.read_tensorboard_size(
            tensorboard="tensorboard_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].tensorboard
        mock_val = "tensorboard_value"
        assert arg == mock_val


def test_read_tensorboard_size_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.read_tensorboard_size(
            tensorboard_service.ReadTensorboardSizeRequest(),
            tensorboard="tensorboard_value",
        )


@pytest.mark.asyncio
async def test_read_tensorboard_size_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.read_tensorboard_size), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.ReadTensorboardSizeResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.ReadTensorboardSizeResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.read_tensorboard_size(
            tensorboard="tensorboard_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].tensorboard
        mock_val = "tensorboard_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_read_tensorboard_size_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.read_tensorboard_size(
            tensorboard_service.ReadTensorboardSizeRequest(),
            tensorboard="tensorboard_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.CreateTensorboardExperimentRequest,
        dict,
    ],
)
def test_create_tensorboard_experiment(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_create_tensorboard_experiment_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.parent = "parent_value"

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
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_tensorboard_experiment_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.CreateTensorboardExperimentRequest()

    request.parent = "parent_value"

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
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


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
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].tensorboard_experiment
        mock_val = gca_tensorboard_experiment.TensorboardExperiment(name="name_value")
        assert arg == mock_val
        arg = args[0].tensorboard_experiment_id
        mock_val = "tensorboard_experiment_id_value"
        assert arg == mock_val


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
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].tensorboard_experiment
        mock_val = gca_tensorboard_experiment.TensorboardExperiment(name="name_value")
        assert arg == mock_val
        arg = args[0].tensorboard_experiment_id
        mock_val = "tensorboard_experiment_id_value"
        assert arg == mock_val


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


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.GetTensorboardExperimentRequest,
        dict,
    ],
)
def test_get_tensorboard_experiment(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_get_tensorboard_experiment_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.name = "name_value"

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
    assert (
        "x-goog-request-params",
        "name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_tensorboard_experiment_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.GetTensorboardExperimentRequest()

    request.name = "name_value"

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
    assert (
        "x-goog-request-params",
        "name=name_value",
    ) in kw["metadata"]


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
        client.get_tensorboard_experiment(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_get_tensorboard_experiment_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_tensorboard_experiment(
            tensorboard_service.GetTensorboardExperimentRequest(),
            name="name_value",
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
        response = await client.get_tensorboard_experiment(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_get_tensorboard_experiment_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_tensorboard_experiment(
            tensorboard_service.GetTensorboardExperimentRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.UpdateTensorboardExperimentRequest,
        dict,
    ],
)
def test_update_tensorboard_experiment(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_update_tensorboard_experiment_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.tensorboard_experiment.name = "name_value"

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
        "tensorboard_experiment.name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_tensorboard_experiment_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.UpdateTensorboardExperimentRequest()

    request.tensorboard_experiment.name = "name_value"

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
        "tensorboard_experiment.name=name_value",
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
        arg = args[0].tensorboard_experiment
        mock_val = gca_tensorboard_experiment.TensorboardExperiment(name="name_value")
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=["paths_value"])
        assert arg == mock_val


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
        arg = args[0].tensorboard_experiment
        mock_val = gca_tensorboard_experiment.TensorboardExperiment(name="name_value")
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=["paths_value"])
        assert arg == mock_val


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


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.ListTensorboardExperimentsRequest,
        dict,
    ],
)
def test_list_tensorboard_experiments(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_list_tensorboard_experiments_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.parent = "parent_value"

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
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_tensorboard_experiments_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ListTensorboardExperimentsRequest()

    request.parent = "parent_value"

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
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


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
        client.list_tensorboard_experiments(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


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
        response = await client.list_tensorboard_experiments(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


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


def test_list_tensorboard_experiments_pager(transport_name: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials,
        transport=transport_name,
    )

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
                tensorboard_experiments=[],
                next_page_token="def",
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

        results = list(pager)
        assert len(results) == 6
        assert all(
            isinstance(i, tensorboard_experiment.TensorboardExperiment) for i in results
        )


def test_list_tensorboard_experiments_pages(transport_name: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials,
        transport=transport_name,
    )

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
                tensorboard_experiments=[],
                next_page_token="def",
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
                tensorboard_experiments=[],
                next_page_token="def",
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
        async_pager = await client.list_tensorboard_experiments(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
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
                tensorboard_experiments=[],
                next_page_token="def",
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
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.list_tensorboard_experiments(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.DeleteTensorboardExperimentRequest,
        dict,
    ],
)
def test_delete_tensorboard_experiment(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_delete_tensorboard_experiment_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.name = "name_value"

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
    assert (
        "x-goog-request-params",
        "name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_tensorboard_experiment_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.DeleteTensorboardExperimentRequest()

    request.name = "name_value"

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
    assert (
        "x-goog-request-params",
        "name=name_value",
    ) in kw["metadata"]


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
        client.delete_tensorboard_experiment(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_delete_tensorboard_experiment_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_tensorboard_experiment(
            tensorboard_service.DeleteTensorboardExperimentRequest(),
            name="name_value",
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
        response = await client.delete_tensorboard_experiment(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_delete_tensorboard_experiment_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_tensorboard_experiment(
            tensorboard_service.DeleteTensorboardExperimentRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.CreateTensorboardRunRequest,
        dict,
    ],
)
def test_create_tensorboard_run(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_create_tensorboard_run_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.parent = "parent_value"

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
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_tensorboard_run_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.CreateTensorboardRunRequest()

    request.parent = "parent_value"

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
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


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
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].tensorboard_run
        mock_val = gca_tensorboard_run.TensorboardRun(name="name_value")
        assert arg == mock_val
        arg = args[0].tensorboard_run_id
        mock_val = "tensorboard_run_id_value"
        assert arg == mock_val


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
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].tensorboard_run
        mock_val = gca_tensorboard_run.TensorboardRun(name="name_value")
        assert arg == mock_val
        arg = args[0].tensorboard_run_id
        mock_val = "tensorboard_run_id_value"
        assert arg == mock_val


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


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.BatchCreateTensorboardRunsRequest,
        dict,
    ],
)
def test_batch_create_tensorboard_runs(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_create_tensorboard_runs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.BatchCreateTensorboardRunsResponse()
        response = client.batch_create_tensorboard_runs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.BatchCreateTensorboardRunsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, tensorboard_service.BatchCreateTensorboardRunsResponse)


def test_batch_create_tensorboard_runs_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_create_tensorboard_runs), "__call__"
    ) as call:
        client.batch_create_tensorboard_runs()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.BatchCreateTensorboardRunsRequest()


@pytest.mark.asyncio
async def test_batch_create_tensorboard_runs_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.BatchCreateTensorboardRunsRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_create_tensorboard_runs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.BatchCreateTensorboardRunsResponse()
        )
        response = await client.batch_create_tensorboard_runs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.BatchCreateTensorboardRunsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, tensorboard_service.BatchCreateTensorboardRunsResponse)


@pytest.mark.asyncio
async def test_batch_create_tensorboard_runs_async_from_dict():
    await test_batch_create_tensorboard_runs_async(request_type=dict)


def test_batch_create_tensorboard_runs_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.BatchCreateTensorboardRunsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_create_tensorboard_runs), "__call__"
    ) as call:
        call.return_value = tensorboard_service.BatchCreateTensorboardRunsResponse()
        client.batch_create_tensorboard_runs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_batch_create_tensorboard_runs_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.BatchCreateTensorboardRunsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_create_tensorboard_runs), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.BatchCreateTensorboardRunsResponse()
        )
        await client.batch_create_tensorboard_runs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


def test_batch_create_tensorboard_runs_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_create_tensorboard_runs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.BatchCreateTensorboardRunsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.batch_create_tensorboard_runs(
            parent="parent_value",
            requests=[
                tensorboard_service.CreateTensorboardRunRequest(parent="parent_value")
            ],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].requests
        mock_val = [
            tensorboard_service.CreateTensorboardRunRequest(parent="parent_value")
        ]
        assert arg == mock_val


def test_batch_create_tensorboard_runs_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.batch_create_tensorboard_runs(
            tensorboard_service.BatchCreateTensorboardRunsRequest(),
            parent="parent_value",
            requests=[
                tensorboard_service.CreateTensorboardRunRequest(parent="parent_value")
            ],
        )


@pytest.mark.asyncio
async def test_batch_create_tensorboard_runs_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_create_tensorboard_runs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.BatchCreateTensorboardRunsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.BatchCreateTensorboardRunsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.batch_create_tensorboard_runs(
            parent="parent_value",
            requests=[
                tensorboard_service.CreateTensorboardRunRequest(parent="parent_value")
            ],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].requests
        mock_val = [
            tensorboard_service.CreateTensorboardRunRequest(parent="parent_value")
        ]
        assert arg == mock_val


@pytest.mark.asyncio
async def test_batch_create_tensorboard_runs_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.batch_create_tensorboard_runs(
            tensorboard_service.BatchCreateTensorboardRunsRequest(),
            parent="parent_value",
            requests=[
                tensorboard_service.CreateTensorboardRunRequest(parent="parent_value")
            ],
        )


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.GetTensorboardRunRequest,
        dict,
    ],
)
def test_get_tensorboard_run(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_get_tensorboard_run_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.name = "name_value"

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
    assert (
        "x-goog-request-params",
        "name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_tensorboard_run_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.GetTensorboardRunRequest()

    request.name = "name_value"

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
    assert (
        "x-goog-request-params",
        "name=name_value",
    ) in kw["metadata"]


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
        client.get_tensorboard_run(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_get_tensorboard_run_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_tensorboard_run(
            tensorboard_service.GetTensorboardRunRequest(),
            name="name_value",
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
        response = await client.get_tensorboard_run(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_get_tensorboard_run_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_tensorboard_run(
            tensorboard_service.GetTensorboardRunRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.UpdateTensorboardRunRequest,
        dict,
    ],
)
def test_update_tensorboard_run(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_update_tensorboard_run_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.tensorboard_run.name = "name_value"

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
        "tensorboard_run.name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_tensorboard_run_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.UpdateTensorboardRunRequest()

    request.tensorboard_run.name = "name_value"

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
        "tensorboard_run.name=name_value",
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
        arg = args[0].tensorboard_run
        mock_val = gca_tensorboard_run.TensorboardRun(name="name_value")
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=["paths_value"])
        assert arg == mock_val


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
        arg = args[0].tensorboard_run
        mock_val = gca_tensorboard_run.TensorboardRun(name="name_value")
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=["paths_value"])
        assert arg == mock_val


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


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.ListTensorboardRunsRequest,
        dict,
    ],
)
def test_list_tensorboard_runs(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_list_tensorboard_runs_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.parent = "parent_value"

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
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_tensorboard_runs_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ListTensorboardRunsRequest()

    request.parent = "parent_value"

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
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


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
        client.list_tensorboard_runs(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_list_tensorboard_runs_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_tensorboard_runs(
            tensorboard_service.ListTensorboardRunsRequest(),
            parent="parent_value",
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
        response = await client.list_tensorboard_runs(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_list_tensorboard_runs_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_tensorboard_runs(
            tensorboard_service.ListTensorboardRunsRequest(),
            parent="parent_value",
        )


def test_list_tensorboard_runs_pager(transport_name: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials,
        transport=transport_name,
    )

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
                tensorboard_runs=[],
                next_page_token="def",
            ),
            tensorboard_service.ListTensorboardRunsResponse(
                tensorboard_runs=[
                    tensorboard_run.TensorboardRun(),
                ],
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

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, tensorboard_run.TensorboardRun) for i in results)


def test_list_tensorboard_runs_pages(transport_name: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials,
        transport=transport_name,
    )

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
                tensorboard_runs=[],
                next_page_token="def",
            ),
            tensorboard_service.ListTensorboardRunsResponse(
                tensorboard_runs=[
                    tensorboard_run.TensorboardRun(),
                ],
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
                tensorboard_runs=[],
                next_page_token="def",
            ),
            tensorboard_service.ListTensorboardRunsResponse(
                tensorboard_runs=[
                    tensorboard_run.TensorboardRun(),
                ],
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
        async_pager = await client.list_tensorboard_runs(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
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
                tensorboard_runs=[],
                next_page_token="def",
            ),
            tensorboard_service.ListTensorboardRunsResponse(
                tensorboard_runs=[
                    tensorboard_run.TensorboardRun(),
                ],
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
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.list_tensorboard_runs(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.DeleteTensorboardRunRequest,
        dict,
    ],
)
def test_delete_tensorboard_run(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_delete_tensorboard_run_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.name = "name_value"

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
    assert (
        "x-goog-request-params",
        "name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_tensorboard_run_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.DeleteTensorboardRunRequest()

    request.name = "name_value"

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
    assert (
        "x-goog-request-params",
        "name=name_value",
    ) in kw["metadata"]


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
        client.delete_tensorboard_run(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_delete_tensorboard_run_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_tensorboard_run(
            tensorboard_service.DeleteTensorboardRunRequest(),
            name="name_value",
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
        response = await client.delete_tensorboard_run(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_delete_tensorboard_run_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_tensorboard_run(
            tensorboard_service.DeleteTensorboardRunRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.BatchCreateTensorboardTimeSeriesRequest,
        dict,
    ],
)
def test_batch_create_tensorboard_time_series(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_create_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            tensorboard_service.BatchCreateTensorboardTimeSeriesResponse()
        )
        response = client.batch_create_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.BatchCreateTensorboardTimeSeriesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, tensorboard_service.BatchCreateTensorboardTimeSeriesResponse
    )


def test_batch_create_tensorboard_time_series_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_create_tensorboard_time_series), "__call__"
    ) as call:
        client.batch_create_tensorboard_time_series()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.BatchCreateTensorboardTimeSeriesRequest()


@pytest.mark.asyncio
async def test_batch_create_tensorboard_time_series_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.BatchCreateTensorboardTimeSeriesRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_create_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.BatchCreateTensorboardTimeSeriesResponse()
        )
        response = await client.batch_create_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.BatchCreateTensorboardTimeSeriesRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, tensorboard_service.BatchCreateTensorboardTimeSeriesResponse
    )


@pytest.mark.asyncio
async def test_batch_create_tensorboard_time_series_async_from_dict():
    await test_batch_create_tensorboard_time_series_async(request_type=dict)


def test_batch_create_tensorboard_time_series_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.BatchCreateTensorboardTimeSeriesRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_create_tensorboard_time_series), "__call__"
    ) as call:
        call.return_value = (
            tensorboard_service.BatchCreateTensorboardTimeSeriesResponse()
        )
        client.batch_create_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_batch_create_tensorboard_time_series_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.BatchCreateTensorboardTimeSeriesRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_create_tensorboard_time_series), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.BatchCreateTensorboardTimeSeriesResponse()
        )
        await client.batch_create_tensorboard_time_series(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


def test_batch_create_tensorboard_time_series_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_create_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            tensorboard_service.BatchCreateTensorboardTimeSeriesResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.batch_create_tensorboard_time_series(
            parent="parent_value",
            requests=[
                tensorboard_service.CreateTensorboardTimeSeriesRequest(
                    parent="parent_value"
                )
            ],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].requests
        mock_val = [
            tensorboard_service.CreateTensorboardTimeSeriesRequest(
                parent="parent_value"
            )
        ]
        assert arg == mock_val


def test_batch_create_tensorboard_time_series_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.batch_create_tensorboard_time_series(
            tensorboard_service.BatchCreateTensorboardTimeSeriesRequest(),
            parent="parent_value",
            requests=[
                tensorboard_service.CreateTensorboardTimeSeriesRequest(
                    parent="parent_value"
                )
            ],
        )


@pytest.mark.asyncio
async def test_batch_create_tensorboard_time_series_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_create_tensorboard_time_series), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            tensorboard_service.BatchCreateTensorboardTimeSeriesResponse()
        )

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.BatchCreateTensorboardTimeSeriesResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.batch_create_tensorboard_time_series(
            parent="parent_value",
            requests=[
                tensorboard_service.CreateTensorboardTimeSeriesRequest(
                    parent="parent_value"
                )
            ],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].requests
        mock_val = [
            tensorboard_service.CreateTensorboardTimeSeriesRequest(
                parent="parent_value"
            )
        ]
        assert arg == mock_val


@pytest.mark.asyncio
async def test_batch_create_tensorboard_time_series_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.batch_create_tensorboard_time_series(
            tensorboard_service.BatchCreateTensorboardTimeSeriesRequest(),
            parent="parent_value",
            requests=[
                tensorboard_service.CreateTensorboardTimeSeriesRequest(
                    parent="parent_value"
                )
            ],
        )


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.CreateTensorboardTimeSeriesRequest,
        dict,
    ],
)
def test_create_tensorboard_time_series(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_create_tensorboard_time_series_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.parent = "parent_value"

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
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_tensorboard_time_series_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.CreateTensorboardTimeSeriesRequest()

    request.parent = "parent_value"

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
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


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
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].tensorboard_time_series
        mock_val = gca_tensorboard_time_series.TensorboardTimeSeries(name="name_value")
        assert arg == mock_val


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
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].tensorboard_time_series
        mock_val = gca_tensorboard_time_series.TensorboardTimeSeries(name="name_value")
        assert arg == mock_val


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


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.GetTensorboardTimeSeriesRequest,
        dict,
    ],
)
def test_get_tensorboard_time_series(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_get_tensorboard_time_series_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.name = "name_value"

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
    assert (
        "x-goog-request-params",
        "name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_tensorboard_time_series_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.GetTensorboardTimeSeriesRequest()

    request.name = "name_value"

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
    assert (
        "x-goog-request-params",
        "name=name_value",
    ) in kw["metadata"]


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
        client.get_tensorboard_time_series(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_get_tensorboard_time_series_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_tensorboard_time_series(
            tensorboard_service.GetTensorboardTimeSeriesRequest(),
            name="name_value",
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
        response = await client.get_tensorboard_time_series(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_get_tensorboard_time_series_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_tensorboard_time_series(
            tensorboard_service.GetTensorboardTimeSeriesRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.UpdateTensorboardTimeSeriesRequest,
        dict,
    ],
)
def test_update_tensorboard_time_series(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_update_tensorboard_time_series_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.tensorboard_time_series.name = "name_value"

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
        "tensorboard_time_series.name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_tensorboard_time_series_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.UpdateTensorboardTimeSeriesRequest()

    request.tensorboard_time_series.name = "name_value"

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
        "tensorboard_time_series.name=name_value",
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
        arg = args[0].tensorboard_time_series
        mock_val = gca_tensorboard_time_series.TensorboardTimeSeries(name="name_value")
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=["paths_value"])
        assert arg == mock_val


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
        arg = args[0].tensorboard_time_series
        mock_val = gca_tensorboard_time_series.TensorboardTimeSeries(name="name_value")
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=["paths_value"])
        assert arg == mock_val


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


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.ListTensorboardTimeSeriesRequest,
        dict,
    ],
)
def test_list_tensorboard_time_series(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_list_tensorboard_time_series_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.parent = "parent_value"

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
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_tensorboard_time_series_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ListTensorboardTimeSeriesRequest()

    request.parent = "parent_value"

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
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


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
        client.list_tensorboard_time_series(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


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
        response = await client.list_tensorboard_time_series(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


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


def test_list_tensorboard_time_series_pager(transport_name: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials,
        transport=transport_name,
    )

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
                tensorboard_time_series=[],
                next_page_token="def",
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

        results = list(pager)
        assert len(results) == 6
        assert all(
            isinstance(i, tensorboard_time_series.TensorboardTimeSeries)
            for i in results
        )


def test_list_tensorboard_time_series_pages(transport_name: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials,
        transport=transport_name,
    )

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
                tensorboard_time_series=[],
                next_page_token="def",
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
                tensorboard_time_series=[],
                next_page_token="def",
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
        async_pager = await client.list_tensorboard_time_series(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
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
                tensorboard_time_series=[],
                next_page_token="def",
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
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.list_tensorboard_time_series(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.DeleteTensorboardTimeSeriesRequest,
        dict,
    ],
)
def test_delete_tensorboard_time_series(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_delete_tensorboard_time_series_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.name = "name_value"

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
    assert (
        "x-goog-request-params",
        "name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_tensorboard_time_series_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.DeleteTensorboardTimeSeriesRequest()

    request.name = "name_value"

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
    assert (
        "x-goog-request-params",
        "name=name_value",
    ) in kw["metadata"]


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
        client.delete_tensorboard_time_series(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_delete_tensorboard_time_series_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_tensorboard_time_series(
            tensorboard_service.DeleteTensorboardTimeSeriesRequest(),
            name="name_value",
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
        response = await client.delete_tensorboard_time_series(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_delete_tensorboard_time_series_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_tensorboard_time_series(
            tensorboard_service.DeleteTensorboardTimeSeriesRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.BatchReadTensorboardTimeSeriesDataRequest,
        dict,
    ],
)
def test_batch_read_tensorboard_time_series_data(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_read_tensorboard_time_series_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            tensorboard_service.BatchReadTensorboardTimeSeriesDataResponse()
        )
        response = client.batch_read_tensorboard_time_series_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert (
            args[0] == tensorboard_service.BatchReadTensorboardTimeSeriesDataRequest()
        )

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, tensorboard_service.BatchReadTensorboardTimeSeriesDataResponse
    )


def test_batch_read_tensorboard_time_series_data_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_read_tensorboard_time_series_data), "__call__"
    ) as call:
        client.batch_read_tensorboard_time_series_data()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert (
            args[0] == tensorboard_service.BatchReadTensorboardTimeSeriesDataRequest()
        )


@pytest.mark.asyncio
async def test_batch_read_tensorboard_time_series_data_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.BatchReadTensorboardTimeSeriesDataRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_read_tensorboard_time_series_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.BatchReadTensorboardTimeSeriesDataResponse()
        )
        response = await client.batch_read_tensorboard_time_series_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert (
            args[0] == tensorboard_service.BatchReadTensorboardTimeSeriesDataRequest()
        )

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, tensorboard_service.BatchReadTensorboardTimeSeriesDataResponse
    )


@pytest.mark.asyncio
async def test_batch_read_tensorboard_time_series_data_async_from_dict():
    await test_batch_read_tensorboard_time_series_data_async(request_type=dict)


def test_batch_read_tensorboard_time_series_data_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.BatchReadTensorboardTimeSeriesDataRequest()

    request.tensorboard = "tensorboard_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_read_tensorboard_time_series_data), "__call__"
    ) as call:
        call.return_value = (
            tensorboard_service.BatchReadTensorboardTimeSeriesDataResponse()
        )
        client.batch_read_tensorboard_time_series_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "tensorboard=tensorboard_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_batch_read_tensorboard_time_series_data_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.BatchReadTensorboardTimeSeriesDataRequest()

    request.tensorboard = "tensorboard_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_read_tensorboard_time_series_data), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.BatchReadTensorboardTimeSeriesDataResponse()
        )
        await client.batch_read_tensorboard_time_series_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "tensorboard=tensorboard_value",
    ) in kw["metadata"]


def test_batch_read_tensorboard_time_series_data_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_read_tensorboard_time_series_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            tensorboard_service.BatchReadTensorboardTimeSeriesDataResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.batch_read_tensorboard_time_series_data(
            tensorboard="tensorboard_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].tensorboard
        mock_val = "tensorboard_value"
        assert arg == mock_val


def test_batch_read_tensorboard_time_series_data_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.batch_read_tensorboard_time_series_data(
            tensorboard_service.BatchReadTensorboardTimeSeriesDataRequest(),
            tensorboard="tensorboard_value",
        )


@pytest.mark.asyncio
async def test_batch_read_tensorboard_time_series_data_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.batch_read_tensorboard_time_series_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            tensorboard_service.BatchReadTensorboardTimeSeriesDataResponse()
        )

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.BatchReadTensorboardTimeSeriesDataResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.batch_read_tensorboard_time_series_data(
            tensorboard="tensorboard_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].tensorboard
        mock_val = "tensorboard_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_batch_read_tensorboard_time_series_data_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.batch_read_tensorboard_time_series_data(
            tensorboard_service.BatchReadTensorboardTimeSeriesDataRequest(),
            tensorboard="tensorboard_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.ReadTensorboardTimeSeriesDataRequest,
        dict,
    ],
)
def test_read_tensorboard_time_series_data(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_read_tensorboard_time_series_data_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.tensorboard_time_series = "tensorboard_time_series_value"

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
        "tensorboard_time_series=tensorboard_time_series_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_read_tensorboard_time_series_data_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ReadTensorboardTimeSeriesDataRequest()

    request.tensorboard_time_series = "tensorboard_time_series_value"

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
        "tensorboard_time_series=tensorboard_time_series_value",
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
        arg = args[0].tensorboard_time_series
        mock_val = "tensorboard_time_series_value"
        assert arg == mock_val


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
        arg = args[0].tensorboard_time_series
        mock_val = "tensorboard_time_series_value"
        assert arg == mock_val


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


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.ReadTensorboardBlobDataRequest,
        dict,
    ],
)
def test_read_tensorboard_blob_data(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_read_tensorboard_blob_data_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.time_series = "time_series_value"

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
    assert (
        "x-goog-request-params",
        "time_series=time_series_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_read_tensorboard_blob_data_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ReadTensorboardBlobDataRequest()

    request.time_series = "time_series_value"

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
    assert (
        "x-goog-request-params",
        "time_series=time_series_value",
    ) in kw["metadata"]


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
        client.read_tensorboard_blob_data(
            time_series="time_series_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].time_series
        mock_val = "time_series_value"
        assert arg == mock_val


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
        arg = args[0].time_series
        mock_val = "time_series_value"
        assert arg == mock_val


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


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.WriteTensorboardExperimentDataRequest,
        dict,
    ],
)
def test_write_tensorboard_experiment_data(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.write_tensorboard_experiment_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.WriteTensorboardExperimentDataResponse()
        response = client.write_tensorboard_experiment_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.WriteTensorboardExperimentDataRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, tensorboard_service.WriteTensorboardExperimentDataResponse
    )


def test_write_tensorboard_experiment_data_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.write_tensorboard_experiment_data), "__call__"
    ) as call:
        client.write_tensorboard_experiment_data()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.WriteTensorboardExperimentDataRequest()


@pytest.mark.asyncio
async def test_write_tensorboard_experiment_data_async(
    transport: str = "grpc_asyncio",
    request_type=tensorboard_service.WriteTensorboardExperimentDataRequest,
):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.write_tensorboard_experiment_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.WriteTensorboardExperimentDataResponse()
        )
        response = await client.write_tensorboard_experiment_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == tensorboard_service.WriteTensorboardExperimentDataRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, tensorboard_service.WriteTensorboardExperimentDataResponse
    )


@pytest.mark.asyncio
async def test_write_tensorboard_experiment_data_async_from_dict():
    await test_write_tensorboard_experiment_data_async(request_type=dict)


def test_write_tensorboard_experiment_data_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.WriteTensorboardExperimentDataRequest()

    request.tensorboard_experiment = "tensorboard_experiment_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.write_tensorboard_experiment_data), "__call__"
    ) as call:
        call.return_value = tensorboard_service.WriteTensorboardExperimentDataResponse()
        client.write_tensorboard_experiment_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "tensorboard_experiment=tensorboard_experiment_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_write_tensorboard_experiment_data_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.WriteTensorboardExperimentDataRequest()

    request.tensorboard_experiment = "tensorboard_experiment_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.write_tensorboard_experiment_data), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.WriteTensorboardExperimentDataResponse()
        )
        await client.write_tensorboard_experiment_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "tensorboard_experiment=tensorboard_experiment_value",
    ) in kw["metadata"]


def test_write_tensorboard_experiment_data_flattened():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.write_tensorboard_experiment_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.WriteTensorboardExperimentDataResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.write_tensorboard_experiment_data(
            tensorboard_experiment="tensorboard_experiment_value",
            write_run_data_requests=[
                tensorboard_service.WriteTensorboardRunDataRequest(
                    tensorboard_run="tensorboard_run_value"
                )
            ],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].tensorboard_experiment
        mock_val = "tensorboard_experiment_value"
        assert arg == mock_val
        arg = args[0].write_run_data_requests
        mock_val = [
            tensorboard_service.WriteTensorboardRunDataRequest(
                tensorboard_run="tensorboard_run_value"
            )
        ]
        assert arg == mock_val


def test_write_tensorboard_experiment_data_flattened_error():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.write_tensorboard_experiment_data(
            tensorboard_service.WriteTensorboardExperimentDataRequest(),
            tensorboard_experiment="tensorboard_experiment_value",
            write_run_data_requests=[
                tensorboard_service.WriteTensorboardRunDataRequest(
                    tensorboard_run="tensorboard_run_value"
                )
            ],
        )


@pytest.mark.asyncio
async def test_write_tensorboard_experiment_data_flattened_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.write_tensorboard_experiment_data), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = tensorboard_service.WriteTensorboardExperimentDataResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            tensorboard_service.WriteTensorboardExperimentDataResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.write_tensorboard_experiment_data(
            tensorboard_experiment="tensorboard_experiment_value",
            write_run_data_requests=[
                tensorboard_service.WriteTensorboardRunDataRequest(
                    tensorboard_run="tensorboard_run_value"
                )
            ],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].tensorboard_experiment
        mock_val = "tensorboard_experiment_value"
        assert arg == mock_val
        arg = args[0].write_run_data_requests
        mock_val = [
            tensorboard_service.WriteTensorboardRunDataRequest(
                tensorboard_run="tensorboard_run_value"
            )
        ]
        assert arg == mock_val


@pytest.mark.asyncio
async def test_write_tensorboard_experiment_data_flattened_error_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.write_tensorboard_experiment_data(
            tensorboard_service.WriteTensorboardExperimentDataRequest(),
            tensorboard_experiment="tensorboard_experiment_value",
            write_run_data_requests=[
                tensorboard_service.WriteTensorboardRunDataRequest(
                    tensorboard_run="tensorboard_run_value"
                )
            ],
        )


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.WriteTensorboardRunDataRequest,
        dict,
    ],
)
def test_write_tensorboard_run_data(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_write_tensorboard_run_data_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.tensorboard_run = "tensorboard_run_value"

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
    assert (
        "x-goog-request-params",
        "tensorboard_run=tensorboard_run_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_write_tensorboard_run_data_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.WriteTensorboardRunDataRequest()

    request.tensorboard_run = "tensorboard_run_value"

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
    assert (
        "x-goog-request-params",
        "tensorboard_run=tensorboard_run_value",
    ) in kw["metadata"]


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
        arg = args[0].tensorboard_run
        mock_val = "tensorboard_run_value"
        assert arg == mock_val
        arg = args[0].time_series_data
        mock_val = [
            tensorboard_data.TimeSeriesData(
                tensorboard_time_series_id="tensorboard_time_series_id_value"
            )
        ]
        assert arg == mock_val


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
        arg = args[0].tensorboard_run
        mock_val = "tensorboard_run_value"
        assert arg == mock_val
        arg = args[0].time_series_data
        mock_val = [
            tensorboard_data.TimeSeriesData(
                tensorboard_time_series_id="tensorboard_time_series_id_value"
            )
        ]
        assert arg == mock_val


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


@pytest.mark.parametrize(
    "request_type",
    [
        tensorboard_service.ExportTensorboardTimeSeriesDataRequest,
        dict,
    ],
)
def test_export_tensorboard_time_series_data(request_type, transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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


def test_export_tensorboard_time_series_data_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
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

    request.tensorboard_time_series = "tensorboard_time_series_value"

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
        "tensorboard_time_series=tensorboard_time_series_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_export_tensorboard_time_series_data_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = tensorboard_service.ExportTensorboardTimeSeriesDataRequest()

    request.tensorboard_time_series = "tensorboard_time_series_value"

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
        "tensorboard_time_series=tensorboard_time_series_value",
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
        arg = args[0].tensorboard_time_series
        mock_val = "tensorboard_time_series_value"
        assert arg == mock_val


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
        arg = args[0].tensorboard_time_series
        mock_val = "tensorboard_time_series_value"
        assert arg == mock_val


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


def test_export_tensorboard_time_series_data_pager(transport_name: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials,
        transport=transport_name,
    )

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
                time_series_data_points=[],
                next_page_token="def",
            ),
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse(
                time_series_data_points=[
                    tensorboard_data.TimeSeriesDataPoint(),
                ],
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

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, tensorboard_data.TimeSeriesDataPoint) for i in results)


def test_export_tensorboard_time_series_data_pages(transport_name: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials,
        transport=transport_name,
    )

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
                time_series_data_points=[],
                next_page_token="def",
            ),
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse(
                time_series_data_points=[
                    tensorboard_data.TimeSeriesDataPoint(),
                ],
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
                time_series_data_points=[],
                next_page_token="def",
            ),
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse(
                time_series_data_points=[
                    tensorboard_data.TimeSeriesDataPoint(),
                ],
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
        async_pager = await client.export_tensorboard_time_series_data(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
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
                time_series_data_points=[],
                next_page_token="def",
            ),
            tensorboard_service.ExportTensorboardTimeSeriesDataResponse(
                time_series_data_points=[
                    tensorboard_data.TimeSeriesDataPoint(),
                ],
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
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
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
            credentials=ga_credentials.AnonymousCredentials(),
            transport=transport,
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

    # It is an error to provide an api_key and a transport instance.
    transport = transports.TensorboardServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    options = client_options.ClientOptions()
    options.api_key = "api_key"
    with pytest.raises(ValueError):
        client = TensorboardServiceClient(
            client_options=options,
            transport=transport,
        )

    # It is an error to provide an api_key and a credential.
    options = mock.Mock()
    options.api_key = "api_key"
    with pytest.raises(ValueError):
        client = TensorboardServiceClient(
            client_options=options, credentials=ga_credentials.AnonymousCredentials()
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.TensorboardServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = TensorboardServiceClient(
            client_options={"scopes": ["1", "2"]},
            transport=transport,
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


@pytest.mark.parametrize(
    "transport_name",
    [
        "grpc",
    ],
)
def test_transport_kind(transport_name):
    transport = TensorboardServiceClient.get_transport_class(transport_name)(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    assert transport.kind == transport_name


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    assert isinstance(
        client.transport,
        transports.TensorboardServiceGrpcTransport,
    )


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
        "read_tensorboard_usage",
        "read_tensorboard_size",
        "create_tensorboard_experiment",
        "get_tensorboard_experiment",
        "update_tensorboard_experiment",
        "list_tensorboard_experiments",
        "delete_tensorboard_experiment",
        "create_tensorboard_run",
        "batch_create_tensorboard_runs",
        "get_tensorboard_run",
        "update_tensorboard_run",
        "list_tensorboard_runs",
        "delete_tensorboard_run",
        "batch_create_tensorboard_time_series",
        "create_tensorboard_time_series",
        "get_tensorboard_time_series",
        "update_tensorboard_time_series",
        "list_tensorboard_time_series",
        "delete_tensorboard_time_series",
        "batch_read_tensorboard_time_series_data",
        "read_tensorboard_time_series_data",
        "read_tensorboard_blob_data",
        "write_tensorboard_experiment_data",
        "write_tensorboard_run_data",
        "export_tensorboard_time_series_data",
        "set_iam_policy",
        "get_iam_policy",
        "test_iam_permissions",
        "get_location",
        "list_locations",
        "get_operation",
        "wait_operation",
        "cancel_operation",
        "delete_operation",
        "list_operations",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    with pytest.raises(NotImplementedError):
        transport.close()

    # Additionally, the LRO client (a property) should
    # also raise NotImplementedError
    with pytest.raises(NotImplementedError):
        transport.operations_client

    # Catch all for all remaining methods and properties
    remainder = [
        "kind",
    ]
    for r in remainder:
        with pytest.raises(NotImplementedError):
            getattr(transport, r)()


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
            credentials_file="credentials.json",
            quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=None,
            default_scopes=("https://www.googleapis.com/auth/cloud-platform",),
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


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.TensorboardServiceGrpcTransport,
        transports.TensorboardServiceGrpcAsyncIOTransport,
    ],
)
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
def test_tensorboard_service_transport_auth_gdch_credentials(transport_class):
    host = "https://language.com"
    api_audience_tests = [None, "https://language2.com"]
    api_audience_expect = [host, "https://language2.com"]
    for t, e in zip(api_audience_tests, api_audience_expect):
        with mock.patch.object(google.auth, "default", autospec=True) as adc:
            gdch_mock = mock.MagicMock()
            type(gdch_mock).with_gdch_audience = mock.PropertyMock(
                return_value=gdch_mock
            )
            adc.return_value = (gdch_mock, None)
            transport_class(host=host, api_audience=t)
            gdch_mock.with_gdch_audience.assert_called_once_with(e)


@pytest.mark.parametrize(
    "transport_class,grpc_helpers",
    [
        (transports.TensorboardServiceGrpcTransport, grpc_helpers),
        (transports.TensorboardServiceGrpcAsyncIOTransport, grpc_helpers_async),
    ],
)
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


@pytest.mark.parametrize(
    "transport_name",
    [
        "grpc",
        "grpc_asyncio",
    ],
)
def test_tensorboard_service_host_no_port(transport_name):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="aiplatform.googleapis.com"
        ),
        transport=transport_name,
    )
    assert client.transport._host == ("aiplatform.googleapis.com:443")


@pytest.mark.parametrize(
    "transport_name",
    [
        "grpc",
        "grpc_asyncio",
    ],
)
def test_tensorboard_service_host_with_port(transport_name):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="aiplatform.googleapis.com:8000"
        ),
        transport=transport_name,
    )
    assert client.transport._host == ("aiplatform.googleapis.com:8000")


def test_tensorboard_service_grpc_transport_channel():
    channel = grpc.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.TensorboardServiceGrpcTransport(
        host="squid.clam.whelk",
        channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


def test_tensorboard_service_grpc_asyncio_transport_channel():
    channel = aio.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.TensorboardServiceGrpcAsyncIOTransport(
        host="squid.clam.whelk",
        channel=channel,
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
                scopes=None,
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
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )
    transport = client.transport

    # Ensure that we have a api-core operations client.
    assert isinstance(
        transport.operations_client,
        operations_v1.OperationsClient,
    )

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_tensorboard_service_grpc_lro_async_client():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc_asyncio",
    )
    transport = client.transport

    # Ensure that we have a api-core operations client.
    assert isinstance(
        transport.operations_client,
        operations_v1.OperationsAsyncClient,
    )

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_tensorboard_path():
    project = "squid"
    location = "clam"
    tensorboard = "whelk"
    expected = (
        "projects/{project}/locations/{location}/tensorboards/{tensorboard}".format(
            project=project,
            location=location,
            tensorboard=tensorboard,
        )
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
    expected = "folders/{folder}".format(
        folder=folder,
    )
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
    expected = "organizations/{organization}".format(
        organization=organization,
    )
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
    expected = "projects/{project}".format(
        project=project,
    )
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
        project=project,
        location=location,
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


def test_client_with_default_client_info():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(
        transports.TensorboardServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        client = TensorboardServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(
        transports.TensorboardServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        transport_class = TensorboardServiceClient.get_transport_class()
        transport = transport_class(
            credentials=ga_credentials.AnonymousCredentials(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)


@pytest.mark.asyncio
async def test_transport_close_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc_asyncio",
    )
    with mock.patch.object(
        type(getattr(client.transport, "grpc_channel")), "close"
    ) as close:
        async with client:
            close.assert_not_called()
        close.assert_called_once()


def test_delete_operation(transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.DeleteOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        response = client.delete_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_delete_operation_async(transport: str = "grpc"):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.DeleteOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.delete_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_operation_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.DeleteOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        call.return_value = None

        client.delete_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_operation_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.DeleteOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        await client.delete_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


def test_delete_operation_from_dict():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.delete_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


@pytest.mark.asyncio
async def test_delete_operation_from_dict_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.delete_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


def test_cancel_operation(transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.CancelOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        response = client.cancel_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_cancel_operation_async(transport: str = "grpc"):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.CancelOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.cancel_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_cancel_operation_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.CancelOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        call.return_value = None

        client.cancel_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_cancel_operation_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.CancelOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        await client.cancel_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


def test_cancel_operation_from_dict():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.cancel_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


@pytest.mark.asyncio
async def test_cancel_operation_from_dict_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.cancel_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


def test_wait_operation(transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.WaitOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.wait_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation()
        response = client.wait_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.Operation)


@pytest.mark.asyncio
async def test_wait_operation(transport: str = "grpc"):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.WaitOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.wait_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation()
        )
        response = await client.wait_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.Operation)


def test_wait_operation_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.WaitOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.wait_operation), "__call__") as call:
        call.return_value = operations_pb2.Operation()

        client.wait_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_wait_operation_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.WaitOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.wait_operation), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation()
        )
        await client.wait_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


def test_wait_operation_from_dict():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.wait_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation()

        response = client.wait_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


@pytest.mark.asyncio
async def test_wait_operation_from_dict_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.wait_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation()
        )
        response = await client.wait_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


def test_get_operation(transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.GetOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation()
        response = client.get_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.Operation)


@pytest.mark.asyncio
async def test_get_operation_async(transport: str = "grpc"):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.GetOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation()
        )
        response = await client.get_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.Operation)


def test_get_operation_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.GetOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        call.return_value = operations_pb2.Operation()

        client.get_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_operation_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.GetOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation()
        )
        await client.get_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


def test_get_operation_from_dict():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation()

        response = client.get_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


@pytest.mark.asyncio
async def test_get_operation_from_dict_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation()
        )
        response = await client.get_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


def test_list_operations(transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.ListOperationsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.ListOperationsResponse()
        response = client.list_operations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.ListOperationsResponse)


@pytest.mark.asyncio
async def test_list_operations_async(transport: str = "grpc"):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.ListOperationsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.ListOperationsResponse()
        )
        response = await client.list_operations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.ListOperationsResponse)


def test_list_operations_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.ListOperationsRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        call.return_value = operations_pb2.ListOperationsResponse()

        client.list_operations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_operations_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.ListOperationsRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.ListOperationsResponse()
        )
        await client.list_operations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


def test_list_operations_from_dict():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.ListOperationsResponse()

        response = client.list_operations(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


@pytest.mark.asyncio
async def test_list_operations_from_dict_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.ListOperationsResponse()
        )
        response = await client.list_operations(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


def test_list_locations(transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = locations_pb2.ListLocationsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_locations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = locations_pb2.ListLocationsResponse()
        response = client.list_locations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, locations_pb2.ListLocationsResponse)


@pytest.mark.asyncio
async def test_list_locations_async(transport: str = "grpc"):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = locations_pb2.ListLocationsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_locations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            locations_pb2.ListLocationsResponse()
        )
        response = await client.list_locations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, locations_pb2.ListLocationsResponse)


def test_list_locations_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = locations_pb2.ListLocationsRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_locations), "__call__") as call:
        call.return_value = locations_pb2.ListLocationsResponse()

        client.list_locations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_locations_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = locations_pb2.ListLocationsRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_locations), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            locations_pb2.ListLocationsResponse()
        )
        await client.list_locations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


def test_list_locations_from_dict():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_locations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = locations_pb2.ListLocationsResponse()

        response = client.list_locations(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


@pytest.mark.asyncio
async def test_list_locations_from_dict_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_locations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            locations_pb2.ListLocationsResponse()
        )
        response = await client.list_locations(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


def test_get_location(transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = locations_pb2.GetLocationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_location), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = locations_pb2.Location()
        response = client.get_location(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, locations_pb2.Location)


@pytest.mark.asyncio
async def test_get_location_async(transport: str = "grpc_asyncio"):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = locations_pb2.GetLocationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_location), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            locations_pb2.Location()
        )
        response = await client.get_location(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, locations_pb2.Location)


def test_get_location_field_headers():
    client = TensorboardServiceClient(credentials=ga_credentials.AnonymousCredentials())

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = locations_pb2.GetLocationRequest()
    request.name = "locations/abc"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_location), "__call__") as call:
        call.return_value = locations_pb2.Location()

        client.get_location(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations/abc",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_location_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials()
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = locations_pb2.GetLocationRequest()
    request.name = "locations/abc"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_location), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            locations_pb2.Location()
        )
        await client.get_location(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations/abc",
    ) in kw["metadata"]


def test_get_location_from_dict():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_locations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = locations_pb2.Location()

        response = client.get_location(
            request={
                "name": "locations/abc",
            }
        )
        call.assert_called()


@pytest.mark.asyncio
async def test_get_location_from_dict_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_locations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            locations_pb2.Location()
        )
        response = await client.get_location(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


def test_set_iam_policy(transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = iam_policy_pb2.SetIamPolicyRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy_pb2.Policy(
            version=774,
            etag=b"etag_blob",
        )
        response = client.set_iam_policy(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy_pb2.Policy)

    assert response.version == 774

    assert response.etag == b"etag_blob"


@pytest.mark.asyncio
async def test_set_iam_policy_async(transport: str = "grpc_asyncio"):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = iam_policy_pb2.SetIamPolicyRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            policy_pb2.Policy(
                version=774,
                etag=b"etag_blob",
            )
        )
        response = await client.set_iam_policy(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy_pb2.Policy)

    assert response.version == 774

    assert response.etag == b"etag_blob"


def test_set_iam_policy_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy_pb2.SetIamPolicyRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_iam_policy), "__call__") as call:
        call.return_value = policy_pb2.Policy()

        client.set_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "resource=resource/value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_set_iam_policy_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy_pb2.SetIamPolicyRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_iam_policy), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(policy_pb2.Policy())

        await client.set_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "resource=resource/value",
    ) in kw["metadata"]


def test_set_iam_policy_from_dict():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy_pb2.Policy()

        response = client.set_iam_policy(
            request={
                "resource": "resource_value",
                "policy": policy_pb2.Policy(version=774),
            }
        )
        call.assert_called()


@pytest.mark.asyncio
async def test_set_iam_policy_from_dict_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(policy_pb2.Policy())

        response = await client.set_iam_policy(
            request={
                "resource": "resource_value",
                "policy": policy_pb2.Policy(version=774),
            }
        )
        call.assert_called()


def test_get_iam_policy(transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = iam_policy_pb2.GetIamPolicyRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy_pb2.Policy(
            version=774,
            etag=b"etag_blob",
        )

        response = client.get_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy_pb2.Policy)

    assert response.version == 774

    assert response.etag == b"etag_blob"


@pytest.mark.asyncio
async def test_get_iam_policy_async(transport: str = "grpc_asyncio"):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = iam_policy_pb2.GetIamPolicyRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            policy_pb2.Policy(
                version=774,
                etag=b"etag_blob",
            )
        )

        response = await client.get_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy_pb2.Policy)

    assert response.version == 774

    assert response.etag == b"etag_blob"


def test_get_iam_policy_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy_pb2.GetIamPolicyRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_iam_policy), "__call__") as call:
        call.return_value = policy_pb2.Policy()

        client.get_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "resource=resource/value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_iam_policy_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy_pb2.GetIamPolicyRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_iam_policy), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(policy_pb2.Policy())

        await client.get_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "resource=resource/value",
    ) in kw["metadata"]


def test_get_iam_policy_from_dict():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy_pb2.Policy()

        response = client.get_iam_policy(
            request={
                "resource": "resource_value",
                "options": options_pb2.GetPolicyOptions(requested_policy_version=2598),
            }
        )
        call.assert_called()


@pytest.mark.asyncio
async def test_get_iam_policy_from_dict_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(policy_pb2.Policy())

        response = await client.get_iam_policy(
            request={
                "resource": "resource_value",
                "options": options_pb2.GetPolicyOptions(requested_policy_version=2598),
            }
        )
        call.assert_called()


def test_test_iam_permissions(transport: str = "grpc"):
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = iam_policy_pb2.TestIamPermissionsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.test_iam_permissions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = iam_policy_pb2.TestIamPermissionsResponse(
            permissions=["permissions_value"],
        )

        response = client.test_iam_permissions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, iam_policy_pb2.TestIamPermissionsResponse)

    assert response.permissions == ["permissions_value"]


@pytest.mark.asyncio
async def test_test_iam_permissions_async(transport: str = "grpc_asyncio"):
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = iam_policy_pb2.TestIamPermissionsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.test_iam_permissions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            iam_policy_pb2.TestIamPermissionsResponse(
                permissions=["permissions_value"],
            )
        )

        response = await client.test_iam_permissions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, iam_policy_pb2.TestIamPermissionsResponse)

    assert response.permissions == ["permissions_value"]


def test_test_iam_permissions_field_headers():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy_pb2.TestIamPermissionsRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.test_iam_permissions), "__call__"
    ) as call:
        call.return_value = iam_policy_pb2.TestIamPermissionsResponse()

        client.test_iam_permissions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "resource=resource/value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_test_iam_permissions_field_headers_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy_pb2.TestIamPermissionsRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.test_iam_permissions), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            iam_policy_pb2.TestIamPermissionsResponse()
        )

        await client.test_iam_permissions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "resource=resource/value",
    ) in kw["metadata"]


def test_test_iam_permissions_from_dict():
    client = TensorboardServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.test_iam_permissions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = iam_policy_pb2.TestIamPermissionsResponse()

        response = client.test_iam_permissions(
            request={
                "resource": "resource_value",
                "permissions": ["permissions_value"],
            }
        )
        call.assert_called()


@pytest.mark.asyncio
async def test_test_iam_permissions_from_dict_async():
    client = TensorboardServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.test_iam_permissions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            iam_policy_pb2.TestIamPermissionsResponse()
        )

        response = await client.test_iam_permissions(
            request={
                "resource": "resource_value",
                "permissions": ["permissions_value"],
            }
        )
        call.assert_called()


def test_transport_close():
    transports = {
        "grpc": "_grpc_channel",
    }

    for transport, close_name in transports.items():
        client = TensorboardServiceClient(
            credentials=ga_credentials.AnonymousCredentials(), transport=transport
        )
        with mock.patch.object(
            type(getattr(client.transport, close_name)), "close"
        ) as close:
            with client:
                close.assert_not_called()
            close.assert_called_once()


def test_client_ctx():
    transports = [
        "grpc",
    ]
    for transport in transports:
        client = TensorboardServiceClient(
            credentials=ga_credentials.AnonymousCredentials(), transport=transport
        )
        # Test client calls underlying transport.
        with mock.patch.object(type(client.transport), "close") as close:
            close.assert_not_called()
            with client:
                pass
            close.assert_called()


@pytest.mark.parametrize(
    "client_class,transport_class",
    [
        (TensorboardServiceClient, transports.TensorboardServiceGrpcTransport),
        (
            TensorboardServiceAsyncClient,
            transports.TensorboardServiceGrpcAsyncIOTransport,
        ),
    ],
)
def test_api_key_credentials(client_class, transport_class):
    with mock.patch.object(
        google.auth._default, "get_api_key_credentials", create=True
    ) as get_api_key_credentials:
        mock_cred = mock.Mock()
        get_api_key_credentials.return_value = mock_cred
        options = client_options.ClientOptions()
        options.api_key = "api_key"
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class(client_options=options)
            patched.assert_called_once_with(
                credentials=mock_cred,
                credentials_file=None,
                host=client.DEFAULT_ENDPOINT,
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
                always_use_jwt_access=True,
                api_audience=None,
            )
