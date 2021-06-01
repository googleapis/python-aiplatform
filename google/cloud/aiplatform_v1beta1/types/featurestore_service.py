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

from google.cloud.aiplatform_v1beta1.types import entity_type as gca_entity_type
from google.cloud.aiplatform_v1beta1.types import feature as gca_feature
from google.cloud.aiplatform_v1beta1.types import (
    feature_selector as gca_feature_selector,
)
from google.cloud.aiplatform_v1beta1.types import featurestore as gca_featurestore
from google.cloud.aiplatform_v1beta1.types import io
from google.cloud.aiplatform_v1beta1.types import operation
from google.protobuf import field_mask_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "CreateFeaturestoreRequest",
        "GetFeaturestoreRequest",
        "ListFeaturestoresRequest",
        "ListFeaturestoresResponse",
        "UpdateFeaturestoreRequest",
        "DeleteFeaturestoreRequest",
        "ImportFeatureValuesRequest",
        "ImportFeatureValuesResponse",
        "BatchReadFeatureValuesRequest",
        "ExportFeatureValuesRequest",
        "DestinationFeatureSetting",
        "FeatureValueDestination",
        "ExportFeatureValuesResponse",
        "BatchReadFeatureValuesResponse",
        "CreateEntityTypeRequest",
        "GetEntityTypeRequest",
        "ListEntityTypesRequest",
        "ListEntityTypesResponse",
        "UpdateEntityTypeRequest",
        "DeleteEntityTypeRequest",
        "CreateFeatureRequest",
        "BatchCreateFeaturesRequest",
        "BatchCreateFeaturesResponse",
        "GetFeatureRequest",
        "ListFeaturesRequest",
        "ListFeaturesResponse",
        "SearchFeaturesRequest",
        "SearchFeaturesResponse",
        "UpdateFeatureRequest",
        "DeleteFeatureRequest",
        "CreateFeaturestoreOperationMetadata",
        "UpdateFeaturestoreOperationMetadata",
        "ImportFeatureValuesOperationMetadata",
        "ExportFeatureValuesOperationMetadata",
        "BatchReadFeatureValuesOperationMetadata",
        "CreateEntityTypeOperationMetadata",
        "CreateFeatureOperationMetadata",
        "BatchCreateFeaturesOperationMetadata",
    },
)


class CreateFeaturestoreRequest(proto.Message):
    r"""Request message for
    [FeaturestoreService.CreateFeaturestore][google.cloud.aiplatform.v1beta1.FeaturestoreService.CreateFeaturestore].

    Attributes:
        parent (str):
            Required. The resource name of the Location to create
            Featurestores. Format:
            ``projects/{project}/locations/{location}'``
        featurestore (google.cloud.aiplatform_v1beta1.types.Featurestore):
            Required. The Featurestore to create.
        featurestore_id (str):
            Required. The ID to use for this Featurestore, which will
            become the final component of the Featurestore's resource
            name.

            This value may be up to 60 characters, and valid characters
            are ``[a-z0-9_]``. The first character cannot be a number.

            The value must be unique within the project and location.
    """

    parent = proto.Field(proto.STRING, number=1,)
    featurestore = proto.Field(
        proto.MESSAGE, number=2, message=gca_featurestore.Featurestore,
    )
    featurestore_id = proto.Field(proto.STRING, number=3,)


class GetFeaturestoreRequest(proto.Message):
    r"""Request message for
    [FeaturestoreService.GetFeaturestore][google.cloud.aiplatform.v1beta1.FeaturestoreService.GetFeaturestore].

    Attributes:
        name (str):
            Required. The name of the Featurestore
            resource.
    """

    name = proto.Field(proto.STRING, number=1,)


class ListFeaturestoresRequest(proto.Message):
    r"""Request message for
    [FeaturestoreService.ListFeaturestores][google.cloud.aiplatform.v1beta1.FeaturestoreService.ListFeaturestores].

    Attributes:
        parent (str):
            Required. The resource name of the Location to list
            Featurestores. Format:
            ``projects/{project}/locations/{location}``
        filter (str):
            Lists the featurestores that match the filter expression.
            The following fields are supported:

            -  ``display_name``: Supports =, != comparisons.
            -  ``create_time``: Supports =, !=, <, >, <=, and >=
               comparisons. Values must be in RFC 3339 format.
            -  ``update_time``: Supports =, !=, <, >, <=, and >=
               comparisons. Values must be in RFC 3339 format.
            -  ``online_serving_config.fixed_node_count``: Supports =,
               !=, <, >, <=, and >= comparisons.
            -  ``labels``: Supports key-value equality and key presence.

            Examples:

            -  ``create_time > "2020-01-01" OR update_time > "2020-01-01"``
               Featurestores created or updated after 2020-01-01.
            -  ``labels.env = "prod"`` Featurestores with label "env"
               set to "prod".
        page_size (int):
            The maximum number of Featurestores to
            return. The service may return fewer than this
            value. If unspecified, at most 100 Featurestores
            will be returned. The maximum value is 100; any
            value greater than 100 will be coerced to 100.
        page_token (str):
            A page token, received from a previous
            [FeaturestoreService.ListFeaturestores][google.cloud.aiplatform.v1beta1.FeaturestoreService.ListFeaturestores]
            call. Provide this to retrieve the subsequent page.

            When paginating, all other parameters provided to
            [FeaturestoreService.ListFeaturestores][google.cloud.aiplatform.v1beta1.FeaturestoreService.ListFeaturestores]
            must match the call that provided the page token.
        order_by (str):
            A comma-separated list of fields to order by, sorted in
            ascending order. Use "desc" after a field name for
            descending. Supported Fields:

            -  ``display_name``
            -  ``create_time``
            -  ``update_time``
            -  ``online_serving_config.fixed_node_count``
        read_mask (google.protobuf.field_mask_pb2.FieldMask):
            Mask specifying which fields to read.
    """

    parent = proto.Field(proto.STRING, number=1,)
    filter = proto.Field(proto.STRING, number=2,)
    page_size = proto.Field(proto.INT32, number=3,)
    page_token = proto.Field(proto.STRING, number=4,)
    order_by = proto.Field(proto.STRING, number=5,)
    read_mask = proto.Field(proto.MESSAGE, number=6, message=field_mask_pb2.FieldMask,)


class ListFeaturestoresResponse(proto.Message):
    r"""Response message for
    [FeaturestoreService.ListFeaturestores][google.cloud.aiplatform.v1beta1.FeaturestoreService.ListFeaturestores].

    Attributes:
        featurestores (Sequence[google.cloud.aiplatform_v1beta1.types.Featurestore]):
            The Featurestores matching the request.
        next_page_token (str):
            A token, which can be sent as
            [ListFeaturestoresRequest.page_token][google.cloud.aiplatform.v1beta1.ListFeaturestoresRequest.page_token]
            to retrieve the next page. If this field is omitted, there
            are no subsequent pages.
    """

    @property
    def raw_page(self):
        return self

    featurestores = proto.RepeatedField(
        proto.MESSAGE, number=1, message=gca_featurestore.Featurestore,
    )
    next_page_token = proto.Field(proto.STRING, number=2,)


class UpdateFeaturestoreRequest(proto.Message):
    r"""Request message for
    [FeaturestoreService.UpdateFeaturestore][google.cloud.aiplatform.v1beta1.FeaturestoreService.UpdateFeaturestore].

    Attributes:
        featurestore (google.cloud.aiplatform_v1beta1.types.Featurestore):
            Required. The Featurestore's ``name`` field is used to
            identify the Featurestore to be updated. Format:
            ``projects/{project}/locations/{location}/featurestores/{featurestore}``
        update_mask (google.protobuf.field_mask_pb2.FieldMask):
            Field mask is used to specify the fields to be overwritten
            in the Featurestore resource by the update. The fields
            specified in the update_mask are relative to the resource,
            not the full request. A field will be overwritten if it is
            in the mask. If the user does not provide a mask then only
            the non-empty fields present in the request will be
            overwritten. Set the update_mask to ``*`` to override all
            fields.

            Updatable fields:

            -  ``display_name``
            -  ``labels``
            -  ``online_serving_config.fixed_node_count``
            -  ``retention_policy.online_storage_ttl_days``
    """

    featurestore = proto.Field(
        proto.MESSAGE, number=1, message=gca_featurestore.Featurestore,
    )
    update_mask = proto.Field(
        proto.MESSAGE, number=2, message=field_mask_pb2.FieldMask,
    )


class DeleteFeaturestoreRequest(proto.Message):
    r"""Request message for
    [FeaturestoreService.DeleteFeaturestore][google.cloud.aiplatform.v1beta1.FeaturestoreService.DeleteFeaturestore].

    Attributes:
        name (str):
            Required. The name of the Featurestore to be deleted.
            Format:
            ``projects/{project}/locations/{location}/featurestores/{featurestore}``
        force (bool):
            If set to true, any EntityTypes and Features
            for this Featurestore will also be deleted.
            (Otherwise, the request will only work if the
            Featurestore has no EntityTypes.)
    """

    name = proto.Field(proto.STRING, number=1,)
    force = proto.Field(proto.BOOL, number=2,)


class ImportFeatureValuesRequest(proto.Message):
    r"""Request message for
    [FeaturestoreService.ImportFeatureValues][google.cloud.aiplatform.v1beta1.FeaturestoreService.ImportFeatureValues].

    Attributes:
        avro_source (google.cloud.aiplatform_v1beta1.types.AvroSource):

        bigquery_source (google.cloud.aiplatform_v1beta1.types.BigQuerySource):

        csv_source (google.cloud.aiplatform_v1beta1.types.CsvSource):

        feature_time_field (str):
            Source column that holds the Feature
            timestamp for all Feature values in each entity.
        feature_time (google.protobuf.timestamp_pb2.Timestamp):
            Single Feature timestamp for all entities
            being imported. The timestamp must not have
            higher than millisecond precision.
        entity_type (str):
            Required. The resource name of the EntityType grouping the
            Features for which values are being imported. Format:
            ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entityType}``
        entity_id_field (str):
            Source column that holds entity IDs. If not provided, entity
            IDs are extracted from the column named ``entity_id``.
        feature_specs (Sequence[google.cloud.aiplatform_v1beta1.types.ImportFeatureValuesRequest.FeatureSpec]):
            Required. Specifications defining which Feature values to
            import from the entity. The request fails if no
            feature_specs are provided, and having multiple
            feature_specs for one Feature is not allowed.
        disable_online_serving (bool):
            If set, data will not be imported for online
            serving. This is typically used for backfilling,
            where Feature generation timestamps are not in
            the timestamp range needed for online serving.
        worker_count (int):
            Specifies the number of workers that are used
            to write data to the Featurestore. Consider the
            online serving capacity that you require to
            achieve the desired import throughput without
            interfering with online serving. The value must
            be positive, and less than or equal to 100. If
            not set, defaults to using 1 worker. The low
            count ensures minimal impact on online serving
            performance.
    """

    class FeatureSpec(proto.Message):
        r"""Defines the Feature value(s) to import.
        Attributes:
            id (str):
                Required. ID of the Feature to import values
                of. This Feature must exist in the target
                EntityType, or the request will fail.
            source_field (str):
                Source column to get the Feature values from.
                If not set, uses the column with the same name
                as the Feature ID.
        """

        id = proto.Field(proto.STRING, number=1,)
        source_field = proto.Field(proto.STRING, number=2,)

    avro_source = proto.Field(
        proto.MESSAGE, number=2, oneof="source", message=io.AvroSource,
    )
    bigquery_source = proto.Field(
        proto.MESSAGE, number=3, oneof="source", message=io.BigQuerySource,
    )
    csv_source = proto.Field(
        proto.MESSAGE, number=4, oneof="source", message=io.CsvSource,
    )
    feature_time_field = proto.Field(
        proto.STRING, number=6, oneof="feature_time_source",
    )
    feature_time = proto.Field(
        proto.MESSAGE,
        number=7,
        oneof="feature_time_source",
        message=timestamp_pb2.Timestamp,
    )
    entity_type = proto.Field(proto.STRING, number=1,)
    entity_id_field = proto.Field(proto.STRING, number=5,)
    feature_specs = proto.RepeatedField(proto.MESSAGE, number=8, message=FeatureSpec,)
    disable_online_serving = proto.Field(proto.BOOL, number=9,)
    worker_count = proto.Field(proto.INT32, number=11,)


class ImportFeatureValuesResponse(proto.Message):
    r"""Response message for
    [FeaturestoreService.ImportFeatureValues][google.cloud.aiplatform.v1beta1.FeaturestoreService.ImportFeatureValues].

    Attributes:
        imported_entity_count (int):
            Number of entities that have been imported by
            the operation.
        imported_feature_value_count (int):
            Number of Feature values that have been
            imported by the operation.
        invalid_row_count (int):
            The number of rows in input source that weren't imported due
            to either

            -  Not having any featureValues.
            -  Having a null entityId.
            -  Having a null timestamp.
            -  Not being parsable (applicable for CSV sources).
    """

    imported_entity_count = proto.Field(proto.INT64, number=1,)
    imported_feature_value_count = proto.Field(proto.INT64, number=2,)
    invalid_row_count = proto.Field(proto.INT64, number=6,)


class BatchReadFeatureValuesRequest(proto.Message):
    r"""Request message for
    [FeaturestoreService.BatchReadFeatureValues][google.cloud.aiplatform.v1beta1.FeaturestoreService.BatchReadFeatureValues].
    (- Next Id: 6 -)

    Attributes:
        csv_read_instances (google.cloud.aiplatform_v1beta1.types.CsvSource):
            Each read instance consists of exactly one read timestamp
            and one or more entity IDs identifying entities of the
            corresponding EntityTypes whose Features are requested.

            Each output instance contains Feature values of requested
            entities concatenated together as of the read time.

            An example read instance may be
            ``foo_entity_id, bar_entity_id, 2020-01-01T10:00:00.123Z``.

            An example output instance may be
            ``foo_entity_id, bar_entity_id, 2020-01-01T10:00:00.123Z, foo_entity_feature1_value, bar_entity_feature2_value``.

            Timestamp in each read instance must be millisecond-aligned.

            ``csv_read_instances`` are read instances stored in a
            plain-text CSV file. The header should be:
            [ENTITY_TYPE_ID1], [ENTITY_TYPE_ID2], ..., timestamp

            The columns can be in any order.

            Values in the timestamp column must use the RFC 3339 format,
            e.g. ``2012-07-30T10:43:17.123Z``.
        featurestore (str):
            Required. The resource name of the Featurestore from which
            to query Feature values. Format:
            ``projects/{project}/locations/{location}/featurestores/{featurestore}``
        destination (google.cloud.aiplatform_v1beta1.types.FeatureValueDestination):
            Required. Specifies output location and
            format.
        entity_type_specs (Sequence[google.cloud.aiplatform_v1beta1.types.BatchReadFeatureValuesRequest.EntityTypeSpec]):
            Required. Specifies EntityType grouping Features to read
            values of and settings. Each EntityType referenced in
            [BatchReadFeatureValuesRequest.entity_type_specs] must have
            a column specifying entity IDs in tha EntityType in
            [BatchReadFeatureValuesRequest.request][] .
    """

    class EntityTypeSpec(proto.Message):
        r"""Selects Features of an EntityType to read values of and
        specifies read settings.

        Attributes:
            entity_type_id (str):
                Required. ID of the EntityType to select Features. The
                EntityType id is the
                [entity_type_id][google.cloud.aiplatform.v1beta1.CreateEntityTypeRequest.entity_type_id]
                specified during EntityType creation.
            feature_selector (google.cloud.aiplatform_v1beta1.types.FeatureSelector):
                Required. Selectors choosing which Feature
                values to read from the EntityType.
            settings (Sequence[google.cloud.aiplatform_v1beta1.types.DestinationFeatureSetting]):
                Per-Feature settings for the batch read.
        """

        entity_type_id = proto.Field(proto.STRING, number=1,)
        feature_selector = proto.Field(
            proto.MESSAGE, number=2, message=gca_feature_selector.FeatureSelector,
        )
        settings = proto.RepeatedField(
            proto.MESSAGE, number=3, message="DestinationFeatureSetting",
        )

    csv_read_instances = proto.Field(
        proto.MESSAGE, number=3, oneof="read_option", message=io.CsvSource,
    )
    featurestore = proto.Field(proto.STRING, number=1,)
    destination = proto.Field(
        proto.MESSAGE, number=4, message="FeatureValueDestination",
    )
    entity_type_specs = proto.RepeatedField(
        proto.MESSAGE, number=7, message=EntityTypeSpec,
    )


class ExportFeatureValuesRequest(proto.Message):
    r"""Request message for
    [FeaturestoreService.ExportFeatureValues][google.cloud.aiplatform.v1beta1.FeaturestoreService.ExportFeatureValues].

    Attributes:
        snapshot_export (google.cloud.aiplatform_v1beta1.types.ExportFeatureValuesRequest.SnapshotExport):
            Exports Feature values of all entities of the
            EntityType as of a snapshot time.
        entity_type (str):
            Required. The resource name of the EntityType from which to
            export Feature values. Format:
            ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}``
        destination (google.cloud.aiplatform_v1beta1.types.FeatureValueDestination):
            Required. Specifies destination location and
            format.
        feature_selector (google.cloud.aiplatform_v1beta1.types.FeatureSelector):
            Required. Selects Features to export values
            of.
        settings (Sequence[google.cloud.aiplatform_v1beta1.types.DestinationFeatureSetting]):
            Per-Feature export settings.
    """

    class SnapshotExport(proto.Message):
        r"""Describes exporting Feature values as of the snapshot
        timestamp.

        Attributes:
            snapshot_time (google.protobuf.timestamp_pb2.Timestamp):
                Exports Feature values as of this timestamp.
                If not set, retrieve values as of now.
                Timestamp, if present, must not have higher than
                millisecond precision.
        """

        snapshot_time = proto.Field(
            proto.MESSAGE, number=1, message=timestamp_pb2.Timestamp,
        )

    snapshot_export = proto.Field(
        proto.MESSAGE, number=3, oneof="mode", message=SnapshotExport,
    )
    entity_type = proto.Field(proto.STRING, number=1,)
    destination = proto.Field(
        proto.MESSAGE, number=4, message="FeatureValueDestination",
    )
    feature_selector = proto.Field(
        proto.MESSAGE, number=5, message=gca_feature_selector.FeatureSelector,
    )
    settings = proto.RepeatedField(
        proto.MESSAGE, number=6, message="DestinationFeatureSetting",
    )


class DestinationFeatureSetting(proto.Message):
    r"""
    Attributes:
        feature_id (str):
            Required. The ID of the Feature to apply the
            setting to.
        destination_field (str):
            Specify the field name in the export
            destination. If not specified, Feature ID is
            used.
    """

    feature_id = proto.Field(proto.STRING, number=1,)
    destination_field = proto.Field(proto.STRING, number=2,)


class FeatureValueDestination(proto.Message):
    r"""A destination location for Feature values and format.
    Attributes:
        bigquery_destination (google.cloud.aiplatform_v1beta1.types.BigQueryDestination):
            Output in BigQuery format.
            [BigQueryDestination.output_uri][google.cloud.aiplatform.v1beta1.BigQueryDestination.output_uri]
            in
            [FeatureValueDestination.bigquery_destination][google.cloud.aiplatform.v1beta1.FeatureValueDestination.bigquery_destination]
            must refer to a table.
        tfrecord_destination (google.cloud.aiplatform_v1beta1.types.TFRecordDestination):
            Output in TFRecord format.

            Below are the mapping from Feature value type in
            Featurestore to Feature value type in TFRecord:

            ::

                Value type in Featurestore                 | Value type in TFRecord
                DOUBLE, DOUBLE_ARRAY                       | FLOAT_LIST
                INT64, INT64_ARRAY                         | INT64_LIST
                STRING, STRING_ARRAY, BYTES                | BYTES_LIST
                true -> byte_string("true"), false -> byte_string("false")
                BOOL, BOOL_ARRAY (true, false)             | BYTES_LIST
        csv_destination (google.cloud.aiplatform_v1beta1.types.CsvDestination):
            Output in CSV format. Array Feature value
            types are not allowed in CSV format.
    """

    bigquery_destination = proto.Field(
        proto.MESSAGE, number=1, oneof="destination", message=io.BigQueryDestination,
    )
    tfrecord_destination = proto.Field(
        proto.MESSAGE, number=2, oneof="destination", message=io.TFRecordDestination,
    )
    csv_destination = proto.Field(
        proto.MESSAGE, number=3, oneof="destination", message=io.CsvDestination,
    )


class ExportFeatureValuesResponse(proto.Message):
    r"""Response message for
    [FeaturestoreService.ExportFeatureValues][google.cloud.aiplatform.v1beta1.FeaturestoreService.ExportFeatureValues].
        """


class BatchReadFeatureValuesResponse(proto.Message):
    r"""Response message for
    [FeaturestoreService.BatchReadFeatureValues][google.cloud.aiplatform.v1beta1.FeaturestoreService.BatchReadFeatureValues].
        """


class CreateEntityTypeRequest(proto.Message):
    r"""Request message for
    [FeaturestoreService.CreateEntityType][google.cloud.aiplatform.v1beta1.FeaturestoreService.CreateEntityType].

    Attributes:
        parent (str):
            Required. The resource name of the Featurestore to create
            EntityTypes. Format:
            ``projects/{project}/locations/{location}/featurestores/{featurestore}``
        entity_type (google.cloud.aiplatform_v1beta1.types.EntityType):
            The EntityType to create.
        entity_type_id (str):
            Required. The ID to use for the EntityType, which will
            become the final component of the EntityType's resource
            name.

            This value may be up to 60 characters, and valid characters
            are ``[a-z0-9_]``. The first character cannot be a number.

            The value must be unique within a featurestore.
    """

    parent = proto.Field(proto.STRING, number=1,)
    entity_type = proto.Field(
        proto.MESSAGE, number=2, message=gca_entity_type.EntityType,
    )
    entity_type_id = proto.Field(proto.STRING, number=3,)


class GetEntityTypeRequest(proto.Message):
    r"""Request message for
    [FeaturestoreService.GetEntityType][google.cloud.aiplatform.v1beta1.FeaturestoreService.GetEntityType].

    Attributes:
        name (str):
            Required. The name of the EntityType resource. Format:
            ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}``
    """

    name = proto.Field(proto.STRING, number=1,)


class ListEntityTypesRequest(proto.Message):
    r"""Request message for
    [FeaturestoreService.ListEntityTypes][google.cloud.aiplatform.v1beta1.FeaturestoreService.ListEntityTypes].

    Attributes:
        parent (str):
            Required. The resource name of the Featurestore to list
            EntityTypes. Format:
            ``projects/{project}/locations/{location}/featurestores/{featurestore}``
        filter (str):
            Lists the EntityTypes that match the filter expression. The
            following filters are supported:

            -  ``create_time``: Supports =, !=, <, >, >=, and <=
               comparisons. Values must be in RFC 3339 format.
            -  ``update_time``: Supports =, !=, <, >, >=, and <=
               comparisons. Values must be in RFC 3339 format.
            -  ``labels``: Supports key-value equality as well as key
               presence.

            Examples:

            -  ``create_time > \"2020-01-31T15:30:00.000000Z\" OR update_time > \"2020-01-31T15:30:00.000000Z\"``
               --> EntityTypes created or updated after
               2020-01-31T15:30:00.000000Z.
            -  ``labels.active = yes AND labels.env = prod`` -->
               EntityTypes having both (active: yes) and (env: prod)
               labels.
            -  ``labels.env: *`` --> Any EntityType which has a label
               with 'env' as the key.
        page_size (int):
            The maximum number of EntityTypes to return.
            The service may return fewer than this value. If
            unspecified, at most 1000 EntityTypes will be
            returned. The maximum value is 1000; any value
            greater than 1000 will be coerced to 1000.
        page_token (str):
            A page token, received from a previous
            [FeaturestoreService.ListEntityTypes][google.cloud.aiplatform.v1beta1.FeaturestoreService.ListEntityTypes]
            call. Provide this to retrieve the subsequent page.

            When paginating, all other parameters provided to
            [FeaturestoreService.ListEntityTypes][google.cloud.aiplatform.v1beta1.FeaturestoreService.ListEntityTypes]
            must match the call that provided the page token.
        order_by (str):
            A comma-separated list of fields to order by, sorted in
            ascending order. Use "desc" after a field name for
            descending.

            Supported fields:

            -  ``entity_type_id``
            -  ``create_time``
            -  ``update_time``
        read_mask (google.protobuf.field_mask_pb2.FieldMask):
            Mask specifying which fields to read.
    """

    parent = proto.Field(proto.STRING, number=1,)
    filter = proto.Field(proto.STRING, number=2,)
    page_size = proto.Field(proto.INT32, number=3,)
    page_token = proto.Field(proto.STRING, number=4,)
    order_by = proto.Field(proto.STRING, number=5,)
    read_mask = proto.Field(proto.MESSAGE, number=6, message=field_mask_pb2.FieldMask,)


class ListEntityTypesResponse(proto.Message):
    r"""Response message for
    [FeaturestoreService.ListEntityTypes][google.cloud.aiplatform.v1beta1.FeaturestoreService.ListEntityTypes].

    Attributes:
        entity_types (Sequence[google.cloud.aiplatform_v1beta1.types.EntityType]):
            The EntityTypes matching the request.
        next_page_token (str):
            A token, which can be sent as
            [ListEntityTypesRequest.page_token][google.cloud.aiplatform.v1beta1.ListEntityTypesRequest.page_token]
            to retrieve the next page. If this field is omitted, there
            are no subsequent pages.
    """

    @property
    def raw_page(self):
        return self

    entity_types = proto.RepeatedField(
        proto.MESSAGE, number=1, message=gca_entity_type.EntityType,
    )
    next_page_token = proto.Field(proto.STRING, number=2,)


class UpdateEntityTypeRequest(proto.Message):
    r"""Request message for
    [FeaturestoreService.UpdateEntityType][google.cloud.aiplatform.v1beta1.FeaturestoreService.UpdateEntityType].

    Attributes:
        entity_type (google.cloud.aiplatform_v1beta1.types.EntityType):
            Required. The EntityType's ``name`` field is used to
            identify the EntityType to be updated. Format:
            ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}``
        update_mask (google.protobuf.field_mask_pb2.FieldMask):
            Field mask is used to specify the fields to be overwritten
            in the EntityType resource by the update. The fields
            specified in the update_mask are relative to the resource,
            not the full request. A field will be overwritten if it is
            in the mask. If the user does not provide a mask then only
            the non-empty fields present in the request will be
            overwritten. Set the update_mask to ``*`` to override all
            fields.

            Updatable fields:

            -  ``description``
            -  ``labels``
            -  ``monitoring_config.snapshot_analysis.disabled``
            -  ``monitoring_config.snapshot_analysis.monitoring_interval``
    """

    entity_type = proto.Field(
        proto.MESSAGE, number=1, message=gca_entity_type.EntityType,
    )
    update_mask = proto.Field(
        proto.MESSAGE, number=2, message=field_mask_pb2.FieldMask,
    )


class DeleteEntityTypeRequest(proto.Message):
    r"""Request message for [FeaturestoreService.DeleteEntityTypes][].
    Attributes:
        name (str):
            Required. The name of the EntityType to be deleted. Format:
            ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}``
        force (bool):
            If set to true, any Features for this
            EntityType will also be deleted. (Otherwise, the
            request will only work if the EntityType has no
            Features.)
    """

    name = proto.Field(proto.STRING, number=1,)
    force = proto.Field(proto.BOOL, number=2,)


class CreateFeatureRequest(proto.Message):
    r"""Request message for
    [FeaturestoreService.CreateFeature][google.cloud.aiplatform.v1beta1.FeaturestoreService.CreateFeature].

    Attributes:
        parent (str):
            Required. The resource name of the EntityType to create a
            Feature. Format:
            ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}``
        feature (google.cloud.aiplatform_v1beta1.types.Feature):
            Required. The Feature to create.
        feature_id (str):
            Required. The ID to use for the Feature, which will become
            the final component of the Feature's resource name.

            This value may be up to 60 characters, and valid characters
            are ``[a-z0-9_]``. The first character cannot be a number.

            The value must be unique within an EntityType.
    """

    parent = proto.Field(proto.STRING, number=1,)
    feature = proto.Field(proto.MESSAGE, number=2, message=gca_feature.Feature,)
    feature_id = proto.Field(proto.STRING, number=3,)


class BatchCreateFeaturesRequest(proto.Message):
    r"""Request message for
    [FeaturestoreService.BatchCreateFeatures][google.cloud.aiplatform.v1beta1.FeaturestoreService.BatchCreateFeatures].

    Attributes:
        parent (str):
            Required. The resource name of the EntityType to create the
            batch of Features under. Format:
            ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}``
        requests (Sequence[google.cloud.aiplatform_v1beta1.types.CreateFeatureRequest]):
            Required. The request message specifying the Features to
            create. All Features must be created under the same parent
            EntityType. The ``parent`` field in each child request
            message can be omitted. If ``parent`` is set in a child
            request, then the value must match the ``parent`` value in
            this request message.
    """

    parent = proto.Field(proto.STRING, number=1,)
    requests = proto.RepeatedField(
        proto.MESSAGE, number=2, message="CreateFeatureRequest",
    )


class BatchCreateFeaturesResponse(proto.Message):
    r"""Response message for
    [FeaturestoreService.BatchCreateFeatures][google.cloud.aiplatform.v1beta1.FeaturestoreService.BatchCreateFeatures].

    Attributes:
        features (Sequence[google.cloud.aiplatform_v1beta1.types.Feature]):
            The Features created.
    """

    features = proto.RepeatedField(
        proto.MESSAGE, number=1, message=gca_feature.Feature,
    )


class GetFeatureRequest(proto.Message):
    r"""Request message for
    [FeaturestoreService.GetFeature][google.cloud.aiplatform.v1beta1.FeaturestoreService.GetFeature].

    Attributes:
        name (str):
            Required. The name of the Feature resource. Format:
            ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}``
    """

    name = proto.Field(proto.STRING, number=1,)


class ListFeaturesRequest(proto.Message):
    r"""Request message for
    [FeaturestoreService.ListFeatures][google.cloud.aiplatform.v1beta1.FeaturestoreService.ListFeatures].

    Attributes:
        parent (str):
            Required. The resource name of the Location to list
            Features. Format:
            ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}``
        filter (str):
            Lists the Features that match the filter expression. The
            following filters are supported:

            -  ``value_type``: Supports = and != comparisons.
            -  ``create_time``: Supports =, !=, <, >, >=, and <=
               comparisons. Values must be in RFC 3339 format.
            -  ``update_time``: Supports =, !=, <, >, >=, and <=
               comparisons. Values must be in RFC 3339 format.
            -  ``labels``: Supports key-value equality as well as key
               presence.

            Examples:

            -  ``value_type = DOUBLE`` --> Features whose type is
               DOUBLE.
            -  ``create_time > \"2020-01-31T15:30:00.000000Z\" OR update_time > \"2020-01-31T15:30:00.000000Z\"``
               --> EntityTypes created or updated after
               2020-01-31T15:30:00.000000Z.
            -  ``labels.active = yes AND labels.env = prod`` -->
               Features having both (active: yes) and (env: prod)
               labels.
            -  ``labels.env: *`` --> Any Feature which has a label with
               'env' as the key.
        page_size (int):
            The maximum number of Features to return. The
            service may return fewer than this value. If
            unspecified, at most 1000 Features will be
            returned. The maximum value is 1000; any value
            greater than 1000 will be coerced to 1000.
        page_token (str):
            A page token, received from a previous
            [FeaturestoreService.ListFeatures][google.cloud.aiplatform.v1beta1.FeaturestoreService.ListFeatures]
            call. Provide this to retrieve the subsequent page.

            When paginating, all other parameters provided to
            [FeaturestoreService.ListFeatures][google.cloud.aiplatform.v1beta1.FeaturestoreService.ListFeatures]
            must match the call that provided the page token.
        order_by (str):
            A comma-separated list of fields to order by, sorted in
            ascending order. Use "desc" after a field name for
            descending. Supported fields:

            -  ``feature_id``
            -  ``value_type``
            -  ``create_time``
            -  ``update_time``
        read_mask (google.protobuf.field_mask_pb2.FieldMask):
            Mask specifying which fields to read.
        latest_stats_count (int):
            If set, return the most recent
            [ListFeaturesRequest.latest_stats_count][google.cloud.aiplatform.v1beta1.ListFeaturesRequest.latest_stats_count]
            of stats for each Feature in response. Valid value is [0,
            10]. If number of stats exists <
            [ListFeaturesRequest.latest_stats_count][google.cloud.aiplatform.v1beta1.ListFeaturesRequest.latest_stats_count],
            return all existing stats.
    """

    parent = proto.Field(proto.STRING, number=1,)
    filter = proto.Field(proto.STRING, number=2,)
    page_size = proto.Field(proto.INT32, number=3,)
    page_token = proto.Field(proto.STRING, number=4,)
    order_by = proto.Field(proto.STRING, number=5,)
    read_mask = proto.Field(proto.MESSAGE, number=6, message=field_mask_pb2.FieldMask,)
    latest_stats_count = proto.Field(proto.INT32, number=7,)


class ListFeaturesResponse(proto.Message):
    r"""Response message for
    [FeaturestoreService.ListFeatures][google.cloud.aiplatform.v1beta1.FeaturestoreService.ListFeatures].

    Attributes:
        features (Sequence[google.cloud.aiplatform_v1beta1.types.Feature]):
            The Features matching the request.
        next_page_token (str):
            A token, which can be sent as
            [ListFeaturesRequest.page_token][google.cloud.aiplatform.v1beta1.ListFeaturesRequest.page_token]
            to retrieve the next page. If this field is omitted, there
            are no subsequent pages.
    """

    @property
    def raw_page(self):
        return self

    features = proto.RepeatedField(
        proto.MESSAGE, number=1, message=gca_feature.Feature,
    )
    next_page_token = proto.Field(proto.STRING, number=2,)


class SearchFeaturesRequest(proto.Message):
    r"""Request message for
    [FeaturestoreService.SearchFeatures][google.cloud.aiplatform.v1beta1.FeaturestoreService.SearchFeatures].

    Attributes:
        location (str):
            Required. The resource name of the Location to search
            Features. Format:
            ``projects/{project}/locations/{location}``
        query (str):
            Query string that is a conjunction of field-restricted
            queries and/or field-restricted filters. Field-restricted
            queries and filters can be combined using ``AND`` to form a
            conjunction.

            A field query is in the form FIELD:QUERY. This implicitly
            checks if QUERY exists as a substring within Feature's
            FIELD. The QUERY and the FIELD are converted to a sequence
            of words (i.e. tokens) for comparison. This is done by:

            -  Removing leading/trailing whitespace and tokenizing the
               search value. Characters that are not one of alphanumeric
               [a-zA-Z0-9], underscore [_], or asterisk [*] are treated
               as delimiters for tokens. (*) is treated as a wildcard
               that matches characters within a token.
            -  Ignoring case.
            -  Prepending an asterisk to the first and appending an
               asterisk to the last token in QUERY.

            A QUERY must be either a singular token or a phrase. A
            phrase is one or multiple words enclosed in double quotation
            marks ("). With phrases, the order of the words is
            important. Words in the phrase must be matching in order and
            consecutively.

            Supported FIELDs for field-restricted queries:

            -  ``feature_id``
            -  ``description``
            -  ``entity_type_id``

            Examples:

            -  ``feature_id: foo`` --> Matches a Feature with ID
               containing the substring ``foo`` (eg. ``foo``,
               ``foofeature``, ``barfoo``).
            -  ``feature_id: foo*feature`` --> Matches a Feature with ID
               containing the substring ``foo*feature`` (eg.
               ``foobarfeature``).
            -  ``feature_id: foo AND description: bar`` --> Matches a
               Feature with ID containing the substring ``foo`` and
               description containing the substring ``bar``.

            Besides field queries, the following exact-match filters are
            supported. The exact-match filters do not support wildcards.
            Unlike field-restricted queries, exact-match filters are
            case-sensitive.

            -  ``feature_id``: Supports = comparisons.
            -  ``description``: Supports = comparisons. Multi-token
               filters should be enclosed in quotes.
            -  ``entity_type_id``: Supports = comparisons.
            -  ``value_type``: Supports = and != comparisons.
            -  ``labels``: Supports key-value equality as well as key
               presence.
            -  ``featurestore_id``: Supports = comparisons.

            Examples:

            -  ``description = "foo bar"`` --> Any Feature with
               description exactly equal to ``foo bar``
            -  ``value_type = DOUBLE`` --> Features whose type is
               DOUBLE.
            -  ``labels.active = yes AND labels.env = prod`` -->
               Features having both (active: yes) and (env: prod)
               labels.
            -  ``labels.env: *`` --> Any Feature which has a label with
               ``env`` as the key.
        page_size (int):
            The maximum number of Features to return. The
            service may return fewer than this value. If
            unspecified, at most 100 Features will be
            returned. The maximum value is 100; any value
            greater than 100 will be coerced to 100.
        page_token (str):
            A page token, received from a previous
            [FeaturestoreService.SearchFeatures][google.cloud.aiplatform.v1beta1.FeaturestoreService.SearchFeatures]
            call. Provide this to retrieve the subsequent page.

            When paginating, all other parameters provided to
            [FeaturestoreService.SearchFeatures][google.cloud.aiplatform.v1beta1.FeaturestoreService.SearchFeatures],
            except ``page_size``, must match the call that provided the
            page token.
    """

    location = proto.Field(proto.STRING, number=1,)
    query = proto.Field(proto.STRING, number=3,)
    page_size = proto.Field(proto.INT32, number=4,)
    page_token = proto.Field(proto.STRING, number=5,)


class SearchFeaturesResponse(proto.Message):
    r"""Response message for
    [FeaturestoreService.SearchFeatures][google.cloud.aiplatform.v1beta1.FeaturestoreService.SearchFeatures].

    Attributes:
        features (Sequence[google.cloud.aiplatform_v1beta1.types.Feature]):
            The Features matching the request.

            Fields returned:

            -  ``name``
            -  ``description``
            -  ``labels``
            -  ``create_time``
            -  ``update_time``
        next_page_token (str):
            A token, which can be sent as
            [SearchFeaturesRequest.page_token][google.cloud.aiplatform.v1beta1.SearchFeaturesRequest.page_token]
            to retrieve the next page. If this field is omitted, there
            are no subsequent pages.
    """

    @property
    def raw_page(self):
        return self

    features = proto.RepeatedField(
        proto.MESSAGE, number=1, message=gca_feature.Feature,
    )
    next_page_token = proto.Field(proto.STRING, number=2,)


class UpdateFeatureRequest(proto.Message):
    r"""Request message for
    [FeaturestoreService.UpdateFeature][google.cloud.aiplatform.v1beta1.FeaturestoreService.UpdateFeature].

    Attributes:
        feature (google.cloud.aiplatform_v1beta1.types.Feature):
            Required. The Feature's ``name`` field is used to identify
            the Feature to be updated. Format:
            ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}/features/{feature}``
        update_mask (google.protobuf.field_mask_pb2.FieldMask):
            Field mask is used to specify the fields to be overwritten
            in the Features resource by the update. The fields specified
            in the update_mask are relative to the resource, not the
            full request. A field will be overwritten if it is in the
            mask. If the user does not provide a mask then only the
            non-empty fields present in the request will be overwritten.
            Set the update_mask to ``*`` to override all fields.

            Updatable fields:

            -  ``description``
            -  ``labels``
            -  ``monitoring_config.snapshot_analysis.disabled``
            -  ``monitoring_config.snapshot_analysis.monitoring_interval``
    """

    feature = proto.Field(proto.MESSAGE, number=1, message=gca_feature.Feature,)
    update_mask = proto.Field(
        proto.MESSAGE, number=2, message=field_mask_pb2.FieldMask,
    )


class DeleteFeatureRequest(proto.Message):
    r"""Request message for
    [FeaturestoreService.DeleteFeature][google.cloud.aiplatform.v1beta1.FeaturestoreService.DeleteFeature].

    Attributes:
        name (str):
            Required. The name of the Features to be deleted. Format:
            ``projects/{project}/locations/{location}/featurestores/{featurestore}/entityTypes/{entity_type}/features/{feature}``
    """

    name = proto.Field(proto.STRING, number=1,)


class CreateFeaturestoreOperationMetadata(proto.Message):
    r"""Details of operations that perform create Featurestore.
    Attributes:
        generic_metadata (google.cloud.aiplatform_v1beta1.types.GenericOperationMetadata):
            Operation metadata for Featurestore.
    """

    generic_metadata = proto.Field(
        proto.MESSAGE, number=1, message=operation.GenericOperationMetadata,
    )


class UpdateFeaturestoreOperationMetadata(proto.Message):
    r"""Details of operations that perform update Featurestore.
    Attributes:
        generic_metadata (google.cloud.aiplatform_v1beta1.types.GenericOperationMetadata):
            Operation metadata for Featurestore.
    """

    generic_metadata = proto.Field(
        proto.MESSAGE, number=1, message=operation.GenericOperationMetadata,
    )


class ImportFeatureValuesOperationMetadata(proto.Message):
    r"""Details of operations that perform import feature values.
    Attributes:
        generic_metadata (google.cloud.aiplatform_v1beta1.types.GenericOperationMetadata):
            Operation metadata for Featurestore import
            feature values.
        imported_entity_count (int):
            Number of entities that have been imported by
            the operation.
        imported_feature_value_count (int):
            Number of feature values that have been
            imported by the operation.
        invalid_row_count (int):
            The number of rows in input source that weren't imported due
            to either

            -  Not having any featureValues.
            -  Having a null entityId.
            -  Having a null timestamp.
            -  Not being parsable (applicable for CSV sources).
    """

    generic_metadata = proto.Field(
        proto.MESSAGE, number=1, message=operation.GenericOperationMetadata,
    )
    imported_entity_count = proto.Field(proto.INT64, number=2,)
    imported_feature_value_count = proto.Field(proto.INT64, number=3,)
    invalid_row_count = proto.Field(proto.INT64, number=6,)


class ExportFeatureValuesOperationMetadata(proto.Message):
    r"""Details of operations that exports Features values.
    Attributes:
        generic_metadata (google.cloud.aiplatform_v1beta1.types.GenericOperationMetadata):
            Operation metadata for Featurestore export
            Feature values.
    """

    generic_metadata = proto.Field(
        proto.MESSAGE, number=1, message=operation.GenericOperationMetadata,
    )


class BatchReadFeatureValuesOperationMetadata(proto.Message):
    r"""Details of operations that batch reads Feature values.
    Attributes:
        generic_metadata (google.cloud.aiplatform_v1beta1.types.GenericOperationMetadata):
            Operation metadata for Featurestore batch
            read Features values.
    """

    generic_metadata = proto.Field(
        proto.MESSAGE, number=1, message=operation.GenericOperationMetadata,
    )


class CreateEntityTypeOperationMetadata(proto.Message):
    r"""Details of operations that perform create EntityType.
    Attributes:
        generic_metadata (google.cloud.aiplatform_v1beta1.types.GenericOperationMetadata):
            Operation metadata for EntityType.
    """

    generic_metadata = proto.Field(
        proto.MESSAGE, number=1, message=operation.GenericOperationMetadata,
    )


class CreateFeatureOperationMetadata(proto.Message):
    r"""Details of operations that perform create Feature.
    Attributes:
        generic_metadata (google.cloud.aiplatform_v1beta1.types.GenericOperationMetadata):
            Operation metadata for Feature.
    """

    generic_metadata = proto.Field(
        proto.MESSAGE, number=1, message=operation.GenericOperationMetadata,
    )


class BatchCreateFeaturesOperationMetadata(proto.Message):
    r"""Details of operations that perform batch create Features.
    Attributes:
        generic_metadata (google.cloud.aiplatform_v1beta1.types.GenericOperationMetadata):
            Operation metadata for Feature.
    """

    generic_metadata = proto.Field(
        proto.MESSAGE, number=1, message=operation.GenericOperationMetadata,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
