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


def test_purge_memories(client):
    """Tests purging memories."""
    memory_bank = client.memory_banks.create()
    try:
        client.memory_banks.memories.create(
            name=memory_bank.name,
            fact="memory_fact_1",
            scope={"user_id": "123"},
            config={"wait_for_completion": True},
        )
        client.memory_banks.memories.create(
            name=memory_bank.name,
            fact="memory_fact_2",
            scope={"user_id": "123"},
            config={"wait_for_completion": True},
        )
        client.memory_banks.memories.create(
            name=memory_bank.name,
            fact="memory_fact_3",
            scope={"user_id": "456"},
            config={"wait_for_completion": True},
        )
        client.memory_banks.memories.create(
            name=memory_bank.name,
            fact="memory_fact_4",
            scope={"user_id": "456"},
            config={
                "wait_for_completion": True,
                "metadata": {"my_key": {"string_value": "my_value"}},
            },
        )
        operation = client.memory_banks.memories.purge(
            name=memory_bank.name,
            filter="scope.user_id=123",
            config={"wait_for_completion": True},
        )
        assert operation.done
        assert operation.response.purge_count == 2
        # Memories were not actually purged, because `force` was False.
        assert len(list(client.memory_banks.memories.list(name=memory_bank.name))) == 4
        # Now, actually purge the memories.
        operation = client.memory_banks.memories.purge(
            name=memory_bank.name,
            filter="scope.user_id=123",
            force=True,
            config={"wait_for_completion": True},
        )
        assert operation.done
        assert operation.response.purge_count == 2
        assert len(list(client.memory_banks.memories.list(name=memory_bank.name))) == 2
        # Purge memories using filter groups.
        operation = client.memory_banks.memories.purge(
            name=memory_bank.name,
            force=True,
            filter_groups=[
                {"filters": [{"key": "my_key", "value": {"string_value": "my_value"}}]}
            ],
            config={
                "wait_for_completion": True,
            },
        )
        assert operation.done
        assert operation.response.purge_count == 1
        assert len(list(client.memory_banks.memories.list(name=memory_bank.name))) == 1
    finally:
        client.memory_banks.delete(name=memory_bank.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="memory_banks.memories.purge",
)


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_purge_memories_async(client):
    memory_bank = client.memory_banks.create()
    try:
        client.memory_banks.memories.create(
            name=memory_bank.name,
            fact="memory_fact_1",
            scope={"user_id": "123"},
            config={"wait_for_completion": True},
        )
        client.memory_banks.memories.create(
            name=memory_bank.name,
            fact="memory_fact_2",
            scope={"user_id": "123"},
            config={"wait_for_completion": True},
        )
        client.memory_banks.memories.create(
            name=memory_bank.name,
            fact="memory_fact_3",
            scope={"user_id": "456"},
            config={"wait_for_completion": True},
        )

        operation = await client.aio.memory_banks.memories.purge(
            name=memory_bank.name,
            filter="scope.user_id=123",
            config={"wait_for_completion": True},
        )
        assert operation.done
        assert operation.response.purge_count == 2
        # Memories were not actually purged, because `force` was False.
        assert len(list(client.memory_banks.memories.list(name=memory_bank.name))) == 3
        # Now, actually purge the memories.
        operation = await client.aio.memory_banks.memories.purge(
            name=memory_bank.name,
            filter="scope.user_id=123",
            force=True,
            config={"wait_for_completion": True},
        )
        assert operation.done
        assert operation.response.purge_count == 2
        assert len(list(client.memory_banks.memories.list(name=memory_bank.name))) == 1
    finally:
        client.memory_banks.delete(name=memory_bank.name, force=True)
