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
import importlib
from google.cloud import aiplatform
from vertexai.preview import rag
from google.cloud.aiplatform_v1beta1 import (
    VertexRagServiceClient,
)
import mock
import pytest
import test_rag_constants as tc


@pytest.fixture
def retrieve_contexts_mock():
    with mock.patch.object(
        VertexRagServiceClient,
        "retrieve_contexts",
    ) as retrieve_contexts_mock:
        retrieve_contexts_mock.return_value = tc.TEST_RETRIEVAL_RESPONSE
        yield retrieve_contexts_mock


@pytest.fixture
def rag_client_mock_exception():
    with mock.patch.object(
        rag.utils._gapic_utils, "create_rag_service_client"
    ) as rag_client_mock_exception:
        api_client_mock = mock.Mock(spec=VertexRagServiceClient)
        # retrieve_contexts
        api_client_mock.retrieve_contexts.side_effect = Exception
        rag_client_mock_exception.return_value = api_client_mock
        yield rag_client_mock_exception


def retrieve_contexts_eq(response, expected_response):
    assert len(response.contexts.contexts) == len(expected_response.contexts.contexts)
    assert (
        response.contexts.contexts[0].text
        == expected_response.contexts.contexts[0].text
    )
    assert (
        response.contexts.contexts[0].source_uri
        == expected_response.contexts.contexts[0].source_uri
    )


@pytest.mark.usefixtures("google_auth_mock")
class TestRagRetrieval:
    def setup_method(self):
        importlib.reload(aiplatform.initializer)
        importlib.reload(aiplatform)
        aiplatform.init()

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    @pytest.mark.usefixtures("retrieve_contexts_mock")
    def test_retrieval_query_rag_resources_success(self):
        response = rag.retrieval_query(
            rag_resources=[tc.TEST_RAG_RESOURCE],
            text=tc.TEST_QUERY_TEXT,
            similarity_top_k=2,
            vector_distance_threshold=0.5,
        )
        retrieve_contexts_eq(response, tc.TEST_RETRIEVAL_RESPONSE)

    @pytest.mark.usefixtures("retrieve_contexts_mock")
    def test_retrieval_query_rag_corpora_success(self):
        response = rag.retrieval_query(
            rag_corpora=[tc.TEST_RAG_CORPUS_ID],
            text=tc.TEST_QUERY_TEXT,
            similarity_top_k=2,
            vector_distance_threshold=0.5,
        )
        retrieve_contexts_eq(response, tc.TEST_RETRIEVAL_RESPONSE)

    @pytest.mark.usefixtures("rag_client_mock_exception")
    def test_retrieval_query_failure(self):
        with pytest.raises(RuntimeError) as e:
            rag.retrieval_query(
                rag_resources=[tc.TEST_RAG_RESOURCE],
                text=tc.TEST_QUERY_TEXT,
                similarity_top_k=2,
                vector_distance_threshold=0.5,
            )
            e.match("Failed in retrieving contexts due to")

    def test_retrieval_query_invalid_name(self):
        with pytest.raises(ValueError) as e:
            rag.retrieval_query(
                rag_resources=[tc.TEST_RAG_RESOURCE_INVALID_NAME],
                text=tc.TEST_QUERY_TEXT,
                similarity_top_k=2,
                vector_distance_threshold=0.5,
            )
            e.match("Invalid RagCorpus name")

    def test_retrieval_query_multiple_rag_corpora(self):
        with pytest.raises(ValueError) as e:
            rag.retrieval_query(
                rag_corpora=[tc.TEST_RAG_CORPUS_ID, tc.TEST_RAG_CORPUS_ID],
                text=tc.TEST_QUERY_TEXT,
                similarity_top_k=2,
                vector_distance_threshold=0.5,
            )
            e.match("Currently only support 1 RagCorpus")

    def test_retrieval_query_multiple_rag_resources(self):
        with pytest.raises(ValueError) as e:
            rag.retrieval_query(
                rag_resources=[tc.TEST_RAG_RESOURCE, tc.TEST_RAG_RESOURCE],
                text=tc.TEST_QUERY_TEXT,
                similarity_top_k=2,
                vector_distance_threshold=0.5,
            )
            e.match("Currently only support 1 RagResource")
