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

import pytest

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types


def test_get_memory(client):
    agent_engine = client.agent_engines.create()
    operation = client.agent_engines.create_memory(
        name=agent_engine.api_resource.name,
        fact="memory_fact",
        scope={"user_id": "123"},
    )
    assert isinstance(operation, types.AgentEngineMemoryOperation)
    memory = client.agent_engines.get_memory(
        name=operation.response.name,
    )
    assert isinstance(memory, types.Memory)
    assert memory.name == operation.response.name


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.get_memory",
)


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_get_memory_async(client):
    # TODO(b/431785750): use async methods for create() and create_memory() when available
    agent_engine = client.agent_engines.create()
    operation = client.agent_engines.create_memory(
        name=agent_engine.api_resource.name,
        fact="memory_fact",
        scope={"user_id": "123"},
    )
    assert isinstance(operation, types.AgentEngineMemoryOperation)
    memory = await client.aio.agent_engines.get_memory(
        name=operation.response.name,
    )
    assert isinstance(memory, types.Memory)
    assert memory.name == operation.response.name
