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

import os

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types

_TEST_CLASS_METHODS = [
    {"name": "query", "api_mode": ""},
]


def test_create_config_lightweight(client):
    agent_display_name = "test-display-name"
    agent_description = "my agent"

    if not os.environ.get("GCS_BUCKET"):
        raise ValueError("GCS_BUCKET environment variable is not set.")

    config = client.agent_engines._create_config(
        mode="create",
        staging_bucket=os.environ["GCS_BUCKET"],
        display_name=agent_display_name,
        description=agent_description,
    )
    assert config == {
        "display_name": agent_display_name,
        "description": agent_description,
    }


def test_create_with_labels(client):
    labels = {"test-label": "test-value"}
    agent_engine = client.agent_engines.create(
        config={"labels": labels},
    )
    assert agent_engine.api_resource.labels == labels
    # Clean up resources.
    client.agent_engines.delete(name=agent_engine.api_resource.name, force=True)


def test_create_with_context_spec(client):
    project = "test-project"
    location = "us-central1"
    parent = f"projects/{project}/locations/{location}"
    generation_model = f"{parent}/publishers/google/models/gemini-2.0-flash-001"
    embedding_model = f"{parent}/publishers/google/models/text-embedding-005"
    customization_config = {
        "memory_topics": [
            {"managed_memory_topic": {"managed_topic_enum": "USER_PREFERENCES"}}
        ],
        "generate_memories_examples": [
            {
                "conversation_source": {
                    "events": [
                        {"content": {"role": "user", "parts": [{"text": "Hello"}]}}
                    ]
                },
                "generatedMemories": [
                    {
                        "fact": "I like to say hello.",
                        "topics": [{"managed_memory_topic": "USER_PREFERENCES"}],
                    }
                ],
            }
        ],
    }
    memory_bank_customization_config = types.MemoryBankCustomizationConfig(
        **customization_config
    )

    agent_engine = client.agent_engines.create(
        config={
            "context_spec": {
                "memory_bank_config": {
                    "generation_config": {"model": generation_model},
                    "similarity_search_config": {
                        "embedding_model": embedding_model,
                    },
                    "ttl_config": {"default_ttl": "120s"},
                    "customization_configs": [memory_bank_customization_config],
                },
            },
            "http_options": {"api_version": "v1beta1"},
        },
    )
    agent_engine = client.agent_engines.get(name=agent_engine.api_resource.name)
    memory_bank_config = agent_engine.api_resource.context_spec.memory_bank_config
    assert memory_bank_config.generation_config.model == generation_model
    assert (
        memory_bank_config.similarity_search_config.embedding_model == embedding_model
    )
    assert memory_bank_config.ttl_config.default_ttl == "120s"
    assert memory_bank_config.customization_configs == [
        memory_bank_customization_config
    ]
    # Clean up resources.
    client.agent_engines.delete(name=agent_engine.api_resource.name, force=True)


def test_create_with_source_packages(
    client,
    mock_agent_engine_create_base64_encoded_tarball,
    mock_agent_engine_create_path_exists,
):
    """Tests creating an agent engine with source packages."""
    with (
        mock_agent_engine_create_base64_encoded_tarball,
        mock_agent_engine_create_path_exists,
    ):
        agent_engine = client.agent_engines.create(
            config={
                "display_name": "test-agent-engine-source-packages",
                "source_packages": [
                    "test_module.py",
                    "requirements.txt",
                ],
                "entrypoint_module": "test_module",
                "entrypoint_object": "test_object",
                "class_methods": _TEST_CLASS_METHODS,
                "http_options": {
                    "base_url": "https://us-west1-aiplatform.googleapis.com",
                    "api_version": "v1beta1",
                },
            },
        )
        assert (
            agent_engine.api_resource.display_name
            == "test-agent-engine-source-packages"
        )
        # Clean up resources.
        client.agent_engines.delete(name=agent_engine.api_resource.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.create",
)
