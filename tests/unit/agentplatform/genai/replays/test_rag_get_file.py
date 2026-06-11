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
"""Tests the rag.get_file() method against the Agent Platform endpoint using replays."""

import pytest

from tests.unit.agentplatform.genai.replays import pytest_helper
from agentplatform._genai import types


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)


def test_get_rag_file(client):

    rag_file = client.rag.get_file(
        name="projects/vertex-sdk-dev/locations/us-central1/ragCorpora/2305843009213693952/ragFiles/5692491588344435788",
    )

    assert isinstance(rag_file, types.RagFile)


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_get_rag_file_async(client):

    rag_file = await client.aio.rag.get_file(
        name="projects/vertex-sdk-dev/locations/us-central1/ragCorpora/2305843009213693952/ragFiles/5692491588344435788",
    )

    assert isinstance(rag_file, types.RagFile)
