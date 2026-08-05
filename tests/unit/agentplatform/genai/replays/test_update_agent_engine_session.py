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
from tests.unit.agentplatform.genai.replays import pytest_helper
import pytest


def test_update_session(client):
  agent_engine = client.agent_engines.create()
  try:
    assert isinstance(agent_engine, types.AgentEngine)
    assert isinstance(agent_engine.api_resource, types.ReasoningEngine)

    session_operation = client.agent_engines.sessions.create(
        name=agent_engine.api_resource.name,
        user_id="test-user-123",
        config=types.CreateAgentEngineSessionConfig(
            display_name="initial_session",
        ),
    )
    assert isinstance(session_operation, types.AgentEngineSessionOperation)

    updated_session = client.agent_engines.sessions.update(
        name=session_operation.response.name,
        config=types.UpdateAgentEngineSessionConfig(
            display_name="updated_session",
            user_id="test-user-123",
            labels={"env": "test", "tier": "dev"},
        ),
    )
    assert isinstance(updated_session, types.Session)
    assert updated_session.display_name == "updated_session"
    assert updated_session.user_id == "test-user-123"
    assert updated_session.labels == {"env": "test", "tier": "dev"}

    # Second update: update with explicit update_mask
    mask_updated_session = client.agent_engines.sessions.update(
        name=session_operation.response.name,
        config=types.UpdateAgentEngineSessionConfig(
            display_name="session_with_mask",
            user_id="test-user-123",
            update_mask="displayName",
        ),
    )
    assert isinstance(mask_updated_session, types.Session)
    assert mask_updated_session.display_name == "session_with_mask"

    # Third update: update with ttl (duration)
    ttl_updated_session = client.agent_engines.sessions.update(
        name=session_operation.response.name,
        config=types.UpdateAgentEngineSessionConfig(
            user_id="test-user-123",
            ttl="86400s",
        ),
    )
    assert isinstance(ttl_updated_session, types.Session)
  finally:
    client.agent_engines.delete(name=agent_engine.api_resource.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.sessions.update",
)

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_update_session_async(client):
  agent_engine = client.agent_engines.create()
  try:
    assert isinstance(agent_engine, types.AgentEngine)
    assert isinstance(agent_engine.api_resource, types.ReasoningEngine)

    session_operation = await client.aio.agent_engines.sessions.create(
        name=agent_engine.api_resource.name,
        user_id="test-user-123",
        config=types.CreateAgentEngineSessionConfig(
            display_name="initial_session",
        ),
    )
    assert isinstance(session_operation, types.AgentEngineSessionOperation)

    updated_session = await client.aio.agent_engines.sessions.update(
        name=session_operation.response.name,
        config=types.UpdateAgentEngineSessionConfig(
            display_name="updated_session",
            user_id="test-user-123",
            labels={"env": "test", "tier": "dev"},
            ttl="86400s",
        ),
    )
    assert isinstance(updated_session, types.Session)
    assert updated_session.display_name == "updated_session"
    assert updated_session.user_id == "test-user-123"
    assert updated_session.labels == {"env": "test", "tier": "dev"}
  finally:
    client.agent_engines.delete(name=agent_engine.api_resource.name, force=True)
