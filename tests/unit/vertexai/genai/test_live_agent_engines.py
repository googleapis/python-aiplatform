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
from unittest import mock

import google.auth
import google.auth.credentials
from google.cloud import aiplatform
import vertexai
from google.cloud.aiplatform import initializer as aiplatform_initializer
from vertexai._genai import live_agent_engines
import pytest


_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
pytestmark = pytest.mark.usefixtures("google_auth_mock")


class TestLiveAgentEngines:
    """Unit tests for the GenAI client."""

    def setup_method(self):
        importlib.reload(aiplatform_initializer)
        importlib.reload(aiplatform)
        importlib.reload(vertexai)
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("google_auth_mock")
    @mock.patch.object(live_agent_engines, "ws_connect")
    @mock.patch.object(google.auth, "default")
    async def test_async_live_agent_engines_connect(
        self, mock_auth_default, mock_ws_connect
    ):
        """Tests the AsyncLiveAgentEngines.connect method, as well as the AsyncLiveAgentEngineSession methods."""
        # Mock credentials to avoid refresh issues
        mock_creds = mock.Mock(spec=google.auth.credentials.Credentials)
        mock_creds.token = "test-token"
        mock_creds.valid = True
        mock_auth_default.return_value = (mock_creds, None)

        test_client = vertexai.Client(project=_TEST_PROJECT, location=_TEST_LOCATION)
        mock_ws = mock.AsyncMock()
        mock_ws_connect.return_value.__aenter__.return_value = mock_ws

        mock_ws.recv.side_effect = [
            json.dumps({"output": "HELLO"}).encode("utf-8"),
            json.dumps({"output": "WORLD"}).encode("utf-8"),
        ]

        async with test_client.aio.live.agent_engines.connect(
            agent_engine="test-agent-engine",
            config={"class_method": "bidi_stream_query", "input": {"query": "hello"}},
        ) as session:
            assert session is not None

            # Send additional messages
            await session.send({"query": "world"})

            # Receive responses
            responses = []
            response = await session.receive()
            responses.append(response)
            response = await session.receive()
            responses.append(response)

            await session.close()

        assert responses == [{"output": "HELLO"}, {"output": "WORLD"}]

        mock_ws.send.assert_has_calls(
            [
                mock.call(
                    json.dumps(
                        {
                            "setup": {
                                "name": (
                                    f"projects/{_TEST_PROJECT}/locations/"
                                    f"{_TEST_LOCATION}/reasoningEngines/"
                                    "test-agent-engine"
                                ),
                                "class_method": "bidi_stream_query",
                                "input": {"query": "hello"},
                            }
                        }
                    )
                ),
                mock.call(json.dumps({"bidi_stream_input": {"query": "world"}})),
            ]
        )
        mock_ws.close.assert_called_once()
        mock_auth_default.assert_called_once_with(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        mock_creds.refresh.assert_not_called()
