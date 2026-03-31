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
"""Tests for vertex_rag.retrieval_preview."""

import importlib
from google.cloud import aiplatform
from google.cloud.aiplatform_v1beta1 import VertexRagServiceAsyncClient
from google.cloud.aiplatform_v1beta1 import VertexRagServiceClient
import test_rag_constants_preview
from vertexai.preview import rag
import mock
import pytest

tc = test_rag_constants_preview


@pytest.fixture
def retrieve_contexts_mock():
    with mock.patch.object(
        VertexRagServiceClient,
        "retrieve_contexts",
    ) as patched_retrieve_contexts:
        patched_retrieve_contexts.return_value = tc.TEST_RETRIEVAL_RESPONSE
        yield patched_retrieve_contexts


@pytest.fixture
def ask_contexts_mock():
    with mock.patch.object(
        VertexRagServiceClient,
        "ask_contexts",
    ) as patched_ask_contexts:
        patched_ask_contexts.return_value = tc.TEST_RETRIEVAL_RESPONSE
        yield patched_ask_contexts


@pytest.fixture
def async_retrieve_contexts_mock():
    with mock.patch.object(
        VertexRagServiceAsyncClient,
        "async_retrieve_contexts",
        new_callable=mock.AsyncMock,
    ) as patched_async_retrieve_contexts:
        lro_mock = mock.Mock()
        lro_mock.result = mock.AsyncMock(return_value=tc.TEST_RETRIEVAL_RESPONSE)
        patched_async_retrieve_contexts.return_value = lro_mock
        yield patched_async_retrieve_contexts


@pytest.fixture
def rag_client_mock_exception():
    with mock.patch.object(
        rag.utils._gapic_utils,
        "create_rag_service_client",  # pylint: disable=protected-access
    ) as patched_rag_client_mock_exception:
        api_client_mock = mock.Mock(spec=VertexRagServiceClient)
        # retrieve_contexts
        api_client_mock.retrieve_contexts.side_effect = Exception
        patched_rag_client_mock_exception.return_value = api_client_mock
        yield patched_rag_client_mock_exception


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
class TestRagRetrieval:  # pylint: disable=missing-class-docstring

    def setup_method(self):
        importlib.reload(aiplatform.initializer)
        importlib.reload(aiplatform)
        aiplatform.init()

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    @pytest.mark.usefixtures("retrieve_contexts_mock")
    def test_retrieval_query_rag_resources_success(self):
        with pytest.warns(DeprecationWarning):
            response = rag.retrieval_query(
                rag_resources=[tc.TEST_RAG_RESOURCE],
                text=tc.TEST_QUERY_TEXT,
                similarity_top_k=2,
                vector_distance_threshold=0.5,
                vector_search_alpha=0.5,
            )
            retrieve_contexts_eq(response, tc.TEST_RETRIEVAL_RESPONSE)

    @pytest.mark.usefixtures("ask_contexts_mock")
    def test_ask_contexts_rag_resources_success(self):
        response = rag.ask_contexts(
            rag_resources=[tc.TEST_RAG_RESOURCE],
            text=tc.TEST_QUERY_TEXT,
            rag_retrieval_config=tc.TEST_RAG_RETRIEVAL_CONFIG_ALPHA,
        )
        retrieve_contexts_eq(response, tc.TEST_RETRIEVAL_RESPONSE)

    @pytest.mark.usefixtures("ask_contexts_mock")
    def test_ask_contexts_multiple_rag_resources_success(self):
        response = rag.ask_contexts(
            rag_resources=[tc.TEST_RAG_RESOURCE, tc.TEST_RAG_RESOURCE],
            text=tc.TEST_QUERY_TEXT,
            rag_retrieval_config=tc.TEST_RAG_RETRIEVAL_CONFIG_ALPHA,
        )
        retrieve_contexts_eq(response, tc.TEST_RETRIEVAL_RESPONSE)

    @pytest.mark.usefixtures("ask_contexts_mock")
    def test_ask_contexts_multiple_rag_corpora_success(self):
        with pytest.warns(DeprecationWarning):
            response = rag.ask_contexts(
                rag_corpora=[tc.TEST_RAG_CORPUS_ID, tc.TEST_RAG_CORPUS_ID],
                text=tc.TEST_QUERY_TEXT,
                rag_retrieval_config=tc.TEST_RAG_RETRIEVAL_CONFIG_ALPHA,
            )
            retrieve_contexts_eq(response, tc.TEST_RETRIEVAL_RESPONSE)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("async_retrieve_contexts_mock")
    async def test_async_retrieve_contexts_rag_resources_success(self):
        response = await rag.async_retrieve_contexts(
            rag_resources=[tc.TEST_RAG_RESOURCE],
            text=tc.TEST_QUERY_TEXT,
            rag_retrieval_config=tc.TEST_RAG_RETRIEVAL_CONFIG_ALPHA,
        )
        retrieve_contexts_eq(response, tc.TEST_RETRIEVAL_RESPONSE)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("async_retrieve_contexts_mock")
    async def test_async_retrieve_contexts_multiple_rag_resources_success(self):
        response = await rag.async_retrieve_contexts(
            rag_resources=[tc.TEST_RAG_RESOURCE, tc.TEST_RAG_RESOURCE],
            text=tc.TEST_QUERY_TEXT,
            rag_retrieval_config=tc.TEST_RAG_RETRIEVAL_CONFIG_ALPHA,
        )
        retrieve_contexts_eq(response, tc.TEST_RETRIEVAL_RESPONSE)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("async_retrieve_contexts_mock")
    async def test_async_retrieve_contexts_multiple_rag_corpora_success(self):
        with pytest.warns(DeprecationWarning):
            response = await rag.async_retrieve_contexts(
                rag_corpora=[tc.TEST_RAG_CORPUS_ID, tc.TEST_RAG_CORPUS_ID],
                text=tc.TEST_QUERY_TEXT,
                rag_retrieval_config=tc.TEST_RAG_RETRIEVAL_CONFIG_ALPHA,
            )
            retrieve_contexts_eq(response, tc.TEST_RETRIEVAL_RESPONSE)

    @pytest.mark.usefixtures("retrieve_contexts_mock")
    def test_retrieval_query_rag_resources_config_success(self):
        response = rag.retrieval_query(
            rag_resources=[tc.TEST_RAG_RESOURCE],
            text=tc.TEST_QUERY_TEXT,
            rag_retrieval_config=tc.TEST_RAG_RETRIEVAL_CONFIG_ALPHA,
        )
        retrieve_contexts_eq(response, tc.TEST_RETRIEVAL_RESPONSE)

    @pytest.mark.usefixtures("retrieve_contexts_mock")
    def test_retrieval_query_rag_resources_similarity_config_success(self):
        response = rag.retrieval_query(
            rag_resources=[tc.TEST_RAG_RESOURCE],
            text=tc.TEST_QUERY_TEXT,
            rag_retrieval_config=tc.TEST_RAG_RETRIEVAL_SIMILARITY_CONFIG,
        )
        retrieve_contexts_eq(response, tc.TEST_RETRIEVAL_RESPONSE)

    @pytest.mark.usefixtures("retrieve_contexts_mock")
    def test_retrieval_query_rag_resources_default_config_success(self):
        response = rag.retrieval_query(
            rag_resources=[tc.TEST_RAG_RESOURCE],
            text=tc.TEST_QUERY_TEXT,
        )
        retrieve_contexts_eq(response, tc.TEST_RETRIEVAL_RESPONSE)

    @pytest.mark.usefixtures("retrieve_contexts_mock")
    def test_retrieval_query_rag_corpora_success(self):
        with pytest.warns(DeprecationWarning):
            response = rag.retrieval_query(
                rag_corpora=[tc.TEST_RAG_CORPUS_ID],
                text=tc.TEST_QUERY_TEXT,
                similarity_top_k=2,
                vector_distance_threshold=0.5,
            )
            retrieve_contexts_eq(response, tc.TEST_RETRIEVAL_RESPONSE)

    @pytest.mark.usefixtures("retrieve_contexts_mock")
    def test_retrieval_query_rag_corpora_config_success(self):
        response = rag.retrieval_query(
            rag_corpora=[tc.TEST_RAG_CORPUS_ID],
            text=tc.TEST_QUERY_TEXT,
            rag_retrieval_config=tc.TEST_RAG_RETRIEVAL_CONFIG,
        )
        retrieve_contexts_eq(response, tc.TEST_RETRIEVAL_RESPONSE)

    @pytest.mark.usefixtures("retrieve_contexts_mock")
    def test_retrieval_query_rag_corpora_config_rank_service_success(self):
        response = rag.retrieval_query(
            rag_corpora=[tc.TEST_RAG_CORPUS_ID],
            text=tc.TEST_QUERY_TEXT,
            rag_retrieval_config=tc.TEST_RAG_RETRIEVAL_CONFIG_RANK_SERVICE,
        )
        retrieve_contexts_eq(response, tc.TEST_RETRIEVAL_RESPONSE)

    @pytest.mark.usefixtures("retrieve_contexts_mock")
    def test_retrieval_query_with_metadata_filter(self, retrieve_contexts_mock):
        metadata_filter = 'doc.metadata.genre == "fiction"'
        rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=10,
            filter=rag.Filter(
                vector_distance_threshold=0.5, metadata_filter=metadata_filter
            ),
        )
        rag.retrieval_query(
            rag_resources=[tc.TEST_RAG_RESOURCE],
            text=tc.TEST_QUERY_TEXT,
            rag_retrieval_config=rag_retrieval_config,
        )
        retrieve_contexts_mock.assert_called_once()
        args, kwargs = retrieve_contexts_mock.call_args
        request = kwargs["request"]
        assert (
            request.query.rag_retrieval_config.filter.metadata_filter == metadata_filter
        )

    @pytest.mark.usefixtures("retrieve_contexts_mock")
    def test_retrieval_query_rag_corpora_config_llm_ranker_success(self):
        response = rag.retrieval_query(
            rag_corpora=[tc.TEST_RAG_CORPUS_ID],
            text=tc.TEST_QUERY_TEXT,
            rag_retrieval_config=tc.TEST_RAG_RETRIEVAL_CONFIG_LLM_RANKER,
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

    @pytest.mark.usefixtures("rag_client_mock_exception")
    def test_retrieval_query_config_failure(self):
        with pytest.raises(RuntimeError) as e:
            rag.retrieval_query(
                rag_resources=[tc.TEST_RAG_RESOURCE],
                text=tc.TEST_QUERY_TEXT,
                rag_retrieval_config=tc.TEST_RAG_RETRIEVAL_CONFIG,
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

    def test_retrieval_query_invalid_name_config(self):
        with pytest.raises(ValueError) as e:
            rag.retrieval_query(
                rag_resources=[tc.TEST_RAG_RESOURCE_INVALID_NAME],
                text=tc.TEST_QUERY_TEXT,
                rag_retrieval_config=tc.TEST_RAG_RETRIEVAL_CONFIG,
            )
            e.match("Invalid RagCorpus name")

    def test_retrieval_query_multiple_rag_corpora(self):
        with pytest.raises(ValueError) as e:
            rag.retrieval_query(
                rag_corpora=[
                    tc.TEST_RAG_CORPUS_ID,
                    tc.TEST_RAG_CORPUS_ID,
                ],
                text=tc.TEST_QUERY_TEXT,
                similarity_top_k=2,
                vector_distance_threshold=0.5,
            )
            e.match("Currently only support 1 RagCorpus")

    def test_retrieval_query_multiple_rag_corpora_config(self):
        with pytest.raises(ValueError) as e:
            rag.retrieval_query(
                rag_corpora=[
                    tc.TEST_RAG_CORPUS_ID,
                    tc.TEST_RAG_CORPUS_ID,
                ],
                text=tc.TEST_QUERY_TEXT,
                rag_retrieval_config=tc.TEST_RAG_RETRIEVAL_CONFIG,
            )
            e.match("Currently only support 1 RagCorpus")

    def test_retrieval_query_multiple_rag_resources(self):
        with pytest.raises(ValueError) as e:
            rag.retrieval_query(
                rag_resources=[
                    tc.TEST_RAG_RESOURCE,
                    tc.TEST_RAG_RESOURCE,
                ],
                text=tc.TEST_QUERY_TEXT,
                similarity_top_k=2,
                vector_distance_threshold=0.5,
            )
            e.match("Currently only support 1 RagResource")

    def test_retrieval_query_multiple_rag_resources_config(self):
        with pytest.raises(ValueError) as e:
            rag.retrieval_query(
                rag_resources=[
                    tc.TEST_RAG_RESOURCE,
                    tc.TEST_RAG_RESOURCE,
                ],
                text=tc.TEST_QUERY_TEXT,
                rag_retrieval_config=tc.TEST_RAG_RETRIEVAL_CONFIG,
            )
            e.match("Currently only support 1 RagResource")

    def test_retrieval_query_multiple_rag_resources_similarity_config(self):
        with pytest.raises(ValueError) as e:
            rag.retrieval_query(
                rag_resources=[
                    tc.TEST_RAG_RESOURCE,
                    tc.TEST_RAG_RESOURCE,
                ],
                text=tc.TEST_QUERY_TEXT,
                rag_retrieval_config=tc.TEST_RAG_RETRIEVAL_SIMILARITY_CONFIG,
            )
            e.match("Currently only support 1 RagResource")

    def test_retrieval_query_invalid_config_filter(self):
        with pytest.raises(ValueError) as e:
            rag.retrieval_query(
                rag_resources=[tc.TEST_RAG_RESOURCE],
                text=tc.TEST_QUERY_TEXT,
                rag_retrieval_config=tc.TEST_RAG_RETRIEVAL_ERROR_CONFIG,
            )
            e.match(
                "Only one of vector_distance_threshold or"
                " vector_similarity_threshold can be specified at a time"
                " in rag_retrieval_config."
            )
