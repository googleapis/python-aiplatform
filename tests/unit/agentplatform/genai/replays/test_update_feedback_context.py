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
# pylint: disable=protected-access,bad-continuation,missing-function-docstring

from agentplatform._genai import types
from google.genai import types as genai_types
from tests.unit.agentplatform.genai.replays import pytest_helper
from google.genai._api_client import HttpOptions
import pytest

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="feedback_entries.feedback_contexts.update",
    http_options=HttpOptions(
        api_version="v1beta1",
    ),
)

pytest_plugins = ("pytest_asyncio",)


def test_update_and_get(client):
    agent_engine = client.agent_engines.create()

    try:
        operation = client.feedback_entries.create(
            name=agent_engine.api_resource.name,
            session_id="session_123",
            event_id="event_456",
            feedback_type=types.FeedbackType.THUMBS_UP,
        )
        feedback_entry = operation.response

        update_operation = client.feedback_entries.feedback_contexts.update(
            parent=feedback_entry.name,
            context_events=[
                types.SessionEvent(
                    author="user",
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="Hello World")]
                    ),
                )
            ],
        )

        assert isinstance(update_operation, types.RuntimeFeedbackContextOperation)
        assert update_operation.done

        updated_context = update_operation.response
        assert updated_context is not None
        assert isinstance(updated_context, types.FeedbackContext)
        assert updated_context.name == f"{feedback_entry.name}/feedbackContext"
        assert len(updated_context.context_events) == 1
        assert updated_context.context_events[0].content.parts[0].text == "Hello World"

        fetched_context = client.feedback_entries.feedback_contexts.get(
            parent=feedback_entry.name,
        )
        assert isinstance(fetched_context, types.FeedbackContext)
        assert fetched_context.name == f"{feedback_entry.name}/feedbackContext"
        assert len(fetched_context.context_events) == 1
        assert fetched_context.context_events[0].content.parts[0].text == "Hello World"

        update_operation = client.feedback_entries.feedback_contexts.update(
            parent=feedback_entry.name,
            context_events=[
                types.SessionEvent(
                    author="user",
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="Hello World")]
                    ),
                ),
                types.SessionEvent(
                    author="model",
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="Hello back")]
                    ),
                ),
            ],
        )
        assert isinstance(update_operation, types.RuntimeFeedbackContextOperation)
        assert update_operation.done

        updated_context = update_operation.response
        assert len(updated_context.context_events) == 2
        assert updated_context.context_events[1].content.parts[0].text == "Hello back"

        update_operation = client.feedback_entries.feedback_contexts.update(
            parent=feedback_entry.name,
            context_events=[],
        )
        assert isinstance(update_operation, types.RuntimeFeedbackContextOperation)
        assert update_operation.done

        updated_context = update_operation.response
        assert not updated_context.context_events

    finally:
        # Clean up resources.
        client.agent_engines.delete(
            name=agent_engine.api_resource.name,
            force=True,
        )


@pytest.mark.asyncio
async def test_update_and_get_async(client):
    agent_engine = client.agent_engines.create()

    try:
        operation = await client.aio.feedback_entries.create(
            name=agent_engine.api_resource.name,
            session_id="session_123",
            event_id="event_456",
            feedback_type=types.FeedbackType.THUMBS_UP,
        )
        feedback_entry = operation.response

        update_operation = await client.aio.feedback_entries.feedback_contexts.update(
            parent=feedback_entry.name,
            context_events=[
                types.SessionEvent(
                    author="user",
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="Hello World")]
                    ),
                )
            ],
        )

        assert isinstance(update_operation, types.RuntimeFeedbackContextOperation)
        assert update_operation.done

        updated_context = update_operation.response
        assert updated_context is not None
        assert isinstance(updated_context, types.FeedbackContext)
        assert updated_context.name == f"{feedback_entry.name}/feedbackContext"
        assert len(updated_context.context_events) == 1
        assert updated_context.context_events[0].content.parts[0].text == "Hello World"

        fetched_context = await client.aio.feedback_entries.feedback_contexts.get(
            parent=feedback_entry.name,
        )
        assert isinstance(fetched_context, types.FeedbackContext)
        assert fetched_context.name == f"{feedback_entry.name}/feedbackContext"
        assert len(fetched_context.context_events) == 1
        assert fetched_context.context_events[0].content.parts[0].text == "Hello World"

        update_operation = await client.aio.feedback_entries.feedback_contexts.update(
            parent=feedback_entry.name,
            context_events=[
                types.SessionEvent(
                    author="user",
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="Hello World")]
                    ),
                ),
                types.SessionEvent(
                    author="model",
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="Hello back")]
                    ),
                ),
            ],
        )
        assert isinstance(update_operation, types.RuntimeFeedbackContextOperation)
        assert update_operation.done

        updated_context = update_operation.response
        assert len(updated_context.context_events) == 2
        assert updated_context.context_events[1].content.parts[0].text == "Hello back"

        update_operation = await client.aio.feedback_entries.feedback_contexts.update(
            parent=feedback_entry.name,
            context_events=[],
        )
        assert isinstance(update_operation, types.RuntimeFeedbackContextOperation)
        assert update_operation.done

        updated_context = update_operation.response
        assert not updated_context.context_events

    finally:
        # Clean up resources.
        await client.aio.agent_engines.delete(
            name=agent_engine.api_resource.name,
            force=True,
        )
