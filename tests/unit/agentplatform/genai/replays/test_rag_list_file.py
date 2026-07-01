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
"""Tests the rag.list_files() method against the Agent Platform endpoint using replays."""
import pytest

from tests.unit.agentplatform.genai.replays import pytest_helper
from agentplatform._genai import types


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)


def test_list_rag_files(client):

    file_list = client.rag.list_files(
        name="projects/964831358985/locations/us-central1/ragCorpora/7890781536176308224",
    )

    assert isinstance(file_list, types.ListRagFilesResponse)


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_list_rag_files_async(client):

    file_list = await client.aio.rag.list_files(
        name="projects/964831358985/locations/us-central1/ragCorpora/7890781536176308224",
    )

    assert isinstance(file_list, types.ListRagFilesResponse)
