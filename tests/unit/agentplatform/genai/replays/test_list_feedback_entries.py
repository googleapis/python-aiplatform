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
    test_method="feedback_entries.list",
    http_options=HttpOptions(
        api_version="v1beta1",
    ),
)

pytest_plugins = ("pytest_asyncio",)


def test_list(client):
    agent_engine = client.agent_engines.create()
    assert isinstance(agent_engine, types.AgentEngine)
    assert isinstance(agent_engine.api_resource, types.ReasoningEngine)

    try:
        # Create THUMBS_UP feedback entry.
        operation_up = client.feedback_entries.create(
            name=agent_engine.api_resource.name,
            session_id="session_123",
            event_id="event_456",
            feedback_type=types.FeedbackType.THUMBS_UP,
            config=types.CreateAgentEngineFeedbackEntryConfig(
                feedback_text="Great response!",
                feedback_labels=["incomplete", "inaccurate"],
                user_id="user_789",
                source="Test IDE",
                custom_metadata={"key1": "val1", "key2": "val2"},
            ),
        )
        assert isinstance(operation_up, types.AgentEngineFeedbackEntryOperation)
        assert operation_up.done

        # Create THUMBS_DOWN feedback entry.
        operation_down = client.feedback_entries.create(
            name=agent_engine.api_resource.name,
            session_id="session_abc",
            event_id="event_xyz",
            feedback_type=types.FeedbackType.THUMBS_DOWN,
            config=types.CreateAgentEngineFeedbackEntryConfig(
                feedback_text="Response was incorrect.",
                feedback_labels=["off_topic", "hallucination"],
                user_id="user_789",
                source="Test IDE",
                custom_metadata={"key_a": "val_a"},
            ),
        )
        assert isinstance(operation_down, types.AgentEngineFeedbackEntryOperation)
        assert operation_down.done

        # List and verify the feedback entries.
        response = client.feedback_entries.list(parent=agent_engine.api_resource.name)
        feedback_entries = list(response)
        assert len(feedback_entries) == 2

        thumbs_up_entry = next(
            f
            for f in feedback_entries
            if f.feedback_type == types.FeedbackType.THUMBS_UP
        )
        thumbs_down_entry = next(
            f
            for f in feedback_entries
            if f.feedback_type == types.FeedbackType.THUMBS_DOWN
        )

        assert thumbs_up_entry.feedback_text == "Great response!"
        assert thumbs_up_entry.user_id == "user_789"
        assert thumbs_up_entry.source == "Test IDE"
        assert thumbs_up_entry.session_id == "session_123"
        assert thumbs_up_entry.event_id == "event_456"
        assert thumbs_up_entry.feedback_labels == ["incomplete", "inaccurate"]
        assert thumbs_up_entry.custom_metadata == {"key1": "val1", "key2": "val2"}

        assert thumbs_down_entry.feedback_text == "Response was incorrect."
        assert thumbs_down_entry.user_id == "user_789"
        assert thumbs_down_entry.source == "Test IDE"
        assert thumbs_down_entry.session_id == "session_abc"
        assert thumbs_down_entry.event_id == "event_xyz"
        assert thumbs_down_entry.feedback_labels == ["off_topic", "hallucination"]
        assert thumbs_down_entry.custom_metadata == {"key_a": "val_a"}
    finally:
        # Clean up resources.
        client.agent_engines.delete(
            name=agent_engine.api_resource.name,
            force=True,
        )


@pytest.mark.asyncio
async def test_list_async(client):
    agent_engine = client.agent_engines.create()
    assert isinstance(agent_engine, types.AgentEngine)
    assert isinstance(agent_engine.api_resource, types.ReasoningEngine)

    try:
        # Create THUMBS_UP feedback entry.
        operation_up = await client.aio.feedback_entries.create(
            name=agent_engine.api_resource.name,
            session_id="session_123",
            event_id="event_456",
            feedback_type=types.FeedbackType.THUMBS_UP,
            config=types.CreateAgentEngineFeedbackEntryConfig(
                feedback_text="Great response!",
                feedback_labels=["incomplete", "inaccurate"],
                user_id="user_789",
                source="Test IDE",
                custom_metadata={"key1": "val1", "key2": "val2"},
            ),
        )
        assert isinstance(operation_up, types.AgentEngineFeedbackEntryOperation)
        assert operation_up.done

        # Create THUMBS_DOWN feedback entry.
        operation_down = await client.aio.feedback_entries.create(
            name=agent_engine.api_resource.name,
            session_id="session_abc",
            event_id="event_xyz",
            feedback_type=types.FeedbackType.THUMBS_DOWN,
            config=types.CreateAgentEngineFeedbackEntryConfig(
                feedback_text="Response was incorrect.",
                feedback_labels=["off_topic", "hallucination"],
                user_id="user_789",
                source="Test IDE",
                custom_metadata={"key_a": "val_a"},
            ),
        )
        assert isinstance(operation_down, types.AgentEngineFeedbackEntryOperation)
        assert operation_down.done

        # List and verify the feedback entries.
        response = await client.aio.feedback_entries.list(
            parent=agent_engine.api_resource.name
        )
        feedback_entries = [f async for f in response]
        assert len(feedback_entries) == 2

        thumbs_up_entry = next(
            f
            for f in feedback_entries
            if f.feedback_type == types.FeedbackType.THUMBS_UP
        )
        thumbs_down_entry = next(
            f
            for f in feedback_entries
            if f.feedback_type == types.FeedbackType.THUMBS_DOWN
        )

        assert thumbs_up_entry.feedback_text == "Great response!"
        assert thumbs_up_entry.user_id == "user_789"
        assert thumbs_up_entry.source == "Test IDE"
        assert thumbs_up_entry.session_id == "session_123"
        assert thumbs_up_entry.event_id == "event_456"
        assert thumbs_up_entry.feedback_labels == ["incomplete", "inaccurate"]
        assert thumbs_up_entry.custom_metadata == {"key1": "val1", "key2": "val2"}

        assert thumbs_down_entry.feedback_text == "Response was incorrect."
        assert thumbs_down_entry.user_id == "user_789"
        assert thumbs_down_entry.source == "Test IDE"
        assert thumbs_down_entry.session_id == "session_abc"
        assert thumbs_down_entry.event_id == "event_xyz"
        assert thumbs_down_entry.feedback_labels == ["off_topic", "hallucination"]
        assert thumbs_down_entry.custom_metadata == {"key_a": "val_a"}
    finally:
        # Clean up resources.
        await client.aio.agent_engines.delete(
            name=agent_engine.api_resource.name,
            force=True,
        )
