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

import datetime
import pytest

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types


def test_list_session_events(client):
    agent_engine = client.agent_engines.create()
    operation = client.agent_engines.sessions.create(
        name=agent_engine.api_resource.name,
        user_id="test-user-123",
    )
    session = operation.response
    assert not list(
        client.agent_engines.sessions.events.list(
            name=session.name,
        )
    )
    client.agent_engines.sessions.events.append(
        name=session.name,
        author="test-user-123",
        invocation_id="test-invocation-id",
        timestamp=datetime.datetime.fromtimestamp(1234567890, tz=datetime.timezone.utc),
    )
    session_event_list = client.agent_engines.sessions.events.list(
        name=session.name,
    )
    assert len(session_event_list) == 1
    assert isinstance(session_event_list[0], types.SessionEvent)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.sessions.events.list",
)


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_async_list_session_events(client):
    agent_engine = client.agent_engines.create()
    operation = await client.aio.agent_engines.sessions.create(
        name=agent_engine.api_resource.name,
        user_id="test-user-123",
    )
    session = operation.response
    pager = await client.aio.agent_engines.sessions.events.list(name=session.name)
    assert not [item async for item in pager]

    await client.aio.agent_engines.sessions.events.append(
        name=session.name,
        author="test-user-123",
        invocation_id="test-invocation-id",
        timestamp=datetime.datetime.fromtimestamp(1234567890, tz=datetime.timezone.utc),
    )
    pager = await client.aio.agent_engines.sessions.events.list(name=session.name)
    session_event_list = [item async for item in pager]
    assert len(session_event_list) == 1
    assert isinstance(session_event_list[0], types.SessionEvent)

    client.agent_engines.delete(name=agent_engine.api_resource.name, force=True)
