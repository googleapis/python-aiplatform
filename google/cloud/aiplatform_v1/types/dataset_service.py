# -*- coding: utf-8 -*-
# Copyright 2020 Google LLC
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

from google.cloud.aiplatform_v1.types import annotation
from google.cloud.aiplatform_v1.types import data_item
from google.cloud.aiplatform_v1.types import dataset as gca_dataset
from google.cloud.aiplatform_v1.types import operation
from google.protobuf import field_mask_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1",
    manifest={
        "CreateDatasetRequest",
        "CreateDatasetOperationMetadata",
        "GetDatasetRequest",
        "UpdateDatasetRequest",
        "ListDatasetsRequest",
        "ListDatasetsResponse",
        "DeleteDatasetRequest",
        "ImportDataRequest",
        "ImportDataResponse",
        "ImportDataOperationMetadata",
        "ExportDataRequest",
        "ExportDataResponse",
        "ExportDataOperationMetadata",
        "ListDataItemsRequest",
        "ListDataItemsResponse",
        "GetAnnotationSpecRequest",
        "ListAnnotationsRequest",
        "ListAnnotationsResponse",
    },
)


class CreateDatasetRequest(proto.Message):
    r"""Request message for
    [DatasetService.CreateDataset][google.cloud.aiplatform.v1.DatasetService.CreateDataset].

    Attributes:
        parent (str):
            Required. The resource name of the Location to create the
            Dataset in. Format:
            ``projects/{project}/locations/{location}``
        dataset (google.cloud.aiplatform_v1.types.Dataset):
            Required. The Dataset to create.
    """

    parent = proto.Field(proto.STRING, number=1,)
    dataset = proto.Field(proto.MESSAGE, number=2, message=gca_dataset.Dataset,)


class CreateDatasetOperationMetadata(proto.Message):
    r"""Runtime operation information for
    [DatasetService.CreateDataset][google.cloud.aiplatform.v1.DatasetService.CreateDataset].

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1.types.GenericOperationMetadata):
            The operation generic information.
    """

    generic_metadata = proto.Field(
        proto.MESSAGE, number=1, message=operation.GenericOperationMetadata,
    )


class GetDatasetRequest(proto.Message):
    r"""Request message for
    [DatasetService.GetDataset][google.cloud.aiplatform.v1.DatasetService.GetDataset].

    Attributes:
        name (str):
            Required. The name of the Dataset resource.
        read_mask (google.protobuf.field_mask_pb2.FieldMask):
            Mask specifying which fields to read.
    """

    name = proto.Field(proto.STRING, number=1,)
    read_mask = proto.Field(proto.MESSAGE, number=2, message=field_mask_pb2.FieldMask,)


class UpdateDatasetRequest(proto.Message):
    r"""Request message for
    [DatasetService.UpdateDataset][google.cloud.aiplatform.v1.DatasetService.UpdateDataset].

    Attributes:
        dataset (google.cloud.aiplatform_v1.types.Dataset):
            Required. The Dataset which replaces the
            resource on the server.
        update_mask (google.protobuf.field_mask_pb2.FieldMask):
            Required. The update mask applies to the resource. For the
            ``FieldMask`` definition, see
            `FieldMask <https://tinyurl.com/protobufs/google.protobuf#fieldmask>`__.
            Updatable fields:

            -  ``display_name``
            -  ``description``
            -  ``labels``
    """

    dataset = proto.Field(proto.MESSAGE, number=1, message=gca_dataset.Dataset,)
    update_mask = proto.Field(
        proto.MESSAGE, number=2, message=field_mask_pb2.FieldMask,
    )


class ListDatasetsRequest(proto.Message):
    r"""Request message for
    [DatasetService.ListDatasets][google.cloud.aiplatform.v1.DatasetService.ListDatasets].

    Attributes:
        parent (str):
            Required. The name of the Dataset's parent resource. Format:
            ``projects/{project}/locations/{location}``
        filter (str):
            An expression for filtering the results of the request. For
            field names both snake_case and camelCase are supported.

            -  ``display_name``: supports = and !=
            -  ``metadata_schema_uri``: supports = and !=
            -  ``labels`` supports general map functions that is:

               -  ``labels.key=value`` - key:value equality
               -  \`labels.key:\* or labels:key - key existence
               -  A key including a space must be quoted.
                  ``labels."a key"``.

            Some examples:

            -  ``displayName="myDisplayName"``
            -  ``labels.myKey="myValue"``
        page_size (int):
            The standard list page size.
        page_token (str):
            The standard list page token.
        read_mask (google.protobuf.field_mask_pb2.FieldMask):
            Mask specifying which fields to read.
        order_by (str):
            A comma-separated list of fields to order by, sorted in
            ascending order. Use "desc" after a field name for
            descending. Supported fields:

            -  ``display_name``
            -  ``create_time``
            -  ``update_time``
    """

    parent = proto.Field(proto.STRING, number=1,)
    filter = proto.Field(proto.STRING, number=2,)
    page_size = proto.Field(proto.INT32, number=3,)
    page_token = proto.Field(proto.STRING, number=4,)
    read_mask = proto.Field(proto.MESSAGE, number=5, message=field_mask_pb2.FieldMask,)
    order_by = proto.Field(proto.STRING, number=6,)


class ListDatasetsResponse(proto.Message):
    r"""Response message for
    [DatasetService.ListDatasets][google.cloud.aiplatform.v1.DatasetService.ListDatasets].

    Attributes:
        datasets (Sequence[google.cloud.aiplatform_v1.types.Dataset]):
            A list of Datasets that matches the specified
            filter in the request.
        next_page_token (str):
            The standard List next-page token.
    """

    @property
    def raw_page(self):
        return self

    datasets = proto.RepeatedField(
        proto.MESSAGE, number=1, message=gca_dataset.Dataset,
    )
    next_page_token = proto.Field(proto.STRING, number=2,)


class DeleteDatasetRequest(proto.Message):
    r"""Request message for
    [DatasetService.DeleteDataset][google.cloud.aiplatform.v1.DatasetService.DeleteDataset].

    Attributes:
        name (str):
            Required. The resource name of the Dataset to delete.
            Format:
            ``projects/{project}/locations/{location}/datasets/{dataset}``
    """

    name = proto.Field(proto.STRING, number=1,)


class ImportDataRequest(proto.Message):
    r"""Request message for
    [DatasetService.ImportData][google.cloud.aiplatform.v1.DatasetService.ImportData].

    Attributes:
        name (str):
            Required. The name of the Dataset resource. Format:
            ``projects/{project}/locations/{location}/datasets/{dataset}``
        import_configs (Sequence[google.cloud.aiplatform_v1.types.ImportDataConfig]):
            Required. The desired input locations. The
            contents of all input locations will be imported
            in one batch.
    """

    name = proto.Field(proto.STRING, number=1,)
    import_configs = proto.RepeatedField(
        proto.MESSAGE, number=2, message=gca_dataset.ImportDataConfig,
    )


class ImportDataResponse(proto.Message):
    r"""Response message for
    [DatasetService.ImportData][google.cloud.aiplatform.v1.DatasetService.ImportData].
        """


class ImportDataOperationMetadata(proto.Message):
    r"""Runtime operation information for
    [DatasetService.ImportData][google.cloud.aiplatform.v1.DatasetService.ImportData].

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1.types.GenericOperationMetadata):
            The common part of the operation metadata.
    """

    generic_metadata = proto.Field(
        proto.MESSAGE, number=1, message=operation.GenericOperationMetadata,
    )


class ExportDataRequest(proto.Message):
    r"""Request message for
    [DatasetService.ExportData][google.cloud.aiplatform.v1.DatasetService.ExportData].

    Attributes:
        name (str):
            Required. The name of the Dataset resource. Format:
            ``projects/{project}/locations/{location}/datasets/{dataset}``
        export_config (google.cloud.aiplatform_v1.types.ExportDataConfig):
            Required. The desired output location.
    """

    name = proto.Field(proto.STRING, number=1,)
    export_config = proto.Field(
        proto.MESSAGE, number=2, message=gca_dataset.ExportDataConfig,
    )


class ExportDataResponse(proto.Message):
    r"""Response message for
    [DatasetService.ExportData][google.cloud.aiplatform.v1.DatasetService.ExportData].

    Attributes:
        exported_files (Sequence[str]):
            All of the files that are exported in this
            export operation.
    """

    exported_files = proto.RepeatedField(proto.STRING, number=1,)


class ExportDataOperationMetadata(proto.Message):
    r"""Runtime operation information for
    [DatasetService.ExportData][google.cloud.aiplatform.v1.DatasetService.ExportData].

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1.types.GenericOperationMetadata):
            The common part of the operation metadata.
        gcs_output_directory (str):
            A Google Cloud Storage directory which path
            ends with '/'. The exported data is stored in
            the directory.
    """

    generic_metadata = proto.Field(
        proto.MESSAGE, number=1, message=operation.GenericOperationMetadata,
    )
    gcs_output_directory = proto.Field(proto.STRING, number=2,)


class ListDataItemsRequest(proto.Message):
    r"""Request message for
    [DatasetService.ListDataItems][google.cloud.aiplatform.v1.DatasetService.ListDataItems].

    Attributes:
        parent (str):
            Required. The resource name of the Dataset to list DataItems
            from. Format:
            ``projects/{project}/locations/{location}/datasets/{dataset}``
        filter (str):
            The standard list filter.
        page_size (int):
            The standard list page size.
        page_token (str):
            The standard list page token.
        read_mask (google.protobuf.field_mask_pb2.FieldMask):
            Mask specifying which fields to read.
        order_by (str):
            A comma-separated list of fields to order by,
            sorted in ascending order. Use "desc" after a
            field name for descending.
    """

    parent = proto.Field(proto.STRING, number=1,)
    filter = proto.Field(proto.STRING, number=2,)
    page_size = proto.Field(proto.INT32, number=3,)
    page_token = proto.Field(proto.STRING, number=4,)
    read_mask = proto.Field(proto.MESSAGE, number=5, message=field_mask_pb2.FieldMask,)
    order_by = proto.Field(proto.STRING, number=6,)


class ListDataItemsResponse(proto.Message):
    r"""Response message for
    [DatasetService.ListDataItems][google.cloud.aiplatform.v1.DatasetService.ListDataItems].

    Attributes:
        data_items (Sequence[google.cloud.aiplatform_v1.types.DataItem]):
            A list of DataItems that matches the
            specified filter in the request.
        next_page_token (str):
            The standard List next-page token.
    """

    @property
    def raw_page(self):
        return self

    data_items = proto.RepeatedField(
        proto.MESSAGE, number=1, message=data_item.DataItem,
    )
    next_page_token = proto.Field(proto.STRING, number=2,)


class GetAnnotationSpecRequest(proto.Message):
    r"""Request message for
    [DatasetService.GetAnnotationSpec][google.cloud.aiplatform.v1.DatasetService.GetAnnotationSpec].

    Attributes:
        name (str):
            Required. The name of the AnnotationSpec resource. Format:

            ``projects/{project}/locations/{location}/datasets/{dataset}/annotationSpecs/{annotation_spec}``
        read_mask (google.protobuf.field_mask_pb2.FieldMask):
            Mask specifying which fields to read.
    """

    name = proto.Field(proto.STRING, number=1,)
    read_mask = proto.Field(proto.MESSAGE, number=2, message=field_mask_pb2.FieldMask,)


class ListAnnotationsRequest(proto.Message):
    r"""Request message for
    [DatasetService.ListAnnotations][google.cloud.aiplatform.v1.DatasetService.ListAnnotations].

    Attributes:
        parent (str):
            Required. The resource name of the DataItem to list
            Annotations from. Format:

            ``projects/{project}/locations/{location}/datasets/{dataset}/dataItems/{data_item}``
        filter (str):
            The standard list filter.
        page_size (int):
            The standard list page size.
        page_token (str):
            The standard list page token.
        read_mask (google.protobuf.field_mask_pb2.FieldMask):
            Mask specifying which fields to read.
        order_by (str):
            A comma-separated list of fields to order by,
            sorted in ascending order. Use "desc" after a
            field name for descending.
    """

    parent = proto.Field(proto.STRING, number=1,)
    filter = proto.Field(proto.STRING, number=2,)
    page_size = proto.Field(proto.INT32, number=3,)
    page_token = proto.Field(proto.STRING, number=4,)
    read_mask = proto.Field(proto.MESSAGE, number=5, message=field_mask_pb2.FieldMask,)
    order_by = proto.Field(proto.STRING, number=6,)


class ListAnnotationsResponse(proto.Message):
    r"""Response message for
    [DatasetService.ListAnnotations][google.cloud.aiplatform.v1.DatasetService.ListAnnotations].

    Attributes:
        annotations (Sequence[google.cloud.aiplatform_v1.types.Annotation]):
            A list of Annotations that matches the
            specified filter in the request.
        next_page_token (str):
            The standard List next-page token.
    """

    @property
    def raw_page(self):
        return self

    annotations = proto.RepeatedField(
        proto.MESSAGE, number=1, message=annotation.Annotation,
    )
    next_page_token = proto.Field(proto.STRING, number=2,)


__all__ = tuple(sorted(__protobuf__.manifest))
