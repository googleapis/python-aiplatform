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
from agentplatform._genai import types


def test_generate_and_retrieve_profile(client):
    # TODO: Switch to Memory Bank for creation once it supports configs.
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
    memory_bank = client.agent_engines.create(
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
        memory_bank = client.agent_engines.get(name=memory_bank.api_resource.name)
        memory_bank_config = memory_bank.api_resource.context_spec.memory_bank_config
        assert memory_bank_config.customization_configs == [
            memory_bank_customization_config
        ]
        assert memory_bank_config.structured_memory_configs == [
            structured_memory_config_obj
        ]

        scope = {"user_id": "123"}
        client.memory_banks.memories.generate(
            name=memory_bank.api_resource.name,
            scope=scope,
            direct_contents_source={
                "events": [{"content": {"parts": [{"text": "My name is Kim."}]}}]
            },
        )
        memories = list(
            client.memory_banks.memories.retrieve(
                name=memory_bank.api_resource.name,
                scope=scope,
                config={"memory_types": ["STRUCTURED_PROFILE"]},
            )
        )
        assert len(memories) >= 1
        assert memories[0].memory.structured_content is not None

        response = client.memory_banks.memories.retrieve_profiles(
            name=memory_bank.api_resource.name, scope=scope
        )
        assert len(response.profiles) == 1

    finally:
        # Clean up resources.
        client.memory_banks.delete(name=memory_bank.api_resource.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="memory_banks.memories.retrieve_profiles",
)
