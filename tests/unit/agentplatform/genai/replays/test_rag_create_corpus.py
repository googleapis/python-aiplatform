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
"""Tests the rag._create_corpus() method against the Agent Platform endpoint using replays."""

import pytest

from tests.unit.agentplatform.genai.replays import pytest_helper
from agentplatform._genai import types


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)


def test_create_rag_corpus_private(client):

    corpus_op = client.rag._create_corpus(
        rag_corpus=types.RagCorpus(
            display_name="My Test Corpus",
            description="My Test Corpus Description",
        ),
    )

    assert isinstance(corpus_op, types.CreateRagCorpusOperation)


def test_create_rag_corpus(client):

    corpus_description = "My Test Corpus Description"

    corpus = client.rag.create_corpus(
        rag_corpus=types.RagCorpus(
            display_name="My Test Corpus",
            description=corpus_description,
        ),
    )

    assert isinstance(corpus, types.RagCorpus)
    assert corpus.description == corpus_description


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_create_rag_corpus_private_async(client):

    corpus_op = await client.aio.rag._create_corpus(
        rag_corpus=types.RagCorpus(
            display_name="My Test Corpus",
            description="My Test Corpus Description",
        ),
    )

    assert isinstance(corpus_op, types.CreateRagCorpusOperation)


@pytest.mark.asyncio
async def test_create_rag_corpus_async(client):

    corpus_description = "My Test Corpus Description"

    corpus = await client.aio.rag.create_corpus(
        rag_corpus=types.RagCorpus(
            display_name="My Test Corpus",
            description=corpus_description,
        ),
    )

    assert isinstance(corpus, types.RagCorpus)
    assert corpus.description == corpus_description
