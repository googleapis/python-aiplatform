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
import pydantic


def test_generate_and_retrieve_profile(client):

    class ProfileSchema(pydantic.BaseModel):

        class DemographicDetails(pydantic.BaseModel):
            hometown: str

        name: str = pydantic.Field(description="User's name")
        demographics: DemographicDetails

    expected_schema = {
        "title": "ProfileSchema",
        "type": "object",
        "required": ["name", "demographics"],
        "properties": {
            "name": {
                "title": "Name",
                "description": "User's name",
                "type": "string",
            },
            "demographics": {
                "type": "object",
                "properties": {
                    "hometown": {
                        "type": "string",
                    },
                },
                "required": ["hometown"],
            },
        },
    }

    customization_config = {"disable_natural_language_memories": True}
    memory_bank_customization_config = types.MemoryBankCustomizationConfig(
        **customization_config
    )
    structured_memory_config = {
        "scope_keys": ["user_id"],
        "schema_configs": [
            {
                "id": "user-profile-1",
                "memory_json_schema": ProfileSchema.model_json_schema(),
            },
            {
                "id": "user-profile-2",
                "memory_schema": expected_schema,
            },
            {
                "id": "user-profile-3",
                "memory_json_schema": expected_schema,
            },
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
            types.StructuredMemoryConfig(
                scope_keys=["user_id"],
                schema_configs=[
                    types.StructuredMemorySchemaConfig(
                        id="user-profile-1",
                        memory_schema=expected_schema,
                    ),
                    types.StructuredMemorySchemaConfig(
                        id="user-profile-2",
                        memory_schema=expected_schema,
                    ),
                    types.StructuredMemorySchemaConfig(
                        id="user-profile-3",
                        memory_schema=expected_schema,
                    ),
                ],
            )
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
        # One profile is generated for each schema config.
        assert len(response.profiles) == 3

    finally:
        # Clean up resources.
        client.agent_engines.delete(name=agent_engine.api_resource.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.retrieve_profiles",
)
