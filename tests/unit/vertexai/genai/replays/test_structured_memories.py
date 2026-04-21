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


def test_generate_and_retrieve_profile(client):
    # TODO: Use prod once available.
    client._api_client._http_options.base_url = (
        "https://us-central1-autopush-aiplatform.sandbox.googleapis.com"
    )
    customization_config = {"disable_natural_language_memories": True}
    memory_bank_customization_config = types.MemoryBankCustomizationConfig(
        **customization_config
    )
    structured_memory_config = {
        "scope_keys": ["user_id"],
        "schema_configs": [
            {
                "id": "user-profile",
                "memory_schema": {
                    "properties": {
                        "name": {"description": "User's name", "type": "string"}
                    },
                    "type": "object",
                },
            }
        ],
    }
    structured_memory_config_obj = types.StructuredMemoryConfig(
        **structured_memory_config
    )
    agent_engine = client.agent_engines.create(
        config={
            "context_spec": {
                "memory_bank_config": {
                    "customization_configs": [memory_bank_customization_config],
                    "structured_memory_configs": [structured_memory_config_obj],
                },
            },
            "http_options": {"api_version": "v1beta1"},
        },
    )
    try:
        agent_engine = client.agent_engines.get(name=agent_engine.api_resource.name)
        memory_bank_config = agent_engine.api_resource.context_spec.memory_bank_config
        assert memory_bank_config.customization_configs == [
            memory_bank_customization_config
        ]
        assert memory_bank_config.structured_memory_configs == [
            structured_memory_config_obj
        ]

        scope = {"user_id": "123"}
        client.agent_engines.memories.generate(
            name=agent_engine.api_resource.name,
            scope=scope,
            direct_contents_source={
                "events": [{"content": {"parts": [{"text": "My name is Kim."}]}}]
            },
        )
        memories = list(
            client.agent_engines.memories.retrieve(
                name=agent_engine.api_resource.name,
                scope=scope,
                config={"memory_types": ["STRUCTURED_PROFILE"]},
            )
        )
        assert len(memories) >= 1
        assert memories[0].memory.structured_content is not None

        response = client.agent_engines.memories.retrieve_profiles(
            name=agent_engine.api_resource.name, scope=scope
        )
        assert len(response.profiles) == 1

    finally:
        # Clean up resources.
        client.agent_engines.delete(name=agent_engine.api_resource.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.retrieve_profiles",
)
