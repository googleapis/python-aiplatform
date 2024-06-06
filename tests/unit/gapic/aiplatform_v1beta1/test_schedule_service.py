# -*- coding: utf-8 -*-
# Copyright 2024 Google LLC
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
from collections.abc import Iterable
from google.protobuf import json_format
import json
import math
import pytest
from google.api_core import api_core_version
from proto.marshal.rules.dates import DurationRule, TimestampRule
from proto.marshal.rules import wrappers
from requests import Response
from requests import Request, PreparedRequest
from requests.sessions import Session
from google.protobuf import json_format

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
from google.cloud.aiplatform_v1beta1.services.schedule_service import (
    ScheduleServiceAsyncClient,
)
from google.cloud.aiplatform_v1beta1.services.schedule_service import (
    ScheduleServiceClient,
)
from google.cloud.aiplatform_v1beta1.services.schedule_service import pagers
from google.cloud.aiplatform_v1beta1.services.schedule_service import transports
from google.cloud.aiplatform_v1beta1.types import accelerator_type
from google.cloud.aiplatform_v1beta1.types import artifact
from google.cloud.aiplatform_v1beta1.types import context
from google.cloud.aiplatform_v1beta1.types import encryption_spec
from google.cloud.aiplatform_v1beta1.types import execution
from google.cloud.aiplatform_v1beta1.types import explanation
from google.cloud.aiplatform_v1beta1.types import explanation_metadata
from google.cloud.aiplatform_v1beta1.types import io
from google.cloud.aiplatform_v1beta1.types import job_state
from google.cloud.aiplatform_v1beta1.types import machine_resources
from google.cloud.aiplatform_v1beta1.types import model_monitoring_alert
from google.cloud.aiplatform_v1beta1.types import model_monitoring_job
from google.cloud.aiplatform_v1beta1.types import model_monitoring_service
from google.cloud.aiplatform_v1beta1.types import model_monitoring_spec
from google.cloud.aiplatform_v1beta1.types import notebook_execution_job
from google.cloud.aiplatform_v1beta1.types import notebook_service
from google.cloud.aiplatform_v1beta1.types import operation as gca_operation
from google.cloud.aiplatform_v1beta1.types import pipeline_failure_policy
from google.cloud.aiplatform_v1beta1.types import pipeline_job
from google.cloud.aiplatform_v1beta1.types import pipeline_service
from google.cloud.aiplatform_v1beta1.types import pipeline_state
from google.cloud.aiplatform_v1beta1.types import schedule
from google.cloud.aiplatform_v1beta1.types import schedule as gca_schedule
from google.cloud.aiplatform_v1beta1.types import schedule_service
from google.cloud.aiplatform_v1beta1.types import value
from google.cloud.location import locations_pb2
from google.iam.v1 import iam_policy_pb2  # type: ignore
from google.iam.v1 import options_pb2  # type: ignore
from google.iam.v1 import policy_pb2  # type: ignore
from google.longrunning import operations_pb2  # type: ignore
from google.oauth2 import service_account
from google.protobuf import any_pb2  # type: ignore
from google.protobuf import duration_pb2  # type: ignore
from google.protobuf import empty_pb2  # type: ignore
from google.protobuf import field_mask_pb2  # type: ignore
from google.protobuf import struct_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
from google.rpc import status_pb2  # type: ignore
from google.type import interval_pb2  # type: ignore
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


# If default endpoint template is localhost, then default mtls endpoint will be the same.
# This method modifies the default endpoint template so the client can produce a different
# mtls endpoint for endpoint testing purposes.
def modify_default_endpoint_template(client):
    return (
        "test.{UNIVERSE_DOMAIN}"
        if ("localhost" in client._DEFAULT_ENDPOINT_TEMPLATE)
        else client._DEFAULT_ENDPOINT_TEMPLATE
    )


def test__get_default_mtls_endpoint():
    api_endpoint = "example.googleapis.com"
    api_mtls_endpoint = "example.mtls.googleapis.com"
    sandbox_endpoint = "example.sandbox.googleapis.com"
    sandbox_mtls_endpoint = "example.mtls.sandbox.googleapis.com"
    non_googleapi = "api.example.com"

    assert ScheduleServiceClient._get_default_mtls_endpoint(None) is None
    assert (
        ScheduleServiceClient._get_default_mtls_endpoint(api_endpoint)
        == api_mtls_endpoint
    )
    assert (
        ScheduleServiceClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        ScheduleServiceClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        ScheduleServiceClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        ScheduleServiceClient._get_default_mtls_endpoint(non_googleapi) == non_googleapi
    )


def test__read_environment_variables():
    assert ScheduleServiceClient._read_environment_variables() == (False, "auto", None)

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        assert ScheduleServiceClient._read_environment_variables() == (
            True,
            "auto",
            None,
        )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "false"}):
        assert ScheduleServiceClient._read_environment_variables() == (
            False,
            "auto",
            None,
        )

    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}
    ):
        with pytest.raises(ValueError) as excinfo:
            ScheduleServiceClient._read_environment_variables()
    assert (
        str(excinfo.value)
        == "Environment variable `GOOGLE_API_USE_CLIENT_CERTIFICATE` must be either `true` or `false`"
    )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        assert ScheduleServiceClient._read_environment_variables() == (
            False,
            "never",
            None,
        )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        assert ScheduleServiceClient._read_environment_variables() == (
            False,
            "always",
            None,
        )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"}):
        assert ScheduleServiceClient._read_environment_variables() == (
            False,
            "auto",
            None,
        )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError) as excinfo:
            ScheduleServiceClient._read_environment_variables()
    assert (
        str(excinfo.value)
        == "Environment variable `GOOGLE_API_USE_MTLS_ENDPOINT` must be `never`, `auto` or `always`"
    )

    with mock.patch.dict(os.environ, {"GOOGLE_CLOUD_UNIVERSE_DOMAIN": "foo.com"}):
        assert ScheduleServiceClient._read_environment_variables() == (
            False,
            "auto",
            "foo.com",
        )


def test__get_client_cert_source():
    mock_provided_cert_source = mock.Mock()
    mock_default_cert_source = mock.Mock()

    assert ScheduleServiceClient._get_client_cert_source(None, False) is None
    assert (
        ScheduleServiceClient._get_client_cert_source(mock_provided_cert_source, False)
        is None
    )
    assert (
        ScheduleServiceClient._get_client_cert_source(mock_provided_cert_source, True)
        == mock_provided_cert_source
    )

    with mock.patch(
        "google.auth.transport.mtls.has_default_client_cert_source", return_value=True
    ):
        with mock.patch(
            "google.auth.transport.mtls.default_client_cert_source",
            return_value=mock_default_cert_source,
        ):
            assert (
                ScheduleServiceClient._get_client_cert_source(None, True)
                is mock_default_cert_source
            )
            assert (
                ScheduleServiceClient._get_client_cert_source(
                    mock_provided_cert_source, "true"
                )
                is mock_provided_cert_source
            )


@mock.patch.object(
    ScheduleServiceClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(ScheduleServiceClient),
)
@mock.patch.object(
    ScheduleServiceAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(ScheduleServiceAsyncClient),
)
def test__get_api_endpoint():
    api_override = "foo.com"
    mock_client_cert_source = mock.Mock()
    default_universe = ScheduleServiceClient._DEFAULT_UNIVERSE
    default_endpoint = ScheduleServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(
        UNIVERSE_DOMAIN=default_universe
    )
    mock_universe = "bar.com"
    mock_endpoint = ScheduleServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(
        UNIVERSE_DOMAIN=mock_universe
    )

    assert (
        ScheduleServiceClient._get_api_endpoint(
            api_override, mock_client_cert_source, default_universe, "always"
        )
        == api_override
    )
    assert (
        ScheduleServiceClient._get_api_endpoint(
            None, mock_client_cert_source, default_universe, "auto"
        )
        == ScheduleServiceClient.DEFAULT_MTLS_ENDPOINT
    )
    assert (
        ScheduleServiceClient._get_api_endpoint(None, None, default_universe, "auto")
        == default_endpoint
    )
    assert (
        ScheduleServiceClient._get_api_endpoint(None, None, default_universe, "always")
        == ScheduleServiceClient.DEFAULT_MTLS_ENDPOINT
    )
    assert (
        ScheduleServiceClient._get_api_endpoint(
            None, mock_client_cert_source, default_universe, "always"
        )
        == ScheduleServiceClient.DEFAULT_MTLS_ENDPOINT
    )
    assert (
        ScheduleServiceClient._get_api_endpoint(None, None, mock_universe, "never")
        == mock_endpoint
    )
    assert (
        ScheduleServiceClient._get_api_endpoint(None, None, default_universe, "never")
        == default_endpoint
    )

    with pytest.raises(MutualTLSChannelError) as excinfo:
        ScheduleServiceClient._get_api_endpoint(
            None, mock_client_cert_source, mock_universe, "auto"
        )
    assert (
        str(excinfo.value)
        == "mTLS is not supported in any universe other than googleapis.com."
    )


def test__get_universe_domain():
    client_universe_domain = "foo.com"
    universe_domain_env = "bar.com"

    assert (
        ScheduleServiceClient._get_universe_domain(
            client_universe_domain, universe_domain_env
        )
        == client_universe_domain
    )
    assert (
        ScheduleServiceClient._get_universe_domain(None, universe_domain_env)
        == universe_domain_env
    )
    assert (
        ScheduleServiceClient._get_universe_domain(None, None)
        == ScheduleServiceClient._DEFAULT_UNIVERSE
    )

    with pytest.raises(ValueError) as excinfo:
        ScheduleServiceClient._get_universe_domain("", None)
    assert str(excinfo.value) == "Universe Domain cannot be an empty string."


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (ScheduleServiceClient, transports.ScheduleServiceGrpcTransport, "grpc"),
        (ScheduleServiceClient, transports.ScheduleServiceRestTransport, "rest"),
    ],
)
def test__validate_universe_domain(client_class, transport_class, transport_name):
    client = client_class(
        transport=transport_class(credentials=ga_credentials.AnonymousCredentials())
    )
    assert client._validate_universe_domain() == True

    # Test the case when universe is already validated.
    assert client._validate_universe_domain() == True

    if transport_name == "grpc":
        # Test the case where credentials are provided by the
        # `local_channel_credentials`. The default universes in both match.
        channel = grpc.secure_channel(
            "http://localhost/", grpc.local_channel_credentials()
        )
        client = client_class(transport=transport_class(channel=channel))
        assert client._validate_universe_domain() == True

        # Test the case where credentials do not exist: e.g. a transport is provided
        # with no credentials. Validation should still succeed because there is no
        # mismatch with non-existent credentials.
        channel = grpc.secure_channel(
            "http://localhost/", grpc.local_channel_credentials()
        )
        transport = transport_class(channel=channel)
        transport._credentials = None
        client = client_class(transport=transport)
        assert client._validate_universe_domain() == True

    # TODO: This is needed to cater for older versions of google-auth
    # Make this test unconditional once the minimum supported version of
    # google-auth becomes 2.23.0 or higher.
    google_auth_major, google_auth_minor = [
        int(part) for part in google.auth.__version__.split(".")[0:2]
    ]
    if google_auth_major > 2 or (google_auth_major == 2 and google_auth_minor >= 23):
        credentials = ga_credentials.AnonymousCredentials()
        credentials._universe_domain = "foo.com"
        # Test the case when there is a universe mismatch from the credentials.
        client = client_class(transport=transport_class(credentials=credentials))
        with pytest.raises(ValueError) as excinfo:
            client._validate_universe_domain()
        assert (
            str(excinfo.value)
            == "The configured universe domain (googleapis.com) does not match the universe domain found in the credentials (foo.com). If you haven't configured the universe domain explicitly, `googleapis.com` is the default."
        )

        # Test the case when there is a universe mismatch from the client.
        #
        # TODO: Make this test unconditional once the minimum supported version of
        # google-api-core becomes 2.15.0 or higher.
        api_core_major, api_core_minor = [
            int(part) for part in api_core_version.__version__.split(".")[0:2]
        ]
        if api_core_major > 2 or (api_core_major == 2 and api_core_minor >= 15):
            client = client_class(
                client_options={"universe_domain": "bar.com"},
                transport=transport_class(
                    credentials=ga_credentials.AnonymousCredentials(),
                ),
            )
            with pytest.raises(ValueError) as excinfo:
                client._validate_universe_domain()
            assert (
                str(excinfo.value)
                == "The configured universe domain (bar.com) does not match the universe domain found in the credentials (googleapis.com). If you haven't configured the universe domain explicitly, `googleapis.com` is the default."
            )

    # Test that ValueError is raised if universe_domain is provided via client options and credentials is None
    with pytest.raises(ValueError):
        client._compare_universes("foo.bar", None)


@pytest.mark.parametrize(
    "client_class,transport_name",
    [
        (ScheduleServiceClient, "grpc"),
        (ScheduleServiceAsyncClient, "grpc_asyncio"),
        (ScheduleServiceClient, "rest"),
    ],
)
def test_schedule_service_client_from_service_account_info(
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

        assert client.transport._host == (
            "aiplatform.googleapis.com:443"
            if transport_name in ["grpc", "grpc_asyncio"]
            else "https://aiplatform.googleapis.com"
        )


@pytest.mark.parametrize(
    "transport_class,transport_name",
    [
        (transports.ScheduleServiceGrpcTransport, "grpc"),
        (transports.ScheduleServiceGrpcAsyncIOTransport, "grpc_asyncio"),
        (transports.ScheduleServiceRestTransport, "rest"),
    ],
)
def test_schedule_service_client_service_account_always_use_jwt(
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
        (ScheduleServiceClient, "grpc"),
        (ScheduleServiceAsyncClient, "grpc_asyncio"),
        (ScheduleServiceClient, "rest"),
    ],
)
def test_schedule_service_client_from_service_account_file(
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

        assert client.transport._host == (
            "aiplatform.googleapis.com:443"
            if transport_name in ["grpc", "grpc_asyncio"]
            else "https://aiplatform.googleapis.com"
        )


def test_schedule_service_client_get_transport_class():
    transport = ScheduleServiceClient.get_transport_class()
    available_transports = [
        transports.ScheduleServiceGrpcTransport,
        transports.ScheduleServiceRestTransport,
    ]
    assert transport in available_transports

    transport = ScheduleServiceClient.get_transport_class("grpc")
    assert transport == transports.ScheduleServiceGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (ScheduleServiceClient, transports.ScheduleServiceGrpcTransport, "grpc"),
        (
            ScheduleServiceAsyncClient,
            transports.ScheduleServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
        (ScheduleServiceClient, transports.ScheduleServiceRestTransport, "rest"),
    ],
)
@mock.patch.object(
    ScheduleServiceClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(ScheduleServiceClient),
)
@mock.patch.object(
    ScheduleServiceAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(ScheduleServiceAsyncClient),
)
def test_schedule_service_client_client_options(
    client_class, transport_class, transport_name
):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(ScheduleServiceClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=ga_credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(ScheduleServiceClient, "get_transport_class") as gtc:
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
                host=client._DEFAULT_ENDPOINT_TEMPLATE.format(
                    UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE
                ),
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
        with pytest.raises(MutualTLSChannelError) as excinfo:
            client = client_class(transport=transport_name)
    assert (
        str(excinfo.value)
        == "Environment variable `GOOGLE_API_USE_MTLS_ENDPOINT` must be `never`, `auto` or `always`"
    )

    # Check the case GOOGLE_API_USE_CLIENT_CERTIFICATE has unsupported value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}
    ):
        with pytest.raises(ValueError) as excinfo:
            client = client_class(transport=transport_name)
    assert (
        str(excinfo.value)
        == "Environment variable `GOOGLE_API_USE_CLIENT_CERTIFICATE` must be either `true` or `false`"
    )

    # Check the case quota_project_id is provided
    options = client_options.ClientOptions(quota_project_id="octopus")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client._DEFAULT_ENDPOINT_TEMPLATE.format(
                UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE
            ),
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
            host=client._DEFAULT_ENDPOINT_TEMPLATE.format(
                UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE
            ),
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
            ScheduleServiceClient,
            transports.ScheduleServiceGrpcTransport,
            "grpc",
            "true",
        ),
        (
            ScheduleServiceAsyncClient,
            transports.ScheduleServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "true",
        ),
        (
            ScheduleServiceClient,
            transports.ScheduleServiceGrpcTransport,
            "grpc",
            "false",
        ),
        (
            ScheduleServiceAsyncClient,
            transports.ScheduleServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "false",
        ),
        (
            ScheduleServiceClient,
            transports.ScheduleServiceRestTransport,
            "rest",
            "true",
        ),
        (
            ScheduleServiceClient,
            transports.ScheduleServiceRestTransport,
            "rest",
            "false",
        ),
    ],
)
@mock.patch.object(
    ScheduleServiceClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(ScheduleServiceClient),
)
@mock.patch.object(
    ScheduleServiceAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(ScheduleServiceAsyncClient),
)
@mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"})
def test_schedule_service_client_mtls_env_auto(
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
                expected_host = client._DEFAULT_ENDPOINT_TEMPLATE.format(
                    UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE
                )
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
                        expected_host = client._DEFAULT_ENDPOINT_TEMPLATE.format(
                            UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE
                        )
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
                    host=client._DEFAULT_ENDPOINT_TEMPLATE.format(
                        UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE
                    ),
                    scopes=None,
                    client_cert_source_for_mtls=None,
                    quota_project_id=None,
                    client_info=transports.base.DEFAULT_CLIENT_INFO,
                    always_use_jwt_access=True,
                    api_audience=None,
                )


@pytest.mark.parametrize(
    "client_class", [ScheduleServiceClient, ScheduleServiceAsyncClient]
)
@mock.patch.object(
    ScheduleServiceClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(ScheduleServiceClient),
)
@mock.patch.object(
    ScheduleServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(ScheduleServiceAsyncClient),
)
def test_schedule_service_client_get_mtls_endpoint_and_cert_source(client_class):
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

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT has
    # unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError) as excinfo:
            client_class.get_mtls_endpoint_and_cert_source()

        assert (
            str(excinfo.value)
            == "Environment variable `GOOGLE_API_USE_MTLS_ENDPOINT` must be `never`, `auto` or `always`"
        )

    # Check the case GOOGLE_API_USE_CLIENT_CERTIFICATE has unsupported value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}
    ):
        with pytest.raises(ValueError) as excinfo:
            client_class.get_mtls_endpoint_and_cert_source()

        assert (
            str(excinfo.value)
            == "Environment variable `GOOGLE_API_USE_CLIENT_CERTIFICATE` must be either `true` or `false`"
        )


@pytest.mark.parametrize(
    "client_class", [ScheduleServiceClient, ScheduleServiceAsyncClient]
)
@mock.patch.object(
    ScheduleServiceClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(ScheduleServiceClient),
)
@mock.patch.object(
    ScheduleServiceAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(ScheduleServiceAsyncClient),
)
def test_schedule_service_client_client_api_endpoint(client_class):
    mock_client_cert_source = client_cert_source_callback
    api_override = "foo.com"
    default_universe = ScheduleServiceClient._DEFAULT_UNIVERSE
    default_endpoint = ScheduleServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(
        UNIVERSE_DOMAIN=default_universe
    )
    mock_universe = "bar.com"
    mock_endpoint = ScheduleServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(
        UNIVERSE_DOMAIN=mock_universe
    )

    # If ClientOptions.api_endpoint is set and GOOGLE_API_USE_CLIENT_CERTIFICATE="true",
    # use ClientOptions.api_endpoint as the api endpoint regardless.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        with mock.patch(
            "google.auth.transport.requests.AuthorizedSession.configure_mtls_channel"
        ):
            options = client_options.ClientOptions(
                client_cert_source=mock_client_cert_source, api_endpoint=api_override
            )
            client = client_class(
                client_options=options,
                credentials=ga_credentials.AnonymousCredentials(),
            )
            assert client.api_endpoint == api_override

    # If ClientOptions.api_endpoint is not set and GOOGLE_API_USE_MTLS_ENDPOINT="never",
    # use the _DEFAULT_ENDPOINT_TEMPLATE populated with GDU as the api endpoint.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        client = client_class(credentials=ga_credentials.AnonymousCredentials())
        assert client.api_endpoint == default_endpoint

    # If ClientOptions.api_endpoint is not set and GOOGLE_API_USE_MTLS_ENDPOINT="always",
    # use the DEFAULT_MTLS_ENDPOINT as the api endpoint.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        client = client_class(credentials=ga_credentials.AnonymousCredentials())
        assert client.api_endpoint == client_class.DEFAULT_MTLS_ENDPOINT

    # If ClientOptions.api_endpoint is not set, GOOGLE_API_USE_MTLS_ENDPOINT="auto" (default),
    # GOOGLE_API_USE_CLIENT_CERTIFICATE="false" (default), default cert source doesn't exist,
    # and ClientOptions.universe_domain="bar.com",
    # use the _DEFAULT_ENDPOINT_TEMPLATE populated with universe domain as the api endpoint.
    options = client_options.ClientOptions()
    universe_exists = hasattr(options, "universe_domain")
    if universe_exists:
        options = client_options.ClientOptions(universe_domain=mock_universe)
        client = client_class(
            client_options=options, credentials=ga_credentials.AnonymousCredentials()
        )
    else:
        client = client_class(
            client_options=options, credentials=ga_credentials.AnonymousCredentials()
        )
    assert client.api_endpoint == (
        mock_endpoint if universe_exists else default_endpoint
    )
    assert client.universe_domain == (
        mock_universe if universe_exists else default_universe
    )

    # If ClientOptions does not have a universe domain attribute and GOOGLE_API_USE_MTLS_ENDPOINT="never",
    # use the _DEFAULT_ENDPOINT_TEMPLATE populated with GDU as the api endpoint.
    options = client_options.ClientOptions()
    if hasattr(options, "universe_domain"):
        delattr(options, "universe_domain")
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        client = client_class(
            client_options=options, credentials=ga_credentials.AnonymousCredentials()
        )
        assert client.api_endpoint == default_endpoint


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (ScheduleServiceClient, transports.ScheduleServiceGrpcTransport, "grpc"),
        (
            ScheduleServiceAsyncClient,
            transports.ScheduleServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
        (ScheduleServiceClient, transports.ScheduleServiceRestTransport, "rest"),
    ],
)
def test_schedule_service_client_client_options_scopes(
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
            host=client._DEFAULT_ENDPOINT_TEMPLATE.format(
                UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE
            ),
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
            ScheduleServiceClient,
            transports.ScheduleServiceGrpcTransport,
            "grpc",
            grpc_helpers,
        ),
        (
            ScheduleServiceAsyncClient,
            transports.ScheduleServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            grpc_helpers_async,
        ),
        (ScheduleServiceClient, transports.ScheduleServiceRestTransport, "rest", None),
    ],
)
def test_schedule_service_client_client_options_credentials_file(
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
            host=client._DEFAULT_ENDPOINT_TEMPLATE.format(
                UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE
            ),
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )


def test_schedule_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.schedule_service.transports.ScheduleServiceGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = ScheduleServiceClient(
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
            ScheduleServiceClient,
            transports.ScheduleServiceGrpcTransport,
            "grpc",
            grpc_helpers,
        ),
        (
            ScheduleServiceAsyncClient,
            transports.ScheduleServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            grpc_helpers_async,
        ),
    ],
)
def test_schedule_service_client_create_channel_credentials_file(
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
            host=client._DEFAULT_ENDPOINT_TEMPLATE.format(
                UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE
            ),
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
        schedule_service.CreateScheduleRequest,
        dict,
    ],
)
def test_create_schedule(request_type, transport: str = "grpc"):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_schedule.Schedule(
            name="name_value",
            display_name="display_name_value",
            max_run_count=1410,
            started_run_count=1843,
            state=gca_schedule.Schedule.State.ACTIVE,
            max_concurrent_run_count=2596,
            allow_queueing=True,
            catch_up=True,
            cron="cron_value",
        )
        response = client.create_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = schedule_service.CreateScheduleRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_schedule.Schedule)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.max_run_count == 1410
    assert response.started_run_count == 1843
    assert response.state == gca_schedule.Schedule.State.ACTIVE
    assert response.max_concurrent_run_count == 2596
    assert response.allow_queueing is True
    assert response.catch_up is True


def test_create_schedule_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_schedule), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.create_schedule()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == schedule_service.CreateScheduleRequest()


def test_create_schedule_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = schedule_service.CreateScheduleRequest(
        parent="parent_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_schedule), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.create_schedule(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == schedule_service.CreateScheduleRequest(
            parent="parent_value",
        )


def test_create_schedule_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = ScheduleServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.create_schedule in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.create_schedule] = mock_rpc
        request = {}
        client.create_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.create_schedule(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_create_schedule_empty_call_async():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_schedule.Schedule(
                name="name_value",
                display_name="display_name_value",
                max_run_count=1410,
                started_run_count=1843,
                state=gca_schedule.Schedule.State.ACTIVE,
                max_concurrent_run_count=2596,
                allow_queueing=True,
                catch_up=True,
            )
        )
        response = await client.create_schedule()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == schedule_service.CreateScheduleRequest()


@pytest.mark.asyncio
async def test_create_schedule_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = ScheduleServiceAsyncClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.create_schedule
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        class AwaitableMock(mock.AsyncMock):
            def __await__(self):
                self.await_count += 1
                return iter([])

        mock_object = AwaitableMock()
        client._client._transport._wrapped_methods[
            client._client._transport.create_schedule
        ] = mock_object

        request = {}
        await client.create_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_object.call_count == 1

        await client.create_schedule(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_object.call_count == 2


@pytest.mark.asyncio
async def test_create_schedule_async(
    transport: str = "grpc_asyncio", request_type=schedule_service.CreateScheduleRequest
):
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_schedule.Schedule(
                name="name_value",
                display_name="display_name_value",
                max_run_count=1410,
                started_run_count=1843,
                state=gca_schedule.Schedule.State.ACTIVE,
                max_concurrent_run_count=2596,
                allow_queueing=True,
                catch_up=True,
            )
        )
        response = await client.create_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = schedule_service.CreateScheduleRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_schedule.Schedule)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.max_run_count == 1410
    assert response.started_run_count == 1843
    assert response.state == gca_schedule.Schedule.State.ACTIVE
    assert response.max_concurrent_run_count == 2596
    assert response.allow_queueing is True
    assert response.catch_up is True


@pytest.mark.asyncio
async def test_create_schedule_async_from_dict():
    await test_create_schedule_async(request_type=dict)


def test_create_schedule_field_headers():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = schedule_service.CreateScheduleRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_schedule), "__call__") as call:
        call.return_value = gca_schedule.Schedule()
        client.create_schedule(request)

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
async def test_create_schedule_field_headers_async():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = schedule_service.CreateScheduleRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_schedule), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_schedule.Schedule()
        )
        await client.create_schedule(request)

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


def test_create_schedule_flattened():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_schedule.Schedule()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_schedule(
            parent="parent_value",
            schedule=gca_schedule.Schedule(cron="cron_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].schedule
        mock_val = gca_schedule.Schedule(cron="cron_value")
        assert arg == mock_val


def test_create_schedule_flattened_error():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_schedule(
            schedule_service.CreateScheduleRequest(),
            parent="parent_value",
            schedule=gca_schedule.Schedule(cron="cron_value"),
        )


@pytest.mark.asyncio
async def test_create_schedule_flattened_async():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_schedule.Schedule()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_schedule.Schedule()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_schedule(
            parent="parent_value",
            schedule=gca_schedule.Schedule(cron="cron_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].schedule
        mock_val = gca_schedule.Schedule(cron="cron_value")
        assert arg == mock_val


@pytest.mark.asyncio
async def test_create_schedule_flattened_error_async():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_schedule(
            schedule_service.CreateScheduleRequest(),
            parent="parent_value",
            schedule=gca_schedule.Schedule(cron="cron_value"),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        schedule_service.DeleteScheduleRequest,
        dict,
    ],
)
def test_delete_schedule(request_type, transport: str = "grpc"):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = schedule_service.DeleteScheduleRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_schedule_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_schedule), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.delete_schedule()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == schedule_service.DeleteScheduleRequest()


def test_delete_schedule_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = schedule_service.DeleteScheduleRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_schedule), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.delete_schedule(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == schedule_service.DeleteScheduleRequest(
            name="name_value",
        )


def test_delete_schedule_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = ScheduleServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.delete_schedule in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.delete_schedule] = mock_rpc
        request = {}
        client.delete_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.delete_schedule(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_delete_schedule_empty_call_async():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_schedule()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == schedule_service.DeleteScheduleRequest()


@pytest.mark.asyncio
async def test_delete_schedule_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = ScheduleServiceAsyncClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.delete_schedule
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        class AwaitableMock(mock.AsyncMock):
            def __await__(self):
                self.await_count += 1
                return iter([])

        mock_object = AwaitableMock()
        client._client._transport._wrapped_methods[
            client._client._transport.delete_schedule
        ] = mock_object

        request = {}
        await client.delete_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_object.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.delete_schedule(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_object.call_count == 2


@pytest.mark.asyncio
async def test_delete_schedule_async(
    transport: str = "grpc_asyncio", request_type=schedule_service.DeleteScheduleRequest
):
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = schedule_service.DeleteScheduleRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_schedule_async_from_dict():
    await test_delete_schedule_async(request_type=dict)


def test_delete_schedule_field_headers():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = schedule_service.DeleteScheduleRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_schedule), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_schedule(request)

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
async def test_delete_schedule_field_headers_async():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = schedule_service.DeleteScheduleRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_schedule), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_schedule(request)

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


def test_delete_schedule_flattened():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_schedule(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_delete_schedule_flattened_error():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_schedule(
            schedule_service.DeleteScheduleRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_schedule_flattened_async():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_schedule(
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
async def test_delete_schedule_flattened_error_async():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_schedule(
            schedule_service.DeleteScheduleRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        schedule_service.GetScheduleRequest,
        dict,
    ],
)
def test_get_schedule(request_type, transport: str = "grpc"):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = schedule.Schedule(
            name="name_value",
            display_name="display_name_value",
            max_run_count=1410,
            started_run_count=1843,
            state=schedule.Schedule.State.ACTIVE,
            max_concurrent_run_count=2596,
            allow_queueing=True,
            catch_up=True,
            cron="cron_value",
        )
        response = client.get_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = schedule_service.GetScheduleRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, schedule.Schedule)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.max_run_count == 1410
    assert response.started_run_count == 1843
    assert response.state == schedule.Schedule.State.ACTIVE
    assert response.max_concurrent_run_count == 2596
    assert response.allow_queueing is True
    assert response.catch_up is True


def test_get_schedule_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_schedule), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.get_schedule()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == schedule_service.GetScheduleRequest()


def test_get_schedule_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = schedule_service.GetScheduleRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_schedule), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.get_schedule(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == schedule_service.GetScheduleRequest(
            name="name_value",
        )


def test_get_schedule_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = ScheduleServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.get_schedule in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.get_schedule] = mock_rpc
        request = {}
        client.get_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_schedule(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_get_schedule_empty_call_async():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            schedule.Schedule(
                name="name_value",
                display_name="display_name_value",
                max_run_count=1410,
                started_run_count=1843,
                state=schedule.Schedule.State.ACTIVE,
                max_concurrent_run_count=2596,
                allow_queueing=True,
                catch_up=True,
            )
        )
        response = await client.get_schedule()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == schedule_service.GetScheduleRequest()


@pytest.mark.asyncio
async def test_get_schedule_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = ScheduleServiceAsyncClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.get_schedule
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        class AwaitableMock(mock.AsyncMock):
            def __await__(self):
                self.await_count += 1
                return iter([])

        mock_object = AwaitableMock()
        client._client._transport._wrapped_methods[
            client._client._transport.get_schedule
        ] = mock_object

        request = {}
        await client.get_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_object.call_count == 1

        await client.get_schedule(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_object.call_count == 2


@pytest.mark.asyncio
async def test_get_schedule_async(
    transport: str = "grpc_asyncio", request_type=schedule_service.GetScheduleRequest
):
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            schedule.Schedule(
                name="name_value",
                display_name="display_name_value",
                max_run_count=1410,
                started_run_count=1843,
                state=schedule.Schedule.State.ACTIVE,
                max_concurrent_run_count=2596,
                allow_queueing=True,
                catch_up=True,
            )
        )
        response = await client.get_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = schedule_service.GetScheduleRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, schedule.Schedule)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.max_run_count == 1410
    assert response.started_run_count == 1843
    assert response.state == schedule.Schedule.State.ACTIVE
    assert response.max_concurrent_run_count == 2596
    assert response.allow_queueing is True
    assert response.catch_up is True


@pytest.mark.asyncio
async def test_get_schedule_async_from_dict():
    await test_get_schedule_async(request_type=dict)


def test_get_schedule_field_headers():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = schedule_service.GetScheduleRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_schedule), "__call__") as call:
        call.return_value = schedule.Schedule()
        client.get_schedule(request)

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
async def test_get_schedule_field_headers_async():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = schedule_service.GetScheduleRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_schedule), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(schedule.Schedule())
        await client.get_schedule(request)

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


def test_get_schedule_flattened():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = schedule.Schedule()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_schedule(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_get_schedule_flattened_error():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_schedule(
            schedule_service.GetScheduleRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_get_schedule_flattened_async():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = schedule.Schedule()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(schedule.Schedule())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_schedule(
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
async def test_get_schedule_flattened_error_async():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_schedule(
            schedule_service.GetScheduleRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        schedule_service.ListSchedulesRequest,
        dict,
    ],
)
def test_list_schedules(request_type, transport: str = "grpc"):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_schedules), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = schedule_service.ListSchedulesResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_schedules(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = schedule_service.ListSchedulesRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListSchedulesPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_schedules_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_schedules), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.list_schedules()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == schedule_service.ListSchedulesRequest()


def test_list_schedules_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = schedule_service.ListSchedulesRequest(
        parent="parent_value",
        filter="filter_value",
        page_token="page_token_value",
        order_by="order_by_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_schedules), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.list_schedules(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == schedule_service.ListSchedulesRequest(
            parent="parent_value",
            filter="filter_value",
            page_token="page_token_value",
            order_by="order_by_value",
        )


def test_list_schedules_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = ScheduleServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.list_schedules in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.list_schedules] = mock_rpc
        request = {}
        client.list_schedules(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_schedules(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_list_schedules_empty_call_async():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_schedules), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            schedule_service.ListSchedulesResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_schedules()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == schedule_service.ListSchedulesRequest()


@pytest.mark.asyncio
async def test_list_schedules_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = ScheduleServiceAsyncClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.list_schedules
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        class AwaitableMock(mock.AsyncMock):
            def __await__(self):
                self.await_count += 1
                return iter([])

        mock_object = AwaitableMock()
        client._client._transport._wrapped_methods[
            client._client._transport.list_schedules
        ] = mock_object

        request = {}
        await client.list_schedules(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_object.call_count == 1

        await client.list_schedules(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_object.call_count == 2


@pytest.mark.asyncio
async def test_list_schedules_async(
    transport: str = "grpc_asyncio", request_type=schedule_service.ListSchedulesRequest
):
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_schedules), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            schedule_service.ListSchedulesResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_schedules(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = schedule_service.ListSchedulesRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListSchedulesAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_schedules_async_from_dict():
    await test_list_schedules_async(request_type=dict)


def test_list_schedules_field_headers():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = schedule_service.ListSchedulesRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_schedules), "__call__") as call:
        call.return_value = schedule_service.ListSchedulesResponse()
        client.list_schedules(request)

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
async def test_list_schedules_field_headers_async():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = schedule_service.ListSchedulesRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_schedules), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            schedule_service.ListSchedulesResponse()
        )
        await client.list_schedules(request)

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


def test_list_schedules_flattened():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_schedules), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = schedule_service.ListSchedulesResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_schedules(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_list_schedules_flattened_error():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_schedules(
            schedule_service.ListSchedulesRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_schedules_flattened_async():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_schedules), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = schedule_service.ListSchedulesResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            schedule_service.ListSchedulesResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_schedules(
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
async def test_list_schedules_flattened_error_async():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_schedules(
            schedule_service.ListSchedulesRequest(),
            parent="parent_value",
        )


def test_list_schedules_pager(transport_name: str = "grpc"):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_schedules), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            schedule_service.ListSchedulesResponse(
                schedules=[
                    schedule.Schedule(),
                    schedule.Schedule(),
                    schedule.Schedule(),
                ],
                next_page_token="abc",
            ),
            schedule_service.ListSchedulesResponse(
                schedules=[],
                next_page_token="def",
            ),
            schedule_service.ListSchedulesResponse(
                schedules=[
                    schedule.Schedule(),
                ],
                next_page_token="ghi",
            ),
            schedule_service.ListSchedulesResponse(
                schedules=[
                    schedule.Schedule(),
                    schedule.Schedule(),
                ],
            ),
            RuntimeError,
        )

        expected_metadata = ()
        expected_metadata = tuple(expected_metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_schedules(request={})

        assert pager._metadata == expected_metadata

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, schedule.Schedule) for i in results)


def test_list_schedules_pages(transport_name: str = "grpc"):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_schedules), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            schedule_service.ListSchedulesResponse(
                schedules=[
                    schedule.Schedule(),
                    schedule.Schedule(),
                    schedule.Schedule(),
                ],
                next_page_token="abc",
            ),
            schedule_service.ListSchedulesResponse(
                schedules=[],
                next_page_token="def",
            ),
            schedule_service.ListSchedulesResponse(
                schedules=[
                    schedule.Schedule(),
                ],
                next_page_token="ghi",
            ),
            schedule_service.ListSchedulesResponse(
                schedules=[
                    schedule.Schedule(),
                    schedule.Schedule(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_schedules(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_schedules_async_pager():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_schedules), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            schedule_service.ListSchedulesResponse(
                schedules=[
                    schedule.Schedule(),
                    schedule.Schedule(),
                    schedule.Schedule(),
                ],
                next_page_token="abc",
            ),
            schedule_service.ListSchedulesResponse(
                schedules=[],
                next_page_token="def",
            ),
            schedule_service.ListSchedulesResponse(
                schedules=[
                    schedule.Schedule(),
                ],
                next_page_token="ghi",
            ),
            schedule_service.ListSchedulesResponse(
                schedules=[
                    schedule.Schedule(),
                    schedule.Schedule(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_schedules(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, schedule.Schedule) for i in responses)


@pytest.mark.asyncio
async def test_list_schedules_async_pages():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_schedules), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            schedule_service.ListSchedulesResponse(
                schedules=[
                    schedule.Schedule(),
                    schedule.Schedule(),
                    schedule.Schedule(),
                ],
                next_page_token="abc",
            ),
            schedule_service.ListSchedulesResponse(
                schedules=[],
                next_page_token="def",
            ),
            schedule_service.ListSchedulesResponse(
                schedules=[
                    schedule.Schedule(),
                ],
                next_page_token="ghi",
            ),
            schedule_service.ListSchedulesResponse(
                schedules=[
                    schedule.Schedule(),
                    schedule.Schedule(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.list_schedules(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        schedule_service.PauseScheduleRequest,
        dict,
    ],
)
def test_pause_schedule(request_type, transport: str = "grpc"):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.pause_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        response = client.pause_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = schedule_service.PauseScheduleRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_pause_schedule_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.pause_schedule), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.pause_schedule()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == schedule_service.PauseScheduleRequest()


def test_pause_schedule_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = schedule_service.PauseScheduleRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.pause_schedule), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.pause_schedule(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == schedule_service.PauseScheduleRequest(
            name="name_value",
        )


def test_pause_schedule_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = ScheduleServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.pause_schedule in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.pause_schedule] = mock_rpc
        request = {}
        client.pause_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.pause_schedule(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_pause_schedule_empty_call_async():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.pause_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.pause_schedule()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == schedule_service.PauseScheduleRequest()


@pytest.mark.asyncio
async def test_pause_schedule_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = ScheduleServiceAsyncClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.pause_schedule
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        class AwaitableMock(mock.AsyncMock):
            def __await__(self):
                self.await_count += 1
                return iter([])

        mock_object = AwaitableMock()
        client._client._transport._wrapped_methods[
            client._client._transport.pause_schedule
        ] = mock_object

        request = {}
        await client.pause_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_object.call_count == 1

        await client.pause_schedule(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_object.call_count == 2


@pytest.mark.asyncio
async def test_pause_schedule_async(
    transport: str = "grpc_asyncio", request_type=schedule_service.PauseScheduleRequest
):
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.pause_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.pause_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = schedule_service.PauseScheduleRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_pause_schedule_async_from_dict():
    await test_pause_schedule_async(request_type=dict)


def test_pause_schedule_field_headers():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = schedule_service.PauseScheduleRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.pause_schedule), "__call__") as call:
        call.return_value = None
        client.pause_schedule(request)

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
async def test_pause_schedule_field_headers_async():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = schedule_service.PauseScheduleRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.pause_schedule), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        await client.pause_schedule(request)

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


def test_pause_schedule_flattened():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.pause_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.pause_schedule(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_pause_schedule_flattened_error():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.pause_schedule(
            schedule_service.PauseScheduleRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_pause_schedule_flattened_async():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.pause_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.pause_schedule(
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
async def test_pause_schedule_flattened_error_async():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.pause_schedule(
            schedule_service.PauseScheduleRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        schedule_service.ResumeScheduleRequest,
        dict,
    ],
)
def test_resume_schedule(request_type, transport: str = "grpc"):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.resume_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        response = client.resume_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = schedule_service.ResumeScheduleRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_resume_schedule_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.resume_schedule), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.resume_schedule()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == schedule_service.ResumeScheduleRequest()


def test_resume_schedule_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = schedule_service.ResumeScheduleRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.resume_schedule), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.resume_schedule(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == schedule_service.ResumeScheduleRequest(
            name="name_value",
        )


def test_resume_schedule_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = ScheduleServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.resume_schedule in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.resume_schedule] = mock_rpc
        request = {}
        client.resume_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.resume_schedule(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_resume_schedule_empty_call_async():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.resume_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.resume_schedule()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == schedule_service.ResumeScheduleRequest()


@pytest.mark.asyncio
async def test_resume_schedule_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = ScheduleServiceAsyncClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.resume_schedule
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        class AwaitableMock(mock.AsyncMock):
            def __await__(self):
                self.await_count += 1
                return iter([])

        mock_object = AwaitableMock()
        client._client._transport._wrapped_methods[
            client._client._transport.resume_schedule
        ] = mock_object

        request = {}
        await client.resume_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_object.call_count == 1

        await client.resume_schedule(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_object.call_count == 2


@pytest.mark.asyncio
async def test_resume_schedule_async(
    transport: str = "grpc_asyncio", request_type=schedule_service.ResumeScheduleRequest
):
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.resume_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.resume_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = schedule_service.ResumeScheduleRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_resume_schedule_async_from_dict():
    await test_resume_schedule_async(request_type=dict)


def test_resume_schedule_field_headers():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = schedule_service.ResumeScheduleRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.resume_schedule), "__call__") as call:
        call.return_value = None
        client.resume_schedule(request)

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
async def test_resume_schedule_field_headers_async():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = schedule_service.ResumeScheduleRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.resume_schedule), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        await client.resume_schedule(request)

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


def test_resume_schedule_flattened():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.resume_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.resume_schedule(
            name="name_value",
            catch_up=True,
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val
        arg = args[0].catch_up
        mock_val = True
        assert arg == mock_val


def test_resume_schedule_flattened_error():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.resume_schedule(
            schedule_service.ResumeScheduleRequest(),
            name="name_value",
            catch_up=True,
        )


@pytest.mark.asyncio
async def test_resume_schedule_flattened_async():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.resume_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.resume_schedule(
            name="name_value",
            catch_up=True,
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val
        arg = args[0].catch_up
        mock_val = True
        assert arg == mock_val


@pytest.mark.asyncio
async def test_resume_schedule_flattened_error_async():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.resume_schedule(
            schedule_service.ResumeScheduleRequest(),
            name="name_value",
            catch_up=True,
        )


@pytest.mark.parametrize(
    "request_type",
    [
        schedule_service.UpdateScheduleRequest,
        dict,
    ],
)
def test_update_schedule(request_type, transport: str = "grpc"):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_schedule.Schedule(
            name="name_value",
            display_name="display_name_value",
            max_run_count=1410,
            started_run_count=1843,
            state=gca_schedule.Schedule.State.ACTIVE,
            max_concurrent_run_count=2596,
            allow_queueing=True,
            catch_up=True,
            cron="cron_value",
        )
        response = client.update_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = schedule_service.UpdateScheduleRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_schedule.Schedule)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.max_run_count == 1410
    assert response.started_run_count == 1843
    assert response.state == gca_schedule.Schedule.State.ACTIVE
    assert response.max_concurrent_run_count == 2596
    assert response.allow_queueing is True
    assert response.catch_up is True


def test_update_schedule_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_schedule), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.update_schedule()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == schedule_service.UpdateScheduleRequest()


def test_update_schedule_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = schedule_service.UpdateScheduleRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_schedule), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.update_schedule(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == schedule_service.UpdateScheduleRequest()


def test_update_schedule_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = ScheduleServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.update_schedule in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.update_schedule] = mock_rpc
        request = {}
        client.update_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.update_schedule(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_update_schedule_empty_call_async():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_schedule.Schedule(
                name="name_value",
                display_name="display_name_value",
                max_run_count=1410,
                started_run_count=1843,
                state=gca_schedule.Schedule.State.ACTIVE,
                max_concurrent_run_count=2596,
                allow_queueing=True,
                catch_up=True,
            )
        )
        response = await client.update_schedule()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == schedule_service.UpdateScheduleRequest()


@pytest.mark.asyncio
async def test_update_schedule_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = ScheduleServiceAsyncClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.update_schedule
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        class AwaitableMock(mock.AsyncMock):
            def __await__(self):
                self.await_count += 1
                return iter([])

        mock_object = AwaitableMock()
        client._client._transport._wrapped_methods[
            client._client._transport.update_schedule
        ] = mock_object

        request = {}
        await client.update_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_object.call_count == 1

        await client.update_schedule(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_object.call_count == 2


@pytest.mark.asyncio
async def test_update_schedule_async(
    transport: str = "grpc_asyncio", request_type=schedule_service.UpdateScheduleRequest
):
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_schedule.Schedule(
                name="name_value",
                display_name="display_name_value",
                max_run_count=1410,
                started_run_count=1843,
                state=gca_schedule.Schedule.State.ACTIVE,
                max_concurrent_run_count=2596,
                allow_queueing=True,
                catch_up=True,
            )
        )
        response = await client.update_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = schedule_service.UpdateScheduleRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_schedule.Schedule)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.max_run_count == 1410
    assert response.started_run_count == 1843
    assert response.state == gca_schedule.Schedule.State.ACTIVE
    assert response.max_concurrent_run_count == 2596
    assert response.allow_queueing is True
    assert response.catch_up is True


@pytest.mark.asyncio
async def test_update_schedule_async_from_dict():
    await test_update_schedule_async(request_type=dict)


def test_update_schedule_field_headers():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = schedule_service.UpdateScheduleRequest()

    request.schedule.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_schedule), "__call__") as call:
        call.return_value = gca_schedule.Schedule()
        client.update_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "schedule.name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_schedule_field_headers_async():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = schedule_service.UpdateScheduleRequest()

    request.schedule.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_schedule), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_schedule.Schedule()
        )
        await client.update_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "schedule.name=name_value",
    ) in kw["metadata"]


def test_update_schedule_flattened():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_schedule.Schedule()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_schedule(
            schedule=gca_schedule.Schedule(cron="cron_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].schedule
        mock_val = gca_schedule.Schedule(cron="cron_value")
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=["paths_value"])
        assert arg == mock_val


def test_update_schedule_flattened_error():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_schedule(
            schedule_service.UpdateScheduleRequest(),
            schedule=gca_schedule.Schedule(cron="cron_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_schedule_flattened_async():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_schedule), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_schedule.Schedule()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_schedule.Schedule()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_schedule(
            schedule=gca_schedule.Schedule(cron="cron_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].schedule
        mock_val = gca_schedule.Schedule(cron="cron_value")
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=["paths_value"])
        assert arg == mock_val


@pytest.mark.asyncio
async def test_update_schedule_flattened_error_async():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_schedule(
            schedule_service.UpdateScheduleRequest(),
            schedule=gca_schedule.Schedule(cron="cron_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        schedule_service.CreateScheduleRequest,
        dict,
    ],
)
def test_create_schedule_rest(request_type):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request_init["schedule"] = {
        "cron": "cron_value",
        "create_pipeline_job_request": {
            "parent": "parent_value",
            "pipeline_job": {
                "name": "name_value",
                "display_name": "display_name_value",
                "create_time": {"seconds": 751, "nanos": 543},
                "start_time": {},
                "end_time": {},
                "update_time": {},
                "pipeline_spec": {"fields": {}},
                "state": 1,
                "job_detail": {
                    "pipeline_context": {
                        "name": "name_value",
                        "display_name": "display_name_value",
                        "etag": "etag_value",
                        "labels": {},
                        "create_time": {},
                        "update_time": {},
                        "parent_contexts": [
                            "parent_contexts_value1",
                            "parent_contexts_value2",
                        ],
                        "schema_title": "schema_title_value",
                        "schema_version": "schema_version_value",
                        "metadata": {},
                        "description": "description_value",
                    },
                    "pipeline_run_context": {},
                    "task_details": [
                        {
                            "task_id": 735,
                            "parent_task_id": 1480,
                            "task_name": "task_name_value",
                            "create_time": {},
                            "start_time": {},
                            "end_time": {},
                            "executor_detail": {
                                "container_detail": {
                                    "main_job": "main_job_value",
                                    "pre_caching_check_job": "pre_caching_check_job_value",
                                    "failed_main_jobs": [
                                        "failed_main_jobs_value1",
                                        "failed_main_jobs_value2",
                                    ],
                                    "failed_pre_caching_check_jobs": [
                                        "failed_pre_caching_check_jobs_value1",
                                        "failed_pre_caching_check_jobs_value2",
                                    ],
                                },
                                "custom_job_detail": {
                                    "job": "job_value",
                                    "failed_jobs": [
                                        "failed_jobs_value1",
                                        "failed_jobs_value2",
                                    ],
                                },
                            },
                            "state": 1,
                            "execution": {
                                "name": "name_value",
                                "display_name": "display_name_value",
                                "state": 1,
                                "etag": "etag_value",
                                "labels": {},
                                "create_time": {},
                                "update_time": {},
                                "schema_title": "schema_title_value",
                                "schema_version": "schema_version_value",
                                "metadata": {},
                                "description": "description_value",
                            },
                            "error": {
                                "code": 411,
                                "message": "message_value",
                                "details": [
                                    {
                                        "type_url": "type.googleapis.com/google.protobuf.Duration",
                                        "value": b"\x08\x0c\x10\xdb\x07",
                                    }
                                ],
                            },
                            "pipeline_task_status": [
                                {"update_time": {}, "state": 1, "error": {}}
                            ],
                            "inputs": {},
                            "outputs": {},
                        }
                    ],
                },
                "error": {},
                "labels": {},
                "runtime_config": {
                    "parameters": {},
                    "gcs_output_directory": "gcs_output_directory_value",
                    "parameter_values": {},
                    "failure_policy": 1,
                    "input_artifacts": {},
                },
                "encryption_spec": {"kms_key_name": "kms_key_name_value"},
                "service_account": "service_account_value",
                "network": "network_value",
                "reserved_ip_ranges": [
                    "reserved_ip_ranges_value1",
                    "reserved_ip_ranges_value2",
                ],
                "template_uri": "template_uri_value",
                "template_metadata": {"version": "version_value"},
                "schedule_name": "schedule_name_value",
                "preflight_validations": True,
            },
            "pipeline_job_id": "pipeline_job_id_value",
        },
        "create_model_monitoring_job_request": {
            "parent": "parent_value",
            "model_monitoring_job": {
                "name": "name_value",
                "display_name": "display_name_value",
                "model_monitoring_spec": {
                    "objective_spec": {
                        "tabular_objective": {
                            "feature_drift_spec": {
                                "features": ["features_value1", "features_value2"],
                                "categorical_metric_type": "categorical_metric_type_value",
                                "numeric_metric_type": "numeric_metric_type_value",
                                "default_categorical_alert_condition": {
                                    "threshold": 0.973
                                },
                                "default_numeric_alert_condition": {},
                                "feature_alert_conditions": {},
                            },
                            "prediction_output_drift_spec": {},
                            "feature_attribution_spec": {
                                "features": ["features_value1", "features_value2"],
                                "default_alert_condition": {},
                                "feature_alert_conditions": {},
                                "batch_explanation_dedicated_resources": {
                                    "machine_spec": {
                                        "machine_type": "machine_type_value",
                                        "accelerator_type": 1,
                                        "accelerator_count": 1805,
                                        "tpu_topology": "tpu_topology_value",
                                    },
                                    "starting_replica_count": 2355,
                                    "max_replica_count": 1805,
                                },
                            },
                        },
                        "explanation_spec": {
                            "parameters": {
                                "sampled_shapley_attribution": {"path_count": 1077},
                                "integrated_gradients_attribution": {
                                    "step_count": 1092,
                                    "smooth_grad_config": {
                                        "noise_sigma": 0.11660000000000001,
                                        "feature_noise_sigma": {
                                            "noise_sigma": [
                                                {"name": "name_value", "sigma": 0.529}
                                            ]
                                        },
                                        "noisy_sample_count": 1947,
                                    },
                                    "blur_baseline_config": {"max_blur_sigma": 0.1482},
                                },
                                "xrai_attribution": {
                                    "step_count": 1092,
                                    "smooth_grad_config": {},
                                    "blur_baseline_config": {},
                                },
                                "examples": {
                                    "example_gcs_source": {
                                        "data_format": 1,
                                        "gcs_source": {
                                            "uris": ["uris_value1", "uris_value2"]
                                        },
                                    },
                                    "nearest_neighbor_search_config": {
                                        "null_value": 0,
                                        "number_value": 0.1285,
                                        "string_value": "string_value_value",
                                        "bool_value": True,
                                        "struct_value": {},
                                        "list_value": {"values": {}},
                                    },
                                    "presets": {"query": 1, "modality": 1},
                                    "gcs_source": {},
                                    "neighbor_count": 1494,
                                },
                                "top_k": 541,
                                "output_indices": {},
                            },
                            "metadata": {
                                "inputs": {},
                                "outputs": {},
                                "feature_attributions_schema_uri": "feature_attributions_schema_uri_value",
                                "latent_space_source": "latent_space_source_value",
                            },
                        },
                        "baseline_dataset": {
                            "columnized_dataset": {
                                "vertex_dataset": "vertex_dataset_value",
                                "gcs_source": {
                                    "gcs_uri": "gcs_uri_value",
                                    "format_": 1,
                                },
                                "bigquery_source": {
                                    "table_uri": "table_uri_value",
                                    "query": "query_value",
                                },
                                "timestamp_field": "timestamp_field_value",
                            },
                            "batch_prediction_output": {
                                "batch_prediction_job": "batch_prediction_job_value"
                            },
                            "vertex_endpoint_logs": {
                                "endpoints": ["endpoints_value1", "endpoints_value2"]
                            },
                            "time_interval": {"start_time": {}, "end_time": {}},
                            "time_offset": {
                                "offset": "offset_value",
                                "window": "window_value",
                            },
                        },
                        "target_dataset": {},
                    },
                    "notification_spec": {
                        "email_config": {
                            "user_emails": ["user_emails_value1", "user_emails_value2"]
                        },
                        "enable_cloud_logging": True,
                        "notification_channel_configs": [
                            {"notification_channel": "notification_channel_value"}
                        ],
                    },
                    "output_spec": {
                        "gcs_base_directory": {
                            "output_uri_prefix": "output_uri_prefix_value"
                        }
                    },
                },
                "create_time": {},
                "update_time": {},
                "state": 1,
                "schedule": "schedule_value",
                "job_execution_detail": {
                    "baseline_datasets": [
                        {"location": "location_value", "time_range": {}}
                    ],
                    "target_datasets": {},
                    "objective_status": {},
                    "error": {},
                },
                "schedule_time": {},
            },
            "model_monitoring_job_id": "model_monitoring_job_id_value",
        },
        "create_notebook_execution_job_request": {
            "parent": "parent_value",
            "notebook_execution_job": {
                "dataform_repository_source": {
                    "dataform_repository_resource_name": "dataform_repository_resource_name_value",
                    "commit_sha": "commit_sha_value",
                },
                "gcs_notebook_source": {
                    "uri": "uri_value",
                    "generation": "generation_value",
                },
                "direct_notebook_source": {"content": b"content_blob"},
                "notebook_runtime_template_resource_name": "notebook_runtime_template_resource_name_value",
                "gcs_output_uri": "gcs_output_uri_value",
                "execution_user": "execution_user_value",
                "service_account": "service_account_value",
                "name": "name_value",
                "display_name": "display_name_value",
                "execution_timeout": {"seconds": 751, "nanos": 543},
                "schedule_resource_name": "schedule_resource_name_value",
                "job_state": 1,
                "status": {},
                "create_time": {},
                "update_time": {},
                "labels": {},
            },
            "notebook_execution_job_id": "notebook_execution_job_id_value",
        },
        "name": "name_value",
        "display_name": "display_name_value",
        "start_time": {},
        "end_time": {},
        "max_run_count": 1410,
        "started_run_count": 1843,
        "state": 1,
        "create_time": {},
        "update_time": {},
        "next_run_time": {},
        "last_pause_time": {},
        "last_resume_time": {},
        "max_concurrent_run_count": 2596,
        "allow_queueing": True,
        "catch_up": True,
        "last_scheduled_run_response": {
            "scheduled_run_time": {},
            "run_response": "run_response_value",
        },
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = schedule_service.CreateScheduleRequest.meta.fields["schedule"]

    def get_message_fields(field):
        # Given a field which is a message (composite type), return a list with
        # all the fields of the message.
        # If the field is not a composite type, return an empty list.
        message_fields = []

        if hasattr(field, "message") and field.message:
            is_field_type_proto_plus_type = not hasattr(field.message, "DESCRIPTOR")

            if is_field_type_proto_plus_type:
                message_fields = field.message.meta.fields.values()
            # Add `# pragma: NO COVER` because there may not be any `*_pb2` field types
            else:  # pragma: NO COVER
                message_fields = field.message.DESCRIPTOR.fields
        return message_fields

    runtime_nested_fields = [
        (field.name, nested_field.name)
        for field in get_message_fields(test_field)
        for nested_field in get_message_fields(field)
    ]

    subfields_not_in_runtime = []

    # For each item in the sample request, create a list of sub fields which are not present at runtime
    # Add `# pragma: NO COVER` because this test code will not run if all subfields are present at runtime
    for field, value in request_init["schedule"].items():  # pragma: NO COVER
        result = None
        is_repeated = False
        # For repeated fields
        if isinstance(value, list) and len(value):
            is_repeated = True
            result = value[0]
        # For fields where the type is another message
        if isinstance(value, dict):
            result = value

        if result and hasattr(result, "keys"):
            for subfield in result.keys():
                if (field, subfield) not in runtime_nested_fields:
                    subfields_not_in_runtime.append(
                        {
                            "field": field,
                            "subfield": subfield,
                            "is_repeated": is_repeated,
                        }
                    )

    # Remove fields from the sample request which are not present in the runtime version of the dependency
    # Add `# pragma: NO COVER` because this test code will not run if all subfields are present at runtime
    for subfield_to_delete in subfields_not_in_runtime:  # pragma: NO COVER
        field = subfield_to_delete.get("field")
        field_repeated = subfield_to_delete.get("is_repeated")
        subfield = subfield_to_delete.get("subfield")
        if subfield:
            if field_repeated:
                for i in range(0, len(request_init["schedule"][field])):
                    del request_init["schedule"][field][i][subfield]
            else:
                del request_init["schedule"][field][subfield]
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gca_schedule.Schedule(
            name="name_value",
            display_name="display_name_value",
            max_run_count=1410,
            started_run_count=1843,
            state=gca_schedule.Schedule.State.ACTIVE,
            max_concurrent_run_count=2596,
            allow_queueing=True,
            catch_up=True,
            cron="cron_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = gca_schedule.Schedule.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.create_schedule(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_schedule.Schedule)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.max_run_count == 1410
    assert response.started_run_count == 1843
    assert response.state == gca_schedule.Schedule.State.ACTIVE
    assert response.max_concurrent_run_count == 2596
    assert response.allow_queueing is True
    assert response.catch_up is True


def test_create_schedule_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = ScheduleServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.create_schedule in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.create_schedule] = mock_rpc

        request = {}
        client.create_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.create_schedule(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_create_schedule_rest_required_fields(
    request_type=schedule_service.CreateScheduleRequest,
):
    transport_class = transports.ScheduleServiceRestTransport

    request_init = {}
    request_init["parent"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(pb_request, use_integers_for_enums=False)
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).create_schedule._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).create_schedule._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = gca_schedule.Schedule()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            # Convert return value to protobuf type
            return_value = gca_schedule.Schedule.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.create_schedule(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_create_schedule_rest_unset_required_fields():
    transport = transports.ScheduleServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.create_schedule._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(())
        & set(
            (
                "parent",
                "schedule",
            )
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_create_schedule_rest_interceptors(null_interceptor):
    transport = transports.ScheduleServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.ScheduleServiceRestInterceptor(),
    )
    client = ScheduleServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.ScheduleServiceRestInterceptor, "post_create_schedule"
    ) as post, mock.patch.object(
        transports.ScheduleServiceRestInterceptor, "pre_create_schedule"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = schedule_service.CreateScheduleRequest.pb(
            schedule_service.CreateScheduleRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = gca_schedule.Schedule.to_json(
            gca_schedule.Schedule()
        )

        request = schedule_service.CreateScheduleRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = gca_schedule.Schedule()

        client.create_schedule(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_create_schedule_rest_bad_request(
    transport: str = "rest", request_type=schedule_service.CreateScheduleRequest
):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.create_schedule(request)


def test_create_schedule_rest_flattened():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gca_schedule.Schedule()

        # get arguments that satisfy an http rule for this method
        sample_request = {"parent": "projects/sample1/locations/sample2"}

        # get truthy value for each flattened field
        mock_args = dict(
            parent="parent_value",
            schedule=gca_schedule.Schedule(cron="cron_value"),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = gca_schedule.Schedule.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.create_schedule(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{parent=projects/*/locations/*}/schedules"
            % client.transport._host,
            args[1],
        )


def test_create_schedule_rest_flattened_error(transport: str = "rest"):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_schedule(
            schedule_service.CreateScheduleRequest(),
            parent="parent_value",
            schedule=gca_schedule.Schedule(cron="cron_value"),
        )


def test_create_schedule_rest_error():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        schedule_service.DeleteScheduleRequest,
        dict,
    ],
)
def test_delete_schedule_rest(request_type):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/schedules/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.delete_schedule(request)

    # Establish that the response is the type that we expect.
    assert response.operation.name == "operations/spam"


def test_delete_schedule_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = ScheduleServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.delete_schedule in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.delete_schedule] = mock_rpc

        request = {}
        client.delete_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.delete_schedule(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_delete_schedule_rest_required_fields(
    request_type=schedule_service.DeleteScheduleRequest,
):
    transport_class = transports.ScheduleServiceRestTransport

    request_init = {}
    request_init["name"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(pb_request, use_integers_for_enums=False)
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).delete_schedule._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).delete_schedule._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = operations_pb2.Operation(name="operations/spam")
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "delete",
                "query_params": pb_request,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.delete_schedule(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_delete_schedule_rest_unset_required_fields():
    transport = transports.ScheduleServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.delete_schedule._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_delete_schedule_rest_interceptors(null_interceptor):
    transport = transports.ScheduleServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.ScheduleServiceRestInterceptor(),
    )
    client = ScheduleServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.ScheduleServiceRestInterceptor, "post_delete_schedule"
    ) as post, mock.patch.object(
        transports.ScheduleServiceRestInterceptor, "pre_delete_schedule"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = schedule_service.DeleteScheduleRequest.pb(
            schedule_service.DeleteScheduleRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = json_format.MessageToJson(
            operations_pb2.Operation()
        )

        request = schedule_service.DeleteScheduleRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()

        client.delete_schedule(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_delete_schedule_rest_bad_request(
    transport: str = "rest", request_type=schedule_service.DeleteScheduleRequest
):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/schedules/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.delete_schedule(request)


def test_delete_schedule_rest_flattened():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/schedules/sample3"
        }

        # get truthy value for each flattened field
        mock_args = dict(
            name="name_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.delete_schedule(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/schedules/*}"
            % client.transport._host,
            args[1],
        )


def test_delete_schedule_rest_flattened_error(transport: str = "rest"):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_schedule(
            schedule_service.DeleteScheduleRequest(),
            name="name_value",
        )


def test_delete_schedule_rest_error():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        schedule_service.GetScheduleRequest,
        dict,
    ],
)
def test_get_schedule_rest(request_type):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/schedules/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = schedule.Schedule(
            name="name_value",
            display_name="display_name_value",
            max_run_count=1410,
            started_run_count=1843,
            state=schedule.Schedule.State.ACTIVE,
            max_concurrent_run_count=2596,
            allow_queueing=True,
            catch_up=True,
            cron="cron_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = schedule.Schedule.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.get_schedule(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, schedule.Schedule)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.max_run_count == 1410
    assert response.started_run_count == 1843
    assert response.state == schedule.Schedule.State.ACTIVE
    assert response.max_concurrent_run_count == 2596
    assert response.allow_queueing is True
    assert response.catch_up is True


def test_get_schedule_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = ScheduleServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.get_schedule in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.get_schedule] = mock_rpc

        request = {}
        client.get_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_schedule(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_get_schedule_rest_required_fields(
    request_type=schedule_service.GetScheduleRequest,
):
    transport_class = transports.ScheduleServiceRestTransport

    request_init = {}
    request_init["name"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(pb_request, use_integers_for_enums=False)
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_schedule._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_schedule._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = schedule.Schedule()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "get",
                "query_params": pb_request,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            # Convert return value to protobuf type
            return_value = schedule.Schedule.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.get_schedule(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_schedule_rest_unset_required_fields():
    transport = transports.ScheduleServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_schedule._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_schedule_rest_interceptors(null_interceptor):
    transport = transports.ScheduleServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.ScheduleServiceRestInterceptor(),
    )
    client = ScheduleServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.ScheduleServiceRestInterceptor, "post_get_schedule"
    ) as post, mock.patch.object(
        transports.ScheduleServiceRestInterceptor, "pre_get_schedule"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = schedule_service.GetScheduleRequest.pb(
            schedule_service.GetScheduleRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = schedule.Schedule.to_json(schedule.Schedule())

        request = schedule_service.GetScheduleRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = schedule.Schedule()

        client.get_schedule(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_get_schedule_rest_bad_request(
    transport: str = "rest", request_type=schedule_service.GetScheduleRequest
):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/schedules/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.get_schedule(request)


def test_get_schedule_rest_flattened():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = schedule.Schedule()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/schedules/sample3"
        }

        # get truthy value for each flattened field
        mock_args = dict(
            name="name_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = schedule.Schedule.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.get_schedule(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/schedules/*}"
            % client.transport._host,
            args[1],
        )


def test_get_schedule_rest_flattened_error(transport: str = "rest"):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_schedule(
            schedule_service.GetScheduleRequest(),
            name="name_value",
        )


def test_get_schedule_rest_error():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        schedule_service.ListSchedulesRequest,
        dict,
    ],
)
def test_list_schedules_rest(request_type):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = schedule_service.ListSchedulesResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = schedule_service.ListSchedulesResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.list_schedules(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListSchedulesPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_schedules_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = ScheduleServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.list_schedules in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.list_schedules] = mock_rpc

        request = {}
        client.list_schedules(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_schedules(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_list_schedules_rest_required_fields(
    request_type=schedule_service.ListSchedulesRequest,
):
    transport_class = transports.ScheduleServiceRestTransport

    request_init = {}
    request_init["parent"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(pb_request, use_integers_for_enums=False)
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_schedules._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_schedules._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(
        (
            "filter",
            "order_by",
            "page_size",
            "page_token",
        )
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = schedule_service.ListSchedulesResponse()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "get",
                "query_params": pb_request,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            # Convert return value to protobuf type
            return_value = schedule_service.ListSchedulesResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.list_schedules(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_list_schedules_rest_unset_required_fields():
    transport = transports.ScheduleServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.list_schedules._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(
            (
                "filter",
                "orderBy",
                "pageSize",
                "pageToken",
            )
        )
        & set(("parent",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_schedules_rest_interceptors(null_interceptor):
    transport = transports.ScheduleServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.ScheduleServiceRestInterceptor(),
    )
    client = ScheduleServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.ScheduleServiceRestInterceptor, "post_list_schedules"
    ) as post, mock.patch.object(
        transports.ScheduleServiceRestInterceptor, "pre_list_schedules"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = schedule_service.ListSchedulesRequest.pb(
            schedule_service.ListSchedulesRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = schedule_service.ListSchedulesResponse.to_json(
            schedule_service.ListSchedulesResponse()
        )

        request = schedule_service.ListSchedulesRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = schedule_service.ListSchedulesResponse()

        client.list_schedules(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_list_schedules_rest_bad_request(
    transport: str = "rest", request_type=schedule_service.ListSchedulesRequest
):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.list_schedules(request)


def test_list_schedules_rest_flattened():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = schedule_service.ListSchedulesResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {"parent": "projects/sample1/locations/sample2"}

        # get truthy value for each flattened field
        mock_args = dict(
            parent="parent_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = schedule_service.ListSchedulesResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.list_schedules(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{parent=projects/*/locations/*}/schedules"
            % client.transport._host,
            args[1],
        )


def test_list_schedules_rest_flattened_error(transport: str = "rest"):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_schedules(
            schedule_service.ListSchedulesRequest(),
            parent="parent_value",
        )


def test_list_schedules_rest_pager(transport: str = "rest"):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            schedule_service.ListSchedulesResponse(
                schedules=[
                    schedule.Schedule(),
                    schedule.Schedule(),
                    schedule.Schedule(),
                ],
                next_page_token="abc",
            ),
            schedule_service.ListSchedulesResponse(
                schedules=[],
                next_page_token="def",
            ),
            schedule_service.ListSchedulesResponse(
                schedules=[
                    schedule.Schedule(),
                ],
                next_page_token="ghi",
            ),
            schedule_service.ListSchedulesResponse(
                schedules=[
                    schedule.Schedule(),
                    schedule.Schedule(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(
            schedule_service.ListSchedulesResponse.to_json(x) for x in response
        )
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {"parent": "projects/sample1/locations/sample2"}

        pager = client.list_schedules(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, schedule.Schedule) for i in results)

        pages = list(client.list_schedules(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        schedule_service.PauseScheduleRequest,
        dict,
    ],
)
def test_pause_schedule_rest(request_type):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/schedules/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = ""

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.pause_schedule(request)

    # Establish that the response is the type that we expect.
    assert response is None


def test_pause_schedule_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = ScheduleServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.pause_schedule in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.pause_schedule] = mock_rpc

        request = {}
        client.pause_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.pause_schedule(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_pause_schedule_rest_required_fields(
    request_type=schedule_service.PauseScheduleRequest,
):
    transport_class = transports.ScheduleServiceRestTransport

    request_init = {}
    request_init["name"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(pb_request, use_integers_for_enums=False)
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).pause_schedule._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).pause_schedule._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = None
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = ""

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.pause_schedule(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_pause_schedule_rest_unset_required_fields():
    transport = transports.ScheduleServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.pause_schedule._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_pause_schedule_rest_interceptors(null_interceptor):
    transport = transports.ScheduleServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.ScheduleServiceRestInterceptor(),
    )
    client = ScheduleServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.ScheduleServiceRestInterceptor, "pre_pause_schedule"
    ) as pre:
        pre.assert_not_called()
        pb_message = schedule_service.PauseScheduleRequest.pb(
            schedule_service.PauseScheduleRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()

        request = schedule_service.PauseScheduleRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata

        client.pause_schedule(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()


def test_pause_schedule_rest_bad_request(
    transport: str = "rest", request_type=schedule_service.PauseScheduleRequest
):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/schedules/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.pause_schedule(request)


def test_pause_schedule_rest_flattened():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/schedules/sample3"
        }

        # get truthy value for each flattened field
        mock_args = dict(
            name="name_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = ""
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.pause_schedule(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/schedules/*}:pause"
            % client.transport._host,
            args[1],
        )


def test_pause_schedule_rest_flattened_error(transport: str = "rest"):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.pause_schedule(
            schedule_service.PauseScheduleRequest(),
            name="name_value",
        )


def test_pause_schedule_rest_error():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        schedule_service.ResumeScheduleRequest,
        dict,
    ],
)
def test_resume_schedule_rest(request_type):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/schedules/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = ""

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.resume_schedule(request)

    # Establish that the response is the type that we expect.
    assert response is None


def test_resume_schedule_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = ScheduleServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.resume_schedule in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.resume_schedule] = mock_rpc

        request = {}
        client.resume_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.resume_schedule(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_resume_schedule_rest_required_fields(
    request_type=schedule_service.ResumeScheduleRequest,
):
    transport_class = transports.ScheduleServiceRestTransport

    request_init = {}
    request_init["name"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(pb_request, use_integers_for_enums=False)
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).resume_schedule._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).resume_schedule._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = None
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = ""

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.resume_schedule(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_resume_schedule_rest_unset_required_fields():
    transport = transports.ScheduleServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.resume_schedule._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_resume_schedule_rest_interceptors(null_interceptor):
    transport = transports.ScheduleServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.ScheduleServiceRestInterceptor(),
    )
    client = ScheduleServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.ScheduleServiceRestInterceptor, "pre_resume_schedule"
    ) as pre:
        pre.assert_not_called()
        pb_message = schedule_service.ResumeScheduleRequest.pb(
            schedule_service.ResumeScheduleRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()

        request = schedule_service.ResumeScheduleRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata

        client.resume_schedule(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()


def test_resume_schedule_rest_bad_request(
    transport: str = "rest", request_type=schedule_service.ResumeScheduleRequest
):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/schedules/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.resume_schedule(request)


def test_resume_schedule_rest_flattened():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/schedules/sample3"
        }

        # get truthy value for each flattened field
        mock_args = dict(
            name="name_value",
            catch_up=True,
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = ""
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.resume_schedule(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/schedules/*}:resume"
            % client.transport._host,
            args[1],
        )


def test_resume_schedule_rest_flattened_error(transport: str = "rest"):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.resume_schedule(
            schedule_service.ResumeScheduleRequest(),
            name="name_value",
            catch_up=True,
        )


def test_resume_schedule_rest_error():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        schedule_service.UpdateScheduleRequest,
        dict,
    ],
)
def test_update_schedule_rest(request_type):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {
        "schedule": {"name": "projects/sample1/locations/sample2/schedules/sample3"}
    }
    request_init["schedule"] = {
        "cron": "cron_value",
        "create_pipeline_job_request": {
            "parent": "parent_value",
            "pipeline_job": {
                "name": "name_value",
                "display_name": "display_name_value",
                "create_time": {"seconds": 751, "nanos": 543},
                "start_time": {},
                "end_time": {},
                "update_time": {},
                "pipeline_spec": {"fields": {}},
                "state": 1,
                "job_detail": {
                    "pipeline_context": {
                        "name": "name_value",
                        "display_name": "display_name_value",
                        "etag": "etag_value",
                        "labels": {},
                        "create_time": {},
                        "update_time": {},
                        "parent_contexts": [
                            "parent_contexts_value1",
                            "parent_contexts_value2",
                        ],
                        "schema_title": "schema_title_value",
                        "schema_version": "schema_version_value",
                        "metadata": {},
                        "description": "description_value",
                    },
                    "pipeline_run_context": {},
                    "task_details": [
                        {
                            "task_id": 735,
                            "parent_task_id": 1480,
                            "task_name": "task_name_value",
                            "create_time": {},
                            "start_time": {},
                            "end_time": {},
                            "executor_detail": {
                                "container_detail": {
                                    "main_job": "main_job_value",
                                    "pre_caching_check_job": "pre_caching_check_job_value",
                                    "failed_main_jobs": [
                                        "failed_main_jobs_value1",
                                        "failed_main_jobs_value2",
                                    ],
                                    "failed_pre_caching_check_jobs": [
                                        "failed_pre_caching_check_jobs_value1",
                                        "failed_pre_caching_check_jobs_value2",
                                    ],
                                },
                                "custom_job_detail": {
                                    "job": "job_value",
                                    "failed_jobs": [
                                        "failed_jobs_value1",
                                        "failed_jobs_value2",
                                    ],
                                },
                            },
                            "state": 1,
                            "execution": {
                                "name": "name_value",
                                "display_name": "display_name_value",
                                "state": 1,
                                "etag": "etag_value",
                                "labels": {},
                                "create_time": {},
                                "update_time": {},
                                "schema_title": "schema_title_value",
                                "schema_version": "schema_version_value",
                                "metadata": {},
                                "description": "description_value",
                            },
                            "error": {
                                "code": 411,
                                "message": "message_value",
                                "details": [
                                    {
                                        "type_url": "type.googleapis.com/google.protobuf.Duration",
                                        "value": b"\x08\x0c\x10\xdb\x07",
                                    }
                                ],
                            },
                            "pipeline_task_status": [
                                {"update_time": {}, "state": 1, "error": {}}
                            ],
                            "inputs": {},
                            "outputs": {},
                        }
                    ],
                },
                "error": {},
                "labels": {},
                "runtime_config": {
                    "parameters": {},
                    "gcs_output_directory": "gcs_output_directory_value",
                    "parameter_values": {},
                    "failure_policy": 1,
                    "input_artifacts": {},
                },
                "encryption_spec": {"kms_key_name": "kms_key_name_value"},
                "service_account": "service_account_value",
                "network": "network_value",
                "reserved_ip_ranges": [
                    "reserved_ip_ranges_value1",
                    "reserved_ip_ranges_value2",
                ],
                "template_uri": "template_uri_value",
                "template_metadata": {"version": "version_value"},
                "schedule_name": "schedule_name_value",
                "preflight_validations": True,
            },
            "pipeline_job_id": "pipeline_job_id_value",
        },
        "create_model_monitoring_job_request": {
            "parent": "parent_value",
            "model_monitoring_job": {
                "name": "name_value",
                "display_name": "display_name_value",
                "model_monitoring_spec": {
                    "objective_spec": {
                        "tabular_objective": {
                            "feature_drift_spec": {
                                "features": ["features_value1", "features_value2"],
                                "categorical_metric_type": "categorical_metric_type_value",
                                "numeric_metric_type": "numeric_metric_type_value",
                                "default_categorical_alert_condition": {
                                    "threshold": 0.973
                                },
                                "default_numeric_alert_condition": {},
                                "feature_alert_conditions": {},
                            },
                            "prediction_output_drift_spec": {},
                            "feature_attribution_spec": {
                                "features": ["features_value1", "features_value2"],
                                "default_alert_condition": {},
                                "feature_alert_conditions": {},
                                "batch_explanation_dedicated_resources": {
                                    "machine_spec": {
                                        "machine_type": "machine_type_value",
                                        "accelerator_type": 1,
                                        "accelerator_count": 1805,
                                        "tpu_topology": "tpu_topology_value",
                                    },
                                    "starting_replica_count": 2355,
                                    "max_replica_count": 1805,
                                },
                            },
                        },
                        "explanation_spec": {
                            "parameters": {
                                "sampled_shapley_attribution": {"path_count": 1077},
                                "integrated_gradients_attribution": {
                                    "step_count": 1092,
                                    "smooth_grad_config": {
                                        "noise_sigma": 0.11660000000000001,
                                        "feature_noise_sigma": {
                                            "noise_sigma": [
                                                {"name": "name_value", "sigma": 0.529}
                                            ]
                                        },
                                        "noisy_sample_count": 1947,
                                    },
                                    "blur_baseline_config": {"max_blur_sigma": 0.1482},
                                },
                                "xrai_attribution": {
                                    "step_count": 1092,
                                    "smooth_grad_config": {},
                                    "blur_baseline_config": {},
                                },
                                "examples": {
                                    "example_gcs_source": {
                                        "data_format": 1,
                                        "gcs_source": {
                                            "uris": ["uris_value1", "uris_value2"]
                                        },
                                    },
                                    "nearest_neighbor_search_config": {
                                        "null_value": 0,
                                        "number_value": 0.1285,
                                        "string_value": "string_value_value",
                                        "bool_value": True,
                                        "struct_value": {},
                                        "list_value": {"values": {}},
                                    },
                                    "presets": {"query": 1, "modality": 1},
                                    "gcs_source": {},
                                    "neighbor_count": 1494,
                                },
                                "top_k": 541,
                                "output_indices": {},
                            },
                            "metadata": {
                                "inputs": {},
                                "outputs": {},
                                "feature_attributions_schema_uri": "feature_attributions_schema_uri_value",
                                "latent_space_source": "latent_space_source_value",
                            },
                        },
                        "baseline_dataset": {
                            "columnized_dataset": {
                                "vertex_dataset": "vertex_dataset_value",
                                "gcs_source": {
                                    "gcs_uri": "gcs_uri_value",
                                    "format_": 1,
                                },
                                "bigquery_source": {
                                    "table_uri": "table_uri_value",
                                    "query": "query_value",
                                },
                                "timestamp_field": "timestamp_field_value",
                            },
                            "batch_prediction_output": {
                                "batch_prediction_job": "batch_prediction_job_value"
                            },
                            "vertex_endpoint_logs": {
                                "endpoints": ["endpoints_value1", "endpoints_value2"]
                            },
                            "time_interval": {"start_time": {}, "end_time": {}},
                            "time_offset": {
                                "offset": "offset_value",
                                "window": "window_value",
                            },
                        },
                        "target_dataset": {},
                    },
                    "notification_spec": {
                        "email_config": {
                            "user_emails": ["user_emails_value1", "user_emails_value2"]
                        },
                        "enable_cloud_logging": True,
                        "notification_channel_configs": [
                            {"notification_channel": "notification_channel_value"}
                        ],
                    },
                    "output_spec": {
                        "gcs_base_directory": {
                            "output_uri_prefix": "output_uri_prefix_value"
                        }
                    },
                },
                "create_time": {},
                "update_time": {},
                "state": 1,
                "schedule": "schedule_value",
                "job_execution_detail": {
                    "baseline_datasets": [
                        {"location": "location_value", "time_range": {}}
                    ],
                    "target_datasets": {},
                    "objective_status": {},
                    "error": {},
                },
                "schedule_time": {},
            },
            "model_monitoring_job_id": "model_monitoring_job_id_value",
        },
        "create_notebook_execution_job_request": {
            "parent": "parent_value",
            "notebook_execution_job": {
                "dataform_repository_source": {
                    "dataform_repository_resource_name": "dataform_repository_resource_name_value",
                    "commit_sha": "commit_sha_value",
                },
                "gcs_notebook_source": {
                    "uri": "uri_value",
                    "generation": "generation_value",
                },
                "direct_notebook_source": {"content": b"content_blob"},
                "notebook_runtime_template_resource_name": "notebook_runtime_template_resource_name_value",
                "gcs_output_uri": "gcs_output_uri_value",
                "execution_user": "execution_user_value",
                "service_account": "service_account_value",
                "name": "name_value",
                "display_name": "display_name_value",
                "execution_timeout": {"seconds": 751, "nanos": 543},
                "schedule_resource_name": "schedule_resource_name_value",
                "job_state": 1,
                "status": {},
                "create_time": {},
                "update_time": {},
                "labels": {},
            },
            "notebook_execution_job_id": "notebook_execution_job_id_value",
        },
        "name": "projects/sample1/locations/sample2/schedules/sample3",
        "display_name": "display_name_value",
        "start_time": {},
        "end_time": {},
        "max_run_count": 1410,
        "started_run_count": 1843,
        "state": 1,
        "create_time": {},
        "update_time": {},
        "next_run_time": {},
        "last_pause_time": {},
        "last_resume_time": {},
        "max_concurrent_run_count": 2596,
        "allow_queueing": True,
        "catch_up": True,
        "last_scheduled_run_response": {
            "scheduled_run_time": {},
            "run_response": "run_response_value",
        },
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = schedule_service.UpdateScheduleRequest.meta.fields["schedule"]

    def get_message_fields(field):
        # Given a field which is a message (composite type), return a list with
        # all the fields of the message.
        # If the field is not a composite type, return an empty list.
        message_fields = []

        if hasattr(field, "message") and field.message:
            is_field_type_proto_plus_type = not hasattr(field.message, "DESCRIPTOR")

            if is_field_type_proto_plus_type:
                message_fields = field.message.meta.fields.values()
            # Add `# pragma: NO COVER` because there may not be any `*_pb2` field types
            else:  # pragma: NO COVER
                message_fields = field.message.DESCRIPTOR.fields
        return message_fields

    runtime_nested_fields = [
        (field.name, nested_field.name)
        for field in get_message_fields(test_field)
        for nested_field in get_message_fields(field)
    ]

    subfields_not_in_runtime = []

    # For each item in the sample request, create a list of sub fields which are not present at runtime
    # Add `# pragma: NO COVER` because this test code will not run if all subfields are present at runtime
    for field, value in request_init["schedule"].items():  # pragma: NO COVER
        result = None
        is_repeated = False
        # For repeated fields
        if isinstance(value, list) and len(value):
            is_repeated = True
            result = value[0]
        # For fields where the type is another message
        if isinstance(value, dict):
            result = value

        if result and hasattr(result, "keys"):
            for subfield in result.keys():
                if (field, subfield) not in runtime_nested_fields:
                    subfields_not_in_runtime.append(
                        {
                            "field": field,
                            "subfield": subfield,
                            "is_repeated": is_repeated,
                        }
                    )

    # Remove fields from the sample request which are not present in the runtime version of the dependency
    # Add `# pragma: NO COVER` because this test code will not run if all subfields are present at runtime
    for subfield_to_delete in subfields_not_in_runtime:  # pragma: NO COVER
        field = subfield_to_delete.get("field")
        field_repeated = subfield_to_delete.get("is_repeated")
        subfield = subfield_to_delete.get("subfield")
        if subfield:
            if field_repeated:
                for i in range(0, len(request_init["schedule"][field])):
                    del request_init["schedule"][field][i][subfield]
            else:
                del request_init["schedule"][field][subfield]
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gca_schedule.Schedule(
            name="name_value",
            display_name="display_name_value",
            max_run_count=1410,
            started_run_count=1843,
            state=gca_schedule.Schedule.State.ACTIVE,
            max_concurrent_run_count=2596,
            allow_queueing=True,
            catch_up=True,
            cron="cron_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = gca_schedule.Schedule.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.update_schedule(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_schedule.Schedule)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.max_run_count == 1410
    assert response.started_run_count == 1843
    assert response.state == gca_schedule.Schedule.State.ACTIVE
    assert response.max_concurrent_run_count == 2596
    assert response.allow_queueing is True
    assert response.catch_up is True


def test_update_schedule_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = ScheduleServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.update_schedule in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.update_schedule] = mock_rpc

        request = {}
        client.update_schedule(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.update_schedule(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_update_schedule_rest_required_fields(
    request_type=schedule_service.UpdateScheduleRequest,
):
    transport_class = transports.ScheduleServiceRestTransport

    request_init = {}
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(pb_request, use_integers_for_enums=False)
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_schedule._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_schedule._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("update_mask",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone

    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = gca_schedule.Schedule()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "patch",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            # Convert return value to protobuf type
            return_value = gca_schedule.Schedule.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.update_schedule(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_update_schedule_rest_unset_required_fields():
    transport = transports.ScheduleServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.update_schedule._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("updateMask",))
        & set(
            (
                "schedule",
                "updateMask",
            )
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_update_schedule_rest_interceptors(null_interceptor):
    transport = transports.ScheduleServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.ScheduleServiceRestInterceptor(),
    )
    client = ScheduleServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.ScheduleServiceRestInterceptor, "post_update_schedule"
    ) as post, mock.patch.object(
        transports.ScheduleServiceRestInterceptor, "pre_update_schedule"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = schedule_service.UpdateScheduleRequest.pb(
            schedule_service.UpdateScheduleRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = gca_schedule.Schedule.to_json(
            gca_schedule.Schedule()
        )

        request = schedule_service.UpdateScheduleRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = gca_schedule.Schedule()

        client.update_schedule(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_update_schedule_rest_bad_request(
    transport: str = "rest", request_type=schedule_service.UpdateScheduleRequest
):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {
        "schedule": {"name": "projects/sample1/locations/sample2/schedules/sample3"}
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.update_schedule(request)


def test_update_schedule_rest_flattened():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gca_schedule.Schedule()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "schedule": {"name": "projects/sample1/locations/sample2/schedules/sample3"}
        }

        # get truthy value for each flattened field
        mock_args = dict(
            schedule=gca_schedule.Schedule(cron="cron_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = gca_schedule.Schedule.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.update_schedule(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{schedule.name=projects/*/locations/*/schedules/*}"
            % client.transport._host,
            args[1],
        )


def test_update_schedule_rest_flattened_error(transport: str = "rest"):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_schedule(
            schedule_service.UpdateScheduleRequest(),
            schedule=gca_schedule.Schedule(cron="cron_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


def test_update_schedule_rest_error():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.ScheduleServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = ScheduleServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.ScheduleServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = ScheduleServiceClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide an api_key and a transport instance.
    transport = transports.ScheduleServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    options = client_options.ClientOptions()
    options.api_key = "api_key"
    with pytest.raises(ValueError):
        client = ScheduleServiceClient(
            client_options=options,
            transport=transport,
        )

    # It is an error to provide an api_key and a credential.
    options = client_options.ClientOptions()
    options.api_key = "api_key"
    with pytest.raises(ValueError):
        client = ScheduleServiceClient(
            client_options=options, credentials=ga_credentials.AnonymousCredentials()
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.ScheduleServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = ScheduleServiceClient(
            client_options={"scopes": ["1", "2"]},
            transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.ScheduleServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    client = ScheduleServiceClient(transport=transport)
    assert client.transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.ScheduleServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.ScheduleServiceGrpcAsyncIOTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.ScheduleServiceGrpcTransport,
        transports.ScheduleServiceGrpcAsyncIOTransport,
        transports.ScheduleServiceRestTransport,
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
        "rest",
    ],
)
def test_transport_kind(transport_name):
    transport = ScheduleServiceClient.get_transport_class(transport_name)(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    assert transport.kind == transport_name


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    assert isinstance(
        client.transport,
        transports.ScheduleServiceGrpcTransport,
    )


def test_schedule_service_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(core_exceptions.DuplicateCredentialArgs):
        transport = transports.ScheduleServiceTransport(
            credentials=ga_credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_schedule_service_base_transport():
    # Instantiate the base transport.
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.schedule_service.transports.ScheduleServiceTransport.__init__"
    ) as Transport:
        Transport.return_value = None
        transport = transports.ScheduleServiceTransport(
            credentials=ga_credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "create_schedule",
        "delete_schedule",
        "get_schedule",
        "list_schedules",
        "pause_schedule",
        "resume_schedule",
        "update_schedule",
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


def test_schedule_service_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        google.auth, "load_credentials_from_file", autospec=True
    ) as load_creds, mock.patch(
        "google.cloud.aiplatform_v1beta1.services.schedule_service.transports.ScheduleServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.ScheduleServiceTransport(
            credentials_file="credentials.json",
            quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=None,
            default_scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


def test_schedule_service_base_transport_with_adc():
    # Test the default credentials are used if credentials and credentials_file are None.
    with mock.patch.object(google.auth, "default", autospec=True) as adc, mock.patch(
        "google.cloud.aiplatform_v1beta1.services.schedule_service.transports.ScheduleServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.ScheduleServiceTransport()
        adc.assert_called_once()


def test_schedule_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        ScheduleServiceClient()
        adc.assert_called_once_with(
            scopes=None,
            default_scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id=None,
        )


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.ScheduleServiceGrpcTransport,
        transports.ScheduleServiceGrpcAsyncIOTransport,
    ],
)
def test_schedule_service_transport_auth_adc(transport_class):
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
        transports.ScheduleServiceGrpcTransport,
        transports.ScheduleServiceGrpcAsyncIOTransport,
        transports.ScheduleServiceRestTransport,
    ],
)
def test_schedule_service_transport_auth_gdch_credentials(transport_class):
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
        (transports.ScheduleServiceGrpcTransport, grpc_helpers),
        (transports.ScheduleServiceGrpcAsyncIOTransport, grpc_helpers_async),
    ],
)
def test_schedule_service_transport_create_channel(transport_class, grpc_helpers):
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
        transports.ScheduleServiceGrpcTransport,
        transports.ScheduleServiceGrpcAsyncIOTransport,
    ],
)
def test_schedule_service_grpc_transport_client_cert_source_for_mtls(transport_class):
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


def test_schedule_service_http_transport_client_cert_source_for_mtls():
    cred = ga_credentials.AnonymousCredentials()
    with mock.patch(
        "google.auth.transport.requests.AuthorizedSession.configure_mtls_channel"
    ) as mock_configure_mtls_channel:
        transports.ScheduleServiceRestTransport(
            credentials=cred, client_cert_source_for_mtls=client_cert_source_callback
        )
        mock_configure_mtls_channel.assert_called_once_with(client_cert_source_callback)


def test_schedule_service_rest_lro_client():
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    transport = client.transport

    # Ensure that we have a api-core operations client.
    assert isinstance(
        transport.operations_client,
        operations_v1.AbstractOperationsClient,
    )

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


@pytest.mark.parametrize(
    "transport_name",
    [
        "grpc",
        "grpc_asyncio",
        "rest",
    ],
)
def test_schedule_service_host_no_port(transport_name):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="aiplatform.googleapis.com"
        ),
        transport=transport_name,
    )
    assert client.transport._host == (
        "aiplatform.googleapis.com:443"
        if transport_name in ["grpc", "grpc_asyncio"]
        else "https://aiplatform.googleapis.com"
    )


@pytest.mark.parametrize(
    "transport_name",
    [
        "grpc",
        "grpc_asyncio",
        "rest",
    ],
)
def test_schedule_service_host_with_port(transport_name):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="aiplatform.googleapis.com:8000"
        ),
        transport=transport_name,
    )
    assert client.transport._host == (
        "aiplatform.googleapis.com:8000"
        if transport_name in ["grpc", "grpc_asyncio"]
        else "https://aiplatform.googleapis.com:8000"
    )


@pytest.mark.parametrize(
    "transport_name",
    [
        "rest",
    ],
)
def test_schedule_service_client_transport_session_collision(transport_name):
    creds1 = ga_credentials.AnonymousCredentials()
    creds2 = ga_credentials.AnonymousCredentials()
    client1 = ScheduleServiceClient(
        credentials=creds1,
        transport=transport_name,
    )
    client2 = ScheduleServiceClient(
        credentials=creds2,
        transport=transport_name,
    )
    session1 = client1.transport.create_schedule._session
    session2 = client2.transport.create_schedule._session
    assert session1 != session2
    session1 = client1.transport.delete_schedule._session
    session2 = client2.transport.delete_schedule._session
    assert session1 != session2
    session1 = client1.transport.get_schedule._session
    session2 = client2.transport.get_schedule._session
    assert session1 != session2
    session1 = client1.transport.list_schedules._session
    session2 = client2.transport.list_schedules._session
    assert session1 != session2
    session1 = client1.transport.pause_schedule._session
    session2 = client2.transport.pause_schedule._session
    assert session1 != session2
    session1 = client1.transport.resume_schedule._session
    session2 = client2.transport.resume_schedule._session
    assert session1 != session2
    session1 = client1.transport.update_schedule._session
    session2 = client2.transport.update_schedule._session
    assert session1 != session2


def test_schedule_service_grpc_transport_channel():
    channel = grpc.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.ScheduleServiceGrpcTransport(
        host="squid.clam.whelk",
        channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


def test_schedule_service_grpc_asyncio_transport_channel():
    channel = aio.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.ScheduleServiceGrpcAsyncIOTransport(
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
        transports.ScheduleServiceGrpcTransport,
        transports.ScheduleServiceGrpcAsyncIOTransport,
    ],
)
def test_schedule_service_transport_channel_mtls_with_client_cert_source(
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
        transports.ScheduleServiceGrpcTransport,
        transports.ScheduleServiceGrpcAsyncIOTransport,
    ],
)
def test_schedule_service_transport_channel_mtls_with_adc(transport_class):
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


def test_schedule_service_grpc_lro_client():
    client = ScheduleServiceClient(
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


def test_schedule_service_grpc_lro_async_client():
    client = ScheduleServiceAsyncClient(
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
    actual = ScheduleServiceClient.artifact_path(
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
    path = ScheduleServiceClient.artifact_path(**expected)

    # Check that the path construction is reversible.
    actual = ScheduleServiceClient.parse_artifact_path(path)
    assert expected == actual


def test_batch_prediction_job_path():
    project = "winkle"
    location = "nautilus"
    batch_prediction_job = "scallop"
    expected = "projects/{project}/locations/{location}/batchPredictionJobs/{batch_prediction_job}".format(
        project=project,
        location=location,
        batch_prediction_job=batch_prediction_job,
    )
    actual = ScheduleServiceClient.batch_prediction_job_path(
        project, location, batch_prediction_job
    )
    assert expected == actual


def test_parse_batch_prediction_job_path():
    expected = {
        "project": "abalone",
        "location": "squid",
        "batch_prediction_job": "clam",
    }
    path = ScheduleServiceClient.batch_prediction_job_path(**expected)

    # Check that the path construction is reversible.
    actual = ScheduleServiceClient.parse_batch_prediction_job_path(path)
    assert expected == actual


def test_context_path():
    project = "whelk"
    location = "octopus"
    metadata_store = "oyster"
    context = "nudibranch"
    expected = "projects/{project}/locations/{location}/metadataStores/{metadata_store}/contexts/{context}".format(
        project=project,
        location=location,
        metadata_store=metadata_store,
        context=context,
    )
    actual = ScheduleServiceClient.context_path(
        project, location, metadata_store, context
    )
    assert expected == actual


def test_parse_context_path():
    expected = {
        "project": "cuttlefish",
        "location": "mussel",
        "metadata_store": "winkle",
        "context": "nautilus",
    }
    path = ScheduleServiceClient.context_path(**expected)

    # Check that the path construction is reversible.
    actual = ScheduleServiceClient.parse_context_path(path)
    assert expected == actual


def test_custom_job_path():
    project = "scallop"
    location = "abalone"
    custom_job = "squid"
    expected = "projects/{project}/locations/{location}/customJobs/{custom_job}".format(
        project=project,
        location=location,
        custom_job=custom_job,
    )
    actual = ScheduleServiceClient.custom_job_path(project, location, custom_job)
    assert expected == actual


def test_parse_custom_job_path():
    expected = {
        "project": "clam",
        "location": "whelk",
        "custom_job": "octopus",
    }
    path = ScheduleServiceClient.custom_job_path(**expected)

    # Check that the path construction is reversible.
    actual = ScheduleServiceClient.parse_custom_job_path(path)
    assert expected == actual


def test_dataset_path():
    project = "oyster"
    location = "nudibranch"
    dataset = "cuttlefish"
    expected = "projects/{project}/locations/{location}/datasets/{dataset}".format(
        project=project,
        location=location,
        dataset=dataset,
    )
    actual = ScheduleServiceClient.dataset_path(project, location, dataset)
    assert expected == actual


def test_parse_dataset_path():
    expected = {
        "project": "mussel",
        "location": "winkle",
        "dataset": "nautilus",
    }
    path = ScheduleServiceClient.dataset_path(**expected)

    # Check that the path construction is reversible.
    actual = ScheduleServiceClient.parse_dataset_path(path)
    assert expected == actual


def test_endpoint_path():
    project = "scallop"
    location = "abalone"
    endpoint = "squid"
    expected = "projects/{project}/locations/{location}/endpoints/{endpoint}".format(
        project=project,
        location=location,
        endpoint=endpoint,
    )
    actual = ScheduleServiceClient.endpoint_path(project, location, endpoint)
    assert expected == actual


def test_parse_endpoint_path():
    expected = {
        "project": "clam",
        "location": "whelk",
        "endpoint": "octopus",
    }
    path = ScheduleServiceClient.endpoint_path(**expected)

    # Check that the path construction is reversible.
    actual = ScheduleServiceClient.parse_endpoint_path(path)
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
    actual = ScheduleServiceClient.execution_path(
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
    path = ScheduleServiceClient.execution_path(**expected)

    # Check that the path construction is reversible.
    actual = ScheduleServiceClient.parse_execution_path(path)
    assert expected == actual


def test_model_monitor_path():
    project = "squid"
    location = "clam"
    model_monitor = "whelk"
    expected = (
        "projects/{project}/locations/{location}/modelMonitors/{model_monitor}".format(
            project=project,
            location=location,
            model_monitor=model_monitor,
        )
    )
    actual = ScheduleServiceClient.model_monitor_path(project, location, model_monitor)
    assert expected == actual


def test_parse_model_monitor_path():
    expected = {
        "project": "octopus",
        "location": "oyster",
        "model_monitor": "nudibranch",
    }
    path = ScheduleServiceClient.model_monitor_path(**expected)

    # Check that the path construction is reversible.
    actual = ScheduleServiceClient.parse_model_monitor_path(path)
    assert expected == actual


def test_model_monitoring_job_path():
    project = "cuttlefish"
    location = "mussel"
    model_monitor = "winkle"
    model_monitoring_job = "nautilus"
    expected = "projects/{project}/locations/{location}/modelMonitors/{model_monitor}/modelMonitoringJobs/{model_monitoring_job}".format(
        project=project,
        location=location,
        model_monitor=model_monitor,
        model_monitoring_job=model_monitoring_job,
    )
    actual = ScheduleServiceClient.model_monitoring_job_path(
        project, location, model_monitor, model_monitoring_job
    )
    assert expected == actual


def test_parse_model_monitoring_job_path():
    expected = {
        "project": "scallop",
        "location": "abalone",
        "model_monitor": "squid",
        "model_monitoring_job": "clam",
    }
    path = ScheduleServiceClient.model_monitoring_job_path(**expected)

    # Check that the path construction is reversible.
    actual = ScheduleServiceClient.parse_model_monitoring_job_path(path)
    assert expected == actual


def test_network_path():
    project = "whelk"
    network = "octopus"
    expected = "projects/{project}/global/networks/{network}".format(
        project=project,
        network=network,
    )
    actual = ScheduleServiceClient.network_path(project, network)
    assert expected == actual


def test_parse_network_path():
    expected = {
        "project": "oyster",
        "network": "nudibranch",
    }
    path = ScheduleServiceClient.network_path(**expected)

    # Check that the path construction is reversible.
    actual = ScheduleServiceClient.parse_network_path(path)
    assert expected == actual


def test_notebook_execution_job_path():
    project = "cuttlefish"
    location = "mussel"
    notebook_execution_job = "winkle"
    expected = "projects/{project}/locations/{location}/notebookExecutionJobs/{notebook_execution_job}".format(
        project=project,
        location=location,
        notebook_execution_job=notebook_execution_job,
    )
    actual = ScheduleServiceClient.notebook_execution_job_path(
        project, location, notebook_execution_job
    )
    assert expected == actual


def test_parse_notebook_execution_job_path():
    expected = {
        "project": "nautilus",
        "location": "scallop",
        "notebook_execution_job": "abalone",
    }
    path = ScheduleServiceClient.notebook_execution_job_path(**expected)

    # Check that the path construction is reversible.
    actual = ScheduleServiceClient.parse_notebook_execution_job_path(path)
    assert expected == actual


def test_notebook_runtime_template_path():
    project = "squid"
    location = "clam"
    notebook_runtime_template = "whelk"
    expected = "projects/{project}/locations/{location}/notebookRuntimeTemplates/{notebook_runtime_template}".format(
        project=project,
        location=location,
        notebook_runtime_template=notebook_runtime_template,
    )
    actual = ScheduleServiceClient.notebook_runtime_template_path(
        project, location, notebook_runtime_template
    )
    assert expected == actual


def test_parse_notebook_runtime_template_path():
    expected = {
        "project": "octopus",
        "location": "oyster",
        "notebook_runtime_template": "nudibranch",
    }
    path = ScheduleServiceClient.notebook_runtime_template_path(**expected)

    # Check that the path construction is reversible.
    actual = ScheduleServiceClient.parse_notebook_runtime_template_path(path)
    assert expected == actual


def test_pipeline_job_path():
    project = "cuttlefish"
    location = "mussel"
    pipeline_job = "winkle"
    expected = (
        "projects/{project}/locations/{location}/pipelineJobs/{pipeline_job}".format(
            project=project,
            location=location,
            pipeline_job=pipeline_job,
        )
    )
    actual = ScheduleServiceClient.pipeline_job_path(project, location, pipeline_job)
    assert expected == actual


def test_parse_pipeline_job_path():
    expected = {
        "project": "nautilus",
        "location": "scallop",
        "pipeline_job": "abalone",
    }
    path = ScheduleServiceClient.pipeline_job_path(**expected)

    # Check that the path construction is reversible.
    actual = ScheduleServiceClient.parse_pipeline_job_path(path)
    assert expected == actual


def test_schedule_path():
    project = "squid"
    location = "clam"
    schedule = "whelk"
    expected = "projects/{project}/locations/{location}/schedules/{schedule}".format(
        project=project,
        location=location,
        schedule=schedule,
    )
    actual = ScheduleServiceClient.schedule_path(project, location, schedule)
    assert expected == actual


def test_parse_schedule_path():
    expected = {
        "project": "octopus",
        "location": "oyster",
        "schedule": "nudibranch",
    }
    path = ScheduleServiceClient.schedule_path(**expected)

    # Check that the path construction is reversible.
    actual = ScheduleServiceClient.parse_schedule_path(path)
    assert expected == actual


def test_common_billing_account_path():
    billing_account = "cuttlefish"
    expected = "billingAccounts/{billing_account}".format(
        billing_account=billing_account,
    )
    actual = ScheduleServiceClient.common_billing_account_path(billing_account)
    assert expected == actual


def test_parse_common_billing_account_path():
    expected = {
        "billing_account": "mussel",
    }
    path = ScheduleServiceClient.common_billing_account_path(**expected)

    # Check that the path construction is reversible.
    actual = ScheduleServiceClient.parse_common_billing_account_path(path)
    assert expected == actual


def test_common_folder_path():
    folder = "winkle"
    expected = "folders/{folder}".format(
        folder=folder,
    )
    actual = ScheduleServiceClient.common_folder_path(folder)
    assert expected == actual


def test_parse_common_folder_path():
    expected = {
        "folder": "nautilus",
    }
    path = ScheduleServiceClient.common_folder_path(**expected)

    # Check that the path construction is reversible.
    actual = ScheduleServiceClient.parse_common_folder_path(path)
    assert expected == actual


def test_common_organization_path():
    organization = "scallop"
    expected = "organizations/{organization}".format(
        organization=organization,
    )
    actual = ScheduleServiceClient.common_organization_path(organization)
    assert expected == actual


def test_parse_common_organization_path():
    expected = {
        "organization": "abalone",
    }
    path = ScheduleServiceClient.common_organization_path(**expected)

    # Check that the path construction is reversible.
    actual = ScheduleServiceClient.parse_common_organization_path(path)
    assert expected == actual


def test_common_project_path():
    project = "squid"
    expected = "projects/{project}".format(
        project=project,
    )
    actual = ScheduleServiceClient.common_project_path(project)
    assert expected == actual


def test_parse_common_project_path():
    expected = {
        "project": "clam",
    }
    path = ScheduleServiceClient.common_project_path(**expected)

    # Check that the path construction is reversible.
    actual = ScheduleServiceClient.parse_common_project_path(path)
    assert expected == actual


def test_common_location_path():
    project = "whelk"
    location = "octopus"
    expected = "projects/{project}/locations/{location}".format(
        project=project,
        location=location,
    )
    actual = ScheduleServiceClient.common_location_path(project, location)
    assert expected == actual


def test_parse_common_location_path():
    expected = {
        "project": "oyster",
        "location": "nudibranch",
    }
    path = ScheduleServiceClient.common_location_path(**expected)

    # Check that the path construction is reversible.
    actual = ScheduleServiceClient.parse_common_location_path(path)
    assert expected == actual


def test_client_with_default_client_info():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(
        transports.ScheduleServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        client = ScheduleServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(
        transports.ScheduleServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        transport_class = ScheduleServiceClient.get_transport_class()
        transport = transport_class(
            credentials=ga_credentials.AnonymousCredentials(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)


@pytest.mark.asyncio
async def test_transport_close_async():
    client = ScheduleServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc_asyncio",
    )
    with mock.patch.object(
        type(getattr(client.transport, "grpc_channel")), "close"
    ) as close:
        async with client:
            close.assert_not_called()
        close.assert_called_once()


def test_get_location_rest_bad_request(
    transport: str = "rest", request_type=locations_pb2.GetLocationRequest
):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    request = request_type()
    request = json_format.ParseDict(
        {"name": "projects/sample1/locations/sample2"}, request
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.get_location(request)


@pytest.mark.parametrize(
    "request_type",
    [
        locations_pb2.GetLocationRequest,
        dict,
    ],
)
def test_get_location_rest(request_type):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request_init = {"name": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = locations_pb2.Location()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        response = client.get_location(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, locations_pb2.Location)


def test_list_locations_rest_bad_request(
    transport: str = "rest", request_type=locations_pb2.ListLocationsRequest
):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    request = request_type()
    request = json_format.ParseDict({"name": "projects/sample1"}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.list_locations(request)


@pytest.mark.parametrize(
    "request_type",
    [
        locations_pb2.ListLocationsRequest,
        dict,
    ],
)
def test_list_locations_rest(request_type):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request_init = {"name": "projects/sample1"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = locations_pb2.ListLocationsResponse()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        response = client.list_locations(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, locations_pb2.ListLocationsResponse)


def test_get_iam_policy_rest_bad_request(
    transport: str = "rest", request_type=iam_policy_pb2.GetIamPolicyRequest
):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    request = request_type()
    request = json_format.ParseDict(
        {"resource": "projects/sample1/locations/sample2/featurestores/sample3"},
        request,
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.get_iam_policy(request)


@pytest.mark.parametrize(
    "request_type",
    [
        iam_policy_pb2.GetIamPolicyRequest,
        dict,
    ],
)
def test_get_iam_policy_rest(request_type):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request_init = {
        "resource": "projects/sample1/locations/sample2/featurestores/sample3"
    }
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = policy_pb2.Policy()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        response = client.get_iam_policy(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy_pb2.Policy)


def test_set_iam_policy_rest_bad_request(
    transport: str = "rest", request_type=iam_policy_pb2.SetIamPolicyRequest
):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    request = request_type()
    request = json_format.ParseDict(
        {"resource": "projects/sample1/locations/sample2/featurestores/sample3"},
        request,
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.set_iam_policy(request)


@pytest.mark.parametrize(
    "request_type",
    [
        iam_policy_pb2.SetIamPolicyRequest,
        dict,
    ],
)
def test_set_iam_policy_rest(request_type):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request_init = {
        "resource": "projects/sample1/locations/sample2/featurestores/sample3"
    }
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = policy_pb2.Policy()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        response = client.set_iam_policy(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy_pb2.Policy)


def test_test_iam_permissions_rest_bad_request(
    transport: str = "rest", request_type=iam_policy_pb2.TestIamPermissionsRequest
):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    request = request_type()
    request = json_format.ParseDict(
        {"resource": "projects/sample1/locations/sample2/featurestores/sample3"},
        request,
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.test_iam_permissions(request)


@pytest.mark.parametrize(
    "request_type",
    [
        iam_policy_pb2.TestIamPermissionsRequest,
        dict,
    ],
)
def test_test_iam_permissions_rest(request_type):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request_init = {
        "resource": "projects/sample1/locations/sample2/featurestores/sample3"
    }
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = iam_policy_pb2.TestIamPermissionsResponse()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        response = client.test_iam_permissions(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, iam_policy_pb2.TestIamPermissionsResponse)


def test_cancel_operation_rest_bad_request(
    transport: str = "rest", request_type=operations_pb2.CancelOperationRequest
):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    request = request_type()
    request = json_format.ParseDict(
        {"name": "projects/sample1/locations/sample2/operations/sample3"}, request
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.cancel_operation(request)


@pytest.mark.parametrize(
    "request_type",
    [
        operations_pb2.CancelOperationRequest,
        dict,
    ],
)
def test_cancel_operation_rest(request_type):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request_init = {"name": "projects/sample1/locations/sample2/operations/sample3"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = "{}"

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        response = client.cancel_operation(request)

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_operation_rest_bad_request(
    transport: str = "rest", request_type=operations_pb2.DeleteOperationRequest
):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    request = request_type()
    request = json_format.ParseDict(
        {"name": "projects/sample1/locations/sample2/operations/sample3"}, request
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.delete_operation(request)


@pytest.mark.parametrize(
    "request_type",
    [
        operations_pb2.DeleteOperationRequest,
        dict,
    ],
)
def test_delete_operation_rest(request_type):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request_init = {"name": "projects/sample1/locations/sample2/operations/sample3"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = "{}"

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        response = client.delete_operation(request)

    # Establish that the response is the type that we expect.
    assert response is None


def test_get_operation_rest_bad_request(
    transport: str = "rest", request_type=operations_pb2.GetOperationRequest
):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    request = request_type()
    request = json_format.ParseDict(
        {"name": "projects/sample1/locations/sample2/operations/sample3"}, request
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.get_operation(request)


@pytest.mark.parametrize(
    "request_type",
    [
        operations_pb2.GetOperationRequest,
        dict,
    ],
)
def test_get_operation_rest(request_type):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request_init = {"name": "projects/sample1/locations/sample2/operations/sample3"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        response = client.get_operation(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.Operation)


def test_list_operations_rest_bad_request(
    transport: str = "rest", request_type=operations_pb2.ListOperationsRequest
):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    request = request_type()
    request = json_format.ParseDict(
        {"name": "projects/sample1/locations/sample2"}, request
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.list_operations(request)


@pytest.mark.parametrize(
    "request_type",
    [
        operations_pb2.ListOperationsRequest,
        dict,
    ],
)
def test_list_operations_rest(request_type):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request_init = {"name": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.ListOperationsResponse()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        response = client.list_operations(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.ListOperationsResponse)


def test_wait_operation_rest_bad_request(
    transport: str = "rest", request_type=operations_pb2.WaitOperationRequest
):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    request = request_type()
    request = json_format.ParseDict(
        {"name": "projects/sample1/locations/sample2/operations/sample3"}, request
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.wait_operation(request)


@pytest.mark.parametrize(
    "request_type",
    [
        operations_pb2.WaitOperationRequest,
        dict,
    ],
)
def test_wait_operation_rest(request_type):
    client = ScheduleServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request_init = {"name": "projects/sample1/locations/sample2/operations/sample3"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        response = client.wait_operation(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.Operation)


def test_delete_operation(transport: str = "grpc"):
    client = ScheduleServiceClient(
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
async def test_delete_operation_async(transport: str = "grpc_asyncio"):
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
async def test_cancel_operation_async(transport: str = "grpc_asyncio"):
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
async def test_wait_operation(transport: str = "grpc_asyncio"):
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
async def test_get_operation_async(transport: str = "grpc_asyncio"):
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
async def test_list_operations_async(transport: str = "grpc_asyncio"):
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
async def test_list_locations_async(transport: str = "grpc_asyncio"):
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(credentials=ga_credentials.AnonymousCredentials())

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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
    client = ScheduleServiceClient(
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
    client = ScheduleServiceAsyncClient(
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
        "rest": "_session",
        "grpc": "_grpc_channel",
    }

    for transport, close_name in transports.items():
        client = ScheduleServiceClient(
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
        "rest",
        "grpc",
    ]
    for transport in transports:
        client = ScheduleServiceClient(
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
        (ScheduleServiceClient, transports.ScheduleServiceGrpcTransport),
        (ScheduleServiceAsyncClient, transports.ScheduleServiceGrpcAsyncIOTransport),
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
                host=client._DEFAULT_ENDPOINT_TEMPLATE.format(
                    UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE
                ),
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
                always_use_jwt_access=True,
                api_audience=None,
            )
