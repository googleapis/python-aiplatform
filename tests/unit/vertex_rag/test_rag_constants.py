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

from vertexai.preview.rag.utils.resources import (
    EmbeddingModelConfig,
    RagCorpus,
    RagFile,
    RagResource,
)
from google.cloud import aiplatform
from google.cloud.aiplatform_v1beta1 import (
    GoogleDriveSource,
    RagFileChunkingConfig,
    ImportRagFilesConfig,
    ImportRagFilesRequest,
    ImportRagFilesResponse,
    RagCorpus as GapicRagCorpus,
    RagFile as GapicRagFile,
    RagContexts,
    RetrieveContextsResponse,
)


TEST_PROJECT = "test-project"
TEST_PROJECT_NUMBER = "12345678"
TEST_REGION = "us-central1"
TEST_CORPUS_DISPLAY_NAME = "my-corpus-1"
TEST_CORPUS_DISCRIPTION = "My first corpus."
TEST_RAG_CORPUS_ID = "generate-123"
TEST_API_ENDPOINT = "us-central1-" + aiplatform.constants.base.API_BASE_PATH
TEST_RAG_CORPUS_RESOURCE_NAME = f"projects/{TEST_PROJECT_NUMBER}/locations/{TEST_REGION}/ragCorpora/{TEST_RAG_CORPUS_ID}"

# RagCorpus
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
TEST_EMBEDDING_MODEL_CONFIG = EmbeddingModelConfig(
    publisher_model="publishers/google/models/textembedding-gecko",
)
TEST_RAG_CORPUS = RagCorpus(
    name=TEST_RAG_CORPUS_RESOURCE_NAME,
    display_name=TEST_CORPUS_DISPLAY_NAME,
    description=TEST_CORPUS_DISCRIPTION,
    embedding_model_config=TEST_EMBEDDING_MODEL_CONFIG,
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
TEST_IMPORT_REQUEST_DRIVE_FOLDER = ImportRagFilesRequest(
    parent=TEST_RAG_CORPUS_RESOURCE_NAME,
    import_rag_files_config=TEST_IMPORT_FILES_CONFIG_DRIVE_FOLDER,
)
# Google Drive files
TEST_DRIVE_FILE_ID = "456"
TEST_DRIVE_FILE = f"https://drive.google.com/file/d/{TEST_DRIVE_FILE_ID}"
TEST_IMPORT_FILES_CONFIG_DRIVE_FILE = ImportRagFilesConfig(
    rag_file_chunking_config=RagFileChunkingConfig(
        chunk_size=TEST_CHUNK_SIZE,
        chunk_overlap=TEST_CHUNK_OVERLAP,
    )
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
