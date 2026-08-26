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

from agentplatform._genai import types
from tests.unit.agentplatform.genai.replays import pytest_helper


def test_generate_and_retrieve_profile(client):
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
    memory_bank = client.memory_banks.create(
        managed_semantic_memory_config={
            "unstructured_memory_configs": [memory_bank_customization_config],
            "structured_memory_configs": [structured_memory_config_obj],
        }
    )
    try:
        memory_bank = client.memory_banks.get(name=memory_bank.name)
        memory_config = memory_bank.managed_semantic_memory_config
        assert memory_config.unstructured_memory_configs == [
            memory_bank_customization_config
        ]
        assert memory_config.structured_memory_configs == [structured_memory_config_obj]

        scope = {"user_id": "123"}
        client.memory_banks.memories.generate(
            name=memory_bank.name,
            scope=scope,
            direct_contents_source={
                "events": [{"content": {"parts": [{"text": "My name is Kim."}]}}]
            },
        )
        memories = list(
            client.memory_banks.memories.retrieve(
                name=memory_bank.name,
                scope=scope,
                config={"memory_types": ["STRUCTURED_PROFILE"]},
            )
        )
        assert len(memories) >= 1
        assert memories[0].memory.structured_content is not None

        response = client.memory_banks.memories.retrieve_profiles(
            name=memory_bank.name, scope=scope
        )
        assert len(response.profiles) == 1

    finally:
        # Clean up resources.
        client.memory_banks.delete(name=memory_bank.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="memory_banks.memories.retrieve_profiles",
)
