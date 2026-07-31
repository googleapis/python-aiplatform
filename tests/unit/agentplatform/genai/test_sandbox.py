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

import importlib
import os
import sys
from unittest import mock

from google import auth
from google.auth import credentials as auth_credentials
import google.cloud
import agentplatform
from google.cloud import aiplatform
from agentplatform._genai import sandboxes
from google.cloud.aiplatform import initializer
from vertexai._genai import (
    sandboxes as vertexai_sandboxes,
)
from google.genai import client
from google.genai import types as genai_types
import pytest


_TEST_CREDENTIALS = mock.Mock(spec=auth_credentials.AnonymousCredentials())
_TEST_LOCATION = "us-central1"
_TEST_PROJECT = "test-project"
_TEST_RESOURCE_ID = "1028944691210842416"
_TEST_SANDBOX_ID = "sandbox-123"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_AGENT_ENGINE_RESOURCE_NAME = (
    f"{_TEST_PARENT}/reasoningEngines/{_TEST_RESOURCE_ID}"
)
_TEST_SANDBOX_RESOURCE_NAME = (
    f"{_TEST_AGENT_ENGINE_RESOURCE_NAME}/sandboxes/{_TEST_SANDBOX_ID}"
)
_TEST_AGENT_ENGINE_ENV_KEY = "GOOGLE_CLOUD_AGENT_ENGINE_ENV"
_TEST_AGENT_ENGINE_ENV_VALUE = "test_env_value"
_TEST_SERVICE_ACCOUNT_EMAIL = "test-sa@test-project.iam.gserviceaccount.com"


@pytest.fixture(scope="module")
def google_auth_mock():
    with mock.patch.object(auth, "default") as google_auth_mock:
        google_auth_mock.return_value = (
            auth_credentials.AnonymousCredentials(),
            _TEST_PROJECT,
        )
        yield google_auth_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestSandbox:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        importlib.reload(agentplatform)
        os.environ[_TEST_AGENT_ENGINE_ENV_KEY] = _TEST_AGENT_ENGINE_ENV_VALUE
        self.client = agentplatform.Client(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @mock.patch.object(client.Client, "_get_api_client")
    def test_send_command(self, mock_get_api_client):
        mock_sandbox = mock.Mock()
        mock_sandbox.connection_info.load_balancer_ip = None
        mock_sandbox.connection_info.load_balancer_hostname = (
            "test-us-central1.sandbox.vertexai.goog"
        )
        mock_sandbox.connection_info.routing_token = "test_routing_token"
        mock_http_client = mock_get_api_client.return_value
        mock_http_client.request.return_value = genai_types.HttpResponse(
            body=b"{}", headers={}
        )

        self.client.sandboxes.send_command(
            http_method="GET",
            access_token="test_token",
            sandbox_environment=mock_sandbox,
            path="test/path",
        )

        call_args = mock_get_api_client.call_args
        assert call_args is not None
        _, kwargs = call_args
        http_options = kwargs["http_options"]
        assert http_options.base_url == (
            "https://test-us-central1.sandbox.vertexai.goog/test/path"
        )
        assert http_options.headers["Authorization"] == "Bearer test_token"

        mock_http_client.request.assert_called_with("GET", "test/path", {})

    @mock.patch.object(sandboxes.Sandboxes, "generate_access_token")
    @mock.patch.object(client.Client, "_get_api_client")
    def test_generate_browser_ws_headers(
        self, mock_get_api_client, mock_generate_access_token
    ):
        mock_generate_access_token.return_value = "test_token"

        mock_sandbox = mock.Mock()
        mock_sandbox.connection_info.load_balancer_ip = None
        mock_sandbox.connection_info.load_balancer_hostname = (
            "test-us-central1.sandbox.vertexai.goog"
        )
        mock_sandbox.connection_info.routing_token = "test_routing_token"
        mock_http_client = mock_get_api_client.return_value
        mock_http_client.request.return_value = genai_types.HttpResponse(
            body=b'{"endpoint": "test/endpoint"}', headers={}
        )
        ws_url, headers = (
            self.client.sandboxes.generate_browser_ws_headers(
                sandbox_environment=mock_sandbox,
                service_account_email=_TEST_SERVICE_ACCOUNT_EMAIL,
                timeout=3600,
            )
        )
        assert ws_url == "wss://test-us-central1.sandbox.vertexai.goog/test/endpoint"
        assert (
            headers["Sec-WebSocket-Protocol"]
            == "v1.stream, test_token, test_routing_token, 9222"
        )


@pytest.mark.parametrize(
    "module",
    [sandboxes, vertexai_sandboxes],
    ids=["agentplatform", "vertexai"],
)
def test_sandboxes_module_does_not_import_google_cloud_iam_at_module_scope(module):
    """The module must be importable when `google-cloud-iam` is absent.

    Only `generate_access_token` needs the package, so importing the module -
    which is what the `client.agent_engines.sandboxes` property does - must not
    require it. Regression test for b/507135729; see b/541269262.
    """
    # A module-scope `import x` binds `x` as an attribute of the module, so its
    # absence is a direct check that the import is not at module scope.
    assert not hasattr(module, "iam_credentials_v1")

    # Belt and braces: re-import the module with the package made unavailable.
    # `google.cloud` is a namespace package, so `from google.cloud import x`
    # resolves via the parent attribute before consulting sys.modules; the
    # attribute has to be removed too, or the block silently does nothing.
    name = module.__name__
    had_attr = hasattr(google.cloud, "iam_credentials_v1")
    saved_attr = getattr(google.cloud, "iam_credentials_v1", None)
    if had_attr:
        delattr(google.cloud, "iam_credentials_v1")
    try:
        with mock.patch.dict(
            sys.modules, {"google.cloud.iam_credentials_v1": None}
        ):
            sys.modules.pop(name, None)
            reimported = importlib.import_module(name)
            assert reimported.Sandboxes is not None
    finally:
        if had_attr:
            setattr(google.cloud, "iam_credentials_v1", saved_attr)
        # `mock.patch.dict` has restored the original module object in
        # sys.modules; re-point the parent package attribute at it so that no
        # later test sees the copy built while the dependency was blocked.
        parent_name, _, leaf = name.rpartition(".")
        setattr(sys.modules[parent_name], leaf, sys.modules[name])
