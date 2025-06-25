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


from google.cloud import aiplatform
from google.cloud.aiplatform_v1beta1 import (
    GoogleDriveSource,
    ImportRagFilesConfig,
    ImportRagFilesRequest,
    ImportRagFilesResponse,
    JiraSource as GapicJiraSource,
    RagContexts,
    RagCorpus as GapicRagCorpus,
    RagEngineConfig as GapicRagEngineConfig,
    RagFileChunkingConfig,
    RagFileParsingConfig,
    RagFileTransformationConfig,
    RagFile as GapicRagFile,
    RagManagedDbConfig as GapicRagManagedDbConfig,
    RagVectorDbConfig as GapicRagVectorDbConfig,
    RetrieveContextsResponse,
    SharePointSources as GapicSharePointSources,
    SlackSource as GapicSlackSource,
    VertexAiSearchConfig as GapicVertexAiSearchConfig,
)
from google.cloud.aiplatform_v1beta1.types import api_auth
from google.cloud.aiplatform_v1beta1.types import EncryptionSpec
from vertexai.preview.rag import (
    ANN,
    Basic,
    DocumentCorpus,
    EmbeddingModelConfig,
    Enterprise,
    Filter,
    HybridSearch,
    JiraQuery,
    JiraSource,
    KNN,
    LayoutParserConfig,
    LlmParserConfig,
    LlmRanker,
    MemoryCorpus,
    Pinecone,
    RagCorpus,
    RagCorpusTypeConfig,
    RagEmbeddingModelConfig,
    RagEngineConfig,
    RagFile,
    RagManagedDb,
    RagManagedDbConfig,
    RagResource,
    RagRetrievalConfig,
    RagVectorDbConfig,
    RankService,
    Ranking,
    Scaled,
    SharePointSource,
    SharePointSources,
    SlackChannel,
    SlackChannelsSource,
    Unprovisioned,
    VertexAiSearchConfig,
    VertexFeatureStore,
    VertexPredictionEndpoint,
    VertexVectorSearch,
    Weaviate,
)
from google.protobuf import timestamp_pb2


TEST_PROJECT = "test-project"
TEST_PROJECT_NUMBER = "12345678"
TEST_REGION = "us-central1"
TEST_CORPUS_DISPLAY_NAME = "my-corpus-1"
TEST_CORPUS_DISCRIPTION = "My first corpus."
TEST_RAG_CORPUS_ID = "generate-123"
TEST_API_ENDPOINT = "us-central1-" + aiplatform.constants.base.API_BASE_PATH
TEST_RAG_CORPUS_RESOURCE_NAME = f"projects/{TEST_PROJECT_NUMBER}/locations/{TEST_REGION}/ragCorpora/{TEST_RAG_CORPUS_ID}"

# RagCorpus
TEST_WEAVIATE_HTTP_ENDPOINT = "test.weaviate.com"
TEST_WEAVIATE_COLLECTION_NAME = "test-collection"
TEST_WEAVIATE_API_KEY_SECRET_VERSION = (
    "projects/test-project/secrets/test-secret/versions/1"
)
TEST_ENCRYPTION_SPEC = EncryptionSpec(
    kms_key_name="projects/test-project/locations/us-central1/keyRings/test-key-ring/cryptoKeys/test-key"
)
TEST_WEAVIATE_CONFIG = Weaviate(
    weaviate_http_endpoint=TEST_WEAVIATE_HTTP_ENDPOINT,
    collection_name=TEST_WEAVIATE_COLLECTION_NAME,
    api_key=TEST_WEAVIATE_API_KEY_SECRET_VERSION,
)
TEST_PINECONE_INDEX_NAME = "test-pinecone-index"
TEST_PINECONE_API_KEY_SECRET_VERSION = (
    "projects/test-project/secrets/test-secret/versions/1"
)
TEST_PINECONE_CONFIG = Pinecone(
    index_name=TEST_PINECONE_INDEX_NAME,
    api_key=TEST_PINECONE_API_KEY_SECRET_VERSION,
)
TEST_RAG_MANAGED_DB_ANN_TREE_DEPTH = 3
TEST_RAG_MANAGED_DB_ANN_LEAF_COUNT = 100
TEST_RAG_MANAGED_DB_CONFIG = RagManagedDb()
TEST_RAG_MANAGED_DB_KNN_CONFIG = RagManagedDb(
    retrieval_strategy=KNN(),
)
TEST_RAG_MANAGED_DB_ANN_CONFIG = RagManagedDb(
    retrieval_strategy=ANN(
        tree_depth=TEST_RAG_MANAGED_DB_ANN_TREE_DEPTH,
        leaf_count=TEST_RAG_MANAGED_DB_ANN_LEAF_COUNT,
    ),
)
TEST_VERTEX_VECTOR_SEARCH_INDEX_ENDPOINT = "test-vector-search-index-endpoint"
TEST_VERTEX_VECTOR_SEARCH_INDEX = "test-vector-search-index"
TEST_VERTEX_VECTOR_SEARCH_CONFIG = VertexVectorSearch(
    index_endpoint=TEST_VERTEX_VECTOR_SEARCH_INDEX_ENDPOINT,
    index=TEST_VERTEX_VECTOR_SEARCH_INDEX,
)
TEST_VERTEX_FEATURE_STORE_RESOURCE_NAME = "test-feature-view-resource-name"
TEST_GAPIC_RAG_CORPUS = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
)
TEST_GAPIC_RAG_CORPUS.rag_embedding_model_config.vertex_prediction_endpoint.endpoint = (
    "projects/{}/locations/{}/publishers/google/models/textembedding-gecko".format(
        TEST_PROJECT, TEST_REGION
    )
)
TEST_GAPIC_CMEK_RAG_CORPUS = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    encryption_spec=EncryptionSpec(
        kms_key_name="projects/test-project/locations/us-central1/keyRings/test-key-ring/cryptoKeys/test-key"
    ),
)
TEST_GAPIC_RAG_CORPUS_WEAVIATE = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    rag_vector_db_config=GapicRagVectorDbConfig(
        weaviate=GapicRagVectorDbConfig.Weaviate(
            http_endpoint=TEST_WEAVIATE_HTTP_ENDPOINT,
            collection_name=TEST_WEAVIATE_COLLECTION_NAME,
        ),
        api_auth=api_auth.ApiAuth(
            api_key_config=api_auth.ApiAuth.ApiKeyConfig(
                api_key_secret_version=TEST_WEAVIATE_API_KEY_SECRET_VERSION
            ),
        ),
    ),
)
TEST_GAPIC_RAG_CORPUS_VERTEX_FEATURE_STORE = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    rag_vector_db_config=GapicRagVectorDbConfig(
        vertex_feature_store=GapicRagVectorDbConfig.VertexFeatureStore(
            feature_view_resource_name=TEST_VERTEX_FEATURE_STORE_RESOURCE_NAME
        ),
    ),
)
TEST_GAPIC_RAG_CORPUS_VERTEX_VECTOR_SEARCH = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    rag_vector_db_config=GapicRagVectorDbConfig(
        vertex_vector_search=GapicRagVectorDbConfig.VertexVectorSearch(
            index_endpoint=TEST_VERTEX_VECTOR_SEARCH_INDEX_ENDPOINT,
            index=TEST_VERTEX_VECTOR_SEARCH_INDEX,
        ),
    ),
)
TEST_GAPIC_RAG_CORPUS_PINECONE = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    rag_vector_db_config=GapicRagVectorDbConfig(
        pinecone=GapicRagVectorDbConfig.Pinecone(index_name=TEST_PINECONE_INDEX_NAME),
        api_auth=api_auth.ApiAuth(
            api_key_config=api_auth.ApiAuth.ApiKeyConfig(
                api_key_secret_version=TEST_PINECONE_API_KEY_SECRET_VERSION
            ),
        ),
    ),
)
TEST_GAPIC_RAG_CORPUS_RAG_MANAGED_DB = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    rag_vector_db_config=GapicRagVectorDbConfig(
        rag_managed_db=GapicRagVectorDbConfig.RagManagedDb()
    ),
)
TEST_GAPIC_RAG_CORPUS_RAG_MANAGED_DB_KNN = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    rag_vector_db_config=GapicRagVectorDbConfig(
        rag_managed_db=GapicRagVectorDbConfig.RagManagedDb(
            knn=GapicRagVectorDbConfig.RagManagedDb.KNN()
        )
    ),
)
TEST_GAPIC_RAG_CORPUS_RAG_MANAGED_DB_ANN = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    rag_vector_db_config=GapicRagVectorDbConfig(
        rag_managed_db=GapicRagVectorDbConfig.RagManagedDb(
            ann=GapicRagVectorDbConfig.RagManagedDb.ANN(
                tree_depth=TEST_RAG_MANAGED_DB_ANN_TREE_DEPTH,
                leaf_count=TEST_RAG_MANAGED_DB_ANN_LEAF_COUNT,
            )
        )
    ),
)

TEST_EMBEDDING_MODEL_CONFIG = EmbeddingModelConfig(
    publisher_model="publishers/google/models/textembedding-gecko",
)
TEST_RAG_EMBEDDING_MODEL_CONFIG = RagEmbeddingModelConfig(
    vertex_prediction_endpoint=VertexPredictionEndpoint(
        publisher_model="projects/{}/locations/{}/publishers/google/models/textembedding-gecko".format(
            TEST_PROJECT, TEST_REGION
        ),
    ),
)
TEST_BACKEND_CONFIG_EMBEDDING_MODEL_CONFIG = RagVectorDbConfig(
    rag_embedding_model_config=TEST_RAG_EMBEDDING_MODEL_CONFIG,
)
TEST_VERTEX_FEATURE_STORE_CONFIG = VertexFeatureStore(
    resource_name=TEST_VERTEX_FEATURE_STORE_RESOURCE_NAME,
)
TEST_RAG_CORPUS = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    embedding_model_config=TEST_EMBEDDING_MODEL_CONFIG,
)
TEST_CMEK_RAG_CORPUS = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    encryption_spec=EncryptionSpec(
        kms_key_name="projects/test-project/locations/us-central1/keyRings/test-key-ring/cryptoKeys/test-key"
    ),
)
TEST_RAG_CORPUS_WEAVIATE = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    vector_db=TEST_WEAVIATE_CONFIG,
)
TEST_RAG_CORPUS_VERTEX_FEATURE_STORE = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    vector_db=TEST_VERTEX_FEATURE_STORE_CONFIG,
)
TEST_RAG_CORPUS_PINECONE = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    vector_db=TEST_PINECONE_CONFIG,
)
TEST_RAG_CORPUS_RAG_MANAGED_DB = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    vector_db=TEST_RAG_MANAGED_DB_CONFIG,
)
TEST_RAG_CORPUS_RAG_MANAGED_DB_KNN = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    vector_db=TEST_RAG_MANAGED_DB_KNN_CONFIG,
)
TEST_RAG_CORPUS_RAG_MANAGED_DB_ANN = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    vector_db=TEST_RAG_MANAGED_DB_ANN_CONFIG,
)
TEST_RAG_CORPUS_VERTEX_VECTOR_SEARCH = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    vector_db=TEST_VERTEX_VECTOR_SEARCH_CONFIG,
)
TEST_PAGE_TOKEN = "test-page-token"
# Backend Config
TEST_GAPIC_RAG_CORPUS_BACKEND_CONFIG = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
)
TEST_GAPIC_RAG_CORPUS_BACKEND_CONFIG.vector_db_config.rag_embedding_model_config.vertex_prediction_endpoint.endpoint = "projects/{}/locations/{}/publishers/google/models/textembedding-gecko".format(
    TEST_PROJECT, TEST_REGION
)
TEST_GAPIC_RAG_CORPUS_VERTEX_VECTOR_SEARCH_BACKEND_CONFIG = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    vector_db_config=GapicRagVectorDbConfig(
        vertex_vector_search=GapicRagVectorDbConfig.VertexVectorSearch(
            index_endpoint=TEST_VERTEX_VECTOR_SEARCH_INDEX_ENDPOINT,
            index=TEST_VERTEX_VECTOR_SEARCH_INDEX,
        ),
    ),
)
TEST_GAPIC_RAG_CORPUS_PINECONE_BACKEND_CONFIG = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    vector_db_config=GapicRagVectorDbConfig(
        pinecone=GapicRagVectorDbConfig.Pinecone(index_name=TEST_PINECONE_INDEX_NAME),
        api_auth=api_auth.ApiAuth(
            api_key_config=api_auth.ApiAuth.ApiKeyConfig(
                api_key_secret_version=TEST_PINECONE_API_KEY_SECRET_VERSION
            ),
        ),
    ),
)
TEST_GAPIC_RAG_CORPUS_RAG_MANAGED_DB_BACKEND_CONFIG = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    vector_db_config=GapicRagVectorDbConfig(
        rag_managed_db=GapicRagVectorDbConfig.RagManagedDb()
    ),
)
TEST_GAPIC_RAG_CORPUS_RAG_MANAGED_DB_KNN_BACKEND_CONFIG = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    vector_db_config=GapicRagVectorDbConfig(
        rag_managed_db=GapicRagVectorDbConfig.RagManagedDb(
            knn=GapicRagVectorDbConfig.RagManagedDb.KNN()
        )
    ),
)
TEST_GAPIC_RAG_CORPUS_RAG_MANAGED_DB_ANN_BACKEND_CONFIG = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    vector_db_config=GapicRagVectorDbConfig(
        rag_managed_db=GapicRagVectorDbConfig.RagManagedDb(
            ann=GapicRagVectorDbConfig.RagManagedDb.ANN(
                tree_depth=TEST_RAG_MANAGED_DB_ANN_TREE_DEPTH,
                leaf_count=TEST_RAG_MANAGED_DB_ANN_LEAF_COUNT,
            )
        )
    ),
)
TEST_RAG_CORPUS_BACKEND = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    backend_config=TEST_BACKEND_CONFIG_EMBEDDING_MODEL_CONFIG,
)
TEST_BACKEND_CONFIG_PINECONE_CONFIG = RagVectorDbConfig(
    vector_db=TEST_PINECONE_CONFIG,
)
TEST_BACKEND_CONFIG_RAG_MANAGED_DB_CONFIG = RagVectorDbConfig(
    vector_db=TEST_RAG_MANAGED_DB_CONFIG,
)
TEST_BACKEND_CONFIG_RAG_MANAGED_DB_KNN_CONFIG = RagVectorDbConfig(
    vector_db=TEST_RAG_MANAGED_DB_KNN_CONFIG,
)
TEST_BACKEND_CONFIG_RAG_MANAGED_DB_ANN_CONFIG = RagVectorDbConfig(
    vector_db=TEST_RAG_MANAGED_DB_ANN_CONFIG,
)
TEST_RAG_CORPUS_PINECONE_BACKEND = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    backend_config=TEST_BACKEND_CONFIG_PINECONE_CONFIG,
)
TEST_RAG_CORPUS_RAG_MANAGED_DB_BACKEND = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    backend_config=TEST_BACKEND_CONFIG_RAG_MANAGED_DB_CONFIG,
)
TEST_RAG_CORPUS_RAG_MANAGED_DB_KNN_BACKEND = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    backend_config=TEST_BACKEND_CONFIG_RAG_MANAGED_DB_KNN_CONFIG,
)
TEST_RAG_CORPUS_RAG_MANAGED_DB_ANN_BACKEND = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    backend_config=TEST_BACKEND_CONFIG_RAG_MANAGED_DB_ANN_CONFIG,
)
TEST_BACKEND_CONFIG_VERTEX_VECTOR_SEARCH_CONFIG = RagVectorDbConfig(
    vector_db=TEST_VERTEX_VECTOR_SEARCH_CONFIG,
)
TEST_RAG_CORPUS_VERTEX_VECTOR_SEARCH_BACKEND = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    backend_config=TEST_BACKEND_CONFIG_VERTEX_VECTOR_SEARCH_CONFIG,
)
# Vertex AI Search Config
TEST_VERTEX_AI_SEARCH_ENGINE_SERVING_CONFIG = f"projects/{TEST_PROJECT_NUMBER}/locations/{TEST_REGION}/collections/test-collection/engines/test-engine/servingConfigs/test-serving-config"
TEST_VERTEX_AI_SEARCH_DATASTORE_SERVING_CONFIG = f"projects/{TEST_PROJECT_NUMBER}/locations/{TEST_REGION}/collections/test-collection/dataStores/test-datastore/servingConfigs/test-serving-config"
TEST_GAPIC_RAG_CORPUS_VERTEX_AI_ENGINE_SEARCH_CONFIG = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    vertex_ai_search_config=GapicVertexAiSearchConfig(
        serving_config=TEST_VERTEX_AI_SEARCH_ENGINE_SERVING_CONFIG,
    ),
)
TEST_GAPIC_RAG_CORPUS_VERTEX_AI_DATASTORE_SEARCH_CONFIG = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    vertex_ai_search_config=GapicVertexAiSearchConfig(
        serving_config=TEST_VERTEX_AI_SEARCH_DATASTORE_SERVING_CONFIG,
    ),
)
TEST_VERTEX_AI_SEARCH_CONFIG_ENGINE = VertexAiSearchConfig(
    serving_config=TEST_VERTEX_AI_SEARCH_ENGINE_SERVING_CONFIG,
)
TEST_VERTEX_AI_SEARCH_CONFIG_DATASTORE = VertexAiSearchConfig(
    serving_config=TEST_VERTEX_AI_SEARCH_DATASTORE_SERVING_CONFIG,
)
TEST_VERTEX_AI_SEARCH_CONFIG_INVALID = VertexAiSearchConfig(
    serving_config="invalid-serving-config",
)
TEST_VERTEX_AI_SEARCH_CONFIG_EMPTY = VertexAiSearchConfig()

TEST_RAG_CORPUS_VERTEX_AI_ENGINE_SEARCH_CONFIG = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    vertex_ai_search_config=TEST_VERTEX_AI_SEARCH_CONFIG_ENGINE,
)
TEST_RAG_CORPUS_VERTEX_AI_DATASTORE_SEARCH_CONFIG = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    vertex_ai_search_config=TEST_VERTEX_AI_SEARCH_CONFIG_DATASTORE,
)

# RagFiles
TEST_PATH = "usr/home/my_file.txt"
TEST_GCS_PATH = "gs://usr/home/data_dir/"
TEST_FILE_DISPLAY_NAME = "my-file.txt"
TEST_FILE_DESCRIPTION = "my file."
TEST_HEADERS = {"X-Goog-Upload-Protocol": "multipart"}
TEST_UPLOAD_REQUEST_URI = "https://{}/upload/v1beta1/projects/{}/locations/{}/ragCorpora/{}/ragFiles:upload".format(
    TEST_API_ENDPOINT, TEST_PROJECT_NUMBER, TEST_REGION, TEST_RAG_CORPUS_ID
)
TEST_RAG_FILE_ID = "generate-456"
TEST_RAG_FILE_RESOURCE_NAME = (
    TEST_RAG_CORPUS_RESOURCE_NAME + f"/ragFiles/{TEST_RAG_FILE_ID}"
)
TEST_UPLOAD_RAG_FILE_RESPONSE_CONTENT = ""
TEST_RAG_FILE_JSON = {
    "ragFile": {
        "name": TEST_RAG_FILE_RESOURCE_NAME,
        "displayName": TEST_FILE_DISPLAY_NAME,
    }
}
TEST_RAG_FILE_JSON_ERROR = {"error": {"code": 13}}
TEST_CHUNK_SIZE = 512
TEST_CHUNK_OVERLAP = 100
TEST_RAG_FILE_TRANSFORMATION_CONFIG = RagFileTransformationConfig(
    rag_file_chunking_config=RagFileChunkingConfig(
        fixed_length_chunking=RagFileChunkingConfig.FixedLengthChunking(
            chunk_size=TEST_CHUNK_SIZE,
            chunk_overlap=TEST_CHUNK_OVERLAP,
        ),
    ),
)
# GCS
TEST_IMPORT_FILES_CONFIG_GCS = ImportRagFilesConfig(
    rag_file_transformation_config=TEST_RAG_FILE_TRANSFORMATION_CONFIG,
    rebuild_ann_index=False,
    max_embedding_requests_per_min=1000,
)
TEST_IMPORT_FILES_CONFIG_GCS_REBUILD_ANN_INDEX = ImportRagFilesConfig(
    rag_file_transformation_config=TEST_RAG_FILE_TRANSFORMATION_CONFIG,
    rebuild_ann_index=True,
    max_embedding_requests_per_min=1000,
)
TEST_IMPORT_FILES_CONFIG_GCS_REBUILD_ANN_INDEX.gcs_source.uris = [TEST_GCS_PATH]
TEST_IMPORT_FILES_CONFIG_GCS_REBUILD_ANN_INDEX.rag_file_parsing_config.advanced_parser.use_advanced_pdf_parsing = (
    False
)
TEST_IMPORT_FILES_CONFIG_GCS.gcs_source.uris = [TEST_GCS_PATH]
TEST_IMPORT_FILES_CONFIG_GCS.rag_file_parsing_config.advanced_parser.use_advanced_pdf_parsing = (
    False
)
TEST_IMPORT_REQUEST_GCS = ImportRagFilesRequest(
    parent=TEST_RAG_CORPUS_RESOURCE_NAME,
    import_rag_files_config=TEST_IMPORT_FILES_CONFIG_GCS,
)
TEST_IMPORT_REQUEST_GCS_REBUILD_ANN_INDEX = ImportRagFilesRequest(
    parent=TEST_RAG_CORPUS_RESOURCE_NAME,
    import_rag_files_config=TEST_IMPORT_FILES_CONFIG_GCS_REBUILD_ANN_INDEX,
)
# Google Drive folders
TEST_DRIVE_FOLDER_ID = "123"
TEST_DRIVE_FOLDER = (
    f"https://drive.google.com/corp/drive/folders/{TEST_DRIVE_FOLDER_ID}"
)
TEST_DRIVE_FOLDER_2 = (
    f"https://drive.google.com/drive/folders/{TEST_DRIVE_FOLDER_ID}?resourcekey=0-eiOT3"
)
TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER = ImportRagFilesConfig(
    rag_file_transformation_config=TEST_RAG_FILE_TRANSFORMATION_CONFIG,
    rebuild_ann_index=False,
    max_embedding_requests_per_min=1000,
)
TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER.google_drive_source.resource_ids = [
    GoogleDriveSource.ResourceId(
        resource_id=TEST_DRIVE_FOLDER_ID,
        resource_type=GoogleDriveSource.ResourceId.ResourceType.RESOURCE_TYPE_FOLDER,
    )
]
TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER.rag_file_parsing_config.advanced_parser.use_advanced_pdf_parsing = (
    False
)
TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER_PARSING = ImportRagFilesConfig(
    rag_file_transformation_config=TEST_RAG_FILE_TRANSFORMATION_CONFIG,
    rebuild_ann_index=False,
    max_embedding_requests_per_min=1000,
)
TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER_PARSING.google_drive_source.resource_ids = [
    GoogleDriveSource.ResourceId(
        resource_id=TEST_DRIVE_FOLDER_ID,
        resource_type=GoogleDriveSource.ResourceId.ResourceType.RESOURCE_TYPE_FOLDER,
    )
]
TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER_PARSING.rag_file_parsing_config.advanced_parser.use_advanced_pdf_parsing = (
    True
)
TEST_IMPORT_REQUEST_DRIVE_FOLDER = ImportRagFilesRequest(
    parent=TEST_RAG_CORPUS_RESOURCE_NAME,
    import_rag_files_config=TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER,
)
TEST_IMPORT_REQUEST_DRIVE_FOLDER_PARSING = ImportRagFilesRequest(
    parent=TEST_RAG_CORPUS_RESOURCE_NAME,
    import_rag_files_config=TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER_PARSING,
)

# RagEngineConfig Resource
TEST_RAG_ENGINE_CONFIG_RESOURCE_NAME = (
    f"projects/{TEST_PROJECT_NUMBER}/locations/{TEST_REGION}/ragEngineConfig"
)
TEST_RAG_ENGINE_CONFIG_BASIC = RagEngineConfig(
    name=TEST_RAG_ENGINE_CONFIG_RESOURCE_NAME,
    rag_managed_db_config=RagManagedDbConfig(tier=Basic()),
)
TEST_RAG_ENGINE_CONFIG_SCALED = RagEngineConfig(
    name=TEST_RAG_ENGINE_CONFIG_RESOURCE_NAME,
    rag_managed_db_config=RagManagedDbConfig(tier=Scaled()),
)
TEST_RAG_ENGINE_CONFIG_UNPROVISIONED = RagEngineConfig(
    name=TEST_RAG_ENGINE_CONFIG_RESOURCE_NAME,
    rag_managed_db_config=RagManagedDbConfig(tier=Unprovisioned()),
)
TEST_RAG_ENGINE_CONFIG_ENTERPRISE = RagEngineConfig(
    name=TEST_RAG_ENGINE_CONFIG_RESOURCE_NAME,
    rag_managed_db_config=RagManagedDbConfig(tier=Enterprise()),
)
TEST_DEFAULT_RAG_ENGINE_CONFIG = RagEngineConfig(
    name=TEST_RAG_ENGINE_CONFIG_RESOURCE_NAME,
    rag_managed_db_config=None,
)
TEST_GAPIC_RAG_ENGINE_CONFIG_BASIC = GapicRagEngineConfig(
    name=TEST_RAG_ENGINE_CONFIG_RESOURCE_NAME,
    rag_managed_db_config=GapicRagManagedDbConfig(
        basic=GapicRagManagedDbConfig.Basic()
    ),
)
TEST_GAPIC_RAG_ENGINE_CONFIG_SCALED = GapicRagEngineConfig(
    name=TEST_RAG_ENGINE_CONFIG_RESOURCE_NAME,
    rag_managed_db_config=GapicRagManagedDbConfig(
        scaled=GapicRagManagedDbConfig.Scaled()
    ),
)
TEST_GAPIC_RAG_ENGINE_CONFIG_UNPROVISIONED = GapicRagEngineConfig(
    name=TEST_RAG_ENGINE_CONFIG_RESOURCE_NAME,
    rag_managed_db_config=GapicRagManagedDbConfig(
        unprovisioned=GapicRagManagedDbConfig.Unprovisioned()
    ),
)
TEST_GAPIC_RAG_ENGINE_CONFIG_ENTERPRISE = GapicRagEngineConfig(
    name=TEST_RAG_ENGINE_CONFIG_RESOURCE_NAME,
    rag_managed_db_config=GapicRagManagedDbConfig(
        enterprise=GapicRagManagedDbConfig.Enterprise()
    ),
)

# Google Drive files
TEST_DRIVE_FILE_ID = "456"
TEST_DRIVE_FILE = f"https://drive.google.com/file/d/{TEST_DRIVE_FILE_ID}"
TEST_IMPORT_FILES_CONFIG_DRIVE_FILE = ImportRagFilesConfig(
    rag_file_transformation_config=TEST_RAG_FILE_TRANSFORMATION_CONFIG,
    rag_file_parsing_config=RagFileParsingConfig(
        advanced_parser=RagFileParsingConfig.AdvancedParser(
            use_advanced_pdf_parsing=False
        )
    ),
    rebuild_ann_index=False,
    max_embedding_requests_per_min=1000,
)
TEST_IMPORT_FILES_CONFIG_DRIVE_FILE.max_embedding_requests_per_min = 800

TEST_IMPORT_FILES_CONFIG_DRIVE_FILE.google_drive_source.resource_ids = [
    GoogleDriveSource.ResourceId(
        resource_id=TEST_DRIVE_FILE_ID,
        resource_type=GoogleDriveSource.ResourceId.ResourceType.RESOURCE_TYPE_FILE,
    )
]
TEST_IMPORT_REQUEST_DRIVE_FILE = ImportRagFilesRequest(
    parent=TEST_RAG_CORPUS_RESOURCE_NAME,
    import_rag_files_config=TEST_IMPORT_FILES_CONFIG_DRIVE_FILE,
)

TEST_IMPORT_REQUEST_DRIVE_FILE_GLOBAL_QUOTA_CONTROL = ImportRagFilesRequest(
    parent=TEST_RAG_CORPUS_RESOURCE_NAME,
    import_rag_files_config=TEST_IMPORT_FILES_CONFIG_DRIVE_FILE,
)
TEST_IMPORT_REQUEST_DRIVE_FILE_GLOBAL_QUOTA_CONTROL.import_rag_files_config.global_max_embedding_requests_per_min = (
    8000
)

TEST_IMPORT_RESPONSE = ImportRagFilesResponse(imported_rag_files_count=2)

TEST_GAPIC_RAG_FILE = GapicRagFile(
    name=TEST_RAG_FILE_RESOURCE_NAME,
    display_name=TEST_FILE_DISPLAY_NAME,
    description=TEST_FILE_DESCRIPTION,
)
TEST_RAG_FILE = RagFile(
    name=TEST_RAG_FILE_RESOURCE_NAME,
    display_name=TEST_FILE_DISPLAY_NAME,
    description=TEST_FILE_DESCRIPTION,
)
# Slack sources
TEST_SLACK_CHANNEL_ID = "123"
TEST_SLACK_CHANNEL_ID_2 = "456"
TEST_SLACK_START_TIME = timestamp_pb2.Timestamp()
TEST_SLACK_START_TIME.GetCurrentTime()
TEST_SLACK_END_TIME = timestamp_pb2.Timestamp()
TEST_SLACK_END_TIME.GetCurrentTime()
TEST_SLACK_API_KEY_SECRET_VERSION = (
    "projects/test-project/secrets/test-secret/versions/1"
)
TEST_SLACK_API_KEY_SECRET_VERSION_2 = (
    "projects/test-project/secrets/test-secret/versions/2"
)
TEST_SLACK_SOURCE = SlackChannelsSource(
    channels=[
        SlackChannel(
            channel_id=TEST_SLACK_CHANNEL_ID,
            api_key=TEST_SLACK_API_KEY_SECRET_VERSION,
            start_time=TEST_SLACK_START_TIME,
            end_time=TEST_SLACK_END_TIME,
        ),
        SlackChannel(
            channel_id=TEST_SLACK_CHANNEL_ID_2,
            api_key=TEST_SLACK_API_KEY_SECRET_VERSION_2,
        ),
    ],
)
TEST_RAG_FILE_PARSING_CONFIG = RagFileParsingConfig(
    advanced_parser=RagFileParsingConfig.AdvancedParser(use_advanced_pdf_parsing=False)
)
TEST_IMPORT_FILES_CONFIG_SLACK_SOURCE = ImportRagFilesConfig(
    rag_file_parsing_config=TEST_RAG_FILE_PARSING_CONFIG,
    rag_file_transformation_config=TEST_RAG_FILE_TRANSFORMATION_CONFIG,
    rebuild_ann_index=False,
    max_embedding_requests_per_min=1000,
)
TEST_IMPORT_FILES_CONFIG_SLACK_SOURCE.slack_source.channels = [
    GapicSlackSource.SlackChannels(
        channels=[
            GapicSlackSource.SlackChannels.SlackChannel(
                channel_id=TEST_SLACK_CHANNEL_ID,
                start_time=TEST_SLACK_START_TIME,
                end_time=TEST_SLACK_END_TIME,
            ),
        ],
        api_key_config=api_auth.ApiAuth.ApiKeyConfig(
            api_key_secret_version=TEST_SLACK_API_KEY_SECRET_VERSION
        ),
    ),
    GapicSlackSource.SlackChannels(
        channels=[
            GapicSlackSource.SlackChannels.SlackChannel(
                channel_id=TEST_SLACK_CHANNEL_ID_2,
                start_time=None,
                end_time=None,
            ),
        ],
        api_key_config=api_auth.ApiAuth.ApiKeyConfig(
            api_key_secret_version=TEST_SLACK_API_KEY_SECRET_VERSION_2
        ),
    ),
]
TEST_IMPORT_REQUEST_SLACK_SOURCE = ImportRagFilesRequest(
    parent=TEST_RAG_CORPUS_RESOURCE_NAME,
    import_rag_files_config=TEST_IMPORT_FILES_CONFIG_SLACK_SOURCE,
)
# Jira sources
TEST_JIRA_EMAIL = "test@test.com"
TEST_JIRA_PROJECT = "test-project"
TEST_JIRA_CUSTOM_QUERY = "test-custom-query"
TEST_JIRA_SERVER_URI = "test.atlassian.net"
TEST_JIRA_API_KEY_SECRET_VERSION = (
    "projects/test-project/secrets/test-secret/versions/1"
)
TEST_JIRA_SOURCE = JiraSource(
    queries=[
        JiraQuery(
            email=TEST_JIRA_EMAIL,
            jira_projects=[TEST_JIRA_PROJECT],
            custom_queries=[TEST_JIRA_CUSTOM_QUERY],
            api_key=TEST_JIRA_API_KEY_SECRET_VERSION,
            server_uri=TEST_JIRA_SERVER_URI,
        )
    ],
)
TEST_IMPORT_FILES_CONFIG_JIRA_SOURCE = ImportRagFilesConfig(
    rag_file_parsing_config=TEST_RAG_FILE_PARSING_CONFIG,
    rag_file_transformation_config=TEST_RAG_FILE_TRANSFORMATION_CONFIG,
    rebuild_ann_index=False,
    max_embedding_requests_per_min=1000,
)
TEST_IMPORT_FILES_CONFIG_JIRA_SOURCE.jira_source.jira_queries = [
    GapicJiraSource.JiraQueries(
        custom_queries=[TEST_JIRA_CUSTOM_QUERY],
        projects=[TEST_JIRA_PROJECT],
        email=TEST_JIRA_EMAIL,
        server_uri=TEST_JIRA_SERVER_URI,
        api_key_config=api_auth.ApiAuth.ApiKeyConfig(
            api_key_secret_version=TEST_JIRA_API_KEY_SECRET_VERSION
        ),
    )
]
TEST_IMPORT_REQUEST_JIRA_SOURCE = ImportRagFilesRequest(
    parent=TEST_RAG_CORPUS_RESOURCE_NAME,
    import_rag_files_config=TEST_IMPORT_FILES_CONFIG_JIRA_SOURCE,
)

# SharePoint sources
TEST_SHARE_POINT_SOURCE = SharePointSources(
    share_point_sources=[
        SharePointSource(
            sharepoint_folder_path="test-sharepoint-folder-path",
            drive_name="test-drive-name",
            client_id="test-client-id",
            client_secret="test-client-secret",
            tenant_id="test-tenant-id",
            sharepoint_site_name="test-sharepoint-site-name",
        )
    ],
)
TEST_IMPORT_FILES_CONFIG_SHARE_POINT_SOURCE = ImportRagFilesConfig(
    rag_file_parsing_config=TEST_RAG_FILE_PARSING_CONFIG,
    rag_file_transformation_config=TEST_RAG_FILE_TRANSFORMATION_CONFIG,
    max_embedding_requests_per_min=1000,
    share_point_sources=GapicSharePointSources(
        share_point_sources=[
            GapicSharePointSources.SharePointSource(
                sharepoint_folder_path="test-sharepoint-folder-path",
                drive_name="test-drive-name",
                client_id="test-client-id",
                client_secret=api_auth.ApiAuth.ApiKeyConfig(
                    api_key_secret_version="test-client-secret"
                ),
                tenant_id="test-tenant-id",
                sharepoint_site_name="test-sharepoint-site-name",
            )
        ]
    ),
    rebuild_ann_index=False,
)

TEST_IMPORT_REQUEST_SHARE_POINT_SOURCE = ImportRagFilesRequest(
    parent=TEST_RAG_CORPUS_RESOURCE_NAME,
    import_rag_files_config=TEST_IMPORT_FILES_CONFIG_SHARE_POINT_SOURCE,
)

TEST_SHARE_POINT_SOURCE_2_DRIVES = SharePointSources(
    share_point_sources=[
        SharePointSource(
            sharepoint_folder_path="test-sharepoint-folder-path",
            drive_name="test-drive-name",
            drive_id="test-drive-id",
            client_id="test-client-id",
            client_secret="test-client-secret",
            tenant_id="test-tenant-id",
            sharepoint_site_name="test-sharepoint-site-name",
        )
    ],
)

TEST_SHARE_POINT_SOURCE_NO_DRIVES = SharePointSources(
    share_point_sources=[
        SharePointSource(
            sharepoint_folder_path="test-sharepoint-folder-path",
            client_id="test-client-id",
            client_secret="test-client-secret",
            tenant_id="test-tenant-id",
            sharepoint_site_name="test-sharepoint-site-name",
        )
    ],
)

TEST_SHARE_POINT_SOURCE_2_FOLDERS = SharePointSources(
    share_point_sources=[
        SharePointSource(
            sharepoint_folder_path="test-sharepoint-folder-path",
            sharepoint_folder_id="test-sharepoint-folder-id",
            drive_name="test-drive-name",
            client_id="test-client-id",
            client_secret="test-client-secret",
            tenant_id="test-tenant-id",
            sharepoint_site_name="test-sharepoint-site-name",
        )
    ],
)

TEST_SHARE_POINT_SOURCE_NO_FOLDERS = SharePointSources(
    share_point_sources=[
        SharePointSource(
            drive_name="test-drive-name",
            client_id="test-client-id",
            client_secret="test-client-secret",
            tenant_id="test-tenant-id",
            sharepoint_site_name="test-sharepoint-site-name",
        )
    ],
)

TEST_LAYOUT_PARSER_WITH_PROCESSOR_PATH_CONFIG = LayoutParserConfig(
    processor_name="projects/test-project/locations/us/processors/abc123",
    max_parsing_requests_per_min=100,
    global_max_parsing_requests_per_min=1000,
)

TEST_LAYOUT_PARSER_WITH_PROCESSOR_VERSION_PATH_CONFIG = LayoutParserConfig(
    processor_name="projects/test-project/locations/us/processors/abc123/processorVersions/pretrained-layout-parser-v0.0-2020-01-0",
    max_parsing_requests_per_min=100,
)

TEST_GAPIC_LLM_PARSER = RagFileParsingConfig.LlmParser(
    model_name="gemini-1.5-pro-002",
    max_parsing_requests_per_min=500,
    global_max_parsing_requests_per_min=1000,
    custom_parsing_prompt="test-custom-parsing-prompt",
)

TEST_LLM_PARSER_CONFIG = LlmParserConfig(
    model_name="gemini-1.5-pro-002",
    max_parsing_requests_per_min=500,
    global_max_parsing_requests_per_min=1000,
    custom_parsing_prompt="test-custom-parsing-prompt",
)

TEST_RAG_MEMORY_CORPUS_CONFIG = MemoryCorpus(
    llm_parser=TEST_LLM_PARSER_CONFIG,
)

TEST_RAG_MEMORY_CORPUS = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    corpus_type_config=RagCorpusTypeConfig(
        corpus_type_config=TEST_RAG_MEMORY_CORPUS_CONFIG
    ),
)

TEST_GAPIC_RAG_MEMORY_CORPUS = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    corpus_type_config=GapicRagCorpus.CorpusTypeConfig(
        memory_corpus=GapicRagCorpus.CorpusTypeConfig.MemoryCorpus(
            llm_parser=RagFileParsingConfig.LlmParser(
                model_name="gemini-1.5-pro-002",
                max_parsing_requests_per_min=500,
                global_max_parsing_requests_per_min=1000,
                custom_parsing_prompt="test-custom-parsing-prompt",
            )
        )
    ),
)

TEST_RAG_DOCUMENT_CORPUS_CONFIG = DocumentCorpus()

TEST_RAG_DOCUMENT_CORPUS = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    corpus_type_config=RagCorpusTypeConfig(
        corpus_type_config=TEST_RAG_DOCUMENT_CORPUS_CONFIG
    ),
)

TEST_GAPIC_RAG_DOCUMENT_CORPUS = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    corpus_type_config=GapicRagCorpus.CorpusTypeConfig(
        document_corpus=GapicRagCorpus.CorpusTypeConfig.DocumentCorpus()
    ),
)

TEST_IMPORT_FILES_CONFIG_SHARE_POINT_SOURCE_NO_FOLDERS = ImportRagFilesConfig(
    rag_file_transformation_config=TEST_RAG_FILE_TRANSFORMATION_CONFIG,
    max_embedding_requests_per_min=1000,
    share_point_sources=GapicSharePointSources(
        share_point_sources=[
            GapicSharePointSources.SharePointSource(
                drive_name="test-drive-name",
                client_id="test-client-id",
                client_secret=api_auth.ApiAuth.ApiKeyConfig(
                    api_key_secret_version="test-client-secret"
                ),
                tenant_id="test-tenant-id",
                sharepoint_site_name="test-sharepoint-site-name",
            )
        ]
    ),
    rebuild_ann_index=False,
)

TEST_IMPORT_REQUEST_SHARE_POINT_SOURCE_NO_FOLDERS = ImportRagFilesRequest(
    parent=TEST_RAG_CORPUS_RESOURCE_NAME,
    import_rag_files_config=TEST_IMPORT_FILES_CONFIG_SHARE_POINT_SOURCE,
)

TEST_IMPORT_FILES_CONFIG_LAYOUT_PARSER_WITH_PROCESSOR_PATH = ImportRagFilesConfig(
    TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER
)
TEST_IMPORT_FILES_CONFIG_LAYOUT_PARSER_WITH_PROCESSOR_PATH.rag_file_parsing_config = (
    RagFileParsingConfig(
        layout_parser=RagFileParsingConfig.LayoutParser(
            processor_name="projects/test-project/locations/us/processors/abc123",
            max_parsing_requests_per_min=100,
            global_max_parsing_requests_per_min=1000,
        )
    )
)

TEST_IMPORT_REQUEST_LAYOUT_PARSER_WITH_PROCESSOR_PATH = ImportRagFilesRequest(
    parent=TEST_RAG_CORPUS_RESOURCE_NAME,
    import_rag_files_config=TEST_IMPORT_FILES_CONFIG_LAYOUT_PARSER_WITH_PROCESSOR_PATH,
)

TEST_IMPORT_FILES_CONFIG_LAYOUT_PARSER_WITH_PROCESSOR_VERSION_PATH = (
    ImportRagFilesConfig(TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER)
)
TEST_IMPORT_FILES_CONFIG_LAYOUT_PARSER_WITH_PROCESSOR_VERSION_PATH.rag_file_parsing_config = RagFileParsingConfig(
    layout_parser=RagFileParsingConfig.LayoutParser(
        processor_name="projects/test-project/locations/us/processors/abc123/processorVersions/pretrained-layout-parser-v0.0-2020-01-0",
        max_parsing_requests_per_min=100,
    )
)

TEST_IMPORT_REQUEST_LAYOUT_PARSER_WITH_PROCESSOR_VERSION_PATH = ImportRagFilesRequest(
    parent=TEST_RAG_CORPUS_RESOURCE_NAME,
    import_rag_files_config=TEST_IMPORT_FILES_CONFIG_LAYOUT_PARSER_WITH_PROCESSOR_VERSION_PATH,
)

TEST_IMPORT_FILES_CONFIG_LLM_PARSER = ImportRagFilesConfig(
    TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER
)

TEST_IMPORT_FILES_CONFIG_LLM_PARSER.rag_file_parsing_config = RagFileParsingConfig(
    llm_parser=RagFileParsingConfig.LlmParser(
        model_name="gemini-1.5-pro-002",
        max_parsing_requests_per_min=500,
        global_max_parsing_requests_per_min=1000,
        custom_parsing_prompt="test-custom-parsing-prompt",
    )
)

TEST_IMPORT_REQUEST_LLM_PARSER = ImportRagFilesRequest(
    parent=TEST_RAG_CORPUS_RESOURCE_NAME,
    import_rag_files_config=TEST_IMPORT_FILES_CONFIG_LLM_PARSER,
)

# Retrieval
TEST_QUERY_TEXT = "What happen to the fox and the dog?"
TEST_CONTEXTS = RagContexts(
    contexts=[
        RagContexts.Context(
            source_uri="https://drive.google.com/file/d/123/view?usp=drivesdk",
            text="The quick brown fox jumps over the lazy dog.",
        ),
        RagContexts.Context(text="The slow red fox jumps over the lazy dog."),
    ]
)
TEST_RETRIEVAL_RESPONSE = RetrieveContextsResponse(contexts=TEST_CONTEXTS)
TEST_RAG_RESOURCE = RagResource(
    rag_corpus=TEST_RAG_CORPUS_RESOURCE_NAME,
    rag_file_ids=[TEST_RAG_FILE_ID],
)
TEST_RAG_RESOURCE_INVALID_NAME = RagResource(
    rag_corpus="213lkj-1/23jkl/",
    rag_file_ids=[TEST_RAG_FILE_ID],
)
TEST_RAG_RETRIEVAL_CONFIG = RagRetrievalConfig(
    top_k=2,
    filter=Filter(vector_distance_threshold=0.5),
)
TEST_RAG_RETRIEVAL_CONFIG_ALPHA = RagRetrievalConfig(
    top_k=2,
    filter=Filter(vector_distance_threshold=0.5),
    hybrid_search=HybridSearch(alpha=0.5),
)
TEST_RAG_RETRIEVAL_SIMILARITY_CONFIG = RagRetrievalConfig(
    top_k=2,
    filter=Filter(vector_distance_threshold=0.5),
    hybrid_search=HybridSearch(alpha=0.5),
)
TEST_RAG_RETRIEVAL_ERROR_CONFIG = RagRetrievalConfig(
    top_k=2,
    filter=Filter(vector_distance_threshold=0.5, vector_similarity_threshold=0.5),
)
TEST_RAG_RETRIEVAL_RANKING_CONFIG = RagRetrievalConfig(
    top_k=2,
    filter=Filter(vector_distance_threshold=0.5),
    ranking=Ranking(rank_service=RankService(model_name="test-rank-service")),
)
TEST_RAG_RETRIEVAL_ERROR_RANKING_CONFIG = RagRetrievalConfig(
    top_k=2,
    filter=Filter(vector_distance_threshold=0.5),
    ranking=Ranking(
        rank_service=RankService(model_name="test-rank-service"),
        llm_ranker=LlmRanker(model_name="test-llm-ranker"),
    ),
)
TEST_RAG_RETRIEVAL_CONFIG_RANK_SERVICE = RagRetrievalConfig(
    top_k=2,
    filter=Filter(vector_distance_threshold=0.5),
    ranking=Ranking(rank_service=RankService(model_name="test-model-name")),
)
TEST_RAG_RETRIEVAL_CONFIG_LLM_RANKER = RagRetrievalConfig(
    top_k=2,
    filter=Filter(vector_distance_threshold=0.5),
    ranking=Ranking(llm_ranker=LlmRanker(model_name="test-model-name")),
)
