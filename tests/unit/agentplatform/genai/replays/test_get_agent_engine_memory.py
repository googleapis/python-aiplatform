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

from tests.unit.agentplatform.genai.replays import pytest_helper
from agentplatform._genai import types


def test_get_memory(client):
    agent_engine = client.runtimes.create()
    operation = client.runtimes.memories.create(
        name=agent_engine.api_resource.name,
        fact="memory_fact",
        scope={"user_id": "123"},
    )
    assert isinstance(operation, types.RuntimeMemoryOperation)
    memory = client.runtimes.memories.get(
        name=operation.response.name,
    )
    assert isinstance(memory, types.Memory)
    assert memory.name == operation.response.name
    client.runtimes.delete(name=agent_engine.api_resource.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="runtimes.memories.get",
)


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_get_memory_async(client):
    agent_engine = client.runtimes.create()
    operation = await client.aio.runtimes.memories.create(
        name=agent_engine.api_resource.name,
        fact="memory_fact",
        scope={"user_id": "123"},
    )
    assert isinstance(operation, types.RuntimeMemoryOperation)
    memory = await client.aio.runtimes.memories.get(
        name=operation.response.name,
    )
    assert isinstance(memory, types.Memory)
    assert memory.name == operation.response.name
    await client.aio.runtimes.delete(
        name=agent_engine.api_resource.name, force=True
    )
