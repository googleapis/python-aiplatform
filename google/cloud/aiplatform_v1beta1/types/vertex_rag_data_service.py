# -*- coding: utf-8 -*-
# Copyright 2025 Google LLC
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

from google.cloud.aiplatform_v1beta1.types import operation
from google.cloud.aiplatform_v1beta1.types import vertex_rag_data
import google.rpc.status_pb2 as status_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "CreateRagCorpusRequest",
        "GetRagCorpusRequest",
        "ListRagCorporaRequest",
        "ListRagCorporaResponse",
        "DeleteRagCorpusRequest",
        "UploadRagFileRequest",
        "UploadRagFileResponse",
        "ImportRagFilesRequest",
        "ImportRagFilesResponse",
        "GetRagFileRequest",
        "ListRagFilesRequest",
        "ListRagFilesResponse",
        "DeleteRagFileRequest",
        "CreateRagCorpusOperationMetadata",
        "GetRagEngineConfigRequest",
        "UpdateRagCorpusRequest",
        "UpdateRagCorpusOperationMetadata",
        "ImportRagFilesOperationMetadata",
        "UpdateRagEngineConfigRequest",
        "UpdateRagEngineConfigOperationMetadata",
        "BatchCreateRagDataSchemasOperationMetadata",
        "BatchCreateRagMetadataOperationMetadata",
        "BatchCreateRagDataSchemasResponse",
        "BatchCreateRagMetadataResponse",
        "CreateRagDataSchemaRequest",
        "BatchCreateRagDataSchemasRequest",
        "GetRagDataSchemaRequest",
        "ListRagDataSchemasRequest",
        "ListRagDataSchemasResponse",
        "BatchDeleteRagDataSchemasRequest",
        "DeleteRagDataSchemaRequest",
        "CreateRagMetadataRequest",
        "BatchCreateRagMetadataRequest",
        "UpdateRagMetadataRequest",
        "GetRagMetadataRequest",
        "ListRagMetadataRequest",
        "ListRagMetadataResponse",
        "DeleteRagMetadataRequest",
        "BatchDeleteRagMetadataRequest",
    },
)


class CreateRagCorpusRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.CreateRagCorpus][google.cloud.aiplatform.v1beta1.VertexRagDataService.CreateRagCorpus].

    Attributes:
        parent (str):
            Required. The resource name of the Location to create the
            RagCorpus in. Format:
            ``projects/{project}/locations/{location}``
        rag_corpus (google.cloud.aiplatform_v1beta1.types.RagCorpus):
            Required. The RagCorpus to create.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    rag_corpus: vertex_rag_data.RagCorpus = proto.Field(
        proto.MESSAGE,
        number=2,
        message=vertex_rag_data.RagCorpus,
    )


class GetRagCorpusRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.GetRagCorpus][google.cloud.aiplatform.v1beta1.VertexRagDataService.GetRagCorpus]

    Attributes:
        name (str):
            Required. The name of the RagCorpus resource. Format:
            ``projects/{project}/locations/{location}/ragCorpora/{rag_corpus}``
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class ListRagCorporaRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.ListRagCorpora][google.cloud.aiplatform.v1beta1.VertexRagDataService.ListRagCorpora].

    Attributes:
        parent (str):
            Required. The resource name of the Location from which to
            list the RagCorpora. Format:
            ``projects/{project}/locations/{location}``
        page_size (int):
            Optional. The standard list page size.
        page_token (str):
            Optional. The standard list page token. Typically obtained
            via
            [ListRagCorporaResponse.next_page_token][google.cloud.aiplatform.v1beta1.ListRagCorporaResponse.next_page_token]
            of the previous
            [VertexRagDataService.ListRagCorpora][google.cloud.aiplatform.v1beta1.VertexRagDataService.ListRagCorpora]
            call.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    page_size: int = proto.Field(
        proto.INT32,
        number=2,
    )
    page_token: str = proto.Field(
        proto.STRING,
        number=3,
    )


class ListRagCorporaResponse(proto.Message):
    r"""Response message for
    [VertexRagDataService.ListRagCorpora][google.cloud.aiplatform.v1beta1.VertexRagDataService.ListRagCorpora].

    Attributes:
        rag_corpora (MutableSequence[google.cloud.aiplatform_v1beta1.types.RagCorpus]):
            List of RagCorpora in the requested page.
        next_page_token (str):
            A token to retrieve the next page of results. Pass to
            [ListRagCorporaRequest.page_token][google.cloud.aiplatform.v1beta1.ListRagCorporaRequest.page_token]
            to obtain that page.
    """

    @property
    def raw_page(self):
        return self

    rag_corpora: MutableSequence[vertex_rag_data.RagCorpus] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message=vertex_rag_data.RagCorpus,
    )
    next_page_token: str = proto.Field(
        proto.STRING,
        number=2,
    )


class DeleteRagCorpusRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.DeleteRagCorpus][google.cloud.aiplatform.v1beta1.VertexRagDataService.DeleteRagCorpus].

    Attributes:
        name (str):
            Required. The name of the RagCorpus resource to be deleted.
            Format:
            ``projects/{project}/locations/{location}/ragCorpora/{rag_corpus}``
        force (bool):
            Optional. If set to true, any RagFiles in
            this RagCorpus will also be deleted. Otherwise,
            the request will only work if the RagCorpus has
            no RagFiles.
        force_delete (bool):
            Optional. If set to true, any errors
            generated by external vector database during the
            deletion will be ignored. The default value is
            false.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    force: bool = proto.Field(
        proto.BOOL,
        number=2,
    )
    force_delete: bool = proto.Field(
        proto.BOOL,
        number=3,
    )


class UploadRagFileRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.UploadRagFile][google.cloud.aiplatform.v1beta1.VertexRagDataService.UploadRagFile].

    Attributes:
        parent (str):
            Required. The name of the RagCorpus resource into which to
            upload the file. Format:
            ``projects/{project}/locations/{location}/ragCorpora/{rag_corpus}``
        rag_file (google.cloud.aiplatform_v1beta1.types.RagFile):
            Required. The RagFile to upload.
        upload_rag_file_config (google.cloud.aiplatform_v1beta1.types.UploadRagFileConfig):
            Required. The config for the RagFiles to be uploaded into
            the RagCorpus.
            [VertexRagDataService.UploadRagFile][google.cloud.aiplatform.v1beta1.VertexRagDataService.UploadRagFile].
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    rag_file: vertex_rag_data.RagFile = proto.Field(
        proto.MESSAGE,
        number=2,
        message=vertex_rag_data.RagFile,
    )
    upload_rag_file_config: vertex_rag_data.UploadRagFileConfig = proto.Field(
        proto.MESSAGE,
        number=5,
        message=vertex_rag_data.UploadRagFileConfig,
    )


class UploadRagFileResponse(proto.Message):
    r"""Response message for
    [VertexRagDataService.UploadRagFile][google.cloud.aiplatform.v1beta1.VertexRagDataService.UploadRagFile].

    This message has `oneof`_ fields (mutually exclusive fields).
    For each oneof, at most one member field can be set at the same time.
    Setting any member of the oneof automatically clears all other
    members.

    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        rag_file (google.cloud.aiplatform_v1beta1.types.RagFile):
            The RagFile that had been uploaded into the
            RagCorpus.

            This field is a member of `oneof`_ ``result``.
        error (google.rpc.status_pb2.Status):
            The error that occurred while processing the
            RagFile.

            This field is a member of `oneof`_ ``result``.
    """

    rag_file: vertex_rag_data.RagFile = proto.Field(
        proto.MESSAGE,
        number=1,
        oneof="result",
        message=vertex_rag_data.RagFile,
    )
    error: status_pb2.Status = proto.Field(
        proto.MESSAGE,
        number=4,
        oneof="result",
        message=status_pb2.Status,
    )


class ImportRagFilesRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.ImportRagFiles][google.cloud.aiplatform.v1beta1.VertexRagDataService.ImportRagFiles].

    Attributes:
        parent (str):
            Required. The name of the RagCorpus resource into which to
            import files. Format:
            ``projects/{project}/locations/{location}/ragCorpora/{rag_corpus}``
        import_rag_files_config (google.cloud.aiplatform_v1beta1.types.ImportRagFilesConfig):
            Required. The config for the RagFiles to be synced and
            imported into the RagCorpus.
            [VertexRagDataService.ImportRagFiles][google.cloud.aiplatform.v1beta1.VertexRagDataService.ImportRagFiles].
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    import_rag_files_config: vertex_rag_data.ImportRagFilesConfig = proto.Field(
        proto.MESSAGE,
        number=2,
        message=vertex_rag_data.ImportRagFilesConfig,
    )


class ImportRagFilesResponse(proto.Message):
    r"""Response message for
    [VertexRagDataService.ImportRagFiles][google.cloud.aiplatform.v1beta1.VertexRagDataService.ImportRagFiles].

    This message has `oneof`_ fields (mutually exclusive fields).
    For each oneof, at most one member field can be set at the same time.
    Setting any member of the oneof automatically clears all other
    members.

    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        partial_failures_gcs_path (str):
            The Google Cloud Storage path into which the
            partial failures were written.

            This field is a member of `oneof`_ ``partial_failure_sink``.
        partial_failures_bigquery_table (str):
            The BigQuery table into which the partial
            failures were written.

            This field is a member of `oneof`_ ``partial_failure_sink``.
        imported_rag_files_count (int):
            The number of RagFiles that had been imported
            into the RagCorpus.
        failed_rag_files_count (int):
            The number of RagFiles that had failed while
            importing into the RagCorpus.
        skipped_rag_files_count (int):
            The number of RagFiles that was skipped while
            importing into the RagCorpus.
    """

    partial_failures_gcs_path: str = proto.Field(
        proto.STRING,
        number=4,
        oneof="partial_failure_sink",
    )
    partial_failures_bigquery_table: str = proto.Field(
        proto.STRING,
        number=5,
        oneof="partial_failure_sink",
    )
    imported_rag_files_count: int = proto.Field(
        proto.INT64,
        number=1,
    )
    failed_rag_files_count: int = proto.Field(
        proto.INT64,
        number=2,
    )
    skipped_rag_files_count: int = proto.Field(
        proto.INT64,
        number=3,
    )


class GetRagFileRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.GetRagFile][google.cloud.aiplatform.v1beta1.VertexRagDataService.GetRagFile]

    Attributes:
        name (str):
            Required. The name of the RagFile resource. Format:
            ``projects/{project}/locations/{location}/ragCorpora/{rag_corpus}/ragFiles/{rag_file}``
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class ListRagFilesRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.ListRagFiles][google.cloud.aiplatform.v1beta1.VertexRagDataService.ListRagFiles].

    Attributes:
        parent (str):
            Required. The resource name of the RagCorpus from which to
            list the RagFiles. Format:
            ``projects/{project}/locations/{location}/ragCorpora/{rag_corpus}``
        page_size (int):
            Optional. The standard list page size.
        page_token (str):
            Optional. The standard list page token. Typically obtained
            via
            [ListRagFilesResponse.next_page_token][google.cloud.aiplatform.v1beta1.ListRagFilesResponse.next_page_token]
            of the previous
            [VertexRagDataService.ListRagFiles][google.cloud.aiplatform.v1beta1.VertexRagDataService.ListRagFiles]
            call.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    page_size: int = proto.Field(
        proto.INT32,
        number=2,
    )
    page_token: str = proto.Field(
        proto.STRING,
        number=3,
    )


class ListRagFilesResponse(proto.Message):
    r"""Response message for
    [VertexRagDataService.ListRagFiles][google.cloud.aiplatform.v1beta1.VertexRagDataService.ListRagFiles].

    Attributes:
        rag_files (MutableSequence[google.cloud.aiplatform_v1beta1.types.RagFile]):
            List of RagFiles in the requested page.
        next_page_token (str):
            A token to retrieve the next page of results. Pass to
            [ListRagFilesRequest.page_token][google.cloud.aiplatform.v1beta1.ListRagFilesRequest.page_token]
            to obtain that page.
    """

    @property
    def raw_page(self):
        return self

    rag_files: MutableSequence[vertex_rag_data.RagFile] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message=vertex_rag_data.RagFile,
    )
    next_page_token: str = proto.Field(
        proto.STRING,
        number=2,
    )


class DeleteRagFileRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.DeleteRagFile][google.cloud.aiplatform.v1beta1.VertexRagDataService.DeleteRagFile].

    Attributes:
        name (str):
            Required. The name of the RagFile resource to be deleted.
            Format:
            ``projects/{project}/locations/{location}/ragCorpora/{rag_corpus}/ragFiles/{rag_file}``
        force_delete (bool):
            Optional. If set to true, any errors
            generated by external vector database during the
            deletion will be ignored. The default value is
            false.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    force_delete: bool = proto.Field(
        proto.BOOL,
        number=2,
    )


class CreateRagCorpusOperationMetadata(proto.Message):
    r"""Runtime operation information for
    [VertexRagDataService.CreateRagCorpus][google.cloud.aiplatform.v1beta1.VertexRagDataService.CreateRagCorpus].

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1beta1.types.GenericOperationMetadata):
            The operation generic information.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )


class GetRagEngineConfigRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.GetRagEngineConfig][google.cloud.aiplatform.v1beta1.VertexRagDataService.GetRagEngineConfig]

    Attributes:
        name (str):
            Required. The name of the RagEngineConfig resource. Format:
            ``projects/{project}/locations/{location}/ragEngineConfig``
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class UpdateRagCorpusRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.UpdateRagCorpus][google.cloud.aiplatform.v1beta1.VertexRagDataService.UpdateRagCorpus].

    Attributes:
        rag_corpus (google.cloud.aiplatform_v1beta1.types.RagCorpus):
            Required. The RagCorpus which replaces the
            resource on the server.
    """

    rag_corpus: vertex_rag_data.RagCorpus = proto.Field(
        proto.MESSAGE,
        number=1,
        message=vertex_rag_data.RagCorpus,
    )


class UpdateRagCorpusOperationMetadata(proto.Message):
    r"""Runtime operation information for
    [VertexRagDataService.UpdateRagCorpus][google.cloud.aiplatform.v1beta1.VertexRagDataService.UpdateRagCorpus].

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1beta1.types.GenericOperationMetadata):
            The operation generic information.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )


class ImportRagFilesOperationMetadata(proto.Message):
    r"""Runtime operation information for
    [VertexRagDataService.ImportRagFiles][google.cloud.aiplatform.v1beta1.VertexRagDataService.ImportRagFiles].

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1beta1.types.GenericOperationMetadata):
            The operation generic information.
        rag_corpus_id (int):
            The resource ID of RagCorpus that this
            operation is executed on.
        import_rag_files_config (google.cloud.aiplatform_v1beta1.types.ImportRagFilesConfig):
            Output only. The config that was passed in
            the ImportRagFilesRequest.
        progress_percentage (int):
            The progress percentage of the operation. Value is in the
            range [0, 100]. This percentage is calculated as follows:
            progress_percentage = 100 \* (successes + failures + skips)
            / total
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )
    rag_corpus_id: int = proto.Field(
        proto.INT64,
        number=2,
    )
    import_rag_files_config: vertex_rag_data.ImportRagFilesConfig = proto.Field(
        proto.MESSAGE,
        number=3,
        message=vertex_rag_data.ImportRagFilesConfig,
    )
    progress_percentage: int = proto.Field(
        proto.INT32,
        number=4,
    )


class UpdateRagEngineConfigRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.UpdateRagEngineConfig][google.cloud.aiplatform.v1beta1.VertexRagDataService.UpdateRagEngineConfig].

    Attributes:
        rag_engine_config (google.cloud.aiplatform_v1beta1.types.RagEngineConfig):
            Required. The updated RagEngineConfig.

            NOTE: Downgrading your RagManagedDb's
            ComputeTier could temporarily increase request
            latencies until the operation is fully complete.
    """

    rag_engine_config: vertex_rag_data.RagEngineConfig = proto.Field(
        proto.MESSAGE,
        number=1,
        message=vertex_rag_data.RagEngineConfig,
    )


class UpdateRagEngineConfigOperationMetadata(proto.Message):
    r"""Runtime operation information for
    [VertexRagDataService.UpdateRagEngineConfig][google.cloud.aiplatform.v1beta1.VertexRagDataService.UpdateRagEngineConfig].

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1beta1.types.GenericOperationMetadata):
            The operation generic information.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )


class BatchCreateRagDataSchemasOperationMetadata(proto.Message):
    r"""Runtime operation information for
    [VertexRagDataService.BatchCreateRagDataSchemas][google.cloud.aiplatform.v1beta1.VertexRagDataService.BatchCreateRagDataSchemas].

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1beta1.types.GenericOperationMetadata):
            The operation generic information.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )


class BatchCreateRagMetadataOperationMetadata(proto.Message):
    r"""Runtime operation information for
    [VertexRagDataService.BatchCreateRagMetadata][google.cloud.aiplatform.v1beta1.VertexRagDataService.BatchCreateRagMetadata].

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1beta1.types.GenericOperationMetadata):
            The operation generic information.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )


class BatchCreateRagDataSchemasResponse(proto.Message):
    r"""Response message for
    [VertexRagDataService.BatchCreateRagDataSchemas][google.cloud.aiplatform.v1beta1.VertexRagDataService.BatchCreateRagDataSchemas].

    Attributes:
        rag_data_schemas (MutableSequence[google.cloud.aiplatform_v1beta1.types.RagDataSchema]):
            RagDataSchemas created.
    """

    rag_data_schemas: MutableSequence[vertex_rag_data.RagDataSchema] = (
        proto.RepeatedField(
            proto.MESSAGE,
            number=1,
            message=vertex_rag_data.RagDataSchema,
        )
    )


class BatchCreateRagMetadataResponse(proto.Message):
    r"""Response message for
    [VertexRagDataService.BatchCreateRagMetadata][google.cloud.aiplatform.v1beta1.VertexRagDataService.BatchCreateRagMetadata].

    Attributes:
        rag_metadata (MutableSequence[google.cloud.aiplatform_v1beta1.types.RagMetadata]):
            RagMetadata created.
    """

    rag_metadata: MutableSequence[vertex_rag_data.RagMetadata] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message=vertex_rag_data.RagMetadata,
    )


class CreateRagDataSchemaRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.CreateRagDataSchema][google.cloud.aiplatform.v1beta1.VertexRagDataService.CreateRagDataSchema].


    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        parent (str):
            Required. The resource name of the RagCorpus to create the
            RagDataSchema in. Format:
            ``projects/{project}/locations/{location}/ragCorpora/{rag_corpus}``
        rag_data_schema (google.cloud.aiplatform_v1beta1.types.RagDataSchema):
            Required. The RagDataSchema to create.
        rag_data_schema_id (str):
            Optional. The ID to use for the RagDataSchema, which will
            become the final component of the RagDataSchema's resource
            name if the user chooses to specify. Otherwise,
            RagDataSchema id will be generated by system.

            This value should be up to 63 characters, and valid
            characters are /[a-z][0-9]-/. The first character must be a
            letter, the last could be a letter or a number.

            This field is a member of `oneof`_ ``_rag_data_schema_id``.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    rag_data_schema: vertex_rag_data.RagDataSchema = proto.Field(
        proto.MESSAGE,
        number=2,
        message=vertex_rag_data.RagDataSchema,
    )
    rag_data_schema_id: str = proto.Field(
        proto.STRING,
        number=3,
        optional=True,
    )


class BatchCreateRagDataSchemasRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.BatchCreateRagDataSchemas][google.cloud.aiplatform.v1beta1.VertexRagDataService.BatchCreateRagDataSchemas].

    Attributes:
        parent (str):
            Required. The resource name of the RagCorpus to create the
            RagDataSchemas in. Format:
            ``projects/{project}/locations/{location}/ragCorpora/{rag_corpus}``
        requests (MutableSequence[google.cloud.aiplatform_v1beta1.types.CreateRagDataSchemaRequest]):
            Required. The request messages for
            [VertexRagDataService.CreateRagDataSchema][google.cloud.aiplatform.v1beta1.VertexRagDataService.CreateRagDataSchema].
            A maximum of 500 schemas can be created in a batch.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    requests: MutableSequence["CreateRagDataSchemaRequest"] = proto.RepeatedField(
        proto.MESSAGE,
        number=2,
        message="CreateRagDataSchemaRequest",
    )


class GetRagDataSchemaRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.GetRagDataSchema][google.cloud.aiplatform.v1beta1.VertexRagDataService.GetRagDataSchema]

    Attributes:
        name (str):
            Required. The name of the RagDataSchema resource. Format:
            ``projects/{project}/locations/{location}/ragCorpora/{rag_corpus}/ragDataSchemas/{rag_data_schema}``
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class ListRagDataSchemasRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.ListRagDataSchemas][google.cloud.aiplatform.v1beta1.VertexRagDataService.ListRagDataSchemas].

    Attributes:
        parent (str):
            Required. The resource name of the RagCorpus from which to
            list the RagDataSchemas. Format:
            ``projects/{project}/locations/{location}/ragCorpora/{rag_corpus}``
        page_size (int):
            Optional. The standard list page size. The
            maximum value is 100. If not specified, a
            default value of 100 will be used.
        page_token (str):
            Optional. The standard list page token. Typically obtained
            via
            [ListRagDataSchemasResponse.next_page_token][google.cloud.aiplatform.v1beta1.ListRagDataSchemasResponse.next_page_token]
            of the previous
            [VertexRagDataService.ListRagDataSchemas][google.cloud.aiplatform.v1beta1.VertexRagDataService.ListRagDataSchemas]
            call.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    page_size: int = proto.Field(
        proto.INT32,
        number=2,
    )
    page_token: str = proto.Field(
        proto.STRING,
        number=3,
    )


class ListRagDataSchemasResponse(proto.Message):
    r"""Response message for
    [VertexRagDataService.ListRagDataSchemas][google.cloud.aiplatform.v1beta1.VertexRagDataService.ListRagDataSchemas].

    Attributes:
        rag_data_schemas (MutableSequence[google.cloud.aiplatform_v1beta1.types.RagDataSchema]):
            List of RagDataSchemas in the requested page.
        next_page_token (str):
            A token to retrieve the next page of results. Pass to
            [ListRagDataSchemasRequest.page_token][google.cloud.aiplatform.v1beta1.ListRagDataSchemasRequest.page_token]
            to obtain that page.
    """

    @property
    def raw_page(self):
        return self

    rag_data_schemas: MutableSequence[vertex_rag_data.RagDataSchema] = (
        proto.RepeatedField(
            proto.MESSAGE,
            number=1,
            message=vertex_rag_data.RagDataSchema,
        )
    )
    next_page_token: str = proto.Field(
        proto.STRING,
        number=2,
    )


class BatchDeleteRagDataSchemasRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.BatchDeleteRagDataSchemas][google.cloud.aiplatform.v1beta1.VertexRagDataService.BatchDeleteRagDataSchemas].

    Attributes:
        parent (str):
            Required. The resource name of the RagCorpus from which to
            delete the RagDataSchemas. Format:
            ``projects/{project}/locations/{location}/ragCorpora/{rag_corpus}``
        names (MutableSequence[str]):
            Required. The RagDataSchemas to delete. A maximum of 500
            schemas can be deleted in a batch. Format:
            ``projects/{project}/locations/{location}/ragCorpora/{rag_corpus}/ragDataSchemas/{rag_data_schema}``
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    names: MutableSequence[str] = proto.RepeatedField(
        proto.STRING,
        number=2,
    )


class DeleteRagDataSchemaRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.DeleteRagDataSchema][google.cloud.aiplatform.v1beta1.VertexRagDataService.DeleteRagDataSchema].

    Attributes:
        name (str):
            Required. The name of the RagDataSchema resource to be
            deleted. Format:
            ``projects/{project}/locations/{location}/ragCorpora/{rag_corpus}/ragDataSchemas/{rag_data_schema}``
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class CreateRagMetadataRequest(proto.Message):
    r"""Request message for CreateRagMetadata.

    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        parent (str):
            Required. The parent resource where this metadata will be
            created. Format:
            ``projects/{project_number}/locations/{location_id}/ragCorpora/{rag_corpus}/ragFiles/{rag_file}``
        rag_metadata (google.cloud.aiplatform_v1beta1.types.RagMetadata):
            Required. The metadata to create.
        rag_metadata_id (str):
            Optional. The ID to use for the metadata, which will become
            the final component of the metadata's resource name if the
            user chooses to specify. Otherwise, metadata id will be
            generated by system.

            This value should be up to 63 characters, and valid
            characters are /[a-z][0-9]-/. The first character must be a
            letter, the last could be a letter or a number.

            This field is a member of `oneof`_ ``_rag_metadata_id``.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    rag_metadata: vertex_rag_data.RagMetadata = proto.Field(
        proto.MESSAGE,
        number=2,
        message=vertex_rag_data.RagMetadata,
    )
    rag_metadata_id: str = proto.Field(
        proto.STRING,
        number=3,
        optional=True,
    )


class BatchCreateRagMetadataRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.BatchCreateRagMetadata][google.cloud.aiplatform.v1beta1.VertexRagDataService.BatchCreateRagMetadata].

    Attributes:
        parent (str):
            Required. The parent resource where the RagMetadata will be
            created. Format:
            ``projects/{project_number}/locations/{location_id}/ragCorpora/{rag_corpus}/ragFiles/{rag_file}``
        requests (MutableSequence[google.cloud.aiplatform_v1beta1.types.CreateRagMetadataRequest]):
            Required. The request messages for
            [VertexRagDataService.CreateRagMetadata][google.cloud.aiplatform.v1beta1.VertexRagDataService.CreateRagMetadata].
            A maximum of 500 rag file metadata can be created in a
            batch.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    requests: MutableSequence["CreateRagMetadataRequest"] = proto.RepeatedField(
        proto.MESSAGE,
        number=2,
        message="CreateRagMetadataRequest",
    )


class UpdateRagMetadataRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.UpdateRagMetadata][google.cloud.aiplatform.v1beta1.VertexRagDataService.UpdateRagMetadata].

    Attributes:
        rag_metadata (google.cloud.aiplatform_v1beta1.types.RagMetadata):
            Required. The RagMetadata which replaces the
            resource on the server.
    """

    rag_metadata: vertex_rag_data.RagMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=vertex_rag_data.RagMetadata,
    )


class GetRagMetadataRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.GetRagMetadata][google.cloud.aiplatform.v1beta1.VertexRagDataService.GetRagMetadata]

    Attributes:
        name (str):
            Required. The name of the RagMetadata resource. Format:
            ``projects/{project}/locations/{location}/ragCorpora/{rag_corpus}/ragFiles/{rag_file}/ragMetadata/{rag_metadata}``
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class ListRagMetadataRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.ListRagMetadata][google.cloud.aiplatform.v1beta1.VertexRagDataService.ListRagMetadata].

    Attributes:
        parent (str):
            Required. The resource name of the RagFile from which to
            list the RagMetadata. Format:
            ``projects/{project}/locations/{location}/ragCorpora/{rag_corpus}/ragFiles/{rag_file}``
        page_size (int):
            Optional. The standard list page size. The
            maximum value is 100. If not specified, a
            default value of 100 will be used.
        page_token (str):
            Optional. The standard list page token. Typically obtained
            via
            [ListRagMetadataResponse.next_page_token][google.cloud.aiplatform.v1beta1.ListRagMetadataResponse.next_page_token]
            of the previous
            [VertexRagDataService.ListRagMetadata][google.cloud.aiplatform.v1beta1.VertexRagDataService.ListRagMetadata]
            call.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    page_size: int = proto.Field(
        proto.INT32,
        number=2,
    )
    page_token: str = proto.Field(
        proto.STRING,
        number=3,
    )


class ListRagMetadataResponse(proto.Message):
    r"""Response message for
    [VertexRagDataService.ListRagMetadata][google.cloud.aiplatform.v1beta1.VertexRagDataService.ListRagMetadata].

    Attributes:
        rag_metadata (MutableSequence[google.cloud.aiplatform_v1beta1.types.RagMetadata]):
            List of RagMetadata in the requested page.
        next_page_token (str):
            A token to retrieve the next page of results. Pass to
            [ListRagMetadataRequest.page_token][google.cloud.aiplatform.v1beta1.ListRagMetadataRequest.page_token]
            to obtain that page.
    """

    @property
    def raw_page(self):
        return self

    rag_metadata: MutableSequence[vertex_rag_data.RagMetadata] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message=vertex_rag_data.RagMetadata,
    )
    next_page_token: str = proto.Field(
        proto.STRING,
        number=2,
    )


class DeleteRagMetadataRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.DeleteRagMetadata][google.cloud.aiplatform.v1beta1.VertexRagDataService.DeleteRagMetadata].

    Attributes:
        name (str):
            Required. The name of the RagMetadata resource to be
            deleted. Format:
            ``projects/{project}/locations/{location}/ragCorpora/{rag_corpus}/ragFiles/{rag_file}/ragMetadata/{rag_metadata}``
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class BatchDeleteRagMetadataRequest(proto.Message):
    r"""Request message for
    [VertexRagDataService.BatchDeleteRagMetadata][google.cloud.aiplatform.v1beta1.VertexRagDataService.BatchDeleteRagMetadata].

    Attributes:
        parent (str):
            Required. The resource name of the RagFile from which to
            delete the RagMetadata. Format:
            ``projects/{project}/locations/{location}/ragCorpora/{rag_corpus}/ragFiles/{rag_file}``
        names (MutableSequence[str]):
            Required. The RagMetadata to delete.
            A maximum of 500 rag metadata can be deleted in
            a batch.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    names: MutableSequence[str] = proto.RepeatedField(
        proto.STRING,
        number=2,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
