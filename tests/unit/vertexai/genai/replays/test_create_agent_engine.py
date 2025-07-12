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


def test_create_config_lightweight(client):
    agent_display_name = "test-display-name"
    agent_description = "my agent"

    agent_engine = client.agent_engines.create(
        config={
            "display_name": agent_display_name,
            "description": agent_description,
        },
    )
    assert agent_engine.api_resource.display_name == agent_display_name
    assert agent_engine.api_resource.description == agent_description


def test_create_config_with_context_spec(client):
    if not os.environ.get("GOOGLE_CLOUD_PROJECT"):
        raise ValueError("GOOGLE_CLOUD_PROJECT environ variable is not set.")
    if not os.environ.get("GOOGLE_CLOUD_LOCATION"):
        raise ValueError("GOOGLE_CLOUD_LOCATION environ variable is not set.")
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    location = os.environ["GOOGLE_CLOUD_LOCATION"]
    parent = f"projects/{project}/locations/{location}"
    generation_model = f"{parent}/publishers/google/models/gemini-2.0-flash-001"
    embedding_model = f"{parent}/publishers/google/models/text-embedding-005"

    agent_engine = client.agent_engines.create(
        config={
            "context_spec": {
                "memory_bank_config": {
                    "generation_config": {"model": generation_model},
                    "similarity_search_config": {"embedding_model": embedding_model},
                },
            },
        }
    )
    assert agent_engine.api_resource


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.create",
)
