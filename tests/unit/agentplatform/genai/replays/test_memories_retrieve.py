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


from tests.unit.agentplatform.genai.replays import pytest_helper
from agentplatform._genai import types
from google.genai import pagers


def test_retrieve_memories_with_similarity_search_params(client):
    memory_bank = client.memory_banks.create()
    try:
        assert not list(
            client.memory_banks.memories.retrieve(
                name=memory_bank.name,
                scope={"user_id": "123"},
                similarity_search_params=types.RetrieveMemoriesRequestSimilaritySearchParams(
                    search_query="memory_fact_1",
                ),
            )
        )
        client.memory_banks.memories.create(
            name=memory_bank.name,
            fact="memory_fact_1",
            scope={"user_id": "123"},
        )
        assert (
            len(
                list(
                    client.memory_banks.memories.retrieve(
                        name=memory_bank.name,
                        scope={"user_id": "123"},
                    )
                )
            )
            == 1
        )
        assert not list(
            client.memory_banks.memories.retrieve(
                name=memory_bank.name,
                scope={"user_id": "456"},
            )
        )
        client.memory_banks.memories.create(
            name=memory_bank.name,
            fact="memory_fact_2",
            scope={"user_id": "123"},
        )
        assert (
            len(
                list(
                    client.memory_banks.memories.retrieve(
                        name=memory_bank.name,
                        scope={"user_id": "123"},
                    )
                )
            )
            == 2
        )
    finally:
        client.memory_banks.delete(name=memory_bank.name, force=True)


def test_retrieve_memories_with_simple_retrieval_params(client):
    memory_bank = client.memory_banks.create()
    try:
        client.memory_banks.memories.create(
            name=memory_bank.name,
            fact="memory_fact_1",
            scope={"user_id": "123"},
        )
        memories = client.memory_banks.memories.retrieve(
            name=memory_bank.name,
            scope={"user_id": "123"},
            simple_retrieval_params=types.RetrieveMemoriesRequestSimpleRetrievalParams(
                page_size=1,
            ),
        )
        assert isinstance(memories, pagers.Pager)
        assert isinstance(
            memories.page[0], types.RetrieveMemoriesResponseRetrievedMemory
        )
        assert memories.page_size == 1

        client.memory_banks.memories.create(
            name=memory_bank.name,
            fact="memory_fact_2",
            scope={"user_id": "123"},
        )
        memories = client.memory_banks.memories.retrieve(
            name=memory_bank.name, scope={"user_id": "123"}
        )
        assert memories.page_size == 2

        memories = client.memory_banks.memories.retrieve(
            name=memory_bank.name,
            scope={"user_id": "123"},
            config={"filter": 'fact="memory_fact_2"'},
        )
        assert memories.page_size == 1
        assert memories.page[0].memory.fact == "memory_fact_2"

    finally:
        # Clean up resources.
        client.memory_banks.delete(name=memory_bank.name, force=True)


def test_retrieve_memories_with_metadata(client):
    memory_bank = client.memory_banks.create()
    try:
        metadata = {
            "my_string_key": types.MemoryMetadataValue(string_value="my_string_value"),
            "my_double_key": types.MemoryMetadataValue(double_value=123.456),
            "my_boolean_key": types.MemoryMetadataValue(bool_value=True),
            "my_timestamp_key": types.MemoryMetadataValue(
                timestamp_value=datetime.datetime(
                    2027, 1, 1, 12, 30, 00, tzinfo=datetime.timezone.utc
                )
            ),
        }
        scope = {"user_id": "123"}
        client.memory_banks.memories.create(
            name=memory_bank.name,
            fact="memory_fact_1",
            scope=scope,
        )
        operation = client.memory_banks.memories.create(
            name=memory_bank.name,
            fact="memory_fact_2",
            scope=scope,
            config={"metadata": metadata},
        )
        memory_name2 = operation.response.name

        results = client.memory_banks.memories.retrieve(
            name=memory_bank.name,
            scope=scope,
            config={
                "filter_groups": [
                    {
                        "filters": [
                            {
                                "key": "my_string_key",
                                "value": {"string_value": "my_string_value"},
                            }
                        ]
                    }
                ],
            },
        )
        assert len(results) == 1
        assert results[0].memory.name == memory_name2

    finally:
        # Clean up resources.
        client.memory_banks.delete(name=memory_bank.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="memory_banks.memories.retrieve",
)


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_retrieve_memories_async(client):
    memory_bank = client.memory_banks.create()
    try:
        operation = await client.aio.memory_banks.memories.create(
            name=memory_bank.name,
            fact="memory_fact",
            scope={"user_id": "123"},
        )
        assert isinstance(operation, types.MemoryOperation)
        pager = await client.aio.memory_banks.memories.retrieve(
            name=memory_bank.name,
            scope={"user_id": "123"},
        )
        memories = [item async for item in pager]
        assert len(memories) == 1
        assert isinstance(memories[0], types.RetrieveMemoriesResponseRetrievedMemory)
    finally:
        await client.aio.memory_banks.delete(name=memory_bank.name, force=True)
