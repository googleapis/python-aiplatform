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
# pylint: disable=protected-access,bad-continuation,missing-function-docstring, g-bad-import-order

import time

from agentplatform._genai import types
from tests.unit.agentplatform.genai.replays import pytest_helper

DISPLAY_NAME = "My Test Memory Bank"
DESCRIPTION = "My Test Memory Bank Description"
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


def test_private_create_memory_bank(client):
    memory_bank_config = {
        "generation_config": GENERATION_CONFIG,
        "similarity_search_config": SIMILARITY_SEARCH_CONFIG,
        "customization_configs": UNSTRUCTURED_MEMORY_CONFIGS,
        "structured_memory_configs": STRUCTURED_MEMORY_SCHEMA_CONFIGS,
        "ttl_config": TTL_CONFIG,
        "disable_memory_revisions": True,
    }
    memory_operation = client.memory_banks._create(
        memory_bank_config=memory_bank_config,
        config={
            "display_name": DISPLAY_NAME,
            "description": DESCRIPTION,
        },
    )
    assert isinstance(memory_operation, types.MemoryBankOperation)
    # Give time for the operation to complete.
    time.sleep(10)
    # Extract the ReasoningEngine name from the operation name.
    name = "/".join(memory_operation.name.split("/")[0:-2])
    client.memory_banks.delete(name=name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="memory_banks._create",
)
