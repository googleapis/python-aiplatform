# -*- coding: utf-8 -*-
# Copyright 2026 Google LLC
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
import asyncio
from unittest import mock
from unittest.mock import AsyncMock

import grpc
from grpc.experimental import aio
from collections.abc import Iterable, AsyncIterable
from google.protobuf import json_format
import json
import math
import pytest
from collections.abc import Sequence, Mapping
from google.api_core import api_core_version
from proto.marshal.rules.dates import DurationRule, TimestampRule
from proto.marshal.rules import wrappers
try:
    import aiohttp  # type: ignore
    from google.auth.aio.transport.sessions import AsyncAuthorizedSession
    from google.api_core.operations_v1 import AsyncOperationsRestClient
    HAS_ASYNC_REST_EXTRA = True
except ImportError: # pragma: NO COVER
    HAS_ASYNC_REST_EXTRA = False
from requests import Response
from requests import Request, PreparedRequest
from requests.sessions import Session
from google.protobuf import json_format

try:
    from google.auth.aio import credentials as ga_credentials_async
    HAS_GOOGLE_AUTH_AIO = True
except ImportError: # pragma: NO COVER
    HAS_GOOGLE_AUTH_AIO = False

from google.api_core import client_options
from google.api_core import exceptions as core_exceptions
from google.api_core import future
from google.api_core import gapic_v1
from google.api_core import grpc_helpers
from google.api_core import grpc_helpers_async
from google.api_core import operation
from google.api_core import operations_v1
from google.api_core import path_template
from google.api_core import retry as retries
from google.auth import credentials as ga_credentials
from google.auth.exceptions import MutualTLSChannelError
from google.cloud.aiplatform_v1.services.agent_anomaly_detection_service import AgentAnomalyDetectionServiceAsyncClient
from google.cloud.aiplatform_v1.services.agent_anomaly_detection_service import AgentAnomalyDetectionServiceClient
from google.cloud.aiplatform_v1.services.agent_anomaly_detection_service import pagers
from google.cloud.aiplatform_v1.services.agent_anomaly_detection_service import transports
from google.cloud.aiplatform_v1.types import agent_anomaly_detection_service
from google.cloud.aiplatform_v1.types import encryption_spec
from google.cloud.location import locations_pb2
from google.iam.v1 import iam_policy_pb2  # type: ignore
from google.iam.v1 import options_pb2  # type: ignore
from google.iam.v1 import policy_pb2  # type: ignore
from google.longrunning import operations_pb2 # type: ignore
from google.oauth2 import service_account
import google.api_core.operation_async as operation_async  # type: ignore
import google.auth
import google.protobuf.empty_pb2 as empty_pb2  # type: ignore
import google.protobuf.timestamp_pb2 as timestamp_pb2  # type: ignore



CRED_INFO_JSON = {
    "credential_source": "/path/to/file",
    "credential_type": "service account credentials",
    "principal": "service-account@example.com",
}
CRED_INFO_STRING = json.dumps(CRED_INFO_JSON)


@pytest.fixture(autouse=True)
def disable_mtls_env():
    with mock.patch.dict(
        os.environ,
        {
            "GOOGLE_API_USE_CLIENT_CERTIFICATE": "false",
            "CLOUDSDK_CONTEXT_AWARE_USE_CLIENT_CERTIFICATE": "false",
        },
    ):
        yield


async def mock_async_gen(data, chunk_size=1):
    for i in range(0, len(data)):  # pragma: NO COVER
        chunk = data[i : i + chunk_size]
        yield chunk.encode("utf-8")

def client_cert_source_callback():
    return b"cert bytes", b"key bytes"

# TODO: use async auth anon credentials by default once the minimum version of google-auth is upgraded.
# See related issue: https://github.com/googleapis/gapic-generator-python/issues/2107.
def async_anonymous_credentials():
    if HAS_GOOGLE_AUTH_AIO:
        return ga_credentials_async.AnonymousCredentials()
    return ga_credentials.AnonymousCredentials()

# If default endpoint is localhost, then default mtls endpoint will be the same.
# This method modifies the default endpoint so the client can produce a different
# mtls endpoint for endpoint testing purposes.
def modify_default_endpoint(client):
    return "foo.googleapis.com" if ("localhost" in client.DEFAULT_ENDPOINT) else client.DEFAULT_ENDPOINT

# If default endpoint template is localhost, then default mtls endpoint will be the same.
# This method modifies the default endpoint template so the client can produce a different
# mtls endpoint for endpoint testing purposes.
def modify_default_endpoint_template(client):
    return "test.{UNIVERSE_DOMAIN}" if ("localhost" in client._DEFAULT_ENDPOINT_TEMPLATE) else client._DEFAULT_ENDPOINT_TEMPLATE


@pytest.fixture(autouse=True)
def set_event_loop():
    try:
        asyncio.get_running_loop()
        yield
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            yield
        finally:
            loop.close()
            asyncio.set_event_loop(None)


def test__get_client_cert_source():
    mock_provided_cert_source = mock.Mock()
    mock_default_cert_source = mock.Mock()

    assert AgentAnomalyDetectionServiceClient._get_client_cert_source(None, False) is None
    assert AgentAnomalyDetectionServiceClient._get_client_cert_source(mock_provided_cert_source, False) is None
    assert AgentAnomalyDetectionServiceClient._get_client_cert_source(mock_provided_cert_source, True) == mock_provided_cert_source

    with mock.patch('google.auth.transport.mtls.has_default_client_cert_source', return_value=True):
        with mock.patch('google.auth.transport.mtls.default_client_cert_source', return_value=mock_default_cert_source):
            assert AgentAnomalyDetectionServiceClient._get_client_cert_source(None, True) is mock_default_cert_source
            assert AgentAnomalyDetectionServiceClient._get_client_cert_source(mock_provided_cert_source, "true") is mock_provided_cert_source


@pytest.mark.parametrize("error_code,cred_info_json,show_cred_info", [
    (401, CRED_INFO_JSON, True),
    (403, CRED_INFO_JSON, True),
    (404, CRED_INFO_JSON, True),
    (500, CRED_INFO_JSON, False),
    (401, None, False),
    (403, None, False),
    (404, None, False),
    (500, None, False)
])
def test__add_cred_info_for_auth_errors(error_code, cred_info_json, show_cred_info):
    cred = mock.Mock(["get_cred_info"])
    cred.get_cred_info = mock.Mock(return_value=cred_info_json)
    client = AgentAnomalyDetectionServiceClient(credentials=cred)
    client._transport._credentials = cred

    error = core_exceptions.GoogleAPICallError("message", details=["foo"])
    error.code = error_code

    client._add_cred_info_for_auth_errors(error)
    if show_cred_info:
        assert error.details == ["foo", CRED_INFO_STRING]
    else:
        assert error.details == ["foo"]

@pytest.mark.parametrize("error_code", [401,403,404,500])
def test__add_cred_info_for_auth_errors_no_get_cred_info(error_code):
    cred = mock.Mock([])
    assert not hasattr(cred, "get_cred_info")
    client = AgentAnomalyDetectionServiceClient(credentials=cred)
    client._transport._credentials = cred

    error = core_exceptions.GoogleAPICallError("message", details=[])
    error.code = error_code

    client._add_cred_info_for_auth_errors(error)
    assert error.details == []

@pytest.mark.parametrize("client_class,transport_name", [
    (AgentAnomalyDetectionServiceClient, "grpc"),
    (AgentAnomalyDetectionServiceAsyncClient, "grpc_asyncio"),
    (AgentAnomalyDetectionServiceClient, "rest"),
])
def test_agent_anomaly_detection_service_client_from_service_account_info(client_class, transport_name):
    creds = ga_credentials.AnonymousCredentials()
    with mock.patch.object(service_account.Credentials, 'from_service_account_info') as factory:
        factory.return_value = creds
        info = {"valid": True}
        client = client_class.from_service_account_info(info, transport=transport_name)
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        assert client.transport._host == (
            'aiplatform.googleapis.com:443'
            if transport_name in ['grpc', 'grpc_asyncio']
            else
            'https://aiplatform.googleapis.com'
        )


@pytest.mark.parametrize("transport_class,transport_name", [
    (transports.AgentAnomalyDetectionServiceGrpcTransport, "grpc"),
    (transports.AgentAnomalyDetectionServiceGrpcAsyncIOTransport, "grpc_asyncio"),
    (transports.AgentAnomalyDetectionServiceRestTransport, "rest"),
])
def test_agent_anomaly_detection_service_client_service_account_always_use_jwt(transport_class, transport_name):
    with mock.patch.object(service_account.Credentials, 'with_always_use_jwt_access', create=True) as use_jwt:
        creds = service_account.Credentials(None, None, None)
        transport = transport_class(credentials=creds, always_use_jwt_access=True)
        use_jwt.assert_called_once_with(True)

    with mock.patch.object(service_account.Credentials, 'with_always_use_jwt_access', create=True) as use_jwt:
        creds = service_account.Credentials(None, None, None)
        transport = transport_class(credentials=creds, always_use_jwt_access=False)
        use_jwt.assert_not_called()


@pytest.mark.parametrize("client_class,transport_name", [
    (AgentAnomalyDetectionServiceClient, "grpc"),
    (AgentAnomalyDetectionServiceAsyncClient, "grpc_asyncio"),
    (AgentAnomalyDetectionServiceClient, "rest"),
])
def test_agent_anomaly_detection_service_client_from_service_account_file(client_class, transport_name):
    creds = ga_credentials.AnonymousCredentials()
    with mock.patch.object(service_account.Credentials, 'from_service_account_file') as factory:
        factory.return_value = creds
        client = client_class.from_service_account_file("dummy/file/path.json", transport=transport_name)
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        client = client_class.from_service_account_json("dummy/file/path.json", transport=transport_name)
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        assert client.transport._host == (
            'aiplatform.googleapis.com:443'
            if transport_name in ['grpc', 'grpc_asyncio']
            else
            'https://aiplatform.googleapis.com'
        )


def test_agent_anomaly_detection_service_client_get_transport_class():
    transport = AgentAnomalyDetectionServiceClient.get_transport_class()
    available_transports = [
        transports.AgentAnomalyDetectionServiceGrpcTransport,
        transports.AgentAnomalyDetectionServiceRestTransport,
    ]
    assert transport in available_transports

    transport = AgentAnomalyDetectionServiceClient.get_transport_class("grpc")
    assert transport == transports.AgentAnomalyDetectionServiceGrpcTransport


@pytest.mark.parametrize("client_class,transport_class,transport_name", [
    (AgentAnomalyDetectionServiceClient, transports.AgentAnomalyDetectionServiceGrpcTransport, "grpc"),
    (AgentAnomalyDetectionServiceAsyncClient, transports.AgentAnomalyDetectionServiceGrpcAsyncIOTransport, "grpc_asyncio"),
    (AgentAnomalyDetectionServiceClient, transports.AgentAnomalyDetectionServiceRestTransport, "rest"),
])
@mock.patch.object(AgentAnomalyDetectionServiceClient, "_DEFAULT_ENDPOINT_TEMPLATE", modify_default_endpoint_template(AgentAnomalyDetectionServiceClient))
@mock.patch.object(AgentAnomalyDetectionServiceAsyncClient, "_DEFAULT_ENDPOINT_TEMPLATE", modify_default_endpoint_template(AgentAnomalyDetectionServiceAsyncClient))
def test_agent_anomaly_detection_service_client_client_options(client_class, transport_class, transport_name):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(AgentAnomalyDetectionServiceClient, 'get_transport_class') as gtc:
        transport = transport_class(
            credentials=ga_credentials.AnonymousCredentials()
        )
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(AgentAnomalyDetectionServiceClient, 'get_transport_class') as gtc:
        client = client_class(transport=transport_name)
        gtc.assert_called()

    # Check the case api_endpoint is provided.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch.object(transport_class, '__init__') as patched:
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
        with mock.patch.object(transport_class, '__init__') as patched:
            patched.return_value = None
            client = client_class(transport=transport_name)
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE),
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
        with mock.patch.object(transport_class, '__init__') as patched:
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
    assert str(excinfo.value) == "Environment variable `GOOGLE_API_USE_MTLS_ENDPOINT` must be `never`, `auto` or `always`"

    # Check the case quota_project_id is provided
    options = client_options.ClientOptions(quota_project_id="octopus")
    with mock.patch.object(transport_class, '__init__') as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE),
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id="octopus",
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )
    # Check the case api_endpoint is provided
    options = client_options.ClientOptions(api_audience="https://language.googleapis.com")
    with mock.patch.object(transport_class, '__init__') as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE),
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience="https://language.googleapis.com"
        )

@pytest.mark.parametrize("client_class,transport_class,transport_name,use_client_cert_env", [
    (AgentAnomalyDetectionServiceClient, transports.AgentAnomalyDetectionServiceGrpcTransport, "grpc", "true"),
    (AgentAnomalyDetectionServiceAsyncClient, transports.AgentAnomalyDetectionServiceGrpcAsyncIOTransport, "grpc_asyncio", "true"),
    (AgentAnomalyDetectionServiceClient, transports.AgentAnomalyDetectionServiceGrpcTransport, "grpc", "false"),
    (AgentAnomalyDetectionServiceAsyncClient, transports.AgentAnomalyDetectionServiceGrpcAsyncIOTransport, "grpc_asyncio", "false"),
    (AgentAnomalyDetectionServiceClient, transports.AgentAnomalyDetectionServiceRestTransport, "rest", "true"),
    (AgentAnomalyDetectionServiceClient, transports.AgentAnomalyDetectionServiceRestTransport, "rest", "false"),
])
@mock.patch.object(AgentAnomalyDetectionServiceClient, "_DEFAULT_ENDPOINT_TEMPLATE", modify_default_endpoint_template(AgentAnomalyDetectionServiceClient))
@mock.patch.object(AgentAnomalyDetectionServiceAsyncClient, "_DEFAULT_ENDPOINT_TEMPLATE", modify_default_endpoint_template(AgentAnomalyDetectionServiceAsyncClient))
@mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"})
def test_agent_anomaly_detection_service_client_mtls_env_auto(client_class, transport_class, transport_name, use_client_cert_env):
    # This tests the endpoint autoswitch behavior. Endpoint is autoswitched to the default
    # mtls endpoint, if GOOGLE_API_USE_CLIENT_CERTIFICATE is "true" and client cert exists.

    # Check the case client_cert_source is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}):
        options = client_options.ClientOptions(client_cert_source=client_cert_source_callback)
        with mock.patch.object(transport_class, '__init__') as patched:
            patched.return_value = None
            client = client_class(client_options=options, transport=transport_name)

            if use_client_cert_env == "false":
                expected_client_cert_source = None
                expected_host = client._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE)
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
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}):
        with mock.patch.object(transport_class, '__init__') as patched:
            with mock.patch('google.auth.transport.mtls.has_default_client_cert_source', return_value=True):
                with mock.patch('google.auth.transport.mtls.default_client_cert_source', return_value=client_cert_source_callback):
                    if use_client_cert_env == "false":
                        expected_host = client._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE)
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
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}):
        with mock.patch.object(transport_class, '__init__') as patched:
            with mock.patch("google.auth.transport.mtls.has_default_client_cert_source", return_value=False):
                patched.return_value = None
                client = client_class(transport=transport_name)
                patched.assert_called_once_with(
                    credentials=None,
                    credentials_file=None,
                    host=client._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE),
                    scopes=None,
                    client_cert_source_for_mtls=None,
                    quota_project_id=None,
                    client_info=transports.base.DEFAULT_CLIENT_INFO,
                    always_use_jwt_access=True,
                    api_audience=None,
                )


@pytest.mark.parametrize("client_class", [
    AgentAnomalyDetectionServiceClient, AgentAnomalyDetectionServiceAsyncClient
])
@mock.patch.object(AgentAnomalyDetectionServiceClient, "DEFAULT_ENDPOINT", modify_default_endpoint(AgentAnomalyDetectionServiceClient))
@mock.patch.object(AgentAnomalyDetectionServiceAsyncClient, "DEFAULT_ENDPOINT", modify_default_endpoint(AgentAnomalyDetectionServiceAsyncClient))
def test_agent_anomaly_detection_service_client_get_mtls_endpoint_and_cert_source(client_class):
    mock_client_cert_source = mock.Mock()

    # Test the case GOOGLE_API_USE_CLIENT_CERTIFICATE is "true".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        mock_api_endpoint = "foo"
        options = client_options.ClientOptions(client_cert_source=mock_client_cert_source, api_endpoint=mock_api_endpoint)
        api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source(options)
        assert api_endpoint == mock_api_endpoint
        assert cert_source == mock_client_cert_source

    # Test the case GOOGLE_API_USE_CLIENT_CERTIFICATE is "false".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "false"}):
        mock_client_cert_source = mock.Mock()
        mock_api_endpoint = "foo"
        options = client_options.ClientOptions(client_cert_source=mock_client_cert_source, api_endpoint=mock_api_endpoint)
        api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source(options)
        assert api_endpoint == mock_api_endpoint
        assert cert_source is None

    # Test the case GOOGLE_API_USE_CLIENT_CERTIFICATE is "Unsupported".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}):
        if hasattr(google.auth.transport.mtls, "should_use_client_cert"):
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

    # Test cases for mTLS enablement when GOOGLE_API_USE_CLIENT_CERTIFICATE is unset.
    test_cases = [
        (
            # With workloads present in config, mTLS is enabled.
            {
                "version": 1,
                "cert_configs": {
                    "workload": {
                        "cert_path": "path/to/cert/file",
                        "key_path": "path/to/key/file",
                    }
                },
            },
            mock_client_cert_source,
        ),
        (
            # With workloads not present in config, mTLS is disabled.
            {
                "version": 1,
                "cert_configs": {},
            },
            None,
        ),
    ]
    if hasattr(google.auth.transport.mtls, "should_use_client_cert"):
        for config_data, expected_cert_source in test_cases:
            env = os.environ.copy()
            env.pop("GOOGLE_API_USE_CLIENT_CERTIFICATE", None)
            env.pop("CLOUDSDK_CONTEXT_AWARE_USE_CLIENT_CERTIFICATE", None)
            with mock.patch.dict(os.environ, env, clear=True):
                    config_filename = "mock_certificate_config.json"
                    config_file_content = json.dumps(config_data)
                    m = mock.mock_open(read_data=config_file_content)
                    with mock.patch("builtins.open", m), mock.patch("os.path.exists", side_effect=lambda path: os.path.basename(path) == config_filename):
                        with mock.patch.dict(
                            os.environ, {"GOOGLE_API_CERTIFICATE_CONFIG": config_filename}
                        ):
                            mock_api_endpoint = "foo"
                            options = client_options.ClientOptions(
                                client_cert_source=mock_client_cert_source,
                                api_endpoint=mock_api_endpoint,
                            )
                            api_endpoint, cert_source = (
                                client_class.get_mtls_endpoint_and_cert_source(options)
                            )
                            assert api_endpoint == mock_api_endpoint
                            assert cert_source is expected_cert_source

    # Test cases for mTLS enablement when GOOGLE_API_USE_CLIENT_CERTIFICATE is unset(empty).
    test_cases = [
        (
            # With workloads present in config, mTLS is enabled.
            {
                "version": 1,
                "cert_configs": {
                    "workload": {
                        "cert_path": "path/to/cert/file",
                        "key_path": "path/to/key/file",
                    }
                },
            },
            mock_client_cert_source,
        ),
        (
            # With workloads not present in config, mTLS is disabled.
            {
                "version": 1,
                "cert_configs": {},
            },
            None,
        ),
    ]
    if hasattr(google.auth.transport.mtls, "should_use_client_cert"):
        for config_data, expected_cert_source in test_cases:
            env = os.environ.copy()
            env.pop("GOOGLE_API_USE_CLIENT_CERTIFICATE", "")
            env.pop("CLOUDSDK_CONTEXT_AWARE_USE_CLIENT_CERTIFICATE", "")
            with mock.patch.dict(os.environ, env, clear=True):
                    config_filename = "mock_certificate_config.json"
                    config_file_content = json.dumps(config_data)
                    m = mock.mock_open(read_data=config_file_content)
                    with mock.patch("builtins.open", m), mock.patch("os.path.exists", side_effect=lambda path: os.path.basename(path) == config_filename):
                        with mock.patch.dict(
                            os.environ, {"GOOGLE_API_CERTIFICATE_CONFIG": config_filename}
                        ):
                            mock_api_endpoint = "foo"
                            options = client_options.ClientOptions(
                                client_cert_source=mock_client_cert_source,
                                api_endpoint=mock_api_endpoint,
                            )
                            api_endpoint, cert_source = (
                                client_class.get_mtls_endpoint_and_cert_source(options)
                            )
                            assert api_endpoint == mock_api_endpoint
                            assert cert_source is expected_cert_source

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
        with mock.patch('google.auth.transport.mtls.has_default_client_cert_source', return_value=False):
            api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source()
            assert api_endpoint == client_class.DEFAULT_ENDPOINT
            assert cert_source is None

    # Test the case GOOGLE_API_USE_MTLS_ENDPOINT is "auto" and default cert exists.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        with mock.patch('google.auth.transport.mtls.has_default_client_cert_source', return_value=True):
            with mock.patch('google.auth.transport.mtls.default_client_cert_source', return_value=mock_client_cert_source):
                api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source()
                assert api_endpoint == client_class.DEFAULT_MTLS_ENDPOINT
                assert cert_source == mock_client_cert_source

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT has
    # unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError) as excinfo:
            client_class.get_mtls_endpoint_and_cert_source()

        assert str(excinfo.value) == "Environment variable `GOOGLE_API_USE_MTLS_ENDPOINT` must be `never`, `auto` or `always`"

@pytest.mark.parametrize("client_class", [
    AgentAnomalyDetectionServiceClient, AgentAnomalyDetectionServiceAsyncClient
])
@mock.patch.object(AgentAnomalyDetectionServiceClient, "_DEFAULT_ENDPOINT_TEMPLATE", modify_default_endpoint_template(AgentAnomalyDetectionServiceClient))
@mock.patch.object(AgentAnomalyDetectionServiceAsyncClient, "_DEFAULT_ENDPOINT_TEMPLATE", modify_default_endpoint_template(AgentAnomalyDetectionServiceAsyncClient))
def test_agent_anomaly_detection_service_client_client_api_endpoint(client_class):
    mock_client_cert_source = client_cert_source_callback
    api_override = "foo.com"
    default_universe = AgentAnomalyDetectionServiceClient._DEFAULT_UNIVERSE
    default_endpoint = AgentAnomalyDetectionServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=default_universe)
    mock_universe = "bar.com"
    mock_endpoint = AgentAnomalyDetectionServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=mock_universe)

    # If ClientOptions.api_endpoint is set and GOOGLE_API_USE_CLIENT_CERTIFICATE="true",
    # use ClientOptions.api_endpoint as the api endpoint regardless.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        with mock.patch("google.auth.transport.requests.AuthorizedSession.configure_mtls_channel"):
            options = client_options.ClientOptions(client_cert_source=mock_client_cert_source, api_endpoint=api_override)
            client = client_class(client_options=options, credentials=ga_credentials.AnonymousCredentials())
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
        client = client_class(client_options=options, credentials=ga_credentials.AnonymousCredentials())
    else:
        client = client_class(client_options=options, credentials=ga_credentials.AnonymousCredentials())
    assert client.api_endpoint == (mock_endpoint if universe_exists else default_endpoint)
    assert client.universe_domain == (mock_universe if universe_exists else default_universe)

    # If ClientOptions does not have a universe domain attribute and GOOGLE_API_USE_MTLS_ENDPOINT="never",
    # use the _DEFAULT_ENDPOINT_TEMPLATE populated with GDU as the api endpoint.
    options = client_options.ClientOptions()
    if hasattr(options, "universe_domain"):
        delattr(options, "universe_domain")
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        client = client_class(client_options=options, credentials=ga_credentials.AnonymousCredentials())
        assert client.api_endpoint == default_endpoint


@pytest.mark.parametrize("client_class,transport_class,transport_name", [
    (AgentAnomalyDetectionServiceClient, transports.AgentAnomalyDetectionServiceGrpcTransport, "grpc"),
    (AgentAnomalyDetectionServiceAsyncClient, transports.AgentAnomalyDetectionServiceGrpcAsyncIOTransport, "grpc_asyncio"),
    (AgentAnomalyDetectionServiceClient, transports.AgentAnomalyDetectionServiceRestTransport, "rest"),
])
def test_agent_anomaly_detection_service_client_client_options_scopes(client_class, transport_class, transport_name):
    # Check the case scopes are provided.
    options = client_options.ClientOptions(
        scopes=["1", "2"],
    )
    with mock.patch.object(transport_class, '__init__') as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE),
            scopes=["1", "2"],
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )

@pytest.mark.parametrize("client_class,transport_class,transport_name,grpc_helpers", [
    (AgentAnomalyDetectionServiceClient, transports.AgentAnomalyDetectionServiceGrpcTransport, "grpc", grpc_helpers),
    (AgentAnomalyDetectionServiceAsyncClient, transports.AgentAnomalyDetectionServiceGrpcAsyncIOTransport, "grpc_asyncio", grpc_helpers_async),
    (AgentAnomalyDetectionServiceClient, transports.AgentAnomalyDetectionServiceRestTransport, "rest", None),
])
def test_agent_anomaly_detection_service_client_client_options_credentials_file(client_class, transport_class, transport_name, grpc_helpers):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(
        credentials_file="credentials.json"
    )

    with mock.patch.object(transport_class, '__init__') as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE),
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )

def test_agent_anomaly_detection_service_client_client_options_from_dict():
    with mock.patch('google.cloud.aiplatform_v1.services.agent_anomaly_detection_service.transports.AgentAnomalyDetectionServiceGrpcTransport.__init__') as grpc_transport:
        grpc_transport.return_value = None
        client = AgentAnomalyDetectionServiceClient(
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
            always_use_jwt_access=True,
            api_audience=None,
        )


@pytest.mark.parametrize("client_class,transport_class,transport_name,grpc_helpers", [
    (AgentAnomalyDetectionServiceClient, transports.AgentAnomalyDetectionServiceGrpcTransport, "grpc", grpc_helpers),
    (AgentAnomalyDetectionServiceAsyncClient, transports.AgentAnomalyDetectionServiceGrpcAsyncIOTransport, "grpc_asyncio", grpc_helpers_async),
])
def test_agent_anomaly_detection_service_client_create_channel_credentials_file(client_class, transport_class, transport_name, grpc_helpers):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(
        credentials_file="credentials.json"
    )

    with mock.patch.object(transport_class, '__init__') as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE),
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
                'https://www.googleapis.com/auth/cloud-platform',
),
            scopes=None,
            default_host="aiplatform.googleapis.com",
            ssl_credentials=None,
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
            ],
        )


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest(),
  {},
])
def test_get_agent_anomaly_detection_scope(request_type, transport: str = 'grpc'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_agent_anomaly_detection_scope),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.AgentAnomalyDetectionScope(
            name='name_value',
            display_name='display_name_value',
            log_buckets=['log_buckets_value'],
            observability_buckets=['observability_buckets_value'],
            auto_enroll=True,
            state=agent_anomaly_detection_service.AgentAnomalyDetectionScope.State.CREATING,
        )
        response = client.get_agent_anomaly_detection_scope(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, agent_anomaly_detection_service.AgentAnomalyDetectionScope)
    assert response.name == 'name_value'
    assert response.display_name == 'display_name_value'
    assert response.log_buckets == ['log_buckets_value']
    assert response.observability_buckets == ['observability_buckets_value']
    assert response.auto_enroll is True
    assert response.state == agent_anomaly_detection_service.AgentAnomalyDetectionScope.State.CREATING


def test_get_agent_anomaly_detection_scope_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='grpc',
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest(
        name='name_value',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_agent_anomaly_detection_scope),
            '__call__') as call:
        call.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client.get_agent_anomaly_detection_scope(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest(
            name='name_value',
        )
        assert args[0] == request_msg

def test_get_agent_anomaly_detection_scope_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.get_agent_anomaly_detection_scope in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.get_agent_anomaly_detection_scope] = mock_rpc
        request = {}
        client.get_agent_anomaly_detection_scope(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_agent_anomaly_detection_scope(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
async def test_get_agent_anomaly_detection_scope_async_use_cached_wrapped_rpc(transport: str = "grpc_asyncio"):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._client._transport.get_agent_anomaly_detection_scope in client._client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[client._client._transport.get_agent_anomaly_detection_scope] = mock_rpc

        request = {}
        await client.get_agent_anomaly_detection_scope(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.get_agent_anomaly_detection_scope(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest(),
  {},
])
async def test_get_agent_anomaly_detection_scope_async(request_type, transport: str = 'grpc_asyncio'):
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_agent_anomaly_detection_scope),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.AgentAnomalyDetectionScope(
            name='name_value',
            display_name='display_name_value',
            log_buckets=['log_buckets_value'],
            observability_buckets=['observability_buckets_value'],
            auto_enroll=True,
            state=agent_anomaly_detection_service.AgentAnomalyDetectionScope.State.CREATING,
        ))
        response = await client.get_agent_anomaly_detection_scope(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, agent_anomaly_detection_service.AgentAnomalyDetectionScope)
    assert response.name == 'name_value'
    assert response.display_name == 'display_name_value'
    assert response.log_buckets == ['log_buckets_value']
    assert response.observability_buckets == ['observability_buckets_value']
    assert response.auto_enroll is True
    assert response.state == agent_anomaly_detection_service.AgentAnomalyDetectionScope.State.CREATING

def test_get_agent_anomaly_detection_scope_field_headers():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_agent_anomaly_detection_scope),
            '__call__') as call:
        call.return_value = agent_anomaly_detection_service.AgentAnomalyDetectionScope()
        client.get_agent_anomaly_detection_scope(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_get_agent_anomaly_detection_scope_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_agent_anomaly_detection_scope),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.AgentAnomalyDetectionScope())
        await client.get_agent_anomaly_detection_scope(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


def test_get_agent_anomaly_detection_scope_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_agent_anomaly_detection_scope),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.AgentAnomalyDetectionScope()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_agent_anomaly_detection_scope(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val


def test_get_agent_anomaly_detection_scope_flattened_error():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_agent_anomaly_detection_scope(
            agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest(),
            name='name_value',
        )

@pytest.mark.asyncio
async def test_get_agent_anomaly_detection_scope_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_agent_anomaly_detection_scope),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.AgentAnomalyDetectionScope()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.AgentAnomalyDetectionScope())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_agent_anomaly_detection_scope(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_get_agent_anomaly_detection_scope_flattened_error_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_agent_anomaly_detection_scope(
            agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest(),
            name='name_value',
        )


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.GetMonitoredAgentRequest(),
  {},
])
def test_get_monitored_agent(request_type, transport: str = 'grpc'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_monitored_agent),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.MonitoredAgent(
            name='name_value',
            display_name='display_name_value',
            state=agent_anomaly_detection_service.MonitoredAgent.EnablementState.ACTIVE,
            status_message='status_message_value',
        )
        response = client.get_monitored_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.GetMonitoredAgentRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, agent_anomaly_detection_service.MonitoredAgent)
    assert response.name == 'name_value'
    assert response.display_name == 'display_name_value'
    assert response.state == agent_anomaly_detection_service.MonitoredAgent.EnablementState.ACTIVE
    assert response.status_message == 'status_message_value'


def test_get_monitored_agent_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='grpc',
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = agent_anomaly_detection_service.GetMonitoredAgentRequest(
        name='name_value',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_monitored_agent),
            '__call__') as call:
        call.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client.get_monitored_agent(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.GetMonitoredAgentRequest(
            name='name_value',
        )
        assert args[0] == request_msg

def test_get_monitored_agent_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.get_monitored_agent in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.get_monitored_agent] = mock_rpc
        request = {}
        client.get_monitored_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_monitored_agent(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
async def test_get_monitored_agent_async_use_cached_wrapped_rpc(transport: str = "grpc_asyncio"):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._client._transport.get_monitored_agent in client._client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[client._client._transport.get_monitored_agent] = mock_rpc

        request = {}
        await client.get_monitored_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.get_monitored_agent(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.GetMonitoredAgentRequest(),
  {},
])
async def test_get_monitored_agent_async(request_type, transport: str = 'grpc_asyncio'):
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_monitored_agent),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.MonitoredAgent(
            name='name_value',
            display_name='display_name_value',
            state=agent_anomaly_detection_service.MonitoredAgent.EnablementState.ACTIVE,
            status_message='status_message_value',
        ))
        response = await client.get_monitored_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.GetMonitoredAgentRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, agent_anomaly_detection_service.MonitoredAgent)
    assert response.name == 'name_value'
    assert response.display_name == 'display_name_value'
    assert response.state == agent_anomaly_detection_service.MonitoredAgent.EnablementState.ACTIVE
    assert response.status_message == 'status_message_value'

def test_get_monitored_agent_field_headers():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.GetMonitoredAgentRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_monitored_agent),
            '__call__') as call:
        call.return_value = agent_anomaly_detection_service.MonitoredAgent()
        client.get_monitored_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_get_monitored_agent_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.GetMonitoredAgentRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_monitored_agent),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.MonitoredAgent())
        await client.get_monitored_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


def test_get_monitored_agent_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_monitored_agent),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.MonitoredAgent()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_monitored_agent(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val


def test_get_monitored_agent_flattened_error():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_monitored_agent(
            agent_anomaly_detection_service.GetMonitoredAgentRequest(),
            name='name_value',
        )

@pytest.mark.asyncio
async def test_get_monitored_agent_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_monitored_agent),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.MonitoredAgent()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.MonitoredAgent())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_monitored_agent(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_get_monitored_agent_flattened_error_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_monitored_agent(
            agent_anomaly_detection_service.GetMonitoredAgentRequest(),
            name='name_value',
        )


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.ListMonitoredAgentsRequest(),
  {},
])
def test_list_monitored_agents(request_type, transport: str = 'grpc'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_monitored_agents),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.ListMonitoredAgentsResponse(
            next_page_token='next_page_token_value',
            total_size=1086,
        )
        response = client.list_monitored_agents(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.ListMonitoredAgentsRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListMonitoredAgentsPager)
    assert response.next_page_token == 'next_page_token_value'
    assert response.total_size == 1086


def test_list_monitored_agents_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='grpc',
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = agent_anomaly_detection_service.ListMonitoredAgentsRequest(
        parent='parent_value',
        page_token='page_token_value',
        filter='filter_value',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_monitored_agents),
            '__call__') as call:
        call.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client.list_monitored_agents(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ListMonitoredAgentsRequest(
            parent='parent_value',
            page_token='page_token_value',
            filter='filter_value',
        )
        assert args[0] == request_msg

def test_list_monitored_agents_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.list_monitored_agents in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.list_monitored_agents] = mock_rpc
        request = {}
        client.list_monitored_agents(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_monitored_agents(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
async def test_list_monitored_agents_async_use_cached_wrapped_rpc(transport: str = "grpc_asyncio"):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._client._transport.list_monitored_agents in client._client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[client._client._transport.list_monitored_agents] = mock_rpc

        request = {}
        await client.list_monitored_agents(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.list_monitored_agents(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.ListMonitoredAgentsRequest(),
  {},
])
async def test_list_monitored_agents_async(request_type, transport: str = 'grpc_asyncio'):
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_monitored_agents),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.ListMonitoredAgentsResponse(
            next_page_token='next_page_token_value',
            total_size=1086,
        ))
        response = await client.list_monitored_agents(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.ListMonitoredAgentsRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListMonitoredAgentsAsyncPager)
    assert response.next_page_token == 'next_page_token_value'
    assert response.total_size == 1086

def test_list_monitored_agents_field_headers():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.ListMonitoredAgentsRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_monitored_agents),
            '__call__') as call:
        call.return_value = agent_anomaly_detection_service.ListMonitoredAgentsResponse()
        client.list_monitored_agents(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_list_monitored_agents_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.ListMonitoredAgentsRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_monitored_agents),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.ListMonitoredAgentsResponse())
        await client.list_monitored_agents(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


def test_list_monitored_agents_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_monitored_agents),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.ListMonitoredAgentsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_monitored_agents(
            parent='parent_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val


def test_list_monitored_agents_flattened_error():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_monitored_agents(
            agent_anomaly_detection_service.ListMonitoredAgentsRequest(),
            parent='parent_value',
        )

@pytest.mark.asyncio
async def test_list_monitored_agents_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_monitored_agents),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.ListMonitoredAgentsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.ListMonitoredAgentsResponse())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_monitored_agents(
            parent='parent_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_list_monitored_agents_flattened_error_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_monitored_agents(
            agent_anomaly_detection_service.ListMonitoredAgentsRequest(),
            parent='parent_value',
        )


def test_list_monitored_agents_pager(transport_name: str = "grpc"):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_monitored_agents),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent_anomaly_detection_service.ListMonitoredAgentsResponse(
                monitored_agents=[
                    agent_anomaly_detection_service.MonitoredAgent(),
                    agent_anomaly_detection_service.MonitoredAgent(),
                    agent_anomaly_detection_service.MonitoredAgent(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.ListMonitoredAgentsResponse(
                monitored_agents=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.ListMonitoredAgentsResponse(
                monitored_agents=[
                    agent_anomaly_detection_service.MonitoredAgent(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.ListMonitoredAgentsResponse(
                monitored_agents=[
                    agent_anomaly_detection_service.MonitoredAgent(),
                    agent_anomaly_detection_service.MonitoredAgent(),
                ],
            ),
            RuntimeError,
        )

        expected_metadata = ()
        retry = retries.Retry()
        timeout = 5
        expected_metadata = tuple(expected_metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((
                ('parent', ''),
            )),
        )
        pager = client.list_monitored_agents(request={}, retry=retry, timeout=timeout)

        assert pager._metadata == expected_metadata
        assert pager._retry == retry
        assert pager._timeout == timeout

        assert pager.next_page_token == 'abc'
        assert str(pager).startswith(f'{pager.__class__.__name__}<')

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, agent_anomaly_detection_service.MonitoredAgent)
                   for i in results)
def test_list_monitored_agents_pages(transport_name: str = "grpc"):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_monitored_agents),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent_anomaly_detection_service.ListMonitoredAgentsResponse(
                monitored_agents=[
                    agent_anomaly_detection_service.MonitoredAgent(),
                    agent_anomaly_detection_service.MonitoredAgent(),
                    agent_anomaly_detection_service.MonitoredAgent(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.ListMonitoredAgentsResponse(
                monitored_agents=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.ListMonitoredAgentsResponse(
                monitored_agents=[
                    agent_anomaly_detection_service.MonitoredAgent(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.ListMonitoredAgentsResponse(
                monitored_agents=[
                    agent_anomaly_detection_service.MonitoredAgent(),
                    agent_anomaly_detection_service.MonitoredAgent(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_monitored_agents(request={}).pages)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token

@pytest.mark.asyncio
async def test_list_monitored_agents_async_pager():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_monitored_agents),
            '__call__', new_callable=mock.AsyncMock) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent_anomaly_detection_service.ListMonitoredAgentsResponse(
                monitored_agents=[
                    agent_anomaly_detection_service.MonitoredAgent(),
                    agent_anomaly_detection_service.MonitoredAgent(),
                    agent_anomaly_detection_service.MonitoredAgent(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.ListMonitoredAgentsResponse(
                monitored_agents=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.ListMonitoredAgentsResponse(
                monitored_agents=[
                    agent_anomaly_detection_service.MonitoredAgent(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.ListMonitoredAgentsResponse(
                monitored_agents=[
                    agent_anomaly_detection_service.MonitoredAgent(),
                    agent_anomaly_detection_service.MonitoredAgent(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_monitored_agents(request={},)
        assert async_pager.next_page_token == 'abc'
        assert str(async_pager).startswith(f'{async_pager.__class__.__name__}<')

        responses = []
        async for response in async_pager: # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, agent_anomaly_detection_service.MonitoredAgent)
                for i in responses)


@pytest.mark.asyncio
async def test_list_monitored_agents_async_pages():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_monitored_agents),
            '__call__', new_callable=mock.AsyncMock) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent_anomaly_detection_service.ListMonitoredAgentsResponse(
                monitored_agents=[
                    agent_anomaly_detection_service.MonitoredAgent(),
                    agent_anomaly_detection_service.MonitoredAgent(),
                    agent_anomaly_detection_service.MonitoredAgent(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.ListMonitoredAgentsResponse(
                monitored_agents=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.ListMonitoredAgentsResponse(
                monitored_agents=[
                    agent_anomaly_detection_service.MonitoredAgent(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.ListMonitoredAgentsResponse(
                monitored_agents=[
                    agent_anomaly_detection_service.MonitoredAgent(),
                    agent_anomaly_detection_service.MonitoredAgent(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (
            await client.list_monitored_agents(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token

@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.EnableMonitoredAgentRequest(),
  {},
])
def test_enable_monitored_agent(request_type, transport: str = 'grpc'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.enable_monitored_agent),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/spam')
        response = client.enable_monitored_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.EnableMonitoredAgentRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_enable_monitored_agent_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='grpc',
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = agent_anomaly_detection_service.EnableMonitoredAgentRequest(
        name='name_value',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.enable_monitored_agent),
            '__call__') as call:
        call.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client.enable_monitored_agent(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.EnableMonitoredAgentRequest(
            name='name_value',
        )
        assert args[0] == request_msg

def test_enable_monitored_agent_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.enable_monitored_agent in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.enable_monitored_agent] = mock_rpc
        request = {}
        client.enable_monitored_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.enable_monitored_agent(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
async def test_enable_monitored_agent_async_use_cached_wrapped_rpc(transport: str = "grpc_asyncio"):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._client._transport.enable_monitored_agent in client._client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[client._client._transport.enable_monitored_agent] = mock_rpc

        request = {}
        await client.enable_monitored_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.enable_monitored_agent(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.EnableMonitoredAgentRequest(),
  {},
])
async def test_enable_monitored_agent_async(request_type, transport: str = 'grpc_asyncio'):
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.enable_monitored_agent),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name='operations/spam')
        )
        response = await client.enable_monitored_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.EnableMonitoredAgentRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)

def test_enable_monitored_agent_field_headers():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.EnableMonitoredAgentRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.enable_monitored_agent),
            '__call__') as call:
        call.return_value = operations_pb2.Operation(name='operations/op')
        client.enable_monitored_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_enable_monitored_agent_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.EnableMonitoredAgentRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.enable_monitored_agent),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(operations_pb2.Operation(name='operations/op'))
        await client.enable_monitored_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


def test_enable_monitored_agent_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.enable_monitored_agent),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/op')
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.enable_monitored_agent(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val


def test_enable_monitored_agent_flattened_error():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.enable_monitored_agent(
            agent_anomaly_detection_service.EnableMonitoredAgentRequest(),
            name='name_value',
        )

@pytest.mark.asyncio
async def test_enable_monitored_agent_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.enable_monitored_agent),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/op')

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name='operations/spam')
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.enable_monitored_agent(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_enable_monitored_agent_flattened_error_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.enable_monitored_agent(
            agent_anomaly_detection_service.EnableMonitoredAgentRequest(),
            name='name_value',
        )


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.DisableMonitoredAgentRequest(),
  {},
])
def test_disable_monitored_agent(request_type, transport: str = 'grpc'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.disable_monitored_agent),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/spam')
        response = client.disable_monitored_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.DisableMonitoredAgentRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_disable_monitored_agent_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='grpc',
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = agent_anomaly_detection_service.DisableMonitoredAgentRequest(
        name='name_value',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.disable_monitored_agent),
            '__call__') as call:
        call.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client.disable_monitored_agent(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.DisableMonitoredAgentRequest(
            name='name_value',
        )
        assert args[0] == request_msg

def test_disable_monitored_agent_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.disable_monitored_agent in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.disable_monitored_agent] = mock_rpc
        request = {}
        client.disable_monitored_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.disable_monitored_agent(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
async def test_disable_monitored_agent_async_use_cached_wrapped_rpc(transport: str = "grpc_asyncio"):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._client._transport.disable_monitored_agent in client._client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[client._client._transport.disable_monitored_agent] = mock_rpc

        request = {}
        await client.disable_monitored_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.disable_monitored_agent(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.DisableMonitoredAgentRequest(),
  {},
])
async def test_disable_monitored_agent_async(request_type, transport: str = 'grpc_asyncio'):
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.disable_monitored_agent),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name='operations/spam')
        )
        response = await client.disable_monitored_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.DisableMonitoredAgentRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)

def test_disable_monitored_agent_field_headers():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.DisableMonitoredAgentRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.disable_monitored_agent),
            '__call__') as call:
        call.return_value = operations_pb2.Operation(name='operations/op')
        client.disable_monitored_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_disable_monitored_agent_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.DisableMonitoredAgentRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.disable_monitored_agent),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(operations_pb2.Operation(name='operations/op'))
        await client.disable_monitored_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


def test_disable_monitored_agent_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.disable_monitored_agent),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/op')
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.disable_monitored_agent(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val


def test_disable_monitored_agent_flattened_error():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.disable_monitored_agent(
            agent_anomaly_detection_service.DisableMonitoredAgentRequest(),
            name='name_value',
        )

@pytest.mark.asyncio
async def test_disable_monitored_agent_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.disable_monitored_agent),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/op')

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name='operations/spam')
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.disable_monitored_agent(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_disable_monitored_agent_flattened_error_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.disable_monitored_agent(
            agent_anomaly_detection_service.DisableMonitoredAgentRequest(),
            name='name_value',
        )


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest(),
  {},
])
def test_delete_agent_anomaly_detection_scope(request_type, transport: str = 'grpc'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_agent_anomaly_detection_scope),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/spam')
        response = client.delete_agent_anomaly_detection_scope(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_agent_anomaly_detection_scope_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='grpc',
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest(
        name='name_value',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_agent_anomaly_detection_scope),
            '__call__') as call:
        call.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client.delete_agent_anomaly_detection_scope(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest(
            name='name_value',
        )
        assert args[0] == request_msg

def test_delete_agent_anomaly_detection_scope_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.delete_agent_anomaly_detection_scope in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.delete_agent_anomaly_detection_scope] = mock_rpc
        request = {}
        client.delete_agent_anomaly_detection_scope(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.delete_agent_anomaly_detection_scope(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
async def test_delete_agent_anomaly_detection_scope_async_use_cached_wrapped_rpc(transport: str = "grpc_asyncio"):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._client._transport.delete_agent_anomaly_detection_scope in client._client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[client._client._transport.delete_agent_anomaly_detection_scope] = mock_rpc

        request = {}
        await client.delete_agent_anomaly_detection_scope(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.delete_agent_anomaly_detection_scope(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest(),
  {},
])
async def test_delete_agent_anomaly_detection_scope_async(request_type, transport: str = 'grpc_asyncio'):
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_agent_anomaly_detection_scope),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name='operations/spam')
        )
        response = await client.delete_agent_anomaly_detection_scope(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)

def test_delete_agent_anomaly_detection_scope_field_headers():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_agent_anomaly_detection_scope),
            '__call__') as call:
        call.return_value = operations_pb2.Operation(name='operations/op')
        client.delete_agent_anomaly_detection_scope(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_delete_agent_anomaly_detection_scope_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_agent_anomaly_detection_scope),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(operations_pb2.Operation(name='operations/op'))
        await client.delete_agent_anomaly_detection_scope(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


def test_delete_agent_anomaly_detection_scope_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_agent_anomaly_detection_scope),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/op')
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_agent_anomaly_detection_scope(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val


def test_delete_agent_anomaly_detection_scope_flattened_error():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_agent_anomaly_detection_scope(
            agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest(),
            name='name_value',
        )

@pytest.mark.asyncio
async def test_delete_agent_anomaly_detection_scope_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_agent_anomaly_detection_scope),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/op')

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name='operations/spam')
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_agent_anomaly_detection_scope(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_delete_agent_anomaly_detection_scope_flattened_error_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_agent_anomaly_detection_scope(
            agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest(),
            name='name_value',
        )


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest(),
  {},
])
def test_create_agent_anomaly_detection_scope(request_type, transport: str = 'grpc'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_agent_anomaly_detection_scope),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/spam')
        response = client.create_agent_anomaly_detection_scope(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_create_agent_anomaly_detection_scope_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='grpc',
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest(
        parent='parent_value',
        agent_anomaly_detection_scope_id='agent_anomaly_detection_scope_id_value',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_agent_anomaly_detection_scope),
            '__call__') as call:
        call.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client.create_agent_anomaly_detection_scope(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest(
            parent='parent_value',
            agent_anomaly_detection_scope_id='agent_anomaly_detection_scope_id_value',
        )
        assert args[0] == request_msg

def test_create_agent_anomaly_detection_scope_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.create_agent_anomaly_detection_scope in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.create_agent_anomaly_detection_scope] = mock_rpc
        request = {}
        client.create_agent_anomaly_detection_scope(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.create_agent_anomaly_detection_scope(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
async def test_create_agent_anomaly_detection_scope_async_use_cached_wrapped_rpc(transport: str = "grpc_asyncio"):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._client._transport.create_agent_anomaly_detection_scope in client._client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[client._client._transport.create_agent_anomaly_detection_scope] = mock_rpc

        request = {}
        await client.create_agent_anomaly_detection_scope(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.create_agent_anomaly_detection_scope(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest(),
  {},
])
async def test_create_agent_anomaly_detection_scope_async(request_type, transport: str = 'grpc_asyncio'):
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_agent_anomaly_detection_scope),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name='operations/spam')
        )
        response = await client.create_agent_anomaly_detection_scope(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)

def test_create_agent_anomaly_detection_scope_field_headers():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_agent_anomaly_detection_scope),
            '__call__') as call:
        call.return_value = operations_pb2.Operation(name='operations/op')
        client.create_agent_anomaly_detection_scope(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_create_agent_anomaly_detection_scope_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_agent_anomaly_detection_scope),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(operations_pb2.Operation(name='operations/op'))
        await client.create_agent_anomaly_detection_scope(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


def test_create_agent_anomaly_detection_scope_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_agent_anomaly_detection_scope),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/op')
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_agent_anomaly_detection_scope(
            parent='parent_value',
            agent_anomaly_detection_scope=agent_anomaly_detection_service.AgentAnomalyDetectionScope(name='name_value'),
            agent_anomaly_detection_scope_id='agent_anomaly_detection_scope_id_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val
        arg = args[0].agent_anomaly_detection_scope
        mock_val = agent_anomaly_detection_service.AgentAnomalyDetectionScope(name='name_value')
        assert arg == mock_val
        arg = args[0].agent_anomaly_detection_scope_id
        mock_val = 'agent_anomaly_detection_scope_id_value'
        assert arg == mock_val


def test_create_agent_anomaly_detection_scope_flattened_error():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_agent_anomaly_detection_scope(
            agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest(),
            parent='parent_value',
            agent_anomaly_detection_scope=agent_anomaly_detection_service.AgentAnomalyDetectionScope(name='name_value'),
            agent_anomaly_detection_scope_id='agent_anomaly_detection_scope_id_value',
        )

@pytest.mark.asyncio
async def test_create_agent_anomaly_detection_scope_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.create_agent_anomaly_detection_scope),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/op')

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name='operations/spam')
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_agent_anomaly_detection_scope(
            parent='parent_value',
            agent_anomaly_detection_scope=agent_anomaly_detection_service.AgentAnomalyDetectionScope(name='name_value'),
            agent_anomaly_detection_scope_id='agent_anomaly_detection_scope_id_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val
        arg = args[0].agent_anomaly_detection_scope
        mock_val = agent_anomaly_detection_service.AgentAnomalyDetectionScope(name='name_value')
        assert arg == mock_val
        arg = args[0].agent_anomaly_detection_scope_id
        mock_val = 'agent_anomaly_detection_scope_id_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_create_agent_anomaly_detection_scope_flattened_error_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_agent_anomaly_detection_scope(
            agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest(),
            parent='parent_value',
            agent_anomaly_detection_scope=agent_anomaly_detection_service.AgentAnomalyDetectionScope(name='name_value'),
            agent_anomaly_detection_scope_id='agent_anomaly_detection_scope_id_value',
        )


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest(),
  {},
])
def test_list_agent_anomaly_detection_scopes(request_type, transport: str = 'grpc'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_agent_anomaly_detection_scopes),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
            next_page_token='next_page_token_value',
        )
        response = client.list_agent_anomaly_detection_scopes(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListAgentAnomalyDetectionScopesPager)
    assert response.next_page_token == 'next_page_token_value'


def test_list_agent_anomaly_detection_scopes_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='grpc',
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest(
        parent='parent_value',
        page_token='page_token_value',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_agent_anomaly_detection_scopes),
            '__call__') as call:
        call.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client.list_agent_anomaly_detection_scopes(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest(
            parent='parent_value',
            page_token='page_token_value',
        )
        assert args[0] == request_msg

def test_list_agent_anomaly_detection_scopes_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.list_agent_anomaly_detection_scopes in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.list_agent_anomaly_detection_scopes] = mock_rpc
        request = {}
        client.list_agent_anomaly_detection_scopes(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_agent_anomaly_detection_scopes(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
async def test_list_agent_anomaly_detection_scopes_async_use_cached_wrapped_rpc(transport: str = "grpc_asyncio"):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._client._transport.list_agent_anomaly_detection_scopes in client._client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[client._client._transport.list_agent_anomaly_detection_scopes] = mock_rpc

        request = {}
        await client.list_agent_anomaly_detection_scopes(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.list_agent_anomaly_detection_scopes(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest(),
  {},
])
async def test_list_agent_anomaly_detection_scopes_async(request_type, transport: str = 'grpc_asyncio'):
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_agent_anomaly_detection_scopes),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
            next_page_token='next_page_token_value',
        ))
        response = await client.list_agent_anomaly_detection_scopes(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListAgentAnomalyDetectionScopesAsyncPager)
    assert response.next_page_token == 'next_page_token_value'

def test_list_agent_anomaly_detection_scopes_field_headers():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_agent_anomaly_detection_scopes),
            '__call__') as call:
        call.return_value = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse()
        client.list_agent_anomaly_detection_scopes(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_list_agent_anomaly_detection_scopes_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_agent_anomaly_detection_scopes),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse())
        await client.list_agent_anomaly_detection_scopes(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


def test_list_agent_anomaly_detection_scopes_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_agent_anomaly_detection_scopes),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_agent_anomaly_detection_scopes(
            parent='parent_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val


def test_list_agent_anomaly_detection_scopes_flattened_error():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_agent_anomaly_detection_scopes(
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest(),
            parent='parent_value',
        )

@pytest.mark.asyncio
async def test_list_agent_anomaly_detection_scopes_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_agent_anomaly_detection_scopes),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_agent_anomaly_detection_scopes(
            parent='parent_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_list_agent_anomaly_detection_scopes_flattened_error_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_agent_anomaly_detection_scopes(
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest(),
            parent='parent_value',
        )


def test_list_agent_anomaly_detection_scopes_pager(transport_name: str = "grpc"):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_agent_anomaly_detection_scopes),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
                agent_anomaly_detection_scopes=[
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
                agent_anomaly_detection_scopes=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
                agent_anomaly_detection_scopes=[
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
                agent_anomaly_detection_scopes=[
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                ],
            ),
            RuntimeError,
        )

        expected_metadata = ()
        retry = retries.Retry()
        timeout = 5
        expected_metadata = tuple(expected_metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((
                ('parent', ''),
            )),
        )
        pager = client.list_agent_anomaly_detection_scopes(request={}, retry=retry, timeout=timeout)

        assert pager._metadata == expected_metadata
        assert pager._retry == retry
        assert pager._timeout == timeout

        assert pager.next_page_token == 'abc'
        assert str(pager).startswith(f'{pager.__class__.__name__}<')

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, agent_anomaly_detection_service.AgentAnomalyDetectionScope)
                   for i in results)
def test_list_agent_anomaly_detection_scopes_pages(transport_name: str = "grpc"):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_agent_anomaly_detection_scopes),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
                agent_anomaly_detection_scopes=[
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
                agent_anomaly_detection_scopes=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
                agent_anomaly_detection_scopes=[
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
                agent_anomaly_detection_scopes=[
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_agent_anomaly_detection_scopes(request={}).pages)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token

@pytest.mark.asyncio
async def test_list_agent_anomaly_detection_scopes_async_pager():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_agent_anomaly_detection_scopes),
            '__call__', new_callable=mock.AsyncMock) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
                agent_anomaly_detection_scopes=[
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
                agent_anomaly_detection_scopes=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
                agent_anomaly_detection_scopes=[
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
                agent_anomaly_detection_scopes=[
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_agent_anomaly_detection_scopes(request={},)
        assert async_pager.next_page_token == 'abc'
        assert str(async_pager).startswith(f'{async_pager.__class__.__name__}<')

        responses = []
        async for response in async_pager: # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, agent_anomaly_detection_service.AgentAnomalyDetectionScope)
                for i in responses)


@pytest.mark.asyncio
async def test_list_agent_anomaly_detection_scopes_async_pages():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_agent_anomaly_detection_scopes),
            '__call__', new_callable=mock.AsyncMock) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
                agent_anomaly_detection_scopes=[
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
                agent_anomaly_detection_scopes=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
                agent_anomaly_detection_scopes=[
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
                agent_anomaly_detection_scopes=[
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (
            await client.list_agent_anomaly_detection_scopes(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token

@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.ListAnalyzedSessionsRequest(),
  {},
])
def test_list_analyzed_sessions(request_type, transport: str = 'grpc'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_sessions),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
            next_page_token='next_page_token_value',
        )
        response = client.list_analyzed_sessions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.ListAnalyzedSessionsRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListAnalyzedSessionsPager)
    assert response.next_page_token == 'next_page_token_value'


def test_list_analyzed_sessions_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='grpc',
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = agent_anomaly_detection_service.ListAnalyzedSessionsRequest(
        parent='parent_value',
        page_token='page_token_value',
        filter='filter_value',
        order_by='order_by_value',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_sessions),
            '__call__') as call:
        call.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client.list_analyzed_sessions(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ListAnalyzedSessionsRequest(
            parent='parent_value',
            page_token='page_token_value',
            filter='filter_value',
            order_by='order_by_value',
        )
        assert args[0] == request_msg

def test_list_analyzed_sessions_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.list_analyzed_sessions in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.list_analyzed_sessions] = mock_rpc
        request = {}
        client.list_analyzed_sessions(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_analyzed_sessions(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
async def test_list_analyzed_sessions_async_use_cached_wrapped_rpc(transport: str = "grpc_asyncio"):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._client._transport.list_analyzed_sessions in client._client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[client._client._transport.list_analyzed_sessions] = mock_rpc

        request = {}
        await client.list_analyzed_sessions(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.list_analyzed_sessions(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.ListAnalyzedSessionsRequest(),
  {},
])
async def test_list_analyzed_sessions_async(request_type, transport: str = 'grpc_asyncio'):
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_sessions),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
            next_page_token='next_page_token_value',
        ))
        response = await client.list_analyzed_sessions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.ListAnalyzedSessionsRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListAnalyzedSessionsAsyncPager)
    assert response.next_page_token == 'next_page_token_value'

def test_list_analyzed_sessions_field_headers():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.ListAnalyzedSessionsRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_sessions),
            '__call__') as call:
        call.return_value = agent_anomaly_detection_service.ListAnalyzedSessionsResponse()
        client.list_analyzed_sessions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_list_analyzed_sessions_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.ListAnalyzedSessionsRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_sessions),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.ListAnalyzedSessionsResponse())
        await client.list_analyzed_sessions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


def test_list_analyzed_sessions_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_sessions),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.ListAnalyzedSessionsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_analyzed_sessions(
            parent='parent_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val


def test_list_analyzed_sessions_flattened_error():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_analyzed_sessions(
            agent_anomaly_detection_service.ListAnalyzedSessionsRequest(),
            parent='parent_value',
        )

@pytest.mark.asyncio
async def test_list_analyzed_sessions_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_sessions),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.ListAnalyzedSessionsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.ListAnalyzedSessionsResponse())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_analyzed_sessions(
            parent='parent_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_list_analyzed_sessions_flattened_error_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_analyzed_sessions(
            agent_anomaly_detection_service.ListAnalyzedSessionsRequest(),
            parent='parent_value',
        )


def test_list_analyzed_sessions_pager(transport_name: str = "grpc"):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_sessions),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
                analyzed_sessions=[
                    agent_anomaly_detection_service.AnalyzedSession(),
                    agent_anomaly_detection_service.AnalyzedSession(),
                    agent_anomaly_detection_service.AnalyzedSession(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
                analyzed_sessions=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
                analyzed_sessions=[
                    agent_anomaly_detection_service.AnalyzedSession(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
                analyzed_sessions=[
                    agent_anomaly_detection_service.AnalyzedSession(),
                    agent_anomaly_detection_service.AnalyzedSession(),
                ],
            ),
            RuntimeError,
        )

        expected_metadata = ()
        retry = retries.Retry()
        timeout = 5
        expected_metadata = tuple(expected_metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((
                ('parent', ''),
            )),
        )
        pager = client.list_analyzed_sessions(request={}, retry=retry, timeout=timeout)

        assert pager._metadata == expected_metadata
        assert pager._retry == retry
        assert pager._timeout == timeout

        assert pager.next_page_token == 'abc'
        assert str(pager).startswith(f'{pager.__class__.__name__}<')

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, agent_anomaly_detection_service.AnalyzedSession)
                   for i in results)
def test_list_analyzed_sessions_pages(transport_name: str = "grpc"):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_sessions),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
                analyzed_sessions=[
                    agent_anomaly_detection_service.AnalyzedSession(),
                    agent_anomaly_detection_service.AnalyzedSession(),
                    agent_anomaly_detection_service.AnalyzedSession(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
                analyzed_sessions=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
                analyzed_sessions=[
                    agent_anomaly_detection_service.AnalyzedSession(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
                analyzed_sessions=[
                    agent_anomaly_detection_service.AnalyzedSession(),
                    agent_anomaly_detection_service.AnalyzedSession(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_analyzed_sessions(request={}).pages)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token

@pytest.mark.asyncio
async def test_list_analyzed_sessions_async_pager():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_sessions),
            '__call__', new_callable=mock.AsyncMock) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
                analyzed_sessions=[
                    agent_anomaly_detection_service.AnalyzedSession(),
                    agent_anomaly_detection_service.AnalyzedSession(),
                    agent_anomaly_detection_service.AnalyzedSession(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
                analyzed_sessions=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
                analyzed_sessions=[
                    agent_anomaly_detection_service.AnalyzedSession(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
                analyzed_sessions=[
                    agent_anomaly_detection_service.AnalyzedSession(),
                    agent_anomaly_detection_service.AnalyzedSession(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_analyzed_sessions(request={},)
        assert async_pager.next_page_token == 'abc'
        assert str(async_pager).startswith(f'{async_pager.__class__.__name__}<')

        responses = []
        async for response in async_pager: # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, agent_anomaly_detection_service.AnalyzedSession)
                for i in responses)


@pytest.mark.asyncio
async def test_list_analyzed_sessions_async_pages():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_sessions),
            '__call__', new_callable=mock.AsyncMock) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
                analyzed_sessions=[
                    agent_anomaly_detection_service.AnalyzedSession(),
                    agent_anomaly_detection_service.AnalyzedSession(),
                    agent_anomaly_detection_service.AnalyzedSession(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
                analyzed_sessions=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
                analyzed_sessions=[
                    agent_anomaly_detection_service.AnalyzedSession(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
                analyzed_sessions=[
                    agent_anomaly_detection_service.AnalyzedSession(),
                    agent_anomaly_detection_service.AnalyzedSession(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (
            await client.list_analyzed_sessions(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token

@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.GetAnalyzedSessionRequest(),
  {},
])
def test_get_analyzed_session(request_type, transport: str = 'grpc'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_analyzed_session),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.AnalyzedSession(
            name='name_value',
            session_id='session_id_value',
            user_id='user_id_value',
            agent_resource_name='agent_resource_name_value',
            session_state=agent_anomaly_detection_service.AnalyzedSession.SessionState.SESSION_STATE_UNANALYZED,
            agent_display_name='agent_display_name_value',
            agent_state=agent_anomaly_detection_service.MonitoredAgent.EnablementState.ACTIVE,
            location='location_value',
            agent_type=agent_anomaly_detection_service.AgentResource.AgentType.REASONING_ENGINE,
        )
        response = client.get_analyzed_session(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.GetAnalyzedSessionRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, agent_anomaly_detection_service.AnalyzedSession)
    assert response.name == 'name_value'
    assert response.session_id == 'session_id_value'
    assert response.user_id == 'user_id_value'
    assert response.agent_resource_name == 'agent_resource_name_value'
    assert response.session_state == agent_anomaly_detection_service.AnalyzedSession.SessionState.SESSION_STATE_UNANALYZED
    assert response.agent_display_name == 'agent_display_name_value'
    assert response.agent_state == agent_anomaly_detection_service.MonitoredAgent.EnablementState.ACTIVE
    assert response.location == 'location_value'
    assert response.agent_type == agent_anomaly_detection_service.AgentResource.AgentType.REASONING_ENGINE


def test_get_analyzed_session_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='grpc',
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = agent_anomaly_detection_service.GetAnalyzedSessionRequest(
        name='name_value',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_analyzed_session),
            '__call__') as call:
        call.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client.get_analyzed_session(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.GetAnalyzedSessionRequest(
            name='name_value',
        )
        assert args[0] == request_msg

def test_get_analyzed_session_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.get_analyzed_session in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.get_analyzed_session] = mock_rpc
        request = {}
        client.get_analyzed_session(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_analyzed_session(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
async def test_get_analyzed_session_async_use_cached_wrapped_rpc(transport: str = "grpc_asyncio"):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._client._transport.get_analyzed_session in client._client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[client._client._transport.get_analyzed_session] = mock_rpc

        request = {}
        await client.get_analyzed_session(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.get_analyzed_session(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.GetAnalyzedSessionRequest(),
  {},
])
async def test_get_analyzed_session_async(request_type, transport: str = 'grpc_asyncio'):
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_analyzed_session),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.AnalyzedSession(
            name='name_value',
            session_id='session_id_value',
            user_id='user_id_value',
            agent_resource_name='agent_resource_name_value',
            session_state=agent_anomaly_detection_service.AnalyzedSession.SessionState.SESSION_STATE_UNANALYZED,
            agent_display_name='agent_display_name_value',
            agent_state=agent_anomaly_detection_service.MonitoredAgent.EnablementState.ACTIVE,
            location='location_value',
            agent_type=agent_anomaly_detection_service.AgentResource.AgentType.REASONING_ENGINE,
        ))
        response = await client.get_analyzed_session(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.GetAnalyzedSessionRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, agent_anomaly_detection_service.AnalyzedSession)
    assert response.name == 'name_value'
    assert response.session_id == 'session_id_value'
    assert response.user_id == 'user_id_value'
    assert response.agent_resource_name == 'agent_resource_name_value'
    assert response.session_state == agent_anomaly_detection_service.AnalyzedSession.SessionState.SESSION_STATE_UNANALYZED
    assert response.agent_display_name == 'agent_display_name_value'
    assert response.agent_state == agent_anomaly_detection_service.MonitoredAgent.EnablementState.ACTIVE
    assert response.location == 'location_value'
    assert response.agent_type == agent_anomaly_detection_service.AgentResource.AgentType.REASONING_ENGINE

def test_get_analyzed_session_field_headers():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.GetAnalyzedSessionRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_analyzed_session),
            '__call__') as call:
        call.return_value = agent_anomaly_detection_service.AnalyzedSession()
        client.get_analyzed_session(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_get_analyzed_session_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.GetAnalyzedSessionRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_analyzed_session),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.AnalyzedSession())
        await client.get_analyzed_session(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


def test_get_analyzed_session_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_analyzed_session),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.AnalyzedSession()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_analyzed_session(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val


def test_get_analyzed_session_flattened_error():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_analyzed_session(
            agent_anomaly_detection_service.GetAnalyzedSessionRequest(),
            name='name_value',
        )

@pytest.mark.asyncio
async def test_get_analyzed_session_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_analyzed_session),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.AnalyzedSession()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.AnalyzedSession())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_analyzed_session(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_get_analyzed_session_flattened_error_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_analyzed_session(
            agent_anomaly_detection_service.GetAnalyzedSessionRequest(),
            name='name_value',
        )


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.ListAnalyzedInvocationsRequest(),
  {},
])
def test_list_analyzed_invocations(request_type, transport: str = 'grpc'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_invocations),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
            next_page_token='next_page_token_value',
        )
        response = client.list_analyzed_invocations(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.ListAnalyzedInvocationsRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListAnalyzedInvocationsPager)
    assert response.next_page_token == 'next_page_token_value'


def test_list_analyzed_invocations_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='grpc',
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = agent_anomaly_detection_service.ListAnalyzedInvocationsRequest(
        parent='parent_value',
        page_token='page_token_value',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_invocations),
            '__call__') as call:
        call.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client.list_analyzed_invocations(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ListAnalyzedInvocationsRequest(
            parent='parent_value',
            page_token='page_token_value',
        )
        assert args[0] == request_msg

def test_list_analyzed_invocations_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.list_analyzed_invocations in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.list_analyzed_invocations] = mock_rpc
        request = {}
        client.list_analyzed_invocations(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_analyzed_invocations(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
async def test_list_analyzed_invocations_async_use_cached_wrapped_rpc(transport: str = "grpc_asyncio"):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._client._transport.list_analyzed_invocations in client._client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[client._client._transport.list_analyzed_invocations] = mock_rpc

        request = {}
        await client.list_analyzed_invocations(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.list_analyzed_invocations(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.ListAnalyzedInvocationsRequest(),
  {},
])
async def test_list_analyzed_invocations_async(request_type, transport: str = 'grpc_asyncio'):
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_invocations),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
            next_page_token='next_page_token_value',
        ))
        response = await client.list_analyzed_invocations(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.ListAnalyzedInvocationsRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListAnalyzedInvocationsAsyncPager)
    assert response.next_page_token == 'next_page_token_value'

def test_list_analyzed_invocations_field_headers():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.ListAnalyzedInvocationsRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_invocations),
            '__call__') as call:
        call.return_value = agent_anomaly_detection_service.ListAnalyzedInvocationsResponse()
        client.list_analyzed_invocations(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_list_analyzed_invocations_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.ListAnalyzedInvocationsRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_invocations),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.ListAnalyzedInvocationsResponse())
        await client.list_analyzed_invocations(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


def test_list_analyzed_invocations_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_invocations),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.ListAnalyzedInvocationsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_analyzed_invocations(
            parent='parent_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val


def test_list_analyzed_invocations_flattened_error():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_analyzed_invocations(
            agent_anomaly_detection_service.ListAnalyzedInvocationsRequest(),
            parent='parent_value',
        )

@pytest.mark.asyncio
async def test_list_analyzed_invocations_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_invocations),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.ListAnalyzedInvocationsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.ListAnalyzedInvocationsResponse())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_analyzed_invocations(
            parent='parent_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_list_analyzed_invocations_flattened_error_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_analyzed_invocations(
            agent_anomaly_detection_service.ListAnalyzedInvocationsRequest(),
            parent='parent_value',
        )


def test_list_analyzed_invocations_pager(transport_name: str = "grpc"):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_invocations),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
                analyzed_invocations=[
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
                analyzed_invocations=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
                analyzed_invocations=[
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
                analyzed_invocations=[
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                ],
            ),
            RuntimeError,
        )

        expected_metadata = ()
        retry = retries.Retry()
        timeout = 5
        expected_metadata = tuple(expected_metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((
                ('parent', ''),
            )),
        )
        pager = client.list_analyzed_invocations(request={}, retry=retry, timeout=timeout)

        assert pager._metadata == expected_metadata
        assert pager._retry == retry
        assert pager._timeout == timeout

        assert pager.next_page_token == 'abc'
        assert str(pager).startswith(f'{pager.__class__.__name__}<')

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, agent_anomaly_detection_service.AnalyzedInvocation)
                   for i in results)
def test_list_analyzed_invocations_pages(transport_name: str = "grpc"):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_invocations),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
                analyzed_invocations=[
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
                analyzed_invocations=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
                analyzed_invocations=[
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
                analyzed_invocations=[
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_analyzed_invocations(request={}).pages)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token

@pytest.mark.asyncio
async def test_list_analyzed_invocations_async_pager():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_invocations),
            '__call__', new_callable=mock.AsyncMock) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
                analyzed_invocations=[
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
                analyzed_invocations=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
                analyzed_invocations=[
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
                analyzed_invocations=[
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_analyzed_invocations(request={},)
        assert async_pager.next_page_token == 'abc'
        assert str(async_pager).startswith(f'{async_pager.__class__.__name__}<')

        responses = []
        async for response in async_pager: # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, agent_anomaly_detection_service.AnalyzedInvocation)
                for i in responses)


@pytest.mark.asyncio
async def test_list_analyzed_invocations_async_pages():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_invocations),
            '__call__', new_callable=mock.AsyncMock) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
                analyzed_invocations=[
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
                analyzed_invocations=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
                analyzed_invocations=[
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
                analyzed_invocations=[
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (
            await client.list_analyzed_invocations(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token

@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.GetAnalyzedInvocationRequest(),
  {},
])
def test_get_analyzed_invocation(request_type, transport: str = 'grpc'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_analyzed_invocation),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.AnalyzedInvocation(
            name='name_value',
            invocation_id='invocation_id_value',
            invocation_state=agent_anomaly_detection_service.AnalyzedInvocation.InvocationState.INVOCATION_STATE_ANOMALOUS,
        )
        response = client.get_analyzed_invocation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.GetAnalyzedInvocationRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, agent_anomaly_detection_service.AnalyzedInvocation)
    assert response.name == 'name_value'
    assert response.invocation_id == 'invocation_id_value'
    assert response.invocation_state == agent_anomaly_detection_service.AnalyzedInvocation.InvocationState.INVOCATION_STATE_ANOMALOUS


def test_get_analyzed_invocation_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='grpc',
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = agent_anomaly_detection_service.GetAnalyzedInvocationRequest(
        name='name_value',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_analyzed_invocation),
            '__call__') as call:
        call.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client.get_analyzed_invocation(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.GetAnalyzedInvocationRequest(
            name='name_value',
        )
        assert args[0] == request_msg

def test_get_analyzed_invocation_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.get_analyzed_invocation in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.get_analyzed_invocation] = mock_rpc
        request = {}
        client.get_analyzed_invocation(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_analyzed_invocation(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
async def test_get_analyzed_invocation_async_use_cached_wrapped_rpc(transport: str = "grpc_asyncio"):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._client._transport.get_analyzed_invocation in client._client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[client._client._transport.get_analyzed_invocation] = mock_rpc

        request = {}
        await client.get_analyzed_invocation(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.get_analyzed_invocation(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.GetAnalyzedInvocationRequest(),
  {},
])
async def test_get_analyzed_invocation_async(request_type, transport: str = 'grpc_asyncio'):
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_analyzed_invocation),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.AnalyzedInvocation(
            name='name_value',
            invocation_id='invocation_id_value',
            invocation_state=agent_anomaly_detection_service.AnalyzedInvocation.InvocationState.INVOCATION_STATE_ANOMALOUS,
        ))
        response = await client.get_analyzed_invocation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.GetAnalyzedInvocationRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, agent_anomaly_detection_service.AnalyzedInvocation)
    assert response.name == 'name_value'
    assert response.invocation_id == 'invocation_id_value'
    assert response.invocation_state == agent_anomaly_detection_service.AnalyzedInvocation.InvocationState.INVOCATION_STATE_ANOMALOUS

def test_get_analyzed_invocation_field_headers():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.GetAnalyzedInvocationRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_analyzed_invocation),
            '__call__') as call:
        call.return_value = agent_anomaly_detection_service.AnalyzedInvocation()
        client.get_analyzed_invocation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_get_analyzed_invocation_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.GetAnalyzedInvocationRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_analyzed_invocation),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.AnalyzedInvocation())
        await client.get_analyzed_invocation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


def test_get_analyzed_invocation_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_analyzed_invocation),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.AnalyzedInvocation()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_analyzed_invocation(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val


def test_get_analyzed_invocation_flattened_error():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_analyzed_invocation(
            agent_anomaly_detection_service.GetAnalyzedInvocationRequest(),
            name='name_value',
        )

@pytest.mark.asyncio
async def test_get_analyzed_invocation_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.get_analyzed_invocation),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.AnalyzedInvocation()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.AnalyzedInvocation())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_analyzed_invocation(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_get_analyzed_invocation_flattened_error_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_analyzed_invocation(
            agent_anomaly_detection_service.GetAnalyzedInvocationRequest(),
            name='name_value',
        )


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest(),
  {},
])
def test_aggregate_analyzed_sessions(request_type, transport: str = 'grpc'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.aggregate_analyzed_sessions),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
            next_page_token='next_page_token_value',
        )
        response = client.aggregate_analyzed_sessions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.AggregateAnalyzedSessionsPager)
    assert response.next_page_token == 'next_page_token_value'


def test_aggregate_analyzed_sessions_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='grpc',
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest(
        parent='parent_value',
        filter='filter_value',
        page_token='page_token_value',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.aggregate_analyzed_sessions),
            '__call__') as call:
        call.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client.aggregate_analyzed_sessions(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest(
            parent='parent_value',
            filter='filter_value',
            page_token='page_token_value',
        )
        assert args[0] == request_msg

def test_aggregate_analyzed_sessions_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.aggregate_analyzed_sessions in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.aggregate_analyzed_sessions] = mock_rpc
        request = {}
        client.aggregate_analyzed_sessions(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.aggregate_analyzed_sessions(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
async def test_aggregate_analyzed_sessions_async_use_cached_wrapped_rpc(transport: str = "grpc_asyncio"):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._client._transport.aggregate_analyzed_sessions in client._client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[client._client._transport.aggregate_analyzed_sessions] = mock_rpc

        request = {}
        await client.aggregate_analyzed_sessions(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.aggregate_analyzed_sessions(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest(),
  {},
])
async def test_aggregate_analyzed_sessions_async(request_type, transport: str = 'grpc_asyncio'):
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.aggregate_analyzed_sessions),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value =grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
            next_page_token='next_page_token_value',
        ))
        response = await client.aggregate_analyzed_sessions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.AggregateAnalyzedSessionsAsyncPager)
    assert response.next_page_token == 'next_page_token_value'

def test_aggregate_analyzed_sessions_field_headers():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.aggregate_analyzed_sessions),
            '__call__') as call:
        call.return_value = agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse()
        client.aggregate_analyzed_sessions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_aggregate_analyzed_sessions_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest()

    request.parent = 'parent_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.aggregate_analyzed_sessions),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse())
        await client.aggregate_analyzed_sessions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent_value',
    ) in kw['metadata']


def test_aggregate_analyzed_sessions_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.aggregate_analyzed_sessions),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.aggregate_analyzed_sessions(
            parent='parent_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val


def test_aggregate_analyzed_sessions_flattened_error():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.aggregate_analyzed_sessions(
            agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest(),
            parent='parent_value',
        )

@pytest.mark.asyncio
async def test_aggregate_analyzed_sessions_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.aggregate_analyzed_sessions),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.aggregate_analyzed_sessions(
            parent='parent_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = 'parent_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_aggregate_analyzed_sessions_flattened_error_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.aggregate_analyzed_sessions(
            agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest(),
            parent='parent_value',
        )


def test_aggregate_analyzed_sessions_pager(transport_name: str = "grpc"):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.aggregate_analyzed_sessions),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
                agent_aggregates=[
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
                agent_aggregates=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
                agent_aggregates=[
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
                agent_aggregates=[
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                ],
            ),
            RuntimeError,
        )

        expected_metadata = ()
        retry = retries.Retry()
        timeout = 5
        expected_metadata = tuple(expected_metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((
                ('parent', ''),
            )),
        )
        pager = client.aggregate_analyzed_sessions(request={}, retry=retry, timeout=timeout)

        assert pager._metadata == expected_metadata
        assert pager._retry == retry
        assert pager._timeout == timeout

        assert pager.next_page_token == 'abc'
        assert str(pager).startswith(f'{pager.__class__.__name__}<')

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate)
                   for i in results)
def test_aggregate_analyzed_sessions_pages(transport_name: str = "grpc"):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.aggregate_analyzed_sessions),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
                agent_aggregates=[
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
                agent_aggregates=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
                agent_aggregates=[
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
                agent_aggregates=[
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.aggregate_analyzed_sessions(request={}).pages)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token

@pytest.mark.asyncio
async def test_aggregate_analyzed_sessions_async_pager():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.aggregate_analyzed_sessions),
            '__call__', new_callable=mock.AsyncMock) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
                agent_aggregates=[
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
                agent_aggregates=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
                agent_aggregates=[
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
                agent_aggregates=[
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.aggregate_analyzed_sessions(request={},)
        assert async_pager.next_page_token == 'abc'
        assert str(async_pager).startswith(f'{async_pager.__class__.__name__}<')

        responses = []
        async for response in async_pager: # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate)
                for i in responses)


@pytest.mark.asyncio
async def test_aggregate_analyzed_sessions_async_pages():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.aggregate_analyzed_sessions),
            '__call__', new_callable=mock.AsyncMock) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
                agent_aggregates=[
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
                agent_aggregates=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
                agent_aggregates=[
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
                agent_aggregates=[
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (
            await client.aggregate_analyzed_sessions(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token

@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.ClearTrainingDataRequest(),
  {},
])
def test_clear_training_data(request_type, transport: str = 'grpc'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.clear_training_data),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/spam')
        response = client.clear_training_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.ClearTrainingDataRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_clear_training_data_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='grpc',
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = agent_anomaly_detection_service.ClearTrainingDataRequest(
        name='name_value',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.clear_training_data),
            '__call__') as call:
        call.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client.clear_training_data(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ClearTrainingDataRequest(
            name='name_value',
        )
        assert args[0] == request_msg

def test_clear_training_data_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.clear_training_data in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.clear_training_data] = mock_rpc
        request = {}
        client.clear_training_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.clear_training_data(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
async def test_clear_training_data_async_use_cached_wrapped_rpc(transport: str = "grpc_asyncio"):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._client._transport.clear_training_data in client._client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[client._client._transport.clear_training_data] = mock_rpc

        request = {}
        await client.clear_training_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.clear_training_data(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.ClearTrainingDataRequest(),
  {},
])
async def test_clear_training_data_async(request_type, transport: str = 'grpc_asyncio'):
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.clear_training_data),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name='operations/spam')
        )
        response = await client.clear_training_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = agent_anomaly_detection_service.ClearTrainingDataRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)

def test_clear_training_data_field_headers():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.ClearTrainingDataRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.clear_training_data),
            '__call__') as call:
        call.return_value = operations_pb2.Operation(name='operations/op')
        client.clear_training_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


@pytest.mark.asyncio
async def test_clear_training_data_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent_anomaly_detection_service.ClearTrainingDataRequest()

    request.name = 'name_value'

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.clear_training_data),
            '__call__') as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(operations_pb2.Operation(name='operations/op'))
        await client.clear_training_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name_value',
    ) in kw['metadata']


def test_clear_training_data_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.clear_training_data),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/op')
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.clear_training_data(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val


def test_clear_training_data_flattened_error():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.clear_training_data(
            agent_anomaly_detection_service.ClearTrainingDataRequest(),
            name='name_value',
        )

@pytest.mark.asyncio
async def test_clear_training_data_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client.transport.clear_training_data),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/op')

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name='operations/spam')
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.clear_training_data(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = 'name_value'
        assert arg == mock_val

@pytest.mark.asyncio
async def test_clear_training_data_flattened_error_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.clear_training_data(
            agent_anomaly_detection_service.ClearTrainingDataRequest(),
            name='name_value',
        )


def test_get_agent_anomaly_detection_scope_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.get_agent_anomaly_detection_scope in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.get_agent_anomaly_detection_scope] = mock_rpc

        request = {}
        client.get_agent_anomaly_detection_scope(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_agent_anomaly_detection_scope(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_get_agent_anomaly_detection_scope_rest_required_fields(request_type=agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest):
    transport_class = transports.AgentAnomalyDetectionServiceRestTransport

    request_init = {}
    request_init["name"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(json_format.MessageToJson(
        pb_request,
        use_integers_for_enums=False
    ))

    # verify fields with default values are dropped

    default_values = getattr(
        transport_class._BaseGetAgentAnomalyDetectionScope,
        "_BaseGetAgentAnomalyDetectionScope__REQUIRED_FIELDS_DEFAULT_VALUES",
        {},
    )
    unset_fields = {k: v for k, v in default_values.items() if k not in jsonified_request}
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = 'name_value'

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == 'name_value'

    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = agent_anomaly_detection_service.AgentAnomalyDetectionScope()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "get",
                'query_params': pb_request,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            # Convert return value to protobuf type
            return_value = agent_anomaly_detection_service.AgentAnomalyDetectionScope.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.get_agent_anomaly_detection_scope(request)

            expected_params = [
                ('$alt', 'json;enum-encoding=int')
            ]
            actual_params = req.call_args.kwargs['params']
            assert sorted(expected_params) == sorted(actual_params)


def test_get_agent_anomaly_detection_scope_rest_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.AgentAnomalyDetectionScope()

        # get arguments that satisfy an http rule for this method
        sample_request = {'name': 'projects/sample1/locations/sample2/agentAnomalyDetectionScopes/sample3'}

        # get truthy value for each flattened field
        mock_args = dict(
            name='name_value',
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.AgentAnomalyDetectionScope.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.get_agent_anomaly_detection_scope(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("%s/v1/{name=projects/*/locations/*/agentAnomalyDetectionScopes/*}" % client.transport._host, args[1])


def test_get_agent_anomaly_detection_scope_rest_flattened_error(transport: str = 'rest'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_agent_anomaly_detection_scope(
            agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest(),
            name='name_value',
        )


def test_get_monitored_agent_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.get_monitored_agent in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.get_monitored_agent] = mock_rpc

        request = {}
        client.get_monitored_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_monitored_agent(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_get_monitored_agent_rest_required_fields(request_type=agent_anomaly_detection_service.GetMonitoredAgentRequest):
    transport_class = transports.AgentAnomalyDetectionServiceRestTransport

    request_init = {}
    request_init["name"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(json_format.MessageToJson(
        pb_request,
        use_integers_for_enums=False
    ))

    # verify fields with default values are dropped

    default_values = getattr(
        transport_class._BaseGetMonitoredAgent,
        "_BaseGetMonitoredAgent__REQUIRED_FIELDS_DEFAULT_VALUES",
        {},
    )
    unset_fields = {k: v for k, v in default_values.items() if k not in jsonified_request}
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = 'name_value'

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == 'name_value'

    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = agent_anomaly_detection_service.MonitoredAgent()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "get",
                'query_params': pb_request,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            # Convert return value to protobuf type
            return_value = agent_anomaly_detection_service.MonitoredAgent.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.get_monitored_agent(request)

            expected_params = [
                ('$alt', 'json;enum-encoding=int')
            ]
            actual_params = req.call_args.kwargs['params']
            assert sorted(expected_params) == sorted(actual_params)


def test_get_monitored_agent_rest_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.MonitoredAgent()

        # get arguments that satisfy an http rule for this method
        sample_request = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}

        # get truthy value for each flattened field
        mock_args = dict(
            name='name_value',
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.MonitoredAgent.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.get_monitored_agent(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("%s/v1/{name=projects/*/locations/*/monitoredAgents/*}" % client.transport._host, args[1])


def test_get_monitored_agent_rest_flattened_error(transport: str = 'rest'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_monitored_agent(
            agent_anomaly_detection_service.GetMonitoredAgentRequest(),
            name='name_value',
        )


def test_list_monitored_agents_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.list_monitored_agents in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.list_monitored_agents] = mock_rpc

        request = {}
        client.list_monitored_agents(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_monitored_agents(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_list_monitored_agents_rest_required_fields(request_type=agent_anomaly_detection_service.ListMonitoredAgentsRequest):
    transport_class = transports.AgentAnomalyDetectionServiceRestTransport

    request_init = {}
    request_init["parent"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(json_format.MessageToJson(
        pb_request,
        use_integers_for_enums=False
    ))

    # verify fields with default values are dropped

    default_values = getattr(
        transport_class._BaseListMonitoredAgents,
        "_BaseListMonitoredAgents__REQUIRED_FIELDS_DEFAULT_VALUES",
        {},
    )
    unset_fields = {k: v for k, v in default_values.items() if k not in jsonified_request}
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = 'parent_value'

    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("filter", "pageSize", "pageToken", ))

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == 'parent_value'

    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = agent_anomaly_detection_service.ListMonitoredAgentsResponse()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "get",
                'query_params': pb_request,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            # Convert return value to protobuf type
            return_value = agent_anomaly_detection_service.ListMonitoredAgentsResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.list_monitored_agents(request)

            expected_params = [
                ('$alt', 'json;enum-encoding=int')
            ]
            actual_params = req.call_args.kwargs['params']
            assert sorted(expected_params) == sorted(actual_params)


def test_list_monitored_agents_rest_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.ListMonitoredAgentsResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {'parent': 'projects/sample1/locations/sample2'}

        # get truthy value for each flattened field
        mock_args = dict(
            parent='parent_value',
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.ListMonitoredAgentsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.list_monitored_agents(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("%s/v1/{parent=projects/*/locations/*}/monitoredAgents" % client.transport._host, args[1])


def test_list_monitored_agents_rest_flattened_error(transport: str = 'rest'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_monitored_agents(
            agent_anomaly_detection_service.ListMonitoredAgentsRequest(),
            parent='parent_value',
        )


def test_list_monitored_agents_rest_pager(transport: str = 'rest'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        #with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            agent_anomaly_detection_service.ListMonitoredAgentsResponse(
                monitored_agents=[
                    agent_anomaly_detection_service.MonitoredAgent(),
                    agent_anomaly_detection_service.MonitoredAgent(),
                    agent_anomaly_detection_service.MonitoredAgent(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.ListMonitoredAgentsResponse(
                monitored_agents=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.ListMonitoredAgentsResponse(
                monitored_agents=[
                    agent_anomaly_detection_service.MonitoredAgent(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.ListMonitoredAgentsResponse(
                monitored_agents=[
                    agent_anomaly_detection_service.MonitoredAgent(),
                    agent_anomaly_detection_service.MonitoredAgent(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(agent_anomaly_detection_service.ListMonitoredAgentsResponse.to_json(x) for x in response)
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode('UTF-8')
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {'parent': 'projects/sample1/locations/sample2'}

        pager = client.list_monitored_agents(request=sample_request)

        assert pager.next_page_token == 'abc'
        assert str(pager).startswith(f'{pager.__class__.__name__}<')

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, agent_anomaly_detection_service.MonitoredAgent)
                for i in results)

        pages = list(client.list_monitored_agents(request=sample_request).pages)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token


def test_enable_monitored_agent_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.enable_monitored_agent in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.enable_monitored_agent] = mock_rpc

        request = {}
        client.enable_monitored_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.enable_monitored_agent(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_enable_monitored_agent_rest_required_fields(request_type=agent_anomaly_detection_service.EnableMonitoredAgentRequest):
    transport_class = transports.AgentAnomalyDetectionServiceRestTransport

    request_init = {}
    request_init["name"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(json_format.MessageToJson(
        pb_request,
        use_integers_for_enums=False
    ))

    # verify fields with default values are dropped

    default_values = getattr(
        transport_class._BaseEnableMonitoredAgent,
        "_BaseEnableMonitoredAgent__REQUIRED_FIELDS_DEFAULT_VALUES",
        {},
    )
    unset_fields = {k: v for k, v in default_values.items() if k not in jsonified_request}
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = 'name_value'

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == 'name_value'

    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = operations_pb2.Operation(name='operations/spam')
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "post",
                'query_params': pb_request,
            }
            transcode_result['body'] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.enable_monitored_agent(request)

            expected_params = [
                ('$alt', 'json;enum-encoding=int')
            ]
            actual_params = req.call_args.kwargs['params']
            assert sorted(expected_params) == sorted(actual_params)


def test_enable_monitored_agent_rest_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name='operations/spam')

        # get arguments that satisfy an http rule for this method
        sample_request = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}

        # get truthy value for each flattened field
        mock_args = dict(
            name='name_value',
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.enable_monitored_agent(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("%s/v1/{name=projects/*/locations/*/monitoredAgents/*}:enable" % client.transport._host, args[1])


def test_enable_monitored_agent_rest_flattened_error(transport: str = 'rest'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.enable_monitored_agent(
            agent_anomaly_detection_service.EnableMonitoredAgentRequest(),
            name='name_value',
        )


def test_disable_monitored_agent_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.disable_monitored_agent in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.disable_monitored_agent] = mock_rpc

        request = {}
        client.disable_monitored_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.disable_monitored_agent(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_disable_monitored_agent_rest_required_fields(request_type=agent_anomaly_detection_service.DisableMonitoredAgentRequest):
    transport_class = transports.AgentAnomalyDetectionServiceRestTransport

    request_init = {}
    request_init["name"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(json_format.MessageToJson(
        pb_request,
        use_integers_for_enums=False
    ))

    # verify fields with default values are dropped

    default_values = getattr(
        transport_class._BaseDisableMonitoredAgent,
        "_BaseDisableMonitoredAgent__REQUIRED_FIELDS_DEFAULT_VALUES",
        {},
    )
    unset_fields = {k: v for k, v in default_values.items() if k not in jsonified_request}
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = 'name_value'

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == 'name_value'

    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = operations_pb2.Operation(name='operations/spam')
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "post",
                'query_params': pb_request,
            }
            transcode_result['body'] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.disable_monitored_agent(request)

            expected_params = [
                ('$alt', 'json;enum-encoding=int')
            ]
            actual_params = req.call_args.kwargs['params']
            assert sorted(expected_params) == sorted(actual_params)


def test_disable_monitored_agent_rest_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name='operations/spam')

        # get arguments that satisfy an http rule for this method
        sample_request = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}

        # get truthy value for each flattened field
        mock_args = dict(
            name='name_value',
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.disable_monitored_agent(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("%s/v1/{name=projects/*/locations/*/monitoredAgents/*}:disable" % client.transport._host, args[1])


def test_disable_monitored_agent_rest_flattened_error(transport: str = 'rest'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.disable_monitored_agent(
            agent_anomaly_detection_service.DisableMonitoredAgentRequest(),
            name='name_value',
        )


def test_delete_agent_anomaly_detection_scope_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.delete_agent_anomaly_detection_scope in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.delete_agent_anomaly_detection_scope] = mock_rpc

        request = {}
        client.delete_agent_anomaly_detection_scope(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.delete_agent_anomaly_detection_scope(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_delete_agent_anomaly_detection_scope_rest_required_fields(request_type=agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest):
    transport_class = transports.AgentAnomalyDetectionServiceRestTransport

    request_init = {}
    request_init["name"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(json_format.MessageToJson(
        pb_request,
        use_integers_for_enums=False
    ))

    # verify fields with default values are dropped

    default_values = getattr(
        transport_class._BaseDeleteAgentAnomalyDetectionScope,
        "_BaseDeleteAgentAnomalyDetectionScope__REQUIRED_FIELDS_DEFAULT_VALUES",
        {},
    )
    unset_fields = {k: v for k, v in default_values.items() if k not in jsonified_request}
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = 'name_value'

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == 'name_value'

    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = operations_pb2.Operation(name='operations/spam')
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "delete",
                'query_params': pb_request,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.delete_agent_anomaly_detection_scope(request)

            expected_params = [
                ('$alt', 'json;enum-encoding=int')
            ]
            actual_params = req.call_args.kwargs['params']
            assert sorted(expected_params) == sorted(actual_params)


def test_delete_agent_anomaly_detection_scope_rest_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name='operations/spam')

        # get arguments that satisfy an http rule for this method
        sample_request = {'name': 'projects/sample1/locations/sample2/agentAnomalyDetectionScopes/sample3'}

        # get truthy value for each flattened field
        mock_args = dict(
            name='name_value',
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.delete_agent_anomaly_detection_scope(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("%s/v1/{name=projects/*/locations/*/agentAnomalyDetectionScopes/*}" % client.transport._host, args[1])


def test_delete_agent_anomaly_detection_scope_rest_flattened_error(transport: str = 'rest'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_agent_anomaly_detection_scope(
            agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest(),
            name='name_value',
        )


def test_create_agent_anomaly_detection_scope_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.create_agent_anomaly_detection_scope in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.create_agent_anomaly_detection_scope] = mock_rpc

        request = {}
        client.create_agent_anomaly_detection_scope(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.create_agent_anomaly_detection_scope(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_create_agent_anomaly_detection_scope_rest_required_fields(request_type=agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest):
    transport_class = transports.AgentAnomalyDetectionServiceRestTransport

    request_init = {}
    request_init["parent"] = ""
    request_init["agent_anomaly_detection_scope_id"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(json_format.MessageToJson(
        pb_request,
        use_integers_for_enums=False
    ))

    # verify fields with default values are dropped
    assert "agentAnomalyDetectionScopeId" not in jsonified_request

    default_values = getattr(
        transport_class._BaseCreateAgentAnomalyDetectionScope,
        "_BaseCreateAgentAnomalyDetectionScope__REQUIRED_FIELDS_DEFAULT_VALUES",
        {},
    )
    unset_fields = {k: v for k, v in default_values.items() if k not in jsonified_request}
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present
    assert "agentAnomalyDetectionScopeId" in jsonified_request
    assert jsonified_request["agentAnomalyDetectionScopeId"] == request_init["agent_anomaly_detection_scope_id"]

    jsonified_request["parent"] = 'parent_value'
    jsonified_request["agentAnomalyDetectionScopeId"] = 'agent_anomaly_detection_scope_id_value'

    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("agentAnomalyDetectionScopeId", ))

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == 'parent_value'
    assert "agentAnomalyDetectionScopeId" in jsonified_request
    assert jsonified_request["agentAnomalyDetectionScopeId"] == 'agent_anomaly_detection_scope_id_value'

    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = operations_pb2.Operation(name='operations/spam')
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "post",
                'query_params': pb_request,
            }
            transcode_result['body'] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.create_agent_anomaly_detection_scope(request)

            expected_params = [
                (
                    "agentAnomalyDetectionScopeId",
                    "",
                ),
                ('$alt', 'json;enum-encoding=int')
            ]
            actual_params = req.call_args.kwargs['params']
            assert sorted(expected_params) == sorted(actual_params)


def test_create_agent_anomaly_detection_scope_rest_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name='operations/spam')

        # get arguments that satisfy an http rule for this method
        sample_request = {'parent': 'projects/sample1/locations/sample2'}

        # get truthy value for each flattened field
        mock_args = dict(
            parent='parent_value',
            agent_anomaly_detection_scope=agent_anomaly_detection_service.AgentAnomalyDetectionScope(name='name_value'),
            agent_anomaly_detection_scope_id='agent_anomaly_detection_scope_id_value',
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.create_agent_anomaly_detection_scope(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("%s/v1/{parent=projects/*/locations/*}/agentAnomalyDetectionScopes" % client.transport._host, args[1])


def test_create_agent_anomaly_detection_scope_rest_flattened_error(transport: str = 'rest'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_agent_anomaly_detection_scope(
            agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest(),
            parent='parent_value',
            agent_anomaly_detection_scope=agent_anomaly_detection_service.AgentAnomalyDetectionScope(name='name_value'),
            agent_anomaly_detection_scope_id='agent_anomaly_detection_scope_id_value',
        )


def test_list_agent_anomaly_detection_scopes_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.list_agent_anomaly_detection_scopes in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.list_agent_anomaly_detection_scopes] = mock_rpc

        request = {}
        client.list_agent_anomaly_detection_scopes(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_agent_anomaly_detection_scopes(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_list_agent_anomaly_detection_scopes_rest_required_fields(request_type=agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest):
    transport_class = transports.AgentAnomalyDetectionServiceRestTransport

    request_init = {}
    request_init["parent"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(json_format.MessageToJson(
        pb_request,
        use_integers_for_enums=False
    ))

    # verify fields with default values are dropped

    default_values = getattr(
        transport_class._BaseListAgentAnomalyDetectionScopes,
        "_BaseListAgentAnomalyDetectionScopes__REQUIRED_FIELDS_DEFAULT_VALUES",
        {},
    )
    unset_fields = {k: v for k, v in default_values.items() if k not in jsonified_request}
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = 'parent_value'

    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("pageSize", "pageToken", ))

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == 'parent_value'

    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "get",
                'query_params': pb_request,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            # Convert return value to protobuf type
            return_value = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.list_agent_anomaly_detection_scopes(request)

            expected_params = [
                ('$alt', 'json;enum-encoding=int')
            ]
            actual_params = req.call_args.kwargs['params']
            assert sorted(expected_params) == sorted(actual_params)


def test_list_agent_anomaly_detection_scopes_rest_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {'parent': 'projects/sample1/locations/sample2'}

        # get truthy value for each flattened field
        mock_args = dict(
            parent='parent_value',
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.list_agent_anomaly_detection_scopes(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("%s/v1/{parent=projects/*/locations/*}/agentAnomalyDetectionScopes" % client.transport._host, args[1])


def test_list_agent_anomaly_detection_scopes_rest_flattened_error(transport: str = 'rest'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_agent_anomaly_detection_scopes(
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest(),
            parent='parent_value',
        )


def test_list_agent_anomaly_detection_scopes_rest_pager(transport: str = 'rest'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        #with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
                agent_anomaly_detection_scopes=[
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
                agent_anomaly_detection_scopes=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
                agent_anomaly_detection_scopes=[
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
                agent_anomaly_detection_scopes=[
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                    agent_anomaly_detection_service.AgentAnomalyDetectionScope(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse.to_json(x) for x in response)
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode('UTF-8')
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {'parent': 'projects/sample1/locations/sample2'}

        pager = client.list_agent_anomaly_detection_scopes(request=sample_request)

        assert pager.next_page_token == 'abc'
        assert str(pager).startswith(f'{pager.__class__.__name__}<')

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, agent_anomaly_detection_service.AgentAnomalyDetectionScope)
                for i in results)

        pages = list(client.list_agent_anomaly_detection_scopes(request=sample_request).pages)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token


def test_list_analyzed_sessions_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.list_analyzed_sessions in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.list_analyzed_sessions] = mock_rpc

        request = {}
        client.list_analyzed_sessions(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_analyzed_sessions(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_list_analyzed_sessions_rest_required_fields(request_type=agent_anomaly_detection_service.ListAnalyzedSessionsRequest):
    transport_class = transports.AgentAnomalyDetectionServiceRestTransport

    request_init = {}
    request_init["parent"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(json_format.MessageToJson(
        pb_request,
        use_integers_for_enums=False
    ))

    # verify fields with default values are dropped

    default_values = getattr(
        transport_class._BaseListAnalyzedSessions,
        "_BaseListAnalyzedSessions__REQUIRED_FIELDS_DEFAULT_VALUES",
        {},
    )
    unset_fields = {k: v for k, v in default_values.items() if k not in jsonified_request}
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = 'parent_value'

    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("filter", "orderBy", "pageSize", "pageToken", "view", ))

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == 'parent_value'

    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = agent_anomaly_detection_service.ListAnalyzedSessionsResponse()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "get",
                'query_params': pb_request,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            # Convert return value to protobuf type
            return_value = agent_anomaly_detection_service.ListAnalyzedSessionsResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.list_analyzed_sessions(request)

            expected_params = [
                ('$alt', 'json;enum-encoding=int')
            ]
            actual_params = req.call_args.kwargs['params']
            assert sorted(expected_params) == sorted(actual_params)


def test_list_analyzed_sessions_rest_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.ListAnalyzedSessionsResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {'parent': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}

        # get truthy value for each flattened field
        mock_args = dict(
            parent='parent_value',
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.ListAnalyzedSessionsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.list_analyzed_sessions(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("%s/v1/{parent=projects/*/locations/*/monitoredAgents/*}/analyzedSessions" % client.transport._host, args[1])


def test_list_analyzed_sessions_rest_flattened_error(transport: str = 'rest'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_analyzed_sessions(
            agent_anomaly_detection_service.ListAnalyzedSessionsRequest(),
            parent='parent_value',
        )


def test_list_analyzed_sessions_rest_pager(transport: str = 'rest'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        #with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
                analyzed_sessions=[
                    agent_anomaly_detection_service.AnalyzedSession(),
                    agent_anomaly_detection_service.AnalyzedSession(),
                    agent_anomaly_detection_service.AnalyzedSession(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
                analyzed_sessions=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
                analyzed_sessions=[
                    agent_anomaly_detection_service.AnalyzedSession(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
                analyzed_sessions=[
                    agent_anomaly_detection_service.AnalyzedSession(),
                    agent_anomaly_detection_service.AnalyzedSession(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(agent_anomaly_detection_service.ListAnalyzedSessionsResponse.to_json(x) for x in response)
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode('UTF-8')
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {'parent': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}

        pager = client.list_analyzed_sessions(request=sample_request)

        assert pager.next_page_token == 'abc'
        assert str(pager).startswith(f'{pager.__class__.__name__}<')

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, agent_anomaly_detection_service.AnalyzedSession)
                for i in results)

        pages = list(client.list_analyzed_sessions(request=sample_request).pages)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token


def test_get_analyzed_session_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.get_analyzed_session in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.get_analyzed_session] = mock_rpc

        request = {}
        client.get_analyzed_session(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_analyzed_session(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_get_analyzed_session_rest_required_fields(request_type=agent_anomaly_detection_service.GetAnalyzedSessionRequest):
    transport_class = transports.AgentAnomalyDetectionServiceRestTransport

    request_init = {}
    request_init["name"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(json_format.MessageToJson(
        pb_request,
        use_integers_for_enums=False
    ))

    # verify fields with default values are dropped

    default_values = getattr(
        transport_class._BaseGetAnalyzedSession,
        "_BaseGetAnalyzedSession__REQUIRED_FIELDS_DEFAULT_VALUES",
        {},
    )
    unset_fields = {k: v for k, v in default_values.items() if k not in jsonified_request}
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = 'name_value'

    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("view", ))

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == 'name_value'

    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = agent_anomaly_detection_service.AnalyzedSession()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "get",
                'query_params': pb_request,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            # Convert return value to protobuf type
            return_value = agent_anomaly_detection_service.AnalyzedSession.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.get_analyzed_session(request)

            expected_params = [
                ('$alt', 'json;enum-encoding=int')
            ]
            actual_params = req.call_args.kwargs['params']
            assert sorted(expected_params) == sorted(actual_params)


def test_get_analyzed_session_rest_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.AnalyzedSession()

        # get arguments that satisfy an http rule for this method
        sample_request = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3/analyzedSessions/sample4'}

        # get truthy value for each flattened field
        mock_args = dict(
            name='name_value',
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.AnalyzedSession.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.get_analyzed_session(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("%s/v1/{name=projects/*/locations/*/monitoredAgents/*/analyzedSessions/*}" % client.transport._host, args[1])


def test_get_analyzed_session_rest_flattened_error(transport: str = 'rest'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_analyzed_session(
            agent_anomaly_detection_service.GetAnalyzedSessionRequest(),
            name='name_value',
        )


def test_list_analyzed_invocations_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.list_analyzed_invocations in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.list_analyzed_invocations] = mock_rpc

        request = {}
        client.list_analyzed_invocations(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_analyzed_invocations(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_list_analyzed_invocations_rest_required_fields(request_type=agent_anomaly_detection_service.ListAnalyzedInvocationsRequest):
    transport_class = transports.AgentAnomalyDetectionServiceRestTransport

    request_init = {}
    request_init["parent"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(json_format.MessageToJson(
        pb_request,
        use_integers_for_enums=False
    ))

    # verify fields with default values are dropped

    default_values = getattr(
        transport_class._BaseListAnalyzedInvocations,
        "_BaseListAnalyzedInvocations__REQUIRED_FIELDS_DEFAULT_VALUES",
        {},
    )
    unset_fields = {k: v for k, v in default_values.items() if k not in jsonified_request}
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = 'parent_value'

    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("pageSize", "pageToken", ))

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == 'parent_value'

    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = agent_anomaly_detection_service.ListAnalyzedInvocationsResponse()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "get",
                'query_params': pb_request,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            # Convert return value to protobuf type
            return_value = agent_anomaly_detection_service.ListAnalyzedInvocationsResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.list_analyzed_invocations(request)

            expected_params = [
                ('$alt', 'json;enum-encoding=int')
            ]
            actual_params = req.call_args.kwargs['params']
            assert sorted(expected_params) == sorted(actual_params)


def test_list_analyzed_invocations_rest_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.ListAnalyzedInvocationsResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {'parent': 'projects/sample1/locations/sample2/monitoredAgents/sample3/analyzedSessions/sample4'}

        # get truthy value for each flattened field
        mock_args = dict(
            parent='parent_value',
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.ListAnalyzedInvocationsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.list_analyzed_invocations(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("%s/v1/{parent=projects/*/locations/*/monitoredAgents/*/analyzedSessions/*}/analyzedInvocations" % client.transport._host, args[1])


def test_list_analyzed_invocations_rest_flattened_error(transport: str = 'rest'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_analyzed_invocations(
            agent_anomaly_detection_service.ListAnalyzedInvocationsRequest(),
            parent='parent_value',
        )


def test_list_analyzed_invocations_rest_pager(transport: str = 'rest'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        #with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
                analyzed_invocations=[
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
                analyzed_invocations=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
                analyzed_invocations=[
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
                analyzed_invocations=[
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                    agent_anomaly_detection_service.AnalyzedInvocation(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(agent_anomaly_detection_service.ListAnalyzedInvocationsResponse.to_json(x) for x in response)
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode('UTF-8')
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {'parent': 'projects/sample1/locations/sample2/monitoredAgents/sample3/analyzedSessions/sample4'}

        pager = client.list_analyzed_invocations(request=sample_request)

        assert pager.next_page_token == 'abc'
        assert str(pager).startswith(f'{pager.__class__.__name__}<')

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, agent_anomaly_detection_service.AnalyzedInvocation)
                for i in results)

        pages = list(client.list_analyzed_invocations(request=sample_request).pages)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token


def test_get_analyzed_invocation_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.get_analyzed_invocation in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.get_analyzed_invocation] = mock_rpc

        request = {}
        client.get_analyzed_invocation(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_analyzed_invocation(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_get_analyzed_invocation_rest_required_fields(request_type=agent_anomaly_detection_service.GetAnalyzedInvocationRequest):
    transport_class = transports.AgentAnomalyDetectionServiceRestTransport

    request_init = {}
    request_init["name"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(json_format.MessageToJson(
        pb_request,
        use_integers_for_enums=False
    ))

    # verify fields with default values are dropped

    default_values = getattr(
        transport_class._BaseGetAnalyzedInvocation,
        "_BaseGetAnalyzedInvocation__REQUIRED_FIELDS_DEFAULT_VALUES",
        {},
    )
    unset_fields = {k: v for k, v in default_values.items() if k not in jsonified_request}
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = 'name_value'

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == 'name_value'

    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = agent_anomaly_detection_service.AnalyzedInvocation()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "get",
                'query_params': pb_request,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            # Convert return value to protobuf type
            return_value = agent_anomaly_detection_service.AnalyzedInvocation.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.get_analyzed_invocation(request)

            expected_params = [
                ('$alt', 'json;enum-encoding=int')
            ]
            actual_params = req.call_args.kwargs['params']
            assert sorted(expected_params) == sorted(actual_params)


def test_get_analyzed_invocation_rest_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.AnalyzedInvocation()

        # get arguments that satisfy an http rule for this method
        sample_request = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3/analyzedSessions/sample4/analyzedInvocations/sample5'}

        # get truthy value for each flattened field
        mock_args = dict(
            name='name_value',
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.AnalyzedInvocation.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.get_analyzed_invocation(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("%s/v1/{name=projects/*/locations/*/monitoredAgents/*/analyzedSessions/*/analyzedInvocations/*}" % client.transport._host, args[1])


def test_get_analyzed_invocation_rest_flattened_error(transport: str = 'rest'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_analyzed_invocation(
            agent_anomaly_detection_service.GetAnalyzedInvocationRequest(),
            name='name_value',
        )


def test_aggregate_analyzed_sessions_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.aggregate_analyzed_sessions in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.aggregate_analyzed_sessions] = mock_rpc

        request = {}
        client.aggregate_analyzed_sessions(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.aggregate_analyzed_sessions(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_aggregate_analyzed_sessions_rest_required_fields(request_type=agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest):
    transport_class = transports.AgentAnomalyDetectionServiceRestTransport

    request_init = {}
    request_init["parent"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(json_format.MessageToJson(
        pb_request,
        use_integers_for_enums=False
    ))

    # verify fields with default values are dropped

    default_values = getattr(
        transport_class._BaseAggregateAnalyzedSessions,
        "_BaseAggregateAnalyzedSessions__REQUIRED_FIELDS_DEFAULT_VALUES",
        {},
    )
    unset_fields = {k: v for k, v in default_values.items() if k not in jsonified_request}
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = 'parent_value'

    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("filter", "pageSize", "pageToken", ))

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == 'parent_value'

    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "get",
                'query_params': pb_request,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            # Convert return value to protobuf type
            return_value = agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.aggregate_analyzed_sessions(request)

            expected_params = [
                ('$alt', 'json;enum-encoding=int')
            ]
            actual_params = req.call_args.kwargs['params']
            assert sorted(expected_params) == sorted(actual_params)


def test_aggregate_analyzed_sessions_rest_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {'parent': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}

        # get truthy value for each flattened field
        mock_args = dict(
            parent='parent_value',
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.aggregate_analyzed_sessions(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("%s/v1/{parent=projects/*/locations/*/monitoredAgents/*}/analyzedSessions:aggregate" % client.transport._host, args[1])


def test_aggregate_analyzed_sessions_rest_flattened_error(transport: str = 'rest'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.aggregate_analyzed_sessions(
            agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest(),
            parent='parent_value',
        )


def test_aggregate_analyzed_sessions_rest_pager(transport: str = 'rest'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        #with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
                agent_aggregates=[
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                ],
                next_page_token='abc',
            ),
            agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
                agent_aggregates=[],
                next_page_token='def',
            ),
            agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
                agent_aggregates=[
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                ],
                next_page_token='ghi',
            ),
            agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
                agent_aggregates=[
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                    agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.to_json(x) for x in response)
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode('UTF-8')
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {'parent': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}

        pager = client.aggregate_analyzed_sessions(request=sample_request)

        assert pager.next_page_token == 'abc'
        assert str(pager).startswith(f'{pager.__class__.__name__}<')

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate)
                for i in results)

        pages = list(client.aggregate_analyzed_sessions(request=sample_request).pages)
        for page_, token in zip(pages, ['abc','def','ghi', '']):
            assert page_.raw_page.next_page_token == token


def test_clear_training_data_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.clear_training_data in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = "foo" # operation_request.operation in compute client(s) expect a string.
        client._transport._wrapped_methods[client._transport.clear_training_data] = mock_rpc

        request = {}
        client.clear_training_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.clear_training_data(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_clear_training_data_rest_required_fields(request_type=agent_anomaly_detection_service.ClearTrainingDataRequest):
    transport_class = transports.AgentAnomalyDetectionServiceRestTransport

    request_init = {}
    request_init["name"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(json_format.MessageToJson(
        pb_request,
        use_integers_for_enums=False
    ))

    # verify fields with default values are dropped

    default_values = getattr(
        transport_class._BaseClearTrainingData,
        "_BaseClearTrainingData__REQUIRED_FIELDS_DEFAULT_VALUES",
        {},
    )
    unset_fields = {k: v for k, v in default_values.items() if k not in jsonified_request}
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = 'name_value'

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == 'name_value'

    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport='rest',
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = operations_pb2.Operation(name='operations/spam')
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, 'transcode') as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                'uri': 'v1/sample_method',
                'method': "post",
                'query_params': pb_request,
            }
            transcode_result['body'] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode('UTF-8')
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.clear_training_data(request)

            expected_params = [
                ('$alt', 'json;enum-encoding=int')
            ]
            actual_params = req.call_args.kwargs['params']
            assert sorted(expected_params) == sorted(actual_params)


def test_clear_training_data_rest_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name='operations/spam')

        # get arguments that satisfy an http rule for this method
        sample_request = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}

        # get truthy value for each flattened field
        mock_args = dict(
            name='name_value',
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.clear_training_data(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate("%s/v1/{name=projects/*/locations/*/monitoredAgents/*}:clearTrainingData" % client.transport._host, args[1])


def test_clear_training_data_rest_flattened_error(transport: str = 'rest'):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.clear_training_data(
            agent_anomaly_detection_service.ClearTrainingDataRequest(),
            name='name_value',
        )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.AgentAnomalyDetectionServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.AgentAnomalyDetectionServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = AgentAnomalyDetectionServiceClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide an api_key and a transport instance.
    transport = transports.AgentAnomalyDetectionServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    options = client_options.ClientOptions()
    options.api_key = "api_key"
    with pytest.raises(ValueError):
        client = AgentAnomalyDetectionServiceClient(
            client_options=options,
            transport=transport,
        )

    # It is an error to provide an api_key and a credential.
    options = client_options.ClientOptions()
    options.api_key = "api_key"
    with pytest.raises(ValueError):
        client = AgentAnomalyDetectionServiceClient(
            client_options=options,
            credentials=ga_credentials.AnonymousCredentials()
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.AgentAnomalyDetectionServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = AgentAnomalyDetectionServiceClient(
            client_options={"scopes": ["1", "2"]},
            transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.AgentAnomalyDetectionServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    client = AgentAnomalyDetectionServiceClient(transport=transport)
    assert client.transport is transport

def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.AgentAnomalyDetectionServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.AgentAnomalyDetectionServiceGrpcAsyncIOTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

@pytest.mark.parametrize("transport_class", [
    transports.AgentAnomalyDetectionServiceGrpcTransport,
    transports.AgentAnomalyDetectionServiceGrpcAsyncIOTransport,
    transports.AgentAnomalyDetectionServiceRestTransport,
])
def test_transport_adc(transport_class):
    # Test default credentials are used if not provided.
    with mock.patch.object(google.auth, 'default') as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport_class()
        adc.assert_called_once()

def test_transport_kind_grpc():
    transport = AgentAnomalyDetectionServiceClient.get_transport_class("grpc")(
        credentials=ga_credentials.AnonymousCredentials()
    )
    assert transport.kind == "grpc"


def test_initialize_client_w_grpc():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc"
    )
    assert client is not None


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_agent_anomaly_detection_scope_empty_call_grpc():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.get_agent_anomaly_detection_scope),
            '__call__') as call:
        call.return_value = agent_anomaly_detection_service.AgentAnomalyDetectionScope()
        client.get_agent_anomaly_detection_scope(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_monitored_agent_empty_call_grpc():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.get_monitored_agent),
            '__call__') as call:
        call.return_value = agent_anomaly_detection_service.MonitoredAgent()
        client.get_monitored_agent(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.GetMonitoredAgentRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_monitored_agents_empty_call_grpc():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.list_monitored_agents),
            '__call__') as call:
        call.return_value = agent_anomaly_detection_service.ListMonitoredAgentsResponse()
        client.list_monitored_agents(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ListMonitoredAgentsRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_enable_monitored_agent_empty_call_grpc():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.enable_monitored_agent),
            '__call__') as call:
        call.return_value = operations_pb2.Operation(name='operations/op')
        client.enable_monitored_agent(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.EnableMonitoredAgentRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_disable_monitored_agent_empty_call_grpc():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.disable_monitored_agent),
            '__call__') as call:
        call.return_value = operations_pb2.Operation(name='operations/op')
        client.disable_monitored_agent(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.DisableMonitoredAgentRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_delete_agent_anomaly_detection_scope_empty_call_grpc():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_agent_anomaly_detection_scope),
            '__call__') as call:
        call.return_value = operations_pb2.Operation(name='operations/op')
        client.delete_agent_anomaly_detection_scope(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_create_agent_anomaly_detection_scope_empty_call_grpc():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.create_agent_anomaly_detection_scope),
            '__call__') as call:
        call.return_value = operations_pb2.Operation(name='operations/op')
        client.create_agent_anomaly_detection_scope(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_agent_anomaly_detection_scopes_empty_call_grpc():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.list_agent_anomaly_detection_scopes),
            '__call__') as call:
        call.return_value = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse()
        client.list_agent_anomaly_detection_scopes(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_analyzed_sessions_empty_call_grpc():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_sessions),
            '__call__') as call:
        call.return_value = agent_anomaly_detection_service.ListAnalyzedSessionsResponse()
        client.list_analyzed_sessions(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ListAnalyzedSessionsRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_analyzed_session_empty_call_grpc():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.get_analyzed_session),
            '__call__') as call:
        call.return_value = agent_anomaly_detection_service.AnalyzedSession()
        client.get_analyzed_session(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.GetAnalyzedSessionRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_analyzed_invocations_empty_call_grpc():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_invocations),
            '__call__') as call:
        call.return_value = agent_anomaly_detection_service.ListAnalyzedInvocationsResponse()
        client.list_analyzed_invocations(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ListAnalyzedInvocationsRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_analyzed_invocation_empty_call_grpc():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.get_analyzed_invocation),
            '__call__') as call:
        call.return_value = agent_anomaly_detection_service.AnalyzedInvocation()
        client.get_analyzed_invocation(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.GetAnalyzedInvocationRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_aggregate_analyzed_sessions_empty_call_grpc():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.aggregate_analyzed_sessions),
            '__call__') as call:
        call.return_value = agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse()
        client.aggregate_analyzed_sessions(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_clear_training_data_empty_call_grpc():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.clear_training_data),
            '__call__') as call:
        call.return_value = operations_pb2.Operation(name='operations/op')
        client.clear_training_data(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ClearTrainingDataRequest()
        assert args[0] == request_msg


def test_transport_kind_grpc_asyncio():
    transport = AgentAnomalyDetectionServiceAsyncClient.get_transport_class("grpc_asyncio")(
        credentials=async_anonymous_credentials()
    )
    assert transport.kind == "grpc_asyncio"


def test_initialize_client_w_grpc_asyncio():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio"
    )
    assert client is not None


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_agent_anomaly_detection_scope_empty_call_grpc_asyncio():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.get_agent_anomaly_detection_scope),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.AgentAnomalyDetectionScope(
            name='name_value',
            display_name='display_name_value',
            log_buckets=['log_buckets_value'],
            observability_buckets=['observability_buckets_value'],
            auto_enroll=True,
            state=agent_anomaly_detection_service.AgentAnomalyDetectionScope.State.CREATING,
        ))
        await client.get_agent_anomaly_detection_scope(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_monitored_agent_empty_call_grpc_asyncio():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.get_monitored_agent),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.MonitoredAgent(
            name='name_value',
            display_name='display_name_value',
            state=agent_anomaly_detection_service.MonitoredAgent.EnablementState.ACTIVE,
            status_message='status_message_value',
        ))
        await client.get_monitored_agent(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.GetMonitoredAgentRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_monitored_agents_empty_call_grpc_asyncio():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.list_monitored_agents),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.ListMonitoredAgentsResponse(
            next_page_token='next_page_token_value',
            total_size=1086,
        ))
        await client.list_monitored_agents(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ListMonitoredAgentsRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_enable_monitored_agent_empty_call_grpc_asyncio():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.enable_monitored_agent),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name='operations/spam')
        )
        await client.enable_monitored_agent(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.EnableMonitoredAgentRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_disable_monitored_agent_empty_call_grpc_asyncio():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.disable_monitored_agent),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name='operations/spam')
        )
        await client.disable_monitored_agent(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.DisableMonitoredAgentRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_delete_agent_anomaly_detection_scope_empty_call_grpc_asyncio():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_agent_anomaly_detection_scope),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name='operations/spam')
        )
        await client.delete_agent_anomaly_detection_scope(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_create_agent_anomaly_detection_scope_empty_call_grpc_asyncio():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.create_agent_anomaly_detection_scope),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name='operations/spam')
        )
        await client.create_agent_anomaly_detection_scope(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_agent_anomaly_detection_scopes_empty_call_grpc_asyncio():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.list_agent_anomaly_detection_scopes),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
            next_page_token='next_page_token_value',
        ))
        await client.list_agent_anomaly_detection_scopes(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_analyzed_sessions_empty_call_grpc_asyncio():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_sessions),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
            next_page_token='next_page_token_value',
        ))
        await client.list_analyzed_sessions(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ListAnalyzedSessionsRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_analyzed_session_empty_call_grpc_asyncio():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.get_analyzed_session),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.AnalyzedSession(
            name='name_value',
            session_id='session_id_value',
            user_id='user_id_value',
            agent_resource_name='agent_resource_name_value',
            session_state=agent_anomaly_detection_service.AnalyzedSession.SessionState.SESSION_STATE_UNANALYZED,
            agent_display_name='agent_display_name_value',
            agent_state=agent_anomaly_detection_service.MonitoredAgent.EnablementState.ACTIVE,
            location='location_value',
            agent_type=agent_anomaly_detection_service.AgentResource.AgentType.REASONING_ENGINE,
        ))
        await client.get_analyzed_session(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.GetAnalyzedSessionRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_analyzed_invocations_empty_call_grpc_asyncio():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_invocations),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
            next_page_token='next_page_token_value',
        ))
        await client.list_analyzed_invocations(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ListAnalyzedInvocationsRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_analyzed_invocation_empty_call_grpc_asyncio():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.get_analyzed_invocation),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.AnalyzedInvocation(
            name='name_value',
            invocation_id='invocation_id_value',
            invocation_state=agent_anomaly_detection_service.AnalyzedInvocation.InvocationState.INVOCATION_STATE_ANOMALOUS,
        ))
        await client.get_analyzed_invocation(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.GetAnalyzedInvocationRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_aggregate_analyzed_sessions_empty_call_grpc_asyncio():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.aggregate_analyzed_sessions),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
            next_page_token='next_page_token_value',
        ))
        await client.aggregate_analyzed_sessions(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_clear_training_data_empty_call_grpc_asyncio():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.clear_training_data),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name='operations/spam')
        )
        await client.clear_training_data(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ClearTrainingDataRequest()
        assert args[0] == request_msg


def test_transport_kind_rest():
    transport = AgentAnomalyDetectionServiceClient.get_transport_class("rest")(
        credentials=ga_credentials.AnonymousCredentials()
    )
    assert transport.kind == "rest"


def test_get_agent_anomaly_detection_scope_rest_bad_request(request_type=agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/agentAnomalyDetectionScopes/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.get_agent_anomaly_detection_scope(request)


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest,
  dict,
])
def test_get_agent_anomaly_detection_scope_rest_call_success(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/agentAnomalyDetectionScopes/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.AgentAnomalyDetectionScope(
              name='name_value',
              display_name='display_name_value',
              log_buckets=['log_buckets_value'],
              observability_buckets=['observability_buckets_value'],
              auto_enroll=True,
              state=agent_anomaly_detection_service.AgentAnomalyDetectionScope.State.CREATING,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.AgentAnomalyDetectionScope.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.get_agent_anomaly_detection_scope(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, agent_anomaly_detection_service.AgentAnomalyDetectionScope)
    assert response.name == 'name_value'
    assert response.display_name == 'display_name_value'
    assert response.log_buckets == ['log_buckets_value']
    assert response.observability_buckets == ['observability_buckets_value']
    assert response.auto_enroll is True
    assert response.state == agent_anomaly_detection_service.AgentAnomalyDetectionScope.State.CREATING


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_agent_anomaly_detection_scope_rest_interceptors(null_interceptor):
    transport = transports.AgentAnomalyDetectionServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.AgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_get_agent_anomaly_detection_scope") as post, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_get_agent_anomaly_detection_scope_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "pre_get_agent_anomaly_detection_scope") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest.pb(agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = agent_anomaly_detection_service.AgentAnomalyDetectionScope.to_json(agent_anomaly_detection_service.AgentAnomalyDetectionScope())
        req.return_value.content = return_value

        request = agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = agent_anomaly_detection_service.AgentAnomalyDetectionScope()
        post_with_metadata.return_value = agent_anomaly_detection_service.AgentAnomalyDetectionScope(), metadata

        client.get_agent_anomaly_detection_scope(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_get_monitored_agent_rest_bad_request(request_type=agent_anomaly_detection_service.GetMonitoredAgentRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.get_monitored_agent(request)


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.GetMonitoredAgentRequest,
  dict,
])
def test_get_monitored_agent_rest_call_success(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.MonitoredAgent(
              name='name_value',
              display_name='display_name_value',
              state=agent_anomaly_detection_service.MonitoredAgent.EnablementState.ACTIVE,
              status_message='status_message_value',
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.MonitoredAgent.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.get_monitored_agent(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, agent_anomaly_detection_service.MonitoredAgent)
    assert response.name == 'name_value'
    assert response.display_name == 'display_name_value'
    assert response.state == agent_anomaly_detection_service.MonitoredAgent.EnablementState.ACTIVE
    assert response.status_message == 'status_message_value'


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_monitored_agent_rest_interceptors(null_interceptor):
    transport = transports.AgentAnomalyDetectionServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.AgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_get_monitored_agent") as post, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_get_monitored_agent_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "pre_get_monitored_agent") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.GetMonitoredAgentRequest.pb(agent_anomaly_detection_service.GetMonitoredAgentRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = agent_anomaly_detection_service.MonitoredAgent.to_json(agent_anomaly_detection_service.MonitoredAgent())
        req.return_value.content = return_value

        request = agent_anomaly_detection_service.GetMonitoredAgentRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = agent_anomaly_detection_service.MonitoredAgent()
        post_with_metadata.return_value = agent_anomaly_detection_service.MonitoredAgent(), metadata

        client.get_monitored_agent(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_list_monitored_agents_rest_bad_request(request_type=agent_anomaly_detection_service.ListMonitoredAgentsRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.list_monitored_agents(request)


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.ListMonitoredAgentsRequest,
  dict,
])
def test_list_monitored_agents_rest_call_success(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.ListMonitoredAgentsResponse(
              next_page_token='next_page_token_value',
              total_size=1086,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.ListMonitoredAgentsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.list_monitored_agents(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListMonitoredAgentsPager)
    assert response.next_page_token == 'next_page_token_value'
    assert response.total_size == 1086


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_monitored_agents_rest_interceptors(null_interceptor):
    transport = transports.AgentAnomalyDetectionServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.AgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_list_monitored_agents") as post, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_list_monitored_agents_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "pre_list_monitored_agents") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.ListMonitoredAgentsRequest.pb(agent_anomaly_detection_service.ListMonitoredAgentsRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = agent_anomaly_detection_service.ListMonitoredAgentsResponse.to_json(agent_anomaly_detection_service.ListMonitoredAgentsResponse())
        req.return_value.content = return_value

        request = agent_anomaly_detection_service.ListMonitoredAgentsRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = agent_anomaly_detection_service.ListMonitoredAgentsResponse()
        post_with_metadata.return_value = agent_anomaly_detection_service.ListMonitoredAgentsResponse(), metadata

        client.list_monitored_agents(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_enable_monitored_agent_rest_bad_request(request_type=agent_anomaly_detection_service.EnableMonitoredAgentRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.enable_monitored_agent(request)


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.EnableMonitoredAgentRequest,
  dict,
])
def test_enable_monitored_agent_rest_call_success(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name='operations/spam')

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.enable_monitored_agent(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_enable_monitored_agent_rest_interceptors(null_interceptor):
    transport = transports.AgentAnomalyDetectionServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.AgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(operation.Operation, "_set_result_from_operation"), \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_enable_monitored_agent") as post, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_enable_monitored_agent_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "pre_enable_monitored_agent") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.EnableMonitoredAgentRequest.pb(agent_anomaly_detection_service.EnableMonitoredAgentRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = json_format.MessageToJson(operations_pb2.Operation())
        req.return_value.content = return_value

        request = agent_anomaly_detection_service.EnableMonitoredAgentRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.enable_monitored_agent(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_disable_monitored_agent_rest_bad_request(request_type=agent_anomaly_detection_service.DisableMonitoredAgentRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.disable_monitored_agent(request)


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.DisableMonitoredAgentRequest,
  dict,
])
def test_disable_monitored_agent_rest_call_success(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name='operations/spam')

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.disable_monitored_agent(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_disable_monitored_agent_rest_interceptors(null_interceptor):
    transport = transports.AgentAnomalyDetectionServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.AgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(operation.Operation, "_set_result_from_operation"), \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_disable_monitored_agent") as post, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_disable_monitored_agent_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "pre_disable_monitored_agent") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.DisableMonitoredAgentRequest.pb(agent_anomaly_detection_service.DisableMonitoredAgentRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = json_format.MessageToJson(operations_pb2.Operation())
        req.return_value.content = return_value

        request = agent_anomaly_detection_service.DisableMonitoredAgentRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.disable_monitored_agent(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_delete_agent_anomaly_detection_scope_rest_bad_request(request_type=agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/agentAnomalyDetectionScopes/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.delete_agent_anomaly_detection_scope(request)


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest,
  dict,
])
def test_delete_agent_anomaly_detection_scope_rest_call_success(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/agentAnomalyDetectionScopes/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name='operations/spam')

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.delete_agent_anomaly_detection_scope(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_delete_agent_anomaly_detection_scope_rest_interceptors(null_interceptor):
    transport = transports.AgentAnomalyDetectionServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.AgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(operation.Operation, "_set_result_from_operation"), \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_delete_agent_anomaly_detection_scope") as post, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_delete_agent_anomaly_detection_scope_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "pre_delete_agent_anomaly_detection_scope") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest.pb(agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = json_format.MessageToJson(operations_pb2.Operation())
        req.return_value.content = return_value

        request = agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.delete_agent_anomaly_detection_scope(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_create_agent_anomaly_detection_scope_rest_bad_request(request_type=agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.create_agent_anomaly_detection_scope(request)


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest,
  dict,
])
def test_create_agent_anomaly_detection_scope_rest_call_success(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2'}
    request_init["agent_anomaly_detection_scope"] = {'name': 'name_value', 'display_name': 'display_name_value', 'log_buckets': ['log_buckets_value1', 'log_buckets_value2'], 'observability_buckets': ['observability_buckets_value1', 'observability_buckets_value2'], 'auto_enroll': True, 'state': 1, 'encryption_spec': {'kms_key_name': 'kms_key_name_value'}}
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest.meta.fields["agent_anomaly_detection_scope"]

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
            else: # pragma: NO COVER
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
    for field, value in request_init["agent_anomaly_detection_scope"].items(): # pragma: NO COVER
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
                        {"field": field, "subfield": subfield, "is_repeated": is_repeated}
                    )

    # Remove fields from the sample request which are not present in the runtime version of the dependency
    # Add `# pragma: NO COVER` because this test code will not run if all subfields are present at runtime
    for subfield_to_delete in subfields_not_in_runtime: # pragma: NO COVER
        field = subfield_to_delete.get("field")
        field_repeated = subfield_to_delete.get("is_repeated")
        subfield = subfield_to_delete.get("subfield")
        if subfield:
            if field_repeated:
                for i in range(0, len(request_init["agent_anomaly_detection_scope"][field])):
                    del request_init["agent_anomaly_detection_scope"][field][i][subfield]
            else:
                del request_init["agent_anomaly_detection_scope"][field][subfield]
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name='operations/spam')

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.create_agent_anomaly_detection_scope(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_create_agent_anomaly_detection_scope_rest_interceptors(null_interceptor):
    transport = transports.AgentAnomalyDetectionServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.AgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(operation.Operation, "_set_result_from_operation"), \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_create_agent_anomaly_detection_scope") as post, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_create_agent_anomaly_detection_scope_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "pre_create_agent_anomaly_detection_scope") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest.pb(agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = json_format.MessageToJson(operations_pb2.Operation())
        req.return_value.content = return_value

        request = agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.create_agent_anomaly_detection_scope(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_list_agent_anomaly_detection_scopes_rest_bad_request(request_type=agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.list_agent_anomaly_detection_scopes(request)


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest,
  dict,
])
def test_list_agent_anomaly_detection_scopes_rest_call_success(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
              next_page_token='next_page_token_value',
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.list_agent_anomaly_detection_scopes(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListAgentAnomalyDetectionScopesPager)
    assert response.next_page_token == 'next_page_token_value'


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_agent_anomaly_detection_scopes_rest_interceptors(null_interceptor):
    transport = transports.AgentAnomalyDetectionServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.AgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_list_agent_anomaly_detection_scopes") as post, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_list_agent_anomaly_detection_scopes_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "pre_list_agent_anomaly_detection_scopes") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest.pb(agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse.to_json(agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse())
        req.return_value.content = return_value

        request = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse()
        post_with_metadata.return_value = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(), metadata

        client.list_agent_anomaly_detection_scopes(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_list_analyzed_sessions_rest_bad_request(request_type=agent_anomaly_detection_service.ListAnalyzedSessionsRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.list_analyzed_sessions(request)


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.ListAnalyzedSessionsRequest,
  dict,
])
def test_list_analyzed_sessions_rest_call_success(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
              next_page_token='next_page_token_value',
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.ListAnalyzedSessionsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.list_analyzed_sessions(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListAnalyzedSessionsPager)
    assert response.next_page_token == 'next_page_token_value'


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_analyzed_sessions_rest_interceptors(null_interceptor):
    transport = transports.AgentAnomalyDetectionServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.AgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_list_analyzed_sessions") as post, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_list_analyzed_sessions_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "pre_list_analyzed_sessions") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.ListAnalyzedSessionsRequest.pb(agent_anomaly_detection_service.ListAnalyzedSessionsRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = agent_anomaly_detection_service.ListAnalyzedSessionsResponse.to_json(agent_anomaly_detection_service.ListAnalyzedSessionsResponse())
        req.return_value.content = return_value

        request = agent_anomaly_detection_service.ListAnalyzedSessionsRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = agent_anomaly_detection_service.ListAnalyzedSessionsResponse()
        post_with_metadata.return_value = agent_anomaly_detection_service.ListAnalyzedSessionsResponse(), metadata

        client.list_analyzed_sessions(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_get_analyzed_session_rest_bad_request(request_type=agent_anomaly_detection_service.GetAnalyzedSessionRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3/analyzedSessions/sample4'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.get_analyzed_session(request)


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.GetAnalyzedSessionRequest,
  dict,
])
def test_get_analyzed_session_rest_call_success(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3/analyzedSessions/sample4'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.AnalyzedSession(
              name='name_value',
              session_id='session_id_value',
              user_id='user_id_value',
              agent_resource_name='agent_resource_name_value',
              session_state=agent_anomaly_detection_service.AnalyzedSession.SessionState.SESSION_STATE_UNANALYZED,
              agent_display_name='agent_display_name_value',
              agent_state=agent_anomaly_detection_service.MonitoredAgent.EnablementState.ACTIVE,
              location='location_value',
              agent_type=agent_anomaly_detection_service.AgentResource.AgentType.REASONING_ENGINE,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.AnalyzedSession.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.get_analyzed_session(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, agent_anomaly_detection_service.AnalyzedSession)
    assert response.name == 'name_value'
    assert response.session_id == 'session_id_value'
    assert response.user_id == 'user_id_value'
    assert response.agent_resource_name == 'agent_resource_name_value'
    assert response.session_state == agent_anomaly_detection_service.AnalyzedSession.SessionState.SESSION_STATE_UNANALYZED
    assert response.agent_display_name == 'agent_display_name_value'
    assert response.agent_state == agent_anomaly_detection_service.MonitoredAgent.EnablementState.ACTIVE
    assert response.location == 'location_value'
    assert response.agent_type == agent_anomaly_detection_service.AgentResource.AgentType.REASONING_ENGINE


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_analyzed_session_rest_interceptors(null_interceptor):
    transport = transports.AgentAnomalyDetectionServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.AgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_get_analyzed_session") as post, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_get_analyzed_session_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "pre_get_analyzed_session") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.GetAnalyzedSessionRequest.pb(agent_anomaly_detection_service.GetAnalyzedSessionRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = agent_anomaly_detection_service.AnalyzedSession.to_json(agent_anomaly_detection_service.AnalyzedSession())
        req.return_value.content = return_value

        request = agent_anomaly_detection_service.GetAnalyzedSessionRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = agent_anomaly_detection_service.AnalyzedSession()
        post_with_metadata.return_value = agent_anomaly_detection_service.AnalyzedSession(), metadata

        client.get_analyzed_session(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_list_analyzed_invocations_rest_bad_request(request_type=agent_anomaly_detection_service.ListAnalyzedInvocationsRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2/monitoredAgents/sample3/analyzedSessions/sample4'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.list_analyzed_invocations(request)


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.ListAnalyzedInvocationsRequest,
  dict,
])
def test_list_analyzed_invocations_rest_call_success(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2/monitoredAgents/sample3/analyzedSessions/sample4'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
              next_page_token='next_page_token_value',
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.ListAnalyzedInvocationsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.list_analyzed_invocations(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListAnalyzedInvocationsPager)
    assert response.next_page_token == 'next_page_token_value'


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_analyzed_invocations_rest_interceptors(null_interceptor):
    transport = transports.AgentAnomalyDetectionServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.AgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_list_analyzed_invocations") as post, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_list_analyzed_invocations_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "pre_list_analyzed_invocations") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.ListAnalyzedInvocationsRequest.pb(agent_anomaly_detection_service.ListAnalyzedInvocationsRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = agent_anomaly_detection_service.ListAnalyzedInvocationsResponse.to_json(agent_anomaly_detection_service.ListAnalyzedInvocationsResponse())
        req.return_value.content = return_value

        request = agent_anomaly_detection_service.ListAnalyzedInvocationsRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = agent_anomaly_detection_service.ListAnalyzedInvocationsResponse()
        post_with_metadata.return_value = agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(), metadata

        client.list_analyzed_invocations(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_get_analyzed_invocation_rest_bad_request(request_type=agent_anomaly_detection_service.GetAnalyzedInvocationRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3/analyzedSessions/sample4/analyzedInvocations/sample5'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.get_analyzed_invocation(request)


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.GetAnalyzedInvocationRequest,
  dict,
])
def test_get_analyzed_invocation_rest_call_success(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3/analyzedSessions/sample4/analyzedInvocations/sample5'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.AnalyzedInvocation(
              name='name_value',
              invocation_id='invocation_id_value',
              invocation_state=agent_anomaly_detection_service.AnalyzedInvocation.InvocationState.INVOCATION_STATE_ANOMALOUS,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.AnalyzedInvocation.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.get_analyzed_invocation(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, agent_anomaly_detection_service.AnalyzedInvocation)
    assert response.name == 'name_value'
    assert response.invocation_id == 'invocation_id_value'
    assert response.invocation_state == agent_anomaly_detection_service.AnalyzedInvocation.InvocationState.INVOCATION_STATE_ANOMALOUS


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_analyzed_invocation_rest_interceptors(null_interceptor):
    transport = transports.AgentAnomalyDetectionServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.AgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_get_analyzed_invocation") as post, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_get_analyzed_invocation_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "pre_get_analyzed_invocation") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.GetAnalyzedInvocationRequest.pb(agent_anomaly_detection_service.GetAnalyzedInvocationRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = agent_anomaly_detection_service.AnalyzedInvocation.to_json(agent_anomaly_detection_service.AnalyzedInvocation())
        req.return_value.content = return_value

        request = agent_anomaly_detection_service.GetAnalyzedInvocationRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = agent_anomaly_detection_service.AnalyzedInvocation()
        post_with_metadata.return_value = agent_anomaly_detection_service.AnalyzedInvocation(), metadata

        client.get_analyzed_invocation(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_aggregate_analyzed_sessions_rest_bad_request(request_type=agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.aggregate_analyzed_sessions(request)


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest,
  dict,
])
def test_aggregate_analyzed_sessions_rest_call_success(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
              next_page_token='next_page_token_value',
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.aggregate_analyzed_sessions(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.AggregateAnalyzedSessionsPager)
    assert response.next_page_token == 'next_page_token_value'


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_aggregate_analyzed_sessions_rest_interceptors(null_interceptor):
    transport = transports.AgentAnomalyDetectionServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.AgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_aggregate_analyzed_sessions") as post, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_aggregate_analyzed_sessions_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "pre_aggregate_analyzed_sessions") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest.pb(agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.to_json(agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse())
        req.return_value.content = return_value

        request = agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse()
        post_with_metadata.return_value = agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(), metadata

        client.aggregate_analyzed_sessions(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_clear_training_data_rest_bad_request(request_type=agent_anomaly_detection_service.ClearTrainingDataRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.clear_training_data(request)


@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.ClearTrainingDataRequest,
  dict,
])
def test_clear_training_data_rest_call_success(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name='operations/spam')

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode('UTF-8')
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.clear_training_data(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_clear_training_data_rest_interceptors(null_interceptor):
    transport = transports.AgentAnomalyDetectionServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=None if null_interceptor else transports.AgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(operation.Operation, "_set_result_from_operation"), \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_clear_training_data") as post, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "post_clear_training_data_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AgentAnomalyDetectionServiceRestInterceptor, "pre_clear_training_data") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.ClearTrainingDataRequest.pb(agent_anomaly_detection_service.ClearTrainingDataRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = json_format.MessageToJson(operations_pb2.Operation())
        req.return_value.content = return_value

        request = agent_anomaly_detection_service.ClearTrainingDataRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.clear_training_data(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_get_location_rest_bad_request(request_type=locations_pb2.GetLocationRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type()
    request = json_format.ParseDict({'name': 'projects/sample1/locations/sample2'}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = Response()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.get_location(request)


@pytest.mark.parametrize("request_type", [
    locations_pb2.GetLocationRequest,
    dict,
])
def test_get_location_rest(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    request_init = {'name': 'projects/sample1/locations/sample2'}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = locations_pb2.Location()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode('UTF-8')

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = client.get_location(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, locations_pb2.Location)


def test_list_locations_rest_bad_request(request_type=locations_pb2.ListLocationsRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type()
    request = json_format.ParseDict({'name': 'projects/sample1'}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = Response()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.list_locations(request)


@pytest.mark.parametrize("request_type", [
    locations_pb2.ListLocationsRequest,
    dict,
])
def test_list_locations_rest(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    request_init = {'name': 'projects/sample1'}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = locations_pb2.ListLocationsResponse()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode('UTF-8')

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = client.list_locations(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, locations_pb2.ListLocationsResponse)


def test_get_iam_policy_rest_bad_request(request_type=iam_policy_pb2.GetIamPolicyRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type()
    request = json_format.ParseDict({'resource': 'projects/sample1/locations/sample2/featurestores/sample3'}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = Response()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.get_iam_policy(request)


@pytest.mark.parametrize("request_type", [
    iam_policy_pb2.GetIamPolicyRequest,
    dict,
])
def test_get_iam_policy_rest(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    request_init = {'resource': 'projects/sample1/locations/sample2/featurestores/sample3'}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = policy_pb2.Policy()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode('UTF-8')

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = client.get_iam_policy(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy_pb2.Policy)


def test_set_iam_policy_rest_bad_request(request_type=iam_policy_pb2.SetIamPolicyRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type()
    request = json_format.ParseDict({'resource': 'projects/sample1/locations/sample2/featurestores/sample3'}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = Response()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.set_iam_policy(request)


@pytest.mark.parametrize("request_type", [
    iam_policy_pb2.SetIamPolicyRequest,
    dict,
])
def test_set_iam_policy_rest(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    request_init = {'resource': 'projects/sample1/locations/sample2/featurestores/sample3'}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = policy_pb2.Policy()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode('UTF-8')

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = client.set_iam_policy(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy_pb2.Policy)


def test_test_iam_permissions_rest_bad_request(request_type=iam_policy_pb2.TestIamPermissionsRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type()
    request = json_format.ParseDict({'resource': 'projects/sample1/locations/sample2/featurestores/sample3'}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = Response()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.test_iam_permissions(request)


@pytest.mark.parametrize("request_type", [
    iam_policy_pb2.TestIamPermissionsRequest,
    dict,
])
def test_test_iam_permissions_rest(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    request_init = {'resource': 'projects/sample1/locations/sample2/featurestores/sample3'}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = iam_policy_pb2.TestIamPermissionsResponse()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode('UTF-8')

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = client.test_iam_permissions(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, iam_policy_pb2.TestIamPermissionsResponse)


def test_cancel_operation_rest_bad_request(request_type=operations_pb2.CancelOperationRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type()
    request = json_format.ParseDict({'name': 'projects/sample1/locations/sample2/operations/sample3'}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = Response()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.cancel_operation(request)


@pytest.mark.parametrize("request_type", [
    operations_pb2.CancelOperationRequest,
    dict,
])
def test_cancel_operation_rest(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    request_init = {'name': 'projects/sample1/locations/sample2/operations/sample3'}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = '{}'
        response_value.content = json_return_value.encode('UTF-8')

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = client.cancel_operation(request)

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_operation_rest_bad_request(request_type=operations_pb2.DeleteOperationRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type()
    request = json_format.ParseDict({'name': 'projects/sample1/locations/sample2/operations/sample3'}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = Response()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.delete_operation(request)


@pytest.mark.parametrize("request_type", [
    operations_pb2.DeleteOperationRequest,
    dict,
])
def test_delete_operation_rest(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    request_init = {'name': 'projects/sample1/locations/sample2/operations/sample3'}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = '{}'
        response_value.content = json_return_value.encode('UTF-8')

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = client.delete_operation(request)

    # Establish that the response is the type that we expect.
    assert response is None


def test_get_operation_rest_bad_request(request_type=operations_pb2.GetOperationRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type()
    request = json_format.ParseDict({'name': 'projects/sample1/locations/sample2/operations/sample3'}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = Response()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.get_operation(request)


@pytest.mark.parametrize("request_type", [
    operations_pb2.GetOperationRequest,
    dict,
])
def test_get_operation_rest(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    request_init = {'name': 'projects/sample1/locations/sample2/operations/sample3'}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode('UTF-8')

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = client.get_operation(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.Operation)


def test_list_operations_rest_bad_request(request_type=operations_pb2.ListOperationsRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type()
    request = json_format.ParseDict({'name': 'projects/sample1/locations/sample2'}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = Response()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.list_operations(request)


@pytest.mark.parametrize("request_type", [
    operations_pb2.ListOperationsRequest,
    dict,
])
def test_list_operations_rest(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    request_init = {'name': 'projects/sample1/locations/sample2'}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.ListOperationsResponse()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode('UTF-8')

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = client.list_operations(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.ListOperationsResponse)


def test_wait_operation_rest_bad_request(request_type=operations_pb2.WaitOperationRequest):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type()
    request = json_format.ParseDict({'name': 'projects/sample1/locations/sample2/operations/sample3'}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = Response()
        json_return_value = ''
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.wait_operation(request)


@pytest.mark.parametrize("request_type", [
    operations_pb2.WaitOperationRequest,
    dict,
])
def test_wait_operation_rest(request_type):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    request_init = {'name': 'projects/sample1/locations/sample2/operations/sample3'}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode('UTF-8')

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = client.wait_operation(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.Operation)

def test_initialize_client_w_rest():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )
    assert client is not None


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_agent_anomaly_detection_scope_empty_call_rest():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.get_agent_anomaly_detection_scope),
            '__call__') as call:
        client.get_agent_anomaly_detection_scope(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_monitored_agent_empty_call_rest():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.get_monitored_agent),
            '__call__') as call:
        client.get_monitored_agent(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.GetMonitoredAgentRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_monitored_agents_empty_call_rest():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.list_monitored_agents),
            '__call__') as call:
        client.list_monitored_agents(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ListMonitoredAgentsRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_enable_monitored_agent_empty_call_rest():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.enable_monitored_agent),
            '__call__') as call:
        client.enable_monitored_agent(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.EnableMonitoredAgentRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_disable_monitored_agent_empty_call_rest():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.disable_monitored_agent),
            '__call__') as call:
        client.disable_monitored_agent(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.DisableMonitoredAgentRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_delete_agent_anomaly_detection_scope_empty_call_rest():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_agent_anomaly_detection_scope),
            '__call__') as call:
        client.delete_agent_anomaly_detection_scope(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_create_agent_anomaly_detection_scope_empty_call_rest():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.create_agent_anomaly_detection_scope),
            '__call__') as call:
        client.create_agent_anomaly_detection_scope(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_agent_anomaly_detection_scopes_empty_call_rest():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.list_agent_anomaly_detection_scopes),
            '__call__') as call:
        client.list_agent_anomaly_detection_scopes(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_analyzed_sessions_empty_call_rest():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_sessions),
            '__call__') as call:
        client.list_analyzed_sessions(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ListAnalyzedSessionsRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_analyzed_session_empty_call_rest():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.get_analyzed_session),
            '__call__') as call:
        client.get_analyzed_session(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.GetAnalyzedSessionRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_analyzed_invocations_empty_call_rest():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_invocations),
            '__call__') as call:
        client.list_analyzed_invocations(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ListAnalyzedInvocationsRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_analyzed_invocation_empty_call_rest():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.get_analyzed_invocation),
            '__call__') as call:
        client.get_analyzed_invocation(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.GetAnalyzedInvocationRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_aggregate_analyzed_sessions_empty_call_rest():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.aggregate_analyzed_sessions),
            '__call__') as call:
        client.aggregate_analyzed_sessions(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_clear_training_data_empty_call_rest():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.clear_training_data),
            '__call__') as call:
        client.clear_training_data(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ClearTrainingDataRequest()
        assert args[0] == request_msg


def test_agent_anomaly_detection_service_rest_lro_client():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    transport = client.transport

    # Ensure that we have an api-core operations client.
    assert isinstance(
        transport.operations_client,
operations_v1.AbstractOperationsClient,
    )

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client

def test_transport_kind_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    transport = AgentAnomalyDetectionServiceAsyncClient.get_transport_class("rest_asyncio")(
        credentials=async_anonymous_credentials()
    )
    assert transport.kind == "rest_asyncio"


@pytest.mark.asyncio
async def test_get_agent_anomaly_detection_scope_rest_asyncio_bad_request(request_type=agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/agentAnomalyDetectionScopes/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.get_agent_anomaly_detection_scope(request)


@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest,
  dict,
])
async def test_get_agent_anomaly_detection_scope_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/agentAnomalyDetectionScopes/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.AgentAnomalyDetectionScope(
              name='name_value',
              display_name='display_name_value',
              log_buckets=['log_buckets_value'],
              observability_buckets=['observability_buckets_value'],
              auto_enroll=True,
              state=agent_anomaly_detection_service.AgentAnomalyDetectionScope.State.CREATING,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.AgentAnomalyDetectionScope.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.get_agent_anomaly_detection_scope(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, agent_anomaly_detection_service.AgentAnomalyDetectionScope)
    assert response.name == 'name_value'
    assert response.display_name == 'display_name_value'
    assert response.log_buckets == ['log_buckets_value']
    assert response.observability_buckets == ['observability_buckets_value']
    assert response.auto_enroll is True
    assert response.state == agent_anomaly_detection_service.AgentAnomalyDetectionScope.State.CREATING


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_get_agent_anomaly_detection_scope_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    transport = transports.AsyncAgentAnomalyDetectionServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=None if null_interceptor else transports.AsyncAgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceAsyncClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_get_agent_anomaly_detection_scope") as post, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_get_agent_anomaly_detection_scope_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "pre_get_agent_anomaly_detection_scope") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest.pb(agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = agent_anomaly_detection_service.AgentAnomalyDetectionScope.to_json(agent_anomaly_detection_service.AgentAnomalyDetectionScope())
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = agent_anomaly_detection_service.AgentAnomalyDetectionScope()
        post_with_metadata.return_value = agent_anomaly_detection_service.AgentAnomalyDetectionScope(), metadata

        await client.get_agent_anomaly_detection_scope(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()

@pytest.mark.asyncio
async def test_get_monitored_agent_rest_asyncio_bad_request(request_type=agent_anomaly_detection_service.GetMonitoredAgentRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.get_monitored_agent(request)


@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.GetMonitoredAgentRequest,
  dict,
])
async def test_get_monitored_agent_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.MonitoredAgent(
              name='name_value',
              display_name='display_name_value',
              state=agent_anomaly_detection_service.MonitoredAgent.EnablementState.ACTIVE,
              status_message='status_message_value',
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.MonitoredAgent.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.get_monitored_agent(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, agent_anomaly_detection_service.MonitoredAgent)
    assert response.name == 'name_value'
    assert response.display_name == 'display_name_value'
    assert response.state == agent_anomaly_detection_service.MonitoredAgent.EnablementState.ACTIVE
    assert response.status_message == 'status_message_value'


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_get_monitored_agent_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    transport = transports.AsyncAgentAnomalyDetectionServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=None if null_interceptor else transports.AsyncAgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceAsyncClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_get_monitored_agent") as post, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_get_monitored_agent_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "pre_get_monitored_agent") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.GetMonitoredAgentRequest.pb(agent_anomaly_detection_service.GetMonitoredAgentRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = agent_anomaly_detection_service.MonitoredAgent.to_json(agent_anomaly_detection_service.MonitoredAgent())
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = agent_anomaly_detection_service.GetMonitoredAgentRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = agent_anomaly_detection_service.MonitoredAgent()
        post_with_metadata.return_value = agent_anomaly_detection_service.MonitoredAgent(), metadata

        await client.get_monitored_agent(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()

@pytest.mark.asyncio
async def test_list_monitored_agents_rest_asyncio_bad_request(request_type=agent_anomaly_detection_service.ListMonitoredAgentsRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.list_monitored_agents(request)


@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.ListMonitoredAgentsRequest,
  dict,
])
async def test_list_monitored_agents_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.ListMonitoredAgentsResponse(
              next_page_token='next_page_token_value',
              total_size=1086,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.ListMonitoredAgentsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.list_monitored_agents(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListMonitoredAgentsAsyncPager)
    assert response.next_page_token == 'next_page_token_value'
    assert response.total_size == 1086


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_list_monitored_agents_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    transport = transports.AsyncAgentAnomalyDetectionServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=None if null_interceptor else transports.AsyncAgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceAsyncClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_list_monitored_agents") as post, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_list_monitored_agents_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "pre_list_monitored_agents") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.ListMonitoredAgentsRequest.pb(agent_anomaly_detection_service.ListMonitoredAgentsRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = agent_anomaly_detection_service.ListMonitoredAgentsResponse.to_json(agent_anomaly_detection_service.ListMonitoredAgentsResponse())
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = agent_anomaly_detection_service.ListMonitoredAgentsRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = agent_anomaly_detection_service.ListMonitoredAgentsResponse()
        post_with_metadata.return_value = agent_anomaly_detection_service.ListMonitoredAgentsResponse(), metadata

        await client.list_monitored_agents(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()

@pytest.mark.asyncio
async def test_enable_monitored_agent_rest_asyncio_bad_request(request_type=agent_anomaly_detection_service.EnableMonitoredAgentRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.enable_monitored_agent(request)


@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.EnableMonitoredAgentRequest,
  dict,
])
async def test_enable_monitored_agent_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name='operations/spam')

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.enable_monitored_agent(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_enable_monitored_agent_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    transport = transports.AsyncAgentAnomalyDetectionServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=None if null_interceptor else transports.AsyncAgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceAsyncClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(operation.Operation, "_set_result_from_operation"), \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_enable_monitored_agent") as post, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_enable_monitored_agent_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "pre_enable_monitored_agent") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.EnableMonitoredAgentRequest.pb(agent_anomaly_detection_service.EnableMonitoredAgentRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = json_format.MessageToJson(operations_pb2.Operation())
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = agent_anomaly_detection_service.EnableMonitoredAgentRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.enable_monitored_agent(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()

@pytest.mark.asyncio
async def test_disable_monitored_agent_rest_asyncio_bad_request(request_type=agent_anomaly_detection_service.DisableMonitoredAgentRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.disable_monitored_agent(request)


@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.DisableMonitoredAgentRequest,
  dict,
])
async def test_disable_monitored_agent_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name='operations/spam')

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.disable_monitored_agent(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_disable_monitored_agent_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    transport = transports.AsyncAgentAnomalyDetectionServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=None if null_interceptor else transports.AsyncAgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceAsyncClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(operation.Operation, "_set_result_from_operation"), \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_disable_monitored_agent") as post, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_disable_monitored_agent_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "pre_disable_monitored_agent") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.DisableMonitoredAgentRequest.pb(agent_anomaly_detection_service.DisableMonitoredAgentRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = json_format.MessageToJson(operations_pb2.Operation())
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = agent_anomaly_detection_service.DisableMonitoredAgentRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.disable_monitored_agent(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()

@pytest.mark.asyncio
async def test_delete_agent_anomaly_detection_scope_rest_asyncio_bad_request(request_type=agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/agentAnomalyDetectionScopes/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.delete_agent_anomaly_detection_scope(request)


@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest,
  dict,
])
async def test_delete_agent_anomaly_detection_scope_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/agentAnomalyDetectionScopes/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name='operations/spam')

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.delete_agent_anomaly_detection_scope(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_delete_agent_anomaly_detection_scope_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    transport = transports.AsyncAgentAnomalyDetectionServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=None if null_interceptor else transports.AsyncAgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceAsyncClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(operation.Operation, "_set_result_from_operation"), \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_delete_agent_anomaly_detection_scope") as post, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_delete_agent_anomaly_detection_scope_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "pre_delete_agent_anomaly_detection_scope") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest.pb(agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = json_format.MessageToJson(operations_pb2.Operation())
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.delete_agent_anomaly_detection_scope(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()

@pytest.mark.asyncio
async def test_create_agent_anomaly_detection_scope_rest_asyncio_bad_request(request_type=agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.create_agent_anomaly_detection_scope(request)


@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest,
  dict,
])
async def test_create_agent_anomaly_detection_scope_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2'}
    request_init["agent_anomaly_detection_scope"] = {'name': 'name_value', 'display_name': 'display_name_value', 'log_buckets': ['log_buckets_value1', 'log_buckets_value2'], 'observability_buckets': ['observability_buckets_value1', 'observability_buckets_value2'], 'auto_enroll': True, 'state': 1, 'encryption_spec': {'kms_key_name': 'kms_key_name_value'}}
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest.meta.fields["agent_anomaly_detection_scope"]

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
            else: # pragma: NO COVER
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
    for field, value in request_init["agent_anomaly_detection_scope"].items(): # pragma: NO COVER
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
                        {"field": field, "subfield": subfield, "is_repeated": is_repeated}
                    )

    # Remove fields from the sample request which are not present in the runtime version of the dependency
    # Add `# pragma: NO COVER` because this test code will not run if all subfields are present at runtime
    for subfield_to_delete in subfields_not_in_runtime: # pragma: NO COVER
        field = subfield_to_delete.get("field")
        field_repeated = subfield_to_delete.get("is_repeated")
        subfield = subfield_to_delete.get("subfield")
        if subfield:
            if field_repeated:
                for i in range(0, len(request_init["agent_anomaly_detection_scope"][field])):
                    del request_init["agent_anomaly_detection_scope"][field][i][subfield]
            else:
                del request_init["agent_anomaly_detection_scope"][field][subfield]
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name='operations/spam')

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.create_agent_anomaly_detection_scope(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_create_agent_anomaly_detection_scope_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    transport = transports.AsyncAgentAnomalyDetectionServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=None if null_interceptor else transports.AsyncAgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceAsyncClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(operation.Operation, "_set_result_from_operation"), \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_create_agent_anomaly_detection_scope") as post, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_create_agent_anomaly_detection_scope_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "pre_create_agent_anomaly_detection_scope") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest.pb(agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = json_format.MessageToJson(operations_pb2.Operation())
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.create_agent_anomaly_detection_scope(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()

@pytest.mark.asyncio
async def test_list_agent_anomaly_detection_scopes_rest_asyncio_bad_request(request_type=agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.list_agent_anomaly_detection_scopes(request)


@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest,
  dict,
])
async def test_list_agent_anomaly_detection_scopes_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(
              next_page_token='next_page_token_value',
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.list_agent_anomaly_detection_scopes(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListAgentAnomalyDetectionScopesAsyncPager)
    assert response.next_page_token == 'next_page_token_value'


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_list_agent_anomaly_detection_scopes_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    transport = transports.AsyncAgentAnomalyDetectionServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=None if null_interceptor else transports.AsyncAgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceAsyncClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_list_agent_anomaly_detection_scopes") as post, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_list_agent_anomaly_detection_scopes_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "pre_list_agent_anomaly_detection_scopes") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest.pb(agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse.to_json(agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse())
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse()
        post_with_metadata.return_value = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse(), metadata

        await client.list_agent_anomaly_detection_scopes(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()

@pytest.mark.asyncio
async def test_list_analyzed_sessions_rest_asyncio_bad_request(request_type=agent_anomaly_detection_service.ListAnalyzedSessionsRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.list_analyzed_sessions(request)


@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.ListAnalyzedSessionsRequest,
  dict,
])
async def test_list_analyzed_sessions_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.ListAnalyzedSessionsResponse(
              next_page_token='next_page_token_value',
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.ListAnalyzedSessionsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.list_analyzed_sessions(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListAnalyzedSessionsAsyncPager)
    assert response.next_page_token == 'next_page_token_value'


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_list_analyzed_sessions_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    transport = transports.AsyncAgentAnomalyDetectionServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=None if null_interceptor else transports.AsyncAgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceAsyncClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_list_analyzed_sessions") as post, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_list_analyzed_sessions_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "pre_list_analyzed_sessions") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.ListAnalyzedSessionsRequest.pb(agent_anomaly_detection_service.ListAnalyzedSessionsRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = agent_anomaly_detection_service.ListAnalyzedSessionsResponse.to_json(agent_anomaly_detection_service.ListAnalyzedSessionsResponse())
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = agent_anomaly_detection_service.ListAnalyzedSessionsRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = agent_anomaly_detection_service.ListAnalyzedSessionsResponse()
        post_with_metadata.return_value = agent_anomaly_detection_service.ListAnalyzedSessionsResponse(), metadata

        await client.list_analyzed_sessions(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()

@pytest.mark.asyncio
async def test_get_analyzed_session_rest_asyncio_bad_request(request_type=agent_anomaly_detection_service.GetAnalyzedSessionRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3/analyzedSessions/sample4'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.get_analyzed_session(request)


@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.GetAnalyzedSessionRequest,
  dict,
])
async def test_get_analyzed_session_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3/analyzedSessions/sample4'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.AnalyzedSession(
              name='name_value',
              session_id='session_id_value',
              user_id='user_id_value',
              agent_resource_name='agent_resource_name_value',
              session_state=agent_anomaly_detection_service.AnalyzedSession.SessionState.SESSION_STATE_UNANALYZED,
              agent_display_name='agent_display_name_value',
              agent_state=agent_anomaly_detection_service.MonitoredAgent.EnablementState.ACTIVE,
              location='location_value',
              agent_type=agent_anomaly_detection_service.AgentResource.AgentType.REASONING_ENGINE,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.AnalyzedSession.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.get_analyzed_session(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, agent_anomaly_detection_service.AnalyzedSession)
    assert response.name == 'name_value'
    assert response.session_id == 'session_id_value'
    assert response.user_id == 'user_id_value'
    assert response.agent_resource_name == 'agent_resource_name_value'
    assert response.session_state == agent_anomaly_detection_service.AnalyzedSession.SessionState.SESSION_STATE_UNANALYZED
    assert response.agent_display_name == 'agent_display_name_value'
    assert response.agent_state == agent_anomaly_detection_service.MonitoredAgent.EnablementState.ACTIVE
    assert response.location == 'location_value'
    assert response.agent_type == agent_anomaly_detection_service.AgentResource.AgentType.REASONING_ENGINE


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_get_analyzed_session_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    transport = transports.AsyncAgentAnomalyDetectionServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=None if null_interceptor else transports.AsyncAgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceAsyncClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_get_analyzed_session") as post, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_get_analyzed_session_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "pre_get_analyzed_session") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.GetAnalyzedSessionRequest.pb(agent_anomaly_detection_service.GetAnalyzedSessionRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = agent_anomaly_detection_service.AnalyzedSession.to_json(agent_anomaly_detection_service.AnalyzedSession())
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = agent_anomaly_detection_service.GetAnalyzedSessionRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = agent_anomaly_detection_service.AnalyzedSession()
        post_with_metadata.return_value = agent_anomaly_detection_service.AnalyzedSession(), metadata

        await client.get_analyzed_session(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()

@pytest.mark.asyncio
async def test_list_analyzed_invocations_rest_asyncio_bad_request(request_type=agent_anomaly_detection_service.ListAnalyzedInvocationsRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2/monitoredAgents/sample3/analyzedSessions/sample4'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.list_analyzed_invocations(request)


@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.ListAnalyzedInvocationsRequest,
  dict,
])
async def test_list_analyzed_invocations_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2/monitoredAgents/sample3/analyzedSessions/sample4'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(
              next_page_token='next_page_token_value',
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.ListAnalyzedInvocationsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.list_analyzed_invocations(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListAnalyzedInvocationsAsyncPager)
    assert response.next_page_token == 'next_page_token_value'


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_list_analyzed_invocations_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    transport = transports.AsyncAgentAnomalyDetectionServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=None if null_interceptor else transports.AsyncAgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceAsyncClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_list_analyzed_invocations") as post, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_list_analyzed_invocations_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "pre_list_analyzed_invocations") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.ListAnalyzedInvocationsRequest.pb(agent_anomaly_detection_service.ListAnalyzedInvocationsRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = agent_anomaly_detection_service.ListAnalyzedInvocationsResponse.to_json(agent_anomaly_detection_service.ListAnalyzedInvocationsResponse())
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = agent_anomaly_detection_service.ListAnalyzedInvocationsRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = agent_anomaly_detection_service.ListAnalyzedInvocationsResponse()
        post_with_metadata.return_value = agent_anomaly_detection_service.ListAnalyzedInvocationsResponse(), metadata

        await client.list_analyzed_invocations(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()

@pytest.mark.asyncio
async def test_get_analyzed_invocation_rest_asyncio_bad_request(request_type=agent_anomaly_detection_service.GetAnalyzedInvocationRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3/analyzedSessions/sample4/analyzedInvocations/sample5'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.get_analyzed_invocation(request)


@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.GetAnalyzedInvocationRequest,
  dict,
])
async def test_get_analyzed_invocation_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3/analyzedSessions/sample4/analyzedInvocations/sample5'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.AnalyzedInvocation(
              name='name_value',
              invocation_id='invocation_id_value',
              invocation_state=agent_anomaly_detection_service.AnalyzedInvocation.InvocationState.INVOCATION_STATE_ANOMALOUS,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.AnalyzedInvocation.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.get_analyzed_invocation(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, agent_anomaly_detection_service.AnalyzedInvocation)
    assert response.name == 'name_value'
    assert response.invocation_id == 'invocation_id_value'
    assert response.invocation_state == agent_anomaly_detection_service.AnalyzedInvocation.InvocationState.INVOCATION_STATE_ANOMALOUS


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_get_analyzed_invocation_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    transport = transports.AsyncAgentAnomalyDetectionServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=None if null_interceptor else transports.AsyncAgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceAsyncClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_get_analyzed_invocation") as post, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_get_analyzed_invocation_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "pre_get_analyzed_invocation") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.GetAnalyzedInvocationRequest.pb(agent_anomaly_detection_service.GetAnalyzedInvocationRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = agent_anomaly_detection_service.AnalyzedInvocation.to_json(agent_anomaly_detection_service.AnalyzedInvocation())
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = agent_anomaly_detection_service.GetAnalyzedInvocationRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = agent_anomaly_detection_service.AnalyzedInvocation()
        post_with_metadata.return_value = agent_anomaly_detection_service.AnalyzedInvocation(), metadata

        await client.get_analyzed_invocation(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()

@pytest.mark.asyncio
async def test_aggregate_analyzed_sessions_rest_asyncio_bad_request(request_type=agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.aggregate_analyzed_sessions(request)


@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest,
  dict,
])
async def test_aggregate_analyzed_sessions_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {'parent': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(
              next_page_token='next_page_token_value',
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.aggregate_analyzed_sessions(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.AggregateAnalyzedSessionsAsyncPager)
    assert response.next_page_token == 'next_page_token_value'


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_aggregate_analyzed_sessions_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    transport = transports.AsyncAgentAnomalyDetectionServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=None if null_interceptor else transports.AsyncAgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceAsyncClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_aggregate_analyzed_sessions") as post, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_aggregate_analyzed_sessions_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "pre_aggregate_analyzed_sessions") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest.pb(agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.to_json(agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse())
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse()
        post_with_metadata.return_value = agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse(), metadata

        await client.aggregate_analyzed_sessions(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()

@pytest.mark.asyncio
async def test_clear_training_data_rest_asyncio_bad_request(request_type=agent_anomaly_detection_service.ClearTrainingDataRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.clear_training_data(request)


@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
  agent_anomaly_detection_service.ClearTrainingDataRequest,
  dict,
])
async def test_clear_training_data_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {'name': 'projects/sample1/locations/sample2/monitoredAgents/sample3'}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name='operations/spam')

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.clear_training_data(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_clear_training_data_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    transport = transports.AsyncAgentAnomalyDetectionServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=None if null_interceptor else transports.AsyncAgentAnomalyDetectionServiceRestInterceptor(),
        )
    client = AgentAnomalyDetectionServiceAsyncClient(transport=transport)

    with mock.patch.object(type(client.transport._session), "request") as req, \
        mock.patch.object(path_template, "transcode")  as transcode, \
        mock.patch.object(operation.Operation, "_set_result_from_operation"), \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_clear_training_data") as post, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "post_clear_training_data_with_metadata") as post_with_metadata, \
        mock.patch.object(transports.AsyncAgentAnomalyDetectionServiceRestInterceptor, "pre_clear_training_data") as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = agent_anomaly_detection_service.ClearTrainingDataRequest.pb(agent_anomaly_detection_service.ClearTrainingDataRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = json_format.MessageToJson(operations_pb2.Operation())
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = agent_anomaly_detection_service.ClearTrainingDataRequest()
        metadata =[
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.clear_training_data(request, metadata=[("key", "val"), ("cephalopod", "squid"),])

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()

@pytest.mark.asyncio
async def test_get_location_rest_asyncio_bad_request(request_type=locations_pb2.GetLocationRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )
    request = request_type()
    request = json_format.ParseDict({'name': 'projects/sample1/locations/sample2'}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.get_location(request)

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
    locations_pb2.GetLocationRequest,
    dict,
])
async def test_get_location_rest_asyncio(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    request_init = {'name': 'projects/sample1/locations/sample2'}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = locations_pb2.Location()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = await client.get_location(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, locations_pb2.Location)

@pytest.mark.asyncio
async def test_list_locations_rest_asyncio_bad_request(request_type=locations_pb2.ListLocationsRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )
    request = request_type()
    request = json_format.ParseDict({'name': 'projects/sample1'}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.list_locations(request)

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
    locations_pb2.ListLocationsRequest,
    dict,
])
async def test_list_locations_rest_asyncio(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    request_init = {'name': 'projects/sample1'}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = locations_pb2.ListLocationsResponse()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = await client.list_locations(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, locations_pb2.ListLocationsResponse)

@pytest.mark.asyncio
async def test_get_iam_policy_rest_asyncio_bad_request(request_type=iam_policy_pb2.GetIamPolicyRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )
    request = request_type()
    request = json_format.ParseDict({'resource': 'projects/sample1/locations/sample2/featurestores/sample3'}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.get_iam_policy(request)

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
    iam_policy_pb2.GetIamPolicyRequest,
    dict,
])
async def test_get_iam_policy_rest_asyncio(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    request_init = {'resource': 'projects/sample1/locations/sample2/featurestores/sample3'}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = policy_pb2.Policy()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = await client.get_iam_policy(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy_pb2.Policy)

@pytest.mark.asyncio
async def test_set_iam_policy_rest_asyncio_bad_request(request_type=iam_policy_pb2.SetIamPolicyRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )
    request = request_type()
    request = json_format.ParseDict({'resource': 'projects/sample1/locations/sample2/featurestores/sample3'}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.set_iam_policy(request)

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
    iam_policy_pb2.SetIamPolicyRequest,
    dict,
])
async def test_set_iam_policy_rest_asyncio(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    request_init = {'resource': 'projects/sample1/locations/sample2/featurestores/sample3'}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = policy_pb2.Policy()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = await client.set_iam_policy(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy_pb2.Policy)

@pytest.mark.asyncio
async def test_test_iam_permissions_rest_asyncio_bad_request(request_type=iam_policy_pb2.TestIamPermissionsRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )
    request = request_type()
    request = json_format.ParseDict({'resource': 'projects/sample1/locations/sample2/featurestores/sample3'}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.test_iam_permissions(request)

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
    iam_policy_pb2.TestIamPermissionsRequest,
    dict,
])
async def test_test_iam_permissions_rest_asyncio(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    request_init = {'resource': 'projects/sample1/locations/sample2/featurestores/sample3'}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = iam_policy_pb2.TestIamPermissionsResponse()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = await client.test_iam_permissions(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, iam_policy_pb2.TestIamPermissionsResponse)

@pytest.mark.asyncio
async def test_cancel_operation_rest_asyncio_bad_request(request_type=operations_pb2.CancelOperationRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )
    request = request_type()
    request = json_format.ParseDict({'name': 'projects/sample1/locations/sample2/operations/sample3'}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.cancel_operation(request)

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
    operations_pb2.CancelOperationRequest,
    dict,
])
async def test_cancel_operation_rest_asyncio(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    request_init = {'name': 'projects/sample1/locations/sample2/operations/sample3'}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = '{}'
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = await client.cancel_operation(request)

    # Establish that the response is the type that we expect.
    assert response is None

@pytest.mark.asyncio
async def test_delete_operation_rest_asyncio_bad_request(request_type=operations_pb2.DeleteOperationRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )
    request = request_type()
    request = json_format.ParseDict({'name': 'projects/sample1/locations/sample2/operations/sample3'}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.delete_operation(request)

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
    operations_pb2.DeleteOperationRequest,
    dict,
])
async def test_delete_operation_rest_asyncio(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    request_init = {'name': 'projects/sample1/locations/sample2/operations/sample3'}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = '{}'
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = await client.delete_operation(request)

    # Establish that the response is the type that we expect.
    assert response is None

@pytest.mark.asyncio
async def test_get_operation_rest_asyncio_bad_request(request_type=operations_pb2.GetOperationRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )
    request = request_type()
    request = json_format.ParseDict({'name': 'projects/sample1/locations/sample2/operations/sample3'}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.get_operation(request)

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
    operations_pb2.GetOperationRequest,
    dict,
])
async def test_get_operation_rest_asyncio(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    request_init = {'name': 'projects/sample1/locations/sample2/operations/sample3'}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = await client.get_operation(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.Operation)

@pytest.mark.asyncio
async def test_list_operations_rest_asyncio_bad_request(request_type=operations_pb2.ListOperationsRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )
    request = request_type()
    request = json_format.ParseDict({'name': 'projects/sample1/locations/sample2'}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.list_operations(request)

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
    operations_pb2.ListOperationsRequest,
    dict,
])
async def test_list_operations_rest_asyncio(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    request_init = {'name': 'projects/sample1/locations/sample2'}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.ListOperationsResponse()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = await client.list_operations(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.ListOperationsResponse)

@pytest.mark.asyncio
async def test_wait_operation_rest_asyncio_bad_request(request_type=operations_pb2.WaitOperationRequest):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )
    request = request_type()
    request = json_format.ParseDict({'name': 'projects/sample1/locations/sample2/operations/sample3'}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req, pytest.raises(core_exceptions.BadRequest):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b'{}')
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.wait_operation(request)

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [
    operations_pb2.WaitOperationRequest,
    dict,
])
async def test_wait_operation_rest_asyncio(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    request_init = {'name': 'projects/sample1/locations/sample2/operations/sample3'}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(AsyncAuthorizedSession, 'request') as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(return_value=json_return_value.encode('UTF-8'))

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = await client.wait_operation(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.Operation)

def test_initialize_client_w_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )
    assert client is not None


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_agent_anomaly_detection_scope_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.get_agent_anomaly_detection_scope),
            '__call__') as call:
        await client.get_agent_anomaly_detection_scope(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_monitored_agent_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.get_monitored_agent),
            '__call__') as call:
        await client.get_monitored_agent(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.GetMonitoredAgentRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_monitored_agents_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.list_monitored_agents),
            '__call__') as call:
        await client.list_monitored_agents(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ListMonitoredAgentsRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_enable_monitored_agent_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.enable_monitored_agent),
            '__call__') as call:
        await client.enable_monitored_agent(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.EnableMonitoredAgentRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_disable_monitored_agent_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.disable_monitored_agent),
            '__call__') as call:
        await client.disable_monitored_agent(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.DisableMonitoredAgentRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_delete_agent_anomaly_detection_scope_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.delete_agent_anomaly_detection_scope),
            '__call__') as call:
        await client.delete_agent_anomaly_detection_scope(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_create_agent_anomaly_detection_scope_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.create_agent_anomaly_detection_scope),
            '__call__') as call:
        await client.create_agent_anomaly_detection_scope(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_agent_anomaly_detection_scopes_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.list_agent_anomaly_detection_scopes),
            '__call__') as call:
        await client.list_agent_anomaly_detection_scopes(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_analyzed_sessions_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_sessions),
            '__call__') as call:
        await client.list_analyzed_sessions(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ListAnalyzedSessionsRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_analyzed_session_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.get_analyzed_session),
            '__call__') as call:
        await client.get_analyzed_session(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.GetAnalyzedSessionRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_analyzed_invocations_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.list_analyzed_invocations),
            '__call__') as call:
        await client.list_analyzed_invocations(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ListAnalyzedInvocationsRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_analyzed_invocation_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.get_analyzed_invocation),
            '__call__') as call:
        await client.get_analyzed_invocation(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.GetAnalyzedInvocationRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_aggregate_analyzed_sessions_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.aggregate_analyzed_sessions),
            '__call__') as call:
        await client.aggregate_analyzed_sessions(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest()
        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_clear_training_data_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
            type(client.transport.clear_training_data),
            '__call__') as call:
        await client.clear_training_data(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = agent_anomaly_detection_service.ClearTrainingDataRequest()
        assert args[0] == request_msg


def test_agent_anomaly_detection_service_rest_asyncio_lro_client():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )
    transport = client.transport

    # Ensure that we have an api-core operations client.
    assert isinstance(
        transport.operations_client,
operations_v1.AsyncOperationsRestClient,
    )

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client

def test_unsupported_parameter_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    options = client_options.ClientOptions(quota_project_id="octopus")
    with pytest.raises(core_exceptions.AsyncRestUnsupportedParameterError, match="google.api_core.client_options.ClientOptions.quota_project_id") as exc:  # type: ignore
        client = AgentAnomalyDetectionServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport="rest_asyncio",
            client_options=options
    )


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    assert isinstance(
        client.transport,
        transports.AgentAnomalyDetectionServiceGrpcTransport,
    )

def test_agent_anomaly_detection_service_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(core_exceptions.DuplicateCredentialArgs):
        transport = transports.AgentAnomalyDetectionServiceTransport(
            credentials=ga_credentials.AnonymousCredentials(),
            credentials_file="credentials.json"
        )


def test_agent_anomaly_detection_service_base_transport():
    # Instantiate the base transport.
    with mock.patch('google.cloud.aiplatform_v1.services.agent_anomaly_detection_service.transports.AgentAnomalyDetectionServiceTransport.__init__') as Transport:
        Transport.return_value = None
        transport = transports.AgentAnomalyDetectionServiceTransport(
            credentials=ga_credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        'get_agent_anomaly_detection_scope',
        'get_monitored_agent',
        'list_monitored_agents',
        'enable_monitored_agent',
        'disable_monitored_agent',
        'delete_agent_anomaly_detection_scope',
        'create_agent_anomaly_detection_scope',
        'list_agent_anomaly_detection_scopes',
        'list_analyzed_sessions',
        'get_analyzed_session',
        'list_analyzed_invocations',
        'get_analyzed_invocation',
        'aggregate_analyzed_sessions',
        'clear_training_data',
        'set_iam_policy',
        'get_iam_policy',
        'test_iam_permissions',
        'get_location',
        'list_locations',
        'get_operation',
        'wait_operation',
        'cancel_operation',
        'delete_operation',
        'list_operations',
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
        'kind',
    ]
    for r in remainder:
        with pytest.raises(NotImplementedError):
            getattr(transport, r)()


def test_agent_anomaly_detection_service_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(google.auth, 'load_credentials_from_file', autospec=True) as load_creds, mock.patch('google.cloud.aiplatform_v1.services.agent_anomaly_detection_service.transports.AgentAnomalyDetectionServiceTransport._prep_wrapped_messages') as Transport:
        Transport.return_value = None
        load_creds.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.AgentAnomalyDetectionServiceTransport(
            credentials_file="credentials.json",
            quota_project_id="octopus",
        )
        load_creds.assert_called_once_with("credentials.json",
            scopes=None,
            default_scopes=(
            'https://www.googleapis.com/auth/cloud-platform',
),
            quota_project_id="octopus",
        )


def test_agent_anomaly_detection_service_base_transport_with_adc():
    # Test the default credentials are used if credentials and credentials_file are None.
    with mock.patch.object(google.auth, 'default', autospec=True) as adc, mock.patch('google.cloud.aiplatform_v1.services.agent_anomaly_detection_service.transports.AgentAnomalyDetectionServiceTransport._prep_wrapped_messages') as Transport:
        Transport.return_value = None
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.AgentAnomalyDetectionServiceTransport()
        adc.assert_called_once()


def test_agent_anomaly_detection_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(google.auth, 'default', autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        AgentAnomalyDetectionServiceClient()
        adc.assert_called_once_with(
            scopes=None,
            default_scopes=(
            'https://www.googleapis.com/auth/cloud-platform',
),
            quota_project_id=None,
        )


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.AgentAnomalyDetectionServiceGrpcTransport,
        transports.AgentAnomalyDetectionServiceGrpcAsyncIOTransport,
    ],
)
def test_agent_anomaly_detection_service_transport_auth_adc(transport_class):
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(google.auth, 'default', autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport_class(quota_project_id="octopus", scopes=["1", "2"])
        adc.assert_called_once_with(
            scopes=["1", "2"],
            default_scopes=(                'https://www.googleapis.com/auth/cloud-platform',),
            quota_project_id="octopus",
        )


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.AgentAnomalyDetectionServiceGrpcTransport,
        transports.AgentAnomalyDetectionServiceGrpcAsyncIOTransport,
        transports.AgentAnomalyDetectionServiceRestTransport,
    ],
)
def test_agent_anomaly_detection_service_transport_auth_gdch_credentials(transport_class):
    host = 'https://language.com'
    api_audience_tests = [None, 'https://language2.com']
    api_audience_expect = [host, 'https://language2.com']
    for t, e in zip(api_audience_tests, api_audience_expect):
        with mock.patch.object(google.auth, 'default', autospec=True) as adc:
            gdch_mock = mock.MagicMock()
            type(gdch_mock).with_gdch_audience = mock.PropertyMock(return_value=gdch_mock)
            adc.return_value = (gdch_mock, None)
            transport_class(host=host, api_audience=t)
            gdch_mock.with_gdch_audience.assert_called_once_with(
                e
            )


@pytest.mark.parametrize(
    "transport_class,grpc_helpers",
    [
        (transports.AgentAnomalyDetectionServiceGrpcTransport, grpc_helpers),
        (transports.AgentAnomalyDetectionServiceGrpcAsyncIOTransport, grpc_helpers_async)
    ],
)
def test_agent_anomaly_detection_service_transport_create_channel(transport_class, grpc_helpers):
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc, mock.patch.object(
        grpc_helpers, "create_channel", autospec=True
    ) as create_channel:
        creds = ga_credentials.AnonymousCredentials()
        adc.return_value = (creds, None)
        transport_class(
            quota_project_id="octopus",
            scopes=["1", "2"]
        )

        create_channel.assert_called_with(
            "aiplatform.googleapis.com:443",
            credentials=creds,
            credentials_file=None,
            quota_project_id="octopus",
            default_scopes=(
                'https://www.googleapis.com/auth/cloud-platform',
),
            scopes=["1", "2"],
            default_host="aiplatform.googleapis.com",
            ssl_credentials=None,
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
            ],
        )


@pytest.mark.parametrize("transport_class", [transports.AgentAnomalyDetectionServiceGrpcTransport, transports.AgentAnomalyDetectionServiceGrpcAsyncIOTransport])
def test_agent_anomaly_detection_service_grpc_transport_client_cert_source_for_mtls(
    transport_class
):
    cred = ga_credentials.AnonymousCredentials()

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
                client_cert_source_for_mtls=client_cert_source_callback
            )
            expected_cert, expected_key = client_cert_source_callback()
            mock_ssl_cred.assert_called_once_with(
                certificate_chain=expected_cert,
                private_key=expected_key
            )

def test_agent_anomaly_detection_service_http_transport_client_cert_source_for_mtls():
    cred = ga_credentials.AnonymousCredentials()
    with mock.patch("google.auth.transport.requests.AuthorizedSession.configure_mtls_channel") as mock_configure_mtls_channel:
        transports.AgentAnomalyDetectionServiceRestTransport (
            credentials=cred,
            client_cert_source_for_mtls=client_cert_source_callback
        )
        mock_configure_mtls_channel.assert_called_once_with(client_cert_source_callback)


@pytest.mark.parametrize("transport_name", [
    "grpc",
    "grpc_asyncio",
    "rest",
])
def test_agent_anomaly_detection_service_host_no_port(transport_name):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(api_endpoint='aiplatform.googleapis.com'),
         transport=transport_name,
    )
    assert client.transport._host == (
        'aiplatform.googleapis.com:443'
        if transport_name in ['grpc', 'grpc_asyncio']
        else 'https://aiplatform.googleapis.com'
    )

@pytest.mark.parametrize("transport_name", [
    "grpc",
    "grpc_asyncio",
    "rest",
])
def test_agent_anomaly_detection_service_host_with_port(transport_name):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(api_endpoint='aiplatform.googleapis.com:8000'),
        transport=transport_name,
    )
    assert client.transport._host == (
        'aiplatform.googleapis.com:8000'
        if transport_name in ['grpc', 'grpc_asyncio']
        else 'https://aiplatform.googleapis.com:8000'
    )

@pytest.mark.parametrize("transport_name", [
    "rest",
])
def test_agent_anomaly_detection_service_client_transport_session_collision(transport_name):
    creds1 = ga_credentials.AnonymousCredentials()
    creds2 = ga_credentials.AnonymousCredentials()
    client1 = AgentAnomalyDetectionServiceClient(
        credentials=creds1,
        transport=transport_name,
    )
    client2 = AgentAnomalyDetectionServiceClient(
        credentials=creds2,
        transport=transport_name,
    )
    session1 = client1.transport.get_agent_anomaly_detection_scope._session
    session2 = client2.transport.get_agent_anomaly_detection_scope._session
    assert session1 != session2
    session1 = client1.transport.get_monitored_agent._session
    session2 = client2.transport.get_monitored_agent._session
    assert session1 != session2
    session1 = client1.transport.list_monitored_agents._session
    session2 = client2.transport.list_monitored_agents._session
    assert session1 != session2
    session1 = client1.transport.enable_monitored_agent._session
    session2 = client2.transport.enable_monitored_agent._session
    assert session1 != session2
    session1 = client1.transport.disable_monitored_agent._session
    session2 = client2.transport.disable_monitored_agent._session
    assert session1 != session2
    session1 = client1.transport.delete_agent_anomaly_detection_scope._session
    session2 = client2.transport.delete_agent_anomaly_detection_scope._session
    assert session1 != session2
    session1 = client1.transport.create_agent_anomaly_detection_scope._session
    session2 = client2.transport.create_agent_anomaly_detection_scope._session
    assert session1 != session2
    session1 = client1.transport.list_agent_anomaly_detection_scopes._session
    session2 = client2.transport.list_agent_anomaly_detection_scopes._session
    assert session1 != session2
    session1 = client1.transport.list_analyzed_sessions._session
    session2 = client2.transport.list_analyzed_sessions._session
    assert session1 != session2
    session1 = client1.transport.get_analyzed_session._session
    session2 = client2.transport.get_analyzed_session._session
    assert session1 != session2
    session1 = client1.transport.list_analyzed_invocations._session
    session2 = client2.transport.list_analyzed_invocations._session
    assert session1 != session2
    session1 = client1.transport.get_analyzed_invocation._session
    session2 = client2.transport.get_analyzed_invocation._session
    assert session1 != session2
    session1 = client1.transport.aggregate_analyzed_sessions._session
    session2 = client2.transport.aggregate_analyzed_sessions._session
    assert session1 != session2
    session1 = client1.transport.clear_training_data._session
    session2 = client2.transport.clear_training_data._session
    assert session1 != session2
def test_agent_anomaly_detection_service_grpc_transport_channel():
    channel = grpc.secure_channel('http://localhost/', grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.AgentAnomalyDetectionServiceGrpcTransport(
        host="squid.clam.whelk",
        channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


def test_agent_anomaly_detection_service_grpc_asyncio_transport_channel():
    channel = aio.secure_channel('http://localhost/', grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.AgentAnomalyDetectionServiceGrpcAsyncIOTransport(
        host="squid.clam.whelk",
        channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


# Remove this test when deprecated arguments (api_mtls_endpoint, client_cert_source) are
# removed from grpc/grpc_asyncio transport constructor.
@pytest.mark.filterwarnings("ignore::FutureWarning")
@pytest.mark.parametrize("transport_class", [transports.AgentAnomalyDetectionServiceGrpcTransport, transports.AgentAnomalyDetectionServiceGrpcAsyncIOTransport])
def test_agent_anomaly_detection_service_transport_channel_mtls_with_client_cert_source(
    transport_class
):
    with mock.patch("grpc.ssl_channel_credentials", autospec=True) as grpc_ssl_channel_cred:
        with mock.patch.object(transport_class, "create_channel") as grpc_create_channel:
            mock_ssl_cred = mock.Mock()
            grpc_ssl_channel_cred.return_value = mock_ssl_cred

            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel

            cred = ga_credentials.AnonymousCredentials()
            with pytest.warns(DeprecationWarning):
                with mock.patch.object(google.auth, 'default') as adc:
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
@pytest.mark.parametrize("transport_class", [transports.AgentAnomalyDetectionServiceGrpcTransport, transports.AgentAnomalyDetectionServiceGrpcAsyncIOTransport])
def test_agent_anomaly_detection_service_transport_channel_mtls_with_adc(
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
                scopes=None,
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )
            assert transport.grpc_channel == mock_grpc_channel


def test_agent_anomaly_detection_service_grpc_lro_client():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
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


def test_agent_anomaly_detection_service_grpc_lro_async_client():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=ga_credentials.AnonymousCredentials(),
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


def test_agent_anomaly_detection_scope_path():
    project = "squid"
    location = "clam"
    agent_anomaly_detection_scope = "whelk"
    expected = "projects/{project}/locations/{location}/agentAnomalyDetectionScopes/{agent_anomaly_detection_scope}".format(project=project, location=location, agent_anomaly_detection_scope=agent_anomaly_detection_scope, )
    actual = AgentAnomalyDetectionServiceClient.agent_anomaly_detection_scope_path(project, location, agent_anomaly_detection_scope)
    assert expected == actual


def test_parse_agent_anomaly_detection_scope_path():
    expected = {
        "project": "octopus",
        "location": "oyster",
        "agent_anomaly_detection_scope": "nudibranch",
    }
    path = AgentAnomalyDetectionServiceClient.agent_anomaly_detection_scope_path(**expected)

    # Check that the path construction is reversible.
    actual = AgentAnomalyDetectionServiceClient.parse_agent_anomaly_detection_scope_path(path)
    assert expected == actual

def test_analyzed_invocation_path():
    project = "cuttlefish"
    location = "mussel"
    monitored_agent = "winkle"
    analyzed_session = "nautilus"
    analyzed_invocation = "scallop"
    expected = "projects/{project}/locations/{location}/monitoredAgents/{monitored_agent}/analyzedSessions/{analyzed_session}/analyzedInvocations/{analyzed_invocation}".format(project=project, location=location, monitored_agent=monitored_agent, analyzed_session=analyzed_session, analyzed_invocation=analyzed_invocation, )
    actual = AgentAnomalyDetectionServiceClient.analyzed_invocation_path(project, location, monitored_agent, analyzed_session, analyzed_invocation)
    assert expected == actual


def test_parse_analyzed_invocation_path():
    expected = {
        "project": "abalone",
        "location": "squid",
        "monitored_agent": "clam",
        "analyzed_session": "whelk",
        "analyzed_invocation": "octopus",
    }
    path = AgentAnomalyDetectionServiceClient.analyzed_invocation_path(**expected)

    # Check that the path construction is reversible.
    actual = AgentAnomalyDetectionServiceClient.parse_analyzed_invocation_path(path)
    assert expected == actual

def test_analyzed_session_path():
    project = "oyster"
    location = "nudibranch"
    monitored_agent = "cuttlefish"
    analyzed_session = "mussel"
    expected = "projects/{project}/locations/{location}/monitoredAgents/{monitored_agent}/analyzedSessions/{analyzed_session}".format(project=project, location=location, monitored_agent=monitored_agent, analyzed_session=analyzed_session, )
    actual = AgentAnomalyDetectionServiceClient.analyzed_session_path(project, location, monitored_agent, analyzed_session)
    assert expected == actual


def test_parse_analyzed_session_path():
    expected = {
        "project": "winkle",
        "location": "nautilus",
        "monitored_agent": "scallop",
        "analyzed_session": "abalone",
    }
    path = AgentAnomalyDetectionServiceClient.analyzed_session_path(**expected)

    # Check that the path construction is reversible.
    actual = AgentAnomalyDetectionServiceClient.parse_analyzed_session_path(path)
    assert expected == actual

def test_monitored_agent_path():
    project = "squid"
    location = "clam"
    monitored_agent = "whelk"
    expected = "projects/{project}/locations/{location}/monitoredAgents/{monitored_agent}".format(project=project, location=location, monitored_agent=monitored_agent, )
    actual = AgentAnomalyDetectionServiceClient.monitored_agent_path(project, location, monitored_agent)
    assert expected == actual


def test_parse_monitored_agent_path():
    expected = {
        "project": "octopus",
        "location": "oyster",
        "monitored_agent": "nudibranch",
    }
    path = AgentAnomalyDetectionServiceClient.monitored_agent_path(**expected)

    # Check that the path construction is reversible.
    actual = AgentAnomalyDetectionServiceClient.parse_monitored_agent_path(path)
    assert expected == actual

def test_common_billing_account_path():
    billing_account = "cuttlefish"
    expected = "billingAccounts/{billing_account}".format(billing_account=billing_account, )
    actual = AgentAnomalyDetectionServiceClient.common_billing_account_path(billing_account)
    assert expected == actual


def test_parse_common_billing_account_path():
    expected = {
        "billing_account": "mussel",
    }
    path = AgentAnomalyDetectionServiceClient.common_billing_account_path(**expected)

    # Check that the path construction is reversible.
    actual = AgentAnomalyDetectionServiceClient.parse_common_billing_account_path(path)
    assert expected == actual

def test_common_folder_path():
    folder = "winkle"
    expected = "folders/{folder}".format(folder=folder, )
    actual = AgentAnomalyDetectionServiceClient.common_folder_path(folder)
    assert expected == actual


def test_parse_common_folder_path():
    expected = {
        "folder": "nautilus",
    }
    path = AgentAnomalyDetectionServiceClient.common_folder_path(**expected)

    # Check that the path construction is reversible.
    actual = AgentAnomalyDetectionServiceClient.parse_common_folder_path(path)
    assert expected == actual

def test_common_organization_path():
    organization = "scallop"
    expected = "organizations/{organization}".format(organization=organization, )
    actual = AgentAnomalyDetectionServiceClient.common_organization_path(organization)
    assert expected == actual


def test_parse_common_organization_path():
    expected = {
        "organization": "abalone",
    }
    path = AgentAnomalyDetectionServiceClient.common_organization_path(**expected)

    # Check that the path construction is reversible.
    actual = AgentAnomalyDetectionServiceClient.parse_common_organization_path(path)
    assert expected == actual

def test_common_project_path():
    project = "squid"
    expected = "projects/{project}".format(project=project, )
    actual = AgentAnomalyDetectionServiceClient.common_project_path(project)
    assert expected == actual


def test_parse_common_project_path():
    expected = {
        "project": "clam",
    }
    path = AgentAnomalyDetectionServiceClient.common_project_path(**expected)

    # Check that the path construction is reversible.
    actual = AgentAnomalyDetectionServiceClient.parse_common_project_path(path)
    assert expected == actual

def test_common_location_path():
    project = "whelk"
    location = "octopus"
    expected = "projects/{project}/locations/{location}".format(project=project, location=location, )
    actual = AgentAnomalyDetectionServiceClient.common_location_path(project, location)
    assert expected == actual


def test_parse_common_location_path():
    expected = {
        "project": "oyster",
        "location": "nudibranch",
    }
    path = AgentAnomalyDetectionServiceClient.common_location_path(**expected)

    # Check that the path construction is reversible.
    actual = AgentAnomalyDetectionServiceClient.parse_common_location_path(path)
    assert expected == actual


def test_client_with_default_client_info():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(transports.AgentAnomalyDetectionServiceTransport, '_prep_wrapped_messages') as prep:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(transports.AgentAnomalyDetectionServiceTransport, '_prep_wrapped_messages') as prep:
        transport_class = AgentAnomalyDetectionServiceClient.get_transport_class()
        transport = transport_class(
            credentials=ga_credentials.AnonymousCredentials(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)


def test_delete_operation(transport: str = "grpc"):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
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
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.DeleteOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            None
        )
        response = await client.delete_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_operation_field_headers():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.DeleteOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        call.return_value =  None

        client.delete_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=locations",) in kw["metadata"]

@pytest.mark.asyncio
async def test_delete_operation_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.DeleteOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            None
        )
        await client.delete_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=locations",) in kw["metadata"]


def test_delete_operation_from_dict():
    client = AgentAnomalyDetectionServiceClient(
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
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            None
        )
        response = await client.delete_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


def test_delete_operation_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        client.delete_operation()
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == operations_pb2.DeleteOperationRequest()

@pytest.mark.asyncio
async def test_delete_operation_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            None
        )
        await client.delete_operation()
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == operations_pb2.DeleteOperationRequest()


def test_cancel_operation(transport: str = "grpc"):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
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
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.CancelOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            None
        )
        response = await client.cancel_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_cancel_operation_field_headers():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.CancelOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        call.return_value =  None

        client.cancel_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=locations",) in kw["metadata"]

@pytest.mark.asyncio
async def test_cancel_operation_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.CancelOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            None
        )
        await client.cancel_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=locations",) in kw["metadata"]


def test_cancel_operation_from_dict():
    client = AgentAnomalyDetectionServiceClient(
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
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            None
        )
        response = await client.cancel_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


def test_cancel_operation_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        client.cancel_operation()
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == operations_pb2.CancelOperationRequest()

@pytest.mark.asyncio
async def test_cancel_operation_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            None
        )
        await client.cancel_operation()
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == operations_pb2.CancelOperationRequest()


def test_wait_operation(transport: str = "grpc"):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
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
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport=transport,
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
    client = AgentAnomalyDetectionServiceClient(
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
    assert ("x-goog-request-params", "name=locations",) in kw["metadata"]

@pytest.mark.asyncio
async def test_wait_operation_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    assert ("x-goog-request-params", "name=locations",) in kw["metadata"]


def test_wait_operation_from_dict():
    client = AgentAnomalyDetectionServiceClient(
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
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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


def test_wait_operation_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.wait_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation()

        client.wait_operation()
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == operations_pb2.WaitOperationRequest()

@pytest.mark.asyncio
async def test_wait_operation_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.wait_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation()
        )
        await client.wait_operation()
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == operations_pb2.WaitOperationRequest()


def test_get_operation(transport: str = "grpc"):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
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
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport=transport,
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
    client = AgentAnomalyDetectionServiceClient(
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
    assert ("x-goog-request-params", "name=locations",) in kw["metadata"]

@pytest.mark.asyncio
async def test_get_operation_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    assert ("x-goog-request-params", "name=locations",) in kw["metadata"]


def test_get_operation_from_dict():
    client = AgentAnomalyDetectionServiceClient(
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
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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


def test_get_operation_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation()

        client.get_operation()
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == operations_pb2.GetOperationRequest()

@pytest.mark.asyncio
async def test_get_operation_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation()
        )
        await client.get_operation()
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == operations_pb2.GetOperationRequest()


def test_list_operations(transport: str = "grpc"):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
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
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport=transport,
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
    client = AgentAnomalyDetectionServiceClient(
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
    assert ("x-goog-request-params", "name=locations",) in kw["metadata"]

@pytest.mark.asyncio
async def test_list_operations_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    assert ("x-goog-request-params", "name=locations",) in kw["metadata"]


def test_list_operations_from_dict():
    client = AgentAnomalyDetectionServiceClient(
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
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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


def test_list_operations_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.ListOperationsResponse()

        client.list_operations()
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == operations_pb2.ListOperationsRequest()

@pytest.mark.asyncio
async def test_list_operations_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.ListOperationsResponse()
        )
        await client.list_operations()
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == operations_pb2.ListOperationsRequest()


def test_list_locations(transport: str = "grpc"):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
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
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport=transport,
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
    client = AgentAnomalyDetectionServiceClient(
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
    assert ("x-goog-request-params", "name=locations",) in kw["metadata"]

@pytest.mark.asyncio
async def test_list_locations_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    assert ("x-goog-request-params", "name=locations",) in kw["metadata"]


def test_list_locations_from_dict():
    client = AgentAnomalyDetectionServiceClient(
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
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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


def test_list_locations_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_locations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = locations_pb2.ListLocationsResponse()

        client.list_locations()
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == locations_pb2.ListLocationsRequest()

@pytest.mark.asyncio
async def test_list_locations_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_locations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            locations_pb2.ListLocationsResponse()
        )
        await client.list_locations()
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == locations_pb2.ListLocationsRequest()


def test_get_location(transport: str = "grpc"):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
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
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport=transport,
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
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials())

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
    assert ("x-goog-request-params", "name=locations/abc",) in kw["metadata"]

@pytest.mark.asyncio
async def test_get_location_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials()
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
    assert ("x-goog-request-params", "name=locations/abc",) in kw["metadata"]


def test_get_location_from_dict():
    client = AgentAnomalyDetectionServiceClient(
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
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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


def test_get_location_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_location), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = locations_pb2.Location()

        client.get_location()
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == locations_pb2.GetLocationRequest()

@pytest.mark.asyncio
async def test_get_location_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_location), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            locations_pb2.Location()
        )
        await client.get_location()
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == locations_pb2.GetLocationRequest()


def test_set_iam_policy(transport: str = "grpc"):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = iam_policy_pb2.SetIamPolicyRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy_pb2.Policy(version=774, etag=b"etag_blob",)
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
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = iam_policy_pb2.SetIamPolicyRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            policy_pb2.Policy(version=774, etag=b"etag_blob",)
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
    client = AgentAnomalyDetectionServiceClient(
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
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]

@pytest.mark.asyncio
async def test_set_iam_policy_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


def test_set_iam_policy_from_dict():
    client = AgentAnomalyDetectionServiceClient(
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
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            policy_pb2.Policy()
        )

        response = await client.set_iam_policy(
            request={
                "resource": "resource_value",
                "policy": policy_pb2.Policy(version=774),
            }
        )
        call.assert_called()


def test_set_iam_policy_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy_pb2.Policy()

        client.set_iam_policy()

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == iam_policy_pb2.SetIamPolicyRequest()


@pytest.mark.asyncio
async def test_set_iam_policy_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            policy_pb2.Policy()
        )

        await client.set_iam_policy()

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == iam_policy_pb2.SetIamPolicyRequest()

def test_get_iam_policy(transport: str = "grpc"):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = iam_policy_pb2.GetIamPolicyRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy_pb2.Policy(version=774, etag=b"etag_blob",)

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
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = iam_policy_pb2.GetIamPolicyRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_iam_policy), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            policy_pb2.Policy(version=774, etag=b"etag_blob",)
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
    client = AgentAnomalyDetectionServiceClient(
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
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_iam_policy_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy_pb2.GetIamPolicyRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_iam_policy), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(policy_pb2.Policy())

        await client.get_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


def test_get_iam_policy_from_dict():
    client = AgentAnomalyDetectionServiceClient(
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
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            policy_pb2.Policy()
        )

        response = await client.get_iam_policy(
            request={
                "resource": "resource_value",
                "options": options_pb2.GetPolicyOptions(requested_policy_version=2598),
            }
        )
        call.assert_called()


def test_get_iam_policy_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy_pb2.Policy()

        client.get_iam_policy()

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == iam_policy_pb2.GetIamPolicyRequest()


@pytest.mark.asyncio
async def test_get_iam_policy_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            policy_pb2.Policy()
        )

        await client.get_iam_policy()

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == iam_policy_pb2.GetIamPolicyRequest()

def test_test_iam_permissions(transport: str = "grpc"):
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport=transport,
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
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport=transport,
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
            iam_policy_pb2.TestIamPermissionsResponse(permissions=["permissions_value"],)
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
    client = AgentAnomalyDetectionServiceClient(
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
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_test_iam_permissions_field_headers_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


def test_test_iam_permissions_from_dict():
    client = AgentAnomalyDetectionServiceClient(
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
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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


def test_test_iam_permissions_flattened():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.test_iam_permissions), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = iam_policy_pb2.TestIamPermissionsResponse()

        client.test_iam_permissions()

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == iam_policy_pb2.TestIamPermissionsRequest()


@pytest.mark.asyncio
async def test_test_iam_permissions_flattened_async():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.test_iam_permissions), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            iam_policy_pb2.TestIamPermissionsResponse()
        )

        await client.test_iam_permissions()

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == iam_policy_pb2.TestIamPermissionsRequest()


def test_transport_close_grpc():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc"
    )
    with mock.patch.object(type(getattr(client.transport, "_grpc_channel")), "close") as close:
        with client:
            close.assert_not_called()
        close.assert_called_once()


@pytest.mark.asyncio
async def test_transport_close_grpc_asyncio():
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio"
    )
    with mock.patch.object(type(getattr(client.transport, "_grpc_channel")), "close") as close:
        async with client:
            close.assert_not_called()
        close.assert_called_once()


def test_transport_close_rest():
    client = AgentAnomalyDetectionServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest"
    )
    with mock.patch.object(type(getattr(client.transport, "_session")), "close") as close:
        with client:
            close.assert_not_called()
        close.assert_called_once()


@pytest.mark.asyncio
async def test_transport_close_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip("the library must be installed with the `async_rest` extra to test this feature.")
    client = AgentAnomalyDetectionServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio"
    )
    with mock.patch.object(type(getattr(client.transport, "_session")), "close") as close:
        async with client:
            close.assert_not_called()
        close.assert_called_once()


def test_client_ctx():
    transports = [
        'rest',
        'grpc',
    ]
    for transport in transports:
        client = AgentAnomalyDetectionServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport=transport
        )
        # Test client calls underlying transport.
        with mock.patch.object(type(client.transport), "close") as close:
            close.assert_not_called()
            with client:
                pass
            close.assert_called()

@pytest.mark.parametrize("client_class,transport_class", [
    (AgentAnomalyDetectionServiceClient, transports.AgentAnomalyDetectionServiceGrpcTransport),
    (AgentAnomalyDetectionServiceAsyncClient, transports.AgentAnomalyDetectionServiceGrpcAsyncIOTransport),
])
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
                host=client._DEFAULT_ENDPOINT_TEMPLATE.format(UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE),
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
                always_use_jwt_access=True,
                api_audience=None,
            )
