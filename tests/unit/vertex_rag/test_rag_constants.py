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

from vertexai.rag import (
    Basic,
    Filter,
    LayoutParserConfig,
    LlmParserConfig,
    LlmRanker,
    Pinecone,
    RagCorpus,
    RagEngineConfig,
    RagFile,
    RagManagedDbConfig,
    RagResource,
    RagRetrievalConfig,
    RagVectorDbConfig,
    Ranking,
    RankService,
    Scaled,
    SharePointSource,
    SharePointSources,
    SlackChannelsSource,
    SlackChannel,
    JiraSource,
    JiraQuery,
    Unprovisioned,
    VertexVectorSearch,
    RagEmbeddingModelConfig,
    VertexAiSearchConfig,
    VertexPredictionEndpoint,
)

from google.cloud.aiplatform_v1 import (
    GoogleDriveSource,
    RagEngineConfig as GapicRagEngineConfig,
    RagFileChunkingConfig,
    RagFileParsingConfig,
    RagFileTransformationConfig,
    RagManagedDbConfig as GapicRagManagedDbConfig,
    ImportRagFilesConfig,
    ImportRagFilesRequest,
    ImportRagFilesResponse,
    JiraSource as GapicJiraSource,
    RagCorpus as GapicRagCorpus,
    RagFile as GapicRagFile,
    SharePointSources as GapicSharePointSources,
    SlackSource as GapicSlackSource,
    RagContexts,
    RetrieveContextsResponse,
    RagVectorDbConfig as GapicRagVectorDbConfig,
    VertexAiSearchConfig as GapicVertexAiSearchConfig,
)
from google.cloud.aiplatform_v1.types import api_auth
from google.cloud.aiplatform_v1.types import EncryptionSpec
from google.protobuf import timestamp_pb2

from google.cloud.aiplatform_v1.types import content

from google.cloud.aiplatform_v1.types.vertex_rag_data import RagChunk

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
TEST_PINECONE_INDEX_NAME = "test-pinecone-index"
TEST_PINECONE_API_KEY_SECRET_VERSION = (
    "projects/test-project/secrets/test-secret/versions/1"
)
TEST_PINECONE_CONFIG = Pinecone(
    index_name=TEST_PINECONE_INDEX_NAME,
    api_key=TEST_PINECONE_API_KEY_SECRET_VERSION,
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
TEST_GAPIC_RAG_CORPUS.vector_db_config.rag_embedding_model_config.vertex_prediction_endpoint.endpoint = "projects/{}/locations/{}/publishers/google/models/textembedding-gecko".format(
    TEST_PROJECT, TEST_REGION
)
TEST_GAPIC_CMEK_RAG_CORPUS = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    encryption_spec=EncryptionSpec(
        kms_key_name="projects/test-project/locations/us-central1/keyRings/test-key-ring/cryptoKeys/test-key"
    ),
)
TEST_GAPIC_RAG_CORPUS_VERTEX_VECTOR_SEARCH = GapicRagCorpus(
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
TEST_GAPIC_RAG_CORPUS_PINECONE = GapicRagCorpus(
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

TEST_EMBEDDING_MODEL_CONFIG = RagEmbeddingModelConfig(
    vertex_prediction_endpoint=VertexPredictionEndpoint(
        publisher_model=(
            "projects/{}/locations/{}/publishers/google/models/textembedding-gecko".format(
                TEST_PROJECT, TEST_REGION
            )
        ),
    ),
)
TEST_BACKEND_CONFIG_EMBEDDING_MODEL_CONFIG = RagVectorDbConfig(
    rag_embedding_model_config=TEST_EMBEDDING_MODEL_CONFIG,
)
TEST_RAG_CORPUS = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    backend_config=TEST_BACKEND_CONFIG_EMBEDDING_MODEL_CONFIG,
)
TEST_CMEK_RAG_CORPUS = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    encryption_spec=EncryptionSpec(
        kms_key_name="projects/test-project/locations/us-central1/keyRings/test-key-ring/cryptoKeys/test-key"
    ),
)
TEST_BACKEND_CONFIG_PINECONE_CONFIG = RagVectorDbConfig(
    vector_db=TEST_PINECONE_CONFIG,
)
TEST_RAG_CORPUS_PINECONE = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    backend_config=TEST_BACKEND_CONFIG_PINECONE_CONFIG,
)
TEST_BACKEND_CONFIG_VERTEX_VECTOR_SEARCH_CONFIG = RagVectorDbConfig(
    vector_db=TEST_VERTEX_VECTOR_SEARCH_CONFIG,
)
TEST_RAG_CORPUS_VERTEX_VECTOR_SEARCH = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    backend_config=TEST_BACKEND_CONFIG_VERTEX_VECTOR_SEARCH_CONFIG,
)
TEST_PAGE_TOKEN = "test-page-token"

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
TEST_UPLOAD_REQUEST_URI = "https://{}/upload/v1/projects/{}/locations/{}/ragCorpora/{}/ragFiles:upload".format(
    TEST_API_ENDPOINT, TEST_PROJECT_NUMBER, TEST_REGION, TEST_RAG_CORPUS_ID
)
TEST_RAG_FILE_ID = "generate-456"
TEST_RAG_FILE_RESOURCE_NAME = (
    TEST_RAG_CORPUS_RESOURCE_NAME + f"/ragFiles/{TEST_RAG_FILE_ID}"
)
TEST_UPLOAD_RAG_FILE_RESPONSE_CONTENT = ""
TEST_CHUNK_SIZE = 512
TEST_CHUNK_OVERLAP = 100
TEST_RAG_FILE_JSON = {
    "ragFile": {
        "name": TEST_RAG_FILE_RESOURCE_NAME,
        "displayName": TEST_FILE_DISPLAY_NAME,
    }
}
TEST_RAG_FILE_JSON_WITH_UPLOAD_CONFIG = {
    "ragFile": {
        "name": TEST_RAG_FILE_RESOURCE_NAME,
        "displayName": TEST_FILE_DISPLAY_NAME,
    },
    "rag_file_transformation_config": {
        "rag_file_transformation_config": {
            "rag_file_chunking_config": {
                "fixed_length_chunking": {
                    "chunk_size": TEST_CHUNK_SIZE,
                    "chunk_overlap": TEST_CHUNK_OVERLAP,
                }
            }
        }
    },
}
TEST_RAG_FILE_JSON_ERROR = {"error": {"code": 13}}
TEST_RAG_FILE_TRANSFORMATION_CONFIG = RagFileTransformationConfig(
    rag_file_chunking_config=RagFileChunkingConfig(
        fixed_length_chunking=RagFileChunkingConfig.FixedLengthChunking(
            chunk_size=TEST_CHUNK_SIZE,
            chunk_overlap=TEST_CHUNK_OVERLAP,
        ),
    ),
)
TEST_IMPORT_RESULT_GCS_SINK = "gs://test-bucket/test-object.ndjson"
TEST_IMPORT_RESULT_BIGQUERY_SINK = "bq://test-project.test_dataset.test_table"
# GCS
TEST_IMPORT_FILES_CONFIG_GCS = ImportRagFilesConfig(
    rag_file_transformation_config=TEST_RAG_FILE_TRANSFORMATION_CONFIG,
)
TEST_IMPORT_FILES_CONFIG_GCS.gcs_source.uris = [TEST_GCS_PATH]
TEST_IMPORT_REQUEST_GCS = ImportRagFilesRequest(
    parent=TEST_RAG_CORPUS_RESOURCE_NAME,
    import_rag_files_config=TEST_IMPORT_FILES_CONFIG_GCS,
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
)
TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER.google_drive_source.resource_ids = [
    GoogleDriveSource.ResourceId(
        resource_id=TEST_DRIVE_FOLDER_ID,
        resource_type=GoogleDriveSource.ResourceId.ResourceType.RESOURCE_TYPE_FOLDER,
    )
]
TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER_PARSING = ImportRagFilesConfig()
TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER_PARSING.google_drive_source.resource_ids = [
    GoogleDriveSource.ResourceId(
        resource_id=TEST_DRIVE_FOLDER_ID,
        resource_type=GoogleDriveSource.ResourceId.ResourceType.RESOURCE_TYPE_FOLDER,
    )
]
TEST_IMPORT_REQUEST_DRIVE_FOLDER = ImportRagFilesRequest(
    parent=TEST_RAG_CORPUS_RESOURCE_NAME,
    import_rag_files_config=TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER,
)
TEST_IMPORT_REQUEST_DRIVE_FOLDER_PARSING = ImportRagFilesRequest(
    parent=TEST_RAG_CORPUS_RESOURCE_NAME,
    import_rag_files_config=TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER_PARSING,
)
# Google Drive files
TEST_DRIVE_FILE_ID = "456"
TEST_DRIVE_FILE = f"https://drive.google.com/file/d/{TEST_DRIVE_FILE_ID}"
TEST_IMPORT_FILES_CONFIG_DRIVE_FILE = ImportRagFilesConfig(
    rag_file_transformation_config=TEST_RAG_FILE_TRANSFORMATION_CONFIG,
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
TEST_IMPORT_FILES_CONFIG_SLACK_SOURCE = ImportRagFilesConfig(
    rag_file_transformation_config=TEST_RAG_FILE_TRANSFORMATION_CONFIG,
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
    rag_file_transformation_config=TEST_RAG_FILE_TRANSFORMATION_CONFIG,
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
    rag_file_transformation_config=TEST_RAG_FILE_TRANSFORMATION_CONFIG,
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
)

TEST_LAYOUT_PARSER_WITH_PROCESSOR_VERSION_PATH_CONFIG = LayoutParserConfig(
    processor_name="projects/test-project/locations/us/processors/abc123/processorVersions/pretrained-layout-parser-v0.0-2020-01-0",
    max_parsing_requests_per_min=100,
)

TEST_IMPORT_FILES_CONFIG_SHARE_POINT_SOURCE_NO_FOLDERS = ImportRagFilesConfig(
    rag_file_transformation_config=TEST_RAG_FILE_TRANSFORMATION_CONFIG,
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
TEST_RAG_RETRIEVAL_SIMILARITY_CONFIG = RagRetrievalConfig(
    top_k=2,
    filter=Filter(vector_similarity_threshold=0.5),
)
TEST_RAG_RETRIEVAL_ERROR_CONFIG = RagRetrievalConfig(
    top_k=2,
    filter=Filter(vector_distance_threshold=0.5, vector_similarity_threshold=0.5),
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
TEST_LLM_PARSER_CONFIG = LlmParserConfig(
    model_name="gemini-1.5-pro-002",
    max_parsing_requests_per_min=500,
    custom_parsing_prompt="test-custom-parsing-prompt",
)


TEST_IMPORT_FILES_CONFIG_LLM_PARSER = ImportRagFilesConfig(
    TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER
)

TEST_IMPORT_FILES_CONFIG_LLM_PARSER.rag_file_parsing_config = RagFileParsingConfig(
    llm_parser=RagFileParsingConfig.LlmParser(
        model_name="gemini-1.5-pro-002",
        max_parsing_requests_per_min=500,
        custom_parsing_prompt="test-custom-parsing-prompt",
    )
)

TEST_IMPORT_REQUEST_LLM_PARSER = ImportRagFilesRequest(
    parent=TEST_RAG_CORPUS_RESOURCE_NAME,
    import_rag_files_config=TEST_IMPORT_FILES_CONFIG_LLM_PARSER,
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

# Inline Citations test constants
TEST_ORIGINAL_TEXT = (
    "You can activate the parking radar using a switch or through the"
    " infotainment system. When the ignition is switched on, the parking assist"
    " system, which includes the reversing radar, is enabled automatically. The"
    " parking assist system detects obstacles using sensors and alerts the"
    " driver with an image on the infotainment touchscreen and a speaker alarm."
    " You can also enable or disable the reversing radar specifically by"
    " navigating to Home > ADAS > Parking Assist > Reversing Radar in the"
    " infotainment system. Alternatively, there is a reversing radar switch,"
    " often labeled with a 'P' and radiating lines, on the center console that"
    " can be pressed to activate the parking radar."
)

TEST_GROUNDING_SUPPORTS = [
    content.GroundingSupport(
        segment=content.Segment(
            end_index=85,
            text="You can activate the parking radar using a switch or through the infotainment system.",
        ),
        grounding_chunk_indices=[0, 1],
        confidence_scores=[0.6708929538726807, 0.6224815249443054],
    ),
    content.GroundingSupport(
        segment=content.Segment(
            start_index=86,
            end_index=208,
            text="When the ignition is switched on, the parking assist system, which includes the reversing radar, is enabled automatically.",
        ),
        grounding_chunk_indices=[2],
        confidence_scores=[0.7646936178207397],
    ),
    content.GroundingSupport(
        segment=content.Segment(
            start_index=209,
            end_index=355,
            text="The parking assist system detects obstacles using sensors and alerts the driver with an image on the infotainment touchscreen and a speaker alarm.",
        ),
        grounding_chunk_indices=[3],
        confidence_scores=[0.9851489067077637],
    ),
    content.GroundingSupport(
        segment=content.Segment(
            start_index=512,
            end_index=680,
            text='Alternatively, there is a reversing radar switch, often labeled with a "P" and radiating lines, on the center console that can be pressed to activate the parking radar.',
        ),
        grounding_chunk_indices=[2],
        confidence_scores=[0.691600501537323],
    ),
]

TEST_GROUNDING_CHUNKS = [
    content.GroundingChunk(
        retrieved_context=content.GroundingChunk.RetrievedContext(
            uri="gs://sample-gcs-directory/file2.pdf",
            title="file2.pdf",
            text='* "to switch to a 180° perspective displayed in full screen." (Source: First bullet point, top left)\n* "Tap the radar icon in the panoramic view to enable the radar display, and tap it again to disable." (Source: Second bullet point, top left)\n* "When the radar display is enabled, a warning is displayed as the vehicle is approaching an obstacle." (Source: Second bullet point, top left)\n* **Title:** "Portrait mode:" (Source: Text section, left column)\n* "On the bottom of the infotainment touchscreen, tap any two of the icons for front, rear, right and left views." (Source: Bullet point under "Portrait mode:")\n* "Views of the two selected areas are displayed in the image section." (Source: Bullet point under "Portrait mode:")\n* "Slowly tap the vehicle image on the right to switch between transparent and non-transparent vehicle images." (Source: Bullet point under "Portrait mode:")\n* "After the vehicle starts, the image before last power-off is displayed on the transparent panoramic view screen." (Source: Bullet point, left column)\n* "Foreign bodies shown may be inconsistent with the actual ones in the underbody and surrounding blind areas." (Source: Bullet point, left column)\n* "The underbody image update will begin only after the vehicle has started to run and will be complete when the vehicle has been driven beyond its length." (Source: Bullet point, left column)\n* **Image Content:** The image shows a split-screen display. The left side shows a top-down view of a vehicle. The right side shows a fisheye camera view from the rear of the vehicle. (Source: Image in the left column)\n* **Image Content:** Icons on the bottom of the screen include "Settings", "PA", "3D", "OFF", "0*", a camera icon, a box icon, another box icon, and "OFF". (Source: Image in the left column)\n* **Image Content:** Text overlay on the image: "19:04 (昼) AVM Please watch the surroundings". (Source: Image in the left column)\n* **Title:** "WARNING" (Source: Red triangle warning box, bottom left)\n* "This system uses wide-angle fisheye cameras, so the object on the display screen may appear somewhat deformed in comparison with the actual object." (Source: Text under "WARNING", bottom left)\n* **Title:** "WARNING" (Source: Red triangle warning box, top right)\n* "The panoramic view system is only to be used for parking/driving assistance." (Source: Bullet point under "WARNING", top right)\n* "It is not safe to rely solely on this system to park or drive the vehicle, because there are some blind spots in front of and behind the vehicle." (Source: Bullet point under "WARNING", top right)\n* "The surroundings of the vehicle should be observed in other ways during the parking/driving process, so as to avoid accidents." (Source: Bullet point under "WARNING", top right)\n* "When the side mirrors are not extended in place, do not use the panoramic view system; and when the panoramic view system is used for parking/driving, ensure that all the car doors are closed." (Source: Bullet point under "WARNING", top right)\n* "The distance to an object displayed on the panoramic view screen may be different from the distance perceived subjectively, especially when the object is closer to the vehicle." (Source: Bullet point under "WARNING", top right)\n* "Assess the distance in various ways." (Source: Bullet point under "WARNING", top right)\n* "Cameras are installed above the front bumper, the lower parts of the side mirrors, and the rear license plate." (Source: Bullet point under "WARNING", top right)\n* "Make sure the cameras are unobstructed." (Source: Bullet point under "WARNING", top right)\n* "To prevent affecting camera performance, avoid spraying directly on the cameras when washing the vehicle body with high-pressure water." (Source: Bullet point under "WARNING", top right)\n* "Wipe any water or dust off the camera in time." (Source: Bullet point under "WARNING", top right)\n* "Protect the cameras from any impact to prevent damage or malfunction." (Source: Bullet point under "WARNING", top right)\n* "134" (Source: Page number, bottom center)"',
            rag_chunk=RagChunk(
                text='* "to switch to a 180° perspective displayed in full screen." (Source: First bullet point, top left)\n* "Tap the radar icon in the panoramic view to enable the radar display, and tap it again to disable." (Source: Second bullet point, top left)\n* "When the radar display is enabled, a warning is displayed as the vehicle is approaching an obstacle." (Source: Second bullet point, top left)\n* **Title:** "Portrait mode:" (Source: Text section, left column)\n* "On the bottom of the infotainment touchscreen, tap any two of the icons for front, rear, right and left views." (Source: Bullet point under "Portrait mode:")\n* "Views of the two selected areas are displayed in the image section." (Source: Bullet point under "Portrait mode:")\n* "Slowly tap the vehicle image on the right to switch between transparent and non-transparent vehicle images." (Source: Bullet point under "Portrait mode:")\n* "After the vehicle starts, the image before last power-off is displayed on the transparent panoramic view screen." (Source: Bullet point, left column)\n* "Foreign bodies shown may be inconsistent with the actual ones in the underbody and surrounding blind areas." (Source: Bullet point, left column)\n* "The underbody image update will begin only after the vehicle has started to run and will be complete when the vehicle has been driven beyond its length." (Source: Bullet point, left column)\n* **Image Content:** The image shows a split-screen display. The left side shows a top-down view of a vehicle. The right side shows a fisheye camera view from the rear of the vehicle. (Source: Image in the left column)\n* **Image Content:** Icons on the bottom of the screen include "Settings", "PA", "3D", "OFF", "0*", a camera icon, a box icon, another box icon, and "OFF". (Source: Image in the left column)\n* **Image Content:** Text overlay on the image: "19:04 (昼) AVM Please watch the surroundings". (Source: Image in the left column)\n* **Title:** "WARNING" (Source: Red triangle warning box, bottom left)\n* "This system uses wide-angle fisheye cameras, so the object on the display screen may appear somewhat deformed in comparison with the actual object." (Source: Text under "WARNING", bottom left)\n* **Title:** "WARNING" (Source: Red triangle warning box, top right)\n* "The panoramic view system is only to be used for parking/driving assistance." (Source: Bullet point under "WARNING", top right)\n* "It is not safe to rely solely on this system to park or drive the vehicle, because there are some blind spots in front of and behind the vehicle." (Source: Bullet point under "WARNING", top right)\n* "The surroundings of the vehicle should be observed in other ways during the parking/driving process, so as to avoid accidents." (Source: Bullet point under "WARNING", top right)\n* "When the side mirrors are not extended in place, do not use the panoramic view system; and when the panoramic view system is used for parking/driving, ensure that all the car doors are closed." (Source: Bullet point under "WARNING", top right)\n* "The distance to an object displayed on the panoramic view screen may be different from the distance perceived subjectively, especially when the object is closer to the vehicle." (Source: Bullet point under "WARNING", top right)\n* "Assess the distance in various ways." (Source: Bullet point under "WARNING", top right)\n* "Cameras are installed above the front bumper, the lower parts of the side mirrors, and the rear license plate." (Source: Bullet point under "WARNING", top right)\n* "Make sure the cameras are unobstructed." (Source: Bullet point under "WARNING", top right)\n* "To prevent affecting camera performance, avoid spraying directly on the cameras when washing the vehicle body with high-pressure water." (Source: Bullet point under "WARNING", top right)\n* "Wipe any water or dust off the camera in time." (Source: Bullet point under "WARNING", top right)\n* "Protect the cameras from any impact to prevent damage or malfunction." (Source: Bullet point under "WARNING", top right)\n* "134" (Source: Page number, bottom center)"',
                page_span=RagChunk.PageSpan(first_page=15, last_page=15),
            ),
        )
    ),
    content.GroundingChunk(
        retrieved_context=content.GroundingChunk.RetrievedContext(
            uri="gs://sample-gcs-directory/file2.pdf",
            title="file2.pdf",
            text='| Fact                                                                                                                                        | Source                                            |\n|---------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------|\n| When the low pressure warning light comes on, avoid sharp turns or emergency braking, and reduce vehicle speed.                             | WARNING (top left)                                |\n| Pull it over to the curb and stop as soon as possible.                                                                                      | WARNING (top left)                                |\n| Driving with low tire pressure can cause permanent damage to tires and increase the likelihood of tire scrapping.                           | WARNING (top left)                                |\n| Serious tire damage can lead to traffic accidents, resulting in serious injuries or deaths.                                                 | WARNING (top left)                                |\n| Title: Acoustic Vehicle Alert System (AVAS)                                                                                                 | Main text                                         |\n| Acoustic Vehicle Alerting System (AVAS) refers to the broadcast to pedestrians near the vehicle when it is traveling at low speed.          | Main text, under "Acoustic Vehicle Alert System (AVAS)" |\n| When driving forward: The broadcast volume increases with the increase of vehicle speed in the range of 0 km/h < V ≤ 20 km/h.               | Main text, under "Acoustic Vehicle Alert System (AVAS)" |\n| When driving forward: The broadcast volume decreases with the increase of vehicle speed in the range of 20 km/h < V ≤ 30 km/h.               | Main text, under "Acoustic Vehicle Alert System (AVAS)" |\n| When driving forward: At speeds above 30 km/h, the broadcast sound stops automatically.                                                     | Main text, under "Acoustic Vehicle Alert System (AVAS)" |\n| The vehicle makes a continuous and balanced prompt sound when moving in Reverse.                                                            | Main text, under "Acoustic Vehicle Alert System (AVAS)" |\n| AVAS has two sound sources: standard and brand.                                                                                             | Main text, under "Acoustic Vehicle Alert System (AVAS)" |\n| To choose a sound source, go to → Vehicle → Notifications.                                                                                    | Main text, under "Acoustic Vehicle Alert System (AVAS)" |\n| If the AVAS prompt sound cannot be heard when driving at a low speed, stop the vehicle in a relatively safe and quiet place.                | WARNING (bottom left)                             |\n| Open a window, then drive at a constant speed of 20 km/h in D gear and check whether an audio prompt can be heard from the front of the vehicle. | WARNING (top right)                               |\n| If it is confirmed that there is no sound, contact a BYD authorized dealer or service provider to deal with it.                              | WARNING (top right)                               |\n| Title: Panoramic View\\* | Main text                                         |\n| To enable the panoramic view, tap Vehicle View on the infotainment system homepage, press the button on the steering wheel or shift into Reverse. | Main text, under "Panoramic View\\*"                |\n| The image shows a steering wheel with a button labeled with a camera icon and "360".                                                        | Image next to "Panoramic View\\*" description      |\n| The steering wheel image has the BYD logo in the center.                                                                                    | Image next to "Panoramic View\\*" description      |\n| Landscape mode: On the bottom of the infotainment touchscreen, tap the icon for front, rear, right, or left view.                           | Main text, under "Panoramic View\\*"                |\n| View of the selected area is displayed in the image section.                                                                                | Main text, under "Panoramic View\\*"                |\n| The image shows an infotainment screen displaying a top-down view of a vehicle on the left and a rear camera view on the right.             | Image under "Landscape mode:"                     |\n| The infotainment screen image shows icons for front view, rear view, left view, right view, 3D view, and settings.                         | Image under "Landscape mode:"                     |\n| The infotainment screen image displays "19:04", "AVM Settings", "Front", "Please watch the surroundings", "P", "AUTO HOLD", "OFF", "A/C OFF". | Image under "Landscape mode:"                     |\n| In the single front and rear views, double-tap the image section.                                                                           | Main text, under "Panoramic View\\*"                |\n| Section Number: 04                                                                                                                          | Right sidebar                                     |\n| Section Title: USING AND DRIVING                                                                                                            | Right sidebar                                     |\n| Page Number: 133                                                                                                                            | Bottom right corner                               |',
            rag_chunk=RagChunk(
                text='| Fact                                                                                                                                        | Source                                            |\n|---------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------|\n| When the low pressure warning light comes on, avoid sharp turns or emergency braking, and reduce vehicle speed.                             | WARNING (top left)                                |\n| Pull it over to the curb and stop as soon as possible.                                                                                      | WARNING (top left)                                |\n| Driving with low tire pressure can cause permanent damage to tires and increase the likelihood of tire scrapping.                           | WARNING (top left)                                |\n| Serious tire damage can lead to traffic accidents, resulting in serious injuries or deaths.                                                 | WARNING (top left)                                |\n| Title: Acoustic Vehicle Alert System (AVAS)                                                                                                 | Main text                                         |\n| Acoustic Vehicle Alerting System (AVAS) refers to the broadcast to pedestrians near the vehicle when it is traveling at low speed.          | Main text, under "Acoustic Vehicle Alert System (AVAS)" |\n| When driving forward: The broadcast volume increases with the increase of vehicle speed in the range of 0 km/h < V ≤ 20 km/h.               | Main text, under "Acoustic Vehicle Alert System (AVAS)" |\n| When driving forward: The broadcast volume decreases with the increase of vehicle speed in the range of 20 km/h < V ≤ 30 km/h.               | Main text, under "Acoustic Vehicle Alert System (AVAS)" |\n| When driving forward: At speeds above 30 km/h, the broadcast sound stops automatically.                                                     | Main text, under "Acoustic Vehicle Alert System (AVAS)" |\n| The vehicle makes a continuous and balanced prompt sound when moving in Reverse.                                                            | Main text, under "Acoustic Vehicle Alert System (AVAS)" |\n| AVAS has two sound sources: standard and brand.                                                                                             | Main text, under "Acoustic Vehicle Alert System (AVAS)" |\n| To choose a sound source, go to → Vehicle → Notifications.                                                                                    | Main text, under "Acoustic Vehicle Alert System (AVAS)" |\n| If the AVAS prompt sound cannot be heard when driving at a low speed, stop the vehicle in a relatively safe and quiet place.                | WARNING (bottom left)                             |\n| Open a window, then drive at a constant speed of 20 km/h in D gear and check whether an audio prompt can be heard from the front of the vehicle. | WARNING (top right)                               |\n| If it is confirmed that there is no sound, contact a BYD authorized dealer or service provider to deal with it.                              | WARNING (top right)                               |\n| Title: Panoramic View\\* | Main text                                         |\n| To enable the panoramic view, tap Vehicle View on the infotainment system homepage, press the button on the steering wheel or shift into Reverse. | Main text, under "Panoramic View\\*"                |\n| The image shows a steering wheel with a button labeled with a camera icon and "360".                                                        | Image next to "Panoramic View\\*" description      |\n| The steering wheel image has the BYD logo in the center.                                                                                    | Image next to "Panoramic View\\*" description      |\n| Landscape mode: On the bottom of the infotainment touchscreen, tap the icon for front, rear, right, or left view.                           | Main text, under "Panoramic View\\*"                |\n| View of the selected area is displayed in the image section.                                                                                | Main text, under "Panoramic View\\*"                |\n| The image shows an infotainment screen displaying a top-down view of a vehicle on the left and a rear camera view on the right.             | Image under "Landscape mode:"                     |\n| The infotainment screen image shows icons for front view, rear view, left view, right view, 3D view, and settings.                         | Image under "Landscape mode:"                     |\n| The infotainment screen image displays "19:04", "AVM Settings", "Front", "Please watch the surroundings", "P", "AUTO HOLD", "OFF", "A/C OFF". | Image under "Landscape mode:"                     |\n| In the single front and rear views, double-tap the image section.                                                                           | Main text, under "Panoramic View\\*"                |\n| Section Number: 04                                                                                                                          | Right sidebar                                     |\n| Section Title: USING AND DRIVING                                                                                                            | Right sidebar                                     |\n| Page Number: 133                                                                                                                            | Bottom right corner                               |',
                page_span=RagChunk.PageSpan(first_page=14, last_page=14),
            ),
        )
    ),
    content.GroundingChunk(
        retrieved_context=content.GroundingChunk.RetrievedContext(
            uri="gs://sample-gcs-directory/file2.pdf",
            title="file2.pdf",
            text='",\n    "source": "Third bullet point under the \'WARNING\' title on the right side of the page."\n  },\n  {\n    "fact": "When no camera is available, a \\"No video signal detected\\" message is displayed.",\n    "source": "Fourth bullet point under the \'WARNING\' title on the right side of the page."\n  },\n  {\n    "fact": "Reversing Radar Power Switch",\n    "source": "Title of the section below the \'WARNING\' box on the right side of the page."\n  },\n  {\n    "fact": "You can enable or disable the reversing radar with the switch* or in Home icon → ADAS → Parking Assist → Reversing Radar.",\n    "source": "First bullet point under the \'Reversing Radar Power Switch\' title. (Note: The \'Home icon\' is represented by an image of a house with an arrow.)"\n  },\n  {\n    "fact": "When the ignition is switched on, the parking assist system is enabled automatically.",\n    "source": "Second bullet point under the \'Reversing Radar Power Switch\' title."\n  },\n  {\n    "fact": "An image shows a close-up of a car\'s center console, highlighting a button with a car icon and radiating lines, labeled \'P\'. A blue circle with an arrow points to this button.",\n    "source": "Image below the \'Reversing Radar Power Switch\' section."\n  },\n  {\n    "fact": "When the parking assist system is enabled, the vehicle is not in \\"P\\", and the Electronic Parking Brake (EPB) and Auto Vehicle Hold (AVH) are released, the obstacle detection mode of the parking assist system is enabled.",\n    "source": "First part of the bullet point below the image on the right side of the page."\n  },\n  {\n    "fact": "When enabled, the system raises an alarm if obstacles are found surrounding the vehicle; when disabled, it does not.",\n    "source": "Second part of the bullet point below the image on the right side of the page."\n  },\n  {\n    "fact": "135",\n    "source": "Page number at the bottom right of the page."\n  }\n]',
            rag_chunk=RagChunk(
                text='",\n    "source": "Third bullet point under the \'WARNING\' title on the right side of the page."\n  },\n  {\n    "fact": "When no camera is available, a \\"No video signal detected\\" message is displayed.",\n    "source": "Fourth bullet point under the \'WARNING\' title on the right side of the page."\n  },\n  {\n    "fact": "Reversing Radar Power Switch",\n    "source": "Title of the section below the \'WARNING\' box on the right side of the page."\n  },\n  {\n    "fact": "You can enable or disable the reversing radar with the switch* or in Home icon → ADAS → Parking Assist → Reversing Radar.",\n    "source": "First bullet point under the \'Reversing Radar Power Switch\' title. (Note: The \'Home icon\' is represented by an image of a house with an arrow.)"\n  },\n  {\n    "fact": "When the ignition is switched on, the parking assist system is enabled automatically.",\n    "source": "Second bullet point under the \'Reversing Radar Power Switch\' title."\n  },\n  {\n    "fact": "An image shows a close-up of a car\'s center console, highlighting a button with a car icon and radiating lines, labeled \'P\'. A blue circle with an arrow points to this button.",\n    "source": "Image below the \'Reversing Radar Power Switch\' section."\n  },\n  {\n    "fact": "When the parking assist system is enabled, the vehicle is not in \\"P\\", and the Electronic Parking Brake (EPB) and Auto Vehicle Hold (AVH) are released, the obstacle detection mode of the parking assist system is enabled.",\n    "source": "First part of the bullet point below the image on the right side of the page."\n  },\n  {\n    "fact": "When enabled, the system raises an alarm if obstacles are found surrounding the vehicle; when disabled, it does not.",\n    "source": "Second part of the bullet point below the image on the right side of the page."\n  },\n  {\n    "fact": "135",\n    "source": "Page number at the bottom right of the page."\n  }\n]',
                page_span=RagChunk.PageSpan(first_page=16, last_page=16),
            ),
        )
    ),
    content.GroundingChunk(
        retrieved_context=content.GroundingChunk.RetrievedContext(
            uri="gs://sample-gcs-directory/file2.pdf",
            title="file2.pdf",
            text='```json\n[\n  {\n    "fact": "04",\n    "source": "Top right corner of the page, within a black box."\n  },\n  {\n    "fact": "USING AND DRIVING",\n    "source": "Vertically aligned text on the right side of the page, next to the \'04\' box."\n  },\n  {\n    "fact": "WARNING",\n    "source": "Title of the first grey box on the left side of the page."\n  },\n  {\n    "fact": "After the vehicle is powered on, if you press the panoramic view start button or shift into reverse while the infotainment system is not fully activated, the output on the panoramic view screen will be delayed or the screen will flash.",\n    "source": "First bullet point under the \'WARNING\' title on the left side of the page."\n  },\n  {\n    "fact": "This is a normal part of the camera power-on process.",\n    "source": "Sub-statement within the first bullet point under the \'WARNING\' title on the left side of the page."\n  },\n  {\n    "fact": "When the vehicle runs at a low speed, the transparent panoramic view function is affected by speed fluctuation or multiple stops, so there will be misalignment between the images below the vehicle and that outside the vehicle.",\n    "source": "Second bullet point under the \'WARNING\' title on the left side of the page."\n  },\n  {\n    "fact": "Parking Assist System",\n    "source": "Title of the section below the first \'WARNING\' box on the left side of the page."\n  },\n  {\n    "fact": "During vehicle parking, the parking assist system detects obstacles by sensors, and prompts the driver with the proximity of obstacles by an image on the infotainment touchscreen* and a speaker alarm.",\n    "source": "First bullet point under the \'Parking Assist System\' title."\n  },\n  {\n    "fact": "The parking assist system helps with reversing.",\n    "source": "Second bullet point under the \'Parking Assist System\' title."\n  },\n  {\n    "fact": "Pay attention to the environment behind and around the vehicle during reversing.",\n    "source": "Sub-statement within the second bullet point under the \'Parking Assist System\' title."\n  },\n  {\n    "fact": "When you reverse the vehicle, a reversing image will be displayed on the infotainment touchscreen automatically.",\n    "source": "Third bullet point under the \'Parking Assist System\' title."\n  },\n  {\n    "fact": "For your driving safety, when the reversing image is displayed, all buttons will be disabled except some volume and calls-related buttons.",\n    "source": "Fourth bullet point under the \'Parking Assist System\' title."\n  },\n  {\n    "fact": "After reversing ends, the interface will be restored.",\n    "source": "Fifth bullet point under the \'Parking Assist System\' title."\n  },\n  {\n    "fact": "WARNING",\n    "source": "Title of the grey box on the right side of the page."\n  },\n  {\n    "fact": "The parking assist system ceases to operate when the vehicle speed is over 10 km/h.",\n    "source": "First bullet point under the \'WARNING\' title on the right side of the page."\n  },\n  {\n    "fact": "Do not place any articles within the sensors\' working range.",\n    "source": "Second bullet point under the \'WARNING\' title on the right side of the page."\n  },\n  {\n    "fact": "To prevent sensor malfunction, do not wash the sensor area with water or steam.",\n    "source": "Third bullet point under the \'WARNING\' title on the right side of the page."\n  },\n  {\n    "fact": "When no camera is available, a \\"No video signal detected\\" message is displayed.",\n    "source": "Fourth bullet point under the \'WARNING\' title on the right side of the page."\n  },\n  {\n    "fact": "Reversing Radar Power Switch",\n    "source": "Title of the section below the \'WARNING\' box on the right side of the page."\n  },\n  {\n    "fact": "You can enable or disable the reversing radar with the switch* or in Home icon → ADAS → Parking Assist → Reversing Radar.",\n    "source": "First bullet point under the \'Reversing Radar Power Switch\' title. (Note: The \'Home icon\' is represented by an image of a house with an arrow.)"',
            rag_chunk=RagChunk(
                text='```json\n[\n  {\n    "fact": "04",\n    "source": "Top right corner of the page, within a black box."\n  },\n  {\n    "fact": "USING AND DRIVING",\n    "source": "Vertically aligned text on the right side of the page, next to the \'04\' box."\n  },\n  {\n    "fact": "WARNING",\n    "source": "Title of the first grey box on the left side of the page."\n  },\n  {\n    "fact": "After the vehicle is powered on, if you press the panoramic view start button or shift into reverse while the infotainment system is not fully activated, the output on the panoramic view screen will be delayed or the screen will flash.",\n    "source": "First bullet point under the \'WARNING\' title on the left side of the page."\n  },\n  {\n    "fact": "This is a normal part of the camera power-on process.",\n    "source": "Sub-statement within the first bullet point under the \'WARNING\' title on the left side of the page."\n  },\n  {\n    "fact": "When the vehicle runs at a low speed, the transparent panoramic view function is affected by speed fluctuation or multiple stops, so there will be misalignment between the images below the vehicle and that outside the vehicle.",\n    "source": "Second bullet point under the \'WARNING\' title on the left side of the page."\n  },\n  {\n    "fact": "Parking Assist System",\n    "source": "Title of the section below the first \'WARNING\' box on the left side of the page."\n  },\n  {\n    "fact": "During vehicle parking, the parking assist system detects obstacles by sensors, and prompts the driver with the proximity of obstacles by an image on the infotainment touchscreen* and a speaker alarm.",\n    "source": "First bullet point under the \'Parking Assist System\' title."\n  },\n  {\n    "fact": "The parking assist system helps with reversing.",\n    "source": "Second bullet point under the \'Parking Assist System\' title."\n  },\n  {\n    "fact": "Pay attention to the environment behind and around the vehicle during reversing.",\n    "source": "Sub-statement within the second bullet point under the \'Parking Assist System\' title."\n  },\n  {\n    "fact": "When you reverse the vehicle, a reversing image will be displayed on the infotainment touchscreen automatically.",\n    "source": "Third bullet point under the \'Parking Assist System\' title."\n  },\n  {\n    "fact": "For your driving safety, when the reversing image is displayed, all buttons will be disabled except some volume and calls-related buttons.",\n    "source": "Fourth bullet point under the \'Parking Assist System\' title."\n  },\n  {\n    "fact": "After reversing ends, the interface will be restored.",\n    "source": "Fifth bullet point under the \'Parking Assist System\' title."\n  },\n  {\n    "fact": "WARNING",\n    "source": "Title of the grey box on the right side of the page."\n  },\n  {\n    "fact": "The parking assist system ceases to operate when the vehicle speed is over 10 km/h.",\n    "source": "First bullet point under the \'WARNING\' title on the right side of the page."\n  },\n  {\n    "fact": "Do not place any articles within the sensors\' working range.",\n    "source": "Second bullet point under the \'WARNING\' title on the right side of the page."\n  },\n  {\n    "fact": "To prevent sensor malfunction, do not wash the sensor area with water or steam.",\n    "source": "Third bullet point under the \'WARNING\' title on the right side of the page."\n  },\n  {\n    "fact": "When no camera is available, a \\"No video signal detected\\" message is displayed.",\n    "source": "Fourth bullet point under the \'WARNING\' title on the right side of the page."\n  },\n  {\n    "fact": "Reversing Radar Power Switch",\n    "source": "Title of the section below the \'WARNING\' box on the right side of the page."\n  },\n  {\n    "fact": "You can enable or disable the reversing radar with the switch* or in Home icon → ADAS → Parking Assist → Reversing Radar.",\n    "source": "First bullet point under the \'Reversing Radar Power Switch\' title. (Note: The \'Home icon\' is represented by an image of a house with an arrow.)"',
                page_span=RagChunk.PageSpan(first_page=16, last_page=16),
            ),
        )
    ),
    content.GroundingChunk(
        retrieved_context=content.GroundingChunk.RetrievedContext(
            uri="gs://sample-gcs-directory/file2.pdf",
            title="file2.pdf",
            text='| Fact                                                                                                                                | Source                                       |\n|-------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------|\n| **Table: Alarm Indication** |                                              |\n| Approximate Distance (mm): About 200 to 400                                                                                         | Table Row 1, Column 1                        |\n| Touchscreen Display Example: [Image of a car with detection zones at the rear, specifically showing a red zone directly behind]     | Table Row 1, Column 2                        |\n| Alarm Sound: Continuous                                                                                                             | Table Row 1, Column 3                        |\n| **CAUTION** | Section Title                                |\n| 0~200mm is the blind spot range of the system.                                                                                      | "CAUTION" section                            |\n| For the poor detection accuracy and inaccurate alarm information. the alarm prompts in 0~200m are for reference only                | "CAUTION" section                            |\n| **Working Sensors and Detection Range** | Section Title                                |\n| All sensors are activated upon reversing.                                                                                           | "Working Sensors and Detection Range" section |\n| The illustration shows the sensors\' detection range.                                                                                | "Working Sensors and Detection Range" section |\n| Sensors have a range limitation, so drivers must check the surroundings before slowly reversing the vehicle.                        | "Working Sensors and Detection Range" section |\n| ① About 1,200 mm                                                                                                                    | "Working Sensors and Detection Range" section |\n| ② About 600 mm                                                                                                                    | "Working Sensors and Detection Range" section |\n| Diagram: Shows a side view of a car with detection zone ① extending approximately 1,200 mm behind the vehicle.                       | Diagram under "Working Sensors and Detection Range" |\n| Diagram: Shows a top view of a car with detection zones ① at the rear corners and detection zones ② directly behind the vehicle.    | Diagram under "Working Sensors and Detection Range" |\n| **Error message** | Section Title                                |\n| Failure of the parking radar system is indicated by a message on the instrument cluster and a beep.                                 | "Error message" section                      |\n| Image: Shows a "P" symbol with radar waves and the text "Parking radar failed, please contact BYD service."                         | Image next to "Error message" section         |\n| **! REMINDER** | Section Title                                |\n| The parking assist system is only for assistance, and is not a substitute for personal judgment.                                    | "REMINDER" section, first bullet point       |\n| Be sure to operate the vehicle based on your observations.                                                                          | "REMINDER" section, first bullet point       |\n| Sensors will not work properly if accessories or other objects are placed within their detection range.                               | "REMINDER" section, second bullet point      |\n| In some cases, the system cannot operate properly and will fail to detect certain objects as the vehicle approaches them.           | "REMINDER" section, third bullet point       |\n| Therefore, be sure to observe the vehicle\'s surroundings at all times.                                                              | "REMINDER" section, third bullet point       |\n| Do not rely solely upon the system.                                                                                                 | "REMINDER" section, third bullet point       |\n| **Sensor Detection Information** | Section Title                                |\n| Certain vehicle conditions and surroundings may affect the sensors\' ability to accurately detect obstacles.                         | "Sensor Detection Information" section       |\n| Detection accuracy may be affected if:                                                                                              | "Sensor Detection Information" section       |\n| • There is dirt, water or fog on the sensor.                                                                                        | "Sensor Detection Information" section, bullet point |\n| 04                                                                                                                                  | Top right corner of a grey box             |\n| USING AND DRIVING                                                                                                                   | Text vertically aligned on the right side      |\n| 137                                                                                                                                 | Bottom right corner of the page              |',
            rag_chunk=RagChunk(
                text='| Fact                                                                                                                                | Source                                       |\n|-------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------|\n| **Table: Alarm Indication** |                                              |\n| Approximate Distance (mm): About 200 to 400                                                                                         | Table Row 1, Column 1                        |\n| Touchscreen Display Example: [Image of a car with detection zones at the rear, specifically showing a red zone directly behind]     | Table Row 1, Column 2                        |\n| Alarm Sound: Continuous                                                                                                             | Table Row 1, Column 3                        |\n| **CAUTION** | Section Title                                |\n| 0~200mm is the blind spot range of the system.                                                                                      | "CAUTION" section                            |\n| For the poor detection accuracy and inaccurate alarm information. the alarm prompts in 0~200m are for reference only                | "CAUTION" section                            |\n| **Working Sensors and Detection Range** | Section Title                                |\n| All sensors are activated upon reversing.                                                                                           | "Working Sensors and Detection Range" section |\n| The illustration shows the sensors\' detection range.                                                                                | "Working Sensors and Detection Range" section |\n| Sensors have a range limitation, so drivers must check the surroundings before slowly reversing the vehicle.                        | "Working Sensors and Detection Range" section |\n| ① About 1,200 mm                                                                                                                    | "Working Sensors and Detection Range" section |\n| ② About 600 mm                                                                                                                    | "Working Sensors and Detection Range" section |\n| Diagram: Shows a side view of a car with detection zone ① extending approximately 1,200 mm behind the vehicle.                       | Diagram under "Working Sensors and Detection Range" |\n| Diagram: Shows a top view of a car with detection zones ① at the rear corners and detection zones ② directly behind the vehicle.    | Diagram under "Working Sensors and Detection Range" |\n| **Error message** | Section Title                                |\n| Failure of the parking radar system is indicated by a message on the instrument cluster and a beep.                                 | "Error message" section                      |\n| Image: Shows a "P" symbol with radar waves and the text "Parking radar failed, please contact BYD service."                         | Image next to "Error message" section         |\n| **! REMINDER** | Section Title                                |\n| The parking assist system is only for assistance, and is not a substitute for personal judgment.                                    | "REMINDER" section, first bullet point       |\n| Be sure to operate the vehicle based on your observations.                                                                          | "REMINDER" section, first bullet point       |\n| Sensors will not work properly if accessories or other objects are placed within their detection range.                               | "REMINDER" section, second bullet point      |\n| In some cases, the system cannot operate properly and will fail to detect certain objects as the vehicle approaches them.           | "REMINDER" section, third bullet point       |\n| Therefore, be sure to observe the vehicle\'s surroundings at all times.                                                              | "REMINDER" section, third bullet point       |\n| Do not rely solely upon the system.                                                                                                 | "REMINDER" section, third bullet point       |\n| **Sensor Detection Information** | Section Title                                |\n| Certain vehicle conditions and surroundings may affect the sensors\' ability to accurately detect obstacles.                         | "Sensor Detection Information" section       |\n| Detection accuracy may be affected if:                                                                                              | "Sensor Detection Information" section       |\n| • There is dirt, water or fog on the sensor.                                                                                        | "Sensor Detection Information" section, bullet point |\n| 04                                                                                                                                  | Top right corner of a grey box             |\n| USING AND DRIVING                                                                                                                   | Text vertically aligned on the right side      |\n| 137                                                                                                                                 | Bottom right corner of the page              |',
                page_span=RagChunk.PageSpan(first_page=18, last_page=18),
            ),
        )
    ),
    content.GroundingChunk(
        retrieved_context=content.GroundingChunk.RetrievedContext(
            uri="gs://sample-gcs-directory/file1.pdf",
            title="file1.pdf",
            text='| Fact                                                                                                                               | Source                                    |\n|------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------|\n| Driver Assistance Switches                                                                                                         | Title                                     |\n| The center console also features a reversing radar switch\\*, BSA switch\\*, and AVH switch\\*.                                       | Driver Assistance Switches section        |\n| ① Reversing radar switch\\* | Driver Assistance Switches section        |\n| Press this switch to activate parking radar. See P135 for details.                                                                 | Driver Assistance Switches section        |\n| ② BSA switch\\* | Driver Assistance Switches section        |\n| Press this switch to activate blind spot assist. (See P128 for details).                                                           | Driver Assistance Switches section        |\n| ③ AVH switch\\* | Driver Assistance Switches section        |\n| Press this switch to activate automatic vehicle hold. See P111 for details.                                                        | Driver Assistance Switches section        |\n| Window Control Switch on Passenger Side                                                                                            | Title                                     |\n| When the ignition is on, the window control switches near passengers can be used to roll the associated windows up or down.           | Window Control Switch on Passenger Side section / Top right text |\n| Hazard Warning Light Switch                                                                                                        | Title                                     |\n| When the hazard warning light button is pressed, all turn signals and turn signal indicators on the instrument cluster start flashing. | Hazard Warning Light Switch section       |\n| They all stop flashing when the hazard warning light button is pressed again.                                                        | Hazard Warning Light Switch section       |\n| CAUTION                                                                                                                            | Heading                                   |\n| The hazard warning lights are used to alert drivers and pedestrians of possible risks.                                             | CAUTION section                           |\n| Mode Switches                                                                                                                      | Title                                     |\n| These switches enable drivers to select from the different regenerative braking, snow, and ECO, SPORT or NORMAL modes.             | Mode Switches section                     |\n| 72                                                                                                                                 | Page number                               |\n| An image shows a button on the steering wheel column with three arrows pointing left.                                              | Image under "Driver Assistance Switches"  |\n| An image shows three buttons labeled 1, 2, and 3 on the center console.                                                            | Image under "Driver Assistance Switches"  |\n| Button 1 is labeled "P".                                                                                                           | Image under "Driver Assistance Switches"  |\n| Button 2 is labeled with an icon of a car with waves on its side.                                                                    | Image under "Driver Assistance Switches"  |\n| Button 3 is labeled "AVH".                                                                                                         | Image under "Driver Assistance Switches"  |\n| An image shows a window control switch on the passenger side door with an arrow pointing up and down.                              | Image near "used to roll the associated windows up or down." |\n| An image shows the hazard warning light switch with a red triangle icon.                                                           | Image under "Hazard Warning Light Switch" |',
            rag_chunk=RagChunk(
                text='| Fact                                                                                                                               | Source                                    |\n|------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------|\n| Driver Assistance Switches                                                                                                         | Title                                     |\n| The center console also features a reversing radar switch\\*, BSA switch\\*, and AVH switch\\*.                                       | Driver Assistance Switches section        |\n| ① Reversing radar switch\\* | Driver Assistance Switches section        |\n| Press this switch to activate parking radar. See P135 for details.                                                                 | Driver Assistance Switches section        |\n| ② BSA switch\\* | Driver Assistance Switches section        |\n| Press this switch to activate blind spot assist. (See P128 for details).                                                           | Driver Assistance Switches section        |\n| ③ AVH switch\\* | Driver Assistance Switches section        |\n| Press this switch to activate automatic vehicle hold. See P111 for details.                                                        | Driver Assistance Switches section        |\n| Window Control Switch on Passenger Side                                                                                            | Title                                     |\n| When the ignition is on, the window control switches near passengers can be used to roll the associated windows up or down.           | Window Control Switch on Passenger Side section / Top right text |\n| Hazard Warning Light Switch                                                                                                        | Title                                     |\n| When the hazard warning light button is pressed, all turn signals and turn signal indicators on the instrument cluster start flashing. | Hazard Warning Light Switch section       |\n| They all stop flashing when the hazard warning light button is pressed again.                                                        | Hazard Warning Light Switch section       |\n| CAUTION                                                                                                                            | Heading                                   |\n| The hazard warning lights are used to alert drivers and pedestrians of possible risks.                                             | CAUTION section                           |\n| Mode Switches                                                                                                                      | Title                                     |\n| These switches enable drivers to select from the different regenerative braking, snow, and ECO, SPORT or NORMAL modes.             | Mode Switches section                     |\n| 72                                                                                                                                 | Page number                               |\n| An image shows a button on the steering wheel column with three arrows pointing left.                                              | Image under "Driver Assistance Switches"  |\n| An image shows three buttons labeled 1, 2, and 3 on the center console.                                                            | Image under "Driver Assistance Switches"  |\n| Button 1 is labeled "P".                                                                                                           | Image under "Driver Assistance Switches"  |\n| Button 2 is labeled with an icon of a car with waves on its side.                                                                    | Image under "Driver Assistance Switches"  |\n| Button 3 is labeled "AVH".                                                                                                         | Image under "Driver Assistance Switches"  |\n| An image shows a window control switch on the passenger side door with an arrow pointing up and down.                              | Image near "used to roll the associated windows up or down." |\n| An image shows the hazard warning light switch with a red triangle icon.                                                           | Image under "Hazard Warning Light Switch" |',
                page_span=RagChunk.PageSpan(first_page=73, last_page=73),
            ),
        )
    ),
    content.GroundingChunk(
        retrieved_context=content.GroundingChunk.RetrievedContext(
            uri="gs://sample-gcs-directory/file2.pdf",
            title="file2.pdf",
            text='| Fact                                                                                                                                  | Source                                                               |\n|---------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------|\n| There is snow or frost on the sensor.                                                                                                 | Left column, 1st bullet point                                        |\n| The sensor is masked in any way.                                                                                                      | Left column, 2nd bullet point                                        |\n| The vehicle leans significantly to one side or is overloaded.                                                                         | Left column, 3rd bullet point                                        |\n| The vehicle is moving on particularly bumpy roads, slopes, gravel or grass.                                                           | Left column, 4th bullet point                                        |\n| The sensor has been repainted.                                                                                                        | Left column, 5th bullet point                                        |\n| The vicinity is noisy due to honking of vehicles, motorcycle engines, air brakes of large vehicles, or other noises that produce ultrasonic waves. | Left column, 6th bullet point                                        |\n| There\'s another vehicle with parking assist system nearby.                                                                            | Left column, 7th bullet point                                        |\n| The vehicle is fitted with a tow eye.                                                                                                 | Left column, 8th bullet point                                        |\n| The bumper or the sensor was hit hard.                                                                                                | Left column, 9th bullet point                                        |\n| The vehicle is approaching a high or zigzag curb.                                                                                     | Left column, 10th bullet point                                       |\n| The vehicle is driving in the sun or in the cold.                                                                                     | Left column, 11th bullet point                                       |\n| The vehicle is fitted with non-original, lower suspension.                                                                            | Left column, 12th bullet point                                       |\n| Except as described above, sensors may not be able to correctly determine the actual distance due to the shape of the object.         | Left column, paragraph below 12th bullet point                       |\n| The shape and material of obstacles may prevent sensors from detecting them, especially the following:                                  | Left column, paragraph below previous fact                           |\n| Electric wires, fences, and ropes                                                                                                     | Left column, 1st sub-bullet point under "obstacles"                  |\n| Cotton, snow, and other materials that absorb radio waves                                                                             | Left column, 2nd sub-bullet point under "obstacles"                 |\n| Any object with sharp edges and corners                                                                                               | Left column, 3rd sub-bullet point under "obstacles"                 |\n| Low obstacles                                                                                                                         | Left column, 4th sub-bullet point under "obstacles"                 |\n| High obstacles facing outwards towards the vehicle                                                                                    | Left column, 5th sub-bullet point under "obstacles"                 |\n| Any object under the bumper                                                                                                           | Right column, 1st bullet point                                       |\n| Any object close to the vehicle                                                                                                       | Right column, 2nd bullet point                                       |\n| Persons near the vehicle (depending on the type of clothing)                                                                          | Right column, 3rd bullet point                                       |\n| If an image is displayed on the infotainment touchscreen* or there is a beep, it may be that the sensor detects an obstacle or is interfered. | Right column, paragraph below 3rd bullet point                       |\n| If the issue persists, go to a BYD authorized dealer or service provider for inspection.                                              | Right column, continuation of paragraph below 3rd bullet point       |\n| CAUTION                                                                                                                               | Right column, heading of caution box                                 |\n| To prevent sensor malfunction, do not rinse or apply steam to the sensor area.                                                        | Right column, bullet point within caution box                        |\n| Driving Safety Systems                                                                                                                | Right column, main heading                                           |\n| For better driving safety, the following driving safety systems works automatically based on driving conditions.                        | Right column, paragraph under "Driving Safety Systems"               |\n| However, these systems only provide assistance, and excessive reliance on them is not recommended.                                    | Right column, continuation of paragraph under "Driving Safety Systems" |\n| Intelligent Power Braking System                                                                                                      | Right column, sub-heading                                            |\n| The intelligent power braking system is an advanced decoupled electrohydraulic brake system integrating vacuum booster, electronic vacuum pump, Antilock Braking System (ABS), Electronic Stability Controller (ESC) system and other features. | Right column, 1st bullet point under "Intelligent Power Braking System" |\n| The system assists vehicle braking according to the driver\'s demands and improves vehicle stability, comfort, and the recovery efficiency of brake energy."\n',
            rag_chunk=RagChunk(
                text='| Fact                                                                                                                                  | Source                                                               |\n|---------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------|\n| There is snow or frost on the sensor.                                                                                                 | Left column, 1st bullet point                                        |\n| The sensor is masked in any way.                                                                                                      | Left column, 2nd bullet point                                        |\n| The vehicle leans significantly to one side or is overloaded.                                                                         | Left column, 3rd bullet point                                        |\n| The vehicle is moving on particularly bumpy roads, slopes, gravel or grass.                                                           | Left column, 4th bullet point                                        |\n| The sensor has been repainted.                                                                                                        | Left column, 5th bullet point                                        |\n| The vicinity is noisy due to honking of vehicles, motorcycle engines, air brakes of large vehicles, or other noises that produce ultrasonic waves. | Left column, 6th bullet point                                        |\n| There\'s another vehicle with parking assist system nearby.                                                                            | Left column, 7th bullet point                                        |\n| The vehicle is fitted with a tow eye.                                                                                                 | Left column, 8th bullet point                                        |\n| The bumper or the sensor was hit hard.                                                                                                | Left column, 9th bullet point                                        |\n| The vehicle is approaching a high or zigzag curb.                                                                                     | Left column, 10th bullet point                                       |\n| The vehicle is driving in the sun or in the cold.                                                                                     | Left column, 11th bullet point                                       |\n| The vehicle is fitted with non-original, lower suspension.                                                                            | Left column, 12th bullet point                                       |\n| Except as described above, sensors may not be able to correctly determine the actual distance due to the shape of the object.         | Left column, paragraph below 12th bullet point                       |\n| The shape and material of obstacles may prevent sensors from detecting them, especially the following:                                  | Left column, paragraph below previous fact                           |\n| Electric wires, fences, and ropes                                                                                                     | Left column, 1st sub-bullet point under "obstacles"                  |\n| Cotton, snow, and other materials that absorb radio waves                                                                             | Left column, 2nd sub-bullet point under "obstacles"                 |\n| Any object with sharp edges and corners                                                                                               | Left column, 3rd sub-bullet point under "obstacles"                 |\n| Low obstacles                                                                                                                         | Left column, 4th sub-bullet point under "obstacles"                 |\n| High obstacles facing outwards towards the vehicle                                                                                    | Left column, 5th sub-bullet point under "obstacles"                 |\n| Any object under the bumper                                                                                                           | Right column, 1st bullet point                                       |\n| Any object close to the vehicle                                                                                                       | Right column, 2nd bullet point                                       |\n| Persons near the vehicle (depending on the type of clothing)                                                                          | Right column, 3rd bullet point                                       |\n| If an image is displayed on the infotainment touchscreen* or there is a beep, it may be that the sensor detects an obstacle or is interfered. | Right column, paragraph below 3rd bullet point                       |\n| If the issue persists, go to a BYD authorized dealer or service provider for inspection.                                              | Right column, continuation of paragraph below 3rd bullet point       |\n| CAUTION                                                                                                                               | Right column, heading of caution box                                 |\n| To prevent sensor malfunction, do not rinse or apply steam to the sensor area.                                                        | Right column, bullet point within caution box                        |\n| Driving Safety Systems                                                                                                                | Right column, main heading                                           |\n| For better driving safety, the following driving safety systems works automatically based on driving conditions.                        | Right column, paragraph under "Driving Safety Systems"               |\n| However, these systems only provide assistance, and excessive reliance on them is not recommended.                                    | Right column, continuation of paragraph under "Driving Safety Systems" |\n| Intelligent Power Braking System                                                                                                      | Right column, sub-heading                                            |\n| The intelligent power braking system is an advanced decoupled electrohydraulic brake system integrating vacuum booster, electronic vacuum pump, Antilock Braking System (ABS), Electronic Stability Controller (ESC) system and other features. | Right column, 1st bullet point under "Intelligent Power Braking System" |\n| The system assists vehicle braking according to the driver\'s demands and improves vehicle stability, comfort, and the recovery efficiency of brake energy."\n',
                page_span=RagChunk.PageSpan(first_page=19, last_page=19),
            ),
        )
    ),
    content.GroundingChunk(
        retrieved_context=content.GroundingChunk.RetrievedContext(
            uri="gs://sample-gcs-directory/file1.pdf",
            title="file1.pdf",
            text='```text\n[Fact]: WARNING\n[Source]: Top-left section of the image, red triangle icon.\n\n[Fact]: EPB cannot provide a sufficient parking force.\n[Source]: Text under "WARNING".\n\n[Fact]: Automatic Vehicle Hold (AVH)\n[Source]: Title, below "WARNING".\n\n[Fact]: Automatic vehicle hold (AVH): The automatic vehicle hold (AVH) is activated automatically when the moving vehicle needs to be stationary for longer periods of time, such as in traffic jams on a slope or waiting at traffic lights.\n[Source]: Text below "Automatic Vehicle Hold (AVH)".\n\n[Fact]: AVH standby\n[Source]: Sub-title below the description of AVH.\n\n[Fact]: When the ignition is on, press the AVH switch to enable the function.\n[Source]: First bullet point under "AVH standby".\n\n[Fact]: The AVH standby indicator (AVH) is displayed on the instrument cluster.\n[Source]: First bullet point under "AVH standby". (Note: The icon is depicted as "AVH" with a line through it and a circle around it).\n\n[Fact]: Press the AVH switch again to disable AVH.\n[Source]: Second bullet point under "AVH standby".\n\n[Fact]: Image shows a close-up of a car\'s center console with a button labeled "AVH" highlighted by a blue circle.\n[Source]: Image below "AVH standby".\n\n[Fact]: AVH activated\n[Source]: Sub-title below the image.\n\n[Fact]: When the AVH standby indicator (AVH with a line through it and a circle) is solid on, press and hold the brake pedal until the vehicle stops (vehicle speed reduces to zero) to activate AVH.\n[Source]: Bullet point under "AVH activated".\n\n[Fact]: At this time, the vehicle is in AVH state with (AVH) displayed on the instrument cluster.\n[Source]: Bullet point under "AVH activated". (Note: The icon is depicted as "AVH" in a circle).\n\n[Fact]: CAUTION\n[Source]: Top-right section of the image, yellow triangle icon.\n\n[Fact]: For AVH to be activated, all of the follow conditions must be met:\n[Source]: First bullet point under "CAUTION".\n\n[Fact]: The driver\'s seat belt is fastened and the doors are closed.\n[Source]: Sub-bullet point under the first bullet point of "CAUTION".\n\n[Fact]: Intelligent power braking system and electronic park brake (EPB) systems are normal.\n[Source]: Sub-bullet point under the first bullet point of "CAUTION".\n\n[Fact]: Pressing the accelerator pedal, shifting into Park, or engaging the EPB manually can make AVH exit to the standby status.\n[Source]: Second bullet point under "CAUTION".\n\n[Fact]: The AVH is off by factory default.\n[Source]: Third bullet point under "CAUTION".\n\n[Fact]: AVH running\n[Source]: Sub-title below "CAUTION".\n\n[Fact]: The AVH function runs normally when it is activated, brake lights and the high-mount brake light are on, and the AVH indicator (AVH in a circle) is solid on on the instrument cluster.\n[Source]: First bullet point under "AVH running".\n\n[Fact]: The AVH function exits to the standby mode after the vehicle stops for 10 minutes, with the AVH standby indicator (AVH with a line through it and a circle) lighting up and gear shifted into Park.\n[Source]: Second bullet point under "AVH running".\n\n[Fact]: Shift into “D”, drive the vehicle normally, then press and hold the brake pedal until the vehicle stops (vehicle speed reduces to zero) to activate AVH.\n[Source]: Third bullet point under "AVH running".\n\n[Fact]: AVH exits\n[Source]: Sub-title below "AVH running".\n\n[Fact]: When the AVH function runs normally, the following actions make AVH exit and shift the vehicle from Drive to Park automatically:\n[Source]: Introductory sentence under "AVH exits".\n\n[Fact]: Open the driver\'s door.\n[Source]: First bullet point under "AVH exits".\n\n[Fact]: Unlock the driver\'s seat belt.\n[Source]: Second bullet point under "AVH exits".\n\n[Fact]: The gear status is in Drive when the vehicle stops, and EPB is enabled.\n[Source]: Third bullet point under "AVH exits".\n\n[Fact]: 04\n[Source]: Black box on the right side of the page.\n\n[Fact]: USING AND DRIVING\n[Source]: Text vertically aligned on the right side of the page, next to "04".\n',
            rag_chunk=RagChunk(
                text='```text\n[Fact]: WARNING\n[Source]: Top-left section of the image, red triangle icon.\n\n[Fact]: EPB cannot provide a sufficient parking force.\n[Source]: Text under "WARNING".\n\n[Fact]: Automatic Vehicle Hold (AVH)\n[Source]: Title, below "WARNING".\n\n[Fact]: Automatic vehicle hold (AVH): The automatic vehicle hold (AVH) is activated automatically when the moving vehicle needs to be stationary for longer periods of time, such as in traffic jams on a slope or waiting at traffic lights.\n[Source]: Text below "Automatic Vehicle Hold (AVH)".\n\n[Fact]: AVH standby\n[Source]: Sub-title below the description of AVH.\n\n[Fact]: When the ignition is on, press the AVH switch to enable the function.\n[Source]: First bullet point under "AVH standby".\n\n[Fact]: The AVH standby indicator (AVH) is displayed on the instrument cluster.\n[Source]: First bullet point under "AVH standby". (Note: The icon is depicted as "AVH" with a line through it and a circle around it).\n\n[Fact]: Press the AVH switch again to disable AVH.\n[Source]: Second bullet point under "AVH standby".\n\n[Fact]: Image shows a close-up of a car\'s center console with a button labeled "AVH" highlighted by a blue circle.\n[Source]: Image below "AVH standby".\n\n[Fact]: AVH activated\n[Source]: Sub-title below the image.\n\n[Fact]: When the AVH standby indicator (AVH with a line through it and a circle) is solid on, press and hold the brake pedal until the vehicle stops (vehicle speed reduces to zero) to activate AVH.\n[Source]: Bullet point under "AVH activated".\n\n[Fact]: At this time, the vehicle is in AVH state with (AVH) displayed on the instrument cluster.\n[Source]: Bullet point under "AVH activated". (Note: The icon is depicted as "AVH" in a circle).\n\n[Fact]: CAUTION\n[Source]: Top-right section of the image, yellow triangle icon.\n\n[Fact]: For AVH to be activated, all of the follow conditions must be met:\n[Source]: First bullet point under "CAUTION".\n\n[Fact]: The driver\'s seat belt is fastened and the doors are closed.\n[Source]: Sub-bullet point under the first bullet point of "CAUTION".\n\n[Fact]: Intelligent power braking system and electronic park brake (EPB) systems are normal.\n[Source]: Sub-bullet point under the first bullet point of "CAUTION".\n\n[Fact]: Pressing the accelerator pedal, shifting into Park, or engaging the EPB manually can make AVH exit to the standby status.\n[Source]: Second bullet point under "CAUTION".\n\n[Fact]: The AVH is off by factory default.\n[Source]: Third bullet point under "CAUTION".\n\n[Fact]: AVH running\n[Source]: Sub-title below "CAUTION".\n\n[Fact]: The AVH function runs normally when it is activated, brake lights and the high-mount brake light are on, and the AVH indicator (AVH in a circle) is solid on on the instrument cluster.\n[Source]: First bullet point under "AVH running".\n\n[Fact]: The AVH function exits to the standby mode after the vehicle stops for 10 minutes, with the AVH standby indicator (AVH with a line through it and a circle) lighting up and gear shifted into Park.\n[Source]: Second bullet point under "AVH running".\n\n[Fact]: Shift into “D”, drive the vehicle normally, then press and hold the brake pedal until the vehicle stops (vehicle speed reduces to zero) to activate AVH.\n[Source]: Third bullet point under "AVH running".\n\n[Fact]: AVH exits\n[Source]: Sub-title below "AVH running".\n\n[Fact]: When the AVH function runs normally, the following actions make AVH exit and shift the vehicle from Drive to Park automatically:\n[Source]: Introductory sentence under "AVH exits".\n\n[Fact]: Open the driver\'s door.\n[Source]: First bullet point under "AVH exits".\n\n[Fact]: Unlock the driver\'s seat belt.\n[Source]: Second bullet point under "AVH exits".\n\n[Fact]: The gear status is in Drive when the vehicle stops, and EPB is enabled.\n[Source]: Third bullet point under "AVH exits".\n\n[Fact]: 04\n[Source]: Black box on the right side of the page.\n\n[Fact]: USING AND DRIVING\n[Source]: Text vertically aligned on the right side of the page, next to "04".\n',
                page_span=RagChunk.PageSpan(first_page=112, last_page=112),
            ),
        )
    ),
    content.GroundingChunk(
        retrieved_context=content.GroundingChunk.RetrievedContext(
            uri="gs://sample-gcs-directory/file1.pdf",
            title="file1.pdf",
            text='```json\n[\n  {"fact": "Press the brake pedal to stop the vehicle and shift into Park. EPB is engaged automatically.", "source": "Page 1, Left Column, Unheaded section"},\n  {"fact": "Do not release the brake pedal until the indicator on the instrument cluster stops flashing and becomes steady on and the \\"EPB ON\\" message is displayed.", "source": "Page 1, Left Column, Unheaded section"},\n  {"fact": "CAUTION", "source": "Page 1, Left Column, Title of Caution Box"},\n  {"fact": "The EPB is not automatically engaged if you switch off the ignition immediately after pressing the EPB switch.", "source": "Page 1, Left Column, Caution Box, Bullet 1"},\n  {"fact": "This function may be used for towing or pushing the vehicle after the vehicle breaks down.", "source": "Page 1, Left Column, Caution Box, Bullet 1"},\n  {"fact": "Do not release the brake pedal early in the process, especially when the vehicle is stopped on a slope; otherwise the vehicle may slip back.", "source": "Page 1, Left Column, Caution Box, Bullet 2"},\n  {"fact": "This function is designed to improve vehicle safety.", "source": "Page 1, Left Column, Caution Box, Bullet 3"},\n  {"fact": "Excessive reliance on or frequent use of the function is not recommended.", "source": "Page 1, Left Column, Caution Box, Bullet 3"},\n  {"fact": "For safety reasons, make sure that the vehicle is shifted into \\"P\\" or the EPB is engaged before getting off.", "source": "Page 1, Left Column, Caution Box, Bullet 3"},\n  {"fact": "The EPB system conducts power-up self-check within several seconds after the vehicle is started.", "source": "Page 1, Left Column, Caution Box, Bullet 4"},\n  {"fact": "In this process, the system does not respond to any function.", "source": "Page 1, Left Column, Caution Box, Bullet 4"},\n  {"fact": "Releasing EPB Manually", "source": "Page 1, Left Column, Section Title"},\n  {"fact": "When vehicle has been powered on and is not shifted into P (Park), press and hold the brake pedal and the EPB switch until the indicator on the instrument cluster goes out, indicating EPB has been released, and an \\"EPB released\\" message is displayed.", "source": "Page 1, Left Column, Releasing EPB Manually, Bullet 1"},\n  {"fact": "CAUTION", "source": "Page 1, Right Column, Title of Caution Box"},\n  {"fact": "The P gear is the vehicle\'s parking gear, meaning that the vehicle is in a stable parking status, while EPB is the vehicle\'s main parking device.", "source": "Page 1, Right Column, Caution Box, Bullet 1"},\n  {"fact": "To ensure parking safety, release EPB with the EPB switch only when the vehicle is not in P gear (parking gear).", "source": "Page 1, Right Column, Caution Box, Bullet 1"},\n  {"fact": "Automatic EPB Release upon Vehicle Start", "source": "Page 1, Right Column, Section Title"},\n  {"fact": "With the vehicle parked, start the vehicle, press and hold the brake pedal, and shift from \\"P\\" or \\"N\\" into a driving gear such as \\"D\\" or \\"R\\".", "source": "Page 1, Right Column, Automatic EPB Release upon Vehicle Start, Bullet 1"},\n  {"fact": "EPB is released automatically, the indicator goes off, and the \\"EPB released\\" message is displayed.", "source": "Page 1, Right Column, Automatic EPB Release upon Vehicle Start, Bullet 1"},\n  {"fact": "CAUTION", "source": "Page 1, Right Column, Title of Caution Box"},\n  {"fact": "Be sure to always press and hold the brake pedal when shifting gears.", "source": "Page 1, Right Column, Caution Box, Bullet 1"},\n  {"fact": "Release the pedal only after the intended gear is displayed on the instrument cluster."\n',
            rag_chunk=RagChunk(
                text='```json\n[\n  {"fact": "Press the brake pedal to stop the vehicle and shift into Park. EPB is engaged automatically.", "source": "Page 1, Left Column, Unheaded section"},\n  {"fact": "Do not release the brake pedal until the indicator on the instrument cluster stops flashing and becomes steady on and the \\"EPB ON\\" message is displayed.", "source": "Page 1, Left Column, Unheaded section"},\n  {"fact": "CAUTION", "source": "Page 1, Left Column, Title of Caution Box"},\n  {"fact": "The EPB is not automatically engaged if you switch off the ignition immediately after pressing the EPB switch.", "source": "Page 1, Left Column, Caution Box, Bullet 1"},\n  {"fact": "This function may be used for towing or pushing the vehicle after the vehicle breaks down.", "source": "Page 1, Left Column, Caution Box, Bullet 1"},\n  {"fact": "Do not release the brake pedal early in the process, especially when the vehicle is stopped on a slope; otherwise the vehicle may slip back.", "source": "Page 1, Left Column, Caution Box, Bullet 2"},\n  {"fact": "This function is designed to improve vehicle safety.", "source": "Page 1, Left Column, Caution Box, Bullet 3"},\n  {"fact": "Excessive reliance on or frequent use of the function is not recommended.", "source": "Page 1, Left Column, Caution Box, Bullet 3"},\n  {"fact": "For safety reasons, make sure that the vehicle is shifted into \\"P\\" or the EPB is engaged before getting off.", "source": "Page 1, Left Column, Caution Box, Bullet 3"},\n  {"fact": "The EPB system conducts power-up self-check within several seconds after the vehicle is started.", "source": "Page 1, Left Column, Caution Box, Bullet 4"},\n  {"fact": "In this process, the system does not respond to any function.", "source": "Page 1, Left Column, Caution Box, Bullet 4"},\n  {"fact": "Releasing EPB Manually", "source": "Page 1, Left Column, Section Title"},\n  {"fact": "When vehicle has been powered on and is not shifted into P (Park), press and hold the brake pedal and the EPB switch until the indicator on the instrument cluster goes out, indicating EPB has been released, and an \\"EPB released\\" message is displayed.", "source": "Page 1, Left Column, Releasing EPB Manually, Bullet 1"},\n  {"fact": "CAUTION", "source": "Page 1, Right Column, Title of Caution Box"},\n  {"fact": "The P gear is the vehicle\'s parking gear, meaning that the vehicle is in a stable parking status, while EPB is the vehicle\'s main parking device.", "source": "Page 1, Right Column, Caution Box, Bullet 1"},\n  {"fact": "To ensure parking safety, release EPB with the EPB switch only when the vehicle is not in P gear (parking gear).", "source": "Page 1, Right Column, Caution Box, Bullet 1"},\n  {"fact": "Automatic EPB Release upon Vehicle Start", "source": "Page 1, Right Column, Section Title"},\n  {"fact": "With the vehicle parked, start the vehicle, press and hold the brake pedal, and shift from \\"P\\" or \\"N\\" into a driving gear such as \\"D\\" or \\"R\\".", "source": "Page 1, Right Column, Automatic EPB Release upon Vehicle Start, Bullet 1"},\n  {"fact": "EPB is released automatically, the indicator goes off, and the \\"EPB released\\" message is displayed.", "source": "Page 1, Right Column, Automatic EPB Release upon Vehicle Start, Bullet 1"},\n  {"fact": "CAUTION", "source": "Page 1, Right Column, Title of Caution Box"},\n  {"fact": "Be sure to always press and hold the brake pedal when shifting gears.", "source": "Page 1, Right Column, Caution Box, Bullet 1"},\n  {"fact": "Release the pedal only after the intended gear is displayed on the instrument cluster."\n',
                page_span=RagChunk.PageSpan(first_page=110, last_page=110),
            ),
        )
    ),
    content.GroundingChunk(
        retrieved_context=content.GroundingChunk.RetrievedContext(
            uri="gs://sample-gcs-directory/file1.pdf",
            title="file1.pdf",
            text='```json\n[\n  {"fact": "pedal makes the ACC system exit activation and go on standby.", "source": "Page 1, Column 1, Paragraph 1"},\n  {"fact": "Setting vehicle distance", "source": "Page 1, Column 1, Title"},\n  {"fact": "The driver must select a safe vehicle distance.", "source": "Page 1, Column 1, Setting vehicle distance, Bullet 1"},\n  {"fact": "The system adjusts vehicle speed to keep a suitable distance from the vehicle ahead on the same lane.", "source": "Page 1, Column 1, Setting vehicle distance, Bullet 2"},\n  {"fact": "Pressing buttons ③ and ④ on the steering wheel adjusts vehicle distance to any of the four available levels.", "source": "Page 1, Column 1, Setting vehicle distance, Bullet 2"},\n  {"fact": "At each level, vehicle distance is in direct proportion to vehicle speed.", "source": "Page 1, Column 1, Setting vehicle distance, Bullet 2"},\n  {"fact": "The faster the speed, the longer the distance.", "source": "Page 1, Column 1, Setting vehicle distance, Bullet 2"},\n  {"fact": "Increasing/Decreasing speed with ACC activated", "source": "Page 1, Column 1, Title"},\n  {"fact": "When ACC is activated, you can press the accelerator pedal to reach the set target cruise speed in advance.", "source": "Page 1, Column 1, Increasing/Decreasing speed with ACC activated, Bullet 1"},\n  {"fact": "The system then enters over speed mode.", "source": "Page 1, Column 1, Increasing/Decreasing speed with ACC activated, Bullet 1"},\n  {"fact": "At the target cruise speed, if you accelerate without performing any other operations, the vehicle accelerates and then returns to target cruise speed after the accelerator pedal is released.", "source": "Page 1, Column 1, Increasing/Decreasing speed with ACC activated, Bullet 1"},\n  {"fact": "When you press the brake pedal with ACC activated to slow down the vehicle, ACC goes into standby mode.", "source": "Page 1, Column 1, Increasing/Decreasing speed with ACC activated, Bullet 2"},\n  {"fact": "After the brake pedal is released, ACC needs to be reactivated by pressing the button.", "source": "Page 1, Column 1, Increasing/Decreasing speed with ACC activated, Bullet 2"},\n  {"fact": "Follow-to-stop/start", "source": "Page 1, Column 1, Title"},\n  {"fact": "Controlled by ACC, the vehicle can stop when the vehicle ahead stops in normal driving conditions and resume driving automatically following the vehicle ahead if the stop is less than 30 seconds.", "source": "Page 1, Column 1, Follow-to-stop/start, Bullet 1"},\n  {"fact": "If the vehicle stops for 30 seconds to three minutes, press the accelerator pedal or toggle the rocker switch ② to start the vehicle.", "source": "Page 1, Column 1, Follow-to-stop/start, Bullet 2"},\n  {"fact": "System Limitations", "source": "Page 1, Column 2, Title"},\n  {"fact": "The front mmWave radars are installed in the front of the vehicle.", "source": "Page 1, Column 2, System Limitations, Bullet 1"},\n  {"fact": "Blockage of its detection area by contaminants can disturb the intended function.", "source": "Page 1, Column 2, System Limitations, Bullet 1"},\n  {"fact": "In particular, if the sensor is covered by snow completely, the ACC system exits and informs of this on the instrument cluster.", "source": "Page 1, Column 2, System Limitations, Bullet 1"},\n  {"fact": "System function will recover after blockage is removed and the vehicle is restarted or runs on normal roads for a while.", "source": "Page 1, Column 2, System Limitations, Bullet 1"},\n  {"fact": "Front mmWave radar sensors may have a transient function failure from limited detection if the vehicle runs under special conditions, such as circular parking lots or tunnels, for an extended period."\n',
            rag_chunk=RagChunk(
                text='```json\n[\n  {"fact": "pedal makes the ACC system exit activation and go on standby.", "source": "Page 1, Column 1, Paragraph 1"},\n  {"fact": "Setting vehicle distance", "source": "Page 1, Column 1, Title"},\n  {"fact": "The driver must select a safe vehicle distance.", "source": "Page 1, Column 1, Setting vehicle distance, Bullet 1"},\n  {"fact": "The system adjusts vehicle speed to keep a suitable distance from the vehicle ahead on the same lane.", "source": "Page 1, Column 1, Setting vehicle distance, Bullet 2"},\n  {"fact": "Pressing buttons ③ and ④ on the steering wheel adjusts vehicle distance to any of the four available levels.", "source": "Page 1, Column 1, Setting vehicle distance, Bullet 2"},\n  {"fact": "At each level, vehicle distance is in direct proportion to vehicle speed.", "source": "Page 1, Column 1, Setting vehicle distance, Bullet 2"},\n  {"fact": "The faster the speed, the longer the distance.", "source": "Page 1, Column 1, Setting vehicle distance, Bullet 2"},\n  {"fact": "Increasing/Decreasing speed with ACC activated", "source": "Page 1, Column 1, Title"},\n  {"fact": "When ACC is activated, you can press the accelerator pedal to reach the set target cruise speed in advance.", "source": "Page 1, Column 1, Increasing/Decreasing speed with ACC activated, Bullet 1"},\n  {"fact": "The system then enters over speed mode.", "source": "Page 1, Column 1, Increasing/Decreasing speed with ACC activated, Bullet 1"},\n  {"fact": "At the target cruise speed, if you accelerate without performing any other operations, the vehicle accelerates and then returns to target cruise speed after the accelerator pedal is released.", "source": "Page 1, Column 1, Increasing/Decreasing speed with ACC activated, Bullet 1"},\n  {"fact": "When you press the brake pedal with ACC activated to slow down the vehicle, ACC goes into standby mode.", "source": "Page 1, Column 1, Increasing/Decreasing speed with ACC activated, Bullet 2"},\n  {"fact": "After the brake pedal is released, ACC needs to be reactivated by pressing the button.", "source": "Page 1, Column 1, Increasing/Decreasing speed with ACC activated, Bullet 2"},\n  {"fact": "Follow-to-stop/start", "source": "Page 1, Column 1, Title"},\n  {"fact": "Controlled by ACC, the vehicle can stop when the vehicle ahead stops in normal driving conditions and resume driving automatically following the vehicle ahead if the stop is less than 30 seconds.", "source": "Page 1, Column 1, Follow-to-stop/start, Bullet 1"},\n  {"fact": "If the vehicle stops for 30 seconds to three minutes, press the accelerator pedal or toggle the rocker switch ② to start the vehicle.", "source": "Page 1, Column 1, Follow-to-stop/start, Bullet 2"},\n  {"fact": "System Limitations", "source": "Page 1, Column 2, Title"},\n  {"fact": "The front mmWave radars are installed in the front of the vehicle.", "source": "Page 1, Column 2, System Limitations, Bullet 1"},\n  {"fact": "Blockage of its detection area by contaminants can disturb the intended function.", "source": "Page 1, Column 2, System Limitations, Bullet 1"},\n  {"fact": "In particular, if the sensor is covered by snow completely, the ACC system exits and informs of this on the instrument cluster.", "source": "Page 1, Column 2, System Limitations, Bullet 1"},\n  {"fact": "System function will recover after blockage is removed and the vehicle is restarted or runs on normal roads for a while.", "source": "Page 1, Column 2, System Limitations, Bullet 1"},\n  {"fact": "Front mmWave radar sensors may have a transient function failure from limited detection if the vehicle runs under special conditions, such as circular parking lots or tunnels, for an extended period."\n',
                page_span=RagChunk.PageSpan(first_page=116, last_page=116),
            ),
        )
    ),
    content.GroundingChunk(
        retrieved_context=content.GroundingChunk.RetrievedContext(
            uri="gs://sample-gcs-directory/file2.pdf",
            title="file2.pdf",
            text="| Factual Statement                                                              | Page Number |\n| ------------------------------------------------------------------------------- | ----------- |\n| If a Tire Goes Flat                                                             | 190         |\n| If Smart Key Battery Is Exhausted                                               | 186         |\n| If the Vehicle Needs Towing                                                     | 188         |\n| Indicators and Warning Lights                                                   | 35          |\n| Infotainment Touchscreen                                                        | 148         |\n| Installing Child Restraint Systems                                              | 22          |\
| Intelligent Cruise Control (ICC)\\* | 117         |\n| Intelligent Speed Limit Control (ISLC)                                          | 123         |\n| Interior Cleaning                                                               | 173         |\n| Predictive Collision Warning (PCW) & Automatic Emergency Braking (AEB)        | 119         |\
| Regular Maintenance                                                             | 170         |\n| Releasing EPB Manually                                                          | 109         |\n| Saving Energy and Extending Vehicle Service Life                                | 100         |\n| Scheduled Charging                                                              | 88          |\n| LCD Instrument Cluster                                                          | 34          |\n| Seat Belt Overview                                                              | 12          |\n| Light Switches                                                                  | 64          |\n| Seatback Pockets                                                                | 161         |\n| Locking/Unlocking with Mechanical Key                                           | 48          |\n| Seats                                                                           | 57          |\n| Self-Maintenance                                                                | 174         |\n| Low-Voltage Battery                                                             | 96          |\n| Side Mirror Adjustment                                                          | 143         |\n| Smart Access and Start System                                                   | 55          |\n| Snow Chains                                                                     | 104         |\n| Maintenance Plan                                                                | 168         |\n| Starting the Vehicle                                                            | 105         |\n| Steering Assist Mode Settings                                                   | 63          |\n| Maintenance Schedule Requirements                                               | 168         |\n| Steering Wheel Switches                                                         | 60          |\n| Suggestions for Vehicle Use                                                     | 99          |\n| Maintenance System\\* | 170         |\n| Sun Visor                                                                       | 162         |\n| Manual Vehicle Washing                                                          | 172         |\n| Sunroof Maintenance                                                             | 176         |\n| Mode Switches                                                                   | 72          |\n| Sunroof Switch                                                                  | 75          |\n| Switching on A/C with Cloud Service App                                         | 157         |\n| Odometer Switch                                                                 | 71          |\n| Opening the Hood                                                                | 178         |\n| Ordinary Sunroof Maintenance\\* | 177         |\n| Tire Pressure Monitoring                                                        | 131         |\n| Tires                                                                           | 181         |\n| Traffic Sign Recognition (TSR)                                                  | 122         |\n| Trailer Towing                                                                  | 98          |\n| Paint Maintenance Tips                                                          | 171         |\n| Transponder Mounting                                                            | 201         |\n| Panoramic View System\\* | 133         |\n| Parking Assist System\\* | 135         |\n| USB Ports                                                                       | 162         |\n| Using Seat Belts                                                                | 12          |\n| Page Number at the bottom of the document                                       | 206         |",
            rag_chunk=RagChunk(
                text="| Factual Statement                                                              | Page Number |\n| ------------------------------------------------------------------------------- | ----------- |\n| If a Tire Goes Flat                                                             | 190         |\n| If Smart Key Battery Is Exhausted                                               | 186         |\n| If the Vehicle Needs Towing                                                     | 188         |\n| Indicators and Warning Lights                                                   | 35          |\n| Infotainment Touchscreen                                                        | 148         |\n| Installing Child Restraint Systems                                              | 22          |\n| Intelligent Cruise Control (ICC)\\* | 117         |\n| Intelligent Speed Limit Control (ISLC)                                          | 123         |\n| Interior Cleaning                                                               | 173         |\n| Predictive Collision Warning (PCW) & Automatic Emergency Braking (AEB)        | 119         |\n| Regular Maintenance                                                             | 170         |\n| Releasing EPB Manually                                                          | 109         |\n| Saving Energy and Extending Vehicle Service Life                                | 100         |\n| Scheduled Charging                                                              | 88          |\n| LCD Instrument Cluster                                                          | 34          |\n| Seat Belt Overview                                                              | 12          |\n| Light Switches                                                                  | 64          |\n| Seatback Pockets                                                                | 161         |\n| Locking/Unlocking with Mechanical Key                                           | 48          |\n| Seats                                                                           | 57          |\n| Self-Maintenance                                                                | 174         |\n| Low-Voltage Battery                                                             | 96          |\n| Side Mirror Adjustment                                                          | 143         |\n| Smart Access and Start System                                                   | 55          |\n| Snow Chains                                                                     | 104         |\n| Maintenance Plan                                                                | 168         |\n| Starting the Vehicle                                                            | 105         |\n| Steering Assist Mode Settings                                                   | 63          |\n| Maintenance Schedule Requirements                                               | 168         |\n| Steering Wheel Switches                                                         | 60          |\n| Suggestions for Vehicle Use                                                     | 99          |\n| Maintenance System\\* | 170         |\n| Sun Visor                                                                       | 162         |\n| Manual Vehicle Washing                                                          | 172         |\n| Sunroof Maintenance                                                             | 176         |\n| Mode Switches                                                                   | 72          |\n| Sunroof Switch                                                                  | 75          |\n| Switching on A/C with Cloud Service App                                         | 157         |\n| Odometer Switch                                                                 | 71          |\n| Opening the Hood                                                                | 178         |\n| Ordinary Sunroof Maintenance\\* | 177         |\n| Tire Pressure Monitoring                                                        | 131         |\n| Tires                                                                           | 181         |\n| Traffic Sign Recognition (TSR)                                                  | 122         |\n| Trailer Towing                                                                  | 98          |\n| Paint Maintenance Tips                                                          | 171         |\n| Transponder Mounting                                                            | 201         |\n| Panoramic View System\\* | 133         |\n| Parking Assist System\\* | 135         |\n| USB Ports                                                                       | 162         |\n| Using Seat Belts                                                                | 12          |\n| Page Number at the bottom of the document                                       | 206         |",
                page_span=RagChunk.PageSpan(first_page=87, last_page=87),
            ),
        )
    ),
    content.GroundingChunk(
        retrieved_context=content.GroundingChunk.RetrievedContext(
            uri="gs://sample-gcs-directory/file1.pdf",
            title="file1.pdf",
            text='```text\n[Factual Statement]: If the shift is successful, the lever returns to its middle position after it is released.\n[Source]: Page 1, Left Column, First Bullet Point\n\n[Factual Statement]: To prevent unintended vehicle movement, press the "P" button and engage EPB once the vehicle has stopped completely.\n[Source]: Page 1, Left Column, Second Bullet Point\n\n[Factual Statement]: At this time, the EPB indicator turns on.\n[Source]: Page 1, Left Column, Second Bullet Point\n\n[Title]: WARNING\n[Source]: Page 1, Left Column, Warning Box\n\n[Factual Statement]: Transmission may be seriously damaged due to lack of lubrication if the vehicle is allowed to move for too long after the motor is turned off and "N" gear is engaged.\n[Source]: Page 1, Left Column, Warning Box, First Bullet Point\n\n[Factual Statement]: When the motor is running and the vehicle is in the "R"/"D" gear, always stop the vehicle by stepping on the brake pedal, as there is still force transmitted from the actuator and the vehicle can travel slowly even in its idle condition.\n[Source]: Page 1, Left Column, Warning Box, Second Bullet Point\n\n[Factual Statement]: If you want to shift a gear while driving forward, do not step on the accelerator pedal to prevent accidents.\n[Source]: Page 1, Left Column, Warning Box, Third Bullet Point\n\n[Factual Statement]: Never shift to "R" or press the "P" button while the vehicle is moving, in order to prevent accidents.\n[Source]: Page 1, Left Column, Warning Box, Fourth Bullet Point\n\n[Factual Statement]: It is not recommended to allow the vehicle to go down a ramp when it is in the "N" or "P" gear, even if the vehicle is not started.\n[Source]: Page 1, Left Column, Warning Box, Fifth Bullet Point\n\n[Title]: Electronic Parking Brake (EPB)\n[Source]: Page 1, Right Column, Main Title\n\n[Title]: EPB Switch\n[Source]: Page 1, Right Column, Sub-Title\n\n[Factual Statement]: Be sure to engage the Electronic Parking Brake (EPB) every time before parking and leaving the vehicle.\n[Source]: Page 1, Right Column, EPB Switch Section, Bullet Point\n\n[Image Description]: An image shows the interior of a car, focusing on the center console area. A hand is depicted pulling up a switch labeled with a "P" inside a circle and the word "AUTO HOLD" below it. Callouts indicate the EPB switch.\n[Source]: Page 1, Right Column, Image below "EPB Switch"\n\n[Title]: Engaging EPB Manually\n[Source]: Page 1, Right Column, Sub-Title\n\n[Factual Statement]: Pull up the EPB switch.\n[Source]: Page 1, Right Column, Engaging EPB Manually Section, First Sentence\n\n[Factual Statement]: EPB applies an appropriate parking force, and (P) flashes on the instrument cluster and then becomes solid on, indicating that EPB has been applied.\n[Source]: Page 1, Right Column, Engaging EPB Manually Section, First Sentence\n\n[Factual Statement]: The "EPB ON" message is also displayed.\n[Source]: Page 1, Right Column, Engaging EPB Manually Section, Second Sentence\n\n[Title]: CAUTION\n[Source]: Page 1, Right Column, Caution Box\n\n[Factual Statement]: When (P) flashes, EPB is working.\n[Source]: Page 1, Right Column, Caution Box, First Bullet Point\n\n[Factual Statement]: If the vehicle is on a slope, do not release the brake pedal until (P) is steady on.\n[Source]: Page 1, Right Column, Caution Box, First Bullet Point\n\n[Factual Statement]: Otherwise the vehicle may move down.\n[Source]: Page 1, Right Column, Caution Box, First Bullet Point\n\n[Title]: Engaging EPB Automatically\n[Source]: Page 1, Right Column, Sub-Title\n\n[Title]: Engaging EPB automatically when the ignition is switched off\n[Source]: Page 1, Right Column, Sub-Title under "Engaging EPB Automatically"\n\n[Factual Statement]: When the ignition is switched off, EPB engages automatically and (P) lights up on the instrument cluster.\n',
            rag_chunk=RagChunk(
                text='```text\n[Factual Statement]: If the shift is successful, the lever returns to its middle position after it is released.\n[Source]: Page 1, Left Column, First Bullet Point\n\n[Factual Statement]: To prevent unintended vehicle movement, press the "P" button and engage EPB once the vehicle has stopped completely.\n[Source]: Page 1, Left Column, Second Bullet Point\n\n[Factual Statement]: At this time, the EPB indicator turns on.\n[Source]: Page 1, Left Column, Second Bullet Point\n\n[Title]: WARNING\n[Source]: Page 1, Left Column, Warning Box\n\n[Factual Statement]: Transmission may be seriously damaged due to lack of lubrication if the vehicle is allowed to move for too long after the motor is turned off and "N" gear is engaged.\n[Source]: Page 1, Left Column, Warning Box, First Bullet Point\n\n[Factual Statement]: When the motor is running and the vehicle is in the "R"/"D" gear, always stop the vehicle by stepping on the brake pedal, as there is still force transmitted from the actuator and the vehicle can travel slowly even in its idle condition.\n[Source]: Page 1, Left Column, Warning Box, Second Bullet Point\n\n[Factual Statement]: If you want to shift a gear while driving forward, do not step on the accelerator pedal to prevent accidents.\n[Source]: Page 1, Left Column, Warning Box, Third Bullet Point\n\n[Factual Statement]: Never shift to "R" or press the "P" button while the vehicle is moving, in order to prevent accidents.\n[Source]: Page 1, Left Column, Warning Box, Fourth Bullet Point\n\n[Factual Statement]: It is not recommended to allow the vehicle to go down a ramp when it is in the "N" or "P" gear, even if the vehicle is not started.\n[Source]: Page 1, Left Column, Warning Box, Fifth Bullet Point\n\n[Title]: Electronic Parking Brake (EPB)\n[Source]: Page 1, Right Column, Main Title\n\n[Title]: EPB Switch\n[Source]: Page 1, Right Column, Sub-Title\n\n[Factual Statement]: Be sure to engage the Electronic Parking Brake (EPB) every time before parking and leaving the vehicle.\n[Source]: Page 1, Right Column, EPB Switch Section, Bullet Point\n\n[Image Description]: An image shows the interior of a car, focusing on the center console area. A hand is depicted pulling up a switch labeled with a "P" inside a circle and the word "AUTO HOLD" below it. Callouts indicate the EPB switch.\n[Source]: Page 1, Right Column, Image below "EPB Switch"\n\n[Title]: Engaging EPB Manually\n[Source]: Page 1, Right Column, Sub-Title\n\n[Factual Statement]: Pull up the EPB switch.\n[Source]: Page 1, Right Column, Engaging EPB Manually Section, First Sentence\n\n[Factual Statement]: EPB applies an appropriate parking force, and (P) flashes on the instrument cluster and then becomes solid on, indicating that EPB has been applied.\n[Source]: Page 1, Right Column, Engaging EPB Manually Section, First Sentence\n\n[Factual Statement]: The "EPB ON" message is also displayed.\n[Source]: Page 1, Right Column, Engaging EPB Manually Section, Second Sentence\n\n[Title]: CAUTION\n[Source]: Page 1, Right Column, Caution Box\n\n[Factual Statement]: When (P) flashes, EPB is working.\n[Source]: Page 1, Right Column, Caution Box, First Bullet Point\n\n[Factual Statement]: If the vehicle is on a slope, do not release the brake pedal until (P) is steady on.\n[Source]: Page 1, Right Column, Caution Box, First Bullet Point\n\n[Factual Statement]: Otherwise the vehicle may move down.\n[Source]: Page 1, Right Column, Caution Box, First Bullet Point\n\n[Title]: Engaging EPB Automatically\n[Source]: Page 1, Right Column, Sub-Title\n\n[Title]: Engaging EPB automatically when the ignition is switched off\n[Source]: Page 1, Right Column, Sub-Title under "Engaging EPB Automatically"\n\n[Factual Statement]: When the ignition is switched off, EPB engages automatically and (P) lights up on the instrument cluster.\n',
                page_span=RagChunk.PageSpan(first_page=109, last_page=109),
            ),
        )
    ),
    content.GroundingChunk(
        retrieved_context=content.GroundingChunk.RetrievedContext(
            uri="gs://sample-gcs-directory/file1.pdf",
            title="file1.pdf",
            text='",\n  {"source": "Unlocking doors: section, fourth bullet point", "fact": "Doors will not be locked/unlocked when:"},\n  {"source": "Unlocking doors: section, fourth bullet point, sub-bullet 1", "fact": "The NFC key card is placed close to the designated area on the driver\'s side mirror while a door is being opened or closed."},\n  {"source": "Unlocking doors: section, fourth bullet point, sub-bullet 2", "fact": "The ignition is not switched off."},\n  {"source": "CAUTION box, title", "fact": "CAUTION"},\n  {"source": "CAUTION box, content", "fact": "The keyless start permission lasts for up to four minutes."},\n  {"source": "Locking/Unlocking the Trunk heading", "fact": "Locking/Unlocking the Trunk"},\n  {"source": "Opening/Closing trunk with smart key heading", "fact": "Opening/Closing trunk with smart key"},\n  {"source": "Opening/Closing trunk with smart key section, first bullet point", "fact": "When the vehicle is equipped with the electric tailgate system, double-press the trunk release button on the smart key to open the trunk."},\n  {"source": "Opening/Closing trunk with smart key section, first bullet point", "fact": "The turn signals then flash twice."},\n  {"source": "Opening/Closing trunk with smart key section, first bullet point", "fact": "Press this button again to stop opening."},\n  {"source": "Opening/Closing trunk with smart key section, first bullet point", "fact": "Then double press it to close the trunk."},\n  {"source": "Page number", "fact": "51"},\n  {"source": "Right margin header", "fact": "03"},\n  {"source": "Right margin vertical text", "fact": "CONTROLLER OPERATION"}\n]\n',
            rag_chunk=RagChunk(
                text='",\n  {"source": "Unlocking doors: section, fourth bullet point", "fact": "Doors will not be locked/unlocked when:"},\n  {"source": "Unlocking doors: section, fourth bullet point, sub-bullet 1", "fact": "The NFC key card is placed close to the designated area on the driver\'s side mirror while a door is being opened or closed."},\n  {"source": "Unlocking doors: section, fourth bullet point, sub-bullet 2", "fact": "The ignition is not switched off."},\n  {"source": "CAUTION box, title", "fact": "CAUTION"},\n  {"source": "CAUTION box, content", "fact": "The keyless start permission lasts for up to four minutes."},\n  {"source": "Locking/Unlocking the Trunk heading", "fact": "Locking/Unlocking the Trunk"},\n  {"source": "Opening/Closing trunk with smart key heading", "fact": "Opening/Closing trunk with smart key"},\n  {"source": "Opening/Closing trunk with smart key section, first bullet point", "fact": "When the vehicle is equipped with the electric tailgate system, double-press the trunk release button on the smart key to open the trunk."},\n  {"source": "Opening/Closing trunk with smart key section, first bullet point", "fact": "The turn signals then flash twice."},\n  {"source": "Opening/Closing trunk with smart key section, first bullet point", "fact": "Press this button again to stop opening."},\n  {"source": "Opening/Closing trunk with smart key section, first bullet point", "fact": "Then double press it to close the trunk."},\n  {"source": "Page number", "fact": "51"},\n  {"source": "Right margin header", "fact": "03"},\n  {"source": "Right margin vertical text", "fact": "CONTROLLER OPERATION"}\n]\n',
                page_span=RagChunk.PageSpan(first_page=52, last_page=52),
            ),
        )
    ),
    content.GroundingChunk(
        retrieved_context=content.GroundingChunk.RetrievedContext(
            uri="gs://sample-gcs-directory/file1.pdf",
            title="file1.pdf",
            text='Okay, I will extract the factual statements and structured data from the image provided.\n\n**Page Number:**\n* Fact: 50\n    * Source: Bottom left of the page.\n\n**General Information (Top Left Column):**\n* Fact: If the anti-theft alarm system is armed, open any door within 30 seconds after unlocking with the smart key or all doors will relock automatically.\n    * Source: First bullet point, top left column.\n* Fact: If the key is in the vehicle or trunk when the doors are closed and locked, the vehicle will unlock automatically and the turn signals will flash twice.\n    * Source: Second bullet point, top left column.\n* Fact: When equipped with four-door anti-pinch function, press the "Lock" or "Unlock" button for a long time to trigger raising/lowering windows with smart key, and press it for a short time to trigger the lock/unlock function.\n    * Source: Third bullet point, top left column.\n\n**Title: Opening the trunk with smart key**\n* Source: Heading, left column.\n* Fact: Double-press the trunk release button on the smart key.\n    * Source: First sentence under "Opening the trunk with smart key".\n* Fact: The turn signals then flash twice.\n    * Source: Second sentence under "Opening the trunk with smart key".\n\n**REMINDER (Left Column):**\n* Fact (Icon): Exclamation mark in a circle.\n    * Source: Icon next to "REMINDER", left column.\n* Fact (Title): REMINDER\n    * Source: Text next to icon, left column.\n* Fact: Remember to carry the smart key when leaving the vehicle.\n    * Source: Bullet point under "REMINDER", left column.\n\n**Title: Finding the Vehicle with Smart Key**\n* Source: Heading, left column.\n* Fact: When the vehicle is in anti-theft mode, press the lock button.\n    * Source: First sentence of the first bullet point under "Finding the Vehicle with Smart Key".\n* Fact: The vehicle sounds a long beep and turn signals flash 15 times.\n    * Source: Second sentence of the first bullet point under "Finding the Vehicle with Smart Key".\n* Fact: Use this function to locate the vehicle when it cannot be found.\n    * Source: Third sentence of the first bullet point under "Finding the Vehicle with Smart Key".\n* Fact: When the vehicle is in car search mode, press the lock button again.\n    * Source: First sentence of the second bullet point under "Finding the Vehicle with Smart Key".\n* Fact: The vehicle enters the next car search mode.\n    * Source: Second sentence of the second bullet point under "Finding the Vehicle with Smart Key".\n\n**Title: Raising/Lowering Windows with Smart Key**\n* Source: Heading, left column.\n* Fact: When the ignition is switched off:\n    * Source: First bullet point under "Raising/Lowering Windows with Smart Key".\n* Fact: Press and hold the lock button on the smart key to raise the four windows.\n    * Source: Sub-bullet point under "When the ignition is switched off:", left column.\n* Fact: Press and hold the unlock button on the smart key to lower the four windows.\n    * Source: Bullet point, top right column.\n\n**WARNING (Right Column):**\n* Fact (Icon): Exclamation mark in a triangle.\n    * Source: Icon next to "WARNING", right column.\n* Fact (Title): WARNING\n    * Source: Text next to icon, right column.\n* Fact: When using the remote control function to raise windows, pay attention to the safety of occupants in the vehicle, and use this function only after making sure the windows are clear from pinching anyone.\n    * Source: Text within the "WARNING" box, right column.\n\n**REMINDER (Right Column):**\n* Fact (Icon): Exclamation mark in a circle.\n    * Source: Icon next to "REMINDER", right column.\n* Fact (Title): REMINDER\n    * Source: Text next to icon, right column.\n* Fact: To enable or disable key unlock/lock/closing window functions, go to [car settings icon] → Vehicle → Locks.\n    * Source: First part of the bullet point under "REMINDER", right column. (Note: [car settings icon] describes the small icon of a car with what appears to be a settings gear or similar symbol next to it)."',
            rag_chunk=RagChunk(
                text='Okay, I will extract the factual statements and structured data from the image provided.\n\n**Page Number:**\n* Fact: 50\n    * Source: Bottom left of the page.\n\n**General Information (Top Left Column):**\n* Fact: If the anti-theft alarm system is armed, open any door within 30 seconds after unlocking with the smart key or all doors will relock automatically.\n    * Source: First bullet point, top left column.\n* Fact: If the key is in the vehicle or trunk when the doors are closed and locked, the vehicle will unlock automatically and the turn signals will flash twice.\n    * Source: Second bullet point, top left column.\n* Fact: When equipped with four-door anti-pinch function, press the "Lock" or "Unlock" button for a long time to trigger raising/lowering windows with smart key, and press it for a short time to trigger the lock/unlock function.\n    * Source: Third bullet point, top left column.\n\n**Title: Opening the trunk with smart key**\n* Source: Heading, left column.\n* Fact: Double-press the trunk release button on the smart key.\n    * Source: First sentence under "Opening the trunk with smart key".\n* Fact: The turn signals then flash twice.\n    * Source: Second sentence under "Opening the trunk with smart key".\n\n**REMINDER (Left Column):**\n* Fact (Icon): Exclamation mark in a circle.\n    * Source: Icon next to "REMINDER", left column.\n* Fact (Title): REMINDER\n    * Source: Text next to icon, left column.\n* Fact: Remember to carry the smart key when leaving the vehicle.\n    * Source: Bullet point under "REMINDER", left column.\n\n**Title: Finding the Vehicle with Smart Key**\n* Source: Heading, left column.\n* Fact: When the vehicle is in anti-theft mode, press the lock button.\n    * Source: First sentence of the first bullet point under "Finding the Vehicle with Smart Key".\n* Fact: The vehicle sounds a long beep and turn signals flash 15 times.\n    * Source: Second sentence of the first bullet point under "Finding the Vehicle with Smart Key".\n* Fact: Use this function to locate the vehicle when it cannot be found.\n    * Source: Third sentence of the first bullet point under "Finding the Vehicle with Smart Key".\n* Fact: When the vehicle is in car search mode, press the lock button again.\n    * Source: First sentence of the second bullet point under "Finding the Vehicle with Smart Key".\n* Fact: The vehicle enters the next car search mode.\n    * Source: Second sentence of the second bullet point under "Finding the Vehicle with Smart Key".\n\n**Title: Raising/Lowering Windows with Smart Key**\n* Source: Heading, left column.\n* Fact: When the ignition is switched off:\n    * Source: First bullet point under "Raising/Lowering Windows with Smart Key".\n* Fact: Press and hold the lock button on the smart key to raise the four windows.\n    * Source: Sub-bullet point under "When the ignition is switched off:", left column.\n* Fact: Press and hold the unlock button on the smart key to lower the four windows.\n    * Source: Bullet point, top right column.\n\n**WARNING (Right Column):**\n* Fact (Icon): Exclamation mark in a triangle.\n    * Source: Icon next to "WARNING", right column.\n* Fact (Title): WARNING\n    * Source: Text next to icon, right column.\n* Fact: When using the remote control function to raise windows, pay attention to the safety of occupants in the vehicle, and use this function only after making sure the windows are clear from pinching anyone.\n    * Source: Text within the "WARNING" box, right column.\n\n**REMINDER (Right Column):**\n* Fact (Icon): Exclamation mark in a circle.\n    * Source: Icon next to "REMINDER", right column.\n* Fact (Title): REMINDER\n    * Source: Text next to icon, right column.\n* Fact: To enable or disable key unlock/lock/closing window functions, go to [car settings icon] → Vehicle → Locks.\n    * Source: First part of the bullet point under "REMINDER", right column. (Note: [car settings icon] describes the small icon of a car with what appears to be a settings gear or similar symbol next to it)."',
                page_span=RagChunk.PageSpan(first_page=51, last_page=51),
            ),
        )
    ),
    content.GroundingChunk(
        retrieved_context=content.GroundingChunk.RetrievedContext(
            uri="gs://sample-gcs-directory/file1.pdf",
            title="file1.pdf",
            text="| Factual Statement                                           | Source               |\n| :------------------------------------------------------------ | :------------------- |\n| **Figure Index** | Figure Index section |\n| Exterior....................................................7       | Figure Index section |\n| Dashboard...................................................8       | Figure Index section |\n| Center Console..............................................9       | Figure Index section |\n| Doors.......................................................10      | Figure Index section |\n| **Safety** | Safety section       |\n| Seat Belts..................................................12      | Safety section       |\n| Seat Belt Overview..........................................12      | Safety section       |\n| Using Seat Belts............................................12      | Safety section       |\n| Airbags.....................................................15      | Safety section       |\n| Airbag Overview.............................................15      | Safety section       |\n| Driver and Front Passenger Airbags..........................16      | Safety section       |\n| Front Passenger Side Airbags................................16      | Safety section       |\n| Side Curtain Airbags........................................17      | Safety section       |\n| Airbag Triggering Conditions................................18      | Safety section       |\n| Child Restraint Systems.....................................21      | Safety section       |\n| Child Restraint Systems.....................................21      | Safety section       |\n| Anti-theft Alarm System.....................................27      | Safety section       |\n| Anti-theft Alarm System.....................................27      | Safety section       |\n| Data Collection and Processing..............................28      | Safety section       |\n| Data Collection and Processing..............................28      | Safety section       |\n| **Instrument Cluster** | Instrument Cluster section |\n| Instrument Cluster..........................................34      | Instrument Cluster section |\n| Instrument Cluster View.....................................34      | Instrument Cluster section |\n| Instrument Cluster Indicators...............................35      | Instrument Cluster section |\n| **Controller Operation** | Controller Operation section |\n| Doors and Keys..............................................46      | Controller Operation section |\n| Keys........................................................46      | Controller Operation section |\n| Locking/Unlocking Doors.....................................48      | Controller Operation section |\n| Smart Access and Start System...............................55      | Right column         |\n| Child Protection Lock.......................................56      | Right column         |\n| **Seats**...................................................57      | Right column         |\n| Seat Precautions............................................57      | Right column         |\n| Adjusting Front Seats.......................................58      | Right column         |\n| Folding Rear Seats..........................................59      | Right column         |\n| Head Supports...............................................59      | Right column         |\n| **Steering Wheel**..........................................60      | Right column         |\n| Steering Wheel..............................................60      | Right column         |\n| **Switches**................................................64      | Right column         |\n| Light Switches..............................................64      | Right column         |\n| Wiper Switch................................................67      | Right column         |\n| Driver's Door Switches......................................69      | Right column         |\n| Odometer Switch.............................................71      | Right column         |\n| Driver Assistance Switches..................................72      | Right column         |\n| Window Control Switch on Passenger Side.....................72      | Right column         |\n| Hazard Warning Light Switch.................................72      | Right column         |\n| Mode Switches...............................................72      | Right column         |\n| PAB Switch*.................................................73      | Right column         |\n| Emergency Call (E-Call).....................................74      | Right column         |\n| Sunroof Switch..............................................75      | Right column         |\n| Interior Light Switch.......................................77      | Right column         |\n| **Using and Driving** | Using and Driving section |\n| Charging/Discharging........................................80      | Using and Driving section |\n| Charging Instructions.......................................80      | Using and Driving section |\n| Charging....................................................84      | Using and Driving section |\n| Discharging Device*.........................................90      | Using and Driving section |\n| Charging Port Immobilizer System............................91      | Using and Driving section |\n| Driving Range Display*......................................92      | Using and Driving section |\n| Regenerative Braking Settings...............................92      | Using and Driving section |\n| **Battery**.................................................93      | Using and Driving section |\n| High-Voltage Battery........................................93      | Using and Driving section |\n| 3                                                             | Bottom right of page |\n",
            rag_chunk=RagChunk(
                text="| Factual Statement                                           | Source               |\n| :------------------------------------------------------------ | :------------------- |\n| **Figure Index** | Figure Index section |\n| Exterior....................................................7       | Figure Index section |\n| Dashboard...................................................8       | Figure Index section |\n| Center Console..............................................9       | Figure Index section |\n| Doors.......................................................10      | Figure Index section |\n| **Safety** | Safety section       |\n| Seat Belts..................................................12      | Safety section       |\n| Seat Belt Overview..........................................12      | Safety section       |\n| Using Seat Belts............................................12      | Safety section       |\n| Airbags.....................................................15      | Safety section       |\n| Airbag Overview.............................................15      | Safety section       |\n| Driver and Front Passenger Airbags..........................16      | Safety section       |\n| Front Passenger Side Airbags................................16      | Safety section       |\n| Side Curtain Airbags........................................17      | Safety section       |\n| Airbag Triggering Conditions................................18      | Safety section       |\n| Child Restraint Systems.....................................21      | Safety section       |\n| Child Restraint Systems.....................................21      | Safety section       |\n| Anti-theft Alarm System.....................................27      | Safety section       |\n| Anti-theft Alarm System.....................................27      | Safety section       |\n| Data Collection and Processing..............................28      | Safety section       |\n| Data Collection and Processing..............................28      | Safety section       |\n| **Instrument Cluster** | Instrument Cluster section |\n| Instrument Cluster..........................................34      | Instrument Cluster section |\n| Instrument Cluster View.....................................34      | Instrument Cluster section |\n| Instrument Cluster Indicators...............................35      | Instrument Cluster section |\n| **Controller Operation** | Controller Operation section |\n| Doors and Keys..............................................46      | Controller Operation section |\n| Keys........................................................46      | Controller Operation section |\n| Locking/Unlocking Doors.....................................48      | Controller Operation section |\n| Smart Access and Start System...............................55      | Right column         |\n| Child Protection Lock.......................................56      | Right column         |\n| **Seats**...................................................57      | Right column         |\n| Seat Precautions............................................57      | Right column         |\n| Adjusting Front Seats.......................................58      | Right column         |\n| Folding Rear Seats..........................................59      | Right column         |\n| Head Supports...............................................59      | Right column         |\n| **Steering Wheel**..........................................60      | Right column         |\n| Steering Wheel..............................................60      | Right column         |\n| **Switches**................................................64      | Right column         |\n| Light Switches..............................................64      | Right column         |\n| Wiper Switch................................................67      | Right column         |\n| Driver's Door Switches......................................69      | Right column         |\n| Odometer Switch.............................................71      | Right column         |\n| Driver Assistance Switches..................................72      | Right column         |\n| Window Control Switch on Passenger Side.....................72      | Right column         |\n| Hazard Warning Light Switch.................................72      | Right column         |\n| Mode Switches...............................................72      | Right column         |\n| PAB Switch*.................................................73      | Right column         |\n| Emergency Call (E-Call).....................................74      | Right column         |\n| Sunroof Switch..............................................75      | Right column         |\n| Interior Light Switch.......................................77      | Right column         |\n| **Using and Driving** | Using and Driving section |\n| Charging/Discharging........................................80      | Using and Driving section |\n| Charging Instructions.......................................80      | Using and Driving section |\n| Charging....................................................84      | Using and Driving section |\n| Discharging Device*.........................................90      | Using and Driving section |\n| Charging Port Immobilizer System............................91      | Using and Driving section |\n| Driving Range Display*......................................92      | Using and Driving section |\n| Regenerative Braking Settings...............................92      | Using and Driving section |\n| **Battery**.................................................93      | Using and Driving section |\n| High-Voltage Battery........................................93      | Using and Driving section |\n| 3                                                             | Bottom right of page |\n",
                page_span=RagChunk.PageSpan(first_page=4, last_page=4),
            ),
        )
    ),
    content.GroundingChunk(
        retrieved_context=content.GroundingChunk.RetrievedContext(
            uri="gs://sample-gcs-directory/file1.pdf",
            title="file1.pdf",
            text="* **RCW*** (RCW\\*)\n* At vehicle speeds between 5 km/h and 146 km/h, if the rear corner mmWave radar detects a risk of collision with a vehicle approaching quickly from behind on the current lane, the hazard warning light turns on to warn the driver in that vehicle against a possible collision. (RCW\\*)\n* **DOW*** (DOW\\*)\n* DOW is realized with rear corner mmWave radars installed on both sides of the rear bumper. (DOW\\*)\n* When the vehicle is stationary with doors unlocked, the system keeps indicators on side mirrors solid on to warn the driver if moving objects, such as bicycles or automobiles, on an adjacent lane are approaching from behind. (DOW\\*)\n* At the same time, an icon is displayed on the instrument cluster. (DOW\\*)\n* If the driver attempts to open the door at this time, indicators on side mirrors begin to flash and a chime sounds. (DOW\\*)\n* **How to Use** (How to Use)\n* Enable or disable BSD, RCTA, RCTB, RCW, or DOW in the infotainment touchscreen → → ADAS → Active Safety → Blind Spot Assist (BSA). (How to Use)\n* Enable or disable BSD, RCTA, RCTB, RCW, or DOW by pressing the button [image of a car with radar waves and a smaller car in the blind spot, with an 'OFF' overlay, surrounded by a circle with 'A' and an arrow pointing to it]. (How to Use)\n* Image displays a car dashboard view with a highlighted button on the center console. The button depicts a car with radar waves emanating from its rear corners, and a smaller car in the blind spot, all within a circle. An inset shows a close-up of the instrument cluster display, depicting a car from above with radar waves indicating detection of a vehicle in the left blind spot. (How to Use, image)\n* When the blind spot assist system is disabled, no relevant indicators are displayed on the instrument cluster. (How to Use)\n* When the blind spot assist system is standing by, if vehicle conditions, such as speed or gear status, do not meet the requirements of any function, [image of a car with radar waves and a smaller car in the blind spot, with an 'OFF' overlay, within a circle and the letter 'A'] is displayed on the instrument cluster and blind spot assist will not be activated. (How to Use)\n* If the blind spot assist system malfunctions, [image of a car with radar waves and a smaller car in the blind spot, with a wrench symbol overlay] is displayed. (How to Use)\n* When the blind spot assist system is active, [image of a car with radar waves and a smaller car in the blind spot] is displayed, meaning that the function has been activated and can trigger alarms at any time. (How to Use)\n* **Precautions** (Precautions)\n* While the BSD system provides assistance in monitoring blind spots of rearview mirrors, it cannot replace the driver's observation and judgment. (Precautions)\n* The driver must keep control of vehicle at all times and drive properly and is fully responsible for the vehicle. (Precautions)\n* The BSD system may be unable to provide adequate warning on target vehicles approaching from behind at a high speed. (Precautions)\n* The driver must ensure the normal operation of the BSD system, keeping its rear corner mmWave radars in good condition. (Precautions)\n* For example, dirt, snow, or other obstructions need to be cleared right away. (Precautions)\n* The BSD system gives a warning if unrelated targets at the rear side or in the rear (such as work zone barriers, large roadside billboards, reflectors in tunnels, or other objects with a large radar cross section) are mistakenly selected as target vehicles. (Precautions)\n* Detection may be affected or delayed in some environments. (Precautions)\n* If the radar cross section of the target vehicle is too small (a bicycle, electric moped or pedestrian, for example), the system may fail to identify targets, leading to false alarms. (Precautions)\n* Page number: **129** (Bottom right of page)\n* Section number and title: **04 USING AND DRIVING** (Top right of page, vertical text)\"\n",
            rag_chunk=RagChunk(
                text="* **RCW*** (RCW\\*)\n* At vehicle speeds between 5 km/h and 146 km/h, if the rear corner mmWave radar detects a risk of collision with a vehicle approaching quickly from behind on the current lane, the hazard warning light turns on to warn the driver in that vehicle against a possible collision. (RCW\\*)\n* **DOW*** (DOW\\*)\n* DOW is realized with rear corner mmWave radars installed on both sides of the rear bumper. (DOW\\*)\n* When the vehicle is stationary with doors unlocked, the system keeps indicators on side mirrors solid on to warn the driver if moving objects, such as bicycles or automobiles, on an adjacent lane are approaching from behind. (DOW\\*)\n* At the same time, an icon is displayed on the instrument cluster. (DOW\\*)\n* If the driver attempts to open the door at this time, indicators on side mirrors begin to flash and a chime sounds. (DOW\\*)\n* **How to Use** (How to Use)\n* Enable or disable BSD, RCTA, RCTB, RCW, or DOW in the infotainment touchscreen → → ADAS → Active Safety → Blind Spot Assist (BSA). (How to Use)\n* Enable or disable BSD, RCTA, RCTB, RCW, or DOW by pressing the button [image of a car with radar waves and a smaller car in the blind spot, with an 'OFF' overlay, surrounded by a circle with 'A' and an arrow pointing to it]. (How to Use)\n* Image displays a car dashboard view with a highlighted button on the center console. The button depicts a car with radar waves emanating from its rear corners, and a smaller car in the blind spot, all within a circle. An inset shows a close-up of the instrument cluster display, depicting a car from above with radar waves indicating detection of a vehicle in the left blind spot. (How to Use, image)\n* When the blind spot assist system is disabled, no relevant indicators are displayed on the instrument cluster. (How to Use)\n* When the blind spot assist system is standing by, if vehicle conditions, such as speed or gear status, do not meet the requirements of any function, [image of a car with radar waves and a smaller car in the blind spot, with an 'OFF' overlay, within a circle and the letter 'A'] is displayed on the instrument cluster and blind spot assist will not be activated. (How to Use)\n* If the blind spot assist system malfunctions, [image of a car with radar waves and a smaller car in the blind spot, with a wrench symbol overlay] is displayed. (How to Use)\n* When the blind spot assist system is active, [image of a car with radar waves and a smaller car in the blind spot] is displayed, meaning that the function has been activated and can trigger alarms at any time. (How to Use)\n* **Precautions** (Precautions)\n* While the BSD system provides assistance in monitoring blind spots of rearview mirrors, it cannot replace the driver's observation and judgment. (Precautions)\n* The driver must keep control of vehicle at all times and drive properly and is fully responsible for the vehicle. (Precautions)\n* The BSD system may be unable to provide adequate warning on target vehicles approaching from behind at a high speed. (Precautions)\n* The driver must ensure the normal operation of the BSD system, keeping its rear corner mmWave radars in good condition. (Precautions)\n* For example, dirt, snow, or other obstructions need to be cleared right away. (Precautions)\n* The BSD system gives a warning if unrelated targets at the rear side or in the rear (such as work zone barriers, large roadside billboards, reflectors in tunnels, or other objects with a large radar cross section) are mistakenly selected as target vehicles. (Precautions)\n* Detection may be affected or delayed in some environments. (Precautions)\n* If the radar cross section of the target vehicle is too small (a bicycle, electric moped or pedestrian, for example), the system may fail to identify targets, leading to false alarms. (Precautions)\n* Page number: **129** (Bottom right of page)\n* Section number and title: **04 USING AND DRIVING** (Top right of page, vertical text)\"\n",
                page_span=RagChunk.PageSpan(first_page=10, last_page=10),
            ),
        )
    ),
    content.GroundingChunk(
        retrieved_context=content.GroundingChunk.RetrievedContext(
            uri="gs://sample-gcs-directory/file1.pdf",
            title="file1.pdf",
            text='```json\n[\n  {\n    "fact": "Sensor Type",\n    "source": "Page 1, Section Title"\n  },\n  {\n    "fact": "When the sensor detects an obstacle, the corresponding image is displayed on the infotainment touchscreen*, depending on the location of the obstacle and its distance from the vehicle.",\n    "source": "Page 1, Sensor Type section"\n  },\n  {\n    "fact": "When the driver conducts parallel parking or reverse parking, the sensor measures the distance between the vehicle and the obstacle and communicates this information through the infotainment touchscreen and the speaker.",\n    "source": "Page 1, Sensor Type section"\n  },\n  {\n    "fact": "Be aware of the surroundings when using this system.",\n    "source": "Page 1, Sensor Type section"\n  },\n  {\n    "fact": "① Front left sensor*",\n    "source": "Page 1, Sensor Type section, List item"\n  },\n  {\n    "fact": "② Front right sensor*",\n    "source": "Page 1, Sensor Type section, List item"\n  },\n  {\n    "fact": "③ Rear right sensor*",\n    "source": "Page 1, Sensor Type section, List item"\n  },\n  {\n    "fact": "④⑤ Rear middle sensors*",\n    "source": "Page 1, Sensor Type section, List item"\n  },\n  {\n    "fact": "⑥ Rear left sensor*",\n    "source": "Page 1, Diagram label"\n  },\n  {\n    "fact": "Diagram shows a top-down view of a vehicle with sensors labeled 1, 2, 3, 4, 5, and 6.",\n    "source": "Page 1, Diagram"\n  },\n  {\n    "fact": "Sensor labeled \'1\' is located on the front left corner of the vehicle.",\n    "source": "Page 1, Diagram"\n  },\n  {\n    "fact": "Sensor labeled \'2\' is located on the front right corner of the vehicle.",\n    "source": "Page 1, Diagram"\n  },\n  {\n    "fact": "Sensor labeled \'3\' is located on the rear right corner of the vehicle.",\n    "source": "Page 1, Diagram"\n  },\n  {\n    "fact": "Sensor labeled \'4\' is located on the rear right side, towards the middle, of the vehicle.",\n    "source": "Page 1, Diagram"\n  },\n  {\n    "fact": "Sensor labeled \'5\' is located on the rear left side, towards the middle, of the vehicle.",\n    "source": "Page 1, Diagram"\n  },\n  {\n    "fact": "Sensor labeled \'6\' is located on the rear left corner of the vehicle.",\n    "source": "Page 1, Diagram"\n  },\n  {\n    "fact": "Distance Display and Speaker",\n    "source": "Page 1, Section Title"\n  },\n  {\n    "fact": "When the sensor detects an obstacle, the location of the obstacle and its approximate distance from the vehicle are displayed on the infotainment touchscreen, and the speaker beeps.",\n    "source": "Page 1, Distance Display and Speaker section"\n  },\n  {\n    "fact": "Working example of center sensors",\n    "source": "Page 1, Table Title"\n  },\n  {\n    "fact_type": "table_data",\n    "table_title": "Working example of center sensors",\n    "row_header": "About 700 to 1,200",\n    "column_header": "Approximate Distance (mm)",\n    "value": "About 700 to 1,200",\n    "source": "Page 1, Table: Working example of center sensors"\n  },\n  {\n    "fact_type": "table_data",\n    "table_title": "Working example of center sensors",\n    "row_header": "About 700 to 1,200",\n    "column_header": "Touchscreen Display Example",\n    "value": "Image of a car with green arcs behind it, indicating obstacle distance."\n',
            rag_chunk=RagChunk(
                text='```json\n[\n  {\n    "fact": "Sensor Type",\n    "source": "Page 1, Section Title"\n  },\n  {\n    "fact": "When the sensor detects an obstacle, the corresponding image is displayed on the infotainment touchscreen*, depending on the location of the obstacle and its distance from the vehicle.",\n    "source": "Page 1, Sensor Type section"\n  },\n  {\n    "fact": "When the driver conducts parallel parking or reverse parking, the sensor measures the distance between the vehicle and the obstacle and communicates this information through the infotainment touchscreen and the speaker.",\n    "source": "Page 1, Sensor Type section"\n  },\n  {\n    "fact": "Be aware of the surroundings when using this system.",\n    "source": "Page 1, Sensor Type section"\n  },\n  {\n    "fact": "① Front left sensor*",\n    "source": "Page 1, Sensor Type section, List item"\n  },\n  {\n    "fact": "② Front right sensor*",\n    "source": "Page 1, Sensor Type section, List item"\n  },\n  {\n    "fact": "③ Rear right sensor*",\n    "source": "Page 1, Sensor Type section, List item"\n  },\n  {\n    "fact": "④⑤ Rear middle sensors*",\n    "source": "Page 1, Sensor Type section, List item"\n  },\n  {\n    "fact": "⑥ Rear left sensor*",\n    "source": "Page 1, Diagram label"\n  },\n  {\n    "fact": "Diagram shows a top-down view of a vehicle with sensors labeled 1, 2, 3, 4, 5, and 6.",\n    "source": "Page 1, Diagram"\n  },\n  {\n    "fact": "Sensor labeled \'1\' is located on the front left corner of the vehicle.",\n    "source": "Page 1, Diagram"\n  },\n  {\n    "fact": "Sensor labeled \'2\' is located on the front right corner of the vehicle.",\n    "source": "Page 1, Diagram"\n  },\n  {\n    "fact": "Sensor labeled \'3\' is located on the rear right corner of the vehicle.",\n    "source": "Page 1, Diagram"\n  },\n  {\n    "fact": "Sensor labeled \'4\' is located on the rear right side, towards the middle, of the vehicle.",\n    "source": "Page 1, Diagram"\n  },\n  {\n    "fact": "Sensor labeled \'5\' is located on the rear left side, towards the middle, of the vehicle.",\n    "source": "Page 1, Diagram"\n  },\n  {\n    "fact": "Sensor labeled \'6\' is located on the rear left corner of the vehicle.",\n    "source": "Page 1, Diagram"\n  },\n  {\n    "fact": "Distance Display and Speaker",\n    "source": "Page 1, Section Title"\n  },\n  {\n    "fact": "When the sensor detects an obstacle, the location of the obstacle and its approximate distance from the vehicle are displayed on the infotainment touchscreen, and the speaker beeps.",\n    "source": "Page 1, Distance Display and Speaker section"\n  },\n  {\n    "fact": "Working example of center sensors",\n    "source": "Page 1, Table Title"\n  },\n  {\n    "fact_type": "table_data",\n    "table_title": "Working example of center sensors",\n    "row_header": "About 700 to 1,200",\n    "column_header": "Approximate Distance (mm)",\n    "value": "About 700 to 1,200",\n    "source": "Page 1, Table: Working example of center sensors"\n  },\n  {\n    "fact_type": "table_data",\n    "table_title": "Working example of center sensors",\n    "row_header": "About 700 to 1,200",\n    "column_header": "Touchscreen Display Example",\n    "value": "Image of a car with green arcs behind it, indicating obstacle distance."\n',
                page_span=RagChunk.PageSpan(first_page=17, last_page=17),
            ),
        )
    ),
    content.GroundingChunk(
        retrieved_context=content.GroundingChunk.RetrievedContext(
            uri="gs://sample-gcs-directory/file1.pdf",
            title="file1.pdf",
            text='```json\n[\n  {\n    "fact": "Use of a small spare tire or tire repair kit.",\n    "source": "Page 1, Left Column, Bullet Point 1"\n  },\n  {\n    "fact": "Make sure to go to a BYD authorized dealer or service provider for professional calibration of the front mmWave radar or multi-purpose camera in any of the following situations:",\n    "source": "Page 1, Left Column, Bullet Point 2"\n  },\n  {\n    "fact": "The front mmWave radar or multi-purpose camera has been removed.",\n    "source": "Page 1, Left Column, Sub-bullet 1 of Bullet Point 2"\n  },\n  {\n    "fact": "Toe-in or rear camber has been adjusted during wheel alignment.",\n    "source": "Page 1, Left Column, Sub-bullet 2 of Bullet Point 2"\n  },\n  {\n    "fact": "The position of front mmWave radars or the multi-purpose camera has changed after a collision.",\n    "source": "Page 1, Left Column, Sub-bullet 3 of Bullet Point 2"\n  },\n  {\n    "fact": "Do not attempt to test the AEB system on your own using objects such as carton, iron plate, dummy, etc. The system may not work properly and thus result in accidents.",\n    "source": "Page 1, Left Column, Paragraph after Bullet Point 2"\n  },\n  {\n    "fact": "WARNING",\n    "source": "Page 1, Left Column, Warning Box Title"\n  },\n  {\n    "fact": "PCW and AEB serve as driver assistance functions only, so the driver is fully responsible for driving safety.",\n    "source": "Page 1, Left Column, Warning Box, Bullet Point 1"\n  },\n  {\n    "fact": "Influence of weather, road conditions, and other factors may cause PCW and AEB to fail.",\n    "source": "Page 1, Left Column, Warning Box, Bullet Point 2"\n  },\n  {\n    "fact": "Use PCW and AEB based on your needs, traffic, and road conditions.",\n    "source": "Page 1, Left Column, Warning Box, Bullet Point 3"\n  },\n  {\n    "fact": "Traffic Sign Recognition (TSR)",\n    "source": "Page 1, Left Column, Section Title"\n  },\n  {\n    "fact": "The Traffic Sign Recognition (TSR) system identifies speed limit signs through the multi-purpose camera and map*, displays such signs on the current road on the instrument cluster, and sends alarm messages to the driver when vehicle speed exceeds the detected limit.",\n    "source": "Page 1, Left Column, Paragraph under Traffic Sign Recognition (TSR)"\n  },\n  {\n    "fact": "How to Use",\n    "source": "Page 1, Right Column, Section Title"\n  },\n  {\n    "fact": "Enable or disable TSR in the infotainment touchscreen → [car icon] → ADAS → Driving Assist.",\n    "source": "Page 1, Right Column, Bullet Point 1 under How to Use"\n  },\n  {\n    "fact": "When the TSR system identifies the current traffic sign, [60 icon] is displayed on the instrument cluster.",\n    "source": "Page 1, Right Column, Bullet Point 2 under How to Use"\n  },\n  {\n    "fact": "When TSR cannot identify whether the recognized speed limit value applies to the lane, [60? icon] is displayed.",\n    "source": "Page 1, Right Column, Bullet Point 3 under How to Use"\n  },\n  {\n    "fact": "When the TSR system experiences reduced performance, [60 with strike-through icon] is displayed.",\n    "source": "Page 1, Right Column, Bullet Point 4 under How to Use"\n  },\n  {\n    "fact": "When the TSR system has a reduced performance and cannot identify whether the recognized speed limit value applies to the lane, [60? with strike-through icon] is displayed.",\n    "source": "Page 1, Right Column, Bullet Point 5 under How to Use"\n  },\n  {\n    "fact": "If the TSR system malfunctions, [TSR malfunction icon] is displayed."\n',
            rag_chunk=RagChunk(
                text='```json\n[\n  {\n    "fact": "Use of a small spare tire or tire repair kit.",\n    "source": "Page 1, Left Column, Bullet Point 1"\n  },\n  {\n    "fact": "Make sure to go to a BYD authorized dealer or service provider for professional calibration of the front mmWave radar or multi-purpose camera in any of the following situations:",\n    "source": "Page 1, Left Column, Bullet Point 2"\n  },\n  {\n    "fact": "The front mmWave radar or multi-purpose camera has been removed.",\n    "source": "Page 1, Left Column, Sub-bullet 1 of Bullet Point 2"\n  },\n  {\n    "fact": "Toe-in or rear camber has been adjusted during wheel alignment.",\n    "source": "Page 1, Left Column, Sub-bullet 2 of Bullet Point 2"\n  },\n  {\n    "fact": "The position of front mmWave radars or the multi-purpose camera has changed after a collision.",\n    "source": "Page 1, Left Column, Sub-bullet 3 of Bullet Point 2"\n  },\n  {\n    "fact": "Do not attempt to test the AEB system on your own using objects such as carton, iron plate, dummy, etc. The system may not work properly and thus result in accidents.",\n    "source": "Page 1, Left Column, Paragraph after Bullet Point 2"\n  },\n  {\n    "fact": "WARNING",\n    "source": "Page 1, Left Column, Warning Box Title"\n  },\n  {\n    "fact": "PCW and AEB serve as driver assistance functions only, so the driver is fully responsible for driving safety.",\n    "source": "Page 1, Left Column, Warning Box, Bullet Point 1"\n  },\n  {\n    "fact": "Influence of weather, road conditions, and other factors may cause PCW and AEB to fail.",\n    "source": "Page 1, Left Column, Warning Box, Bullet Point 2"\n  },\n  {\n    "fact": "Use PCW and AEB based on your needs, traffic, and road conditions.",\n    "source": "Page 1, Left Column, Warning Box, Bullet Point 3"\n  },\n  {\n    "fact": "Traffic Sign Recognition (TSR)",\n    "source": "Page 1, Left Column, Section Title"\n  },\n  {\n    "fact": "The Traffic Sign Recognition (TSR) system identifies speed limit signs through the multi-purpose camera and map*, displays such signs on the current road on the instrument cluster, and sends alarm messages to the driver when vehicle speed exceeds the detected limit.",\n    "source": "Page 1, Left Column, Paragraph under Traffic Sign Recognition (TSR)"\n  },\n  {\n    "fact": "How to Use",\n    "source": "Page 1, Right Column, Section Title"\n  },\n  {\n    "fact": "Enable or disable TSR in the infotainment touchscreen → [car icon] → ADAS → Driving Assist.",\n    "source": "Page 1, Right Column, Bullet Point 1 under How to Use"\n  },\n  {\n    "fact": "When the TSR system identifies the current traffic sign, [60 icon] is displayed on the instrument cluster.",\n    "source": "Page 1, Right Column, Bullet Point 2 under How to Use"\n  },\n  {\n    "fact": "When TSR cannot identify whether the recognized speed limit value applies to the lane, [60? icon] is displayed.",\n    "source": "Page 1, Right Column, Bullet Point 3 under How to Use"\n  },\n  {\n    "fact": "When the TSR system experiences reduced performance, [60 with strike-through icon] is displayed.",\n    "source": "Page 1, Right Column, Bullet Point 4 under How to Use"\n  },\n  {\n    "fact": "When the TSR system has a reduced performance and cannot identify whether the recognized speed limit value applies to the lane, [60? with strike-through icon] is displayed.",\n    "source": "Page 1, Right Column, Bullet Point 5 under How to Use"\n  },\n  {\n    "fact": "If the TSR system malfunctions, [TSR malfunction icon] is displayed."\n',
                page_span=RagChunk.PageSpan(first_page=3, last_page=3),
            ),
        )
    ),
]

TEST_CITED_TEXT = (
    "You can activate the parking radar using a switch or through the"
    " infotainment system.[0][1] When the ignition is switched on, the parking"
    " assist system, which includes the reversing radar, is enabled"
    " automatically.[2] The parking assist system detects obstacles using"
    " sensors and alerts the driver with an image on the infotainment"
    " touchscreen and a speaker alarm.[3] You can also enable or disable the"
    " reversing radar specifically by navigating to Home > ADAS > Parking"
    " Assist > Reversing Radar in the infotainment system. Alternatively, there"
    " is a reversing radar switch, often labeled with a 'P' and radiating"
    " lines, on the center console that can be pressed to activate the parking"
    " radar.[2]"
)
TEST_FINAL_BIBLIOGRAPHY = """[0] gs://sample-gcs-directory/file2.pdf, p.15
[1] gs://sample-gcs-directory/file2.pdf, p.14
[2] gs://sample-gcs-directory/file2.pdf, p.16
[3] gs://sample-gcs-directory/file2.pdf, p.16"""
