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


@pytest.mark.parametrize(
    "client_class,transport_name",
    [
        (JobServiceClient, "grpc"),
        (JobServiceAsyncClient, "grpc_asyncio"),
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

        assert client.transport._host == ("aiplatform.googleapis.com:443")


@pytest.mark.parametrize(
    "transport_class,transport_name",
    [
        (transports.JobServiceGrpcTransport, "grpc"),
        (transports.JobServiceGrpcAsyncIOTransport, "grpc_asyncio"),
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

        assert client.transport._host == ("aiplatform.googleapis.com:443")


def test_job_service_client_get_transport_class():
    transport = JobServiceClient.get_transport_class()
    available_transports = [
        transports.JobServiceGrpcTransport,
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
    ],
)
@mock.patch.object(
    JobServiceClient, "DEFAULT_ENDPOINT", modify_default_endpoint(JobServiceClient)
)
@mock.patch.object(
    JobServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(JobServiceAsyncClient),
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
    ],
)
@mock.patch.object(
    JobServiceClient, "DEFAULT_ENDPOINT", modify_default_endpoint(JobServiceClient)
)
@mock.patch.object(
    JobServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(JobServiceAsyncClient),
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


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (JobServiceClient, transports.JobServiceGrpcTransport, "grpc"),
        (
            JobServiceAsyncClient,
            transports.JobServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
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
        (JobServiceClient, transports.JobServiceGrpcTransport, "grpc", grpc_helpers),
        (
            JobServiceAsyncClient,
            transports.JobServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            grpc_helpers_async,
        ),
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
            host=client.DEFAULT_ENDPOINT,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
        credentials=ga_credentials.AnonymousCredentials,
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
    options = mock.Mock()
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


@pytest.mark.parametrize(
    "transport_name",
    [
        "grpc",
        "grpc_asyncio",
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
    assert client.transport._host == ("aiplatform.googleapis.com:443")


@pytest.mark.parametrize(
    "transport_name",
    [
        "grpc",
        "grpc_asyncio",
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
    assert client.transport._host == ("aiplatform.googleapis.com:8000")


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
async def test_delete_operation_async(transport: str = "grpc"):
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
async def test_cancel_operation_async(transport: str = "grpc"):
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
async def test_wait_operation(transport: str = "grpc"):
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
async def test_get_operation_async(transport: str = "grpc"):
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
async def test_list_operations_async(transport: str = "grpc"):
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
async def test_list_locations_async(transport: str = "grpc"):
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
                host=client.DEFAULT_ENDPOINT,
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
                always_use_jwt_access=True,
                api_audience=None,
            )
