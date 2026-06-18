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

import pytest
from agentplatform._genai import types
from tests.unit.agentplatform.genai.replays import pytest_helper

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)

file_display_name = "Test rag file upload"


def test_upload_rag_file(client, tmp_path, monkeypatch):
    file_name = "test_replay_upload.txt"

    file_path = tmp_path / file_name
    file_path.write_text("This is a test file for RAG upload.")

    monkeypatch.chdir(tmp_path)

    uploaded_file = client.rag.upload_file(
        corpus_name="projects/vertex-sdk-dev/locations/us-central1/ragCorpora/5400941853124067328",
        path=file_name,
        display_name=file_display_name,
    )

    assert isinstance(uploaded_file, types.RagFile)
    assert uploaded_file.display_name == file_display_name


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_upload_rag_file_async(client, tmp_path, monkeypatch):
    file_name = "test_rag_file_upload.txt"
    file_path = tmp_path / file_name
    file_path.write_text("This is a test file for async RAG upload.")

    monkeypatch.chdir(tmp_path)

    uploaded_file = await client.aio.rag.upload_file(
        corpus_name="projects/vertex-sdk-dev/locations/us-central1/ragCorpora/5400941853124067328",
        path=file_name,
        display_name=file_display_name,
    )

    assert isinstance(uploaded_file, types.RagFile)
    assert uploaded_file.display_name == file_display_name
