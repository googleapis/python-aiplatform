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

from unittest import mock

from google import auth
from google.auth import credentials as auth_credentials
from google.cloud import aiplatform
import vertexai
from google.cloud.aiplatform import initializer
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
        importlib.reload(vertexai)
        os.environ[_TEST_AGENT_ENGINE_ENV_KEY] = _TEST_AGENT_ENGINE_ENV_VALUE
        self.client = vertexai.Client(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @mock.patch.object(client.Client, "_get_api_client")
    def test_send_command(self, mock_get_api_client):
        mock_sandbox = mock.Mock()
        mock_sandbox.connection_info.load_balancer_ip = "127.0.0.1"
        mock_sandbox.connection_info.load_balancer_hostname = None
        mock_http_client = mock_get_api_client.return_value
        mock_http_client.request.return_value = genai_types.HttpResponse(
            body=b"{}", headers={}
        )

        self.client.agent_engines.sandboxes.send_command(
            http_method="GET",
            access_token="test_token",
            sandbox_environment=mock_sandbox,
            path="test/path",
        )

        call_args = mock_get_api_client.call_args
        assert call_args is not None
        _, kwargs = call_args
        http_options = kwargs["http_options"]
        assert http_options.base_url == "http://127.0.0.1/test/path"
        assert http_options.headers["Authorization"] == "Bearer test_token"

        mock_http_client.request.assert_called_with("GET", "test/path", {})
