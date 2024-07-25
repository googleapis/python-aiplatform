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
from __future__ import annotations

from typing import MutableMapping, MutableSequence

import proto  # type: ignore

from google.cloud.aiplatform_v1beta1.types import io
from google.protobuf import timestamp_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "RagEmbeddingModelConfig",
        "RagCorpus",
        "RagFile",
        "RagFileChunkingConfig",
        "UploadRagFileConfig",
        "ImportRagFilesConfig",
    },
)


class RagEmbeddingModelConfig(proto.Message):
    r"""Config for the embedding model to use for RAG.

    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        vertex_prediction_endpoint (google.cloud.aiplatform_v1beta1.types.RagEmbeddingModelConfig.VertexPredictionEndpoint):
            The Vertex AI Prediction Endpoint that either
            refers to a publisher model or an endpoint that
            is hosting a 1P fine-tuned text embedding model.
            Endpoints hosting non-1P fine-tuned text
            embedding models are currently not supported.

            This field is a member of `oneof`_ ``model_config``.
    """

    class VertexPredictionEndpoint(proto.Message):
        r"""Config representing a model hosted on Vertex Prediction
        Endpoint.

        Attributes:
            endpoint (str):
                Required. The endpoint resource name. Format:
                ``projects/{project}/locations/{location}/publishers/{publisher}/models/{model}``
                or
                ``projects/{project}/locations/{location}/endpoints/{endpoint}``
            model (str):
                Output only. The resource name of the model that is deployed
                on the endpoint. Present only when the endpoint is not a
                publisher model. Pattern:
                ``projects/{project}/locations/{location}/models/{model}``
            model_version_id (str):
                Output only. Version ID of the model that is
                deployed on the endpoint. Present only when the
                endpoint is not a publisher model.
        """

        endpoint: str = proto.Field(
            proto.STRING,
            number=1,
        )
        model: str = proto.Field(
            proto.STRING,
            number=2,
        )
        model_version_id: str = proto.Field(
            proto.STRING,
            number=3,
        )

    vertex_prediction_endpoint: VertexPredictionEndpoint = proto.Field(
        proto.MESSAGE,
        number=1,
        oneof="model_config",
        message=VertexPredictionEndpoint,
    )


class RagCorpus(proto.Message):
    r"""A RagCorpus is a RagFile container and a project can have
    multiple RagCorpora.

    Attributes:
        name (str):
            Output only. The resource name of the
            RagCorpus.
        display_name (str):
            Required. The display name of the RagCorpus.
            The name can be up to 128 characters long and
            can consist of any UTF-8 characters.
        description (str):
            Optional. The description of the RagCorpus.
        rag_embedding_model_config (google.cloud.aiplatform_v1beta1.types.RagEmbeddingModelConfig):
            Optional. Immutable. The embedding model
            config of the RagCorpus.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this RagCorpus
            was created.
        update_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this RagCorpus
            was last updated.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    display_name: str = proto.Field(
        proto.STRING,
        number=2,
    )
    description: str = proto.Field(
        proto.STRING,
        number=3,
    )
    rag_embedding_model_config: "RagEmbeddingModelConfig" = proto.Field(
        proto.MESSAGE,
        number=6,
        message="RagEmbeddingModelConfig",
    )
    create_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=4,
        message=timestamp_pb2.Timestamp,
    )
    update_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=5,
        message=timestamp_pb2.Timestamp,
    )


class RagFile(proto.Message):
    r"""A RagFile contains user data for chunking, embedding and
    indexing.

    This message has `oneof`_ fields (mutually exclusive fields).
    For each oneof, at most one member field can be set at the same time.
    Setting any member of the oneof automatically clears all other
    members.

    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        gcs_source (google.cloud.aiplatform_v1beta1.types.GcsSource):
            Output only. Google Cloud Storage location of
            the RagFile. It does not support wildcards in
            the Cloud Storage uri for now.

            This field is a member of `oneof`_ ``rag_file_source``.
        google_drive_source (google.cloud.aiplatform_v1beta1.types.GoogleDriveSource):
            Output only. Google Drive location. Supports
            importing individual files as well as Google
            Drive folders.

            This field is a member of `oneof`_ ``rag_file_source``.
        direct_upload_source (google.cloud.aiplatform_v1beta1.types.DirectUploadSource):
            Output only. The RagFile is encapsulated and
            uploaded in the UploadRagFile request.

            This field is a member of `oneof`_ ``rag_file_source``.
        slack_source (google.cloud.aiplatform_v1beta1.types.SlackSource):
            The RagFile is imported from a Slack channel.

            This field is a member of `oneof`_ ``rag_file_source``.
        jira_source (google.cloud.aiplatform_v1beta1.types.JiraSource):
            The RagFile is imported from a Jira query.

            This field is a member of `oneof`_ ``rag_file_source``.
        name (str):
            Output only. The resource name of the
            RagFile.
        display_name (str):
            Required. The display name of the RagFile.
            The name can be up to 128 characters long and
            can consist of any UTF-8 characters.
        description (str):
            Optional. The description of the RagFile.
        size_bytes (int):
            Output only. The size of the RagFile in
            bytes.
        rag_file_type (google.cloud.aiplatform_v1beta1.types.RagFile.RagFileType):
            Output only. The type of the RagFile.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this RagFile was
            created.
        update_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this RagFile was
            last updated.
    """

    class RagFileType(proto.Enum):
        r"""The type of the RagFile.

        Values:
            RAG_FILE_TYPE_UNSPECIFIED (0):
                RagFile type is unspecified.
            RAG_FILE_TYPE_TXT (1):
                RagFile type is TXT.
            RAG_FILE_TYPE_PDF (2):
                RagFile type is PDF.
        """
        RAG_FILE_TYPE_UNSPECIFIED = 0
        RAG_FILE_TYPE_TXT = 1
        RAG_FILE_TYPE_PDF = 2

    gcs_source: io.GcsSource = proto.Field(
        proto.MESSAGE,
        number=8,
        oneof="rag_file_source",
        message=io.GcsSource,
    )
    google_drive_source: io.GoogleDriveSource = proto.Field(
        proto.MESSAGE,
        number=9,
        oneof="rag_file_source",
        message=io.GoogleDriveSource,
    )
    direct_upload_source: io.DirectUploadSource = proto.Field(
        proto.MESSAGE,
        number=10,
        oneof="rag_file_source",
        message=io.DirectUploadSource,
    )
    slack_source: io.SlackSource = proto.Field(
        proto.MESSAGE,
        number=11,
        oneof="rag_file_source",
        message=io.SlackSource,
    )
    jira_source: io.JiraSource = proto.Field(
        proto.MESSAGE,
        number=12,
        oneof="rag_file_source",
        message=io.JiraSource,
    )
    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    display_name: str = proto.Field(
        proto.STRING,
        number=2,
    )
    description: str = proto.Field(
        proto.STRING,
        number=3,
    )
    size_bytes: int = proto.Field(
        proto.INT64,
        number=4,
    )
    rag_file_type: RagFileType = proto.Field(
        proto.ENUM,
        number=5,
        enum=RagFileType,
    )
    create_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=6,
        message=timestamp_pb2.Timestamp,
    )
    update_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=7,
        message=timestamp_pb2.Timestamp,
    )


class RagFileChunkingConfig(proto.Message):
    r"""Specifies the size and overlap of chunks for RagFiles.

    Attributes:
        chunk_size (int):
            The size of the chunks.
        chunk_overlap (int):
            The overlap between chunks.
    """

    chunk_size: int = proto.Field(
        proto.INT32,
        number=1,
    )
    chunk_overlap: int = proto.Field(
        proto.INT32,
        number=2,
    )


class UploadRagFileConfig(proto.Message):
    r"""Config for uploading RagFile.

    Attributes:
        rag_file_chunking_config (google.cloud.aiplatform_v1beta1.types.RagFileChunkingConfig):
            Specifies the size and overlap of chunks
            after uploading RagFile.
    """

    rag_file_chunking_config: "RagFileChunkingConfig" = proto.Field(
        proto.MESSAGE,
        number=1,
        message="RagFileChunkingConfig",
    )


class ImportRagFilesConfig(proto.Message):
    r"""Config for importing RagFiles.

    This message has `oneof`_ fields (mutually exclusive fields).
    For each oneof, at most one member field can be set at the same time.
    Setting any member of the oneof automatically clears all other
    members.

    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        gcs_source (google.cloud.aiplatform_v1beta1.types.GcsSource):
            Google Cloud Storage location. Supports importing individual
            files as well as entire Google Cloud Storage directories.
            Sample formats:

            -  ``gs://bucket_name/my_directory/object_name/my_file.txt``
            -  ``gs://bucket_name/my_directory``

            This field is a member of `oneof`_ ``import_source``.
        google_drive_source (google.cloud.aiplatform_v1beta1.types.GoogleDriveSource):
            Google Drive location. Supports importing
            individual files as well as Google Drive
            folders.

            This field is a member of `oneof`_ ``import_source``.
        slack_source (google.cloud.aiplatform_v1beta1.types.SlackSource):
            Slack channels with their corresponding
            access tokens.

            This field is a member of `oneof`_ ``import_source``.
        jira_source (google.cloud.aiplatform_v1beta1.types.JiraSource):
            Jira queries with their corresponding
            authentication.

            This field is a member of `oneof`_ ``import_source``.
        rag_file_chunking_config (google.cloud.aiplatform_v1beta1.types.RagFileChunkingConfig):
            Specifies the size and overlap of chunks
            after importing RagFiles.
        max_embedding_requests_per_min (int):
            Optional. The max number of queries per
            minute that this job is allowed to make to the
            embedding model specified on the corpus. This
            value is specific to this job and not shared
            across other import jobs. Consult the Quotas
            page on the project to set an appropriate value
            here. If unspecified, a default value of 1,000
            QPM would be used.
    """

    gcs_source: io.GcsSource = proto.Field(
        proto.MESSAGE,
        number=2,
        oneof="import_source",
        message=io.GcsSource,
    )
    google_drive_source: io.GoogleDriveSource = proto.Field(
        proto.MESSAGE,
        number=3,
        oneof="import_source",
        message=io.GoogleDriveSource,
    )
    slack_source: io.SlackSource = proto.Field(
        proto.MESSAGE,
        number=6,
        oneof="import_source",
        message=io.SlackSource,
    )
    jira_source: io.JiraSource = proto.Field(
        proto.MESSAGE,
        number=7,
        oneof="import_source",
        message=io.JiraSource,
    )
    rag_file_chunking_config: "RagFileChunkingConfig" = proto.Field(
        proto.MESSAGE,
        number=4,
        message="RagFileChunkingConfig",
    )
    max_embedding_requests_per_min: int = proto.Field(
        proto.INT32,
        number=5,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
