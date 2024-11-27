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
from vertexai import rag
from vertexai.preview.generative_models import Tool
import pytest
import test_rag_constants as tc


@pytest.mark.usefixtures("google_auth_mock")
class TestRagStoreValidations:
    def test_retrieval_tool_invalid_name(self):
        with pytest.raises(ValueError) as e:
            Tool.from_retrieval(
                retrieval=rag.Retrieval(
                    source=rag.VertexRagStore(
                        rag_resources=[tc.TEST_RAG_RESOURCE_INVALID_NAME],
                        rag_retrieval_config=tc.TEST_RAG_RETRIEVAL_SIMILARITY_CONFIG,
                    ),
                )
            )
            e.match("Invalid RagCorpus name")

    def test_retrieval_tool_multiple_rag_resources(self):
        with pytest.raises(ValueError) as e:
            Tool.from_retrieval(
                retrieval=rag.Retrieval(
                    source=rag.VertexRagStore(
                        rag_resources=[tc.TEST_RAG_RESOURCE, tc.TEST_RAG_RESOURCE],
                        rag_retrieval_config=tc.TEST_RAG_RETRIEVAL_CONFIG,
                    ),
                )
            )
            e.match("Currently only support 1 RagResource")

    def test_retrieval_tool_invalid_config_filter(self):
        with pytest.raises(ValueError) as e:
            Tool.from_retrieval(
                retrieval=rag.Retrieval(
                    source=rag.VertexRagStore(
                        rag_resources=[tc.TEST_RAG_RESOURCE],
                        rag_retrieval_config=tc.TEST_RAG_RETRIEVAL_ERROR_CONFIG,
                    )
                )
            )
            e.match(
                "Only one of vector_distance_threshold or"
                " vector_similarity_threshold can be specified at a time"
                " in rag_retrieval_config."
            )
