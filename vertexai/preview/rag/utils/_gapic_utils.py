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
import re
from typing import Any, Dict, Sequence, Union
from google.cloud.aiplatform_v1beta1 import (
    RagEmbeddingModelConfig,
    GoogleDriveSource,
    ImportRagFilesConfig,
    ImportRagFilesRequest,
    RagFileChunkingConfig,
    RagCorpus as GapicRagCorpus,
    RagFile as GapicRagFile,
)
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.utils import (
    VertexRagDataAsyncClientWithOverride,
    VertexRagDataClientWithOverride,
    VertexRagClientWithOverride,
)
from vertexai.preview.rag.utils.resources import (
    EmbeddingModelConfig,
    RagCorpus,
    RagFile,
)


_VALID_RESOURCE_NAME_REGEX = "[a-z][a-zA-Z0-9._-]{0,127}"


def create_rag_data_service_client():
    return initializer.global_config.create_client(
        client_class=VertexRagDataClientWithOverride,
    )


def create_rag_data_service_async_client():
    return initializer.global_config.create_client(
        client_class=VertexRagDataAsyncClientWithOverride,
    )


def create_rag_service_client():
    return initializer.global_config.create_client(
        client_class=VertexRagClientWithOverride,
    )


def convert_gapic_to_embedding_model_config(
    gapic_embedding_model_config: RagEmbeddingModelConfig,
) -> EmbeddingModelConfig:
    """Convert GapicRagEmbeddingModelConfig to EmbeddingModelConfig."""
    embedding_model_config = EmbeddingModelConfig()
    path = gapic_embedding_model_config.vertex_prediction_endpoint.endpoint
    publisher_model = re.match(
        r"^projects/(?P<project>.+?)/locations/(?P<location>.+?)/publishers/google/models/(?P<model_id>.+?)$",
        path,
    )
    endpoint = re.match(
        r"^projects/(?P<project>.+?)/locations/(?P<location>.+?)/endpoints/(?P<endpoint>.+?)$",
        path,
    )
    if publisher_model:
        embedding_model_config.publisher_model = path
    if endpoint:
        embedding_model_config.endpoint = path
        embedding_model_config.model = (
            gapic_embedding_model_config.vertex_prediction_endpoint.model
        )
        embedding_model_config.model_version_id = (
            gapic_embedding_model_config.vertex_prediction_endpoint.model_version_id
        )

    return embedding_model_config


def convert_gapic_to_rag_corpus(gapic_rag_corpus: GapicRagCorpus) -> RagCorpus:
    """ "Convert GapicRagCorpus to RagCorpus."""
    rag_corpus = RagCorpus(
        name=gapic_rag_corpus.name,
        display_name=gapic_rag_corpus.display_name,
        description=gapic_rag_corpus.description,
        embedding_model_config=convert_gapic_to_embedding_model_config(
            gapic_rag_corpus.rag_embedding_model_config
        ),
    )
    return rag_corpus


def convert_gapic_to_rag_file(gapic_rag_file: GapicRagFile) -> RagFile:
    """ "Convert GapicRagFile to RagFile."""
    rag_file = RagFile(
        name=gapic_rag_file.name,
        display_name=gapic_rag_file.display_name,
        description=gapic_rag_file.description,
    )
    return rag_file


def convert_json_to_rag_file(upload_rag_file_response: Dict[str, Any]) -> RagFile:
    """Converts a JSON response to a RagFile."""
    rag_file = RagFile(
        name=upload_rag_file_response.get("ragFile").get("name"),
        display_name=upload_rag_file_response.get("ragFile").get("displayName"),
    )
    return rag_file


def convert_path_to_resource_id(
    path: str,
) -> Union[str, GoogleDriveSource.ResourceId]:
    """Converts a path to a Google Cloud storage uri or GoogleDriveSource.ResourceId."""
    if path.startswith("gs://"):
        # Google Cloud Storage source
        return path
    elif path.startswith("https://drive.google.com/"):
        # Google Drive source
        path_list = path.split("/")
        if "file" in path_list:
            index = path_list.index("file") + 2
            resource_id = path_list[index].split("?")[0]
            resource_type = GoogleDriveSource.ResourceId.ResourceType.RESOURCE_TYPE_FILE
        elif "folders" in path_list:
            index = path_list.index("folders") + 1
            resource_id = path_list[index].split("?")[0]
            resource_type = (
                GoogleDriveSource.ResourceId.ResourceType.RESOURCE_TYPE_FOLDER
            )
        else:
            raise ValueError("path %s is not a valid Google Drive url.", path)

        return GoogleDriveSource.ResourceId(
            resource_id=resource_id,
            resource_type=resource_type,
        )
    else:
        raise ValueError(
            "path must be a Google Cloud Storage uri or a Google Drive url."
        )


def prepare_import_files_request(
    corpus_name: str,
    paths: Sequence[str],
    chunk_size: int = 1024,
    chunk_overlap: int = 200,
    max_embedding_requests_per_min: int = 1000,
) -> ImportRagFilesRequest:
    if len(corpus_name.split("/")) != 6:
        raise ValueError(
            "corpus_name must be of the format `projects/{project}/locations/{location}/ragCorpora/{rag_corpus}`"
        )

    rag_file_chunking_config = RagFileChunkingConfig(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    import_rag_files_config = ImportRagFilesConfig(
        rag_file_chunking_config=rag_file_chunking_config,
        max_embedding_requests_per_min=max_embedding_requests_per_min,
    )

    uris = []
    resource_ids = []
    for p in paths:
        output = convert_path_to_resource_id(p)
        if isinstance(output, str):
            uris.append(p)
        else:
            resource_ids.append(output)

    if uris:
        import_rag_files_config.gcs_source.uris = uris
    if resource_ids:
        google_drive_source = GoogleDriveSource(
            resource_ids=resource_ids,
        )
        import_rag_files_config.google_drive_source = google_drive_source

    request = ImportRagFilesRequest(
        parent=corpus_name, import_rag_files_config=import_rag_files_config
    )
    return request


def get_corpus_name(
    name: str,
) -> str:
    if name:
        client = create_rag_data_service_client()
        if client.parse_rag_corpus_path(name):
            return name
        elif re.match("^{}$".format(_VALID_RESOURCE_NAME_REGEX), name):
            return client.rag_corpus_path(
                project=initializer.global_config.project,
                location=initializer.global_config.location,
                rag_corpus=name,
            )
        else:
            raise ValueError(
                "name must be of the format `projects/{project}/locations/{location}/ragCorpora/{rag_corpus}` or `{rag_corpus}`"
            )
    return name


def get_file_name(
    name: str,
    corpus_name: str,
) -> str:
    client = create_rag_data_service_client()
    if client.parse_rag_file_path(name):
        return name
    elif re.match("^{}$".format(_VALID_RESOURCE_NAME_REGEX), name):
        if not corpus_name:
            raise ValueError(
                "corpus_name must be provided if name is a `{rag_file}`, not a "
                "full resource name (`projects/{project}/locations/{location}/ragCorpora/{rag_corpus}/ragFiles/{rag_file}`). "
            )
        return client.rag_file_path(
            project=initializer.global_config.project,
            location=initializer.global_config.location,
            rag_corpus=get_corpus_name(corpus_name),
            rag_file=name,
        )
    else:
        raise ValueError(
            "name must be of the format `projects/{project}/locations/{location}/ragCorpora/{rag_corpus}/ragFiles/{rag_file}` or `{rag_file}`"
        )


def set_embedding_model_config(
    embedding_model_config: EmbeddingModelConfig,
    rag_corpus: GapicRagCorpus,
) -> GapicRagCorpus:
    if embedding_model_config.publisher_model and embedding_model_config.endpoint:
        raise ValueError("publisher_model and endpoint cannot be set at the same time.")
    if (
        not embedding_model_config.publisher_model
        and not embedding_model_config.endpoint
    ):
        raise ValueError("At least one of publisher_model and endpoint must be set.")
    parent = initializer.global_config.common_location_path(project=None, location=None)

    if embedding_model_config.publisher_model:
        publisher_model = embedding_model_config.publisher_model
        full_resource_name = re.match(
            r"^projects/(?P<project>.+?)/locations/(?P<location>.+?)/publishers/google/models/(?P<model_id>.+?)$",
            publisher_model,
        )
        resource_name = re.match(
            r"^publishers/google/models/(?P<model_id>.+?)$",
            publisher_model,
        )
        if full_resource_name:
            rag_corpus.rag_embedding_model_config.vertex_prediction_endpoint.endpoint = (
                publisher_model
            )
        elif resource_name:
            rag_corpus.rag_embedding_model_config.vertex_prediction_endpoint.endpoint = (
                parent + "/" + publisher_model
            )
        else:
            raise ValueError(
                "publisher_model must be of the format `projects/{project}/locations/{location}/publishers/google/models/{model_id}` or `publishers/google/models/{model_id}`"
            )

    if embedding_model_config.endpoint:
        endpoint = embedding_model_config.endpoint
        full_resource_name = re.match(
            r"^projects/(?P<project>.+?)/locations/(?P<location>.+?)/endpoints/(?P<endpoint>.+?)$",
            endpoint,
        )
        resource_name = re.match(
            r"^endpoints/(?P<endpoint>.+?)$",
            endpoint,
        )
        if full_resource_name:
            rag_corpus.rag_embedding_model_config.vertex_prediction_endpoint.endpoint = (
                endpoint
            )
        elif resource_name:
            rag_corpus.rag_embedding_model_config.vertex_prediction_endpoint.endpoint = (
                parent + "/" + endpoint
            )
        else:
            raise ValueError(
                "endpoint must be of the format `projects/{project}/locations/{location}/endpoints/{endpoint}` or `endpoints/{endpoint}`"
            )

    return rag_corpus
