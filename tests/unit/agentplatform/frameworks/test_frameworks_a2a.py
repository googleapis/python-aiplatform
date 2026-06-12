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

import importlib
import os
from unittest import mock

import pytest
import vertexai
from google.cloud.aiplatform import initializer


from a2a.types import AgentSkill

from vertexai.agent_engines.templates.a2a import A2aAgent as VertexA2aAgent
from vertexai.agent_engines.templates.a2a import create_agent_card as vertex_create_card

from agentplatform.agent_engines.templates.a2a import A2aAgent as PlatformA2aAgent
from agentplatform.agent_engines.templates.a2a import create_agent_card as platform_create_card


_TEST_LOCATION = "us-central1"
_TEST_PROJECT = "test-project"
_TEST_SKILL = AgentSkill(
    id="hello_world",
    name="Returns hello world",
    description="just returns hello world",
    tags=["hello world"],
    examples=["hi", "hello world"],
)


@pytest.fixture
def vertex_agent() -> VertexA2aAgent:
    card = vertex_create_card(agent_name="Test", description="Test", skills=[_TEST_SKILL])
    return VertexA2aAgent(agent_card=card)


@pytest.fixture
def platform_agent() -> PlatformA2aAgent:
    card = platform_create_card(agent_name="Test", description="Test", skills=[_TEST_SKILL])
    return PlatformA2aAgent(agent_card=card)


class TestA2aLocationResolution:

    @pytest.fixture(autouse=True)
    def patch_create_rest_routes(self, monkeypatch):
        """Patch to avoid optional dependencies not actually used in these tests."""
        import sys
        from unittest.mock import MagicMock

        mock_rest_routes = MagicMock()
        mock_rest_routes.create_rest_routes = MagicMock()
        monkeypatch.setitem(sys.modules, "a2a.server.routes.rest_routes", mock_rest_routes)

    def setup_method(self):
        importlib.reload(initializer)
        from google.cloud import aiplatform
        importlib.reload(aiplatform)
        importlib.reload(vertexai)
        vertexai.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize(
        "agent_fixture",
        ["vertex_agent", "platform_agent"],
    )
    def test_default_location_from_global_config(self, agent_fixture, request):
        agent = request.getfixturevalue(agent_fixture)
        with mock.patch.dict(os.environ, {}, clear=True):
            agent.set_up()
            assert os.environ.get("GOOGLE_CLOUD_LOCATION") == _TEST_LOCATION

            # Check URL in agent card
            if hasattr(agent.agent_card, "url"):
                url = agent.agent_card.url
            else:
                url = agent.agent_card.supported_interfaces[0].url
            assert _TEST_LOCATION in url

    @pytest.mark.parametrize(
        "agent_fixture",
        ["vertex_agent", "platform_agent"],
    )
    def test_location_from_agent_engine_env_var(self, agent_fixture, request):
        agent = request.getfixturevalue(agent_fixture)
        with mock.patch.dict(
            os.environ,
            {"GOOGLE_CLOUD_AGENT_ENGINE_LOCATION": "us-east1"},
            clear=True,
        ):
            agent.set_up()
            assert os.environ.get("GOOGLE_CLOUD_LOCATION") == "us-east1"

            if hasattr(agent.agent_card, "url"):
                url = agent.agent_card.url
            else:
                url = agent.agent_card.supported_interfaces[0].url
            assert "us-east1" in url

    @pytest.mark.parametrize(
        "agent_fixture",
        ["vertex_agent", "platform_agent"],
    )
    def test_location_from_cloud_location_env_var(self, agent_fixture, request):
        agent = request.getfixturevalue(agent_fixture)
        with mock.patch.dict(
            os.environ,
            {"GOOGLE_CLOUD_LOCATION": "us-west1"},
            clear=True,
        ):
            agent.set_up()
            assert os.environ.get("GOOGLE_CLOUD_LOCATION") == "us-west1"

            if hasattr(agent.agent_card, "url"):
                url = agent.agent_card.url
            else:
                url = agent.agent_card.supported_interfaces[0].url
            assert "us-west1" in url

    @pytest.mark.parametrize(
        "agent_fixture",
        ["vertex_agent", "platform_agent"],
    )
    def test_location_env_var_precedence(self, agent_fixture, request):
        agent = request.getfixturevalue(agent_fixture)
        with mock.patch.dict(
            os.environ,
            {
                "GOOGLE_CLOUD_AGENT_ENGINE_LOCATION": "us-east1",
                "GOOGLE_CLOUD_LOCATION": "us-west1",
            },
            clear=True,
        ):
            agent.set_up()
            # Should not overwrite existing GOOGLE_CLOUD_LOCATION
            assert os.environ.get("GOOGLE_CLOUD_LOCATION") == "us-west1"

            if hasattr(agent.agent_card, "url"):
                url = agent.agent_card.url
            else:
                url = agent.agent_card.supported_interfaces[0].url
            assert "us-east1" in url
