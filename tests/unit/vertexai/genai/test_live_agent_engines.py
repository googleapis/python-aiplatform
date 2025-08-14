import asyncio
import contextlib
import importlib
import json
from unittest import mock
from unittest.mock import AsyncMock, patch
import pytest
from websockets import client

from google.cloud import aiplatform
import vertexai
from google.cloud.aiplatform import initializer as aiplatform_initializer
# from vertexai._genai import live_agent_engines # Assuming this exists

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
    @patch("google.cloud.aiplatform.vertexai._genai.live_agent_engines.ws_connect")
    async def test_async_live_agent_engines_connect(self, mock_ws_connect):
        test_client = vertexai.Client(project=_TEST_PROJECT, location=_TEST_LOCATION)
        mock_ws = mock.AsyncMock()
        mock_ws_connect.return_value.__aenter__.return_value = mock_ws

        mock_ws.recv.side_effect = [
            json.dumps({"output": "HELLO"}).encode("utf-8"),
            json.dumps({"output": "WORLD"}).encode("utf-8"),
        ]

        async with test_client.aio.live.agent_engines.connect(
            agent_engine='test-agent-engine',
            config={"class_method": "bidi_stream_query", "input": {"query": "hello"}},
        ) as session:
            assert session is not None

            # Send additional messages
            await session.send({'query': 'world'})

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
                                "name": f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/reasoningEngines/test-agent-engine",
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
