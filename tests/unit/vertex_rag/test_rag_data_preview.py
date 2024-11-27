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
from google.api_core import operation as ga_operation
from vertexai.preview import rag
from vertexai.preview.rag.utils._gapic_utils import (
    prepare_import_files_request,
    set_embedding_model_config,
)
from google.cloud.aiplatform_v1beta1 import (
    VertexRagDataServiceAsyncClient,
    VertexRagDataServiceClient,
    ListRagCorporaResponse,
    ListRagFilesResponse,
)
from google.cloud import aiplatform
import mock
from unittest.mock import patch
import pytest
import test_rag_constants_preview


@pytest.fixture
def create_rag_corpus_mock():
    with mock.patch.object(
        VertexRagDataServiceClient,
        "create_rag_corpus",
    ) as create_rag_corpus_mock:
        create_rag_corpus_lro_mock = mock.Mock(ga_operation.Operation)
        create_rag_corpus_lro_mock.done.return_value = True
        create_rag_corpus_lro_mock.result.return_value = (
            test_rag_constants_preview.TEST_GAPIC_RAG_CORPUS
        )
        create_rag_corpus_mock.return_value = create_rag_corpus_lro_mock
        yield create_rag_corpus_mock


@pytest.fixture
def create_rag_corpus_mock_weaviate():
    with mock.patch.object(
        VertexRagDataServiceClient,
        "create_rag_corpus",
    ) as create_rag_corpus_mock_weaviate:
        create_rag_corpus_lro_mock = mock.Mock(ga_operation.Operation)
        create_rag_corpus_lro_mock.done.return_value = True
        create_rag_corpus_lro_mock.result.return_value = (
            test_rag_constants_preview.TEST_GAPIC_RAG_CORPUS_WEAVIATE
        )
        create_rag_corpus_mock_weaviate.return_value = create_rag_corpus_lro_mock
        yield create_rag_corpus_mock_weaviate


@pytest.fixture
def create_rag_corpus_mock_vertex_feature_store():
    with mock.patch.object(
        VertexRagDataServiceClient,
        "create_rag_corpus",
    ) as create_rag_corpus_mock_vertex_feature_store:
        create_rag_corpus_lro_mock = mock.Mock(ga_operation.Operation)
        create_rag_corpus_lro_mock.done.return_value = True
        create_rag_corpus_lro_mock.result.return_value = (
            test_rag_constants_preview.TEST_GAPIC_RAG_CORPUS_VERTEX_FEATURE_STORE
        )
        create_rag_corpus_mock_vertex_feature_store.return_value = (
            create_rag_corpus_lro_mock
        )
        yield create_rag_corpus_mock_vertex_feature_store


@pytest.fixture
def create_rag_corpus_mock_vertex_vector_search():
    with mock.patch.object(
        VertexRagDataServiceClient,
        "create_rag_corpus",
    ) as create_rag_corpus_mock_vertex_vector_search:
        create_rag_corpus_lro_mock = mock.Mock(ga_operation.Operation)
        create_rag_corpus_lro_mock.done.return_value = True
        create_rag_corpus_lro_mock.result.return_value = (
            test_rag_constants_preview.TEST_GAPIC_RAG_CORPUS_VERTEX_VECTOR_SEARCH
        )
        create_rag_corpus_mock_vertex_vector_search.return_value = (
            create_rag_corpus_lro_mock
        )
        yield create_rag_corpus_mock_vertex_vector_search


@pytest.fixture
def create_rag_corpus_mock_pinecone():
    with mock.patch.object(
        VertexRagDataServiceClient,
        "create_rag_corpus",
    ) as create_rag_corpus_mock_pinecone:
        create_rag_corpus_lro_mock = mock.Mock(ga_operation.Operation)
        create_rag_corpus_lro_mock.done.return_value = True
        create_rag_corpus_lro_mock.result.return_value = (
            test_rag_constants_preview.TEST_GAPIC_RAG_CORPUS_PINECONE
        )
        create_rag_corpus_mock_pinecone.return_value = create_rag_corpus_lro_mock
        yield create_rag_corpus_mock_pinecone


@pytest.fixture
def create_rag_corpus_mock_vertex_ai_engine_search_config():
    with mock.patch.object(
        VertexRagDataServiceClient,
        "create_rag_corpus",
    ) as create_rag_corpus_mock_vertex_ai_engine_search_config:
        create_rag_corpus_lro_mock = mock.Mock(ga_operation.Operation)
        create_rag_corpus_lro_mock.done.return_value = True
        create_rag_corpus_lro_mock.result.return_value = (
            test_rag_constants_preview.TEST_GAPIC_RAG_CORPUS_VERTEX_AI_ENGINE_SEARCH_CONFIG
        )
        create_rag_corpus_mock_vertex_ai_engine_search_config.return_value = (
            create_rag_corpus_lro_mock
        )
        yield create_rag_corpus_mock_vertex_ai_engine_search_config


@pytest.fixture
def create_rag_corpus_mock_vertex_ai_datastore_search_config():
    with mock.patch.object(
        VertexRagDataServiceClient,
        "create_rag_corpus",
    ) as create_rag_corpus_mock_vertex_ai_datastore_search_config:
        create_rag_corpus_lro_mock = mock.Mock(ga_operation.Operation)
        create_rag_corpus_lro_mock.done.return_value = True
        create_rag_corpus_lro_mock.result.return_value = (
            test_rag_constants_preview.TEST_GAPIC_RAG_CORPUS_VERTEX_AI_DATASTORE_SEARCH_CONFIG
        )
        create_rag_corpus_mock_vertex_ai_datastore_search_config.return_value = (
            create_rag_corpus_lro_mock
        )
        yield create_rag_corpus_mock_vertex_ai_datastore_search_config


@pytest.fixture
def update_rag_corpus_mock_vertex_ai_engine_search_config():
    with mock.patch.object(
        VertexRagDataServiceClient,
        "update_rag_corpus",
    ) as update_rag_corpus_mock_vertex_ai_engine_search_config:
        update_rag_corpus_lro_mock = mock.Mock(ga_operation.Operation)
        update_rag_corpus_lro_mock.done.return_value = True
        update_rag_corpus_lro_mock.result.return_value = (
            test_rag_constants_preview.TEST_GAPIC_RAG_CORPUS_VERTEX_AI_ENGINE_SEARCH_CONFIG
        )
        update_rag_corpus_mock_vertex_ai_engine_search_config.return_value = (
            update_rag_corpus_lro_mock
        )
        yield update_rag_corpus_mock_vertex_ai_engine_search_config


@pytest.fixture
def update_rag_corpus_mock_weaviate():
    with mock.patch.object(
        VertexRagDataServiceClient,
        "update_rag_corpus",
    ) as update_rag_corpus_mock_weaviate:
        update_rag_corpus_lro_mock = mock.Mock(ga_operation.Operation)
        update_rag_corpus_lro_mock.done.return_value = True
        update_rag_corpus_lro_mock.result.return_value = (
            test_rag_constants_preview.TEST_GAPIC_RAG_CORPUS_WEAVIATE
        )
        update_rag_corpus_mock_weaviate.return_value = update_rag_corpus_lro_mock
        yield update_rag_corpus_mock_weaviate


@pytest.fixture
def update_rag_corpus_mock_vertex_feature_store():
    with mock.patch.object(
        VertexRagDataServiceClient,
        "update_rag_corpus",
    ) as update_rag_corpus_mock_vertex_feature_store:
        update_rag_corpus_lro_mock = mock.Mock(ga_operation.Operation)
        update_rag_corpus_lro_mock.done.return_value = True
        update_rag_corpus_lro_mock.result.return_value = (
            test_rag_constants_preview.TEST_GAPIC_RAG_CORPUS_VERTEX_FEATURE_STORE
        )
        update_rag_corpus_mock_vertex_feature_store.return_value = (
            update_rag_corpus_lro_mock
        )
        yield update_rag_corpus_mock_vertex_feature_store


@pytest.fixture
def update_rag_corpus_mock_vertex_vector_search():
    with mock.patch.object(
        VertexRagDataServiceClient,
        "update_rag_corpus",
    ) as update_rag_corpus_mock_vertex_vector_search:
        update_rag_corpus_lro_mock = mock.Mock(ga_operation.Operation)
        update_rag_corpus_lro_mock.done.return_value = True
        update_rag_corpus_lro_mock.result.return_value = (
            test_rag_constants_preview.TEST_GAPIC_RAG_CORPUS_VERTEX_VECTOR_SEARCH
        )
        update_rag_corpus_mock_vertex_vector_search.return_value = (
            update_rag_corpus_lro_mock
        )
        yield update_rag_corpus_mock_vertex_vector_search


@pytest.fixture
def update_rag_corpus_mock_pinecone():
    with mock.patch.object(
        VertexRagDataServiceClient,
        "update_rag_corpus",
    ) as update_rag_corpus_mock_pinecone:
        update_rag_corpus_lro_mock = mock.Mock(ga_operation.Operation)
        update_rag_corpus_lro_mock.done.return_value = True
        update_rag_corpus_lro_mock.result.return_value = (
            test_rag_constants_preview.TEST_GAPIC_RAG_CORPUS_PINECONE
        )
        update_rag_corpus_mock_pinecone.return_value = update_rag_corpus_lro_mock
        yield update_rag_corpus_mock_pinecone


@pytest.fixture
def list_rag_corpora_pager_mock():
    with mock.patch.object(
        VertexRagDataServiceClient,
        "list_rag_corpora",
    ) as list_rag_corpora_pager_mock:
        list_rag_corpora_pager_mock.return_value = [
            ListRagCorporaResponse(
                rag_corpora=[
                    test_rag_constants_preview.TEST_GAPIC_RAG_CORPUS,
                ],
                next_page_token=test_rag_constants_preview.TEST_PAGE_TOKEN,
            ),
        ]
        yield list_rag_corpora_pager_mock


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


@pytest.fixture
def upload_file_mock(authorized_session_mock):
    with patch.object(authorized_session_mock, "post") as mock_post:
        mock_post.return_value = MockResponse(
            test_rag_constants_preview.TEST_RAG_FILE_JSON, 200
        )
        yield mock_post


@pytest.fixture
def upload_file_not_found_mock(authorized_session_mock):
    with patch.object(authorized_session_mock, "post") as mock_post:
        mock_post.return_value = MockResponse(None, 404)
        yield mock_post


@pytest.fixture
def upload_file_error_mock(authorized_session_mock):
    with patch.object(authorized_session_mock, "post") as mock_post:
        mock_post.return_value = MockResponse(
            test_rag_constants_preview.TEST_RAG_FILE_JSON_ERROR, 200
        )
        yield mock_post


@pytest.fixture
def open_file_mock():
    with mock.patch("builtins.open") as open_file_mock:
        yield open_file_mock


@pytest.fixture
def import_files_mock():
    with mock.patch.object(
        VertexRagDataServiceClient, "import_rag_files"
    ) as import_files_mock:
        import_files_lro_mock = mock.Mock(ga_operation.Operation)
        import_files_lro_mock.result.return_value = (
            test_rag_constants_preview.TEST_IMPORT_RESPONSE
        )
        import_files_mock.return_value = import_files_lro_mock
        yield import_files_mock


@pytest.fixture
def import_files_async_mock():
    with mock.patch.object(
        VertexRagDataServiceAsyncClient, "import_rag_files"
    ) as import_files_async_mock:
        import_files_lro_mock = mock.Mock(ga_operation.Operation)
        import_files_lro_mock.result.return_value = (
            test_rag_constants_preview.TEST_IMPORT_RESPONSE
        )
        import_files_async_mock.return_value = import_files_lro_mock
        yield import_files_async_mock


@pytest.fixture
def list_rag_files_pager_mock():
    with mock.patch.object(
        VertexRagDataServiceClient, "list_rag_files"
    ) as list_rag_files_pager_mock:
        list_rag_files_pager_mock.return_value = [
            ListRagFilesResponse(
                rag_files=[
                    test_rag_constants_preview.TEST_GAPIC_RAG_FILE,
                ],
                next_page_token=test_rag_constants_preview.TEST_PAGE_TOKEN,
            ),
        ]
        yield list_rag_files_pager_mock


def rag_corpus_eq(returned_corpus, expected_corpus):
    assert returned_corpus.name == expected_corpus.name
    assert returned_corpus.display_name == expected_corpus.display_name
    assert returned_corpus.vector_db.__eq__(expected_corpus.vector_db)
    assert returned_corpus.vertex_ai_search_config.__eq__(
        expected_corpus.vertex_ai_search_config
    )


def rag_file_eq(returned_file, expected_file):
    assert returned_file.name == expected_file.name
    assert returned_file.display_name == expected_file.display_name


def import_files_request_eq(returned_request, expected_request):
    assert returned_request.parent == expected_request.parent
    assert (
        returned_request.import_rag_files_config.gcs_source.uris
        == expected_request.import_rag_files_config.gcs_source.uris
    )
    assert (
        returned_request.import_rag_files_config.google_drive_source.resource_ids
        == expected_request.import_rag_files_config.google_drive_source.resource_ids
    )
    assert (
        returned_request.import_rag_files_config.slack_source.channels
        == expected_request.import_rag_files_config.slack_source.channels
    )
    assert (
        returned_request.import_rag_files_config.jira_source.jira_queries
        == expected_request.import_rag_files_config.jira_source.jira_queries
    )
    assert (
        returned_request.import_rag_files_config.rag_file_parsing_config
        == expected_request.import_rag_files_config.rag_file_parsing_config
    )


@pytest.mark.usefixtures("google_auth_mock")
class TestRagDataManagement:
    def setup_method(self):
        importlib.reload(aiplatform.initializer)
        importlib.reload(aiplatform)
        aiplatform.init(
            project=test_rag_constants_preview.TEST_PROJECT,
            location=test_rag_constants_preview.TEST_REGION,
        )

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    @pytest.mark.usefixtures("create_rag_corpus_mock")
    def test_create_corpus_success(self):
        rag_corpus = rag.create_corpus(
            display_name=test_rag_constants_preview.TEST_CORPUS_DISPLAY_NAME,
            embedding_model_config=test_rag_constants_preview.TEST_EMBEDDING_MODEL_CONFIG,
        )

        rag_corpus_eq(rag_corpus, test_rag_constants_preview.TEST_RAG_CORPUS)

    @pytest.mark.usefixtures("create_rag_corpus_mock_weaviate")
    def test_create_corpus_weaviate_success(self):
        rag_corpus = rag.create_corpus(
            display_name=test_rag_constants_preview.TEST_CORPUS_DISPLAY_NAME,
            vector_db=test_rag_constants_preview.TEST_WEAVIATE_CONFIG,
        )

        rag_corpus_eq(rag_corpus, test_rag_constants_preview.TEST_RAG_CORPUS_WEAVIATE)

    @pytest.mark.usefixtures("create_rag_corpus_mock_vertex_feature_store")
    def test_create_corpus_vertex_feature_store_success(self):
        rag_corpus = rag.create_corpus(
            display_name=test_rag_constants_preview.TEST_CORPUS_DISPLAY_NAME,
            vector_db=test_rag_constants_preview.TEST_VERTEX_FEATURE_STORE_CONFIG,
        )

        rag_corpus_eq(
            rag_corpus, test_rag_constants_preview.TEST_RAG_CORPUS_VERTEX_FEATURE_STORE
        )

    @pytest.mark.usefixtures("create_rag_corpus_mock_vertex_vector_search")
    def test_create_corpus_vertex_vector_search_success(self):
        rag_corpus = rag.create_corpus(
            display_name=test_rag_constants_preview.TEST_CORPUS_DISPLAY_NAME,
            vector_db=test_rag_constants_preview.TEST_VERTEX_VECTOR_SEARCH_CONFIG,
        )

        rag_corpus_eq(
            rag_corpus, test_rag_constants_preview.TEST_RAG_CORPUS_VERTEX_VECTOR_SEARCH
        )

    @pytest.mark.usefixtures("create_rag_corpus_mock_pinecone")
    def test_create_corpus_pinecone_success(self):
        rag_corpus = rag.create_corpus(
            display_name=test_rag_constants_preview.TEST_CORPUS_DISPLAY_NAME,
            vector_db=test_rag_constants_preview.TEST_PINECONE_CONFIG,
        )

        rag_corpus_eq(rag_corpus, test_rag_constants_preview.TEST_RAG_CORPUS_PINECONE)

    @pytest.mark.usefixtures("create_rag_corpus_mock_vertex_ai_engine_search_config")
    def test_create_corpus_vais_engine_search_config_success(self):
        rag_corpus = rag.create_corpus(
            display_name=test_rag_constants_preview.TEST_CORPUS_DISPLAY_NAME,
            vertex_ai_search_config=test_rag_constants_preview.TEST_VERTEX_AI_SEARCH_CONFIG_ENGINE,
        )

        rag_corpus_eq(
            rag_corpus,
            test_rag_constants_preview.TEST_RAG_CORPUS_VERTEX_AI_ENGINE_SEARCH_CONFIG,
        )

    @pytest.mark.usefixtures("create_rag_corpus_mock_vertex_ai_datastore_search_config")
    def test_create_corpus_vais_datastore_search_config_success(self):
        rag_corpus = rag.create_corpus(
            display_name=test_rag_constants_preview.TEST_CORPUS_DISPLAY_NAME,
            vertex_ai_search_config=test_rag_constants_preview.TEST_VERTEX_AI_SEARCH_CONFIG_DATASTORE,
        )

        rag_corpus_eq(
            rag_corpus,
            test_rag_constants_preview.TEST_RAG_CORPUS_VERTEX_AI_DATASTORE_SEARCH_CONFIG,
        )

    def test_create_corpus_vais_datastore_search_config_with_vector_db_failure(self):
        with pytest.raises(ValueError) as e:
            rag.create_corpus(
                display_name=test_rag_constants_preview.TEST_CORPUS_DISPLAY_NAME,
                vertex_ai_search_config=test_rag_constants_preview.TEST_VERTEX_AI_SEARCH_CONFIG_DATASTORE,
                vector_db=test_rag_constants_preview.TEST_VERTEX_VECTOR_SEARCH_CONFIG,
            )
        e.match("Only one of vertex_ai_search_config or vector_db can be set.")

    def test_create_corpus_vais_datastore_search_config_with_embedding_model_config_failure(
        self,
    ):
        with pytest.raises(ValueError) as e:
            rag.create_corpus(
                display_name=test_rag_constants_preview.TEST_CORPUS_DISPLAY_NAME,
                vertex_ai_search_config=test_rag_constants_preview.TEST_VERTEX_AI_SEARCH_CONFIG_DATASTORE,
                embedding_model_config=test_rag_constants_preview.TEST_EMBEDDING_MODEL_CONFIG,
            )
        e.match(
            "Only one of vertex_ai_search_config or embedding_model_config can be set."
        )

    def test_set_vertex_ai_search_config_with_invalid_serving_config_failure(self):
        with pytest.raises(ValueError) as e:
            rag.create_corpus(
                display_name=test_rag_constants_preview.TEST_CORPUS_DISPLAY_NAME,
                vertex_ai_search_config=test_rag_constants_preview.TEST_VERTEX_AI_SEARCH_CONFIG_INVALID,
            )
        e.match(
            "serving_config must be of the format `projects/{project}/locations/{location}/collections/{collection}/engines/{engine}/servingConfigs/{serving_config}` or `projects/{project}/locations/{location}/collections/{collection}/dataStores/{data_store}/servingConfigs/{serving_config}`"
        )

    def test_set_vertex_ai_search_config_with_empty_serving_config_failure(self):
        with pytest.raises(ValueError) as e:
            rag.create_corpus(
                display_name=test_rag_constants_preview.TEST_CORPUS_DISPLAY_NAME,
                vertex_ai_search_config=test_rag_constants_preview.TEST_VERTEX_AI_SEARCH_CONFIG_EMPTY,
            )
        e.match("serving_config must be set.")

    @pytest.mark.usefixtures("rag_data_client_preview_mock_exception")
    def test_create_corpus_failure(self):
        with pytest.raises(RuntimeError) as e:
            rag.create_corpus(
                display_name=test_rag_constants_preview.TEST_CORPUS_DISPLAY_NAME
            )
        e.match("Failed in RagCorpus creation due to")

    @pytest.mark.usefixtures("update_rag_corpus_mock_weaviate")
    def test_update_corpus_weaviate_success(self):
        rag_corpus = rag.update_corpus(
            corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
            display_name=test_rag_constants_preview.TEST_CORPUS_DISPLAY_NAME,
            vector_db=test_rag_constants_preview.TEST_WEAVIATE_CONFIG,
        )

        rag_corpus_eq(rag_corpus, test_rag_constants_preview.TEST_RAG_CORPUS_WEAVIATE)

    @pytest.mark.usefixtures("update_rag_corpus_mock_weaviate")
    def test_update_corpus_weaviate_no_display_name_success(self):
        rag_corpus = rag.update_corpus(
            corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
            vector_db=test_rag_constants_preview.TEST_WEAVIATE_CONFIG,
        )

        rag_corpus_eq(rag_corpus, test_rag_constants_preview.TEST_RAG_CORPUS_WEAVIATE)

    @pytest.mark.usefixtures("update_rag_corpus_mock_weaviate")
    def test_update_corpus_weaviate_with_description_success(self):
        rag_corpus = rag.update_corpus(
            corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
            description=test_rag_constants_preview.TEST_CORPUS_DISCRIPTION,
            vector_db=test_rag_constants_preview.TEST_WEAVIATE_CONFIG,
        )

        rag_corpus_eq(rag_corpus, test_rag_constants_preview.TEST_RAG_CORPUS_WEAVIATE)

    @pytest.mark.usefixtures("update_rag_corpus_mock_weaviate")
    def test_update_corpus_weaviate_with_description_and_display_name_success(self):
        rag_corpus = rag.update_corpus(
            corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
            description=test_rag_constants_preview.TEST_CORPUS_DISCRIPTION,
            display_name=test_rag_constants_preview.TEST_CORPUS_DISPLAY_NAME,
            vector_db=test_rag_constants_preview.TEST_WEAVIATE_CONFIG,
        )

        rag_corpus_eq(rag_corpus, test_rag_constants_preview.TEST_RAG_CORPUS_WEAVIATE)

    @pytest.mark.usefixtures("update_rag_corpus_mock_vertex_feature_store")
    def test_update_corpus_vertex_feature_store_success(self):
        rag_corpus = rag.update_corpus(
            corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
            display_name=test_rag_constants_preview.TEST_CORPUS_DISPLAY_NAME,
            vector_db=test_rag_constants_preview.TEST_VERTEX_FEATURE_STORE_CONFIG,
        )

        rag_corpus_eq(
            rag_corpus, test_rag_constants_preview.TEST_RAG_CORPUS_VERTEX_FEATURE_STORE
        )

    @pytest.mark.usefixtures("update_rag_corpus_mock_vertex_vector_search")
    def test_update_corpus_vertex_vector_search_success(self):
        rag_corpus = rag.update_corpus(
            corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
            display_name=test_rag_constants_preview.TEST_CORPUS_DISPLAY_NAME,
            vector_db=test_rag_constants_preview.TEST_VERTEX_VECTOR_SEARCH_CONFIG,
        )
        rag_corpus_eq(
            rag_corpus, test_rag_constants_preview.TEST_RAG_CORPUS_VERTEX_VECTOR_SEARCH
        )

    @pytest.mark.usefixtures("update_rag_corpus_mock_pinecone")
    def test_update_corpus_pinecone_success(self):
        rag_corpus = rag.update_corpus(
            corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
            display_name=test_rag_constants_preview.TEST_CORPUS_DISPLAY_NAME,
            vector_db=test_rag_constants_preview.TEST_PINECONE_CONFIG,
        )
        rag_corpus_eq(rag_corpus, test_rag_constants_preview.TEST_RAG_CORPUS_PINECONE)

    @pytest.mark.usefixtures("rag_data_client_preview_mock_exception")
    def test_update_corpus_failure(self):
        with pytest.raises(RuntimeError) as e:
            rag.update_corpus(
                corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
                display_name=test_rag_constants_preview.TEST_CORPUS_DISPLAY_NAME,
            )
        e.match("Failed in RagCorpus update due to")

    @pytest.mark.usefixtures("update_rag_corpus_mock_vertex_ai_engine_search_config")
    def test_update_corpus_vais_engine_search_config_success(self):
        rag_corpus = rag.update_corpus(
            corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
            display_name=test_rag_constants_preview.TEST_CORPUS_DISPLAY_NAME,
            vertex_ai_search_config=test_rag_constants_preview.TEST_VERTEX_AI_SEARCH_CONFIG_ENGINE,
        )

        rag_corpus_eq(
            rag_corpus,
            test_rag_constants_preview.TEST_RAG_CORPUS_VERTEX_AI_ENGINE_SEARCH_CONFIG,
        )

    def test_update_corpus_vais_datastore_search_config_with_vector_db_failure(self):
        with pytest.raises(ValueError) as e:
            rag.update_corpus(
                corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
                display_name=test_rag_constants_preview.TEST_CORPUS_DISPLAY_NAME,
                vertex_ai_search_config=test_rag_constants_preview.TEST_VERTEX_AI_SEARCH_CONFIG_DATASTORE,
                vector_db=test_rag_constants_preview.TEST_VERTEX_VECTOR_SEARCH_CONFIG,
            )
        e.match("Only one of vertex_ai_search_config or vector_db can be set.")

    @pytest.mark.usefixtures("rag_data_client_preview_mock")
    def test_get_corpus_success(self):
        rag_corpus = rag.get_corpus(
            test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME
        )
        rag_corpus_eq(rag_corpus, test_rag_constants_preview.TEST_RAG_CORPUS)

    @pytest.mark.usefixtures("rag_data_client_preview_mock")
    def test_get_corpus_id_success(self):
        rag_corpus = rag.get_corpus(test_rag_constants_preview.TEST_RAG_CORPUS_ID)
        rag_corpus_eq(rag_corpus, test_rag_constants_preview.TEST_RAG_CORPUS)

    @pytest.mark.usefixtures("rag_data_client_preview_mock_exception")
    def test_get_corpus_failure(self):
        with pytest.raises(RuntimeError) as e:
            rag.get_corpus(test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME)
        e.match("Failed in getting the RagCorpus due to")

    def test_list_corpora_pager_success(self, list_rag_corpora_pager_mock):
        aiplatform.init(
            project=test_rag_constants_preview.TEST_PROJECT,
            location=test_rag_constants_preview.TEST_REGION,
        )
        pager = rag.list_corpora(page_size=1)

        list_rag_corpora_pager_mock.assert_called_once()
        assert pager[0].next_page_token == test_rag_constants_preview.TEST_PAGE_TOKEN

    @pytest.mark.usefixtures("rag_data_client_preview_mock_exception")
    def test_list_corpora_failure(self):
        with pytest.raises(RuntimeError) as e:
            rag.list_corpora()
        e.match("Failed in listing the RagCorpora due to")

    def test_delete_corpus_success(self, rag_data_client_preview_mock):
        rag.delete_corpus(test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME)
        assert rag_data_client_preview_mock.call_count == 2

    def test_delete_corpus_id_success(self, rag_data_client_preview_mock):
        rag.delete_corpus(test_rag_constants_preview.TEST_RAG_CORPUS_ID)
        assert rag_data_client_preview_mock.call_count == 2

    @pytest.mark.usefixtures("rag_data_client_preview_mock_exception")
    def test_delete_corpus_failure(self):
        with pytest.raises(RuntimeError) as e:
            rag.delete_corpus(test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME)
        e.match("Failed in RagCorpus deletion due to")

    @pytest.mark.usefixtures("open_file_mock")
    def test_upload_file_success(
        self,
        upload_file_mock,
    ):
        aiplatform.init(
            project=test_rag_constants_preview.TEST_PROJECT,
            location=test_rag_constants_preview.TEST_REGION,
        )
        rag_file = rag.upload_file(
            corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
            path=test_rag_constants_preview.TEST_PATH,
            display_name=test_rag_constants_preview.TEST_FILE_DISPLAY_NAME,
        )

        upload_file_mock.assert_called_once()
        _, mock_kwargs = upload_file_mock.call_args
        assert mock_kwargs["url"] == test_rag_constants_preview.TEST_UPLOAD_REQUEST_URI
        assert mock_kwargs["headers"] == test_rag_constants_preview.TEST_HEADERS

        rag_file_eq(rag_file, test_rag_constants_preview.TEST_RAG_FILE)

    @pytest.mark.usefixtures("rag_data_client_mock_exception", "open_file_mock")
    def test_upload_file_failure(self):
        with pytest.raises(RuntimeError) as e:
            rag.upload_file(
                corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
                path=test_rag_constants_preview.TEST_PATH,
                display_name=test_rag_constants_preview.TEST_FILE_DISPLAY_NAME,
            )
        e.match("Failed in uploading the RagFile due to")

    @pytest.mark.usefixtures("open_file_mock", "upload_file_not_found_mock")
    def test_upload_file_not_found(self):
        with pytest.raises(ValueError) as e:
            rag.upload_file(
                corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
                path=test_rag_constants_preview.TEST_PATH,
                display_name=test_rag_constants_preview.TEST_FILE_DISPLAY_NAME,
            )
        e.match("is not found")

    @pytest.mark.usefixtures("open_file_mock", "upload_file_error_mock")
    def test_upload_file_error(self):
        with pytest.raises(RuntimeError) as e:
            rag.upload_file(
                corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
                path=test_rag_constants_preview.TEST_PATH,
                display_name=test_rag_constants_preview.TEST_FILE_DISPLAY_NAME,
            )
        e.match("Failed in indexing the RagFile due to")

    def test_import_files(self, import_files_mock):
        response = rag.import_files(
            corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
            paths=[test_rag_constants_preview.TEST_GCS_PATH],
        )
        import_files_mock.assert_called_once()

        assert response.imported_rag_files_count == 2

    @pytest.mark.usefixtures("rag_data_client_preview_mock_exception")
    def test_import_files_failure(self):
        with pytest.raises(RuntimeError) as e:
            rag.import_files(
                corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
                paths=[test_rag_constants_preview.TEST_GCS_PATH],
            )
        e.match("Failed in importing the RagFiles due to")

    @pytest.mark.asyncio
    async def test_import_files_async(self, import_files_async_mock):
        response = await rag.import_files_async(
            corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
            paths=[test_rag_constants_preview.TEST_GCS_PATH],
        )
        import_files_async_mock.assert_called_once()

        assert response.result().imported_rag_files_count == 2

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("rag_data_async_client_preview_mock_exception")
    async def test_import_files_async_failure(self):
        with pytest.raises(RuntimeError) as e:
            await rag.import_files_async(
                corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
                paths=[test_rag_constants_preview.TEST_GCS_PATH],
            )
        e.match("Failed in importing the RagFiles due to")

    @pytest.mark.usefixtures("rag_data_client_preview_mock")
    def test_get_file_success(self):
        rag_file = rag.get_file(test_rag_constants_preview.TEST_RAG_FILE_RESOURCE_NAME)
        rag_file_eq(rag_file, test_rag_constants_preview.TEST_RAG_FILE)

    @pytest.mark.usefixtures("rag_data_client_preview_mock")
    def test_get_file_id_success(self):
        rag_file = rag.get_file(
            name=test_rag_constants_preview.TEST_RAG_FILE_ID,
            corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_ID,
        )
        rag_file_eq(rag_file, test_rag_constants_preview.TEST_RAG_FILE)

    @pytest.mark.usefixtures("rag_data_client_preview_mock_exception")
    def test_get_file_failure(self):
        with pytest.raises(RuntimeError) as e:
            rag.get_file(test_rag_constants_preview.TEST_RAG_FILE_RESOURCE_NAME)
        e.match("Failed in getting the RagFile due to")

    def test_list_files_pager_success(self, list_rag_files_pager_mock):
        files = rag.list_files(
            corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
            page_size=1,
        )
        list_rag_files_pager_mock.assert_called_once()
        assert files[0].next_page_token == test_rag_constants_preview.TEST_PAGE_TOKEN

    @pytest.mark.usefixtures("rag_data_client_preview_mock_exception")
    def test_list_files_failure(self):
        with pytest.raises(RuntimeError) as e:
            rag.list_files(
                corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME
            )
        e.match("Failed in listing the RagFiles due to")

    def test_delete_file_success(self, rag_data_client_preview_mock):
        rag.delete_file(test_rag_constants_preview.TEST_RAG_FILE_RESOURCE_NAME)
        assert rag_data_client_preview_mock.call_count == 2

    def test_delete_file_id_success(self, rag_data_client_preview_mock):
        rag.delete_file(
            name=test_rag_constants_preview.TEST_RAG_FILE_ID,
            corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_ID,
        )
        # Passing corpus_name will result in 3 calls to rag_data_client
        assert rag_data_client_preview_mock.call_count == 3

    @pytest.mark.usefixtures("rag_data_client_preview_mock_exception")
    def test_delete_file_failure(self):
        with pytest.raises(RuntimeError) as e:
            rag.delete_file(test_rag_constants_preview.TEST_RAG_FILE_RESOURCE_NAME)
        e.match("Failed in RagFile deletion due to")

    def test_prepare_import_files_request_list_gcs_uris(self):
        paths = [test_rag_constants_preview.TEST_GCS_PATH]
        request = prepare_import_files_request(
            corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
            paths=paths,
            chunk_size=test_rag_constants_preview.TEST_CHUNK_SIZE,
            chunk_overlap=test_rag_constants_preview.TEST_CHUNK_OVERLAP,
        )
        import_files_request_eq(
            request, test_rag_constants_preview.TEST_IMPORT_REQUEST_GCS
        )

    @pytest.mark.parametrize(
        "path",
        [
            test_rag_constants_preview.TEST_DRIVE_FOLDER,
            test_rag_constants_preview.TEST_DRIVE_FOLDER_2,
        ],
    )
    def test_prepare_import_files_request_drive_folders(self, path):
        request = prepare_import_files_request(
            corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
            paths=[path],
            chunk_size=test_rag_constants_preview.TEST_CHUNK_SIZE,
            chunk_overlap=test_rag_constants_preview.TEST_CHUNK_OVERLAP,
        )
        import_files_request_eq(
            request, test_rag_constants_preview.TEST_IMPORT_REQUEST_DRIVE_FOLDER
        )

    @pytest.mark.parametrize(
        "path",
        [
            test_rag_constants_preview.TEST_DRIVE_FOLDER,
            test_rag_constants_preview.TEST_DRIVE_FOLDER_2,
        ],
    )
    def test_prepare_import_files_request_drive_folders_with_pdf_parsing(self, path):
        request = prepare_import_files_request(
            corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
            paths=[path],
            chunk_size=test_rag_constants_preview.TEST_CHUNK_SIZE,
            chunk_overlap=test_rag_constants_preview.TEST_CHUNK_OVERLAP,
            use_advanced_pdf_parsing=True,
        )
        import_files_request_eq(
            request, test_rag_constants_preview.TEST_IMPORT_REQUEST_DRIVE_FOLDER_PARSING
        )

    def test_prepare_import_files_request_drive_files(self):
        paths = [test_rag_constants_preview.TEST_DRIVE_FILE]
        request = prepare_import_files_request(
            corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
            paths=paths,
            chunk_size=test_rag_constants_preview.TEST_CHUNK_SIZE,
            chunk_overlap=test_rag_constants_preview.TEST_CHUNK_OVERLAP,
            max_embedding_requests_per_min=800,
        )
        import_files_request_eq(
            request, test_rag_constants_preview.TEST_IMPORT_REQUEST_DRIVE_FILE
        )

    def test_prepare_import_files_request_invalid_drive_path(self):
        with pytest.raises(ValueError) as e:
            paths = ["https://drive.google.com/bslalsdfk/whichever_file/456"]
            prepare_import_files_request(
                corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
                paths=paths,
                chunk_size=test_rag_constants_preview.TEST_CHUNK_SIZE,
                chunk_overlap=test_rag_constants_preview.TEST_CHUNK_OVERLAP,
            )
        e.match("is not a valid Google Drive url")

    def test_prepare_import_files_request_invalid_path(self):
        with pytest.raises(ValueError) as e:
            paths = ["https://whereever.com/whichever_file/456"]
            prepare_import_files_request(
                corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
                paths=paths,
                chunk_size=test_rag_constants_preview.TEST_CHUNK_SIZE,
                chunk_overlap=test_rag_constants_preview.TEST_CHUNK_OVERLAP,
            )
        e.match("path must be a Google Cloud Storage uri or a Google Drive url")

    def test_prepare_import_files_request_slack_source(self):
        request = prepare_import_files_request(
            corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
            source=test_rag_constants_preview.TEST_SLACK_SOURCE,
            chunk_size=test_rag_constants_preview.TEST_CHUNK_SIZE,
            chunk_overlap=test_rag_constants_preview.TEST_CHUNK_OVERLAP,
        )
        import_files_request_eq(
            request, test_rag_constants_preview.TEST_IMPORT_REQUEST_SLACK_SOURCE
        )

    def test_prepare_import_files_request_jira_source(self):
        request = prepare_import_files_request(
            corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
            source=test_rag_constants_preview.TEST_JIRA_SOURCE,
            chunk_size=test_rag_constants_preview.TEST_CHUNK_SIZE,
            chunk_overlap=test_rag_constants_preview.TEST_CHUNK_OVERLAP,
        )
        import_files_request_eq(
            request, test_rag_constants_preview.TEST_IMPORT_REQUEST_JIRA_SOURCE
        )

    def test_prepare_import_files_request_sharepoint_source(self):
        request = prepare_import_files_request(
            corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
            source=test_rag_constants_preview.TEST_SHARE_POINT_SOURCE,
            chunk_size=test_rag_constants_preview.TEST_CHUNK_SIZE,
            chunk_overlap=test_rag_constants_preview.TEST_CHUNK_OVERLAP,
        )
        import_files_request_eq(
            request, test_rag_constants_preview.TEST_IMPORT_REQUEST_SHARE_POINT_SOURCE
        )

    def test_prepare_import_files_request_sharepoint_source_2_drives(self):
        with pytest.raises(ValueError) as e:
            prepare_import_files_request(
                corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
                source=test_rag_constants_preview.TEST_SHARE_POINT_SOURCE_2_DRIVES,
                chunk_size=test_rag_constants_preview.TEST_CHUNK_SIZE,
                chunk_overlap=test_rag_constants_preview.TEST_CHUNK_OVERLAP,
            )
        e.match("drive_name and drive_id cannot both be set.")

    def test_prepare_import_files_request_sharepoint_source_2_folders(self):
        with pytest.raises(ValueError) as e:
            prepare_import_files_request(
                corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
                source=test_rag_constants_preview.TEST_SHARE_POINT_SOURCE_2_FOLDERS,
                chunk_size=test_rag_constants_preview.TEST_CHUNK_SIZE,
                chunk_overlap=test_rag_constants_preview.TEST_CHUNK_OVERLAP,
            )
        e.match("sharepoint_folder_path and sharepoint_folder_id cannot both be set.")

    def test_prepare_import_files_request_sharepoint_source_no_drives(self):
        with pytest.raises(ValueError) as e:
            prepare_import_files_request(
                corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
                source=test_rag_constants_preview.TEST_SHARE_POINT_SOURCE_NO_DRIVES,
                chunk_size=test_rag_constants_preview.TEST_CHUNK_SIZE,
                chunk_overlap=test_rag_constants_preview.TEST_CHUNK_OVERLAP,
            )
        e.match("Either drive_name and drive_id must be set.")

    def test_prepare_import_files_request_sharepoint_source_no_folders(self):
        request = prepare_import_files_request(
            corpus_name=test_rag_constants_preview.TEST_RAG_CORPUS_RESOURCE_NAME,
            source=test_rag_constants_preview.TEST_SHARE_POINT_SOURCE_NO_FOLDERS,
            chunk_size=test_rag_constants_preview.TEST_CHUNK_SIZE,
            chunk_overlap=test_rag_constants_preview.TEST_CHUNK_OVERLAP,
        )
        import_files_request_eq(
            request,
            test_rag_constants_preview.TEST_IMPORT_REQUEST_SHARE_POINT_SOURCE_NO_FOLDERS,
        )

    def test_set_embedding_model_config_set_both_error(self):
        embedding_model_config = rag.EmbeddingModelConfig(
            publisher_model="whatever",
            endpoint="whatever",
        )
        with pytest.raises(ValueError) as e:
            set_embedding_model_config(
                embedding_model_config,
                test_rag_constants_preview.TEST_GAPIC_RAG_CORPUS,
            )
        e.match("publisher_model and endpoint cannot be set at the same time")

    def test_set_embedding_model_config_not_set_error(self):
        embedding_model_config = rag.EmbeddingModelConfig()
        with pytest.raises(ValueError) as e:
            set_embedding_model_config(
                embedding_model_config,
                test_rag_constants_preview.TEST_GAPIC_RAG_CORPUS,
            )
        e.match("At least one of publisher_model and endpoint must be set")

    def test_set_embedding_model_config_wrong_publisher_model_format_error(self):
        embedding_model_config = rag.EmbeddingModelConfig(publisher_model="whatever")
        with pytest.raises(ValueError) as e:
            set_embedding_model_config(
                embedding_model_config,
                test_rag_constants_preview.TEST_GAPIC_RAG_CORPUS,
            )
        e.match("publisher_model must be of the format ")

    def test_set_embedding_model_config_wrong_endpoint_format_error(self):
        embedding_model_config = rag.EmbeddingModelConfig(endpoint="whatever")
        with pytest.raises(ValueError) as e:
            set_embedding_model_config(
                embedding_model_config,
                test_rag_constants_preview.TEST_GAPIC_RAG_CORPUS,
            )
        e.match("endpoint must be of the format ")