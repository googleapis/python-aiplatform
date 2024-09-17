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

from vertexai.preview.rag import (
    EmbeddingModelConfig,
    Pinecone,
    RagCorpus,
    RagFile,
    RagResource,
    SlackChannelsSource,
    SlackChannel,
    JiraSource,
    JiraQuery,
    Weaviate,
    VertexVectorSearch,
    VertexFeatureStore,
)
from google.cloud.aiplatform_v1beta1 import (
    GoogleDriveSource,
    RagFileChunkingConfig,
    RagFileParsingConfig,
    ImportRagFilesConfig,
    ImportRagFilesRequest,
    ImportRagFilesResponse,
    JiraSource as GapicJiraSource,
    RagCorpus as GapicRagCorpus,
    RagFile as GapicRagFile,
    SlackSource as GapicSlackSource,
    RagContexts,
    RetrieveContextsResponse,
    RagVectorDbConfig,
)
from google.cloud.aiplatform_v1beta1.types import api_auth
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
TEST_GAPIC_RAG_CORPUS_WEAVIATE = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    rag_vector_db_config=RagVectorDbConfig(
        weaviate=RagVectorDbConfig.Weaviate(
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
    rag_vector_db_config=RagVectorDbConfig(
        vertex_feature_store=RagVectorDbConfig.VertexFeatureStore(
            feature_view_resource_name=TEST_VERTEX_FEATURE_STORE_RESOURCE_NAME
        ),
    ),
)
TEST_GAPIC_RAG_CORPUS_VERTEX_VECTOR_SEARCH = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    rag_vector_db_config=RagVectorDbConfig(
        vertex_vector_search=RagVectorDbConfig.VertexVectorSearch(
            index_endpoint=TEST_VERTEX_VECTOR_SEARCH_INDEX_ENDPOINT,
            index=TEST_VERTEX_VECTOR_SEARCH_INDEX,
        ),
    ),
)
TEST_GAPIC_RAG_CORPUS_PINECONE = GapicRagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    rag_vector_db_config=RagVectorDbConfig(
        pinecone=RagVectorDbConfig.Pinecone(index_name=TEST_PINECONE_INDEX_NAME),
        api_auth=api_auth.ApiAuth(
            api_key_config=api_auth.ApiAuth.ApiKeyConfig(
                api_key_secret_version=TEST_PINECONE_API_KEY_SECRET_VERSION
            ),
        ),
    ),
)
TEST_EMBEDDING_MODEL_CONFIG = EmbeddingModelConfig(
    publisher_model="publishers/google/models/textembedding-gecko",
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
TEST_RAG_CORPUS_VERTEX_VECTOR_SEARCH = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    vector_db=TEST_VERTEX_VECTOR_SEARCH_CONFIG,
)
TEST_PAGE_TOKEN = "test-page-token"

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
# GCS
TEST_IMPORT_FILES_CONFIG_GCS = ImportRagFilesConfig()
TEST_IMPORT_FILES_CONFIG_GCS.gcs_source.uris = [TEST_GCS_PATH]
TEST_IMPORT_FILES_CONFIG_GCS.rag_file_parsing_config.use_advanced_pdf_parsing = False
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
TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER = ImportRagFilesConfig()
TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER.google_drive_source.resource_ids = [
    GoogleDriveSource.ResourceId(
        resource_id=TEST_DRIVE_FOLDER_ID,
        resource_type=GoogleDriveSource.ResourceId.ResourceType.RESOURCE_TYPE_FOLDER,
    )
]
TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER.rag_file_parsing_config.use_advanced_pdf_parsing = (
    False
)
TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER_PARSING = ImportRagFilesConfig()
TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER_PARSING.google_drive_source.resource_ids = [
    GoogleDriveSource.ResourceId(
        resource_id=TEST_DRIVE_FOLDER_ID,
        resource_type=GoogleDriveSource.ResourceId.ResourceType.RESOURCE_TYPE_FOLDER,
    )
]
TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER_PARSING.rag_file_parsing_config.use_advanced_pdf_parsing = (
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
# Google Drive files
TEST_DRIVE_FILE_ID = "456"
TEST_DRIVE_FILE = f"https://drive.google.com/file/d/{TEST_DRIVE_FILE_ID}"
TEST_IMPORT_FILES_CONFIG_DRIVE_FILE = ImportRagFilesConfig(
    rag_file_chunking_config=RagFileChunkingConfig(
        chunk_size=TEST_CHUNK_SIZE,
        chunk_overlap=TEST_CHUNK_OVERLAP,
    ),
    rag_file_parsing_config=RagFileParsingConfig(use_advanced_pdf_parsing=False),
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
    rag_file_chunking_config=RagFileChunkingConfig(
        chunk_size=TEST_CHUNK_SIZE,
        chunk_overlap=TEST_CHUNK_OVERLAP,
    )
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
    rag_file_chunking_config=RagFileChunkingConfig(
        chunk_size=TEST_CHUNK_SIZE,
        chunk_overlap=TEST_CHUNK_OVERLAP,
    )
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
