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
# pylint: disable=protected-access,bad-continuation,missing-function-docstring

from unittest import mock

from tests.unit.agentplatform.genai.replays import pytest_helper
from agentplatform._genai import types
from google.genai import _api_client
import httpx
import pytest


# These tests target a2a-sdk 1.0, where the request/response types are protobuf
# messages and client errors are surfaced as `A2AClientError`.
pytest.importorskip(
    "a2a.client.errors", reason="a2a-sdk not installed, skipping Agent Engine A2A tests"
)
from a2a.client import (  # noqa: E402  # pylint: disable=g-import-not-at-top,g-bad-import-order
    errors as a2a_errors,
)
from a2a import types as a2a_types  # noqa: E402

pytest_plugins = ("pytest_asyncio",)


def _build_send_message_request() -> "a2a_types.SendMessageRequest":
    """Builds an a2a 1.0 SendMessageRequest proto for on_message_send."""
    return a2a_types.SendMessageRequest(
        message=a2a_types.Message(
            message_id="msg-123",
            role=a2a_types.Role.ROLE_USER,
            parts=[a2a_types.Part(text="Where will be the Super Bowl held in 2026?")],
        )
    )


@pytest.mark.asyncio
async def test_timeout_is_set(client):
    agent_engine = client.agent_engines.get(
        name="projects/964831358985/locations/us-central1/reasoningEngines/6859679872613089280",
    )
    assert isinstance(agent_engine, types.AgentEngine)

    with mock.patch(
        "httpx.AsyncClient", spec=httpx.AsyncClient
    ) as mock_async_client_factory:
        # Replay mode does not capture A2A calls so instead of relying on the
        # real service, we simulate a failed call.
        mock_response = httpx.Response(
            401,
            request=httpx.Request("POST", "url"),
            json={
                "error": {
                    "code": "UNAUTHENTICATED",
                    "message": "Authentication failed: Missing or invalid API key.",
                }
            },
        )
        mock_async_client_instance = mock_async_client_factory.return_value
        mock_async_client_instance.post.return_value = mock_response
        mock_async_client_instance.send.return_value = mock_response

        # These credentials are missing in replay mode, so we need to set a fake
        # value. (This is not necessary in record mode.)
        class FakeCredentials:
            token = "fake-token"

        agent_engine.api_client._api_client._credentials = FakeCredentials()

        # In a2a 1.0 the wrapped operation forwards the `request` kwarg directly
        # to `client.send_message(request)`, and HTTP failures surface as an
        # `A2AClientError` (the legacy `A2AClientHTTPError` no longer exists).
        with pytest.raises(a2a_errors.A2AClientError) as exc_info:
            await agent_engine.on_message_send(request=_build_send_message_request())

        # Make sure the authentication failure was propagated, otherwise the
        # test is not validating the request path.
        assert "401" in str(exc_info.value)

    mock_async_client_factory.assert_called_once()
    assert mock_async_client_factory.call_args.kwargs["timeout"] == 99.0


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.get",
    http_options=_api_client.HttpOptions(timeout=99000),
)
