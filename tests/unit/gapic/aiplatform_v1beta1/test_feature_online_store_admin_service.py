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
from google.cloud.aiplatform_v1beta1.services.feature_online_store_admin_service import (
    FeatureOnlineStoreAdminServiceAsyncClient,
)
from google.cloud.aiplatform_v1beta1.services.feature_online_store_admin_service import (
    FeatureOnlineStoreAdminServiceClient,
)
from google.cloud.aiplatform_v1beta1.services.feature_online_store_admin_service import (
    pagers,
)
from google.cloud.aiplatform_v1beta1.services.feature_online_store_admin_service import (
    transports,
)
from google.cloud.aiplatform_v1beta1.types import encryption_spec
from google.cloud.aiplatform_v1beta1.types import feature_online_store
from google.cloud.aiplatform_v1beta1.types import (
    feature_online_store as gca_feature_online_store,
)
from google.cloud.aiplatform_v1beta1.types import feature_online_store_admin_service
from google.cloud.aiplatform_v1beta1.types import feature_view
from google.cloud.aiplatform_v1beta1.types import feature_view as gca_feature_view
from google.cloud.aiplatform_v1beta1.types import feature_view_sync
from google.cloud.aiplatform_v1beta1.types import machine_resources
from google.cloud.aiplatform_v1beta1.types import operation as gca_operation
from google.cloud.aiplatform_v1beta1.types import service_networking
from google.cloud.location import locations_pb2
from google.iam.v1 import iam_policy_pb2  # type: ignore
from google.iam.v1 import options_pb2  # type: ignore
from google.iam.v1 import policy_pb2  # type: ignore
from google.longrunning import operations_pb2  # type: ignore
from google.oauth2 import service_account
from google.protobuf import empty_pb2  # type: ignore
from google.protobuf import field_mask_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
from google.rpc import status_pb2  # type: ignore
from google.type import interval_pb2  # type: ignore
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

    assert FeatureOnlineStoreAdminServiceClient._get_default_mtls_endpoint(None) is None
    assert (
        FeatureOnlineStoreAdminServiceClient._get_default_mtls_endpoint(api_endpoint)
        == api_mtls_endpoint
    )
    assert (
        FeatureOnlineStoreAdminServiceClient._get_default_mtls_endpoint(
            api_mtls_endpoint
        )
        == api_mtls_endpoint
    )
    assert (
        FeatureOnlineStoreAdminServiceClient._get_default_mtls_endpoint(
            sandbox_endpoint
        )
        == sandbox_mtls_endpoint
    )
    assert (
        FeatureOnlineStoreAdminServiceClient._get_default_mtls_endpoint(
            sandbox_mtls_endpoint
        )
        == sandbox_mtls_endpoint
    )
    assert (
        FeatureOnlineStoreAdminServiceClient._get_default_mtls_endpoint(non_googleapi)
        == non_googleapi
    )


def test__read_environment_variables():
    assert FeatureOnlineStoreAdminServiceClient._read_environment_variables() == (
        False,
        "auto",
        None,
    )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        assert FeatureOnlineStoreAdminServiceClient._read_environment_variables() == (
            True,
            "auto",
            None,
        )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "false"}):
        assert FeatureOnlineStoreAdminServiceClient._read_environment_variables() == (
            False,
            "auto",
            None,
        )

    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}
    ):
        with pytest.raises(ValueError) as excinfo:
            FeatureOnlineStoreAdminServiceClient._read_environment_variables()
    assert (
        str(excinfo.value)
        == "Environment variable `GOOGLE_API_USE_CLIENT_CERTIFICATE` must be either `true` or `false`"
    )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        assert FeatureOnlineStoreAdminServiceClient._read_environment_variables() == (
            False,
            "never",
            None,
        )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        assert FeatureOnlineStoreAdminServiceClient._read_environment_variables() == (
            False,
            "always",
            None,
        )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"}):
        assert FeatureOnlineStoreAdminServiceClient._read_environment_variables() == (
            False,
            "auto",
            None,
        )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError) as excinfo:
            FeatureOnlineStoreAdminServiceClient._read_environment_variables()
    assert (
        str(excinfo.value)
        == "Environment variable `GOOGLE_API_USE_MTLS_ENDPOINT` must be `never`, `auto` or `always`"
    )

    with mock.patch.dict(os.environ, {"GOOGLE_CLOUD_UNIVERSE_DOMAIN": "foo.com"}):
        assert FeatureOnlineStoreAdminServiceClient._read_environment_variables() == (
            False,
            "auto",
            "foo.com",
        )


def test__get_client_cert_source():
    mock_provided_cert_source = mock.Mock()
    mock_default_cert_source = mock.Mock()

    assert (
        FeatureOnlineStoreAdminServiceClient._get_client_cert_source(None, False)
        is None
    )
    assert (
        FeatureOnlineStoreAdminServiceClient._get_client_cert_source(
            mock_provided_cert_source, False
        )
        is None
    )
    assert (
        FeatureOnlineStoreAdminServiceClient._get_client_cert_source(
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
                FeatureOnlineStoreAdminServiceClient._get_client_cert_source(None, True)
                is mock_default_cert_source
            )
            assert (
                FeatureOnlineStoreAdminServiceClient._get_client_cert_source(
                    mock_provided_cert_source, "true"
                )
                is mock_provided_cert_source
            )


@mock.patch.object(
    FeatureOnlineStoreAdminServiceClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(FeatureOnlineStoreAdminServiceClient),
)
@mock.patch.object(
    FeatureOnlineStoreAdminServiceAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(FeatureOnlineStoreAdminServiceAsyncClient),
)
def test__get_api_endpoint():
    api_override = "foo.com"
    mock_client_cert_source = mock.Mock()
    default_universe = FeatureOnlineStoreAdminServiceClient._DEFAULT_UNIVERSE
    default_endpoint = (
        FeatureOnlineStoreAdminServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(
            UNIVERSE_DOMAIN=default_universe
        )
    )
    mock_universe = "bar.com"
    mock_endpoint = (
        FeatureOnlineStoreAdminServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(
            UNIVERSE_DOMAIN=mock_universe
        )
    )

    assert (
        FeatureOnlineStoreAdminServiceClient._get_api_endpoint(
            api_override, mock_client_cert_source, default_universe, "always"
        )
        == api_override
    )
    assert (
        FeatureOnlineStoreAdminServiceClient._get_api_endpoint(
            None, mock_client_cert_source, default_universe, "auto"
        )
        == FeatureOnlineStoreAdminServiceClient.DEFAULT_MTLS_ENDPOINT
    )
    assert (
        FeatureOnlineStoreAdminServiceClient._get_api_endpoint(
            None, None, default_universe, "auto"
        )
        == default_endpoint
    )
    assert (
        FeatureOnlineStoreAdminServiceClient._get_api_endpoint(
            None, None, default_universe, "always"
        )
        == FeatureOnlineStoreAdminServiceClient.DEFAULT_MTLS_ENDPOINT
    )
    assert (
        FeatureOnlineStoreAdminServiceClient._get_api_endpoint(
            None, mock_client_cert_source, default_universe, "always"
        )
        == FeatureOnlineStoreAdminServiceClient.DEFAULT_MTLS_ENDPOINT
    )
    assert (
        FeatureOnlineStoreAdminServiceClient._get_api_endpoint(
            None, None, mock_universe, "never"
        )
        == mock_endpoint
    )
    assert (
        FeatureOnlineStoreAdminServiceClient._get_api_endpoint(
            None, None, default_universe, "never"
        )
        == default_endpoint
    )

    with pytest.raises(MutualTLSChannelError) as excinfo:
        FeatureOnlineStoreAdminServiceClient._get_api_endpoint(
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
        FeatureOnlineStoreAdminServiceClient._get_universe_domain(
            client_universe_domain, universe_domain_env
        )
        == client_universe_domain
    )
    assert (
        FeatureOnlineStoreAdminServiceClient._get_universe_domain(
            None, universe_domain_env
        )
        == universe_domain_env
    )
    assert (
        FeatureOnlineStoreAdminServiceClient._get_universe_domain(None, None)
        == FeatureOnlineStoreAdminServiceClient._DEFAULT_UNIVERSE
    )

    with pytest.raises(ValueError) as excinfo:
        FeatureOnlineStoreAdminServiceClient._get_universe_domain("", None)
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
    client = FeatureOnlineStoreAdminServiceClient(credentials=cred)
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
    client = FeatureOnlineStoreAdminServiceClient(credentials=cred)
    client._transport._credentials = cred

    error = core_exceptions.GoogleAPICallError("message", details=[])
    error.code = error_code

    client._add_cred_info_for_auth_errors(error)
    assert error.details == []


@pytest.mark.parametrize(
    "client_class,transport_name",
    [
        (FeatureOnlineStoreAdminServiceClient, "grpc"),
        (FeatureOnlineStoreAdminServiceAsyncClient, "grpc_asyncio"),
        (FeatureOnlineStoreAdminServiceClient, "rest"),
    ],
)
def test_feature_online_store_admin_service_client_from_service_account_info(
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
        (transports.FeatureOnlineStoreAdminServiceGrpcTransport, "grpc"),
        (transports.FeatureOnlineStoreAdminServiceGrpcAsyncIOTransport, "grpc_asyncio"),
        (transports.FeatureOnlineStoreAdminServiceRestTransport, "rest"),
    ],
)
def test_feature_online_store_admin_service_client_service_account_always_use_jwt(
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
        (FeatureOnlineStoreAdminServiceClient, "grpc"),
        (FeatureOnlineStoreAdminServiceAsyncClient, "grpc_asyncio"),
        (FeatureOnlineStoreAdminServiceClient, "rest"),
    ],
)
def test_feature_online_store_admin_service_client_from_service_account_file(
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


def test_feature_online_store_admin_service_client_get_transport_class():
    transport = FeatureOnlineStoreAdminServiceClient.get_transport_class()
    available_transports = [
        transports.FeatureOnlineStoreAdminServiceGrpcTransport,
        transports.FeatureOnlineStoreAdminServiceRestTransport,
    ]
    assert transport in available_transports

    transport = FeatureOnlineStoreAdminServiceClient.get_transport_class("grpc")
    assert transport == transports.FeatureOnlineStoreAdminServiceGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (
            FeatureOnlineStoreAdminServiceClient,
            transports.FeatureOnlineStoreAdminServiceGrpcTransport,
            "grpc",
        ),
        (
            FeatureOnlineStoreAdminServiceAsyncClient,
            transports.FeatureOnlineStoreAdminServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
        (
            FeatureOnlineStoreAdminServiceClient,
            transports.FeatureOnlineStoreAdminServiceRestTransport,
            "rest",
        ),
    ],
)
@mock.patch.object(
    FeatureOnlineStoreAdminServiceClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(FeatureOnlineStoreAdminServiceClient),
)
@mock.patch.object(
    FeatureOnlineStoreAdminServiceAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(FeatureOnlineStoreAdminServiceAsyncClient),
)
def test_feature_online_store_admin_service_client_client_options(
    client_class, transport_class, transport_name
):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(
        FeatureOnlineStoreAdminServiceClient, "get_transport_class"
    ) as gtc:
        transport = transport_class(credentials=ga_credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(
        FeatureOnlineStoreAdminServiceClient, "get_transport_class"
    ) as gtc:
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
            FeatureOnlineStoreAdminServiceClient,
            transports.FeatureOnlineStoreAdminServiceGrpcTransport,
            "grpc",
            "true",
        ),
        (
            FeatureOnlineStoreAdminServiceAsyncClient,
            transports.FeatureOnlineStoreAdminServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "true",
        ),
        (
            FeatureOnlineStoreAdminServiceClient,
            transports.FeatureOnlineStoreAdminServiceGrpcTransport,
            "grpc",
            "false",
        ),
        (
            FeatureOnlineStoreAdminServiceAsyncClient,
            transports.FeatureOnlineStoreAdminServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            "false",
        ),
        (
            FeatureOnlineStoreAdminServiceClient,
            transports.FeatureOnlineStoreAdminServiceRestTransport,
            "rest",
            "true",
        ),
        (
            FeatureOnlineStoreAdminServiceClient,
            transports.FeatureOnlineStoreAdminServiceRestTransport,
            "rest",
            "false",
        ),
    ],
)
@mock.patch.object(
    FeatureOnlineStoreAdminServiceClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(FeatureOnlineStoreAdminServiceClient),
)
@mock.patch.object(
    FeatureOnlineStoreAdminServiceAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(FeatureOnlineStoreAdminServiceAsyncClient),
)
@mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"})
def test_feature_online_store_admin_service_client_mtls_env_auto(
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
    "client_class",
    [FeatureOnlineStoreAdminServiceClient, FeatureOnlineStoreAdminServiceAsyncClient],
)
@mock.patch.object(
    FeatureOnlineStoreAdminServiceClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(FeatureOnlineStoreAdminServiceClient),
)
@mock.patch.object(
    FeatureOnlineStoreAdminServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(FeatureOnlineStoreAdminServiceAsyncClient),
)
def test_feature_online_store_admin_service_client_get_mtls_endpoint_and_cert_source(
    client_class,
):
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
    "client_class",
    [FeatureOnlineStoreAdminServiceClient, FeatureOnlineStoreAdminServiceAsyncClient],
)
@mock.patch.object(
    FeatureOnlineStoreAdminServiceClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(FeatureOnlineStoreAdminServiceClient),
)
@mock.patch.object(
    FeatureOnlineStoreAdminServiceAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(FeatureOnlineStoreAdminServiceAsyncClient),
)
def test_feature_online_store_admin_service_client_client_api_endpoint(client_class):
    mock_client_cert_source = client_cert_source_callback
    api_override = "foo.com"
    default_universe = FeatureOnlineStoreAdminServiceClient._DEFAULT_UNIVERSE
    default_endpoint = (
        FeatureOnlineStoreAdminServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(
            UNIVERSE_DOMAIN=default_universe
        )
    )
    mock_universe = "bar.com"
    mock_endpoint = (
        FeatureOnlineStoreAdminServiceClient._DEFAULT_ENDPOINT_TEMPLATE.format(
            UNIVERSE_DOMAIN=mock_universe
        )
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
            FeatureOnlineStoreAdminServiceClient,
            transports.FeatureOnlineStoreAdminServiceGrpcTransport,
            "grpc",
        ),
        (
            FeatureOnlineStoreAdminServiceAsyncClient,
            transports.FeatureOnlineStoreAdminServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
        (
            FeatureOnlineStoreAdminServiceClient,
            transports.FeatureOnlineStoreAdminServiceRestTransport,
            "rest",
        ),
    ],
)
def test_feature_online_store_admin_service_client_client_options_scopes(
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
            FeatureOnlineStoreAdminServiceClient,
            transports.FeatureOnlineStoreAdminServiceGrpcTransport,
            "grpc",
            grpc_helpers,
        ),
        (
            FeatureOnlineStoreAdminServiceAsyncClient,
            transports.FeatureOnlineStoreAdminServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            grpc_helpers_async,
        ),
        (
            FeatureOnlineStoreAdminServiceClient,
            transports.FeatureOnlineStoreAdminServiceRestTransport,
            "rest",
            None,
        ),
    ],
)
def test_feature_online_store_admin_service_client_client_options_credentials_file(
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


def test_feature_online_store_admin_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.feature_online_store_admin_service.transports.FeatureOnlineStoreAdminServiceGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = FeatureOnlineStoreAdminServiceClient(
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
            FeatureOnlineStoreAdminServiceClient,
            transports.FeatureOnlineStoreAdminServiceGrpcTransport,
            "grpc",
            grpc_helpers,
        ),
        (
            FeatureOnlineStoreAdminServiceAsyncClient,
            transports.FeatureOnlineStoreAdminServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
            grpc_helpers_async,
        ),
    ],
)
def test_feature_online_store_admin_service_client_create_channel_credentials_file(
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
        feature_online_store_admin_service.CreateFeatureOnlineStoreRequest,
        dict,
    ],
)
def test_create_feature_online_store(request_type, transport: str = "grpc"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_feature_online_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.create_feature_online_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.CreateFeatureOnlineStoreRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_create_feature_online_store_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = feature_online_store_admin_service.CreateFeatureOnlineStoreRequest(
        parent="parent_value",
        feature_online_store_id="feature_online_store_id_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_feature_online_store), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.create_feature_online_store(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[
            0
        ] == feature_online_store_admin_service.CreateFeatureOnlineStoreRequest(
            parent="parent_value",
            feature_online_store_id="feature_online_store_id_value",
        )


def test_create_feature_online_store_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.create_feature_online_store
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[
            client._transport.create_feature_online_store
        ] = mock_rpc
        request = {}
        client.create_feature_online_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.create_feature_online_store(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_create_feature_online_store_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.create_feature_online_store
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.create_feature_online_store
        ] = mock_rpc

        request = {}
        await client.create_feature_online_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.create_feature_online_store(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_create_feature_online_store_async(
    transport: str = "grpc_asyncio",
    request_type=feature_online_store_admin_service.CreateFeatureOnlineStoreRequest,
):
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_feature_online_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.create_feature_online_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.CreateFeatureOnlineStoreRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_create_feature_online_store_async_from_dict():
    await test_create_feature_online_store_async(request_type=dict)


def test_create_feature_online_store_field_headers():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.CreateFeatureOnlineStoreRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_feature_online_store), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.create_feature_online_store(request)

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
async def test_create_feature_online_store_field_headers_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.CreateFeatureOnlineStoreRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_feature_online_store), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.create_feature_online_store(request)

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


def test_create_feature_online_store_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_feature_online_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_feature_online_store(
            parent="parent_value",
            feature_online_store=gca_feature_online_store.FeatureOnlineStore(
                bigtable=gca_feature_online_store.FeatureOnlineStore.Bigtable(
                    auto_scaling=gca_feature_online_store.FeatureOnlineStore.Bigtable.AutoScaling(
                        min_node_count=1489
                    )
                )
            ),
            feature_online_store_id="feature_online_store_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].feature_online_store
        mock_val = gca_feature_online_store.FeatureOnlineStore(
            bigtable=gca_feature_online_store.FeatureOnlineStore.Bigtable(
                auto_scaling=gca_feature_online_store.FeatureOnlineStore.Bigtable.AutoScaling(
                    min_node_count=1489
                )
            )
        )
        assert arg == mock_val
        arg = args[0].feature_online_store_id
        mock_val = "feature_online_store_id_value"
        assert arg == mock_val


def test_create_feature_online_store_flattened_error():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_feature_online_store(
            feature_online_store_admin_service.CreateFeatureOnlineStoreRequest(),
            parent="parent_value",
            feature_online_store=gca_feature_online_store.FeatureOnlineStore(
                bigtable=gca_feature_online_store.FeatureOnlineStore.Bigtable(
                    auto_scaling=gca_feature_online_store.FeatureOnlineStore.Bigtable.AutoScaling(
                        min_node_count=1489
                    )
                )
            ),
            feature_online_store_id="feature_online_store_id_value",
        )


@pytest.mark.asyncio
async def test_create_feature_online_store_flattened_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_feature_online_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_feature_online_store(
            parent="parent_value",
            feature_online_store=gca_feature_online_store.FeatureOnlineStore(
                bigtable=gca_feature_online_store.FeatureOnlineStore.Bigtable(
                    auto_scaling=gca_feature_online_store.FeatureOnlineStore.Bigtable.AutoScaling(
                        min_node_count=1489
                    )
                )
            ),
            feature_online_store_id="feature_online_store_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].feature_online_store
        mock_val = gca_feature_online_store.FeatureOnlineStore(
            bigtable=gca_feature_online_store.FeatureOnlineStore.Bigtable(
                auto_scaling=gca_feature_online_store.FeatureOnlineStore.Bigtable.AutoScaling(
                    min_node_count=1489
                )
            )
        )
        assert arg == mock_val
        arg = args[0].feature_online_store_id
        mock_val = "feature_online_store_id_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_create_feature_online_store_flattened_error_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_feature_online_store(
            feature_online_store_admin_service.CreateFeatureOnlineStoreRequest(),
            parent="parent_value",
            feature_online_store=gca_feature_online_store.FeatureOnlineStore(
                bigtable=gca_feature_online_store.FeatureOnlineStore.Bigtable(
                    auto_scaling=gca_feature_online_store.FeatureOnlineStore.Bigtable.AutoScaling(
                        min_node_count=1489
                    )
                )
            ),
            feature_online_store_id="feature_online_store_id_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.GetFeatureOnlineStoreRequest,
        dict,
    ],
)
def test_get_feature_online_store(request_type, transport: str = "grpc"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_feature_online_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = feature_online_store.FeatureOnlineStore(
            name="name_value",
            etag="etag_value",
            state=feature_online_store.FeatureOnlineStore.State.STABLE,
            satisfies_pzs=True,
            satisfies_pzi=True,
        )
        response = client.get_feature_online_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.GetFeatureOnlineStoreRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, feature_online_store.FeatureOnlineStore)
    assert response.name == "name_value"
    assert response.etag == "etag_value"
    assert response.state == feature_online_store.FeatureOnlineStore.State.STABLE
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


def test_get_feature_online_store_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = feature_online_store_admin_service.GetFeatureOnlineStoreRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_feature_online_store), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.get_feature_online_store(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[
            0
        ] == feature_online_store_admin_service.GetFeatureOnlineStoreRequest(
            name="name_value",
        )


def test_get_feature_online_store_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.get_feature_online_store
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[
            client._transport.get_feature_online_store
        ] = mock_rpc
        request = {}
        client.get_feature_online_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_feature_online_store(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_get_feature_online_store_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.get_feature_online_store
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.get_feature_online_store
        ] = mock_rpc

        request = {}
        await client.get_feature_online_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.get_feature_online_store(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_get_feature_online_store_async(
    transport: str = "grpc_asyncio",
    request_type=feature_online_store_admin_service.GetFeatureOnlineStoreRequest,
):
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_feature_online_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_online_store.FeatureOnlineStore(
                name="name_value",
                etag="etag_value",
                state=feature_online_store.FeatureOnlineStore.State.STABLE,
                satisfies_pzs=True,
                satisfies_pzi=True,
            )
        )
        response = await client.get_feature_online_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.GetFeatureOnlineStoreRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, feature_online_store.FeatureOnlineStore)
    assert response.name == "name_value"
    assert response.etag == "etag_value"
    assert response.state == feature_online_store.FeatureOnlineStore.State.STABLE
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


@pytest.mark.asyncio
async def test_get_feature_online_store_async_from_dict():
    await test_get_feature_online_store_async(request_type=dict)


def test_get_feature_online_store_field_headers():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.GetFeatureOnlineStoreRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_feature_online_store), "__call__"
    ) as call:
        call.return_value = feature_online_store.FeatureOnlineStore()
        client.get_feature_online_store(request)

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
async def test_get_feature_online_store_field_headers_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.GetFeatureOnlineStoreRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_feature_online_store), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_online_store.FeatureOnlineStore()
        )
        await client.get_feature_online_store(request)

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


def test_get_feature_online_store_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_feature_online_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = feature_online_store.FeatureOnlineStore()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_feature_online_store(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_get_feature_online_store_flattened_error():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_feature_online_store(
            feature_online_store_admin_service.GetFeatureOnlineStoreRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_get_feature_online_store_flattened_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_feature_online_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = feature_online_store.FeatureOnlineStore()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_online_store.FeatureOnlineStore()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_feature_online_store(
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
async def test_get_feature_online_store_flattened_error_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_feature_online_store(
            feature_online_store_admin_service.GetFeatureOnlineStoreRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.ListFeatureOnlineStoresRequest,
        dict,
    ],
)
def test_list_feature_online_stores(request_type, transport: str = "grpc"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_online_stores), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = client.list_feature_online_stores(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.ListFeatureOnlineStoresRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListFeatureOnlineStoresPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_feature_online_stores_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = feature_online_store_admin_service.ListFeatureOnlineStoresRequest(
        parent="parent_value",
        filter="filter_value",
        page_token="page_token_value",
        order_by="order_by_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_online_stores), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.list_feature_online_stores(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[
            0
        ] == feature_online_store_admin_service.ListFeatureOnlineStoresRequest(
            parent="parent_value",
            filter="filter_value",
            page_token="page_token_value",
            order_by="order_by_value",
        )


def test_list_feature_online_stores_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.list_feature_online_stores
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[
            client._transport.list_feature_online_stores
        ] = mock_rpc
        request = {}
        client.list_feature_online_stores(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_feature_online_stores(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_list_feature_online_stores_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.list_feature_online_stores
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.list_feature_online_stores
        ] = mock_rpc

        request = {}
        await client.list_feature_online_stores(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.list_feature_online_stores(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_list_feature_online_stores_async(
    transport: str = "grpc_asyncio",
    request_type=feature_online_store_admin_service.ListFeatureOnlineStoresRequest,
):
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_online_stores), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_feature_online_stores(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.ListFeatureOnlineStoresRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListFeatureOnlineStoresAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_feature_online_stores_async_from_dict():
    await test_list_feature_online_stores_async(request_type=dict)


def test_list_feature_online_stores_field_headers():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.ListFeatureOnlineStoresRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_online_stores), "__call__"
    ) as call:
        call.return_value = (
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse()
        )
        client.list_feature_online_stores(request)

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
async def test_list_feature_online_stores_field_headers_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.ListFeatureOnlineStoresRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_online_stores), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse()
        )
        await client.list_feature_online_stores(request)

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


def test_list_feature_online_stores_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_online_stores), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_feature_online_stores(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_list_feature_online_stores_flattened_error():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_feature_online_stores(
            feature_online_store_admin_service.ListFeatureOnlineStoresRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_feature_online_stores_flattened_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_online_stores), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse()
        )

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_feature_online_stores(
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
async def test_list_feature_online_stores_flattened_error_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_feature_online_stores(
            feature_online_store_admin_service.ListFeatureOnlineStoresRequest(),
            parent="parent_value",
        )


def test_list_feature_online_stores_pager(transport_name: str = "grpc"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_online_stores), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                feature_online_stores=[
                    feature_online_store.FeatureOnlineStore(),
                    feature_online_store.FeatureOnlineStore(),
                    feature_online_store.FeatureOnlineStore(),
                ],
                next_page_token="abc",
            ),
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                feature_online_stores=[],
                next_page_token="def",
            ),
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                feature_online_stores=[
                    feature_online_store.FeatureOnlineStore(),
                ],
                next_page_token="ghi",
            ),
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                feature_online_stores=[
                    feature_online_store.FeatureOnlineStore(),
                    feature_online_store.FeatureOnlineStore(),
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
        pager = client.list_feature_online_stores(
            request={}, retry=retry, timeout=timeout
        )

        assert pager._metadata == expected_metadata
        assert pager._retry == retry
        assert pager._timeout == timeout

        results = list(pager)
        assert len(results) == 6
        assert all(
            isinstance(i, feature_online_store.FeatureOnlineStore) for i in results
        )


def test_list_feature_online_stores_pages(transport_name: str = "grpc"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_online_stores), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                feature_online_stores=[
                    feature_online_store.FeatureOnlineStore(),
                    feature_online_store.FeatureOnlineStore(),
                    feature_online_store.FeatureOnlineStore(),
                ],
                next_page_token="abc",
            ),
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                feature_online_stores=[],
                next_page_token="def",
            ),
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                feature_online_stores=[
                    feature_online_store.FeatureOnlineStore(),
                ],
                next_page_token="ghi",
            ),
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                feature_online_stores=[
                    feature_online_store.FeatureOnlineStore(),
                    feature_online_store.FeatureOnlineStore(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_feature_online_stores(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_feature_online_stores_async_pager():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_online_stores),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                feature_online_stores=[
                    feature_online_store.FeatureOnlineStore(),
                    feature_online_store.FeatureOnlineStore(),
                    feature_online_store.FeatureOnlineStore(),
                ],
                next_page_token="abc",
            ),
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                feature_online_stores=[],
                next_page_token="def",
            ),
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                feature_online_stores=[
                    feature_online_store.FeatureOnlineStore(),
                ],
                next_page_token="ghi",
            ),
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                feature_online_stores=[
                    feature_online_store.FeatureOnlineStore(),
                    feature_online_store.FeatureOnlineStore(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_feature_online_stores(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(
            isinstance(i, feature_online_store.FeatureOnlineStore) for i in responses
        )


@pytest.mark.asyncio
async def test_list_feature_online_stores_async_pages():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_online_stores),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                feature_online_stores=[
                    feature_online_store.FeatureOnlineStore(),
                    feature_online_store.FeatureOnlineStore(),
                    feature_online_store.FeatureOnlineStore(),
                ],
                next_page_token="abc",
            ),
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                feature_online_stores=[],
                next_page_token="def",
            ),
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                feature_online_stores=[
                    feature_online_store.FeatureOnlineStore(),
                ],
                next_page_token="ghi",
            ),
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                feature_online_stores=[
                    feature_online_store.FeatureOnlineStore(),
                    feature_online_store.FeatureOnlineStore(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.list_feature_online_stores(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest,
        dict,
    ],
)
def test_update_feature_online_store(request_type, transport: str = "grpc"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_feature_online_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.update_feature_online_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_update_feature_online_store_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_feature_online_store), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.update_feature_online_store(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert (
            args[0]
            == feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest()
        )


def test_update_feature_online_store_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.update_feature_online_store
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[
            client._transport.update_feature_online_store
        ] = mock_rpc
        request = {}
        client.update_feature_online_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.update_feature_online_store(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_update_feature_online_store_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.update_feature_online_store
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.update_feature_online_store
        ] = mock_rpc

        request = {}
        await client.update_feature_online_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.update_feature_online_store(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_update_feature_online_store_async(
    transport: str = "grpc_asyncio",
    request_type=feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest,
):
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_feature_online_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.update_feature_online_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_update_feature_online_store_async_from_dict():
    await test_update_feature_online_store_async(request_type=dict)


def test_update_feature_online_store_field_headers():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest()

    request.feature_online_store.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_feature_online_store), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.update_feature_online_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "feature_online_store.name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_feature_online_store_field_headers_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest()

    request.feature_online_store.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_feature_online_store), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.update_feature_online_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "feature_online_store.name=name_value",
    ) in kw["metadata"]


def test_update_feature_online_store_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_feature_online_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_feature_online_store(
            feature_online_store=gca_feature_online_store.FeatureOnlineStore(
                bigtable=gca_feature_online_store.FeatureOnlineStore.Bigtable(
                    auto_scaling=gca_feature_online_store.FeatureOnlineStore.Bigtable.AutoScaling(
                        min_node_count=1489
                    )
                )
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].feature_online_store
        mock_val = gca_feature_online_store.FeatureOnlineStore(
            bigtable=gca_feature_online_store.FeatureOnlineStore.Bigtable(
                auto_scaling=gca_feature_online_store.FeatureOnlineStore.Bigtable.AutoScaling(
                    min_node_count=1489
                )
            )
        )
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=["paths_value"])
        assert arg == mock_val


def test_update_feature_online_store_flattened_error():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_feature_online_store(
            feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest(),
            feature_online_store=gca_feature_online_store.FeatureOnlineStore(
                bigtable=gca_feature_online_store.FeatureOnlineStore.Bigtable(
                    auto_scaling=gca_feature_online_store.FeatureOnlineStore.Bigtable.AutoScaling(
                        min_node_count=1489
                    )
                )
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_feature_online_store_flattened_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_feature_online_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_feature_online_store(
            feature_online_store=gca_feature_online_store.FeatureOnlineStore(
                bigtable=gca_feature_online_store.FeatureOnlineStore.Bigtable(
                    auto_scaling=gca_feature_online_store.FeatureOnlineStore.Bigtable.AutoScaling(
                        min_node_count=1489
                    )
                )
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].feature_online_store
        mock_val = gca_feature_online_store.FeatureOnlineStore(
            bigtable=gca_feature_online_store.FeatureOnlineStore.Bigtable(
                auto_scaling=gca_feature_online_store.FeatureOnlineStore.Bigtable.AutoScaling(
                    min_node_count=1489
                )
            )
        )
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=["paths_value"])
        assert arg == mock_val


@pytest.mark.asyncio
async def test_update_feature_online_store_flattened_error_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_feature_online_store(
            feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest(),
            feature_online_store=gca_feature_online_store.FeatureOnlineStore(
                bigtable=gca_feature_online_store.FeatureOnlineStore.Bigtable(
                    auto_scaling=gca_feature_online_store.FeatureOnlineStore.Bigtable.AutoScaling(
                        min_node_count=1489
                    )
                )
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest,
        dict,
    ],
)
def test_delete_feature_online_store(request_type, transport: str = "grpc"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_feature_online_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_feature_online_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_feature_online_store_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_feature_online_store), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.delete_feature_online_store(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[
            0
        ] == feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest(
            name="name_value",
        )


def test_delete_feature_online_store_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.delete_feature_online_store
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[
            client._transport.delete_feature_online_store
        ] = mock_rpc
        request = {}
        client.delete_feature_online_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.delete_feature_online_store(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_delete_feature_online_store_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.delete_feature_online_store
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.delete_feature_online_store
        ] = mock_rpc

        request = {}
        await client.delete_feature_online_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.delete_feature_online_store(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_delete_feature_online_store_async(
    transport: str = "grpc_asyncio",
    request_type=feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest,
):
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_feature_online_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_feature_online_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_feature_online_store_async_from_dict():
    await test_delete_feature_online_store_async(request_type=dict)


def test_delete_feature_online_store_field_headers():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_feature_online_store), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_feature_online_store(request)

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
async def test_delete_feature_online_store_field_headers_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_feature_online_store), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_feature_online_store(request)

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


def test_delete_feature_online_store_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_feature_online_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_feature_online_store(
            name="name_value",
            force=True,
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val
        arg = args[0].force
        mock_val = True
        assert arg == mock_val


def test_delete_feature_online_store_flattened_error():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_feature_online_store(
            feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest(),
            name="name_value",
            force=True,
        )


@pytest.mark.asyncio
async def test_delete_feature_online_store_flattened_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_feature_online_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_feature_online_store(
            name="name_value",
            force=True,
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val
        arg = args[0].force
        mock_val = True
        assert arg == mock_val


@pytest.mark.asyncio
async def test_delete_feature_online_store_flattened_error_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_feature_online_store(
            feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest(),
            name="name_value",
            force=True,
        )


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.CreateFeatureViewRequest,
        dict,
    ],
)
def test_create_feature_view(request_type, transport: str = "grpc"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_feature_view), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.create_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.CreateFeatureViewRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_create_feature_view_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = feature_online_store_admin_service.CreateFeatureViewRequest(
        parent="parent_value",
        feature_view_id="feature_view_id_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_feature_view), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.create_feature_view(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == feature_online_store_admin_service.CreateFeatureViewRequest(
            parent="parent_value",
            feature_view_id="feature_view_id_value",
        )


def test_create_feature_view_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.create_feature_view in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.create_feature_view] = (
            mock_rpc
        )
        request = {}
        client.create_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.create_feature_view(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_create_feature_view_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.create_feature_view
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.create_feature_view
        ] = mock_rpc

        request = {}
        await client.create_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.create_feature_view(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_create_feature_view_async(
    transport: str = "grpc_asyncio",
    request_type=feature_online_store_admin_service.CreateFeatureViewRequest,
):
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_feature_view), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.create_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.CreateFeatureViewRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_create_feature_view_async_from_dict():
    await test_create_feature_view_async(request_type=dict)


def test_create_feature_view_field_headers():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.CreateFeatureViewRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_feature_view), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.create_feature_view(request)

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
async def test_create_feature_view_field_headers_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.CreateFeatureViewRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_feature_view), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.create_feature_view(request)

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


def test_create_feature_view_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_feature_view), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_feature_view(
            parent="parent_value",
            feature_view=gca_feature_view.FeatureView(
                big_query_source=gca_feature_view.FeatureView.BigQuerySource(
                    uri="uri_value"
                )
            ),
            feature_view_id="feature_view_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].feature_view
        mock_val = gca_feature_view.FeatureView(
            big_query_source=gca_feature_view.FeatureView.BigQuerySource(
                uri="uri_value"
            )
        )
        assert arg == mock_val
        arg = args[0].feature_view_id
        mock_val = "feature_view_id_value"
        assert arg == mock_val


def test_create_feature_view_flattened_error():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_feature_view(
            feature_online_store_admin_service.CreateFeatureViewRequest(),
            parent="parent_value",
            feature_view=gca_feature_view.FeatureView(
                big_query_source=gca_feature_view.FeatureView.BigQuerySource(
                    uri="uri_value"
                )
            ),
            feature_view_id="feature_view_id_value",
        )


@pytest.mark.asyncio
async def test_create_feature_view_flattened_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_feature_view), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_feature_view(
            parent="parent_value",
            feature_view=gca_feature_view.FeatureView(
                big_query_source=gca_feature_view.FeatureView.BigQuerySource(
                    uri="uri_value"
                )
            ),
            feature_view_id="feature_view_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val
        arg = args[0].feature_view
        mock_val = gca_feature_view.FeatureView(
            big_query_source=gca_feature_view.FeatureView.BigQuerySource(
                uri="uri_value"
            )
        )
        assert arg == mock_val
        arg = args[0].feature_view_id
        mock_val = "feature_view_id_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_create_feature_view_flattened_error_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_feature_view(
            feature_online_store_admin_service.CreateFeatureViewRequest(),
            parent="parent_value",
            feature_view=gca_feature_view.FeatureView(
                big_query_source=gca_feature_view.FeatureView.BigQuerySource(
                    uri="uri_value"
                )
            ),
            feature_view_id="feature_view_id_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.GetFeatureViewRequest,
        dict,
    ],
)
def test_get_feature_view(request_type, transport: str = "grpc"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_feature_view), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = feature_view.FeatureView(
            name="name_value",
            etag="etag_value",
            service_agent_type=feature_view.FeatureView.ServiceAgentType.SERVICE_AGENT_TYPE_PROJECT,
            service_account_email="service_account_email_value",
            satisfies_pzs=True,
            satisfies_pzi=True,
        )
        response = client.get_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.GetFeatureViewRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, feature_view.FeatureView)
    assert response.name == "name_value"
    assert response.etag == "etag_value"
    assert (
        response.service_agent_type
        == feature_view.FeatureView.ServiceAgentType.SERVICE_AGENT_TYPE_PROJECT
    )
    assert response.service_account_email == "service_account_email_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


def test_get_feature_view_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = feature_online_store_admin_service.GetFeatureViewRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_feature_view), "__call__") as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.get_feature_view(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == feature_online_store_admin_service.GetFeatureViewRequest(
            name="name_value",
        )


def test_get_feature_view_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.get_feature_view in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.get_feature_view] = (
            mock_rpc
        )
        request = {}
        client.get_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_feature_view(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_get_feature_view_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.get_feature_view
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.get_feature_view
        ] = mock_rpc

        request = {}
        await client.get_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.get_feature_view(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_get_feature_view_async(
    transport: str = "grpc_asyncio",
    request_type=feature_online_store_admin_service.GetFeatureViewRequest,
):
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_feature_view), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_view.FeatureView(
                name="name_value",
                etag="etag_value",
                service_agent_type=feature_view.FeatureView.ServiceAgentType.SERVICE_AGENT_TYPE_PROJECT,
                service_account_email="service_account_email_value",
                satisfies_pzs=True,
                satisfies_pzi=True,
            )
        )
        response = await client.get_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.GetFeatureViewRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, feature_view.FeatureView)
    assert response.name == "name_value"
    assert response.etag == "etag_value"
    assert (
        response.service_agent_type
        == feature_view.FeatureView.ServiceAgentType.SERVICE_AGENT_TYPE_PROJECT
    )
    assert response.service_account_email == "service_account_email_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


@pytest.mark.asyncio
async def test_get_feature_view_async_from_dict():
    await test_get_feature_view_async(request_type=dict)


def test_get_feature_view_field_headers():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.GetFeatureViewRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_feature_view), "__call__") as call:
        call.return_value = feature_view.FeatureView()
        client.get_feature_view(request)

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
async def test_get_feature_view_field_headers_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.GetFeatureViewRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_feature_view), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_view.FeatureView()
        )
        await client.get_feature_view(request)

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


def test_get_feature_view_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_feature_view), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = feature_view.FeatureView()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_feature_view(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_get_feature_view_flattened_error():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_feature_view(
            feature_online_store_admin_service.GetFeatureViewRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_get_feature_view_flattened_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_feature_view), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = feature_view.FeatureView()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_view.FeatureView()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_feature_view(
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
async def test_get_feature_view_flattened_error_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_feature_view(
            feature_online_store_admin_service.GetFeatureViewRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.ListFeatureViewsRequest,
        dict,
    ],
)
def test_list_feature_views(request_type, transport: str = "grpc"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_views), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = feature_online_store_admin_service.ListFeatureViewsResponse(
            next_page_token="next_page_token_value",
        )
        response = client.list_feature_views(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.ListFeatureViewsRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListFeatureViewsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_feature_views_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = feature_online_store_admin_service.ListFeatureViewsRequest(
        parent="parent_value",
        filter="filter_value",
        page_token="page_token_value",
        order_by="order_by_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_views), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.list_feature_views(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == feature_online_store_admin_service.ListFeatureViewsRequest(
            parent="parent_value",
            filter="filter_value",
            page_token="page_token_value",
            order_by="order_by_value",
        )


def test_list_feature_views_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.list_feature_views in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.list_feature_views] = (
            mock_rpc
        )
        request = {}
        client.list_feature_views(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_feature_views(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_list_feature_views_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.list_feature_views
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.list_feature_views
        ] = mock_rpc

        request = {}
        await client.list_feature_views(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.list_feature_views(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_list_feature_views_async(
    transport: str = "grpc_asyncio",
    request_type=feature_online_store_admin_service.ListFeatureViewsRequest,
):
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_views), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_online_store_admin_service.ListFeatureViewsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_feature_views(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.ListFeatureViewsRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListFeatureViewsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_feature_views_async_from_dict():
    await test_list_feature_views_async(request_type=dict)


def test_list_feature_views_field_headers():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.ListFeatureViewsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_views), "__call__"
    ) as call:
        call.return_value = (
            feature_online_store_admin_service.ListFeatureViewsResponse()
        )
        client.list_feature_views(request)

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
async def test_list_feature_views_field_headers_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.ListFeatureViewsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_views), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_online_store_admin_service.ListFeatureViewsResponse()
        )
        await client.list_feature_views(request)

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


def test_list_feature_views_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_views), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            feature_online_store_admin_service.ListFeatureViewsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_feature_views(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_list_feature_views_flattened_error():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_feature_views(
            feature_online_store_admin_service.ListFeatureViewsRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_feature_views_flattened_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_views), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            feature_online_store_admin_service.ListFeatureViewsResponse()
        )

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_online_store_admin_service.ListFeatureViewsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_feature_views(
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
async def test_list_feature_views_flattened_error_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_feature_views(
            feature_online_store_admin_service.ListFeatureViewsRequest(),
            parent="parent_value",
        )


def test_list_feature_views_pager(transport_name: str = "grpc"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_views), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            feature_online_store_admin_service.ListFeatureViewsResponse(
                feature_views=[
                    feature_view.FeatureView(),
                    feature_view.FeatureView(),
                    feature_view.FeatureView(),
                ],
                next_page_token="abc",
            ),
            feature_online_store_admin_service.ListFeatureViewsResponse(
                feature_views=[],
                next_page_token="def",
            ),
            feature_online_store_admin_service.ListFeatureViewsResponse(
                feature_views=[
                    feature_view.FeatureView(),
                ],
                next_page_token="ghi",
            ),
            feature_online_store_admin_service.ListFeatureViewsResponse(
                feature_views=[
                    feature_view.FeatureView(),
                    feature_view.FeatureView(),
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
        pager = client.list_feature_views(request={}, retry=retry, timeout=timeout)

        assert pager._metadata == expected_metadata
        assert pager._retry == retry
        assert pager._timeout == timeout

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, feature_view.FeatureView) for i in results)


def test_list_feature_views_pages(transport_name: str = "grpc"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_views), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            feature_online_store_admin_service.ListFeatureViewsResponse(
                feature_views=[
                    feature_view.FeatureView(),
                    feature_view.FeatureView(),
                    feature_view.FeatureView(),
                ],
                next_page_token="abc",
            ),
            feature_online_store_admin_service.ListFeatureViewsResponse(
                feature_views=[],
                next_page_token="def",
            ),
            feature_online_store_admin_service.ListFeatureViewsResponse(
                feature_views=[
                    feature_view.FeatureView(),
                ],
                next_page_token="ghi",
            ),
            feature_online_store_admin_service.ListFeatureViewsResponse(
                feature_views=[
                    feature_view.FeatureView(),
                    feature_view.FeatureView(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_feature_views(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_feature_views_async_pager():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_views),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            feature_online_store_admin_service.ListFeatureViewsResponse(
                feature_views=[
                    feature_view.FeatureView(),
                    feature_view.FeatureView(),
                    feature_view.FeatureView(),
                ],
                next_page_token="abc",
            ),
            feature_online_store_admin_service.ListFeatureViewsResponse(
                feature_views=[],
                next_page_token="def",
            ),
            feature_online_store_admin_service.ListFeatureViewsResponse(
                feature_views=[
                    feature_view.FeatureView(),
                ],
                next_page_token="ghi",
            ),
            feature_online_store_admin_service.ListFeatureViewsResponse(
                feature_views=[
                    feature_view.FeatureView(),
                    feature_view.FeatureView(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_feature_views(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, feature_view.FeatureView) for i in responses)


@pytest.mark.asyncio
async def test_list_feature_views_async_pages():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_views),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            feature_online_store_admin_service.ListFeatureViewsResponse(
                feature_views=[
                    feature_view.FeatureView(),
                    feature_view.FeatureView(),
                    feature_view.FeatureView(),
                ],
                next_page_token="abc",
            ),
            feature_online_store_admin_service.ListFeatureViewsResponse(
                feature_views=[],
                next_page_token="def",
            ),
            feature_online_store_admin_service.ListFeatureViewsResponse(
                feature_views=[
                    feature_view.FeatureView(),
                ],
                next_page_token="ghi",
            ),
            feature_online_store_admin_service.ListFeatureViewsResponse(
                feature_views=[
                    feature_view.FeatureView(),
                    feature_view.FeatureView(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.list_feature_views(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.UpdateFeatureViewRequest,
        dict,
    ],
)
def test_update_feature_view(request_type, transport: str = "grpc"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_feature_view), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.update_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.UpdateFeatureViewRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_update_feature_view_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = feature_online_store_admin_service.UpdateFeatureViewRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_feature_view), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.update_feature_view(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == feature_online_store_admin_service.UpdateFeatureViewRequest()


def test_update_feature_view_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.update_feature_view in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.update_feature_view] = (
            mock_rpc
        )
        request = {}
        client.update_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.update_feature_view(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_update_feature_view_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.update_feature_view
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.update_feature_view
        ] = mock_rpc

        request = {}
        await client.update_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.update_feature_view(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_update_feature_view_async(
    transport: str = "grpc_asyncio",
    request_type=feature_online_store_admin_service.UpdateFeatureViewRequest,
):
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_feature_view), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.update_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.UpdateFeatureViewRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_update_feature_view_async_from_dict():
    await test_update_feature_view_async(request_type=dict)


def test_update_feature_view_field_headers():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.UpdateFeatureViewRequest()

    request.feature_view.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_feature_view), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.update_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "feature_view.name=name_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_feature_view_field_headers_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.UpdateFeatureViewRequest()

    request.feature_view.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_feature_view), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.update_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "feature_view.name=name_value",
    ) in kw["metadata"]


def test_update_feature_view_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_feature_view), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_feature_view(
            feature_view=gca_feature_view.FeatureView(
                big_query_source=gca_feature_view.FeatureView.BigQuerySource(
                    uri="uri_value"
                )
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].feature_view
        mock_val = gca_feature_view.FeatureView(
            big_query_source=gca_feature_view.FeatureView.BigQuerySource(
                uri="uri_value"
            )
        )
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=["paths_value"])
        assert arg == mock_val


def test_update_feature_view_flattened_error():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_feature_view(
            feature_online_store_admin_service.UpdateFeatureViewRequest(),
            feature_view=gca_feature_view.FeatureView(
                big_query_source=gca_feature_view.FeatureView.BigQuerySource(
                    uri="uri_value"
                )
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_feature_view_flattened_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_feature_view), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_feature_view(
            feature_view=gca_feature_view.FeatureView(
                big_query_source=gca_feature_view.FeatureView.BigQuerySource(
                    uri="uri_value"
                )
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].feature_view
        mock_val = gca_feature_view.FeatureView(
            big_query_source=gca_feature_view.FeatureView.BigQuerySource(
                uri="uri_value"
            )
        )
        assert arg == mock_val
        arg = args[0].update_mask
        mock_val = field_mask_pb2.FieldMask(paths=["paths_value"])
        assert arg == mock_val


@pytest.mark.asyncio
async def test_update_feature_view_flattened_error_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_feature_view(
            feature_online_store_admin_service.UpdateFeatureViewRequest(),
            feature_view=gca_feature_view.FeatureView(
                big_query_source=gca_feature_view.FeatureView.BigQuerySource(
                    uri="uri_value"
                )
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.DeleteFeatureViewRequest,
        dict,
    ],
)
def test_delete_feature_view(request_type, transport: str = "grpc"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_feature_view), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.delete_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.DeleteFeatureViewRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_feature_view_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = feature_online_store_admin_service.DeleteFeatureViewRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_feature_view), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.delete_feature_view(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == feature_online_store_admin_service.DeleteFeatureViewRequest(
            name="name_value",
        )


def test_delete_feature_view_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.delete_feature_view in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.delete_feature_view] = (
            mock_rpc
        )
        request = {}
        client.delete_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.delete_feature_view(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_delete_feature_view_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.delete_feature_view
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.delete_feature_view
        ] = mock_rpc

        request = {}
        await client.delete_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods call wrapper_fn to build a cached
        # client._transport.operations_client instance on first rpc call.
        # Subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        await client.delete_feature_view(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_delete_feature_view_async(
    transport: str = "grpc_asyncio",
    request_type=feature_online_store_admin_service.DeleteFeatureViewRequest,
):
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_feature_view), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.delete_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.DeleteFeatureViewRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_delete_feature_view_async_from_dict():
    await test_delete_feature_view_async(request_type=dict)


def test_delete_feature_view_field_headers():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.DeleteFeatureViewRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_feature_view), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_feature_view(request)

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
async def test_delete_feature_view_field_headers_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.DeleteFeatureViewRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_feature_view), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.delete_feature_view(request)

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


def test_delete_feature_view_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_feature_view), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_feature_view(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_delete_feature_view_flattened_error():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_feature_view(
            feature_online_store_admin_service.DeleteFeatureViewRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_feature_view_flattened_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_feature_view), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_feature_view(
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
async def test_delete_feature_view_flattened_error_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_feature_view(
            feature_online_store_admin_service.DeleteFeatureViewRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.SyncFeatureViewRequest,
        dict,
    ],
)
def test_sync_feature_view(request_type, transport: str = "grpc"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.sync_feature_view), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = feature_online_store_admin_service.SyncFeatureViewResponse(
            feature_view_sync="feature_view_sync_value",
        )
        response = client.sync_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.SyncFeatureViewRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, feature_online_store_admin_service.SyncFeatureViewResponse
    )
    assert response.feature_view_sync == "feature_view_sync_value"


def test_sync_feature_view_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = feature_online_store_admin_service.SyncFeatureViewRequest(
        feature_view="feature_view_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.sync_feature_view), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.sync_feature_view(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == feature_online_store_admin_service.SyncFeatureViewRequest(
            feature_view="feature_view_value",
        )


def test_sync_feature_view_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.sync_feature_view in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.sync_feature_view] = (
            mock_rpc
        )
        request = {}
        client.sync_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.sync_feature_view(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_sync_feature_view_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.sync_feature_view
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.sync_feature_view
        ] = mock_rpc

        request = {}
        await client.sync_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.sync_feature_view(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_sync_feature_view_async(
    transport: str = "grpc_asyncio",
    request_type=feature_online_store_admin_service.SyncFeatureViewRequest,
):
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.sync_feature_view), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_online_store_admin_service.SyncFeatureViewResponse(
                feature_view_sync="feature_view_sync_value",
            )
        )
        response = await client.sync_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.SyncFeatureViewRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, feature_online_store_admin_service.SyncFeatureViewResponse
    )
    assert response.feature_view_sync == "feature_view_sync_value"


@pytest.mark.asyncio
async def test_sync_feature_view_async_from_dict():
    await test_sync_feature_view_async(request_type=dict)


def test_sync_feature_view_field_headers():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.SyncFeatureViewRequest()

    request.feature_view = "feature_view_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.sync_feature_view), "__call__"
    ) as call:
        call.return_value = feature_online_store_admin_service.SyncFeatureViewResponse()
        client.sync_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "feature_view=feature_view_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_sync_feature_view_field_headers_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.SyncFeatureViewRequest()

    request.feature_view = "feature_view_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.sync_feature_view), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_online_store_admin_service.SyncFeatureViewResponse()
        )
        await client.sync_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "feature_view=feature_view_value",
    ) in kw["metadata"]


def test_sync_feature_view_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.sync_feature_view), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = feature_online_store_admin_service.SyncFeatureViewResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.sync_feature_view(
            feature_view="feature_view_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].feature_view
        mock_val = "feature_view_value"
        assert arg == mock_val


def test_sync_feature_view_flattened_error():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.sync_feature_view(
            feature_online_store_admin_service.SyncFeatureViewRequest(),
            feature_view="feature_view_value",
        )


@pytest.mark.asyncio
async def test_sync_feature_view_flattened_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.sync_feature_view), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = feature_online_store_admin_service.SyncFeatureViewResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_online_store_admin_service.SyncFeatureViewResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.sync_feature_view(
            feature_view="feature_view_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].feature_view
        mock_val = "feature_view_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_sync_feature_view_flattened_error_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.sync_feature_view(
            feature_online_store_admin_service.SyncFeatureViewRequest(),
            feature_view="feature_view_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.GetFeatureViewSyncRequest,
        dict,
    ],
)
def test_get_feature_view_sync(request_type, transport: str = "grpc"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_feature_view_sync), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = feature_view_sync.FeatureViewSync(
            name="name_value",
            satisfies_pzs=True,
            satisfies_pzi=True,
        )
        response = client.get_feature_view_sync(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.GetFeatureViewSyncRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, feature_view_sync.FeatureViewSync)
    assert response.name == "name_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


def test_get_feature_view_sync_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = feature_online_store_admin_service.GetFeatureViewSyncRequest(
        name="name_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_feature_view_sync), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.get_feature_view_sync(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == feature_online_store_admin_service.GetFeatureViewSyncRequest(
            name="name_value",
        )


def test_get_feature_view_sync_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.get_feature_view_sync
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.get_feature_view_sync] = (
            mock_rpc
        )
        request = {}
        client.get_feature_view_sync(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_feature_view_sync(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_get_feature_view_sync_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.get_feature_view_sync
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.get_feature_view_sync
        ] = mock_rpc

        request = {}
        await client.get_feature_view_sync(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.get_feature_view_sync(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_get_feature_view_sync_async(
    transport: str = "grpc_asyncio",
    request_type=feature_online_store_admin_service.GetFeatureViewSyncRequest,
):
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_feature_view_sync), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_view_sync.FeatureViewSync(
                name="name_value",
                satisfies_pzs=True,
                satisfies_pzi=True,
            )
        )
        response = await client.get_feature_view_sync(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.GetFeatureViewSyncRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, feature_view_sync.FeatureViewSync)
    assert response.name == "name_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


@pytest.mark.asyncio
async def test_get_feature_view_sync_async_from_dict():
    await test_get_feature_view_sync_async(request_type=dict)


def test_get_feature_view_sync_field_headers():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.GetFeatureViewSyncRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_feature_view_sync), "__call__"
    ) as call:
        call.return_value = feature_view_sync.FeatureViewSync()
        client.get_feature_view_sync(request)

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
async def test_get_feature_view_sync_field_headers_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.GetFeatureViewSyncRequest()

    request.name = "name_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_feature_view_sync), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_view_sync.FeatureViewSync()
        )
        await client.get_feature_view_sync(request)

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


def test_get_feature_view_sync_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_feature_view_sync), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = feature_view_sync.FeatureViewSync()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_feature_view_sync(
            name="name_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].name
        mock_val = "name_value"
        assert arg == mock_val


def test_get_feature_view_sync_flattened_error():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_feature_view_sync(
            feature_online_store_admin_service.GetFeatureViewSyncRequest(),
            name="name_value",
        )


@pytest.mark.asyncio
async def test_get_feature_view_sync_flattened_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_feature_view_sync), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = feature_view_sync.FeatureViewSync()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_view_sync.FeatureViewSync()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_feature_view_sync(
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
async def test_get_feature_view_sync_flattened_error_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_feature_view_sync(
            feature_online_store_admin_service.GetFeatureViewSyncRequest(),
            name="name_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.ListFeatureViewSyncsRequest,
        dict,
    ],
)
def test_list_feature_view_syncs(request_type, transport: str = "grpc"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_view_syncs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = client.list_feature_view_syncs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.ListFeatureViewSyncsRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListFeatureViewSyncsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_feature_view_syncs_non_empty_request_with_auto_populated_field():
    # This test is a coverage failsafe to make sure that UUID4 fields are
    # automatically populated, according to AIP-4235, with non-empty requests.
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Populate all string fields in the request which are not UUID4
    # since we want to check that UUID4 are populated automatically
    # if they meet the requirements of AIP 4235.
    request = feature_online_store_admin_service.ListFeatureViewSyncsRequest(
        parent="parent_value",
        filter="filter_value",
        page_token="page_token_value",
        order_by="order_by_value",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_view_syncs), "__call__"
    ) as call:
        call.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client.list_feature_view_syncs(request=request)
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[
            0
        ] == feature_online_store_admin_service.ListFeatureViewSyncsRequest(
            parent="parent_value",
            filter="filter_value",
            page_token="page_token_value",
            order_by="order_by_value",
        )


def test_list_feature_view_syncs_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="grpc",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.list_feature_view_syncs
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[
            client._transport.list_feature_view_syncs
        ] = mock_rpc
        request = {}
        client.list_feature_view_syncs(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_feature_view_syncs(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_list_feature_view_syncs_async_use_cached_wrapped_rpc(
    transport: str = "grpc_asyncio",
):
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method_async.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport=transport,
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._client._transport.list_feature_view_syncs
            in client._client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.AsyncMock()
        mock_rpc.return_value = mock.Mock()
        client._client._transport._wrapped_methods[
            client._client._transport.list_feature_view_syncs
        ] = mock_rpc

        request = {}
        await client.list_feature_view_syncs(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        await client.list_feature_view_syncs(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


@pytest.mark.asyncio
async def test_list_feature_view_syncs_async(
    transport: str = "grpc_asyncio",
    request_type=feature_online_store_admin_service.ListFeatureViewSyncsRequest,
):
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_view_syncs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.list_feature_view_syncs(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        request = feature_online_store_admin_service.ListFeatureViewSyncsRequest()
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListFeatureViewSyncsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_feature_view_syncs_async_from_dict():
    await test_list_feature_view_syncs_async(request_type=dict)


def test_list_feature_view_syncs_field_headers():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.ListFeatureViewSyncsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_view_syncs), "__call__"
    ) as call:
        call.return_value = (
            feature_online_store_admin_service.ListFeatureViewSyncsResponse()
        )
        client.list_feature_view_syncs(request)

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
async def test_list_feature_view_syncs_field_headers_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = feature_online_store_admin_service.ListFeatureViewSyncsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_view_syncs), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_online_store_admin_service.ListFeatureViewSyncsResponse()
        )
        await client.list_feature_view_syncs(request)

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


def test_list_feature_view_syncs_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_view_syncs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            feature_online_store_admin_service.ListFeatureViewSyncsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_feature_view_syncs(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_list_feature_view_syncs_flattened_error():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_feature_view_syncs(
            feature_online_store_admin_service.ListFeatureViewSyncsRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_feature_view_syncs_flattened_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_view_syncs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = (
            feature_online_store_admin_service.ListFeatureViewSyncsResponse()
        )

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_online_store_admin_service.ListFeatureViewSyncsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_feature_view_syncs(
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
async def test_list_feature_view_syncs_flattened_error_async():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_feature_view_syncs(
            feature_online_store_admin_service.ListFeatureViewSyncsRequest(),
            parent="parent_value",
        )


def test_list_feature_view_syncs_pager(transport_name: str = "grpc"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_view_syncs), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                feature_view_syncs=[
                    feature_view_sync.FeatureViewSync(),
                    feature_view_sync.FeatureViewSync(),
                    feature_view_sync.FeatureViewSync(),
                ],
                next_page_token="abc",
            ),
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                feature_view_syncs=[],
                next_page_token="def",
            ),
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                feature_view_syncs=[
                    feature_view_sync.FeatureViewSync(),
                ],
                next_page_token="ghi",
            ),
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                feature_view_syncs=[
                    feature_view_sync.FeatureViewSync(),
                    feature_view_sync.FeatureViewSync(),
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
        pager = client.list_feature_view_syncs(request={}, retry=retry, timeout=timeout)

        assert pager._metadata == expected_metadata
        assert pager._retry == retry
        assert pager._timeout == timeout

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, feature_view_sync.FeatureViewSync) for i in results)


def test_list_feature_view_syncs_pages(transport_name: str = "grpc"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_view_syncs), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                feature_view_syncs=[
                    feature_view_sync.FeatureViewSync(),
                    feature_view_sync.FeatureViewSync(),
                    feature_view_sync.FeatureViewSync(),
                ],
                next_page_token="abc",
            ),
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                feature_view_syncs=[],
                next_page_token="def",
            ),
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                feature_view_syncs=[
                    feature_view_sync.FeatureViewSync(),
                ],
                next_page_token="ghi",
            ),
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                feature_view_syncs=[
                    feature_view_sync.FeatureViewSync(),
                    feature_view_sync.FeatureViewSync(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_feature_view_syncs(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_feature_view_syncs_async_pager():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_view_syncs),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                feature_view_syncs=[
                    feature_view_sync.FeatureViewSync(),
                    feature_view_sync.FeatureViewSync(),
                    feature_view_sync.FeatureViewSync(),
                ],
                next_page_token="abc",
            ),
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                feature_view_syncs=[],
                next_page_token="def",
            ),
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                feature_view_syncs=[
                    feature_view_sync.FeatureViewSync(),
                ],
                next_page_token="ghi",
            ),
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                feature_view_syncs=[
                    feature_view_sync.FeatureViewSync(),
                    feature_view_sync.FeatureViewSync(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_feature_view_syncs(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, feature_view_sync.FeatureViewSync) for i in responses)


@pytest.mark.asyncio
async def test_list_feature_view_syncs_async_pages():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_view_syncs),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                feature_view_syncs=[
                    feature_view_sync.FeatureViewSync(),
                    feature_view_sync.FeatureViewSync(),
                    feature_view_sync.FeatureViewSync(),
                ],
                next_page_token="abc",
            ),
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                feature_view_syncs=[],
                next_page_token="def",
            ),
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                feature_view_syncs=[
                    feature_view_sync.FeatureViewSync(),
                ],
                next_page_token="ghi",
            ),
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                feature_view_syncs=[
                    feature_view_sync.FeatureViewSync(),
                    feature_view_sync.FeatureViewSync(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.list_feature_view_syncs(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_create_feature_online_store_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.create_feature_online_store
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[
            client._transport.create_feature_online_store
        ] = mock_rpc

        request = {}
        client.create_feature_online_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.create_feature_online_store(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_create_feature_online_store_rest_required_fields(
    request_type=feature_online_store_admin_service.CreateFeatureOnlineStoreRequest,
):
    transport_class = transports.FeatureOnlineStoreAdminServiceRestTransport

    request_init = {}
    request_init["parent"] = ""
    request_init["feature_online_store_id"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(pb_request, use_integers_for_enums=False)
    )

    # verify fields with default values are dropped
    assert "featureOnlineStoreId" not in jsonified_request

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).create_feature_online_store._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present
    assert "featureOnlineStoreId" in jsonified_request
    assert (
        jsonified_request["featureOnlineStoreId"]
        == request_init["feature_online_store_id"]
    )

    jsonified_request["parent"] = "parent_value"
    jsonified_request["featureOnlineStoreId"] = "feature_online_store_id_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).create_feature_online_store._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("feature_online_store_id",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"
    assert "featureOnlineStoreId" in jsonified_request
    assert jsonified_request["featureOnlineStoreId"] == "feature_online_store_id_value"

    client = FeatureOnlineStoreAdminServiceClient(
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

            response = client.create_feature_online_store(request)

            expected_params = [
                (
                    "featureOnlineStoreId",
                    "",
                ),
                ("$alt", "json;enum-encoding=int"),
            ]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_create_feature_online_store_rest_unset_required_fields():
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.create_feature_online_store._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(("featureOnlineStoreId",))
        & set(
            (
                "parent",
                "featureOnlineStore",
                "featureOnlineStoreId",
            )
        )
    )


def test_create_feature_online_store_rest_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
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
            feature_online_store=gca_feature_online_store.FeatureOnlineStore(
                bigtable=gca_feature_online_store.FeatureOnlineStore.Bigtable(
                    auto_scaling=gca_feature_online_store.FeatureOnlineStore.Bigtable.AutoScaling(
                        min_node_count=1489
                    )
                )
            ),
            feature_online_store_id="feature_online_store_id_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.create_feature_online_store(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{parent=projects/*/locations/*}/featureOnlineStores"
            % client.transport._host,
            args[1],
        )


def test_create_feature_online_store_rest_flattened_error(transport: str = "rest"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_feature_online_store(
            feature_online_store_admin_service.CreateFeatureOnlineStoreRequest(),
            parent="parent_value",
            feature_online_store=gca_feature_online_store.FeatureOnlineStore(
                bigtable=gca_feature_online_store.FeatureOnlineStore.Bigtable(
                    auto_scaling=gca_feature_online_store.FeatureOnlineStore.Bigtable.AutoScaling(
                        min_node_count=1489
                    )
                )
            ),
            feature_online_store_id="feature_online_store_id_value",
        )


def test_get_feature_online_store_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.get_feature_online_store
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[
            client._transport.get_feature_online_store
        ] = mock_rpc

        request = {}
        client.get_feature_online_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_feature_online_store(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_get_feature_online_store_rest_required_fields(
    request_type=feature_online_store_admin_service.GetFeatureOnlineStoreRequest,
):
    transport_class = transports.FeatureOnlineStoreAdminServiceRestTransport

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
    ).get_feature_online_store._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_feature_online_store._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = feature_online_store.FeatureOnlineStore()
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
            return_value = feature_online_store.FeatureOnlineStore.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.get_feature_online_store(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_feature_online_store_rest_unset_required_fields():
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_feature_online_store._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


def test_get_feature_online_store_rest_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = feature_online_store.FeatureOnlineStore()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
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
        return_value = feature_online_store.FeatureOnlineStore.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.get_feature_online_store(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/featureOnlineStores/*}"
            % client.transport._host,
            args[1],
        )


def test_get_feature_online_store_rest_flattened_error(transport: str = "rest"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_feature_online_store(
            feature_online_store_admin_service.GetFeatureOnlineStoreRequest(),
            name="name_value",
        )


def test_list_feature_online_stores_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.list_feature_online_stores
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[
            client._transport.list_feature_online_stores
        ] = mock_rpc

        request = {}
        client.list_feature_online_stores(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_feature_online_stores(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_list_feature_online_stores_rest_required_fields(
    request_type=feature_online_store_admin_service.ListFeatureOnlineStoresRequest,
):
    transport_class = transports.FeatureOnlineStoreAdminServiceRestTransport

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
    ).list_feature_online_stores._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_feature_online_stores._get_unset_required_fields(jsonified_request)
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

    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = feature_online_store_admin_service.ListFeatureOnlineStoresResponse()
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
                feature_online_store_admin_service.ListFeatureOnlineStoresResponse.pb(
                    return_value
                )
            )
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.list_feature_online_stores(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_list_feature_online_stores_rest_unset_required_fields():
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.list_feature_online_stores._get_unset_required_fields({})
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


def test_list_feature_online_stores_rest_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = (
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse()
        )

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
        return_value = (
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse.pb(
                return_value
            )
        )
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.list_feature_online_stores(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{parent=projects/*/locations/*}/featureOnlineStores"
            % client.transport._host,
            args[1],
        )


def test_list_feature_online_stores_rest_flattened_error(transport: str = "rest"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_feature_online_stores(
            feature_online_store_admin_service.ListFeatureOnlineStoresRequest(),
            parent="parent_value",
        )


def test_list_feature_online_stores_rest_pager(transport: str = "rest"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                feature_online_stores=[
                    feature_online_store.FeatureOnlineStore(),
                    feature_online_store.FeatureOnlineStore(),
                    feature_online_store.FeatureOnlineStore(),
                ],
                next_page_token="abc",
            ),
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                feature_online_stores=[],
                next_page_token="def",
            ),
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                feature_online_stores=[
                    feature_online_store.FeatureOnlineStore(),
                ],
                next_page_token="ghi",
            ),
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                feature_online_stores=[
                    feature_online_store.FeatureOnlineStore(),
                    feature_online_store.FeatureOnlineStore(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse.to_json(
                x
            )
            for x in response
        )
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {"parent": "projects/sample1/locations/sample2"}

        pager = client.list_feature_online_stores(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(
            isinstance(i, feature_online_store.FeatureOnlineStore) for i in results
        )

        pages = list(client.list_feature_online_stores(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_update_feature_online_store_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.update_feature_online_store
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[
            client._transport.update_feature_online_store
        ] = mock_rpc

        request = {}
        client.update_feature_online_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.update_feature_online_store(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_update_feature_online_store_rest_required_fields(
    request_type=feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest,
):
    transport_class = transports.FeatureOnlineStoreAdminServiceRestTransport

    request_init = {}
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(pb_request, use_integers_for_enums=False)
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_feature_online_store._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_feature_online_store._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("update_mask",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone

    client = FeatureOnlineStoreAdminServiceClient(
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

            response = client.update_feature_online_store(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_update_feature_online_store_rest_unset_required_fields():
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.update_feature_online_store._get_unset_required_fields({})
    assert set(unset_fields) == (set(("updateMask",)) & set(("featureOnlineStore",)))


def test_update_feature_online_store_rest_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "feature_online_store": {
                "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
            }
        }

        # get truthy value for each flattened field
        mock_args = dict(
            feature_online_store=gca_feature_online_store.FeatureOnlineStore(
                bigtable=gca_feature_online_store.FeatureOnlineStore.Bigtable(
                    auto_scaling=gca_feature_online_store.FeatureOnlineStore.Bigtable.AutoScaling(
                        min_node_count=1489
                    )
                )
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
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.update_feature_online_store(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{feature_online_store.name=projects/*/locations/*/featureOnlineStores/*}"
            % client.transport._host,
            args[1],
        )


def test_update_feature_online_store_rest_flattened_error(transport: str = "rest"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_feature_online_store(
            feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest(),
            feature_online_store=gca_feature_online_store.FeatureOnlineStore(
                bigtable=gca_feature_online_store.FeatureOnlineStore.Bigtable(
                    auto_scaling=gca_feature_online_store.FeatureOnlineStore.Bigtable.AutoScaling(
                        min_node_count=1489
                    )
                )
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


def test_delete_feature_online_store_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.delete_feature_online_store
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[
            client._transport.delete_feature_online_store
        ] = mock_rpc

        request = {}
        client.delete_feature_online_store(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.delete_feature_online_store(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_delete_feature_online_store_rest_required_fields(
    request_type=feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest,
):
    transport_class = transports.FeatureOnlineStoreAdminServiceRestTransport

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
    ).delete_feature_online_store._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).delete_feature_online_store._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("force",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = FeatureOnlineStoreAdminServiceClient(
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

            response = client.delete_feature_online_store(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_delete_feature_online_store_rest_unset_required_fields():
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.delete_feature_online_store._get_unset_required_fields({})
    assert set(unset_fields) == (set(("force",)) & set(("name",)))


def test_delete_feature_online_store_rest_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
        }

        # get truthy value for each flattened field
        mock_args = dict(
            name="name_value",
            force=True,
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.delete_feature_online_store(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/featureOnlineStores/*}"
            % client.transport._host,
            args[1],
        )


def test_delete_feature_online_store_rest_flattened_error(transport: str = "rest"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_feature_online_store(
            feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest(),
            name="name_value",
            force=True,
        )


def test_create_feature_view_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.create_feature_view in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.create_feature_view] = (
            mock_rpc
        )

        request = {}
        client.create_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.create_feature_view(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_create_feature_view_rest_required_fields(
    request_type=feature_online_store_admin_service.CreateFeatureViewRequest,
):
    transport_class = transports.FeatureOnlineStoreAdminServiceRestTransport

    request_init = {}
    request_init["parent"] = ""
    request_init["feature_view_id"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(pb_request, use_integers_for_enums=False)
    )

    # verify fields with default values are dropped
    assert "featureViewId" not in jsonified_request

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).create_feature_view._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present
    assert "featureViewId" in jsonified_request
    assert jsonified_request["featureViewId"] == request_init["feature_view_id"]

    jsonified_request["parent"] = "parent_value"
    jsonified_request["featureViewId"] = "feature_view_id_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).create_feature_view._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(
        (
            "feature_view_id",
            "run_sync_immediately",
        )
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"
    assert "featureViewId" in jsonified_request
    assert jsonified_request["featureViewId"] == "feature_view_id_value"

    client = FeatureOnlineStoreAdminServiceClient(
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

            response = client.create_feature_view(request)

            expected_params = [
                (
                    "featureViewId",
                    "",
                ),
                ("$alt", "json;enum-encoding=int"),
            ]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_create_feature_view_rest_unset_required_fields():
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.create_feature_view._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(
            (
                "featureViewId",
                "runSyncImmediately",
            )
        )
        & set(
            (
                "parent",
                "featureView",
                "featureViewId",
            )
        )
    )


def test_create_feature_view_rest_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "parent": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
        }

        # get truthy value for each flattened field
        mock_args = dict(
            parent="parent_value",
            feature_view=gca_feature_view.FeatureView(
                big_query_source=gca_feature_view.FeatureView.BigQuerySource(
                    uri="uri_value"
                )
            ),
            feature_view_id="feature_view_id_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.create_feature_view(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{parent=projects/*/locations/*/featureOnlineStores/*}/featureViews"
            % client.transport._host,
            args[1],
        )


def test_create_feature_view_rest_flattened_error(transport: str = "rest"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_feature_view(
            feature_online_store_admin_service.CreateFeatureViewRequest(),
            parent="parent_value",
            feature_view=gca_feature_view.FeatureView(
                big_query_source=gca_feature_view.FeatureView.BigQuerySource(
                    uri="uri_value"
                )
            ),
            feature_view_id="feature_view_id_value",
        )


def test_get_feature_view_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.get_feature_view in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.get_feature_view] = (
            mock_rpc
        )

        request = {}
        client.get_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_feature_view(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_get_feature_view_rest_required_fields(
    request_type=feature_online_store_admin_service.GetFeatureViewRequest,
):
    transport_class = transports.FeatureOnlineStoreAdminServiceRestTransport

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
    ).get_feature_view._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_feature_view._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = feature_view.FeatureView()
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
            return_value = feature_view.FeatureView.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.get_feature_view(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_feature_view_rest_unset_required_fields():
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_feature_view._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


def test_get_feature_view_rest_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = feature_view.FeatureView()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
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
        return_value = feature_view.FeatureView.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.get_feature_view(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*}"
            % client.transport._host,
            args[1],
        )


def test_get_feature_view_rest_flattened_error(transport: str = "rest"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_feature_view(
            feature_online_store_admin_service.GetFeatureViewRequest(),
            name="name_value",
        )


def test_list_feature_views_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.list_feature_views in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.list_feature_views] = (
            mock_rpc
        )

        request = {}
        client.list_feature_views(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_feature_views(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_list_feature_views_rest_required_fields(
    request_type=feature_online_store_admin_service.ListFeatureViewsRequest,
):
    transport_class = transports.FeatureOnlineStoreAdminServiceRestTransport

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
    ).list_feature_views._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_feature_views._get_unset_required_fields(jsonified_request)
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

    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = feature_online_store_admin_service.ListFeatureViewsResponse()
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
                feature_online_store_admin_service.ListFeatureViewsResponse.pb(
                    return_value
                )
            )
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.list_feature_views(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_list_feature_views_rest_unset_required_fields():
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.list_feature_views._get_unset_required_fields({})
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


def test_list_feature_views_rest_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = feature_online_store_admin_service.ListFeatureViewsResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "parent": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
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
        return_value = feature_online_store_admin_service.ListFeatureViewsResponse.pb(
            return_value
        )
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.list_feature_views(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{parent=projects/*/locations/*/featureOnlineStores/*}/featureViews"
            % client.transport._host,
            args[1],
        )


def test_list_feature_views_rest_flattened_error(transport: str = "rest"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_feature_views(
            feature_online_store_admin_service.ListFeatureViewsRequest(),
            parent="parent_value",
        )


def test_list_feature_views_rest_pager(transport: str = "rest"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            feature_online_store_admin_service.ListFeatureViewsResponse(
                feature_views=[
                    feature_view.FeatureView(),
                    feature_view.FeatureView(),
                    feature_view.FeatureView(),
                ],
                next_page_token="abc",
            ),
            feature_online_store_admin_service.ListFeatureViewsResponse(
                feature_views=[],
                next_page_token="def",
            ),
            feature_online_store_admin_service.ListFeatureViewsResponse(
                feature_views=[
                    feature_view.FeatureView(),
                ],
                next_page_token="ghi",
            ),
            feature_online_store_admin_service.ListFeatureViewsResponse(
                feature_views=[
                    feature_view.FeatureView(),
                    feature_view.FeatureView(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(
            feature_online_store_admin_service.ListFeatureViewsResponse.to_json(x)
            for x in response
        )
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {
            "parent": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
        }

        pager = client.list_feature_views(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, feature_view.FeatureView) for i in results)

        pages = list(client.list_feature_views(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_update_feature_view_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.update_feature_view in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.update_feature_view] = (
            mock_rpc
        )

        request = {}
        client.update_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.update_feature_view(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_update_feature_view_rest_required_fields(
    request_type=feature_online_store_admin_service.UpdateFeatureViewRequest,
):
    transport_class = transports.FeatureOnlineStoreAdminServiceRestTransport

    request_init = {}
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(pb_request, use_integers_for_enums=False)
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_feature_view._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).update_feature_view._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("update_mask",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone

    client = FeatureOnlineStoreAdminServiceClient(
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

            response = client.update_feature_view(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_update_feature_view_rest_unset_required_fields():
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.update_feature_view._get_unset_required_fields({})
    assert set(unset_fields) == (set(("updateMask",)) & set(("featureView",)))


def test_update_feature_view_rest_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "feature_view": {
                "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
            }
        }

        # get truthy value for each flattened field
        mock_args = dict(
            feature_view=gca_feature_view.FeatureView(
                big_query_source=gca_feature_view.FeatureView.BigQuerySource(
                    uri="uri_value"
                )
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
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.update_feature_view(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{feature_view.name=projects/*/locations/*/featureOnlineStores/*/featureViews/*}"
            % client.transport._host,
            args[1],
        )


def test_update_feature_view_rest_flattened_error(transport: str = "rest"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_feature_view(
            feature_online_store_admin_service.UpdateFeatureViewRequest(),
            feature_view=gca_feature_view.FeatureView(
                big_query_source=gca_feature_view.FeatureView.BigQuerySource(
                    uri="uri_value"
                )
            ),
            update_mask=field_mask_pb2.FieldMask(paths=["paths_value"]),
        )


def test_delete_feature_view_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.delete_feature_view in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.delete_feature_view] = (
            mock_rpc
        )

        request = {}
        client.delete_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        # Operation methods build a cached wrapper on first rpc call
        # subsequent calls should use the cached wrapper
        wrapper_fn.reset_mock()

        client.delete_feature_view(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_delete_feature_view_rest_required_fields(
    request_type=feature_online_store_admin_service.DeleteFeatureViewRequest,
):
    transport_class = transports.FeatureOnlineStoreAdminServiceRestTransport

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
    ).delete_feature_view._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).delete_feature_view._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = FeatureOnlineStoreAdminServiceClient(
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

            response = client.delete_feature_view(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_delete_feature_view_rest_unset_required_fields():
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.delete_feature_view._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


def test_delete_feature_view_rest_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
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

        client.delete_feature_view(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*}"
            % client.transport._host,
            args[1],
        )


def test_delete_feature_view_rest_flattened_error(transport: str = "rest"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_feature_view(
            feature_online_store_admin_service.DeleteFeatureViewRequest(),
            name="name_value",
        )


def test_sync_feature_view_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert client._transport.sync_feature_view in client._transport._wrapped_methods

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.sync_feature_view] = (
            mock_rpc
        )

        request = {}
        client.sync_feature_view(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.sync_feature_view(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_sync_feature_view_rest_required_fields(
    request_type=feature_online_store_admin_service.SyncFeatureViewRequest,
):
    transport_class = transports.FeatureOnlineStoreAdminServiceRestTransport

    request_init = {}
    request_init["feature_view"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(pb_request, use_integers_for_enums=False)
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).sync_feature_view._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["featureView"] = "feature_view_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).sync_feature_view._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "featureView" in jsonified_request
    assert jsonified_request["featureView"] == "feature_view_value"

    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = feature_online_store_admin_service.SyncFeatureViewResponse()
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
                feature_online_store_admin_service.SyncFeatureViewResponse.pb(
                    return_value
                )
            )
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.sync_feature_view(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_sync_feature_view_rest_unset_required_fields():
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.sync_feature_view._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("featureView",)))


def test_sync_feature_view_rest_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = feature_online_store_admin_service.SyncFeatureViewResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "feature_view": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
        }

        # get truthy value for each flattened field
        mock_args = dict(
            feature_view="feature_view_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = feature_online_store_admin_service.SyncFeatureViewResponse.pb(
            return_value
        )
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.sync_feature_view(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{feature_view=projects/*/locations/*/featureOnlineStores/*/featureViews/*}:sync"
            % client.transport._host,
            args[1],
        )


def test_sync_feature_view_rest_flattened_error(transport: str = "rest"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.sync_feature_view(
            feature_online_store_admin_service.SyncFeatureViewRequest(),
            feature_view="feature_view_value",
        )


def test_get_feature_view_sync_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.get_feature_view_sync
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[client._transport.get_feature_view_sync] = (
            mock_rpc
        )

        request = {}
        client.get_feature_view_sync(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.get_feature_view_sync(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_get_feature_view_sync_rest_required_fields(
    request_type=feature_online_store_admin_service.GetFeatureViewSyncRequest,
):
    transport_class = transports.FeatureOnlineStoreAdminServiceRestTransport

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
    ).get_feature_view_sync._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["name"] = "name_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).get_feature_view_sync._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "name" in jsonified_request
    assert jsonified_request["name"] == "name_value"

    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = feature_view_sync.FeatureViewSync()
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
            return_value = feature_view_sync.FeatureViewSync.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.get_feature_view_sync(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_feature_view_sync_rest_unset_required_fields():
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.get_feature_view_sync._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("name",)))


def test_get_feature_view_sync_rest_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = feature_view_sync.FeatureViewSync()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4/featureViewSyncs/sample5"
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
        return_value = feature_view_sync.FeatureViewSync.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.get_feature_view_sync(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/featureViewSyncs/*}"
            % client.transport._host,
            args[1],
        )


def test_get_feature_view_sync_rest_flattened_error(transport: str = "rest"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_feature_view_sync(
            feature_online_store_admin_service.GetFeatureViewSyncRequest(),
            name="name_value",
        )


def test_list_feature_view_syncs_rest_use_cached_wrapped_rpc():
    # Clients should use _prep_wrapped_messages to create cached wrapped rpcs,
    # instead of constructing them on each call
    with mock.patch("google.api_core.gapic_v1.method.wrap_method") as wrapper_fn:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport="rest",
        )

        # Should wrap all calls on client creation
        assert wrapper_fn.call_count > 0
        wrapper_fn.reset_mock()

        # Ensure method has been cached
        assert (
            client._transport.list_feature_view_syncs
            in client._transport._wrapped_methods
        )

        # Replace cached wrapped function with mock
        mock_rpc = mock.Mock()
        mock_rpc.return_value.name = (
            "foo"  # operation_request.operation in compute client(s) expect a string.
        )
        client._transport._wrapped_methods[
            client._transport.list_feature_view_syncs
        ] = mock_rpc

        request = {}
        client.list_feature_view_syncs(request)

        # Establish that the underlying gRPC stub method was called.
        assert mock_rpc.call_count == 1

        client.list_feature_view_syncs(request)

        # Establish that a new wrapper was not created for this call
        assert wrapper_fn.call_count == 0
        assert mock_rpc.call_count == 2


def test_list_feature_view_syncs_rest_required_fields(
    request_type=feature_online_store_admin_service.ListFeatureViewSyncsRequest,
):
    transport_class = transports.FeatureOnlineStoreAdminServiceRestTransport

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
    ).list_feature_view_syncs._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=ga_credentials.AnonymousCredentials()
    ).list_feature_view_syncs._get_unset_required_fields(jsonified_request)
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

    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = feature_online_store_admin_service.ListFeatureViewSyncsResponse()
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
                feature_online_store_admin_service.ListFeatureViewSyncsResponse.pb(
                    return_value
                )
            )
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value
            req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

            response = client.list_feature_view_syncs(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_list_feature_view_syncs_rest_unset_required_fields():
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials
    )

    unset_fields = transport.list_feature_view_syncs._get_unset_required_fields({})
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


def test_list_feature_view_syncs_rest_flattened():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = feature_online_store_admin_service.ListFeatureViewSyncsResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {
            "parent": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
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
        return_value = (
            feature_online_store_admin_service.ListFeatureViewSyncsResponse.pb(
                return_value
            )
        )
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}

        client.list_feature_view_syncs(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v1beta1/{parent=projects/*/locations/*/featureOnlineStores/*/featureViews/*}/featureViewSyncs"
            % client.transport._host,
            args[1],
        )


def test_list_feature_view_syncs_rest_flattened_error(transport: str = "rest"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_feature_view_syncs(
            feature_online_store_admin_service.ListFeatureViewSyncsRequest(),
            parent="parent_value",
        )


def test_list_feature_view_syncs_rest_pager(transport: str = "rest"):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                feature_view_syncs=[
                    feature_view_sync.FeatureViewSync(),
                    feature_view_sync.FeatureViewSync(),
                    feature_view_sync.FeatureViewSync(),
                ],
                next_page_token="abc",
            ),
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                feature_view_syncs=[],
                next_page_token="def",
            ),
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                feature_view_syncs=[
                    feature_view_sync.FeatureViewSync(),
                ],
                next_page_token="ghi",
            ),
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                feature_view_syncs=[
                    feature_view_sync.FeatureViewSync(),
                    feature_view_sync.FeatureViewSync(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(
            feature_online_store_admin_service.ListFeatureViewSyncsResponse.to_json(x)
            for x in response
        )
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {
            "parent": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
        }

        pager = client.list_feature_view_syncs(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, feature_view_sync.FeatureViewSync) for i in results)

        pages = list(client.list_feature_view_syncs(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.FeatureOnlineStoreAdminServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.FeatureOnlineStoreAdminServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = FeatureOnlineStoreAdminServiceClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide an api_key and a transport instance.
    transport = transports.FeatureOnlineStoreAdminServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    options = client_options.ClientOptions()
    options.api_key = "api_key"
    with pytest.raises(ValueError):
        client = FeatureOnlineStoreAdminServiceClient(
            client_options=options,
            transport=transport,
        )

    # It is an error to provide an api_key and a credential.
    options = client_options.ClientOptions()
    options.api_key = "api_key"
    with pytest.raises(ValueError):
        client = FeatureOnlineStoreAdminServiceClient(
            client_options=options, credentials=ga_credentials.AnonymousCredentials()
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.FeatureOnlineStoreAdminServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = FeatureOnlineStoreAdminServiceClient(
            client_options={"scopes": ["1", "2"]},
            transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.FeatureOnlineStoreAdminServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    client = FeatureOnlineStoreAdminServiceClient(transport=transport)
    assert client.transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.FeatureOnlineStoreAdminServiceGrpcTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.FeatureOnlineStoreAdminServiceGrpcAsyncIOTransport(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.FeatureOnlineStoreAdminServiceGrpcTransport,
        transports.FeatureOnlineStoreAdminServiceGrpcAsyncIOTransport,
        transports.FeatureOnlineStoreAdminServiceRestTransport,
    ],
)
def test_transport_adc(transport_class):
    # Test default credentials are used if not provided.
    with mock.patch.object(google.auth, "default") as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport_class()
        adc.assert_called_once()


def test_transport_kind_grpc():
    transport = FeatureOnlineStoreAdminServiceClient.get_transport_class("grpc")(
        credentials=ga_credentials.AnonymousCredentials()
    )
    assert transport.kind == "grpc"


def test_initialize_client_w_grpc():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="grpc"
    )
    assert client is not None


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_create_feature_online_store_empty_call_grpc():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.create_feature_online_store), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.create_feature_online_store(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = (
            feature_online_store_admin_service.CreateFeatureOnlineStoreRequest()
        )

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_feature_online_store_empty_call_grpc():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.get_feature_online_store), "__call__"
    ) as call:
        call.return_value = feature_online_store.FeatureOnlineStore()
        client.get_feature_online_store(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.GetFeatureOnlineStoreRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_feature_online_stores_empty_call_grpc():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_online_stores), "__call__"
    ) as call:
        call.return_value = (
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse()
        )
        client.list_feature_online_stores(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = (
            feature_online_store_admin_service.ListFeatureOnlineStoresRequest()
        )

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_update_feature_online_store_empty_call_grpc():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.update_feature_online_store), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.update_feature_online_store(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = (
            feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest()
        )

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_delete_feature_online_store_empty_call_grpc():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_feature_online_store), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_feature_online_store(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = (
            feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest()
        )

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_create_feature_view_empty_call_grpc():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.create_feature_view), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.create_feature_view(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.CreateFeatureViewRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_feature_view_empty_call_grpc():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.get_feature_view), "__call__") as call:
        call.return_value = feature_view.FeatureView()
        client.get_feature_view(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.GetFeatureViewRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_feature_views_empty_call_grpc():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_views), "__call__"
    ) as call:
        call.return_value = (
            feature_online_store_admin_service.ListFeatureViewsResponse()
        )
        client.list_feature_views(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.ListFeatureViewsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_update_feature_view_empty_call_grpc():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.update_feature_view), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.update_feature_view(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.UpdateFeatureViewRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_delete_feature_view_empty_call_grpc():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_feature_view), "__call__"
    ) as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.delete_feature_view(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.DeleteFeatureViewRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_sync_feature_view_empty_call_grpc():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.sync_feature_view), "__call__"
    ) as call:
        call.return_value = feature_online_store_admin_service.SyncFeatureViewResponse()
        client.sync_feature_view(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.SyncFeatureViewRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_feature_view_sync_empty_call_grpc():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.get_feature_view_sync), "__call__"
    ) as call:
        call.return_value = feature_view_sync.FeatureViewSync()
        client.get_feature_view_sync(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.GetFeatureViewSyncRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_feature_view_syncs_empty_call_grpc():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="grpc",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_view_syncs), "__call__"
    ) as call:
        call.return_value = (
            feature_online_store_admin_service.ListFeatureViewSyncsResponse()
        )
        client.list_feature_view_syncs(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.ListFeatureViewSyncsRequest()

        assert args[0] == request_msg


def test_transport_kind_grpc_asyncio():
    transport = FeatureOnlineStoreAdminServiceAsyncClient.get_transport_class(
        "grpc_asyncio"
    )(credentials=async_anonymous_credentials())
    assert transport.kind == "grpc_asyncio"


def test_initialize_client_w_grpc_asyncio():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="grpc_asyncio"
    )
    assert client is not None


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_create_feature_online_store_empty_call_grpc_asyncio():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.create_feature_online_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        await client.create_feature_online_store(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = (
            feature_online_store_admin_service.CreateFeatureOnlineStoreRequest()
        )

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_feature_online_store_empty_call_grpc_asyncio():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.get_feature_online_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_online_store.FeatureOnlineStore(
                name="name_value",
                etag="etag_value",
                state=feature_online_store.FeatureOnlineStore.State.STABLE,
                satisfies_pzs=True,
                satisfies_pzi=True,
            )
        )
        await client.get_feature_online_store(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.GetFeatureOnlineStoreRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_feature_online_stores_empty_call_grpc_asyncio():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_online_stores), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                next_page_token="next_page_token_value",
            )
        )
        await client.list_feature_online_stores(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = (
            feature_online_store_admin_service.ListFeatureOnlineStoresRequest()
        )

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_update_feature_online_store_empty_call_grpc_asyncio():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.update_feature_online_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        await client.update_feature_online_store(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = (
            feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest()
        )

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_delete_feature_online_store_empty_call_grpc_asyncio():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_feature_online_store), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        await client.delete_feature_online_store(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = (
            feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest()
        )

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_create_feature_view_empty_call_grpc_asyncio():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.create_feature_view), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        await client.create_feature_view(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.CreateFeatureViewRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_feature_view_empty_call_grpc_asyncio():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.get_feature_view), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_view.FeatureView(
                name="name_value",
                etag="etag_value",
                service_agent_type=feature_view.FeatureView.ServiceAgentType.SERVICE_AGENT_TYPE_PROJECT,
                service_account_email="service_account_email_value",
                satisfies_pzs=True,
                satisfies_pzi=True,
            )
        )
        await client.get_feature_view(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.GetFeatureViewRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_feature_views_empty_call_grpc_asyncio():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_views), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_online_store_admin_service.ListFeatureViewsResponse(
                next_page_token="next_page_token_value",
            )
        )
        await client.list_feature_views(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.ListFeatureViewsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_update_feature_view_empty_call_grpc_asyncio():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.update_feature_view), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        await client.update_feature_view(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.UpdateFeatureViewRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_delete_feature_view_empty_call_grpc_asyncio():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_feature_view), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        await client.delete_feature_view(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.DeleteFeatureViewRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_sync_feature_view_empty_call_grpc_asyncio():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.sync_feature_view), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_online_store_admin_service.SyncFeatureViewResponse(
                feature_view_sync="feature_view_sync_value",
            )
        )
        await client.sync_feature_view(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.SyncFeatureViewRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_feature_view_sync_empty_call_grpc_asyncio():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.get_feature_view_sync), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_view_sync.FeatureViewSync(
                name="name_value",
                satisfies_pzs=True,
                satisfies_pzi=True,
            )
        )
        await client.get_feature_view_sync(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.GetFeatureViewSyncRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_feature_view_syncs_empty_call_grpc_asyncio():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="grpc_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_view_syncs), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(
                next_page_token="next_page_token_value",
            )
        )
        await client.list_feature_view_syncs(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.ListFeatureViewSyncsRequest()

        assert args[0] == request_msg


def test_transport_kind_rest():
    transport = FeatureOnlineStoreAdminServiceClient.get_transport_class("rest")(
        credentials=ga_credentials.AnonymousCredentials()
    )
    assert transport.kind == "rest"


def test_create_feature_online_store_rest_bad_request(
    request_type=feature_online_store_admin_service.CreateFeatureOnlineStoreRequest,
):
    client = FeatureOnlineStoreAdminServiceClient(
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
        client.create_feature_online_store(request)


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.CreateFeatureOnlineStoreRequest,
        dict,
    ],
)
def test_create_feature_online_store_rest_call_success(request_type):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request_init["feature_online_store"] = {
        "bigtable": {
            "auto_scaling": {
                "min_node_count": 1489,
                "max_node_count": 1491,
                "cpu_utilization_target": 2377,
            },
            "enable_direct_bigtable_access": True,
            "bigtable_metadata": {
                "tenant_project_id": "tenant_project_id_value",
                "instance_id": "instance_id_value",
                "table_id": "table_id_value",
            },
        },
        "optimized": {},
        "name": "name_value",
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
        "etag": "etag_value",
        "labels": {},
        "state": 1,
        "dedicated_serving_endpoint": {
            "public_endpoint_domain_name": "public_endpoint_domain_name_value",
            "private_service_connect_config": {
                "enable_private_service_connect": True,
                "project_allowlist": [
                    "project_allowlist_value1",
                    "project_allowlist_value2",
                ],
                "psc_automation_configs": [
                    {
                        "project_id": "project_id_value",
                        "network": "network_value",
                        "ip_address": "ip_address_value",
                        "forwarding_rule": "forwarding_rule_value",
                        "state": 1,
                        "error_message": "error_message_value",
                    }
                ],
                "enable_secure_private_service_connect": True,
                "service_attachment": "service_attachment_value",
            },
            "service_attachment": "service_attachment_value",
        },
        "embedding_management": {"enabled": True},
        "encryption_spec": {"kms_key_name": "kms_key_name_value"},
        "satisfies_pzs": True,
        "satisfies_pzi": True,
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = (
        feature_online_store_admin_service.CreateFeatureOnlineStoreRequest.meta.fields[
            "feature_online_store"
        ]
    )

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
        "feature_online_store"
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
                for i in range(0, len(request_init["feature_online_store"][field])):
                    del request_init["feature_online_store"][field][i][subfield]
            else:
                del request_init["feature_online_store"][field][subfield]
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
        response = client.create_feature_online_store(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_create_feature_online_store_rest_interceptors(null_interceptor):
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.FeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_create_feature_online_store",
    ) as post, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_create_feature_online_store_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_create_feature_online_store",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = (
            feature_online_store_admin_service.CreateFeatureOnlineStoreRequest.pb(
                feature_online_store_admin_service.CreateFeatureOnlineStoreRequest()
            )
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

        request = feature_online_store_admin_service.CreateFeatureOnlineStoreRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.create_feature_online_store(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_get_feature_online_store_rest_bad_request(
    request_type=feature_online_store_admin_service.GetFeatureOnlineStoreRequest,
):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
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
        client.get_feature_online_store(request)


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.GetFeatureOnlineStoreRequest,
        dict,
    ],
)
def test_get_feature_online_store_rest_call_success(request_type):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = feature_online_store.FeatureOnlineStore(
            name="name_value",
            etag="etag_value",
            state=feature_online_store.FeatureOnlineStore.State.STABLE,
            satisfies_pzs=True,
            satisfies_pzi=True,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = feature_online_store.FeatureOnlineStore.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.get_feature_online_store(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, feature_online_store.FeatureOnlineStore)
    assert response.name == "name_value"
    assert response.etag == "etag_value"
    assert response.state == feature_online_store.FeatureOnlineStore.State.STABLE
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_feature_online_store_rest_interceptors(null_interceptor):
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.FeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_get_feature_online_store",
    ) as post, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_get_feature_online_store_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_get_feature_online_store",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = feature_online_store_admin_service.GetFeatureOnlineStoreRequest.pb(
            feature_online_store_admin_service.GetFeatureOnlineStoreRequest()
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
        return_value = feature_online_store.FeatureOnlineStore.to_json(
            feature_online_store.FeatureOnlineStore()
        )
        req.return_value.content = return_value

        request = feature_online_store_admin_service.GetFeatureOnlineStoreRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = feature_online_store.FeatureOnlineStore()
        post_with_metadata.return_value = (
            feature_online_store.FeatureOnlineStore(),
            metadata,
        )

        client.get_feature_online_store(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_list_feature_online_stores_rest_bad_request(
    request_type=feature_online_store_admin_service.ListFeatureOnlineStoresRequest,
):
    client = FeatureOnlineStoreAdminServiceClient(
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
        client.list_feature_online_stores(request)


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.ListFeatureOnlineStoresRequest,
        dict,
    ],
)
def test_list_feature_online_stores_rest_call_success(request_type):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = (
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                next_page_token="next_page_token_value",
            )
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = (
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse.pb(
                return_value
            )
        )
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.list_feature_online_stores(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListFeatureOnlineStoresPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_feature_online_stores_rest_interceptors(null_interceptor):
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.FeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_list_feature_online_stores",
    ) as post, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_list_feature_online_stores_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_list_feature_online_stores",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = (
            feature_online_store_admin_service.ListFeatureOnlineStoresRequest.pb(
                feature_online_store_admin_service.ListFeatureOnlineStoresRequest()
            )
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
        return_value = (
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse.to_json(
                feature_online_store_admin_service.ListFeatureOnlineStoresResponse()
            )
        )
        req.return_value.content = return_value

        request = feature_online_store_admin_service.ListFeatureOnlineStoresRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = (
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse()
        )
        post_with_metadata.return_value = (
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(),
            metadata,
        )

        client.list_feature_online_stores(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_update_feature_online_store_rest_bad_request(
    request_type=feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest,
):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "feature_online_store": {
            "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
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
        client.update_feature_online_store(request)


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest,
        dict,
    ],
)
def test_update_feature_online_store_rest_call_success(request_type):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "feature_online_store": {
            "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
        }
    }
    request_init["feature_online_store"] = {
        "bigtable": {
            "auto_scaling": {
                "min_node_count": 1489,
                "max_node_count": 1491,
                "cpu_utilization_target": 2377,
            },
            "enable_direct_bigtable_access": True,
            "bigtable_metadata": {
                "tenant_project_id": "tenant_project_id_value",
                "instance_id": "instance_id_value",
                "table_id": "table_id_value",
            },
        },
        "optimized": {},
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3",
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
        "etag": "etag_value",
        "labels": {},
        "state": 1,
        "dedicated_serving_endpoint": {
            "public_endpoint_domain_name": "public_endpoint_domain_name_value",
            "private_service_connect_config": {
                "enable_private_service_connect": True,
                "project_allowlist": [
                    "project_allowlist_value1",
                    "project_allowlist_value2",
                ],
                "psc_automation_configs": [
                    {
                        "project_id": "project_id_value",
                        "network": "network_value",
                        "ip_address": "ip_address_value",
                        "forwarding_rule": "forwarding_rule_value",
                        "state": 1,
                        "error_message": "error_message_value",
                    }
                ],
                "enable_secure_private_service_connect": True,
                "service_attachment": "service_attachment_value",
            },
            "service_attachment": "service_attachment_value",
        },
        "embedding_management": {"enabled": True},
        "encryption_spec": {"kms_key_name": "kms_key_name_value"},
        "satisfies_pzs": True,
        "satisfies_pzi": True,
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = (
        feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest.meta.fields[
            "feature_online_store"
        ]
    )

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
        "feature_online_store"
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
                for i in range(0, len(request_init["feature_online_store"][field])):
                    del request_init["feature_online_store"][field][i][subfield]
            else:
                del request_init["feature_online_store"][field][subfield]
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
        response = client.update_feature_online_store(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_update_feature_online_store_rest_interceptors(null_interceptor):
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.FeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_update_feature_online_store",
    ) as post, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_update_feature_online_store_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_update_feature_online_store",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = (
            feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest.pb(
                feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest()
            )
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

        request = feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.update_feature_online_store(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_delete_feature_online_store_rest_bad_request(
    request_type=feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest,
):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
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
        client.delete_feature_online_store(request)


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest,
        dict,
    ],
)
def test_delete_feature_online_store_rest_call_success(request_type):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
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
        response = client.delete_feature_online_store(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_delete_feature_online_store_rest_interceptors(null_interceptor):
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.FeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_delete_feature_online_store",
    ) as post, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_delete_feature_online_store_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_delete_feature_online_store",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = (
            feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest.pb(
                feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest()
            )
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

        request = feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.delete_feature_online_store(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_create_feature_view_rest_bad_request(
    request_type=feature_online_store_admin_service.CreateFeatureViewRequest,
):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "parent": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
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
        client.create_feature_view(request)


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.CreateFeatureViewRequest,
        dict,
    ],
)
def test_create_feature_view_rest_call_success(request_type):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "parent": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
    }
    request_init["feature_view"] = {
        "big_query_source": {
            "uri": "uri_value",
            "entity_id_columns": [
                "entity_id_columns_value1",
                "entity_id_columns_value2",
            ],
        },
        "feature_registry_source": {
            "feature_groups": [
                {
                    "feature_group_id": "feature_group_id_value",
                    "feature_ids": ["feature_ids_value1", "feature_ids_value2"],
                }
            ],
            "project_number": 1503,
        },
        "vertex_rag_source": {"uri": "uri_value", "rag_corpus_id": 1377},
        "name": "name_value",
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
        "etag": "etag_value",
        "labels": {},
        "sync_config": {"cron": "cron_value"},
        "vector_search_config": {
            "tree_ah_config": {"leaf_node_embedding_count": 2595},
            "brute_force_config": {},
            "embedding_column": "embedding_column_value",
            "filter_columns": ["filter_columns_value1", "filter_columns_value2"],
            "crowding_column": "crowding_column_value",
            "embedding_dimension": 1988,
            "distance_measure_type": 1,
        },
        "index_config": {
            "tree_ah_config": {"leaf_node_embedding_count": 2595},
            "brute_force_config": {},
            "embedding_column": "embedding_column_value",
            "filter_columns": ["filter_columns_value1", "filter_columns_value2"],
            "crowding_column": "crowding_column_value",
            "embedding_dimension": 1988,
            "distance_measure_type": 1,
        },
        "optimized_config": {
            "automatic_resources": {
                "min_replica_count": 1803,
                "max_replica_count": 1805,
            }
        },
        "service_agent_type": 1,
        "service_account_email": "service_account_email_value",
        "satisfies_pzs": True,
        "satisfies_pzi": True,
        "bigtable_metadata": {"read_app_profile": "read_app_profile_value"},
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = (
        feature_online_store_admin_service.CreateFeatureViewRequest.meta.fields[
            "feature_view"
        ]
    )

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
    for field, value in request_init["feature_view"].items():  # pragma: NO COVER
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
                for i in range(0, len(request_init["feature_view"][field])):
                    del request_init["feature_view"][field][i][subfield]
            else:
                del request_init["feature_view"][field][subfield]
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
        response = client.create_feature_view(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_create_feature_view_rest_interceptors(null_interceptor):
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.FeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_create_feature_view",
    ) as post, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_create_feature_view_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_create_feature_view",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = feature_online_store_admin_service.CreateFeatureViewRequest.pb(
            feature_online_store_admin_service.CreateFeatureViewRequest()
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

        request = feature_online_store_admin_service.CreateFeatureViewRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.create_feature_view(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_get_feature_view_rest_bad_request(
    request_type=feature_online_store_admin_service.GetFeatureViewRequest,
):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
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
        client.get_feature_view(request)


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.GetFeatureViewRequest,
        dict,
    ],
)
def test_get_feature_view_rest_call_success(request_type):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = feature_view.FeatureView(
            name="name_value",
            etag="etag_value",
            service_agent_type=feature_view.FeatureView.ServiceAgentType.SERVICE_AGENT_TYPE_PROJECT,
            service_account_email="service_account_email_value",
            satisfies_pzs=True,
            satisfies_pzi=True,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = feature_view.FeatureView.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.get_feature_view(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, feature_view.FeatureView)
    assert response.name == "name_value"
    assert response.etag == "etag_value"
    assert (
        response.service_agent_type
        == feature_view.FeatureView.ServiceAgentType.SERVICE_AGENT_TYPE_PROJECT
    )
    assert response.service_account_email == "service_account_email_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_feature_view_rest_interceptors(null_interceptor):
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.FeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_get_feature_view",
    ) as post, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_get_feature_view_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor, "pre_get_feature_view"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = feature_online_store_admin_service.GetFeatureViewRequest.pb(
            feature_online_store_admin_service.GetFeatureViewRequest()
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
        return_value = feature_view.FeatureView.to_json(feature_view.FeatureView())
        req.return_value.content = return_value

        request = feature_online_store_admin_service.GetFeatureViewRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = feature_view.FeatureView()
        post_with_metadata.return_value = feature_view.FeatureView(), metadata

        client.get_feature_view(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_list_feature_views_rest_bad_request(
    request_type=feature_online_store_admin_service.ListFeatureViewsRequest,
):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "parent": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
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
        client.list_feature_views(request)


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.ListFeatureViewsRequest,
        dict,
    ],
)
def test_list_feature_views_rest_call_success(request_type):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "parent": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = feature_online_store_admin_service.ListFeatureViewsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = feature_online_store_admin_service.ListFeatureViewsResponse.pb(
            return_value
        )
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.list_feature_views(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListFeatureViewsPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_feature_views_rest_interceptors(null_interceptor):
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.FeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_list_feature_views",
    ) as post, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_list_feature_views_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_list_feature_views",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = feature_online_store_admin_service.ListFeatureViewsRequest.pb(
            feature_online_store_admin_service.ListFeatureViewsRequest()
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
        return_value = (
            feature_online_store_admin_service.ListFeatureViewsResponse.to_json(
                feature_online_store_admin_service.ListFeatureViewsResponse()
            )
        )
        req.return_value.content = return_value

        request = feature_online_store_admin_service.ListFeatureViewsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = (
            feature_online_store_admin_service.ListFeatureViewsResponse()
        )
        post_with_metadata.return_value = (
            feature_online_store_admin_service.ListFeatureViewsResponse(),
            metadata,
        )

        client.list_feature_views(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_update_feature_view_rest_bad_request(
    request_type=feature_online_store_admin_service.UpdateFeatureViewRequest,
):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "feature_view": {
            "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
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
        client.update_feature_view(request)


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.UpdateFeatureViewRequest,
        dict,
    ],
)
def test_update_feature_view_rest_call_success(request_type):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "feature_view": {
            "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
        }
    }
    request_init["feature_view"] = {
        "big_query_source": {
            "uri": "uri_value",
            "entity_id_columns": [
                "entity_id_columns_value1",
                "entity_id_columns_value2",
            ],
        },
        "feature_registry_source": {
            "feature_groups": [
                {
                    "feature_group_id": "feature_group_id_value",
                    "feature_ids": ["feature_ids_value1", "feature_ids_value2"],
                }
            ],
            "project_number": 1503,
        },
        "vertex_rag_source": {"uri": "uri_value", "rag_corpus_id": 1377},
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4",
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
        "etag": "etag_value",
        "labels": {},
        "sync_config": {"cron": "cron_value"},
        "vector_search_config": {
            "tree_ah_config": {"leaf_node_embedding_count": 2595},
            "brute_force_config": {},
            "embedding_column": "embedding_column_value",
            "filter_columns": ["filter_columns_value1", "filter_columns_value2"],
            "crowding_column": "crowding_column_value",
            "embedding_dimension": 1988,
            "distance_measure_type": 1,
        },
        "index_config": {
            "tree_ah_config": {"leaf_node_embedding_count": 2595},
            "brute_force_config": {},
            "embedding_column": "embedding_column_value",
            "filter_columns": ["filter_columns_value1", "filter_columns_value2"],
            "crowding_column": "crowding_column_value",
            "embedding_dimension": 1988,
            "distance_measure_type": 1,
        },
        "optimized_config": {
            "automatic_resources": {
                "min_replica_count": 1803,
                "max_replica_count": 1805,
            }
        },
        "service_agent_type": 1,
        "service_account_email": "service_account_email_value",
        "satisfies_pzs": True,
        "satisfies_pzi": True,
        "bigtable_metadata": {"read_app_profile": "read_app_profile_value"},
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = (
        feature_online_store_admin_service.UpdateFeatureViewRequest.meta.fields[
            "feature_view"
        ]
    )

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
    for field, value in request_init["feature_view"].items():  # pragma: NO COVER
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
                for i in range(0, len(request_init["feature_view"][field])):
                    del request_init["feature_view"][field][i][subfield]
            else:
                del request_init["feature_view"][field][subfield]
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
        response = client.update_feature_view(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_update_feature_view_rest_interceptors(null_interceptor):
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.FeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_update_feature_view",
    ) as post, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_update_feature_view_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_update_feature_view",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = feature_online_store_admin_service.UpdateFeatureViewRequest.pb(
            feature_online_store_admin_service.UpdateFeatureViewRequest()
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

        request = feature_online_store_admin_service.UpdateFeatureViewRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.update_feature_view(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_delete_feature_view_rest_bad_request(
    request_type=feature_online_store_admin_service.DeleteFeatureViewRequest,
):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
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
        client.delete_feature_view(request)


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.DeleteFeatureViewRequest,
        dict,
    ],
)
def test_delete_feature_view_rest_call_success(request_type):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
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
        response = client.delete_feature_view(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_delete_feature_view_rest_interceptors(null_interceptor):
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.FeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_delete_feature_view",
    ) as post, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_delete_feature_view_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_delete_feature_view",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = feature_online_store_admin_service.DeleteFeatureViewRequest.pb(
            feature_online_store_admin_service.DeleteFeatureViewRequest()
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

        request = feature_online_store_admin_service.DeleteFeatureViewRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        client.delete_feature_view(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_sync_feature_view_rest_bad_request(
    request_type=feature_online_store_admin_service.SyncFeatureViewRequest,
):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "feature_view": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
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
        client.sync_feature_view(request)


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.SyncFeatureViewRequest,
        dict,
    ],
)
def test_sync_feature_view_rest_call_success(request_type):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "feature_view": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = feature_online_store_admin_service.SyncFeatureViewResponse(
            feature_view_sync="feature_view_sync_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = feature_online_store_admin_service.SyncFeatureViewResponse.pb(
            return_value
        )
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.sync_feature_view(request)

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, feature_online_store_admin_service.SyncFeatureViewResponse
    )
    assert response.feature_view_sync == "feature_view_sync_value"


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_sync_feature_view_rest_interceptors(null_interceptor):
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.FeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_sync_feature_view",
    ) as post, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_sync_feature_view_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_sync_feature_view",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = feature_online_store_admin_service.SyncFeatureViewRequest.pb(
            feature_online_store_admin_service.SyncFeatureViewRequest()
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
        return_value = (
            feature_online_store_admin_service.SyncFeatureViewResponse.to_json(
                feature_online_store_admin_service.SyncFeatureViewResponse()
            )
        )
        req.return_value.content = return_value

        request = feature_online_store_admin_service.SyncFeatureViewRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = feature_online_store_admin_service.SyncFeatureViewResponse()
        post_with_metadata.return_value = (
            feature_online_store_admin_service.SyncFeatureViewResponse(),
            metadata,
        )

        client.sync_feature_view(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_get_feature_view_sync_rest_bad_request(
    request_type=feature_online_store_admin_service.GetFeatureViewSyncRequest,
):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4/featureViewSyncs/sample5"
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
        client.get_feature_view_sync(request)


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.GetFeatureViewSyncRequest,
        dict,
    ],
)
def test_get_feature_view_sync_rest_call_success(request_type):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4/featureViewSyncs/sample5"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = feature_view_sync.FeatureViewSync(
            name="name_value",
            satisfies_pzs=True,
            satisfies_pzi=True,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = feature_view_sync.FeatureViewSync.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.get_feature_view_sync(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, feature_view_sync.FeatureViewSync)
    assert response.name == "name_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_feature_view_sync_rest_interceptors(null_interceptor):
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.FeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_get_feature_view_sync",
    ) as post, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_get_feature_view_sync_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_get_feature_view_sync",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = feature_online_store_admin_service.GetFeatureViewSyncRequest.pb(
            feature_online_store_admin_service.GetFeatureViewSyncRequest()
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
        return_value = feature_view_sync.FeatureViewSync.to_json(
            feature_view_sync.FeatureViewSync()
        )
        req.return_value.content = return_value

        request = feature_online_store_admin_service.GetFeatureViewSyncRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = feature_view_sync.FeatureViewSync()
        post_with_metadata.return_value = feature_view_sync.FeatureViewSync(), metadata

        client.get_feature_view_sync(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()
        post_with_metadata.assert_called_once()


def test_list_feature_view_syncs_rest_bad_request(
    request_type=feature_online_store_admin_service.ListFeatureViewSyncsRequest,
):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "parent": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
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
        client.list_feature_view_syncs(request)


@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.ListFeatureViewSyncsRequest,
        dict,
    ],
)
def test_list_feature_view_syncs_rest_call_success(request_type):
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "parent": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = feature_online_store_admin_service.ListFeatureViewSyncsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = (
            feature_online_store_admin_service.ListFeatureViewSyncsResponse.pb(
                return_value
            )
        )
        json_return_value = json_format.MessageToJson(return_value)
        response_value.content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = client.list_feature_view_syncs(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListFeatureViewSyncsPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_list_feature_view_syncs_rest_interceptors(null_interceptor):
    transport = transports.FeatureOnlineStoreAdminServiceRestTransport(
        credentials=ga_credentials.AnonymousCredentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.FeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_list_feature_view_syncs",
    ) as post, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "post_list_feature_view_syncs_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_list_feature_view_syncs",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = feature_online_store_admin_service.ListFeatureViewSyncsRequest.pb(
            feature_online_store_admin_service.ListFeatureViewSyncsRequest()
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
        return_value = (
            feature_online_store_admin_service.ListFeatureViewSyncsResponse.to_json(
                feature_online_store_admin_service.ListFeatureViewSyncsResponse()
            )
        )
        req.return_value.content = return_value

        request = feature_online_store_admin_service.ListFeatureViewSyncsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = (
            feature_online_store_admin_service.ListFeatureViewSyncsResponse()
        )
        post_with_metadata.return_value = (
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(),
            metadata,
        )

        client.list_feature_view_syncs(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(), transport="rest"
    )
    assert client is not None


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_create_feature_online_store_empty_call_rest():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.create_feature_online_store), "__call__"
    ) as call:
        client.create_feature_online_store(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = (
            feature_online_store_admin_service.CreateFeatureOnlineStoreRequest()
        )

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_feature_online_store_empty_call_rest():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.get_feature_online_store), "__call__"
    ) as call:
        client.get_feature_online_store(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.GetFeatureOnlineStoreRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_feature_online_stores_empty_call_rest():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_online_stores), "__call__"
    ) as call:
        client.list_feature_online_stores(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = (
            feature_online_store_admin_service.ListFeatureOnlineStoresRequest()
        )

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_update_feature_online_store_empty_call_rest():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.update_feature_online_store), "__call__"
    ) as call:
        client.update_feature_online_store(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = (
            feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest()
        )

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_delete_feature_online_store_empty_call_rest():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_feature_online_store), "__call__"
    ) as call:
        client.delete_feature_online_store(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = (
            feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest()
        )

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_create_feature_view_empty_call_rest():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.create_feature_view), "__call__"
    ) as call:
        client.create_feature_view(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.CreateFeatureViewRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_feature_view_empty_call_rest():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.get_feature_view), "__call__") as call:
        client.get_feature_view(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.GetFeatureViewRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_feature_views_empty_call_rest():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_views), "__call__"
    ) as call:
        client.list_feature_views(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.ListFeatureViewsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_update_feature_view_empty_call_rest():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.update_feature_view), "__call__"
    ) as call:
        client.update_feature_view(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.UpdateFeatureViewRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_delete_feature_view_empty_call_rest():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_feature_view), "__call__"
    ) as call:
        client.delete_feature_view(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.DeleteFeatureViewRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_sync_feature_view_empty_call_rest():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.sync_feature_view), "__call__"
    ) as call:
        client.sync_feature_view(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.SyncFeatureViewRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_get_feature_view_sync_empty_call_rest():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.get_feature_view_sync), "__call__"
    ) as call:
        client.get_feature_view_sync(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.GetFeatureViewSyncRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
def test_list_feature_view_syncs_empty_call_rest():
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
        transport="rest",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_view_syncs), "__call__"
    ) as call:
        client.list_feature_view_syncs(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.ListFeatureViewSyncsRequest()

        assert args[0] == request_msg


def test_feature_online_store_admin_service_rest_lro_client():
    client = FeatureOnlineStoreAdminServiceClient(
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
    transport = FeatureOnlineStoreAdminServiceAsyncClient.get_transport_class(
        "rest_asyncio"
    )(credentials=async_anonymous_credentials())
    assert transport.kind == "rest_asyncio"


@pytest.mark.asyncio
async def test_create_feature_online_store_rest_asyncio_bad_request(
    request_type=feature_online_store_admin_service.CreateFeatureOnlineStoreRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
        await client.create_feature_online_store(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.CreateFeatureOnlineStoreRequest,
        dict,
    ],
)
async def test_create_feature_online_store_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request_init["feature_online_store"] = {
        "bigtable": {
            "auto_scaling": {
                "min_node_count": 1489,
                "max_node_count": 1491,
                "cpu_utilization_target": 2377,
            },
            "enable_direct_bigtable_access": True,
            "bigtable_metadata": {
                "tenant_project_id": "tenant_project_id_value",
                "instance_id": "instance_id_value",
                "table_id": "table_id_value",
            },
        },
        "optimized": {},
        "name": "name_value",
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
        "etag": "etag_value",
        "labels": {},
        "state": 1,
        "dedicated_serving_endpoint": {
            "public_endpoint_domain_name": "public_endpoint_domain_name_value",
            "private_service_connect_config": {
                "enable_private_service_connect": True,
                "project_allowlist": [
                    "project_allowlist_value1",
                    "project_allowlist_value2",
                ],
                "psc_automation_configs": [
                    {
                        "project_id": "project_id_value",
                        "network": "network_value",
                        "ip_address": "ip_address_value",
                        "forwarding_rule": "forwarding_rule_value",
                        "state": 1,
                        "error_message": "error_message_value",
                    }
                ],
                "enable_secure_private_service_connect": True,
                "service_attachment": "service_attachment_value",
            },
            "service_attachment": "service_attachment_value",
        },
        "embedding_management": {"enabled": True},
        "encryption_spec": {"kms_key_name": "kms_key_name_value"},
        "satisfies_pzs": True,
        "satisfies_pzi": True,
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = (
        feature_online_store_admin_service.CreateFeatureOnlineStoreRequest.meta.fields[
            "feature_online_store"
        ]
    )

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
        "feature_online_store"
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
                for i in range(0, len(request_init["feature_online_store"][field])):
                    del request_init["feature_online_store"][field][i][subfield]
            else:
                del request_init["feature_online_store"][field][subfield]
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
        response = await client.create_feature_online_store(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_create_feature_online_store_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncFeatureOnlineStoreAdminServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_create_feature_online_store",
    ) as post, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_create_feature_online_store_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_create_feature_online_store",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = (
            feature_online_store_admin_service.CreateFeatureOnlineStoreRequest.pb(
                feature_online_store_admin_service.CreateFeatureOnlineStoreRequest()
            )
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

        request = feature_online_store_admin_service.CreateFeatureOnlineStoreRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.create_feature_online_store(
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
async def test_get_feature_online_store_rest_asyncio_bad_request(
    request_type=feature_online_store_admin_service.GetFeatureOnlineStoreRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
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
        await client.get_feature_online_store(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.GetFeatureOnlineStoreRequest,
        dict,
    ],
)
async def test_get_feature_online_store_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = feature_online_store.FeatureOnlineStore(
            name="name_value",
            etag="etag_value",
            state=feature_online_store.FeatureOnlineStore.State.STABLE,
            satisfies_pzs=True,
            satisfies_pzi=True,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = feature_online_store.FeatureOnlineStore.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.get_feature_online_store(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, feature_online_store.FeatureOnlineStore)
    assert response.name == "name_value"
    assert response.etag == "etag_value"
    assert response.state == feature_online_store.FeatureOnlineStore.State.STABLE
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_get_feature_online_store_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncFeatureOnlineStoreAdminServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_get_feature_online_store",
    ) as post, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_get_feature_online_store_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_get_feature_online_store",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = feature_online_store_admin_service.GetFeatureOnlineStoreRequest.pb(
            feature_online_store_admin_service.GetFeatureOnlineStoreRequest()
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
        return_value = feature_online_store.FeatureOnlineStore.to_json(
            feature_online_store.FeatureOnlineStore()
        )
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = feature_online_store_admin_service.GetFeatureOnlineStoreRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = feature_online_store.FeatureOnlineStore()
        post_with_metadata.return_value = (
            feature_online_store.FeatureOnlineStore(),
            metadata,
        )

        await client.get_feature_online_store(
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
async def test_list_feature_online_stores_rest_asyncio_bad_request(
    request_type=feature_online_store_admin_service.ListFeatureOnlineStoresRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
        await client.list_feature_online_stores(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.ListFeatureOnlineStoresRequest,
        dict,
    ],
)
async def test_list_feature_online_stores_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = (
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(
                next_page_token="next_page_token_value",
            )
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = (
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse.pb(
                return_value
            )
        )
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.list_feature_online_stores(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListFeatureOnlineStoresAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_list_feature_online_stores_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncFeatureOnlineStoreAdminServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_list_feature_online_stores",
    ) as post, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_list_feature_online_stores_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_list_feature_online_stores",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = (
            feature_online_store_admin_service.ListFeatureOnlineStoresRequest.pb(
                feature_online_store_admin_service.ListFeatureOnlineStoresRequest()
            )
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
        return_value = (
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse.to_json(
                feature_online_store_admin_service.ListFeatureOnlineStoresResponse()
            )
        )
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = feature_online_store_admin_service.ListFeatureOnlineStoresRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = (
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse()
        )
        post_with_metadata.return_value = (
            feature_online_store_admin_service.ListFeatureOnlineStoresResponse(),
            metadata,
        )

        await client.list_feature_online_stores(
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
async def test_update_feature_online_store_rest_asyncio_bad_request(
    request_type=feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "feature_online_store": {
            "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
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
        await client.update_feature_online_store(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest,
        dict,
    ],
)
async def test_update_feature_online_store_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "feature_online_store": {
            "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
        }
    }
    request_init["feature_online_store"] = {
        "bigtable": {
            "auto_scaling": {
                "min_node_count": 1489,
                "max_node_count": 1491,
                "cpu_utilization_target": 2377,
            },
            "enable_direct_bigtable_access": True,
            "bigtable_metadata": {
                "tenant_project_id": "tenant_project_id_value",
                "instance_id": "instance_id_value",
                "table_id": "table_id_value",
            },
        },
        "optimized": {},
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3",
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
        "etag": "etag_value",
        "labels": {},
        "state": 1,
        "dedicated_serving_endpoint": {
            "public_endpoint_domain_name": "public_endpoint_domain_name_value",
            "private_service_connect_config": {
                "enable_private_service_connect": True,
                "project_allowlist": [
                    "project_allowlist_value1",
                    "project_allowlist_value2",
                ],
                "psc_automation_configs": [
                    {
                        "project_id": "project_id_value",
                        "network": "network_value",
                        "ip_address": "ip_address_value",
                        "forwarding_rule": "forwarding_rule_value",
                        "state": 1,
                        "error_message": "error_message_value",
                    }
                ],
                "enable_secure_private_service_connect": True,
                "service_attachment": "service_attachment_value",
            },
            "service_attachment": "service_attachment_value",
        },
        "embedding_management": {"enabled": True},
        "encryption_spec": {"kms_key_name": "kms_key_name_value"},
        "satisfies_pzs": True,
        "satisfies_pzi": True,
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = (
        feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest.meta.fields[
            "feature_online_store"
        ]
    )

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
        "feature_online_store"
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
                for i in range(0, len(request_init["feature_online_store"][field])):
                    del request_init["feature_online_store"][field][i][subfield]
            else:
                del request_init["feature_online_store"][field][subfield]
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
        response = await client.update_feature_online_store(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_update_feature_online_store_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncFeatureOnlineStoreAdminServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_update_feature_online_store",
    ) as post, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_update_feature_online_store_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_update_feature_online_store",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = (
            feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest.pb(
                feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest()
            )
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

        request = feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.update_feature_online_store(
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
async def test_delete_feature_online_store_rest_asyncio_bad_request(
    request_type=feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
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
        await client.delete_feature_online_store(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest,
        dict,
    ],
)
async def test_delete_feature_online_store_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
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
        response = await client.delete_feature_online_store(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_delete_feature_online_store_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncFeatureOnlineStoreAdminServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_delete_feature_online_store",
    ) as post, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_delete_feature_online_store_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_delete_feature_online_store",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = (
            feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest.pb(
                feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest()
            )
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

        request = feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.delete_feature_online_store(
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
async def test_create_feature_view_rest_asyncio_bad_request(
    request_type=feature_online_store_admin_service.CreateFeatureViewRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "parent": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
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
        await client.create_feature_view(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.CreateFeatureViewRequest,
        dict,
    ],
)
async def test_create_feature_view_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "parent": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
    }
    request_init["feature_view"] = {
        "big_query_source": {
            "uri": "uri_value",
            "entity_id_columns": [
                "entity_id_columns_value1",
                "entity_id_columns_value2",
            ],
        },
        "feature_registry_source": {
            "feature_groups": [
                {
                    "feature_group_id": "feature_group_id_value",
                    "feature_ids": ["feature_ids_value1", "feature_ids_value2"],
                }
            ],
            "project_number": 1503,
        },
        "vertex_rag_source": {"uri": "uri_value", "rag_corpus_id": 1377},
        "name": "name_value",
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
        "etag": "etag_value",
        "labels": {},
        "sync_config": {"cron": "cron_value"},
        "vector_search_config": {
            "tree_ah_config": {"leaf_node_embedding_count": 2595},
            "brute_force_config": {},
            "embedding_column": "embedding_column_value",
            "filter_columns": ["filter_columns_value1", "filter_columns_value2"],
            "crowding_column": "crowding_column_value",
            "embedding_dimension": 1988,
            "distance_measure_type": 1,
        },
        "index_config": {
            "tree_ah_config": {"leaf_node_embedding_count": 2595},
            "brute_force_config": {},
            "embedding_column": "embedding_column_value",
            "filter_columns": ["filter_columns_value1", "filter_columns_value2"],
            "crowding_column": "crowding_column_value",
            "embedding_dimension": 1988,
            "distance_measure_type": 1,
        },
        "optimized_config": {
            "automatic_resources": {
                "min_replica_count": 1803,
                "max_replica_count": 1805,
            }
        },
        "service_agent_type": 1,
        "service_account_email": "service_account_email_value",
        "satisfies_pzs": True,
        "satisfies_pzi": True,
        "bigtable_metadata": {"read_app_profile": "read_app_profile_value"},
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = (
        feature_online_store_admin_service.CreateFeatureViewRequest.meta.fields[
            "feature_view"
        ]
    )

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
    for field, value in request_init["feature_view"].items():  # pragma: NO COVER
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
                for i in range(0, len(request_init["feature_view"][field])):
                    del request_init["feature_view"][field][i][subfield]
            else:
                del request_init["feature_view"][field][subfield]
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
        response = await client.create_feature_view(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_create_feature_view_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncFeatureOnlineStoreAdminServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_create_feature_view",
    ) as post, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_create_feature_view_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_create_feature_view",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = feature_online_store_admin_service.CreateFeatureViewRequest.pb(
            feature_online_store_admin_service.CreateFeatureViewRequest()
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

        request = feature_online_store_admin_service.CreateFeatureViewRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.create_feature_view(
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
async def test_get_feature_view_rest_asyncio_bad_request(
    request_type=feature_online_store_admin_service.GetFeatureViewRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
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
        await client.get_feature_view(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.GetFeatureViewRequest,
        dict,
    ],
)
async def test_get_feature_view_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = feature_view.FeatureView(
            name="name_value",
            etag="etag_value",
            service_agent_type=feature_view.FeatureView.ServiceAgentType.SERVICE_AGENT_TYPE_PROJECT,
            service_account_email="service_account_email_value",
            satisfies_pzs=True,
            satisfies_pzi=True,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = feature_view.FeatureView.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.get_feature_view(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, feature_view.FeatureView)
    assert response.name == "name_value"
    assert response.etag == "etag_value"
    assert (
        response.service_agent_type
        == feature_view.FeatureView.ServiceAgentType.SERVICE_AGENT_TYPE_PROJECT
    )
    assert response.service_account_email == "service_account_email_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_get_feature_view_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncFeatureOnlineStoreAdminServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_get_feature_view",
    ) as post, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_get_feature_view_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_get_feature_view",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = feature_online_store_admin_service.GetFeatureViewRequest.pb(
            feature_online_store_admin_service.GetFeatureViewRequest()
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
        return_value = feature_view.FeatureView.to_json(feature_view.FeatureView())
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = feature_online_store_admin_service.GetFeatureViewRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = feature_view.FeatureView()
        post_with_metadata.return_value = feature_view.FeatureView(), metadata

        await client.get_feature_view(
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
async def test_list_feature_views_rest_asyncio_bad_request(
    request_type=feature_online_store_admin_service.ListFeatureViewsRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "parent": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
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
        await client.list_feature_views(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.ListFeatureViewsRequest,
        dict,
    ],
)
async def test_list_feature_views_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "parent": "projects/sample1/locations/sample2/featureOnlineStores/sample3"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = feature_online_store_admin_service.ListFeatureViewsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = feature_online_store_admin_service.ListFeatureViewsResponse.pb(
            return_value
        )
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.list_feature_views(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListFeatureViewsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_list_feature_views_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncFeatureOnlineStoreAdminServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_list_feature_views",
    ) as post, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_list_feature_views_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_list_feature_views",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = feature_online_store_admin_service.ListFeatureViewsRequest.pb(
            feature_online_store_admin_service.ListFeatureViewsRequest()
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
        return_value = (
            feature_online_store_admin_service.ListFeatureViewsResponse.to_json(
                feature_online_store_admin_service.ListFeatureViewsResponse()
            )
        )
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = feature_online_store_admin_service.ListFeatureViewsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = (
            feature_online_store_admin_service.ListFeatureViewsResponse()
        )
        post_with_metadata.return_value = (
            feature_online_store_admin_service.ListFeatureViewsResponse(),
            metadata,
        )

        await client.list_feature_views(
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
async def test_update_feature_view_rest_asyncio_bad_request(
    request_type=feature_online_store_admin_service.UpdateFeatureViewRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "feature_view": {
            "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
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
        await client.update_feature_view(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.UpdateFeatureViewRequest,
        dict,
    ],
)
async def test_update_feature_view_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "feature_view": {
            "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
        }
    }
    request_init["feature_view"] = {
        "big_query_source": {
            "uri": "uri_value",
            "entity_id_columns": [
                "entity_id_columns_value1",
                "entity_id_columns_value2",
            ],
        },
        "feature_registry_source": {
            "feature_groups": [
                {
                    "feature_group_id": "feature_group_id_value",
                    "feature_ids": ["feature_ids_value1", "feature_ids_value2"],
                }
            ],
            "project_number": 1503,
        },
        "vertex_rag_source": {"uri": "uri_value", "rag_corpus_id": 1377},
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4",
        "create_time": {"seconds": 751, "nanos": 543},
        "update_time": {},
        "etag": "etag_value",
        "labels": {},
        "sync_config": {"cron": "cron_value"},
        "vector_search_config": {
            "tree_ah_config": {"leaf_node_embedding_count": 2595},
            "brute_force_config": {},
            "embedding_column": "embedding_column_value",
            "filter_columns": ["filter_columns_value1", "filter_columns_value2"],
            "crowding_column": "crowding_column_value",
            "embedding_dimension": 1988,
            "distance_measure_type": 1,
        },
        "index_config": {
            "tree_ah_config": {"leaf_node_embedding_count": 2595},
            "brute_force_config": {},
            "embedding_column": "embedding_column_value",
            "filter_columns": ["filter_columns_value1", "filter_columns_value2"],
            "crowding_column": "crowding_column_value",
            "embedding_dimension": 1988,
            "distance_measure_type": 1,
        },
        "optimized_config": {
            "automatic_resources": {
                "min_replica_count": 1803,
                "max_replica_count": 1805,
            }
        },
        "service_agent_type": 1,
        "service_account_email": "service_account_email_value",
        "satisfies_pzs": True,
        "satisfies_pzi": True,
        "bigtable_metadata": {"read_app_profile": "read_app_profile_value"},
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = (
        feature_online_store_admin_service.UpdateFeatureViewRequest.meta.fields[
            "feature_view"
        ]
    )

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
    for field, value in request_init["feature_view"].items():  # pragma: NO COVER
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
                for i in range(0, len(request_init["feature_view"][field])):
                    del request_init["feature_view"][field][i][subfield]
            else:
                del request_init["feature_view"][field][subfield]
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
        response = await client.update_feature_view(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_update_feature_view_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncFeatureOnlineStoreAdminServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_update_feature_view",
    ) as post, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_update_feature_view_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_update_feature_view",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = feature_online_store_admin_service.UpdateFeatureViewRequest.pb(
            feature_online_store_admin_service.UpdateFeatureViewRequest()
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

        request = feature_online_store_admin_service.UpdateFeatureViewRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.update_feature_view(
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
async def test_delete_feature_view_rest_asyncio_bad_request(
    request_type=feature_online_store_admin_service.DeleteFeatureViewRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
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
        await client.delete_feature_view(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.DeleteFeatureViewRequest,
        dict,
    ],
)
async def test_delete_feature_view_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
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
        response = await client.delete_feature_view(request)

    # Establish that the response is the type that we expect.
    json_return_value = json_format.MessageToJson(return_value)


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_delete_feature_view_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncFeatureOnlineStoreAdminServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_delete_feature_view",
    ) as post, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_delete_feature_view_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_delete_feature_view",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = feature_online_store_admin_service.DeleteFeatureViewRequest.pb(
            feature_online_store_admin_service.DeleteFeatureViewRequest()
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

        request = feature_online_store_admin_service.DeleteFeatureViewRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()
        post_with_metadata.return_value = operations_pb2.Operation(), metadata

        await client.delete_feature_view(
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
async def test_sync_feature_view_rest_asyncio_bad_request(
    request_type=feature_online_store_admin_service.SyncFeatureViewRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "feature_view": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
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
        await client.sync_feature_view(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.SyncFeatureViewRequest,
        dict,
    ],
)
async def test_sync_feature_view_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "feature_view": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = feature_online_store_admin_service.SyncFeatureViewResponse(
            feature_view_sync="feature_view_sync_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = feature_online_store_admin_service.SyncFeatureViewResponse.pb(
            return_value
        )
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.sync_feature_view(request)

    # Establish that the response is the type that we expect.
    assert isinstance(
        response, feature_online_store_admin_service.SyncFeatureViewResponse
    )
    assert response.feature_view_sync == "feature_view_sync_value"


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_sync_feature_view_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncFeatureOnlineStoreAdminServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_sync_feature_view",
    ) as post, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_sync_feature_view_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_sync_feature_view",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = feature_online_store_admin_service.SyncFeatureViewRequest.pb(
            feature_online_store_admin_service.SyncFeatureViewRequest()
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
        return_value = (
            feature_online_store_admin_service.SyncFeatureViewResponse.to_json(
                feature_online_store_admin_service.SyncFeatureViewResponse()
            )
        )
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = feature_online_store_admin_service.SyncFeatureViewRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = feature_online_store_admin_service.SyncFeatureViewResponse()
        post_with_metadata.return_value = (
            feature_online_store_admin_service.SyncFeatureViewResponse(),
            metadata,
        )

        await client.sync_feature_view(
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
async def test_get_feature_view_sync_rest_asyncio_bad_request(
    request_type=feature_online_store_admin_service.GetFeatureViewSyncRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4/featureViewSyncs/sample5"
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
        await client.get_feature_view_sync(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.GetFeatureViewSyncRequest,
        dict,
    ],
)
async def test_get_feature_view_sync_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "name": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4/featureViewSyncs/sample5"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = feature_view_sync.FeatureViewSync(
            name="name_value",
            satisfies_pzs=True,
            satisfies_pzi=True,
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = feature_view_sync.FeatureViewSync.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.get_feature_view_sync(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, feature_view_sync.FeatureViewSync)
    assert response.name == "name_value"
    assert response.satisfies_pzs is True
    assert response.satisfies_pzi is True


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_get_feature_view_sync_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncFeatureOnlineStoreAdminServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_get_feature_view_sync",
    ) as post, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_get_feature_view_sync_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_get_feature_view_sync",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = feature_online_store_admin_service.GetFeatureViewSyncRequest.pb(
            feature_online_store_admin_service.GetFeatureViewSyncRequest()
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
        return_value = feature_view_sync.FeatureViewSync.to_json(
            feature_view_sync.FeatureViewSync()
        )
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = feature_online_store_admin_service.GetFeatureViewSyncRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = feature_view_sync.FeatureViewSync()
        post_with_metadata.return_value = feature_view_sync.FeatureViewSync(), metadata

        await client.get_feature_view_sync(
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
async def test_list_feature_view_syncs_rest_asyncio_bad_request(
    request_type=feature_online_store_admin_service.ListFeatureViewSyncsRequest,
):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    # send a request that will satisfy transcoding
    request_init = {
        "parent": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
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
        await client.list_feature_view_syncs(request)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_type",
    [
        feature_online_store_admin_service.ListFeatureViewSyncsRequest,
        dict,
    ],
)
async def test_list_feature_view_syncs_rest_asyncio_call_success(request_type):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )

    # send a request that will satisfy transcoding
    request_init = {
        "parent": "projects/sample1/locations/sample2/featureOnlineStores/sample3/featureViews/sample4"
    }
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = feature_online_store_admin_service.ListFeatureViewSyncsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = mock.Mock()
        response_value.status_code = 200

        # Convert return value to protobuf type
        return_value = (
            feature_online_store_admin_service.ListFeatureViewSyncsResponse.pb(
                return_value
            )
        )
        json_return_value = json_format.MessageToJson(return_value)
        response_value.read = mock.AsyncMock(
            return_value=json_return_value.encode("UTF-8")
        )
        req.return_value = response_value
        req.return_value.headers = {"header-1": "value-1", "header-2": "value-2"}
        response = await client.list_feature_view_syncs(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListFeatureViewSyncsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
@pytest.mark.parametrize("null_interceptor", [True, False])
async def test_list_feature_view_syncs_rest_asyncio_interceptors(null_interceptor):
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    transport = transports.AsyncFeatureOnlineStoreAdminServiceRestTransport(
        credentials=async_anonymous_credentials(),
        interceptor=(
            None
            if null_interceptor
            else transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor()
        ),
    )
    client = FeatureOnlineStoreAdminServiceAsyncClient(transport=transport)

    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_list_feature_view_syncs",
    ) as post, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "post_list_feature_view_syncs_with_metadata",
    ) as post_with_metadata, mock.patch.object(
        transports.AsyncFeatureOnlineStoreAdminServiceRestInterceptor,
        "pre_list_feature_view_syncs",
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        post_with_metadata.assert_not_called()
        pb_message = feature_online_store_admin_service.ListFeatureViewSyncsRequest.pb(
            feature_online_store_admin_service.ListFeatureViewSyncsRequest()
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
        return_value = (
            feature_online_store_admin_service.ListFeatureViewSyncsResponse.to_json(
                feature_online_store_admin_service.ListFeatureViewSyncsResponse()
            )
        )
        req.return_value.read = mock.AsyncMock(return_value=return_value)

        request = feature_online_store_admin_service.ListFeatureViewSyncsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = (
            feature_online_store_admin_service.ListFeatureViewSyncsResponse()
        )
        post_with_metadata.return_value = (
            feature_online_store_admin_service.ListFeatureViewSyncsResponse(),
            metadata,
        )

        await client.list_feature_view_syncs(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="rest_asyncio"
    )
    assert client is not None


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_create_feature_online_store_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.create_feature_online_store), "__call__"
    ) as call:
        await client.create_feature_online_store(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = (
            feature_online_store_admin_service.CreateFeatureOnlineStoreRequest()
        )

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_feature_online_store_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.get_feature_online_store), "__call__"
    ) as call:
        await client.get_feature_online_store(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.GetFeatureOnlineStoreRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_feature_online_stores_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_online_stores), "__call__"
    ) as call:
        await client.list_feature_online_stores(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = (
            feature_online_store_admin_service.ListFeatureOnlineStoresRequest()
        )

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_update_feature_online_store_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.update_feature_online_store), "__call__"
    ) as call:
        await client.update_feature_online_store(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = (
            feature_online_store_admin_service.UpdateFeatureOnlineStoreRequest()
        )

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_delete_feature_online_store_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_feature_online_store), "__call__"
    ) as call:
        await client.delete_feature_online_store(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = (
            feature_online_store_admin_service.DeleteFeatureOnlineStoreRequest()
        )

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_create_feature_view_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.create_feature_view), "__call__"
    ) as call:
        await client.create_feature_view(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.CreateFeatureViewRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_feature_view_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(type(client.transport.get_feature_view), "__call__") as call:
        await client.get_feature_view(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.GetFeatureViewRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_feature_views_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_views), "__call__"
    ) as call:
        await client.list_feature_views(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.ListFeatureViewsRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_update_feature_view_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.update_feature_view), "__call__"
    ) as call:
        await client.update_feature_view(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.UpdateFeatureViewRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_delete_feature_view_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.delete_feature_view), "__call__"
    ) as call:
        await client.delete_feature_view(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.DeleteFeatureViewRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_sync_feature_view_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.sync_feature_view), "__call__"
    ) as call:
        await client.sync_feature_view(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.SyncFeatureViewRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_get_feature_view_sync_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.get_feature_view_sync), "__call__"
    ) as call:
        await client.get_feature_view_sync(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.GetFeatureViewSyncRequest()

        assert args[0] == request_msg


# This test is a coverage failsafe to make sure that totally empty calls,
# i.e. request == None and no flattened fields passed, work.
@pytest.mark.asyncio
async def test_list_feature_view_syncs_empty_call_rest_asyncio():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(),
        transport="rest_asyncio",
    )

    # Mock the actual call, and fake the request.
    with mock.patch.object(
        type(client.transport.list_feature_view_syncs), "__call__"
    ) as call:
        await client.list_feature_view_syncs(request=None)

        # Establish that the underlying stub method was called.
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        request_msg = feature_online_store_admin_service.ListFeatureViewSyncsRequest()

        assert args[0] == request_msg


def test_feature_online_store_admin_service_rest_asyncio_lro_client():
    if not HAS_ASYNC_REST_EXTRA:
        pytest.skip(
            "the library must be installed with the `async_rest` extra to test this feature."
        )
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
        client = FeatureOnlineStoreAdminServiceAsyncClient(
            credentials=async_anonymous_credentials(),
            transport="rest_asyncio",
            client_options=options,
        )


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = FeatureOnlineStoreAdminServiceClient(
        credentials=ga_credentials.AnonymousCredentials(),
    )
    assert isinstance(
        client.transport,
        transports.FeatureOnlineStoreAdminServiceGrpcTransport,
    )


def test_feature_online_store_admin_service_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(core_exceptions.DuplicateCredentialArgs):
        transport = transports.FeatureOnlineStoreAdminServiceTransport(
            credentials=ga_credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_feature_online_store_admin_service_base_transport():
    # Instantiate the base transport.
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.feature_online_store_admin_service.transports.FeatureOnlineStoreAdminServiceTransport.__init__"
    ) as Transport:
        Transport.return_value = None
        transport = transports.FeatureOnlineStoreAdminServiceTransport(
            credentials=ga_credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "create_feature_online_store",
        "get_feature_online_store",
        "list_feature_online_stores",
        "update_feature_online_store",
        "delete_feature_online_store",
        "create_feature_view",
        "get_feature_view",
        "list_feature_views",
        "update_feature_view",
        "delete_feature_view",
        "sync_feature_view",
        "get_feature_view_sync",
        "list_feature_view_syncs",
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


def test_feature_online_store_admin_service_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        google.auth, "load_credentials_from_file", autospec=True
    ) as load_creds, mock.patch(
        "google.cloud.aiplatform_v1beta1.services.feature_online_store_admin_service.transports.FeatureOnlineStoreAdminServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.FeatureOnlineStoreAdminServiceTransport(
            credentials_file="credentials.json",
            quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=None,
            default_scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


def test_feature_online_store_admin_service_base_transport_with_adc():
    # Test the default credentials are used if credentials and credentials_file are None.
    with mock.patch.object(google.auth, "default", autospec=True) as adc, mock.patch(
        "google.cloud.aiplatform_v1beta1.services.feature_online_store_admin_service.transports.FeatureOnlineStoreAdminServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        transport = transports.FeatureOnlineStoreAdminServiceTransport()
        adc.assert_called_once()


def test_feature_online_store_admin_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (ga_credentials.AnonymousCredentials(), None)
        FeatureOnlineStoreAdminServiceClient()
        adc.assert_called_once_with(
            scopes=None,
            default_scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id=None,
        )


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.FeatureOnlineStoreAdminServiceGrpcTransport,
        transports.FeatureOnlineStoreAdminServiceGrpcAsyncIOTransport,
    ],
)
def test_feature_online_store_admin_service_transport_auth_adc(transport_class):
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
        transports.FeatureOnlineStoreAdminServiceGrpcTransport,
        transports.FeatureOnlineStoreAdminServiceGrpcAsyncIOTransport,
        transports.FeatureOnlineStoreAdminServiceRestTransport,
    ],
)
def test_feature_online_store_admin_service_transport_auth_gdch_credentials(
    transport_class,
):
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
        (transports.FeatureOnlineStoreAdminServiceGrpcTransport, grpc_helpers),
        (
            transports.FeatureOnlineStoreAdminServiceGrpcAsyncIOTransport,
            grpc_helpers_async,
        ),
    ],
)
def test_feature_online_store_admin_service_transport_create_channel(
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
        transports.FeatureOnlineStoreAdminServiceGrpcTransport,
        transports.FeatureOnlineStoreAdminServiceGrpcAsyncIOTransport,
    ],
)
def test_feature_online_store_admin_service_grpc_transport_client_cert_source_for_mtls(
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


def test_feature_online_store_admin_service_http_transport_client_cert_source_for_mtls():
    cred = ga_credentials.AnonymousCredentials()
    with mock.patch(
        "google.auth.transport.requests.AuthorizedSession.configure_mtls_channel"
    ) as mock_configure_mtls_channel:
        transports.FeatureOnlineStoreAdminServiceRestTransport(
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
def test_feature_online_store_admin_service_host_no_port(transport_name):
    client = FeatureOnlineStoreAdminServiceClient(
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
def test_feature_online_store_admin_service_host_with_port(transport_name):
    client = FeatureOnlineStoreAdminServiceClient(
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
def test_feature_online_store_admin_service_client_transport_session_collision(
    transport_name,
):
    creds1 = ga_credentials.AnonymousCredentials()
    creds2 = ga_credentials.AnonymousCredentials()
    client1 = FeatureOnlineStoreAdminServiceClient(
        credentials=creds1,
        transport=transport_name,
    )
    client2 = FeatureOnlineStoreAdminServiceClient(
        credentials=creds2,
        transport=transport_name,
    )
    session1 = client1.transport.create_feature_online_store._session
    session2 = client2.transport.create_feature_online_store._session
    assert session1 != session2
    session1 = client1.transport.get_feature_online_store._session
    session2 = client2.transport.get_feature_online_store._session
    assert session1 != session2
    session1 = client1.transport.list_feature_online_stores._session
    session2 = client2.transport.list_feature_online_stores._session
    assert session1 != session2
    session1 = client1.transport.update_feature_online_store._session
    session2 = client2.transport.update_feature_online_store._session
    assert session1 != session2
    session1 = client1.transport.delete_feature_online_store._session
    session2 = client2.transport.delete_feature_online_store._session
    assert session1 != session2
    session1 = client1.transport.create_feature_view._session
    session2 = client2.transport.create_feature_view._session
    assert session1 != session2
    session1 = client1.transport.get_feature_view._session
    session2 = client2.transport.get_feature_view._session
    assert session1 != session2
    session1 = client1.transport.list_feature_views._session
    session2 = client2.transport.list_feature_views._session
    assert session1 != session2
    session1 = client1.transport.update_feature_view._session
    session2 = client2.transport.update_feature_view._session
    assert session1 != session2
    session1 = client1.transport.delete_feature_view._session
    session2 = client2.transport.delete_feature_view._session
    assert session1 != session2
    session1 = client1.transport.sync_feature_view._session
    session2 = client2.transport.sync_feature_view._session
    assert session1 != session2
    session1 = client1.transport.get_feature_view_sync._session
    session2 = client2.transport.get_feature_view_sync._session
    assert session1 != session2
    session1 = client1.transport.list_feature_view_syncs._session
    session2 = client2.transport.list_feature_view_syncs._session
    assert session1 != session2


def test_feature_online_store_admin_service_grpc_transport_channel():
    channel = grpc.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.FeatureOnlineStoreAdminServiceGrpcTransport(
        host="squid.clam.whelk",
        channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


def test_feature_online_store_admin_service_grpc_asyncio_transport_channel():
    channel = aio.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.FeatureOnlineStoreAdminServiceGrpcAsyncIOTransport(
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
        transports.FeatureOnlineStoreAdminServiceGrpcTransport,
        transports.FeatureOnlineStoreAdminServiceGrpcAsyncIOTransport,
    ],
)
def test_feature_online_store_admin_service_transport_channel_mtls_with_client_cert_source(
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
        transports.FeatureOnlineStoreAdminServiceGrpcTransport,
        transports.FeatureOnlineStoreAdminServiceGrpcAsyncIOTransport,
    ],
)
def test_feature_online_store_admin_service_transport_channel_mtls_with_adc(
    transport_class,
):
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


def test_feature_online_store_admin_service_grpc_lro_client():
    client = FeatureOnlineStoreAdminServiceClient(
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


def test_feature_online_store_admin_service_grpc_lro_async_client():
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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


def test_feature_online_store_path():
    project = "squid"
    location = "clam"
    feature_online_store = "whelk"
    expected = "projects/{project}/locations/{location}/featureOnlineStores/{feature_online_store}".format(
        project=project,
        location=location,
        feature_online_store=feature_online_store,
    )
    actual = FeatureOnlineStoreAdminServiceClient.feature_online_store_path(
        project, location, feature_online_store
    )
    assert expected == actual


def test_parse_feature_online_store_path():
    expected = {
        "project": "octopus",
        "location": "oyster",
        "feature_online_store": "nudibranch",
    }
    path = FeatureOnlineStoreAdminServiceClient.feature_online_store_path(**expected)

    # Check that the path construction is reversible.
    actual = FeatureOnlineStoreAdminServiceClient.parse_feature_online_store_path(path)
    assert expected == actual


def test_feature_view_path():
    project = "cuttlefish"
    location = "mussel"
    feature_online_store = "winkle"
    feature_view = "nautilus"
    expected = "projects/{project}/locations/{location}/featureOnlineStores/{feature_online_store}/featureViews/{feature_view}".format(
        project=project,
        location=location,
        feature_online_store=feature_online_store,
        feature_view=feature_view,
    )
    actual = FeatureOnlineStoreAdminServiceClient.feature_view_path(
        project, location, feature_online_store, feature_view
    )
    assert expected == actual


def test_parse_feature_view_path():
    expected = {
        "project": "scallop",
        "location": "abalone",
        "feature_online_store": "squid",
        "feature_view": "clam",
    }
    path = FeatureOnlineStoreAdminServiceClient.feature_view_path(**expected)

    # Check that the path construction is reversible.
    actual = FeatureOnlineStoreAdminServiceClient.parse_feature_view_path(path)
    assert expected == actual


def test_feature_view_sync_path():
    project = "whelk"
    location = "octopus"
    feature_online_store = "oyster"
    feature_view = "nudibranch"
    expected = "projects/{project}/locations/{location}/featureOnlineStores/{feature_online_store}/featureViews/{feature_view}/featureViewSyncs/feature_view_sync".format(
        project=project,
        location=location,
        feature_online_store=feature_online_store,
        feature_view=feature_view,
    )
    actual = FeatureOnlineStoreAdminServiceClient.feature_view_sync_path(
        project, location, feature_online_store, feature_view
    )
    assert expected == actual


def test_parse_feature_view_sync_path():
    expected = {
        "project": "cuttlefish",
        "location": "mussel",
        "feature_online_store": "winkle",
        "feature_view": "nautilus",
    }
    path = FeatureOnlineStoreAdminServiceClient.feature_view_sync_path(**expected)

    # Check that the path construction is reversible.
    actual = FeatureOnlineStoreAdminServiceClient.parse_feature_view_sync_path(path)
    assert expected == actual


def test_common_billing_account_path():
    billing_account = "scallop"
    expected = "billingAccounts/{billing_account}".format(
        billing_account=billing_account,
    )
    actual = FeatureOnlineStoreAdminServiceClient.common_billing_account_path(
        billing_account
    )
    assert expected == actual


def test_parse_common_billing_account_path():
    expected = {
        "billing_account": "abalone",
    }
    path = FeatureOnlineStoreAdminServiceClient.common_billing_account_path(**expected)

    # Check that the path construction is reversible.
    actual = FeatureOnlineStoreAdminServiceClient.parse_common_billing_account_path(
        path
    )
    assert expected == actual


def test_common_folder_path():
    folder = "squid"
    expected = "folders/{folder}".format(
        folder=folder,
    )
    actual = FeatureOnlineStoreAdminServiceClient.common_folder_path(folder)
    assert expected == actual


def test_parse_common_folder_path():
    expected = {
        "folder": "clam",
    }
    path = FeatureOnlineStoreAdminServiceClient.common_folder_path(**expected)

    # Check that the path construction is reversible.
    actual = FeatureOnlineStoreAdminServiceClient.parse_common_folder_path(path)
    assert expected == actual


def test_common_organization_path():
    organization = "whelk"
    expected = "organizations/{organization}".format(
        organization=organization,
    )
    actual = FeatureOnlineStoreAdminServiceClient.common_organization_path(organization)
    assert expected == actual


def test_parse_common_organization_path():
    expected = {
        "organization": "octopus",
    }
    path = FeatureOnlineStoreAdminServiceClient.common_organization_path(**expected)

    # Check that the path construction is reversible.
    actual = FeatureOnlineStoreAdminServiceClient.parse_common_organization_path(path)
    assert expected == actual


def test_common_project_path():
    project = "oyster"
    expected = "projects/{project}".format(
        project=project,
    )
    actual = FeatureOnlineStoreAdminServiceClient.common_project_path(project)
    assert expected == actual


def test_parse_common_project_path():
    expected = {
        "project": "nudibranch",
    }
    path = FeatureOnlineStoreAdminServiceClient.common_project_path(**expected)

    # Check that the path construction is reversible.
    actual = FeatureOnlineStoreAdminServiceClient.parse_common_project_path(path)
    assert expected == actual


def test_common_location_path():
    project = "cuttlefish"
    location = "mussel"
    expected = "projects/{project}/locations/{location}".format(
        project=project,
        location=location,
    )
    actual = FeatureOnlineStoreAdminServiceClient.common_location_path(
        project, location
    )
    assert expected == actual


def test_parse_common_location_path():
    expected = {
        "project": "winkle",
        "location": "nautilus",
    }
    path = FeatureOnlineStoreAdminServiceClient.common_location_path(**expected)

    # Check that the path construction is reversible.
    actual = FeatureOnlineStoreAdminServiceClient.parse_common_location_path(path)
    assert expected == actual


def test_client_with_default_client_info():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        client = FeatureOnlineStoreAdminServiceClient(
            credentials=ga_credentials.AnonymousCredentials(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(
        transports.FeatureOnlineStoreAdminServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        transport_class = FeatureOnlineStoreAdminServiceClient.get_transport_class()
        transport = transport_class(
            credentials=ga_credentials.AnonymousCredentials(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)


def test_delete_operation(transport: str = "grpc"):
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    assert (
        "x-goog-request-params",
        "name=locations/abc",
    ) in kw["metadata"]


def test_get_location_from_dict():
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
        credentials=async_anonymous_credentials(), transport="grpc_asyncio"
    )
    with mock.patch.object(
        type(getattr(client.transport, "_grpc_channel")), "close"
    ) as close:
        async with client:
            close.assert_not_called()
        close.assert_called_once()


def test_transport_close_rest():
    client = FeatureOnlineStoreAdminServiceClient(
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
    client = FeatureOnlineStoreAdminServiceAsyncClient(
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
        client = FeatureOnlineStoreAdminServiceClient(
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
        (
            FeatureOnlineStoreAdminServiceClient,
            transports.FeatureOnlineStoreAdminServiceGrpcTransport,
        ),
        (
            FeatureOnlineStoreAdminServiceAsyncClient,
            transports.FeatureOnlineStoreAdminServiceGrpcAsyncIOTransport,
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
