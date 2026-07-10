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
from google.genai import errors
from google.genai._api_client import HttpOptions
import pytest

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="feedback_entries.delete",
    http_options=HttpOptions(
        api_version="v1beta1",
    ),
)

pytest_plugins = ("pytest_asyncio",)


def test_delete(client):
    agent_engine = client.runtimes.create()
    assert isinstance(agent_engine, types.Runtime)
    assert isinstance(agent_engine.api_resource, types.ReasoningEngine)

    try:
        create_operation = client.feedback_entries.create(
            name=agent_engine.api_resource.name,
            session_id="session_123",
            event_id="event_456",
            feedback_type=types.FeedbackType.THUMBS_UP,
        )
        assert create_operation.done

        delete_operation = client.feedback_entries.delete(
            name=create_operation.response.name
        )
        assert isinstance(
            delete_operation,
            types.DeleteRuntimeFeedbackEntryOperation,
        )
        assert delete_operation.done

        with pytest.raises(errors.ClientError, match="404 NOT_FOUND"):
            client.feedback_entries.get(name=create_operation.response.name)
    finally:
        # Clean up resources.
        client.runtimes.delete(
            name=agent_engine.api_resource.name,
            force=True,
        )


@pytest.mark.asyncio
async def test_delete_async(client):
    agent_engine = client.runtimes.create()
    assert isinstance(agent_engine, types.Runtime)
    assert isinstance(agent_engine.api_resource, types.ReasoningEngine)

    try:
        create_operation = await client.aio.feedback_entries.create(
            name=agent_engine.api_resource.name,
            session_id="session_123",
            event_id="event_456",
            feedback_type=types.FeedbackType.THUMBS_UP,
        )
        assert create_operation.done

        delete_operation = await client.aio.feedback_entries.delete(
            name=create_operation.response.name
        )
        assert isinstance(
            delete_operation,
            types.DeleteRuntimeFeedbackEntryOperation,
        )

        with pytest.raises(errors.ClientError, match="404 NOT_FOUND"):
            await client.aio.feedback_entries.get(name=create_operation.response.name)
    finally:
        # Clean up resources.
        await client.aio.runtimes.delete(
            name=agent_engine.api_resource.name,
            force=True,
        )
