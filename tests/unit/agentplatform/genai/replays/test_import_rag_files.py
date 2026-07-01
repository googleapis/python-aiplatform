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
"""Tests the RAG import files against the Agent Platform endpoint using replays."""
import pytest

from tests.unit.agentplatform.genai.replays import pytest_helper
from agentplatform._genai import types
from google.genai import types as genai_types


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)


def test_rag_import_private(client):

    response = client.rag._import_files(
        name="projects/vertex-sdk-dev/locations/us-central1/ragCorpora/3671559596213796864",
        import_rag_files_request=types.ImportRagFilesRequest(
            import_rag_files_config=types.ImportRagFilesConfig(
                gcs_source=genai_types.GcsSource(
                    uris=["gs://sararob_test/test-rag-file.pdf"]
                ),
            ),
        ),
    )

    assert isinstance(response, types.ImportRagFilesOperation)


def test_rag_import(client):

    gcs_filepath = "gs://sararob_test/test-rag-file.pdf"

    import_file_response = client.rag.import_files(
        name="projects/vertex-sdk-dev/locations/us-central1/ragCorpora/6301661778598166528",
        import_config=types.ImportRagFilesConfig(
            gcs_source=genai_types.GcsSource(uris=[gcs_filepath]),
        ),
    )

    assert isinstance(import_file_response, types.ImportRagFilesResponse)

    assert import_file_response.imported_rag_files_count == 1


def test_rag_import_wrong_project_raises(client):

    gcs_filepath = "gs://sdk-rag-system-test/rag_data/11.pdf"

    with pytest.raises(ValueError):
        client.rag.import_files(
            name="projects/vertex-sdk-dev/locations/us-central1/ragCorpora/6301661778598166528",
            import_config=types.ImportRagFilesConfig(
                gcs_source=genai_types.GcsSource(uris=[gcs_filepath]),
            ),
        )


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_import_files_async(client):

    gcs_filepath = "gs://sararob_test/test-rag-file.pdf"

    import_file_response = await client.aio.rag.import_files(
        name="projects/vertex-sdk-dev/locations/us-central1/ragCorpora/3671559596213796864",
        import_config=types.ImportRagFilesConfig(
            gcs_source=genai_types.GcsSource(uris=[gcs_filepath]),
        ),
    )

    assert isinstance(import_file_response, types.ImportRagFilesResponse)
    # This file is already imported in this corpus, so it should be skipped.
    assert import_file_response.skipped_rag_files_count == 1
