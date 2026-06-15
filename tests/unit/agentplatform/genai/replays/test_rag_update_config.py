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
"""Tests the rag._update_config() method against the Agent Platform endpoint using replays."""

import pytest

from tests.unit.agentplatform.genai.replays import pytest_helper
from agentplatform._genai import types


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)


def test_update_rag_config_private(client):
    config_op = client.rag._update_config(
        updated_config=types.RagEngineConfig(
            name="projects/vertex-sdk-dev/locations/us-central1/ragEngineConfig/test_rag_config",
            rag_managed_db_config=types.RagManagedDbConfig(
                serverless=types.RagManagedDbConfigServerless()
            ),
        ),
    )

    assert isinstance(config_op, types.UpdateRagConfigOperation)


def test_config_update(client):
    updated_config = client.rag.update_config(
        updated_config=types.RagEngineConfig(
            name="projects/vertex-sdk-dev/locations/us-central1/ragEngineConfig",
        )
    )

    assert isinstance(updated_config, types.RagEngineConfig)
    assert (
        updated_config.name
        == "projects/vertex-sdk-dev/locations/us-central1/ragEngineConfig"
    )


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_update_rag_config_private_async(client):
    config_op = await client.aio.rag._update_config(
        updated_config=types.RagEngineConfig(
            name="projects/vertex-sdk-dev/locations/us-central1/ragEngineConfig/test_rag_config",
            rag_managed_db_config=types.RagManagedDbConfig(
                serverless=types.RagManagedDbConfigServerless()
            ),
        ),
    )

    assert isinstance(config_op, types.UpdateRagConfigOperation)


@pytest.mark.asyncio
async def test_config_update_async(client):
    updated_config = await client.aio.rag.update_config(
        updated_config=types.RagEngineConfig(
            name="projects/vertex-sdk-dev/locations/us-central1/ragEngineConfig",
        )
    )

    assert isinstance(updated_config, types.RagEngineConfig)
    assert (
        updated_config.name
        == "projects/vertex-sdk-dev/locations/us-central1/ragEngineConfig"
    )
