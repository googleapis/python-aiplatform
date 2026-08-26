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
import json
import os
from unittest import mock

from google import auth
from google.auth import credentials as auth_credentials
import agentplatform
from google.cloud import aiplatform
from agentplatform._genai import sandbox_templates
from agentplatform._genai import sandboxes
from agentplatform._genai import types as agentplatform_types
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
_TEST_SANDBOX_TEMPLATE_ID = "template-123"
_TEST_SANDBOX_TEMPLATE_RESOURCE_NAME = (
    f"{_TEST_AGENT_ENGINE_RESOURCE_NAME}"
    f"/sandboxEnvironmentTemplates/{_TEST_SANDBOX_TEMPLATE_ID}"
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
            "test-us-central1.example.vertexai.goog"
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
            "https://test-us-central1.example.vertexai.goog/test/path"
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
            "test-us-central1.example.vertexai.goog"
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
        assert ws_url == "wss://test-us-central1.example.vertexai.goog/test/endpoint"
        assert (
            headers["Sec-WebSocket-Protocol"]
            == "v1.stream, test_token, test_routing_token, 9222"
        )

    @mock.patch.object(sandboxes.Sandboxes, "_create")
    def test_create_with_shell_environment_and_existing_template(self, mock_create):
        mock_operation = mock.Mock()
        mock_create.return_value = mock_operation

        result = self.client.sandboxes.create(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            spec={"shell_environment": {}},
            config={
                "sandbox_environment_template": _TEST_SANDBOX_TEMPLATE_RESOURCE_NAME,
                "wait_for_completion": False,
            },
        )

        assert result is mock_operation
        mock_create.assert_called_once()
        _, kwargs = mock_create.call_args
        assert kwargs["name"] == _TEST_AGENT_ENGINE_RESOURCE_NAME
        assert (
            kwargs["config"].sandbox_environment_template
            == _TEST_SANDBOX_TEMPLATE_RESOURCE_NAME
        )

    @mock.patch.object(sandboxes.Sandboxes, "_create")
    @mock.patch.object(sandbox_templates.SandboxTemplates, "create")
    def test_create_with_shell_environment_creates_template_when_absent(
        self, mock_template_create, mock_create
    ):
        mock_template_operation = mock.Mock()
        mock_template_operation.response.name = _TEST_SANDBOX_TEMPLATE_RESOURCE_NAME
        mock_template_create.return_value = mock_template_operation
        mock_create.return_value = mock.Mock()

        self.client.sandboxes.create(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            spec={"shell_environment": {}},
            config={"wait_for_completion": False},
        )

        mock_template_create.assert_called_once()
        _, template_kwargs = mock_template_create.call_args
        template_config = template_kwargs["config"]
        assert (
            template_config.default_container_environment.default_container_category
            == agentplatform_types.DefaultContainerCategory.DEFAULT_CONTAINER_CATEGORY_SHELL_SANDBOX
        )
        mock_create.assert_called_once()
        _, create_kwargs = mock_create.call_args
        assert (
            create_kwargs["config"].sandbox_environment_template
            == _TEST_SANDBOX_TEMPLATE_RESOURCE_NAME
        )

    @mock.patch.object(sandboxes.Sandboxes, "_create")
    @mock.patch.object(sandbox_templates.SandboxTemplates, "create")
    def test_create_with_typed_shell_environment_creates_template_when_absent(
        self, mock_template_create, mock_create
    ):
        mock_template_operation = mock.Mock()
        mock_template_operation.response.name = _TEST_SANDBOX_TEMPLATE_RESOURCE_NAME
        mock_template_create.return_value = mock_template_operation
        mock_create.return_value = mock.Mock()

        shell_environment = agentplatform_types.SandboxEnvironmentSpecShellEnvironment()
        self.client.sandboxes.create(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            spec=agentplatform_types.SandboxEnvironmentSpec(
                shell_environment=shell_environment,
            ),
            config={"wait_for_completion": False},
        )

        mock_template_create.assert_called_once()
        _, template_kwargs = mock_template_create.call_args
        template_config = template_kwargs["config"]
        assert (
            template_config.default_container_environment.default_container_category
            == agentplatform_types.DefaultContainerCategory.DEFAULT_CONTAINER_CATEGORY_SHELL_SANDBOX
        )
        mock_create.assert_called_once()
        _, create_kwargs = mock_create.call_args
        assert (
            create_kwargs["config"].sandbox_environment_template
            == _TEST_SANDBOX_TEMPLATE_RESOURCE_NAME
        )

    @mock.patch.object(sandboxes.Sandboxes, "_create")
    @mock.patch.object(sandbox_templates.SandboxTemplates, "create")
    def test_create_with_computer_use_environment_creates_template_when_absent(
        self, mock_template_create, mock_create
    ):
        mock_template_operation = mock.Mock()
        mock_template_operation.response.name = _TEST_SANDBOX_TEMPLATE_RESOURCE_NAME
        mock_template_create.return_value = mock_template_operation
        mock_create.return_value = mock.Mock()

        self.client.sandboxes.create(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            spec={"computer_use_environment": {}},
            config={"wait_for_completion": False},
        )

        mock_template_create.assert_called_once()
        _, template_kwargs = mock_template_create.call_args
        template_config = template_kwargs["config"]
        assert (
            template_config.default_container_environment.default_container_category
            == agentplatform_types.DefaultContainerCategory.DEFAULT_CONTAINER_CATEGORY_COMPUTER_USE
        )
        mock_create.assert_called_once()
        _, create_kwargs = mock_create.call_args
        assert (
            create_kwargs["config"].sandbox_environment_template
            == _TEST_SANDBOX_TEMPLATE_RESOURCE_NAME
        )

    @mock.patch.object(sandboxes.Sandboxes, "_create")
    @mock.patch.object(sandbox_templates.SandboxTemplates, "create")
    def test_create_with_snapshot_does_not_create_template(
        self, mock_template_create, mock_create
    ):
        mock_operation = mock.Mock()
        mock_create.return_value = mock_operation

        result = self.client.sandboxes.create(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            spec={"computer_use_environment": {}},
            config={
                "sandbox_environment_snapshot": "projects/p/locations/l/agentEngines/ae/sandboxEnvironmentSnapshots/s1",
                "wait_for_completion": False,
            },
        )

        assert result is mock_operation
        mock_template_create.assert_not_called()
        mock_create.assert_called_once()
        _, create_kwargs = mock_create.call_args
        assert (
            create_kwargs["config"].sandbox_environment_snapshot
            == "projects/p/locations/l/agentEngines/ae/sandboxEnvironmentSnapshots/s1"
        )

    @mock.patch.object(sandboxes.Sandboxes, "_create")
    def test_create_without_spec_template_or_snapshot_raises(self, mock_create):
        for spec in (None, {}, agentplatform_types.SandboxEnvironmentSpec()):
            with pytest.raises(ValueError, match="must be provided"):
                self.client.sandboxes.create(
                    name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                    spec=spec,
                )

        mock_create.assert_not_called()


_MODULES = pytest.mark.parametrize(
    "module",
    [sandboxes, vertexai_sandboxes],
    ids=["agentplatform", "vertexai"],
)


class _NoUniverseDomainCredentials:
    """Credentials without a `universe_domain`, to exercise the fallback."""


def _mock_signing(module, credentials, responses, is_mtls=False):
    """Patches google_auth.default and AuthorizedSession for `module`."""
    session = mock.Mock(is_mtls=is_mtls)
    session.post.side_effect = responses
    return (
        mock.patch.object(
            module.google_auth,
            "default",
            return_value=(credentials, _TEST_PROJECT),
        ),
        mock.patch.object(
            module.google_auth_requests,
            "AuthorizedSession",
            return_value=session,
        ),
        session,
    )


def _ok_response(signed_jwt="signed-jwt-value"):
    response = mock.Mock(status_code=200)
    response.json.return_value = {"signedJwt": signed_jwt}
    return response


@_MODULES
def test_sandboxes_module_does_not_reference_google_cloud_iam(module):
    """`google-cloud-iam` is no longer a dependency of this SDK.

    Signing goes through `google-auth`, a core requirement, so nothing may
    reach for `iam_credentials_v1` again. See b/541269262.
    """
    assert not hasattr(module, "iam_credentials_v1")
    assert not hasattr(module, "iam_credentials")


@_MODULES
@pytest.mark.parametrize(
    "credentials_factory,expected_host",
    [
        (_NoUniverseDomainCredentials, "iamcredentials.googleapis.com"),
        (
            lambda: mock.Mock(universe_domain="googleapis.com"),
            "iamcredentials.googleapis.com",
        ),
        (
            lambda: mock.Mock(universe_domain="test.tpc.example"),
            "iamcredentials.test.tpc.example",
        ),
    ],
    ids=["no-universe-domain", "default-universe", "tpc-universe"],
)
def test_generate_access_token_signs_via_google_auth(
    module, credentials_factory, expected_host
):
    """The token is minted by POSTing to the IAM Credentials signJwt endpoint."""
    credentials = credentials_factory()
    default_patch, session_patch, session = _mock_signing(
        module, credentials, [_ok_response()]
    )

    with default_patch as google_auth_default, session_patch as authorized_session:
        client_obj = module.Sandboxes(api_client_=mock.Mock())
        token = client_obj.generate_access_token(
            service_account_email=_TEST_SERVICE_ACCOUNT_EMAIL,
            timeout=1234,
        )

    assert token == "signed-jwt-value"
    # Signed with the resolved credentials, at the cloud-platform scope the
    # generated IAM client used.
    authorized_session.assert_called_once_with(credentials)
    assert google_auth_default.call_args.kwargs["scopes"] == [
        "https://www.googleapis.com/auth/cloud-platform"
    ]

    assert session.post.call_args.args[0] == (
        f"https://{expected_host}/v1/projects/-/serviceAccounts/"
        f"{_TEST_SERVICE_ACCOUNT_EMAIL}:signJwt"
    )
    # Always offered; google-auth decides whether mTLS actually applies.
    session.configure_mtls_channel.assert_called_once_with()
    # A request that never returns must not hang forever.
    assert session.post.call_args.kwargs["timeout"] > 0

    payload = json.loads(session.post.call_args.kwargs["json"]["payload"])
    assert payload["iss"] == _TEST_SERVICE_ACCOUNT_EMAIL
    assert payload["sub"] == _TEST_SERVICE_ACCOUNT_EMAIL
    assert payload["aud"] == "https://aiplatform.googleapis.com/"
    # iat/exp are derived from a single clock read, so this is exact.
    assert payload["exp"] - payload["iat"] == 1234


@_MODULES
@pytest.mark.parametrize("status_code", [503, 504])
def test_generate_access_token_retries_transient_failures(module, status_code):
    """503/504 are retried, as the generated IAM client did."""
    transient = mock.Mock(status_code=status_code)
    default_patch, session_patch, session = _mock_signing(
        module,
        mock.Mock(universe_domain="googleapis.com"),
        [transient, transient, _ok_response()],
    )

    with default_patch, session_patch, mock.patch.object(
        module.time, "sleep"
    ) as sleep:
        client_obj = module.Sandboxes(api_client_=mock.Mock())
        token = client_obj.generate_access_token(
            service_account_email=_TEST_SERVICE_ACCOUNT_EMAIL
        )

    assert token == "signed-jwt-value"
    assert session.post.call_count == 3
    # Backoff grows, matching the replaced client's multiplier.
    delays = [call.args[0] for call in sleep.call_args_list]
    assert delays == sorted(delays) and delays[0] > 0
    transient.raise_for_status.assert_not_called()


@_MODULES
def test_generate_access_token_does_not_retry_client_errors(module):
    """A 4xx is surfaced immediately rather than retried."""
    failure = mock.Mock(status_code=403)
    failure.raise_for_status.side_effect = ValueError("403 Forbidden")
    default_patch, session_patch, session = _mock_signing(
        module, mock.Mock(universe_domain="googleapis.com"), [failure]
    )

    with default_patch, session_patch:
        client_obj = module.Sandboxes(api_client_=mock.Mock())
        with pytest.raises(ValueError, match="403 Forbidden"):
            client_obj.generate_access_token(
                service_account_email=_TEST_SERVICE_ACCOUNT_EMAIL
            )

    assert session.post.call_count == 1


@_MODULES
@pytest.mark.parametrize(
    "universe_domain,expected_host",
    [
        ("googleapis.com", "iamcredentials.mtls.googleapis.com"),
        # mTLS is not defined off the default universe, so stay on the plain host.
        ("test.tpc.example", "iamcredentials.test.tpc.example"),
    ],
    ids=["default-universe", "tpc-universe"],
)
def test_generate_access_token_uses_mtls_endpoint_when_enabled(
    module, universe_domain, expected_host
):
    """With client certificates in play the mTLS host is used.

    The generated IAM client this replaced switched to
    `iamcredentials.mtls.googleapis.com` under
    `GOOGLE_API_USE_CLIENT_CERTIFICATE`, and the genai client backing every
    other call in this module does the same.
    """
    default_patch, session_patch, session = _mock_signing(
        module,
        mock.Mock(universe_domain=universe_domain),
        [_ok_response()],
        is_mtls=True,
    )

    with default_patch, session_patch:
        client_obj = module.Sandboxes(api_client_=mock.Mock())
        client_obj.generate_access_token(
            service_account_email=_TEST_SERVICE_ACCOUNT_EMAIL
        )

    assert session.post.call_args.args[0] == (
        f"https://{expected_host}/v1/projects/-/serviceAccounts/"
        f"{_TEST_SERVICE_ACCOUNT_EMAIL}:signJwt"
    )
