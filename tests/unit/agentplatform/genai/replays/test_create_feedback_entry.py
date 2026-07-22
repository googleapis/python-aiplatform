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

from agentplatform._genai import types
from tests.unit.agentplatform.genai.replays import pytest_helper
from google.genai._api_client import HttpOptions
import pytest

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="feedback_entries.create",
    http_options=HttpOptions(
        api_version="v1beta1",
    ),
)

pytest_plugins = ("pytest_asyncio",)


def test_create(client):
    agent_engine = client.runtimes.create()
    assert isinstance(agent_engine, types.Runtime)
    assert isinstance(agent_engine.api_resource, types.ReasoningEngine)

    try:
        operation = client.feedback_entries.create(
            name=agent_engine.api_resource.name,
            session_id="session_123",
            event_id="event_456",
            feedback_type=types.FeedbackType.THUMBS_UP,
            config=types.CreateRuntimeFeedbackEntryConfig(
                feedback_text="Great response!",
                feedback_labels=["incomplete", "inaccurate"],
                user_id="user_789",
                source="Test IDE",
                custom_metadata={"key1": "val1", "key2": "val2"},
            ),
        )
        assert isinstance(operation, types.RuntimeFeedbackEntryOperation)
        assert operation.done

        assert operation.response is not None
        assert isinstance(operation.response, types.FeedbackEntry)
        assert operation.response.feedback_type == types.FeedbackType.THUMBS_UP
        assert operation.response.feedback_text == "Great response!"
        assert operation.response.session_id == "session_123"
        assert operation.response.event_id == "event_456"
        assert operation.response.source == "Test IDE"
        assert operation.response.user_id == "user_789"
        assert operation.response.feedback_labels == ["incomplete", "inaccurate"]
        assert operation.response.custom_metadata == {
            "key1": "val1",
            "key2": "val2",
        }
    finally:
        # Clean up resources.
        client.runtimes.delete(
            name=agent_engine.api_resource.name,
            force=True,
        )


@pytest.mark.asyncio
async def test_create_async(client):
    agent_engine = client.runtimes.create()
    assert isinstance(agent_engine, types.Runtime)
    assert isinstance(agent_engine.api_resource, types.ReasoningEngine)

    try:
        operation = await client.aio.feedback_entries.create(
            name=agent_engine.api_resource.name,
            session_id="session_123",
            event_id="event_456",
            feedback_type=types.FeedbackType.THUMBS_UP,
            config=types.CreateRuntimeFeedbackEntryConfig(
                feedback_text="Great response!",
                feedback_labels=["incomplete", "inaccurate"],
                user_id="user_789",
                source="Test IDE",
                custom_metadata={"key1": "val1", "key2": "val2"},
            ),
        )
        assert isinstance(operation, types.RuntimeFeedbackEntryOperation)
        assert operation.done

        assert operation.response is not None
        assert isinstance(operation.response, types.FeedbackEntry)
        assert operation.response.feedback_type == types.FeedbackType.THUMBS_UP
        assert operation.response.feedback_text == "Great response!"
        assert operation.response.session_id == "session_123"
        assert operation.response.event_id == "event_456"
        assert operation.response.source == "Test IDE"
        assert operation.response.user_id == "user_789"
        assert operation.response.feedback_labels == ["incomplete", "inaccurate"]
        assert operation.response.custom_metadata == {
            "key1": "val1",
            "key2": "val2",
        }
    finally:
        # Clean up resources.
        await client.aio.runtimes.delete(
            name=agent_engine.api_resource.name,
            force=True,
        )
