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


def test_purge_memories(client):
    """Tests purging memories."""
    agent_engine = client.agent_engines.create()
    try:
        client.agent_engines.memories.create(
            name=agent_engine.api_resource.name,
            fact="memory_fact_1",
            scope={"user_id": "123"},
            config={"wait_for_completion": True},
        )
        client.agent_engines.memories.create(
            name=agent_engine.api_resource.name,
            fact="memory_fact_2",
            scope={"user_id": "123"},
            config={"wait_for_completion": True},
        )
        client.agent_engines.memories.create(
            name=agent_engine.api_resource.name,
            fact="memory_fact_3",
            scope={"user_id": "456"},
            config={"wait_for_completion": True},
        )
        operation = client.agent_engines.memories.purge(
            name=agent_engine.api_resource.name,
            filter="scope.user_id=123",
            config={"wait_for_completion": True},
        )
        assert operation.done
        assert operation.response.purge_count == 2
        # Memories were not actually purged, because `force` was False.
        assert (
            len(
                list(
                    client.agent_engines.memories.list(
                        name=agent_engine.api_resource.name
                    )
                )
            )
            == 3
        )
        # Now, actually purge the memories.
        operation = client.agent_engines.memories.purge(
            name=agent_engine.api_resource.name,
            filter="scope.user_id=123",
            force=True,
            config={"wait_for_completion": True},
        )
        assert operation.done
        assert operation.response.purge_count == 2
        assert (
            len(
                list(
                    client.agent_engines.memories.list(
                        name=agent_engine.api_resource.name
                    )
                )
            )
            == 1
        )
    finally:
        client.agent_engines.delete(name=agent_engine.api_resource.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.memories.purge",
)


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_purge_memories_async(client):
    agent_engine = client.agent_engines.create()
    try:
        client.agent_engines.memories.create(
            name=agent_engine.api_resource.name,
            fact="memory_fact_1",
            scope={"user_id": "123"},
            config={"wait_for_completion": True},
        )
        client.agent_engines.memories.create(
            name=agent_engine.api_resource.name,
            fact="memory_fact_2",
            scope={"user_id": "123"},
            config={"wait_for_completion": True},
        )
        client.agent_engines.memories.create(
            name=agent_engine.api_resource.name,
            fact="memory_fact_3",
            scope={"user_id": "456"},
            config={"wait_for_completion": True},
        )

        operation = await client.aio.agent_engines.memories.purge(
            name=agent_engine.api_resource.name,
            filter="scope.user_id=123",
            config={"wait_for_completion": True},
        )
        assert operation.done
        assert operation.response.purge_count == 2
        # Memories were not actually purged, because `force` was False.
        assert (
            len(
                list(
                    client.agent_engines.memories.list(
                        name=agent_engine.api_resource.name
                    )
                )
            )
            == 3
        )
        # Now, actually purge the memories.
        operation = await client.aio.agent_engines.memories.purge(
            name=agent_engine.api_resource.name,
            filter="scope.user_id=123",
            force=True,
            config={"wait_for_completion": True},
        )
        assert operation.done
        assert operation.response.purge_count == 2
        assert (
            len(
                list(
                    client.agent_engines.memories.list(
                        name=agent_engine.api_resource.name
                    )
                )
            )
            == 1
        )
    finally:
        client.agent_engines.delete(name=agent_engine.api_resource.name, force=True)
