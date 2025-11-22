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
from google.cloud.aiplatform_v1beta1.services.dataset_service import (
    DatasetServiceAsyncClient,
)
from google.cloud.aiplatform_v1beta1.services.dataset_service import (
    DatasetServiceClient,
)
from google.cloud.aiplatform_v1beta1.services.dataset_service import pagers
from google.cloud.aiplatform_v1beta1.services.dataset_service import transports
from google.cloud.aiplatform_v1beta1.types import annotation
from google.cloud.aiplatform_v1beta1.types import annotation_spec
from google.cloud.aiplatform_v1beta1.types import content
from google.cloud.aiplatform_v1beta1.types import data_item
from google.cloud.aiplatform_v1beta1.types import dataset
from google.cloud.aiplatform_v1beta1.types import dataset as gca_dataset
from google.cloud.aiplatform_v1beta1.types import dataset_service
from google.cloud.aiplatform_v1beta1.types import dataset_version
from google.cloud.aiplatform_v1beta1.types import dataset_version as gca_dataset_version
from google.cloud.aiplatform_v1beta1.types import encryption_spec
from google.cloud.aiplatform_v1beta1.types import io
from google.cloud.aiplatform_v1beta1.types import openapi
from google.cloud.aiplatform_v1beta1.types import operation as gca_operation
from google.cloud.aiplatform_v1beta1.types import saved_query
from google.cloud.aiplatform_v1beta1.types import tool
from google.cloud.location import locations_pb2
from google.iam.v1 import iam_policy_pb2  # type: ignore
from google.iam.v1 import options_pb2  # type: ignore
from google.iam.v1 import policy_pb2  # type: ignore
from google.longrunning import operations_pb2  # type: ignore
from google.oauth2 import service_account
from google.protobuf import duration_pb2  # type: ignore
from google.protobuf import empty_pb2  # type: ignore
from google.protobuf import field_mask_pb2  # type: ignore
from google.protobuf import struct_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
from google.type import latlng_pb2  # type: ignore
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

    assert DatasetServiceClient._get_default_mtls_endpoint(None) is None
    assert (
        DatasetServiceClient._get_default_mtls_endpoint(api_endpoint)
        == api_mtls_endpoint
    )
    assert (
        DatasetServiceClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        DatasetServiceClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        DatasetServiceClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        DatasetServiceClient._get_default_mtls_endpoint(non_googleapi) == non_googleapi
    )


def test__read_environment_variables():
    assert DatasetServiceClient._read_environment_variables() == (False, "auto", None)

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        assert DatasetServiceClient._read_environment_variables() == (
            True,
            "auto",
            None,
        )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "false"}):
        assert DatasetServiceClient._read_environment_variables() == (
            False,
            "auto",
            None,
        )

    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}
    ):
        with pytest.raises(ValueError) as excinfo:
            DatasetServiceClient._read_environment_variables()
    assert (
        str(excinfo.value)
        == "Environment variable `GOOGLE_API_USE_CLIENT_CERTIFICATE` must be either `true` or `false`"
    )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        assert DatasetServiceClient._read_environment_variables() == (
            False,
            "never",
            None,
        )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        assert DatasetServiceClient._read_environment_variables() == (
            False,
            "always",
            None,
        )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"}):
        assert DatasetServiceClient._read_environment_variables() == (
            False,
            "auto",
            None,
        )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError) as excinfo:
            DatasetServiceClient._read_environment_variables()
    assert (
        str(excinfo.value)
        == "Environment variable `GOOGLE_API_USE_MTLS_ENDPOINT` must be `never`, `auto` or `always`"
    )

    with mock.patch.dict(os.environ, {"GOOGLE_CLOUD_UNIVERSE_DOMAIN": "foo.com"}):
        assert DatasetServiceClient._read_environment_variables() == (
            False,
            "auto",
            "foo.com",
        )


def test__get_client_cert_source():
    mock_provided_cert_source = mock.Mock()
    mock_default_cert_source = mock.Mock()

    assert DatasetServiceClient._get_client_cert_source(None, False) is None
    assert (
        DatasetServiceClient._get_client_cert_source(mock_provided_cert_source, False)
        is None
    )
    assert (
        DatasetServiceClient._get_client_cert_source(mock_provided_cert_source, True)
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
                DatasetServiceClient._get_client_cert_source(None, True)
                is mock_default_cert_source
            )
            assert (
                DatasetServiceClient._get_client_cert_source(
                    mock_provided_cert_source, "true"
                )
                is mock_provided_cert_source
            )


@mock.patch.object(
    DatasetServiceClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(DatasetServiceClient),
)
@mock.patch.object(
    DatasetServiceAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(DatasetServiceAsyncClient),
)
def test__get_api_endpoint():
    api_override = "foo.com"
    mock_client_cert_source = mock.Mock()
    default_universe = DatasetServiceClient._DEFAULT_UNIVERSE
    default_endpoint = DatasetServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(
        UNIVERSE_DOMAIN=default_universe
    )
    mock_universe = "bar.com"
    mock_endpoint = DatasetServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(
        UNIVERSE_DOMAIN=mock_universe
    )

    assert (
        DatasetServiceClient._get_api_endpoint(
            api_override, mock_client_cert_source, default_universe, "always"
        )
        == api_override
    )
    assert (
        DatasetServiceClient._get_api_endpoint(
            None, mock_client_cert_source, default_universe, "auto"
        )
        == DatasetServiceClient.DEFAULT_MTLS_ENDPOINT
    )
    assert (
        DatasetServiceClient._get_api_endpoint(None, None, default_universe, "auto")
        == default_endpoint
    )
    assert (
        DatasetServiceClient._get_api_endpoint(None, None, default_universe, "always")
        == DatasetServiceClient.DEFAULT_MTLS_ENDPOINT
    )
    assert (
        DatasetServiceClient._get_api_endpoint(
            None, mock_client_cert_source, default_universe, "always"
        )
        == DatasetServiceClient.DEFAULT_MTLS_ENDPOINT
    )
    assert (
        DatasetServiceClient._get_api_endpoint(None, None, mock_universe, "never")
        == mock_endpoint
    )
    assert (
        DatasetServiceClient._get_api_endpoint(None, None, default_universe, "never")
        == default_endpoint
    )

    with pytest.raises(MutualTLSChannelError) as excinfo:
        DatasetServiceClient._get_api_endpoint(
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
        DatasetServiceClient._get_universe_domain(
            client_universe_domain, universe_domain_env
        )
        == client_universe_domain
    )
    assert (
        DatasetServiceClient._get_universe_domain(None, universe_domain_env)
        == universe_domain_env
    )
    assert (
        DatasetServiceClient._get_universe_domain(None, None)
        == DatasetServiceClient._DEFAULT_UNIVERSE
    )

    with pytest.raises(ValueError) as excinfo:
        DatasetServiceClient._get_universe_domain("", None)
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
    client = DatasetServiceClient(credentials=cred)
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
    client = DatasetServiceClient(credentials=cred)
    client._transport._credentials = cred

    error = core_exceptions.GoogleAPICallError("message", details=[])
    error.code = error_code

    client._add_cred_info_for_auth_errors(error)
    assert error.details == []


@pytest.mark.parametrize(
    "client_class,transport_name",
    [
        (DatasetServiceClient, "grpc"),
        (DatasetServiceAsyncClient, "grpc_asyncio"),
        (DatasetServiceClient, "rest"),
    ],
)
def test_dataset_service_client_from_service_account_info(client_class, transport_name):
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
        (transports.DatasetServiceGrpcTransport, "grpc"),
        (transports.DatasetServiceGrpcAsyncIOTransport, "grpc_asyncio"),
        (transports.DatasetServiceRestTransport, "rest"),
    ],
)
def test_dataset_service_client_service_account_always_use_jwt(
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
        (DatasetServiceClient, "grpc"),
        (DatasetServiceAsyncClient, "grpc_asyncio"),
        (DatasetServiceClient, "rest"),
    ],
)
def test_dataset_service_client_from_service_account_file(client_class, transport_name):
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


def test_dataset_service_client_get_transport_class():
    transport = DatasetServiceClient.get_transport_class()
    available_transports = [
        transports.DatasetServiceGrpcTransport,
        transports.DatasetServiceRestTransport,
    ]
    assert transport in available_transports

    transport = DatasetServiceClient.get_transport_class("grpc")
    assert transport == transports.DatasetServiceGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (DatasetServiceClient, transports.DatasetServiceGrpcTransport, "grpc"),
        (
            DatasetServiceAsyncClient,
            transports.DatasetServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
        (DatasetServiceClient, transports.DatasetServiceRestTransport, "rest"),
    ],
)
@mock.patch.object(
    DatasetServiceClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(DatasetServiceClient),
)
@mock.patch.object(
    DatasetServiceAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(DatasetServiceAsyncClient),
)
def test_dataset_service_client_client_options(
    client_class, transport_class, transport_name
):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(DatasetServiceClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=ga_credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(DatasetServiceClient, "get_transport_class") as gtc:
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
        (DatasetServiceClient, transports.DatasetServiceGrpcTransport, "grpc", "true"),
        (
            DatasetServiceAsyncClient,
            transports.DatasetServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "true",
        ),
        (DatasetServiceClient, transports.DatasetServiceGrpcTransport, "grpc", "false"),
        (
            DatasetServiceAsyncClient,
            transports.DatasetServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "false",
        ),
        (DatasetServiceClient, transports.DatasetServiceRestTransport, "rest", "true"),
        (DatasetServiceClient, transports.DatasetServiceRestTransport, "rest", "false"),
    ],
)
@mock.patch.object(
    DatasetServiceClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(DatasetServiceClient),
)
@mock.patch.object(
    DatasetServiceAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(DatasetServiceAsyncClient),
)
@mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"})
def test_dataset_service_client_mtls_env_auto(
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
    "client_class", [DatasetServiceClient, DatasetServiceAsyncClient]
)
@mock.patch.object(
    DatasetServiceClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(DatasetServiceClient),
)
@mock.patch.object(
    DatasetServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(DatasetServiceAsyncClient),
)
def test_dataset_service_client_get_mtls_endpoint_and_cert_source(client_class):
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
    "client_class", [DatasetServiceClient, DatasetServiceAsyncClient]
)
@mock.patch.object(
    DatasetServiceClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(DatasetServiceClient),
)
@mock.patch.object(
    DatasetServiceAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(DatasetServiceAsyncClient),
)
def test_dataset_service_client_client_api_endpoint(client_class):
    mock_client_cert_source = client_cert_source_callback
    api_override = "foo.com"
    default_universe = DatasetServiceClient._DEFAULT_UNIVERSE
    default_endpoint = DatasetServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(
        UNIVERSE_DOMAIN=default_universe
    )
    mock_universe = "bar.com"
    mock_endpoint = DatasetServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(
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
        (DatasetServiceClient, transports.DatasetServiceGrpcTransport, "grpc"),
        (
            DatasetServiceAsyncClient,
            transports.DatasetServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
        (DatasetServiceClient, transports.DatasetServiceRestTransport, "rest"),
    ],
)
def test_dataset_service_client_client_options_scopes(
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
            DatasetServiceClient,
            transports.DatasetServiceGrpcTransport,
            "grpc",
            grpc_helpers,
        ),
        (
            DatasetServiceAsyncClient,
            transports.DatasetServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            grpc_helpers_async,
        ),
        (DatasetServiceClient, transports.DatasetServiceRestTransport, "rest", None),
    ],
)
def test_dataset_service_client_client_options_credentials_file(
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


def test_dataset_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.dataset_service.transports.DatasetServiceGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = DatasetServiceClient(
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
            DatasetServiceClient,
            transports.DatasetServiceGrpcTransport,
            "grpc",
            grpc_helpers,
        ),
        (
            DatasetServiceAsyncClient,
            transports.DatasetServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            grpc_helpers_async,
        ),
    ],
)
def test_dataset_service_client_create_channel_credentials_file(
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
        dataset_service.CreateDatasetRequest,
        dict,
    ],
)
def test_create_dataset(request_type, transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.create_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = dataset_service.CreateDatasetRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_create_dataset_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = dataset_service.CreateDatasetRequest(
        parent="parent_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_dataset), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.create_dataset(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == dataset_service.CreateDatasetRequest(
            parent="parent_value",
        )


def test_create_dataset_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.create_dataset in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.create_dataset] = mock_rpc
        request = {}
        client.create_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.create_dataset(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_create_dataset_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = DatasetServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.create_dataset
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.create_dataset
        ] = mock_rpc

        request = {}
        await client.create_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.create_dataset(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_create_dataset_async(
    transport: str = "grpc_asyncio", request_type=dataset_service.CreateDatasetRequest
):
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.create_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = dataset_service.CreateDatasetRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_create_dataset_async_from_dict():
    await test_create_dataset_async(request_type=dict)


def test_create_dataset_field_headers():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.CreateDatasetRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_dataset), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.create_dataset(request)

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
async def test_create_dataset_field_headers_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.CreateDatasetRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_dataset), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.create_dataset(request)

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


def test_create_dataset_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_dataset(
            parent="parent_value",
            dataset=gca_dataset.Dataset(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].dataset
        mock_val = gca_dataset.Dataset(name="name_value")
        assert arg == mock_val


def test_create_dataset_flattened_error():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_dataset(
            dataset_service.CreateDatasetRequest(),
            parent="parent_value",
            dataset=gca_dataset.Dataset(name="name_value"),
        )


@pytest.mark.asyncio
async def test_create_dataset_flattened_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.create_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_dataset(
            parent="parent_value",
            dataset=gca_dataset.Dataset(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].dataset
        mock_val = gca_dataset.Dataset(name="name_value")
        assert arg == mock_val


@pytest.mark.asyncio
async def test_create_dataset_flattened_error_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_dataset(
            dataset_service.CreateDatasetRequest(),
            parent="parent_value",
            dataset=gca_dataset.Dataset(name="name_value"),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.GetDatasetRequest,
        dict,
    ],
)
def test_get_dataset(request_type, transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset.Dataset(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            metadata_schema_uri="metadata_schema_uri_value",
            data_item_count=1584,
            etag="etag_value",
            metadata_artifact="metadata_artifact_value",
            model_reference="model_reference_value",
            satisfies_pzs=True,
            satisfies_pzi=True,
        )
        response = client.get_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = dataset_service.GetDatasetRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, dataset.Dataset)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.metadata_schema_uri == "metadata_schema_uri_value"
    assert response.data_item_count == 1584
    assert response.etag == "etag_value"
    assert response.metadata_artifact == "metadata_artifact_value"
    assert response.model_reference == "model_reference_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


def test_get_dataset_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = dataset_service.GetDatasetRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_dataset), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.get_dataset(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == dataset_service.GetDatasetRequest(
            name="name_value",
        )


def test_get_dataset_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.get_dataset in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.get_dataset] = mock_rpc
        request = {}
        client.get_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_dataset(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_get_dataset_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = DatasetServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.get_dataset
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.get_dataset
        ] = mock_rpc

        request = {}
        await client.get_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.get_dataset(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_get_dataset_async(
    transport: str = "grpc_asyncio", request_type=dataset_service.GetDatasetRequest
):
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset.Dataset(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
                metadata_schema_uri="metadata_schema_uri_value",
                data_item_count=1584,
                etag="etag_value",
                metadata_artifact="metadata_artifact_value",
                model_reference="model_reference_value",
                satisfies_pzs=True,
                satisfies_pzi=True,
            )
        )
        response = await client.get_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = dataset_service.GetDatasetRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, dataset.Dataset)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.metadata_schema_uri == "metadata_schema_uri_value"
    assert response.data_item_count == 1584
    assert response.etag == "etag_value"
    assert response.metadata_artifact == "metadata_artifact_value"
    assert response.model_reference == "model_reference_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


@pytest.mark.asyncio
async def test_get_dataset_async_from_dict():
    await test_get_dataset_async(request_type=dict)


def test_get_dataset_field_headers():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.GetDatasetRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_dataset), "__call__") as call:
        call.return_value = dataset.Dataset()
        client.get_dataset(request)

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
async def test_get_dataset_field_headers_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.GetDatasetRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_dataset), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(dataset.Dataset())
        await client.get_dataset(request)

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


def test_get_dataset_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset.Dataset()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_dataset(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_get_dataset_flattened_error():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_dataset(
            dataset_service.GetDatasetRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_get_dataset_flattened_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset.Dataset()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(dataset.Dataset())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_dataset(
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
async def test_get_dataset_flattened_error_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_dataset(
            dataset_service.GetDatasetRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.UpdateDatasetRequest,
        dict,
    ],
)
def test_update_dataset(request_type, transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_dataset.Dataset(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            metadata_schema_uri="metadata_schema_uri_value",
            data_item_count=1584,
            etag="etag_value",
            metadata_artifact="metadata_artifact_value",
            model_reference="model_reference_value",
            satisfies_pzs=True,
            satisfies_pzi=True,
        )
        response = client.update_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = dataset_service.UpdateDatasetRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_dataset.Dataset)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.metadata_schema_uri == "metadata_schema_uri_value"
    assert response.data_item_count == 1584
    assert response.etag == "etag_value"
    assert response.metadata_artifact == "metadata_artifact_value"
    assert response.model_reference == "model_reference_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


def test_update_dataset_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = dataset_service.UpdateDatasetRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_dataset), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.update_dataset(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == dataset_service.UpdateDatasetRequest()


def test_update_dataset_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.update_dataset in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.update_dataset] = mock_rpc
        request = {}
        client.update_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.update_dataset(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_update_dataset_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = DatasetServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.update_dataset
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.update_dataset
        ] = mock_rpc

        request = {}
        await client.update_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.update_dataset(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_update_dataset_async(
    transport: str = "grpc_asyncio", request_type=dataset_service.UpdateDatasetRequest
):
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_dataset.Dataset(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
                metadata_schema_uri="metadata_schema_uri_value",
                data_item_count=1584,
                etag="etag_value",
                metadata_artifact="metadata_artifact_value",
                model_reference="model_reference_value",
                satisfies_pzs=True,
                satisfies_pzi=True,
            )
        )
        response = await client.update_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = dataset_service.UpdateDatasetRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_dataset.Dataset)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.metadata_schema_uri == "metadata_schema_uri_value"
    assert response.data_item_count == 1584
    assert response.etag == "etag_value"
    assert response.metadata_artifact == "metadata_artifact_value"
    assert response.model_reference == "model_reference_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


@pytest.mark.asyncio
async def test_update_dataset_async_from_dict():
    await test_update_dataset_async(request_type=dict)


def test_update_dataset_field_headers():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.UpdateDatasetRequest()

    request.dataset.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_dataset), "__call__") as call:
        call.return_value = gca_dataset.Dataset()
        client.update_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "dataset.name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_dataset_field_headers_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.UpdateDatasetRequest()

    request.dataset.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_dataset), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gca_dataset.Dataset())
        await client.update_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "dataset.name=name_value",
    ) in kw["metadata"]


def test_update_dataset_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_dataset.Dataset()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_dataset(
            dataset=gca_dataset.Dataset(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].dataset
        mock_val = gca_dataset.Dataset(name="name_value")
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=["paths_value"])
        assert arg == mock_val


def test_update_dataset_flattened_error():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_dataset(
            dataset_service.UpdateDatasetRequest(),
            dataset=gca_dataset.Dataset(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_dataset_flattened_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.update_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_dataset.Dataset()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gca_dataset.Dataset())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_dataset(
            dataset=gca_dataset.Dataset(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].dataset
        mock_val = gca_dataset.Dataset(name="name_value")
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=["paths_value"])
        assert arg == mock_val


@pytest.mark.asyncio
async def test_update_dataset_flattened_error_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_dataset(
            dataset_service.UpdateDatasetRequest(),
            dataset=gca_dataset.Dataset(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.ListDatasetsRequest,
        dict,
    ],
)
def test_list_datasets(request_type, transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_datasets), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_service.ListDatasetsResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_datasets(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = dataset_service.ListDatasetsRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDatasetsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_datasets_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = dataset_service.ListDatasetsRequest(
        parent="parent_value",
        filter="filter_value",
        page_token="page_token_value",
        order_by="order_by_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_datasets), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.list_datasets(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == dataset_service.ListDatasetsRequest(
            parent="parent_value",
            filter="filter_value",
            page_token="page_token_value",
            order_by="order_by_value",
        )


def test_list_datasets_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.list_datasets in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.list_datasets] = mock_rpc
        request = {}
        client.list_datasets(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_datasets(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_list_datasets_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = DatasetServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.list_datasets
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.list_datasets
        ] = mock_rpc

        request = {}
        await client.list_datasets(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.list_datasets(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_list_datasets_async(
    transport: str = "grpc_asyncio", request_type=dataset_service.ListDatasetsRequest
):
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_datasets), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.ListDatasetsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_datasets(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = dataset_service.ListDatasetsRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDatasetsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_datasets_async_from_dict():
    await test_list_datasets_async(request_type=dict)


def test_list_datasets_field_headers():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.ListDatasetsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_datasets), "__call__") as call:
        call.return_value = dataset_service.ListDatasetsResponse()
        client.list_datasets(request)

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
async def test_list_datasets_field_headers_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.ListDatasetsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_datasets), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.ListDatasetsResponse()
        )
        await client.list_datasets(request)

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


def test_list_datasets_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_datasets), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_service.ListDatasetsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_datasets(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_list_datasets_flattened_error():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_datasets(
            dataset_service.ListDatasetsRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_datasets_flattened_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_datasets), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_service.ListDatasetsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.ListDatasetsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_datasets(
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
async def test_list_datasets_flattened_error_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_datasets(
            dataset_service.ListDatasetsRequest(),
            parent="parent_value",
        )


def test_list_datasets_pager(transport_name: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_datasets), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListDatasetsResponse(
                datasets=[
                    dataset.Dataset(),
                    dataset.Dataset(),
                    dataset.Dataset(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListDatasetsResponse(
                datasets=[],
                next_page_token="def",
            ),
            dataset_service.ListDatasetsResponse(
                datasets=[
                    dataset.Dataset(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListDatasetsResponse(
                datasets=[
                    dataset.Dataset(),
                    dataset.Dataset(),
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
        pager = client.list_datasets(request={}, retry=retry, timeout=timeout)

        assert pager._metadata == expected_metadata
        assert pager._retry == retry
        assert pager._timeout == timeout

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, dataset.Dataset) for i in results)


def test_list_datasets_pages(transport_name: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_datasets), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListDatasetsResponse(
                datasets=[
                    dataset.Dataset(),
                    dataset.Dataset(),
                    dataset.Dataset(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListDatasetsResponse(
                datasets=[],
                next_page_token="def",
            ),
            dataset_service.ListDatasetsResponse(
                datasets=[
                    dataset.Dataset(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListDatasetsResponse(
                datasets=[
                    dataset.Dataset(),
                    dataset.Dataset(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_datasets(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_datasets_async_pager():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_datasets), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListDatasetsResponse(
                datasets=[
                    dataset.Dataset(),
                    dataset.Dataset(),
                    dataset.Dataset(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListDatasetsResponse(
                datasets=[],
                next_page_token="def",
            ),
            dataset_service.ListDatasetsResponse(
                datasets=[
                    dataset.Dataset(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListDatasetsResponse(
                datasets=[
                    dataset.Dataset(),
                    dataset.Dataset(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_datasets(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, dataset.Dataset) for i in responses)


@pytest.mark.asyncio
async def test_list_datasets_async_pages():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_datasets), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListDatasetsResponse(
                datasets=[
                    dataset.Dataset(),
                    dataset.Dataset(),
                    dataset.Dataset(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListDatasetsResponse(
                datasets=[],
                next_page_token="def",
            ),
            dataset_service.ListDatasetsResponse(
                datasets=[
                    dataset.Dataset(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListDatasetsResponse(
                datasets=[
                    dataset.Dataset(),
                    dataset.Dataset(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.list_datasets(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.DeleteDatasetRequest,
        dict,
    ],
)
def test_delete_dataset(request_type, transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = dataset_service.DeleteDatasetRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_dataset_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = dataset_service.DeleteDatasetRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_dataset), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.delete_dataset(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == dataset_service.DeleteDatasetRequest(
            name="name_value",
        )


def test_delete_dataset_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.delete_dataset in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.delete_dataset] = mock_rpc
        request = {}
        client.delete_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.delete_dataset(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_delete_dataset_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = DatasetServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.delete_dataset
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.delete_dataset
        ] = mock_rpc

        request = {}
        await client.delete_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.delete_dataset(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_delete_dataset_async(
    transport: str = "grpc_asyncio", request_type=dataset_service.DeleteDatasetRequest
):
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = dataset_service.DeleteDatasetRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_dataset_async_from_dict():
    await test_delete_dataset_async(request_type=dict)


def test_delete_dataset_field_headers():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.DeleteDatasetRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_dataset), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_dataset(request)

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
async def test_delete_dataset_field_headers_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.DeleteDatasetRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_dataset), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_dataset(request)

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


def test_delete_dataset_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_dataset(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_delete_dataset_flattened_error():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_dataset(
            dataset_service.DeleteDatasetRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_dataset_flattened_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_dataset(
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
async def test_delete_dataset_flattened_error_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_dataset(
            dataset_service.DeleteDatasetRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.ImportDataRequest,
        dict,
    ],
)
def test_import_data(request_type, transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.import_data), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.import_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = dataset_service.ImportDataRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_import_data_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = dataset_service.ImportDataRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.import_data), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.import_data(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == dataset_service.ImportDataRequest(
            name="name_value",
        )


def test_import_data_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.import_data in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.import_data] = mock_rpc
        request = {}
        client.import_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.import_data(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_import_data_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = DatasetServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.import_data
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.import_data
        ] = mock_rpc

        request = {}
        await client.import_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.import_data(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_import_data_async(
    transport: str = "grpc_asyncio", request_type=dataset_service.ImportDataRequest
):
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.import_data), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.import_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = dataset_service.ImportDataRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_import_data_async_from_dict():
    await test_import_data_async(request_type=dict)


def test_import_data_field_headers():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.ImportDataRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.import_data), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.import_data(request)

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
async def test_import_data_field_headers_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.ImportDataRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.import_data), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.import_data(request)

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


def test_import_data_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.import_data), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.import_data(
            name="name_value",
            import_configs=[
                dataset.ImportDataConfig(gcs_source=io.GcsSource(uris=["uris_value"]))
            ],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val
        arg = args[0].import_configs
        mock_val = [
            dataset.ImportDataConfig(gcs_source=io.GcsSource(uris=["uris_value"]))
        ]
        assert arg == mock_val


def test_import_data_flattened_error():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.import_data(
            dataset_service.ImportDataRequest(),
            name="name_value",
            import_configs=[
                dataset.ImportDataConfig(gcs_source=io.GcsSource(uris=["uris_value"]))
            ],
        )


@pytest.mark.asyncio
async def test_import_data_flattened_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.import_data), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.import_data(
            name="name_value",
            import_configs=[
                dataset.ImportDataConfig(gcs_source=io.GcsSource(uris=["uris_value"]))
            ],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val
        arg = args[0].import_configs
        mock_val = [
            dataset.ImportDataConfig(gcs_source=io.GcsSource(uris=["uris_value"]))
        ]
        assert arg == mock_val


@pytest.mark.asyncio
async def test_import_data_flattened_error_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.import_data(
            dataset_service.ImportDataRequest(),
            name="name_value",
            import_configs=[
                dataset.ImportDataConfig(gcs_source=io.GcsSource(uris=["uris_value"]))
            ],
        )


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.ExportDataRequest,
        dict,
    ],
)
def test_export_data(request_type, transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.export_data), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.export_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = dataset_service.ExportDataRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_export_data_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = dataset_service.ExportDataRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.export_data), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.export_data(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == dataset_service.ExportDataRequest(
            name="name_value",
        )


def test_export_data_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.export_data in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.export_data] = mock_rpc
        request = {}
        client.export_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.export_data(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_export_data_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = DatasetServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.export_data
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.export_data
        ] = mock_rpc

        request = {}
        await client.export_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.export_data(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_export_data_async(
    transport: str = "grpc_asyncio", request_type=dataset_service.ExportDataRequest
):
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.export_data), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.export_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = dataset_service.ExportDataRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_export_data_async_from_dict():
    await test_export_data_async(request_type=dict)


def test_export_data_field_headers():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.ExportDataRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.export_data), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.export_data(request)

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
async def test_export_data_field_headers_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.ExportDataRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.export_data), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.export_data(request)

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


def test_export_data_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.export_data), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.export_data(
            name="name_value",
            export_config=dataset.ExportDataConfig(
                gcs_destination=io.GcsDestination(
                    output_uri_prefix="output_uri_prefix_value"
                )
            ),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val
        arg = args[0].export_config
        mock_val = dataset.ExportDataConfig(
            gcs_destination=io.GcsDestination(
                output_uri_prefix="output_uri_prefix_value"
            )
        )
        assert arg == mock_val


def test_export_data_flattened_error():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.export_data(
            dataset_service.ExportDataRequest(),
            name="name_value",
            export_config=dataset.ExportDataConfig(
                gcs_destination=io.GcsDestination(
                    output_uri_prefix="output_uri_prefix_value"
                )
            ),
        )


@pytest.mark.asyncio
async def test_export_data_flattened_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.export_data), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.export_data(
            name="name_value",
            export_config=dataset.ExportDataConfig(
                gcs_destination=io.GcsDestination(
                    output_uri_prefix="output_uri_prefix_value"
                )
            ),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val
        arg = args[0].export_config
        mock_val = dataset.ExportDataConfig(
            gcs_destination=io.GcsDestination(
                output_uri_prefix="output_uri_prefix_value"
            )
        )
        assert arg == mock_val


@pytest.mark.asyncio
async def test_export_data_flattened_error_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.export_data(
            dataset_service.ExportDataRequest(),
            name="name_value",
            export_config=dataset.ExportDataConfig(
                gcs_destination=io.GcsDestination(
                    output_uri_prefix="output_uri_prefix_value"
                )
            ),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.CreateDatasetVersionRequest,
        dict,
    ],
)
def test_create_dataset_version(request_type, transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.create_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = dataset_service.CreateDatasetVersionRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_create_dataset_version_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = dataset_service.CreateDatasetVersionRequest(
        parent="parent_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_dataset_version), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.create_dataset_version(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == dataset_service.CreateDatasetVersionRequest(
            parent="parent_value",
        )


def test_create_dataset_version_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.create_dataset_version
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.create_dataset_version] = (
            mock_rpc
        )
        request = {}
        client.create_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.create_dataset_version(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_create_dataset_version_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = DatasetServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.create_dataset_version
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.create_dataset_version
        ] = mock_rpc

        request = {}
        await client.create_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.create_dataset_version(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_create_dataset_version_async(
    transport: str = "grpc_asyncio",
    request_type=dataset_service.CreateDatasetVersionRequest,
):
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.create_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = dataset_service.CreateDatasetVersionRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_create_dataset_version_async_from_dict():
    await test_create_dataset_version_async(request_type=dict)


def test_create_dataset_version_field_headers():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.CreateDatasetVersionRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_dataset_version), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.create_dataset_version(request)

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
async def test_create_dataset_version_field_headers_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.CreateDatasetVersionRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_dataset_version), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.create_dataset_version(request)

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


def test_create_dataset_version_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_dataset_version(
            parent="parent_value",
            dataset_version=gca_dataset_version.DatasetVersion(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].dataset_version
        mock_val = gca_dataset_version.DatasetVersion(name="name_value")
        assert arg == mock_val


def test_create_dataset_version_flattened_error():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_dataset_version(
            dataset_service.CreateDatasetVersionRequest(),
            parent="parent_value",
            dataset_version=gca_dataset_version.DatasetVersion(name="name_value"),
        )


@pytest.mark.asyncio
async def test_create_dataset_version_flattened_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_dataset_version(
            parent="parent_value",
            dataset_version=gca_dataset_version.DatasetVersion(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].dataset_version
        mock_val = gca_dataset_version.DatasetVersion(name="name_value")
        assert arg == mock_val


@pytest.mark.asyncio
async def test_create_dataset_version_flattened_error_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_dataset_version(
            dataset_service.CreateDatasetVersionRequest(),
            parent="parent_value",
            dataset_version=gca_dataset_version.DatasetVersion(name="name_value"),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.UpdateDatasetVersionRequest,
        dict,
    ],
)
def test_update_dataset_version(request_type, transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_dataset_version.DatasetVersion(
            name="name_value",
            etag="etag_value",
            big_query_dataset_name="big_query_dataset_name_value",
            display_name="display_name_value",
            model_reference="model_reference_value",
            satisfies_pzs=True,
            satisfies_pzi=True,
        )
        response = client.update_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = dataset_service.UpdateDatasetVersionRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_dataset_version.DatasetVersion)
    assert response.name == "name_value"
    assert response.etag == "etag_value"
    assert response.big_query_dataset_name == "big_query_dataset_name_value"
    assert response.display_name == "display_name_value"
    assert response.model_reference == "model_reference_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


def test_update_dataset_version_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = dataset_service.UpdateDatasetVersionRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_dataset_version), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.update_dataset_version(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == dataset_service.UpdateDatasetVersionRequest()


def test_update_dataset_version_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.update_dataset_version
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.update_dataset_version] = (
            mock_rpc
        )
        request = {}
        client.update_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.update_dataset_version(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_update_dataset_version_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = DatasetServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.update_dataset_version
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.update_dataset_version
        ] = mock_rpc

        request = {}
        await client.update_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.update_dataset_version(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_update_dataset_version_async(
    transport: str = "grpc_asyncio",
    request_type=dataset_service.UpdateDatasetVersionRequest,
):
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_dataset_version.DatasetVersion(
                name="name_value",
                etag="etag_value",
                big_query_dataset_name="big_query_dataset_name_value",
                display_name="display_name_value",
                model_reference="model_reference_value",
                satisfies_pzs=True,
                satisfies_pzi=True,
            )
        )
        response = await client.update_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = dataset_service.UpdateDatasetVersionRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_dataset_version.DatasetVersion)
    assert response.name == "name_value"
    assert response.etag == "etag_value"
    assert response.big_query_dataset_name == "big_query_dataset_name_value"
    assert response.display_name == "display_name_value"
    assert response.model_reference == "model_reference_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


@pytest.mark.asyncio
async def test_update_dataset_version_async_from_dict():
    await test_update_dataset_version_async(request_type=dict)


def test_update_dataset_version_field_headers():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.UpdateDatasetVersionRequest()

    request.dataset_version.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_dataset_version), "__call__"
    ) as call:
        call.return_value = gca_dataset_version.DatasetVersion()
        client.update_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "dataset_version.name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_dataset_version_field_headers_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.UpdateDatasetVersionRequest()

    request.dataset_version.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_dataset_version), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_dataset_version.DatasetVersion()
        )
        await client.update_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "dataset_version.name=name_value",
    ) in kw["metadata"]


def test_update_dataset_version_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_dataset_version.DatasetVersion()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_dataset_version(
            dataset_version=gca_dataset_version.DatasetVersion(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].dataset_version
        mock_val = gca_dataset_version.DatasetVersion(name="name_value")
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=["paths_value"])
        assert arg == mock_val


def test_update_dataset_version_flattened_error():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_dataset_version(
            dataset_service.UpdateDatasetVersionRequest(),
            dataset_version=gca_dataset_version.DatasetVersion(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_dataset_version_flattened_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_dataset_version.DatasetVersion()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_dataset_version.DatasetVersion()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_dataset_version(
            dataset_version=gca_dataset_version.DatasetVersion(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].dataset_version
        mock_val = gca_dataset_version.DatasetVersion(name="name_value")
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=["paths_value"])
        assert arg == mock_val


@pytest.mark.asyncio
async def test_update_dataset_version_flattened_error_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_dataset_version(
            dataset_service.UpdateDatasetVersionRequest(),
            dataset_version=gca_dataset_version.DatasetVersion(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.DeleteDatasetVersionRequest,
        dict,
    ],
)
def test_delete_dataset_version(request_type, transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = dataset_service.DeleteDatasetVersionRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_dataset_version_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = dataset_service.DeleteDatasetVersionRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_dataset_version), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.delete_dataset_version(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == dataset_service.DeleteDatasetVersionRequest(
            name="name_value",
        )


def test_delete_dataset_version_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.delete_dataset_version
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.delete_dataset_version] = (
            mock_rpc
        )
        request = {}
        client.delete_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.delete_dataset_version(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_delete_dataset_version_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = DatasetServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.delete_dataset_version
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.delete_dataset_version
        ] = mock_rpc

        request = {}
        await client.delete_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.delete_dataset_version(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_delete_dataset_version_async(
    transport: str = "grpc_asyncio",
    request_type=dataset_service.DeleteDatasetVersionRequest,
):
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = dataset_service.DeleteDatasetVersionRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_dataset_version_async_from_dict():
    await test_delete_dataset_version_async(request_type=dict)


def test_delete_dataset_version_field_headers():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.DeleteDatasetVersionRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_dataset_version), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_dataset_version(request)

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
async def test_delete_dataset_version_field_headers_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.DeleteDatasetVersionRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_dataset_version), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_dataset_version(request)

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


def test_delete_dataset_version_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_dataset_version(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_delete_dataset_version_flattened_error():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_dataset_version(
            dataset_service.DeleteDatasetVersionRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_dataset_version_flattened_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_dataset_version(
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
async def test_delete_dataset_version_flattened_error_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_dataset_version(
            dataset_service.DeleteDatasetVersionRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.GetDatasetVersionRequest,
        dict,
    ],
)
def test_get_dataset_version(request_type, transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_version.DatasetVersion(
            name="name_value",
            etag="etag_value",
            big_query_dataset_name="big_query_dataset_name_value",
            display_name="display_name_value",
            model_reference="model_reference_value",
            satisfies_pzs=True,
            satisfies_pzi=True,
        )
        response = client.get_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = dataset_service.GetDatasetVersionRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, dataset_version.DatasetVersion)
    assert response.name == "name_value"
    assert response.etag == "etag_value"
    assert response.big_query_dataset_name == "big_query_dataset_name_value"
    assert response.display_name == "display_name_value"
    assert response.model_reference == "model_reference_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


def test_get_dataset_version_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = dataset_service.GetDatasetVersionRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_dataset_version), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.get_dataset_version(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == dataset_service.GetDatasetVersionRequest(
            name="name_value",
        )


def test_get_dataset_version_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.get_dataset_version in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.get_dataset_version] = (
            mock_rpc
        )
        request = {}
        client.get_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_dataset_version(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_get_dataset_version_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = DatasetServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.get_dataset_version
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.get_dataset_version
        ] = mock_rpc

        request = {}
        await client.get_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.get_dataset_version(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_get_dataset_version_async(
    transport: str = "grpc_asyncio",
    request_type=dataset_service.GetDatasetVersionRequest,
):
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_version.DatasetVersion(
                name="name_value",
                etag="etag_value",
                big_query_dataset_name="big_query_dataset_name_value",
                display_name="display_name_value",
                model_reference="model_reference_value",
                satisfies_pzs=True,
                satisfies_pzi=True,
            )
        )
        response = await client.get_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = dataset_service.GetDatasetVersionRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, dataset_version.DatasetVersion)
    assert response.name == "name_value"
    assert response.etag == "etag_value"
    assert response.big_query_dataset_name == "big_query_dataset_name_value"
    assert response.display_name == "display_name_value"
    assert response.model_reference == "model_reference_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


@pytest.mark.asyncio
async def test_get_dataset_version_async_from_dict():
    await test_get_dataset_version_async(request_type=dict)


def test_get_dataset_version_field_headers():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.GetDatasetVersionRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_dataset_version), "__call__"
    ) as call:
        call.return_value = dataset_version.DatasetVersion()
        client.get_dataset_version(request)

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
async def test_get_dataset_version_field_headers_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.GetDatasetVersionRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_dataset_version), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_version.DatasetVersion()
        )
        await client.get_dataset_version(request)

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


def test_get_dataset_version_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_version.DatasetVersion()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_dataset_version(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_get_dataset_version_flattened_error():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_dataset_version(
            dataset_service.GetDatasetVersionRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_get_dataset_version_flattened_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_version.DatasetVersion()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_version.DatasetVersion()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_dataset_version(
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
async def test_get_dataset_version_flattened_error_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_dataset_version(
            dataset_service.GetDatasetVersionRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.ListDatasetVersionsRequest,
        dict,
    ],
)
def test_list_dataset_versions(request_type, transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_dataset_versions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_service.ListDatasetVersionsResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_dataset_versions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = dataset_service.ListDatasetVersionsRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDatasetVersionsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_dataset_versions_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = dataset_service.ListDatasetVersionsRequest(
        parent="parent_value",
        filter="filter_value",
        page_token="page_token_value",
        order_by="order_by_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_dataset_versions), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.list_dataset_versions(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == dataset_service.ListDatasetVersionsRequest(
            parent="parent_value",
            filter="filter_value",
            page_token="page_token_value",
            order_by="order_by_value",
        )


def test_list_dataset_versions_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.list_dataset_versions
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.list_dataset_versions] = (
            mock_rpc
        )
        request = {}
        client.list_dataset_versions(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_dataset_versions(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_list_dataset_versions_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = DatasetServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.list_dataset_versions
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.list_dataset_versions
        ] = mock_rpc

        request = {}
        await client.list_dataset_versions(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.list_dataset_versions(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_list_dataset_versions_async(
    transport: str = "grpc_asyncio",
    request_type=dataset_service.ListDatasetVersionsRequest,
):
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_dataset_versions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.ListDatasetVersionsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_dataset_versions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = dataset_service.ListDatasetVersionsRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDatasetVersionsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_dataset_versions_async_from_dict():
    await test_list_dataset_versions_async(request_type=dict)


def test_list_dataset_versions_field_headers():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.ListDatasetVersionsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_dataset_versions), "__call__"
    ) as call:
        call.return_value = dataset_service.ListDatasetVersionsResponse()
        client.list_dataset_versions(request)

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
async def test_list_dataset_versions_field_headers_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.ListDatasetVersionsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_dataset_versions), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.ListDatasetVersionsResponse()
        )
        await client.list_dataset_versions(request)

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


def test_list_dataset_versions_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_dataset_versions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_service.ListDatasetVersionsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_dataset_versions(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_list_dataset_versions_flattened_error():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_dataset_versions(
            dataset_service.ListDatasetVersionsRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_dataset_versions_flattened_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_dataset_versions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_service.ListDatasetVersionsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.ListDatasetVersionsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_dataset_versions(
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
async def test_list_dataset_versions_flattened_error_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_dataset_versions(
            dataset_service.ListDatasetVersionsRequest(),
            parent="parent_value",
        )


def test_list_dataset_versions_pager(transport_name: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_dataset_versions), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListDatasetVersionsResponse(
                dataset_versions=[
                    dataset_version.DatasetVersion(),
                    dataset_version.DatasetVersion(),
                    dataset_version.DatasetVersion(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListDatasetVersionsResponse(
                dataset_versions=[],
                next_page_token="def",
            ),
            dataset_service.ListDatasetVersionsResponse(
                dataset_versions=[
                    dataset_version.DatasetVersion(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListDatasetVersionsResponse(
                dataset_versions=[
                    dataset_version.DatasetVersion(),
                    dataset_version.DatasetVersion(),
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
        pager = client.list_dataset_versions(request={}, retry=retry, timeout=timeout)

        assert pager._metadata == expected_metadata
        assert pager._retry == retry
        assert pager._timeout == timeout

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, dataset_version.DatasetVersion) for i in results)


def test_list_dataset_versions_pages(transport_name: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_dataset_versions), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListDatasetVersionsResponse(
                dataset_versions=[
                    dataset_version.DatasetVersion(),
                    dataset_version.DatasetVersion(),
                    dataset_version.DatasetVersion(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListDatasetVersionsResponse(
                dataset_versions=[],
                next_page_token="def",
            ),
            dataset_service.ListDatasetVersionsResponse(
                dataset_versions=[
                    dataset_version.DatasetVersion(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListDatasetVersionsResponse(
                dataset_versions=[
                    dataset_version.DatasetVersion(),
                    dataset_version.DatasetVersion(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_dataset_versions(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_dataset_versions_async_pager():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_dataset_versions),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListDatasetVersionsResponse(
                dataset_versions=[
                    dataset_version.DatasetVersion(),
                    dataset_version.DatasetVersion(),
                    dataset_version.DatasetVersion(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListDatasetVersionsResponse(
                dataset_versions=[],
                next_page_token="def",
            ),
            dataset_service.ListDatasetVersionsResponse(
                dataset_versions=[
                    dataset_version.DatasetVersion(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListDatasetVersionsResponse(
                dataset_versions=[
                    dataset_version.DatasetVersion(),
                    dataset_version.DatasetVersion(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_dataset_versions(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, dataset_version.DatasetVersion) for i in responses)


@pytest.mark.asyncio
async def test_list_dataset_versions_async_pages():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_dataset_versions),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListDatasetVersionsResponse(
                dataset_versions=[
                    dataset_version.DatasetVersion(),
                    dataset_version.DatasetVersion(),
                    dataset_version.DatasetVersion(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListDatasetVersionsResponse(
                dataset_versions=[],
                next_page_token="def",
            ),
            dataset_service.ListDatasetVersionsResponse(
                dataset_versions=[
                    dataset_version.DatasetVersion(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListDatasetVersionsResponse(
                dataset_versions=[
                    dataset_version.DatasetVersion(),
                    dataset_version.DatasetVersion(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.list_dataset_versions(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.RestoreDatasetVersionRequest,
        dict,
    ],
)
def test_restore_dataset_version(request_type, transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.restore_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.restore_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = dataset_service.RestoreDatasetVersionRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_restore_dataset_version_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = dataset_service.RestoreDatasetVersionRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.restore_dataset_version), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.restore_dataset_version(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == dataset_service.RestoreDatasetVersionRequest(
            name="name_value",
        )


def test_restore_dataset_version_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.restore_dataset_version
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[
            client._transport.restore_dataset_version
        ] = mock_rpc
        request = {}
        client.restore_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.restore_dataset_version(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_restore_dataset_version_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = DatasetServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.restore_dataset_version
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.restore_dataset_version
        ] = mock_rpc

        request = {}
        await client.restore_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.restore_dataset_version(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_restore_dataset_version_async(
    transport: str = "grpc_asyncio",
    request_type=dataset_service.RestoreDatasetVersionRequest,
):
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.restore_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.restore_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = dataset_service.RestoreDatasetVersionRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_restore_dataset_version_async_from_dict():
    await test_restore_dataset_version_async(request_type=dict)


def test_restore_dataset_version_field_headers():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.RestoreDatasetVersionRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.restore_dataset_version), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.restore_dataset_version(request)

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
async def test_restore_dataset_version_field_headers_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.RestoreDatasetVersionRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.restore_dataset_version), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.restore_dataset_version(request)

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


def test_restore_dataset_version_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.restore_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.restore_dataset_version(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_restore_dataset_version_flattened_error():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.restore_dataset_version(
            dataset_service.RestoreDatasetVersionRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_restore_dataset_version_flattened_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.restore_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.restore_dataset_version(
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
async def test_restore_dataset_version_flattened_error_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.restore_dataset_version(
            dataset_service.RestoreDatasetVersionRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.ListDataItemsRequest,
        dict,
    ],
)
def test_list_data_items(request_type, transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_data_items), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_service.ListDataItemsResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_data_items(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = dataset_service.ListDataItemsRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDataItemsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_data_items_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = dataset_service.ListDataItemsRequest(
        parent="parent_value",
        filter="filter_value",
        page_token="page_token_value",
        order_by="order_by_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_data_items), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.list_data_items(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == dataset_service.ListDataItemsRequest(
            parent="parent_value",
            filter="filter_value",
            page_token="page_token_value",
            order_by="order_by_value",
        )


def test_list_data_items_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.list_data_items in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.list_data_items] = mock_rpc
        request = {}
        client.list_data_items(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_data_items(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_list_data_items_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = DatasetServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.list_data_items
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.list_data_items
        ] = mock_rpc

        request = {}
        await client.list_data_items(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.list_data_items(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_list_data_items_async(
    transport: str = "grpc_asyncio", request_type=dataset_service.ListDataItemsRequest
):
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_data_items), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.ListDataItemsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_data_items(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = dataset_service.ListDataItemsRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDataItemsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_data_items_async_from_dict():
    await test_list_data_items_async(request_type=dict)


def test_list_data_items_field_headers():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.ListDataItemsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_data_items), "__call__") as call:
        call.return_value = dataset_service.ListDataItemsResponse()
        client.list_data_items(request)

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
async def test_list_data_items_field_headers_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.ListDataItemsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_data_items), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.ListDataItemsResponse()
        )
        await client.list_data_items(request)

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


def test_list_data_items_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_data_items), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_service.ListDataItemsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_data_items(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_list_data_items_flattened_error():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_data_items(
            dataset_service.ListDataItemsRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_data_items_flattened_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_data_items), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_service.ListDataItemsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.ListDataItemsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_data_items(
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
async def test_list_data_items_flattened_error_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_data_items(
            dataset_service.ListDataItemsRequest(),
            parent="parent_value",
        )


def test_list_data_items_pager(transport_name: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_data_items), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListDataItemsResponse(
                data_items=[
                    data_item.DataItem(),
                    data_item.DataItem(),
                    data_item.DataItem(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListDataItemsResponse(
                data_items=[],
                next_page_token="def",
            ),
            dataset_service.ListDataItemsResponse(
                data_items=[
                    data_item.DataItem(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListDataItemsResponse(
                data_items=[
                    data_item.DataItem(),
                    data_item.DataItem(),
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
        pager = client.list_data_items(request={}, retry=retry, timeout=timeout)

        assert pager._metadata == expected_metadata
        assert pager._retry == retry
        assert pager._timeout == timeout

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, data_item.DataItem) for i in results)


def test_list_data_items_pages(transport_name: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_data_items), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListDataItemsResponse(
                data_items=[
                    data_item.DataItem(),
                    data_item.DataItem(),
                    data_item.DataItem(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListDataItemsResponse(
                data_items=[],
                next_page_token="def",
            ),
            dataset_service.ListDataItemsResponse(
                data_items=[
                    data_item.DataItem(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListDataItemsResponse(
                data_items=[
                    data_item.DataItem(),
                    data_item.DataItem(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_data_items(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_data_items_async_pager():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_data_items), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListDataItemsResponse(
                data_items=[
                    data_item.DataItem(),
                    data_item.DataItem(),
                    data_item.DataItem(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListDataItemsResponse(
                data_items=[],
                next_page_token="def",
            ),
            dataset_service.ListDataItemsResponse(
                data_items=[
                    data_item.DataItem(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListDataItemsResponse(
                data_items=[
                    data_item.DataItem(),
                    data_item.DataItem(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_data_items(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, data_item.DataItem) for i in responses)


@pytest.mark.asyncio
async def test_list_data_items_async_pages():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_data_items), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListDataItemsResponse(
                data_items=[
                    data_item.DataItem(),
                    data_item.DataItem(),
                    data_item.DataItem(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListDataItemsResponse(
                data_items=[],
                next_page_token="def",
            ),
            dataset_service.ListDataItemsResponse(
                data_items=[
                    data_item.DataItem(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListDataItemsResponse(
                data_items=[
                    data_item.DataItem(),
                    data_item.DataItem(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.list_data_items(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.SearchDataItemsRequest,
        dict,
    ],
)
def test_search_data_items(request_type, transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_data_items), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_service.SearchDataItemsResponse(
            next_page_token="next_page_token_value",
        )
        response = client.search_data_items(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = dataset_service.SearchDataItemsRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.SearchDataItemsPager)
    assert response.next_page_token == "next_page_token_value"


def test_search_data_items_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = dataset_service.SearchDataItemsRequest(
        order_by_data_item="order_by_data_item_value",
        dataset="dataset_value",
        saved_query="saved_query_value",
        data_labeling_job="data_labeling_job_value",
        data_item_filter="data_item_filter_value",
        annotations_filter="annotations_filter_value",
        order_by="order_by_value",
        page_token="page_token_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_data_items), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.search_data_items(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == dataset_service.SearchDataItemsRequest(
            order_by_data_item="order_by_data_item_value",
            dataset="dataset_value",
            saved_query="saved_query_value",
            data_labeling_job="data_labeling_job_value",
            data_item_filter="data_item_filter_value",
            annotations_filter="annotations_filter_value",
            order_by="order_by_value",
            page_token="page_token_value",
        )


def test_search_data_items_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.search_data_items in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.search_data_items] = (
            mock_rpc
        )
        request = {}
        client.search_data_items(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.search_data_items(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_search_data_items_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = DatasetServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.search_data_items
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.search_data_items
        ] = mock_rpc

        request = {}
        await client.search_data_items(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.search_data_items(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_search_data_items_async(
    transport: str = "grpc_asyncio", request_type=dataset_service.SearchDataItemsRequest
):
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_data_items), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.SearchDataItemsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.search_data_items(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = dataset_service.SearchDataItemsRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.SearchDataItemsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_search_data_items_async_from_dict():
    await test_search_data_items_async(request_type=dict)


def test_search_data_items_field_headers():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.SearchDataItemsRequest()

    request.dataset = "dataset_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_data_items), "__call__"
    ) as call:
        call.return_value = dataset_service.SearchDataItemsResponse()
        client.search_data_items(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "dataset=dataset_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_search_data_items_field_headers_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.SearchDataItemsRequest()

    request.dataset = "dataset_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_data_items), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.SearchDataItemsResponse()
        )
        await client.search_data_items(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "dataset=dataset_value",
    ) in kw["metadata"]


def test_search_data_items_pager(transport_name: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_data_items), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.SearchDataItemsResponse(
                data_item_views=[
                    dataset_service.DataItemView(),
                    dataset_service.DataItemView(),
                    dataset_service.DataItemView(),
                ],
                next_page_token="abc",
            ),
            dataset_service.SearchDataItemsResponse(
                data_item_views=[],
                next_page_token="def",
            ),
            dataset_service.SearchDataItemsResponse(
                data_item_views=[
                    dataset_service.DataItemView(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.SearchDataItemsResponse(
                data_item_views=[
                    dataset_service.DataItemView(),
                    dataset_service.DataItemView(),
                ],
            ),
            RuntimeError,
        )

        expected_metadata = ()
        retry = retries.Retry()
        timeout = 5
        expected_metadata = tuple(expected_metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("dataset", ""),)),
        )
        pager = client.search_data_items(request={}, retry=retry, timeout=timeout)

        assert pager._metadata == expected_metadata
        assert pager._retry == retry
        assert pager._timeout == timeout

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, dataset_service.DataItemView) for i in results)


def test_search_data_items_pages(transport_name: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_data_items), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.SearchDataItemsResponse(
                data_item_views=[
                    dataset_service.DataItemView(),
                    dataset_service.DataItemView(),
                    dataset_service.DataItemView(),
                ],
                next_page_token="abc",
            ),
            dataset_service.SearchDataItemsResponse(
                data_item_views=[],
                next_page_token="def",
            ),
            dataset_service.SearchDataItemsResponse(
                data_item_views=[
                    dataset_service.DataItemView(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.SearchDataItemsResponse(
                data_item_views=[
                    dataset_service.DataItemView(),
                    dataset_service.DataItemView(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.search_data_items(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_search_data_items_async_pager():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_data_items),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.SearchDataItemsResponse(
                data_item_views=[
                    dataset_service.DataItemView(),
                    dataset_service.DataItemView(),
                    dataset_service.DataItemView(),
                ],
                next_page_token="abc",
            ),
            dataset_service.SearchDataItemsResponse(
                data_item_views=[],
                next_page_token="def",
            ),
            dataset_service.SearchDataItemsResponse(
                data_item_views=[
                    dataset_service.DataItemView(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.SearchDataItemsResponse(
                data_item_views=[
                    dataset_service.DataItemView(),
                    dataset_service.DataItemView(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.search_data_items(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, dataset_service.DataItemView) for i in responses)


@pytest.mark.asyncio
async def test_search_data_items_async_pages():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_data_items),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.SearchDataItemsResponse(
                data_item_views=[
                    dataset_service.DataItemView(),
                    dataset_service.DataItemView(),
                    dataset_service.DataItemView(),
                ],
                next_page_token="abc",
            ),
            dataset_service.SearchDataItemsResponse(
                data_item_views=[],
                next_page_token="def",
            ),
            dataset_service.SearchDataItemsResponse(
                data_item_views=[
                    dataset_service.DataItemView(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.SearchDataItemsResponse(
                data_item_views=[
                    dataset_service.DataItemView(),
                    dataset_service.DataItemView(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.search_data_items(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.ListSavedQueriesRequest,
        dict,
    ],
)
def test_list_saved_queries(request_type, transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_saved_queries), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_service.ListSavedQueriesResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_saved_queries(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = dataset_service.ListSavedQueriesRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListSavedQueriesPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_saved_queries_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = dataset_service.ListSavedQueriesRequest(
        parent="parent_value",
        filter="filter_value",
        page_token="page_token_value",
        order_by="order_by_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_saved_queries), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.list_saved_queries(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == dataset_service.ListSavedQueriesRequest(
            parent="parent_value",
            filter="filter_value",
            page_token="page_token_value",
            order_by="order_by_value",
        )


def test_list_saved_queries_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.list_saved_queries in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.list_saved_queries] = (
            mock_rpc
        )
        request = {}
        client.list_saved_queries(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_saved_queries(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_list_saved_queries_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = DatasetServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.list_saved_queries
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.list_saved_queries
        ] = mock_rpc

        request = {}
        await client.list_saved_queries(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.list_saved_queries(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_list_saved_queries_async(
    transport: str = "grpc_asyncio",
    request_type=dataset_service.ListSavedQueriesRequest,
):
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_saved_queries), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.ListSavedQueriesResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_saved_queries(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = dataset_service.ListSavedQueriesRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListSavedQueriesAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_saved_queries_async_from_dict():
    await test_list_saved_queries_async(request_type=dict)


def test_list_saved_queries_field_headers():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.ListSavedQueriesRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_saved_queries), "__call__"
    ) as call:
        call.return_value = dataset_service.ListSavedQueriesResponse()
        client.list_saved_queries(request)

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
async def test_list_saved_queries_field_headers_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.ListSavedQueriesRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_saved_queries), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.ListSavedQueriesResponse()
        )
        await client.list_saved_queries(request)

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


def test_list_saved_queries_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_saved_queries), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_service.ListSavedQueriesResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_saved_queries(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_list_saved_queries_flattened_error():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_saved_queries(
            dataset_service.ListSavedQueriesRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_saved_queries_flattened_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_saved_queries), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_service.ListSavedQueriesResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.ListSavedQueriesResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_saved_queries(
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
async def test_list_saved_queries_flattened_error_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_saved_queries(
            dataset_service.ListSavedQueriesRequest(),
            parent="parent_value",
        )


def test_list_saved_queries_pager(transport_name: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_saved_queries), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListSavedQueriesResponse(
                saved_queries=[
                    saved_query.SavedQuery(),
                    saved_query.SavedQuery(),
                    saved_query.SavedQuery(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListSavedQueriesResponse(
                saved_queries=[],
                next_page_token="def",
            ),
            dataset_service.ListSavedQueriesResponse(
                saved_queries=[
                    saved_query.SavedQuery(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListSavedQueriesResponse(
                saved_queries=[
                    saved_query.SavedQuery(),
                    saved_query.SavedQuery(),
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
        pager = client.list_saved_queries(request={}, retry=retry, timeout=timeout)

        assert pager._metadata == expected_metadata
        assert pager._retry == retry
        assert pager._timeout == timeout

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, saved_query.SavedQuery) for i in results)


def test_list_saved_queries_pages(transport_name: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_saved_queries), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListSavedQueriesResponse(
                saved_queries=[
                    saved_query.SavedQuery(),
                    saved_query.SavedQuery(),
                    saved_query.SavedQuery(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListSavedQueriesResponse(
                saved_queries=[],
                next_page_token="def",
            ),
            dataset_service.ListSavedQueriesResponse(
                saved_queries=[
                    saved_query.SavedQuery(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListSavedQueriesResponse(
                saved_queries=[
                    saved_query.SavedQuery(),
                    saved_query.SavedQuery(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_saved_queries(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_saved_queries_async_pager():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_saved_queries),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListSavedQueriesResponse(
                saved_queries=[
                    saved_query.SavedQuery(),
                    saved_query.SavedQuery(),
                    saved_query.SavedQuery(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListSavedQueriesResponse(
                saved_queries=[],
                next_page_token="def",
            ),
            dataset_service.ListSavedQueriesResponse(
                saved_queries=[
                    saved_query.SavedQuery(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListSavedQueriesResponse(
                saved_queries=[
                    saved_query.SavedQuery(),
                    saved_query.SavedQuery(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_saved_queries(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, saved_query.SavedQuery) for i in responses)


@pytest.mark.asyncio
async def test_list_saved_queries_async_pages():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_saved_queries),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListSavedQueriesResponse(
                saved_queries=[
                    saved_query.SavedQuery(),
                    saved_query.SavedQuery(),
                    saved_query.SavedQuery(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListSavedQueriesResponse(
                saved_queries=[],
                next_page_token="def",
            ),
            dataset_service.ListSavedQueriesResponse(
                saved_queries=[
                    saved_query.SavedQuery(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListSavedQueriesResponse(
                saved_queries=[
                    saved_query.SavedQuery(),
                    saved_query.SavedQuery(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.list_saved_queries(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.DeleteSavedQueryRequest,
        dict,
    ],
)
def test_delete_saved_query(request_type, transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_saved_query), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_saved_query(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = dataset_service.DeleteSavedQueryRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_saved_query_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = dataset_service.DeleteSavedQueryRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_saved_query), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.delete_saved_query(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == dataset_service.DeleteSavedQueryRequest(
            name="name_value",
        )


def test_delete_saved_query_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.delete_saved_query in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.delete_saved_query] = (
            mock_rpc
        )
        request = {}
        client.delete_saved_query(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.delete_saved_query(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_delete_saved_query_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = DatasetServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.delete_saved_query
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.delete_saved_query
        ] = mock_rpc

        request = {}
        await client.delete_saved_query(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.delete_saved_query(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_delete_saved_query_async(
    transport: str = "grpc_asyncio",
    request_type=dataset_service.DeleteSavedQueryRequest,
):
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_saved_query), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_saved_query(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = dataset_service.DeleteSavedQueryRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_saved_query_async_from_dict():
    await test_delete_saved_query_async(request_type=dict)


def test_delete_saved_query_field_headers():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.DeleteSavedQueryRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_saved_query), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_saved_query(request)

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
async def test_delete_saved_query_field_headers_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.DeleteSavedQueryRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_saved_query), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_saved_query(request)

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


def test_delete_saved_query_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_saved_query), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_saved_query(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_delete_saved_query_flattened_error():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_saved_query(
            dataset_service.DeleteSavedQueryRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_saved_query_flattened_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_saved_query), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_saved_query(
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
async def test_delete_saved_query_flattened_error_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_saved_query(
            dataset_service.DeleteSavedQueryRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.GetAnnotationSpecRequest,
        dict,
    ],
)
def test_get_annotation_spec(request_type, transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_annotation_spec), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = annotation_spec.AnnotationSpec(
            name="name_value",
            display_name="display_name_value",
            etag="etag_value",
        )
        response = client.get_annotation_spec(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = dataset_service.GetAnnotationSpecRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, annotation_spec.AnnotationSpec)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.etag == "etag_value"


def test_get_annotation_spec_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = dataset_service.GetAnnotationSpecRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_annotation_spec), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.get_annotation_spec(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == dataset_service.GetAnnotationSpecRequest(
            name="name_value",
        )


def test_get_annotation_spec_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.get_annotation_spec in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.get_annotation_spec] = (
            mock_rpc
        )
        request = {}
        client.get_annotation_spec(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_annotation_spec(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_get_annotation_spec_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = DatasetServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.get_annotation_spec
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.get_annotation_spec
        ] = mock_rpc

        request = {}
        await client.get_annotation_spec(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.get_annotation_spec(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_get_annotation_spec_async(
    transport: str = "grpc_asyncio",
    request_type=dataset_service.GetAnnotationSpecRequest,
):
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_annotation_spec), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            annotation_spec.AnnotationSpec(
                name="name_value",
                display_name="display_name_value",
                etag="etag_value",
            )
        )
        response = await client.get_annotation_spec(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = dataset_service.GetAnnotationSpecRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, annotation_spec.AnnotationSpec)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.etag == "etag_value"


@pytest.mark.asyncio
async def test_get_annotation_spec_async_from_dict():
    await test_get_annotation_spec_async(request_type=dict)


def test_get_annotation_spec_field_headers():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.GetAnnotationSpecRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_annotation_spec), "__call__"
    ) as call:
        call.return_value = annotation_spec.AnnotationSpec()
        client.get_annotation_spec(request)

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
async def test_get_annotation_spec_field_headers_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.GetAnnotationSpecRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_annotation_spec), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            annotation_spec.AnnotationSpec()
        )
        await client.get_annotation_spec(request)

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


def test_get_annotation_spec_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_annotation_spec), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = annotation_spec.AnnotationSpec()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_annotation_spec(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_get_annotation_spec_flattened_error():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_annotation_spec(
            dataset_service.GetAnnotationSpecRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_get_annotation_spec_flattened_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_annotation_spec), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = annotation_spec.AnnotationSpec()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            annotation_spec.AnnotationSpec()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_annotation_spec(
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
async def test_get_annotation_spec_flattened_error_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_annotation_spec(
            dataset_service.GetAnnotationSpecRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.ListAnnotationsRequest,
        dict,
    ],
)
def test_list_annotations(request_type, transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_annotations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_service.ListAnnotationsResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_annotations(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = dataset_service.ListAnnotationsRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListAnnotationsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_annotations_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = dataset_service.ListAnnotationsRequest(
        parent="parent_value",
        filter="filter_value",
        page_token="page_token_value",
        order_by="order_by_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_annotations), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.list_annotations(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == dataset_service.ListAnnotationsRequest(
            parent="parent_value",
            filter="filter_value",
            page_token="page_token_value",
            order_by="order_by_value",
        )


def test_list_annotations_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.list_annotations in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.list_annotations] = (
            mock_rpc
        )
        request = {}
        client.list_annotations(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_annotations(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_list_annotations_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = DatasetServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.list_annotations
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.list_annotations
        ] = mock_rpc

        request = {}
        await client.list_annotations(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.list_annotations(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_list_annotations_async(
    transport: str = "grpc_asyncio", request_type=dataset_service.ListAnnotationsRequest
):
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_annotations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.ListAnnotationsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_annotations(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = dataset_service.ListAnnotationsRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListAnnotationsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_annotations_async_from_dict():
    await test_list_annotations_async(request_type=dict)


def test_list_annotations_field_headers():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.ListAnnotationsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_annotations), "__call__") as call:
        call.return_value = dataset_service.ListAnnotationsResponse()
        client.list_annotations(request)

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
async def test_list_annotations_field_headers_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.ListAnnotationsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_annotations), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.ListAnnotationsResponse()
        )
        await client.list_annotations(request)

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


def test_list_annotations_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_annotations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_service.ListAnnotationsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_annotations(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_list_annotations_flattened_error():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_annotations(
            dataset_service.ListAnnotationsRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_annotations_flattened_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_annotations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_service.ListAnnotationsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.ListAnnotationsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_annotations(
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
async def test_list_annotations_flattened_error_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_annotations(
            dataset_service.ListAnnotationsRequest(),
            parent="parent_value",
        )


def test_list_annotations_pager(transport_name: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_annotations), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListAnnotationsResponse(
                annotations=[
                    annotation.Annotation(),
                    annotation.Annotation(),
                    annotation.Annotation(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListAnnotationsResponse(
                annotations=[],
                next_page_token="def",
            ),
            dataset_service.ListAnnotationsResponse(
                annotations=[
                    annotation.Annotation(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListAnnotationsResponse(
                annotations=[
                    annotation.Annotation(),
                    annotation.Annotation(),
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
        pager = client.list_annotations(request={}, retry=retry, timeout=timeout)

        assert pager._metadata == expected_metadata
        assert pager._retry == retry
        assert pager._timeout == timeout

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, annotation.Annotation) for i in results)


def test_list_annotations_pages(transport_name: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_annotations), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListAnnotationsResponse(
                annotations=[
                    annotation.Annotation(),
                    annotation.Annotation(),
                    annotation.Annotation(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListAnnotationsResponse(
                annotations=[],
                next_page_token="def",
            ),
            dataset_service.ListAnnotationsResponse(
                annotations=[
                    annotation.Annotation(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListAnnotationsResponse(
                annotations=[
                    annotation.Annotation(),
                    annotation.Annotation(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_annotations(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_annotations_async_pager():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_annotations), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListAnnotationsResponse(
                annotations=[
                    annotation.Annotation(),
                    annotation.Annotation(),
                    annotation.Annotation(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListAnnotationsResponse(
                annotations=[],
                next_page_token="def",
            ),
            dataset_service.ListAnnotationsResponse(
                annotations=[
                    annotation.Annotation(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListAnnotationsResponse(
                annotations=[
                    annotation.Annotation(),
                    annotation.Annotation(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_annotations(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, annotation.Annotation) for i in responses)


@pytest.mark.asyncio
async def test_list_annotations_async_pages():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_annotations), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListAnnotationsResponse(
                annotations=[
                    annotation.Annotation(),
                    annotation.Annotation(),
                    annotation.Annotation(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListAnnotationsResponse(
                annotations=[],
                next_page_token="def",
            ),
            dataset_service.ListAnnotationsResponse(
                annotations=[
                    annotation.Annotation(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListAnnotationsResponse(
                annotations=[
                    annotation.Annotation(),
                    annotation.Annotation(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.list_annotations(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.AssessDataRequest,
        dict,
    ],
)
def test_assess_data(request_type, transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.assess_data), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.assess_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = dataset_service.AssessDataRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_assess_data_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = dataset_service.AssessDataRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.assess_data), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.assess_data(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == dataset_service.AssessDataRequest(
            name="name_value",
        )


def test_assess_data_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.assess_data in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.assess_data] = mock_rpc
        request = {}
        client.assess_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.assess_data(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_assess_data_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = DatasetServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.assess_data
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.assess_data
        ] = mock_rpc

        request = {}
        await client.assess_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.assess_data(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_assess_data_async(
    transport: str = "grpc_asyncio", request_type=dataset_service.AssessDataRequest
):
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.assess_data), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.assess_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = dataset_service.AssessDataRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_assess_data_async_from_dict():
    await test_assess_data_async(request_type=dict)


def test_assess_data_field_headers():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.AssessDataRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.assess_data), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.assess_data(request)

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
async def test_assess_data_field_headers_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.AssessDataRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.assess_data), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.assess_data(request)

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


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.AssembleDataRequest,
        dict,
    ],
)
def test_assemble_data(request_type, transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.assemble_data), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.assemble_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = dataset_service.AssembleDataRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_assemble_data_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = dataset_service.AssembleDataRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.assemble_data), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.assemble_data(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == dataset_service.AssembleDataRequest(
            name="name_value",
        )


def test_assemble_data_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.assemble_data in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.assemble_data] = mock_rpc
        request = {}
        client.assemble_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.assemble_data(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_assemble_data_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = DatasetServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.assemble_data
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.assemble_data
        ] = mock_rpc

        request = {}
        await client.assemble_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.assemble_data(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_assemble_data_async(
    transport: str = "grpc_asyncio", request_type=dataset_service.AssembleDataRequest
):
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.assemble_data), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.assemble_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = dataset_service.AssembleDataRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_assemble_data_async_from_dict():
    await test_assemble_data_async(request_type=dict)


def test_assemble_data_field_headers():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.AssembleDataRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.assemble_data), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.assemble_data(request)

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
async def test_assemble_data_field_headers_async():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.AssembleDataRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.assemble_data), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.assemble_data(request)

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


def test_create_dataset_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.create_dataset in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.create_dataset] = mock_rpc

        request = {}
        client.create_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.create_dataset(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_create_dataset_rest_required_fields(
    request_type=dataset_service.CreateDatasetRequest,
):
    transport_class = transports.DatasetServiceRestTransport

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
    ).create_dataset._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).create_dataset._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = DatasetServiceClient(
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

            response = client.create_dataset(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_create_dataset_rest_unset_required_fields():
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.create_dataset._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(())
        & set(
            (
                "parent",
                "dataset",
            )
        )
    )


def test_create_dataset_rest_flattened():
    client = DatasetServiceClient(
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
            dataset=gca_dataset.Dataset(name="name_value"),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.create_dataset(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{parent=projects/*/locations/*}/datasets"
            % client.transport._host,
            args[1],
        )


def test_create_dataset_rest_flattened_error(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_dataset(
            dataset_service.CreateDatasetRequest(),
            parent="parent_value",
            dataset=gca_dataset.Dataset(name="name_value"),
        )


def test_get_dataset_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.get_dataset in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.get_dataset] = mock_rpc

        request = {}
        client.get_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_dataset(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_get_dataset_rest_required_fields(
    request_type=dataset_service.GetDatasetRequest,
):
    transport_class = transports.DatasetServiceRestTransport

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
    ).get_dataset._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_dataset._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("read_mask",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = dataset.Dataset()
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
            return_value = dataset.Dataset.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.get_dataset(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_dataset_rest_unset_required_fields():
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_dataset._get_unset_required_fields({})
    assert set(unset_fields) == (set(("readMask",)) & set(("name",)))


def test_get_dataset_rest_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset.Dataset()

        # get arguments that satisfy an http rule for this method
        sample_request = {"name": "projects/sample1/locations/sample2/datasets/sample3"}

        # get truthy value for each flattened field
        mock_args = dict(
            name="name_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = dataset.Dataset.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.get_dataset(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/datasets/*}"
            % client.transport._host,
            args[1],
        )


def test_get_dataset_rest_flattened_error(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_dataset(
            dataset_service.GetDatasetRequest(),
            name="name_value",
        )


def test_update_dataset_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.update_dataset in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.update_dataset] = mock_rpc

        request = {}
        client.update_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.update_dataset(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_update_dataset_rest_required_fields(
    request_type=dataset_service.UpdateDatasetRequest,
):
    transport_class = transports.DatasetServiceRestTransport

    request_init = {}
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(pb_request, use_integers_for_enums=False)
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_dataset._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_dataset._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("update_mask",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone

    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = gca_dataset.Dataset()
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
            return_value = gca_dataset.Dataset.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.update_dataset(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_update_dataset_rest_unset_required_fields():
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.update_dataset._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("updateMask",))
        & set(
            (
                "dataset",
                "updateMask",
            )
        )
    )


def test_update_dataset_rest_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gca_dataset.Dataset()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "dataset": {"name": "projects/sample1/locations/sample2/datasets/sample3"}
        }

        # get truthy value for each flattened field
        mock_args = dict(
            dataset=gca_dataset.Dataset(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = gca_dataset.Dataset.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.update_dataset(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{dataset.name=projects/*/locations/*/datasets/*}"
            % client.transport._host,
            args[1],
        )


def test_update_dataset_rest_flattened_error(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_dataset(
            dataset_service.UpdateDatasetRequest(),
            dataset=gca_dataset.Dataset(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


def test_list_datasets_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.list_datasets in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.list_datasets] = mock_rpc

        request = {}
        client.list_datasets(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_datasets(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_list_datasets_rest_required_fields(
    request_type=dataset_service.ListDatasetsRequest,
):
    transport_class = transports.DatasetServiceRestTransport

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
    ).list_datasets._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_datasets._get_unset_required_fields(jsonified_request)
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

    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = dataset_service.ListDatasetsResponse()
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
            return_value = dataset_service.ListDatasetsResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.list_datasets(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_list_datasets_rest_unset_required_fields():
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.list_datasets._get_unset_required_fields({})
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


def test_list_datasets_rest_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset_service.ListDatasetsResponse()

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
        return_value = dataset_service.ListDatasetsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.list_datasets(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{parent=projects/*/locations/*}/datasets"
            % client.transport._host,
            args[1],
        )


def test_list_datasets_rest_flattened_error(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_datasets(
            dataset_service.ListDatasetsRequest(),
            parent="parent_value",
        )


def test_list_datasets_rest_pager(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            dataset_service.ListDatasetsResponse(
                datasets=[
                    dataset.Dataset(),
                    dataset.Dataset(),
                    dataset.Dataset(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListDatasetsResponse(
                datasets=[],
                next_page_token="def",
            ),
            dataset_service.ListDatasetsResponse(
                datasets=[
                    dataset.Dataset(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListDatasetsResponse(
                datasets=[
                    dataset.Dataset(),
                    dataset.Dataset(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(
            dataset_service.ListDatasetsResponse.to_json(x) for x in response
        )
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {"parent": "projects/sample1/locations/sample2"}

        pager = client.list_datasets(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, dataset.Dataset) for i in results)

        pages = list(client.list_datasets(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_delete_dataset_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.delete_dataset in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.delete_dataset] = mock_rpc

        request = {}
        client.delete_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.delete_dataset(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_delete_dataset_rest_required_fields(
    request_type=dataset_service.DeleteDatasetRequest,
):
    transport_class = transports.DatasetServiceRestTransport

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
    ).delete_dataset._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).delete_dataset._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = DatasetServiceClient(
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

            response = client.delete_dataset(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_delete_dataset_rest_unset_required_fields():
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.delete_dataset._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


def test_delete_dataset_rest_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {"name": "projects/sample1/locations/sample2/datasets/sample3"}

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

        client.delete_dataset(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/datasets/*}"
            % client.transport._host,
            args[1],
        )


def test_delete_dataset_rest_flattened_error(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_dataset(
            dataset_service.DeleteDatasetRequest(),
            name="name_value",
        )


def test_import_data_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.import_data in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.import_data] = mock_rpc

        request = {}
        client.import_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.import_data(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_import_data_rest_required_fields(
    request_type=dataset_service.ImportDataRequest,
):
    transport_class = transports.DatasetServiceRestTransport

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
    ).import_data._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).import_data._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = DatasetServiceClient(
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

            response = client.import_data(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_import_data_rest_unset_required_fields():
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.import_data._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(())
        & set(
            (
                "name",
                "importConfigs",
            )
        )
    )


def test_import_data_rest_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {"name": "projects/sample1/locations/sample2/datasets/sample3"}

        # get truthy value for each flattened field
        mock_args = dict(
            name="name_value",
            import_configs=[
                dataset.ImportDataConfig(gcs_source=io.GcsSource(uris=["uris_value"]))
            ],
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.import_data(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/datasets/*}:import"
            % client.transport._host,
            args[1],
        )


def test_import_data_rest_flattened_error(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.import_data(
            dataset_service.ImportDataRequest(),
            name="name_value",
            import_configs=[
                dataset.ImportDataConfig(gcs_source=io.GcsSource(uris=["uris_value"]))
            ],
        )


def test_export_data_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.export_data in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.export_data] = mock_rpc

        request = {}
        client.export_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.export_data(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_export_data_rest_required_fields(
    request_type=dataset_service.ExportDataRequest,
):
    transport_class = transports.DatasetServiceRestTransport

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
    ).export_data._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).export_data._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = DatasetServiceClient(
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

            response = client.export_data(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_export_data_rest_unset_required_fields():
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.export_data._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(())
        & set(
            (
                "name",
                "exportConfig",
            )
        )
    )


def test_export_data_rest_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {"name": "projects/sample1/locations/sample2/datasets/sample3"}

        # get truthy value for each flattened field
        mock_args = dict(
            name="name_value",
            export_config=dataset.ExportDataConfig(
                gcs_destination=io.GcsDestination(
                    output_uri_prefix="output_uri_prefix_value"
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

        client.export_data(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/datasets/*}:export"
            % client.transport._host,
            args[1],
        )


def test_export_data_rest_flattened_error(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.export_data(
            dataset_service.ExportDataRequest(),
            name="name_value",
            export_config=dataset.ExportDataConfig(
                gcs_destination=io.GcsDestination(
                    output_uri_prefix="output_uri_prefix_value"
                )
            ),
        )


def test_create_dataset_version_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.create_dataset_version
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.create_dataset_version] = (
            mock_rpc
        )

        request = {}
        client.create_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.create_dataset_version(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_create_dataset_version_rest_required_fields(
    request_type=dataset_service.CreateDatasetVersionRequest,
):
    transport_class = transports.DatasetServiceRestTransport

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
    ).create_dataset_version._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).create_dataset_version._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = DatasetServiceClient(
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

            response = client.create_dataset_version(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_create_dataset_version_rest_unset_required_fields():
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.create_dataset_version._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(())
        & set(
            (
                "parent",
                "datasetVersion",
            )
        )
    )


def test_create_dataset_version_rest_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "parent": "projects/sample1/locations/sample2/datasets/sample3"
        }

        # get truthy value for each flattened field
        mock_args = dict(
            parent="parent_value",
            dataset_version=gca_dataset_version.DatasetVersion(name="name_value"),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.create_dataset_version(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{parent=projects/*/locations/*/datasets/*}/datasetVersions"
            % client.transport._host,
            args[1],
        )


def test_create_dataset_version_rest_flattened_error(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_dataset_version(
            dataset_service.CreateDatasetVersionRequest(),
            parent="parent_value",
            dataset_version=gca_dataset_version.DatasetVersion(name="name_value"),
        )


def test_update_dataset_version_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.update_dataset_version
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.update_dataset_version] = (
            mock_rpc
        )

        request = {}
        client.update_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.update_dataset_version(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_update_dataset_version_rest_required_fields(
    request_type=dataset_service.UpdateDatasetVersionRequest,
):
    transport_class = transports.DatasetServiceRestTransport

    request_init = {}
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(pb_request, use_integers_for_enums=False)
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_dataset_version._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_dataset_version._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("update_mask",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone

    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = gca_dataset_version.DatasetVersion()
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
            return_value = gca_dataset_version.DatasetVersion.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.update_dataset_version(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_update_dataset_version_rest_unset_required_fields():
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.update_dataset_version._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("updateMask",))
        & set(
            (
                "datasetVersion",
                "updateMask",
            )
        )
    )


def test_update_dataset_version_rest_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gca_dataset_version.DatasetVersion()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "dataset_version": {
                "name": "projects/sample1/locations/sample2/datasets/sample3/datasetVersions/sample4"
            }
        }

        # get truthy value for each flattened field
        mock_args = dict(
            dataset_version=gca_dataset_version.DatasetVersion(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = gca_dataset_version.DatasetVersion.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.update_dataset_version(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{dataset_version.name=projects/*/locations/*/datasets/*/datasetVersions/*}"
            % client.transport._host,
            args[1],
        )


def test_update_dataset_version_rest_flattened_error(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_dataset_version(
            dataset_service.UpdateDatasetVersionRequest(),
            dataset_version=gca_dataset_version.DatasetVersion(name="name_value"),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


def test_delete_dataset_version_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.delete_dataset_version
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.delete_dataset_version] = (
            mock_rpc
        )

        request = {}
        client.delete_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.delete_dataset_version(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_delete_dataset_version_rest_required_fields(
    request_type=dataset_service.DeleteDatasetVersionRequest,
):
    transport_class = transports.DatasetServiceRestTransport

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
    ).delete_dataset_version._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).delete_dataset_version._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = DatasetServiceClient(
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

            response = client.delete_dataset_version(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_delete_dataset_version_rest_unset_required_fields():
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.delete_dataset_version._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


def test_delete_dataset_version_rest_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/datasets/sample3/datasetVersions/sample4"
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

        client.delete_dataset_version(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/datasets/*/datasetVersions/*}"
            % client.transport._host,
            args[1],
        )


def test_delete_dataset_version_rest_flattened_error(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_dataset_version(
            dataset_service.DeleteDatasetVersionRequest(),
            name="name_value",
        )


def test_get_dataset_version_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.get_dataset_version in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.get_dataset_version] = (
            mock_rpc
        )

        request = {}
        client.get_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_dataset_version(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_get_dataset_version_rest_required_fields(
    request_type=dataset_service.GetDatasetVersionRequest,
):
    transport_class = transports.DatasetServiceRestTransport

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
    ).get_dataset_version._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_dataset_version._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("read_mask",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = dataset_version.DatasetVersion()
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
            return_value = dataset_version.DatasetVersion.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.get_dataset_version(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_dataset_version_rest_unset_required_fields():
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_dataset_version._get_unset_required_fields({})
    assert set(unset_fields) == (set(("readMask",)) & set(("name",)))


def test_get_dataset_version_rest_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset_version.DatasetVersion()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/datasets/sample3/datasetVersions/sample4"
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
        return_value = dataset_version.DatasetVersion.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.get_dataset_version(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/datasets/*/datasetVersions/*}"
            % client.transport._host,
            args[1],
        )


def test_get_dataset_version_rest_flattened_error(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_dataset_version(
            dataset_service.GetDatasetVersionRequest(),
            name="name_value",
        )


def test_list_dataset_versions_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.list_dataset_versions
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.list_dataset_versions] = (
            mock_rpc
        )

        request = {}
        client.list_dataset_versions(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_dataset_versions(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_list_dataset_versions_rest_required_fields(
    request_type=dataset_service.ListDatasetVersionsRequest,
):
    transport_class = transports.DatasetServiceRestTransport

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
    ).list_dataset_versions._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_dataset_versions._get_unset_required_fields(jsonified_request)
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

    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = dataset_service.ListDatasetVersionsResponse()
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
            return_value = dataset_service.ListDatasetVersionsResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.list_dataset_versions(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_list_dataset_versions_rest_unset_required_fields():
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.list_dataset_versions._get_unset_required_fields({})
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


def test_list_dataset_versions_rest_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset_service.ListDatasetVersionsResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "parent": "projects/sample1/locations/sample2/datasets/sample3"
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
        return_value = dataset_service.ListDatasetVersionsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.list_dataset_versions(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{parent=projects/*/locations/*/datasets/*}/datasetVersions"
            % client.transport._host,
            args[1],
        )


def test_list_dataset_versions_rest_flattened_error(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_dataset_versions(
            dataset_service.ListDatasetVersionsRequest(),
            parent="parent_value",
        )


def test_list_dataset_versions_rest_pager(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            dataset_service.ListDatasetVersionsResponse(
                dataset_versions=[
                    dataset_version.DatasetVersion(),
                    dataset_version.DatasetVersion(),
                    dataset_version.DatasetVersion(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListDatasetVersionsResponse(
                dataset_versions=[],
                next_page_token="def",
            ),
            dataset_service.ListDatasetVersionsResponse(
                dataset_versions=[
                    dataset_version.DatasetVersion(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListDatasetVersionsResponse(
                dataset_versions=[
                    dataset_version.DatasetVersion(),
                    dataset_version.DatasetVersion(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(
            dataset_service.ListDatasetVersionsResponse.to_json(x) for x in response
        )
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {
            "parent": "projects/sample1/locations/sample2/datasets/sample3"
        }

        pager = client.list_dataset_versions(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, dataset_version.DatasetVersion) for i in results)

        pages = list(client.list_dataset_versions(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_restore_dataset_version_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.restore_dataset_version
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[
            client._transport.restore_dataset_version
        ] = mock_rpc

        request = {}
        client.restore_dataset_version(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.restore_dataset_version(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_restore_dataset_version_rest_required_fields(
    request_type=dataset_service.RestoreDatasetVersionRequest,
):
    transport_class = transports.DatasetServiceRestTransport

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
    ).restore_dataset_version._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).restore_dataset_version._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = DatasetServiceClient(
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
                "method": "get",
                "query_params": pb_request,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.restore_dataset_version(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_restore_dataset_version_rest_unset_required_fields():
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.restore_dataset_version._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


def test_restore_dataset_version_rest_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/datasets/sample3/datasetVersions/sample4"
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

        client.restore_dataset_version(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/datasets/*/datasetVersions/*}:restore"
            % client.transport._host,
            args[1],
        )


def test_restore_dataset_version_rest_flattened_error(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.restore_dataset_version(
            dataset_service.RestoreDatasetVersionRequest(),
            name="name_value",
        )


def test_list_data_items_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.list_data_items in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.list_data_items] = mock_rpc

        request = {}
        client.list_data_items(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_data_items(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_list_data_items_rest_required_fields(
    request_type=dataset_service.ListDataItemsRequest,
):
    transport_class = transports.DatasetServiceRestTransport

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
    ).list_data_items._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_data_items._get_unset_required_fields(jsonified_request)
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

    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = dataset_service.ListDataItemsResponse()
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
            return_value = dataset_service.ListDataItemsResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.list_data_items(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_list_data_items_rest_unset_required_fields():
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.list_data_items._get_unset_required_fields({})
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


def test_list_data_items_rest_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset_service.ListDataItemsResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "parent": "projects/sample1/locations/sample2/datasets/sample3"
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
        return_value = dataset_service.ListDataItemsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.list_data_items(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{parent=projects/*/locations/*/datasets/*}/dataItems"
            % client.transport._host,
            args[1],
        )


def test_list_data_items_rest_flattened_error(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_data_items(
            dataset_service.ListDataItemsRequest(),
            parent="parent_value",
        )


def test_list_data_items_rest_pager(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            dataset_service.ListDataItemsResponse(
                data_items=[
                    data_item.DataItem(),
                    data_item.DataItem(),
                    data_item.DataItem(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListDataItemsResponse(
                data_items=[],
                next_page_token="def",
            ),
            dataset_service.ListDataItemsResponse(
                data_items=[
                    data_item.DataItem(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListDataItemsResponse(
                data_items=[
                    data_item.DataItem(),
                    data_item.DataItem(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(
            dataset_service.ListDataItemsResponse.to_json(x) for x in response
        )
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {
            "parent": "projects/sample1/locations/sample2/datasets/sample3"
        }

        pager = client.list_data_items(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, data_item.DataItem) for i in results)

        pages = list(client.list_data_items(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_search_data_items_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.search_data_items in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.search_data_items] = (
            mock_rpc
        )

        request = {}
        client.search_data_items(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.search_data_items(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_search_data_items_rest_required_fields(
    request_type=dataset_service.SearchDataItemsRequest,
):
    transport_class = transports.DatasetServiceRestTransport

    request_init = {}
    request_init["dataset"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(pb_request, use_integers_for_enums=False)
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).search_data_items._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["dataset"] = "dataset_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).search_data_items._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(
        (
            "annotation_filters",
            "annotations_filter",
            "annotations_limit",
            "data_item_filter",
            "data_labeling_job",
            "field_mask",
            "order_by",
            "order_by_annotation",
            "order_by_data_item",
            "page_size",
            "page_token",
            "saved_query",
        )
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "dataset" in jsonified_request
    assert jsonified_request["dataset"] == "dataset_value"

    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = dataset_service.SearchDataItemsResponse()
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
            return_value = dataset_service.SearchDataItemsResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.search_data_items(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_search_data_items_rest_unset_required_fields():
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.search_data_items._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(
            (
                "annotationFilters",
                "annotationsFilter",
                "annotationsLimit",
                "dataItemFilter",
                "dataLabelingJob",
                "fieldMask",
                "orderBy",
                "orderByAnnotation",
                "orderByDataItem",
                "pageSize",
                "pageToken",
                "savedQuery",
            )
        )
        & set(("dataset",))
    )


def test_search_data_items_rest_pager(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            dataset_service.SearchDataItemsResponse(
                data_item_views=[
                    dataset_service.DataItemView(),
                    dataset_service.DataItemView(),
                    dataset_service.DataItemView(),
                ],
                next_page_token="abc",
            ),
            dataset_service.SearchDataItemsResponse(
                data_item_views=[],
                next_page_token="def",
            ),
            dataset_service.SearchDataItemsResponse(
                data_item_views=[
                    dataset_service.DataItemView(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.SearchDataItemsResponse(
                data_item_views=[
                    dataset_service.DataItemView(),
                    dataset_service.DataItemView(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(
            dataset_service.SearchDataItemsResponse.to_json(x) for x in response
        )
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {
            "dataset": "projects/sample1/locations/sample2/datasets/sample3"
        }

        pager = client.search_data_items(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, dataset_service.DataItemView) for i in results)

        pages = list(client.search_data_items(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_list_saved_queries_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.list_saved_queries in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.list_saved_queries] = (
            mock_rpc
        )

        request = {}
        client.list_saved_queries(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_saved_queries(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_list_saved_queries_rest_required_fields(
    request_type=dataset_service.ListSavedQueriesRequest,
):
    transport_class = transports.DatasetServiceRestTransport

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
    ).list_saved_queries._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_saved_queries._get_unset_required_fields(jsonified_request)
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

    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = dataset_service.ListSavedQueriesResponse()
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
            return_value = dataset_service.ListSavedQueriesResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.list_saved_queries(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_list_saved_queries_rest_unset_required_fields():
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.list_saved_queries._get_unset_required_fields({})
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


def test_list_saved_queries_rest_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset_service.ListSavedQueriesResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "parent": "projects/sample1/locations/sample2/datasets/sample3"
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
        return_value = dataset_service.ListSavedQueriesResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.list_saved_queries(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{parent=projects/*/locations/*/datasets/*}/savedQueries"
            % client.transport._host,
            args[1],
        )


def test_list_saved_queries_rest_flattened_error(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_saved_queries(
            dataset_service.ListSavedQueriesRequest(),
            parent="parent_value",
        )


def test_list_saved_queries_rest_pager(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            dataset_service.ListSavedQueriesResponse(
                saved_queries=[
                    saved_query.SavedQuery(),
                    saved_query.SavedQuery(),
                    saved_query.SavedQuery(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListSavedQueriesResponse(
                saved_queries=[],
                next_page_token="def",
            ),
            dataset_service.ListSavedQueriesResponse(
                saved_queries=[
                    saved_query.SavedQuery(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListSavedQueriesResponse(
                saved_queries=[
                    saved_query.SavedQuery(),
                    saved_query.SavedQuery(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(
            dataset_service.ListSavedQueriesResponse.to_json(x) for x in response
        )
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {
            "parent": "projects/sample1/locations/sample2/datasets/sample3"
        }

        pager = client.list_saved_queries(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, saved_query.SavedQuery) for i in results)

        pages = list(client.list_saved_queries(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_delete_saved_query_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.delete_saved_query in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.delete_saved_query] = (
            mock_rpc
        )

        request = {}
        client.delete_saved_query(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.delete_saved_query(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_delete_saved_query_rest_required_fields(
    request_type=dataset_service.DeleteSavedQueryRequest,
):
    transport_class = transports.DatasetServiceRestTransport

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
    ).delete_saved_query._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).delete_saved_query._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = DatasetServiceClient(
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

            response = client.delete_saved_query(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_delete_saved_query_rest_unset_required_fields():
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.delete_saved_query._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


def test_delete_saved_query_rest_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/datasets/sample3/savedQueries/sample4"
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

        client.delete_saved_query(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/datasets/*/savedQueries/*}"
            % client.transport._host,
            args[1],
        )


def test_delete_saved_query_rest_flattened_error(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_saved_query(
            dataset_service.DeleteSavedQueryRequest(),
            name="name_value",
        )


def test_get_annotation_spec_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.get_annotation_spec in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.get_annotation_spec] = (
            mock_rpc
        )

        request = {}
        client.get_annotation_spec(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_annotation_spec(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_get_annotation_spec_rest_required_fields(
    request_type=dataset_service.GetAnnotationSpecRequest,
):
    transport_class = transports.DatasetServiceRestTransport

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
    ).get_annotation_spec._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_annotation_spec._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("read_mask",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = annotation_spec.AnnotationSpec()
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
            return_value = annotation_spec.AnnotationSpec.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.get_annotation_spec(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_annotation_spec_rest_unset_required_fields():
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_annotation_spec._get_unset_required_fields({})
    assert set(unset_fields) == (set(("readMask",)) & set(("name",)))


def test_get_annotation_spec_rest_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = annotation_spec.AnnotationSpec()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/datasets/sample3/annotationSpecs/sample4"
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
        return_value = annotation_spec.AnnotationSpec.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.get_annotation_spec(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*}"
            % client.transport._host,
            args[1],
        )


def test_get_annotation_spec_rest_flattened_error(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_annotation_spec(
            dataset_service.GetAnnotationSpecRequest(),
            name="name_value",
        )


def test_list_annotations_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.list_annotations in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.list_annotations] = (
            mock_rpc
        )

        request = {}
        client.list_annotations(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_annotations(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_list_annotations_rest_required_fields(
    request_type=dataset_service.ListAnnotationsRequest,
):
    transport_class = transports.DatasetServiceRestTransport

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
    ).list_annotations._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_annotations._get_unset_required_fields(jsonified_request)
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

    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = dataset_service.ListAnnotationsResponse()
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
            return_value = dataset_service.ListAnnotationsResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.list_annotations(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_list_annotations_rest_unset_required_fields():
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.list_annotations._get_unset_required_fields({})
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


def test_list_annotations_rest_flattened():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset_service.ListAnnotationsResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "parent": "projects/sample1/locations/sample2/datasets/sample3/dataItems/sample4"
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
        return_value = dataset_service.ListAnnotationsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.list_annotations(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{parent=projects/*/locations/*/datasets/*/dataItems/*}/annotations"
            % client.transport._host,
            args[1],
        )


def test_list_annotations_rest_flattened_error(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_annotations(
            dataset_service.ListAnnotationsRequest(),
            parent="parent_value",
        )


def test_list_annotations_rest_pager(transport: str = "rest"):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            dataset_service.ListAnnotationsResponse(
                annotations=[
                    annotation.Annotation(),
                    annotation.Annotation(),
                    annotation.Annotation(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListAnnotationsResponse(
                annotations=[],
                next_page_token="def",
            ),
            dataset_service.ListAnnotationsResponse(
                annotations=[
                    annotation.Annotation(),
                ],
                next_page_token="ghi",
            ),
            dataset_service.ListAnnotationsResponse(
                annotations=[
                    annotation.Annotation(),
                    annotation.Annotation(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(
            dataset_service.ListAnnotationsResponse.to_json(x) for x in response
        )
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {
            "parent": "projects/sample1/locations/sample2/datasets/sample3/dataItems/sample4"
        }

        pager = client.list_annotations(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, annotation.Annotation) for i in results)

        pages = list(client.list_annotations(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_assess_data_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.assess_data in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.assess_data] = mock_rpc

        request = {}
        client.assess_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.assess_data(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_assess_data_rest_required_fields(
    request_type=dataset_service.AssessDataRequest,
):
    transport_class = transports.DatasetServiceRestTransport

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
    ).assess_data._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).assess_data._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = DatasetServiceClient(
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

            response = client.assess_data(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_assess_data_rest_unset_required_fields():
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.assess_data._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


def test_assemble_data_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.assemble_data in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.assemble_data] = mock_rpc

        request = {}
        client.assemble_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.assemble_data(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_assemble_data_rest_required_fields(
    request_type=dataset_service.AssembleDataRequest,
):
    transport_class = transports.DatasetServiceRestTransport

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
    ).assemble_data._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).assemble_data._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = DatasetServiceClient(
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

            response = client.assemble_data(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_assemble_data_rest_unset_required_fields():
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.assemble_data._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.DatasetServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.DatasetServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = DatasetServiceClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide an api_key and a transport instance.
    transport = transports.DatasetServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    options = client_options.ClientOptions()
    options.api_key = "api_key"
    with pytest.raises(ValueError):
        client = DatasetServiceClient(
            client_options=options,
            transport=transport,
        )

    # It is an error to provide an api_key and a credential.
    options = client_options.ClientOptions()
    options.api_key = "api_key"
    with pytest.raises(ValueError):
        client = DatasetServiceClient(
            client_options=options, credentials=ga_credentials.AnonymousCredentials()
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.DatasetServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = DatasetServiceClient(
            client_options={"scopes": ["1", "2"]},
            transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.DatasetServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    client = DatasetServiceClient(transport=transport)
    assert client.transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.DatasetServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.DatasetServiceGrpcAsyncIOTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.DatasetServiceGrpcTransport,
        transports.DatasetServiceGrpcAsyncIOTransport,
        transports.DatasetServiceRestTransport,
    ],
)
def test_transport_adc(transport_class):
    # Test default credentials are used if not provided.
    with mock.patch.object(google.auth, "default") as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport_class()
        adc.assert_called_once()


def test_transport_kind_grpc():
    transport = DatasetServiceClient.get_transport_class("grpc")(
        credentials=ga_credentials.AnonymousCredentials()
    )
    assert transport.kind == "grpc"


def test_initialize_client_w_grpc():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc"
    )
    assert client is not None


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_create_dataset_empty_call_grpc():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.create_dataset), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.create_dataset(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.CreateDatasetRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_dataset_empty_call_grpc():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.get_dataset), "__call__") as call:
        call.return_value = dataset.Dataset()
        client.get_dataset(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.GetDatasetRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_update_dataset_empty_call_grpc():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.update_dataset), "__call__") as call:
        call.return_value = gca_dataset.Dataset()
        client.update_dataset(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.UpdateDatasetRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_datasets_empty_call_grpc():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.list_datasets), "__call__") as call:
        call.return_value = dataset_service.ListDatasetsResponse()
        client.list_datasets(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ListDatasetsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_delete_dataset_empty_call_grpc():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.delete_dataset), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_dataset(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.DeleteDatasetRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_import_data_empty_call_grpc():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.import_data), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.import_data(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ImportDataRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_export_data_empty_call_grpc():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.export_data), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.export_data(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ExportDataRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_create_dataset_version_empty_call_grpc():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.create_dataset_version), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.create_dataset_version(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.CreateDatasetVersionRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_update_dataset_version_empty_call_grpc():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.update_dataset_version), "__call__"
    ) as call:
        call.return_value = gca_dataset_version.DatasetVersion()
        client.update_dataset_version(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.UpdateDatasetVersionRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_delete_dataset_version_empty_call_grpc():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_dataset_version), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_dataset_version(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.DeleteDatasetVersionRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_dataset_version_empty_call_grpc():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.get_dataset_version), "__call__"
    ) as call:
        call.return_value = dataset_version.DatasetVersion()
        client.get_dataset_version(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.GetDatasetVersionRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_dataset_versions_empty_call_grpc():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.list_dataset_versions), "__call__"
    ) as call:
        call.return_value = dataset_service.ListDatasetVersionsResponse()
        client.list_dataset_versions(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ListDatasetVersionsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_restore_dataset_version_empty_call_grpc():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.restore_dataset_version), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.restore_dataset_version(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.RestoreDatasetVersionRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_data_items_empty_call_grpc():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.list_data_items), "__call__") as call:
        call.return_value = dataset_service.ListDataItemsResponse()
        client.list_data_items(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ListDataItemsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_search_data_items_empty_call_grpc():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.search_data_items), "__call__"
    ) as call:
        call.return_value = dataset_service.SearchDataItemsResponse()
        client.search_data_items(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.SearchDataItemsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_saved_queries_empty_call_grpc():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.list_saved_queries), "__call__"
    ) as call:
        call.return_value = dataset_service.ListSavedQueriesResponse()
        client.list_saved_queries(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ListSavedQueriesRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_delete_saved_query_empty_call_grpc():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_saved_query), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_saved_query(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.DeleteSavedQueryRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_annotation_spec_empty_call_grpc():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.get_annotation_spec), "__call__"
    ) as call:
        call.return_value = annotation_spec.AnnotationSpec()
        client.get_annotation_spec(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.GetAnnotationSpecRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_annotations_empty_call_grpc():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.list_annotations), "__call__") as call:
        call.return_value = dataset_service.ListAnnotationsResponse()
        client.list_annotations(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ListAnnotationsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_assess_data_empty_call_grpc():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.assess_data), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.assess_data(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.AssessDataRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_assemble_data_empty_call_grpc():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.assemble_data), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.assemble_data(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.AssembleDataRequest()

        assert args[0] == request_msg


def test_transport_kind_grpc_asyncio():
    transport = DatasetServiceAsyncClient.get_transport_class("grpc_asyncio")(
        credentials=async_anonymous_credentials()
    )
    assert transport.kind == "grpc_asyncio"


def test_initialize_client_w_grpc_asyncio():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="grpc_asyncio"
    )
    assert client is not None


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_create_dataset_empty_call_grpc_asyncio():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.create_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        await client.create_dataset(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.CreateDatasetRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_dataset_empty_call_grpc_asyncio():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.get_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset.Dataset(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
                metadata_schema_uri="metadata_schema_uri_value",
                data_item_count=1584,
                etag="etag_value",
                metadata_artifact="metadata_artifact_value",
                model_reference="model_reference_value",
                satisfies_pzs=True,
                satisfies_pzi=True,
            )
        )
        await client.get_dataset(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.GetDatasetRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_update_dataset_empty_call_grpc_asyncio():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.update_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_dataset.Dataset(
                name="name_value",
                display_name="display_name_value",
                description="description_value",
                metadata_schema_uri="metadata_schema_uri_value",
                data_item_count=1584,
                etag="etag_value",
                metadata_artifact="metadata_artifact_value",
                model_reference="model_reference_value",
                satisfies_pzs=True,
                satisfies_pzi=True,
            )
        )
        await client.update_dataset(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.UpdateDatasetRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_datasets_empty_call_grpc_asyncio():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.list_datasets), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.ListDatasetsResponse(
                next_page_token="next_page_token_value",
            )
        )
        await client.list_datasets(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ListDatasetsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_delete_dataset_empty_call_grpc_asyncio():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.delete_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        await client.delete_dataset(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.DeleteDatasetRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_import_data_empty_call_grpc_asyncio():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.import_data), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        await client.import_data(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ImportDataRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_export_data_empty_call_grpc_asyncio():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.export_data), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        await client.export_data(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ExportDataRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_create_dataset_version_empty_call_grpc_asyncio():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.create_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        await client.create_dataset_version(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.CreateDatasetVersionRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_update_dataset_version_empty_call_grpc_asyncio():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.update_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gca_dataset_version.DatasetVersion(
                name="name_value",
                etag="etag_value",
                big_query_dataset_name="big_query_dataset_name_value",
                display_name="display_name_value",
                model_reference="model_reference_value",
                satisfies_pzs=True,
                satisfies_pzi=True,
            )
        )
        await client.update_dataset_version(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.UpdateDatasetVersionRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_delete_dataset_version_empty_call_grpc_asyncio():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        await client.delete_dataset_version(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.DeleteDatasetVersionRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_dataset_version_empty_call_grpc_asyncio():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.get_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_version.DatasetVersion(
                name="name_value",
                etag="etag_value",
                big_query_dataset_name="big_query_dataset_name_value",
                display_name="display_name_value",
                model_reference="model_reference_value",
                satisfies_pzs=True,
                satisfies_pzi=True,
            )
        )
        await client.get_dataset_version(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.GetDatasetVersionRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_dataset_versions_empty_call_grpc_asyncio():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.list_dataset_versions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.ListDatasetVersionsResponse(
                next_page_token="next_page_token_value",
            )
        )
        await client.list_dataset_versions(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ListDatasetVersionsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_restore_dataset_version_empty_call_grpc_asyncio():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.restore_dataset_version), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        await client.restore_dataset_version(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.RestoreDatasetVersionRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_data_items_empty_call_grpc_asyncio():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.list_data_items), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.ListDataItemsResponse(
                next_page_token="next_page_token_value",
            )
        )
        await client.list_data_items(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ListDataItemsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_search_data_items_empty_call_grpc_asyncio():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.search_data_items), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.SearchDataItemsResponse(
                next_page_token="next_page_token_value",
            )
        )
        await client.search_data_items(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.SearchDataItemsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_saved_queries_empty_call_grpc_asyncio():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.list_saved_queries), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.ListSavedQueriesResponse(
                next_page_token="next_page_token_value",
            )
        )
        await client.list_saved_queries(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ListSavedQueriesRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_delete_saved_query_empty_call_grpc_asyncio():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_saved_query), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        await client.delete_saved_query(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.DeleteSavedQueryRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_annotation_spec_empty_call_grpc_asyncio():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.get_annotation_spec), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            annotation_spec.AnnotationSpec(
                name="name_value",
                display_name="display_name_value",
                etag="etag_value",
            )
        )
        await client.get_annotation_spec(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.GetAnnotationSpecRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_annotations_empty_call_grpc_asyncio():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.list_annotations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            dataset_service.ListAnnotationsResponse(
                next_page_token="next_page_token_value",
            )
        )
        await client.list_annotations(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ListAnnotationsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_assess_data_empty_call_grpc_asyncio():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.assess_data), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        await client.assess_data(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.AssessDataRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_assemble_data_empty_call_grpc_asyncio():
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.assemble_data), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        await client.assemble_data(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.AssembleDataRequest()

        assert args[0] == request_msg


def test_transport_kind_rest():
    transport = DatasetServiceClient.get_transport_class("rest")(
        credentials=ga_credentials.AnonymousCredentials()
    )
    assert transport.kind == "rest"


def test_create_dataset_rest_bad_request(
    request_type=dataset_service.CreateDatasetRequest,
):
    client = DatasetServiceClient(
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
        client.create_dataset(request)


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.CreateDatasetRequest,
        dict,
    ],
)
def test_create_dataset_rest_call_success(request_type):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request_init["dataset"] = {
        "name": "name_value",
        "display_name": "display_name_value",
        "description": "description_value",
        "metadata_schema_uri": "metadata_schema_uri_value",
        "metadata": {
            "null_value": 0,
            "number_value": 0.1285,
            "string_value": "string_value_value",
            "bool_value": True,
            "struct_value": {"fields": {}},
            "list_value": {"values": {}},
        },
        "data_item_count": 1584,
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
        "etag": "etag_value",
        "labels": {},
        "saved_queries": [
            {
                "name": "name_value",
                "display_name": "display_name_value",
                "metadata": {},
                "create_time": {},
                "update_time": {},
                "annotation_filter": "annotation_filter_value",
                "problem_type": "problem_type_value",
                "annotation_spec_count": 2253,
                "etag": "etag_value",
                "support_automl_training": True,
            }
        ],
        "encryption_spec": {"kms_key_name": "kms_key_name_value"},
        "metadata_artifact": "metadata_artifact_value",
        "model_reference": "model_reference_value",
        "satisfies_pzs": True,
        "satisfies_pzi": True,
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = dataset_service.CreateDatasetRequest.meta.fields["dataset"]

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
    for field, value in request_init["dataset"].items():  # pragma: NO COVER
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
                for i in range(0, len(request_init["dataset"][field])):
                    del request_init["dataset"][field][i][subfield]
            else:
                del request_init["dataset"][field][subfield]
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
        response = client.create_dataset(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_create_dataset_rest_interceptors(null_interceptor):
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None if null_interceptor else transports.DatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_create_dataset"
    ) as post, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_create_dataset_with_metadata"
    ) as post_with_metadata, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "pre_create_dataset"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.CreateDatasetRequest.pb(
            dataset_service.CreateDatasetRequest()
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

        request = dataset_service.CreateDatasetRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.create_dataset(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_get_dataset_rest_bad_request(request_type=dataset_service.GetDatasetRequest):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        client.get_dataset(request)


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.GetDatasetRequest,
        dict,
    ],
)
def test_get_dataset_rest_call_success(request_type):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset.Dataset(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            metadata_schema_uri="metadata_schema_uri_value",
            data_item_count=1584,
            etag="etag_value",
            metadata_artifact="metadata_artifact_value",
            model_reference="model_reference_value",
            satisfies_pzs=True,
            satisfies_pzi=True,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = dataset.Dataset.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.get_dataset(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, dataset.Dataset)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.metadata_schema_uri == "metadata_schema_uri_value"
    assert response.data_item_count == 1584
    assert response.etag == "etag_value"
    assert response.metadata_artifact == "metadata_artifact_value"
    assert response.model_reference == "model_reference_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_dataset_rest_interceptors(null_interceptor):
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None if null_interceptor else transports.DatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_get_dataset"
    ) as post, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_get_dataset_with_metadata"
    ) as post_with_metadata, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "pre_get_dataset"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.GetDatasetRequest.pb(
            dataset_service.GetDatasetRequest()
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
        return_value = dataset.Dataset.to_json(dataset.Dataset())
        req.return_value.content = return_value

        request = dataset_service.GetDatasetRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = dataset.Dataset()
        post_with_metadata.return_value = dataset.Dataset(), metadata

        client.get_dataset(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_update_dataset_rest_bad_request(
    request_type=dataset_service.UpdateDatasetRequest,
):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "dataset": {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        client.update_dataset(request)


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.UpdateDatasetRequest,
        dict,
    ],
)
def test_update_dataset_rest_call_success(request_type):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "dataset": {"name": "projects/sample1/locations/sample2/datasets/sample3"}
    }
    request_init["dataset"] = {
        "name": "projects/sample1/locations/sample2/datasets/sample3",
        "display_name": "display_name_value",
        "description": "description_value",
        "metadata_schema_uri": "metadata_schema_uri_value",
        "metadata": {
            "null_value": 0,
            "number_value": 0.1285,
            "string_value": "string_value_value",
            "bool_value": True,
            "struct_value": {"fields": {}},
            "list_value": {"values": {}},
        },
        "data_item_count": 1584,
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
        "etag": "etag_value",
        "labels": {},
        "saved_queries": [
            {
                "name": "name_value",
                "display_name": "display_name_value",
                "metadata": {},
                "create_time": {},
                "update_time": {},
                "annotation_filter": "annotation_filter_value",
                "problem_type": "problem_type_value",
                "annotation_spec_count": 2253,
                "etag": "etag_value",
                "support_automl_training": True,
            }
        ],
        "encryption_spec": {"kms_key_name": "kms_key_name_value"},
        "metadata_artifact": "metadata_artifact_value",
        "model_reference": "model_reference_value",
        "satisfies_pzs": True,
        "satisfies_pzi": True,
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = dataset_service.UpdateDatasetRequest.meta.fields["dataset"]

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
    for field, value in request_init["dataset"].items():  # pragma: NO COVER
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
                for i in range(0, len(request_init["dataset"][field])):
                    del request_init["dataset"][field][i][subfield]
            else:
                del request_init["dataset"][field][subfield]
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gca_dataset.Dataset(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            metadata_schema_uri="metadata_schema_uri_value",
            data_item_count=1584,
            etag="etag_value",
            metadata_artifact="metadata_artifact_value",
            model_reference="model_reference_value",
            satisfies_pzs=True,
            satisfies_pzi=True,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = gca_dataset.Dataset.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.update_dataset(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_dataset.Dataset)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.metadata_schema_uri == "metadata_schema_uri_value"
    assert response.data_item_count == 1584
    assert response.etag == "etag_value"
    assert response.metadata_artifact == "metadata_artifact_value"
    assert response.model_reference == "model_reference_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_update_dataset_rest_interceptors(null_interceptor):
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None if null_interceptor else transports.DatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_update_dataset"
    ) as post, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_update_dataset_with_metadata"
    ) as post_with_metadata, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "pre_update_dataset"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.UpdateDatasetRequest.pb(
            dataset_service.UpdateDatasetRequest()
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
        return_value = gca_dataset.Dataset.to_json(gca_dataset.Dataset())
        req.return_value.content = return_value

        request = dataset_service.UpdateDatasetRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = gca_dataset.Dataset()
        post_with_metadata.return_value = gca_dataset.Dataset(), metadata

        client.update_dataset(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_list_datasets_rest_bad_request(
    request_type=dataset_service.ListDatasetsRequest,
):
    client = DatasetServiceClient(
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
        client.list_datasets(request)


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.ListDatasetsRequest,
        dict,
    ],
)
def test_list_datasets_rest_call_success(request_type):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset_service.ListDatasetsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = dataset_service.ListDatasetsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.list_datasets(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDatasetsPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_datasets_rest_interceptors(null_interceptor):
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None if null_interceptor else transports.DatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_list_datasets"
    ) as post, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_list_datasets_with_metadata"
    ) as post_with_metadata, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "pre_list_datasets"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.ListDatasetsRequest.pb(
            dataset_service.ListDatasetsRequest()
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
        return_value = dataset_service.ListDatasetsResponse.to_json(
            dataset_service.ListDatasetsResponse()
        )
        req.return_value.content = return_value

        request = dataset_service.ListDatasetsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = dataset_service.ListDatasetsResponse()
        post_with_metadata.return_value = (
            dataset_service.ListDatasetsResponse(),
            metadata,
        )

        client.list_datasets(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_delete_dataset_rest_bad_request(
    request_type=dataset_service.DeleteDatasetRequest,
):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        client.delete_dataset(request)


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.DeleteDatasetRequest,
        dict,
    ],
)
def test_delete_dataset_rest_call_success(request_type):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        response = client.delete_dataset(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_delete_dataset_rest_interceptors(null_interceptor):
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None if null_interceptor else transports.DatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_delete_dataset"
    ) as post, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_delete_dataset_with_metadata"
    ) as post_with_metadata, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "pre_delete_dataset"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.DeleteDatasetRequest.pb(
            dataset_service.DeleteDatasetRequest()
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

        request = dataset_service.DeleteDatasetRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.delete_dataset(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_import_data_rest_bad_request(request_type=dataset_service.ImportDataRequest):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        client.import_data(request)


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.ImportDataRequest,
        dict,
    ],
)
def test_import_data_rest_call_success(request_type):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        response = client.import_data(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_import_data_rest_interceptors(null_interceptor):
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None if null_interceptor else transports.DatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_import_data"
    ) as post, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_import_data_with_metadata"
    ) as post_with_metadata, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "pre_import_data"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.ImportDataRequest.pb(
            dataset_service.ImportDataRequest()
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

        request = dataset_service.ImportDataRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.import_data(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_export_data_rest_bad_request(request_type=dataset_service.ExportDataRequest):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        client.export_data(request)


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.ExportDataRequest,
        dict,
    ],
)
def test_export_data_rest_call_success(request_type):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        response = client.export_data(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_export_data_rest_interceptors(null_interceptor):
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None if null_interceptor else transports.DatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_export_data"
    ) as post, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_export_data_with_metadata"
    ) as post_with_metadata, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "pre_export_data"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.ExportDataRequest.pb(
            dataset_service.ExportDataRequest()
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

        request = dataset_service.ExportDataRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.export_data(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_create_dataset_version_rest_bad_request(
    request_type=dataset_service.CreateDatasetVersionRequest,
):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/datasets/sample3"}
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
        client.create_dataset_version(request)


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.CreateDatasetVersionRequest,
        dict,
    ],
)
def test_create_dataset_version_rest_call_success(request_type):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/datasets/sample3"}
    request_init["dataset_version"] = {
        "name": "name_value",
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
        "etag": "etag_value",
        "big_query_dataset_name": "big_query_dataset_name_value",
        "display_name": "display_name_value",
        "metadata": {
            "null_value": 0,
            "number_value": 0.1285,
            "string_value": "string_value_value",
            "bool_value": True,
            "struct_value": {"fields": {}},
            "list_value": {"values": {}},
        },
        "model_reference": "model_reference_value",
        "satisfies_pzs": True,
        "satisfies_pzi": True,
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = dataset_service.CreateDatasetVersionRequest.meta.fields[
        "dataset_version"
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
    for field, value in request_init["dataset_version"].items():  # pragma: NO COVER
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
                for i in range(0, len(request_init["dataset_version"][field])):
                    del request_init["dataset_version"][field][i][subfield]
            else:
                del request_init["dataset_version"][field][subfield]
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
        response = client.create_dataset_version(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_create_dataset_version_rest_interceptors(null_interceptor):
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None if null_interceptor else transports.DatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_create_dataset_version"
    ) as post, mock.patch.object(
        transports.DatasetServiceRestInterceptor,
        "post_create_dataset_version_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "pre_create_dataset_version"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.CreateDatasetVersionRequest.pb(
            dataset_service.CreateDatasetVersionRequest()
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

        request = dataset_service.CreateDatasetVersionRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.create_dataset_version(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_update_dataset_version_rest_bad_request(
    request_type=dataset_service.UpdateDatasetVersionRequest,
):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "dataset_version": {
            "name": "projects/sample1/locations/sample2/datasets/sample3/datasetVersions/sample4"
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
        client.update_dataset_version(request)


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.UpdateDatasetVersionRequest,
        dict,
    ],
)
def test_update_dataset_version_rest_call_success(request_type):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "dataset_version": {
            "name": "projects/sample1/locations/sample2/datasets/sample3/datasetVersions/sample4"
        }
    }
    request_init["dataset_version"] = {
        "name": "projects/sample1/locations/sample2/datasets/sample3/datasetVersions/sample4",
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
        "etag": "etag_value",
        "big_query_dataset_name": "big_query_dataset_name_value",
        "display_name": "display_name_value",
        "metadata": {
            "null_value": 0,
            "number_value": 0.1285,
            "string_value": "string_value_value",
            "bool_value": True,
            "struct_value": {"fields": {}},
            "list_value": {"values": {}},
        },
        "model_reference": "model_reference_value",
        "satisfies_pzs": True,
        "satisfies_pzi": True,
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = dataset_service.UpdateDatasetVersionRequest.meta.fields[
        "dataset_version"
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
    for field, value in request_init["dataset_version"].items():  # pragma: NO COVER
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
                for i in range(0, len(request_init["dataset_version"][field])):
                    del request_init["dataset_version"][field][i][subfield]
            else:
                del request_init["dataset_version"][field][subfield]
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gca_dataset_version.DatasetVersion(
            name="name_value",
            etag="etag_value",
            big_query_dataset_name="big_query_dataset_name_value",
            display_name="display_name_value",
            model_reference="model_reference_value",
            satisfies_pzs=True,
            satisfies_pzi=True,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = gca_dataset_version.DatasetVersion.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.update_dataset_version(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_dataset_version.DatasetVersion)
    assert response.name == "name_value"
    assert response.etag == "etag_value"
    assert response.big_query_dataset_name == "big_query_dataset_name_value"
    assert response.display_name == "display_name_value"
    assert response.model_reference == "model_reference_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_update_dataset_version_rest_interceptors(null_interceptor):
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None if null_interceptor else transports.DatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_update_dataset_version"
    ) as post, mock.patch.object(
        transports.DatasetServiceRestInterceptor,
        "post_update_dataset_version_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "pre_update_dataset_version"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.UpdateDatasetVersionRequest.pb(
            dataset_service.UpdateDatasetVersionRequest()
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
        return_value = gca_dataset_version.DatasetVersion.to_json(
            gca_dataset_version.DatasetVersion()
        )
        req.return_value.content = return_value

        request = dataset_service.UpdateDatasetVersionRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = gca_dataset_version.DatasetVersion()
        post_with_metadata.return_value = gca_dataset_version.DatasetVersion(), metadata

        client.update_dataset_version(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_delete_dataset_version_rest_bad_request(
    request_type=dataset_service.DeleteDatasetVersionRequest,
):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/datasets/sample3/datasetVersions/sample4"
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
        client.delete_dataset_version(request)


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.DeleteDatasetVersionRequest,
        dict,
    ],
)
def test_delete_dataset_version_rest_call_success(request_type):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/datasets/sample3/datasetVersions/sample4"
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
        response = client.delete_dataset_version(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_delete_dataset_version_rest_interceptors(null_interceptor):
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None if null_interceptor else transports.DatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_delete_dataset_version"
    ) as post, mock.patch.object(
        transports.DatasetServiceRestInterceptor,
        "post_delete_dataset_version_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "pre_delete_dataset_version"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.DeleteDatasetVersionRequest.pb(
            dataset_service.DeleteDatasetVersionRequest()
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

        request = dataset_service.DeleteDatasetVersionRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.delete_dataset_version(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_get_dataset_version_rest_bad_request(
    request_type=dataset_service.GetDatasetVersionRequest,
):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/datasets/sample3/datasetVersions/sample4"
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
        client.get_dataset_version(request)


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.GetDatasetVersionRequest,
        dict,
    ],
)
def test_get_dataset_version_rest_call_success(request_type):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/datasets/sample3/datasetVersions/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset_version.DatasetVersion(
            name="name_value",
            etag="etag_value",
            big_query_dataset_name="big_query_dataset_name_value",
            display_name="display_name_value",
            model_reference="model_reference_value",
            satisfies_pzs=True,
            satisfies_pzi=True,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = dataset_version.DatasetVersion.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.get_dataset_version(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, dataset_version.DatasetVersion)
    assert response.name == "name_value"
    assert response.etag == "etag_value"
    assert response.big_query_dataset_name == "big_query_dataset_name_value"
    assert response.display_name == "display_name_value"
    assert response.model_reference == "model_reference_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_dataset_version_rest_interceptors(null_interceptor):
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None if null_interceptor else transports.DatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_get_dataset_version"
    ) as post, mock.patch.object(
        transports.DatasetServiceRestInterceptor,
        "post_get_dataset_version_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "pre_get_dataset_version"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.GetDatasetVersionRequest.pb(
            dataset_service.GetDatasetVersionRequest()
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
        return_value = dataset_version.DatasetVersion.to_json(
            dataset_version.DatasetVersion()
        )
        req.return_value.content = return_value

        request = dataset_service.GetDatasetVersionRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = dataset_version.DatasetVersion()
        post_with_metadata.return_value = dataset_version.DatasetVersion(), metadata

        client.get_dataset_version(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_list_dataset_versions_rest_bad_request(
    request_type=dataset_service.ListDatasetVersionsRequest,
):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/datasets/sample3"}
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
        client.list_dataset_versions(request)


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.ListDatasetVersionsRequest,
        dict,
    ],
)
def test_list_dataset_versions_rest_call_success(request_type):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/datasets/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset_service.ListDatasetVersionsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = dataset_service.ListDatasetVersionsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.list_dataset_versions(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDatasetVersionsPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_dataset_versions_rest_interceptors(null_interceptor):
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None if null_interceptor else transports.DatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_list_dataset_versions"
    ) as post, mock.patch.object(
        transports.DatasetServiceRestInterceptor,
        "post_list_dataset_versions_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "pre_list_dataset_versions"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.ListDatasetVersionsRequest.pb(
            dataset_service.ListDatasetVersionsRequest()
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
        return_value = dataset_service.ListDatasetVersionsResponse.to_json(
            dataset_service.ListDatasetVersionsResponse()
        )
        req.return_value.content = return_value

        request = dataset_service.ListDatasetVersionsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = dataset_service.ListDatasetVersionsResponse()
        post_with_metadata.return_value = (
            dataset_service.ListDatasetVersionsResponse(),
            metadata,
        )

        client.list_dataset_versions(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_restore_dataset_version_rest_bad_request(
    request_type=dataset_service.RestoreDatasetVersionRequest,
):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/datasets/sample3/datasetVersions/sample4"
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
        client.restore_dataset_version(request)


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.RestoreDatasetVersionRequest,
        dict,
    ],
)
def test_restore_dataset_version_rest_call_success(request_type):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/datasets/sample3/datasetVersions/sample4"
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
        response = client.restore_dataset_version(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_restore_dataset_version_rest_interceptors(null_interceptor):
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None if null_interceptor else transports.DatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_restore_dataset_version"
    ) as post, mock.patch.object(
        transports.DatasetServiceRestInterceptor,
        "post_restore_dataset_version_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "pre_restore_dataset_version"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.RestoreDatasetVersionRequest.pb(
            dataset_service.RestoreDatasetVersionRequest()
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

        request = dataset_service.RestoreDatasetVersionRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.restore_dataset_version(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_list_data_items_rest_bad_request(
    request_type=dataset_service.ListDataItemsRequest,
):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/datasets/sample3"}
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
        client.list_data_items(request)


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.ListDataItemsRequest,
        dict,
    ],
)
def test_list_data_items_rest_call_success(request_type):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/datasets/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset_service.ListDataItemsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = dataset_service.ListDataItemsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.list_data_items(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDataItemsPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_data_items_rest_interceptors(null_interceptor):
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None if null_interceptor else transports.DatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_list_data_items"
    ) as post, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_list_data_items_with_metadata"
    ) as post_with_metadata, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "pre_list_data_items"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.ListDataItemsRequest.pb(
            dataset_service.ListDataItemsRequest()
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
        return_value = dataset_service.ListDataItemsResponse.to_json(
            dataset_service.ListDataItemsResponse()
        )
        req.return_value.content = return_value

        request = dataset_service.ListDataItemsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = dataset_service.ListDataItemsResponse()
        post_with_metadata.return_value = (
            dataset_service.ListDataItemsResponse(),
            metadata,
        )

        client.list_data_items(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_search_data_items_rest_bad_request(
    request_type=dataset_service.SearchDataItemsRequest,
):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {"dataset": "projects/sample1/locations/sample2/datasets/sample3"}
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
        client.search_data_items(request)


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.SearchDataItemsRequest,
        dict,
    ],
)
def test_search_data_items_rest_call_success(request_type):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"dataset": "projects/sample1/locations/sample2/datasets/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset_service.SearchDataItemsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = dataset_service.SearchDataItemsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.search_data_items(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.SearchDataItemsPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_search_data_items_rest_interceptors(null_interceptor):
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None if null_interceptor else transports.DatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_search_data_items"
    ) as post, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_search_data_items_with_metadata"
    ) as post_with_metadata, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "pre_search_data_items"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.SearchDataItemsRequest.pb(
            dataset_service.SearchDataItemsRequest()
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
        return_value = dataset_service.SearchDataItemsResponse.to_json(
            dataset_service.SearchDataItemsResponse()
        )
        req.return_value.content = return_value

        request = dataset_service.SearchDataItemsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = dataset_service.SearchDataItemsResponse()
        post_with_metadata.return_value = (
            dataset_service.SearchDataItemsResponse(),
            metadata,
        )

        client.search_data_items(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_list_saved_queries_rest_bad_request(
    request_type=dataset_service.ListSavedQueriesRequest,
):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/datasets/sample3"}
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
        client.list_saved_queries(request)


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.ListSavedQueriesRequest,
        dict,
    ],
)
def test_list_saved_queries_rest_call_success(request_type):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/datasets/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset_service.ListSavedQueriesResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = dataset_service.ListSavedQueriesResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.list_saved_queries(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListSavedQueriesPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_saved_queries_rest_interceptors(null_interceptor):
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None if null_interceptor else transports.DatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_list_saved_queries"
    ) as post, mock.patch.object(
        transports.DatasetServiceRestInterceptor,
        "post_list_saved_queries_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "pre_list_saved_queries"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.ListSavedQueriesRequest.pb(
            dataset_service.ListSavedQueriesRequest()
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
        return_value = dataset_service.ListSavedQueriesResponse.to_json(
            dataset_service.ListSavedQueriesResponse()
        )
        req.return_value.content = return_value

        request = dataset_service.ListSavedQueriesRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = dataset_service.ListSavedQueriesResponse()
        post_with_metadata.return_value = (
            dataset_service.ListSavedQueriesResponse(),
            metadata,
        )

        client.list_saved_queries(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_delete_saved_query_rest_bad_request(
    request_type=dataset_service.DeleteSavedQueryRequest,
):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/datasets/sample3/savedQueries/sample4"
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
        client.delete_saved_query(request)


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.DeleteSavedQueryRequest,
        dict,
    ],
)
def test_delete_saved_query_rest_call_success(request_type):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/datasets/sample3/savedQueries/sample4"
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
        response = client.delete_saved_query(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_delete_saved_query_rest_interceptors(null_interceptor):
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None if null_interceptor else transports.DatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_delete_saved_query"
    ) as post, mock.patch.object(
        transports.DatasetServiceRestInterceptor,
        "post_delete_saved_query_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "pre_delete_saved_query"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.DeleteSavedQueryRequest.pb(
            dataset_service.DeleteSavedQueryRequest()
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

        request = dataset_service.DeleteSavedQueryRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.delete_saved_query(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_get_annotation_spec_rest_bad_request(
    request_type=dataset_service.GetAnnotationSpecRequest,
):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/datasets/sample3/annotationSpecs/sample4"
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
        client.get_annotation_spec(request)


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.GetAnnotationSpecRequest,
        dict,
    ],
)
def test_get_annotation_spec_rest_call_success(request_type):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/datasets/sample3/annotationSpecs/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = annotation_spec.AnnotationSpec(
            name="name_value",
            display_name="display_name_value",
            etag="etag_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = annotation_spec.AnnotationSpec.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.get_annotation_spec(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, annotation_spec.AnnotationSpec)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.etag == "etag_value"


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_annotation_spec_rest_interceptors(null_interceptor):
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None if null_interceptor else transports.DatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_get_annotation_spec"
    ) as post, mock.patch.object(
        transports.DatasetServiceRestInterceptor,
        "post_get_annotation_spec_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "pre_get_annotation_spec"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.GetAnnotationSpecRequest.pb(
            dataset_service.GetAnnotationSpecRequest()
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
        return_value = annotation_spec.AnnotationSpec.to_json(
            annotation_spec.AnnotationSpec()
        )
        req.return_value.content = return_value

        request = dataset_service.GetAnnotationSpecRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = annotation_spec.AnnotationSpec()
        post_with_metadata.return_value = annotation_spec.AnnotationSpec(), metadata

        client.get_annotation_spec(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_list_annotations_rest_bad_request(
    request_type=dataset_service.ListAnnotationsRequest,
):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "parent": "projects/sample1/locations/sample2/datasets/sample3/dataItems/sample4"
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
        client.list_annotations(request)


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.ListAnnotationsRequest,
        dict,
    ],
)
def test_list_annotations_rest_call_success(request_type):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "parent": "projects/sample1/locations/sample2/datasets/sample3/dataItems/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset_service.ListAnnotationsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = dataset_service.ListAnnotationsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.list_annotations(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListAnnotationsPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_annotations_rest_interceptors(null_interceptor):
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None if null_interceptor else transports.DatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_list_annotations"
    ) as post, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_list_annotations_with_metadata"
    ) as post_with_metadata, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "pre_list_annotations"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.ListAnnotationsRequest.pb(
            dataset_service.ListAnnotationsRequest()
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
        return_value = dataset_service.ListAnnotationsResponse.to_json(
            dataset_service.ListAnnotationsResponse()
        )
        req.return_value.content = return_value

        request = dataset_service.ListAnnotationsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = dataset_service.ListAnnotationsResponse()
        post_with_metadata.return_value = (
            dataset_service.ListAnnotationsResponse(),
            metadata,
        )

        client.list_annotations(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_assess_data_rest_bad_request(request_type=dataset_service.AssessDataRequest):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        client.assess_data(request)


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.AssessDataRequest,
        dict,
    ],
)
def test_assess_data_rest_call_success(request_type):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        response = client.assess_data(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_assess_data_rest_interceptors(null_interceptor):
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None if null_interceptor else transports.DatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_assess_data"
    ) as post, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_assess_data_with_metadata"
    ) as post_with_metadata, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "pre_assess_data"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.AssessDataRequest.pb(
            dataset_service.AssessDataRequest()
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

        request = dataset_service.AssessDataRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.assess_data(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_assemble_data_rest_bad_request(
    request_type=dataset_service.AssembleDataRequest,
):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        client.assemble_data(request)


@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.AssembleDataRequest,
        dict,
    ],
)
def test_assemble_data_rest_call_success(request_type):
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        response = client.assemble_data(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_assemble_data_rest_interceptors(null_interceptor):
    transport = transports.DatasetServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None if null_interceptor else transports.DatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_assemble_data"
    ) as post, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "post_assemble_data_with_metadata"
    ) as post_with_metadata, mock.patch.object(
        transports.DatasetServiceRestInterceptor, "pre_assemble_data"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.AssembleDataRequest.pb(
            dataset_service.AssembleDataRequest()
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

        request = dataset_service.AssembleDataRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.assemble_data(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    assert client is not None


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_create_dataset_empty_call_rest():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.create_dataset), "__call__") as call:
        client.create_dataset(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.CreateDatasetRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_dataset_empty_call_rest():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.get_dataset), "__call__") as call:
        client.get_dataset(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.GetDatasetRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_update_dataset_empty_call_rest():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.update_dataset), "__call__") as call:
        client.update_dataset(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.UpdateDatasetRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_datasets_empty_call_rest():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.list_datasets), "__call__") as call:
        client.list_datasets(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ListDatasetsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_delete_dataset_empty_call_rest():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.delete_dataset), "__call__") as call:
        client.delete_dataset(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.DeleteDatasetRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_import_data_empty_call_rest():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.import_data), "__call__") as call:
        client.import_data(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ImportDataRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_export_data_empty_call_rest():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.export_data), "__call__") as call:
        client.export_data(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ExportDataRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_create_dataset_version_empty_call_rest():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.create_dataset_version), "__call__"
    ) as call:
        client.create_dataset_version(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.CreateDatasetVersionRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_update_dataset_version_empty_call_rest():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.update_dataset_version), "__call__"
    ) as call:
        client.update_dataset_version(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.UpdateDatasetVersionRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_delete_dataset_version_empty_call_rest():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_dataset_version), "__call__"
    ) as call:
        client.delete_dataset_version(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.DeleteDatasetVersionRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_dataset_version_empty_call_rest():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.get_dataset_version), "__call__"
    ) as call:
        client.get_dataset_version(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.GetDatasetVersionRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_dataset_versions_empty_call_rest():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.list_dataset_versions), "__call__"
    ) as call:
        client.list_dataset_versions(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ListDatasetVersionsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_restore_dataset_version_empty_call_rest():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.restore_dataset_version), "__call__"
    ) as call:
        client.restore_dataset_version(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.RestoreDatasetVersionRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_data_items_empty_call_rest():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.list_data_items), "__call__") as call:
        client.list_data_items(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ListDataItemsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_search_data_items_empty_call_rest():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.search_data_items), "__call__"
    ) as call:
        client.search_data_items(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.SearchDataItemsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_saved_queries_empty_call_rest():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.list_saved_queries), "__call__"
    ) as call:
        client.list_saved_queries(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ListSavedQueriesRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_delete_saved_query_empty_call_rest():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_saved_query), "__call__"
    ) as call:
        client.delete_saved_query(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.DeleteSavedQueryRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_annotation_spec_empty_call_rest():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.get_annotation_spec), "__call__"
    ) as call:
        client.get_annotation_spec(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.GetAnnotationSpecRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_annotations_empty_call_rest():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.list_annotations), "__call__") as call:
        client.list_annotations(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ListAnnotationsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_assess_data_empty_call_rest():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.assess_data), "__call__") as call:
        client.assess_data(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.AssessDataRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_assemble_data_empty_call_rest():
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.assemble_data), "__call__") as call:
        client.assemble_data(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.AssembleDataRequest()

        assert args[0] == request_msg


def test_dataset_service_rest_lro_client():
    client = DatasetServiceClient(
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
    transport = DatasetServiceAsyncClient.get_transport_class("rest_asyncio")(
        credentials=async_anonymous_credentials()
    )
    assert transport.kind == "rest_asyncio"


@pytest.mark.asyncio
async def test_create_dataset_rest_asyncio_bad_request(
    request_type=dataset_service.CreateDatasetRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
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
        await client.create_dataset(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.CreateDatasetRequest,
        dict,
    ],
)
async def test_create_dataset_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request_init["dataset"] = {
        "name": "name_value",
        "display_name": "display_name_value",
        "description": "description_value",
        "metadata_schema_uri": "metadata_schema_uri_value",
        "metadata": {
            "null_value": 0,
            "number_value": 0.1285,
            "string_value": "string_value_value",
            "bool_value": True,
            "struct_value": {"fields": {}},
            "list_value": {"values": {}},
        },
        "data_item_count": 1584,
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
        "etag": "etag_value",
        "labels": {},
        "saved_queries": [
            {
                "name": "name_value",
                "display_name": "display_name_value",
                "metadata": {},
                "create_time": {},
                "update_time": {},
                "annotation_filter": "annotation_filter_value",
                "problem_type": "problem_type_value",
                "annotation_spec_count": 2253,
                "etag": "etag_value",
                "support_automl_training": True,
            }
        ],
        "encryption_spec": {"kms_key_name": "kms_key_name_value"},
        "metadata_artifact": "metadata_artifact_value",
        "model_reference": "model_reference_value",
        "satisfies_pzs": True,
        "satisfies_pzi": True,
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = dataset_service.CreateDatasetRequest.meta.fields["dataset"]

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
    for field, value in request_init["dataset"].items():  # pragma: NO COVER
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
                for i in range(0, len(request_init["dataset"][field])):
                    del request_init["dataset"][field][i][subfield]
            else:
                del request_init["dataset"][field][subfield]
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
        response = await client.create_dataset(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_create_dataset_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncDatasetServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncDatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_create_dataset"
    ) as post, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor,
        "post_create_dataset_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "pre_create_dataset"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.CreateDatasetRequest.pb(
            dataset_service.CreateDatasetRequest()
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

        request = dataset_service.CreateDatasetRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.create_dataset(
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
async def test_get_dataset_rest_asyncio_bad_request(
    request_type=dataset_service.GetDatasetRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        await client.get_dataset(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.GetDatasetRequest,
        dict,
    ],
)
async def test_get_dataset_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset.Dataset(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            metadata_schema_uri="metadata_schema_uri_value",
            data_item_count=1584,
            etag="etag_value",
            metadata_artifact="metadata_artifact_value",
            model_reference="model_reference_value",
            satisfies_pzs=True,
            satisfies_pzi=True,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = dataset.Dataset.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.get_dataset(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, dataset.Dataset)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.metadata_schema_uri == "metadata_schema_uri_value"
    assert response.data_item_count == 1584
    assert response.etag == "etag_value"
    assert response.metadata_artifact == "metadata_artifact_value"
    assert response.model_reference == "model_reference_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_get_dataset_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncDatasetServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncDatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_get_dataset"
    ) as post, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_get_dataset_with_metadata"
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "pre_get_dataset"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.GetDatasetRequest.pb(
            dataset_service.GetDatasetRequest()
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
        return_value = dataset.Dataset.to_json(dataset.Dataset())
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = dataset_service.GetDatasetRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = dataset.Dataset()
        post_with_metadata.return_value = dataset.Dataset(), metadata

        await client.get_dataset(
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
async def test_update_dataset_rest_asyncio_bad_request(
    request_type=dataset_service.UpdateDatasetRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "dataset": {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        await client.update_dataset(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.UpdateDatasetRequest,
        dict,
    ],
)
async def test_update_dataset_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "dataset": {"name": "projects/sample1/locations/sample2/datasets/sample3"}
    }
    request_init["dataset"] = {
        "name": "projects/sample1/locations/sample2/datasets/sample3",
        "display_name": "display_name_value",
        "description": "description_value",
        "metadata_schema_uri": "metadata_schema_uri_value",
        "metadata": {
            "null_value": 0,
            "number_value": 0.1285,
            "string_value": "string_value_value",
            "bool_value": True,
            "struct_value": {"fields": {}},
            "list_value": {"values": {}},
        },
        "data_item_count": 1584,
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
        "etag": "etag_value",
        "labels": {},
        "saved_queries": [
            {
                "name": "name_value",
                "display_name": "display_name_value",
                "metadata": {},
                "create_time": {},
                "update_time": {},
                "annotation_filter": "annotation_filter_value",
                "problem_type": "problem_type_value",
                "annotation_spec_count": 2253,
                "etag": "etag_value",
                "support_automl_training": True,
            }
        ],
        "encryption_spec": {"kms_key_name": "kms_key_name_value"},
        "metadata_artifact": "metadata_artifact_value",
        "model_reference": "model_reference_value",
        "satisfies_pzs": True,
        "satisfies_pzi": True,
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = dataset_service.UpdateDatasetRequest.meta.fields["dataset"]

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
    for field, value in request_init["dataset"].items():  # pragma: NO COVER
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
                for i in range(0, len(request_init["dataset"][field])):
                    del request_init["dataset"][field][i][subfield]
            else:
                del request_init["dataset"][field][subfield]
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gca_dataset.Dataset(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            metadata_schema_uri="metadata_schema_uri_value",
            data_item_count=1584,
            etag="etag_value",
            metadata_artifact="metadata_artifact_value",
            model_reference="model_reference_value",
            satisfies_pzs=True,
            satisfies_pzi=True,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = gca_dataset.Dataset.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.update_dataset(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_dataset.Dataset)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.metadata_schema_uri == "metadata_schema_uri_value"
    assert response.data_item_count == 1584
    assert response.etag == "etag_value"
    assert response.metadata_artifact == "metadata_artifact_value"
    assert response.model_reference == "model_reference_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_update_dataset_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncDatasetServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncDatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_update_dataset"
    ) as post, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor,
        "post_update_dataset_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "pre_update_dataset"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.UpdateDatasetRequest.pb(
            dataset_service.UpdateDatasetRequest()
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
        return_value = gca_dataset.Dataset.to_json(gca_dataset.Dataset())
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = dataset_service.UpdateDatasetRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = gca_dataset.Dataset()
        post_with_metadata.return_value = gca_dataset.Dataset(), metadata

        await client.update_dataset(
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
async def test_list_datasets_rest_asyncio_bad_request(
    request_type=dataset_service.ListDatasetsRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
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
        await client.list_datasets(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.ListDatasetsRequest,
        dict,
    ],
)
async def test_list_datasets_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset_service.ListDatasetsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = dataset_service.ListDatasetsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.list_datasets(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDatasetsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_list_datasets_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncDatasetServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncDatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_list_datasets"
    ) as post, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor,
        "post_list_datasets_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "pre_list_datasets"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.ListDatasetsRequest.pb(
            dataset_service.ListDatasetsRequest()
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
        return_value = dataset_service.ListDatasetsResponse.to_json(
            dataset_service.ListDatasetsResponse()
        )
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = dataset_service.ListDatasetsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = dataset_service.ListDatasetsResponse()
        post_with_metadata.return_value = (
            dataset_service.ListDatasetsResponse(),
            metadata,
        )

        await client.list_datasets(
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
async def test_delete_dataset_rest_asyncio_bad_request(
    request_type=dataset_service.DeleteDatasetRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        await client.delete_dataset(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.DeleteDatasetRequest,
        dict,
    ],
)
async def test_delete_dataset_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        response = await client.delete_dataset(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_delete_dataset_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncDatasetServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncDatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_delete_dataset"
    ) as post, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor,
        "post_delete_dataset_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "pre_delete_dataset"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.DeleteDatasetRequest.pb(
            dataset_service.DeleteDatasetRequest()
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

        request = dataset_service.DeleteDatasetRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.delete_dataset(
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
async def test_import_data_rest_asyncio_bad_request(
    request_type=dataset_service.ImportDataRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        await client.import_data(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.ImportDataRequest,
        dict,
    ],
)
async def test_import_data_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        response = await client.import_data(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_import_data_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncDatasetServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncDatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_import_data"
    ) as post, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_import_data_with_metadata"
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "pre_import_data"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.ImportDataRequest.pb(
            dataset_service.ImportDataRequest()
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

        request = dataset_service.ImportDataRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.import_data(
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
async def test_export_data_rest_asyncio_bad_request(
    request_type=dataset_service.ExportDataRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        await client.export_data(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.ExportDataRequest,
        dict,
    ],
)
async def test_export_data_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        response = await client.export_data(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_export_data_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncDatasetServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncDatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_export_data"
    ) as post, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_export_data_with_metadata"
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "pre_export_data"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.ExportDataRequest.pb(
            dataset_service.ExportDataRequest()
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

        request = dataset_service.ExportDataRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.export_data(
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
async def test_create_dataset_version_rest_asyncio_bad_request(
    request_type=dataset_service.CreateDatasetVersionRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/datasets/sample3"}
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
        await client.create_dataset_version(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.CreateDatasetVersionRequest,
        dict,
    ],
)
async def test_create_dataset_version_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/datasets/sample3"}
    request_init["dataset_version"] = {
        "name": "name_value",
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
        "etag": "etag_value",
        "big_query_dataset_name": "big_query_dataset_name_value",
        "display_name": "display_name_value",
        "metadata": {
            "null_value": 0,
            "number_value": 0.1285,
            "string_value": "string_value_value",
            "bool_value": True,
            "struct_value": {"fields": {}},
            "list_value": {"values": {}},
        },
        "model_reference": "model_reference_value",
        "satisfies_pzs": True,
        "satisfies_pzi": True,
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = dataset_service.CreateDatasetVersionRequest.meta.fields[
        "dataset_version"
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
    for field, value in request_init["dataset_version"].items():  # pragma: NO COVER
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
                for i in range(0, len(request_init["dataset_version"][field])):
                    del request_init["dataset_version"][field][i][subfield]
            else:
                del request_init["dataset_version"][field][subfield]
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
        response = await client.create_dataset_version(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_create_dataset_version_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncDatasetServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncDatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_create_dataset_version"
    ) as post, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor,
        "post_create_dataset_version_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "pre_create_dataset_version"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.CreateDatasetVersionRequest.pb(
            dataset_service.CreateDatasetVersionRequest()
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

        request = dataset_service.CreateDatasetVersionRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.create_dataset_version(
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
async def test_update_dataset_version_rest_asyncio_bad_request(
    request_type=dataset_service.UpdateDatasetVersionRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "dataset_version": {
            "name": "projects/sample1/locations/sample2/datasets/sample3/datasetVersions/sample4"
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
        await client.update_dataset_version(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.UpdateDatasetVersionRequest,
        dict,
    ],
)
async def test_update_dataset_version_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "dataset_version": {
            "name": "projects/sample1/locations/sample2/datasets/sample3/datasetVersions/sample4"
        }
    }
    request_init["dataset_version"] = {
        "name": "projects/sample1/locations/sample2/datasets/sample3/datasetVersions/sample4",
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
        "etag": "etag_value",
        "big_query_dataset_name": "big_query_dataset_name_value",
        "display_name": "display_name_value",
        "metadata": {
            "null_value": 0,
            "number_value": 0.1285,
            "string_value": "string_value_value",
            "bool_value": True,
            "struct_value": {"fields": {}},
            "list_value": {"values": {}},
        },
        "model_reference": "model_reference_value",
        "satisfies_pzs": True,
        "satisfies_pzi": True,
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = dataset_service.UpdateDatasetVersionRequest.meta.fields[
        "dataset_version"
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
    for field, value in request_init["dataset_version"].items():  # pragma: NO COVER
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
                for i in range(0, len(request_init["dataset_version"][field])):
                    del request_init["dataset_version"][field][i][subfield]
            else:
                del request_init["dataset_version"][field][subfield]
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gca_dataset_version.DatasetVersion(
            name="name_value",
            etag="etag_value",
            big_query_dataset_name="big_query_dataset_name_value",
            display_name="display_name_value",
            model_reference="model_reference_value",
            satisfies_pzs=True,
            satisfies_pzi=True,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = gca_dataset_version.DatasetVersion.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.update_dataset_version(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_dataset_version.DatasetVersion)
    assert response.name == "name_value"
    assert response.etag == "etag_value"
    assert response.big_query_dataset_name == "big_query_dataset_name_value"
    assert response.display_name == "display_name_value"
    assert response.model_reference == "model_reference_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_update_dataset_version_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncDatasetServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncDatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_update_dataset_version"
    ) as post, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor,
        "post_update_dataset_version_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "pre_update_dataset_version"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.UpdateDatasetVersionRequest.pb(
            dataset_service.UpdateDatasetVersionRequest()
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
        return_value = gca_dataset_version.DatasetVersion.to_json(
            gca_dataset_version.DatasetVersion()
        )
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = dataset_service.UpdateDatasetVersionRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = gca_dataset_version.DatasetVersion()
        post_with_metadata.return_value = gca_dataset_version.DatasetVersion(), metadata

        await client.update_dataset_version(
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
async def test_delete_dataset_version_rest_asyncio_bad_request(
    request_type=dataset_service.DeleteDatasetVersionRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/datasets/sample3/datasetVersions/sample4"
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
        await client.delete_dataset_version(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.DeleteDatasetVersionRequest,
        dict,
    ],
)
async def test_delete_dataset_version_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/datasets/sample3/datasetVersions/sample4"
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
        response = await client.delete_dataset_version(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_delete_dataset_version_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncDatasetServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncDatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_delete_dataset_version"
    ) as post, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor,
        "post_delete_dataset_version_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "pre_delete_dataset_version"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.DeleteDatasetVersionRequest.pb(
            dataset_service.DeleteDatasetVersionRequest()
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

        request = dataset_service.DeleteDatasetVersionRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.delete_dataset_version(
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
async def test_get_dataset_version_rest_asyncio_bad_request(
    request_type=dataset_service.GetDatasetVersionRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/datasets/sample3/datasetVersions/sample4"
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
        await client.get_dataset_version(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.GetDatasetVersionRequest,
        dict,
    ],
)
async def test_get_dataset_version_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/datasets/sample3/datasetVersions/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset_version.DatasetVersion(
            name="name_value",
            etag="etag_value",
            big_query_dataset_name="big_query_dataset_name_value",
            display_name="display_name_value",
            model_reference="model_reference_value",
            satisfies_pzs=True,
            satisfies_pzi=True,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = dataset_version.DatasetVersion.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.get_dataset_version(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, dataset_version.DatasetVersion)
    assert response.name == "name_value"
    assert response.etag == "etag_value"
    assert response.big_query_dataset_name == "big_query_dataset_name_value"
    assert response.display_name == "display_name_value"
    assert response.model_reference == "model_reference_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_get_dataset_version_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncDatasetServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncDatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_get_dataset_version"
    ) as post, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor,
        "post_get_dataset_version_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "pre_get_dataset_version"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.GetDatasetVersionRequest.pb(
            dataset_service.GetDatasetVersionRequest()
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
        return_value = dataset_version.DatasetVersion.to_json(
            dataset_version.DatasetVersion()
        )
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = dataset_service.GetDatasetVersionRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = dataset_version.DatasetVersion()
        post_with_metadata.return_value = dataset_version.DatasetVersion(), metadata

        await client.get_dataset_version(
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
async def test_list_dataset_versions_rest_asyncio_bad_request(
    request_type=dataset_service.ListDatasetVersionsRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/datasets/sample3"}
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
        await client.list_dataset_versions(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.ListDatasetVersionsRequest,
        dict,
    ],
)
async def test_list_dataset_versions_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/datasets/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset_service.ListDatasetVersionsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = dataset_service.ListDatasetVersionsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.list_dataset_versions(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDatasetVersionsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_list_dataset_versions_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncDatasetServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncDatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_list_dataset_versions"
    ) as post, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor,
        "post_list_dataset_versions_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "pre_list_dataset_versions"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.ListDatasetVersionsRequest.pb(
            dataset_service.ListDatasetVersionsRequest()
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
        return_value = dataset_service.ListDatasetVersionsResponse.to_json(
            dataset_service.ListDatasetVersionsResponse()
        )
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = dataset_service.ListDatasetVersionsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = dataset_service.ListDatasetVersionsResponse()
        post_with_metadata.return_value = (
            dataset_service.ListDatasetVersionsResponse(),
            metadata,
        )

        await client.list_dataset_versions(
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
async def test_restore_dataset_version_rest_asyncio_bad_request(
    request_type=dataset_service.RestoreDatasetVersionRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/datasets/sample3/datasetVersions/sample4"
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
        await client.restore_dataset_version(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.RestoreDatasetVersionRequest,
        dict,
    ],
)
async def test_restore_dataset_version_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/datasets/sample3/datasetVersions/sample4"
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
        response = await client.restore_dataset_version(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_restore_dataset_version_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncDatasetServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncDatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_restore_dataset_version"
    ) as post, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor,
        "post_restore_dataset_version_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "pre_restore_dataset_version"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.RestoreDatasetVersionRequest.pb(
            dataset_service.RestoreDatasetVersionRequest()
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

        request = dataset_service.RestoreDatasetVersionRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.restore_dataset_version(
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
async def test_list_data_items_rest_asyncio_bad_request(
    request_type=dataset_service.ListDataItemsRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/datasets/sample3"}
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
        await client.list_data_items(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.ListDataItemsRequest,
        dict,
    ],
)
async def test_list_data_items_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/datasets/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset_service.ListDataItemsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = dataset_service.ListDataItemsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.list_data_items(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDataItemsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_list_data_items_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncDatasetServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncDatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_list_data_items"
    ) as post, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor,
        "post_list_data_items_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "pre_list_data_items"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.ListDataItemsRequest.pb(
            dataset_service.ListDataItemsRequest()
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
        return_value = dataset_service.ListDataItemsResponse.to_json(
            dataset_service.ListDataItemsResponse()
        )
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = dataset_service.ListDataItemsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = dataset_service.ListDataItemsResponse()
        post_with_metadata.return_value = (
            dataset_service.ListDataItemsResponse(),
            metadata,
        )

        await client.list_data_items(
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
async def test_search_data_items_rest_asyncio_bad_request(
    request_type=dataset_service.SearchDataItemsRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {"dataset": "projects/sample1/locations/sample2/datasets/sample3"}
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
        await client.search_data_items(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.SearchDataItemsRequest,
        dict,
    ],
)
async def test_search_data_items_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"dataset": "projects/sample1/locations/sample2/datasets/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset_service.SearchDataItemsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = dataset_service.SearchDataItemsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.search_data_items(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.SearchDataItemsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_search_data_items_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncDatasetServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncDatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_search_data_items"
    ) as post, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor,
        "post_search_data_items_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "pre_search_data_items"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.SearchDataItemsRequest.pb(
            dataset_service.SearchDataItemsRequest()
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
        return_value = dataset_service.SearchDataItemsResponse.to_json(
            dataset_service.SearchDataItemsResponse()
        )
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = dataset_service.SearchDataItemsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = dataset_service.SearchDataItemsResponse()
        post_with_metadata.return_value = (
            dataset_service.SearchDataItemsResponse(),
            metadata,
        )

        await client.search_data_items(
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
async def test_list_saved_queries_rest_asyncio_bad_request(
    request_type=dataset_service.ListSavedQueriesRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/datasets/sample3"}
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
        await client.list_saved_queries(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.ListSavedQueriesRequest,
        dict,
    ],
)
async def test_list_saved_queries_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2/datasets/sample3"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset_service.ListSavedQueriesResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = dataset_service.ListSavedQueriesResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.list_saved_queries(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListSavedQueriesAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_list_saved_queries_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncDatasetServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncDatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_list_saved_queries"
    ) as post, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor,
        "post_list_saved_queries_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "pre_list_saved_queries"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.ListSavedQueriesRequest.pb(
            dataset_service.ListSavedQueriesRequest()
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
        return_value = dataset_service.ListSavedQueriesResponse.to_json(
            dataset_service.ListSavedQueriesResponse()
        )
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = dataset_service.ListSavedQueriesRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = dataset_service.ListSavedQueriesResponse()
        post_with_metadata.return_value = (
            dataset_service.ListSavedQueriesResponse(),
            metadata,
        )

        await client.list_saved_queries(
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
async def test_delete_saved_query_rest_asyncio_bad_request(
    request_type=dataset_service.DeleteSavedQueryRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/datasets/sample3/savedQueries/sample4"
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
        await client.delete_saved_query(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.DeleteSavedQueryRequest,
        dict,
    ],
)
async def test_delete_saved_query_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/datasets/sample3/savedQueries/sample4"
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
        response = await client.delete_saved_query(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_delete_saved_query_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncDatasetServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncDatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_delete_saved_query"
    ) as post, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor,
        "post_delete_saved_query_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "pre_delete_saved_query"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.DeleteSavedQueryRequest.pb(
            dataset_service.DeleteSavedQueryRequest()
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

        request = dataset_service.DeleteSavedQueryRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.delete_saved_query(
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
async def test_get_annotation_spec_rest_asyncio_bad_request(
    request_type=dataset_service.GetAnnotationSpecRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/datasets/sample3/annotationSpecs/sample4"
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
        await client.get_annotation_spec(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.GetAnnotationSpecRequest,
        dict,
    ],
)
async def test_get_annotation_spec_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/datasets/sample3/annotationSpecs/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = annotation_spec.AnnotationSpec(
            name="name_value",
            display_name="display_name_value",
            etag="etag_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = annotation_spec.AnnotationSpec.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.get_annotation_spec(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, annotation_spec.AnnotationSpec)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.etag == "etag_value"


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_get_annotation_spec_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncDatasetServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncDatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_get_annotation_spec"
    ) as post, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor,
        "post_get_annotation_spec_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "pre_get_annotation_spec"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.GetAnnotationSpecRequest.pb(
            dataset_service.GetAnnotationSpecRequest()
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
        return_value = annotation_spec.AnnotationSpec.to_json(
            annotation_spec.AnnotationSpec()
        )
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = dataset_service.GetAnnotationSpecRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = annotation_spec.AnnotationSpec()
        post_with_metadata.return_value = annotation_spec.AnnotationSpec(), metadata

        await client.get_annotation_spec(
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
async def test_list_annotations_rest_asyncio_bad_request(
    request_type=dataset_service.ListAnnotationsRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "parent": "projects/sample1/locations/sample2/datasets/sample3/dataItems/sample4"
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
        await client.list_annotations(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.ListAnnotationsRequest,
        dict,
    ],
)
async def test_list_annotations_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "parent": "projects/sample1/locations/sample2/datasets/sample3/dataItems/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = dataset_service.ListAnnotationsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = dataset_service.ListAnnotationsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.list_annotations(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListAnnotationsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_list_annotations_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncDatasetServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncDatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_list_annotations"
    ) as post, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor,
        "post_list_annotations_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "pre_list_annotations"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.ListAnnotationsRequest.pb(
            dataset_service.ListAnnotationsRequest()
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
        return_value = dataset_service.ListAnnotationsResponse.to_json(
            dataset_service.ListAnnotationsResponse()
        )
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = dataset_service.ListAnnotationsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = dataset_service.ListAnnotationsResponse()
        post_with_metadata.return_value = (
            dataset_service.ListAnnotationsResponse(),
            metadata,
        )

        await client.list_annotations(
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
async def test_assess_data_rest_asyncio_bad_request(
    request_type=dataset_service.AssessDataRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        await client.assess_data(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.AssessDataRequest,
        dict,
    ],
)
async def test_assess_data_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        response = await client.assess_data(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_assess_data_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncDatasetServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncDatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_assess_data"
    ) as post, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_assess_data_with_metadata"
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "pre_assess_data"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.AssessDataRequest.pb(
            dataset_service.AssessDataRequest()
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

        request = dataset_service.AssessDataRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.assess_data(
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
async def test_assemble_data_rest_asyncio_bad_request(
    request_type=dataset_service.AssembleDataRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        await client.assemble_data(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        dataset_service.AssembleDataRequest,
        dict,
    ],
)
async def test_assemble_data_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"name": "projects/sample1/locations/sample2/datasets/sample3"}
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
        response = await client.assemble_data(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_assemble_data_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncDatasetServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncDatasetServiceRestInterceptor()
        ),
    )
    client = DatasetServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "post_assemble_data"
    ) as post, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor,
        "post_assemble_data_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncDatasetServiceRestInterceptor, "pre_assemble_data"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = dataset_service.AssembleDataRequest.pb(
            dataset_service.AssembleDataRequest()
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

        request = dataset_service.AssembleDataRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.assemble_data(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    assert client is not None


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_create_dataset_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.create_dataset), "__call__") as call:
        await client.create_dataset(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.CreateDatasetRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_dataset_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.get_dataset), "__call__") as call:
        await client.get_dataset(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.GetDatasetRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_update_dataset_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.update_dataset), "__call__") as call:
        await client.update_dataset(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.UpdateDatasetRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_datasets_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.list_datasets), "__call__") as call:
        await client.list_datasets(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ListDatasetsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_delete_dataset_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.delete_dataset), "__call__") as call:
        await client.delete_dataset(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.DeleteDatasetRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_import_data_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.import_data), "__call__") as call:
        await client.import_data(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ImportDataRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_export_data_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.export_data), "__call__") as call:
        await client.export_data(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ExportDataRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_create_dataset_version_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.create_dataset_version), "__call__"
    ) as call:
        await client.create_dataset_version(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.CreateDatasetVersionRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_update_dataset_version_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.update_dataset_version), "__call__"
    ) as call:
        await client.update_dataset_version(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.UpdateDatasetVersionRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_delete_dataset_version_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_dataset_version), "__call__"
    ) as call:
        await client.delete_dataset_version(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.DeleteDatasetVersionRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_dataset_version_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.get_dataset_version), "__call__"
    ) as call:
        await client.get_dataset_version(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.GetDatasetVersionRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_dataset_versions_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.list_dataset_versions), "__call__"
    ) as call:
        await client.list_dataset_versions(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ListDatasetVersionsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_restore_dataset_version_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.restore_dataset_version), "__call__"
    ) as call:
        await client.restore_dataset_version(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.RestoreDatasetVersionRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_data_items_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.list_data_items), "__call__") as call:
        await client.list_data_items(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ListDataItemsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_search_data_items_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.search_data_items), "__call__"
    ) as call:
        await client.search_data_items(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.SearchDataItemsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_saved_queries_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.list_saved_queries), "__call__"
    ) as call:
        await client.list_saved_queries(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ListSavedQueriesRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_delete_saved_query_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_saved_query), "__call__"
    ) as call:
        await client.delete_saved_query(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.DeleteSavedQueryRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_annotation_spec_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.get_annotation_spec), "__call__"
    ) as call:
        await client.get_annotation_spec(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.GetAnnotationSpecRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_annotations_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.list_annotations), "__call__") as call:
        await client.list_annotations(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.ListAnnotationsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_assess_data_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.assess_data), "__call__") as call:
        await client.assess_data(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.AssessDataRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_assemble_data_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.assemble_data), "__call__") as call:
        await client.assemble_data(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = dataset_service.AssembleDataRequest()

        assert args[0] == request_msg


def test_dataset_service_rest_asyncio_lro_client():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = DatasetServiceAsyncClient(
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
        client = DatasetServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport="rest_asyncio",
            client_options=options,
        )


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = DatasetServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    assert isinstance(
        client.transport,
        transports.DatasetServiceGrpcTransport,
    )


def test_dataset_service_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(core_exceptions.DuplicateCredentialArgs):
        transport = transports.DatasetServiceTransport(
            credentials=ga_credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_dataset_service_base_transport():
    # Instantiate the base transport.
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.dataset_service.transports.DatasetServiceTransport.__init__"
    ) as Transport:
        Transport.return_value = None
        transport = transports.DatasetServiceTransport(
            credentials=ga_credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "create_dataset",
        "get_dataset",
        "update_dataset",
        "list_datasets",
        "delete_dataset",
        "import_data",
        "export_data",
        "create_dataset_version",
        "update_dataset_version",
        "delete_dataset_version",
        "get_dataset_version",
        "list_dataset_versions",
        "restore_dataset_version",
        "list_data_items",
        "search_data_items",
        "list_saved_queries",
        "delete_saved_query",
        "get_annotation_spec",
        "list_annotations",
        "assess_data",
        "assemble_data",
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


def test_dataset_service_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        google.auth, "load_credentials_from_file", autospec=True
    ) as load_creds, mock.patch(
        "google.cloud.aiplatform_v1beta1.services.dataset_service.transports.DatasetServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.DatasetServiceTransport(
            credentials_file="credentials.json",
            quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=None,
            default_scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


def test_dataset_service_base_transport_with_adc():
    # Test the default credentials are used if credentials and credentials_file are None.
    with mock.patch.object(google.auth, "default", autospec=True) as adc, mock.patch(
        "google.cloud.aiplatform_v1beta1.services.dataset_service.transports.DatasetServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.DatasetServiceTransport()
        adc.assert_called_once()


def test_dataset_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        DatasetServiceClient()
        adc.assert_called_once_with(
            scopes=None,
            default_scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id=None,
        )


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.DatasetServiceGrpcTransport,
        transports.DatasetServiceGrpcAsyncIOTransport,
    ],
)
def test_dataset_service_transport_auth_adc(transport_class):
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
        transports.DatasetServiceGrpcTransport,
        transports.DatasetServiceGrpcAsyncIOTransport,
        transports.DatasetServiceRestTransport,
    ],
)
def test_dataset_service_transport_auth_gdch_credentials(transport_class):
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
        (transports.DatasetServiceGrpcTransport, grpc_helpers),
        (transports.DatasetServiceGrpcAsyncIOTransport, grpc_helpers_async),
    ],
)
def test_dataset_service_transport_create_channel(transport_class, grpc_helpers):
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
        transports.DatasetServiceGrpcTransport,
        transports.DatasetServiceGrpcAsyncIOTransport,
    ],
)
def test_dataset_service_grpc_transport_client_cert_source_for_mtls(transport_class):
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


def test_dataset_service_http_transport_client_cert_source_for_mtls():
    cred = ga_credentials.AnonymousCredentials()
    with mock.patch(
        "google.auth.transport.requests.AuthorizedSession.configure_mtls_channel"
    ) as mock_configure_mtls_channel:
        transports.DatasetServiceRestTransport(
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
def test_dataset_service_host_no_port(transport_name):
    client = DatasetServiceClient(
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
def test_dataset_service_host_with_port(transport_name):
    client = DatasetServiceClient(
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
def test_dataset_service_client_transport_session_collision(transport_name):
    creds1 = ga_credentials.AnonymousCredentials()
    creds2 = ga_credentials.AnonymousCredentials()
    client1 = DatasetServiceClient(
        credentials=creds1,
        transport=transport_name,
    )
    client2 = DatasetServiceClient(
        credentials=creds2,
        transport=transport_name,
    )
    session1 = client1.transport.create_dataset._session
    session2 = client2.transport.create_dataset._session
    assert session1 != session2
    session1 = client1.transport.get_dataset._session
    session2 = client2.transport.get_dataset._session
    assert session1 != session2
    session1 = client1.transport.update_dataset._session
    session2 = client2.transport.update_dataset._session
    assert session1 != session2
    session1 = client1.transport.list_datasets._session
    session2 = client2.transport.list_datasets._session
    assert session1 != session2
    session1 = client1.transport.delete_dataset._session
    session2 = client2.transport.delete_dataset._session
    assert session1 != session2
    session1 = client1.transport.import_data._session
    session2 = client2.transport.import_data._session
    assert session1 != session2
    session1 = client1.transport.export_data._session
    session2 = client2.transport.export_data._session
    assert session1 != session2
    session1 = client1.transport.create_dataset_version._session
    session2 = client2.transport.create_dataset_version._session
    assert session1 != session2
    session1 = client1.transport.update_dataset_version._session
    session2 = client2.transport.update_dataset_version._session
    assert session1 != session2
    session1 = client1.transport.delete_dataset_version._session
    session2 = client2.transport.delete_dataset_version._session
    assert session1 != session2
    session1 = client1.transport.get_dataset_version._session
    session2 = client2.transport.get_dataset_version._session
    assert session1 != session2
    session1 = client1.transport.list_dataset_versions._session
    session2 = client2.transport.list_dataset_versions._session
    assert session1 != session2
    session1 = client1.transport.restore_dataset_version._session
    session2 = client2.transport.restore_dataset_version._session
    assert session1 != session2
    session1 = client1.transport.list_data_items._session
    session2 = client2.transport.list_data_items._session
    assert session1 != session2
    session1 = client1.transport.search_data_items._session
    session2 = client2.transport.search_data_items._session
    assert session1 != session2
    session1 = client1.transport.list_saved_queries._session
    session2 = client2.transport.list_saved_queries._session
    assert session1 != session2
    session1 = client1.transport.delete_saved_query._session
    session2 = client2.transport.delete_saved_query._session
    assert session1 != session2
    session1 = client1.transport.get_annotation_spec._session
    session2 = client2.transport.get_annotation_spec._session
    assert session1 != session2
    session1 = client1.transport.list_annotations._session
    session2 = client2.transport.list_annotations._session
    assert session1 != session2
    session1 = client1.transport.assess_data._session
    session2 = client2.transport.assess_data._session
    assert session1 != session2
    session1 = client1.transport.assemble_data._session
    session2 = client2.transport.assemble_data._session
    assert session1 != session2


def test_dataset_service_grpc_transport_channel():
    channel = grpc.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.DatasetServiceGrpcTransport(
        host="squid.clam.whelk",
        channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


def test_dataset_service_grpc_asyncio_transport_channel():
    channel = aio.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.DatasetServiceGrpcAsyncIOTransport(
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
        transports.DatasetServiceGrpcTransport,
        transports.DatasetServiceGrpcAsyncIOTransport,
    ],
)
def test_dataset_service_transport_channel_mtls_with_client_cert_source(
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
        transports.DatasetServiceGrpcTransport,
        transports.DatasetServiceGrpcAsyncIOTransport,
    ],
)
def test_dataset_service_transport_channel_mtls_with_adc(transport_class):
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


def test_dataset_service_grpc_lro_client():
    client = DatasetServiceClient(
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


def test_dataset_service_grpc_lro_async_client():
    client = DatasetServiceAsyncClient(
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


def test_annotation_path():
    project = "squid"
    location = "clam"
    dataset = "whelk"
    data_item = "octopus"
    annotation = "oyster"
    expected = "projects/{project}/locations/{location}/datasets/{dataset}/dataItems/{data_item}/annotations/{annotation}".format(
        project=project,
        location=location,
        dataset=dataset,
        data_item=data_item,
        annotation=annotation,
    )
    actual = DatasetServiceClient.annotation_path(
        project, location, dataset, data_item, annotation
    )
    assert expected == actual


def test_parse_annotation_path():
    expected = {
        "project": "nudibranch",
        "location": "cuttlefish",
        "dataset": "mussel",
        "data_item": "winkle",
        "annotation": "nautilus",
    }
    path = DatasetServiceClient.annotation_path(**expected)

    # Check that the path construction is reversible.
    actual = DatasetServiceClient.parse_annotation_path(path)
    assert expected == actual


def test_annotation_spec_path():
    project = "scallop"
    location = "abalone"
    dataset = "squid"
    annotation_spec = "clam"
    expected = "projects/{project}/locations/{location}/datasets/{dataset}/annotationSpecs/{annotation_spec}".format(
        project=project,
        location=location,
        dataset=dataset,
        annotation_spec=annotation_spec,
    )
    actual = DatasetServiceClient.annotation_spec_path(
        project, location, dataset, annotation_spec
    )
    assert expected == actual


def test_parse_annotation_spec_path():
    expected = {
        "project": "whelk",
        "location": "octopus",
        "dataset": "oyster",
        "annotation_spec": "nudibranch",
    }
    path = DatasetServiceClient.annotation_spec_path(**expected)

    # Check that the path construction is reversible.
    actual = DatasetServiceClient.parse_annotation_spec_path(path)
    assert expected == actual


def test_cached_content_path():
    project = "cuttlefish"
    location = "mussel"
    cached_content = "winkle"
    expected = "projects/{project}/locations/{location}/cachedContents/{cached_content}".format(
        project=project,
        location=location,
        cached_content=cached_content,
    )
    actual = DatasetServiceClient.cached_content_path(project, location, cached_content)
    assert expected == actual


def test_parse_cached_content_path():
    expected = {
        "project": "nautilus",
        "location": "scallop",
        "cached_content": "abalone",
    }
    path = DatasetServiceClient.cached_content_path(**expected)

    # Check that the path construction is reversible.
    actual = DatasetServiceClient.parse_cached_content_path(path)
    assert expected == actual


def test_data_item_path():
    project = "squid"
    location = "clam"
    dataset = "whelk"
    data_item = "octopus"
    expected = "projects/{project}/locations/{location}/datasets/{dataset}/dataItems/{data_item}".format(
        project=project,
        location=location,
        dataset=dataset,
        data_item=data_item,
    )
    actual = DatasetServiceClient.data_item_path(project, location, dataset, data_item)
    assert expected == actual


def test_parse_data_item_path():
    expected = {
        "project": "oyster",
        "location": "nudibranch",
        "dataset": "cuttlefish",
        "data_item": "mussel",
    }
    path = DatasetServiceClient.data_item_path(**expected)

    # Check that the path construction is reversible.
    actual = DatasetServiceClient.parse_data_item_path(path)
    assert expected == actual


def test_dataset_path():
    project = "winkle"
    location = "nautilus"
    dataset = "scallop"
    expected = "projects/{project}/locations/{location}/datasets/{dataset}".format(
        project=project,
        location=location,
        dataset=dataset,
    )
    actual = DatasetServiceClient.dataset_path(project, location, dataset)
    assert expected == actual


def test_parse_dataset_path():
    expected = {
        "project": "abalone",
        "location": "squid",
        "dataset": "clam",
    }
    path = DatasetServiceClient.dataset_path(**expected)

    # Check that the path construction is reversible.
    actual = DatasetServiceClient.parse_dataset_path(path)
    assert expected == actual


def test_dataset_version_path():
    project = "whelk"
    location = "octopus"
    dataset = "oyster"
    dataset_version = "nudibranch"
    expected = "projects/{project}/locations/{location}/datasets/{dataset}/datasetVersions/{dataset_version}".format(
        project=project,
        location=location,
        dataset=dataset,
        dataset_version=dataset_version,
    )
    actual = DatasetServiceClient.dataset_version_path(
        project, location, dataset, dataset_version
    )
    assert expected == actual


def test_parse_dataset_version_path():
    expected = {
        "project": "cuttlefish",
        "location": "mussel",
        "dataset": "winkle",
        "dataset_version": "nautilus",
    }
    path = DatasetServiceClient.dataset_version_path(**expected)

    # Check that the path construction is reversible.
    actual = DatasetServiceClient.parse_dataset_version_path(path)
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
    actual = DatasetServiceClient.endpoint_path(project, location, endpoint)
    assert expected == actual


def test_parse_endpoint_path():
    expected = {
        "project": "clam",
        "location": "whelk",
        "endpoint": "octopus",
    }
    path = DatasetServiceClient.endpoint_path(**expected)

    # Check that the path construction is reversible.
    actual = DatasetServiceClient.parse_endpoint_path(path)
    assert expected == actual


def test_rag_corpus_path():
    project = "oyster"
    location = "nudibranch"
    rag_corpus = "cuttlefish"
    expected = "projects/{project}/locations/{location}/ragCorpora/{rag_corpus}".format(
        project=project,
        location=location,
        rag_corpus=rag_corpus,
    )
    actual = DatasetServiceClient.rag_corpus_path(project, location, rag_corpus)
    assert expected == actual


def test_parse_rag_corpus_path():
    expected = {
        "project": "mussel",
        "location": "winkle",
        "rag_corpus": "nautilus",
    }
    path = DatasetServiceClient.rag_corpus_path(**expected)

    # Check that the path construction is reversible.
    actual = DatasetServiceClient.parse_rag_corpus_path(path)
    assert expected == actual


def test_saved_query_path():
    project = "scallop"
    location = "abalone"
    dataset = "squid"
    saved_query = "clam"
    expected = "projects/{project}/locations/{location}/datasets/{dataset}/savedQueries/{saved_query}".format(
        project=project,
        location=location,
        dataset=dataset,
        saved_query=saved_query,
    )
    actual = DatasetServiceClient.saved_query_path(
        project, location, dataset, saved_query
    )
    assert expected == actual


def test_parse_saved_query_path():
    expected = {
        "project": "whelk",
        "location": "octopus",
        "dataset": "oyster",
        "saved_query": "nudibranch",
    }
    path = DatasetServiceClient.saved_query_path(**expected)

    # Check that the path construction is reversible.
    actual = DatasetServiceClient.parse_saved_query_path(path)
    assert expected == actual


def test_common_billing_account_path():
    billing_account = "cuttlefish"
    expected = "billingAccounts/{billing_account}".format(
        billing_account=billing_account,
    )
    actual = DatasetServiceClient.common_billing_account_path(billing_account)
    assert expected == actual


def test_parse_common_billing_account_path():
    expected = {
        "billing_account": "mussel",
    }
    path = DatasetServiceClient.common_billing_account_path(**expected)

    # Check that the path construction is reversible.
    actual = DatasetServiceClient.parse_common_billing_account_path(path)
    assert expected == actual


def test_common_folder_path():
    folder = "winkle"
    expected = "folders/{folder}".format(
        folder=folder,
    )
    actual = DatasetServiceClient.common_folder_path(folder)
    assert expected == actual


def test_parse_common_folder_path():
    expected = {
        "folder": "nautilus",
    }
    path = DatasetServiceClient.common_folder_path(**expected)

    # Check that the path construction is reversible.
    actual = DatasetServiceClient.parse_common_folder_path(path)
    assert expected == actual


def test_common_organization_path():
    organization = "scallop"
    expected = "organizations/{organization}".format(
        organization=organization,
    )
    actual = DatasetServiceClient.common_organization_path(organization)
    assert expected == actual


def test_parse_common_organization_path():
    expected = {
        "organization": "abalone",
    }
    path = DatasetServiceClient.common_organization_path(**expected)

    # Check that the path construction is reversible.
    actual = DatasetServiceClient.parse_common_organization_path(path)
    assert expected == actual


def test_common_project_path():
    project = "squid"
    expected = "projects/{project}".format(
        project=project,
    )
    actual = DatasetServiceClient.common_project_path(project)
    assert expected == actual


def test_parse_common_project_path():
    expected = {
        "project": "clam",
    }
    path = DatasetServiceClient.common_project_path(**expected)

    # Check that the path construction is reversible.
    actual = DatasetServiceClient.parse_common_project_path(path)
    assert expected == actual


def test_common_location_path():
    project = "whelk"
    location = "octopus"
    expected = "projects/{project}/locations/{location}".format(
        project=project,
        location=location,
    )
    actual = DatasetServiceClient.common_location_path(project, location)
    assert expected == actual


def test_parse_common_location_path():
    expected = {
        "project": "oyster",
        "location": "nudibranch",
    }
    path = DatasetServiceClient.common_location_path(**expected)

    # Check that the path construction is reversible.
    actual = DatasetServiceClient.parse_common_location_path(path)
    assert expected == actual


def test_client_with_default_client_info():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(
        transports.DatasetServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        client = DatasetServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(
        transports.DatasetServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        transport_class = DatasetServiceClient.get_transport_class()
        transport = transport_class(
            credentials=ga_credentials.AnonymousCredentials(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)


def test_delete_operation(transport: str = "grpc"):
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(credentials=ga_credentials.AnonymousCredentials())

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
    client = DatasetServiceAsyncClient(credentials=async_anonymous_credentials())

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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="grpc_asyncio"
    )
    with mock.patch.object(
        type(getattr(client.transport, "_grpc_channel")), "close"
    ) as close:
        async with client:
            close.assert_not_called()
        close.assert_called_once()


def test_transport_close_rest():
    client = DatasetServiceClient(
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
    client = DatasetServiceAsyncClient(
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
        client = DatasetServiceClient(
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
        (DatasetServiceClient, transports.DatasetServiceGrpcTransport),
        (DatasetServiceAsyncClient, transports.DatasetServiceGrpcAsyncIOTransport),
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
