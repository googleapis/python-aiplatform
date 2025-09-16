# -*- coding: utf-8 -*-
# Copyright 2025 Google LLC
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
from collections.abc import Iterable, AsyncIterable
from google.protobuf import json_format
import json
import math
import pytest
from google.api_core import api_core_version
from proto.marshal.rules.dates import DurationRule, TimestampRule
from proto.marshal.rules import wrappers

try:
    import aiohttp  # type: ignore
    from google.auth.aio.transport.sessions import AsyncAuthorizedSession
    from google.api_core.operations_v1 import AsyncOperationsRestClient

    HAS_ASYNC_REST_EXTRA = True
except ImportError:  # pragma: NO COVER
    HAS_ASYNC_REST_EXTRA = False
from requests import Response
from requests import Request, PreparedRequest
from requests.sessions import Session
from google.protobuf import json_format

try:
    from google.auth.aio import credentials as ga_credentials_async

    HAS_GOOGLE_AUTH_AIO = True
except ImportError:  # pragma: NO COVER
    HAS_GOOGLE_AUTH_AIO = False

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
from google.api_core import retry as retries
from google.auth import credentials as ga_credentials
from google.auth.exceptions import MutualTLSChannelError
from google.cloud.aiplatform_v1beta1.services.vertex_rag_data_service import (
    VertexRagDataServiceAsyncClient,
)
from google.cloud.aiplatform_v1beta1.services.vertex_rag_data_service import (
    VertexRagDataServiceClient,
)
from google.cloud.aiplatform_v1beta1.services.vertex_rag_data_service import pagers
from google.cloud.aiplatform_v1beta1.services.vertex_rag_data_service import transports
from google.cloud.aiplatform_v1beta1.types import api_auth
from google.cloud.aiplatform_v1beta1.types import encryption_spec
from google.cloud.aiplatform_v1beta1.types import io
from google.cloud.aiplatform_v1beta1.types import operation as gca_operation
from google.cloud.aiplatform_v1beta1.types import vertex_rag_data
from google.cloud.aiplatform_v1beta1.types import vertex_rag_data_service
from google.cloud.location import locations_pb2
from google.iam.v1 import iam_policy_pb2  # type: ignore
from google.iam.v1 import options_pb2  # type: ignore
from google.iam.v1 import policy_pb2  # type: ignore
from google.longrunning import operations_pb2  # type: ignore
from google.oauth2 import service_account
from google.protobuf import empty_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
from google.rpc import status_pb2  # type: ignore
import google.auth


CRED_INFO_JSON = {
    "credential_source": "/path/to/file",
    "credential_type": "service account credentials",
    "principal": "service-account@example.com",
}
CRED_INFO_STRING = json.dumps(CRED_INFO_JSON)


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

    assert VertexRagDataServiceClient._get_default_mtls_endpoint(None) is None
    assert (
        VertexRagDataServiceClient._get_default_mtls_endpoint(api_endpoint)
        == api_mtls_endpoint
    )
    assert (
        VertexRagDataServiceClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        VertexRagDataServiceClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        VertexRagDataServiceClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        VertexRagDataServiceClient._get_default_mtls_endpoint(non_googleapi)
        == non_googleapi
    )


def test__read_environment_variables():
    assert VertexRagDataServiceClient._read_environment_variables() == (
        False,
        "auto",
        None,
    )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        assert VertexRagDataServiceClient._read_environment_variables() == (
            True,
            "auto",
            None,
        )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "false"}):
        assert VertexRagDataServiceClient._read_environment_variables() == (
            False,
            "auto",
            None,
        )

    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}
    ):
        with pytest.raises(ValueError) as excinfo:
            VertexRagDataServiceClient._read_environment_variables()
    assert (
        str(excinfo.value)
        == "Environment variable `GOOGLE_API_USE_CLIENT_CERTIFICATE` must be either `true` or `false`"
    )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        assert VertexRagDataServiceClient._read_environment_variables() == (
            False,
            "never",
            None,
        )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        assert VertexRagDataServiceClient._read_environment_variables() == (
            False,
            "always",
            None,
        )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"}):
        assert VertexRagDataServiceClient._read_environment_variables() == (
            False,
            "auto",
            None,
        )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError) as excinfo:
            VertexRagDataServiceClient._read_environment_variables()
    assert (
        str(excinfo.value)
        == "Environment variable `GOOGLE_API_USE_MTLS_ENDPOINT` must be `never`, `auto` or `always`"
    )

    with mock.patch.dict(os.environ, {"GOOGLE_CLOUD_UNIVERSE_DOMAIN": "foo.com"}):
        assert VertexRagDataServiceClient._read_environment_variables() == (
            False,
            "auto",
            "foo.com",
        )


def test__get_client_cert_source():
    mock_provided_cert_source = mock.Mock()
    mock_default_cert_source = mock.Mock()

    assert VertexRagDataServiceClient._get_client_cert_source(None, False) is None
    assert (
        VertexRagDataServiceClient._get_client_cert_source(
            mock_provided_cert_source, False
        )
        is None
    )
    assert (
        VertexRagDataServiceClient._get_client_cert_source(
            mock_provided_cert_source, True
        )
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
                VertexRagDataServiceClient._get_client_cert_source(None, True)
                is mock_default_cert_source
            )
            assert (
                VertexRagDataServiceClient._get_client_cert_source(
                    mock_provided_cert_source, "true"
                )
                is mock_provided_cert_source
            )


@mock.patch.object(
    VertexRagDataServiceClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(VertexRagDataServiceClient),
)
@mock.patch.object(
    VertexRagDataServiceAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(VertexRagDataServiceAsyncClient),
)
def test__get_api_endpoint():
    api_override = "foo.com"
    mock_client_cert_source = mock.Mock()
    default_universe = VertexRagDataServiceClient._DEFAULT_UNIVERSE
    default_endpoint = VertexRagDataServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(
        UNIVERSE_DOMAIN=default_universe
    )
    mock_universe = "bar.com"
    mock_endpoint = VertexRagDataServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(
        UNIVERSE_DOMAIN=mock_universe
    )

    assert (
        VertexRagDataServiceClient._get_api_endpoint(
            api_override, mock_client_cert_source, default_universe, "always"
        )
        == api_override
    )
    assert (
        VertexRagDataServiceClient._get_api_endpoint(
            None, mock_client_cert_source, default_universe, "auto"
        )
        == VertexRagDataServiceClient.DEFAULT_MTLS_ENDPOINT
    )
    assert (
        VertexRagDataServiceClient._get_api_endpoint(
            None, None, default_universe, "auto"
        )
        == default_endpoint
    )
    assert (
        VertexRagDataServiceClient._get_api_endpoint(
            None, None, default_universe, "always"
        )
        == VertexRagDataServiceClient.DEFAULT_MTLS_ENDPOINT
    )
    assert (
        VertexRagDataServiceClient._get_api_endpoint(
            None, mock_client_cert_source, default_universe, "always"
        )
        == VertexRagDataServiceClient.DEFAULT_MTLS_ENDPOINT
    )
    assert (
        VertexRagDataServiceClient._get_api_endpoint(None, None, mock_universe, "never")
        == mock_endpoint
    )
    assert (
        VertexRagDataServiceClient._get_api_endpoint(
            None, None, default_universe, "never"
        )
        == default_endpoint
    )

    with pytest.raises(MutualTLSChannelError) as excinfo:
        VertexRagDataServiceClient._get_api_endpoint(
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
        VertexRagDataServiceClient._get_universe_domain(
            client_universe_domain, universe_domain_env
        )
        == client_universe_domain
    )
    assert (
        VertexRagDataServiceClient._get_universe_domain(None, universe_domain_env)
        == universe_domain_env
    )
    assert (
        VertexRagDataServiceClient._get_universe_domain(None, None)
        == VertexRagDataServiceClient._DEFAULT_UNIVERSE
    )

    with pytest.raises(ValueError) as excinfo:
        VertexRagDataServiceClient._get_universe_domain("", None)
    assert str(excinfo.value) == "Universe Domain cannot be an empty string."


@pytest.mark.parametrize(
    "error_code,cred_info_json,show_cred_info",
    [
        (401, CRED_INFO_JSON, True),
        (403, CRED_INFO_JSON, True),
        (404, CRED_INFO_JSON, True),
        (500, CRED_INFO_JSON, False),
        (401, None, False),
        (403, None, False),
        (404, None, False),
        (500, None, False),
    ],
)
def test__add_cred_info_for_auth_errors(error_code, cred_info_json, show_cred_info):
    cred = mock.Mock(["get_cred_info"])
    cred.get_cred_info = mock.Mock(return_value=cred_info_json)
    client = VertexRagDataServiceClient(credentials=cred)
    client._transport._credentials = cred

    error = core_exceptions.GoogleAPICallError("message", details=["foo"])
    error.code = error_code

    client._add_cred_info_for_auth_errors(error)
    if show_cred_info:
        assert error.details == ["foo", CRED_INFO_STRING]
    else:
        assert error.details == ["foo"]


@pytest.mark.parametrize("error_code", [401, 403, 404, 500])
def test__add_cred_info_for_auth_errors_no_get_cred_info(error_code):
    cred = mock.Mock([])
    assert not hasattr(cred, "get_cred_info")
    client = VertexRagDataServiceClient(credentials=cred)
    client._transport._credentials = cred

    error = core_exceptions.GoogleAPICallError("message", details=[])
    error.code = error_code

    client._add_cred_info_for_auth_errors(error)
    assert error.details == []


@pytest.mark.parametrize(
    "client_class,transport_name",
    [
        (VertexRagDataServiceClient, "grpc"),
        (VertexRagDataServiceAsyncClient, "grpc_asyncio"),
        (VertexRagDataServiceClient, "rest"),
    ],
)
def test_vertex_rag_data_service_client_from_service_account_info(
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
        (transports.VertexRagDataServiceGrpcTransport, "grpc"),
        (transports.VertexRagDataServiceGrpcAsyncIOTransport, "grpc_asyncio"),
        (transports.VertexRagDataServiceRestTransport, "rest"),
    ],
)
def test_vertex_rag_data_service_client_service_account_always_use_jwt(
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
        (VertexRagDataServiceClient, "grpc"),
        (VertexRagDataServiceAsyncClient, "grpc_asyncio"),
        (VertexRagDataServiceClient, "rest"),
    ],
)
def test_vertex_rag_data_service_client_from_service_account_file(
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


def test_vertex_rag_data_service_client_get_transport_class():
    transport = VertexRagDataServiceClient.get_transport_class()
    available_transports = [
        transports.VertexRagDataServiceGrpcTransport,
        transports.VertexRagDataServiceRestTransport,
    ]
    assert transport in available_transports

    transport = VertexRagDataServiceClient.get_transport_class("grpc")
    assert transport == transports.VertexRagDataServiceGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (
            VertexRagDataServiceClient,
            transports.VertexRagDataServiceGrpcTransport,
            "grpc",
        ),
        (
            VertexRagDataServiceAsyncClient,
            transports.VertexRagDataServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
        (
            VertexRagDataServiceClient,
            transports.VertexRagDataServiceRestTransport,
            "rest",
        ),
    ],
)
@mock.patch.object(
    VertexRagDataServiceClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(VertexRagDataServiceClient),
)
@mock.patch.object(
    VertexRagDataServiceAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(VertexRagDataServiceAsyncClient),
)
def test_vertex_rag_data_service_client_client_options(
    client_class, transport_class, transport_name
):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(VertexRagDataServiceClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=ga_credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(VertexRagDataServiceClient, "get_transport_class") as gtc:
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
            VertexRagDataServiceClient,
            transports.VertexRagDataServiceGrpcTransport,
            "grpc",
            "true",
        ),
        (
            VertexRagDataServiceAsyncClient,
            transports.VertexRagDataServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "true",
        ),
        (
            VertexRagDataServiceClient,
            transports.VertexRagDataServiceGrpcTransport,
            "grpc",
            "false",
        ),
        (
            VertexRagDataServiceAsyncClient,
            transports.VertexRagDataServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "false",
        ),
        (
            VertexRagDataServiceClient,
            transports.VertexRagDataServiceRestTransport,
            "rest",
            "true",
        ),
        (
            VertexRagDataServiceClient,
            transports.VertexRagDataServiceRestTransport,
            "rest",
            "false",
        ),
    ],
)
@mock.patch.object(
    VertexRagDataServiceClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(VertexRagDataServiceClient),
)
@mock.patch.object(
    VertexRagDataServiceAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(VertexRagDataServiceAsyncClient),
)
@mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"})
def test_vertex_rag_data_service_client_mtls_env_auto(
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
    "client_class", [VertexRagDataServiceClient, VertexRagDataServiceAsyncClient]
)
@mock.patch.object(
    VertexRagDataServiceClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(VertexRagDataServiceClient),
)
@mock.patch.object(
    VertexRagDataServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(VertexRagDataServiceAsyncClient),
)
def test_vertex_rag_data_service_client_get_mtls_endpoint_and_cert_source(client_class):
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
                api_endpoint, cert_source = (
                    client_class.get_mtls_endpoint_and_cert_source()
                )
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
    "client_class", [VertexRagDataServiceClient, VertexRagDataServiceAsyncClient]
)
@mock.patch.object(
    VertexRagDataServiceClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(VertexRagDataServiceClient),
)
@mock.patch.object(
    VertexRagDataServiceAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(VertexRagDataServiceAsyncClient),
)
def test_vertex_rag_data_service_client_client_api_endpoint(client_class):
    mock_client_cert_source = client_cert_source_callback
    api_override = "foo.com"
    default_universe = VertexRagDataServiceClient._DEFAULT_UNIVERSE
    default_endpoint = VertexRagDataServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(
        UNIVERSE_DOMAIN=default_universe
    )
    mock_universe = "bar.com"
    mock_endpoint = VertexRagDataServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(
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
        (
            VertexRagDataServiceClient,
            transports.VertexRagDataServiceGrpcTransport,
            "grpc",
        ),
        (
            VertexRagDataServiceAsyncClient,
            transports.VertexRagDataServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
        (
            VertexRagDataServiceClient,
            transports.VertexRagDataServiceRestTransport,
            "rest",
        ),
    ],
)
def test_vertex_rag_data_service_client_client_options_scopes(
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
            VertexRagDataServiceClient,
            transports.VertexRagDataServiceGrpcTransport,
            "grpc",
            grpc_helpers,
        ),
        (
            VertexRagDataServiceAsyncClient,
            transports.VertexRagDataServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            grpc_helpers_async,
        ),
        (
            VertexRagDataServiceClient,
            transports.VertexRagDataServiceRestTransport,
            "rest",
            None,
        ),
    ],
)
def test_vertex_rag_data_service_client_client_options_credentials_file(
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


def test_vertex_rag_data_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.vertex_rag_data_service.transports.VertexRagDataServiceGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = VertexRagDataServiceClient(
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
            VertexRagDataServiceClient,
            transports.VertexRagDataServiceGrpcTransport,
            "grpc",
            grpc_helpers,
        ),
        (
            VertexRagDataServiceAsyncClient,
            transports.VertexRagDataServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            grpc_helpers_async,
        ),
    ],
)
def test_vertex_rag_data_service_client_create_channel_credentials_file(
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
        vertex_rag_data_service.CreateRagCorpusRequest,
        dict,
    ],
)
def test_create_rag_corpus(request_type, transport: str = "grpc"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_rag_corpus), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.create_rag_corpus(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.CreateRagCorpusRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_create_rag_corpus_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = vertex_rag_data_service.CreateRagCorpusRequest(
        parent="parent_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_rag_corpus), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.create_rag_corpus(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == vertex_rag_data_service.CreateRagCorpusRequest(
            parent="parent_value",
        )


def test_create_rag_corpus_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.create_rag_corpus in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.create_rag_corpus] = (
            mock_rpc
        )
        request = {}
        client.create_rag_corpus(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.create_rag_corpus(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_create_rag_corpus_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.create_rag_corpus
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.create_rag_corpus
        ] = mock_rpc

        request = {}
        await client.create_rag_corpus(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.create_rag_corpus(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_create_rag_corpus_async(
    transport: str = "grpc_asyncio",
    request_type=vertex_rag_data_service.CreateRagCorpusRequest,
):
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_rag_corpus), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.create_rag_corpus(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.CreateRagCorpusRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_create_rag_corpus_async_from_dict():
    await test_create_rag_corpus_async(request_type=dict)


def test_create_rag_corpus_field_headers():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.CreateRagCorpusRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_rag_corpus), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.create_rag_corpus(request)

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
async def test_create_rag_corpus_field_headers_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.CreateRagCorpusRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_rag_corpus), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.create_rag_corpus(request)

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


def test_create_rag_corpus_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_rag_corpus), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_rag_corpus(
            parent="parent_value",
            rag_corpus=vertex_rag_data.RagCorpus(
                vector_db_config=vertex_rag_data.RagVectorDbConfig(
                    rag_managed_db=vertex_rag_data.RagVectorDbConfig.RagManagedDb(
                        knn=None
                    )
                )
            ),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].rag_corpus
        mock_val = vertex_rag_data.RagCorpus(
            vector_db_config=vertex_rag_data.RagVectorDbConfig(
                rag_managed_db=vertex_rag_data.RagVectorDbConfig.RagManagedDb(knn=None)
            )
        )
        assert arg == mock_val


def test_create_rag_corpus_flattened_error():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_rag_corpus(
            vertex_rag_data_service.CreateRagCorpusRequest(),
            parent="parent_value",
            rag_corpus=vertex_rag_data.RagCorpus(
                vector_db_config=vertex_rag_data.RagVectorDbConfig(
                    rag_managed_db=vertex_rag_data.RagVectorDbConfig.RagManagedDb(
                        knn=None
                    )
                )
            ),
        )


@pytest.mark.asyncio
async def test_create_rag_corpus_flattened_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_rag_corpus), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_rag_corpus(
            parent="parent_value",
            rag_corpus=vertex_rag_data.RagCorpus(
                vector_db_config=vertex_rag_data.RagVectorDbConfig(
                    rag_managed_db=vertex_rag_data.RagVectorDbConfig.RagManagedDb(
                        knn=None
                    )
                )
            ),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].rag_corpus
        mock_val = vertex_rag_data.RagCorpus(
            vector_db_config=vertex_rag_data.RagVectorDbConfig(
                rag_managed_db=vertex_rag_data.RagVectorDbConfig.RagManagedDb(knn=None)
            )
        )
        assert arg == mock_val


@pytest.mark.asyncio
async def test_create_rag_corpus_flattened_error_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_rag_corpus(
            vertex_rag_data_service.CreateRagCorpusRequest(),
            parent="parent_value",
            rag_corpus=vertex_rag_data.RagCorpus(
                vector_db_config=vertex_rag_data.RagVectorDbConfig(
                    rag_managed_db=vertex_rag_data.RagVectorDbConfig.RagManagedDb(
                        knn=None
                    )
                )
            ),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.UpdateRagCorpusRequest,
        dict,
    ],
)
def test_update_rag_corpus(request_type, transport: str = "grpc"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_rag_corpus), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.update_rag_corpus(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.UpdateRagCorpusRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_update_rag_corpus_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = vertex_rag_data_service.UpdateRagCorpusRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_rag_corpus), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.update_rag_corpus(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == vertex_rag_data_service.UpdateRagCorpusRequest()


def test_update_rag_corpus_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.update_rag_corpus in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.update_rag_corpus] = (
            mock_rpc
        )
        request = {}
        client.update_rag_corpus(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.update_rag_corpus(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_update_rag_corpus_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.update_rag_corpus
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.update_rag_corpus
        ] = mock_rpc

        request = {}
        await client.update_rag_corpus(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.update_rag_corpus(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_update_rag_corpus_async(
    transport: str = "grpc_asyncio",
    request_type=vertex_rag_data_service.UpdateRagCorpusRequest,
):
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_rag_corpus), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.update_rag_corpus(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.UpdateRagCorpusRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_update_rag_corpus_async_from_dict():
    await test_update_rag_corpus_async(request_type=dict)


def test_update_rag_corpus_field_headers():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.UpdateRagCorpusRequest()

    request.rag_corpus.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_rag_corpus), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.update_rag_corpus(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "rag_corpus.name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_rag_corpus_field_headers_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.UpdateRagCorpusRequest()

    request.rag_corpus.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_rag_corpus), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.update_rag_corpus(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "rag_corpus.name=name_value",
    ) in kw["metadata"]


def test_update_rag_corpus_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_rag_corpus), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_rag_corpus(
            rag_corpus=vertex_rag_data.RagCorpus(
                vector_db_config=vertex_rag_data.RagVectorDbConfig(
                    rag_managed_db=vertex_rag_data.RagVectorDbConfig.RagManagedDb(
                        knn=None
                    )
                )
            ),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].rag_corpus
        mock_val = vertex_rag_data.RagCorpus(
            vector_db_config=vertex_rag_data.RagVectorDbConfig(
                rag_managed_db=vertex_rag_data.RagVectorDbConfig.RagManagedDb(knn=None)
            )
        )
        assert arg == mock_val


def test_update_rag_corpus_flattened_error():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_rag_corpus(
            vertex_rag_data_service.UpdateRagCorpusRequest(),
            rag_corpus=vertex_rag_data.RagCorpus(
                vector_db_config=vertex_rag_data.RagVectorDbConfig(
                    rag_managed_db=vertex_rag_data.RagVectorDbConfig.RagManagedDb(
                        knn=None
                    )
                )
            ),
        )


@pytest.mark.asyncio
async def test_update_rag_corpus_flattened_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_rag_corpus), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_rag_corpus(
            rag_corpus=vertex_rag_data.RagCorpus(
                vector_db_config=vertex_rag_data.RagVectorDbConfig(
                    rag_managed_db=vertex_rag_data.RagVectorDbConfig.RagManagedDb(
                        knn=None
                    )
                )
            ),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].rag_corpus
        mock_val = vertex_rag_data.RagCorpus(
            vector_db_config=vertex_rag_data.RagVectorDbConfig(
                rag_managed_db=vertex_rag_data.RagVectorDbConfig.RagManagedDb(knn=None)
            )
        )
        assert arg == mock_val


@pytest.mark.asyncio
async def test_update_rag_corpus_flattened_error_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_rag_corpus(
            vertex_rag_data_service.UpdateRagCorpusRequest(),
            rag_corpus=vertex_rag_data.RagCorpus(
                vector_db_config=vertex_rag_data.RagVectorDbConfig(
                    rag_managed_db=vertex_rag_data.RagVectorDbConfig.RagManagedDb(
                        knn=None
                    )
                )
            ),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.GetRagCorpusRequest,
        dict,
    ],
)
def test_get_rag_corpus(request_type, transport: str = "grpc"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_rag_corpus), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = vertex_rag_data.RagCorpus(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            rag_files_count=1588,
        )
        response = client.get_rag_corpus(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.GetRagCorpusRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, vertex_rag_data.RagCorpus)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.rag_files_count == 1588


def test_get_rag_corpus_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = vertex_rag_data_service.GetRagCorpusRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_rag_corpus), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.get_rag_corpus(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == vertex_rag_data_service.GetRagCorpusRequest(
            name="name_value",
        )


def test_get_rag_corpus_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.get_rag_corpus in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.get_rag_corpus] = mock_rpc
        request = {}
        client.get_rag_corpus(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_rag_corpus(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_get_rag_corpus_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.get_rag_corpus
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.get_rag_corpus
        ] = mock_rpc

        request = {}
        await client.get_rag_corpus(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.get_rag_corpus(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_get_rag_corpus_async(
    transport: str = "grpc_asyncio",
    request_type=vertex_rag_data_service.GetRagCorpusRequest,
):
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_rag_corpus), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data.RagCorpus(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
                rag_files_count=1588,
            )
        )
        response = await client.get_rag_corpus(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.GetRagCorpusRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, vertex_rag_data.RagCorpus)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.rag_files_count == 1588


@pytest.mark.asyncio
async def test_get_rag_corpus_async_from_dict():
    await test_get_rag_corpus_async(request_type=dict)


def test_get_rag_corpus_field_headers():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.GetRagCorpusRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_rag_corpus), "__call__") as call:
        call.return_value = vertex_rag_data.RagCorpus()
        client.get_rag_corpus(request)

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
async def test_get_rag_corpus_field_headers_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.GetRagCorpusRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_rag_corpus), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data.RagCorpus()
        )
        await client.get_rag_corpus(request)

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


def test_get_rag_corpus_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_rag_corpus), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = vertex_rag_data.RagCorpus()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_rag_corpus(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_get_rag_corpus_flattened_error():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_rag_corpus(
            vertex_rag_data_service.GetRagCorpusRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_get_rag_corpus_flattened_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_rag_corpus), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = vertex_rag_data.RagCorpus()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data.RagCorpus()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_rag_corpus(
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
async def test_get_rag_corpus_flattened_error_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_rag_corpus(
            vertex_rag_data_service.GetRagCorpusRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.ListRagCorporaRequest,
        dict,
    ],
)
def test_list_rag_corpora(request_type, transport: str = "grpc"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_corpora), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = vertex_rag_data_service.ListRagCorporaResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_rag_corpora(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.ListRagCorporaRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListRagCorporaPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_rag_corpora_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = vertex_rag_data_service.ListRagCorporaRequest(
        parent="parent_value",
        page_token="page_token_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_corpora), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.list_rag_corpora(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == vertex_rag_data_service.ListRagCorporaRequest(
            parent="parent_value",
            page_token="page_token_value",
        )


def test_list_rag_corpora_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.list_rag_corpora in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.list_rag_corpora] = (
            mock_rpc
        )
        request = {}
        client.list_rag_corpora(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_rag_corpora(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_list_rag_corpora_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.list_rag_corpora
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.list_rag_corpora
        ] = mock_rpc

        request = {}
        await client.list_rag_corpora(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.list_rag_corpora(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_list_rag_corpora_async(
    transport: str = "grpc_asyncio",
    request_type=vertex_rag_data_service.ListRagCorporaRequest,
):
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_corpora), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data_service.ListRagCorporaResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_rag_corpora(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.ListRagCorporaRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListRagCorporaAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_rag_corpora_async_from_dict():
    await test_list_rag_corpora_async(request_type=dict)


def test_list_rag_corpora_field_headers():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.ListRagCorporaRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_corpora), "__call__") as call:
        call.return_value = vertex_rag_data_service.ListRagCorporaResponse()
        client.list_rag_corpora(request)

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
async def test_list_rag_corpora_field_headers_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.ListRagCorporaRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_corpora), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data_service.ListRagCorporaResponse()
        )
        await client.list_rag_corpora(request)

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


def test_list_rag_corpora_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_corpora), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = vertex_rag_data_service.ListRagCorporaResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_rag_corpora(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_list_rag_corpora_flattened_error():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_rag_corpora(
            vertex_rag_data_service.ListRagCorporaRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_rag_corpora_flattened_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_corpora), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = vertex_rag_data_service.ListRagCorporaResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data_service.ListRagCorporaResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_rag_corpora(
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
async def test_list_rag_corpora_flattened_error_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_rag_corpora(
            vertex_rag_data_service.ListRagCorporaRequest(),
            parent="parent_value",
        )


def test_list_rag_corpora_pager(transport_name: str = "grpc"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_corpora), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            vertex_rag_data_service.ListRagCorporaResponse(
                rag_corpora=[
                    vertex_rag_data.RagCorpus(),
                    vertex_rag_data.RagCorpus(),
                    vertex_rag_data.RagCorpus(),
                ],
                next_page_token="abc",
            ),
            vertex_rag_data_service.ListRagCorporaResponse(
                rag_corpora=[],
                next_page_token="def",
            ),
            vertex_rag_data_service.ListRagCorporaResponse(
                rag_corpora=[
                    vertex_rag_data.RagCorpus(),
                ],
                next_page_token="ghi",
            ),
            vertex_rag_data_service.ListRagCorporaResponse(
                rag_corpora=[
                    vertex_rag_data.RagCorpus(),
                    vertex_rag_data.RagCorpus(),
                ],
            ),
            RuntimeError,
        )

        expected_metadata = ()
        retry = retries.Retry()
        timeout = 5
        expected_metadata = tuple(expected_metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_rag_corpora(request={}, retry=retry, timeout=timeout)

        assert pager._metadata == expected_metadata
        assert pager._retry == retry
        assert pager._timeout == timeout

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, vertex_rag_data.RagCorpus) for i in results)


def test_list_rag_corpora_pages(transport_name: str = "grpc"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_corpora), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            vertex_rag_data_service.ListRagCorporaResponse(
                rag_corpora=[
                    vertex_rag_data.RagCorpus(),
                    vertex_rag_data.RagCorpus(),
                    vertex_rag_data.RagCorpus(),
                ],
                next_page_token="abc",
            ),
            vertex_rag_data_service.ListRagCorporaResponse(
                rag_corpora=[],
                next_page_token="def",
            ),
            vertex_rag_data_service.ListRagCorporaResponse(
                rag_corpora=[
                    vertex_rag_data.RagCorpus(),
                ],
                next_page_token="ghi",
            ),
            vertex_rag_data_service.ListRagCorporaResponse(
                rag_corpora=[
                    vertex_rag_data.RagCorpus(),
                    vertex_rag_data.RagCorpus(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_rag_corpora(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_rag_corpora_async_pager():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_rag_corpora), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            vertex_rag_data_service.ListRagCorporaResponse(
                rag_corpora=[
                    vertex_rag_data.RagCorpus(),
                    vertex_rag_data.RagCorpus(),
                    vertex_rag_data.RagCorpus(),
                ],
                next_page_token="abc",
            ),
            vertex_rag_data_service.ListRagCorporaResponse(
                rag_corpora=[],
                next_page_token="def",
            ),
            vertex_rag_data_service.ListRagCorporaResponse(
                rag_corpora=[
                    vertex_rag_data.RagCorpus(),
                ],
                next_page_token="ghi",
            ),
            vertex_rag_data_service.ListRagCorporaResponse(
                rag_corpora=[
                    vertex_rag_data.RagCorpus(),
                    vertex_rag_data.RagCorpus(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_rag_corpora(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, vertex_rag_data.RagCorpus) for i in responses)


@pytest.mark.asyncio
async def test_list_rag_corpora_async_pages():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_rag_corpora), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            vertex_rag_data_service.ListRagCorporaResponse(
                rag_corpora=[
                    vertex_rag_data.RagCorpus(),
                    vertex_rag_data.RagCorpus(),
                    vertex_rag_data.RagCorpus(),
                ],
                next_page_token="abc",
            ),
            vertex_rag_data_service.ListRagCorporaResponse(
                rag_corpora=[],
                next_page_token="def",
            ),
            vertex_rag_data_service.ListRagCorporaResponse(
                rag_corpora=[
                    vertex_rag_data.RagCorpus(),
                ],
                next_page_token="ghi",
            ),
            vertex_rag_data_service.ListRagCorporaResponse(
                rag_corpora=[
                    vertex_rag_data.RagCorpus(),
                    vertex_rag_data.RagCorpus(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.list_rag_corpora(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.DeleteRagCorpusRequest,
        dict,
    ],
)
def test_delete_rag_corpus(request_type, transport: str = "grpc"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_rag_corpus), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_rag_corpus(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.DeleteRagCorpusRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_rag_corpus_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = vertex_rag_data_service.DeleteRagCorpusRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_rag_corpus), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.delete_rag_corpus(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == vertex_rag_data_service.DeleteRagCorpusRequest(
            name="name_value",
        )


def test_delete_rag_corpus_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.delete_rag_corpus in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.delete_rag_corpus] = (
            mock_rpc
        )
        request = {}
        client.delete_rag_corpus(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.delete_rag_corpus(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_delete_rag_corpus_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.delete_rag_corpus
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.delete_rag_corpus
        ] = mock_rpc

        request = {}
        await client.delete_rag_corpus(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.delete_rag_corpus(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_delete_rag_corpus_async(
    transport: str = "grpc_asyncio",
    request_type=vertex_rag_data_service.DeleteRagCorpusRequest,
):
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_rag_corpus), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_rag_corpus(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.DeleteRagCorpusRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_rag_corpus_async_from_dict():
    await test_delete_rag_corpus_async(request_type=dict)


def test_delete_rag_corpus_field_headers():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.DeleteRagCorpusRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_rag_corpus), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_rag_corpus(request)

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
async def test_delete_rag_corpus_field_headers_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.DeleteRagCorpusRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_rag_corpus), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_rag_corpus(request)

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


def test_delete_rag_corpus_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_rag_corpus), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_rag_corpus(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_delete_rag_corpus_flattened_error():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_rag_corpus(
            vertex_rag_data_service.DeleteRagCorpusRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_rag_corpus_flattened_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_rag_corpus), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_rag_corpus(
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
async def test_delete_rag_corpus_flattened_error_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_rag_corpus(
            vertex_rag_data_service.DeleteRagCorpusRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.UploadRagFileRequest,
        dict,
    ],
)
def test_upload_rag_file(request_type, transport: str = "grpc"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.upload_rag_file), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = vertex_rag_data_service.UploadRagFileResponse()
        response = client.upload_rag_file(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.UploadRagFileRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, vertex_rag_data_service.UploadRagFileResponse)


def test_upload_rag_file_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = vertex_rag_data_service.UploadRagFileRequest(
        parent="parent_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.upload_rag_file), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.upload_rag_file(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == vertex_rag_data_service.UploadRagFileRequest(
            parent="parent_value",
        )


def test_upload_rag_file_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.upload_rag_file in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.upload_rag_file] = mock_rpc
        request = {}
        client.upload_rag_file(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.upload_rag_file(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_upload_rag_file_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.upload_rag_file
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.upload_rag_file
        ] = mock_rpc

        request = {}
        await client.upload_rag_file(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.upload_rag_file(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_upload_rag_file_async(
    transport: str = "grpc_asyncio",
    request_type=vertex_rag_data_service.UploadRagFileRequest,
):
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.upload_rag_file), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data_service.UploadRagFileResponse()
        )
        response = await client.upload_rag_file(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.UploadRagFileRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, vertex_rag_data_service.UploadRagFileResponse)


@pytest.mark.asyncio
async def test_upload_rag_file_async_from_dict():
    await test_upload_rag_file_async(request_type=dict)


def test_upload_rag_file_field_headers():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.UploadRagFileRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.upload_rag_file), "__call__") as call:
        call.return_value = vertex_rag_data_service.UploadRagFileResponse()
        client.upload_rag_file(request)

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
async def test_upload_rag_file_field_headers_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.UploadRagFileRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.upload_rag_file), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data_service.UploadRagFileResponse()
        )
        await client.upload_rag_file(request)

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


def test_upload_rag_file_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.upload_rag_file), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = vertex_rag_data_service.UploadRagFileResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.upload_rag_file(
            parent="parent_value",
            rag_file=vertex_rag_data.RagFile(
                gcs_source=io.GcsSource(uris=["uris_value"])
            ),
            upload_rag_file_config=vertex_rag_data.UploadRagFileConfig(
                rag_file_chunking_config=vertex_rag_data.RagFileChunkingConfig(
                    fixed_length_chunking=vertex_rag_data.RagFileChunkingConfig.FixedLengthChunking(
                        chunk_size=1075
                    )
                )
            ),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].rag_file
        mock_val = vertex_rag_data.RagFile(gcs_source=io.GcsSource(uris=["uris_value"]))
        assert arg == mock_val
        arg = args[0].upload_rag_file_config
        mock_val = vertex_rag_data.UploadRagFileConfig(
            rag_file_chunking_config=vertex_rag_data.RagFileChunkingConfig(
                fixed_length_chunking=vertex_rag_data.RagFileChunkingConfig.FixedLengthChunking(
                    chunk_size=1075
                )
            )
        )
        assert arg == mock_val


def test_upload_rag_file_flattened_error():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.upload_rag_file(
            vertex_rag_data_service.UploadRagFileRequest(),
            parent="parent_value",
            rag_file=vertex_rag_data.RagFile(
                gcs_source=io.GcsSource(uris=["uris_value"])
            ),
            upload_rag_file_config=vertex_rag_data.UploadRagFileConfig(
                rag_file_chunking_config=vertex_rag_data.RagFileChunkingConfig(
                    fixed_length_chunking=vertex_rag_data.RagFileChunkingConfig.FixedLengthChunking(
                        chunk_size=1075
                    )
                )
            ),
        )


@pytest.mark.asyncio
async def test_upload_rag_file_flattened_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.upload_rag_file), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = vertex_rag_data_service.UploadRagFileResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data_service.UploadRagFileResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.upload_rag_file(
            parent="parent_value",
            rag_file=vertex_rag_data.RagFile(
                gcs_source=io.GcsSource(uris=["uris_value"])
            ),
            upload_rag_file_config=vertex_rag_data.UploadRagFileConfig(
                rag_file_chunking_config=vertex_rag_data.RagFileChunkingConfig(
                    fixed_length_chunking=vertex_rag_data.RagFileChunkingConfig.FixedLengthChunking(
                        chunk_size=1075
                    )
                )
            ),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].rag_file
        mock_val = vertex_rag_data.RagFile(gcs_source=io.GcsSource(uris=["uris_value"]))
        assert arg == mock_val
        arg = args[0].upload_rag_file_config
        mock_val = vertex_rag_data.UploadRagFileConfig(
            rag_file_chunking_config=vertex_rag_data.RagFileChunkingConfig(
                fixed_length_chunking=vertex_rag_data.RagFileChunkingConfig.FixedLengthChunking(
                    chunk_size=1075
                )
            )
        )
        assert arg == mock_val


@pytest.mark.asyncio
async def test_upload_rag_file_flattened_error_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.upload_rag_file(
            vertex_rag_data_service.UploadRagFileRequest(),
            parent="parent_value",
            rag_file=vertex_rag_data.RagFile(
                gcs_source=io.GcsSource(uris=["uris_value"])
            ),
            upload_rag_file_config=vertex_rag_data.UploadRagFileConfig(
                rag_file_chunking_config=vertex_rag_data.RagFileChunkingConfig(
                    fixed_length_chunking=vertex_rag_data.RagFileChunkingConfig.FixedLengthChunking(
                        chunk_size=1075
                    )
                )
            ),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.ImportRagFilesRequest,
        dict,
    ],
)
def test_import_rag_files(request_type, transport: str = "grpc"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.import_rag_files), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.import_rag_files(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.ImportRagFilesRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_import_rag_files_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = vertex_rag_data_service.ImportRagFilesRequest(
        parent="parent_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.import_rag_files), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.import_rag_files(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == vertex_rag_data_service.ImportRagFilesRequest(
            parent="parent_value",
        )


def test_import_rag_files_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.import_rag_files in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.import_rag_files] = (
            mock_rpc
        )
        request = {}
        client.import_rag_files(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.import_rag_files(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_import_rag_files_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.import_rag_files
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.import_rag_files
        ] = mock_rpc

        request = {}
        await client.import_rag_files(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.import_rag_files(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_import_rag_files_async(
    transport: str = "grpc_asyncio",
    request_type=vertex_rag_data_service.ImportRagFilesRequest,
):
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.import_rag_files), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.import_rag_files(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.ImportRagFilesRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_import_rag_files_async_from_dict():
    await test_import_rag_files_async(request_type=dict)


def test_import_rag_files_field_headers():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.ImportRagFilesRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.import_rag_files), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.import_rag_files(request)

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
async def test_import_rag_files_field_headers_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.ImportRagFilesRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.import_rag_files), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.import_rag_files(request)

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


def test_import_rag_files_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.import_rag_files), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.import_rag_files(
            parent="parent_value",
            import_rag_files_config=vertex_rag_data.ImportRagFilesConfig(
                gcs_source=io.GcsSource(uris=["uris_value"])
            ),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].import_rag_files_config
        mock_val = vertex_rag_data.ImportRagFilesConfig(
            gcs_source=io.GcsSource(uris=["uris_value"])
        )
        assert arg == mock_val


def test_import_rag_files_flattened_error():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.import_rag_files(
            vertex_rag_data_service.ImportRagFilesRequest(),
            parent="parent_value",
            import_rag_files_config=vertex_rag_data.ImportRagFilesConfig(
                gcs_source=io.GcsSource(uris=["uris_value"])
            ),
        )


@pytest.mark.asyncio
async def test_import_rag_files_flattened_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.import_rag_files), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.import_rag_files(
            parent="parent_value",
            import_rag_files_config=vertex_rag_data.ImportRagFilesConfig(
                gcs_source=io.GcsSource(uris=["uris_value"])
            ),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].import_rag_files_config
        mock_val = vertex_rag_data.ImportRagFilesConfig(
            gcs_source=io.GcsSource(uris=["uris_value"])
        )
        assert arg == mock_val


@pytest.mark.asyncio
async def test_import_rag_files_flattened_error_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.import_rag_files(
            vertex_rag_data_service.ImportRagFilesRequest(),
            parent="parent_value",
            import_rag_files_config=vertex_rag_data.ImportRagFilesConfig(
                gcs_source=io.GcsSource(uris=["uris_value"])
            ),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.GetRagFileRequest,
        dict,
    ],
)
def test_get_rag_file(request_type, transport: str = "grpc"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_rag_file), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = vertex_rag_data.RagFile(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            size_bytes=1089,
            rag_file_type=vertex_rag_data.RagFile.RagFileType.RAG_FILE_TYPE_TXT,
            user_metadata="user_metadata_value",
        )
        response = client.get_rag_file(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.GetRagFileRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, vertex_rag_data.RagFile)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.size_bytes == 1089
    assert (
        response.rag_file_type == vertex_rag_data.RagFile.RagFileType.RAG_FILE_TYPE_TXT
    )
    assert response.user_metadata == "user_metadata_value"


def test_get_rag_file_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = vertex_rag_data_service.GetRagFileRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_rag_file), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.get_rag_file(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == vertex_rag_data_service.GetRagFileRequest(
            name="name_value",
        )


def test_get_rag_file_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.get_rag_file in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.get_rag_file] = mock_rpc
        request = {}
        client.get_rag_file(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_rag_file(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_get_rag_file_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.get_rag_file
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.get_rag_file
        ] = mock_rpc

        request = {}
        await client.get_rag_file(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.get_rag_file(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_get_rag_file_async(
    transport: str = "grpc_asyncio",
    request_type=vertex_rag_data_service.GetRagFileRequest,
):
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_rag_file), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data.RagFile(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
                size_bytes=1089,
                rag_file_type=vertex_rag_data.RagFile.RagFileType.RAG_FILE_TYPE_TXT,
                user_metadata="user_metadata_value",
            )
        )
        response = await client.get_rag_file(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.GetRagFileRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, vertex_rag_data.RagFile)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.size_bytes == 1089
    assert (
        response.rag_file_type == vertex_rag_data.RagFile.RagFileType.RAG_FILE_TYPE_TXT
    )
    assert response.user_metadata == "user_metadata_value"


@pytest.mark.asyncio
async def test_get_rag_file_async_from_dict():
    await test_get_rag_file_async(request_type=dict)


def test_get_rag_file_field_headers():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.GetRagFileRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_rag_file), "__call__") as call:
        call.return_value = vertex_rag_data.RagFile()
        client.get_rag_file(request)

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
async def test_get_rag_file_field_headers_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.GetRagFileRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_rag_file), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data.RagFile()
        )
        await client.get_rag_file(request)

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


def test_get_rag_file_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_rag_file), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = vertex_rag_data.RagFile()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_rag_file(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_get_rag_file_flattened_error():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_rag_file(
            vertex_rag_data_service.GetRagFileRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_get_rag_file_flattened_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_rag_file), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = vertex_rag_data.RagFile()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data.RagFile()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_rag_file(
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
async def test_get_rag_file_flattened_error_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_rag_file(
            vertex_rag_data_service.GetRagFileRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.ListRagFilesRequest,
        dict,
    ],
)
def test_list_rag_files(request_type, transport: str = "grpc"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_files), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = vertex_rag_data_service.ListRagFilesResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_rag_files(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.ListRagFilesRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListRagFilesPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_rag_files_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = vertex_rag_data_service.ListRagFilesRequest(
        parent="parent_value",
        page_token="page_token_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_files), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.list_rag_files(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == vertex_rag_data_service.ListRagFilesRequest(
            parent="parent_value",
            page_token="page_token_value",
        )


def test_list_rag_files_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.list_rag_files in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.list_rag_files] = mock_rpc
        request = {}
        client.list_rag_files(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_rag_files(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_list_rag_files_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.list_rag_files
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.list_rag_files
        ] = mock_rpc

        request = {}
        await client.list_rag_files(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.list_rag_files(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_list_rag_files_async(
    transport: str = "grpc_asyncio",
    request_type=vertex_rag_data_service.ListRagFilesRequest,
):
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_files), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data_service.ListRagFilesResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_rag_files(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.ListRagFilesRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListRagFilesAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_rag_files_async_from_dict():
    await test_list_rag_files_async(request_type=dict)


def test_list_rag_files_field_headers():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.ListRagFilesRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_files), "__call__") as call:
        call.return_value = vertex_rag_data_service.ListRagFilesResponse()
        client.list_rag_files(request)

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
async def test_list_rag_files_field_headers_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.ListRagFilesRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_files), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data_service.ListRagFilesResponse()
        )
        await client.list_rag_files(request)

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


def test_list_rag_files_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_files), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = vertex_rag_data_service.ListRagFilesResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_rag_files(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_list_rag_files_flattened_error():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_rag_files(
            vertex_rag_data_service.ListRagFilesRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_rag_files_flattened_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_files), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = vertex_rag_data_service.ListRagFilesResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data_service.ListRagFilesResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_rag_files(
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
async def test_list_rag_files_flattened_error_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_rag_files(
            vertex_rag_data_service.ListRagFilesRequest(),
            parent="parent_value",
        )


def test_list_rag_files_pager(transport_name: str = "grpc"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_files), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            vertex_rag_data_service.ListRagFilesResponse(
                rag_files=[
                    vertex_rag_data.RagFile(),
                    vertex_rag_data.RagFile(),
                    vertex_rag_data.RagFile(),
                ],
                next_page_token="abc",
            ),
            vertex_rag_data_service.ListRagFilesResponse(
                rag_files=[],
                next_page_token="def",
            ),
            vertex_rag_data_service.ListRagFilesResponse(
                rag_files=[
                    vertex_rag_data.RagFile(),
                ],
                next_page_token="ghi",
            ),
            vertex_rag_data_service.ListRagFilesResponse(
                rag_files=[
                    vertex_rag_data.RagFile(),
                    vertex_rag_data.RagFile(),
                ],
            ),
            RuntimeError,
        )

        expected_metadata = ()
        retry = retries.Retry()
        timeout = 5
        expected_metadata = tuple(expected_metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_rag_files(request={}, retry=retry, timeout=timeout)

        assert pager._metadata == expected_metadata
        assert pager._retry == retry
        assert pager._timeout == timeout

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, vertex_rag_data.RagFile) for i in results)


def test_list_rag_files_pages(transport_name: str = "grpc"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_files), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            vertex_rag_data_service.ListRagFilesResponse(
                rag_files=[
                    vertex_rag_data.RagFile(),
                    vertex_rag_data.RagFile(),
                    vertex_rag_data.RagFile(),
                ],
                next_page_token="abc",
            ),
            vertex_rag_data_service.ListRagFilesResponse(
                rag_files=[],
                next_page_token="def",
            ),
            vertex_rag_data_service.ListRagFilesResponse(
                rag_files=[
                    vertex_rag_data.RagFile(),
                ],
                next_page_token="ghi",
            ),
            vertex_rag_data_service.ListRagFilesResponse(
                rag_files=[
                    vertex_rag_data.RagFile(),
                    vertex_rag_data.RagFile(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_rag_files(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_rag_files_async_pager():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_rag_files), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            vertex_rag_data_service.ListRagFilesResponse(
                rag_files=[
                    vertex_rag_data.RagFile(),
                    vertex_rag_data.RagFile(),
                    vertex_rag_data.RagFile(),
                ],
                next_page_token="abc",
            ),
            vertex_rag_data_service.ListRagFilesResponse(
                rag_files=[],
                next_page_token="def",
            ),
            vertex_rag_data_service.ListRagFilesResponse(
                rag_files=[
                    vertex_rag_data.RagFile(),
                ],
                next_page_token="ghi",
            ),
            vertex_rag_data_service.ListRagFilesResponse(
                rag_files=[
                    vertex_rag_data.RagFile(),
                    vertex_rag_data.RagFile(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_rag_files(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, vertex_rag_data.RagFile) for i in responses)


@pytest.mark.asyncio
async def test_list_rag_files_async_pages():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_rag_files), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            vertex_rag_data_service.ListRagFilesResponse(
                rag_files=[
                    vertex_rag_data.RagFile(),
                    vertex_rag_data.RagFile(),
                    vertex_rag_data.RagFile(),
                ],
                next_page_token="abc",
            ),
            vertex_rag_data_service.ListRagFilesResponse(
                rag_files=[],
                next_page_token="def",
            ),
            vertex_rag_data_service.ListRagFilesResponse(
                rag_files=[
                    vertex_rag_data.RagFile(),
                ],
                next_page_token="ghi",
            ),
            vertex_rag_data_service.ListRagFilesResponse(
                rag_files=[
                    vertex_rag_data.RagFile(),
                    vertex_rag_data.RagFile(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.list_rag_files(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.DeleteRagFileRequest,
        dict,
    ],
)
def test_delete_rag_file(request_type, transport: str = "grpc"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_rag_file), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_rag_file(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.DeleteRagFileRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_rag_file_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = vertex_rag_data_service.DeleteRagFileRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_rag_file), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.delete_rag_file(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == vertex_rag_data_service.DeleteRagFileRequest(
            name="name_value",
        )


def test_delete_rag_file_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.delete_rag_file in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.delete_rag_file] = mock_rpc
        request = {}
        client.delete_rag_file(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.delete_rag_file(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_delete_rag_file_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.delete_rag_file
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.delete_rag_file
        ] = mock_rpc

        request = {}
        await client.delete_rag_file(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.delete_rag_file(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_delete_rag_file_async(
    transport: str = "grpc_asyncio",
    request_type=vertex_rag_data_service.DeleteRagFileRequest,
):
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_rag_file), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_rag_file(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.DeleteRagFileRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_rag_file_async_from_dict():
    await test_delete_rag_file_async(request_type=dict)


def test_delete_rag_file_field_headers():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.DeleteRagFileRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_rag_file), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_rag_file(request)

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
async def test_delete_rag_file_field_headers_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.DeleteRagFileRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_rag_file), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_rag_file(request)

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


def test_delete_rag_file_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_rag_file), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_rag_file(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_delete_rag_file_flattened_error():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_rag_file(
            vertex_rag_data_service.DeleteRagFileRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_rag_file_flattened_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_rag_file), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_rag_file(
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
async def test_delete_rag_file_flattened_error_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_rag_file(
            vertex_rag_data_service.DeleteRagFileRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.UpdateRagEngineConfigRequest,
        dict,
    ],
)
def test_update_rag_engine_config(request_type, transport: str = "grpc"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_rag_engine_config), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.update_rag_engine_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.UpdateRagEngineConfigRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_update_rag_engine_config_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = vertex_rag_data_service.UpdateRagEngineConfigRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_rag_engine_config), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.update_rag_engine_config(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == vertex_rag_data_service.UpdateRagEngineConfigRequest()


def test_update_rag_engine_config_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.update_rag_engine_config
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[
            client._transport.update_rag_engine_config
        ] = mock_rpc
        request = {}
        client.update_rag_engine_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.update_rag_engine_config(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_update_rag_engine_config_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.update_rag_engine_config
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.update_rag_engine_config
        ] = mock_rpc

        request = {}
        await client.update_rag_engine_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.update_rag_engine_config(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_update_rag_engine_config_async(
    transport: str = "grpc_asyncio",
    request_type=vertex_rag_data_service.UpdateRagEngineConfigRequest,
):
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_rag_engine_config), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.update_rag_engine_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.UpdateRagEngineConfigRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_update_rag_engine_config_async_from_dict():
    await test_update_rag_engine_config_async(request_type=dict)


def test_update_rag_engine_config_field_headers():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.UpdateRagEngineConfigRequest()

    request.rag_engine_config.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_rag_engine_config), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.update_rag_engine_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "rag_engine_config.name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_rag_engine_config_field_headers_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.UpdateRagEngineConfigRequest()

    request.rag_engine_config.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_rag_engine_config), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.update_rag_engine_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "rag_engine_config.name=name_value",
    ) in kw["metadata"]


def test_update_rag_engine_config_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_rag_engine_config), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_rag_engine_config(
            rag_engine_config=vertex_rag_data.RagEngineConfig(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].rag_engine_config
        mock_val = vertex_rag_data.RagEngineConfig(name="name_value")
        assert arg == mock_val


def test_update_rag_engine_config_flattened_error():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_rag_engine_config(
            vertex_rag_data_service.UpdateRagEngineConfigRequest(),
            rag_engine_config=vertex_rag_data.RagEngineConfig(name="name_value"),
        )


@pytest.mark.asyncio
async def test_update_rag_engine_config_flattened_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_rag_engine_config), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_rag_engine_config(
            rag_engine_config=vertex_rag_data.RagEngineConfig(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].rag_engine_config
        mock_val = vertex_rag_data.RagEngineConfig(name="name_value")
        assert arg == mock_val


@pytest.mark.asyncio
async def test_update_rag_engine_config_flattened_error_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_rag_engine_config(
            vertex_rag_data_service.UpdateRagEngineConfigRequest(),
            rag_engine_config=vertex_rag_data.RagEngineConfig(name="name_value"),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.GetRagEngineConfigRequest,
        dict,
    ],
)
def test_get_rag_engine_config(request_type, transport: str = "grpc"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_rag_engine_config), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = vertex_rag_data.RagEngineConfig(
            name="name_value",
        )
        response = client.get_rag_engine_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.GetRagEngineConfigRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, vertex_rag_data.RagEngineConfig)
    assert response.name == "name_value"


def test_get_rag_engine_config_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = vertex_rag_data_service.GetRagEngineConfigRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_rag_engine_config), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.get_rag_engine_config(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == vertex_rag_data_service.GetRagEngineConfigRequest(
            name="name_value",
        )


def test_get_rag_engine_config_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.get_rag_engine_config
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.get_rag_engine_config] = (
            mock_rpc
        )
        request = {}
        client.get_rag_engine_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_rag_engine_config(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_get_rag_engine_config_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.get_rag_engine_config
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.get_rag_engine_config
        ] = mock_rpc

        request = {}
        await client.get_rag_engine_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.get_rag_engine_config(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_get_rag_engine_config_async(
    transport: str = "grpc_asyncio",
    request_type=vertex_rag_data_service.GetRagEngineConfigRequest,
):
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_rag_engine_config), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data.RagEngineConfig(
                name="name_value",
            )
        )
        response = await client.get_rag_engine_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = vertex_rag_data_service.GetRagEngineConfigRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, vertex_rag_data.RagEngineConfig)
    assert response.name == "name_value"


@pytest.mark.asyncio
async def test_get_rag_engine_config_async_from_dict():
    await test_get_rag_engine_config_async(request_type=dict)


def test_get_rag_engine_config_field_headers():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.GetRagEngineConfigRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_rag_engine_config), "__call__"
    ) as call:
        call.return_value = vertex_rag_data.RagEngineConfig()
        client.get_rag_engine_config(request)

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
async def test_get_rag_engine_config_field_headers_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = vertex_rag_data_service.GetRagEngineConfigRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_rag_engine_config), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data.RagEngineConfig()
        )
        await client.get_rag_engine_config(request)

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


def test_get_rag_engine_config_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_rag_engine_config), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = vertex_rag_data.RagEngineConfig()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_rag_engine_config(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_get_rag_engine_config_flattened_error():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_rag_engine_config(
            vertex_rag_data_service.GetRagEngineConfigRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_get_rag_engine_config_flattened_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_rag_engine_config), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = vertex_rag_data.RagEngineConfig()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data.RagEngineConfig()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_rag_engine_config(
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
async def test_get_rag_engine_config_flattened_error_async():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_rag_engine_config(
            vertex_rag_data_service.GetRagEngineConfigRequest(),
            name="name_value",
        )


def test_create_rag_corpus_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.create_rag_corpus in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.create_rag_corpus] = (
            mock_rpc
        )

        request = {}
        client.create_rag_corpus(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.create_rag_corpus(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_create_rag_corpus_rest_required_fields(
    request_type=vertex_rag_data_service.CreateRagCorpusRequest,
):
    transport_class = transports.VertexRagDataServiceRestTransport

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
    ).create_rag_corpus._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).create_rag_corpus._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = VertexRagDataServiceClient(
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
                "method": "post",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.create_rag_corpus(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_create_rag_corpus_rest_unset_required_fields():
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.create_rag_corpus._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(())
        & set(
            (
                "parent",
                "ragCorpus",
            )
        )
    )


def test_create_rag_corpus_rest_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {"parent": "projects/sample1/locations/sample2"}

        # get truthy value for each flattened field
        mock_args = dict(
            parent="parent_value",
            rag_corpus=vertex_rag_data.RagCorpus(
                vector_db_config=vertex_rag_data.RagVectorDbConfig(
                    rag_managed_db=vertex_rag_data.RagVectorDbConfig.RagManagedDb(
                        knn=None
                    )
                )
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.create_rag_corpus(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{parent=projects/*/locations/*}/ragCorpora"
            % client.transport._host,
            args[1],
        )


def test_create_rag_corpus_rest_flattened_error(transport: str = "rest"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_rag_corpus(
            vertex_rag_data_service.CreateRagCorpusRequest(),
            parent="parent_value",
            rag_corpus=vertex_rag_data.RagCorpus(
                vector_db_config=vertex_rag_data.RagVectorDbConfig(
                    rag_managed_db=vertex_rag_data.RagVectorDbConfig.RagManagedDb(
                        knn=None
                    )
                )
            ),
        )


def test_update_rag_corpus_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.update_rag_corpus in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.update_rag_corpus] = (
            mock_rpc
        )

        request = {}
        client.update_rag_corpus(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.update_rag_corpus(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_update_rag_corpus_rest_required_fields(
    request_type=vertex_rag_data_service.UpdateRagCorpusRequest,
):
    transport_class = transports.VertexRagDataServiceRestTransport

    request_init = {}
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(pb_request, use_integers_for_enums=False)
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_rag_corpus._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_rag_corpus._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone

    client = VertexRagDataServiceClient(
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
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.update_rag_corpus(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_update_rag_corpus_rest_unset_required_fields():
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.update_rag_corpus._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("ragCorpus",)))


def test_update_rag_corpus_rest_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "rag_corpus": {
                "name": "projects/sample1/locations/sample2/ragCorpora/sample3"
            }
        }

        # get truthy value for each flattened field
        mock_args = dict(
            rag_corpus=vertex_rag_data.RagCorpus(
                vector_db_config=vertex_rag_data.RagVectorDbConfig(
                    rag_managed_db=vertex_rag_data.RagVectorDbConfig.RagManagedDb(
                        knn=None
                    )
                )
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.update_rag_corpus(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{rag_corpus.name=projects/*/locations/*/ragCorpora/*}"
            % client.transport._host,
            args[1],
        )


def test_update_rag_corpus_rest_flattened_error(transport: str = "rest"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_rag_corpus(
            vertex_rag_data_service.UpdateRagCorpusRequest(),
            rag_corpus=vertex_rag_data.RagCorpus(
                vector_db_config=vertex_rag_data.RagVectorDbConfig(
                    rag_managed_db=vertex_rag_data.RagVectorDbConfig.RagManagedDb(
                        knn=None
                    )
                )
            ),
        )


def test_get_rag_corpus_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.get_rag_corpus in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.get_rag_corpus] = mock_rpc

        request = {}
        client.get_rag_corpus(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_rag_corpus(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_get_rag_corpus_rest_required_fields(
    request_type=vertex_rag_data_service.GetRagCorpusRequest,
):
    transport_class = transports.VertexRagDataServiceRestTransport

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
    ).get_rag_corpus._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_rag_corpus._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = vertex_rag_data.RagCorpus()
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
            return_value = vertex_rag_data.RagCorpus.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.get_rag_corpus(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_rag_corpus_rest_unset_required_fields():
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_rag_corpus._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


def test_get_rag_corpus_rest_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = vertex_rag_data.RagCorpus()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/ragCorpora/sample3"
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
        return_value = vertex_rag_data.RagCorpus.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.get_rag_corpus(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/ragCorpora/*}"
            % client.transport._host,
            args[1],
        )


def test_get_rag_corpus_rest_flattened_error(transport: str = "rest"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_rag_corpus(
            vertex_rag_data_service.GetRagCorpusRequest(),
            name="name_value",
        )


def test_list_rag_corpora_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.list_rag_corpora in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.list_rag_corpora] = (
            mock_rpc
        )

        request = {}
        client.list_rag_corpora(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_rag_corpora(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_list_rag_corpora_rest_required_fields(
    request_type=vertex_rag_data_service.ListRagCorporaRequest,
):
    transport_class = transports.VertexRagDataServiceRestTransport

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
    ).list_rag_corpora._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_rag_corpora._get_unset_required_fields(jsonified_request)
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

    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = vertex_rag_data_service.ListRagCorporaResponse()
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
            return_value = vertex_rag_data_service.ListRagCorporaResponse.pb(
                return_value
            )
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.list_rag_corpora(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_list_rag_corpora_rest_unset_required_fields():
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.list_rag_corpora._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(
            (
                "pageSize",
                "pageToken",
            )
        )
        & set(("parent",))
    )


def test_list_rag_corpora_rest_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = vertex_rag_data_service.ListRagCorporaResponse()

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
        return_value = vertex_rag_data_service.ListRagCorporaResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.list_rag_corpora(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{parent=projects/*/locations/*}/ragCorpora"
            % client.transport._host,
            args[1],
        )


def test_list_rag_corpora_rest_flattened_error(transport: str = "rest"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_rag_corpora(
            vertex_rag_data_service.ListRagCorporaRequest(),
            parent="parent_value",
        )


def test_list_rag_corpora_rest_pager(transport: str = "rest"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            vertex_rag_data_service.ListRagCorporaResponse(
                rag_corpora=[
                    vertex_rag_data.RagCorpus(),
                    vertex_rag_data.RagCorpus(),
                    vertex_rag_data.RagCorpus(),
                ],
                next_page_token="abc",
            ),
            vertex_rag_data_service.ListRagCorporaResponse(
                rag_corpora=[],
                next_page_token="def",
            ),
            vertex_rag_data_service.ListRagCorporaResponse(
                rag_corpora=[
                    vertex_rag_data.RagCorpus(),
                ],
                next_page_token="ghi",
            ),
            vertex_rag_data_service.ListRagCorporaResponse(
                rag_corpora=[
                    vertex_rag_data.RagCorpus(),
                    vertex_rag_data.RagCorpus(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(
            vertex_rag_data_service.ListRagCorporaResponse.to_json(x) for x in response
        )
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {"parent": "projects/sample1/locations/sample2"}

        pager = client.list_rag_corpora(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, vertex_rag_data.RagCorpus) for i in results)

        pages = list(client.list_rag_corpora(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_delete_rag_corpus_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.delete_rag_corpus in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.delete_rag_corpus] = (
            mock_rpc
        )

        request = {}
        client.delete_rag_corpus(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.delete_rag_corpus(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_delete_rag_corpus_rest_required_fields(
    request_type=vertex_rag_data_service.DeleteRagCorpusRequest,
):
    transport_class = transports.VertexRagDataServiceRestTransport

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
    ).delete_rag_corpus._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).delete_rag_corpus._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("force",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = VertexRagDataServiceClient(
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
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.delete_rag_corpus(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_delete_rag_corpus_rest_unset_required_fields():
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.delete_rag_corpus._get_unset_required_fields({})
    assert set(unset_fields) == (set(("force",)) & set(("name",)))


def test_delete_rag_corpus_rest_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/ragCorpora/sample3"
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
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.delete_rag_corpus(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/ragCorpora/*}"
            % client.transport._host,
            args[1],
        )


def test_delete_rag_corpus_rest_flattened_error(transport: str = "rest"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_rag_corpus(
            vertex_rag_data_service.DeleteRagCorpusRequest(),
            name="name_value",
        )


def test_upload_rag_file_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.upload_rag_file in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.upload_rag_file] = mock_rpc

        request = {}
        client.upload_rag_file(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.upload_rag_file(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_upload_rag_file_rest_required_fields(
    request_type=vertex_rag_data_service.UploadRagFileRequest,
):
    transport_class = transports.VertexRagDataServiceRestTransport

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
    ).upload_rag_file._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).upload_rag_file._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = vertex_rag_data_service.UploadRagFileResponse()
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
            return_value = vertex_rag_data_service.UploadRagFileResponse.pb(
                return_value
            )
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.upload_rag_file(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_upload_rag_file_rest_unset_required_fields():
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.upload_rag_file._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(())
        & set(
            (
                "parent",
                "ragFile",
                "uploadRagFileConfig",
            )
        )
    )


def test_upload_rag_file_rest_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = vertex_rag_data_service.UploadRagFileResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "parent": "projects/sample1/locations/sample2/ragCorpora/sample3"
        }

        # get truthy value for each flattened field
        mock_args = dict(
            parent="parent_value",
            rag_file=vertex_rag_data.RagFile(
                gcs_source=io.GcsSource(uris=["uris_value"])
            ),
            upload_rag_file_config=vertex_rag_data.UploadRagFileConfig(
                rag_file_chunking_config=vertex_rag_data.RagFileChunkingConfig(
                    fixed_length_chunking=vertex_rag_data.RagFileChunkingConfig.FixedLengthChunking(
                        chunk_size=1075
                    )
                )
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = vertex_rag_data_service.UploadRagFileResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.upload_rag_file(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{parent=projects/*/locations/*/ragCorpora/*}/ragFiles:upload"
            % client.transport._host,
            args[1],
        )


def test_upload_rag_file_rest_flattened_error(transport: str = "rest"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.upload_rag_file(
            vertex_rag_data_service.UploadRagFileRequest(),
            parent="parent_value",
            rag_file=vertex_rag_data.RagFile(
                gcs_source=io.GcsSource(uris=["uris_value"])
            ),
            upload_rag_file_config=vertex_rag_data.UploadRagFileConfig(
                rag_file_chunking_config=vertex_rag_data.RagFileChunkingConfig(
                    fixed_length_chunking=vertex_rag_data.RagFileChunkingConfig.FixedLengthChunking(
                        chunk_size=1075
                    )
                )
            ),
        )


def test_import_rag_files_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.import_rag_files in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.import_rag_files] = (
            mock_rpc
        )

        request = {}
        client.import_rag_files(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.import_rag_files(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_import_rag_files_rest_required_fields(
    request_type=vertex_rag_data_service.ImportRagFilesRequest,
):
    transport_class = transports.VertexRagDataServiceRestTransport

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
    ).import_rag_files._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).import_rag_files._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = VertexRagDataServiceClient(
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
                "method": "post",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.import_rag_files(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_import_rag_files_rest_unset_required_fields():
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.import_rag_files._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(())
        & set(
            (
                "parent",
                "importRagFilesConfig",
            )
        )
    )


def test_import_rag_files_rest_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "parent": "projects/sample1/locations/sample2/ragCorpora/sample3"
        }

        # get truthy value for each flattened field
        mock_args = dict(
            parent="parent_value",
            import_rag_files_config=vertex_rag_data.ImportRagFilesConfig(
                gcs_source=io.GcsSource(uris=["uris_value"])
            ),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.import_rag_files(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{parent=projects/*/locations/*/ragCorpora/*}/ragFiles:import"
            % client.transport._host,
            args[1],
        )


def test_import_rag_files_rest_flattened_error(transport: str = "rest"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.import_rag_files(
            vertex_rag_data_service.ImportRagFilesRequest(),
            parent="parent_value",
            import_rag_files_config=vertex_rag_data.ImportRagFilesConfig(
                gcs_source=io.GcsSource(uris=["uris_value"])
            ),
        )


def test_get_rag_file_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.get_rag_file in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.get_rag_file] = mock_rpc

        request = {}
        client.get_rag_file(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_rag_file(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_get_rag_file_rest_required_fields(
    request_type=vertex_rag_data_service.GetRagFileRequest,
):
    transport_class = transports.VertexRagDataServiceRestTransport

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
    ).get_rag_file._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_rag_file._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = vertex_rag_data.RagFile()
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
            return_value = vertex_rag_data.RagFile.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.get_rag_file(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_rag_file_rest_unset_required_fields():
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_rag_file._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


def test_get_rag_file_rest_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = vertex_rag_data.RagFile()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/ragCorpora/sample3/ragFiles/sample4"
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
        return_value = vertex_rag_data.RagFile.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.get_rag_file(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/ragCorpora/*/ragFiles/*}"
            % client.transport._host,
            args[1],
        )


def test_get_rag_file_rest_flattened_error(transport: str = "rest"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_rag_file(
            vertex_rag_data_service.GetRagFileRequest(),
            name="name_value",
        )


def test_list_rag_files_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.list_rag_files in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.list_rag_files] = mock_rpc

        request = {}
        client.list_rag_files(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_rag_files(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_list_rag_files_rest_required_fields(
    request_type=vertex_rag_data_service.ListRagFilesRequest,
):
    transport_class = transports.VertexRagDataServiceRestTransport

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
    ).list_rag_files._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_rag_files._get_unset_required_fields(jsonified_request)
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

    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = vertex_rag_data_service.ListRagFilesResponse()
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
            return_value = vertex_rag_data_service.ListRagFilesResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.list_rag_files(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_list_rag_files_rest_unset_required_fields():
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.list_rag_files._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(
            (
                "pageSize",
                "pageToken",
            )
        )
        & set(("parent",))
    )


def test_list_rag_files_rest_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = vertex_rag_data_service.ListRagFilesResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "parent": "projects/sample1/locations/sample2/ragCorpora/sample3"
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
        return_value = vertex_rag_data_service.ListRagFilesResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.list_rag_files(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{parent=projects/*/locations/*/ragCorpora/*}/ragFiles"
            % client.transport._host,
            args[1],
        )


def test_list_rag_files_rest_flattened_error(transport: str = "rest"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_rag_files(
            vertex_rag_data_service.ListRagFilesRequest(),
            parent="parent_value",
        )


def test_list_rag_files_rest_pager(transport: str = "rest"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            vertex_rag_data_service.ListRagFilesResponse(
                rag_files=[
                    vertex_rag_data.RagFile(),
                    vertex_rag_data.RagFile(),
                    vertex_rag_data.RagFile(),
                ],
                next_page_token="abc",
            ),
            vertex_rag_data_service.ListRagFilesResponse(
                rag_files=[],
                next_page_token="def",
            ),
            vertex_rag_data_service.ListRagFilesResponse(
                rag_files=[
                    vertex_rag_data.RagFile(),
                ],
                next_page_token="ghi",
            ),
            vertex_rag_data_service.ListRagFilesResponse(
                rag_files=[
                    vertex_rag_data.RagFile(),
                    vertex_rag_data.RagFile(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(
            vertex_rag_data_service.ListRagFilesResponse.to_json(x) for x in response
        )
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {
            "parent": "projects/sample1/locations/sample2/ragCorpora/sample3"
        }

        pager = client.list_rag_files(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, vertex_rag_data.RagFile) for i in results)

        pages = list(client.list_rag_files(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_delete_rag_file_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.delete_rag_file in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.delete_rag_file] = mock_rpc

        request = {}
        client.delete_rag_file(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.delete_rag_file(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_delete_rag_file_rest_required_fields(
    request_type=vertex_rag_data_service.DeleteRagFileRequest,
):
    transport_class = transports.VertexRagDataServiceRestTransport

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
    ).delete_rag_file._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).delete_rag_file._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("force_delete",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = VertexRagDataServiceClient(
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
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.delete_rag_file(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_delete_rag_file_rest_unset_required_fields():
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.delete_rag_file._get_unset_required_fields({})
    assert set(unset_fields) == (set(("forceDelete",)) & set(("name",)))


def test_delete_rag_file_rest_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/ragCorpora/sample3/ragFiles/sample4"
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
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.delete_rag_file(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/ragCorpora/*/ragFiles/*}"
            % client.transport._host,
            args[1],
        )


def test_delete_rag_file_rest_flattened_error(transport: str = "rest"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_rag_file(
            vertex_rag_data_service.DeleteRagFileRequest(),
            name="name_value",
        )


def test_update_rag_engine_config_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.update_rag_engine_config
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[
            client._transport.update_rag_engine_config
        ] = mock_rpc

        request = {}
        client.update_rag_engine_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.update_rag_engine_config(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_update_rag_engine_config_rest_required_fields(
    request_type=vertex_rag_data_service.UpdateRagEngineConfigRequest,
):
    transport_class = transports.VertexRagDataServiceRestTransport

    request_init = {}
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(pb_request, use_integers_for_enums=False)
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_rag_engine_config._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_rag_engine_config._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone

    client = VertexRagDataServiceClient(
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
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.update_rag_engine_config(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_update_rag_engine_config_rest_unset_required_fields():
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.update_rag_engine_config._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("ragEngineConfig",)))


def test_update_rag_engine_config_rest_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "rag_engine_config": {
                "name": "projects/sample1/locations/sample2/ragEngineConfig"
            }
        }

        # get truthy value for each flattened field
        mock_args = dict(
            rag_engine_config=vertex_rag_data.RagEngineConfig(name="name_value"),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.update_rag_engine_config(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{rag_engine_config.name=projects/*/locations/*/ragEngineConfig}"
            % client.transport._host,
            args[1],
        )


def test_update_rag_engine_config_rest_flattened_error(transport: str = "rest"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_rag_engine_config(
            vertex_rag_data_service.UpdateRagEngineConfigRequest(),
            rag_engine_config=vertex_rag_data.RagEngineConfig(name="name_value"),
        )


def test_get_rag_engine_config_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.get_rag_engine_config
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.get_rag_engine_config] = (
            mock_rpc
        )

        request = {}
        client.get_rag_engine_config(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_rag_engine_config(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_get_rag_engine_config_rest_required_fields(
    request_type=vertex_rag_data_service.GetRagEngineConfigRequest,
):
    transport_class = transports.VertexRagDataServiceRestTransport

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
    ).get_rag_engine_config._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_rag_engine_config._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = vertex_rag_data.RagEngineConfig()
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
            return_value = vertex_rag_data.RagEngineConfig.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.get_rag_engine_config(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_rag_engine_config_rest_unset_required_fields():
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_rag_engine_config._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


def test_get_rag_engine_config_rest_flattened():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = vertex_rag_data.RagEngineConfig()

        # get arguments that satisfy an http rule for this method
        sample_request = {"name": "projects/sample1/locations/sample2/ragEngineConfig"}

        # get truthy value for each flattened field
        mock_args = dict(
            name="name_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = vertex_rag_data.RagEngineConfig.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.get_rag_engine_config(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/ragEngineConfig}"
            % client.transport._host,
            args[1],
        )


def test_get_rag_engine_config_rest_flattened_error(transport: str = "rest"):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_rag_engine_config(
            vertex_rag_data_service.GetRagEngineConfigRequest(),
            name="name_value",
        )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.VertexRagDataServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.VertexRagDataServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = VertexRagDataServiceClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide an api_key and a transport instance.
    transport = transports.VertexRagDataServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    options = client_options.ClientOptions()
    options.api_key = "api_key"
    with pytest.raises(ValueError):
        client = VertexRagDataServiceClient(
            client_options=options,
            transport=transport,
        )

    # It is an error to provide an api_key and a credential.
    options = client_options.ClientOptions()
    options.api_key = "api_key"
    with pytest.raises(ValueError):
        client = VertexRagDataServiceClient(
            client_options=options, credentials=ga_credentials.AnonymousCredentials()
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.VertexRagDataServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = VertexRagDataServiceClient(
            client_options={"scopes": ["1", "2"]},
            transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.VertexRagDataServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    client = VertexRagDataServiceClient(transport=transport)
    assert client.transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.VertexRagDataServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.VertexRagDataServiceGrpcAsyncIOTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.VertexRagDataServiceGrpcTransport,
        transports.VertexRagDataServiceGrpcAsyncIOTransport,
        transports.VertexRagDataServiceRestTransport,
    ],
)
def test_transport_adc(transport_class):
    # Test default credentials are used if not provided.
    with mock.patch.object(google.auth, "default") as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport_class()
        adc.assert_called_once()


def test_transport_kind_grpc():
    transport = VertexRagDataServiceClient.get_transport_class("grpc")(
        credentials=ga_credentials.AnonymousCredentials()
    )
    assert transport.kind == "grpc"


def test_initialize_client_w_grpc():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc"
    )
    assert client is not None


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_create_rag_corpus_empty_call_grpc():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.create_rag_corpus), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.create_rag_corpus(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.CreateRagCorpusRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_update_rag_corpus_empty_call_grpc():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.update_rag_corpus), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.update_rag_corpus(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.UpdateRagCorpusRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_rag_corpus_empty_call_grpc():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.get_rag_corpus), "__call__") as call:
        call.return_value = vertex_rag_data.RagCorpus()
        client.get_rag_corpus(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.GetRagCorpusRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_rag_corpora_empty_call_grpc():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_corpora), "__call__") as call:
        call.return_value = vertex_rag_data_service.ListRagCorporaResponse()
        client.list_rag_corpora(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.ListRagCorporaRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_delete_rag_corpus_empty_call_grpc():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_rag_corpus), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_rag_corpus(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.DeleteRagCorpusRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_upload_rag_file_empty_call_grpc():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.upload_rag_file), "__call__") as call:
        call.return_value = vertex_rag_data_service.UploadRagFileResponse()
        client.upload_rag_file(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.UploadRagFileRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_import_rag_files_empty_call_grpc():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.import_rag_files), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.import_rag_files(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.ImportRagFilesRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_rag_file_empty_call_grpc():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.get_rag_file), "__call__") as call:
        call.return_value = vertex_rag_data.RagFile()
        client.get_rag_file(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.GetRagFileRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_rag_files_empty_call_grpc():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_files), "__call__") as call:
        call.return_value = vertex_rag_data_service.ListRagFilesResponse()
        client.list_rag_files(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.ListRagFilesRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_delete_rag_file_empty_call_grpc():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.delete_rag_file), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_rag_file(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.DeleteRagFileRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_update_rag_engine_config_empty_call_grpc():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.update_rag_engine_config), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.update_rag_engine_config(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.UpdateRagEngineConfigRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_rag_engine_config_empty_call_grpc():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.get_rag_engine_config), "__call__"
    ) as call:
        call.return_value = vertex_rag_data.RagEngineConfig()
        client.get_rag_engine_config(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.GetRagEngineConfigRequest()

        assert args[0] == request_msg


def test_transport_kind_grpc_asyncio():
    transport = VertexRagDataServiceAsyncClient.get_transport_class("grpc_asyncio")(
        credentials=async_anonymous_credentials()
    )
    assert transport.kind == "grpc_asyncio"


def test_initialize_client_w_grpc_asyncio():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="grpc_asyncio"
    )
    assert client is not None


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_create_rag_corpus_empty_call_grpc_asyncio():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.create_rag_corpus), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        await client.create_rag_corpus(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.CreateRagCorpusRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_update_rag_corpus_empty_call_grpc_asyncio():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.update_rag_corpus), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        await client.update_rag_corpus(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.UpdateRagCorpusRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_rag_corpus_empty_call_grpc_asyncio():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.get_rag_corpus), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data.RagCorpus(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
                rag_files_count=1588,
            )
        )
        await client.get_rag_corpus(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.GetRagCorpusRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_rag_corpora_empty_call_grpc_asyncio():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_corpora), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data_service.ListRagCorporaResponse(
                next_page_token="next_page_token_value",
            )
        )
        await client.list_rag_corpora(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.ListRagCorporaRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_delete_rag_corpus_empty_call_grpc_asyncio():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_rag_corpus), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        await client.delete_rag_corpus(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.DeleteRagCorpusRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_upload_rag_file_empty_call_grpc_asyncio():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.upload_rag_file), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data_service.UploadRagFileResponse()
        )
        await client.upload_rag_file(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.UploadRagFileRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_import_rag_files_empty_call_grpc_asyncio():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.import_rag_files), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        await client.import_rag_files(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.ImportRagFilesRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_rag_file_empty_call_grpc_asyncio():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.get_rag_file), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data.RagFile(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
                size_bytes=1089,
                rag_file_type=vertex_rag_data.RagFile.RagFileType.RAG_FILE_TYPE_TXT,
                user_metadata="user_metadata_value",
            )
        )
        await client.get_rag_file(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.GetRagFileRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_rag_files_empty_call_grpc_asyncio():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_files), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data_service.ListRagFilesResponse(
                next_page_token="next_page_token_value",
            )
        )
        await client.list_rag_files(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.ListRagFilesRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_delete_rag_file_empty_call_grpc_asyncio():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.delete_rag_file), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        await client.delete_rag_file(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.DeleteRagFileRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_update_rag_engine_config_empty_call_grpc_asyncio():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.update_rag_engine_config), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        await client.update_rag_engine_config(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.UpdateRagEngineConfigRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_rag_engine_config_empty_call_grpc_asyncio():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.get_rag_engine_config), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            vertex_rag_data.RagEngineConfig(
                name="name_value",
            )
        )
        await client.get_rag_engine_config(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.GetRagEngineConfigRequest()

        assert args[0] == request_msg


def test_transport_kind_rest():
    transport = VertexRagDataServiceClient.get_transport_class("rest")(
        credentials=ga_credentials.AnonymousCredentials()
    )
    assert transport.kind == "rest"


def test_create_rag_corpus_rest_bad_request(
    request_type=vertex_rag_data_service.CreateRagCorpusRequest,
):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ""
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.create_rag_corpus(request)


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.CreateRagCorpusRequest,
        dict,
    ],
)
def test_create_rag_corpus_rest_call_success(request_type):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request_init["rag_corpus"] = {
        "vector_db_config": {
            "rag_managed_db": {
                "knn": {},
                "ann": {"tree_depth": 1060, "leaf_count": 1056},
            },
            "weaviate": {
                "http_endpoint": "http_endpoint_value",
                "collection_name": "collection_name_value",
            },
            "pinecone": {"index_name": "index_name_value"},
            "vertex_feature_store": {
                "feature_view_resource_name": "feature_view_resource_name_value"
            },
            "vertex_vector_search": {
                "index_endpoint": "index_endpoint_value",
                "index": "index_value",
            },
            "api_auth": {
                "api_key_config": {
                    "api_key_secret_version": "api_key_secret_version_value"
                }
            },
            "rag_embedding_model_config": {
                "vertex_prediction_endpoint": {
                    "endpoint": "endpoint_value",
                    "model": "model_value",
                    "model_version_id": "model_version_id_value",
                },
                "hybrid_search_config": {
                    "sparse_embedding_config": {
                        "bm25": {"multilingual": True, "k1": 0.156, "b": 0.98}
                    },
                    "dense_embedding_model_prediction_endpoint": {},
                },
            },
        },
        "vertex_ai_search_config": {"serving_config": "serving_config_value"},
        "name": "name_value",
        "display_name": "display_name_value",
        "description": "description_value",
        "rag_embedding_model_config": {},
        "rag_vector_db_config": {},
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
        "corpus_status": {"state": 1, "error_status": "error_status_value"},
        "rag_files_count": 1588,
        "encryption_spec": {"kms_key_name": "kms_key_name_value"},
        "corpus_type_config": {
            "document_corpus": {},
            "memory_corpus": {
                "llm_parser": {
                    "model_name": "model_name_value",
                    "max_parsing_requests_per_min": 3005,
                    "global_max_parsing_requests_per_min": 3725,
                    "custom_parsing_prompt": "custom_parsing_prompt_value",
                }
            },
        },
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = vertex_rag_data_service.CreateRagCorpusRequest.meta.fields[
        "rag_corpus"
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
    for field, value in request_init["rag_corpus"].items():  # pragma: NO COVER
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
                for i in range(0, len(request_init["rag_corpus"][field])):
                    del request_init["rag_corpus"][field][i][subfield]
            else:
                del request_init["rag_corpus"][field][subfield]
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.create_rag_corpus(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_create_rag_corpus_rest_interceptors(null_interceptor):
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.VertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "post_create_rag_corpus"
    ) as post, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor,
        "post_create_rag_corpus_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "pre_create_rag_corpus"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.CreateRagCorpusRequest.pb(
            vertex_rag_data_service.CreateRagCorpusRequest()
        )
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

        request = vertex_rag_data_service.CreateRagCorpusRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.create_rag_corpus(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_update_rag_corpus_rest_bad_request(
    request_type=vertex_rag_data_service.UpdateRagCorpusRequest,
):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "rag_corpus": {"name": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ""
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.update_rag_corpus(request)


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.UpdateRagCorpusRequest,
        dict,
    ],
)
def test_update_rag_corpus_rest_call_success(request_type):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "rag_corpus": {"name": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    }
    request_init["rag_corpus"] = {
        "vector_db_config": {
            "rag_managed_db": {
                "knn": {},
                "ann": {"tree_depth": 1060, "leaf_count": 1056},
            },
            "weaviate": {
                "http_endpoint": "http_endpoint_value",
                "collection_name": "collection_name_value",
            },
            "pinecone": {"index_name": "index_name_value"},
            "vertex_feature_store": {
                "feature_view_resource_name": "feature_view_resource_name_value"
            },
            "vertex_vector_search": {
                "index_endpoint": "index_endpoint_value",
                "index": "index_value",
            },
            "api_auth": {
                "api_key_config": {
                    "api_key_secret_version": "api_key_secret_version_value"
                }
            },
            "rag_embedding_model_config": {
                "vertex_prediction_endpoint": {
                    "endpoint": "endpoint_value",
                    "model": "model_value",
                    "model_version_id": "model_version_id_value",
                },
                "hybrid_search_config": {
                    "sparse_embedding_config": {
                        "bm25": {"multilingual": True, "k1": 0.156, "b": 0.98}
                    },
                    "dense_embedding_model_prediction_endpoint": {},
                },
            },
        },
        "vertex_ai_search_config": {"serving_config": "serving_config_value"},
        "name": "projects/sample1/locations/sample2/ragCorpora/sample3",
        "display_name": "display_name_value",
        "description": "description_value",
        "rag_embedding_model_config": {},
        "rag_vector_db_config": {},
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
        "corpus_status": {"state": 1, "error_status": "error_status_value"},
        "rag_files_count": 1588,
        "encryption_spec": {"kms_key_name": "kms_key_name_value"},
        "corpus_type_config": {
            "document_corpus": {},
            "memory_corpus": {
                "llm_parser": {
                    "model_name": "model_name_value",
                    "max_parsing_requests_per_min": 3005,
                    "global_max_parsing_requests_per_min": 3725,
                    "custom_parsing_prompt": "custom_parsing_prompt_value",
                }
            },
        },
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = vertex_rag_data_service.UpdateRagCorpusRequest.meta.fields[
        "rag_corpus"
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
    for field, value in request_init["rag_corpus"].items():  # pragma: NO COVER
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
                for i in range(0, len(request_init["rag_corpus"][field])):
                    del request_init["rag_corpus"][field][i][subfield]
            else:
                del request_init["rag_corpus"][field][subfield]
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.update_rag_corpus(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_update_rag_corpus_rest_interceptors(null_interceptor):
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.VertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "post_update_rag_corpus"
    ) as post, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor,
        "post_update_rag_corpus_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "pre_update_rag_corpus"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.UpdateRagCorpusRequest.pb(
            vertex_rag_data_service.UpdateRagCorpusRequest()
        )
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

        request = vertex_rag_data_service.UpdateRagCorpusRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.update_rag_corpus(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_get_rag_corpus_rest_bad_request(
    request_type=vertex_rag_data_service.GetRagCorpusRequest,
):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ""
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.get_rag_corpus(request)


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.GetRagCorpusRequest,
        dict,
    ],
)
def test_get_rag_corpus_rest_call_success(request_type):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = vertex_rag_data.RagCorpus(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            rag_files_count=1588,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = vertex_rag_data.RagCorpus.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.get_rag_corpus(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, vertex_rag_data.RagCorpus)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.rag_files_count == 1588


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_rag_corpus_rest_interceptors(null_interceptor):
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.VertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "post_get_rag_corpus"
    ) as post, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor,
        "post_get_rag_corpus_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "pre_get_rag_corpus"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.GetRagCorpusRequest.pb(
            vertex_rag_data_service.GetRagCorpusRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = vertex_rag_data.RagCorpus.to_json(vertex_rag_data.RagCorpus())
        req.return_value.content = return_value

        request = vertex_rag_data_service.GetRagCorpusRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = vertex_rag_data.RagCorpus()
        post_with_metadata.return_value = vertex_rag_data.RagCorpus(), metadata

        client.get_rag_corpus(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_list_rag_corpora_rest_bad_request(
    request_type=vertex_rag_data_service.ListRagCorporaRequest,
):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ""
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.list_rag_corpora(request)


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.ListRagCorporaRequest,
        dict,
    ],
)
def test_list_rag_corpora_rest_call_success(request_type):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = vertex_rag_data_service.ListRagCorporaResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = vertex_rag_data_service.ListRagCorporaResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.list_rag_corpora(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListRagCorporaPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_rag_corpora_rest_interceptors(null_interceptor):
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.VertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "post_list_rag_corpora"
    ) as post, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor,
        "post_list_rag_corpora_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "pre_list_rag_corpora"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.ListRagCorporaRequest.pb(
            vertex_rag_data_service.ListRagCorporaRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = vertex_rag_data_service.ListRagCorporaResponse.to_json(
            vertex_rag_data_service.ListRagCorporaResponse()
        )
        req.return_value.content = return_value

        request = vertex_rag_data_service.ListRagCorporaRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = vertex_rag_data_service.ListRagCorporaResponse()
        post_with_metadata.return_value = (
            vertex_rag_data_service.ListRagCorporaResponse(),
            metadata,
        )

        client.list_rag_corpora(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_delete_rag_corpus_rest_bad_request(
    request_type=vertex_rag_data_service.DeleteRagCorpusRequest,
):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ""
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.delete_rag_corpus(request)


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.DeleteRagCorpusRequest,
        dict,
    ],
)
def test_delete_rag_corpus_rest_call_success(request_type):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.delete_rag_corpus(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_delete_rag_corpus_rest_interceptors(null_interceptor):
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.VertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "post_delete_rag_corpus"
    ) as post, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor,
        "post_delete_rag_corpus_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "pre_delete_rag_corpus"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.DeleteRagCorpusRequest.pb(
            vertex_rag_data_service.DeleteRagCorpusRequest()
        )
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

        request = vertex_rag_data_service.DeleteRagCorpusRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.delete_rag_corpus(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_upload_rag_file_rest_bad_request(
    request_type=vertex_rag_data_service.UploadRagFileRequest,
):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ""
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.upload_rag_file(request)


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.UploadRagFileRequest,
        dict,
    ],
)
def test_upload_rag_file_rest_call_success(request_type):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = vertex_rag_data_service.UploadRagFileResponse()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = vertex_rag_data_service.UploadRagFileResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.upload_rag_file(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, vertex_rag_data_service.UploadRagFileResponse)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_upload_rag_file_rest_interceptors(null_interceptor):
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.VertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "post_upload_rag_file"
    ) as post, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor,
        "post_upload_rag_file_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "pre_upload_rag_file"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.UploadRagFileRequest.pb(
            vertex_rag_data_service.UploadRagFileRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = vertex_rag_data_service.UploadRagFileResponse.to_json(
            vertex_rag_data_service.UploadRagFileResponse()
        )
        req.return_value.content = return_value

        request = vertex_rag_data_service.UploadRagFileRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = vertex_rag_data_service.UploadRagFileResponse()
        post_with_metadata.return_value = (
            vertex_rag_data_service.UploadRagFileResponse(),
            metadata,
        )

        client.upload_rag_file(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_import_rag_files_rest_bad_request(
    request_type=vertex_rag_data_service.ImportRagFilesRequest,
):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ""
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.import_rag_files(request)


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.ImportRagFilesRequest,
        dict,
    ],
)
def test_import_rag_files_rest_call_success(request_type):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.import_rag_files(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_import_rag_files_rest_interceptors(null_interceptor):
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.VertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "post_import_rag_files"
    ) as post, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor,
        "post_import_rag_files_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "pre_import_rag_files"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.ImportRagFilesRequest.pb(
            vertex_rag_data_service.ImportRagFilesRequest()
        )
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

        request = vertex_rag_data_service.ImportRagFilesRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.import_rag_files(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_get_rag_file_rest_bad_request(
    request_type=vertex_rag_data_service.GetRagFileRequest,
):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/ragCorpora/sample3/ragFiles/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ""
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.get_rag_file(request)


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.GetRagFileRequest,
        dict,
    ],
)
def test_get_rag_file_rest_call_success(request_type):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/ragCorpora/sample3/ragFiles/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = vertex_rag_data.RagFile(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            size_bytes=1089,
            rag_file_type=vertex_rag_data.RagFile.RagFileType.RAG_FILE_TYPE_TXT,
            user_metadata="user_metadata_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = vertex_rag_data.RagFile.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.get_rag_file(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, vertex_rag_data.RagFile)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.size_bytes == 1089
    assert (
        response.rag_file_type == vertex_rag_data.RagFile.RagFileType.RAG_FILE_TYPE_TXT
    )
    assert response.user_metadata == "user_metadata_value"


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_rag_file_rest_interceptors(null_interceptor):
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.VertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "post_get_rag_file"
    ) as post, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor,
        "post_get_rag_file_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "pre_get_rag_file"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.GetRagFileRequest.pb(
            vertex_rag_data_service.GetRagFileRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = vertex_rag_data.RagFile.to_json(vertex_rag_data.RagFile())
        req.return_value.content = return_value

        request = vertex_rag_data_service.GetRagFileRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = vertex_rag_data.RagFile()
        post_with_metadata.return_value = vertex_rag_data.RagFile(), metadata

        client.get_rag_file(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_list_rag_files_rest_bad_request(
    request_type=vertex_rag_data_service.ListRagFilesRequest,
):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ""
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.list_rag_files(request)


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.ListRagFilesRequest,
        dict,
    ],
)
def test_list_rag_files_rest_call_success(request_type):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = vertex_rag_data_service.ListRagFilesResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = vertex_rag_data_service.ListRagFilesResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.list_rag_files(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListRagFilesPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_rag_files_rest_interceptors(null_interceptor):
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.VertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "post_list_rag_files"
    ) as post, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor,
        "post_list_rag_files_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "pre_list_rag_files"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.ListRagFilesRequest.pb(
            vertex_rag_data_service.ListRagFilesRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = vertex_rag_data_service.ListRagFilesResponse.to_json(
            vertex_rag_data_service.ListRagFilesResponse()
        )
        req.return_value.content = return_value

        request = vertex_rag_data_service.ListRagFilesRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = vertex_rag_data_service.ListRagFilesResponse()
        post_with_metadata.return_value = (
            vertex_rag_data_service.ListRagFilesResponse(),
            metadata,
        )

        client.list_rag_files(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_delete_rag_file_rest_bad_request(
    request_type=vertex_rag_data_service.DeleteRagFileRequest,
):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/ragCorpora/sample3/ragFiles/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ""
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.delete_rag_file(request)


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.DeleteRagFileRequest,
        dict,
    ],
)
def test_delete_rag_file_rest_call_success(request_type):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/ragCorpora/sample3/ragFiles/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.delete_rag_file(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_delete_rag_file_rest_interceptors(null_interceptor):
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.VertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "post_delete_rag_file"
    ) as post, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor,
        "post_delete_rag_file_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "pre_delete_rag_file"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.DeleteRagFileRequest.pb(
            vertex_rag_data_service.DeleteRagFileRequest()
        )
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

        request = vertex_rag_data_service.DeleteRagFileRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.delete_rag_file(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_update_rag_engine_config_rest_bad_request(
    request_type=vertex_rag_data_service.UpdateRagEngineConfigRequest,
):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "rag_engine_config": {
            "name": "projects/sample1/locations/sample2/ragEngineConfig"
        }
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ""
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.update_rag_engine_config(request)


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.UpdateRagEngineConfigRequest,
        dict,
    ],
)
def test_update_rag_engine_config_rest_call_success(request_type):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "rag_engine_config": {
            "name": "projects/sample1/locations/sample2/ragEngineConfig"
        }
    }
    request_init["rag_engine_config"] = {
        "name": "projects/sample1/locations/sample2/ragEngineConfig",
        "rag_managed_db_config": {
            "enterprise": {},
            "scaled": {},
            "basic": {},
            "unprovisioned": {},
        },
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = vertex_rag_data_service.UpdateRagEngineConfigRequest.meta.fields[
        "rag_engine_config"
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
    for field, value in request_init["rag_engine_config"].items():  # pragma: NO COVER
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
                for i in range(0, len(request_init["rag_engine_config"][field])):
                    del request_init["rag_engine_config"][field][i][subfield]
            else:
                del request_init["rag_engine_config"][field][subfield]
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.update_rag_engine_config(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_update_rag_engine_config_rest_interceptors(null_interceptor):
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.VertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "post_update_rag_engine_config"
    ) as post, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor,
        "post_update_rag_engine_config_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "pre_update_rag_engine_config"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.UpdateRagEngineConfigRequest.pb(
            vertex_rag_data_service.UpdateRagEngineConfigRequest()
        )
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

        request = vertex_rag_data_service.UpdateRagEngineConfigRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.update_rag_engine_config(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_get_rag_engine_config_rest_bad_request(
    request_type=vertex_rag_data_service.GetRagEngineConfigRequest,
):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/ragEngineConfig"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        json_return_value = ""
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.get_rag_engine_config(request)


@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.GetRagEngineConfigRequest,
        dict,
    ],
)
def test_get_rag_engine_config_rest_call_success(request_type):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/ragEngineConfig"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = vertex_rag_data.RagEngineConfig(
            name="name_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = vertex_rag_data.RagEngineConfig.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.get_rag_engine_config(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, vertex_rag_data.RagEngineConfig)
    assert response.name == "name_value"


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_rag_engine_config_rest_interceptors(null_interceptor):
    transport = transports.VertexRagDataServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.VertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "post_get_rag_engine_config"
    ) as post, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor,
        "post_get_rag_engine_config_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.VertexRagDataServiceRestInterceptor, "pre_get_rag_engine_config"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.GetRagEngineConfigRequest.pb(
            vertex_rag_data_service.GetRagEngineConfigRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = vertex_rag_data.RagEngineConfig.to_json(
            vertex_rag_data.RagEngineConfig()
        )
        req.return_value.content = return_value

        request = vertex_rag_data_service.GetRagEngineConfigRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = vertex_rag_data.RagEngineConfig()
        post_with_metadata.return_value = vertex_rag_data.RagEngineConfig(), metadata

        client.get_rag_engine_config(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_get_location_rest_bad_request(request_type=locations_pb2.GetLocationRequest):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
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
        json_return_value = ""
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.get_location(request)


@pytest.mark.parametrize(
    "request_type",
    [
        locations_pb2.GetLocationRequest,
        dict,
    ],
)
def test_get_location_rest(request_type):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    request_init = {"name": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = locations_pb2.Location()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = client.get_location(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, locations_pb2.Location)


def test_list_locations_rest_bad_request(
    request_type=locations_pb2.ListLocationsRequest,
):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type()
    request = json_format.ParseDict({"name": "projects/sample1"}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        json_return_value = ""
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.list_locations(request)


@pytest.mark.parametrize(
    "request_type",
    [
        locations_pb2.ListLocationsRequest,
        dict,
    ],
)
def test_list_locations_rest(request_type):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    request_init = {"name": "projects/sample1"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = locations_pb2.ListLocationsResponse()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = client.list_locations(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, locations_pb2.ListLocationsResponse)


def test_get_iam_policy_rest_bad_request(
    request_type=iam_policy_pb2.GetIamPolicyRequest,
):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
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
        json_return_value = ""
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.get_iam_policy(request)


@pytest.mark.parametrize(
    "request_type",
    [
        iam_policy_pb2.GetIamPolicyRequest,
        dict,
    ],
)
def test_get_iam_policy_rest(request_type):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    request_init = {
        "resource": "projects/sample1/locations/sample2/featurestores/sample3"
    }
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = policy_pb2.Policy()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = client.get_iam_policy(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy_pb2.Policy)


def test_set_iam_policy_rest_bad_request(
    request_type=iam_policy_pb2.SetIamPolicyRequest,
):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
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
        json_return_value = ""
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.set_iam_policy(request)


@pytest.mark.parametrize(
    "request_type",
    [
        iam_policy_pb2.SetIamPolicyRequest,
        dict,
    ],
)
def test_set_iam_policy_rest(request_type):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    request_init = {
        "resource": "projects/sample1/locations/sample2/featurestores/sample3"
    }
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = policy_pb2.Policy()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = client.set_iam_policy(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy_pb2.Policy)


def test_test_iam_permissions_rest_bad_request(
    request_type=iam_policy_pb2.TestIamPermissionsRequest,
):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
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
        json_return_value = ""
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.test_iam_permissions(request)


@pytest.mark.parametrize(
    "request_type",
    [
        iam_policy_pb2.TestIamPermissionsRequest,
        dict,
    ],
)
def test_test_iam_permissions_rest(request_type):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    request_init = {
        "resource": "projects/sample1/locations/sample2/featurestores/sample3"
    }
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = iam_policy_pb2.TestIamPermissionsResponse()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = client.test_iam_permissions(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, iam_policy_pb2.TestIamPermissionsResponse)


def test_cancel_operation_rest_bad_request(
    request_type=operations_pb2.CancelOperationRequest,
):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
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
        json_return_value = ""
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.cancel_operation(request)


@pytest.mark.parametrize(
    "request_type",
    [
        operations_pb2.CancelOperationRequest,
        dict,
    ],
)
def test_cancel_operation_rest(request_type):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    request_init = {"name": "projects/sample1/locations/sample2/operations/sample3"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = "{}"
        response_value.content = json_return_value.encode("UTF-8")

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = client.cancel_operation(request)

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_operation_rest_bad_request(
    request_type=operations_pb2.DeleteOperationRequest,
):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
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
        json_return_value = ""
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.delete_operation(request)


@pytest.mark.parametrize(
    "request_type",
    [
        operations_pb2.DeleteOperationRequest,
        dict,
    ],
)
def test_delete_operation_rest(request_type):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    request_init = {"name": "projects/sample1/locations/sample2/operations/sample3"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = "{}"
        response_value.content = json_return_value.encode("UTF-8")

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = client.delete_operation(request)

    # Establish that the response is the type that we expect.
    assert response is None


def test_get_operation_rest_bad_request(
    request_type=operations_pb2.GetOperationRequest,
):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
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
        json_return_value = ""
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.get_operation(request)


@pytest.mark.parametrize(
    "request_type",
    [
        operations_pb2.GetOperationRequest,
        dict,
    ],
)
def test_get_operation_rest(request_type):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    request_init = {"name": "projects/sample1/locations/sample2/operations/sample3"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = client.get_operation(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.Operation)


def test_list_operations_rest_bad_request(
    request_type=operations_pb2.ListOperationsRequest,
):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
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
        json_return_value = ""
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.list_operations(request)


@pytest.mark.parametrize(
    "request_type",
    [
        operations_pb2.ListOperationsRequest,
        dict,
    ],
)
def test_list_operations_rest(request_type):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    request_init = {"name": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.ListOperationsResponse()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = client.list_operations(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.ListOperationsResponse)


def test_wait_operation_rest_bad_request(
    request_type=operations_pb2.WaitOperationRequest,
):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
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
        json_return_value = ""
        response_value.json = mock.Mock(return_value={})
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        client.wait_operation(request)


@pytest.mark.parametrize(
    "request_type",
    [
        operations_pb2.WaitOperationRequest,
        dict,
    ],
)
def test_wait_operation_rest(request_type):
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    request_init = {"name": "projects/sample1/locations/sample2/operations/sample3"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = client.wait_operation(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.Operation)


def test_initialize_client_w_rest():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    assert client is not None


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_create_rag_corpus_empty_call_rest():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.create_rag_corpus), "__call__"
    ) as call:
        client.create_rag_corpus(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.CreateRagCorpusRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_update_rag_corpus_empty_call_rest():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.update_rag_corpus), "__call__"
    ) as call:
        client.update_rag_corpus(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.UpdateRagCorpusRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_rag_corpus_empty_call_rest():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.get_rag_corpus), "__call__") as call:
        client.get_rag_corpus(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.GetRagCorpusRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_rag_corpora_empty_call_rest():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_corpora), "__call__") as call:
        client.list_rag_corpora(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.ListRagCorporaRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_delete_rag_corpus_empty_call_rest():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_rag_corpus), "__call__"
    ) as call:
        client.delete_rag_corpus(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.DeleteRagCorpusRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_upload_rag_file_empty_call_rest():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.upload_rag_file), "__call__") as call:
        client.upload_rag_file(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.UploadRagFileRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_import_rag_files_empty_call_rest():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.import_rag_files), "__call__") as call:
        client.import_rag_files(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.ImportRagFilesRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_rag_file_empty_call_rest():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.get_rag_file), "__call__") as call:
        client.get_rag_file(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.GetRagFileRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_rag_files_empty_call_rest():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_files), "__call__") as call:
        client.list_rag_files(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.ListRagFilesRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_delete_rag_file_empty_call_rest():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.delete_rag_file), "__call__") as call:
        client.delete_rag_file(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.DeleteRagFileRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_update_rag_engine_config_empty_call_rest():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.update_rag_engine_config), "__call__"
    ) as call:
        client.update_rag_engine_config(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.UpdateRagEngineConfigRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_rag_engine_config_empty_call_rest():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.get_rag_engine_config), "__call__"
    ) as call:
        client.get_rag_engine_config(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.GetRagEngineConfigRequest()

        assert args[0] == request_msg


def test_vertex_rag_data_service_rest_lro_client():
    client = VertexRagDataServiceClient(
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
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = VertexRagDataServiceAsyncClient.get_transport_class("rest_asyncio")(
        credentials=async_anonymous_credentials()
    )
    assert transport.kind == "rest_asyncio"


@pytest.mark.asyncio
async def test_create_rag_corpus_rest_asyncio_bad_request(
    request_type=vertex_rag_data_service.CreateRagCorpusRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b"{}")
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.create_rag_corpus(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.CreateRagCorpusRequest,
        dict,
    ],
)
async def test_create_rag_corpus_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request_init["rag_corpus"] = {
        "vector_db_config": {
            "rag_managed_db": {
                "knn": {},
                "ann": {"tree_depth": 1060, "leaf_count": 1056},
            },
            "weaviate": {
                "http_endpoint": "http_endpoint_value",
                "collection_name": "collection_name_value",
            },
            "pinecone": {"index_name": "index_name_value"},
            "vertex_feature_store": {
                "feature_view_resource_name": "feature_view_resource_name_value"
            },
            "vertex_vector_search": {
                "index_endpoint": "index_endpoint_value",
                "index": "index_value",
            },
            "api_auth": {
                "api_key_config": {
                    "api_key_secret_version": "api_key_secret_version_value"
                }
            },
            "rag_embedding_model_config": {
                "vertex_prediction_endpoint": {
                    "endpoint": "endpoint_value",
                    "model": "model_value",
                    "model_version_id": "model_version_id_value",
                },
                "hybrid_search_config": {
                    "sparse_embedding_config": {
                        "bm25": {"multilingual": True, "k1": 0.156, "b": 0.98}
                    },
                    "dense_embedding_model_prediction_endpoint": {},
                },
            },
        },
        "vertex_ai_search_config": {"serving_config": "serving_config_value"},
        "name": "name_value",
        "display_name": "display_name_value",
        "description": "description_value",
        "rag_embedding_model_config": {},
        "rag_vector_db_config": {},
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
        "corpus_status": {"state": 1, "error_status": "error_status_value"},
        "rag_files_count": 1588,
        "encryption_spec": {"kms_key_name": "kms_key_name_value"},
        "corpus_type_config": {
            "document_corpus": {},
            "memory_corpus": {
                "llm_parser": {
                    "model_name": "model_name_value",
                    "max_parsing_requests_per_min": 3005,
                    "global_max_parsing_requests_per_min": 3725,
                    "custom_parsing_prompt": "custom_parsing_prompt_value",
                }
            },
        },
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = vertex_rag_data_service.CreateRagCorpusRequest.meta.fields[
        "rag_corpus"
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
    for field, value in request_init["rag_corpus"].items():  # pragma: NO COVER
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
                for i in range(0, len(request_init["rag_corpus"][field])):
                    del request_init["rag_corpus"][field][i][subfield]
            else:
                del request_init["rag_corpus"][field][subfield]
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.create_rag_corpus(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_create_rag_corpus_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncVertexRagDataServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncVertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor, "post_create_rag_corpus"
    ) as post, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor,
        "post_create_rag_corpus_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor, "pre_create_rag_corpus"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.CreateRagCorpusRequest.pb(
            vertex_rag_data_service.CreateRagCorpusRequest()
        )
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

        request = vertex_rag_data_service.CreateRagCorpusRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.create_rag_corpus(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


@pytest.mark.asyncio
async def test_update_rag_corpus_rest_asyncio_bad_request(
    request_type=vertex_rag_data_service.UpdateRagCorpusRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "rag_corpus": {"name": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b"{}")
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.update_rag_corpus(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.UpdateRagCorpusRequest,
        dict,
    ],
)
async def test_update_rag_corpus_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "rag_corpus": {"name": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    }
    request_init["rag_corpus"] = {
        "vector_db_config": {
            "rag_managed_db": {
                "knn": {},
                "ann": {"tree_depth": 1060, "leaf_count": 1056},
            },
            "weaviate": {
                "http_endpoint": "http_endpoint_value",
                "collection_name": "collection_name_value",
            },
            "pinecone": {"index_name": "index_name_value"},
            "vertex_feature_store": {
                "feature_view_resource_name": "feature_view_resource_name_value"
            },
            "vertex_vector_search": {
                "index_endpoint": "index_endpoint_value",
                "index": "index_value",
            },
            "api_auth": {
                "api_key_config": {
                    "api_key_secret_version": "api_key_secret_version_value"
                }
            },
            "rag_embedding_model_config": {
                "vertex_prediction_endpoint": {
                    "endpoint": "endpoint_value",
                    "model": "model_value",
                    "model_version_id": "model_version_id_value",
                },
                "hybrid_search_config": {
                    "sparse_embedding_config": {
                        "bm25": {"multilingual": True, "k1": 0.156, "b": 0.98}
                    },
                    "dense_embedding_model_prediction_endpoint": {},
                },
            },
        },
        "vertex_ai_search_config": {"serving_config": "serving_config_value"},
        "name": "projects/sample1/locations/sample2/ragCorpora/sample3",
        "display_name": "display_name_value",
        "description": "description_value",
        "rag_embedding_model_config": {},
        "rag_vector_db_config": {},
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
        "corpus_status": {"state": 1, "error_status": "error_status_value"},
        "rag_files_count": 1588,
        "encryption_spec": {"kms_key_name": "kms_key_name_value"},
        "corpus_type_config": {
            "document_corpus": {},
            "memory_corpus": {
                "llm_parser": {
                    "model_name": "model_name_value",
                    "max_parsing_requests_per_min": 3005,
                    "global_max_parsing_requests_per_min": 3725,
                    "custom_parsing_prompt": "custom_parsing_prompt_value",
                }
            },
        },
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = vertex_rag_data_service.UpdateRagCorpusRequest.meta.fields[
        "rag_corpus"
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
    for field, value in request_init["rag_corpus"].items():  # pragma: NO COVER
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
                for i in range(0, len(request_init["rag_corpus"][field])):
                    del request_init["rag_corpus"][field][i][subfield]
            else:
                del request_init["rag_corpus"][field][subfield]
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.update_rag_corpus(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_update_rag_corpus_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncVertexRagDataServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncVertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor, "post_update_rag_corpus"
    ) as post, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor,
        "post_update_rag_corpus_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor, "pre_update_rag_corpus"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.UpdateRagCorpusRequest.pb(
            vertex_rag_data_service.UpdateRagCorpusRequest()
        )
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

        request = vertex_rag_data_service.UpdateRagCorpusRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.update_rag_corpus(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


@pytest.mark.asyncio
async def test_get_rag_corpus_rest_asyncio_bad_request(
    request_type=vertex_rag_data_service.GetRagCorpusRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b"{}")
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.get_rag_corpus(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.GetRagCorpusRequest,
        dict,
    ],
)
async def test_get_rag_corpus_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = vertex_rag_data.RagCorpus(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            rag_files_count=1588,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = vertex_rag_data.RagCorpus.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.get_rag_corpus(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, vertex_rag_data.RagCorpus)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.rag_files_count == 1588


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_get_rag_corpus_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncVertexRagDataServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncVertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor, "post_get_rag_corpus"
    ) as post, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor,
        "post_get_rag_corpus_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor, "pre_get_rag_corpus"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.GetRagCorpusRequest.pb(
            vertex_rag_data_service.GetRagCorpusRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = vertex_rag_data.RagCorpus.to_json(vertex_rag_data.RagCorpus())
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = vertex_rag_data_service.GetRagCorpusRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = vertex_rag_data.RagCorpus()
        post_with_metadata.return_value = vertex_rag_data.RagCorpus(), metadata

        await client.get_rag_corpus(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


@pytest.mark.asyncio
async def test_list_rag_corpora_rest_asyncio_bad_request(
    request_type=vertex_rag_data_service.ListRagCorporaRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b"{}")
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.list_rag_corpora(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.ListRagCorporaRequest,
        dict,
    ],
)
async def test_list_rag_corpora_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = vertex_rag_data_service.ListRagCorporaResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = vertex_rag_data_service.ListRagCorporaResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.list_rag_corpora(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListRagCorporaAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_list_rag_corpora_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncVertexRagDataServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncVertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor, "post_list_rag_corpora"
    ) as post, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor,
        "post_list_rag_corpora_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor, "pre_list_rag_corpora"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.ListRagCorporaRequest.pb(
            vertex_rag_data_service.ListRagCorporaRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = vertex_rag_data_service.ListRagCorporaResponse.to_json(
            vertex_rag_data_service.ListRagCorporaResponse()
        )
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = vertex_rag_data_service.ListRagCorporaRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = vertex_rag_data_service.ListRagCorporaResponse()
        post_with_metadata.return_value = (
            vertex_rag_data_service.ListRagCorporaResponse(),
            metadata,
        )

        await client.list_rag_corpora(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


@pytest.mark.asyncio
async def test_delete_rag_corpus_rest_asyncio_bad_request(
    request_type=vertex_rag_data_service.DeleteRagCorpusRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b"{}")
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.delete_rag_corpus(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.DeleteRagCorpusRequest,
        dict,
    ],
)
async def test_delete_rag_corpus_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.delete_rag_corpus(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_delete_rag_corpus_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncVertexRagDataServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncVertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor, "post_delete_rag_corpus"
    ) as post, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor,
        "post_delete_rag_corpus_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor, "pre_delete_rag_corpus"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.DeleteRagCorpusRequest.pb(
            vertex_rag_data_service.DeleteRagCorpusRequest()
        )
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

        request = vertex_rag_data_service.DeleteRagCorpusRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.delete_rag_corpus(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


@pytest.mark.asyncio
async def test_upload_rag_file_rest_asyncio_bad_request(
    request_type=vertex_rag_data_service.UploadRagFileRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b"{}")
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.upload_rag_file(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.UploadRagFileRequest,
        dict,
    ],
)
async def test_upload_rag_file_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = vertex_rag_data_service.UploadRagFileResponse()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = vertex_rag_data_service.UploadRagFileResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.upload_rag_file(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, vertex_rag_data_service.UploadRagFileResponse)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_upload_rag_file_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncVertexRagDataServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncVertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor, "post_upload_rag_file"
    ) as post, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor,
        "post_upload_rag_file_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor, "pre_upload_rag_file"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.UploadRagFileRequest.pb(
            vertex_rag_data_service.UploadRagFileRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = vertex_rag_data_service.UploadRagFileResponse.to_json(
            vertex_rag_data_service.UploadRagFileResponse()
        )
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = vertex_rag_data_service.UploadRagFileRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = vertex_rag_data_service.UploadRagFileResponse()
        post_with_metadata.return_value = (
            vertex_rag_data_service.UploadRagFileResponse(),
            metadata,
        )

        await client.upload_rag_file(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


@pytest.mark.asyncio
async def test_import_rag_files_rest_asyncio_bad_request(
    request_type=vertex_rag_data_service.ImportRagFilesRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b"{}")
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.import_rag_files(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.ImportRagFilesRequest,
        dict,
    ],
)
async def test_import_rag_files_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.import_rag_files(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_import_rag_files_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncVertexRagDataServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncVertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor, "post_import_rag_files"
    ) as post, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor,
        "post_import_rag_files_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor, "pre_import_rag_files"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.ImportRagFilesRequest.pb(
            vertex_rag_data_service.ImportRagFilesRequest()
        )
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

        request = vertex_rag_data_service.ImportRagFilesRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.import_rag_files(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


@pytest.mark.asyncio
async def test_get_rag_file_rest_asyncio_bad_request(
    request_type=vertex_rag_data_service.GetRagFileRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/ragCorpora/sample3/ragFiles/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b"{}")
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.get_rag_file(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.GetRagFileRequest,
        dict,
    ],
)
async def test_get_rag_file_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/ragCorpora/sample3/ragFiles/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = vertex_rag_data.RagFile(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            size_bytes=1089,
            rag_file_type=vertex_rag_data.RagFile.RagFileType.RAG_FILE_TYPE_TXT,
            user_metadata="user_metadata_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = vertex_rag_data.RagFile.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.get_rag_file(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, vertex_rag_data.RagFile)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.size_bytes == 1089
    assert (
        response.rag_file_type == vertex_rag_data.RagFile.RagFileType.RAG_FILE_TYPE_TXT
    )
    assert response.user_metadata == "user_metadata_value"


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_get_rag_file_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncVertexRagDataServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncVertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor, "post_get_rag_file"
    ) as post, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor,
        "post_get_rag_file_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor, "pre_get_rag_file"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.GetRagFileRequest.pb(
            vertex_rag_data_service.GetRagFileRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = vertex_rag_data.RagFile.to_json(vertex_rag_data.RagFile())
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = vertex_rag_data_service.GetRagFileRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = vertex_rag_data.RagFile()
        post_with_metadata.return_value = vertex_rag_data.RagFile(), metadata

        await client.get_rag_file(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


@pytest.mark.asyncio
async def test_list_rag_files_rest_asyncio_bad_request(
    request_type=vertex_rag_data_service.ListRagFilesRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b"{}")
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.list_rag_files(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.ListRagFilesRequest,
        dict,
    ],
)
async def test_list_rag_files_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/ragCorpora/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = vertex_rag_data_service.ListRagFilesResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = vertex_rag_data_service.ListRagFilesResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.list_rag_files(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListRagFilesAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_list_rag_files_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncVertexRagDataServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncVertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor, "post_list_rag_files"
    ) as post, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor,
        "post_list_rag_files_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor, "pre_list_rag_files"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.ListRagFilesRequest.pb(
            vertex_rag_data_service.ListRagFilesRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = vertex_rag_data_service.ListRagFilesResponse.to_json(
            vertex_rag_data_service.ListRagFilesResponse()
        )
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = vertex_rag_data_service.ListRagFilesRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = vertex_rag_data_service.ListRagFilesResponse()
        post_with_metadata.return_value = (
            vertex_rag_data_service.ListRagFilesResponse(),
            metadata,
        )

        await client.list_rag_files(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


@pytest.mark.asyncio
async def test_delete_rag_file_rest_asyncio_bad_request(
    request_type=vertex_rag_data_service.DeleteRagFileRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/ragCorpora/sample3/ragFiles/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b"{}")
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.delete_rag_file(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.DeleteRagFileRequest,
        dict,
    ],
)
async def test_delete_rag_file_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/ragCorpora/sample3/ragFiles/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.delete_rag_file(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_delete_rag_file_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncVertexRagDataServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncVertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor, "post_delete_rag_file"
    ) as post, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor,
        "post_delete_rag_file_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor, "pre_delete_rag_file"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.DeleteRagFileRequest.pb(
            vertex_rag_data_service.DeleteRagFileRequest()
        )
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

        request = vertex_rag_data_service.DeleteRagFileRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.delete_rag_file(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


@pytest.mark.asyncio
async def test_update_rag_engine_config_rest_asyncio_bad_request(
    request_type=vertex_rag_data_service.UpdateRagEngineConfigRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "rag_engine_config": {
            "name": "projects/sample1/locations/sample2/ragEngineConfig"
        }
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b"{}")
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.update_rag_engine_config(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.UpdateRagEngineConfigRequest,
        dict,
    ],
)
async def test_update_rag_engine_config_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "rag_engine_config": {
            "name": "projects/sample1/locations/sample2/ragEngineConfig"
        }
    }
    request_init["rag_engine_config"] = {
        "name": "projects/sample1/locations/sample2/ragEngineConfig",
        "rag_managed_db_config": {
            "enterprise": {},
            "scaled": {},
            "basic": {},
            "unprovisioned": {},
        },
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = vertex_rag_data_service.UpdateRagEngineConfigRequest.meta.fields[
        "rag_engine_config"
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
    for field, value in request_init["rag_engine_config"].items():  # pragma: NO COVER
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
                for i in range(0, len(request_init["rag_engine_config"][field])):
                    del request_init["rag_engine_config"][field][i][subfield]
            else:
                del request_init["rag_engine_config"][field][subfield]
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.update_rag_engine_config(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_update_rag_engine_config_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncVertexRagDataServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncVertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor,
        "post_update_rag_engine_config",
    ) as post, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor,
        "post_update_rag_engine_config_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor,
        "pre_update_rag_engine_config",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.UpdateRagEngineConfigRequest.pb(
            vertex_rag_data_service.UpdateRagEngineConfigRequest()
        )
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

        request = vertex_rag_data_service.UpdateRagEngineConfigRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.update_rag_engine_config(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


@pytest.mark.asyncio
async def test_get_rag_engine_config_rest_asyncio_bad_request(
    request_type=vertex_rag_data_service.GetRagEngineConfigRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/ragEngineConfig"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b"{}")
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.get_rag_engine_config(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        vertex_rag_data_service.GetRagEngineConfigRequest,
        dict,
    ],
)
async def test_get_rag_engine_config_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/ragEngineConfig"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = vertex_rag_data.RagEngineConfig(
            name="name_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = vertex_rag_data.RagEngineConfig.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.get_rag_engine_config(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, vertex_rag_data.RagEngineConfig)
    assert response.name == "name_value"


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_get_rag_engine_config_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncVertexRagDataServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncVertexRagDataServiceRestInterceptor()
        ),
    )
    client = VertexRagDataServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor,
        "post_get_rag_engine_config",
    ) as post, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor,
        "post_get_rag_engine_config_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncVertexRagDataServiceRestInterceptor, "pre_get_rag_engine_config"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = vertex_rag_data_service.GetRagEngineConfigRequest.pb(
            vertex_rag_data_service.GetRagEngineConfigRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = mock.Mock()
        req.return_value.status_code = 200
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        return_value = vertex_rag_data.RagEngineConfig.to_json(
            vertex_rag_data.RagEngineConfig()
        )
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = vertex_rag_data_service.GetRagEngineConfigRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = vertex_rag_data.RagEngineConfig()
        post_with_metadata.return_value = vertex_rag_data.RagEngineConfig(), metadata

        await client.get_rag_engine_config(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


@pytest.mark.asyncio
async def test_get_location_rest_asyncio_bad_request(
    request_type=locations_pb2.GetLocationRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )
    request = request_type()
    request = json_format.ParseDict(
        {"name": "projects/sample1/locations/sample2"}, request
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b"{}")
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.get_location(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        locations_pb2.GetLocationRequest,
        dict,
    ],
)
async def test_get_location_rest_asyncio(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    request_init = {"name": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = locations_pb2.Location()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = await client.get_location(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, locations_pb2.Location)


@pytest.mark.asyncio
async def test_list_locations_rest_asyncio_bad_request(
    request_type=locations_pb2.ListLocationsRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )
    request = request_type()
    request = json_format.ParseDict({"name": "projects/sample1"}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b"{}")
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.list_locations(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        locations_pb2.ListLocationsRequest,
        dict,
    ],
)
async def test_list_locations_rest_asyncio(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    request_init = {"name": "projects/sample1"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = locations_pb2.ListLocationsResponse()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = await client.list_locations(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, locations_pb2.ListLocationsResponse)


@pytest.mark.asyncio
async def test_get_iam_policy_rest_asyncio_bad_request(
    request_type=iam_policy_pb2.GetIamPolicyRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )
    request = request_type()
    request = json_format.ParseDict(
        {"resource": "projects/sample1/locations/sample2/featurestores/sample3"},
        request,
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b"{}")
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.get_iam_policy(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        iam_policy_pb2.GetIamPolicyRequest,
        dict,
    ],
)
async def test_get_iam_policy_rest_asyncio(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    request_init = {
        "resource": "projects/sample1/locations/sample2/featurestores/sample3"
    }
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = policy_pb2.Policy()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = await client.get_iam_policy(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy_pb2.Policy)


@pytest.mark.asyncio
async def test_set_iam_policy_rest_asyncio_bad_request(
    request_type=iam_policy_pb2.SetIamPolicyRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )
    request = request_type()
    request = json_format.ParseDict(
        {"resource": "projects/sample1/locations/sample2/featurestores/sample3"},
        request,
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b"{}")
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.set_iam_policy(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        iam_policy_pb2.SetIamPolicyRequest,
        dict,
    ],
)
async def test_set_iam_policy_rest_asyncio(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    request_init = {
        "resource": "projects/sample1/locations/sample2/featurestores/sample3"
    }
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = policy_pb2.Policy()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = await client.set_iam_policy(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy_pb2.Policy)


@pytest.mark.asyncio
async def test_test_iam_permissions_rest_asyncio_bad_request(
    request_type=iam_policy_pb2.TestIamPermissionsRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )
    request = request_type()
    request = json_format.ParseDict(
        {"resource": "projects/sample1/locations/sample2/featurestores/sample3"},
        request,
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b"{}")
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.test_iam_permissions(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        iam_policy_pb2.TestIamPermissionsRequest,
        dict,
    ],
)
async def test_test_iam_permissions_rest_asyncio(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    request_init = {
        "resource": "projects/sample1/locations/sample2/featurestores/sample3"
    }
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = iam_policy_pb2.TestIamPermissionsResponse()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = await client.test_iam_permissions(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, iam_policy_pb2.TestIamPermissionsResponse)


@pytest.mark.asyncio
async def test_cancel_operation_rest_asyncio_bad_request(
    request_type=operations_pb2.CancelOperationRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )
    request = request_type()
    request = json_format.ParseDict(
        {"name": "projects/sample1/locations/sample2/operations/sample3"}, request
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b"{}")
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.cancel_operation(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        operations_pb2.CancelOperationRequest,
        dict,
    ],
)
async def test_cancel_operation_rest_asyncio(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    request_init = {"name": "projects/sample1/locations/sample2/operations/sample3"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = "{}"
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = await client.cancel_operation(request)

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_delete_operation_rest_asyncio_bad_request(
    request_type=operations_pb2.DeleteOperationRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )
    request = request_type()
    request = json_format.ParseDict(
        {"name": "projects/sample1/locations/sample2/operations/sample3"}, request
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b"{}")
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.delete_operation(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        operations_pb2.DeleteOperationRequest,
        dict,
    ],
)
async def test_delete_operation_rest_asyncio(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    request_init = {"name": "projects/sample1/locations/sample2/operations/sample3"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = "{}"
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = await client.delete_operation(request)

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_get_operation_rest_asyncio_bad_request(
    request_type=operations_pb2.GetOperationRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )
    request = request_type()
    request = json_format.ParseDict(
        {"name": "projects/sample1/locations/sample2/operations/sample3"}, request
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b"{}")
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.get_operation(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        operations_pb2.GetOperationRequest,
        dict,
    ],
)
async def test_get_operation_rest_asyncio(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    request_init = {"name": "projects/sample1/locations/sample2/operations/sample3"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = await client.get_operation(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.Operation)


@pytest.mark.asyncio
async def test_list_operations_rest_asyncio_bad_request(
    request_type=operations_pb2.ListOperationsRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )
    request = request_type()
    request = json_format.ParseDict(
        {"name": "projects/sample1/locations/sample2"}, request
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b"{}")
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.list_operations(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        operations_pb2.ListOperationsRequest,
        dict,
    ],
)
async def test_list_operations_rest_asyncio(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    request_init = {"name": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.ListOperationsResponse()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = await client.list_operations(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.ListOperationsResponse)


@pytest.mark.asyncio
async def test_wait_operation_rest_asyncio_bad_request(
    request_type=operations_pb2.WaitOperationRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )
    request = request_type()
    request = json_format.ParseDict(
        {"name": "projects/sample1/locations/sample2/operations/sample3"}, request
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.read = mock.AsyncMock(return_value=b"{}")
        response_value.status_code = 400
        response_value.request = mock.Mock()
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        await client.wait_operation(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        operations_pb2.WaitOperationRequest,
        dict,
    ],
)
async def test_wait_operation_rest_asyncio(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    request_init = {"name": "projects/sample1/locations/sample2/operations/sample3"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(AsyncAuthorizedSession, "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation()

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )

        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        response = await client.wait_operation(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.Operation)


def test_initialize_client_w_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    assert client is not None


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_create_rag_corpus_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.create_rag_corpus), "__call__"
    ) as call:
        await client.create_rag_corpus(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.CreateRagCorpusRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_update_rag_corpus_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.update_rag_corpus), "__call__"
    ) as call:
        await client.update_rag_corpus(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.UpdateRagCorpusRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_rag_corpus_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.get_rag_corpus), "__call__") as call:
        await client.get_rag_corpus(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.GetRagCorpusRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_rag_corpora_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_corpora), "__call__") as call:
        await client.list_rag_corpora(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.ListRagCorporaRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_delete_rag_corpus_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_rag_corpus), "__call__"
    ) as call:
        await client.delete_rag_corpus(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.DeleteRagCorpusRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_upload_rag_file_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.upload_rag_file), "__call__") as call:
        await client.upload_rag_file(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.UploadRagFileRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_import_rag_files_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.import_rag_files), "__call__") as call:
        await client.import_rag_files(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.ImportRagFilesRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_rag_file_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.get_rag_file), "__call__") as call:
        await client.get_rag_file(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.GetRagFileRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_rag_files_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.list_rag_files), "__call__") as call:
        await client.list_rag_files(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.ListRagFilesRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_delete_rag_file_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.delete_rag_file), "__call__") as call:
        await client.delete_rag_file(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.DeleteRagFileRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_update_rag_engine_config_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.update_rag_engine_config), "__call__"
    ) as call:
        await client.update_rag_engine_config(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.UpdateRagEngineConfigRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_rag_engine_config_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.get_rag_engine_config), "__call__"
    ) as call:
        await client.get_rag_engine_config(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = vertex_rag_data_service.GetRagEngineConfigRequest()

        assert args[0] == request_msg


def test_vertex_rag_data_service_rest_asyncio_lro_client():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
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
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    options = client_options.ClientOptions(quota_project_id="octopus")
    with pytest.raises(core_exceptions.AsyncRestUnsupportedParameterError, match="google.api_core.client_options.ClientOptions.quota_project_id") as exc:  # type: ignore
        client = VertexRagDataServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport="rest_asyncio",
            client_options=options,
        )


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    assert isinstance(
        client.transport,
        transports.VertexRagDataServiceGrpcTransport,
    )


def test_vertex_rag_data_service_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(core_exceptions.DuplicateCredentialArgs):
        transport = transports.VertexRagDataServiceTransport(
            credentials=ga_credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_vertex_rag_data_service_base_transport():
    # Instantiate the base transport.
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.vertex_rag_data_service.transports.VertexRagDataServiceTransport.__init__"
    ) as Transport:
        Transport.return_value = None
        transport = transports.VertexRagDataServiceTransport(
            credentials=ga_credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "create_rag_corpus",
        "update_rag_corpus",
        "get_rag_corpus",
        "list_rag_corpora",
        "delete_rag_corpus",
        "upload_rag_file",
        "import_rag_files",
        "get_rag_file",
        "list_rag_files",
        "delete_rag_file",
        "update_rag_engine_config",
        "get_rag_engine_config",
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


def test_vertex_rag_data_service_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        google.auth, "load_credentials_from_file", autospec=True
    ) as load_creds, mock.patch(
        "google.cloud.aiplatform_v1beta1.services.vertex_rag_data_service.transports.VertexRagDataServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.VertexRagDataServiceTransport(
            credentials_file="credentials.json",
            quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=None,
            default_scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


def test_vertex_rag_data_service_base_transport_with_adc():
    # Test the default credentials are used if credentials and credentials_file are None.
    with mock.patch.object(google.auth, "default", autospec=True) as adc, mock.patch(
        "google.cloud.aiplatform_v1beta1.services.vertex_rag_data_service.transports.VertexRagDataServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.VertexRagDataServiceTransport()
        adc.assert_called_once()


def test_vertex_rag_data_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        VertexRagDataServiceClient()
        adc.assert_called_once_with(
            scopes=None,
            default_scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id=None,
        )


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.VertexRagDataServiceGrpcTransport,
        transports.VertexRagDataServiceGrpcAsyncIOTransport,
    ],
)
def test_vertex_rag_data_service_transport_auth_adc(transport_class):
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
        transports.VertexRagDataServiceGrpcTransport,
        transports.VertexRagDataServiceGrpcAsyncIOTransport,
        transports.VertexRagDataServiceRestTransport,
    ],
)
def test_vertex_rag_data_service_transport_auth_gdch_credentials(transport_class):
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
        (transports.VertexRagDataServiceGrpcTransport, grpc_helpers),
        (transports.VertexRagDataServiceGrpcAsyncIOTransport, grpc_helpers_async),
    ],
)
def test_vertex_rag_data_service_transport_create_channel(
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
        transports.VertexRagDataServiceGrpcTransport,
        transports.VertexRagDataServiceGrpcAsyncIOTransport,
    ],
)
def test_vertex_rag_data_service_grpc_transport_client_cert_source_for_mtls(
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


def test_vertex_rag_data_service_http_transport_client_cert_source_for_mtls():
    cred = ga_credentials.AnonymousCredentials()
    with mock.patch(
        "google.auth.transport.requests.AuthorizedSession.configure_mtls_channel"
    ) as mock_configure_mtls_channel:
        transports.VertexRagDataServiceRestTransport(
            credentials=cred, client_cert_source_for_mtls=client_cert_source_callback
        )
        mock_configure_mtls_channel.assert_called_once_with(client_cert_source_callback)


@pytest.mark.parametrize(
    "transport_name",
    [
        "grpc",
        "grpc_asyncio",
        "rest",
    ],
)
def test_vertex_rag_data_service_host_no_port(transport_name):
    client = VertexRagDataServiceClient(
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
def test_vertex_rag_data_service_host_with_port(transport_name):
    client = VertexRagDataServiceClient(
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
def test_vertex_rag_data_service_client_transport_session_collision(transport_name):
    creds1 = ga_credentials.AnonymousCredentials()
    creds2 = ga_credentials.AnonymousCredentials()
    client1 = VertexRagDataServiceClient(
        credentials=creds1,
        transport=transport_name,
    )
    client2 = VertexRagDataServiceClient(
        credentials=creds2,
        transport=transport_name,
    )
    session1 = client1.transport.create_rag_corpus._session
    session2 = client2.transport.create_rag_corpus._session
    assert session1 != session2
    session1 = client1.transport.update_rag_corpus._session
    session2 = client2.transport.update_rag_corpus._session
    assert session1 != session2
    session1 = client1.transport.get_rag_corpus._session
    session2 = client2.transport.get_rag_corpus._session
    assert session1 != session2
    session1 = client1.transport.list_rag_corpora._session
    session2 = client2.transport.list_rag_corpora._session
    assert session1 != session2
    session1 = client1.transport.delete_rag_corpus._session
    session2 = client2.transport.delete_rag_corpus._session
    assert session1 != session2
    session1 = client1.transport.upload_rag_file._session
    session2 = client2.transport.upload_rag_file._session
    assert session1 != session2
    session1 = client1.transport.import_rag_files._session
    session2 = client2.transport.import_rag_files._session
    assert session1 != session2
    session1 = client1.transport.get_rag_file._session
    session2 = client2.transport.get_rag_file._session
    assert session1 != session2
    session1 = client1.transport.list_rag_files._session
    session2 = client2.transport.list_rag_files._session
    assert session1 != session2
    session1 = client1.transport.delete_rag_file._session
    session2 = client2.transport.delete_rag_file._session
    assert session1 != session2
    session1 = client1.transport.update_rag_engine_config._session
    session2 = client2.transport.update_rag_engine_config._session
    assert session1 != session2
    session1 = client1.transport.get_rag_engine_config._session
    session2 = client2.transport.get_rag_engine_config._session
    assert session1 != session2


def test_vertex_rag_data_service_grpc_transport_channel():
    channel = grpc.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.VertexRagDataServiceGrpcTransport(
        host="squid.clam.whelk",
        channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


def test_vertex_rag_data_service_grpc_asyncio_transport_channel():
    channel = aio.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.VertexRagDataServiceGrpcAsyncIOTransport(
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
        transports.VertexRagDataServiceGrpcTransport,
        transports.VertexRagDataServiceGrpcAsyncIOTransport,
    ],
)
def test_vertex_rag_data_service_transport_channel_mtls_with_client_cert_source(
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
        transports.VertexRagDataServiceGrpcTransport,
        transports.VertexRagDataServiceGrpcAsyncIOTransport,
    ],
)
def test_vertex_rag_data_service_transport_channel_mtls_with_adc(transport_class):
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


def test_vertex_rag_data_service_grpc_lro_client():
    client = VertexRagDataServiceClient(
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


def test_vertex_rag_data_service_grpc_lro_async_client():
    client = VertexRagDataServiceAsyncClient(
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


def test_endpoint_path():
    project = "squid"
    location = "clam"
    endpoint = "whelk"
    expected = "projects/{project}/locations/{location}/endpoints/{endpoint}".format(
        project=project,
        location=location,
        endpoint=endpoint,
    )
    actual = VertexRagDataServiceClient.endpoint_path(project, location, endpoint)
    assert expected == actual


def test_parse_endpoint_path():
    expected = {
        "project": "octopus",
        "location": "oyster",
        "endpoint": "nudibranch",
    }
    path = VertexRagDataServiceClient.endpoint_path(**expected)

    # Check that the path construction is reversible.
    actual = VertexRagDataServiceClient.parse_endpoint_path(path)
    assert expected == actual


def test_model_path():
    project = "cuttlefish"
    location = "mussel"
    model = "winkle"
    expected = "projects/{project}/locations/{location}/models/{model}".format(
        project=project,
        location=location,
        model=model,
    )
    actual = VertexRagDataServiceClient.model_path(project, location, model)
    assert expected == actual


def test_parse_model_path():
    expected = {
        "project": "nautilus",
        "location": "scallop",
        "model": "abalone",
    }
    path = VertexRagDataServiceClient.model_path(**expected)

    # Check that the path construction is reversible.
    actual = VertexRagDataServiceClient.parse_model_path(path)
    assert expected == actual


def test_rag_corpus_path():
    project = "squid"
    location = "clam"
    rag_corpus = "whelk"
    expected = "projects/{project}/locations/{location}/ragCorpora/{rag_corpus}".format(
        project=project,
        location=location,
        rag_corpus=rag_corpus,
    )
    actual = VertexRagDataServiceClient.rag_corpus_path(project, location, rag_corpus)
    assert expected == actual


def test_parse_rag_corpus_path():
    expected = {
        "project": "octopus",
        "location": "oyster",
        "rag_corpus": "nudibranch",
    }
    path = VertexRagDataServiceClient.rag_corpus_path(**expected)

    # Check that the path construction is reversible.
    actual = VertexRagDataServiceClient.parse_rag_corpus_path(path)
    assert expected == actual


def test_rag_engine_config_path():
    project = "cuttlefish"
    location = "mussel"
    expected = "projects/{project}/locations/{location}/ragEngineConfig".format(
        project=project,
        location=location,
    )
    actual = VertexRagDataServiceClient.rag_engine_config_path(project, location)
    assert expected == actual


def test_parse_rag_engine_config_path():
    expected = {
        "project": "winkle",
        "location": "nautilus",
    }
    path = VertexRagDataServiceClient.rag_engine_config_path(**expected)

    # Check that the path construction is reversible.
    actual = VertexRagDataServiceClient.parse_rag_engine_config_path(path)
    assert expected == actual


def test_rag_file_path():
    project = "scallop"
    location = "abalone"
    rag_corpus = "squid"
    rag_file = "clam"
    expected = "projects/{project}/locations/{location}/ragCorpora/{rag_corpus}/ragFiles/{rag_file}".format(
        project=project,
        location=location,
        rag_corpus=rag_corpus,
        rag_file=rag_file,
    )
    actual = VertexRagDataServiceClient.rag_file_path(
        project, location, rag_corpus, rag_file
    )
    assert expected == actual


def test_parse_rag_file_path():
    expected = {
        "project": "whelk",
        "location": "octopus",
        "rag_corpus": "oyster",
        "rag_file": "nudibranch",
    }
    path = VertexRagDataServiceClient.rag_file_path(**expected)

    # Check that the path construction is reversible.
    actual = VertexRagDataServiceClient.parse_rag_file_path(path)
    assert expected == actual


def test_secret_version_path():
    project = "cuttlefish"
    secret = "mussel"
    secret_version = "winkle"
    expected = "projects/{project}/secrets/{secret}/versions/{secret_version}".format(
        project=project,
        secret=secret,
        secret_version=secret_version,
    )
    actual = VertexRagDataServiceClient.secret_version_path(
        project, secret, secret_version
    )
    assert expected == actual


def test_parse_secret_version_path():
    expected = {
        "project": "nautilus",
        "secret": "scallop",
        "secret_version": "abalone",
    }
    path = VertexRagDataServiceClient.secret_version_path(**expected)

    # Check that the path construction is reversible.
    actual = VertexRagDataServiceClient.parse_secret_version_path(path)
    assert expected == actual


def test_common_billing_account_path():
    billing_account = "squid"
    expected = "billingAccounts/{billing_account}".format(
        billing_account=billing_account,
    )
    actual = VertexRagDataServiceClient.common_billing_account_path(billing_account)
    assert expected == actual


def test_parse_common_billing_account_path():
    expected = {
        "billing_account": "clam",
    }
    path = VertexRagDataServiceClient.common_billing_account_path(**expected)

    # Check that the path construction is reversible.
    actual = VertexRagDataServiceClient.parse_common_billing_account_path(path)
    assert expected == actual


def test_common_folder_path():
    folder = "whelk"
    expected = "folders/{folder}".format(
        folder=folder,
    )
    actual = VertexRagDataServiceClient.common_folder_path(folder)
    assert expected == actual


def test_parse_common_folder_path():
    expected = {
        "folder": "octopus",
    }
    path = VertexRagDataServiceClient.common_folder_path(**expected)

    # Check that the path construction is reversible.
    actual = VertexRagDataServiceClient.parse_common_folder_path(path)
    assert expected == actual


def test_common_organization_path():
    organization = "oyster"
    expected = "organizations/{organization}".format(
        organization=organization,
    )
    actual = VertexRagDataServiceClient.common_organization_path(organization)
    assert expected == actual


def test_parse_common_organization_path():
    expected = {
        "organization": "nudibranch",
    }
    path = VertexRagDataServiceClient.common_organization_path(**expected)

    # Check that the path construction is reversible.
    actual = VertexRagDataServiceClient.parse_common_organization_path(path)
    assert expected == actual


def test_common_project_path():
    project = "cuttlefish"
    expected = "projects/{project}".format(
        project=project,
    )
    actual = VertexRagDataServiceClient.common_project_path(project)
    assert expected == actual


def test_parse_common_project_path():
    expected = {
        "project": "mussel",
    }
    path = VertexRagDataServiceClient.common_project_path(**expected)

    # Check that the path construction is reversible.
    actual = VertexRagDataServiceClient.parse_common_project_path(path)
    assert expected == actual


def test_common_location_path():
    project = "winkle"
    location = "nautilus"
    expected = "projects/{project}/locations/{location}".format(
        project=project,
        location=location,
    )
    actual = VertexRagDataServiceClient.common_location_path(project, location)
    assert expected == actual


def test_parse_common_location_path():
    expected = {
        "project": "scallop",
        "location": "abalone",
    }
    path = VertexRagDataServiceClient.common_location_path(**expected)

    # Check that the path construction is reversible.
    actual = VertexRagDataServiceClient.parse_common_location_path(path)
    assert expected == actual


def test_client_with_default_client_info():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(
        transports.VertexRagDataServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        client = VertexRagDataServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(
        transports.VertexRagDataServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        transport_class = VertexRagDataServiceClient.get_transport_class()
        transport = transport_class(
            credentials=ga_credentials.AnonymousCredentials(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)


def test_delete_operation(transport: str = "grpc"):
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
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
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


def test_wait_operation_from_dict():
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
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


def test_get_operation(transport: str = "grpc"):
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
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
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


def test_get_operation_from_dict():
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
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


def test_list_operations(transport: str = "grpc"):
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
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
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


def test_list_operations_from_dict():
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
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


def test_list_locations(transport: str = "grpc"):
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
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
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


def test_list_locations_from_dict():
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
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


def test_get_location(transport: str = "grpc"):
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials()
    )

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
    client = VertexRagDataServiceAsyncClient(credentials=async_anonymous_credentials())

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
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
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


def test_set_iam_policy(transport: str = "grpc"):
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
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
    assert (
        "x-goog-request-params",
        "resource=resource/value",
    ) in kw["metadata"]


def test_set_iam_policy_from_dict():
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(),
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
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
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
    assert (
        "x-goog-request-params",
        "resource=resource/value",
    ) in kw["metadata"]


def test_test_iam_permissions_from_dict():
    client = VertexRagDataServiceClient(
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
    client = VertexRagDataServiceAsyncClient(
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


def test_transport_close_grpc():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc"
    )
    with mock.patch.object(
        type(getattr(client.transport, "_grpc_channel")), "close"
    ) as close:
        with client:
            close.assert_not_called()
        close.assert_called_once()


@pytest.mark.asyncio
async def test_transport_close_grpc_asyncio():
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="grpc_asyncio"
    )
    with mock.patch.object(
        type(getattr(client.transport, "_grpc_channel")), "close"
    ) as close:
        async with client:
            close.assert_not_called()
        close.assert_called_once()


def test_transport_close_rest():
    client = VertexRagDataServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    with mock.patch.object(
        type(getattr(client.transport, "_session")), "close"
    ) as close:
        with client:
            close.assert_not_called()
        close.assert_called_once()


@pytest.mark.asyncio
async def test_transport_close_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = VertexRagDataServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    with mock.patch.object(
        type(getattr(client.transport, "_session")), "close"
    ) as close:
        async with client:
            close.assert_not_called()
        close.assert_called_once()


def test_client_ctx():
    transports = [
        "rest",
        "grpc",
    ]
    for transport in transports:
        client = VertexRagDataServiceClient(
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
        (VertexRagDataServiceClient, transports.VertexRagDataServiceGrpcTransport),
        (
            VertexRagDataServiceAsyncClient,
            transports.VertexRagDataServiceGrpcAsyncIOTransport,
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
