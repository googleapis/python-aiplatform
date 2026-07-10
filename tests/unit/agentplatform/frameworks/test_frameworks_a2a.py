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
                config=_genai_types.RuntimeConfig(
                    display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                    staging_bucket=_TEST_STAGING_BUCKET,
                ),
            )

        request_mock.assert_called_once()
        _, _, request_dict, _ = request_mock.call_args[0]
        class_methods = request_dict["spec"]["class_methods"]
        assert any("a2a_agent_card" in method for method in class_methods)


class TestA2aLocationResolution:
    @pytest.fixture(autouse=True)
    def patch_create_rest_routes(self, monkeypatch):
        """Patch to avoid optional dependencies not actually used in these tests."""
        import sys
        from unittest.mock import MagicMock

        mock_rest_routes = MagicMock()
        mock_rest_routes.create_rest_routes = MagicMock()
        monkeypatch.setitem(
            sys.modules, "a2a.server.routes.rest_routes", mock_rest_routes
        )

    def test_location_from_agent_engine_env_var(self):
        agent = _make_agent()
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

    def test_location_env_var_precedence(self):
        agent = _make_agent()
        with mock.patch.dict(
            os.environ,
            {
                "GOOGLE_CLOUD_AGENT_ENGINE_LOCATION": "us-east1",
                "GOOGLE_CLOUD_LOCATION": "us-west1",
            },
            clear=True,
        ):
            agent.set_up()
            # Should not overwrite existing GOOGLE_CLOUD_LOCATION.
            assert os.environ.get("GOOGLE_CLOUD_LOCATION") == "us-west1"

            if hasattr(agent.agent_card, "url"):
                url = agent.agent_card.url
            else:
                url = agent.agent_card.supported_interfaces[0].url
            assert "us-east1" in url
