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


def test_list_memories(client):
    agent_engine = client.agent_engines.create()
    assert not list(
        client.agent_engines.memories.list(
            name=agent_engine.api_resource.name,
        )
    )
    client.agent_engines.memories.create(
        name=agent_engine.api_resource.name,
        fact="memory_fact",
        scope={"user_id": "123"},
        config={
            "wait_for_completion": True,
        },
    )
    client.agent_engines.memories.create(
        name=agent_engine.api_resource.name,
        fact="memory_fact_2",
        scope={"user_id": "456"},
        config={
            "wait_for_completion": True,
        },
    )
    memory_list = client.agent_engines.memories.list(
        name=agent_engine.api_resource.name,
        config=types.ListAgentEngineMemoryConfig(
            page_size=1,
            order_by="create_time asc",
        ),
    )
    assert len(memory_list) == 1
    assert isinstance(memory_list[0], types.Memory)
    assert memory_list[0].fact == "memory_fact"
    assert memory_list[0].scope["user_id"] == "123"
    # Clean up resources.
    agent_engine.delete(force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.memories.list",
)


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_async_list_memories(client):
    agent_engine = client.agent_engines.create()
    pager = await client.aio.agent_engines.memories.list(
        name=agent_engine.api_resource.name
    )
    assert not [item async for item in pager]

    await client.aio.agent_engines.memories.create(
        name=agent_engine.api_resource.name,
        fact="memory_fact_2",
        scope={"user_id": "456"},
        config={
            "wait_for_completion": True,
        },
    )
    pager = await client.aio.agent_engines.memories.list(
        name=agent_engine.api_resource.name
    )
    memory_list = [item async for item in pager]
    assert len(memory_list) == 1
    assert isinstance(memory_list[0], types.Memory)

    await client.aio.agent_engines.delete(
        name=agent_engine.api_resource.name, force=True
    )
