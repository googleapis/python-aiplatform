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

from agentplatform._genai import types
from tests.unit.agentplatform.genai.replays import pytest_helper


def test_get_memory(client):
    memory_bank = client.memory_banks.create()
    try:
        operation = client.memory_banks.memories.create(
            name=memory_bank.name,
            fact="memory_fact",
            scope={"user_id": "123"},
        )
        assert isinstance(operation, types.MemoryOperation)
        memory = client.memory_banks.memories.get(
            name=operation.response.name,
        )
        assert isinstance(memory, types.Memory)
        assert memory.name == operation.response.name
    finally:
        client.memory_banks.delete(name=memory_bank.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="memory_banks.memories.get",
)


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_get_memory_async(client):
    memory_bank = client.memory_banks.create()
    operation = await client.aio.memory_banks.memories.create(
        name=memory_bank.name,
        fact="memory_fact",
        scope={"user_id": "123"},
    )
    assert isinstance(operation, types.MemoryOperation)
    memory = await client.aio.memory_banks.memories.get(
        name=operation.response.name,
    )
    assert isinstance(memory, types.Memory)
    assert memory.name == operation.response.name
    await client.aio.memory_banks.delete(name=memory_bank.name, force=True)
