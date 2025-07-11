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

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types
from google.genai import pagers


def test_retrieve_memories_with_similarity_search_params(client):
    agent_engine = client.agent_engines.create()
    assert not list(
        client.agent_engines.retrieve_memories(
            name=agent_engine.api_resource.name,
            scope={"user_id": "123"},
            similarity_search_params=types.RetrieveMemoriesRequestSimilaritySearchParams(
                search_query="memory_fact_1",
            ),
        )
    )
    client.agent_engines.create_memory(
        name=agent_engine.api_resource.name,
        fact="memory_fact_1",
        scope={"user_id": "123"},
    )
    assert (
        len(
            list(
                client.agent_engines.retrieve_memories(
                    name=agent_engine.api_resource.name,
                    scope={"user_id": "123"},
                )
            )
        )
        == 1
    )
    assert not list(
        client.agent_engines.retrieve_memories(
            name=agent_engine.api_resource.name,
            scope={"user_id": "456"},
        )
    )
    client.agent_engines.create_memory(
        name=agent_engine.api_resource.name,
        fact="memory_fact_2",
        scope={"user_id": "123"},
    )
    assert (
        len(
            list(
                client.agent_engines.retrieve_memories(
                    name=agent_engine.api_resource.name,
                    scope={"user_id": "123"},
                )
            )
        )
        == 2
    )


def test_retrieve_memories_with_simple_retrieval_params(client):
    agent_engine = client.agent_engines.create()
    client.agent_engines.create_memory(
        name=agent_engine.api_resource.name,
        fact="memory_fact_1",
        scope={"user_id": "123"},
    )
    memories = client.agent_engines.retrieve_memories(
        name=agent_engine.api_resource.name,
        scope={"user_id": "123"},
        simple_retrieval_params=types.RetrieveMemoriesRequestSimpleRetrievalParams(
            page_size=1,
        ),
    )
    assert isinstance(memories, pagers.Pager)
    assert isinstance(memories.page[0], types.RetrieveMemoriesResponseRetrievedMemory)
    assert memories.page_size == 1


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.create_memory",
)
