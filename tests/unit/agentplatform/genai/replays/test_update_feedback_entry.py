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
    test_method="feedback_entries.update",
    http_options=HttpOptions(
        api_version="v1beta1",
    ),
)

pytest_plugins = ("pytest_asyncio",)


def test_update(client):
    agent_engine = client.agent_engines.create()
    assert isinstance(agent_engine, types.AgentEngine)
    assert isinstance(agent_engine.api_resource, types.ReasoningEngine)

    try:
        operation = client.feedback_entries.create(
            name=agent_engine.api_resource.name,
            session_id="session_123",
            event_id="event_456",
            feedback_type=types.FeedbackType.THUMBS_UP,
            config=types.CreateRuntimeFeedbackEntryConfig(
                feedback_text="Great response!",
                feedback_labels=["incomplete"],
                user_id="user_789",
                source="Test IDE",
                custom_metadata={"key1": "val1", "key2": "val2"},
            ),
        )
        assert isinstance(operation, types.RuntimeFeedbackEntryOperation)
        assert operation.done

        assert operation.response is not None
        assert isinstance(operation.response, types.FeedbackEntry)

        feedback_entry = operation.response

        update_operation = client.feedback_entries.update(
            name=feedback_entry.name,
            config=types.UpdateRuntimeFeedbackEntryConfig(
                update_mask="feedbackType,feedbackText,feedbackLabels,userId,source,customMetadata",
                feedback_type=types.FeedbackType.THUMBS_DOWN,
                feedback_text="Actually bad response!",
                feedback_labels=["inaccurate", "too_slow"],
                user_id="user_new_999",
                source="New Surface",
                custom_metadata={"key1": "val1", "key2": "val2"},
            ),
        )

        assert isinstance(update_operation, types.RuntimeFeedbackEntryOperation)
        assert update_operation.done

        updated_feedback = update_operation.response
        assert updated_feedback is not None
        assert isinstance(updated_feedback, types.FeedbackEntry)
        assert updated_feedback.feedback_type == types.FeedbackType.THUMBS_DOWN
        assert updated_feedback.feedback_text == "Actually bad response!"
        assert updated_feedback.user_id == "user_new_999"
        assert updated_feedback.source == "New Surface"
        assert updated_feedback.feedback_labels == ["inaccurate", "too_slow"]
        assert updated_feedback.custom_metadata == {"key1": "val1", "key2": "val2"}
        assert updated_feedback.session_id == "session_123"
        assert updated_feedback.event_id == "event_456"

        # Second update: change only session_id and event_id via a scoped mask.
        session_update_operation = client.feedback_entries.update(
            name=feedback_entry.name,
            config=types.UpdateRuntimeFeedbackEntryConfig(
                update_mask="sessionId,eventId",
                session_id="session_new_456",
                event_id="event_new_789",
            ),
        )

        assert isinstance(session_update_operation, types.RuntimeFeedbackEntryOperation)
        assert session_update_operation.done

        session_updated_feedback = session_update_operation.response
        assert session_updated_feedback is not None
        assert isinstance(session_updated_feedback, types.FeedbackEntry)
        assert session_updated_feedback.session_id == "session_new_456"
        assert session_updated_feedback.event_id == "event_new_789"
        # Fields from the first update are preserved.
        assert session_updated_feedback.feedback_type == types.FeedbackType.THUMBS_DOWN
        assert session_updated_feedback.feedback_labels == [
            "inaccurate",
            "too_slow",
        ]

    finally:
        # Clean up resources.
        client.agent_engines.delete(
            name=agent_engine.api_resource.name,
            force=True,
        )


@pytest.mark.asyncio
async def test_update_async(client):
    agent_engine = client.agent_engines.create()
    assert isinstance(agent_engine, types.AgentEngine)
    assert isinstance(agent_engine.api_resource, types.ReasoningEngine)

    try:
        operation = await client.aio.feedback_entries.create(
            name=agent_engine.api_resource.name,
            session_id="session_123",
            event_id="event_456",
            feedback_type=types.FeedbackType.THUMBS_UP,
            config=types.CreateRuntimeFeedbackEntryConfig(
                feedback_text="Great response!",
                feedback_labels=["incomplete"],
                user_id="user_789",
                source="Test IDE",
                custom_metadata={"key1": "val1", "key2": "val2"},
            ),
        )
        assert isinstance(operation, types.RuntimeFeedbackEntryOperation)
        assert operation.done

        assert operation.response is not None
        assert isinstance(operation.response, types.FeedbackEntry)

        feedback_entry = operation.response

        update_operation = await client.aio.feedback_entries.update(
            name=feedback_entry.name,
            config=types.UpdateRuntimeFeedbackEntryConfig(
                update_mask="feedbackType,feedbackText,feedbackLabels,userId,source,customMetadata",
                feedback_type=types.FeedbackType.THUMBS_DOWN,
                feedback_text="Actually bad response!",
                feedback_labels=["inaccurate", "too_slow"],
                user_id="user_new_999",
                source="New Surface",
                custom_metadata={"key1": "val1", "key2": "val2"},
            ),
        )

        assert isinstance(update_operation, types.RuntimeFeedbackEntryOperation)
        assert update_operation.done

        updated_feedback = update_operation.response
        assert updated_feedback is not None
        assert isinstance(updated_feedback, types.FeedbackEntry)
        assert updated_feedback.feedback_type == types.FeedbackType.THUMBS_DOWN
        assert updated_feedback.feedback_text == "Actually bad response!"
        assert updated_feedback.user_id == "user_new_999"
        assert updated_feedback.source == "New Surface"
        assert updated_feedback.feedback_labels == ["inaccurate", "too_slow"]
        assert updated_feedback.custom_metadata == {"key1": "val1", "key2": "val2"}
        assert updated_feedback.session_id == "session_123"
        assert updated_feedback.event_id == "event_456"

        # Second update: change only session_id and event_id via a scoped mask.
        session_update_operation = await client.aio.feedback_entries.update(
            name=feedback_entry.name,
            config=types.UpdateRuntimeFeedbackEntryConfig(
                update_mask="sessionId,eventId",
                session_id="session_new_456",
                event_id="event_new_789",
            ),
        )

        assert isinstance(session_update_operation, types.RuntimeFeedbackEntryOperation)
        assert session_update_operation.done

        session_updated_feedback = session_update_operation.response
        assert session_updated_feedback is not None
        assert isinstance(session_updated_feedback, types.FeedbackEntry)
        assert session_updated_feedback.session_id == "session_new_456"
        assert session_updated_feedback.event_id == "event_new_789"
        # Fields from the first update are preserved.
        assert session_updated_feedback.feedback_type == types.FeedbackType.THUMBS_DOWN
        assert session_updated_feedback.feedback_labels == [
            "inaccurate",
            "too_slow",
        ]

    finally:
        # Clean up resources.
        await client.aio.agent_engines.delete(
            name=agent_engine.api_resource.name,
            force=True,
        )
