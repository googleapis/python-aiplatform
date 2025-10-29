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
from google.genai import types as genai_types


def test_generate_and_rollback_memories(client):
    # TODO(): Use prod endpoint once experiment is fully rolled out.
    client._api_client._http_options.base_url = (
        "https://us-central1-autopush-aiplatform.sandbox.googleapis.com/"
    )
    agent_engine = client.agent_engines.create()
    assert not list(
        client.agent_engines.memories.list(
            name=agent_engine.api_resource.name,
        )
    )
    # Generate memories using source content. This result is non-deterministic,
    # because an LLM is used to generate the memories.
    client.agent_engines.memories.generate(
        name=agent_engine.api_resource.name,
        scope={"user_id": "test-user-id"},
        direct_contents_source=types.GenerateMemoriesRequestDirectContentsSource(
            events=[
                types.GenerateMemoriesRequestDirectContentsSourceEvent(
                    content=genai_types.Content(
                        role="model",
                        parts=[
                            genai_types.Part(
                                text="I am a software engineer focusing in security"
                            )
                        ],
                    )
                )
            ]
        ),
        config=types.GenerateAgentEngineMemoriesConfig(
            revision_labels={"key": "value"}
        ),
    )
    memories = list(
        client.agent_engines.memories.list(
            name=agent_engine.api_resource.name,
        )
    )
    assert len(memories) >= 1

    # Every action that modifies a memory creates a new revision.
    memory_revisions = list(
        client.agent_engines.memories.revisions.list(
            name=memories[0].name,
        )
    )
    assert len(memory_revisions) >= 1
    # The revision's labels depend on the generation request's revision labels.
    assert memory_revisions[0].labels == {"key": "value"}
    revision_name = memory_revisions[0].name

    # Update the memory.
    client.agent_engines.memories._update(
        name=memories[0].name,
        fact="This is temporary",
        scope={"user_id": "test-user-id"},
    )
    memory = client.agent_engines.memories.get(name=memories[0].name)
    assert memory.fact == "This is temporary"

    # Rollback to the revision with the original fact that was created by the
    # generation request.
    client.agent_engines.memories.rollback(
        name=memories[0].name,
        target_revision_id=revision_name.split("/")[-1],
    )
    memory = client.agent_engines.memories.get(name=memories[0].name)
    assert memory.fact == memory_revisions[0].fact

    # Update the memory again using generation. We use the original source
    # content to ensure that the original memory is updated. The response should
    # refer to the previous revision.
    pre_extracted_fact = "I am a software engineer focusing in security"
    response = client.agent_engines.memories.generate(
        name=agent_engine.api_resource.name,
        scope={"user_id": "test-user-id"},
        direct_memories_source=types.GenerateMemoriesRequestDirectMemoriesSource(
            direct_memories=[
                types.GenerateMemoriesRequestDirectMemoriesSourceDirectMemory(
                    fact=pre_extracted_fact
                )
            ]
        ),
    )
    # The memory was updated, so the previous revision is set.
    assert response.response.generated_memories[0].previous_revision is not None
    memory_revisions = list(
        client.agent_engines.memories.revisions.list(name=memories[0].name)
    )
    # Memory Revisions are returned in descending order by revision create time.
    # We can't make an assertion on the actual value, since it's
    # generated and thus non-deterministic.
    assert memory_revisions[0].extracted_memories[0].fact is not None
    client.agent_engines.delete(name=agent_engine.api_resource.name, force=True)


def test_generate_memories_direct_memories_source(client):
    agent_engine = client.agent_engines.create()
    client.agent_engines.memories.generate(
        name=agent_engine.api_resource.name,
        scope={"user_id": "test-user-id"},
        direct_memories_source=types.GenerateMemoriesRequestDirectMemoriesSource(
            direct_memories=[
                types.GenerateMemoriesRequestDirectMemoriesSourceDirectMemory(
                    fact="I am a software engineer."
                ),
                types.GenerateMemoriesRequestDirectMemoriesSourceDirectMemory(
                    fact="I like to write replay tests."
                ),
            ]
        ),
        config=types.GenerateAgentEngineMemoriesConfig(wait_for_completion=True),
    )
    assert (
        len(
            list(
                client.agent_engines.memories.list(
                    name=agent_engine.api_resource.name,
                )
            )
        )
        >= 1
    )
    client.agent_engines.delete(name=agent_engine.api_resource.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.generate_memories",
)


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_generate_and_rollback_memories_async(client):
    # TODO(): Use prod endpoint once revisions experiment is fully rolled out.
    client._api_client._http_options.base_url = (
        "https://us-central1-autopush-aiplatform.sandbox.googleapis.com/"
    )
    agent_engine = client.agent_engines.create()
    await client.aio.agent_engines.memories.generate(
        name=agent_engine.api_resource.name,
        scope={"user_id": "test-user-id"},
        direct_memories_source=types.GenerateMemoriesRequestDirectMemoriesSource(
            direct_memories=[
                types.GenerateMemoriesRequestDirectMemoriesSourceDirectMemory(
                    fact="I am a software engineer."
                ),
                types.GenerateMemoriesRequestDirectMemoriesSourceDirectMemory(
                    fact="I like to write replay tests."
                ),
            ]
        ),
        config=types.GenerateAgentEngineMemoriesConfig(wait_for_completion=True),
    )
    memories_pager = await client.aio.agent_engines.memories.list(
        name=agent_engine.api_resource.name
    )
    memory_list = [item async for item in memories_pager]
    assert len(memory_list) >= 1

    revisions_pager = await client.aio.agent_engines.memories.revisions.list(
        name=memory_list[0].name
    )
    memory_revisions = [item async for item in revisions_pager]
    assert len(memory_revisions) >= 1
    revision_name = memory_revisions[0].name

    # Update the memory.
    client.agent_engines.memories._update(
        name=memory_list[0].name,
        fact="This is temporary",
        scope={"user_id": "test-user-id"},
    )
    memory = await client.aio.agent_engines.memories.get(name=memory_list[0].name)
    assert memory.fact == "This is temporary"

    # Rollback to the revision with the original fact that was created by the
    # generation request.
    await client.aio.agent_engines.memories.rollback(
        name=memory_list[0].name,
        target_revision_id=revision_name.split("/")[-1],
    )
    memory = await client.aio.agent_engines.memories.get(name=memory_list[0].name)
    assert memory.fact == memory_revisions[0].fact

    await client.aio.agent_engines.delete(
        name=agent_engine.api_resource.name, force=True
    )
