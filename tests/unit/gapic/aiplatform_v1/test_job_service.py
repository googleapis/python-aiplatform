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
from google.cloud.aiplatform_v1.services.job_service import JobServiceAsyncClient
from google.cloud.aiplatform_v1.services.job_service import JobServiceClient
from google.cloud.aiplatform_v1.services.job_service import pagers
from google.cloud.aiplatform_v1.services.job_service import transports
from google.cloud.aiplatform_v1.types import accelerator_type
from google.cloud.aiplatform_v1.types import batch_prediction_job
from google.cloud.aiplatform_v1.types import (
    batch_prediction_job as gca_batch_prediction_job,
)
from google.cloud.aiplatform_v1.types import completion_stats
from google.cloud.aiplatform_v1.types import custom_job
from google.cloud.aiplatform_v1.types import custom_job as gca_custom_job
from google.cloud.aiplatform_v1.types import data_labeling_job
from google.cloud.aiplatform_v1.types import data_labeling_job as gca_data_labeling_job
from google.cloud.aiplatform_v1.types import encryption_spec
from google.cloud.aiplatform_v1.types import env_var
from google.cloud.aiplatform_v1.types import explanation
from google.cloud.aiplatform_v1.types import explanation_metadata
from google.cloud.aiplatform_v1.types import hyperparameter_tuning_job
from google.cloud.aiplatform_v1.types import (
    hyperparameter_tuning_job as gca_hyperparameter_tuning_job,
)
from google.cloud.aiplatform_v1.types import io
from google.cloud.aiplatform_v1.types import job_service
from google.cloud.aiplatform_v1.types import job_state
from google.cloud.aiplatform_v1.types import machine_resources
from google.cloud.aiplatform_v1.types import manual_batch_tuning_parameters
from google.cloud.aiplatform_v1.types import model
from google.cloud.aiplatform_v1.types import model_deployment_monitoring_job
from google.cloud.aiplatform_v1.types import (
    model_deployment_monitoring_job as gca_model_deployment_monitoring_job,
)
from google.cloud.aiplatform_v1.types import model_monitoring
from google.cloud.aiplatform_v1.types import nas_job
from google.cloud.aiplatform_v1.types import nas_job as gca_nas_job
from google.cloud.aiplatform_v1.types import operation as gca_operation
from google.cloud.aiplatform_v1.types import study
from google.cloud.aiplatform_v1.types import unmanaged_container_model
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
from google.protobuf import wrappers_pb2  # type: ignore
from google.rpc import status_pb2  # type: ignore
from google.type import money_pb2  # type: ignore
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

    assert JobServiceClient._get_default_mtls_endpoint(None) is None
    assert (
        JobServiceClient._get_default_mtls_endpoint(api_endpoint) == api_mtls_endpoint
    )
    assert (
        JobServiceClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        JobServiceClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        JobServiceClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert JobServiceClient._get_default_mtls_endpoint(non_googleapi) == non_googleapi


def test__read_environment_variables():
    assert JobServiceClient._read_environment_variables() == (False, "auto", None)

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        assert JobServiceClient._read_environment_variables() == (True, "auto", None)

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "false"}):
        assert JobServiceClient._read_environment_variables() == (False, "auto", None)

    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}
    ):
        with pytest.raises(ValueError) as excinfo:
            JobServiceClient._read_environment_variables()
    assert (
        str(excinfo.value)
        == "Environment variable `GOOGLE_API_USE_CLIENT_CERTIFICATE` must be either `true` or `false`"
    )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        assert JobServiceClient._read_environment_variables() == (False, "never", None)

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        assert JobServiceClient._read_environment_variables() == (False, "always", None)

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"}):
        assert JobServiceClient._read_environment_variables() == (False, "auto", None)

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError) as excinfo:
            JobServiceClient._read_environment_variables()
    assert (
        str(excinfo.value)
        == "Environment variable `GOOGLE_API_USE_MTLS_ENDPOINT` must be `never`, `auto` or `always`"
    )

    with mock.patch.dict(os.environ, {"GOOGLE_CLOUD_UNIVERSE_DOMAIN": "foo.com"}):
        assert JobServiceClient._read_environment_variables() == (
            False,
            "auto",
            "foo.com",
        )


def test__get_client_cert_source():
    mock_provided_cert_source = mock.Mock()
    mock_default_cert_source = mock.Mock()

    assert JobServiceClient._get_client_cert_source(None, False) is None
    assert (
        JobServiceClient._get_client_cert_source(mock_provided_cert_source, False)
        is None
    )
    assert (
        JobServiceClient._get_client_cert_source(mock_provided_cert_source, True)
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
                JobServiceClient._get_client_cert_source(None, True)
                is mock_default_cert_source
            )
            assert (
                JobServiceClient._get_client_cert_source(
                    mock_provided_cert_source, "true"
                )
                is mock_provided_cert_source
            )


@mock.patch.object(
    JobServiceClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(JobServiceClient),
)
@mock.patch.object(
    JobServiceAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(JobServiceAsyncClient),
)
def test__get_api_endpoint():
    api_override = "foo.com"
    mock_client_cert_source = mock.Mock()
    default_universe = JobServiceClient._DEFAULT_UNIVERSE
    default_endpoint = JobServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(
        UNIVERSE_DOMAIN=default_universe
    )
    mock_universe = "bar.com"
    mock_endpoint = JobServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(
        UNIVERSE_DOMAIN=mock_universe
    )

    assert (
        JobServiceClient._get_api_endpoint(
            api_override, mock_client_cert_source, default_universe, "always"
        )
        == api_override
    )
    assert (
        JobServiceClient._get_api_endpoint(
            None, mock_client_cert_source, default_universe, "auto"
        )
        == JobServiceClient.DEFAULT_MTLS_ENDPOINT
    )
    assert (
        JobServiceClient._get_api_endpoint(None, None, default_universe, "auto")
        == default_endpoint
    )
    assert (
        JobServiceClient._get_api_endpoint(None, None, default_universe, "always")
        == JobServiceClient.DEFAULT_MTLS_ENDPOINT
    )
    assert (
        JobServiceClient._get_api_endpoint(
            None, mock_client_cert_source, default_universe, "always"
        )
        == JobServiceClient.DEFAULT_MTLS_ENDPOINT
    )
    assert (
        JobServiceClient._get_api_endpoint(None, None, mock_universe, "never")
        == mock_endpoint
    )
    assert (
        JobServiceClient._get_api_endpoint(None, None, default_universe, "never")
        == default_endpoint
    )

    with pytest.raises(MutualTLSChannelError) as excinfo:
        JobServiceClient._get_api_endpoint(
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
        JobServiceClient._get_universe_domain(
            client_universe_domain, universe_domain_env
        )
        == client_universe_domain
    )
    assert (
        JobServiceClient._get_universe_domain(None, universe_domain_env)
        == universe_domain_env
    )
    assert (
        JobServiceClient._get_universe_domain(None, None)
        == JobServiceClient._DEFAULT_UNIVERSE
    )

    with pytest.raises(ValueError) as excinfo:
        JobServiceClient._get_universe_domain("", None)
    assert str(excinfo.value) == "Universe Domain cannot be an empty string."


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (JobServiceClient, transports.JobServiceGrpcTransport, "grpc"),
        (JobServiceClient, transports.JobServiceRestTransport, "rest"),
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
        (JobServiceClient, "grpc"),
        (JobServiceAsyncClient, "grpc_asyncio"),
        (JobServiceClient, "rest"),
    ],
)
def test_job_service_client_from_service_account_info(client_class, transport_name):
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
        (transports.JobServiceGrpcTransport, "grpc"),
        (transports.JobServiceGrpcAsyncIOTransport, "grpc_asyncio"),
        (transports.JobServiceRestTransport, "rest"),
    ],
)
def test_job_service_client_service_account_always_use_jwt(
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
        (JobServiceClient, "grpc"),
        (JobServiceAsyncClient, "grpc_asyncio"),
        (JobServiceClient, "rest"),
    ],
)
def test_job_service_client_from_service_account_file(client_class, transport_name):
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


def test_job_service_client_get_transport_class():
    transport = JobServiceClient.get_transport_class()
    available_transports = [
        transports.JobServiceGrpcTransport,
        transports.JobServiceRestTransport,
    ]
    assert transport in available_transports

    transport = JobServiceClient.get_transport_class("grpc")
    assert transport == transports.JobServiceGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (JobServiceClient, transports.JobServiceGrpcTransport, "grpc"),
        (
            JobServiceAsyncClient,
            transports.JobServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
        (JobServiceClient, transports.JobServiceRestTransport, "rest"),
    ],
)
@mock.patch.object(
    JobServiceClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(JobServiceClient),
)
@mock.patch.object(
    JobServiceAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(JobServiceAsyncClient),
)
def test_job_service_client_client_options(
    client_class, transport_class, transport_name
):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(JobServiceClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=ga_credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(JobServiceClient, "get_transport_class") as gtc:
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
        (JobServiceClient, transports.JobServiceGrpcTransport, "grpc", "true"),
        (
            JobServiceAsyncClient,
            transports.JobServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "true",
        ),
        (JobServiceClient, transports.JobServiceGrpcTransport, "grpc", "false"),
        (
            JobServiceAsyncClient,
            transports.JobServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "false",
        ),
        (JobServiceClient, transports.JobServiceRestTransport, "rest", "true"),
        (JobServiceClient, transports.JobServiceRestTransport, "rest", "false"),
    ],
)
@mock.patch.object(
    JobServiceClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(JobServiceClient),
)
@mock.patch.object(
    JobServiceAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(JobServiceAsyncClient),
)
@mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"})
def test_job_service_client_mtls_env_auto(
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


@pytest.mark.parametrize("client_class", [JobServiceClient, JobServiceAsyncClient])
@mock.patch.object(
    JobServiceClient, "DEFAULT_ENDPOINT", modify_default_endpoint(JobServiceClient)
)
@mock.patch.object(
    JobServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(JobServiceAsyncClient),
)
def test_job_service_client_get_mtls_endpoint_and_cert_source(client_class):
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


@pytest.mark.parametrize("client_class", [JobServiceClient, JobServiceAsyncClient])
@mock.patch.object(
    JobServiceClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(JobServiceClient),
)
@mock.patch.object(
    JobServiceAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(JobServiceAsyncClient),
)
def test_job_service_client_client_api_endpoint(client_class):
    mock_client_cert_source = client_cert_source_callback
    api_override = "foo.com"
    default_universe = JobServiceClient._DEFAULT_UNIVERSE
    default_endpoint = JobServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(
        UNIVERSE_DOMAIN=default_universe
    )
    mock_universe = "bar.com"
    mock_endpoint = JobServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(
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
        (JobServiceClient, transports.JobServiceGrpcTransport, "grpc"),
        (
            JobServiceAsyncClient,
            transports.JobServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
        (JobServiceClient, transports.JobServiceRestTransport, "rest"),
    ],
)
def test_job_service_client_client_options_scopes(
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
        (JobServiceClient, transports.JobServiceGrpcTransport, "grpc", grpc_helpers),
        (
            JobServiceAsyncClient,
            transports.JobServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            grpc_helpers_async,
        ),
        (JobServiceClient, transports.JobServiceRestTransport, "rest", None),
    ],
)
def test_job_service_client_client_options_credentials_file(
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


def test_job_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.aiplatform_v1.services.job_service.transports.JobServiceGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = JobServiceClient(client_options={"api_endpoint": "squid.clam.whelk"})
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
        (JobServiceClient, transports.JobServiceGrpcTransport, "grpc", grpc_helpers),
        (
            JobServiceAsyncClient,
            transports.JobServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            grpc_helpers_async,
        ),
    ],
)
def test_job_service_client_create_channel_credentials_file(
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
            default_scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/cloud-platform.read-only",
            ),
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
        job_service.CreateCustomJobRequest,
        dict,
    ],
)
def test_create_custom_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_custom_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_custom_job.CustomJob(
            name="name_value",
            display_name="display_name_value",
            state=job_state.JobState.JOB_STATE_QUEUED,
        )
        response = client.create_custom_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CreateCustomJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_custom_job.CustomJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED


def test_create_custom_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_custom_job), "__call__"
    ) as call:
        client.create_custom_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CreateCustomJobRequest()


@pytest.mark.asyncio
async def test_create_custom_job_async(
    transport: str = "grpc_asyncio", request_type=job_service.CreateCustomJobRequest
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_custom_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_custom_job.CustomJob(
                name="name_value",
                display_name="display_name_value",
                state=job_state.JobState.JOB_STATE_QUEUED,
            )
        )
        response = await client.create_custom_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CreateCustomJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_custom_job.CustomJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED


@pytest.mark.asyncio
async def test_create_custom_job_async_from_dict():
    await test_create_custom_job_async(request_type=dict)


def test_create_custom_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CreateCustomJobRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_custom_job), "__call__"
    ) as call:
        call.return_value = gca_custom_job.CustomJob()
        client.create_custom_job(request)

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
async def test_create_custom_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CreateCustomJobRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_custom_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_custom_job.CustomJob()
        )
        await client.create_custom_job(request)

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


def test_create_custom_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_custom_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_custom_job.CustomJob()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_custom_job(
            parent="parent_value",
            custom_job=gca_custom_job.CustomJob(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].custom_job
        mock_val = gca_custom_job.CustomJob(name="name_value")
        assert arg == mock_val


def test_create_custom_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_custom_job(
            job_service.CreateCustomJobRequest(),
            parent="parent_value",
            custom_job=gca_custom_job.CustomJob(name="name_value"),
        )


@pytest.mark.asyncio
async def test_create_custom_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_custom_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_custom_job.CustomJob()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_custom_job.CustomJob()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_custom_job(
            parent="parent_value",
            custom_job=gca_custom_job.CustomJob(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].custom_job
        mock_val = gca_custom_job.CustomJob(name="name_value")
        assert arg == mock_val


@pytest.mark.asyncio
async def test_create_custom_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_custom_job(
            job_service.CreateCustomJobRequest(),
            parent="parent_value",
            custom_job=gca_custom_job.CustomJob(name="name_value"),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.GetCustomJobRequest,
        dict,
    ],
)
def test_get_custom_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_custom_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = custom_job.CustomJob(
            name="name_value",
            display_name="display_name_value",
            state=job_state.JobState.JOB_STATE_QUEUED,
        )
        response = client.get_custom_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.GetCustomJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, custom_job.CustomJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED


def test_get_custom_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_custom_job), "__call__") as call:
        client.get_custom_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.GetCustomJobRequest()


@pytest.mark.asyncio
async def test_get_custom_job_async(
    transport: str = "grpc_asyncio", request_type=job_service.GetCustomJobRequest
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_custom_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            custom_job.CustomJob(
                name="name_value",
                display_name="display_name_value",
                state=job_state.JobState.JOB_STATE_QUEUED,
            )
        )
        response = await client.get_custom_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.GetCustomJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, custom_job.CustomJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED


@pytest.mark.asyncio
async def test_get_custom_job_async_from_dict():
    await test_get_custom_job_async(request_type=dict)


def test_get_custom_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.GetCustomJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_custom_job), "__call__") as call:
        call.return_value = custom_job.CustomJob()
        client.get_custom_job(request)

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
async def test_get_custom_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.GetCustomJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_custom_job), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            custom_job.CustomJob()
        )
        await client.get_custom_job(request)

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


def test_get_custom_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_custom_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = custom_job.CustomJob()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_custom_job(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_get_custom_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_custom_job(
            job_service.GetCustomJobRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_get_custom_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_custom_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = custom_job.CustomJob()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            custom_job.CustomJob()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_custom_job(
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
async def test_get_custom_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_custom_job(
            job_service.GetCustomJobRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.ListCustomJobsRequest,
        dict,
    ],
)
def test_list_custom_jobs(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_custom_jobs), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListCustomJobsResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_custom_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ListCustomJobsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListCustomJobsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_custom_jobs_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_custom_jobs), "__call__") as call:
        client.list_custom_jobs()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ListCustomJobsRequest()


@pytest.mark.asyncio
async def test_list_custom_jobs_async(
    transport: str = "grpc_asyncio", request_type=job_service.ListCustomJobsRequest
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_custom_jobs), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListCustomJobsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_custom_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ListCustomJobsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListCustomJobsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_custom_jobs_async_from_dict():
    await test_list_custom_jobs_async(request_type=dict)


def test_list_custom_jobs_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.ListCustomJobsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_custom_jobs), "__call__") as call:
        call.return_value = job_service.ListCustomJobsResponse()
        client.list_custom_jobs(request)

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
async def test_list_custom_jobs_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.ListCustomJobsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_custom_jobs), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListCustomJobsResponse()
        )
        await client.list_custom_jobs(request)

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


def test_list_custom_jobs_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_custom_jobs), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListCustomJobsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_custom_jobs(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_list_custom_jobs_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_custom_jobs(
            job_service.ListCustomJobsRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_custom_jobs_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_custom_jobs), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListCustomJobsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListCustomJobsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_custom_jobs(
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
async def test_list_custom_jobs_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_custom_jobs(
            job_service.ListCustomJobsRequest(),
            parent="parent_value",
        )


def test_list_custom_jobs_pager(transport_name: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_custom_jobs), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListCustomJobsResponse(
                custom_jobs=[
                    custom_job.CustomJob(),
                    custom_job.CustomJob(),
                    custom_job.CustomJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListCustomJobsResponse(
                custom_jobs=[],
                next_page_token="def",
            ),
            job_service.ListCustomJobsResponse(
                custom_jobs=[
                    custom_job.CustomJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListCustomJobsResponse(
                custom_jobs=[
                    custom_job.CustomJob(),
                    custom_job.CustomJob(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_custom_jobs(request={})

        assert pager._metadata == metadata

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, custom_job.CustomJob) for i in results)


def test_list_custom_jobs_pages(transport_name: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_custom_jobs), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListCustomJobsResponse(
                custom_jobs=[
                    custom_job.CustomJob(),
                    custom_job.CustomJob(),
                    custom_job.CustomJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListCustomJobsResponse(
                custom_jobs=[],
                next_page_token="def",
            ),
            job_service.ListCustomJobsResponse(
                custom_jobs=[
                    custom_job.CustomJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListCustomJobsResponse(
                custom_jobs=[
                    custom_job.CustomJob(),
                    custom_job.CustomJob(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_custom_jobs(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_custom_jobs_async_pager():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_custom_jobs), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListCustomJobsResponse(
                custom_jobs=[
                    custom_job.CustomJob(),
                    custom_job.CustomJob(),
                    custom_job.CustomJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListCustomJobsResponse(
                custom_jobs=[],
                next_page_token="def",
            ),
            job_service.ListCustomJobsResponse(
                custom_jobs=[
                    custom_job.CustomJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListCustomJobsResponse(
                custom_jobs=[
                    custom_job.CustomJob(),
                    custom_job.CustomJob(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_custom_jobs(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, custom_job.CustomJob) for i in responses)


@pytest.mark.asyncio
async def test_list_custom_jobs_async_pages():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_custom_jobs), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListCustomJobsResponse(
                custom_jobs=[
                    custom_job.CustomJob(),
                    custom_job.CustomJob(),
                    custom_job.CustomJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListCustomJobsResponse(
                custom_jobs=[],
                next_page_token="def",
            ),
            job_service.ListCustomJobsResponse(
                custom_jobs=[
                    custom_job.CustomJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListCustomJobsResponse(
                custom_jobs=[
                    custom_job.CustomJob(),
                    custom_job.CustomJob(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.list_custom_jobs(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.DeleteCustomJobRequest,
        dict,
    ],
)
def test_delete_custom_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_custom_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_custom_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.DeleteCustomJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_custom_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_custom_job), "__call__"
    ) as call:
        client.delete_custom_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.DeleteCustomJobRequest()


@pytest.mark.asyncio
async def test_delete_custom_job_async(
    transport: str = "grpc_asyncio", request_type=job_service.DeleteCustomJobRequest
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_custom_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_custom_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.DeleteCustomJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_custom_job_async_from_dict():
    await test_delete_custom_job_async(request_type=dict)


def test_delete_custom_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.DeleteCustomJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_custom_job), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_custom_job(request)

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
async def test_delete_custom_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.DeleteCustomJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_custom_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_custom_job(request)

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


def test_delete_custom_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_custom_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_custom_job(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_delete_custom_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_custom_job(
            job_service.DeleteCustomJobRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_custom_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_custom_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_custom_job(
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
async def test_delete_custom_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_custom_job(
            job_service.DeleteCustomJobRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.CancelCustomJobRequest,
        dict,
    ],
)
def test_cancel_custom_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_custom_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        response = client.cancel_custom_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CancelCustomJobRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_cancel_custom_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_custom_job), "__call__"
    ) as call:
        client.cancel_custom_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CancelCustomJobRequest()


@pytest.mark.asyncio
async def test_cancel_custom_job_async(
    transport: str = "grpc_asyncio", request_type=job_service.CancelCustomJobRequest
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_custom_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.cancel_custom_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CancelCustomJobRequest()

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_cancel_custom_job_async_from_dict():
    await test_cancel_custom_job_async(request_type=dict)


def test_cancel_custom_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CancelCustomJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_custom_job), "__call__"
    ) as call:
        call.return_value = None
        client.cancel_custom_job(request)

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
async def test_cancel_custom_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CancelCustomJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_custom_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        await client.cancel_custom_job(request)

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


def test_cancel_custom_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_custom_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.cancel_custom_job(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_cancel_custom_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.cancel_custom_job(
            job_service.CancelCustomJobRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_cancel_custom_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_custom_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.cancel_custom_job(
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
async def test_cancel_custom_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.cancel_custom_job(
            job_service.CancelCustomJobRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.CreateDataLabelingJobRequest,
        dict,
    ],
)
def test_create_data_labeling_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_data_labeling_job.DataLabelingJob(
            name="name_value",
            display_name="display_name_value",
            datasets=["datasets_value"],
            labeler_count=1375,
            instruction_uri="instruction_uri_value",
            inputs_schema_uri="inputs_schema_uri_value",
            state=job_state.JobState.JOB_STATE_QUEUED,
            labeling_progress=1810,
            specialist_pools=["specialist_pools_value"],
        )
        response = client.create_data_labeling_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CreateDataLabelingJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_data_labeling_job.DataLabelingJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.datasets == ["datasets_value"]
    assert response.labeler_count == 1375
    assert response.instruction_uri == "instruction_uri_value"
    assert response.inputs_schema_uri == "inputs_schema_uri_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert response.labeling_progress == 1810
    assert response.specialist_pools == ["specialist_pools_value"]


def test_create_data_labeling_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_data_labeling_job), "__call__"
    ) as call:
        client.create_data_labeling_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CreateDataLabelingJobRequest()


@pytest.mark.asyncio
async def test_create_data_labeling_job_async(
    transport: str = "grpc_asyncio",
    request_type=job_service.CreateDataLabelingJobRequest,
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_data_labeling_job.DataLabelingJob(
                name="name_value",
                display_name="display_name_value",
                datasets=["datasets_value"],
                labeler_count=1375,
                instruction_uri="instruction_uri_value",
                inputs_schema_uri="inputs_schema_uri_value",
                state=job_state.JobState.JOB_STATE_QUEUED,
                labeling_progress=1810,
                specialist_pools=["specialist_pools_value"],
            )
        )
        response = await client.create_data_labeling_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CreateDataLabelingJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_data_labeling_job.DataLabelingJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.datasets == ["datasets_value"]
    assert response.labeler_count == 1375
    assert response.instruction_uri == "instruction_uri_value"
    assert response.inputs_schema_uri == "inputs_schema_uri_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert response.labeling_progress == 1810
    assert response.specialist_pools == ["specialist_pools_value"]


@pytest.mark.asyncio
async def test_create_data_labeling_job_async_from_dict():
    await test_create_data_labeling_job_async(request_type=dict)


def test_create_data_labeling_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CreateDataLabelingJobRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_data_labeling_job), "__call__"
    ) as call:
        call.return_value = gca_data_labeling_job.DataLabelingJob()
        client.create_data_labeling_job(request)

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
async def test_create_data_labeling_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CreateDataLabelingJobRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_data_labeling_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_data_labeling_job.DataLabelingJob()
        )
        await client.create_data_labeling_job(request)

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


def test_create_data_labeling_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_data_labeling_job.DataLabelingJob()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_data_labeling_job(
            parent="parent_value",
            data_labeling_job=gca_data_labeling_job.DataLabelingJob(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].data_labeling_job
        mock_val = gca_data_labeling_job.DataLabelingJob(name="name_value")
        assert arg == mock_val


def test_create_data_labeling_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_data_labeling_job(
            job_service.CreateDataLabelingJobRequest(),
            parent="parent_value",
            data_labeling_job=gca_data_labeling_job.DataLabelingJob(name="name_value"),
        )


@pytest.mark.asyncio
async def test_create_data_labeling_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_data_labeling_job.DataLabelingJob()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_data_labeling_job.DataLabelingJob()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_data_labeling_job(
            parent="parent_value",
            data_labeling_job=gca_data_labeling_job.DataLabelingJob(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].data_labeling_job
        mock_val = gca_data_labeling_job.DataLabelingJob(name="name_value")
        assert arg == mock_val


@pytest.mark.asyncio
async def test_create_data_labeling_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_data_labeling_job(
            job_service.CreateDataLabelingJobRequest(),
            parent="parent_value",
            data_labeling_job=gca_data_labeling_job.DataLabelingJob(name="name_value"),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.GetDataLabelingJobRequest,
        dict,
    ],
)
def test_get_data_labeling_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = data_labeling_job.DataLabelingJob(
            name="name_value",
            display_name="display_name_value",
            datasets=["datasets_value"],
            labeler_count=1375,
            instruction_uri="instruction_uri_value",
            inputs_schema_uri="inputs_schema_uri_value",
            state=job_state.JobState.JOB_STATE_QUEUED,
            labeling_progress=1810,
            specialist_pools=["specialist_pools_value"],
        )
        response = client.get_data_labeling_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.GetDataLabelingJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, data_labeling_job.DataLabelingJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.datasets == ["datasets_value"]
    assert response.labeler_count == 1375
    assert response.instruction_uri == "instruction_uri_value"
    assert response.inputs_schema_uri == "inputs_schema_uri_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert response.labeling_progress == 1810
    assert response.specialist_pools == ["specialist_pools_value"]


def test_get_data_labeling_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_data_labeling_job), "__call__"
    ) as call:
        client.get_data_labeling_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.GetDataLabelingJobRequest()


@pytest.mark.asyncio
async def test_get_data_labeling_job_async(
    transport: str = "grpc_asyncio", request_type=job_service.GetDataLabelingJobRequest
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            data_labeling_job.DataLabelingJob(
                name="name_value",
                display_name="display_name_value",
                datasets=["datasets_value"],
                labeler_count=1375,
                instruction_uri="instruction_uri_value",
                inputs_schema_uri="inputs_schema_uri_value",
                state=job_state.JobState.JOB_STATE_QUEUED,
                labeling_progress=1810,
                specialist_pools=["specialist_pools_value"],
            )
        )
        response = await client.get_data_labeling_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.GetDataLabelingJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, data_labeling_job.DataLabelingJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.datasets == ["datasets_value"]
    assert response.labeler_count == 1375
    assert response.instruction_uri == "instruction_uri_value"
    assert response.inputs_schema_uri == "inputs_schema_uri_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert response.labeling_progress == 1810
    assert response.specialist_pools == ["specialist_pools_value"]


@pytest.mark.asyncio
async def test_get_data_labeling_job_async_from_dict():
    await test_get_data_labeling_job_async(request_type=dict)


def test_get_data_labeling_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.GetDataLabelingJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_data_labeling_job), "__call__"
    ) as call:
        call.return_value = data_labeling_job.DataLabelingJob()
        client.get_data_labeling_job(request)

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
async def test_get_data_labeling_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.GetDataLabelingJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_data_labeling_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            data_labeling_job.DataLabelingJob()
        )
        await client.get_data_labeling_job(request)

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


def test_get_data_labeling_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = data_labeling_job.DataLabelingJob()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_data_labeling_job(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_get_data_labeling_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_data_labeling_job(
            job_service.GetDataLabelingJobRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_get_data_labeling_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = data_labeling_job.DataLabelingJob()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            data_labeling_job.DataLabelingJob()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_data_labeling_job(
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
async def test_get_data_labeling_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_data_labeling_job(
            job_service.GetDataLabelingJobRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.ListDataLabelingJobsRequest,
        dict,
    ],
)
def test_list_data_labeling_jobs(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_data_labeling_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListDataLabelingJobsResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_data_labeling_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ListDataLabelingJobsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDataLabelingJobsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_data_labeling_jobs_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_data_labeling_jobs), "__call__"
    ) as call:
        client.list_data_labeling_jobs()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ListDataLabelingJobsRequest()


@pytest.mark.asyncio
async def test_list_data_labeling_jobs_async(
    transport: str = "grpc_asyncio",
    request_type=job_service.ListDataLabelingJobsRequest,
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_data_labeling_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListDataLabelingJobsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_data_labeling_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ListDataLabelingJobsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDataLabelingJobsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_data_labeling_jobs_async_from_dict():
    await test_list_data_labeling_jobs_async(request_type=dict)


def test_list_data_labeling_jobs_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.ListDataLabelingJobsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_data_labeling_jobs), "__call__"
    ) as call:
        call.return_value = job_service.ListDataLabelingJobsResponse()
        client.list_data_labeling_jobs(request)

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
async def test_list_data_labeling_jobs_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.ListDataLabelingJobsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_data_labeling_jobs), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListDataLabelingJobsResponse()
        )
        await client.list_data_labeling_jobs(request)

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


def test_list_data_labeling_jobs_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_data_labeling_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListDataLabelingJobsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_data_labeling_jobs(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_list_data_labeling_jobs_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_data_labeling_jobs(
            job_service.ListDataLabelingJobsRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_data_labeling_jobs_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_data_labeling_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListDataLabelingJobsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListDataLabelingJobsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_data_labeling_jobs(
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
async def test_list_data_labeling_jobs_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_data_labeling_jobs(
            job_service.ListDataLabelingJobsRequest(),
            parent="parent_value",
        )


def test_list_data_labeling_jobs_pager(transport_name: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_data_labeling_jobs), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[
                    data_labeling_job.DataLabelingJob(),
                    data_labeling_job.DataLabelingJob(),
                    data_labeling_job.DataLabelingJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[],
                next_page_token="def",
            ),
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[
                    data_labeling_job.DataLabelingJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[
                    data_labeling_job.DataLabelingJob(),
                    data_labeling_job.DataLabelingJob(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_data_labeling_jobs(request={})

        assert pager._metadata == metadata

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, data_labeling_job.DataLabelingJob) for i in results)


def test_list_data_labeling_jobs_pages(transport_name: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_data_labeling_jobs), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[
                    data_labeling_job.DataLabelingJob(),
                    data_labeling_job.DataLabelingJob(),
                    data_labeling_job.DataLabelingJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[],
                next_page_token="def",
            ),
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[
                    data_labeling_job.DataLabelingJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[
                    data_labeling_job.DataLabelingJob(),
                    data_labeling_job.DataLabelingJob(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_data_labeling_jobs(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_data_labeling_jobs_async_pager():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_data_labeling_jobs),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[
                    data_labeling_job.DataLabelingJob(),
                    data_labeling_job.DataLabelingJob(),
                    data_labeling_job.DataLabelingJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[],
                next_page_token="def",
            ),
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[
                    data_labeling_job.DataLabelingJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[
                    data_labeling_job.DataLabelingJob(),
                    data_labeling_job.DataLabelingJob(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_data_labeling_jobs(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, data_labeling_job.DataLabelingJob) for i in responses)


@pytest.mark.asyncio
async def test_list_data_labeling_jobs_async_pages():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_data_labeling_jobs),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[
                    data_labeling_job.DataLabelingJob(),
                    data_labeling_job.DataLabelingJob(),
                    data_labeling_job.DataLabelingJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[],
                next_page_token="def",
            ),
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[
                    data_labeling_job.DataLabelingJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[
                    data_labeling_job.DataLabelingJob(),
                    data_labeling_job.DataLabelingJob(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.list_data_labeling_jobs(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.DeleteDataLabelingJobRequest,
        dict,
    ],
)
def test_delete_data_labeling_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_data_labeling_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.DeleteDataLabelingJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_data_labeling_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_data_labeling_job), "__call__"
    ) as call:
        client.delete_data_labeling_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.DeleteDataLabelingJobRequest()


@pytest.mark.asyncio
async def test_delete_data_labeling_job_async(
    transport: str = "grpc_asyncio",
    request_type=job_service.DeleteDataLabelingJobRequest,
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_data_labeling_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.DeleteDataLabelingJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_data_labeling_job_async_from_dict():
    await test_delete_data_labeling_job_async(request_type=dict)


def test_delete_data_labeling_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.DeleteDataLabelingJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_data_labeling_job), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_data_labeling_job(request)

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
async def test_delete_data_labeling_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.DeleteDataLabelingJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_data_labeling_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_data_labeling_job(request)

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


def test_delete_data_labeling_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_data_labeling_job(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_delete_data_labeling_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_data_labeling_job(
            job_service.DeleteDataLabelingJobRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_data_labeling_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_data_labeling_job(
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
async def test_delete_data_labeling_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_data_labeling_job(
            job_service.DeleteDataLabelingJobRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.CancelDataLabelingJobRequest,
        dict,
    ],
)
def test_cancel_data_labeling_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        response = client.cancel_data_labeling_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CancelDataLabelingJobRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_cancel_data_labeling_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_data_labeling_job), "__call__"
    ) as call:
        client.cancel_data_labeling_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CancelDataLabelingJobRequest()


@pytest.mark.asyncio
async def test_cancel_data_labeling_job_async(
    transport: str = "grpc_asyncio",
    request_type=job_service.CancelDataLabelingJobRequest,
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.cancel_data_labeling_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CancelDataLabelingJobRequest()

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_cancel_data_labeling_job_async_from_dict():
    await test_cancel_data_labeling_job_async(request_type=dict)


def test_cancel_data_labeling_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CancelDataLabelingJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_data_labeling_job), "__call__"
    ) as call:
        call.return_value = None
        client.cancel_data_labeling_job(request)

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
async def test_cancel_data_labeling_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CancelDataLabelingJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_data_labeling_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        await client.cancel_data_labeling_job(request)

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


def test_cancel_data_labeling_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.cancel_data_labeling_job(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_cancel_data_labeling_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.cancel_data_labeling_job(
            job_service.CancelDataLabelingJobRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_cancel_data_labeling_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_data_labeling_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.cancel_data_labeling_job(
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
async def test_cancel_data_labeling_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.cancel_data_labeling_job(
            job_service.CancelDataLabelingJobRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.CreateHyperparameterTuningJobRequest,
        dict,
    ],
)
def test_create_hyperparameter_tuning_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_hyperparameter_tuning_job.HyperparameterTuningJob(
            name="name_value",
            display_name="display_name_value",
            max_trial_count=1609,
            parallel_trial_count=2128,
            max_failed_trial_count=2317,
            state=job_state.JobState.JOB_STATE_QUEUED,
        )
        response = client.create_hyperparameter_tuning_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CreateHyperparameterTuningJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_hyperparameter_tuning_job.HyperparameterTuningJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.max_trial_count == 1609
    assert response.parallel_trial_count == 2128
    assert response.max_failed_trial_count == 2317
    assert response.state == job_state.JobState.JOB_STATE_QUEUED


def test_create_hyperparameter_tuning_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_hyperparameter_tuning_job), "__call__"
    ) as call:
        client.create_hyperparameter_tuning_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CreateHyperparameterTuningJobRequest()


@pytest.mark.asyncio
async def test_create_hyperparameter_tuning_job_async(
    transport: str = "grpc_asyncio",
    request_type=job_service.CreateHyperparameterTuningJobRequest,
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_hyperparameter_tuning_job.HyperparameterTuningJob(
                name="name_value",
                display_name="display_name_value",
                max_trial_count=1609,
                parallel_trial_count=2128,
                max_failed_trial_count=2317,
                state=job_state.JobState.JOB_STATE_QUEUED,
            )
        )
        response = await client.create_hyperparameter_tuning_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CreateHyperparameterTuningJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_hyperparameter_tuning_job.HyperparameterTuningJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.max_trial_count == 1609
    assert response.parallel_trial_count == 2128
    assert response.max_failed_trial_count == 2317
    assert response.state == job_state.JobState.JOB_STATE_QUEUED


@pytest.mark.asyncio
async def test_create_hyperparameter_tuning_job_async_from_dict():
    await test_create_hyperparameter_tuning_job_async(request_type=dict)


def test_create_hyperparameter_tuning_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CreateHyperparameterTuningJobRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_hyperparameter_tuning_job), "__call__"
    ) as call:
        call.return_value = gca_hyperparameter_tuning_job.HyperparameterTuningJob()
        client.create_hyperparameter_tuning_job(request)

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
async def test_create_hyperparameter_tuning_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CreateHyperparameterTuningJobRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_hyperparameter_tuning_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_hyperparameter_tuning_job.HyperparameterTuningJob()
        )
        await client.create_hyperparameter_tuning_job(request)

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


def test_create_hyperparameter_tuning_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_hyperparameter_tuning_job.HyperparameterTuningJob()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_hyperparameter_tuning_job(
            parent="parent_value",
            hyperparameter_tuning_job=gca_hyperparameter_tuning_job.HyperparameterTuningJob(
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
        arg = args[0].hyperparameter_tuning_job
        mock_val = gca_hyperparameter_tuning_job.HyperparameterTuningJob(
            name="name_value"
        )
        assert arg == mock_val


def test_create_hyperparameter_tuning_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_hyperparameter_tuning_job(
            job_service.CreateHyperparameterTuningJobRequest(),
            parent="parent_value",
            hyperparameter_tuning_job=gca_hyperparameter_tuning_job.HyperparameterTuningJob(
                name="name_value"
            ),
        )


@pytest.mark.asyncio
async def test_create_hyperparameter_tuning_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_hyperparameter_tuning_job.HyperparameterTuningJob()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_hyperparameter_tuning_job.HyperparameterTuningJob()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_hyperparameter_tuning_job(
            parent="parent_value",
            hyperparameter_tuning_job=gca_hyperparameter_tuning_job.HyperparameterTuningJob(
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
        arg = args[0].hyperparameter_tuning_job
        mock_val = gca_hyperparameter_tuning_job.HyperparameterTuningJob(
            name="name_value"
        )
        assert arg == mock_val


@pytest.mark.asyncio
async def test_create_hyperparameter_tuning_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_hyperparameter_tuning_job(
            job_service.CreateHyperparameterTuningJobRequest(),
            parent="parent_value",
            hyperparameter_tuning_job=gca_hyperparameter_tuning_job.HyperparameterTuningJob(
                name="name_value"
            ),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.GetHyperparameterTuningJobRequest,
        dict,
    ],
)
def test_get_hyperparameter_tuning_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = hyperparameter_tuning_job.HyperparameterTuningJob(
            name="name_value",
            display_name="display_name_value",
            max_trial_count=1609,
            parallel_trial_count=2128,
            max_failed_trial_count=2317,
            state=job_state.JobState.JOB_STATE_QUEUED,
        )
        response = client.get_hyperparameter_tuning_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.GetHyperparameterTuningJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, hyperparameter_tuning_job.HyperparameterTuningJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.max_trial_count == 1609
    assert response.parallel_trial_count == 2128
    assert response.max_failed_trial_count == 2317
    assert response.state == job_state.JobState.JOB_STATE_QUEUED


def test_get_hyperparameter_tuning_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_hyperparameter_tuning_job), "__call__"
    ) as call:
        client.get_hyperparameter_tuning_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.GetHyperparameterTuningJobRequest()


@pytest.mark.asyncio
async def test_get_hyperparameter_tuning_job_async(
    transport: str = "grpc_asyncio",
    request_type=job_service.GetHyperparameterTuningJobRequest,
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            hyperparameter_tuning_job.HyperparameterTuningJob(
                name="name_value",
                display_name="display_name_value",
                max_trial_count=1609,
                parallel_trial_count=2128,
                max_failed_trial_count=2317,
                state=job_state.JobState.JOB_STATE_QUEUED,
            )
        )
        response = await client.get_hyperparameter_tuning_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.GetHyperparameterTuningJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, hyperparameter_tuning_job.HyperparameterTuningJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.max_trial_count == 1609
    assert response.parallel_trial_count == 2128
    assert response.max_failed_trial_count == 2317
    assert response.state == job_state.JobState.JOB_STATE_QUEUED


@pytest.mark.asyncio
async def test_get_hyperparameter_tuning_job_async_from_dict():
    await test_get_hyperparameter_tuning_job_async(request_type=dict)


def test_get_hyperparameter_tuning_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.GetHyperparameterTuningJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_hyperparameter_tuning_job), "__call__"
    ) as call:
        call.return_value = hyperparameter_tuning_job.HyperparameterTuningJob()
        client.get_hyperparameter_tuning_job(request)

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
async def test_get_hyperparameter_tuning_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.GetHyperparameterTuningJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_hyperparameter_tuning_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            hyperparameter_tuning_job.HyperparameterTuningJob()
        )
        await client.get_hyperparameter_tuning_job(request)

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


def test_get_hyperparameter_tuning_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = hyperparameter_tuning_job.HyperparameterTuningJob()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_hyperparameter_tuning_job(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_get_hyperparameter_tuning_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_hyperparameter_tuning_job(
            job_service.GetHyperparameterTuningJobRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_get_hyperparameter_tuning_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = hyperparameter_tuning_job.HyperparameterTuningJob()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            hyperparameter_tuning_job.HyperparameterTuningJob()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_hyperparameter_tuning_job(
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
async def test_get_hyperparameter_tuning_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_hyperparameter_tuning_job(
            job_service.GetHyperparameterTuningJobRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.ListHyperparameterTuningJobsRequest,
        dict,
    ],
)
def test_list_hyperparameter_tuning_jobs(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_hyperparameter_tuning_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListHyperparameterTuningJobsResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_hyperparameter_tuning_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ListHyperparameterTuningJobsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListHyperparameterTuningJobsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_hyperparameter_tuning_jobs_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_hyperparameter_tuning_jobs), "__call__"
    ) as call:
        client.list_hyperparameter_tuning_jobs()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ListHyperparameterTuningJobsRequest()


@pytest.mark.asyncio
async def test_list_hyperparameter_tuning_jobs_async(
    transport: str = "grpc_asyncio",
    request_type=job_service.ListHyperparameterTuningJobsRequest,
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_hyperparameter_tuning_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListHyperparameterTuningJobsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_hyperparameter_tuning_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ListHyperparameterTuningJobsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListHyperparameterTuningJobsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_hyperparameter_tuning_jobs_async_from_dict():
    await test_list_hyperparameter_tuning_jobs_async(request_type=dict)


def test_list_hyperparameter_tuning_jobs_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.ListHyperparameterTuningJobsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_hyperparameter_tuning_jobs), "__call__"
    ) as call:
        call.return_value = job_service.ListHyperparameterTuningJobsResponse()
        client.list_hyperparameter_tuning_jobs(request)

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
async def test_list_hyperparameter_tuning_jobs_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.ListHyperparameterTuningJobsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_hyperparameter_tuning_jobs), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListHyperparameterTuningJobsResponse()
        )
        await client.list_hyperparameter_tuning_jobs(request)

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


def test_list_hyperparameter_tuning_jobs_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_hyperparameter_tuning_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListHyperparameterTuningJobsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_hyperparameter_tuning_jobs(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_list_hyperparameter_tuning_jobs_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_hyperparameter_tuning_jobs(
            job_service.ListHyperparameterTuningJobsRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_hyperparameter_tuning_jobs_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_hyperparameter_tuning_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListHyperparameterTuningJobsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListHyperparameterTuningJobsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_hyperparameter_tuning_jobs(
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
async def test_list_hyperparameter_tuning_jobs_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_hyperparameter_tuning_jobs(
            job_service.ListHyperparameterTuningJobsRequest(),
            parent="parent_value",
        )


def test_list_hyperparameter_tuning_jobs_pager(transport_name: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_hyperparameter_tuning_jobs), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[],
                next_page_token="def",
            ),
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_hyperparameter_tuning_jobs(request={})

        assert pager._metadata == metadata

        results = list(pager)
        assert len(results) == 6
        assert all(
            isinstance(i, hyperparameter_tuning_job.HyperparameterTuningJob)
            for i in results
        )


def test_list_hyperparameter_tuning_jobs_pages(transport_name: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_hyperparameter_tuning_jobs), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[],
                next_page_token="def",
            ),
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_hyperparameter_tuning_jobs(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_hyperparameter_tuning_jobs_async_pager():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_hyperparameter_tuning_jobs),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[],
                next_page_token="def",
            ),
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_hyperparameter_tuning_jobs(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(
            isinstance(i, hyperparameter_tuning_job.HyperparameterTuningJob)
            for i in responses
        )


@pytest.mark.asyncio
async def test_list_hyperparameter_tuning_jobs_async_pages():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_hyperparameter_tuning_jobs),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[],
                next_page_token="def",
            ),
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.list_hyperparameter_tuning_jobs(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.DeleteHyperparameterTuningJobRequest,
        dict,
    ],
)
def test_delete_hyperparameter_tuning_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_hyperparameter_tuning_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.DeleteHyperparameterTuningJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_hyperparameter_tuning_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_hyperparameter_tuning_job), "__call__"
    ) as call:
        client.delete_hyperparameter_tuning_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.DeleteHyperparameterTuningJobRequest()


@pytest.mark.asyncio
async def test_delete_hyperparameter_tuning_job_async(
    transport: str = "grpc_asyncio",
    request_type=job_service.DeleteHyperparameterTuningJobRequest,
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_hyperparameter_tuning_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.DeleteHyperparameterTuningJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_hyperparameter_tuning_job_async_from_dict():
    await test_delete_hyperparameter_tuning_job_async(request_type=dict)


def test_delete_hyperparameter_tuning_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.DeleteHyperparameterTuningJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_hyperparameter_tuning_job), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_hyperparameter_tuning_job(request)

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
async def test_delete_hyperparameter_tuning_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.DeleteHyperparameterTuningJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_hyperparameter_tuning_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_hyperparameter_tuning_job(request)

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


def test_delete_hyperparameter_tuning_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_hyperparameter_tuning_job(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_delete_hyperparameter_tuning_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_hyperparameter_tuning_job(
            job_service.DeleteHyperparameterTuningJobRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_hyperparameter_tuning_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_hyperparameter_tuning_job(
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
async def test_delete_hyperparameter_tuning_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_hyperparameter_tuning_job(
            job_service.DeleteHyperparameterTuningJobRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.CancelHyperparameterTuningJobRequest,
        dict,
    ],
)
def test_cancel_hyperparameter_tuning_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        response = client.cancel_hyperparameter_tuning_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CancelHyperparameterTuningJobRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_cancel_hyperparameter_tuning_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_hyperparameter_tuning_job), "__call__"
    ) as call:
        client.cancel_hyperparameter_tuning_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CancelHyperparameterTuningJobRequest()


@pytest.mark.asyncio
async def test_cancel_hyperparameter_tuning_job_async(
    transport: str = "grpc_asyncio",
    request_type=job_service.CancelHyperparameterTuningJobRequest,
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.cancel_hyperparameter_tuning_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CancelHyperparameterTuningJobRequest()

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_cancel_hyperparameter_tuning_job_async_from_dict():
    await test_cancel_hyperparameter_tuning_job_async(request_type=dict)


def test_cancel_hyperparameter_tuning_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CancelHyperparameterTuningJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_hyperparameter_tuning_job), "__call__"
    ) as call:
        call.return_value = None
        client.cancel_hyperparameter_tuning_job(request)

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
async def test_cancel_hyperparameter_tuning_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CancelHyperparameterTuningJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_hyperparameter_tuning_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        await client.cancel_hyperparameter_tuning_job(request)

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


def test_cancel_hyperparameter_tuning_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.cancel_hyperparameter_tuning_job(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_cancel_hyperparameter_tuning_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.cancel_hyperparameter_tuning_job(
            job_service.CancelHyperparameterTuningJobRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_cancel_hyperparameter_tuning_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_hyperparameter_tuning_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.cancel_hyperparameter_tuning_job(
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
async def test_cancel_hyperparameter_tuning_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.cancel_hyperparameter_tuning_job(
            job_service.CancelHyperparameterTuningJobRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.CreateNasJobRequest,
        dict,
    ],
)
def test_create_nas_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_nas_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_nas_job.NasJob(
            name="name_value",
            display_name="display_name_value",
            state=job_state.JobState.JOB_STATE_QUEUED,
            enable_restricted_image_training=True,
        )
        response = client.create_nas_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CreateNasJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_nas_job.NasJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert response.enable_restricted_image_training is True


def test_create_nas_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_nas_job), "__call__") as call:
        client.create_nas_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CreateNasJobRequest()


@pytest.mark.asyncio
async def test_create_nas_job_async(
    transport: str = "grpc_asyncio", request_type=job_service.CreateNasJobRequest
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_nas_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_nas_job.NasJob(
                name="name_value",
                display_name="display_name_value",
                state=job_state.JobState.JOB_STATE_QUEUED,
                enable_restricted_image_training=True,
            )
        )
        response = await client.create_nas_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CreateNasJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_nas_job.NasJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert response.enable_restricted_image_training is True


@pytest.mark.asyncio
async def test_create_nas_job_async_from_dict():
    await test_create_nas_job_async(request_type=dict)


def test_create_nas_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CreateNasJobRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_nas_job), "__call__") as call:
        call.return_value = gca_nas_job.NasJob()
        client.create_nas_job(request)

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
async def test_create_nas_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CreateNasJobRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_nas_job), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gca_nas_job.NasJob())
        await client.create_nas_job(request)

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


def test_create_nas_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_nas_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_nas_job.NasJob()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_nas_job(
            parent="parent_value",
            nas_job=gca_nas_job.NasJob(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].nas_job
        mock_val = gca_nas_job.NasJob(name="name_value")
        assert arg == mock_val


def test_create_nas_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_nas_job(
            job_service.CreateNasJobRequest(),
            parent="parent_value",
            nas_job=gca_nas_job.NasJob(name="name_value"),
        )


@pytest.mark.asyncio
async def test_create_nas_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_nas_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_nas_job.NasJob()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gca_nas_job.NasJob())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_nas_job(
            parent="parent_value",
            nas_job=gca_nas_job.NasJob(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].nas_job
        mock_val = gca_nas_job.NasJob(name="name_value")
        assert arg == mock_val


@pytest.mark.asyncio
async def test_create_nas_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_nas_job(
            job_service.CreateNasJobRequest(),
            parent="parent_value",
            nas_job=gca_nas_job.NasJob(name="name_value"),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.GetNasJobRequest,
        dict,
    ],
)
def test_get_nas_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_nas_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = nas_job.NasJob(
            name="name_value",
            display_name="display_name_value",
            state=job_state.JobState.JOB_STATE_QUEUED,
            enable_restricted_image_training=True,
        )
        response = client.get_nas_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.GetNasJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, nas_job.NasJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert response.enable_restricted_image_training is True


def test_get_nas_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_nas_job), "__call__") as call:
        client.get_nas_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.GetNasJobRequest()


@pytest.mark.asyncio
async def test_get_nas_job_async(
    transport: str = "grpc_asyncio", request_type=job_service.GetNasJobRequest
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_nas_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            nas_job.NasJob(
                name="name_value",
                display_name="display_name_value",
                state=job_state.JobState.JOB_STATE_QUEUED,
                enable_restricted_image_training=True,
            )
        )
        response = await client.get_nas_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.GetNasJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, nas_job.NasJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert response.enable_restricted_image_training is True


@pytest.mark.asyncio
async def test_get_nas_job_async_from_dict():
    await test_get_nas_job_async(request_type=dict)


def test_get_nas_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.GetNasJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_nas_job), "__call__") as call:
        call.return_value = nas_job.NasJob()
        client.get_nas_job(request)

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
async def test_get_nas_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.GetNasJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_nas_job), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(nas_job.NasJob())
        await client.get_nas_job(request)

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


def test_get_nas_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_nas_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = nas_job.NasJob()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_nas_job(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_get_nas_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_nas_job(
            job_service.GetNasJobRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_get_nas_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_nas_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = nas_job.NasJob()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(nas_job.NasJob())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_nas_job(
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
async def test_get_nas_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_nas_job(
            job_service.GetNasJobRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.ListNasJobsRequest,
        dict,
    ],
)
def test_list_nas_jobs(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_nas_jobs), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListNasJobsResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_nas_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ListNasJobsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListNasJobsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_nas_jobs_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_nas_jobs), "__call__") as call:
        client.list_nas_jobs()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ListNasJobsRequest()


@pytest.mark.asyncio
async def test_list_nas_jobs_async(
    transport: str = "grpc_asyncio", request_type=job_service.ListNasJobsRequest
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_nas_jobs), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListNasJobsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_nas_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ListNasJobsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListNasJobsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_nas_jobs_async_from_dict():
    await test_list_nas_jobs_async(request_type=dict)


def test_list_nas_jobs_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.ListNasJobsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_nas_jobs), "__call__") as call:
        call.return_value = job_service.ListNasJobsResponse()
        client.list_nas_jobs(request)

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
async def test_list_nas_jobs_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.ListNasJobsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_nas_jobs), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListNasJobsResponse()
        )
        await client.list_nas_jobs(request)

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


def test_list_nas_jobs_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_nas_jobs), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListNasJobsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_nas_jobs(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_list_nas_jobs_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_nas_jobs(
            job_service.ListNasJobsRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_nas_jobs_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_nas_jobs), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListNasJobsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListNasJobsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_nas_jobs(
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
async def test_list_nas_jobs_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_nas_jobs(
            job_service.ListNasJobsRequest(),
            parent="parent_value",
        )


def test_list_nas_jobs_pager(transport_name: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_nas_jobs), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListNasJobsResponse(
                nas_jobs=[
                    nas_job.NasJob(),
                    nas_job.NasJob(),
                    nas_job.NasJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListNasJobsResponse(
                nas_jobs=[],
                next_page_token="def",
            ),
            job_service.ListNasJobsResponse(
                nas_jobs=[
                    nas_job.NasJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListNasJobsResponse(
                nas_jobs=[
                    nas_job.NasJob(),
                    nas_job.NasJob(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_nas_jobs(request={})

        assert pager._metadata == metadata

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, nas_job.NasJob) for i in results)


def test_list_nas_jobs_pages(transport_name: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_nas_jobs), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListNasJobsResponse(
                nas_jobs=[
                    nas_job.NasJob(),
                    nas_job.NasJob(),
                    nas_job.NasJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListNasJobsResponse(
                nas_jobs=[],
                next_page_token="def",
            ),
            job_service.ListNasJobsResponse(
                nas_jobs=[
                    nas_job.NasJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListNasJobsResponse(
                nas_jobs=[
                    nas_job.NasJob(),
                    nas_job.NasJob(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_nas_jobs(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_nas_jobs_async_pager():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_nas_jobs), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListNasJobsResponse(
                nas_jobs=[
                    nas_job.NasJob(),
                    nas_job.NasJob(),
                    nas_job.NasJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListNasJobsResponse(
                nas_jobs=[],
                next_page_token="def",
            ),
            job_service.ListNasJobsResponse(
                nas_jobs=[
                    nas_job.NasJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListNasJobsResponse(
                nas_jobs=[
                    nas_job.NasJob(),
                    nas_job.NasJob(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_nas_jobs(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, nas_job.NasJob) for i in responses)


@pytest.mark.asyncio
async def test_list_nas_jobs_async_pages():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_nas_jobs), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListNasJobsResponse(
                nas_jobs=[
                    nas_job.NasJob(),
                    nas_job.NasJob(),
                    nas_job.NasJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListNasJobsResponse(
                nas_jobs=[],
                next_page_token="def",
            ),
            job_service.ListNasJobsResponse(
                nas_jobs=[
                    nas_job.NasJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListNasJobsResponse(
                nas_jobs=[
                    nas_job.NasJob(),
                    nas_job.NasJob(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.list_nas_jobs(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.DeleteNasJobRequest,
        dict,
    ],
)
def test_delete_nas_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_nas_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_nas_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.DeleteNasJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_nas_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_nas_job), "__call__") as call:
        client.delete_nas_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.DeleteNasJobRequest()


@pytest.mark.asyncio
async def test_delete_nas_job_async(
    transport: str = "grpc_asyncio", request_type=job_service.DeleteNasJobRequest
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_nas_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_nas_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.DeleteNasJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_nas_job_async_from_dict():
    await test_delete_nas_job_async(request_type=dict)


def test_delete_nas_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.DeleteNasJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_nas_job), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_nas_job(request)

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
async def test_delete_nas_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.DeleteNasJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_nas_job), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_nas_job(request)

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


def test_delete_nas_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_nas_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_nas_job(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_delete_nas_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_nas_job(
            job_service.DeleteNasJobRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_nas_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_nas_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_nas_job(
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
async def test_delete_nas_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_nas_job(
            job_service.DeleteNasJobRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.CancelNasJobRequest,
        dict,
    ],
)
def test_cancel_nas_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_nas_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        response = client.cancel_nas_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CancelNasJobRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_cancel_nas_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_nas_job), "__call__") as call:
        client.cancel_nas_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CancelNasJobRequest()


@pytest.mark.asyncio
async def test_cancel_nas_job_async(
    transport: str = "grpc_asyncio", request_type=job_service.CancelNasJobRequest
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_nas_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.cancel_nas_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CancelNasJobRequest()

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_cancel_nas_job_async_from_dict():
    await test_cancel_nas_job_async(request_type=dict)


def test_cancel_nas_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CancelNasJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_nas_job), "__call__") as call:
        call.return_value = None
        client.cancel_nas_job(request)

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
async def test_cancel_nas_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CancelNasJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_nas_job), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        await client.cancel_nas_job(request)

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


def test_cancel_nas_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_nas_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.cancel_nas_job(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_cancel_nas_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.cancel_nas_job(
            job_service.CancelNasJobRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_cancel_nas_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_nas_job), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.cancel_nas_job(
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
async def test_cancel_nas_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.cancel_nas_job(
            job_service.CancelNasJobRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.GetNasTrialDetailRequest,
        dict,
    ],
)
def test_get_nas_trial_detail(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_nas_trial_detail), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = nas_job.NasTrialDetail(
            name="name_value",
            parameters="parameters_value",
        )
        response = client.get_nas_trial_detail(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.GetNasTrialDetailRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, nas_job.NasTrialDetail)
    assert response.name == "name_value"
    assert response.parameters == "parameters_value"


def test_get_nas_trial_detail_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_nas_trial_detail), "__call__"
    ) as call:
        client.get_nas_trial_detail()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.GetNasTrialDetailRequest()


@pytest.mark.asyncio
async def test_get_nas_trial_detail_async(
    transport: str = "grpc_asyncio", request_type=job_service.GetNasTrialDetailRequest
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_nas_trial_detail), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            nas_job.NasTrialDetail(
                name="name_value",
                parameters="parameters_value",
            )
        )
        response = await client.get_nas_trial_detail(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.GetNasTrialDetailRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, nas_job.NasTrialDetail)
    assert response.name == "name_value"
    assert response.parameters == "parameters_value"


@pytest.mark.asyncio
async def test_get_nas_trial_detail_async_from_dict():
    await test_get_nas_trial_detail_async(request_type=dict)


def test_get_nas_trial_detail_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.GetNasTrialDetailRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_nas_trial_detail), "__call__"
    ) as call:
        call.return_value = nas_job.NasTrialDetail()
        client.get_nas_trial_detail(request)

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
async def test_get_nas_trial_detail_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.GetNasTrialDetailRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_nas_trial_detail), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            nas_job.NasTrialDetail()
        )
        await client.get_nas_trial_detail(request)

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


def test_get_nas_trial_detail_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_nas_trial_detail), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = nas_job.NasTrialDetail()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_nas_trial_detail(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_get_nas_trial_detail_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_nas_trial_detail(
            job_service.GetNasTrialDetailRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_get_nas_trial_detail_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_nas_trial_detail), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = nas_job.NasTrialDetail()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            nas_job.NasTrialDetail()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_nas_trial_detail(
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
async def test_get_nas_trial_detail_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_nas_trial_detail(
            job_service.GetNasTrialDetailRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.ListNasTrialDetailsRequest,
        dict,
    ],
)
def test_list_nas_trial_details(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_nas_trial_details), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListNasTrialDetailsResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_nas_trial_details(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ListNasTrialDetailsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListNasTrialDetailsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_nas_trial_details_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_nas_trial_details), "__call__"
    ) as call:
        client.list_nas_trial_details()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ListNasTrialDetailsRequest()


@pytest.mark.asyncio
async def test_list_nas_trial_details_async(
    transport: str = "grpc_asyncio", request_type=job_service.ListNasTrialDetailsRequest
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_nas_trial_details), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListNasTrialDetailsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_nas_trial_details(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ListNasTrialDetailsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListNasTrialDetailsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_nas_trial_details_async_from_dict():
    await test_list_nas_trial_details_async(request_type=dict)


def test_list_nas_trial_details_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.ListNasTrialDetailsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_nas_trial_details), "__call__"
    ) as call:
        call.return_value = job_service.ListNasTrialDetailsResponse()
        client.list_nas_trial_details(request)

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
async def test_list_nas_trial_details_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.ListNasTrialDetailsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_nas_trial_details), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListNasTrialDetailsResponse()
        )
        await client.list_nas_trial_details(request)

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


def test_list_nas_trial_details_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_nas_trial_details), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListNasTrialDetailsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_nas_trial_details(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_list_nas_trial_details_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_nas_trial_details(
            job_service.ListNasTrialDetailsRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_nas_trial_details_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_nas_trial_details), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListNasTrialDetailsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListNasTrialDetailsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_nas_trial_details(
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
async def test_list_nas_trial_details_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_nas_trial_details(
            job_service.ListNasTrialDetailsRequest(),
            parent="parent_value",
        )


def test_list_nas_trial_details_pager(transport_name: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_nas_trial_details), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListNasTrialDetailsResponse(
                nas_trial_details=[
                    nas_job.NasTrialDetail(),
                    nas_job.NasTrialDetail(),
                    nas_job.NasTrialDetail(),
                ],
                next_page_token="abc",
            ),
            job_service.ListNasTrialDetailsResponse(
                nas_trial_details=[],
                next_page_token="def",
            ),
            job_service.ListNasTrialDetailsResponse(
                nas_trial_details=[
                    nas_job.NasTrialDetail(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListNasTrialDetailsResponse(
                nas_trial_details=[
                    nas_job.NasTrialDetail(),
                    nas_job.NasTrialDetail(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_nas_trial_details(request={})

        assert pager._metadata == metadata

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, nas_job.NasTrialDetail) for i in results)


def test_list_nas_trial_details_pages(transport_name: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_nas_trial_details), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListNasTrialDetailsResponse(
                nas_trial_details=[
                    nas_job.NasTrialDetail(),
                    nas_job.NasTrialDetail(),
                    nas_job.NasTrialDetail(),
                ],
                next_page_token="abc",
            ),
            job_service.ListNasTrialDetailsResponse(
                nas_trial_details=[],
                next_page_token="def",
            ),
            job_service.ListNasTrialDetailsResponse(
                nas_trial_details=[
                    nas_job.NasTrialDetail(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListNasTrialDetailsResponse(
                nas_trial_details=[
                    nas_job.NasTrialDetail(),
                    nas_job.NasTrialDetail(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_nas_trial_details(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_nas_trial_details_async_pager():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_nas_trial_details),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListNasTrialDetailsResponse(
                nas_trial_details=[
                    nas_job.NasTrialDetail(),
                    nas_job.NasTrialDetail(),
                    nas_job.NasTrialDetail(),
                ],
                next_page_token="abc",
            ),
            job_service.ListNasTrialDetailsResponse(
                nas_trial_details=[],
                next_page_token="def",
            ),
            job_service.ListNasTrialDetailsResponse(
                nas_trial_details=[
                    nas_job.NasTrialDetail(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListNasTrialDetailsResponse(
                nas_trial_details=[
                    nas_job.NasTrialDetail(),
                    nas_job.NasTrialDetail(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_nas_trial_details(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, nas_job.NasTrialDetail) for i in responses)


@pytest.mark.asyncio
async def test_list_nas_trial_details_async_pages():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_nas_trial_details),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListNasTrialDetailsResponse(
                nas_trial_details=[
                    nas_job.NasTrialDetail(),
                    nas_job.NasTrialDetail(),
                    nas_job.NasTrialDetail(),
                ],
                next_page_token="abc",
            ),
            job_service.ListNasTrialDetailsResponse(
                nas_trial_details=[],
                next_page_token="def",
            ),
            job_service.ListNasTrialDetailsResponse(
                nas_trial_details=[
                    nas_job.NasTrialDetail(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListNasTrialDetailsResponse(
                nas_trial_details=[
                    nas_job.NasTrialDetail(),
                    nas_job.NasTrialDetail(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.list_nas_trial_details(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.CreateBatchPredictionJobRequest,
        dict,
    ],
)
def test_create_batch_prediction_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_batch_prediction_job.BatchPredictionJob(
            name="name_value",
            display_name="display_name_value",
            model="model_value",
            model_version_id="model_version_id_value",
            service_account="service_account_value",
            generate_explanation=True,
            state=job_state.JobState.JOB_STATE_QUEUED,
            disable_container_logging=True,
        )
        response = client.create_batch_prediction_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CreateBatchPredictionJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_batch_prediction_job.BatchPredictionJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.model == "model_value"
    assert response.model_version_id == "model_version_id_value"
    assert response.service_account == "service_account_value"
    assert response.generate_explanation is True
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert response.disable_container_logging is True


def test_create_batch_prediction_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_batch_prediction_job), "__call__"
    ) as call:
        client.create_batch_prediction_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CreateBatchPredictionJobRequest()


@pytest.mark.asyncio
async def test_create_batch_prediction_job_async(
    transport: str = "grpc_asyncio",
    request_type=job_service.CreateBatchPredictionJobRequest,
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_batch_prediction_job.BatchPredictionJob(
                name="name_value",
                display_name="display_name_value",
                model="model_value",
                model_version_id="model_version_id_value",
                service_account="service_account_value",
                generate_explanation=True,
                state=job_state.JobState.JOB_STATE_QUEUED,
                disable_container_logging=True,
            )
        )
        response = await client.create_batch_prediction_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CreateBatchPredictionJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_batch_prediction_job.BatchPredictionJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.model == "model_value"
    assert response.model_version_id == "model_version_id_value"
    assert response.service_account == "service_account_value"
    assert response.generate_explanation is True
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert response.disable_container_logging is True


@pytest.mark.asyncio
async def test_create_batch_prediction_job_async_from_dict():
    await test_create_batch_prediction_job_async(request_type=dict)


def test_create_batch_prediction_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CreateBatchPredictionJobRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_batch_prediction_job), "__call__"
    ) as call:
        call.return_value = gca_batch_prediction_job.BatchPredictionJob()
        client.create_batch_prediction_job(request)

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
async def test_create_batch_prediction_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CreateBatchPredictionJobRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_batch_prediction_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_batch_prediction_job.BatchPredictionJob()
        )
        await client.create_batch_prediction_job(request)

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


def test_create_batch_prediction_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_batch_prediction_job.BatchPredictionJob()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_batch_prediction_job(
            parent="parent_value",
            batch_prediction_job=gca_batch_prediction_job.BatchPredictionJob(
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
        arg = args[0].batch_prediction_job
        mock_val = gca_batch_prediction_job.BatchPredictionJob(name="name_value")
        assert arg == mock_val


def test_create_batch_prediction_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_batch_prediction_job(
            job_service.CreateBatchPredictionJobRequest(),
            parent="parent_value",
            batch_prediction_job=gca_batch_prediction_job.BatchPredictionJob(
                name="name_value"
            ),
        )


@pytest.mark.asyncio
async def test_create_batch_prediction_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_batch_prediction_job.BatchPredictionJob()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_batch_prediction_job.BatchPredictionJob()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_batch_prediction_job(
            parent="parent_value",
            batch_prediction_job=gca_batch_prediction_job.BatchPredictionJob(
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
        arg = args[0].batch_prediction_job
        mock_val = gca_batch_prediction_job.BatchPredictionJob(name="name_value")
        assert arg == mock_val


@pytest.mark.asyncio
async def test_create_batch_prediction_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_batch_prediction_job(
            job_service.CreateBatchPredictionJobRequest(),
            parent="parent_value",
            batch_prediction_job=gca_batch_prediction_job.BatchPredictionJob(
                name="name_value"
            ),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.GetBatchPredictionJobRequest,
        dict,
    ],
)
def test_get_batch_prediction_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = batch_prediction_job.BatchPredictionJob(
            name="name_value",
            display_name="display_name_value",
            model="model_value",
            model_version_id="model_version_id_value",
            service_account="service_account_value",
            generate_explanation=True,
            state=job_state.JobState.JOB_STATE_QUEUED,
            disable_container_logging=True,
        )
        response = client.get_batch_prediction_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.GetBatchPredictionJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, batch_prediction_job.BatchPredictionJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.model == "model_value"
    assert response.model_version_id == "model_version_id_value"
    assert response.service_account == "service_account_value"
    assert response.generate_explanation is True
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert response.disable_container_logging is True


def test_get_batch_prediction_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_batch_prediction_job), "__call__"
    ) as call:
        client.get_batch_prediction_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.GetBatchPredictionJobRequest()


@pytest.mark.asyncio
async def test_get_batch_prediction_job_async(
    transport: str = "grpc_asyncio",
    request_type=job_service.GetBatchPredictionJobRequest,
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            batch_prediction_job.BatchPredictionJob(
                name="name_value",
                display_name="display_name_value",
                model="model_value",
                model_version_id="model_version_id_value",
                service_account="service_account_value",
                generate_explanation=True,
                state=job_state.JobState.JOB_STATE_QUEUED,
                disable_container_logging=True,
            )
        )
        response = await client.get_batch_prediction_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.GetBatchPredictionJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, batch_prediction_job.BatchPredictionJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.model == "model_value"
    assert response.model_version_id == "model_version_id_value"
    assert response.service_account == "service_account_value"
    assert response.generate_explanation is True
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert response.disable_container_logging is True


@pytest.mark.asyncio
async def test_get_batch_prediction_job_async_from_dict():
    await test_get_batch_prediction_job_async(request_type=dict)


def test_get_batch_prediction_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.GetBatchPredictionJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_batch_prediction_job), "__call__"
    ) as call:
        call.return_value = batch_prediction_job.BatchPredictionJob()
        client.get_batch_prediction_job(request)

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
async def test_get_batch_prediction_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.GetBatchPredictionJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_batch_prediction_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            batch_prediction_job.BatchPredictionJob()
        )
        await client.get_batch_prediction_job(request)

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


def test_get_batch_prediction_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = batch_prediction_job.BatchPredictionJob()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_batch_prediction_job(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_get_batch_prediction_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_batch_prediction_job(
            job_service.GetBatchPredictionJobRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_get_batch_prediction_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = batch_prediction_job.BatchPredictionJob()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            batch_prediction_job.BatchPredictionJob()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_batch_prediction_job(
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
async def test_get_batch_prediction_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_batch_prediction_job(
            job_service.GetBatchPredictionJobRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.ListBatchPredictionJobsRequest,
        dict,
    ],
)
def test_list_batch_prediction_jobs(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_batch_prediction_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListBatchPredictionJobsResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_batch_prediction_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ListBatchPredictionJobsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListBatchPredictionJobsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_batch_prediction_jobs_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_batch_prediction_jobs), "__call__"
    ) as call:
        client.list_batch_prediction_jobs()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ListBatchPredictionJobsRequest()


@pytest.mark.asyncio
async def test_list_batch_prediction_jobs_async(
    transport: str = "grpc_asyncio",
    request_type=job_service.ListBatchPredictionJobsRequest,
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_batch_prediction_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListBatchPredictionJobsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_batch_prediction_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ListBatchPredictionJobsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListBatchPredictionJobsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_batch_prediction_jobs_async_from_dict():
    await test_list_batch_prediction_jobs_async(request_type=dict)


def test_list_batch_prediction_jobs_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.ListBatchPredictionJobsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_batch_prediction_jobs), "__call__"
    ) as call:
        call.return_value = job_service.ListBatchPredictionJobsResponse()
        client.list_batch_prediction_jobs(request)

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
async def test_list_batch_prediction_jobs_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.ListBatchPredictionJobsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_batch_prediction_jobs), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListBatchPredictionJobsResponse()
        )
        await client.list_batch_prediction_jobs(request)

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


def test_list_batch_prediction_jobs_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_batch_prediction_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListBatchPredictionJobsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_batch_prediction_jobs(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_list_batch_prediction_jobs_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_batch_prediction_jobs(
            job_service.ListBatchPredictionJobsRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_batch_prediction_jobs_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_batch_prediction_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListBatchPredictionJobsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListBatchPredictionJobsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_batch_prediction_jobs(
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
async def test_list_batch_prediction_jobs_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_batch_prediction_jobs(
            job_service.ListBatchPredictionJobsRequest(),
            parent="parent_value",
        )


def test_list_batch_prediction_jobs_pager(transport_name: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_batch_prediction_jobs), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[
                    batch_prediction_job.BatchPredictionJob(),
                    batch_prediction_job.BatchPredictionJob(),
                    batch_prediction_job.BatchPredictionJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[],
                next_page_token="def",
            ),
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[
                    batch_prediction_job.BatchPredictionJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[
                    batch_prediction_job.BatchPredictionJob(),
                    batch_prediction_job.BatchPredictionJob(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_batch_prediction_jobs(request={})

        assert pager._metadata == metadata

        results = list(pager)
        assert len(results) == 6
        assert all(
            isinstance(i, batch_prediction_job.BatchPredictionJob) for i in results
        )


def test_list_batch_prediction_jobs_pages(transport_name: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_batch_prediction_jobs), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[
                    batch_prediction_job.BatchPredictionJob(),
                    batch_prediction_job.BatchPredictionJob(),
                    batch_prediction_job.BatchPredictionJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[],
                next_page_token="def",
            ),
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[
                    batch_prediction_job.BatchPredictionJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[
                    batch_prediction_job.BatchPredictionJob(),
                    batch_prediction_job.BatchPredictionJob(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_batch_prediction_jobs(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_batch_prediction_jobs_async_pager():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_batch_prediction_jobs),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[
                    batch_prediction_job.BatchPredictionJob(),
                    batch_prediction_job.BatchPredictionJob(),
                    batch_prediction_job.BatchPredictionJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[],
                next_page_token="def",
            ),
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[
                    batch_prediction_job.BatchPredictionJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[
                    batch_prediction_job.BatchPredictionJob(),
                    batch_prediction_job.BatchPredictionJob(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_batch_prediction_jobs(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(
            isinstance(i, batch_prediction_job.BatchPredictionJob) for i in responses
        )


@pytest.mark.asyncio
async def test_list_batch_prediction_jobs_async_pages():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_batch_prediction_jobs),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[
                    batch_prediction_job.BatchPredictionJob(),
                    batch_prediction_job.BatchPredictionJob(),
                    batch_prediction_job.BatchPredictionJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[],
                next_page_token="def",
            ),
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[
                    batch_prediction_job.BatchPredictionJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[
                    batch_prediction_job.BatchPredictionJob(),
                    batch_prediction_job.BatchPredictionJob(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.list_batch_prediction_jobs(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.DeleteBatchPredictionJobRequest,
        dict,
    ],
)
def test_delete_batch_prediction_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_batch_prediction_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.DeleteBatchPredictionJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_batch_prediction_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_batch_prediction_job), "__call__"
    ) as call:
        client.delete_batch_prediction_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.DeleteBatchPredictionJobRequest()


@pytest.mark.asyncio
async def test_delete_batch_prediction_job_async(
    transport: str = "grpc_asyncio",
    request_type=job_service.DeleteBatchPredictionJobRequest,
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_batch_prediction_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.DeleteBatchPredictionJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_batch_prediction_job_async_from_dict():
    await test_delete_batch_prediction_job_async(request_type=dict)


def test_delete_batch_prediction_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.DeleteBatchPredictionJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_batch_prediction_job), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_batch_prediction_job(request)

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
async def test_delete_batch_prediction_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.DeleteBatchPredictionJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_batch_prediction_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_batch_prediction_job(request)

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


def test_delete_batch_prediction_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_batch_prediction_job(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_delete_batch_prediction_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_batch_prediction_job(
            job_service.DeleteBatchPredictionJobRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_batch_prediction_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_batch_prediction_job(
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
async def test_delete_batch_prediction_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_batch_prediction_job(
            job_service.DeleteBatchPredictionJobRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.CancelBatchPredictionJobRequest,
        dict,
    ],
)
def test_cancel_batch_prediction_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        response = client.cancel_batch_prediction_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CancelBatchPredictionJobRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_cancel_batch_prediction_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_batch_prediction_job), "__call__"
    ) as call:
        client.cancel_batch_prediction_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CancelBatchPredictionJobRequest()


@pytest.mark.asyncio
async def test_cancel_batch_prediction_job_async(
    transport: str = "grpc_asyncio",
    request_type=job_service.CancelBatchPredictionJobRequest,
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.cancel_batch_prediction_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CancelBatchPredictionJobRequest()

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_cancel_batch_prediction_job_async_from_dict():
    await test_cancel_batch_prediction_job_async(request_type=dict)


def test_cancel_batch_prediction_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CancelBatchPredictionJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_batch_prediction_job), "__call__"
    ) as call:
        call.return_value = None
        client.cancel_batch_prediction_job(request)

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
async def test_cancel_batch_prediction_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CancelBatchPredictionJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_batch_prediction_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        await client.cancel_batch_prediction_job(request)

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


def test_cancel_batch_prediction_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.cancel_batch_prediction_job(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_cancel_batch_prediction_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.cancel_batch_prediction_job(
            job_service.CancelBatchPredictionJobRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_cancel_batch_prediction_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.cancel_batch_prediction_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.cancel_batch_prediction_job(
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
async def test_cancel_batch_prediction_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.cancel_batch_prediction_job(
            job_service.CancelBatchPredictionJobRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.CreateModelDeploymentMonitoringJobRequest,
        dict,
    ],
)
def test_create_model_deployment_monitoring_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob(
            name="name_value",
            display_name="display_name_value",
            endpoint="endpoint_value",
            state=job_state.JobState.JOB_STATE_QUEUED,
            schedule_state=gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob.MonitoringScheduleState.PENDING,
            predict_instance_schema_uri="predict_instance_schema_uri_value",
            analysis_instance_schema_uri="analysis_instance_schema_uri_value",
            enable_monitoring_pipeline_logs=True,
        )
        response = client.create_model_deployment_monitoring_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CreateModelDeploymentMonitoringJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob
    )
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.endpoint == "endpoint_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert (
        response.schedule_state
        == gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob.MonitoringScheduleState.PENDING
    )
    assert response.predict_instance_schema_uri == "predict_instance_schema_uri_value"
    assert response.analysis_instance_schema_uri == "analysis_instance_schema_uri_value"
    assert response.enable_monitoring_pipeline_logs is True


def test_create_model_deployment_monitoring_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_model_deployment_monitoring_job), "__call__"
    ) as call:
        client.create_model_deployment_monitoring_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CreateModelDeploymentMonitoringJobRequest()


@pytest.mark.asyncio
async def test_create_model_deployment_monitoring_job_async(
    transport: str = "grpc_asyncio",
    request_type=job_service.CreateModelDeploymentMonitoringJobRequest,
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob(
                name="name_value",
                display_name="display_name_value",
                endpoint="endpoint_value",
                state=job_state.JobState.JOB_STATE_QUEUED,
                schedule_state=gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob.MonitoringScheduleState.PENDING,
                predict_instance_schema_uri="predict_instance_schema_uri_value",
                analysis_instance_schema_uri="analysis_instance_schema_uri_value",
                enable_monitoring_pipeline_logs=True,
            )
        )
        response = await client.create_model_deployment_monitoring_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.CreateModelDeploymentMonitoringJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob
    )
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.endpoint == "endpoint_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert (
        response.schedule_state
        == gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob.MonitoringScheduleState.PENDING
    )
    assert response.predict_instance_schema_uri == "predict_instance_schema_uri_value"
    assert response.analysis_instance_schema_uri == "analysis_instance_schema_uri_value"
    assert response.enable_monitoring_pipeline_logs is True


@pytest.mark.asyncio
async def test_create_model_deployment_monitoring_job_async_from_dict():
    await test_create_model_deployment_monitoring_job_async(request_type=dict)


def test_create_model_deployment_monitoring_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CreateModelDeploymentMonitoringJobRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_model_deployment_monitoring_job), "__call__"
    ) as call:
        call.return_value = (
            gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob()
        )
        client.create_model_deployment_monitoring_job(request)

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
async def test_create_model_deployment_monitoring_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.CreateModelDeploymentMonitoringJobRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_model_deployment_monitoring_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob()
        )
        await client.create_model_deployment_monitoring_job(request)

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


def test_create_model_deployment_monitoring_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_model_deployment_monitoring_job(
            parent="parent_value",
            model_deployment_monitoring_job=gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob(
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
        arg = args[0].model_deployment_monitoring_job
        mock_val = gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob(
            name="name_value"
        )
        assert arg == mock_val


def test_create_model_deployment_monitoring_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_model_deployment_monitoring_job(
            job_service.CreateModelDeploymentMonitoringJobRequest(),
            parent="parent_value",
            model_deployment_monitoring_job=gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob(
                name="name_value"
            ),
        )


@pytest.mark.asyncio
async def test_create_model_deployment_monitoring_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob()
        )

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_model_deployment_monitoring_job(
            parent="parent_value",
            model_deployment_monitoring_job=gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob(
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
        arg = args[0].model_deployment_monitoring_job
        mock_val = gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob(
            name="name_value"
        )
        assert arg == mock_val


@pytest.mark.asyncio
async def test_create_model_deployment_monitoring_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_model_deployment_monitoring_job(
            job_service.CreateModelDeploymentMonitoringJobRequest(),
            parent="parent_value",
            model_deployment_monitoring_job=gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob(
                name="name_value"
            ),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest,
        dict,
    ],
)
def test_search_model_deployment_monitoring_stats_anomalies(
    request_type, transport: str = "grpc"
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_model_deployment_monitoring_stats_anomalies),
        "__call__",
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = client.search_model_deployment_monitoring_stats_anomalies(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert (
            args[0]
            == job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest()
        )

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, pagers.SearchModelDeploymentMonitoringStatsAnomaliesPager
    )
    assert response.next_page_token == "next_page_token_value"


def test_search_model_deployment_monitoring_stats_anomalies_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_model_deployment_monitoring_stats_anomalies),
        "__call__",
    ) as call:
        client.search_model_deployment_monitoring_stats_anomalies()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert (
            args[0]
            == job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest()
        )


@pytest.mark.asyncio
async def test_search_model_deployment_monitoring_stats_anomalies_async(
    transport: str = "grpc_asyncio",
    request_type=job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest,
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_model_deployment_monitoring_stats_anomalies),
        "__call__",
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.search_model_deployment_monitoring_stats_anomalies(
            request
        )

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert (
            args[0]
            == job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest()
        )

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, pagers.SearchModelDeploymentMonitoringStatsAnomaliesAsyncPager
    )
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_search_model_deployment_monitoring_stats_anomalies_async_from_dict():
    await test_search_model_deployment_monitoring_stats_anomalies_async(
        request_type=dict
    )


def test_search_model_deployment_monitoring_stats_anomalies_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest()

    request.model_deployment_monitoring_job = "model_deployment_monitoring_job_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_model_deployment_monitoring_stats_anomalies),
        "__call__",
    ) as call:
        call.return_value = (
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse()
        )
        client.search_model_deployment_monitoring_stats_anomalies(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "model_deployment_monitoring_job=model_deployment_monitoring_job_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_search_model_deployment_monitoring_stats_anomalies_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest()

    request.model_deployment_monitoring_job = "model_deployment_monitoring_job_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_model_deployment_monitoring_stats_anomalies),
        "__call__",
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse()
        )
        await client.search_model_deployment_monitoring_stats_anomalies(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "model_deployment_monitoring_job=model_deployment_monitoring_job_value",
    ) in kw["metadata"]


def test_search_model_deployment_monitoring_stats_anomalies_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_model_deployment_monitoring_stats_anomalies),
        "__call__",
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.search_model_deployment_monitoring_stats_anomalies(
            model_deployment_monitoring_job="model_deployment_monitoring_job_value",
            deployed_model_id="deployed_model_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].model_deployment_monitoring_job
        mock_val = "model_deployment_monitoring_job_value"
        assert arg == mock_val
        arg = args[0].deployed_model_id
        mock_val = "deployed_model_id_value"
        assert arg == mock_val


def test_search_model_deployment_monitoring_stats_anomalies_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.search_model_deployment_monitoring_stats_anomalies(
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest(),
            model_deployment_monitoring_job="model_deployment_monitoring_job_value",
            deployed_model_id="deployed_model_id_value",
        )


@pytest.mark.asyncio
async def test_search_model_deployment_monitoring_stats_anomalies_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_model_deployment_monitoring_stats_anomalies),
        "__call__",
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse()
        )

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.search_model_deployment_monitoring_stats_anomalies(
            model_deployment_monitoring_job="model_deployment_monitoring_job_value",
            deployed_model_id="deployed_model_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].model_deployment_monitoring_job
        mock_val = "model_deployment_monitoring_job_value"
        assert arg == mock_val
        arg = args[0].deployed_model_id
        mock_val = "deployed_model_id_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_search_model_deployment_monitoring_stats_anomalies_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.search_model_deployment_monitoring_stats_anomalies(
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest(),
            model_deployment_monitoring_job="model_deployment_monitoring_job_value",
            deployed_model_id="deployed_model_id_value",
        )


def test_search_model_deployment_monitoring_stats_anomalies_pager(
    transport_name: str = "grpc",
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_model_deployment_monitoring_stats_anomalies),
        "__call__",
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                monitoring_stats=[
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                ],
                next_page_token="abc",
            ),
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                monitoring_stats=[],
                next_page_token="def",
            ),
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                monitoring_stats=[
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                ],
                next_page_token="ghi",
            ),
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                monitoring_stats=[
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata(
                (("model_deployment_monitoring_job", ""),)
            ),
        )
        pager = client.search_model_deployment_monitoring_stats_anomalies(request={})

        assert pager._metadata == metadata

        results = list(pager)
        assert len(results) == 6
        assert all(
            isinstance(
                i, gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies
            )
            for i in results
        )


def test_search_model_deployment_monitoring_stats_anomalies_pages(
    transport_name: str = "grpc",
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_model_deployment_monitoring_stats_anomalies),
        "__call__",
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                monitoring_stats=[
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                ],
                next_page_token="abc",
            ),
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                monitoring_stats=[],
                next_page_token="def",
            ),
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                monitoring_stats=[
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                ],
                next_page_token="ghi",
            ),
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                monitoring_stats=[
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                ],
            ),
            RuntimeError,
        )
        pages = list(
            client.search_model_deployment_monitoring_stats_anomalies(request={}).pages
        )
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_search_model_deployment_monitoring_stats_anomalies_async_pager():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_model_deployment_monitoring_stats_anomalies),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                monitoring_stats=[
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                ],
                next_page_token="abc",
            ),
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                monitoring_stats=[],
                next_page_token="def",
            ),
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                monitoring_stats=[
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                ],
                next_page_token="ghi",
            ),
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                monitoring_stats=[
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.search_model_deployment_monitoring_stats_anomalies(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(
            isinstance(
                i, gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies
            )
            for i in responses
        )


@pytest.mark.asyncio
async def test_search_model_deployment_monitoring_stats_anomalies_async_pages():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_model_deployment_monitoring_stats_anomalies),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                monitoring_stats=[
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                ],
                next_page_token="abc",
            ),
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                monitoring_stats=[],
                next_page_token="def",
            ),
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                monitoring_stats=[
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                ],
                next_page_token="ghi",
            ),
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                monitoring_stats=[
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.search_model_deployment_monitoring_stats_anomalies(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.GetModelDeploymentMonitoringJobRequest,
        dict,
    ],
)
def test_get_model_deployment_monitoring_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = model_deployment_monitoring_job.ModelDeploymentMonitoringJob(
            name="name_value",
            display_name="display_name_value",
            endpoint="endpoint_value",
            state=job_state.JobState.JOB_STATE_QUEUED,
            schedule_state=model_deployment_monitoring_job.ModelDeploymentMonitoringJob.MonitoringScheduleState.PENDING,
            predict_instance_schema_uri="predict_instance_schema_uri_value",
            analysis_instance_schema_uri="analysis_instance_schema_uri_value",
            enable_monitoring_pipeline_logs=True,
        )
        response = client.get_model_deployment_monitoring_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.GetModelDeploymentMonitoringJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, model_deployment_monitoring_job.ModelDeploymentMonitoringJob
    )
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.endpoint == "endpoint_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert (
        response.schedule_state
        == model_deployment_monitoring_job.ModelDeploymentMonitoringJob.MonitoringScheduleState.PENDING
    )
    assert response.predict_instance_schema_uri == "predict_instance_schema_uri_value"
    assert response.analysis_instance_schema_uri == "analysis_instance_schema_uri_value"
    assert response.enable_monitoring_pipeline_logs is True


def test_get_model_deployment_monitoring_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_model_deployment_monitoring_job), "__call__"
    ) as call:
        client.get_model_deployment_monitoring_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.GetModelDeploymentMonitoringJobRequest()


@pytest.mark.asyncio
async def test_get_model_deployment_monitoring_job_async(
    transport: str = "grpc_asyncio",
    request_type=job_service.GetModelDeploymentMonitoringJobRequest,
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            model_deployment_monitoring_job.ModelDeploymentMonitoringJob(
                name="name_value",
                display_name="display_name_value",
                endpoint="endpoint_value",
                state=job_state.JobState.JOB_STATE_QUEUED,
                schedule_state=model_deployment_monitoring_job.ModelDeploymentMonitoringJob.MonitoringScheduleState.PENDING,
                predict_instance_schema_uri="predict_instance_schema_uri_value",
                analysis_instance_schema_uri="analysis_instance_schema_uri_value",
                enable_monitoring_pipeline_logs=True,
            )
        )
        response = await client.get_model_deployment_monitoring_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.GetModelDeploymentMonitoringJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, model_deployment_monitoring_job.ModelDeploymentMonitoringJob
    )
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.endpoint == "endpoint_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert (
        response.schedule_state
        == model_deployment_monitoring_job.ModelDeploymentMonitoringJob.MonitoringScheduleState.PENDING
    )
    assert response.predict_instance_schema_uri == "predict_instance_schema_uri_value"
    assert response.analysis_instance_schema_uri == "analysis_instance_schema_uri_value"
    assert response.enable_monitoring_pipeline_logs is True


@pytest.mark.asyncio
async def test_get_model_deployment_monitoring_job_async_from_dict():
    await test_get_model_deployment_monitoring_job_async(request_type=dict)


def test_get_model_deployment_monitoring_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.GetModelDeploymentMonitoringJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_model_deployment_monitoring_job), "__call__"
    ) as call:
        call.return_value = (
            model_deployment_monitoring_job.ModelDeploymentMonitoringJob()
        )
        client.get_model_deployment_monitoring_job(request)

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
async def test_get_model_deployment_monitoring_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.GetModelDeploymentMonitoringJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_model_deployment_monitoring_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            model_deployment_monitoring_job.ModelDeploymentMonitoringJob()
        )
        await client.get_model_deployment_monitoring_job(request)

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


def test_get_model_deployment_monitoring_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            model_deployment_monitoring_job.ModelDeploymentMonitoringJob()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_model_deployment_monitoring_job(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_get_model_deployment_monitoring_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_model_deployment_monitoring_job(
            job_service.GetModelDeploymentMonitoringJobRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_get_model_deployment_monitoring_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            model_deployment_monitoring_job.ModelDeploymentMonitoringJob()
        )

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            model_deployment_monitoring_job.ModelDeploymentMonitoringJob()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_model_deployment_monitoring_job(
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
async def test_get_model_deployment_monitoring_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_model_deployment_monitoring_job(
            job_service.GetModelDeploymentMonitoringJobRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.ListModelDeploymentMonitoringJobsRequest,
        dict,
    ],
)
def test_list_model_deployment_monitoring_jobs(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_model_deployment_monitoring_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListModelDeploymentMonitoringJobsResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_model_deployment_monitoring_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ListModelDeploymentMonitoringJobsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListModelDeploymentMonitoringJobsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_model_deployment_monitoring_jobs_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_model_deployment_monitoring_jobs), "__call__"
    ) as call:
        client.list_model_deployment_monitoring_jobs()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ListModelDeploymentMonitoringJobsRequest()


@pytest.mark.asyncio
async def test_list_model_deployment_monitoring_jobs_async(
    transport: str = "grpc_asyncio",
    request_type=job_service.ListModelDeploymentMonitoringJobsRequest,
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_model_deployment_monitoring_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListModelDeploymentMonitoringJobsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_model_deployment_monitoring_jobs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ListModelDeploymentMonitoringJobsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListModelDeploymentMonitoringJobsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_model_deployment_monitoring_jobs_async_from_dict():
    await test_list_model_deployment_monitoring_jobs_async(request_type=dict)


def test_list_model_deployment_monitoring_jobs_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.ListModelDeploymentMonitoringJobsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_model_deployment_monitoring_jobs), "__call__"
    ) as call:
        call.return_value = job_service.ListModelDeploymentMonitoringJobsResponse()
        client.list_model_deployment_monitoring_jobs(request)

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
async def test_list_model_deployment_monitoring_jobs_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.ListModelDeploymentMonitoringJobsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_model_deployment_monitoring_jobs), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListModelDeploymentMonitoringJobsResponse()
        )
        await client.list_model_deployment_monitoring_jobs(request)

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


def test_list_model_deployment_monitoring_jobs_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_model_deployment_monitoring_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListModelDeploymentMonitoringJobsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_model_deployment_monitoring_jobs(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_list_model_deployment_monitoring_jobs_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_model_deployment_monitoring_jobs(
            job_service.ListModelDeploymentMonitoringJobsRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_model_deployment_monitoring_jobs_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_model_deployment_monitoring_jobs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = job_service.ListModelDeploymentMonitoringJobsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            job_service.ListModelDeploymentMonitoringJobsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_model_deployment_monitoring_jobs(
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
async def test_list_model_deployment_monitoring_jobs_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_model_deployment_monitoring_jobs(
            job_service.ListModelDeploymentMonitoringJobsRequest(),
            parent="parent_value",
        )


def test_list_model_deployment_monitoring_jobs_pager(transport_name: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_model_deployment_monitoring_jobs), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListModelDeploymentMonitoringJobsResponse(
                model_deployment_monitoring_jobs=[
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListModelDeploymentMonitoringJobsResponse(
                model_deployment_monitoring_jobs=[],
                next_page_token="def",
            ),
            job_service.ListModelDeploymentMonitoringJobsResponse(
                model_deployment_monitoring_jobs=[
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListModelDeploymentMonitoringJobsResponse(
                model_deployment_monitoring_jobs=[
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_model_deployment_monitoring_jobs(request={})

        assert pager._metadata == metadata

        results = list(pager)
        assert len(results) == 6
        assert all(
            isinstance(i, model_deployment_monitoring_job.ModelDeploymentMonitoringJob)
            for i in results
        )


def test_list_model_deployment_monitoring_jobs_pages(transport_name: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_model_deployment_monitoring_jobs), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListModelDeploymentMonitoringJobsResponse(
                model_deployment_monitoring_jobs=[
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListModelDeploymentMonitoringJobsResponse(
                model_deployment_monitoring_jobs=[],
                next_page_token="def",
            ),
            job_service.ListModelDeploymentMonitoringJobsResponse(
                model_deployment_monitoring_jobs=[
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListModelDeploymentMonitoringJobsResponse(
                model_deployment_monitoring_jobs=[
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_model_deployment_monitoring_jobs(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_model_deployment_monitoring_jobs_async_pager():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_model_deployment_monitoring_jobs),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListModelDeploymentMonitoringJobsResponse(
                model_deployment_monitoring_jobs=[
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListModelDeploymentMonitoringJobsResponse(
                model_deployment_monitoring_jobs=[],
                next_page_token="def",
            ),
            job_service.ListModelDeploymentMonitoringJobsResponse(
                model_deployment_monitoring_jobs=[
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListModelDeploymentMonitoringJobsResponse(
                model_deployment_monitoring_jobs=[
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_model_deployment_monitoring_jobs(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(
            isinstance(i, model_deployment_monitoring_job.ModelDeploymentMonitoringJob)
            for i in responses
        )


@pytest.mark.asyncio
async def test_list_model_deployment_monitoring_jobs_async_pages():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_model_deployment_monitoring_jobs),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            job_service.ListModelDeploymentMonitoringJobsResponse(
                model_deployment_monitoring_jobs=[
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListModelDeploymentMonitoringJobsResponse(
                model_deployment_monitoring_jobs=[],
                next_page_token="def",
            ),
            job_service.ListModelDeploymentMonitoringJobsResponse(
                model_deployment_monitoring_jobs=[
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListModelDeploymentMonitoringJobsResponse(
                model_deployment_monitoring_jobs=[
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.list_model_deployment_monitoring_jobs(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.UpdateModelDeploymentMonitoringJobRequest,
        dict,
    ],
)
def test_update_model_deployment_monitoring_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.update_model_deployment_monitoring_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.UpdateModelDeploymentMonitoringJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_update_model_deployment_monitoring_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_model_deployment_monitoring_job), "__call__"
    ) as call:
        client.update_model_deployment_monitoring_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.UpdateModelDeploymentMonitoringJobRequest()


@pytest.mark.asyncio
async def test_update_model_deployment_monitoring_job_async(
    transport: str = "grpc_asyncio",
    request_type=job_service.UpdateModelDeploymentMonitoringJobRequest,
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.update_model_deployment_monitoring_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.UpdateModelDeploymentMonitoringJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_update_model_deployment_monitoring_job_async_from_dict():
    await test_update_model_deployment_monitoring_job_async(request_type=dict)


def test_update_model_deployment_monitoring_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.UpdateModelDeploymentMonitoringJobRequest()

    request.model_deployment_monitoring_job.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_model_deployment_monitoring_job), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.update_model_deployment_monitoring_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "model_deployment_monitoring_job.name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_model_deployment_monitoring_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.UpdateModelDeploymentMonitoringJobRequest()

    request.model_deployment_monitoring_job.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_model_deployment_monitoring_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.update_model_deployment_monitoring_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "model_deployment_monitoring_job.name=name_value",
    ) in kw["metadata"]


def test_update_model_deployment_monitoring_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_model_deployment_monitoring_job(
            model_deployment_monitoring_job=gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob(
                name="name_value"
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].model_deployment_monitoring_job
        mock_val = gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob(
            name="name_value"
        )
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=["paths_value"])
        assert arg == mock_val


def test_update_model_deployment_monitoring_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_model_deployment_monitoring_job(
            job_service.UpdateModelDeploymentMonitoringJobRequest(),
            model_deployment_monitoring_job=gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob(
                name="name_value"
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_model_deployment_monitoring_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_model_deployment_monitoring_job(
            model_deployment_monitoring_job=gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob(
                name="name_value"
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].model_deployment_monitoring_job
        mock_val = gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob(
            name="name_value"
        )
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=["paths_value"])
        assert arg == mock_val


@pytest.mark.asyncio
async def test_update_model_deployment_monitoring_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_model_deployment_monitoring_job(
            job_service.UpdateModelDeploymentMonitoringJobRequest(),
            model_deployment_monitoring_job=gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob(
                name="name_value"
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.DeleteModelDeploymentMonitoringJobRequest,
        dict,
    ],
)
def test_delete_model_deployment_monitoring_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_model_deployment_monitoring_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.DeleteModelDeploymentMonitoringJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_model_deployment_monitoring_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_model_deployment_monitoring_job), "__call__"
    ) as call:
        client.delete_model_deployment_monitoring_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.DeleteModelDeploymentMonitoringJobRequest()


@pytest.mark.asyncio
async def test_delete_model_deployment_monitoring_job_async(
    transport: str = "grpc_asyncio",
    request_type=job_service.DeleteModelDeploymentMonitoringJobRequest,
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_model_deployment_monitoring_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.DeleteModelDeploymentMonitoringJobRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_model_deployment_monitoring_job_async_from_dict():
    await test_delete_model_deployment_monitoring_job_async(request_type=dict)


def test_delete_model_deployment_monitoring_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.DeleteModelDeploymentMonitoringJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_model_deployment_monitoring_job), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_model_deployment_monitoring_job(request)

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
async def test_delete_model_deployment_monitoring_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.DeleteModelDeploymentMonitoringJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_model_deployment_monitoring_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_model_deployment_monitoring_job(request)

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


def test_delete_model_deployment_monitoring_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_model_deployment_monitoring_job(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_delete_model_deployment_monitoring_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_model_deployment_monitoring_job(
            job_service.DeleteModelDeploymentMonitoringJobRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_model_deployment_monitoring_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_model_deployment_monitoring_job(
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
async def test_delete_model_deployment_monitoring_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_model_deployment_monitoring_job(
            job_service.DeleteModelDeploymentMonitoringJobRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.PauseModelDeploymentMonitoringJobRequest,
        dict,
    ],
)
def test_pause_model_deployment_monitoring_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.pause_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        response = client.pause_model_deployment_monitoring_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.PauseModelDeploymentMonitoringJobRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_pause_model_deployment_monitoring_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.pause_model_deployment_monitoring_job), "__call__"
    ) as call:
        client.pause_model_deployment_monitoring_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.PauseModelDeploymentMonitoringJobRequest()


@pytest.mark.asyncio
async def test_pause_model_deployment_monitoring_job_async(
    transport: str = "grpc_asyncio",
    request_type=job_service.PauseModelDeploymentMonitoringJobRequest,
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.pause_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.pause_model_deployment_monitoring_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.PauseModelDeploymentMonitoringJobRequest()

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_pause_model_deployment_monitoring_job_async_from_dict():
    await test_pause_model_deployment_monitoring_job_async(request_type=dict)


def test_pause_model_deployment_monitoring_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.PauseModelDeploymentMonitoringJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.pause_model_deployment_monitoring_job), "__call__"
    ) as call:
        call.return_value = None
        client.pause_model_deployment_monitoring_job(request)

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
async def test_pause_model_deployment_monitoring_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.PauseModelDeploymentMonitoringJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.pause_model_deployment_monitoring_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        await client.pause_model_deployment_monitoring_job(request)

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


def test_pause_model_deployment_monitoring_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.pause_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.pause_model_deployment_monitoring_job(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_pause_model_deployment_monitoring_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.pause_model_deployment_monitoring_job(
            job_service.PauseModelDeploymentMonitoringJobRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_pause_model_deployment_monitoring_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.pause_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.pause_model_deployment_monitoring_job(
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
async def test_pause_model_deployment_monitoring_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.pause_model_deployment_monitoring_job(
            job_service.PauseModelDeploymentMonitoringJobRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.ResumeModelDeploymentMonitoringJobRequest,
        dict,
    ],
)
def test_resume_model_deployment_monitoring_job(request_type, transport: str = "grpc"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.resume_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        response = client.resume_model_deployment_monitoring_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ResumeModelDeploymentMonitoringJobRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_resume_model_deployment_monitoring_job_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.resume_model_deployment_monitoring_job), "__call__"
    ) as call:
        client.resume_model_deployment_monitoring_job()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ResumeModelDeploymentMonitoringJobRequest()


@pytest.mark.asyncio
async def test_resume_model_deployment_monitoring_job_async(
    transport: str = "grpc_asyncio",
    request_type=job_service.ResumeModelDeploymentMonitoringJobRequest,
):
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.resume_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.resume_model_deployment_monitoring_job(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == job_service.ResumeModelDeploymentMonitoringJobRequest()

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_resume_model_deployment_monitoring_job_async_from_dict():
    await test_resume_model_deployment_monitoring_job_async(request_type=dict)


def test_resume_model_deployment_monitoring_job_field_headers():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.ResumeModelDeploymentMonitoringJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.resume_model_deployment_monitoring_job), "__call__"
    ) as call:
        call.return_value = None
        client.resume_model_deployment_monitoring_job(request)

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
async def test_resume_model_deployment_monitoring_job_field_headers_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = job_service.ResumeModelDeploymentMonitoringJobRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.resume_model_deployment_monitoring_job), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        await client.resume_model_deployment_monitoring_job(request)

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


def test_resume_model_deployment_monitoring_job_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.resume_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.resume_model_deployment_monitoring_job(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_resume_model_deployment_monitoring_job_flattened_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.resume_model_deployment_monitoring_job(
            job_service.ResumeModelDeploymentMonitoringJobRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_resume_model_deployment_monitoring_job_flattened_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.resume_model_deployment_monitoring_job), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.resume_model_deployment_monitoring_job(
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
async def test_resume_model_deployment_monitoring_job_flattened_error_async():
    client = JobServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.resume_model_deployment_monitoring_job(
            job_service.ResumeModelDeploymentMonitoringJobRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.CreateCustomJobRequest,
        dict,
    ],
)
def test_create_custom_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request_init["custom_job"] = {
        "name": "name_value",
        "display_name": "display_name_value",
        "job_spec": {
            "worker_pool_specs": [
                {
                    "container_spec": {
                        "image_uri": "image_uri_value",
                        "command": ["command_value1", "command_value2"],
                        "args": ["args_value1", "args_value2"],
                        "env": [{"name": "name_value", "value": "value_value"}],
                    },
                    "python_package_spec": {
                        "executor_image_uri": "executor_image_uri_value",
                        "package_uris": ["package_uris_value1", "package_uris_value2"],
                        "python_module": "python_module_value",
                        "args": ["args_value1", "args_value2"],
                        "env": {},
                    },
                    "machine_spec": {
                        "machine_type": "machine_type_value",
                        "accelerator_type": 1,
                        "accelerator_count": 1805,
                        "tpu_topology": "tpu_topology_value",
                    },
                    "replica_count": 1384,
                    "nfs_mounts": [
                        {
                            "server": "server_value",
                            "path": "path_value",
                            "mount_point": "mount_point_value",
                        }
                    ],
                    "disk_spec": {
                        "boot_disk_type": "boot_disk_type_value",
                        "boot_disk_size_gb": 1792,
                    },
                }
            ],
            "scheduling": {
                "timeout": {"seconds": 751, "nanos": 543},
                "restart_job_on_worker_restart": True,
                "disable_retries": True,
            },
            "service_account": "service_account_value",
            "network": "network_value",
            "reserved_ip_ranges": [
                "reserved_ip_ranges_value1",
                "reserved_ip_ranges_value2",
            ],
            "base_output_directory": {"output_uri_prefix": "output_uri_prefix_value"},
            "protected_artifact_location_id": "protected_artifact_location_id_value",
            "tensorboard": "tensorboard_value",
            "enable_web_access": True,
            "enable_dashboard_access": True,
            "experiment": "experiment_value",
            "experiment_run": "experiment_run_value",
            "models": ["models_value1", "models_value2"],
        },
        "state": 1,
        "create_time": {"seconds": 751, "nanos": 543},
        "start_time": {},
        "end_time": {},
        "update_time": {},
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
        "labels": {},
        "encryption_spec": {"kms_key_name": "kms_key_name_value"},
        "web_access_uris": {},
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = job_service.CreateCustomJobRequest.meta.fields["custom_job"]

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
    for field, value in request_init["custom_job"].items():  # pragma: NO COVER
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
                for i in range(0, len(request_init["custom_job"][field])):
                    del request_init["custom_job"][field][i][subfield]
            else:
                del request_init["custom_job"][field][subfield]
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gca_custom_job.CustomJob(
            name="name_value",
            display_name="display_name_value",
            state=job_state.JobState.JOB_STATE_QUEUED,
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = gca_custom_job.CustomJob.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.create_custom_job(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_custom_job.CustomJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED


def test_create_custom_job_rest_required_fields(
    request_type=job_service.CreateCustomJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).create_custom_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).create_custom_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = gca_custom_job.CustomJob()
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
            return_value = gca_custom_job.CustomJob.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.create_custom_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_create_custom_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.create_custom_job._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(())
        & set(
            (
                "parent",
                "customJob",
            )
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_create_custom_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "post_create_custom_job"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_create_custom_job"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.CreateCustomJobRequest.pb(
            job_service.CreateCustomJobRequest()
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
        req.return_value._content = gca_custom_job.CustomJob.to_json(
            gca_custom_job.CustomJob()
        )

        request = job_service.CreateCustomJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = gca_custom_job.CustomJob()

        client.create_custom_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_create_custom_job_rest_bad_request(
    transport: str = "rest", request_type=job_service.CreateCustomJobRequest
):
    client = JobServiceClient(
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
        client.create_custom_job(request)


def test_create_custom_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gca_custom_job.CustomJob()

        # get arguments that satisfy an http rule for this method
        sample_request = {"parent": "projects/sample1/locations/sample2"}

        # get truthy value for each flattened field
        mock_args = dict(
            parent="parent_value",
            custom_job=gca_custom_job.CustomJob(name="name_value"),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = gca_custom_job.CustomJob.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.create_custom_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{parent=projects/*/locations/*}/customJobs" % client.transport._host,
            args[1],
        )


def test_create_custom_job_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_custom_job(
            job_service.CreateCustomJobRequest(),
            parent="parent_value",
            custom_job=gca_custom_job.CustomJob(name="name_value"),
        )


def test_create_custom_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.GetCustomJobRequest,
        dict,
    ],
)
def test_get_custom_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/customJobs/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = custom_job.CustomJob(
            name="name_value",
            display_name="display_name_value",
            state=job_state.JobState.JOB_STATE_QUEUED,
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = custom_job.CustomJob.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.get_custom_job(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, custom_job.CustomJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED


def test_get_custom_job_rest_required_fields(
    request_type=job_service.GetCustomJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).get_custom_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_custom_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = custom_job.CustomJob()
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
            return_value = custom_job.CustomJob.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.get_custom_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_custom_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_custom_job._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_custom_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "post_get_custom_job"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_get_custom_job"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.GetCustomJobRequest.pb(
            job_service.GetCustomJobRequest()
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
        req.return_value._content = custom_job.CustomJob.to_json(custom_job.CustomJob())

        request = job_service.GetCustomJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = custom_job.CustomJob()

        client.get_custom_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_get_custom_job_rest_bad_request(
    transport: str = "rest", request_type=job_service.GetCustomJobRequest
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/customJobs/sample3"}
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
        client.get_custom_job(request)


def test_get_custom_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = custom_job.CustomJob()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/customJobs/sample3"
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
        return_value = custom_job.CustomJob.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.get_custom_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{name=projects/*/locations/*/customJobs/*}" % client.transport._host,
            args[1],
        )


def test_get_custom_job_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_custom_job(
            job_service.GetCustomJobRequest(),
            name="name_value",
        )


def test_get_custom_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.ListCustomJobsRequest,
        dict,
    ],
)
def test_list_custom_jobs_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = job_service.ListCustomJobsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = job_service.ListCustomJobsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.list_custom_jobs(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListCustomJobsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_custom_jobs_rest_required_fields(
    request_type=job_service.ListCustomJobsRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).list_custom_jobs._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_custom_jobs._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(
        (
            "filter",
            "page_size",
            "page_token",
            "read_mask",
        )
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = job_service.ListCustomJobsResponse()
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
            return_value = job_service.ListCustomJobsResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.list_custom_jobs(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_list_custom_jobs_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.list_custom_jobs._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(
            (
                "filter",
                "pageSize",
                "pageToken",
                "readMask",
            )
        )
        & set(("parent",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_custom_jobs_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "post_list_custom_jobs"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_list_custom_jobs"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.ListCustomJobsRequest.pb(
            job_service.ListCustomJobsRequest()
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
        req.return_value._content = job_service.ListCustomJobsResponse.to_json(
            job_service.ListCustomJobsResponse()
        )

        request = job_service.ListCustomJobsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = job_service.ListCustomJobsResponse()

        client.list_custom_jobs(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_list_custom_jobs_rest_bad_request(
    transport: str = "rest", request_type=job_service.ListCustomJobsRequest
):
    client = JobServiceClient(
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
        client.list_custom_jobs(request)


def test_list_custom_jobs_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = job_service.ListCustomJobsResponse()

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
        return_value = job_service.ListCustomJobsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.list_custom_jobs(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{parent=projects/*/locations/*}/customJobs" % client.transport._host,
            args[1],
        )


def test_list_custom_jobs_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_custom_jobs(
            job_service.ListCustomJobsRequest(),
            parent="parent_value",
        )


def test_list_custom_jobs_rest_pager(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            job_service.ListCustomJobsResponse(
                custom_jobs=[
                    custom_job.CustomJob(),
                    custom_job.CustomJob(),
                    custom_job.CustomJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListCustomJobsResponse(
                custom_jobs=[],
                next_page_token="def",
            ),
            job_service.ListCustomJobsResponse(
                custom_jobs=[
                    custom_job.CustomJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListCustomJobsResponse(
                custom_jobs=[
                    custom_job.CustomJob(),
                    custom_job.CustomJob(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(
            job_service.ListCustomJobsResponse.to_json(x) for x in response
        )
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {"parent": "projects/sample1/locations/sample2"}

        pager = client.list_custom_jobs(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, custom_job.CustomJob) for i in results)

        pages = list(client.list_custom_jobs(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.DeleteCustomJobRequest,
        dict,
    ],
)
def test_delete_custom_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/customJobs/sample3"}
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
        response = client.delete_custom_job(request)

    # Establish that the response is the type that we expect.
    assert response.operation.name == "operations/spam"


def test_delete_custom_job_rest_required_fields(
    request_type=job_service.DeleteCustomJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).delete_custom_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).delete_custom_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = JobServiceClient(
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

            response = client.delete_custom_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_delete_custom_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.delete_custom_job._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_delete_custom_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.JobServiceRestInterceptor, "post_delete_custom_job"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_delete_custom_job"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.DeleteCustomJobRequest.pb(
            job_service.DeleteCustomJobRequest()
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

        request = job_service.DeleteCustomJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()

        client.delete_custom_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_delete_custom_job_rest_bad_request(
    transport: str = "rest", request_type=job_service.DeleteCustomJobRequest
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/customJobs/sample3"}
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
        client.delete_custom_job(request)


def test_delete_custom_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/customJobs/sample3"
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

        client.delete_custom_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{name=projects/*/locations/*/customJobs/*}" % client.transport._host,
            args[1],
        )


def test_delete_custom_job_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_custom_job(
            job_service.DeleteCustomJobRequest(),
            name="name_value",
        )


def test_delete_custom_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.CancelCustomJobRequest,
        dict,
    ],
)
def test_cancel_custom_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/customJobs/sample3"}
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
        response = client.cancel_custom_job(request)

    # Establish that the response is the type that we expect.
    assert response is None


def test_cancel_custom_job_rest_required_fields(
    request_type=job_service.CancelCustomJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).cancel_custom_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).cancel_custom_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = JobServiceClient(
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

            response = client.cancel_custom_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_cancel_custom_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.cancel_custom_job._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_cancel_custom_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_cancel_custom_job"
    ) as pre:
        pre.assert_not_called()
        pb_message = job_service.CancelCustomJobRequest.pb(
            job_service.CancelCustomJobRequest()
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

        request = job_service.CancelCustomJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata

        client.cancel_custom_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()


def test_cancel_custom_job_rest_bad_request(
    transport: str = "rest", request_type=job_service.CancelCustomJobRequest
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/customJobs/sample3"}
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
        client.cancel_custom_job(request)


def test_cancel_custom_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/customJobs/sample3"
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

        client.cancel_custom_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{name=projects/*/locations/*/customJobs/*}:cancel"
            % client.transport._host,
            args[1],
        )


def test_cancel_custom_job_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.cancel_custom_job(
            job_service.CancelCustomJobRequest(),
            name="name_value",
        )


def test_cancel_custom_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.CreateDataLabelingJobRequest,
        dict,
    ],
)
def test_create_data_labeling_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request_init["data_labeling_job"] = {
        "name": "name_value",
        "display_name": "display_name_value",
        "datasets": ["datasets_value1", "datasets_value2"],
        "annotation_labels": {},
        "labeler_count": 1375,
        "instruction_uri": "instruction_uri_value",
        "inputs_schema_uri": "inputs_schema_uri_value",
        "inputs": {
            "null_value": 0,
            "number_value": 0.1285,
            "string_value": "string_value_value",
            "bool_value": True,
            "struct_value": {"fields": {}},
            "list_value": {"values": {}},
        },
        "state": 1,
        "labeling_progress": 1810,
        "current_spend": {
            "currency_code": "currency_code_value",
            "units": 563,
            "nanos": 543,
        },
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
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
        "labels": {},
        "specialist_pools": ["specialist_pools_value1", "specialist_pools_value2"],
        "encryption_spec": {"kms_key_name": "kms_key_name_value"},
        "active_learning_config": {
            "max_data_item_count": 2005,
            "max_data_item_percentage": 2506,
            "sample_config": {
                "initial_batch_sample_percentage": 3241,
                "following_batch_sample_percentage": 3472,
                "sample_strategy": 1,
            },
            "training_config": {"timeout_training_milli_hours": 3016},
        },
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = job_service.CreateDataLabelingJobRequest.meta.fields[
        "data_labeling_job"
    ]

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
    for field, value in request_init["data_labeling_job"].items():  # pragma: NO COVER
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
                for i in range(0, len(request_init["data_labeling_job"][field])):
                    del request_init["data_labeling_job"][field][i][subfield]
            else:
                del request_init["data_labeling_job"][field][subfield]
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gca_data_labeling_job.DataLabelingJob(
            name="name_value",
            display_name="display_name_value",
            datasets=["datasets_value"],
            labeler_count=1375,
            instruction_uri="instruction_uri_value",
            inputs_schema_uri="inputs_schema_uri_value",
            state=job_state.JobState.JOB_STATE_QUEUED,
            labeling_progress=1810,
            specialist_pools=["specialist_pools_value"],
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = gca_data_labeling_job.DataLabelingJob.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.create_data_labeling_job(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_data_labeling_job.DataLabelingJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.datasets == ["datasets_value"]
    assert response.labeler_count == 1375
    assert response.instruction_uri == "instruction_uri_value"
    assert response.inputs_schema_uri == "inputs_schema_uri_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert response.labeling_progress == 1810
    assert response.specialist_pools == ["specialist_pools_value"]


def test_create_data_labeling_job_rest_required_fields(
    request_type=job_service.CreateDataLabelingJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).create_data_labeling_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).create_data_labeling_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = gca_data_labeling_job.DataLabelingJob()
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
            return_value = gca_data_labeling_job.DataLabelingJob.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.create_data_labeling_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_create_data_labeling_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.create_data_labeling_job._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(())
        & set(
            (
                "parent",
                "dataLabelingJob",
            )
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_create_data_labeling_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "post_create_data_labeling_job"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_create_data_labeling_job"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.CreateDataLabelingJobRequest.pb(
            job_service.CreateDataLabelingJobRequest()
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
        req.return_value._content = gca_data_labeling_job.DataLabelingJob.to_json(
            gca_data_labeling_job.DataLabelingJob()
        )

        request = job_service.CreateDataLabelingJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = gca_data_labeling_job.DataLabelingJob()

        client.create_data_labeling_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_create_data_labeling_job_rest_bad_request(
    transport: str = "rest", request_type=job_service.CreateDataLabelingJobRequest
):
    client = JobServiceClient(
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
        client.create_data_labeling_job(request)


def test_create_data_labeling_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gca_data_labeling_job.DataLabelingJob()

        # get arguments that satisfy an http rule for this method
        sample_request = {"parent": "projects/sample1/locations/sample2"}

        # get truthy value for each flattened field
        mock_args = dict(
            parent="parent_value",
            data_labeling_job=gca_data_labeling_job.DataLabelingJob(name="name_value"),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = gca_data_labeling_job.DataLabelingJob.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.create_data_labeling_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{parent=projects/*/locations/*}/dataLabelingJobs"
            % client.transport._host,
            args[1],
        )


def test_create_data_labeling_job_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_data_labeling_job(
            job_service.CreateDataLabelingJobRequest(),
            parent="parent_value",
            data_labeling_job=gca_data_labeling_job.DataLabelingJob(name="name_value"),
        )


def test_create_data_labeling_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.GetDataLabelingJobRequest,
        dict,
    ],
)
def test_get_data_labeling_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/dataLabelingJobs/sample3"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = data_labeling_job.DataLabelingJob(
            name="name_value",
            display_name="display_name_value",
            datasets=["datasets_value"],
            labeler_count=1375,
            instruction_uri="instruction_uri_value",
            inputs_schema_uri="inputs_schema_uri_value",
            state=job_state.JobState.JOB_STATE_QUEUED,
            labeling_progress=1810,
            specialist_pools=["specialist_pools_value"],
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = data_labeling_job.DataLabelingJob.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.get_data_labeling_job(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, data_labeling_job.DataLabelingJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.datasets == ["datasets_value"]
    assert response.labeler_count == 1375
    assert response.instruction_uri == "instruction_uri_value"
    assert response.inputs_schema_uri == "inputs_schema_uri_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert response.labeling_progress == 1810
    assert response.specialist_pools == ["specialist_pools_value"]


def test_get_data_labeling_job_rest_required_fields(
    request_type=job_service.GetDataLabelingJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).get_data_labeling_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_data_labeling_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = data_labeling_job.DataLabelingJob()
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
            return_value = data_labeling_job.DataLabelingJob.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.get_data_labeling_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_data_labeling_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_data_labeling_job._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_data_labeling_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "post_get_data_labeling_job"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_get_data_labeling_job"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.GetDataLabelingJobRequest.pb(
            job_service.GetDataLabelingJobRequest()
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
        req.return_value._content = data_labeling_job.DataLabelingJob.to_json(
            data_labeling_job.DataLabelingJob()
        )

        request = job_service.GetDataLabelingJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = data_labeling_job.DataLabelingJob()

        client.get_data_labeling_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_get_data_labeling_job_rest_bad_request(
    transport: str = "rest", request_type=job_service.GetDataLabelingJobRequest
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/dataLabelingJobs/sample3"
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
        client.get_data_labeling_job(request)


def test_get_data_labeling_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = data_labeling_job.DataLabelingJob()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/dataLabelingJobs/sample3"
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
        return_value = data_labeling_job.DataLabelingJob.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.get_data_labeling_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{name=projects/*/locations/*/dataLabelingJobs/*}"
            % client.transport._host,
            args[1],
        )


def test_get_data_labeling_job_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_data_labeling_job(
            job_service.GetDataLabelingJobRequest(),
            name="name_value",
        )


def test_get_data_labeling_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.ListDataLabelingJobsRequest,
        dict,
    ],
)
def test_list_data_labeling_jobs_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = job_service.ListDataLabelingJobsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = job_service.ListDataLabelingJobsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.list_data_labeling_jobs(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDataLabelingJobsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_data_labeling_jobs_rest_required_fields(
    request_type=job_service.ListDataLabelingJobsRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).list_data_labeling_jobs._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_data_labeling_jobs._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(
        (
            "filter",
            "order_by",
            "page_size",
            "page_token",
            "read_mask",
        )
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = job_service.ListDataLabelingJobsResponse()
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
            return_value = job_service.ListDataLabelingJobsResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.list_data_labeling_jobs(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_list_data_labeling_jobs_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.list_data_labeling_jobs._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(
            (
                "filter",
                "orderBy",
                "pageSize",
                "pageToken",
                "readMask",
            )
        )
        & set(("parent",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_data_labeling_jobs_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "post_list_data_labeling_jobs"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_list_data_labeling_jobs"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.ListDataLabelingJobsRequest.pb(
            job_service.ListDataLabelingJobsRequest()
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
        req.return_value._content = job_service.ListDataLabelingJobsResponse.to_json(
            job_service.ListDataLabelingJobsResponse()
        )

        request = job_service.ListDataLabelingJobsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = job_service.ListDataLabelingJobsResponse()

        client.list_data_labeling_jobs(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_list_data_labeling_jobs_rest_bad_request(
    transport: str = "rest", request_type=job_service.ListDataLabelingJobsRequest
):
    client = JobServiceClient(
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
        client.list_data_labeling_jobs(request)


def test_list_data_labeling_jobs_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = job_service.ListDataLabelingJobsResponse()

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
        return_value = job_service.ListDataLabelingJobsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.list_data_labeling_jobs(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{parent=projects/*/locations/*}/dataLabelingJobs"
            % client.transport._host,
            args[1],
        )


def test_list_data_labeling_jobs_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_data_labeling_jobs(
            job_service.ListDataLabelingJobsRequest(),
            parent="parent_value",
        )


def test_list_data_labeling_jobs_rest_pager(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[
                    data_labeling_job.DataLabelingJob(),
                    data_labeling_job.DataLabelingJob(),
                    data_labeling_job.DataLabelingJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[],
                next_page_token="def",
            ),
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[
                    data_labeling_job.DataLabelingJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListDataLabelingJobsResponse(
                data_labeling_jobs=[
                    data_labeling_job.DataLabelingJob(),
                    data_labeling_job.DataLabelingJob(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(
            job_service.ListDataLabelingJobsResponse.to_json(x) for x in response
        )
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {"parent": "projects/sample1/locations/sample2"}

        pager = client.list_data_labeling_jobs(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, data_labeling_job.DataLabelingJob) for i in results)

        pages = list(client.list_data_labeling_jobs(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.DeleteDataLabelingJobRequest,
        dict,
    ],
)
def test_delete_data_labeling_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/dataLabelingJobs/sample3"
    }
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
        response = client.delete_data_labeling_job(request)

    # Establish that the response is the type that we expect.
    assert response.operation.name == "operations/spam"


def test_delete_data_labeling_job_rest_required_fields(
    request_type=job_service.DeleteDataLabelingJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).delete_data_labeling_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).delete_data_labeling_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = JobServiceClient(
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

            response = client.delete_data_labeling_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_delete_data_labeling_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.delete_data_labeling_job._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_delete_data_labeling_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.JobServiceRestInterceptor, "post_delete_data_labeling_job"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_delete_data_labeling_job"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.DeleteDataLabelingJobRequest.pb(
            job_service.DeleteDataLabelingJobRequest()
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

        request = job_service.DeleteDataLabelingJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()

        client.delete_data_labeling_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_delete_data_labeling_job_rest_bad_request(
    transport: str = "rest", request_type=job_service.DeleteDataLabelingJobRequest
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/dataLabelingJobs/sample3"
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
        client.delete_data_labeling_job(request)


def test_delete_data_labeling_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/dataLabelingJobs/sample3"
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

        client.delete_data_labeling_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{name=projects/*/locations/*/dataLabelingJobs/*}"
            % client.transport._host,
            args[1],
        )


def test_delete_data_labeling_job_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_data_labeling_job(
            job_service.DeleteDataLabelingJobRequest(),
            name="name_value",
        )


def test_delete_data_labeling_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.CancelDataLabelingJobRequest,
        dict,
    ],
)
def test_cancel_data_labeling_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/dataLabelingJobs/sample3"
    }
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
        response = client.cancel_data_labeling_job(request)

    # Establish that the response is the type that we expect.
    assert response is None


def test_cancel_data_labeling_job_rest_required_fields(
    request_type=job_service.CancelDataLabelingJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).cancel_data_labeling_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).cancel_data_labeling_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = JobServiceClient(
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

            response = client.cancel_data_labeling_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_cancel_data_labeling_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.cancel_data_labeling_job._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_cancel_data_labeling_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_cancel_data_labeling_job"
    ) as pre:
        pre.assert_not_called()
        pb_message = job_service.CancelDataLabelingJobRequest.pb(
            job_service.CancelDataLabelingJobRequest()
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

        request = job_service.CancelDataLabelingJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata

        client.cancel_data_labeling_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()


def test_cancel_data_labeling_job_rest_bad_request(
    transport: str = "rest", request_type=job_service.CancelDataLabelingJobRequest
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/dataLabelingJobs/sample3"
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
        client.cancel_data_labeling_job(request)


def test_cancel_data_labeling_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/dataLabelingJobs/sample3"
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

        client.cancel_data_labeling_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{name=projects/*/locations/*/dataLabelingJobs/*}:cancel"
            % client.transport._host,
            args[1],
        )


def test_cancel_data_labeling_job_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.cancel_data_labeling_job(
            job_service.CancelDataLabelingJobRequest(),
            name="name_value",
        )


def test_cancel_data_labeling_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.CreateHyperparameterTuningJobRequest,
        dict,
    ],
)
def test_create_hyperparameter_tuning_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request_init["hyperparameter_tuning_job"] = {
        "name": "name_value",
        "display_name": "display_name_value",
        "study_spec": {
            "decay_curve_stopping_spec": {"use_elapsed_duration": True},
            "median_automated_stopping_spec": {"use_elapsed_duration": True},
            "convex_automated_stopping_spec": {
                "max_step_count": 1513,
                "min_step_count": 1511,
                "min_measurement_count": 2257,
                "learning_rate_parameter_name": "learning_rate_parameter_name_value",
                "use_elapsed_duration": True,
                "update_all_stopped_trials": True,
            },
            "metrics": [
                {
                    "metric_id": "metric_id_value",
                    "goal": 1,
                    "safety_config": {
                        "safety_threshold": 0.17200000000000001,
                        "desired_min_safe_trials_fraction": 0.33640000000000003,
                    },
                }
            ],
            "parameters": [
                {
                    "double_value_spec": {
                        "min_value": 0.96,
                        "max_value": 0.962,
                        "default_value": 0.13770000000000002,
                    },
                    "integer_value_spec": {
                        "min_value": 960,
                        "max_value": 962,
                        "default_value": 1377,
                    },
                    "categorical_value_spec": {
                        "values": ["values_value1", "values_value2"],
                        "default_value": "default_value_value",
                    },
                    "discrete_value_spec": {
                        "values": [0.657, 0.658],
                        "default_value": 0.13770000000000002,
                    },
                    "parameter_id": "parameter_id_value",
                    "scale_type": 1,
                    "conditional_parameter_specs": [
                        {
                            "parent_discrete_values": {"values": [0.657, 0.658]},
                            "parent_int_values": {"values": [657, 658]},
                            "parent_categorical_values": {
                                "values": ["values_value1", "values_value2"]
                            },
                            "parameter_spec": {},
                        }
                    ],
                }
            ],
            "algorithm": 2,
            "observation_noise": 1,
            "measurement_selection_type": 1,
            "study_stopping_config": {
                "should_stop_asap": {"value": True},
                "minimum_runtime_constraint": {
                    "max_duration": {"seconds": 751, "nanos": 543},
                    "end_time": {"seconds": 751, "nanos": 543},
                },
                "maximum_runtime_constraint": {},
                "min_num_trials": {"value": 541},
                "max_num_trials": {},
                "max_num_trials_no_progress": {},
                "max_duration_no_progress": {},
            },
        },
        "max_trial_count": 1609,
        "parallel_trial_count": 2128,
        "max_failed_trial_count": 2317,
        "trial_job_spec": {
            "worker_pool_specs": [
                {
                    "container_spec": {
                        "image_uri": "image_uri_value",
                        "command": ["command_value1", "command_value2"],
                        "args": ["args_value1", "args_value2"],
                        "env": [{"name": "name_value", "value": "value_value"}],
                    },
                    "python_package_spec": {
                        "executor_image_uri": "executor_image_uri_value",
                        "package_uris": ["package_uris_value1", "package_uris_value2"],
                        "python_module": "python_module_value",
                        "args": ["args_value1", "args_value2"],
                        "env": {},
                    },
                    "machine_spec": {
                        "machine_type": "machine_type_value",
                        "accelerator_type": 1,
                        "accelerator_count": 1805,
                        "tpu_topology": "tpu_topology_value",
                    },
                    "replica_count": 1384,
                    "nfs_mounts": [
                        {
                            "server": "server_value",
                            "path": "path_value",
                            "mount_point": "mount_point_value",
                        }
                    ],
                    "disk_spec": {
                        "boot_disk_type": "boot_disk_type_value",
                        "boot_disk_size_gb": 1792,
                    },
                }
            ],
            "scheduling": {
                "timeout": {},
                "restart_job_on_worker_restart": True,
                "disable_retries": True,
            },
            "service_account": "service_account_value",
            "network": "network_value",
            "reserved_ip_ranges": [
                "reserved_ip_ranges_value1",
                "reserved_ip_ranges_value2",
            ],
            "base_output_directory": {"output_uri_prefix": "output_uri_prefix_value"},
            "protected_artifact_location_id": "protected_artifact_location_id_value",
            "tensorboard": "tensorboard_value",
            "enable_web_access": True,
            "enable_dashboard_access": True,
            "experiment": "experiment_value",
            "experiment_run": "experiment_run_value",
            "models": ["models_value1", "models_value2"],
        },
        "trials": [
            {
                "name": "name_value",
                "id": "id_value",
                "state": 1,
                "parameters": [
                    {
                        "parameter_id": "parameter_id_value",
                        "value": {
                            "null_value": 0,
                            "number_value": 0.1285,
                            "string_value": "string_value_value",
                            "bool_value": True,
                            "struct_value": {"fields": {}},
                            "list_value": {"values": {}},
                        },
                    }
                ],
                "final_measurement": {
                    "elapsed_duration": {},
                    "step_count": 1092,
                    "metrics": [{"metric_id": "metric_id_value", "value": 0.541}],
                },
                "measurements": {},
                "start_time": {},
                "end_time": {},
                "client_id": "client_id_value",
                "infeasible_reason": "infeasible_reason_value",
                "custom_job": "custom_job_value",
                "web_access_uris": {},
            }
        ],
        "state": 1,
        "create_time": {},
        "start_time": {},
        "end_time": {},
        "update_time": {},
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
        "labels": {},
        "encryption_spec": {"kms_key_name": "kms_key_name_value"},
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = job_service.CreateHyperparameterTuningJobRequest.meta.fields[
        "hyperparameter_tuning_job"
    ]

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
    for field, value in request_init[
        "hyperparameter_tuning_job"
    ].items():  # pragma: NO COVER
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
                for i in range(
                    0, len(request_init["hyperparameter_tuning_job"][field])
                ):
                    del request_init["hyperparameter_tuning_job"][field][i][subfield]
            else:
                del request_init["hyperparameter_tuning_job"][field][subfield]
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gca_hyperparameter_tuning_job.HyperparameterTuningJob(
            name="name_value",
            display_name="display_name_value",
            max_trial_count=1609,
            parallel_trial_count=2128,
            max_failed_trial_count=2317,
            state=job_state.JobState.JOB_STATE_QUEUED,
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = gca_hyperparameter_tuning_job.HyperparameterTuningJob.pb(
            return_value
        )
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.create_hyperparameter_tuning_job(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_hyperparameter_tuning_job.HyperparameterTuningJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.max_trial_count == 1609
    assert response.parallel_trial_count == 2128
    assert response.max_failed_trial_count == 2317
    assert response.state == job_state.JobState.JOB_STATE_QUEUED


def test_create_hyperparameter_tuning_job_rest_required_fields(
    request_type=job_service.CreateHyperparameterTuningJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).create_hyperparameter_tuning_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).create_hyperparameter_tuning_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = gca_hyperparameter_tuning_job.HyperparameterTuningJob()
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
            return_value = gca_hyperparameter_tuning_job.HyperparameterTuningJob.pb(
                return_value
            )
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.create_hyperparameter_tuning_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_create_hyperparameter_tuning_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = (
        transport.create_hyperparameter_tuning_job._get_unset_required_fields({})
    )
    assert set(unset_fields) == (
        set(())
        & set(
            (
                "parent",
                "hyperparameterTuningJob",
            )
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_create_hyperparameter_tuning_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "post_create_hyperparameter_tuning_job"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_create_hyperparameter_tuning_job"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.CreateHyperparameterTuningJobRequest.pb(
            job_service.CreateHyperparameterTuningJobRequest()
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
        req.return_value._content = (
            gca_hyperparameter_tuning_job.HyperparameterTuningJob.to_json(
                gca_hyperparameter_tuning_job.HyperparameterTuningJob()
            )
        )

        request = job_service.CreateHyperparameterTuningJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = gca_hyperparameter_tuning_job.HyperparameterTuningJob()

        client.create_hyperparameter_tuning_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_create_hyperparameter_tuning_job_rest_bad_request(
    transport: str = "rest",
    request_type=job_service.CreateHyperparameterTuningJobRequest,
):
    client = JobServiceClient(
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
        client.create_hyperparameter_tuning_job(request)


def test_create_hyperparameter_tuning_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gca_hyperparameter_tuning_job.HyperparameterTuningJob()

        # get arguments that satisfy an http rule for this method
        sample_request = {"parent": "projects/sample1/locations/sample2"}

        # get truthy value for each flattened field
        mock_args = dict(
            parent="parent_value",
            hyperparameter_tuning_job=gca_hyperparameter_tuning_job.HyperparameterTuningJob(
                name="name_value"
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = gca_hyperparameter_tuning_job.HyperparameterTuningJob.pb(
            return_value
        )
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.create_hyperparameter_tuning_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{parent=projects/*/locations/*}/hyperparameterTuningJobs"
            % client.transport._host,
            args[1],
        )


def test_create_hyperparameter_tuning_job_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_hyperparameter_tuning_job(
            job_service.CreateHyperparameterTuningJobRequest(),
            parent="parent_value",
            hyperparameter_tuning_job=gca_hyperparameter_tuning_job.HyperparameterTuningJob(
                name="name_value"
            ),
        )


def test_create_hyperparameter_tuning_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.GetHyperparameterTuningJobRequest,
        dict,
    ],
)
def test_get_hyperparameter_tuning_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/hyperparameterTuningJobs/sample3"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = hyperparameter_tuning_job.HyperparameterTuningJob(
            name="name_value",
            display_name="display_name_value",
            max_trial_count=1609,
            parallel_trial_count=2128,
            max_failed_trial_count=2317,
            state=job_state.JobState.JOB_STATE_QUEUED,
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = hyperparameter_tuning_job.HyperparameterTuningJob.pb(
            return_value
        )
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.get_hyperparameter_tuning_job(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, hyperparameter_tuning_job.HyperparameterTuningJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.max_trial_count == 1609
    assert response.parallel_trial_count == 2128
    assert response.max_failed_trial_count == 2317
    assert response.state == job_state.JobState.JOB_STATE_QUEUED


def test_get_hyperparameter_tuning_job_rest_required_fields(
    request_type=job_service.GetHyperparameterTuningJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).get_hyperparameter_tuning_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_hyperparameter_tuning_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = hyperparameter_tuning_job.HyperparameterTuningJob()
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
            return_value = hyperparameter_tuning_job.HyperparameterTuningJob.pb(
                return_value
            )
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.get_hyperparameter_tuning_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_hyperparameter_tuning_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_hyperparameter_tuning_job._get_unset_required_fields(
        {}
    )
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_hyperparameter_tuning_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "post_get_hyperparameter_tuning_job"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_get_hyperparameter_tuning_job"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.GetHyperparameterTuningJobRequest.pb(
            job_service.GetHyperparameterTuningJobRequest()
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
        req.return_value._content = (
            hyperparameter_tuning_job.HyperparameterTuningJob.to_json(
                hyperparameter_tuning_job.HyperparameterTuningJob()
            )
        )

        request = job_service.GetHyperparameterTuningJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = hyperparameter_tuning_job.HyperparameterTuningJob()

        client.get_hyperparameter_tuning_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_get_hyperparameter_tuning_job_rest_bad_request(
    transport: str = "rest", request_type=job_service.GetHyperparameterTuningJobRequest
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/hyperparameterTuningJobs/sample3"
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
        client.get_hyperparameter_tuning_job(request)


def test_get_hyperparameter_tuning_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = hyperparameter_tuning_job.HyperparameterTuningJob()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/hyperparameterTuningJobs/sample3"
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
        return_value = hyperparameter_tuning_job.HyperparameterTuningJob.pb(
            return_value
        )
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.get_hyperparameter_tuning_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*}"
            % client.transport._host,
            args[1],
        )


def test_get_hyperparameter_tuning_job_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_hyperparameter_tuning_job(
            job_service.GetHyperparameterTuningJobRequest(),
            name="name_value",
        )


def test_get_hyperparameter_tuning_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.ListHyperparameterTuningJobsRequest,
        dict,
    ],
)
def test_list_hyperparameter_tuning_jobs_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = job_service.ListHyperparameterTuningJobsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = job_service.ListHyperparameterTuningJobsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.list_hyperparameter_tuning_jobs(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListHyperparameterTuningJobsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_hyperparameter_tuning_jobs_rest_required_fields(
    request_type=job_service.ListHyperparameterTuningJobsRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).list_hyperparameter_tuning_jobs._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_hyperparameter_tuning_jobs._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(
        (
            "filter",
            "page_size",
            "page_token",
            "read_mask",
        )
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = job_service.ListHyperparameterTuningJobsResponse()
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
            return_value = job_service.ListHyperparameterTuningJobsResponse.pb(
                return_value
            )
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.list_hyperparameter_tuning_jobs(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_list_hyperparameter_tuning_jobs_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.list_hyperparameter_tuning_jobs._get_unset_required_fields(
        {}
    )
    assert set(unset_fields) == (
        set(
            (
                "filter",
                "pageSize",
                "pageToken",
                "readMask",
            )
        )
        & set(("parent",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_hyperparameter_tuning_jobs_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "post_list_hyperparameter_tuning_jobs"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_list_hyperparameter_tuning_jobs"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.ListHyperparameterTuningJobsRequest.pb(
            job_service.ListHyperparameterTuningJobsRequest()
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
        req.return_value._content = (
            job_service.ListHyperparameterTuningJobsResponse.to_json(
                job_service.ListHyperparameterTuningJobsResponse()
            )
        )

        request = job_service.ListHyperparameterTuningJobsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = job_service.ListHyperparameterTuningJobsResponse()

        client.list_hyperparameter_tuning_jobs(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_list_hyperparameter_tuning_jobs_rest_bad_request(
    transport: str = "rest",
    request_type=job_service.ListHyperparameterTuningJobsRequest,
):
    client = JobServiceClient(
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
        client.list_hyperparameter_tuning_jobs(request)


def test_list_hyperparameter_tuning_jobs_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = job_service.ListHyperparameterTuningJobsResponse()

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
        return_value = job_service.ListHyperparameterTuningJobsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.list_hyperparameter_tuning_jobs(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{parent=projects/*/locations/*}/hyperparameterTuningJobs"
            % client.transport._host,
            args[1],
        )


def test_list_hyperparameter_tuning_jobs_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_hyperparameter_tuning_jobs(
            job_service.ListHyperparameterTuningJobsRequest(),
            parent="parent_value",
        )


def test_list_hyperparameter_tuning_jobs_rest_pager(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[],
                next_page_token="def",
            ),
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListHyperparameterTuningJobsResponse(
                hyperparameter_tuning_jobs=[
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                    hyperparameter_tuning_job.HyperparameterTuningJob(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(
            job_service.ListHyperparameterTuningJobsResponse.to_json(x)
            for x in response
        )
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {"parent": "projects/sample1/locations/sample2"}

        pager = client.list_hyperparameter_tuning_jobs(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(
            isinstance(i, hyperparameter_tuning_job.HyperparameterTuningJob)
            for i in results
        )

        pages = list(
            client.list_hyperparameter_tuning_jobs(request=sample_request).pages
        )
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.DeleteHyperparameterTuningJobRequest,
        dict,
    ],
)
def test_delete_hyperparameter_tuning_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/hyperparameterTuningJobs/sample3"
    }
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
        response = client.delete_hyperparameter_tuning_job(request)

    # Establish that the response is the type that we expect.
    assert response.operation.name == "operations/spam"


def test_delete_hyperparameter_tuning_job_rest_required_fields(
    request_type=job_service.DeleteHyperparameterTuningJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).delete_hyperparameter_tuning_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).delete_hyperparameter_tuning_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = JobServiceClient(
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

            response = client.delete_hyperparameter_tuning_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_delete_hyperparameter_tuning_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = (
        transport.delete_hyperparameter_tuning_job._get_unset_required_fields({})
    )
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_delete_hyperparameter_tuning_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.JobServiceRestInterceptor, "post_delete_hyperparameter_tuning_job"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_delete_hyperparameter_tuning_job"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.DeleteHyperparameterTuningJobRequest.pb(
            job_service.DeleteHyperparameterTuningJobRequest()
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

        request = job_service.DeleteHyperparameterTuningJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()

        client.delete_hyperparameter_tuning_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_delete_hyperparameter_tuning_job_rest_bad_request(
    transport: str = "rest",
    request_type=job_service.DeleteHyperparameterTuningJobRequest,
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/hyperparameterTuningJobs/sample3"
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
        client.delete_hyperparameter_tuning_job(request)


def test_delete_hyperparameter_tuning_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/hyperparameterTuningJobs/sample3"
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

        client.delete_hyperparameter_tuning_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*}"
            % client.transport._host,
            args[1],
        )


def test_delete_hyperparameter_tuning_job_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_hyperparameter_tuning_job(
            job_service.DeleteHyperparameterTuningJobRequest(),
            name="name_value",
        )


def test_delete_hyperparameter_tuning_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.CancelHyperparameterTuningJobRequest,
        dict,
    ],
)
def test_cancel_hyperparameter_tuning_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/hyperparameterTuningJobs/sample3"
    }
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
        response = client.cancel_hyperparameter_tuning_job(request)

    # Establish that the response is the type that we expect.
    assert response is None


def test_cancel_hyperparameter_tuning_job_rest_required_fields(
    request_type=job_service.CancelHyperparameterTuningJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).cancel_hyperparameter_tuning_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).cancel_hyperparameter_tuning_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = JobServiceClient(
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

            response = client.cancel_hyperparameter_tuning_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_cancel_hyperparameter_tuning_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = (
        transport.cancel_hyperparameter_tuning_job._get_unset_required_fields({})
    )
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_cancel_hyperparameter_tuning_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_cancel_hyperparameter_tuning_job"
    ) as pre:
        pre.assert_not_called()
        pb_message = job_service.CancelHyperparameterTuningJobRequest.pb(
            job_service.CancelHyperparameterTuningJobRequest()
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

        request = job_service.CancelHyperparameterTuningJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata

        client.cancel_hyperparameter_tuning_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()


def test_cancel_hyperparameter_tuning_job_rest_bad_request(
    transport: str = "rest",
    request_type=job_service.CancelHyperparameterTuningJobRequest,
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/hyperparameterTuningJobs/sample3"
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
        client.cancel_hyperparameter_tuning_job(request)


def test_cancel_hyperparameter_tuning_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/hyperparameterTuningJobs/sample3"
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

        client.cancel_hyperparameter_tuning_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*}:cancel"
            % client.transport._host,
            args[1],
        )


def test_cancel_hyperparameter_tuning_job_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.cancel_hyperparameter_tuning_job(
            job_service.CancelHyperparameterTuningJobRequest(),
            name="name_value",
        )


def test_cancel_hyperparameter_tuning_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.CreateNasJobRequest,
        dict,
    ],
)
def test_create_nas_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request_init["nas_job"] = {
        "name": "name_value",
        "display_name": "display_name_value",
        "nas_job_spec": {
            "multi_trial_algorithm_spec": {
                "multi_trial_algorithm": 1,
                "metric": {"metric_id": "metric_id_value", "goal": 1},
                "search_trial_spec": {
                    "search_trial_job_spec": {
                        "worker_pool_specs": [
                            {
                                "container_spec": {
                                    "image_uri": "image_uri_value",
                                    "command": ["command_value1", "command_value2"],
                                    "args": ["args_value1", "args_value2"],
                                    "env": [
                                        {"name": "name_value", "value": "value_value"}
                                    ],
                                },
                                "python_package_spec": {
                                    "executor_image_uri": "executor_image_uri_value",
                                    "package_uris": [
                                        "package_uris_value1",
                                        "package_uris_value2",
                                    ],
                                    "python_module": "python_module_value",
                                    "args": ["args_value1", "args_value2"],
                                    "env": {},
                                },
                                "machine_spec": {
                                    "machine_type": "machine_type_value",
                                    "accelerator_type": 1,
                                    "accelerator_count": 1805,
                                    "tpu_topology": "tpu_topology_value",
                                },
                                "replica_count": 1384,
                                "nfs_mounts": [
                                    {
                                        "server": "server_value",
                                        "path": "path_value",
                                        "mount_point": "mount_point_value",
                                    }
                                ],
                                "disk_spec": {
                                    "boot_disk_type": "boot_disk_type_value",
                                    "boot_disk_size_gb": 1792,
                                },
                            }
                        ],
                        "scheduling": {
                            "timeout": {"seconds": 751, "nanos": 543},
                            "restart_job_on_worker_restart": True,
                            "disable_retries": True,
                        },
                        "service_account": "service_account_value",
                        "network": "network_value",
                        "reserved_ip_ranges": [
                            "reserved_ip_ranges_value1",
                            "reserved_ip_ranges_value2",
                        ],
                        "base_output_directory": {
                            "output_uri_prefix": "output_uri_prefix_value"
                        },
                        "protected_artifact_location_id": "protected_artifact_location_id_value",
                        "tensorboard": "tensorboard_value",
                        "enable_web_access": True,
                        "enable_dashboard_access": True,
                        "experiment": "experiment_value",
                        "experiment_run": "experiment_run_value",
                        "models": ["models_value1", "models_value2"],
                    },
                    "max_trial_count": 1609,
                    "max_parallel_trial_count": 2549,
                    "max_failed_trial_count": 2317,
                },
                "train_trial_spec": {
                    "train_trial_job_spec": {},
                    "max_parallel_trial_count": 2549,
                    "frequency": 978,
                },
            },
            "resume_nas_job_id": "resume_nas_job_id_value",
            "search_space_spec": "search_space_spec_value",
        },
        "nas_job_output": {
            "multi_trial_job_output": {
                "search_trials": [
                    {
                        "id": "id_value",
                        "state": 1,
                        "final_measurement": {
                            "elapsed_duration": {},
                            "step_count": 1092,
                            "metrics": [
                                {"metric_id": "metric_id_value", "value": 0.541}
                            ],
                        },
                        "start_time": {"seconds": 751, "nanos": 543},
                        "end_time": {},
                    }
                ],
                "train_trials": {},
            }
        },
        "state": 1,
        "create_time": {},
        "start_time": {},
        "end_time": {},
        "update_time": {},
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
        "labels": {},
        "encryption_spec": {"kms_key_name": "kms_key_name_value"},
        "enable_restricted_image_training": True,
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = job_service.CreateNasJobRequest.meta.fields["nas_job"]

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
    for field, value in request_init["nas_job"].items():  # pragma: NO COVER
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
                for i in range(0, len(request_init["nas_job"][field])):
                    del request_init["nas_job"][field][i][subfield]
            else:
                del request_init["nas_job"][field][subfield]
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gca_nas_job.NasJob(
            name="name_value",
            display_name="display_name_value",
            state=job_state.JobState.JOB_STATE_QUEUED,
            enable_restricted_image_training=True,
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = gca_nas_job.NasJob.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.create_nas_job(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_nas_job.NasJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert response.enable_restricted_image_training is True


def test_create_nas_job_rest_required_fields(
    request_type=job_service.CreateNasJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).create_nas_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).create_nas_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = gca_nas_job.NasJob()
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
            return_value = gca_nas_job.NasJob.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.create_nas_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_create_nas_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.create_nas_job._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(())
        & set(
            (
                "parent",
                "nasJob",
            )
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_create_nas_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "post_create_nas_job"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_create_nas_job"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.CreateNasJobRequest.pb(
            job_service.CreateNasJobRequest()
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
        req.return_value._content = gca_nas_job.NasJob.to_json(gca_nas_job.NasJob())

        request = job_service.CreateNasJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = gca_nas_job.NasJob()

        client.create_nas_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_create_nas_job_rest_bad_request(
    transport: str = "rest", request_type=job_service.CreateNasJobRequest
):
    client = JobServiceClient(
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
        client.create_nas_job(request)


def test_create_nas_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gca_nas_job.NasJob()

        # get arguments that satisfy an http rule for this method
        sample_request = {"parent": "projects/sample1/locations/sample2"}

        # get truthy value for each flattened field
        mock_args = dict(
            parent="parent_value",
            nas_job=gca_nas_job.NasJob(name="name_value"),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = gca_nas_job.NasJob.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.create_nas_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{parent=projects/*/locations/*}/nasJobs" % client.transport._host,
            args[1],
        )


def test_create_nas_job_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_nas_job(
            job_service.CreateNasJobRequest(),
            parent="parent_value",
            nas_job=gca_nas_job.NasJob(name="name_value"),
        )


def test_create_nas_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.GetNasJobRequest,
        dict,
    ],
)
def test_get_nas_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/nasJobs/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = nas_job.NasJob(
            name="name_value",
            display_name="display_name_value",
            state=job_state.JobState.JOB_STATE_QUEUED,
            enable_restricted_image_training=True,
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = nas_job.NasJob.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.get_nas_job(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, nas_job.NasJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert response.enable_restricted_image_training is True


def test_get_nas_job_rest_required_fields(request_type=job_service.GetNasJobRequest):
    transport_class = transports.JobServiceRestTransport

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
    ).get_nas_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_nas_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = nas_job.NasJob()
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
            return_value = nas_job.NasJob.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.get_nas_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_nas_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_nas_job._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_nas_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "post_get_nas_job"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_get_nas_job"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.GetNasJobRequest.pb(job_service.GetNasJobRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = nas_job.NasJob.to_json(nas_job.NasJob())

        request = job_service.GetNasJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = nas_job.NasJob()

        client.get_nas_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_get_nas_job_rest_bad_request(
    transport: str = "rest", request_type=job_service.GetNasJobRequest
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/nasJobs/sample3"}
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
        client.get_nas_job(request)


def test_get_nas_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = nas_job.NasJob()

        # get arguments that satisfy an http rule for this method
        sample_request = {"name": "projects/sample1/locations/sample2/nasJobs/sample3"}

        # get truthy value for each flattened field
        mock_args = dict(
            name="name_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = nas_job.NasJob.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.get_nas_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{name=projects/*/locations/*/nasJobs/*}" % client.transport._host,
            args[1],
        )


def test_get_nas_job_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_nas_job(
            job_service.GetNasJobRequest(),
            name="name_value",
        )


def test_get_nas_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.ListNasJobsRequest,
        dict,
    ],
)
def test_list_nas_jobs_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = job_service.ListNasJobsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = job_service.ListNasJobsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.list_nas_jobs(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListNasJobsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_nas_jobs_rest_required_fields(
    request_type=job_service.ListNasJobsRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).list_nas_jobs._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_nas_jobs._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(
        (
            "filter",
            "page_size",
            "page_token",
            "read_mask",
        )
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = job_service.ListNasJobsResponse()
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
            return_value = job_service.ListNasJobsResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.list_nas_jobs(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_list_nas_jobs_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.list_nas_jobs._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(
            (
                "filter",
                "pageSize",
                "pageToken",
                "readMask",
            )
        )
        & set(("parent",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_nas_jobs_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "post_list_nas_jobs"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_list_nas_jobs"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.ListNasJobsRequest.pb(job_service.ListNasJobsRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = job_service.ListNasJobsResponse.to_json(
            job_service.ListNasJobsResponse()
        )

        request = job_service.ListNasJobsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = job_service.ListNasJobsResponse()

        client.list_nas_jobs(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_list_nas_jobs_rest_bad_request(
    transport: str = "rest", request_type=job_service.ListNasJobsRequest
):
    client = JobServiceClient(
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
        client.list_nas_jobs(request)


def test_list_nas_jobs_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = job_service.ListNasJobsResponse()

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
        return_value = job_service.ListNasJobsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.list_nas_jobs(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{parent=projects/*/locations/*}/nasJobs" % client.transport._host,
            args[1],
        )


def test_list_nas_jobs_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_nas_jobs(
            job_service.ListNasJobsRequest(),
            parent="parent_value",
        )


def test_list_nas_jobs_rest_pager(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            job_service.ListNasJobsResponse(
                nas_jobs=[
                    nas_job.NasJob(),
                    nas_job.NasJob(),
                    nas_job.NasJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListNasJobsResponse(
                nas_jobs=[],
                next_page_token="def",
            ),
            job_service.ListNasJobsResponse(
                nas_jobs=[
                    nas_job.NasJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListNasJobsResponse(
                nas_jobs=[
                    nas_job.NasJob(),
                    nas_job.NasJob(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(job_service.ListNasJobsResponse.to_json(x) for x in response)
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {"parent": "projects/sample1/locations/sample2"}

        pager = client.list_nas_jobs(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, nas_job.NasJob) for i in results)

        pages = list(client.list_nas_jobs(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.DeleteNasJobRequest,
        dict,
    ],
)
def test_delete_nas_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/nasJobs/sample3"}
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
        response = client.delete_nas_job(request)

    # Establish that the response is the type that we expect.
    assert response.operation.name == "operations/spam"


def test_delete_nas_job_rest_required_fields(
    request_type=job_service.DeleteNasJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).delete_nas_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).delete_nas_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = JobServiceClient(
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

            response = client.delete_nas_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_delete_nas_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.delete_nas_job._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_delete_nas_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.JobServiceRestInterceptor, "post_delete_nas_job"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_delete_nas_job"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.DeleteNasJobRequest.pb(
            job_service.DeleteNasJobRequest()
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

        request = job_service.DeleteNasJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()

        client.delete_nas_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_delete_nas_job_rest_bad_request(
    transport: str = "rest", request_type=job_service.DeleteNasJobRequest
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/nasJobs/sample3"}
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
        client.delete_nas_job(request)


def test_delete_nas_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {"name": "projects/sample1/locations/sample2/nasJobs/sample3"}

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

        client.delete_nas_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{name=projects/*/locations/*/nasJobs/*}" % client.transport._host,
            args[1],
        )


def test_delete_nas_job_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_nas_job(
            job_service.DeleteNasJobRequest(),
            name="name_value",
        )


def test_delete_nas_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.CancelNasJobRequest,
        dict,
    ],
)
def test_cancel_nas_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/nasJobs/sample3"}
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
        response = client.cancel_nas_job(request)

    # Establish that the response is the type that we expect.
    assert response is None


def test_cancel_nas_job_rest_required_fields(
    request_type=job_service.CancelNasJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).cancel_nas_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).cancel_nas_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = JobServiceClient(
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

            response = client.cancel_nas_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_cancel_nas_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.cancel_nas_job._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_cancel_nas_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_cancel_nas_job"
    ) as pre:
        pre.assert_not_called()
        pb_message = job_service.CancelNasJobRequest.pb(
            job_service.CancelNasJobRequest()
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

        request = job_service.CancelNasJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata

        client.cancel_nas_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()


def test_cancel_nas_job_rest_bad_request(
    transport: str = "rest", request_type=job_service.CancelNasJobRequest
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/nasJobs/sample3"}
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
        client.cancel_nas_job(request)


def test_cancel_nas_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # get arguments that satisfy an http rule for this method
        sample_request = {"name": "projects/sample1/locations/sample2/nasJobs/sample3"}

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

        client.cancel_nas_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{name=projects/*/locations/*/nasJobs/*}:cancel"
            % client.transport._host,
            args[1],
        )


def test_cancel_nas_job_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.cancel_nas_job(
            job_service.CancelNasJobRequest(),
            name="name_value",
        )


def test_cancel_nas_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.GetNasTrialDetailRequest,
        dict,
    ],
)
def test_get_nas_trial_detail_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/nasJobs/sample3/nasTrialDetails/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = nas_job.NasTrialDetail(
            name="name_value",
            parameters="parameters_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = nas_job.NasTrialDetail.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.get_nas_trial_detail(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, nas_job.NasTrialDetail)
    assert response.name == "name_value"
    assert response.parameters == "parameters_value"


def test_get_nas_trial_detail_rest_required_fields(
    request_type=job_service.GetNasTrialDetailRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).get_nas_trial_detail._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_nas_trial_detail._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = nas_job.NasTrialDetail()
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
            return_value = nas_job.NasTrialDetail.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.get_nas_trial_detail(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_nas_trial_detail_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_nas_trial_detail._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_nas_trial_detail_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "post_get_nas_trial_detail"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_get_nas_trial_detail"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.GetNasTrialDetailRequest.pb(
            job_service.GetNasTrialDetailRequest()
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
        req.return_value._content = nas_job.NasTrialDetail.to_json(
            nas_job.NasTrialDetail()
        )

        request = job_service.GetNasTrialDetailRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = nas_job.NasTrialDetail()

        client.get_nas_trial_detail(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_get_nas_trial_detail_rest_bad_request(
    transport: str = "rest", request_type=job_service.GetNasTrialDetailRequest
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/nasJobs/sample3/nasTrialDetails/sample4"
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
        client.get_nas_trial_detail(request)


def test_get_nas_trial_detail_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = nas_job.NasTrialDetail()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/nasJobs/sample3/nasTrialDetails/sample4"
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
        return_value = nas_job.NasTrialDetail.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.get_nas_trial_detail(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{name=projects/*/locations/*/nasJobs/*/nasTrialDetails/*}"
            % client.transport._host,
            args[1],
        )


def test_get_nas_trial_detail_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_nas_trial_detail(
            job_service.GetNasTrialDetailRequest(),
            name="name_value",
        )


def test_get_nas_trial_detail_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.ListNasTrialDetailsRequest,
        dict,
    ],
)
def test_list_nas_trial_details_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/nasJobs/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = job_service.ListNasTrialDetailsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = job_service.ListNasTrialDetailsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.list_nas_trial_details(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListNasTrialDetailsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_nas_trial_details_rest_required_fields(
    request_type=job_service.ListNasTrialDetailsRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).list_nas_trial_details._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_nas_trial_details._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(
        (
            "page_size",
            "page_token",
        )
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = job_service.ListNasTrialDetailsResponse()
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
            return_value = job_service.ListNasTrialDetailsResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.list_nas_trial_details(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_list_nas_trial_details_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.list_nas_trial_details._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(
            (
                "pageSize",
                "pageToken",
            )
        )
        & set(("parent",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_nas_trial_details_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "post_list_nas_trial_details"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_list_nas_trial_details"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.ListNasTrialDetailsRequest.pb(
            job_service.ListNasTrialDetailsRequest()
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
        req.return_value._content = job_service.ListNasTrialDetailsResponse.to_json(
            job_service.ListNasTrialDetailsResponse()
        )

        request = job_service.ListNasTrialDetailsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = job_service.ListNasTrialDetailsResponse()

        client.list_nas_trial_details(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_list_nas_trial_details_rest_bad_request(
    transport: str = "rest", request_type=job_service.ListNasTrialDetailsRequest
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/nasJobs/sample3"}
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
        client.list_nas_trial_details(request)


def test_list_nas_trial_details_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = job_service.ListNasTrialDetailsResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "parent": "projects/sample1/locations/sample2/nasJobs/sample3"
        }

        # get truthy value for each flattened field
        mock_args = dict(
            parent="parent_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = job_service.ListNasTrialDetailsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.list_nas_trial_details(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{parent=projects/*/locations/*/nasJobs/*}/nasTrialDetails"
            % client.transport._host,
            args[1],
        )


def test_list_nas_trial_details_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_nas_trial_details(
            job_service.ListNasTrialDetailsRequest(),
            parent="parent_value",
        )


def test_list_nas_trial_details_rest_pager(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            job_service.ListNasTrialDetailsResponse(
                nas_trial_details=[
                    nas_job.NasTrialDetail(),
                    nas_job.NasTrialDetail(),
                    nas_job.NasTrialDetail(),
                ],
                next_page_token="abc",
            ),
            job_service.ListNasTrialDetailsResponse(
                nas_trial_details=[],
                next_page_token="def",
            ),
            job_service.ListNasTrialDetailsResponse(
                nas_trial_details=[
                    nas_job.NasTrialDetail(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListNasTrialDetailsResponse(
                nas_trial_details=[
                    nas_job.NasTrialDetail(),
                    nas_job.NasTrialDetail(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(
            job_service.ListNasTrialDetailsResponse.to_json(x) for x in response
        )
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {
            "parent": "projects/sample1/locations/sample2/nasJobs/sample3"
        }

        pager = client.list_nas_trial_details(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, nas_job.NasTrialDetail) for i in results)

        pages = list(client.list_nas_trial_details(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.CreateBatchPredictionJobRequest,
        dict,
    ],
)
def test_create_batch_prediction_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request_init["batch_prediction_job"] = {
        "name": "name_value",
        "display_name": "display_name_value",
        "model": "model_value",
        "model_version_id": "model_version_id_value",
        "unmanaged_container_model": {
            "artifact_uri": "artifact_uri_value",
            "predict_schemata": {
                "instance_schema_uri": "instance_schema_uri_value",
                "parameters_schema_uri": "parameters_schema_uri_value",
                "prediction_schema_uri": "prediction_schema_uri_value",
            },
            "container_spec": {
                "image_uri": "image_uri_value",
                "command": ["command_value1", "command_value2"],
                "args": ["args_value1", "args_value2"],
                "env": [{"name": "name_value", "value": "value_value"}],
                "ports": [{"container_port": 1511}],
                "predict_route": "predict_route_value",
                "health_route": "health_route_value",
                "grpc_ports": {},
                "deployment_timeout": {"seconds": 751, "nanos": 543},
                "shared_memory_size_mb": 2231,
                "startup_probe": {
                    "exec_": {"command": ["command_value1", "command_value2"]},
                    "period_seconds": 1489,
                    "timeout_seconds": 1621,
                },
                "health_probe": {},
            },
        },
        "input_config": {
            "gcs_source": {"uris": ["uris_value1", "uris_value2"]},
            "bigquery_source": {"input_uri": "input_uri_value"},
            "instances_format": "instances_format_value",
        },
        "instance_config": {
            "instance_type": "instance_type_value",
            "key_field": "key_field_value",
            "included_fields": ["included_fields_value1", "included_fields_value2"],
            "excluded_fields": ["excluded_fields_value1", "excluded_fields_value2"],
        },
        "model_parameters": {
            "null_value": 0,
            "number_value": 0.1285,
            "string_value": "string_value_value",
            "bool_value": True,
            "struct_value": {"fields": {}},
            "list_value": {"values": {}},
        },
        "output_config": {
            "gcs_destination": {"output_uri_prefix": "output_uri_prefix_value"},
            "bigquery_destination": {"output_uri": "output_uri_value"},
            "predictions_format": "predictions_format_value",
        },
        "dedicated_resources": {
            "machine_spec": {
                "machine_type": "machine_type_value",
                "accelerator_type": 1,
                "accelerator_count": 1805,
                "tpu_topology": "tpu_topology_value",
            },
            "starting_replica_count": 2355,
            "max_replica_count": 1805,
        },
        "service_account": "service_account_value",
        "manual_batch_tuning_parameters": {"batch_size": 1052},
        "generate_explanation": True,
        "explanation_spec": {
            "parameters": {
                "sampled_shapley_attribution": {"path_count": 1077},
                "integrated_gradients_attribution": {
                    "step_count": 1092,
                    "smooth_grad_config": {
                        "noise_sigma": 0.11660000000000001,
                        "feature_noise_sigma": {
                            "noise_sigma": [{"name": "name_value", "sigma": 0.529}]
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
                    "example_gcs_source": {"data_format": 1, "gcs_source": {}},
                    "nearest_neighbor_search_config": {},
                    "presets": {"query": 1, "modality": 1},
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
        "output_info": {
            "gcs_output_directory": "gcs_output_directory_value",
            "bigquery_output_dataset": "bigquery_output_dataset_value",
            "bigquery_output_table": "bigquery_output_table_value",
        },
        "state": 1,
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
        "partial_failures": {},
        "resources_consumed": {"replica_hours": 0.13920000000000002},
        "completion_stats": {
            "successful_count": 1736,
            "failed_count": 1261,
            "incomplete_count": 1720,
            "successful_forecast_point_count": 3335,
        },
        "create_time": {"seconds": 751, "nanos": 543},
        "start_time": {},
        "end_time": {},
        "update_time": {},
        "labels": {},
        "encryption_spec": {"kms_key_name": "kms_key_name_value"},
        "disable_container_logging": True,
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = job_service.CreateBatchPredictionJobRequest.meta.fields[
        "batch_prediction_job"
    ]

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
    for field, value in request_init[
        "batch_prediction_job"
    ].items():  # pragma: NO COVER
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
                for i in range(0, len(request_init["batch_prediction_job"][field])):
                    del request_init["batch_prediction_job"][field][i][subfield]
            else:
                del request_init["batch_prediction_job"][field][subfield]
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gca_batch_prediction_job.BatchPredictionJob(
            name="name_value",
            display_name="display_name_value",
            model="model_value",
            model_version_id="model_version_id_value",
            service_account="service_account_value",
            generate_explanation=True,
            state=job_state.JobState.JOB_STATE_QUEUED,
            disable_container_logging=True,
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = gca_batch_prediction_job.BatchPredictionJob.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.create_batch_prediction_job(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_batch_prediction_job.BatchPredictionJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.model == "model_value"
    assert response.model_version_id == "model_version_id_value"
    assert response.service_account == "service_account_value"
    assert response.generate_explanation is True
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert response.disable_container_logging is True


def test_create_batch_prediction_job_rest_required_fields(
    request_type=job_service.CreateBatchPredictionJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).create_batch_prediction_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).create_batch_prediction_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = gca_batch_prediction_job.BatchPredictionJob()
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
            return_value = gca_batch_prediction_job.BatchPredictionJob.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.create_batch_prediction_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_create_batch_prediction_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.create_batch_prediction_job._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(())
        & set(
            (
                "parent",
                "batchPredictionJob",
            )
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_create_batch_prediction_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "post_create_batch_prediction_job"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_create_batch_prediction_job"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.CreateBatchPredictionJobRequest.pb(
            job_service.CreateBatchPredictionJobRequest()
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
        req.return_value._content = gca_batch_prediction_job.BatchPredictionJob.to_json(
            gca_batch_prediction_job.BatchPredictionJob()
        )

        request = job_service.CreateBatchPredictionJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = gca_batch_prediction_job.BatchPredictionJob()

        client.create_batch_prediction_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_create_batch_prediction_job_rest_bad_request(
    transport: str = "rest", request_type=job_service.CreateBatchPredictionJobRequest
):
    client = JobServiceClient(
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
        client.create_batch_prediction_job(request)


def test_create_batch_prediction_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gca_batch_prediction_job.BatchPredictionJob()

        # get arguments that satisfy an http rule for this method
        sample_request = {"parent": "projects/sample1/locations/sample2"}

        # get truthy value for each flattened field
        mock_args = dict(
            parent="parent_value",
            batch_prediction_job=gca_batch_prediction_job.BatchPredictionJob(
                name="name_value"
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = gca_batch_prediction_job.BatchPredictionJob.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.create_batch_prediction_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{parent=projects/*/locations/*}/batchPredictionJobs"
            % client.transport._host,
            args[1],
        )


def test_create_batch_prediction_job_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_batch_prediction_job(
            job_service.CreateBatchPredictionJobRequest(),
            parent="parent_value",
            batch_prediction_job=gca_batch_prediction_job.BatchPredictionJob(
                name="name_value"
            ),
        )


def test_create_batch_prediction_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.GetBatchPredictionJobRequest,
        dict,
    ],
)
def test_get_batch_prediction_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/batchPredictionJobs/sample3"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = batch_prediction_job.BatchPredictionJob(
            name="name_value",
            display_name="display_name_value",
            model="model_value",
            model_version_id="model_version_id_value",
            service_account="service_account_value",
            generate_explanation=True,
            state=job_state.JobState.JOB_STATE_QUEUED,
            disable_container_logging=True,
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = batch_prediction_job.BatchPredictionJob.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.get_batch_prediction_job(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, batch_prediction_job.BatchPredictionJob)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.model == "model_value"
    assert response.model_version_id == "model_version_id_value"
    assert response.service_account == "service_account_value"
    assert response.generate_explanation is True
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert response.disable_container_logging is True


def test_get_batch_prediction_job_rest_required_fields(
    request_type=job_service.GetBatchPredictionJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).get_batch_prediction_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_batch_prediction_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = batch_prediction_job.BatchPredictionJob()
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
            return_value = batch_prediction_job.BatchPredictionJob.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.get_batch_prediction_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_batch_prediction_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_batch_prediction_job._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_batch_prediction_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "post_get_batch_prediction_job"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_get_batch_prediction_job"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.GetBatchPredictionJobRequest.pb(
            job_service.GetBatchPredictionJobRequest()
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
        req.return_value._content = batch_prediction_job.BatchPredictionJob.to_json(
            batch_prediction_job.BatchPredictionJob()
        )

        request = job_service.GetBatchPredictionJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = batch_prediction_job.BatchPredictionJob()

        client.get_batch_prediction_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_get_batch_prediction_job_rest_bad_request(
    transport: str = "rest", request_type=job_service.GetBatchPredictionJobRequest
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/batchPredictionJobs/sample3"
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
        client.get_batch_prediction_job(request)


def test_get_batch_prediction_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = batch_prediction_job.BatchPredictionJob()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/batchPredictionJobs/sample3"
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
        return_value = batch_prediction_job.BatchPredictionJob.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.get_batch_prediction_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{name=projects/*/locations/*/batchPredictionJobs/*}"
            % client.transport._host,
            args[1],
        )


def test_get_batch_prediction_job_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_batch_prediction_job(
            job_service.GetBatchPredictionJobRequest(),
            name="name_value",
        )


def test_get_batch_prediction_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.ListBatchPredictionJobsRequest,
        dict,
    ],
)
def test_list_batch_prediction_jobs_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = job_service.ListBatchPredictionJobsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = job_service.ListBatchPredictionJobsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.list_batch_prediction_jobs(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListBatchPredictionJobsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_batch_prediction_jobs_rest_required_fields(
    request_type=job_service.ListBatchPredictionJobsRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).list_batch_prediction_jobs._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_batch_prediction_jobs._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(
        (
            "filter",
            "page_size",
            "page_token",
            "read_mask",
        )
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = job_service.ListBatchPredictionJobsResponse()
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
            return_value = job_service.ListBatchPredictionJobsResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.list_batch_prediction_jobs(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_list_batch_prediction_jobs_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.list_batch_prediction_jobs._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(
            (
                "filter",
                "pageSize",
                "pageToken",
                "readMask",
            )
        )
        & set(("parent",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_batch_prediction_jobs_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "post_list_batch_prediction_jobs"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_list_batch_prediction_jobs"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.ListBatchPredictionJobsRequest.pb(
            job_service.ListBatchPredictionJobsRequest()
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
        req.return_value._content = job_service.ListBatchPredictionJobsResponse.to_json(
            job_service.ListBatchPredictionJobsResponse()
        )

        request = job_service.ListBatchPredictionJobsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = job_service.ListBatchPredictionJobsResponse()

        client.list_batch_prediction_jobs(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_list_batch_prediction_jobs_rest_bad_request(
    transport: str = "rest", request_type=job_service.ListBatchPredictionJobsRequest
):
    client = JobServiceClient(
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
        client.list_batch_prediction_jobs(request)


def test_list_batch_prediction_jobs_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = job_service.ListBatchPredictionJobsResponse()

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
        return_value = job_service.ListBatchPredictionJobsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.list_batch_prediction_jobs(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{parent=projects/*/locations/*}/batchPredictionJobs"
            % client.transport._host,
            args[1],
        )


def test_list_batch_prediction_jobs_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_batch_prediction_jobs(
            job_service.ListBatchPredictionJobsRequest(),
            parent="parent_value",
        )


def test_list_batch_prediction_jobs_rest_pager(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[
                    batch_prediction_job.BatchPredictionJob(),
                    batch_prediction_job.BatchPredictionJob(),
                    batch_prediction_job.BatchPredictionJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[],
                next_page_token="def",
            ),
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[
                    batch_prediction_job.BatchPredictionJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListBatchPredictionJobsResponse(
                batch_prediction_jobs=[
                    batch_prediction_job.BatchPredictionJob(),
                    batch_prediction_job.BatchPredictionJob(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(
            job_service.ListBatchPredictionJobsResponse.to_json(x) for x in response
        )
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {"parent": "projects/sample1/locations/sample2"}

        pager = client.list_batch_prediction_jobs(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(
            isinstance(i, batch_prediction_job.BatchPredictionJob) for i in results
        )

        pages = list(client.list_batch_prediction_jobs(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.DeleteBatchPredictionJobRequest,
        dict,
    ],
)
def test_delete_batch_prediction_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/batchPredictionJobs/sample3"
    }
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
        response = client.delete_batch_prediction_job(request)

    # Establish that the response is the type that we expect.
    assert response.operation.name == "operations/spam"


def test_delete_batch_prediction_job_rest_required_fields(
    request_type=job_service.DeleteBatchPredictionJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).delete_batch_prediction_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).delete_batch_prediction_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = JobServiceClient(
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

            response = client.delete_batch_prediction_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_delete_batch_prediction_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.delete_batch_prediction_job._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_delete_batch_prediction_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.JobServiceRestInterceptor, "post_delete_batch_prediction_job"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_delete_batch_prediction_job"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.DeleteBatchPredictionJobRequest.pb(
            job_service.DeleteBatchPredictionJobRequest()
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

        request = job_service.DeleteBatchPredictionJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()

        client.delete_batch_prediction_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_delete_batch_prediction_job_rest_bad_request(
    transport: str = "rest", request_type=job_service.DeleteBatchPredictionJobRequest
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/batchPredictionJobs/sample3"
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
        client.delete_batch_prediction_job(request)


def test_delete_batch_prediction_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/batchPredictionJobs/sample3"
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

        client.delete_batch_prediction_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{name=projects/*/locations/*/batchPredictionJobs/*}"
            % client.transport._host,
            args[1],
        )


def test_delete_batch_prediction_job_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_batch_prediction_job(
            job_service.DeleteBatchPredictionJobRequest(),
            name="name_value",
        )


def test_delete_batch_prediction_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.CancelBatchPredictionJobRequest,
        dict,
    ],
)
def test_cancel_batch_prediction_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/batchPredictionJobs/sample3"
    }
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
        response = client.cancel_batch_prediction_job(request)

    # Establish that the response is the type that we expect.
    assert response is None


def test_cancel_batch_prediction_job_rest_required_fields(
    request_type=job_service.CancelBatchPredictionJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).cancel_batch_prediction_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).cancel_batch_prediction_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = JobServiceClient(
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

            response = client.cancel_batch_prediction_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_cancel_batch_prediction_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.cancel_batch_prediction_job._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_cancel_batch_prediction_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_cancel_batch_prediction_job"
    ) as pre:
        pre.assert_not_called()
        pb_message = job_service.CancelBatchPredictionJobRequest.pb(
            job_service.CancelBatchPredictionJobRequest()
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

        request = job_service.CancelBatchPredictionJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata

        client.cancel_batch_prediction_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()


def test_cancel_batch_prediction_job_rest_bad_request(
    transport: str = "rest", request_type=job_service.CancelBatchPredictionJobRequest
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/batchPredictionJobs/sample3"
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
        client.cancel_batch_prediction_job(request)


def test_cancel_batch_prediction_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/batchPredictionJobs/sample3"
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

        client.cancel_batch_prediction_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{name=projects/*/locations/*/batchPredictionJobs/*}:cancel"
            % client.transport._host,
            args[1],
        )


def test_cancel_batch_prediction_job_rest_flattened_error(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.cancel_batch_prediction_job(
            job_service.CancelBatchPredictionJobRequest(),
            name="name_value",
        )


def test_cancel_batch_prediction_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.CreateModelDeploymentMonitoringJobRequest,
        dict,
    ],
)
def test_create_model_deployment_monitoring_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request_init["model_deployment_monitoring_job"] = {
        "name": "name_value",
        "display_name": "display_name_value",
        "endpoint": "endpoint_value",
        "state": 1,
        "schedule_state": 1,
        "latest_monitoring_pipeline_metadata": {
            "run_time": {"seconds": 751, "nanos": 543},
            "status": {
                "code": 411,
                "message": "message_value",
                "details": [
                    {
                        "type_url": "type.googleapis.com/google.protobuf.Duration",
                        "value": b"\x08\x0c\x10\xdb\x07",
                    }
                ],
            },
        },
        "model_deployment_monitoring_objective_configs": [
            {
                "deployed_model_id": "deployed_model_id_value",
                "objective_config": {
                    "training_dataset": {
                        "dataset": "dataset_value",
                        "gcs_source": {"uris": ["uris_value1", "uris_value2"]},
                        "bigquery_source": {"input_uri": "input_uri_value"},
                        "data_format": "data_format_value",
                        "target_field": "target_field_value",
                        "logging_sampling_strategy": {
                            "random_sample_config": {"sample_rate": 0.1165}
                        },
                    },
                    "training_prediction_skew_detection_config": {
                        "skew_thresholds": {},
                        "attribution_score_skew_thresholds": {},
                        "default_skew_threshold": {"value": 0.541},
                    },
                    "prediction_drift_detection_config": {
                        "drift_thresholds": {},
                        "attribution_score_drift_thresholds": {},
                        "default_drift_threshold": {},
                    },
                    "explanation_config": {
                        "enable_feature_attributes": True,
                        "explanation_baseline": {
                            "gcs": {"output_uri_prefix": "output_uri_prefix_value"},
                            "bigquery": {"output_uri": "output_uri_value"},
                            "prediction_format": 2,
                        },
                    },
                },
            }
        ],
        "model_deployment_monitoring_schedule_config": {
            "monitor_interval": {"seconds": 751, "nanos": 543},
            "monitor_window": {},
        },
        "logging_sampling_strategy": {},
        "model_monitoring_alert_config": {
            "email_alert_config": {
                "user_emails": ["user_emails_value1", "user_emails_value2"]
            },
            "enable_logging": True,
            "notification_channels": [
                "notification_channels_value1",
                "notification_channels_value2",
            ],
        },
        "predict_instance_schema_uri": "predict_instance_schema_uri_value",
        "sample_predict_instance": {
            "null_value": 0,
            "number_value": 0.1285,
            "string_value": "string_value_value",
            "bool_value": True,
            "struct_value": {"fields": {}},
            "list_value": {"values": {}},
        },
        "analysis_instance_schema_uri": "analysis_instance_schema_uri_value",
        "bigquery_tables": [
            {
                "log_source": 1,
                "log_type": 1,
                "bigquery_table_path": "bigquery_table_path_value",
                "request_response_logging_schema_version": "request_response_logging_schema_version_value",
            }
        ],
        "log_ttl": {},
        "labels": {},
        "create_time": {},
        "update_time": {},
        "next_schedule_time": {},
        "stats_anomalies_base_directory": {},
        "encryption_spec": {"kms_key_name": "kms_key_name_value"},
        "enable_monitoring_pipeline_logs": True,
        "error": {},
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = job_service.CreateModelDeploymentMonitoringJobRequest.meta.fields[
        "model_deployment_monitoring_job"
    ]

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
    for field, value in request_init[
        "model_deployment_monitoring_job"
    ].items():  # pragma: NO COVER
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
                for i in range(
                    0, len(request_init["model_deployment_monitoring_job"][field])
                ):
                    del request_init["model_deployment_monitoring_job"][field][i][
                        subfield
                    ]
            else:
                del request_init["model_deployment_monitoring_job"][field][subfield]
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob(
            name="name_value",
            display_name="display_name_value",
            endpoint="endpoint_value",
            state=job_state.JobState.JOB_STATE_QUEUED,
            schedule_state=gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob.MonitoringScheduleState.PENDING,
            predict_instance_schema_uri="predict_instance_schema_uri_value",
            analysis_instance_schema_uri="analysis_instance_schema_uri_value",
            enable_monitoring_pipeline_logs=True,
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = (
            gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob.pb(
                return_value
            )
        )
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.create_model_deployment_monitoring_job(request)

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob
    )
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.endpoint == "endpoint_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert (
        response.schedule_state
        == gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob.MonitoringScheduleState.PENDING
    )
    assert response.predict_instance_schema_uri == "predict_instance_schema_uri_value"
    assert response.analysis_instance_schema_uri == "analysis_instance_schema_uri_value"
    assert response.enable_monitoring_pipeline_logs is True


def test_create_model_deployment_monitoring_job_rest_required_fields(
    request_type=job_service.CreateModelDeploymentMonitoringJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).create_model_deployment_monitoring_job._get_unset_required_fields(
        jsonified_request
    )
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).create_model_deployment_monitoring_job._get_unset_required_fields(
        jsonified_request
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob()
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
            return_value = (
                gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob.pb(
                    return_value
                )
            )
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.create_model_deployment_monitoring_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_create_model_deployment_monitoring_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = (
        transport.create_model_deployment_monitoring_job._get_unset_required_fields({})
    )
    assert set(unset_fields) == (
        set(())
        & set(
            (
                "parent",
                "modelDeploymentMonitoringJob",
            )
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_create_model_deployment_monitoring_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor,
        "post_create_model_deployment_monitoring_job",
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor,
        "pre_create_model_deployment_monitoring_job",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.CreateModelDeploymentMonitoringJobRequest.pb(
            job_service.CreateModelDeploymentMonitoringJobRequest()
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
        req.return_value._content = (
            gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob.to_json(
                gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob()
            )
        )

        request = job_service.CreateModelDeploymentMonitoringJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = (
            gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob()
        )

        client.create_model_deployment_monitoring_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_create_model_deployment_monitoring_job_rest_bad_request(
    transport: str = "rest",
    request_type=job_service.CreateModelDeploymentMonitoringJobRequest,
):
    client = JobServiceClient(
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
        client.create_model_deployment_monitoring_job(request)


def test_create_model_deployment_monitoring_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = (
            gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob()
        )

        # get arguments that satisfy an http rule for this method
        sample_request = {"parent": "projects/sample1/locations/sample2"}

        # get truthy value for each flattened field
        mock_args = dict(
            parent="parent_value",
            model_deployment_monitoring_job=gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob(
                name="name_value"
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = (
            gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob.pb(
                return_value
            )
        )
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.create_model_deployment_monitoring_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{parent=projects/*/locations/*}/modelDeploymentMonitoringJobs"
            % client.transport._host,
            args[1],
        )


def test_create_model_deployment_monitoring_job_rest_flattened_error(
    transport: str = "rest",
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_model_deployment_monitoring_job(
            job_service.CreateModelDeploymentMonitoringJobRequest(),
            parent="parent_value",
            model_deployment_monitoring_job=gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob(
                name="name_value"
            ),
        )


def test_create_model_deployment_monitoring_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest,
        dict,
    ],
)
def test_search_model_deployment_monitoring_stats_anomalies_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {
        "model_deployment_monitoring_job": "projects/sample1/locations/sample2/modelDeploymentMonitoringJobs/sample3"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = (
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                next_page_token="next_page_token_value",
            )
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = (
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse.pb(
                return_value
            )
        )
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.search_model_deployment_monitoring_stats_anomalies(request)

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, pagers.SearchModelDeploymentMonitoringStatsAnomaliesPager
    )
    assert response.next_page_token == "next_page_token_value"


def test_search_model_deployment_monitoring_stats_anomalies_rest_required_fields(
    request_type=job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest,
):
    transport_class = transports.JobServiceRestTransport

    request_init = {}
    request_init["model_deployment_monitoring_job"] = ""
    request_init["deployed_model_id"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(pb_request, use_integers_for_enums=False)
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).search_model_deployment_monitoring_stats_anomalies._get_unset_required_fields(
        jsonified_request
    )
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request[
        "modelDeploymentMonitoringJob"
    ] = "model_deployment_monitoring_job_value"
    jsonified_request["deployedModelId"] = "deployed_model_id_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).search_model_deployment_monitoring_stats_anomalies._get_unset_required_fields(
        jsonified_request
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "modelDeploymentMonitoringJob" in jsonified_request
    assert (
        jsonified_request["modelDeploymentMonitoringJob"]
        == "model_deployment_monitoring_job_value"
    )
    assert "deployedModelId" in jsonified_request
    assert jsonified_request["deployedModelId"] == "deployed_model_id_value"

    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse()
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
            return_value = (
                job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse.pb(
                    return_value
                )
            )
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.search_model_deployment_monitoring_stats_anomalies(
                request
            )

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_search_model_deployment_monitoring_stats_anomalies_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.search_model_deployment_monitoring_stats_anomalies._get_unset_required_fields(
        {}
    )
    assert set(unset_fields) == (
        set(())
        & set(
            (
                "modelDeploymentMonitoringJob",
                "deployedModelId",
                "objectives",
            )
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_search_model_deployment_monitoring_stats_anomalies_rest_interceptors(
    null_interceptor,
):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor,
        "post_search_model_deployment_monitoring_stats_anomalies",
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor,
        "pre_search_model_deployment_monitoring_stats_anomalies",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = (
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest.pb(
                job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest()
            )
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
        req.return_value._content = (
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse.to_json(
                job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse()
            )
        )

        request = job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = (
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse()
        )

        client.search_model_deployment_monitoring_stats_anomalies(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_search_model_deployment_monitoring_stats_anomalies_rest_bad_request(
    transport: str = "rest",
    request_type=job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest,
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {
        "model_deployment_monitoring_job": "projects/sample1/locations/sample2/modelDeploymentMonitoringJobs/sample3"
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
        client.search_model_deployment_monitoring_stats_anomalies(request)


def test_search_model_deployment_monitoring_stats_anomalies_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = (
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse()
        )

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "model_deployment_monitoring_job": "projects/sample1/locations/sample2/modelDeploymentMonitoringJobs/sample3"
        }

        # get truthy value for each flattened field
        mock_args = dict(
            model_deployment_monitoring_job="model_deployment_monitoring_job_value",
            deployed_model_id="deployed_model_id_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = (
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse.pb(
                return_value
            )
        )
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.search_model_deployment_monitoring_stats_anomalies(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{model_deployment_monitoring_job=projects/*/locations/*/modelDeploymentMonitoringJobs/*}:searchModelDeploymentMonitoringStatsAnomalies"
            % client.transport._host,
            args[1],
        )


def test_search_model_deployment_monitoring_stats_anomalies_rest_flattened_error(
    transport: str = "rest",
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.search_model_deployment_monitoring_stats_anomalies(
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesRequest(),
            model_deployment_monitoring_job="model_deployment_monitoring_job_value",
            deployed_model_id="deployed_model_id_value",
        )


def test_search_model_deployment_monitoring_stats_anomalies_rest_pager(
    transport: str = "rest",
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                monitoring_stats=[
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                ],
                next_page_token="abc",
            ),
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                monitoring_stats=[],
                next_page_token="def",
            ),
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                monitoring_stats=[
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                ],
                next_page_token="ghi",
            ),
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse(
                monitoring_stats=[
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                    gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(
            job_service.SearchModelDeploymentMonitoringStatsAnomaliesResponse.to_json(x)
            for x in response
        )
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {
            "model_deployment_monitoring_job": "projects/sample1/locations/sample2/modelDeploymentMonitoringJobs/sample3"
        }

        pager = client.search_model_deployment_monitoring_stats_anomalies(
            request=sample_request
        )

        results = list(pager)
        assert len(results) == 6
        assert all(
            isinstance(
                i, gca_model_deployment_monitoring_job.ModelMonitoringStatsAnomalies
            )
            for i in results
        )

        pages = list(
            client.search_model_deployment_monitoring_stats_anomalies(
                request=sample_request
            ).pages
        )
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.GetModelDeploymentMonitoringJobRequest,
        dict,
    ],
)
def test_get_model_deployment_monitoring_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/modelDeploymentMonitoringJobs/sample3"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = model_deployment_monitoring_job.ModelDeploymentMonitoringJob(
            name="name_value",
            display_name="display_name_value",
            endpoint="endpoint_value",
            state=job_state.JobState.JOB_STATE_QUEUED,
            schedule_state=model_deployment_monitoring_job.ModelDeploymentMonitoringJob.MonitoringScheduleState.PENDING,
            predict_instance_schema_uri="predict_instance_schema_uri_value",
            analysis_instance_schema_uri="analysis_instance_schema_uri_value",
            enable_monitoring_pipeline_logs=True,
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = model_deployment_monitoring_job.ModelDeploymentMonitoringJob.pb(
            return_value
        )
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.get_model_deployment_monitoring_job(request)

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, model_deployment_monitoring_job.ModelDeploymentMonitoringJob
    )
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.endpoint == "endpoint_value"
    assert response.state == job_state.JobState.JOB_STATE_QUEUED
    assert (
        response.schedule_state
        == model_deployment_monitoring_job.ModelDeploymentMonitoringJob.MonitoringScheduleState.PENDING
    )
    assert response.predict_instance_schema_uri == "predict_instance_schema_uri_value"
    assert response.analysis_instance_schema_uri == "analysis_instance_schema_uri_value"
    assert response.enable_monitoring_pipeline_logs is True


def test_get_model_deployment_monitoring_job_rest_required_fields(
    request_type=job_service.GetModelDeploymentMonitoringJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).get_model_deployment_monitoring_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_model_deployment_monitoring_job._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = model_deployment_monitoring_job.ModelDeploymentMonitoringJob()
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
            return_value = (
                model_deployment_monitoring_job.ModelDeploymentMonitoringJob.pb(
                    return_value
                )
            )
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.get_model_deployment_monitoring_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_model_deployment_monitoring_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = (
        transport.get_model_deployment_monitoring_job._get_unset_required_fields({})
    )
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_model_deployment_monitoring_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor, "post_get_model_deployment_monitoring_job"
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor, "pre_get_model_deployment_monitoring_job"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.GetModelDeploymentMonitoringJobRequest.pb(
            job_service.GetModelDeploymentMonitoringJobRequest()
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
        req.return_value._content = (
            model_deployment_monitoring_job.ModelDeploymentMonitoringJob.to_json(
                model_deployment_monitoring_job.ModelDeploymentMonitoringJob()
            )
        )

        request = job_service.GetModelDeploymentMonitoringJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = (
            model_deployment_monitoring_job.ModelDeploymentMonitoringJob()
        )

        client.get_model_deployment_monitoring_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_get_model_deployment_monitoring_job_rest_bad_request(
    transport: str = "rest",
    request_type=job_service.GetModelDeploymentMonitoringJobRequest,
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/modelDeploymentMonitoringJobs/sample3"
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
        client.get_model_deployment_monitoring_job(request)


def test_get_model_deployment_monitoring_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = model_deployment_monitoring_job.ModelDeploymentMonitoringJob()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/modelDeploymentMonitoringJobs/sample3"
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
        return_value = model_deployment_monitoring_job.ModelDeploymentMonitoringJob.pb(
            return_value
        )
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.get_model_deployment_monitoring_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*}"
            % client.transport._host,
            args[1],
        )


def test_get_model_deployment_monitoring_job_rest_flattened_error(
    transport: str = "rest",
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_model_deployment_monitoring_job(
            job_service.GetModelDeploymentMonitoringJobRequest(),
            name="name_value",
        )


def test_get_model_deployment_monitoring_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.ListModelDeploymentMonitoringJobsRequest,
        dict,
    ],
)
def test_list_model_deployment_monitoring_jobs_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = job_service.ListModelDeploymentMonitoringJobsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = job_service.ListModelDeploymentMonitoringJobsResponse.pb(
            return_value
        )
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.list_model_deployment_monitoring_jobs(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListModelDeploymentMonitoringJobsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_model_deployment_monitoring_jobs_rest_required_fields(
    request_type=job_service.ListModelDeploymentMonitoringJobsRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).list_model_deployment_monitoring_jobs._get_unset_required_fields(
        jsonified_request
    )
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_model_deployment_monitoring_jobs._get_unset_required_fields(
        jsonified_request
    )
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(
        (
            "filter",
            "page_size",
            "page_token",
            "read_mask",
        )
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = job_service.ListModelDeploymentMonitoringJobsResponse()
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
            return_value = job_service.ListModelDeploymentMonitoringJobsResponse.pb(
                return_value
            )
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.list_model_deployment_monitoring_jobs(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_list_model_deployment_monitoring_jobs_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = (
        transport.list_model_deployment_monitoring_jobs._get_unset_required_fields({})
    )
    assert set(unset_fields) == (
        set(
            (
                "filter",
                "pageSize",
                "pageToken",
                "readMask",
            )
        )
        & set(("parent",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_model_deployment_monitoring_jobs_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor,
        "post_list_model_deployment_monitoring_jobs",
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor,
        "pre_list_model_deployment_monitoring_jobs",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.ListModelDeploymentMonitoringJobsRequest.pb(
            job_service.ListModelDeploymentMonitoringJobsRequest()
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
        req.return_value._content = (
            job_service.ListModelDeploymentMonitoringJobsResponse.to_json(
                job_service.ListModelDeploymentMonitoringJobsResponse()
            )
        )

        request = job_service.ListModelDeploymentMonitoringJobsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = job_service.ListModelDeploymentMonitoringJobsResponse()

        client.list_model_deployment_monitoring_jobs(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_list_model_deployment_monitoring_jobs_rest_bad_request(
    transport: str = "rest",
    request_type=job_service.ListModelDeploymentMonitoringJobsRequest,
):
    client = JobServiceClient(
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
        client.list_model_deployment_monitoring_jobs(request)


def test_list_model_deployment_monitoring_jobs_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = job_service.ListModelDeploymentMonitoringJobsResponse()

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
        return_value = job_service.ListModelDeploymentMonitoringJobsResponse.pb(
            return_value
        )
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.list_model_deployment_monitoring_jobs(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{parent=projects/*/locations/*}/modelDeploymentMonitoringJobs"
            % client.transport._host,
            args[1],
        )


def test_list_model_deployment_monitoring_jobs_rest_flattened_error(
    transport: str = "rest",
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_model_deployment_monitoring_jobs(
            job_service.ListModelDeploymentMonitoringJobsRequest(),
            parent="parent_value",
        )


def test_list_model_deployment_monitoring_jobs_rest_pager(transport: str = "rest"):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            job_service.ListModelDeploymentMonitoringJobsResponse(
                model_deployment_monitoring_jobs=[
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                ],
                next_page_token="abc",
            ),
            job_service.ListModelDeploymentMonitoringJobsResponse(
                model_deployment_monitoring_jobs=[],
                next_page_token="def",
            ),
            job_service.ListModelDeploymentMonitoringJobsResponse(
                model_deployment_monitoring_jobs=[
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                ],
                next_page_token="ghi",
            ),
            job_service.ListModelDeploymentMonitoringJobsResponse(
                model_deployment_monitoring_jobs=[
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                    model_deployment_monitoring_job.ModelDeploymentMonitoringJob(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(
            job_service.ListModelDeploymentMonitoringJobsResponse.to_json(x)
            for x in response
        )
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {"parent": "projects/sample1/locations/sample2"}

        pager = client.list_model_deployment_monitoring_jobs(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(
            isinstance(i, model_deployment_monitoring_job.ModelDeploymentMonitoringJob)
            for i in results
        )

        pages = list(
            client.list_model_deployment_monitoring_jobs(request=sample_request).pages
        )
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.UpdateModelDeploymentMonitoringJobRequest,
        dict,
    ],
)
def test_update_model_deployment_monitoring_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {
        "model_deployment_monitoring_job": {
            "name": "projects/sample1/locations/sample2/modelDeploymentMonitoringJobs/sample3"
        }
    }
    request_init["model_deployment_monitoring_job"] = {
        "name": "projects/sample1/locations/sample2/modelDeploymentMonitoringJobs/sample3",
        "display_name": "display_name_value",
        "endpoint": "endpoint_value",
        "state": 1,
        "schedule_state": 1,
        "latest_monitoring_pipeline_metadata": {
            "run_time": {"seconds": 751, "nanos": 543},
            "status": {
                "code": 411,
                "message": "message_value",
                "details": [
                    {
                        "type_url": "type.googleapis.com/google.protobuf.Duration",
                        "value": b"\x08\x0c\x10\xdb\x07",
                    }
                ],
            },
        },
        "model_deployment_monitoring_objective_configs": [
            {
                "deployed_model_id": "deployed_model_id_value",
                "objective_config": {
                    "training_dataset": {
                        "dataset": "dataset_value",
                        "gcs_source": {"uris": ["uris_value1", "uris_value2"]},
                        "bigquery_source": {"input_uri": "input_uri_value"},
                        "data_format": "data_format_value",
                        "target_field": "target_field_value",
                        "logging_sampling_strategy": {
                            "random_sample_config": {"sample_rate": 0.1165}
                        },
                    },
                    "training_prediction_skew_detection_config": {
                        "skew_thresholds": {},
                        "attribution_score_skew_thresholds": {},
                        "default_skew_threshold": {"value": 0.541},
                    },
                    "prediction_drift_detection_config": {
                        "drift_thresholds": {},
                        "attribution_score_drift_thresholds": {},
                        "default_drift_threshold": {},
                    },
                    "explanation_config": {
                        "enable_feature_attributes": True,
                        "explanation_baseline": {
                            "gcs": {"output_uri_prefix": "output_uri_prefix_value"},
                            "bigquery": {"output_uri": "output_uri_value"},
                            "prediction_format": 2,
                        },
                    },
                },
            }
        ],
        "model_deployment_monitoring_schedule_config": {
            "monitor_interval": {"seconds": 751, "nanos": 543},
            "monitor_window": {},
        },
        "logging_sampling_strategy": {},
        "model_monitoring_alert_config": {
            "email_alert_config": {
                "user_emails": ["user_emails_value1", "user_emails_value2"]
            },
            "enable_logging": True,
            "notification_channels": [
                "notification_channels_value1",
                "notification_channels_value2",
            ],
        },
        "predict_instance_schema_uri": "predict_instance_schema_uri_value",
        "sample_predict_instance": {
            "null_value": 0,
            "number_value": 0.1285,
            "string_value": "string_value_value",
            "bool_value": True,
            "struct_value": {"fields": {}},
            "list_value": {"values": {}},
        },
        "analysis_instance_schema_uri": "analysis_instance_schema_uri_value",
        "bigquery_tables": [
            {
                "log_source": 1,
                "log_type": 1,
                "bigquery_table_path": "bigquery_table_path_value",
                "request_response_logging_schema_version": "request_response_logging_schema_version_value",
            }
        ],
        "log_ttl": {},
        "labels": {},
        "create_time": {},
        "update_time": {},
        "next_schedule_time": {},
        "stats_anomalies_base_directory": {},
        "encryption_spec": {"kms_key_name": "kms_key_name_value"},
        "enable_monitoring_pipeline_logs": True,
        "error": {},
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = job_service.UpdateModelDeploymentMonitoringJobRequest.meta.fields[
        "model_deployment_monitoring_job"
    ]

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
    for field, value in request_init[
        "model_deployment_monitoring_job"
    ].items():  # pragma: NO COVER
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
                for i in range(
                    0, len(request_init["model_deployment_monitoring_job"][field])
                ):
                    del request_init["model_deployment_monitoring_job"][field][i][
                        subfield
                    ]
            else:
                del request_init["model_deployment_monitoring_job"][field][subfield]
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
        response = client.update_model_deployment_monitoring_job(request)

    # Establish that the response is the type that we expect.
    assert response.operation.name == "operations/spam"


def test_update_model_deployment_monitoring_job_rest_required_fields(
    request_type=job_service.UpdateModelDeploymentMonitoringJobRequest,
):
    transport_class = transports.JobServiceRestTransport

    request_init = {}
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(pb_request, use_integers_for_enums=False)
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_model_deployment_monitoring_job._get_unset_required_fields(
        jsonified_request
    )
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_model_deployment_monitoring_job._get_unset_required_fields(
        jsonified_request
    )
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("update_mask",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone

    client = JobServiceClient(
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
                "method": "patch",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.update_model_deployment_monitoring_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_update_model_deployment_monitoring_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = (
        transport.update_model_deployment_monitoring_job._get_unset_required_fields({})
    )
    assert set(unset_fields) == (
        set(("updateMask",))
        & set(
            (
                "modelDeploymentMonitoringJob",
                "updateMask",
            )
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_update_model_deployment_monitoring_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.JobServiceRestInterceptor,
        "post_update_model_deployment_monitoring_job",
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor,
        "pre_update_model_deployment_monitoring_job",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.UpdateModelDeploymentMonitoringJobRequest.pb(
            job_service.UpdateModelDeploymentMonitoringJobRequest()
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

        request = job_service.UpdateModelDeploymentMonitoringJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()

        client.update_model_deployment_monitoring_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_update_model_deployment_monitoring_job_rest_bad_request(
    transport: str = "rest",
    request_type=job_service.UpdateModelDeploymentMonitoringJobRequest,
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {
        "model_deployment_monitoring_job": {
            "name": "projects/sample1/locations/sample2/modelDeploymentMonitoringJobs/sample3"
        }
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
        client.update_model_deployment_monitoring_job(request)


def test_update_model_deployment_monitoring_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "model_deployment_monitoring_job": {
                "name": "projects/sample1/locations/sample2/modelDeploymentMonitoringJobs/sample3"
            }
        }

        # get truthy value for each flattened field
        mock_args = dict(
            model_deployment_monitoring_job=gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob(
                name="name_value"
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.update_model_deployment_monitoring_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{model_deployment_monitoring_job.name=projects/*/locations/*/modelDeploymentMonitoringJobs/*}"
            % client.transport._host,
            args[1],
        )


def test_update_model_deployment_monitoring_job_rest_flattened_error(
    transport: str = "rest",
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_model_deployment_monitoring_job(
            job_service.UpdateModelDeploymentMonitoringJobRequest(),
            model_deployment_monitoring_job=gca_model_deployment_monitoring_job.ModelDeploymentMonitoringJob(
                name="name_value"
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


def test_update_model_deployment_monitoring_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.DeleteModelDeploymentMonitoringJobRequest,
        dict,
    ],
)
def test_delete_model_deployment_monitoring_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/modelDeploymentMonitoringJobs/sample3"
    }
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
        response = client.delete_model_deployment_monitoring_job(request)

    # Establish that the response is the type that we expect.
    assert response.operation.name == "operations/spam"


def test_delete_model_deployment_monitoring_job_rest_required_fields(
    request_type=job_service.DeleteModelDeploymentMonitoringJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).delete_model_deployment_monitoring_job._get_unset_required_fields(
        jsonified_request
    )
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).delete_model_deployment_monitoring_job._get_unset_required_fields(
        jsonified_request
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = JobServiceClient(
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

            response = client.delete_model_deployment_monitoring_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_delete_model_deployment_monitoring_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = (
        transport.delete_model_deployment_monitoring_job._get_unset_required_fields({})
    )
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_delete_model_deployment_monitoring_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.JobServiceRestInterceptor,
        "post_delete_model_deployment_monitoring_job",
    ) as post, mock.patch.object(
        transports.JobServiceRestInterceptor,
        "pre_delete_model_deployment_monitoring_job",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = job_service.DeleteModelDeploymentMonitoringJobRequest.pb(
            job_service.DeleteModelDeploymentMonitoringJobRequest()
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

        request = job_service.DeleteModelDeploymentMonitoringJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()

        client.delete_model_deployment_monitoring_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_delete_model_deployment_monitoring_job_rest_bad_request(
    transport: str = "rest",
    request_type=job_service.DeleteModelDeploymentMonitoringJobRequest,
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/modelDeploymentMonitoringJobs/sample3"
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
        client.delete_model_deployment_monitoring_job(request)


def test_delete_model_deployment_monitoring_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/modelDeploymentMonitoringJobs/sample3"
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

        client.delete_model_deployment_monitoring_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*}"
            % client.transport._host,
            args[1],
        )


def test_delete_model_deployment_monitoring_job_rest_flattened_error(
    transport: str = "rest",
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_model_deployment_monitoring_job(
            job_service.DeleteModelDeploymentMonitoringJobRequest(),
            name="name_value",
        )


def test_delete_model_deployment_monitoring_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.PauseModelDeploymentMonitoringJobRequest,
        dict,
    ],
)
def test_pause_model_deployment_monitoring_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/modelDeploymentMonitoringJobs/sample3"
    }
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
        response = client.pause_model_deployment_monitoring_job(request)

    # Establish that the response is the type that we expect.
    assert response is None


def test_pause_model_deployment_monitoring_job_rest_required_fields(
    request_type=job_service.PauseModelDeploymentMonitoringJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).pause_model_deployment_monitoring_job._get_unset_required_fields(
        jsonified_request
    )
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).pause_model_deployment_monitoring_job._get_unset_required_fields(
        jsonified_request
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = JobServiceClient(
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

            response = client.pause_model_deployment_monitoring_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_pause_model_deployment_monitoring_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = (
        transport.pause_model_deployment_monitoring_job._get_unset_required_fields({})
    )
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_pause_model_deployment_monitoring_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor,
        "pre_pause_model_deployment_monitoring_job",
    ) as pre:
        pre.assert_not_called()
        pb_message = job_service.PauseModelDeploymentMonitoringJobRequest.pb(
            job_service.PauseModelDeploymentMonitoringJobRequest()
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

        request = job_service.PauseModelDeploymentMonitoringJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata

        client.pause_model_deployment_monitoring_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()


def test_pause_model_deployment_monitoring_job_rest_bad_request(
    transport: str = "rest",
    request_type=job_service.PauseModelDeploymentMonitoringJobRequest,
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/modelDeploymentMonitoringJobs/sample3"
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
        client.pause_model_deployment_monitoring_job(request)


def test_pause_model_deployment_monitoring_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/modelDeploymentMonitoringJobs/sample3"
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

        client.pause_model_deployment_monitoring_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*}:pause"
            % client.transport._host,
            args[1],
        )


def test_pause_model_deployment_monitoring_job_rest_flattened_error(
    transport: str = "rest",
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.pause_model_deployment_monitoring_job(
            job_service.PauseModelDeploymentMonitoringJobRequest(),
            name="name_value",
        )


def test_pause_model_deployment_monitoring_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        job_service.ResumeModelDeploymentMonitoringJobRequest,
        dict,
    ],
)
def test_resume_model_deployment_monitoring_job_rest(request_type):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/modelDeploymentMonitoringJobs/sample3"
    }
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
        response = client.resume_model_deployment_monitoring_job(request)

    # Establish that the response is the type that we expect.
    assert response is None


def test_resume_model_deployment_monitoring_job_rest_required_fields(
    request_type=job_service.ResumeModelDeploymentMonitoringJobRequest,
):
    transport_class = transports.JobServiceRestTransport

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
    ).resume_model_deployment_monitoring_job._get_unset_required_fields(
        jsonified_request
    )
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).resume_model_deployment_monitoring_job._get_unset_required_fields(
        jsonified_request
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = JobServiceClient(
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

            response = client.resume_model_deployment_monitoring_job(request)

            expected_params = []
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_resume_model_deployment_monitoring_job_rest_unset_required_fields():
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = (
        transport.resume_model_deployment_monitoring_job._get_unset_required_fields({})
    )
    assert set(unset_fields) == (set(()) & set(("name",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_resume_model_deployment_monitoring_job_rest_interceptors(null_interceptor):
    transport = transports.JobServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None
        if null_interceptor
        else transports.JobServiceRestInterceptor(),
    )
    client = JobServiceClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.JobServiceRestInterceptor,
        "pre_resume_model_deployment_monitoring_job",
    ) as pre:
        pre.assert_not_called()
        pb_message = job_service.ResumeModelDeploymentMonitoringJobRequest.pb(
            job_service.ResumeModelDeploymentMonitoringJobRequest()
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

        request = job_service.ResumeModelDeploymentMonitoringJobRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata

        client.resume_model_deployment_monitoring_job(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()


def test_resume_model_deployment_monitoring_job_rest_bad_request(
    transport: str = "rest",
    request_type=job_service.ResumeModelDeploymentMonitoringJobRequest,
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/modelDeploymentMonitoringJobs/sample3"
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
        client.resume_model_deployment_monitoring_job(request)


def test_resume_model_deployment_monitoring_job_rest_flattened():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/modelDeploymentMonitoringJobs/sample3"
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

        client.resume_model_deployment_monitoring_job(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*}:resume"
            % client.transport._host,
            args[1],
        )


def test_resume_model_deployment_monitoring_job_rest_flattened_error(
    transport: str = "rest",
):
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.resume_model_deployment_monitoring_job(
            job_service.ResumeModelDeploymentMonitoringJobRequest(),
            name="name_value",
        )


def test_resume_model_deployment_monitoring_job_rest_error():
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.JobServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = JobServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.JobServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = JobServiceClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide an api_key and a transport instance.
    transport = transports.JobServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    options = client_options.ClientOptions()
    options.api_key = "api_key"
    with pytest.raises(ValueError):
        client = JobServiceClient(
            client_options=options,
            transport=transport,
        )

    # It is an error to provide an api_key and a credential.
    options = client_options.ClientOptions()
    options.api_key = "api_key"
    with pytest.raises(ValueError):
        client = JobServiceClient(
            client_options=options, credentials=ga_credentials.AnonymousCredentials()
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.JobServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = JobServiceClient(
            client_options={"scopes": ["1", "2"]},
            transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.JobServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    client = JobServiceClient(transport=transport)
    assert client.transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.JobServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.JobServiceGrpcAsyncIOTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.JobServiceGrpcTransport,
        transports.JobServiceGrpcAsyncIOTransport,
        transports.JobServiceRestTransport,
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
    transport = JobServiceClient.get_transport_class(transport_name)(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    assert transport.kind == transport_name


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = JobServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    assert isinstance(
        client.transport,
        transports.JobServiceGrpcTransport,
    )


def test_job_service_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(core_exceptions.DuplicateCredentialArgs):
        transport = transports.JobServiceTransport(
            credentials=ga_credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_job_service_base_transport():
    # Instantiate the base transport.
    with mock.patch(
        "google.cloud.aiplatform_v1.services.job_service.transports.JobServiceTransport.__init__"
    ) as Transport:
        Transport.return_value = None
        transport = transports.JobServiceTransport(
            credentials=ga_credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "create_custom_job",
        "get_custom_job",
        "list_custom_jobs",
        "delete_custom_job",
        "cancel_custom_job",
        "create_data_labeling_job",
        "get_data_labeling_job",
        "list_data_labeling_jobs",
        "delete_data_labeling_job",
        "cancel_data_labeling_job",
        "create_hyperparameter_tuning_job",
        "get_hyperparameter_tuning_job",
        "list_hyperparameter_tuning_jobs",
        "delete_hyperparameter_tuning_job",
        "cancel_hyperparameter_tuning_job",
        "create_nas_job",
        "get_nas_job",
        "list_nas_jobs",
        "delete_nas_job",
        "cancel_nas_job",
        "get_nas_trial_detail",
        "list_nas_trial_details",
        "create_batch_prediction_job",
        "get_batch_prediction_job",
        "list_batch_prediction_jobs",
        "delete_batch_prediction_job",
        "cancel_batch_prediction_job",
        "create_model_deployment_monitoring_job",
        "search_model_deployment_monitoring_stats_anomalies",
        "get_model_deployment_monitoring_job",
        "list_model_deployment_monitoring_jobs",
        "update_model_deployment_monitoring_job",
        "delete_model_deployment_monitoring_job",
        "pause_model_deployment_monitoring_job",
        "resume_model_deployment_monitoring_job",
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


def test_job_service_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        google.auth, "load_credentials_from_file", autospec=True
    ) as load_creds, mock.patch(
        "google.cloud.aiplatform_v1.services.job_service.transports.JobServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.JobServiceTransport(
            credentials_file="credentials.json",
            quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=None,
            default_scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/cloud-platform.read-only",
            ),
            quota_project_id="octopus",
        )


def test_job_service_base_transport_with_adc():
    # Test the default credentials are used if credentials and credentials_file are None.
    with mock.patch.object(google.auth, "default", autospec=True) as adc, mock.patch(
        "google.cloud.aiplatform_v1.services.job_service.transports.JobServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.JobServiceTransport()
        adc.assert_called_once()


def test_job_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        JobServiceClient()
        adc.assert_called_once_with(
            scopes=None,
            default_scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/cloud-platform.read-only",
            ),
            quota_project_id=None,
        )


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.JobServiceGrpcTransport,
        transports.JobServiceGrpcAsyncIOTransport,
    ],
)
def test_job_service_transport_auth_adc(transport_class):
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport_class(quota_project_id="octopus", scopes=["1", "2"])
        adc.assert_called_once_with(
            scopes=["1", "2"],
            default_scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/cloud-platform.read-only",
            ),
            quota_project_id="octopus",
        )


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.JobServiceGrpcTransport,
        transports.JobServiceGrpcAsyncIOTransport,
        transports.JobServiceRestTransport,
    ],
)
def test_job_service_transport_auth_gdch_credentials(transport_class):
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
        (transports.JobServiceGrpcTransport, grpc_helpers),
        (transports.JobServiceGrpcAsyncIOTransport, grpc_helpers_async),
    ],
)
def test_job_service_transport_create_channel(transport_class, grpc_helpers):
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
            default_scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/cloud-platform.read-only",
            ),
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
    [transports.JobServiceGrpcTransport, transports.JobServiceGrpcAsyncIOTransport],
)
def test_job_service_grpc_transport_client_cert_source_for_mtls(transport_class):
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


def test_job_service_http_transport_client_cert_source_for_mtls():
    cred = ga_credentials.AnonymousCredentials()
    with mock.patch(
        "google.auth.transport.requests.AuthorizedSession.configure_mtls_channel"
    ) as mock_configure_mtls_channel:
        transports.JobServiceRestTransport(
            credentials=cred, client_cert_source_for_mtls=client_cert_source_callback
        )
        mock_configure_mtls_channel.assert_called_once_with(client_cert_source_callback)


def test_job_service_rest_lro_client():
    client = JobServiceClient(
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
def test_job_service_host_no_port(transport_name):
    client = JobServiceClient(
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
def test_job_service_host_with_port(transport_name):
    client = JobServiceClient(
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
def test_job_service_client_transport_session_collision(transport_name):
    creds1 = ga_credentials.AnonymousCredentials()
    creds2 = ga_credentials.AnonymousCredentials()
    client1 = JobServiceClient(
        credentials=creds1,
        transport=transport_name,
    )
    client2 = JobServiceClient(
        credentials=creds2,
        transport=transport_name,
    )
    session1 = client1.transport.create_custom_job._session
    session2 = client2.transport.create_custom_job._session
    assert session1 != session2
    session1 = client1.transport.get_custom_job._session
    session2 = client2.transport.get_custom_job._session
    assert session1 != session2
    session1 = client1.transport.list_custom_jobs._session
    session2 = client2.transport.list_custom_jobs._session
    assert session1 != session2
    session1 = client1.transport.delete_custom_job._session
    session2 = client2.transport.delete_custom_job._session
    assert session1 != session2
    session1 = client1.transport.cancel_custom_job._session
    session2 = client2.transport.cancel_custom_job._session
    assert session1 != session2
    session1 = client1.transport.create_data_labeling_job._session
    session2 = client2.transport.create_data_labeling_job._session
    assert session1 != session2
    session1 = client1.transport.get_data_labeling_job._session
    session2 = client2.transport.get_data_labeling_job._session
    assert session1 != session2
    session1 = client1.transport.list_data_labeling_jobs._session
    session2 = client2.transport.list_data_labeling_jobs._session
    assert session1 != session2
    session1 = client1.transport.delete_data_labeling_job._session
    session2 = client2.transport.delete_data_labeling_job._session
    assert session1 != session2
    session1 = client1.transport.cancel_data_labeling_job._session
    session2 = client2.transport.cancel_data_labeling_job._session
    assert session1 != session2
    session1 = client1.transport.create_hyperparameter_tuning_job._session
    session2 = client2.transport.create_hyperparameter_tuning_job._session
    assert session1 != session2
    session1 = client1.transport.get_hyperparameter_tuning_job._session
    session2 = client2.transport.get_hyperparameter_tuning_job._session
    assert session1 != session2
    session1 = client1.transport.list_hyperparameter_tuning_jobs._session
    session2 = client2.transport.list_hyperparameter_tuning_jobs._session
    assert session1 != session2
    session1 = client1.transport.delete_hyperparameter_tuning_job._session
    session2 = client2.transport.delete_hyperparameter_tuning_job._session
    assert session1 != session2
    session1 = client1.transport.cancel_hyperparameter_tuning_job._session
    session2 = client2.transport.cancel_hyperparameter_tuning_job._session
    assert session1 != session2
    session1 = client1.transport.create_nas_job._session
    session2 = client2.transport.create_nas_job._session
    assert session1 != session2
    session1 = client1.transport.get_nas_job._session
    session2 = client2.transport.get_nas_job._session
    assert session1 != session2
    session1 = client1.transport.list_nas_jobs._session
    session2 = client2.transport.list_nas_jobs._session
    assert session1 != session2
    session1 = client1.transport.delete_nas_job._session
    session2 = client2.transport.delete_nas_job._session
    assert session1 != session2
    session1 = client1.transport.cancel_nas_job._session
    session2 = client2.transport.cancel_nas_job._session
    assert session1 != session2
    session1 = client1.transport.get_nas_trial_detail._session
    session2 = client2.transport.get_nas_trial_detail._session
    assert session1 != session2
    session1 = client1.transport.list_nas_trial_details._session
    session2 = client2.transport.list_nas_trial_details._session
    assert session1 != session2
    session1 = client1.transport.create_batch_prediction_job._session
    session2 = client2.transport.create_batch_prediction_job._session
    assert session1 != session2
    session1 = client1.transport.get_batch_prediction_job._session
    session2 = client2.transport.get_batch_prediction_job._session
    assert session1 != session2
    session1 = client1.transport.list_batch_prediction_jobs._session
    session2 = client2.transport.list_batch_prediction_jobs._session
    assert session1 != session2
    session1 = client1.transport.delete_batch_prediction_job._session
    session2 = client2.transport.delete_batch_prediction_job._session
    assert session1 != session2
    session1 = client1.transport.cancel_batch_prediction_job._session
    session2 = client2.transport.cancel_batch_prediction_job._session
    assert session1 != session2
    session1 = client1.transport.create_model_deployment_monitoring_job._session
    session2 = client2.transport.create_model_deployment_monitoring_job._session
    assert session1 != session2
    session1 = (
        client1.transport.search_model_deployment_monitoring_stats_anomalies._session
    )
    session2 = (
        client2.transport.search_model_deployment_monitoring_stats_anomalies._session
    )
    assert session1 != session2
    session1 = client1.transport.get_model_deployment_monitoring_job._session
    session2 = client2.transport.get_model_deployment_monitoring_job._session
    assert session1 != session2
    session1 = client1.transport.list_model_deployment_monitoring_jobs._session
    session2 = client2.transport.list_model_deployment_monitoring_jobs._session
    assert session1 != session2
    session1 = client1.transport.update_model_deployment_monitoring_job._session
    session2 = client2.transport.update_model_deployment_monitoring_job._session
    assert session1 != session2
    session1 = client1.transport.delete_model_deployment_monitoring_job._session
    session2 = client2.transport.delete_model_deployment_monitoring_job._session
    assert session1 != session2
    session1 = client1.transport.pause_model_deployment_monitoring_job._session
    session2 = client2.transport.pause_model_deployment_monitoring_job._session
    assert session1 != session2
    session1 = client1.transport.resume_model_deployment_monitoring_job._session
    session2 = client2.transport.resume_model_deployment_monitoring_job._session
    assert session1 != session2


def test_job_service_grpc_transport_channel():
    channel = grpc.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.JobServiceGrpcTransport(
        host="squid.clam.whelk",
        channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


def test_job_service_grpc_asyncio_transport_channel():
    channel = aio.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.JobServiceGrpcAsyncIOTransport(
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
    [transports.JobServiceGrpcTransport, transports.JobServiceGrpcAsyncIOTransport],
)
def test_job_service_transport_channel_mtls_with_client_cert_source(transport_class):
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
    [transports.JobServiceGrpcTransport, transports.JobServiceGrpcAsyncIOTransport],
)
def test_job_service_transport_channel_mtls_with_adc(transport_class):
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


def test_job_service_grpc_lro_client():
    client = JobServiceClient(
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


def test_job_service_grpc_lro_async_client():
    client = JobServiceAsyncClient(
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


def test_batch_prediction_job_path():
    project = "squid"
    location = "clam"
    batch_prediction_job = "whelk"
    expected = "projects/{project}/locations/{location}/batchPredictionJobs/{batch_prediction_job}".format(
        project=project,
        location=location,
        batch_prediction_job=batch_prediction_job,
    )
    actual = JobServiceClient.batch_prediction_job_path(
        project, location, batch_prediction_job
    )
    assert expected == actual


def test_parse_batch_prediction_job_path():
    expected = {
        "project": "octopus",
        "location": "oyster",
        "batch_prediction_job": "nudibranch",
    }
    path = JobServiceClient.batch_prediction_job_path(**expected)

    # Check that the path construction is reversible.
    actual = JobServiceClient.parse_batch_prediction_job_path(path)
    assert expected == actual


def test_context_path():
    project = "cuttlefish"
    location = "mussel"
    metadata_store = "winkle"
    context = "nautilus"
    expected = "projects/{project}/locations/{location}/metadataStores/{metadata_store}/contexts/{context}".format(
        project=project,
        location=location,
        metadata_store=metadata_store,
        context=context,
    )
    actual = JobServiceClient.context_path(project, location, metadata_store, context)
    assert expected == actual


def test_parse_context_path():
    expected = {
        "project": "scallop",
        "location": "abalone",
        "metadata_store": "squid",
        "context": "clam",
    }
    path = JobServiceClient.context_path(**expected)

    # Check that the path construction is reversible.
    actual = JobServiceClient.parse_context_path(path)
    assert expected == actual


def test_custom_job_path():
    project = "whelk"
    location = "octopus"
    custom_job = "oyster"
    expected = "projects/{project}/locations/{location}/customJobs/{custom_job}".format(
        project=project,
        location=location,
        custom_job=custom_job,
    )
    actual = JobServiceClient.custom_job_path(project, location, custom_job)
    assert expected == actual


def test_parse_custom_job_path():
    expected = {
        "project": "nudibranch",
        "location": "cuttlefish",
        "custom_job": "mussel",
    }
    path = JobServiceClient.custom_job_path(**expected)

    # Check that the path construction is reversible.
    actual = JobServiceClient.parse_custom_job_path(path)
    assert expected == actual


def test_data_labeling_job_path():
    project = "winkle"
    location = "nautilus"
    data_labeling_job = "scallop"
    expected = "projects/{project}/locations/{location}/dataLabelingJobs/{data_labeling_job}".format(
        project=project,
        location=location,
        data_labeling_job=data_labeling_job,
    )
    actual = JobServiceClient.data_labeling_job_path(
        project, location, data_labeling_job
    )
    assert expected == actual


def test_parse_data_labeling_job_path():
    expected = {
        "project": "abalone",
        "location": "squid",
        "data_labeling_job": "clam",
    }
    path = JobServiceClient.data_labeling_job_path(**expected)

    # Check that the path construction is reversible.
    actual = JobServiceClient.parse_data_labeling_job_path(path)
    assert expected == actual


def test_dataset_path():
    project = "whelk"
    location = "octopus"
    dataset = "oyster"
    expected = "projects/{project}/locations/{location}/datasets/{dataset}".format(
        project=project,
        location=location,
        dataset=dataset,
    )
    actual = JobServiceClient.dataset_path(project, location, dataset)
    assert expected == actual


def test_parse_dataset_path():
    expected = {
        "project": "nudibranch",
        "location": "cuttlefish",
        "dataset": "mussel",
    }
    path = JobServiceClient.dataset_path(**expected)

    # Check that the path construction is reversible.
    actual = JobServiceClient.parse_dataset_path(path)
    assert expected == actual


def test_endpoint_path():
    project = "winkle"
    location = "nautilus"
    endpoint = "scallop"
    expected = "projects/{project}/locations/{location}/endpoints/{endpoint}".format(
        project=project,
        location=location,
        endpoint=endpoint,
    )
    actual = JobServiceClient.endpoint_path(project, location, endpoint)
    assert expected == actual


def test_parse_endpoint_path():
    expected = {
        "project": "abalone",
        "location": "squid",
        "endpoint": "clam",
    }
    path = JobServiceClient.endpoint_path(**expected)

    # Check that the path construction is reversible.
    actual = JobServiceClient.parse_endpoint_path(path)
    assert expected == actual


def test_hyperparameter_tuning_job_path():
    project = "whelk"
    location = "octopus"
    hyperparameter_tuning_job = "oyster"
    expected = "projects/{project}/locations/{location}/hyperparameterTuningJobs/{hyperparameter_tuning_job}".format(
        project=project,
        location=location,
        hyperparameter_tuning_job=hyperparameter_tuning_job,
    )
    actual = JobServiceClient.hyperparameter_tuning_job_path(
        project, location, hyperparameter_tuning_job
    )
    assert expected == actual


def test_parse_hyperparameter_tuning_job_path():
    expected = {
        "project": "nudibranch",
        "location": "cuttlefish",
        "hyperparameter_tuning_job": "mussel",
    }
    path = JobServiceClient.hyperparameter_tuning_job_path(**expected)

    # Check that the path construction is reversible.
    actual = JobServiceClient.parse_hyperparameter_tuning_job_path(path)
    assert expected == actual


def test_model_path():
    project = "winkle"
    location = "nautilus"
    model = "scallop"
    expected = "projects/{project}/locations/{location}/models/{model}".format(
        project=project,
        location=location,
        model=model,
    )
    actual = JobServiceClient.model_path(project, location, model)
    assert expected == actual


def test_parse_model_path():
    expected = {
        "project": "abalone",
        "location": "squid",
        "model": "clam",
    }
    path = JobServiceClient.model_path(**expected)

    # Check that the path construction is reversible.
    actual = JobServiceClient.parse_model_path(path)
    assert expected == actual


def test_model_deployment_monitoring_job_path():
    project = "whelk"
    location = "octopus"
    model_deployment_monitoring_job = "oyster"
    expected = "projects/{project}/locations/{location}/modelDeploymentMonitoringJobs/{model_deployment_monitoring_job}".format(
        project=project,
        location=location,
        model_deployment_monitoring_job=model_deployment_monitoring_job,
    )
    actual = JobServiceClient.model_deployment_monitoring_job_path(
        project, location, model_deployment_monitoring_job
    )
    assert expected == actual


def test_parse_model_deployment_monitoring_job_path():
    expected = {
        "project": "nudibranch",
        "location": "cuttlefish",
        "model_deployment_monitoring_job": "mussel",
    }
    path = JobServiceClient.model_deployment_monitoring_job_path(**expected)

    # Check that the path construction is reversible.
    actual = JobServiceClient.parse_model_deployment_monitoring_job_path(path)
    assert expected == actual


def test_nas_job_path():
    project = "winkle"
    location = "nautilus"
    nas_job = "scallop"
    expected = "projects/{project}/locations/{location}/nasJobs/{nas_job}".format(
        project=project,
        location=location,
        nas_job=nas_job,
    )
    actual = JobServiceClient.nas_job_path(project, location, nas_job)
    assert expected == actual


def test_parse_nas_job_path():
    expected = {
        "project": "abalone",
        "location": "squid",
        "nas_job": "clam",
    }
    path = JobServiceClient.nas_job_path(**expected)

    # Check that the path construction is reversible.
    actual = JobServiceClient.parse_nas_job_path(path)
    assert expected == actual


def test_nas_trial_detail_path():
    project = "whelk"
    location = "octopus"
    nas_job = "oyster"
    nas_trial_detail = "nudibranch"
    expected = "projects/{project}/locations/{location}/nasJobs/{nas_job}/nasTrialDetails/{nas_trial_detail}".format(
        project=project,
        location=location,
        nas_job=nas_job,
        nas_trial_detail=nas_trial_detail,
    )
    actual = JobServiceClient.nas_trial_detail_path(
        project, location, nas_job, nas_trial_detail
    )
    assert expected == actual


def test_parse_nas_trial_detail_path():
    expected = {
        "project": "cuttlefish",
        "location": "mussel",
        "nas_job": "winkle",
        "nas_trial_detail": "nautilus",
    }
    path = JobServiceClient.nas_trial_detail_path(**expected)

    # Check that the path construction is reversible.
    actual = JobServiceClient.parse_nas_trial_detail_path(path)
    assert expected == actual


def test_network_path():
    project = "scallop"
    network = "abalone"
    expected = "projects/{project}/global/networks/{network}".format(
        project=project,
        network=network,
    )
    actual = JobServiceClient.network_path(project, network)
    assert expected == actual


def test_parse_network_path():
    expected = {
        "project": "squid",
        "network": "clam",
    }
    path = JobServiceClient.network_path(**expected)

    # Check that the path construction is reversible.
    actual = JobServiceClient.parse_network_path(path)
    assert expected == actual


def test_notification_channel_path():
    project = "whelk"
    notification_channel = "octopus"
    expected = "projects/{project}/notificationChannels/{notification_channel}".format(
        project=project,
        notification_channel=notification_channel,
    )
    actual = JobServiceClient.notification_channel_path(project, notification_channel)
    assert expected == actual


def test_parse_notification_channel_path():
    expected = {
        "project": "oyster",
        "notification_channel": "nudibranch",
    }
    path = JobServiceClient.notification_channel_path(**expected)

    # Check that the path construction is reversible.
    actual = JobServiceClient.parse_notification_channel_path(path)
    assert expected == actual


def test_tensorboard_path():
    project = "cuttlefish"
    location = "mussel"
    tensorboard = "winkle"
    expected = (
        "projects/{project}/locations/{location}/tensorboards/{tensorboard}".format(
            project=project,
            location=location,
            tensorboard=tensorboard,
        )
    )
    actual = JobServiceClient.tensorboard_path(project, location, tensorboard)
    assert expected == actual


def test_parse_tensorboard_path():
    expected = {
        "project": "nautilus",
        "location": "scallop",
        "tensorboard": "abalone",
    }
    path = JobServiceClient.tensorboard_path(**expected)

    # Check that the path construction is reversible.
    actual = JobServiceClient.parse_tensorboard_path(path)
    assert expected == actual


def test_trial_path():
    project = "squid"
    location = "clam"
    study = "whelk"
    trial = "octopus"
    expected = (
        "projects/{project}/locations/{location}/studies/{study}/trials/{trial}".format(
            project=project,
            location=location,
            study=study,
            trial=trial,
        )
    )
    actual = JobServiceClient.trial_path(project, location, study, trial)
    assert expected == actual


def test_parse_trial_path():
    expected = {
        "project": "oyster",
        "location": "nudibranch",
        "study": "cuttlefish",
        "trial": "mussel",
    }
    path = JobServiceClient.trial_path(**expected)

    # Check that the path construction is reversible.
    actual = JobServiceClient.parse_trial_path(path)
    assert expected == actual


def test_common_billing_account_path():
    billing_account = "winkle"
    expected = "billingAccounts/{billing_account}".format(
        billing_account=billing_account,
    )
    actual = JobServiceClient.common_billing_account_path(billing_account)
    assert expected == actual


def test_parse_common_billing_account_path():
    expected = {
        "billing_account": "nautilus",
    }
    path = JobServiceClient.common_billing_account_path(**expected)

    # Check that the path construction is reversible.
    actual = JobServiceClient.parse_common_billing_account_path(path)
    assert expected == actual


def test_common_folder_path():
    folder = "scallop"
    expected = "folders/{folder}".format(
        folder=folder,
    )
    actual = JobServiceClient.common_folder_path(folder)
    assert expected == actual


def test_parse_common_folder_path():
    expected = {
        "folder": "abalone",
    }
    path = JobServiceClient.common_folder_path(**expected)

    # Check that the path construction is reversible.
    actual = JobServiceClient.parse_common_folder_path(path)
    assert expected == actual


def test_common_organization_path():
    organization = "squid"
    expected = "organizations/{organization}".format(
        organization=organization,
    )
    actual = JobServiceClient.common_organization_path(organization)
    assert expected == actual


def test_parse_common_organization_path():
    expected = {
        "organization": "clam",
    }
    path = JobServiceClient.common_organization_path(**expected)

    # Check that the path construction is reversible.
    actual = JobServiceClient.parse_common_organization_path(path)
    assert expected == actual


def test_common_project_path():
    project = "whelk"
    expected = "projects/{project}".format(
        project=project,
    )
    actual = JobServiceClient.common_project_path(project)
    assert expected == actual


def test_parse_common_project_path():
    expected = {
        "project": "octopus",
    }
    path = JobServiceClient.common_project_path(**expected)

    # Check that the path construction is reversible.
    actual = JobServiceClient.parse_common_project_path(path)
    assert expected == actual


def test_common_location_path():
    project = "oyster"
    location = "nudibranch"
    expected = "projects/{project}/locations/{location}".format(
        project=project,
        location=location,
    )
    actual = JobServiceClient.common_location_path(project, location)
    assert expected == actual


def test_parse_common_location_path():
    expected = {
        "project": "cuttlefish",
        "location": "mussel",
    }
    path = JobServiceClient.common_location_path(**expected)

    # Check that the path construction is reversible.
    actual = JobServiceClient.parse_common_location_path(path)
    assert expected == actual


def test_client_with_default_client_info():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(
        transports.JobServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        client = JobServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(
        transports.JobServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        transport_class = JobServiceClient.get_transport_class()
        transport = transport_class(
            credentials=ga_credentials.AnonymousCredentials(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)


@pytest.mark.asyncio
async def test_transport_close_async():
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceClient(
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
    client = JobServiceClient(
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
    client = JobServiceClient(
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
    client = JobServiceClient(
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
    client = JobServiceClient(
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
    client = JobServiceClient(
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
    client = JobServiceClient(
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
    client = JobServiceClient(
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
    client = JobServiceClient(
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
    client = JobServiceClient(
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
    client = JobServiceClient(
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
    client = JobServiceClient(
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
    client = JobServiceClient(
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
    client = JobServiceClient(
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
    client = JobServiceClient(
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
    client = JobServiceClient(
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
    client = JobServiceClient(
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
    client = JobServiceClient(
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
    client = JobServiceClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(credentials=ga_credentials.AnonymousCredentials())

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
    client = JobServiceAsyncClient(credentials=ga_credentials.AnonymousCredentials())

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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
    client = JobServiceClient(
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
    client = JobServiceAsyncClient(
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
        client = JobServiceClient(
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
        client = JobServiceClient(
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
        (JobServiceClient, transports.JobServiceGrpcTransport),
        (JobServiceAsyncClient, transports.JobServiceGrpcAsyncIOTransport),
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
