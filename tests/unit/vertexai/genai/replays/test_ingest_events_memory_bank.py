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


def test_ingest_events(client):
    agent_engine = client.agent_engines.create()
    assert not list(
        client.agent_engines.memories.list(
            name=agent_engine.api_resource.name,
        )
    )
    scope = {"user_id": "test-user-id"}
    # Generate memories using source content. This result is non-deterministic,
    # because an LLM is used to generate the memories.
    client.agent_engines.memories.ingest_events(
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
        generation_trigger_config={"generation_rule": {"idle_duration": "60s"}},
    )
    memories = list(
        client.agent_engines.memories.retrieve(
            name=agent_engine.api_resource.name,
            scope=scope,
        )
    )
    # Ingest events should be asynchronous by default, so there should be no
    # memories immediately after the call. Processing will only start after 60s
    # of inactivity.
    assert len(memories) == 0

    client.agent_engines.memories.ingest_events(
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
        config={"wait_for_completion": True, "force_flush": True},
    )
    memories = list(
        client.agent_engines.memories.retrieve(
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

    client.agent_engines.delete(name=agent_engine.api_resource.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.memories.ingest_events",
)
