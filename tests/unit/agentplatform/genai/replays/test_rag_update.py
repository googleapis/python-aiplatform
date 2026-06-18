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
"""Tests the rag._update_corpus() method against the Agent Platform endpoint using replays."""

import pytest

from tests.unit.agentplatform.genai.replays import pytest_helper
from agentplatform._genai import types


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)


def test_update_rag_corpus_private(client):

    corpus_op = client.rag._update_corpus(
        name="projects/vertex-sdk-dev/locations/us-central1/ragCorpora/5685794529555251200",
        rag_corpus=types.RagCorpus(
            display_name="My Updated Vertex AI Search Test Corpus",
            description="My Updated Test Corpus Description",
            vertex_ai_search_config=types.VertexAiSearchConfig(
                serving_config="projects/vertex-sdk-dev/locations/us-central1/collections/default_collection/engines/test-engine/servingConfigs/default_serving_config"
            ),
        ),
    )

    assert isinstance(corpus_op, types.UpdateRagCorpusOperation)


def test_update_rag_corpus(client):
    search_config = types.VertexAiSearchConfig(
        serving_config="projects/vertex-sdk-dev/locations/us-central1/collections/default_collection/engines/test-engine/servingConfigs/default_serving_config"
    )

    # Create a corpus to update
    corpus = client.rag.create_corpus(
        rag_corpus=types.RagCorpus(
            display_name="My Test Corpus",
            description="My Test Corpus Description",
            vertex_ai_search_config=search_config,
        ),
    )

    updated_corpus = client.rag.update_corpus(
        name=corpus.name,
        rag_corpus=types.RagCorpus(
            display_name="My Updated Vertex AI Search Test Corpus",
            description="My Updated Test Corpus Description",
            vertex_ai_search_config=search_config,
        ),
    )

    assert updated_corpus.display_name == "My Updated Vertex AI Search Test Corpus"
    assert updated_corpus.description == "My Updated Test Corpus Description"


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_update_rag_corpus_private_async(client):
    corpus_op = await client.aio.rag._update_corpus(
        name="projects/vertex-sdk-dev/locations/us-central1/ragCorpora/5685794529555251200",
        rag_corpus=types.RagCorpus(
            display_name="My Updated Vertex AI Search Test Corpus",
            description="My Updated Test Corpus Description",
            vertex_ai_search_config=types.VertexAiSearchConfig(
                serving_config="projects/vertex-sdk-dev/locations/us-central1/collections/default_collection/engines/test-engine/servingConfigs/default_serving_config"
            ),
        ),
    )

    assert isinstance(corpus_op, types.UpdateRagCorpusOperation)


@pytest.mark.asyncio
async def test_update_rag_corpus_async(client):
    search_config = types.VertexAiSearchConfig(
        serving_config="projects/vertex-sdk-dev/locations/us-central1/collections/default_collection/engines/test-engine/servingConfigs/default_serving_config"
    )

    # Create a corpus to update
    corpus = await client.aio.rag.create_corpus(
        rag_corpus=types.RagCorpus(
            display_name="My Test Corpus",
            description="My Test Corpus Description",
            vertex_ai_search_config=search_config,
        ),
    )

    updated_corpus = await client.aio.rag.update_corpus(
        name=corpus.name,
        rag_corpus=types.RagCorpus(
            display_name="My Updated Vertex AI Search Test Corpus",
            description="My Updated Test Corpus Description",
            vertex_ai_search_config=search_config,
        ),
    )

    assert updated_corpus.display_name == "My Updated Vertex AI Search Test Corpus"
    assert updated_corpus.description == "My Updated Test Corpus Description"
