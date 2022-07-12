# -*- coding: utf-8 -*-
# Copyright 2022 Google LLC
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
import proto  # type: ignore

from google.cloud.aiplatform_v1.types import artifact as gca_artifact
from google.cloud.aiplatform_v1.types import context as gca_context
from google.cloud.aiplatform_v1.types import event
from google.cloud.aiplatform_v1.types import execution as gca_execution
from google.cloud.aiplatform_v1.types import metadata_schema as gca_metadata_schema
from google.cloud.aiplatform_v1.types import metadata_store as gca_metadata_store
from google.cloud.aiplatform_v1.types import operation
from google.protobuf import field_mask_pb2  # type: ignore

__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1",
    manifest={
        "CreateMetadataStoreRequest",
        "CreateMetadataStoreOperationMetadata",
        "GetMetadataStoreRequest",
        "ListMetadataStoresRequest",
        "ListMetadataStoresResponse",
        "DeleteMetadataStoreRequest",
        "DeleteMetadataStoreOperationMetadata",
        "CreateArtifactRequest",
        "GetArtifactRequest",
        "ListArtifactsRequest",
        "ListArtifactsResponse",
        "UpdateArtifactRequest",
        "DeleteArtifactRequest",
        "PurgeArtifactsRequest",
        "PurgeArtifactsResponse",
        "PurgeArtifactsMetadata",
        "CreateContextRequest",
        "GetContextRequest",
        "ListContextsRequest",
        "ListContextsResponse",
        "UpdateContextRequest",
        "DeleteContextRequest",
        "PurgeContextsRequest",
        "PurgeContextsResponse",
        "PurgeContextsMetadata",
        "AddContextArtifactsAndExecutionsRequest",
        "AddContextArtifactsAndExecutionsResponse",
        "AddContextChildrenRequest",
        "AddContextChildrenResponse",
        "QueryContextLineageSubgraphRequest",
        "CreateExecutionRequest",
        "GetExecutionRequest",
        "ListExecutionsRequest",
        "ListExecutionsResponse",
        "UpdateExecutionRequest",
        "DeleteExecutionRequest",
        "PurgeExecutionsRequest",
        "PurgeExecutionsResponse",
        "PurgeExecutionsMetadata",
        "AddExecutionEventsRequest",
        "AddExecutionEventsResponse",
        "QueryExecutionInputsAndOutputsRequest",
        "CreateMetadataSchemaRequest",
        "GetMetadataSchemaRequest",
        "ListMetadataSchemasRequest",
        "ListMetadataSchemasResponse",
        "QueryArtifactLineageSubgraphRequest",
    },
)


class CreateMetadataStoreRequest(proto.Message):
  r"""Request message for

    [MetadataService.CreateMetadataStore][google.cloud.aiplatform.v1.MetadataService.CreateMetadataStore].

    Attributes:
        parent (str): Required. The resource name of the Location where the
          MetadataStore should be created. Format:
          ``projects/{project}/locations/{location}/``
        metadata_store (google.cloud.aiplatform_v1.types.MetadataStore):
          Required. The MetadataStore to create.
        metadata_store_id (str): The {metadatastore} portion of the resource
          name with the
            format:
              ``projects/{project}/locations/{location}/metadataStores/{metadatastore}``
              If not provided, the MetadataStore's ID will be a UUID generated
              by the service. Must be 4-128 characters in length. Valid
              characters are ``/[a-z][0-9]-/``. Must be unique across all
              MetadataStores in the parent Location. (Otherwise the request will
              fail with ALREADY_EXISTS, or PERMISSION_DENIED if the caller can't
              view the preexisting MetadataStore.)
  """

  parent = proto.Field(
      proto.STRING,
      number=1,
  )
  metadata_store = proto.Field(
      proto.MESSAGE,
      number=2,
      message=gca_metadata_store.MetadataStore,
  )
  metadata_store_id = proto.Field(
      proto.STRING,
      number=3,
  )


class CreateMetadataStoreOperationMetadata(proto.Message):
  r"""Details of operations that perform

    [MetadataService.CreateMetadataStore][google.cloud.aiplatform.v1.MetadataService.CreateMetadataStore].

    Attributes:
        generic_metadata
          (google.cloud.aiplatform_v1.types.GenericOperationMetadata): Operation
          metadata for creating a MetadataStore.
  """

  generic_metadata = proto.Field(
      proto.MESSAGE,
      number=1,
      message=operation.GenericOperationMetadata,
  )


class GetMetadataStoreRequest(proto.Message):
  r"""Request message for

    [MetadataService.GetMetadataStore][google.cloud.aiplatform.v1.MetadataService.GetMetadataStore].

    Attributes:
        name (str): Required. The resource name of the MetadataStore to
          retrieve. Format:
          ``projects/{project}/locations/{location}/metadataStores/{metadatastore}``
  """

  name = proto.Field(
      proto.STRING,
      number=1,
  )


class ListMetadataStoresRequest(proto.Message):
  r"""Request message for

    [MetadataService.ListMetadataStores][google.cloud.aiplatform.v1.MetadataService.ListMetadataStores].

    Attributes:
        parent (str): Required. The Location whose MetadataStores should be
          listed. Format: ``projects/{project}/locations/{location}``
        page_size (int): The maximum number of Metadata Stores to return. The
          service may return fewer. Must be in range 1-1000, inclusive. Defaults
          to 100.
        page_token (str): A page token, received from a previous
          [MetadataService.ListMetadataStores][google.cloud.aiplatform.v1.MetadataService.ListMetadataStores]
          call. Provide this to retrieve the subsequent page.  When paginating,
          all other provided parameters must match the call that provided the
          page token. (Otherwise the request will fail with INVALID_ARGUMENT
          error.)
  """

  parent = proto.Field(
      proto.STRING,
      number=1,
  )
  page_size = proto.Field(
      proto.INT32,
      number=2,
  )
  page_token = proto.Field(
      proto.STRING,
      number=3,
  )


class ListMetadataStoresResponse(proto.Message):
  r"""Response message for

    [MetadataService.ListMetadataStores][google.cloud.aiplatform.v1.MetadataService.ListMetadataStores].

    Attributes:
        metadata_stores
          (Sequence[google.cloud.aiplatform_v1.types.MetadataStore]): The
          MetadataStores found for the Location.
        next_page_token (str): A token, which can be sent as
          [ListMetadataStoresRequest.page_token][google.cloud.aiplatform.v1.ListMetadataStoresRequest.page_token]
          to retrieve the next page. If this field is not populated, there are
          no subsequent pages.
  """

  @property
  def raw_page(self):
    return self

  metadata_stores = proto.RepeatedField(
      proto.MESSAGE,
      number=1,
      message=gca_metadata_store.MetadataStore,
  )
  next_page_token = proto.Field(
      proto.STRING,
      number=2,
  )


class DeleteMetadataStoreRequest(proto.Message):
  r"""Request message for

    [MetadataService.DeleteMetadataStore][google.cloud.aiplatform.v1.MetadataService.DeleteMetadataStore].

    Attributes:
        name (str): Required. The resource name of the MetadataStore to delete.
            Format:
              ``projects/{project}/locations/{location}/metadataStores/{metadatastore}``
        force (bool):
            Deprecated: Field is no longer supported.
  """

  name = proto.Field(
      proto.STRING,
      number=1,
  )
  force = proto.Field(
      proto.BOOL,
      number=2,
  )


class DeleteMetadataStoreOperationMetadata(proto.Message):
  r"""Details of operations that perform

    [MetadataService.DeleteMetadataStore][google.cloud.aiplatform.v1.MetadataService.DeleteMetadataStore].

    Attributes:
        generic_metadata
          (google.cloud.aiplatform_v1.types.GenericOperationMetadata): Operation
          metadata for deleting a MetadataStore.
  """

  generic_metadata = proto.Field(
      proto.MESSAGE,
      number=1,
      message=operation.GenericOperationMetadata,
  )


class CreateArtifactRequest(proto.Message):
  r"""Request message for

    [MetadataService.CreateArtifact][google.cloud.aiplatform.v1.MetadataService.CreateArtifact].

    Attributes:
        parent (str): Required. The resource name of the MetadataStore where the
          Artifact should be created. Format:
          ``projects/{project}/locations/{location}/metadataStores/{metadatastore}``
        artifact (google.cloud.aiplatform_v1.types.Artifact): Required. The
          Artifact to create.
        artifact_id (str): The {artifact} portion of the resource name with the
          format:
          ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/artifacts/{artifact}``
          If not provided, the Artifact's ID will be a UUID generated by the
          service. Must be 4-128 characters in length. Valid characters are
          ``/[a-z][0-9]-/``. Must be unique across all Artifacts in the parent
          MetadataStore. (Otherwise the request will fail with ALREADY_EXISTS,
          or PERMISSION_DENIED if the caller can't view the preexisting
          Artifact.)
  """

  parent = proto.Field(
      proto.STRING,
      number=1,
  )
  artifact = proto.Field(
      proto.MESSAGE,
      number=2,
      message=gca_artifact.Artifact,
  )
  artifact_id = proto.Field(
      proto.STRING,
      number=3,
  )


class GetArtifactRequest(proto.Message):
  r"""Request message for

    [MetadataService.GetArtifact][google.cloud.aiplatform.v1.MetadataService.GetArtifact].

    Attributes:
        name (str): Required. The resource name of the Artifact to retrieve.
            Format:
              ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/artifacts/{artifact}``
  """

  name = proto.Field(
      proto.STRING,
      number=1,
  )


class ListArtifactsRequest(proto.Message):
  r"""Request message for

    [MetadataService.ListArtifacts][google.cloud.aiplatform.v1.MetadataService.ListArtifacts].

    Attributes:
        parent (str): Required. The MetadataStore whose Artifacts should be
          listed. Format:
          ``projects/{project}/locations/{location}/metadataStores/{metadatastore}``
        page_size (int): The maximum number of Artifacts to return. The service
          may return fewer. Must be in range 1-1000, inclusive. Defaults to 100.
        page_token (str): A page token, received from a previous
          [MetadataService.ListArtifacts][google.cloud.aiplatform.v1.MetadataService.ListArtifacts]
          call. Provide this to retrieve the subsequent page.  When paginating,
          all other provided parameters must match the call that provided the
          page token. (Otherwise the request will fail with INVALID_ARGUMENT
          error.)
        filter (str): Filter specifying the boolean condition for the Artifacts
          to satisfy in order to be part of the result set. The syntax to define
          filter query is based on https://google.aip.dev/160. The supported set
          of filters include the following:  -  **Attribute filtering**: For
          example: ``display_name = "test"``. Supported fields include:
          ``name``, ``display_name``, ``uri``, ``state``, ``schema_title``,
          ``create_time``, and ``update_time``. Time fields, such as
          ``create_time`` and ``update_time``, require values specified in
          RFC-3339 format. For example: ``create_time =
          "2020-11-19T11:30:00-04:00"`` -  **Metadata field**: To filter on
          metadata fields use traversal operation as follows:
          ``metadata.<field_name>.<type_value>``. For example:
          ``metadata.field_1.number_value = 10.0`` -  **Context based
          filtering**: To filter Artifacts based on the contexts to which they
          belong, use the function operator with the full resource name
          ``in_context(<context-name>)``. For example:
          ``in_context("projects/<project_number>/locations/<location>/metadataStores/<metadatastore_name>/contexts/<context-id>")``
          Each of the above supported filter types can be combined together
          using logical operators (``AND`` & ``OR``).  For example:
          ``display_name = "test" AND metadata.field1.bool_value = true``.
  """

  parent = proto.Field(
      proto.STRING,
      number=1,
  )
  page_size = proto.Field(
      proto.INT32,
      number=2,
  )
  page_token = proto.Field(
      proto.STRING,
      number=3,
  )
  filter = proto.Field(
      proto.STRING,
      number=4,
  )


class ListArtifactsResponse(proto.Message):
  r"""Response message for

    [MetadataService.ListArtifacts][google.cloud.aiplatform.v1.MetadataService.ListArtifacts].

    Attributes:
        artifacts (Sequence[google.cloud.aiplatform_v1.types.Artifact]): The
          Artifacts retrieved from the MetadataStore.
        next_page_token (str): A token, which can be sent as
          [ListArtifactsRequest.page_token][google.cloud.aiplatform.v1.ListArtifactsRequest.page_token]
          to retrieve the next page. If this field is not populated, there are
          no subsequent pages.
  """

  @property
  def raw_page(self):
    return self

  artifacts = proto.RepeatedField(
      proto.MESSAGE,
      number=1,
      message=gca_artifact.Artifact,
  )
  next_page_token = proto.Field(
      proto.STRING,
      number=2,
  )


class UpdateArtifactRequest(proto.Message):
  r"""Request message for

    [MetadataService.UpdateArtifact][google.cloud.aiplatform.v1.MetadataService.UpdateArtifact].

    Attributes:
        artifact (google.cloud.aiplatform_v1.types.Artifact): Required. The
          Artifact containing updates. The Artifact's
          [Artifact.name][google.cloud.aiplatform.v1.Artifact.name] field is
          used to identify the Artifact to be updated.
            Format:
              ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/artifacts/{artifact}``
        update_mask (google.protobuf.field_mask_pb2.FieldMask): Optional. A
          FieldMask indicating which fields should be updated. Functionality of
          this field is not yet supported.
        allow_missing (bool): If set to true, and the
          [Artifact][google.cloud.aiplatform.v1.Artifact] is not found, a new
          [Artifact][google.cloud.aiplatform.v1.Artifact] is created.
  """

  artifact = proto.Field(
      proto.MESSAGE,
      number=1,
      message=gca_artifact.Artifact,
  )
  update_mask = proto.Field(
      proto.MESSAGE,
      number=2,
      message=field_mask_pb2.FieldMask,
  )
  allow_missing = proto.Field(
      proto.BOOL,
      number=3,
  )


class DeleteArtifactRequest(proto.Message):
  r"""Request message for

    [MetadataService.DeleteArtifact][google.cloud.aiplatform.v1.MetadataService.DeleteArtifact].

    Attributes:
        name (str): Required. The resource name of the Artifact to delete.
            Format:
              ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/artifacts/{artifact}``
        etag (str): Optional. The etag of the Artifact to delete. If this is
          provided, it must match the server's etag. Otherwise, the request will
          fail with a FAILED_PRECONDITION.
  """

  name = proto.Field(
      proto.STRING,
      number=1,
  )
  etag = proto.Field(
      proto.STRING,
      number=2,
  )


class PurgeArtifactsRequest(proto.Message):
  r"""Request message for

    [MetadataService.PurgeArtifacts][google.cloud.aiplatform.v1.MetadataService.PurgeArtifacts].

    Attributes:
        parent (str): Required. The metadata store to purge Artifacts from.
            Format:
              ``projects/{project}/locations/{location}/metadataStores/{metadatastore}``
        filter (str): Required. A required filter matching the Artifacts to be
          purged. E.g., ``update_time <= 2020-11-19T11:30:00-04:00``.
        force (bool): Optional. Flag to indicate to actually perform the purge.
          If ``force`` is set to false, the method will return a sample of
          Artifact names that would be deleted.
  """

  parent = proto.Field(
      proto.STRING,
      number=1,
  )
  filter = proto.Field(
      proto.STRING,
      number=2,
  )
  force = proto.Field(
      proto.BOOL,
      number=3,
  )


class PurgeArtifactsResponse(proto.Message):
  r"""Response message for

    [MetadataService.PurgeArtifacts][google.cloud.aiplatform.v1.MetadataService.PurgeArtifacts].

    Attributes:
        purge_count (int): The number of Artifacts that this request deleted
          (or, if ``force`` is false, the number of Artifacts that will be
          deleted). This can be an estimate.
        purge_sample (Sequence[str]): A sample of the Artifact names that will
          be deleted. Only populated if ``force`` is set to false. The maximum
          number of samples is 100 (it is possible to return fewer).
  """

  purge_count = proto.Field(
      proto.INT64,
      number=1,
  )
  purge_sample = proto.RepeatedField(
      proto.STRING,
      number=2,
  )


class PurgeArtifactsMetadata(proto.Message):
  r"""Details of operations that perform

    [MetadataService.PurgeArtifacts][google.cloud.aiplatform.v1.MetadataService.PurgeArtifacts].

    Attributes:
        generic_metadata
          (google.cloud.aiplatform_v1.types.GenericOperationMetadata): Operation
          metadata for purging Artifacts.
  """

  generic_metadata = proto.Field(
      proto.MESSAGE,
      number=1,
      message=operation.GenericOperationMetadata,
  )


class CreateContextRequest(proto.Message):
  r"""Request message for

    [MetadataService.CreateContext][google.cloud.aiplatform.v1.MetadataService.CreateContext].

    Attributes:
        parent (str): Required. The resource name of the MetadataStore where the
          Context should be created. Format:
          ``projects/{project}/locations/{location}/metadataStores/{metadatastore}``
        context (google.cloud.aiplatform_v1.types.Context): Required. The
          Context to create.
        context_id (str): The {context} portion of the resource name with the
          format:
          ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/contexts/{context}``.
          If not provided, the Context's ID will be a UUID generated by the
          service. Must be 4-128 characters in length. Valid characters are
          ``/[a-z][0-9]-/``. Must be unique across all Contexts in the parent
          MetadataStore. (Otherwise the request will fail with ALREADY_EXISTS,
          or PERMISSION_DENIED if the caller can't view the preexisting
          Context.)
  """

  parent = proto.Field(
      proto.STRING,
      number=1,
  )
  context = proto.Field(
      proto.MESSAGE,
      number=2,
      message=gca_context.Context,
  )
  context_id = proto.Field(
      proto.STRING,
      number=3,
  )


class GetContextRequest(proto.Message):
  r"""Request message for

    [MetadataService.GetContext][google.cloud.aiplatform.v1.MetadataService.GetContext].

    Attributes:
        name (str): Required. The resource name of the Context to retrieve.
            Format:
              ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/contexts/{context}``
  """

  name = proto.Field(
      proto.STRING,
      number=1,
  )


class ListContextsRequest(proto.Message):
  r"""Request message for

    [MetadataService.ListContexts][google.cloud.aiplatform.v1.MetadataService.ListContexts]

    Attributes:
        parent (str): Required. The MetadataStore whose Contexts should be
          listed.
            Format:
              ``projects/{project}/locations/{location}/metadataStores/{metadatastore}``
        page_size (int): The maximum number of Contexts to return. The service
          may return fewer. Must be in range 1-1000, inclusive. Defaults to 100.
        page_token (str): A page token, received from a previous
          [MetadataService.ListContexts][google.cloud.aiplatform.v1.MetadataService.ListContexts]
          call. Provide this to retrieve the subsequent page.  When paginating,
          all other provided parameters must match the call that provided the
          page token. (Otherwise the request will fail with INVALID_ARGUMENT
          error.)
        filter (str): Filter specifying the boolean condition for the Contexts
          to satisfy in order to be part of the result set. The syntax to define
          filter query is based on https://google.aip.dev/160. Following are the
          supported set of filters:  -  **Attribute filtering**: For example:
          ``display_name = "test"``. Supported fields include: ``name``,
          ``display_name``, ``schema_title``, ``create_time``, and
          ``update_time``. Time fields, such as ``create_time`` and
          ``update_time``, require values specified in RFC-3339 format. For
          example: ``create_time = "2020-11-19T11:30:00-04:00"``.  -  **Metadata
          field**: To filter on metadata fields use traversal operation as
          follows: ``metadata.<field_name>.<type_value>``. For example:
          ``metadata.field_1.number_value = 10.0``.  -  **Parent Child
          filtering**: To filter Contexts based on parent-child relationship use
          the HAS operator as
               follows:  ::
                  parent_contexts:
                    "projects/<project_number>/locations/<location>/metadataStores/<metadatastore_name>/contexts/<context_id>"
                  child_contexts:
                    "projects/<project_number>/locations/<location>/metadataStores/<metadatastore_name>/contexts/<context_id>"
                    Each of the above supported filters can be combined together
                    using logical operators (``AND`` & ``OR``).  For example:
                    ``display_name = "test" AND metadata.field1.bool_value =
                    true``.
  """

  parent = proto.Field(
      proto.STRING,
      number=1,
  )
  page_size = proto.Field(
      proto.INT32,
      number=2,
  )
  page_token = proto.Field(
      proto.STRING,
      number=3,
  )
  filter = proto.Field(
      proto.STRING,
      number=4,
  )


class ListContextsResponse(proto.Message):
  r"""Response message for

    [MetadataService.ListContexts][google.cloud.aiplatform.v1.MetadataService.ListContexts].

    Attributes:
        contexts (Sequence[google.cloud.aiplatform_v1.types.Context]): The
          Contexts retrieved from the MetadataStore.
        next_page_token (str): A token, which can be sent as
          [ListContextsRequest.page_token][google.cloud.aiplatform.v1.ListContextsRequest.page_token]
          to retrieve the next page. If this field is not populated, there are
          no subsequent pages.
  """

  @property
  def raw_page(self):
    return self

  contexts = proto.RepeatedField(
      proto.MESSAGE,
      number=1,
      message=gca_context.Context,
  )
  next_page_token = proto.Field(
      proto.STRING,
      number=2,
  )


class UpdateContextRequest(proto.Message):
  r"""Request message for

    [MetadataService.UpdateContext][google.cloud.aiplatform.v1.MetadataService.UpdateContext].

    Attributes:
        context (google.cloud.aiplatform_v1.types.Context): Required. The
          Context containing updates. The Context's
          [Context.name][google.cloud.aiplatform.v1.Context.name] field is used
          to identify the Context to be updated. Format:
          ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/contexts/{context}``
        update_mask (google.protobuf.field_mask_pb2.FieldMask): Optional. A
          FieldMask indicating which fields should be updated. Functionality of
          this field is not yet supported.
        allow_missing (bool): If set to true, and the
          [Context][google.cloud.aiplatform.v1.Context] is not found, a new
          [Context][google.cloud.aiplatform.v1.Context] is created.
  """

  context = proto.Field(
      proto.MESSAGE,
      number=1,
      message=gca_context.Context,
  )
  update_mask = proto.Field(
      proto.MESSAGE,
      number=2,
      message=field_mask_pb2.FieldMask,
  )
  allow_missing = proto.Field(
      proto.BOOL,
      number=3,
  )


class DeleteContextRequest(proto.Message):
  r"""Request message for

    [MetadataService.DeleteContext][google.cloud.aiplatform.v1.MetadataService.DeleteContext].

    Attributes:
        name (str): Required. The resource name of the Context to delete.
            Format:
              ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/contexts/{context}``
        force (bool): The force deletion semantics is still undefined. Users
          should not use this field.
        etag (str): Optional. The etag of the Context to delete. If this is
          provided, it must match the server's etag. Otherwise, the request will
          fail with a FAILED_PRECONDITION.
  """

  name = proto.Field(
      proto.STRING,
      number=1,
  )
  force = proto.Field(
      proto.BOOL,
      number=2,
  )
  etag = proto.Field(
      proto.STRING,
      number=3,
  )


class PurgeContextsRequest(proto.Message):
  r"""Request message for

    [MetadataService.PurgeContexts][google.cloud.aiplatform.v1.MetadataService.PurgeContexts].

    Attributes:
        parent (str): Required. The metadata store to purge Contexts from.
          Format:
          ``projects/{project}/locations/{location}/metadataStores/{metadatastore}``
        filter (str): Required. A required filter matching the Contexts to be
          purged. E.g., ``update_time <= 2020-11-19T11:30:00-04:00``.
        force (bool): Optional. Flag to indicate to actually perform the purge.
          If ``force`` is set to false, the method will return a sample of
          Context names that would be deleted.
  """

  parent = proto.Field(
      proto.STRING,
      number=1,
  )
  filter = proto.Field(
      proto.STRING,
      number=2,
  )
  force = proto.Field(
      proto.BOOL,
      number=3,
  )


class PurgeContextsResponse(proto.Message):
  r"""Response message for

    [MetadataService.PurgeContexts][google.cloud.aiplatform.v1.MetadataService.PurgeContexts].

    Attributes:
        purge_count (int): The number of Contexts that this request deleted (or,
          if ``force`` is false, the number of Contexts that will be deleted).
          This can be an estimate.
        purge_sample (Sequence[str]): A sample of the Context names that will be
          deleted. Only populated if ``force`` is set to false. The maximum
          number of samples is 100 (it is possible to return fewer).
  """

  purge_count = proto.Field(
      proto.INT64,
      number=1,
  )
  purge_sample = proto.RepeatedField(
      proto.STRING,
      number=2,
  )


class PurgeContextsMetadata(proto.Message):
  r"""Details of operations that perform

    [MetadataService.PurgeContexts][google.cloud.aiplatform.v1.MetadataService.PurgeContexts].

    Attributes:
        generic_metadata
          (google.cloud.aiplatform_v1.types.GenericOperationMetadata): Operation
          metadata for purging Contexts.
  """

  generic_metadata = proto.Field(
      proto.MESSAGE,
      number=1,
      message=operation.GenericOperationMetadata,
  )


class AddContextArtifactsAndExecutionsRequest(proto.Message):
  r"""Request message for

    [MetadataService.AddContextArtifactsAndExecutions][google.cloud.aiplatform.v1.MetadataService.AddContextArtifactsAndExecutions].

    Attributes:
        context (str): Required. The resource name of the Context that the
          Artifacts and Executions belong to. Format:
          ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/contexts/{context}``
        artifacts (Sequence[str]): The resource names of the Artifacts to
          attribute to the Context.
            Format:
              ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/artifacts/{artifact}``
        executions (Sequence[str]): The resource names of the Executions to
          associate with the Context.
            Format:
              ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/executions/{execution}``
  """

  context = proto.Field(
      proto.STRING,
      number=1,
  )
  artifacts = proto.RepeatedField(
      proto.STRING,
      number=2,
  )
  executions = proto.RepeatedField(
      proto.STRING,
      number=3,
  )


class AddContextArtifactsAndExecutionsResponse(proto.Message):
  r"""Response message for

    [MetadataService.AddContextArtifactsAndExecutions][google.cloud.aiplatform.v1.MetadataService.AddContextArtifactsAndExecutions].

    """


class AddContextChildrenRequest(proto.Message):
  r"""Request message for

    [MetadataService.AddContextChildren][google.cloud.aiplatform.v1.MetadataService.AddContextChildren].

    Attributes:
        context (str): Required. The resource name of the parent Context.
            Format:
              ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/contexts/{context}``
        child_contexts (Sequence[str]): The resource names of the child
          Contexts.
  """

  context = proto.Field(
      proto.STRING,
      number=1,
  )
  child_contexts = proto.RepeatedField(
      proto.STRING,
      number=2,
  )


class AddContextChildrenResponse(proto.Message):
  r"""Response message for

    [MetadataService.AddContextChildren][google.cloud.aiplatform.v1.MetadataService.AddContextChildren].

    """


class QueryContextLineageSubgraphRequest(proto.Message):
  r"""Request message for

    [MetadataService.QueryContextLineageSubgraph][google.cloud.aiplatform.v1.MetadataService.QueryContextLineageSubgraph].

    Attributes:
        context (str): Required. The resource name of the Context whose
          Artifacts and Executions should be retrieved as a LineageSubgraph.
            Format:
              ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/contexts/{context}``
              The request may error with FAILED_PRECONDITION if the number of
              Artifacts, the number of Executions, or the number of Events that
              would be returned for the Context exceeds 1000.
  """

  context = proto.Field(
      proto.STRING,
      number=1,
  )


class CreateExecutionRequest(proto.Message):
  r"""Request message for

    [MetadataService.CreateExecution][google.cloud.aiplatform.v1.MetadataService.CreateExecution].

    Attributes:
        parent (str): Required. The resource name of the MetadataStore where the
          Execution should be created. Format:
          ``projects/{project}/locations/{location}/metadataStores/{metadatastore}``
        execution (google.cloud.aiplatform_v1.types.Execution): Required. The
          Execution to create.
        execution_id (str): The {execution} portion of the resource name with
          the
            format:
              ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/executions/{execution}``
              If not provided, the Execution's ID will be a UUID generated by
              the service. Must be 4-128 characters in length. Valid characters
              are ``/[a-z][0-9]-/``. Must be unique across all Executions in the
              parent MetadataStore. (Otherwise the request will fail with
              ALREADY_EXISTS, or PERMISSION_DENIED if the caller can't view the
              preexisting Execution.)
  """

  parent = proto.Field(
      proto.STRING,
      number=1,
  )
  execution = proto.Field(
      proto.MESSAGE,
      number=2,
      message=gca_execution.Execution,
  )
  execution_id = proto.Field(
      proto.STRING,
      number=3,
  )


class GetExecutionRequest(proto.Message):
  r"""Request message for

    [MetadataService.GetExecution][google.cloud.aiplatform.v1.MetadataService.GetExecution].

    Attributes:
        name (str): Required. The resource name of the Execution to retrieve.
            Format:
              ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/executions/{execution}``
  """

  name = proto.Field(
      proto.STRING,
      number=1,
  )


class ListExecutionsRequest(proto.Message):
  r"""Request message for

    [MetadataService.ListExecutions][google.cloud.aiplatform.v1.MetadataService.ListExecutions].

    Attributes:
        parent (str): Required. The MetadataStore whose Executions should be
          listed. Format:
          ``projects/{project}/locations/{location}/metadataStores/{metadatastore}``
        page_size (int): The maximum number of Executions to return. The service
          may return fewer. Must be in range 1-1000, inclusive. Defaults to 100.
        page_token (str): A page token, received from a previous
          [MetadataService.ListExecutions][google.cloud.aiplatform.v1.MetadataService.ListExecutions]
          call. Provide this to retrieve the subsequent page.  When paginating,
          all other provided parameters must match the call that provided the
          page token. (Otherwise the request will fail with an INVALID_ARGUMENT
          error.)
        filter (str): Filter specifying the boolean condition for the Executions
          to satisfy in order to be part of the result set. The syntax to define
          filter query is based on
            https://google.aip.dev/160. Following are the supported set of
              filters:  -  **Attribute filtering**: For example: ``display_name
              = "test"``. Supported fields include: ``name``, ``display_name``,
              ``state``, ``schema_title``, ``create_time``, and ``update_time``.
              Time fields, such as ``create_time`` and ``update_time``, require
              values specified in RFC-3339 format. For example: ``create_time =
              "2020-11-19T11:30:00-04:00"``. -  **Metadata field**: To filter on
              metadata fields use traversal operation as follows:
              ``metadata.<field_name>.<type_value>`` For example:
              ``metadata.field_1.number_value = 10.0`` -  **Context based
              filtering**: To filter Executions based on the contexts to which
              they belong use the function operator with the full resource name:
              ``in_context(<context-name>)``. For example:
              ``in_context("projects/<project_number>/locations/<location>/metadataStores/<metadatastore_name>/contexts/<context-id>")``
              Each of the above supported filters can be combined together using
              logical operators (``AND`` & ``OR``). For example: ``display_name
              = "test" AND metadata.field1.bool_value = true``.
  """

  parent = proto.Field(
      proto.STRING,
      number=1,
  )
  page_size = proto.Field(
      proto.INT32,
      number=2,
  )
  page_token = proto.Field(
      proto.STRING,
      number=3,
  )
  filter = proto.Field(
      proto.STRING,
      number=4,
  )


class ListExecutionsResponse(proto.Message):
  r"""Response message for

    [MetadataService.ListExecutions][google.cloud.aiplatform.v1.MetadataService.ListExecutions].

    Attributes:
        executions (Sequence[google.cloud.aiplatform_v1.types.Execution]): The
          Executions retrieved from the MetadataStore.
        next_page_token (str): A token, which can be sent as
          [ListExecutionsRequest.page_token][google.cloud.aiplatform.v1.ListExecutionsRequest.page_token]
          to retrieve the next page. If this field is not populated, there are
          no subsequent pages.
  """

  @property
  def raw_page(self):
    return self

  executions = proto.RepeatedField(
      proto.MESSAGE,
      number=1,
      message=gca_execution.Execution,
  )
  next_page_token = proto.Field(
      proto.STRING,
      number=2,
  )


class UpdateExecutionRequest(proto.Message):
  r"""Request message for

    [MetadataService.UpdateExecution][google.cloud.aiplatform.v1.MetadataService.UpdateExecution].

    Attributes:
        execution (google.cloud.aiplatform_v1.types.Execution): Required. The
          Execution containing updates. The Execution's
          [Execution.name][google.cloud.aiplatform.v1.Execution.name] field is
          used to identify the Execution to be updated.
            Format:
              ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/executions/{execution}``
        update_mask (google.protobuf.field_mask_pb2.FieldMask): Optional. A
          FieldMask indicating which fields should be updated. Functionality of
          this field is not yet supported.
        allow_missing (bool): If set to true, and the
          [Execution][google.cloud.aiplatform.v1.Execution] is not found, a new
          [Execution][google.cloud.aiplatform.v1.Execution] is created.
  """

  execution = proto.Field(
      proto.MESSAGE,
      number=1,
      message=gca_execution.Execution,
  )
  update_mask = proto.Field(
      proto.MESSAGE,
      number=2,
      message=field_mask_pb2.FieldMask,
  )
  allow_missing = proto.Field(
      proto.BOOL,
      number=3,
  )


class DeleteExecutionRequest(proto.Message):
  r"""Request message for

    [MetadataService.DeleteExecution][google.cloud.aiplatform.v1.MetadataService.DeleteExecution].

    Attributes:
        name (str): Required. The resource name of the Execution to delete.
            Format:
              ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/executions/{execution}``
        etag (str): Optional. The etag of the Execution to delete. If this is
          provided, it must match the server's etag. Otherwise, the request will
          fail with a FAILED_PRECONDITION.
  """

  name = proto.Field(
      proto.STRING,
      number=1,
  )
  etag = proto.Field(
      proto.STRING,
      number=2,
  )


class PurgeExecutionsRequest(proto.Message):
  r"""Request message for

    [MetadataService.PurgeExecutions][google.cloud.aiplatform.v1.MetadataService.PurgeExecutions].

    Attributes:
        parent (str): Required. The metadata store to purge Executions from.
            Format:
              ``projects/{project}/locations/{location}/metadataStores/{metadatastore}``
        filter (str): Required. A required filter matching the Executions to be
          purged. E.g., ``update_time <= 2020-11-19T11:30:00-04:00``.
        force (bool): Optional. Flag to indicate to actually perform the purge.
          If ``force`` is set to false, the method will return a sample of
          Execution names that would be deleted.
  """

  parent = proto.Field(
      proto.STRING,
      number=1,
  )
  filter = proto.Field(
      proto.STRING,
      number=2,
  )
  force = proto.Field(
      proto.BOOL,
      number=3,
  )


class PurgeExecutionsResponse(proto.Message):
  r"""Response message for

    [MetadataService.PurgeExecutions][google.cloud.aiplatform.v1.MetadataService.PurgeExecutions].

    Attributes:
        purge_count (int): The number of Executions that this request deleted
          (or, if ``force`` is false, the number of Executions that will be
          deleted). This can be an estimate.
        purge_sample (Sequence[str]): A sample of the Execution names that will
          be deleted. Only populated if ``force`` is set to false. The maximum
          number of samples is 100 (it is possible to return fewer).
  """

  purge_count = proto.Field(
      proto.INT64,
      number=1,
  )
  purge_sample = proto.RepeatedField(
      proto.STRING,
      number=2,
  )


class PurgeExecutionsMetadata(proto.Message):
  r"""Details of operations that perform

    [MetadataService.PurgeExecutions][google.cloud.aiplatform.v1.MetadataService.PurgeExecutions].

    Attributes:
        generic_metadata
          (google.cloud.aiplatform_v1.types.GenericOperationMetadata): Operation
          metadata for purging Executions.
  """

  generic_metadata = proto.Field(
      proto.MESSAGE,
      number=1,
      message=operation.GenericOperationMetadata,
  )


class AddExecutionEventsRequest(proto.Message):
  r"""Request message for

    [MetadataService.AddExecutionEvents][google.cloud.aiplatform.v1.MetadataService.AddExecutionEvents].

    Attributes:
        execution (str): Required. The resource name of the Execution that the
          Events connect Artifacts with. Format:
          ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/executions/{execution}``
        events (Sequence[google.cloud.aiplatform_v1.types.Event]): The Events to
          create and add.
  """

  execution = proto.Field(
      proto.STRING,
      number=1,
  )
  events = proto.RepeatedField(
      proto.MESSAGE,
      number=2,
      message=event.Event,
  )


class AddExecutionEventsResponse(proto.Message):
  r"""Response message for

    [MetadataService.AddExecutionEvents][google.cloud.aiplatform.v1.MetadataService.AddExecutionEvents].

    """


class QueryExecutionInputsAndOutputsRequest(proto.Message):
  r"""Request message for

    [MetadataService.QueryExecutionInputsAndOutputs][google.cloud.aiplatform.v1.MetadataService.QueryExecutionInputsAndOutputs].

    Attributes:
        execution (str): Required. The resource name of the Execution whose
          input and output Artifacts should be retrieved as a LineageSubgraph.
            Format:
              ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/executions/{execution}``
  """

  execution = proto.Field(
      proto.STRING,
      number=1,
  )


class CreateMetadataSchemaRequest(proto.Message):
  r"""Request message for

    [MetadataService.CreateMetadataSchema][google.cloud.aiplatform.v1.MetadataService.CreateMetadataSchema].

    Attributes:
        parent (str): Required. The resource name of the MetadataStore where the
          MetadataSchema should be created. Format:
          ``projects/{project}/locations/{location}/metadataStores/{metadatastore}``
        metadata_schema (google.cloud.aiplatform_v1.types.MetadataSchema):
          Required. The MetadataSchema to create.
        metadata_schema_id (str): The {metadata_schema} portion of the resource
          name with the
            format:
              ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/metadataSchemas/{metadataschema}``
              If not provided, the MetadataStore's ID will be a UUID generated
              by the service. Must be 4-128 characters in length. Valid
              characters are ``/[a-z][0-9]-/``. Must be unique across all
              MetadataSchemas in the parent Location. (Otherwise the request
              will fail with ALREADY_EXISTS, or PERMISSION_DENIED if the caller
              can't view the preexisting MetadataSchema.)
  """

  parent = proto.Field(
      proto.STRING,
      number=1,
  )
  metadata_schema = proto.Field(
      proto.MESSAGE,
      number=2,
      message=gca_metadata_schema.MetadataSchema,
  )
  metadata_schema_id = proto.Field(
      proto.STRING,
      number=3,
  )


class GetMetadataSchemaRequest(proto.Message):
  r"""Request message for

    [MetadataService.GetMetadataSchema][google.cloud.aiplatform.v1.MetadataService.GetMetadataSchema].

    Attributes:
        name (str): Required. The resource name of the MetadataSchema to
          retrieve. Format:
          ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/metadataSchemas/{metadataschema}``
  """

  name = proto.Field(
      proto.STRING,
      number=1,
  )


class ListMetadataSchemasRequest(proto.Message):
  r"""Request message for

    [MetadataService.ListMetadataSchemas][google.cloud.aiplatform.v1.MetadataService.ListMetadataSchemas].

    Attributes:
        parent (str): Required. The MetadataStore whose MetadataSchemas should
          be listed. Format:
          ``projects/{project}/locations/{location}/metadataStores/{metadatastore}``
        page_size (int): The maximum number of MetadataSchemas to return. The
          service may return fewer. Must be in range 1-1000, inclusive. Defaults
          to 100.
        page_token (str): A page token, received from a previous
          [MetadataService.ListMetadataSchemas][google.cloud.aiplatform.v1.MetadataService.ListMetadataSchemas]
          call. Provide this to retrieve the next page.  When paginating, all
          other provided parameters must match the call that provided the page
          token. (Otherwise the request will fail with INVALID_ARGUMENT error.)
        filter (str): A query to filter available MetadataSchemas for matching
          results.
  """

  parent = proto.Field(
      proto.STRING,
      number=1,
  )
  page_size = proto.Field(
      proto.INT32,
      number=2,
  )
  page_token = proto.Field(
      proto.STRING,
      number=3,
  )
  filter = proto.Field(
      proto.STRING,
      number=4,
  )


class ListMetadataSchemasResponse(proto.Message):
  r"""Response message for

    [MetadataService.ListMetadataSchemas][google.cloud.aiplatform.v1.MetadataService.ListMetadataSchemas].

    Attributes:
        metadata_schemas
          (Sequence[google.cloud.aiplatform_v1.types.MetadataSchema]): The
          MetadataSchemas found for the MetadataStore.
        next_page_token (str): A token, which can be sent as
          [ListMetadataSchemasRequest.page_token][google.cloud.aiplatform.v1.ListMetadataSchemasRequest.page_token]
          to retrieve the next page. If this field is not populated, there are
          no subsequent pages.
  """

  @property
  def raw_page(self):
    return self

  metadata_schemas = proto.RepeatedField(
      proto.MESSAGE,
      number=1,
      message=gca_metadata_schema.MetadataSchema,
  )
  next_page_token = proto.Field(
      proto.STRING,
      number=2,
  )


class QueryArtifactLineageSubgraphRequest(proto.Message):
  r"""Request message for

    [MetadataService.QueryArtifactLineageSubgraph][google.cloud.aiplatform.v1.MetadataService.QueryArtifactLineageSubgraph].

    Attributes:
        artifact (str): Required. The resource name of the Artifact whose
          Lineage needs to be retrieved as a LineageSubgraph. Format:
          ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/artifacts/{artifact}``
          The request may error with FAILED_PRECONDITION if the number of
          Artifacts, the number of Executions, or the number of Events that
          would be returned for the Context exceeds 1000.
        max_hops (int): Specifies the size of the lineage graph in terms of
          number of hops from the specified artifact. Negative Value:
          INVALID_ARGUMENT error is returned 0: Only input artifact is returned.
          No value: Transitive closure is performed to return the complete
          graph.
        filter (str): Filter specifying the boolean condition for the Artifacts
          to satisfy in order to be part of the Lineage Subgraph. The syntax to
          define filter query is based on
            https://google.aip.dev/160. The supported set of filters include the
              following:  -  **Attribute filtering**: For example:
              ``display_name = "test"`` Supported fields include: ``name``,
              ``display_name``, ``uri``, ``state``, ``schema_title``,
              ``create_time``, and ``update_time``. Time fields, such as
              ``create_time`` and ``update_time``, require values specified in
              RFC-3339 format. For example: ``create_time =
              "2020-11-19T11:30:00-04:00"`` -  **Metadata field**: To filter on
              metadata fields use traversal operation as follows:
              ``metadata.<field_name>.<type_value>``. For example:
              ``metadata.field_1.number_value = 10.0``  Each of the above
              supported filter types can be combined together using logical
              operators (``AND`` & ``OR``).  For example: ``display_name =
              "test" AND metadata.field1.bool_value = true``.
  """

  artifact = proto.Field(
      proto.STRING,
      number=1,
  )
  max_hops = proto.Field(
      proto.INT32,
      number=2,
  )
  filter = proto.Field(
      proto.STRING,
      number=3,
  )


__all__ = tuple(sorted(__protobuf__.manifest))
