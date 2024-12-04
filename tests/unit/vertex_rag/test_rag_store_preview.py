# -*- coding: utf-8 -*-

# Copyright 2024 Google LLC
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
from vertexai.preview import rag
from vertexai.preview.generative_models import Tool
import pytest
import test_rag_constants_preview


@pytest.mark.usefixtures("google_auth_mock")
class TestRagStore:
    def test_retrieval_tool_success(self):
        with pytest.warns(DeprecationWarning):
            Tool.from_retrieval(
                retrieval=rag.Retrieval(
                    source=rag.VertexRagStore(
                        rag_resources=[test_rag_constants_preview.TEST_RAG_RESOURCE],
                        similarity_top_k=3,
                        vector_distance_threshold=0.4,
                    ),
                )
            )

    def test_retrieval_tool_config_success(self):
        with pytest.warns(DeprecationWarning):
            Tool.from_retrieval(
                retrieval=rag.Retrieval(
                    source=rag.VertexRagStore(
                        rag_corpora=[
                            test_rag_constants_preview.TEST_RAG_CORPUS_ID,
                        ],
                        rag_retrieval_config=test_rag_constants_preview.TEST_RAG_RETRIEVAL_CONFIG,
                    ),
                )
            )

    def test_retrieval_tool_similarity_config_success(self):
        with pytest.warns(DeprecationWarning):
            Tool.from_retrieval(
                retrieval=rag.Retrieval(
                    source=rag.VertexRagStore(
                        rag_corpora=[
                            test_rag_constants_preview.TEST_RAG_CORPUS_ID,
                        ],
                        rag_retrieval_config=test_rag_constants_preview.TEST_RAG_RETRIEVAL_SIMILARITY_CONFIG,
                    ),
                )
            )

    def test_retrieval_tool_ranking_config_success(self):
        with pytest.warns(DeprecationWarning):
            Tool.from_retrieval(
                retrieval=rag.Retrieval(
                    source=rag.VertexRagStore(
                        rag_corpora=[
                            test_rag_constants_preview.TEST_RAG_CORPUS_ID,
                        ],
                        rag_retrieval_config=test_rag_constants_preview.TEST_RAG_RETRIEVAL_RANKING_CONFIG,
                    ),
                )
            )

    def test_empty_retrieval_tool_success(self):
        tool = Tool.from_retrieval(
            retrieval=rag.Retrieval(
                source=rag.VertexRagStore(
                    rag_resources=[test_rag_constants_preview.TEST_RAG_RESOURCE],
                    rag_retrieval_config=rag.RagRetrievalConfig(),
                    similarity_top_k=3,
                    vector_distance_threshold=0.4,
                ),
            )
        )
        assert tool is not None

    def test_retrieval_tool_no_rag_resources(self):
        with pytest.raises(ValueError) as e:
            Tool.from_retrieval(
                retrieval=rag.Retrieval(
                    source=rag.VertexRagStore(
                        rag_retrieval_config=test_rag_constants_preview.TEST_RAG_RETRIEVAL_SIMILARITY_CONFIG,
                    ),
                )
            )
            e.match("rag_resources or rag_corpora must be specified.")

    def test_retrieval_tool_invalid_name(self):
        with pytest.raises(ValueError) as e:
            Tool.from_retrieval(
                retrieval=rag.Retrieval(
                    source=rag.VertexRagStore(
                        rag_resources=[
                            test_rag_constants_preview.TEST_RAG_RESOURCE_INVALID_NAME
                        ],
                        similarity_top_k=3,
                        vector_distance_threshold=0.4,
                    ),
                )
            )
            e.match("Invalid RagCorpus name")

    def test_retrieval_tool_invalid_name_config(self):
        with pytest.raises(ValueError) as e:
            Tool.from_retrieval(
                retrieval=rag.Retrieval(
                    source=rag.VertexRagStore(
                        rag_resources=[
                            test_rag_constants_preview.TEST_RAG_RESOURCE_INVALID_NAME
                        ],
                        rag_retrieval_config=test_rag_constants_preview.TEST_RAG_RETRIEVAL_CONFIG,
                    ),
                )
            )
            e.match("Invalid RagCorpus name")

    def test_retrieval_tool_multiple_rag_corpora(self):
        with pytest.raises(ValueError) as e:
            Tool.from_retrieval(
                retrieval=rag.Retrieval(
                    source=rag.VertexRagStore(
                        rag_corpora=[
                            test_rag_constants_preview.TEST_RAG_CORPUS_ID,
                            test_rag_constants_preview.TEST_RAG_CORPUS_ID,
                        ],
                        similarity_top_k=3,
                        vector_distance_threshold=0.4,
                    ),
                )
            )
            e.match("Currently only support 1 RagCorpus")

    def test_retrieval_tool_multiple_rag_corpora_config(self):
        with pytest.raises(ValueError) as e:
            Tool.from_retrieval(
                retrieval=rag.Retrieval(
                    source=rag.VertexRagStore(
                        rag_corpora=[
                            test_rag_constants_preview.TEST_RAG_CORPUS_ID,
                            test_rag_constants_preview.TEST_RAG_CORPUS_ID,
                        ],
                        rag_retrieval_config=test_rag_constants_preview.TEST_RAG_RETRIEVAL_CONFIG,
                    ),
                )
            )
            e.match("Currently only support 1 RagCorpus")

    def test_retrieval_tool_multiple_rag_resources(self):
        with pytest.raises(ValueError) as e:
            Tool.from_retrieval(
                retrieval=rag.Retrieval(
                    source=rag.VertexRagStore(
                        rag_resources=[
                            test_rag_constants_preview.TEST_RAG_RESOURCE,
                            test_rag_constants_preview.TEST_RAG_RESOURCE,
                        ],
                        similarity_top_k=3,
                        vector_distance_threshold=0.4,
                    ),
                )
            )
            e.match("Currently only support 1 RagResource")

    def test_retrieval_tool_multiple_rag_resources_config(self):
        with pytest.raises(ValueError) as e:
            Tool.from_retrieval(
                retrieval=rag.Retrieval(
                    source=rag.VertexRagStore(
                        rag_resources=[
                            test_rag_constants_preview.TEST_RAG_RESOURCE,
                            test_rag_constants_preview.TEST_RAG_RESOURCE,
                        ],
                        rag_retrieval_config=test_rag_constants_preview.TEST_RAG_RETRIEVAL_CONFIG,
                    ),
                )
            )
            e.match("Currently only support 1 RagResource")

    def test_retrieval_tool_invalid_config_filter(self):
        with pytest.raises(ValueError) as e:
            Tool.from_retrieval(
                retrieval=rag.Retrieval(
                    source=rag.VertexRagStore(
                        rag_resources=[test_rag_constants_preview.TEST_RAG_RESOURCE],
                        rag_retrieval_config=test_rag_constants_preview.TEST_RAG_RETRIEVAL_ERROR_CONFIG,
                    )
                )
            )
            e.match(
                "Only one of vector_distance_threshold or"
                " vector_similarity_threshold can be specified at a time"
                " in rag_retrieval_config."
            )

    def test_retrieval_tool_invalid_ranking_config_filter(self):
        with pytest.raises(ValueError) as e:
            Tool.from_retrieval(
                retrieval=rag.Retrieval(
                    source=rag.VertexRagStore(
                        rag_resources=[test_rag_constants_preview.TEST_RAG_RESOURCE],
                        rag_retrieval_config=test_rag_constants_preview.TEST_RAG_RETRIEVAL_ERROR_RANKING_CONFIG,
                    )
                )
            )
            e.match(
                "Only one of vector_distance_threshold or"
                " vector_similarity_threshold can be specified at a time"
                " in rag_retrieval_config."
            )
