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

from tests.unit.agentplatform.genai.replays import pytest_helper


def test_ingest_events(client):
    agent_engine = client.runtimes.create()
    assert not list(
        client.runtimes.memories.list(
            name=agent_engine.api_resource.name,
        )
    )
    scope = {"user_id": "test-user-id"}
    # Generate memories using source content. This result is non-deterministic,
    # because an LLM is used to generate the memories.
    client.runtimes.memories.ingest_events(
        name=agent_engine.api_resource.name,
        scope=scope,
        direct_contents_source={
            "events": [
                {
                    "content": {
                        "role": "user",
                        "parts": [{"text": "I like dogs."}],
                    }
                }
            ]
        },
        # `overlap_event_count` re-includes trailing events from one generation
        # window in the next so context is preserved across GenerateMemories
        # calls.
        generation_trigger_config={
            "generation_rule": {"idle_duration": "60s", "overlap_event_count": 1}
        },
    )
    memories = list(
        client.runtimes.memories.retrieve(
            name=agent_engine.api_resource.name,
            scope=scope,
        )
    )
    # Ingest events should be asynchronous by default, so there should be no
    # memories immediately after the call. Processing will only start after 60s
    # of inactivity.
    assert len(memories) == 0

    client.runtimes.memories.ingest_events(
        name=agent_engine.api_resource.name,
        scope=scope,
        direct_contents_source={
            "events": [
                {
                    "content": {
                        "role": "user",
                        "parts": [{"text": "I'm a software engineer."}],
                    }
                }
            ]
        },
        # `revision_labels`, `metadata`, and `metadata_merge_strategy` are
        # applied to the memories generated from the ingested events. Because
        # `force_flush` makes generation synchronous, the user-provided metadata
        # is observable on the retrieved memory below.
        config={
            "wait_for_completion": True,
            "force_flush": True,
            "revision_labels": {"source": "ingest-events-test"},
            "metadata": {"topic": {"string_value": "jobs"}},
            "metadata_merge_strategy": "OVERWRITE",
        },
    )
    memories = list(
        client.runtimes.memories.retrieve(
            name=agent_engine.api_resource.name,
            scope=scope,
            simple_retrieval_params={
                "page_size": 1,
            },
        )
    )
    # With `wait_for_completion` and `force_flush` set to True, there should be
    # memories immediately after the call.
    assert len(memories) >= 1
    # The user-provided `metadata` should be applied to the generated memory.
    assert memories[0].memory.metadata["topic"].string_value == "jobs"

    # The user-provided `revision_labels` are applied to the generated memory's
    # revision (not the Memory itself), so list the memory's revisions to verify.
    revisions = list(
        client.runtimes.memories.revisions.list(
            name=memories[0].memory.name,
        )
    )
    assert revisions
    assert revisions[0].labels == {"source": "ingest-events-test"}

    client.runtimes.delete(name=agent_engine.api_resource.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="runtimes.memories.ingest_events",
)
