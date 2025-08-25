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

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types


def test_create_session_with_ttl(client):
    agent_engine = client.agent_engines.create()
    assert isinstance(agent_engine, types.AgentEngine)
    assert isinstance(agent_engine.api_resource, types.ReasoningEngine)

    operation = client.agent_engines.create_session(
        name=agent_engine.api_resource.name,
        user_id="test-user-123",
        config=types.CreateAgentEngineSessionConfig(
            display_name="my_session",
            session_state={"foo": "bar"},
            ttl="120s",
        ),
    )
    assert isinstance(operation, types.AgentEngineSessionOperation)
    assert operation.response.display_name == "my_session"
    assert operation.response.session_state == {"foo": "bar"}
    assert operation.response.user_id == "test-user-123"
    assert operation.response.name.startswith(agent_engine.api_resource.name)
    # Expire time is calculated by the server, so we only check that it is
    # within a reasonable range to avoid flakiness.
    assert (
        operation.response.create_time + datetime.timedelta(seconds=119.5)
        <= operation.response.expire_time
        <= operation.response.create_time + datetime.timedelta(seconds=120.5)
    )
    # Clean up resources.
    client.agent_engines.delete(name=agent_engine.api_resource.name, force=True)


def test_create_session_with_expire_time(client):
    agent_engine = client.agent_engines.create()
    assert isinstance(agent_engine, types.AgentEngine)
    assert isinstance(agent_engine.api_resource, types.ReasoningEngine)
    expire_time = datetime.datetime(
        2026, 1, 1, 12, 30, 00, tzinfo=datetime.timezone.utc
    )

    operation = client.agent_engines.sessions.create(
        name=agent_engine.api_resource.name,
        user_id="test-user-123",
        config=types.CreateAgentEngineSessionConfig(
            display_name="my_session",
            session_state={"foo": "bar"},
            expire_time=expire_time,
        ),
    )
    assert isinstance(operation, types.AgentEngineSessionOperation)
    assert operation.response.display_name == "my_session"
    assert operation.response.session_state == {"foo": "bar"}
    assert operation.response.user_id == "test-user-123"
    assert operation.response.name.startswith(agent_engine.api_resource.name)
    assert operation.response.expire_time == expire_time
    # Clean up resources.
    client.agent_engines.delete(name=agent_engine.api_resource.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.create_session",
)
