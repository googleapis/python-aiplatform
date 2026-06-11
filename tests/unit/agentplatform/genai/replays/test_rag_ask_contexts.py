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
"""Tests the rag.ask_contexts() method against the Agent Platform endpoint using replays."""

import pytest

from tests.unit.agentplatform.genai.replays import pytest_helper
from agentplatform._genai import types
from google.genai import types as genai_types


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)


def test_ask_contexts(client):

    rag_contexts = client.rag.ask_contexts(
        query=types.RagQuery(
            text="earnings",
            similarity_top_k=5,
        ),
        tools=[
            genai_types.Tool(
                retrieval=genai_types.Retrieval(
                    vertex_rag_store=genai_types.VertexRagStore(
                        rag_resources=[
                            genai_types.VertexRagStoreRagResource(
                                rag_corpus="projects/vertex-sdk-dev/locations/us-central1/ragCorpora/2305843009213693952"
                            )
                        ]
                    )
                )
            )
        ],
    )

    assert isinstance(rag_contexts, types.AskContextsResponse)


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_ask_contexts_async(client):

    rag_contexts = await client.aio.rag.ask_contexts(
        query=types.RagQuery(
            text="Grounding query",
            similarity_top_k=5,
        ),
        tools=[
            genai_types.Tool(
                retrieval=genai_types.Retrieval(
                    vertex_rag_store=genai_types.VertexRagStore(
                        rag_resources=[
                            genai_types.VertexRagStoreRagResource(
                                rag_corpus="projects/vertex-sdk-dev/locations/us-central1/ragCorpora/2305843009213693952"
                            )
                        ]
                    )
                )
            )
        ],
    )

    assert isinstance(rag_contexts, types.AskContextsResponse)
