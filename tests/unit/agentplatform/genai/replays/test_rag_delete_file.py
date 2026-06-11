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
"""Tests the rag._delete_file() method against the Agent Platform endpoint using replays."""

import pytest

from agentplatform._genai import types
from tests.unit.agentplatform.genai.replays import pytest_helper


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)


def test_delete_rag_file_private(client):

    file_op = client.rag._delete_file(
        name="projects/vertex-sdk-dev/locations/us-central1/ragCorpora/2227030015734710272/ragFiles/5711059209630117604"
    )

    assert isinstance(file_op, types.DeleteRagFileOperation)


def test_delete_rag_file(client):
    client.rag.delete_file(
        name="projects/vertex-sdk-dev/locations/us-central1/ragCorpora/3671559596213796864/ragFiles/5713990948125380655",
    )


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_delete_rag_file_async(client):

    await client.aio.rag.delete_file(
        name="projects/vertex-sdk-dev/locations/us-central1/ragCorpora/3671559596213796864/ragFiles/5713993151049969908",
    )
