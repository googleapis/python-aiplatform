# Copyright 2026 Google LLC
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

# pylint: disable=protected-access

import json
from unittest import mock
import google.auth.credentials
from agentplatform import _genai as genai
from agentplatform._genai import client as agentplatform_client
from agentplatform._genai import types as agentplatform_types
from google.genai import types as genai_types
import pytest


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
    "model": "gemini-3.5-flash",
}
SIMILARITY_SEARCH_CONFIG = {
    "embedding_model": (
        "projects/test-project/locations/test-location/"
        "publishers/google/models/text-embedding-005"
    )
}
ManagedTopicEnum = agentplatform_types.ManagedTopicEnum
UNSTRUCTURED_MEMORY_CONFIGS = [
    {
        "memory_topics": [
            {
                "managed_memory_topic": {
                    "managed_topic_enum": ManagedTopicEnum.USER_PERSONAL_INFO
                }
            },
            {
                "managed_memory_topic": {
                    "managed_topic_enum": ManagedTopicEnum.USER_PREFERENCES
                }
            },
            {
                "managed_memory_topic": {
                    "managed_topic_enum": ManagedTopicEnum.KEY_CONVERSATION_DETAILS
                }
            },
            {
                "managed_memory_topic": {
                    "managed_topic_enum": ManagedTopicEnum.EXPLICIT_INSTRUCTIONS
                }
            },
        ],
        "consolidation_config": {"revisions_per_candidate_count": 1},
        "generate_memories_examples": [],
        "enable_third_person_memories": False,
    }
]
TTL_CONFIG = {"memory_revision_default_ttl": f"{365 * 24 * 60 * 60}s"}
MEMORY_SCHEMA = {
    "properties": {
        "name": {
            "description": "User's name",
            "type": genai_types.Type.STRING,
        }
    },
    "type": genai_types.Type.OBJECT,
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
API_STRUCTURED_MEMORY_SCHEMA_CONFIGS = [
    {
        "scopeKeys": ["user_id"],
        "schemaConfigs": [
            {
                "id": "user-profile",
                "schema": MEMORY_SCHEMA,
            }
        ],
    }
]


@pytest.fixture
def memory_banks_client():
    creds = mock.create_autospec(google.auth.credentials.Credentials, instance=True)
    creds.token = "test_token"
    client = agentplatform_client.Client(
        project=PROJECT, location=LOCATION, credentials=creds
    )
    return client.memory_banks


@pytest.fixture
def async_memory_banks_client():
    creds = mock.create_autospec(google.auth.credentials.Credentials, instance=True)
    creds.token = "test_token"
    client = agentplatform_client.Client(
        project=PROJECT, location=LOCATION, credentials=creds
    )
    return client.aio.memory_banks


class TestMemoryBanks:
    """Tests for the Memory Banks module."""

    def test_create_memory_bank_no_config(self, memory_banks_client):
        """Tests the creation of a Memory Bank with no config."""
        reasoning_engine = {
            "displayName": DISPLAY_NAME,
            "description": DESCRIPTION,
            "context_spec": {"memory_bank_config": {}},
        }
        with mock.patch.object(
            memory_banks_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.side_effect = [
                genai_types.HttpResponse(body=json.dumps(PENDING_OP)),
                genai_types.HttpResponse(body=json.dumps(FINISHED_OP)),
                genai_types.HttpResponse(body=json.dumps({"name": MEMORY_BANK_NAME})),
            ]

            memory_bank = memory_banks_client.create(
                config={
                    "display_name": DISPLAY_NAME,
                    "description": DESCRIPTION,
                }
            )

            request_mock.assert_has_calls(
                [
                    mock.call(
                        "post",
                        "reasoningEngines",
                        reasoning_engine,
                        None,
                    ),
                    mock.call(
                        "get",
                        OPERATION_NAME,
                        {"_url": {"operationName": OPERATION_NAME}},
                        None,
                    ),
                ]
            )
            assert isinstance(memory_bank, genai.types.MemoryBank)
            assert memory_bank.name == MEMORY_BANK_NAME

    @pytest.mark.asyncio
    async def test_async_create_memory_bank_no_config(self, async_memory_banks_client):
        """Tests the creation of a Memory Bank with no config."""

        reasoning_engine = {
            "displayName": DISPLAY_NAME,
            "description": DESCRIPTION,
            "context_spec": {"memory_bank_config": {}},
        }
        with mock.patch.object(
            async_memory_banks_client._api_client, "async_request", autospec=True
        ) as request_mock:
            request_mock.side_effect = [
                genai_types.HttpResponse(body=json.dumps(PENDING_OP)),
                genai_types.HttpResponse(body=json.dumps(FINISHED_OP)),
                genai_types.HttpResponse(body=json.dumps({"name": MEMORY_BANK_NAME})),
            ]

            memory_bank = await async_memory_banks_client.create(
                config={
                    "display_name": DISPLAY_NAME,
                    "description": DESCRIPTION,
                }
            )

            request_mock.assert_has_calls(
                [
                    mock.call(
                        "post",
                        "reasoningEngines",
                        reasoning_engine,
                        None,
                    ),
                    mock.call(
                        "get",
                        OPERATION_NAME,
                        {"_url": {"operationName": OPERATION_NAME}},
                        None,
                    ),
                ]
            )
            assert isinstance(memory_bank, genai.types.MemoryBank)
            assert memory_bank.name == MEMORY_BANK_NAME

    def test_create_memory_bank_with_config(self, memory_banks_client):
        """Tests the creation of a Memory Bank with config."""
        memory_bank_response = {
            "name": MEMORY_BANK_NAME,
            "displayName": DISPLAY_NAME,
            "description": DESCRIPTION,
        }
        reasoning_engine = {
            "displayName": DISPLAY_NAME,
            "description": DESCRIPTION,
            "context_spec": {
                "memory_bank_config": {
                    "generationConfig": GENERATION_CONFIG,
                    "similaritySearchConfig": SIMILARITY_SEARCH_CONFIG,
                    "customizationConfigs": UNSTRUCTURED_MEMORY_CONFIGS,
                    "structuredMemoryConfigs": API_STRUCTURED_MEMORY_SCHEMA_CONFIGS,
                    "ttlConfig": TTL_CONFIG,
                    "disableMemoryRevisions": False,
                }
            },
        }
        with mock.patch.object(
            memory_banks_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.side_effect = [
                genai_types.HttpResponse(body=json.dumps(PENDING_OP)),
                genai_types.HttpResponse(body=json.dumps(FINISHED_OP)),
                genai_types.HttpResponse(body=json.dumps(memory_bank_response)),
            ]

            memory_bank = memory_banks_client.create(
                managed_semantic_memory_config={
                    "generation_config": GENERATION_CONFIG,
                    "similarity_search_config": SIMILARITY_SEARCH_CONFIG,
                    "unstructured_memory_configs": UNSTRUCTURED_MEMORY_CONFIGS,
                    "structured_memory_configs": STRUCTURED_MEMORY_SCHEMA_CONFIGS,
                    "ttl_config": TTL_CONFIG,
                    "disable_memory_revisions": False,
                },
                config={
                    "display_name": DISPLAY_NAME,
                    "description": DESCRIPTION,
                },
            )

            request_mock.assert_has_calls(
                [
                    mock.call(
                        "post",
                        "reasoningEngines",
                        reasoning_engine,
                        None,
                    ),
                    mock.call(
                        "get",
                        OPERATION_NAME,
                        {"_url": {"operationName": OPERATION_NAME}},
                        None,
                    ),
                ]
            )
            assert isinstance(memory_bank, genai.types.MemoryBank)
            assert memory_bank.name == MEMORY_BANK_NAME

    @pytest.mark.asyncio
    async def test_async_create_memory_bank_with_config(
        self, async_memory_banks_client
    ):
        """Tests the creation of a Memory Bank with config."""

        memory_bank_response = {
            "name": MEMORY_BANK_NAME,
            "displayName": DISPLAY_NAME,
            "description": DESCRIPTION,
        }
        reasoning_engine = {
            "displayName": DISPLAY_NAME,
            "description": DESCRIPTION,
            "context_spec": {
                "memory_bank_config": {
                    "generationConfig": GENERATION_CONFIG,
                    "similaritySearchConfig": SIMILARITY_SEARCH_CONFIG,
                    "customizationConfigs": UNSTRUCTURED_MEMORY_CONFIGS,
                    "structuredMemoryConfigs": API_STRUCTURED_MEMORY_SCHEMA_CONFIGS,
                    "ttlConfig": TTL_CONFIG,
                    "disableMemoryRevisions": False,
                }
            },
        }
        with mock.patch.object(
            async_memory_banks_client._api_client, "async_request", autospec=True
        ) as request_mock:
            request_mock.side_effect = [
                genai_types.HttpResponse(body=json.dumps(PENDING_OP)),
                genai_types.HttpResponse(body=json.dumps(FINISHED_OP)),
                genai_types.HttpResponse(body=json.dumps(memory_bank_response)),
            ]

            memory_bank = await async_memory_banks_client.create(
                managed_semantic_memory_config={
                    "generation_config": GENERATION_CONFIG,
                    "similarity_search_config": SIMILARITY_SEARCH_CONFIG,
                    "unstructured_memory_configs": UNSTRUCTURED_MEMORY_CONFIGS,
                    "structured_memory_configs": STRUCTURED_MEMORY_SCHEMA_CONFIGS,
                    "ttl_config": TTL_CONFIG,
                    "disable_memory_revisions": False,
                },
                config={
                    "display_name": DISPLAY_NAME,
                    "description": DESCRIPTION,
                },
            )

            request_mock.assert_has_calls(
                [
                    mock.call(
                        "post",
                        "reasoningEngines",
                        reasoning_engine,
                        None,
                    ),
                    mock.call(
                        "get",
                        OPERATION_NAME,
                        {"_url": {"operationName": OPERATION_NAME}},
                        None,
                    ),
                ]
            )
            assert isinstance(memory_bank, genai.types.MemoryBank)
            assert memory_bank.name == MEMORY_BANK_NAME

    def test_get_memory_bank(self, memory_banks_client):
        """Tests the retrieval of a Memory Bank."""
        reasoning_engine = {
            "name": MEMORY_BANK_NAME,
            "displayName": DISPLAY_NAME,
            "description": DESCRIPTION,
            "contextSpec": {
                "memoryBankConfig": {
                    "generationConfig": GENERATION_CONFIG,
                    "similaritySearchConfig": SIMILARITY_SEARCH_CONFIG,
                    "customizationConfigs": UNSTRUCTURED_MEMORY_CONFIGS,
                    "structuredMemoryConfigs": API_STRUCTURED_MEMORY_SCHEMA_CONFIGS,
                    "ttlConfig": TTL_CONFIG,
                    "disableMemoryRevisions": False,
                }
            },
        }
        with mock.patch.object(
            memory_banks_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.side_effect = [
                genai_types.HttpResponse(body=json.dumps(reasoning_engine)),
            ]
            memory_bank = memory_banks_client.get(name=MEMORY_BANK_NAME)
            request_mock.assert_called_once_with(
                "get",
                MEMORY_BANK_NAME,
                {"_url": {"name": MEMORY_BANK_NAME}},
                None,
            )
            assert isinstance(memory_bank, genai.types.MemoryBank)
            assert memory_bank.name == MEMORY_BANK_NAME
            assert memory_bank.display_name == DISPLAY_NAME
            assert memory_bank.description == DESCRIPTION
            assert (
                memory_bank.managed_semantic_memory_config
                == agentplatform_types.ManagedSemanticMemoryConfig(
                    generation_config=GENERATION_CONFIG,
                    similarity_search_config=SIMILARITY_SEARCH_CONFIG,
                    unstructured_memory_configs=UNSTRUCTURED_MEMORY_CONFIGS,
                    structured_memory_configs=STRUCTURED_MEMORY_SCHEMA_CONFIGS,
                    ttl_config=TTL_CONFIG,
                    disable_memory_revisions=False,
                )
            )

    @pytest.mark.asyncio
    async def test_async_get_memory_bank(self, async_memory_banks_client):
        """Tests the retrieval of a Memory Bank."""
        reasoning_engine = {
            "name": MEMORY_BANK_NAME,
            "displayName": DISPLAY_NAME,
            "description": DESCRIPTION,
            "contextSpec": {
                "memoryBankConfig": {
                    "generationConfig": GENERATION_CONFIG,
                    "similaritySearchConfig": SIMILARITY_SEARCH_CONFIG,
                    "customizationConfigs": UNSTRUCTURED_MEMORY_CONFIGS,
                    "structuredMemoryConfigs": API_STRUCTURED_MEMORY_SCHEMA_CONFIGS,
                    "ttlConfig": TTL_CONFIG,
                    "disableMemoryRevisions": False,
                }
            },
        }
        with mock.patch.object(
            async_memory_banks_client._api_client, "async_request", autospec=True
        ) as request_mock:
            request_mock.side_effect = [
                genai_types.HttpResponse(body=json.dumps(reasoning_engine)),
            ]
            memory_bank = await async_memory_banks_client.get(name=MEMORY_BANK_NAME)
            request_mock.assert_called_once_with(
                "get",
                MEMORY_BANK_NAME,
                {"_url": {"name": MEMORY_BANK_NAME}},
                None,
            )
            assert isinstance(memory_bank, genai.types.MemoryBank)
            assert memory_bank.name == MEMORY_BANK_NAME
            assert memory_bank.display_name == DISPLAY_NAME
            assert memory_bank.description == DESCRIPTION
            assert (
                memory_bank.managed_semantic_memory_config
                == agentplatform_types.ManagedSemanticMemoryConfig(
                    generation_config=GENERATION_CONFIG,
                    similarity_search_config=SIMILARITY_SEARCH_CONFIG,
                    unstructured_memory_configs=UNSTRUCTURED_MEMORY_CONFIGS,
                    structured_memory_configs=STRUCTURED_MEMORY_SCHEMA_CONFIGS,
                    ttl_config=TTL_CONFIG,
                    disable_memory_revisions=False,
                )
            )

    def test_list_memory_banks(self, memory_banks_client):
        """Tests the listing of Memory Banks."""
        reasoning_engine_1 = {
            "name": MEMORY_BANK_NAME,
            "displayName": DISPLAY_NAME,
            "description": DESCRIPTION,
        }
        reasoning_engine_2 = {
            "name": "projects/test-project/locations/test-location/reasoningEngines/456",  # pylint: disable=line-too-long
            "displayName": "My Second Test Memory Bank",
            "description": "My Second Test Memory Bank Description",
        }
        response = {"reasoningEngines": [reasoning_engine_1, reasoning_engine_2]}
        with mock.patch.object(
            memory_banks_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.side_effect = [
                genai_types.HttpResponse(body=json.dumps(response)),
            ]
            memory_banks = list(memory_banks_client.list())
            request_mock.assert_called_once_with(
                "get",
                "reasoningEngines",
                {},
                None,
            )
            assert len(memory_banks) == 2
            assert isinstance(memory_banks[0], genai.types.MemoryBank)
            assert memory_banks[0].name == MEMORY_BANK_NAME
            assert memory_banks[0].display_name == DISPLAY_NAME
            assert memory_banks[0].description == DESCRIPTION
            assert isinstance(memory_banks[1], genai.types.MemoryBank)
            assert (
                memory_banks[1].name
                == "projects/test-project/locations/test-location/reasoningEngines/456"
            )
            assert memory_banks[1].display_name == "My Second Test Memory Bank"
            assert (
                memory_banks[1].description == "My Second Test Memory Bank Description"
            )

    @pytest.mark.asyncio
    async def test_async_list_memory_banks(self, async_memory_banks_client):
        """Tests the listing of Memory Banks."""
        reasoning_engine_1 = {
            "name": MEMORY_BANK_NAME,
            "displayName": DISPLAY_NAME,
            "description": DESCRIPTION,
        }
        reasoning_engine_2 = {
            "name": "projects/test-project/locations/test-location/reasoningEngines/456",  # pylint: disable=line-too-long
            "displayName": "My Second Test Memory Bank",
            "description": "My Second Test Memory Bank Description",
        }
        response = {"reasoningEngines": [reasoning_engine_1, reasoning_engine_2]}
        with mock.patch.object(
            async_memory_banks_client._api_client, "async_request", autospec=True
        ) as request_mock:
            request_mock.side_effect = [
                genai_types.HttpResponse(body=json.dumps(response)),
            ]
            memory_banks = []
            async for memory_bank in await async_memory_banks_client.list():
                memory_banks.append(memory_bank)
            request_mock.assert_called_once_with(
                "get",
                "reasoningEngines",
                {},
                None,
            )
            assert len(memory_banks) == 2
            assert isinstance(memory_banks[0], genai.types.MemoryBank)
            assert memory_banks[0].name == MEMORY_BANK_NAME
            assert memory_banks[0].display_name == DISPLAY_NAME
            assert memory_banks[0].description == DESCRIPTION
            assert isinstance(memory_banks[1], genai.types.MemoryBank)
            assert (
                memory_banks[1].name
                == "projects/test-project/locations/test-location/reasoningEngines/456"
            )
            assert memory_banks[1].display_name == "My Second Test Memory Bank"
            assert (
                memory_banks[1].description == "My Second Test Memory Bank Description"
            )

    def test_delete_memory_bank(self, memory_banks_client):
        """Tests the deletion of a Memory Bank."""
        with mock.patch.object(
            memory_banks_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.side_effect = [
                genai_types.HttpResponse(body=None),
            ]
            memory_banks_client.delete(name=MEMORY_BANK_NAME, force=True)
            request_mock.assert_called_once_with(
                "delete",
                MEMORY_BANK_NAME,
                {"_url": {"name": MEMORY_BANK_NAME}, "force": True},
                None,
            )

    @pytest.mark.asyncio
    async def test_async_delete_memory_bank(self, async_memory_banks_client):
        """Tests the deletion of a Memory Bank."""
        with mock.patch.object(
            async_memory_banks_client._api_client, "async_request", autospec=True
        ) as request_mock:
            request_mock.side_effect = [
                genai_types.HttpResponse(body=None),
            ]
            await async_memory_banks_client.delete(name=MEMORY_BANK_NAME, force=True)
            request_mock.assert_called_once_with(
                "delete",
                MEMORY_BANK_NAME,
                {"_url": {"name": MEMORY_BANK_NAME}, "force": True},
                None,
            )
