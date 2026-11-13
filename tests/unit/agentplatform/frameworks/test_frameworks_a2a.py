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

import importlib
import os
from unittest import mock

from google import auth
from google.auth import credentials as auth_credentials
import agentplatform
from agentplatform._genai import _runtimes_utils
from agentplatform._genai import types as _genai_types
from google.genai import types as genai_types
import pytest


from a2a.types import AgentSkill

from agentplatform.frameworks.a2a import A2aAgent
from agentplatform.frameworks.a2a import create_agent_card


_TEST_LOCATION = "us-central1"
_TEST_PROJECT = "test-project"
_TEST_RESOURCE_ID = "1028944691210842416"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_AGENT_ENGINE_RESOURCE_NAME = (
    f"{_TEST_PARENT}/reasoningEngines/{_TEST_RESOURCE_ID}"
)
_TEST_AGENT_ENGINE_DISPLAY_NAME = "test-a2a-agent"
_TEST_STAGING_BUCKET = "gs://test-bucket"
_TEST_CREDENTIALS = mock.Mock(spec=auth_credentials.AnonymousCredentials())
_TEST_SKILL = AgentSkill(
    id="hello_world",
    name="Returns hello world",
    description="just returns hello world",
    tags=["hello world"],
    examples=["hi", "hello world"],
)


def _make_agent() -> A2aAgent:
    card = create_agent_card(
        agent_name="Test",
        description="Test",
        skills=[_TEST_SKILL],
    )
    return A2aAgent(agent_card=card)


@pytest.fixture(scope="module")
def google_auth_mock():
    with mock.patch.object(auth, "default") as google_auth_mock:
        google_auth_mock.return_value = (
            auth_credentials.AnonymousCredentials(),
            _TEST_PROJECT,
        )
        yield google_auth_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestA2aAgentCreate:
    def setup_method(self):
        importlib.reload(agentplatform)
        os.environ["GOOGLE_CLOUD_PROJECT"] = _TEST_PROJECT
        os.environ["GOOGLE_CLOUD_LOCATION"] = _TEST_LOCATION
        self.client = agentplatform.Client(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

    def teardown_method(self):
        for key in [
            "GOOGLE_CLOUD_PROJECT",
            "GOOGLE_CLOUD_AGENT_ENGINE_LOCATION",
            "GOOGLE_CLOUD_LOCATION",
            "GOOGLE_GENAI_USE_VERTEXAI",
        ]:
            os.environ.pop(key, None)

    @mock.patch.object(_runtimes_utils, "_prepare")
    @mock.patch.object(_runtimes_utils, "_await_operation")
    @mock.patch.object(
        _runtimes_utils,
        "_get_reasoning_engine_id",
        return_value=_TEST_RESOURCE_ID,
    )
    def test_create_agent_with_agent_card(
        self,
        mock_get_reasoning_engine_id,
        mock_await_operation,
        mock_prepare,
    ):
        mock_await_operation.return_value = _genai_types.RuntimeOperation(
            response=_genai_types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            )
        )
        agent = _make_agent()
        with mock.patch.object(
            self.client.runtimes._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            self.client.runtimes.create(
                agent=agent,
                config=_genai_types.AgentRuntimeConfig(
                    display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                    staging_bucket=_TEST_STAGING_BUCKET,
                ),
            )

        request_mock.assert_called_once()
        _, _, request_dict, _ = request_mock.call_args[0]
        class_methods = request_dict["spec"]["class_methods"]
        assert any("a2a_agent_card" in method for method in class_methods)


class TestA2aPublicCardRoutes:
    """Verifies the public agent card is served at the Agent Runtime card paths."""

    def _build_agent(self):
        """Builds an A2aAgent from the agentplatform framework and runs set_up()."""
        # pylint: disable=g-import-not-at-top
        from a2a import types as a2a_types

        # pylint: enable=g-import-not-at-top
        card = a2a_types.AgentCard(
            name="Test",
            description="Test",
            supported_interfaces=[
                a2a_types.AgentInterface(
                    url="http://example.com",
                    protocol_binding="HTTP+JSON",
                    protocol_version="1.0",
                )
            ],
            version="0.0.1",
            capabilities=a2a_types.AgentCapabilities(),
            skills=[
                a2a_types.AgentSkill(
                    id="hello_world",
                    name="Returns hello world",
                    description="just returns hello world",
                    tags=["hello world"],
                    examples=["hi"],
                )
            ],
            default_input_modes=["text/plain"],
            default_output_modes=["text/plain"],
        )
        agent = A2aAgent(agent_card=card)
        with mock.patch.dict(
            os.environ,
            {
                "GOOGLE_CLOUD_PROJECT": _TEST_PROJECT,
                "GOOGLE_CLOUD_LOCATION": _TEST_LOCATION,
            },
        ):
            agent.set_up()
        return agent

    def _client(self, agent):
        """Builds a Starlette test client over the agent's registered routes."""
        # pylint: disable=g-import-not-at-top
        from starlette.applications import Starlette
        from starlette.testclient import TestClient

        # pylint: enable=g-import-not-at-top
        return TestClient(Starlette(routes=agent.rest_routes))

    def test_public_card_routes_not_shadowed_by_tenant_mount(self):
        """The public card resolves and is not shadowed by the tenant Mount."""
        client = self._client(self._build_agent())
        for path in ("/a2a/card", "/a2a/v1/card"):
            resp = client.get(path)
            assert resp.status_code == 200
            body = resp.json()
            assert body["name"] == "Test"
            assert body["skills"][0]["id"] == "hello_world"


class TestCreateAgentCard:
    """Tests for create_agent_card security_schemes, security, and kwargs support."""

    def test_create_agent_card_with_security_and_kwargs(self):
        """Verifies create_agent_card forwards security_schemes, security, and kwargs."""
        # pylint: disable=g-import-not-at-top
        from a2a import types as a2a_types

        # pylint: enable=g-import-not-at-top
        security_schemes = {
            "bearer_auth": a2a_types.SecurityScheme(
                http_auth_security_scheme=a2a_types.HTTPAuthSecurityScheme(
                    scheme="Bearer",
                    bearer_format="JWT",
                )
            )
        }
        security = [{"bearer_auth": ["read"]}]

        card = create_agent_card(
            agent_name="Secure Agent",
            description="An agent with security schemes",
            skills=[_TEST_SKILL],
            security_schemes=security_schemes,
            security=security,
            documentation_url="https://example.com/docs",
        )

        assert card.name == "Secure Agent"
        assert card.documentation_url == "https://example.com/docs"
        assert "bearer_auth" in card.security_schemes
        assert (
            card.security_schemes[
                "bearer_auth"
            ].http_auth_security_scheme.scheme
            == "Bearer"
        )
        assert len(card.security_requirements) == 1
        assert list(
            card.security_requirements[0].schemes["bearer_auth"].list
        ) == ["read"]

    def test_create_agent_card_with_security_requirement_proto(self):
        """Verifies create_agent_card accepts SecurityRequirement, StringList, and wrapper dicts."""
        # pylint: disable=g-import-not-at-top
        from a2a import types as a2a_types

        # pylint: enable=g-import-not-at-top
        security = [
            a2a_types.SecurityRequirement(
                schemes={"bearer_auth": a2a_types.StringList(list=["read"])}
            ),
            {"oauth2": a2a_types.StringList(list=["write"])},
            {"schemes": {"api_key": ["admin"]}},
            {"schemes": ["custom_scope"]},
        ]

        card = create_agent_card(
            agent_name="Secure Agent",
            description="An agent with security requirements",
            skills=[_TEST_SKILL],
            security=security,
        )

        assert len(card.security_requirements) == 4
        assert list(
            card.security_requirements[0].schemes["bearer_auth"].list
        ) == ["read"]
        assert list(
            card.security_requirements[1].schemes["oauth2"].list
        ) == ["write"]
        assert list(
            card.security_requirements[2].schemes["api_key"].list
        ) == ["admin"]
        assert list(
            card.security_requirements[3].schemes["schemes"].list
        ) == ["custom_scope"]

    def test_create_agent_card_with_v03_agent_card_fallback(self, monkeypatch):
        """Verifies create_agent_card falls back to security key for non-proto AgentCard."""
        # pylint: disable=g-import-not-at-top
        import sys

        # pylint: enable=g-import-not-at-top
        mock_a2a_types = mock.MagicMock()
        del mock_a2a_types.AgentCard.DESCRIPTOR
        mock_a2a_types.AgentCard.side_effect = lambda **kw: kw
        monkeypatch.setitem(sys.modules, "a2a.types", mock_a2a_types)

        security = [{"oauth2": ["openid"]}]
        card = create_agent_card(
            agent_name="Fallback Agent",
            description="Fallback description",
            skills=[_TEST_SKILL],
            security=security,
        )
        assert card["security"] == security
