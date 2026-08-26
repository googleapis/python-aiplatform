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
# pylint: disable=protected-access,bad-continuation,missing-function-docstring,g-bad-import-order

import pytest

from agentplatform._genai import types
from tests.unit.agentplatform.genai.replays import pytest_helper

LOCATION = "test-location"
PROJECT = "test-project"
LOCATION_NAME = f"projects/{PROJECT}/locations/{LOCATION}"
OPERATION_NAME = "projects/test-project/locations/test-location/operations/op-123"
MEMORY_BANK_NAME = "projects/test-project/locations/test-location/reasoningEngines/123"
DISPLAY_NAME = "My Test Memory Bank"
DESCRIPTION = "My Test Memory Bank Description"
PENDING_OP = {
    "name": OPERATION_NAME,
    "done": False,
}
FINISHED_OP = {
    "name": OPERATION_NAME,
    "done": True,
    "response": {"name": MEMORY_BANK_NAME},
}

GENERATION_CONFIG = {
    "model": (
        "projects/test-project/locations/test-location/publishers/google/models/gemini-3.5-flash"
    ),
}
SIMILARITY_SEARCH_CONFIG = {
    "embedding_model": (
        "projects/test-project/locations/test-location/"
        "publishers/google/models/gemini-embedding-2"
    )
}
UNSTRUCTURED_MEMORY_CONFIGS = [
    {
        "memory_topics": [
            {"managed_memory_topic": {"managed_topic_enum": "USER_PERSONAL_INFO"}}
        ],
        "consolidation_config": {"revisions_per_candidate_count": 1},
    }
]
TTL_CONFIG = {"memory_revision_default_ttl": f"{365 * 24 * 60 * 60}s"}
MEMORY_SCHEMA = {
    "properties": {
        "name": {
            "description": "User's name",
            "type": "string",
        }
    },
    "type": "object",
}
# The SDK uses the alias `memory_schema` while the API uses `schema`. The SDK
# inner workings will convert between the two.
STRUCTURED_MEMORY_SCHEMA_CONFIGS = [
    {
        "scopeKeys": ["user_id"],
        "schemaConfigs": [
            {
                "id": "user-profile",
                "memory_schema": MEMORY_SCHEMA,
            }
        ],
    }
]


def test_create_memory_bank(client):
    memory_bank = client.memory_banks.create(
        managed_semantic_memory_config={
            "generation_config": GENERATION_CONFIG,
            "similarity_search_config": SIMILARITY_SEARCH_CONFIG,
            "unstructured_memory_configs": UNSTRUCTURED_MEMORY_CONFIGS,
            "structured_memory_configs": STRUCTURED_MEMORY_SCHEMA_CONFIGS,
            "ttl_config": TTL_CONFIG,
            "disable_memory_revisions": True,
        },
        config={
            "display_name": DISPLAY_NAME,
            "description": DESCRIPTION,
        },
    )
    try:
        memory_bank = client.memory_banks.get(name=memory_bank.name)
        assert memory_bank.name == memory_bank.name
        assert memory_bank.display_name == DISPLAY_NAME
        assert memory_bank.description == DESCRIPTION
        assert (
            memory_bank.managed_semantic_memory_config
            == types.ManagedSemanticMemoryConfig(
                generation_config=GENERATION_CONFIG,
                similarity_search_config=SIMILARITY_SEARCH_CONFIG,
                unstructured_memory_configs=UNSTRUCTURED_MEMORY_CONFIGS,
                structured_memory_configs=STRUCTURED_MEMORY_SCHEMA_CONFIGS,
                ttl_config=TTL_CONFIG,
                disable_memory_revisions=True,
            )
        )

    finally:
        # Clean up resources.
        client.memory_banks.delete(name=memory_bank.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="memory_banks.create",
)

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_create_memory_bank_async(client):
    memory_bank = await client.aio.memory_banks.create(
        managed_semantic_memory_config={
            "generation_config": GENERATION_CONFIG,
            "similarity_search_config": SIMILARITY_SEARCH_CONFIG,
            "unstructured_memory_configs": UNSTRUCTURED_MEMORY_CONFIGS,
            "structured_memory_configs": STRUCTURED_MEMORY_SCHEMA_CONFIGS,
            "ttl_config": TTL_CONFIG,
            "disable_memory_revisions": True,
        },
        config={
            "display_name": DISPLAY_NAME,
            "description": DESCRIPTION,
        },
    )
    try:
        memory_bank = await client.aio.memory_banks.get(name=memory_bank.name)
        assert memory_bank.name == memory_bank.name
        assert memory_bank.display_name == DISPLAY_NAME
        assert memory_bank.description == DESCRIPTION
        assert (
            memory_bank.managed_semantic_memory_config
            == types.ManagedSemanticMemoryConfig(
                generation_config=GENERATION_CONFIG,
                similarity_search_config=SIMILARITY_SEARCH_CONFIG,
                unstructured_memory_configs=UNSTRUCTURED_MEMORY_CONFIGS,
                structured_memory_configs=STRUCTURED_MEMORY_SCHEMA_CONFIGS,
                ttl_config=TTL_CONFIG,
                disable_memory_revisions=True,
            )
        )

    finally:
        # Clean up resources.
        client.memory_banks.delete(name=memory_bank.name, force=True)
