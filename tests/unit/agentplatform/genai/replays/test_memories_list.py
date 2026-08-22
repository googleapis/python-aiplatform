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


def test_list_memories(client):
    memory_bank = client.memory_banks.create()
    try:
        assert not list(
            client.memory_banks.memories.list(
                name=memory_bank.name,
            )
        )
        client.memory_banks.memories.create(
            name=memory_bank.name,
            fact="memory_fact",
            scope={"user_id": "123"},
            config={
                "wait_for_completion": True,
            },
        )
        client.memory_banks.memories.create(
            name=memory_bank.name,
            fact="memory_fact_2",
            scope={"user_id": "456"},
            config={
                "wait_for_completion": True,
            },
        )
        memory_list = client.memory_banks.memories.list(
            name=memory_bank.name,
            config=types.ListMemoriesConfig(
                page_size=1,
                order_by="create_time asc",
            ),
        )
        assert len(memory_list) == 1
        assert isinstance(memory_list[0], types.Memory)
        assert memory_list[0].fact == "memory_fact"
        assert memory_list[0].scope["user_id"] == "123"
    finally:
        # Clean up resources.
        client.memory_banks.delete(name=memory_bank.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="memory_banks.memories.list",
)


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_async_list_memories(client):
    memory_bank = client.memory_banks.create()
    try:
        pager = await client.aio.memory_banks.memories.list(
            name=memory_bank.name,
        )
        assert not [item async for item in pager]

        await client.aio.memory_banks.memories.create(
            name=memory_bank.name,
            fact="memory_fact_2",
            scope={"user_id": "456"},
            config={
                "wait_for_completion": True,
            },
        )
        pager = await client.aio.memory_banks.memories.list(name=memory_bank.name)
        memory_list = [item async for item in pager]
        assert len(memory_list) == 1
        assert isinstance(memory_list[0], types.Memory)
    finally:
        await client.aio.memory_banks.delete(name=memory_bank.name, force=True)
