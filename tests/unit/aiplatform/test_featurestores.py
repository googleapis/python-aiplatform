# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
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

import copy
import pytest
import datetime
import pandas as pd
import uuid

from unittest import mock
from importlib import reload
from unittest.mock import MagicMock, patch

from google.api_core import operation
from google.protobuf import field_mask_pb2, timestamp_pb2

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils

from google.cloud.aiplatform.utils import featurestore_utils
from google.cloud.aiplatform_v1.services.featurestore_service import (
    client as featurestore_service_client,
)
from google.cloud.aiplatform_v1.services.featurestore_online_serving_service import (
    client as featurestore_online_serving_service_client,
)
from google.cloud.aiplatform_v1.types import (
    encryption_spec as gca_encryption_spec,
    entity_type as gca_entity_type,
    feature as gca_feature,
    feature_selector as gca_feature_selector,
    featurestore as gca_featurestore,
    featurestore_service as gca_featurestore_service,
    featurestore_online_service as gca_featurestore_online_service,
    io as gca_io,
    types as gca_types,
)

from google.cloud import bigquery
from google.cloud import bigquery_storage

from google.cloud.bigquery_storage_v1.types import stream as gcbqs_stream

# project
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"

_TEST_FEATURE_TIME_DATETIME = datetime.datetime(
    year=2022, month=1, day=1, hour=11, minute=59, second=59
)

# featurestore
_TEST_FEATURESTORE_ID = "featurestore_id"
_TEST_FEATURESTORE_NAME = f"{_TEST_PARENT}/featurestores/{_TEST_FEATURESTORE_ID}"
_TEST_FEATURESTORE_INVALID = f"{_TEST_PARENT}/featurestore/{_TEST_FEATURESTORE_ID}"

# featurestore online
_TEST_ONLINE_SERVING_CONFIG = 1
_TEST_ONLINE_SERVING_CONFIG_UPDATE = 2

# entity_type
_TEST_ENTITY_TYPE_ID = "entity_type_id"
_TEST_ENTITY_TYPE_NAME = f"{_TEST_FEATURESTORE_NAME}/entityTypes/{_TEST_ENTITY_TYPE_ID}"
_TEST_ENTITY_TYPE_INVALID = (
    f"{_TEST_FEATURESTORE_NAME}/entityType/{_TEST_ENTITY_TYPE_ID}"
)

# feature
_TEST_FEATURE_ID = "feature_id"
_TEST_FEATURE_NAME = f"{_TEST_ENTITY_TYPE_NAME}/features/{_TEST_FEATURE_ID}"
_TEST_FEATURE_INVALID = f"{_TEST_ENTITY_TYPE_NAME}/feature/{_TEST_FEATURE_ID}"
_TEST_FEATURE_VALUE_TYPE_STR = "INT64"
_TEST_FEATURE_VALUE = 99
_TEST_FEATURE_VALUE_TYPE_ENUM = 9
_TEST_FEATURE_ID_INVALID = "1feature_id"

_TEST_BOOL_TYPE = gca_feature.Feature.ValueType.BOOL
_TEST_BOOL_ARR_TYPE = gca_feature.Feature.ValueType.BOOL_ARRAY
_TEST_DOUBLE_TYPE = gca_feature.Feature.ValueType.DOUBLE
_TEST_DOUBLE_ARR_TYPE = gca_feature.Feature.ValueType.DOUBLE_ARRAY
_TEST_INT_TYPE = gca_feature.Feature.ValueType.INT64
_TEST_INT_ARR_TYPE = gca_feature.Feature.ValueType.INT64_ARRAY
_TEST_STR_TYPE = gca_feature.Feature.ValueType.STRING
_TEST_STR_ARR_TYPE = gca_feature.Feature.ValueType.STRING_ARRAY
_TEST_BYTES_TYPE = gca_feature.Feature.ValueType.BYTES

_FEATURE_VALUE_TYPE_KEYS = {
    _TEST_BOOL_TYPE: "bool_value",
    _TEST_BOOL_ARR_TYPE: "bool_array_value",
    _TEST_DOUBLE_TYPE: "double_value",
    _TEST_DOUBLE_ARR_TYPE: "double_array_value",
    _TEST_INT_TYPE: "int64_value",
    _TEST_INT_ARR_TYPE: "int64_array_value",
    _TEST_STR_TYPE: "string_value",
    _TEST_STR_ARR_TYPE: "string_array_value",
    _TEST_BYTES_TYPE: "bytes_value",
}

_TEST_FEATURE_VALUE_TYPE = _TEST_INT_TYPE

_ARRAY_FEATURE_VALUE_TYPE_TO_GCA_TYPE_MAP = {
    _TEST_BOOL_ARR_TYPE: gca_types.BoolArray,
    _TEST_DOUBLE_ARR_TYPE: gca_types.DoubleArray,
    _TEST_INT_ARR_TYPE: gca_types.Int64Array,
    _TEST_STR_ARR_TYPE: gca_types.StringArray,
}

_TEST_BOOL_COL = "bool_col"
_TEST_BOOL_ARR_COL = "bool_array_col"
_TEST_DOUBLE_COL = "double_col"
_TEST_DOUBLE_ARR_COL = "double_array_col"
_TEST_INT_COL = "int64_col"
_TEST_INT_ARR_COL = "int64_array_col"
_TEST_STR_COL = "string_col"
_TEST_STR_ARR_COL = "string_array_col"
_TEST_BYTES_COL = "bytes_col"

_TEST_FEATURE_IDS_FOR_DF_CONSTRUCTION = [
    _TEST_BOOL_COL,
    _TEST_BOOL_ARR_COL,
    _TEST_DOUBLE_COL,
    _TEST_DOUBLE_ARR_COL,
    _TEST_INT_COL,
    _TEST_INT_ARR_COL,
    _TEST_STR_COL,
    _TEST_STR_ARR_COL,
    _TEST_BYTES_COL,
]

_TEST_FEATURE_VALUE_TYPES_FOR_DF_CONSTRUCTION = [
    _TEST_BOOL_TYPE,
    _TEST_BOOL_ARR_TYPE,
    _TEST_DOUBLE_TYPE,
    _TEST_DOUBLE_ARR_TYPE,
    _TEST_INT_TYPE,
    _TEST_INT_ARR_TYPE,
    _TEST_STR_TYPE,
    _TEST_STR_ARR_TYPE,
    _TEST_BYTES_TYPE,
]

# misc
_TEST_DESCRIPTION = "my description"
_TEST_LABELS = {"my_key": "my_value"}
_TEST_DESCRIPTION_UPDATE = "my description update"
_TEST_LABELS_UPDATE = {"my_key_update": "my_value_update"}

# request_metadata
_TEST_REQUEST_METADATA = ()

# CMEK encryption
_TEST_ENCRYPTION_KEY_NAME = "key_1234"
_TEST_ENCRYPTION_SPEC = gca_encryption_spec.EncryptionSpec(
    kms_key_name=_TEST_ENCRYPTION_KEY_NAME
)

# Lists
_TEST_FEATURESTORE_LIST = [
    gca_featurestore.Featurestore(
        name=_TEST_FEATURESTORE_NAME,
        online_serving_config=gca_featurestore.Featurestore.OnlineServingConfig(
            fixed_node_count=_TEST_ONLINE_SERVING_CONFIG
        ),
        encryption_spec=_TEST_ENCRYPTION_SPEC,
    ),
    gca_featurestore.Featurestore(
        name=_TEST_FEATURESTORE_NAME,
        online_serving_config=gca_featurestore.Featurestore.OnlineServingConfig(
            fixed_node_count=_TEST_ONLINE_SERVING_CONFIG
        ),
    ),
    gca_featurestore.Featurestore(
        name=_TEST_FEATURESTORE_NAME,
        online_serving_config=gca_featurestore.Featurestore.OnlineServingConfig(
            fixed_node_count=_TEST_ONLINE_SERVING_CONFIG
        ),
        encryption_spec=_TEST_ENCRYPTION_SPEC,
    ),
]

_TEST_ENTITY_TYPE_LIST = [
    gca_entity_type.EntityType(name=_TEST_ENTITY_TYPE_NAME,),
    gca_entity_type.EntityType(name=_TEST_ENTITY_TYPE_NAME,),
    gca_entity_type.EntityType(name=_TEST_ENTITY_TYPE_NAME,),
]

_TEST_FEATURE_LIST = [
    gca_feature.Feature(name=_TEST_FEATURE_NAME,),
    gca_feature.Feature(name=_TEST_FEATURE_NAME,),
    gca_feature.Feature(name=_TEST_FEATURE_NAME,),
]

_TEST_FEATURE_CONFIGS = {
    "my_feature_id_1": {"value_type": _TEST_FEATURE_VALUE_TYPE_STR},
}

_TEST_IMPORTING_FEATURE_IDS = ["my_feature_id_1"]

_TEST_IMPORTING_FEATURE_SOURCE_FIELDS = {
    "my_feature_id_1": "my_feature_id_1_source_field",
}

_TEST_SERVING_FEATURE_IDS = {
    "my_entity_type_id_1": ["my_feature_id_1_1", "my_feature_id_1_2"],
    "my_entity_type_id_2": ["my_feature_id_2_1", "my_feature_id_2_2"],
}

_TEST_FEATURE_TIME_FIELD = "feature_time_field"
_TEST_FEATURE_TIME = datetime.datetime.now()

_TEST_BQ_SOURCE_URI = "bq://project.dataset.table_name"
_TEST_GCS_AVRO_SOURCE_URIS = [
    "gs://my_bucket/my_file_1.avro",
]
_TEST_GCS_CSV_SOURCE_URI = "gs://my_bucket/my_file_1.csv"
_TEST_GCS_CSV_SOURCE_URIS = [
    "gs://my_bucket/my_file_1.csv",
]
_TEST_GCS_SOURCE_TYPE_CSV = "csv"
_TEST_GCS_SOURCE_TYPE_AVRO = "avro"
_TEST_GCS_SOURCE_TYPE_INVALID = "json"

_TEST_BQ_DESTINATION_URI = "bq://project.dataset.table_name"
_TEST_GCS_OUTPUT_URI_PREFIX = "gs://my_bucket/path/to_prefix"

_TEST_GCS_DESTINATION_TYPE_CSV = "csv"
_TEST_GCS_DESTINATION_TYPE_TFRECORD = "tfrecord"
_TEST_GCS_DESTINATION_TYPE_INVALID = "json"

_TEST_BQ_SOURCE = gca_io.BigQuerySource(input_uri=_TEST_BQ_SOURCE_URI)
_TEST_AVRO_SOURCE = gca_io.AvroSource(
    gcs_source=gca_io.GcsSource(uris=_TEST_GCS_AVRO_SOURCE_URIS)
)
_TEST_CSV_SOURCE = gca_io.CsvSource(
    gcs_source=gca_io.GcsSource(uris=_TEST_GCS_CSV_SOURCE_URIS)
)

_TEST_BQ_DESTINATION = gca_io.BigQueryDestination(output_uri=_TEST_BQ_DESTINATION_URI)
_TEST_CSV_DESTINATION = gca_io.CsvDestination(
    gcs_destination=gca_io.GcsDestination(output_uri_prefix=_TEST_GCS_OUTPUT_URI_PREFIX)
)
_TEST_TFRECORD_DESTINATION = gca_io.TFRecordDestination(
    gcs_destination=gca_io.GcsDestination(output_uri_prefix=_TEST_GCS_OUTPUT_URI_PREFIX)
)

_TEST_READ_ENTITY_ID = "entity_id_1"
_TEST_READ_ENTITY_IDS = ["entity_id_1"]

_TEST_BASE_HEADER_PROTO = (
    gca_featurestore_online_service.ReadFeatureValuesResponse.Header()
)
_TEST_BASE_ENTITY_VIEW_PROTO = (
    gca_featurestore_online_service.ReadFeatureValuesResponse.EntityView()
)
_TEST_BASE_DATA_PROTO = (
    gca_featurestore_online_service.ReadFeatureValuesResponse.EntityView.Data()
)


def _get_entity_type_spec_proto_with_feature_ids(
    entity_type_id, feature_ids, feature_destination_fields=None
):
    feature_destination_fields = feature_destination_fields or {}
    entity_type_spec_proto = gca_featurestore_service.BatchReadFeatureValuesRequest.EntityTypeSpec(
        entity_type_id=entity_type_id,
        feature_selector=gca_feature_selector.FeatureSelector(
            id_matcher=gca_feature_selector.IdMatcher(ids=feature_ids)
        ),
        settings=[
            gca_featurestore_service.DestinationFeatureSetting(
                feature_id=feature_id, destination_field=feature_destination_field
            )
            for feature_id, feature_destination_field in feature_destination_fields.items()
        ]
        or None,
    )
    return entity_type_spec_proto


def _get_header_proto(feature_ids):
    header_proto = copy.deepcopy(_TEST_BASE_HEADER_PROTO)
    header_proto.feature_descriptors = [
        gca_featurestore_online_service.ReadFeatureValuesResponse.FeatureDescriptor(
            id=feature_id
        )
        for feature_id in feature_ids
    ]
    return header_proto


def _get_data_proto(feature_value_type, feature_value):
    data_proto = copy.deepcopy(_TEST_BASE_DATA_PROTO)
    if feature_value is not None:
        if feature_value_type in _ARRAY_FEATURE_VALUE_TYPE_TO_GCA_TYPE_MAP:
            array_proto = _ARRAY_FEATURE_VALUE_TYPE_TO_GCA_TYPE_MAP[
                feature_value_type
            ]()
            array_proto.values = feature_value
            feature_value = array_proto
        data_proto.value = gca_featurestore_online_service.FeatureValue(
            {_FEATURE_VALUE_TYPE_KEYS[feature_value_type]: feature_value}
        )
    return data_proto


def _get_entity_view_proto(entity_id, feature_value_types, feature_values):
    entity_view_proto = copy.deepcopy(_TEST_BASE_ENTITY_VIEW_PROTO)
    entity_view_proto.entity_id = entity_id
    entity_view_data = []
    for feature_value_type, feature_value in zip(feature_value_types, feature_values):
        data = _get_data_proto(feature_value_type, feature_value)
        entity_view_data.append(data)
    entity_view_proto.data = entity_view_data
    return entity_view_proto


def uuid_mock():
    return uuid.UUID(int=1)


# All BigQuery Mocks
@pytest.fixture
def bq_client_mock():
    mock = MagicMock(bigquery.client.Client)
    yield mock


@pytest.fixture
def bq_dataset_mock():
    mock = MagicMock(bigquery.dataset.Dataset)
    yield mock


@pytest.fixture
def bq_init_client_mock(bq_client_mock):
    with patch.object(bigquery, "Client") as bq_init_client_mock:
        bq_init_client_mock.return_value = bq_client_mock
        yield bq_init_client_mock


@pytest.fixture
def bq_init_dataset_mock(bq_dataset_mock):
    with patch.object(bigquery, "Dataset") as bq_init_dataset_mock:
        bq_init_dataset_mock.return_value = bq_dataset_mock
        yield bq_init_dataset_mock


@pytest.fixture
def bq_create_dataset_mock(bq_init_client_mock):
    with patch.object(bigquery.Client, "create_dataset") as bq_create_dataset_mock:
        yield bq_create_dataset_mock


@pytest.fixture
def bq_load_table_from_dataframe_mock(bq_init_client_mock):
    with patch.object(
        bigquery.Client, "load_table_from_dataframe"
    ) as bq_load_table_from_dataframe_mock:
        yield bq_load_table_from_dataframe_mock


@pytest.fixture
def bq_delete_dataset_mock(bq_init_client_mock):
    with patch.object(bigquery.Client, "delete_dataset") as bq_delete_dataset_mock:
        yield bq_delete_dataset_mock


@pytest.fixture
def bqs_client_mock():
    mock = MagicMock(bigquery_storage.BigQueryReadClient)
    yield mock


@pytest.fixture
def bqs_init_client_mock(bqs_client_mock):
    with patch.object(bigquery_storage, "BigQueryReadClient") as bqs_init_client_mock:
        bqs_init_client_mock.return_value = bqs_client_mock
        yield bqs_init_client_mock


@pytest.fixture
def bqs_create_read_session(bqs_init_client_mock):
    with patch.object(
        bigquery_storage.BigQueryReadClient, "create_read_session"
    ) as bqs_create_read_session:
        read_session_proto = gcbqs_stream.ReadSession()
        read_session_proto.streams = [gcbqs_stream.ReadStream()]
        bqs_create_read_session.return_value = read_session_proto
        yield bqs_create_read_session


# All Featurestore Mocks
@pytest.fixture
def get_featurestore_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "get_featurestore"
    ) as get_featurestore_mock:
        get_featurestore_mock.return_value = gca_featurestore.Featurestore(
            name=_TEST_FEATURESTORE_NAME,
            online_serving_config=gca_featurestore.Featurestore.OnlineServingConfig(
                fixed_node_count=_TEST_ONLINE_SERVING_CONFIG
            ),
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        yield get_featurestore_mock


@pytest.fixture
def update_featurestore_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "update_featurestore"
    ) as update_featurestore_mock:
        update_featurestore_lro_mock = mock.Mock(operation.Operation)
        update_featurestore_mock.return_value = update_featurestore_lro_mock
        yield update_featurestore_mock


@pytest.fixture
def list_featurestores_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "list_featurestores"
    ) as list_featurestores_mock:
        list_featurestores_mock.return_value = _TEST_FEATURESTORE_LIST
        yield list_featurestores_mock


@pytest.fixture
def delete_featurestore_mock():
    with mock.patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "delete_featurestore"
    ) as delete_featurestore_mock:
        delete_featurestore_lro_mock = mock.Mock(operation.Operation)
        delete_featurestore_mock.return_value = delete_featurestore_lro_mock
        yield delete_featurestore_mock


@pytest.fixture
def search_features_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "search_features"
    ) as search_features_mock:
        search_features_mock.return_value = _TEST_FEATURE_LIST
        yield search_features_mock


@pytest.fixture
def create_featurestore_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "create_featurestore"
    ) as create_featurestore_mock:
        create_featurestore_lro_mock = mock.Mock(operation.Operation)
        create_featurestore_lro_mock.result.return_value = gca_featurestore.Featurestore(
            name=_TEST_FEATURESTORE_NAME,
            online_serving_config=gca_featurestore.Featurestore.OnlineServingConfig(
                fixed_node_count=_TEST_ONLINE_SERVING_CONFIG
            ),
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        create_featurestore_mock.return_value = create_featurestore_lro_mock
        yield create_featurestore_mock


@pytest.fixture
def batch_read_feature_values_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient,
        "batch_read_feature_values",
    ) as batch_read_feature_values_mock:
        batch_read_feature_values_lro_mock = mock.Mock(operation.Operation)
        batch_read_feature_values_mock.return_value = batch_read_feature_values_lro_mock
        yield batch_read_feature_values_mock


# ALL EntityType Mocks
@pytest.fixture
def get_entity_type_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "get_entity_type"
    ) as get_entity_type_mock:
        get_entity_type_mock.return_value = gca_entity_type.EntityType(
            name=_TEST_ENTITY_TYPE_NAME,
        )
        yield get_entity_type_mock


@pytest.fixture
def update_entity_type_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "update_entity_type"
    ) as update_entity_type_mock:
        update_entity_type_lro_mock = mock.Mock(operation.Operation)
        update_entity_type_mock.return_value = update_entity_type_lro_mock
        yield update_entity_type_mock


@pytest.fixture
def list_entity_types_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "list_entity_types"
    ) as list_entity_types_mock:
        list_entity_types_mock.return_value = _TEST_ENTITY_TYPE_LIST
        yield list_entity_types_mock


@pytest.fixture
def delete_entity_type_mock():
    with mock.patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "delete_entity_type"
    ) as delete_entity_type_mock:
        delete_entity_type_lro_mock = mock.Mock(operation.Operation)
        delete_entity_type_mock.return_value = delete_entity_type_lro_mock
        yield delete_entity_type_mock


@pytest.fixture
def create_entity_type_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "create_entity_type"
    ) as create_entity_type_mock:
        create_entity_type_lro_mock = mock.Mock(operation.Operation)
        create_entity_type_lro_mock.result.return_value = gca_entity_type.EntityType(
            name=_TEST_ENTITY_TYPE_NAME
        )
        create_entity_type_mock.return_value = create_entity_type_lro_mock
        yield create_entity_type_mock


@pytest.fixture
def import_feature_values_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "import_feature_values"
    ) as import_feature_values_mock:
        import_feature_values_lro_mock = mock.Mock(operation.Operation)
        import_feature_values_mock.return_value = import_feature_values_lro_mock
        yield import_feature_values_mock


@pytest.fixture
def read_feature_values_mock():
    with patch.object(
        featurestore_online_serving_service_client.FeaturestoreOnlineServingServiceClient,
        "read_feature_values",
    ) as read_feature_values_mock:
        read_feature_values_mock.return_value = gca_featurestore_online_service.ReadFeatureValuesResponse(
            header=_get_header_proto(feature_ids=[_TEST_FEATURE_ID]),
            entity_view=_get_entity_view_proto(
                entity_id=_TEST_READ_ENTITY_ID,
                feature_value_types=[_TEST_FEATURE_VALUE_TYPE],
                feature_values=[_TEST_FEATURE_VALUE],
            ),
        )
        yield read_feature_values_mock


@pytest.fixture
def streaming_read_feature_values_mock():
    with patch.object(
        featurestore_online_serving_service_client.FeaturestoreOnlineServingServiceClient,
        "streaming_read_feature_values",
    ) as streaming_read_feature_values_mock:
        streaming_read_feature_values_mock.return_value = [
            gca_featurestore_online_service.ReadFeatureValuesResponse(
                header=_get_header_proto(feature_ids=[_TEST_FEATURE_ID])
            ),
            gca_featurestore_online_service.ReadFeatureValuesResponse(
                entity_view=_get_entity_view_proto(
                    entity_id=_TEST_READ_ENTITY_ID,
                    feature_value_types=[_TEST_FEATURE_VALUE_TYPE],
                    feature_values=[_TEST_FEATURE_VALUE],
                ),
            ),
        ]
        yield streaming_read_feature_values_mock


# ALL Feature Mocks
@pytest.fixture
def get_feature_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "get_feature"
    ) as get_feature_mock:
        get_feature_mock.return_value = gca_feature.Feature(
            name=_TEST_FEATURE_NAME, value_type=_TEST_FEATURE_VALUE_TYPE
        )
        yield get_feature_mock


@pytest.fixture
def update_feature_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "update_feature"
    ) as update_feature_mock:
        update_feature_lro_mock = mock.Mock(operation.Operation)
        update_feature_mock.return_value = update_feature_lro_mock
        yield update_feature_mock


@pytest.fixture
def list_features_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "list_features"
    ) as list_features_mock:
        list_features_mock.return_value = _TEST_FEATURE_LIST
        yield list_features_mock


@pytest.fixture
def delete_feature_mock():
    with mock.patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "delete_feature"
    ) as delete_feature_mock:
        delete_feature_lro_mock = mock.Mock(operation.Operation)
        delete_feature_mock.return_value = delete_feature_lro_mock
        yield delete_feature_mock


@pytest.fixture
def create_feature_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "create_feature"
    ) as create_feature_mock:
        create_feature_lro_mock = mock.Mock(operation.Operation)
        create_feature_lro_mock.result.return_value = gca_feature.Feature(
            name=_TEST_FEATURE_NAME, value_type=_TEST_FEATURE_VALUE_TYPE_ENUM,
        )
        create_feature_mock.return_value = create_feature_lro_mock
        yield create_feature_mock


@pytest.fixture
def batch_create_features_mock():
    with patch.object(
        featurestore_service_client.FeaturestoreServiceClient, "batch_create_features"
    ) as batch_create_features_mock:
        batch_create_features_lro_mock = mock.Mock(operation.Operation)
        batch_create_features_mock.return_value = batch_create_features_lro_mock
        yield batch_create_features_mock


class TestFeaturestoreUtils:
    @pytest.mark.parametrize(
        "resource_id", ["resource_id", "resource_id12345", "_resource_id", "_123456"],
    )
    def test_validate_resource_id(self, resource_id: str):
        featurestore_utils.validate_id(resource_id)

    @pytest.mark.parametrize(
        "resource_id",
        [
            "12345resource_id",
            "resource_id/1234",
            "_resource_id/1234",
            "resource-id-1234",
            "123456",
            "c" * 61,
        ],
    )
    def test_validate_invalid_resource_id(self, resource_id: str):
        with pytest.raises(ValueError):
            featurestore_utils.validate_id(resource_id)

    @pytest.mark.parametrize(
        "feature_id", ["resource_id", "resource_id12345", "_resource_id", "_123456"],
    )
    def test_validate_feature_id(self, feature_id: str):
        assert featurestore_utils.validate_feature_id(feature_id=feature_id) is None

    @pytest.mark.parametrize(
        "feature_id",
        [
            "12345resource_id",
            "resource_id/1234",
            "_resource_id/1234",
            "resource-id-1234",
            "123456",
            "c" * 61,
            "entity_id",
            "Entity_ID",
            "feature_timestamp",
            "Feature_Timestamp",
            "arrival_timestamp",
            "Arrival_Timestamp",
        ],
    )
    def test_validate_feature_id_with_raise(self, feature_id: str):
        with pytest.raises(ValueError):
            featurestore_utils.validate_feature_id(feature_id=feature_id)

    @pytest.mark.parametrize(
        "value_type",
        [
            "BOOL",
            "BOOL_ARRAY",
            "DOUBLE",
            "DOUBLE_ARRAY",
            "INT64",
            "INT64_ARRAY",
            "STRING",
            "STRING_ARRAY",
            "BYTES",
        ],
    )
    def test_validate_value_type(self, value_type: str):
        assert featurestore_utils.validate_value_type(value_type=value_type) is None

    @pytest.mark.parametrize(
        "value_type",
        [
            "INT",
            "INT_array",
            "STR",
            "double",
            "bool",
            "array",
            "INT32",
            "VALUE_TYPE_UNSPECIFIED",
        ],
    )
    def test_validate_value_type_with_raise(self, value_type: str):
        with pytest.raises(ValueError):
            featurestore_utils.validate_value_type(value_type=value_type)


class Test_FeatureConfig:
    def test_feature_config_return_create_feature_request(self):

        featureConfig = featurestore_utils._FeatureConfig(
            feature_id=_TEST_FEATURE_ID,
            value_type=_TEST_FEATURE_VALUE_TYPE_STR,
            description=_TEST_DESCRIPTION,
            labels=_TEST_LABELS,
        )

        gapic_feature = gca_feature.Feature(
            description=_TEST_DESCRIPTION,
            value_type=_TEST_FEATURE_VALUE_TYPE_ENUM,
            labels=_TEST_LABELS,
        )

        expected_request = gca_featurestore_service.CreateFeatureRequest(
            feature=gapic_feature, feature_id=_TEST_FEATURE_ID,
        )

        assert featureConfig.get_create_feature_request() == expected_request

    def test_feature_config_create_feature_request_raises_invalid_feature_id(self):
        featureConfig = featurestore_utils._FeatureConfig(
            feature_id=_TEST_FEATURE_ID_INVALID,
            value_type=_TEST_FEATURE_VALUE_TYPE_STR,
            description=_TEST_DESCRIPTION,
            labels=_TEST_LABELS,
        )
        with pytest.raises(ValueError):
            featureConfig.get_create_feature_request()

    @pytest.mark.parametrize("value_type", ["INT", "VALUE_TYPE_UNSPECIFIED"])
    def test_feature_config_create_feature_request_raises_invalid_value_type(
        self, value_type
    ):
        featureConfig = featurestore_utils._FeatureConfig(
            feature_id=_TEST_FEATURE_ID,
            value_type=value_type,
            description=_TEST_DESCRIPTION,
            labels=_TEST_LABELS,
        )
        with pytest.raises(ValueError):
            featureConfig.get_create_feature_request()


class TestFeaturestore:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize(
        "featurestore_name", [_TEST_FEATURESTORE_ID, _TEST_FEATURESTORE_NAME]
    )
    def test_init_featurestore(self, featurestore_name, get_featurestore_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_featurestore = aiplatform.Featurestore(featurestore_name=featurestore_name)

        get_featurestore_mock.assert_called_once_with(
            name=my_featurestore.resource_name, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures("get_featurestore_mock")
    def test_get_entity_type(self, get_entity_type_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_featurestore = aiplatform.Featurestore(
            featurestore_name=_TEST_FEATURESTORE_ID
        )
        my_entity_type = my_featurestore.get_entity_type(
            entity_type_id=_TEST_ENTITY_TYPE_ID
        )

        get_entity_type_mock.assert_called_once_with(
            name=_TEST_ENTITY_TYPE_NAME, retry=base._DEFAULT_RETRY
        )
        assert type(my_entity_type) == aiplatform.EntityType

    @pytest.mark.usefixtures("get_featurestore_mock")
    def test_update_featurestore(self, update_featurestore_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_featurestore = aiplatform.Featurestore(
            featurestore_name=_TEST_FEATURESTORE_ID
        )
        my_featurestore.update(labels=_TEST_LABELS_UPDATE)

        expected_featurestore = gca_featurestore.Featurestore(
            name=_TEST_FEATURESTORE_NAME,
            labels=_TEST_LABELS_UPDATE,
            online_serving_config=gca_featurestore.Featurestore.OnlineServingConfig(),
        )
        update_featurestore_mock.assert_called_once_with(
            featurestore=expected_featurestore,
            update_mask=field_mask_pb2.FieldMask(paths=["labels"]),
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_featurestore_mock")
    def test_update_featurestore_online(self, update_featurestore_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_featurestore = aiplatform.Featurestore(
            featurestore_name=_TEST_FEATURESTORE_ID
        )
        my_featurestore.update_online_store(
            fixed_node_count=_TEST_ONLINE_SERVING_CONFIG_UPDATE
        )

        expected_featurestore = gca_featurestore.Featurestore(
            name=_TEST_FEATURESTORE_NAME,
            online_serving_config=gca_featurestore.Featurestore.OnlineServingConfig(
                fixed_node_count=_TEST_ONLINE_SERVING_CONFIG_UPDATE
            ),
        )
        update_featurestore_mock.assert_called_once_with(
            featurestore=expected_featurestore,
            update_mask=field_mask_pb2.FieldMask(
                paths=["online_serving_config.fixed_node_count"]
            ),
            metadata=_TEST_REQUEST_METADATA,
        )

    def test_list_featurestores(self, list_featurestores_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_featurestore_list = aiplatform.Featurestore.list()

        list_featurestores_mock.assert_called_once_with(
            request={"parent": _TEST_PARENT, "filter": None}
        )
        assert len(my_featurestore_list) == len(_TEST_FEATURESTORE_LIST)
        for my_featurestore in my_featurestore_list:
            assert type(my_featurestore) == aiplatform.Featurestore

    @pytest.mark.parametrize(
        "force, sync",
        [
            (None, True),
            (True, True),
            (False, True),
            (None, False),
            (True, False),
            (False, False),
        ],
    )
    @pytest.mark.usefixtures("get_featurestore_mock")
    def test_delete_featurestore(self, delete_featurestore_mock, force, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_featurestore = aiplatform.Featurestore(
            featurestore_name=_TEST_FEATURESTORE_ID
        )
        my_featurestore.delete(sync=sync, force=force)

        if not sync:
            my_featurestore.wait()

        delete_featurestore_mock.assert_called_once_with(
            name=my_featurestore.resource_name, force=force,
        )

    @pytest.mark.usefixtures("get_featurestore_mock")
    def test_list_entity_types(self, list_entity_types_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_featurestore = aiplatform.Featurestore(
            featurestore_name=_TEST_FEATURESTORE_ID
        )
        my_entity_type_list = my_featurestore.list_entity_types()

        list_entity_types_mock.assert_called_once_with(
            request={"parent": _TEST_FEATURESTORE_NAME, "filter": None}
        )
        assert len(my_entity_type_list) == len(_TEST_ENTITY_TYPE_LIST)
        for my_entity_type in my_entity_type_list:
            assert type(my_entity_type) == aiplatform.EntityType

    @pytest.mark.parametrize(
        "force, sync",
        [
            (None, True),
            (True, True),
            (False, True),
            (None, False),
            (True, False),
            (False, False),
        ],
    )
    @pytest.mark.usefixtures("get_featurestore_mock", "get_entity_type_mock")
    def test_delete_entity_types(self, delete_entity_type_mock, force, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_featurestore = aiplatform.Featurestore(
            featurestore_name=_TEST_FEATURESTORE_ID
        )
        my_featurestore.delete_entity_types(
            entity_type_ids=[_TEST_ENTITY_TYPE_ID, _TEST_ENTITY_TYPE_ID],
            sync=sync,
            force=force,
        )

        if not sync:
            my_featurestore.wait()

        delete_entity_type_mock.assert_has_calls(
            calls=[
                mock.call(name=_TEST_ENTITY_TYPE_NAME, force=force),
                mock.call(name=_TEST_ENTITY_TYPE_NAME, force=force),
            ],
            any_order=True,
        )

    @pytest.mark.usefixtures("get_featurestore_mock", "get_entity_type_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_entity_type(self, create_entity_type_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_featurestore = aiplatform.Featurestore(
            featurestore_name=_TEST_FEATURESTORE_NAME
        )
        my_entity_type = my_featurestore.create_entity_type(
            entity_type_id=_TEST_ENTITY_TYPE_ID,
            description=_TEST_DESCRIPTION,
            labels=_TEST_LABELS,
            sync=sync,
        )

        if not sync:
            my_entity_type.wait()

        expected_entity_type = gca_entity_type.EntityType(
            labels=_TEST_LABELS, description=_TEST_DESCRIPTION,
        )
        create_entity_type_mock.assert_called_once_with(
            parent=_TEST_FEATURESTORE_NAME,
            entity_type=expected_entity_type,
            entity_type_id=_TEST_ENTITY_TYPE_ID,
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_featurestore_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_featurestore(self, create_featurestore_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_featurestore = aiplatform.Featurestore.create(
            featurestore_id=_TEST_FEATURESTORE_ID,
            online_store_fixed_node_count=_TEST_ONLINE_SERVING_CONFIG,
            labels=_TEST_LABELS,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
        )

        if not sync:
            my_featurestore.wait()

        expected_featurestore = gca_featurestore.Featurestore(
            labels=_TEST_LABELS,
            online_serving_config=gca_featurestore.Featurestore.OnlineServingConfig(
                fixed_node_count=_TEST_ONLINE_SERVING_CONFIG
            ),
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        create_featurestore_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            featurestore=expected_featurestore,
            featurestore_id=_TEST_FEATURESTORE_ID,
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_featurestore_mock")
    @pytest.mark.parametrize(
        "serving_feature_ids, feature_destination_fields, expected_entity_type_specs",
        [
            (
                {
                    "my_entity_type_id_1": ["my_feature_id_1_1", "my_feature_id_1_2"],
                    "my_entity_type_id_2": ["my_feature_id_2_1", "my_feature_id_2_2"],
                },
                None,
                [
                    _get_entity_type_spec_proto_with_feature_ids(
                        entity_type_id="my_entity_type_id_1",
                        feature_ids=["my_feature_id_1_1", "my_feature_id_1_2"],
                    ),
                    _get_entity_type_spec_proto_with_feature_ids(
                        entity_type_id="my_entity_type_id_2",
                        feature_ids=["my_feature_id_2_1", "my_feature_id_2_2"],
                    ),
                ],
            ),
            (
                {
                    "my_entity_type_id_1": ["my_feature_id_1_1", "my_feature_id_1_2"],
                    "my_entity_type_id_2": ["my_feature_id_2_1", "my_feature_id_2_2"],
                },
                {
                    f"{_TEST_FEATURESTORE_NAME}/entityTypes/my_entity_type_id_1/features/my_feature_id_1_1": "my_feature_id_1_1_dest",
                    f"{_TEST_FEATURESTORE_NAME}/entityTypes/my_entity_type_id_1/features/my_feature_id_1_2": "my_feature_id_1_2_dest",
                },
                [
                    _get_entity_type_spec_proto_with_feature_ids(
                        entity_type_id="my_entity_type_id_1",
                        feature_ids=["my_feature_id_1_1", "my_feature_id_1_2"],
                        feature_destination_fields={
                            "my_feature_id_1_1": "my_feature_id_1_1_dest",
                            "my_feature_id_1_2": "my_feature_id_1_2_dest",
                        },
                    ),
                    _get_entity_type_spec_proto_with_feature_ids(
                        entity_type_id="my_entity_type_id_2",
                        feature_ids=["my_feature_id_2_1", "my_feature_id_2_2"],
                    ),
                ],
            ),
            (
                {
                    "my_entity_type_id_1": ["my_feature_id_1_1", "my_feature_id_1_2"],
                    "my_entity_type_id_2": ["my_feature_id_2_1", "my_feature_id_2_2"],
                },
                {
                    f"{_TEST_FEATURESTORE_NAME}/entityTypes/my_entity_type_id_1/features/my_feature_id_1_1": "my_feature_id_1_1_dest",
                    f"{_TEST_FEATURESTORE_NAME}/entityTypes/my_entity_type_id_2/features/my_feature_id_2_1": "my_feature_id_2_1_dest",
                },
                [
                    _get_entity_type_spec_proto_with_feature_ids(
                        entity_type_id="my_entity_type_id_1",
                        feature_ids=["my_feature_id_1_1", "my_feature_id_1_2"],
                        feature_destination_fields={
                            "my_feature_id_1_1": "my_feature_id_1_1_dest"
                        },
                    ),
                    _get_entity_type_spec_proto_with_feature_ids(
                        entity_type_id="my_entity_type_id_2",
                        feature_ids=["my_feature_id_2_1", "my_feature_id_2_2"],
                        feature_destination_fields={
                            "my_feature_id_2_1": "my_feature_id_2_1_dest"
                        },
                    ),
                ],
            ),
        ],
    )
    def test_validate_and_get_batch_read_feature_values_request(
        self,
        serving_feature_ids,
        feature_destination_fields,
        expected_entity_type_specs,
    ):

        aiplatform.init(project=_TEST_PROJECT)
        my_featurestore = aiplatform.Featurestore(
            featurestore_name=_TEST_FEATURESTORE_NAME
        )
        expected_batch_read_feature_values_request = gca_featurestore_service.BatchReadFeatureValuesRequest(
            featurestore=_TEST_FEATURESTORE_NAME,
            destination=gca_featurestore_service.FeatureValueDestination(
                bigquery_destination=_TEST_BQ_DESTINATION,
            ),
            entity_type_specs=expected_entity_type_specs,
            bigquery_read_instances=_TEST_BQ_SOURCE,
        )
        assert (
            expected_batch_read_feature_values_request
            == my_featurestore._validate_and_get_batch_read_feature_values_request(
                featurestore_name=my_featurestore.resource_name,
                serving_feature_ids=serving_feature_ids,
                destination=_TEST_BQ_DESTINATION,
                read_instances=_TEST_BQ_SOURCE,
                feature_destination_fields=feature_destination_fields,
            )
        )

    @pytest.mark.usefixtures("get_featurestore_mock")
    @pytest.mark.parametrize(
        "read_instances_uri, expected_read_instances",
        [
            (_TEST_BQ_SOURCE_URI, _TEST_BQ_SOURCE),
            (_TEST_GCS_CSV_SOURCE_URI, _TEST_CSV_SOURCE),
        ],
    )
    def test_validate_and_get_read_instances(
        self, read_instances_uri, expected_read_instances
    ):
        aiplatform.init(project=_TEST_PROJECT)
        my_featurestore = aiplatform.Featurestore(
            featurestore_name=_TEST_FEATURESTORE_NAME
        )
        assert (
            expected_read_instances
            == my_featurestore._validate_and_get_read_instances(
                read_instances_uri=read_instances_uri
            )
        )

    @pytest.mark.usefixtures("get_featurestore_mock")
    @pytest.mark.parametrize(
        "read_instances_uri",
        [
            "gcs://my_bucket/my_file_1.csv",
            "bigquery://project.dataset.table_name",
            "my_bucket/my_file_1.csv",
        ],
    )
    def test_validate_and_get_read_instances_with_raise(self, read_instances_uri):
        aiplatform.init(project=_TEST_PROJECT)
        my_featurestore = aiplatform.Featurestore(
            featurestore_name=_TEST_FEATURESTORE_NAME
        )
        with pytest.raises(ValueError):
            my_featurestore._validate_and_get_read_instances(
                read_instances_uri=read_instances_uri
            )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_featurestore_mock")
    def test_batch_serve_to_bq(self, batch_read_feature_values_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)
        my_featurestore = aiplatform.Featurestore(
            featurestore_name=_TEST_FEATURESTORE_NAME
        )

        expected_entity_type_specs = [
            _get_entity_type_spec_proto_with_feature_ids(
                entity_type_id="my_entity_type_id_1",
                feature_ids=["my_feature_id_1_1", "my_feature_id_1_2"],
            ),
            _get_entity_type_spec_proto_with_feature_ids(
                entity_type_id="my_entity_type_id_2",
                feature_ids=["my_feature_id_2_1", "my_feature_id_2_2"],
            ),
        ]

        expected_batch_read_feature_values_request = gca_featurestore_service.BatchReadFeatureValuesRequest(
            featurestore=my_featurestore.resource_name,
            destination=gca_featurestore_service.FeatureValueDestination(
                bigquery_destination=_TEST_BQ_DESTINATION,
            ),
            entity_type_specs=expected_entity_type_specs,
            bigquery_read_instances=_TEST_BQ_SOURCE,
        )

        my_featurestore.batch_serve_to_bq(
            bq_destination_output_uri=_TEST_BQ_DESTINATION_URI,
            serving_feature_ids=_TEST_SERVING_FEATURE_IDS,
            read_instances_uri=_TEST_BQ_SOURCE_URI,
            sync=sync,
        )

        if not sync:
            my_featurestore.wait()

        batch_read_feature_values_mock.assert_called_once_with(
            request=expected_batch_read_feature_values_request,
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_featurestore_mock")
    def test_batch_serve_to_gcs(self, batch_read_feature_values_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)
        my_featurestore = aiplatform.Featurestore(
            featurestore_name=_TEST_FEATURESTORE_NAME
        )

        expected_entity_type_specs = [
            _get_entity_type_spec_proto_with_feature_ids(
                entity_type_id="my_entity_type_id_1",
                feature_ids=["my_feature_id_1_1", "my_feature_id_1_2"],
            ),
            _get_entity_type_spec_proto_with_feature_ids(
                entity_type_id="my_entity_type_id_2",
                feature_ids=["my_feature_id_2_1", "my_feature_id_2_2"],
            ),
        ]

        expected_batch_read_feature_values_request = gca_featurestore_service.BatchReadFeatureValuesRequest(
            featurestore=my_featurestore.resource_name,
            destination=gca_featurestore_service.FeatureValueDestination(
                tfrecord_destination=_TEST_TFRECORD_DESTINATION,
            ),
            entity_type_specs=expected_entity_type_specs,
            csv_read_instances=_TEST_CSV_SOURCE,
        )

        my_featurestore.batch_serve_to_gcs(
            gcs_destination_output_uri_prefix=_TEST_GCS_OUTPUT_URI_PREFIX,
            gcs_destination_type=_TEST_GCS_DESTINATION_TYPE_TFRECORD,
            serving_feature_ids=_TEST_SERVING_FEATURE_IDS,
            read_instances_uri=_TEST_GCS_CSV_SOURCE_URI,
            sync=sync,
        )

        if not sync:
            my_featurestore.wait()

        batch_read_feature_values_mock.assert_called_once_with(
            request=expected_batch_read_feature_values_request,
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_featurestore_mock")
    def test_batch_serve_to_gcs_with_invalid_gcs_destination_type(self):

        aiplatform.init(project=_TEST_PROJECT)

        my_featurestore = aiplatform.Featurestore(
            featurestore_name=_TEST_FEATURESTORE_NAME
        )
        with pytest.raises(ValueError):
            my_featurestore.batch_serve_to_gcs(
                gcs_destination_output_uri_prefix=_TEST_GCS_OUTPUT_URI_PREFIX,
                gcs_destination_type=_TEST_GCS_DESTINATION_TYPE_INVALID,
                serving_feature_ids=_TEST_SERVING_FEATURE_IDS,
                read_instances_uri=_TEST_GCS_CSV_SOURCE_URI,
            )

    @pytest.mark.usefixtures(
        "get_featurestore_mock",
        "bq_init_client_mock",
        "bq_init_dataset_mock",
        "bq_create_dataset_mock",
        "bq_load_table_from_dataframe_mock",
        "bq_delete_dataset_mock",
        "bqs_init_client_mock",
        "bqs_create_read_session",
    )
    @patch("uuid.uuid4", uuid_mock)
    def test_batch_serve_to_df(self, batch_read_feature_values_mock):
        aiplatform.init(project=_TEST_PROJECT)
        my_featurestore = aiplatform.Featurestore(
            featurestore_name=_TEST_FEATURESTORE_NAME
        )

        read_instances_df = pd.DataFrame()

        expected_temp_bq_dataset_name = f"temp_{_TEST_FEATURESTORE_ID}_{uuid.uuid4()}".replace(
            "-", "_"
        )
        expecte_temp_bq_dataset_id = f"{initializer.global_config.project}.{expected_temp_bq_dataset_name}"[
            :1024
        ]
        expected_temp_bq_read_instances_table_id = (
            f"{expecte_temp_bq_dataset_id}.read_instances"
        )
        expected_temp_bq_batch_serve_table_id = (
            f"{expecte_temp_bq_dataset_id}.batch_serve"
        )

        expected_entity_type_specs = [
            _get_entity_type_spec_proto_with_feature_ids(
                entity_type_id="my_entity_type_id_1",
                feature_ids=["my_feature_id_1_1", "my_feature_id_1_2"],
            ),
            _get_entity_type_spec_proto_with_feature_ids(
                entity_type_id="my_entity_type_id_2",
                feature_ids=["my_feature_id_2_1", "my_feature_id_2_2"],
            ),
        ]

        expected_batch_read_feature_values_request = gca_featurestore_service.BatchReadFeatureValuesRequest(
            featurestore=my_featurestore.resource_name,
            destination=gca_featurestore_service.FeatureValueDestination(
                bigquery_destination=gca_io.BigQueryDestination(
                    output_uri=f"bq://{expected_temp_bq_batch_serve_table_id}"
                ),
            ),
            entity_type_specs=expected_entity_type_specs,
            bigquery_read_instances=gca_io.BigQuerySource(
                input_uri=f"bq://{expected_temp_bq_read_instances_table_id}"
            ),
        )

        my_featurestore.batch_serve_to_df(
            serving_feature_ids=_TEST_SERVING_FEATURE_IDS,
            read_instances_df=read_instances_df,
        )

        batch_read_feature_values_mock.assert_called_once_with(
            request=expected_batch_read_feature_values_request,
            metadata=_TEST_REQUEST_METADATA,
        )


class TestEntityType:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize(
        "entity_type_name, featurestore_id",
        [
            (_TEST_ENTITY_TYPE_NAME, None),
            (_TEST_ENTITY_TYPE_ID, _TEST_FEATURESTORE_ID),
        ],
    )
    def test_init_entity_type(
        self, entity_type_name, featurestore_id, get_entity_type_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        aiplatform.EntityType(
            entity_type_name=entity_type_name, featurestore_id=featurestore_id
        )

        get_entity_type_mock.assert_called_once_with(
            name=_TEST_ENTITY_TYPE_NAME, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures("get_entity_type_mock")
    def test_get_featurestore(self, get_featurestore_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = aiplatform.EntityType(entity_type_name=_TEST_ENTITY_TYPE_NAME)
        my_featurestore = my_entity_type.get_featurestore()

        get_featurestore_mock.assert_called_once_with(
            name=my_featurestore.resource_name, retry=base._DEFAULT_RETRY
        )
        assert type(my_featurestore) == aiplatform.Featurestore

    @pytest.mark.usefixtures("get_entity_type_mock")
    def test_get_feature(self, get_feature_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = aiplatform.EntityType(entity_type_name=_TEST_ENTITY_TYPE_NAME)
        my_feature = my_entity_type.get_feature(feature_id=_TEST_FEATURE_ID)

        get_feature_mock.assert_called_once_with(
            name=my_feature.resource_name, retry=base._DEFAULT_RETRY
        )
        assert type(my_feature) == aiplatform.Feature

    @pytest.mark.usefixtures("get_entity_type_mock")
    def test_update_entity_type(self, update_entity_type_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = aiplatform.EntityType(entity_type_name=_TEST_ENTITY_TYPE_NAME)
        my_entity_type.update(labels=_TEST_LABELS_UPDATE)

        expected_entity_type = gca_entity_type.EntityType(
            name=_TEST_ENTITY_TYPE_NAME, labels=_TEST_LABELS_UPDATE,
        )
        update_entity_type_mock.assert_called_once_with(
            entity_type=expected_entity_type,
            update_mask=field_mask_pb2.FieldMask(paths=["labels"]),
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.parametrize(
        "featurestore_name", [_TEST_FEATURESTORE_NAME, _TEST_FEATURESTORE_ID]
    )
    def test_list_entity_types(self, featurestore_name, list_entity_types_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type_list = aiplatform.EntityType.list(
            featurestore_name=featurestore_name
        )

        list_entity_types_mock.assert_called_once_with(
            request={"parent": _TEST_FEATURESTORE_NAME, "filter": None}
        )
        assert len(my_entity_type_list) == len(_TEST_ENTITY_TYPE_LIST)
        for my_entity_type in my_entity_type_list:
            assert type(my_entity_type) == aiplatform.EntityType

    @pytest.mark.usefixtures("get_entity_type_mock")
    def test_list_features(self, list_features_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = aiplatform.EntityType(entity_type_name=_TEST_ENTITY_TYPE_NAME)
        my_feature_list = my_entity_type.list_features()

        list_features_mock.assert_called_once_with(
            request={"parent": _TEST_ENTITY_TYPE_NAME, "filter": None}
        )
        assert len(my_feature_list) == len(_TEST_FEATURE_LIST)
        for my_feature in my_feature_list:
            assert type(my_feature) == aiplatform.Feature

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_entity_type_mock", "get_feature_mock")
    def test_delete_features(self, delete_feature_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = aiplatform.EntityType(entity_type_name=_TEST_ENTITY_TYPE_NAME)
        my_entity_type.delete_features(
            feature_ids=[_TEST_FEATURE_ID, _TEST_FEATURE_ID], sync=sync
        )

        if not sync:
            my_entity_type.wait()

        delete_feature_mock.assert_has_calls(
            calls=[
                mock.call(name=_TEST_FEATURE_NAME),
                mock.call(name=_TEST_FEATURE_NAME),
            ],
            any_order=True,
        )

    @pytest.mark.usefixtures("get_entity_type_mock", "get_feature_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_feature(self, create_feature_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = aiplatform.EntityType(entity_type_name=_TEST_ENTITY_TYPE_NAME)
        my_feature = my_entity_type.create_feature(
            feature_id=_TEST_FEATURE_ID,
            value_type=_TEST_FEATURE_VALUE_TYPE_STR,
            description=_TEST_DESCRIPTION,
            labels=_TEST_LABELS,
        )

        if not sync:
            my_feature.wait()

        expected_feature = gca_feature.Feature(
            value_type=_TEST_FEATURE_VALUE_TYPE_ENUM,
            labels=_TEST_LABELS,
            description=_TEST_DESCRIPTION,
        )
        expected_request = gca_featurestore_service.CreateFeatureRequest(
            parent=_TEST_ENTITY_TYPE_NAME,
            feature=expected_feature,
            feature_id=_TEST_FEATURE_ID,
        )

        create_feature_mock.assert_called_once_with(
            request=expected_request, metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_entity_type_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_entity_type(self, create_entity_type_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = aiplatform.EntityType.create(
            entity_type_id=_TEST_ENTITY_TYPE_ID,
            featurestore_name=_TEST_FEATURESTORE_NAME,
            description=_TEST_DESCRIPTION,
            labels=_TEST_LABELS,
        )

        if not sync:
            my_entity_type.wait()

        expected_entity_type = gca_entity_type.EntityType(
            description=_TEST_DESCRIPTION, labels=_TEST_LABELS,
        )
        create_entity_type_mock.assert_called_once_with(
            parent=_TEST_FEATURESTORE_NAME,
            entity_type=expected_entity_type,
            entity_type_id=_TEST_ENTITY_TYPE_ID,
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_entity_type_mock")
    def test_validate_and_get_create_feature_requests(self):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = aiplatform.EntityType(entity_type_name=_TEST_ENTITY_TYPE_NAME)
        create_feature_requests = my_entity_type._validate_and_get_create_feature_requests(
            feature_configs=_TEST_FEATURE_CONFIGS
        )

        expected_requests = [
            gca_featurestore_service.CreateFeatureRequest(
                feature=gca_feature.Feature(value_type=_TEST_FEATURE_VALUE_TYPE_ENUM),
                feature_id="my_feature_id_1",
            ),
        ]
        assert create_feature_requests == expected_requests

    @pytest.mark.usefixtures("get_entity_type_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_batch_create_features(self, batch_create_features_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = aiplatform.EntityType(entity_type_name=_TEST_ENTITY_TYPE_NAME)
        my_entity_type.batch_create_features(feature_configs=_TEST_FEATURE_CONFIGS)

        if not sync:
            my_entity_type.wait()

        expected_requests = [
            gca_featurestore_service.CreateFeatureRequest(
                feature=gca_feature.Feature(value_type=_TEST_FEATURE_VALUE_TYPE_ENUM),
                feature_id="my_feature_id_1",
            ),
        ]

        batch_create_features_mock.assert_called_once_with(
            parent=my_entity_type.resource_name,
            requests=expected_requests,
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_entity_type_mock")
    def test_validate_and_get_import_feature_values_request_with_source_fields(self):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = aiplatform.EntityType(entity_type_name=_TEST_ENTITY_TYPE_NAME)
        true_import_feature_values_request = gca_featurestore_service.ImportFeatureValuesRequest(
            bigquery_source=_TEST_BQ_SOURCE,
            feature_time_field=_TEST_FEATURE_TIME_FIELD,
            entity_type=_TEST_ENTITY_TYPE_NAME,
            feature_specs=[
                gca_featurestore_service.ImportFeatureValuesRequest.FeatureSpec(
                    id="my_feature_id_1", source_field="my_feature_id_1_source_field"
                ),
            ],
        )
        assert (
            true_import_feature_values_request
            == my_entity_type._validate_and_get_import_feature_values_request(
                entity_type_name=my_entity_type.resource_name,
                feature_ids=_TEST_IMPORTING_FEATURE_IDS,
                feature_time=_TEST_FEATURE_TIME_FIELD,
                data_source=_TEST_BQ_SOURCE,
                feature_source_fields=_TEST_IMPORTING_FEATURE_SOURCE_FIELDS,
            )
        )

    @pytest.mark.usefixtures("get_entity_type_mock")
    def test_validate_and_get_import_feature_values_request_without_source_fields(self):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = aiplatform.EntityType(entity_type_name=_TEST_ENTITY_TYPE_NAME)

        true_import_feature_values_request = gca_featurestore_service.ImportFeatureValuesRequest(
            entity_type=_TEST_ENTITY_TYPE_NAME,
            feature_specs=[
                gca_featurestore_service.ImportFeatureValuesRequest.FeatureSpec(
                    id="my_feature_id_1"
                ),
            ],
            csv_source=_TEST_CSV_SOURCE,
            feature_time=utils.get_timestamp_proto(_TEST_FEATURE_TIME),
        )
        assert (
            true_import_feature_values_request
            == my_entity_type._validate_and_get_import_feature_values_request(
                entity_type_name=my_entity_type.resource_name,
                feature_ids=_TEST_IMPORTING_FEATURE_IDS,
                feature_time=_TEST_FEATURE_TIME,
                data_source=_TEST_CSV_SOURCE,
            )
        )

    @pytest.mark.usefixtures("get_entity_type_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_ingest_from_bq(self, import_feature_values_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = aiplatform.EntityType(entity_type_name=_TEST_ENTITY_TYPE_NAME)
        my_entity_type.ingest_from_bq(
            feature_ids=_TEST_IMPORTING_FEATURE_IDS,
            feature_time=_TEST_FEATURE_TIME_FIELD,
            bq_source_uri=_TEST_BQ_SOURCE_URI,
            feature_source_fields=_TEST_IMPORTING_FEATURE_SOURCE_FIELDS,
            sync=sync,
        )

        if not sync:
            my_entity_type.wait()

        true_import_feature_values_request = gca_featurestore_service.ImportFeatureValuesRequest(
            entity_type=_TEST_ENTITY_TYPE_NAME,
            feature_specs=[
                gca_featurestore_service.ImportFeatureValuesRequest.FeatureSpec(
                    id="my_feature_id_1", source_field="my_feature_id_1_source_field"
                ),
            ],
            bigquery_source=_TEST_BQ_SOURCE,
            feature_time_field=_TEST_FEATURE_TIME_FIELD,
        )
        import_feature_values_mock.assert_called_once_with(
            request=true_import_feature_values_request, metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_entity_type_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_ingest_from_gcs(self, import_feature_values_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = aiplatform.EntityType(entity_type_name=_TEST_ENTITY_TYPE_NAME)
        my_entity_type.ingest_from_gcs(
            feature_ids=_TEST_IMPORTING_FEATURE_IDS,
            feature_time=_TEST_FEATURE_TIME,
            gcs_source_uris=_TEST_GCS_AVRO_SOURCE_URIS,
            gcs_source_type=_TEST_GCS_SOURCE_TYPE_AVRO,
            sync=sync,
        )

        if not sync:
            my_entity_type.wait()

        true_import_feature_values_request = gca_featurestore_service.ImportFeatureValuesRequest(
            entity_type=_TEST_ENTITY_TYPE_NAME,
            feature_specs=[
                gca_featurestore_service.ImportFeatureValuesRequest.FeatureSpec(
                    id="my_feature_id_1"
                ),
            ],
            avro_source=_TEST_AVRO_SOURCE,
            feature_time=utils.get_timestamp_proto(_TEST_FEATURE_TIME),
        )
        import_feature_values_mock.assert_called_once_with(
            request=true_import_feature_values_request, metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_entity_type_mock")
    def test_ingest_from_gcs_with_invalid_gcs_source_type(self):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = aiplatform.EntityType(entity_type_name=_TEST_ENTITY_TYPE_NAME)
        with pytest.raises(ValueError):
            my_entity_type.ingest_from_gcs(
                feature_ids=_TEST_IMPORTING_FEATURE_IDS,
                feature_time=_TEST_FEATURE_TIME_FIELD,
                gcs_source_uris=_TEST_GCS_CSV_SOURCE_URIS,
                gcs_source_type=_TEST_GCS_SOURCE_TYPE_INVALID,
            )

    @pytest.mark.usefixtures(
        "get_entity_type_mock",
        "bq_init_client_mock",
        "bq_init_dataset_mock",
        "bq_create_dataset_mock",
        "bq_load_table_from_dataframe_mock",
        "bq_delete_dataset_mock",
    )
    @patch("uuid.uuid4", uuid_mock)
    def test_ingest_from_df_using_column(self, import_feature_values_mock):

        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = aiplatform.EntityType(entity_type_name=_TEST_ENTITY_TYPE_NAME)
        df_source = pd.DataFrame()
        my_entity_type.ingest_from_df(
            feature_ids=_TEST_IMPORTING_FEATURE_IDS,
            feature_time=_TEST_FEATURE_TIME_FIELD,
            df_source=df_source,
            feature_source_fields=_TEST_IMPORTING_FEATURE_SOURCE_FIELDS,
        )
        expected_temp_bq_dataset_name = f"temp_{_TEST_FEATURESTORE_ID}_{uuid.uuid4()}".replace(
            "-", "_"
        )
        expecte_temp_bq_dataset_id = f"{initializer.global_config.project}.{expected_temp_bq_dataset_name}"[
            :1024
        ]
        expected_temp_bq_table_id = (
            f"{expecte_temp_bq_dataset_id}.{_TEST_ENTITY_TYPE_ID}"
        )

        true_import_feature_values_request = gca_featurestore_service.ImportFeatureValuesRequest(
            entity_type=_TEST_ENTITY_TYPE_NAME,
            feature_specs=[
                gca_featurestore_service.ImportFeatureValuesRequest.FeatureSpec(
                    id="my_feature_id_1", source_field="my_feature_id_1_source_field"
                ),
            ],
            bigquery_source=gca_io.BigQuerySource(
                input_uri=f"bq://{expected_temp_bq_table_id}"
            ),
            feature_time_field=_TEST_FEATURE_TIME_FIELD,
        )

        import_feature_values_mock.assert_called_once_with(
            request=true_import_feature_values_request, metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures(
        "get_entity_type_mock",
        "bq_init_client_mock",
        "bq_init_dataset_mock",
        "bq_create_dataset_mock",
        "bq_load_table_from_dataframe_mock",
        "bq_delete_dataset_mock",
    )
    @patch("uuid.uuid4", uuid_mock)
    def test_ingest_from_df_using_datetime(self, import_feature_values_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_entity_type = aiplatform.EntityType(entity_type_name=_TEST_ENTITY_TYPE_NAME)
        df_source = pd.DataFrame()
        my_entity_type.ingest_from_df(
            feature_ids=_TEST_IMPORTING_FEATURE_IDS,
            feature_time=_TEST_FEATURE_TIME_DATETIME,
            df_source=df_source,
            feature_source_fields=_TEST_IMPORTING_FEATURE_SOURCE_FIELDS,
        )

        expected_temp_bq_dataset_name = f"temp_{_TEST_FEATURESTORE_ID}_{uuid.uuid4()}".replace(
            "-", "_"
        )
        expecte_temp_bq_dataset_id = f"{initializer.global_config.project}.{expected_temp_bq_dataset_name}"[
            :1024
        ]
        expected_temp_bq_table_id = (
            f"{expecte_temp_bq_dataset_id}.{_TEST_ENTITY_TYPE_ID}"
        )

        timestamp_proto = timestamp_pb2.Timestamp()
        timestamp_proto.FromDatetime(_TEST_FEATURE_TIME_DATETIME)

        true_import_feature_values_request = gca_featurestore_service.ImportFeatureValuesRequest(
            entity_type=_TEST_ENTITY_TYPE_NAME,
            feature_specs=[
                gca_featurestore_service.ImportFeatureValuesRequest.FeatureSpec(
                    id="my_feature_id_1", source_field="my_feature_id_1_source_field"
                ),
            ],
            bigquery_source=gca_io.BigQuerySource(
                input_uri=f"bq://{expected_temp_bq_table_id}"
            ),
            feature_time=timestamp_proto,
        )

        import_feature_values_mock.assert_called_once_with(
            request=true_import_feature_values_request, metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_entity_type_mock", "get_feature_mock")
    def test_read_single_entity(self, read_feature_values_mock):
        aiplatform.init(project=_TEST_PROJECT)
        my_entity_type = aiplatform.EntityType(entity_type_name=_TEST_ENTITY_TYPE_NAME)
        expected_read_feature_values_request = gca_featurestore_online_service.ReadFeatureValuesRequest(
            entity_type=my_entity_type.resource_name,
            entity_id=_TEST_READ_ENTITY_ID,
            feature_selector=gca_feature_selector.FeatureSelector(
                id_matcher=gca_feature_selector.IdMatcher(ids=["*"])
            ),
        )
        result = my_entity_type.read(entity_ids=_TEST_READ_ENTITY_ID)
        read_feature_values_mock.assert_called_once_with(
            request=expected_read_feature_values_request,
            metadata=_TEST_REQUEST_METADATA,
        )
        assert type(result) == pd.DataFrame
        assert len(result) == 1
        assert result.entity_id[0] == _TEST_READ_ENTITY_ID
        assert result.get(_TEST_FEATURE_ID)[0] == _TEST_FEATURE_VALUE

    @pytest.mark.usefixtures("get_entity_type_mock", "get_feature_mock")
    def test_read_multiple_entities(self, streaming_read_feature_values_mock):
        aiplatform.init(project=_TEST_PROJECT)
        my_entity_type = aiplatform.EntityType(entity_type_name=_TEST_ENTITY_TYPE_NAME)
        expected_streaming_read_feature_values_request = gca_featurestore_online_service.StreamingReadFeatureValuesRequest(
            entity_type=my_entity_type.resource_name,
            entity_ids=_TEST_READ_ENTITY_IDS,
            feature_selector=gca_feature_selector.FeatureSelector(
                id_matcher=gca_feature_selector.IdMatcher(ids=[_TEST_FEATURE_ID])
            ),
        )
        result = my_entity_type.read(
            entity_ids=_TEST_READ_ENTITY_IDS, feature_ids=_TEST_FEATURE_ID
        )
        streaming_read_feature_values_mock.assert_called_once_with(
            request=expected_streaming_read_feature_values_request,
            metadata=_TEST_REQUEST_METADATA,
        )
        assert type(result) == pd.DataFrame
        assert len(result) == 1
        assert result.entity_id[0] == _TEST_READ_ENTITY_ID
        assert result.get(_TEST_FEATURE_ID)[0] == _TEST_FEATURE_VALUE

    @pytest.mark.parametrize(
        "feature_ids, feature_value_types, entity_ids, feature_values, expected_df",
        [
            (
                _TEST_FEATURE_IDS_FOR_DF_CONSTRUCTION,
                _TEST_FEATURE_VALUE_TYPES_FOR_DF_CONSTRUCTION,
                ["entity_01", "entity_02"],
                [
                    [
                        False,
                        [True, False],
                        1.2,
                        [1.2, 3.4],
                        1,
                        [1, 2],
                        "test",
                        ["test1", "test2"],
                        b"1",
                    ],
                    [
                        True,
                        [True, True],
                        2.2,
                        [2.2, 4.4],
                        2,
                        [2, 3],
                        "test1",
                        ["test2", "test3"],
                        b"0",
                    ],
                ],
                pd.DataFrame(
                    data=[
                        [
                            "entity_01",
                            False,
                            [True, False],
                            1.2,
                            [1.2, 3.4],
                            1,
                            [1, 2],
                            "test",
                            ["test1", "test2"],
                            b"1",
                        ],
                        [
                            "entity_02",
                            True,
                            [True, True],
                            2.2,
                            [2.2, 4.4],
                            2,
                            [2, 3],
                            "test1",
                            ["test2", "test3"],
                            b"0",
                        ],
                    ],
                    columns=["entity_id"] + _TEST_FEATURE_IDS_FOR_DF_CONSTRUCTION,
                ),
            ),
            (
                _TEST_FEATURE_IDS_FOR_DF_CONSTRUCTION,
                _TEST_FEATURE_VALUE_TYPES_FOR_DF_CONSTRUCTION,
                ["entity_01", "entity_02"],
                [
                    [
                        False,
                        [True, False],
                        1.2,
                        [1.2, 3.4],
                        1,
                        [1, 2],
                        "test",
                        ["test1", "test2"],
                        b"1",
                    ],
                    [None, None, None, None, None, None, None, None, None],
                ],
                pd.DataFrame(
                    data=[
                        [
                            "entity_01",
                            False,
                            [True, False],
                            1.2,
                            [1.2, 3.4],
                            1,
                            [1, 2],
                            "test",
                            ["test1", "test2"],
                            b"1",
                        ],
                        [
                            "entity_02",
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                        ],
                    ],
                    columns=["entity_id"] + _TEST_FEATURE_IDS_FOR_DF_CONSTRUCTION,
                ),
            ),
            (
                _TEST_FEATURE_IDS_FOR_DF_CONSTRUCTION,
                _TEST_FEATURE_VALUE_TYPES_FOR_DF_CONSTRUCTION,
                ["entity_01"],
                [[None, None, None, None, None, None, None, None, None]],
                pd.DataFrame(
                    data=[
                        [
                            "entity_01",
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                            None,
                        ]
                    ],
                    columns=["entity_id"] + _TEST_FEATURE_IDS_FOR_DF_CONSTRUCTION,
                ),
            ),
            (
                _TEST_FEATURE_IDS_FOR_DF_CONSTRUCTION,
                _TEST_FEATURE_VALUE_TYPES_FOR_DF_CONSTRUCTION,
                [
                    "entity_01",
                    "entity_02",
                    "entity_03",
                    "entity_04",
                    "entity_05",
                    "entity_06",
                    "entity_07",
                    "entity_08",
                    "entity_09",
                    "entity_10",
                ],
                [
                    [
                        False,
                        [True, False],
                        1.2,
                        [1.2, 3.4],
                        1,
                        [1, 2],
                        "test",
                        ["test1", "test2"],
                        b"1",
                    ],
                    [
                        None,
                        [True, False],
                        1.2,
                        [1.2, 3.4],
                        1,
                        [1, 2],
                        "test",
                        ["test1", "test2"],
                        b"1",
                    ],
                    [
                        False,
                        None,
                        1.2,
                        [1.2, 3.4],
                        1,
                        [1, 2],
                        "test",
                        ["test1", "test2"],
                        b"1",
                    ],
                    [
                        False,
                        [True, False],
                        None,
                        [1.2, 3.4],
                        1,
                        [1, 2],
                        "test",
                        ["test1", "test2"],
                        b"1",
                    ],
                    [
                        False,
                        [True, False],
                        1.2,
                        None,
                        1,
                        [1, 2],
                        "test",
                        ["test1", "test2"],
                        b"1",
                    ],
                    [
                        False,
                        [True, False],
                        1.2,
                        [1.2, 3.4],
                        None,
                        [1, 2],
                        "test",
                        ["test1", "test2"],
                        b"1",
                    ],
                    [
                        False,
                        [True, False],
                        1.2,
                        [1.2, 3.4],
                        1,
                        None,
                        "test",
                        ["test1", "test2"],
                        b"1",
                    ],
                    [
                        False,
                        [True, False],
                        1.2,
                        [1.2, 3.4],
                        1,
                        [1, 2],
                        None,
                        ["test1", "test2"],
                        b"1",
                    ],
                    [
                        False,
                        [True, False],
                        1.2,
                        [1.2, 3.4],
                        1,
                        [1, 2],
                        "test",
                        None,
                        b"1",
                    ],
                    [
                        False,
                        [True, False],
                        1.2,
                        [1.2, 3.4],
                        1,
                        [1, 2],
                        "test",
                        ["test1", "test2"],
                        None,
                    ],
                ],
                pd.DataFrame(
                    data=[
                        [
                            "entity_01",
                            False,
                            [True, False],
                            1.2,
                            [1.2, 3.4],
                            1,
                            [1, 2],
                            "test",
                            ["test1", "test2"],
                            b"1",
                        ],
                        [
                            "entity_02",
                            None,
                            [True, False],
                            1.2,
                            [1.2, 3.4],
                            1,
                            [1, 2],
                            "test",
                            ["test1", "test2"],
                            b"1",
                        ],
                        [
                            "entity_03",
                            False,
                            None,
                            1.2,
                            [1.2, 3.4],
                            1,
                            [1, 2],
                            "test",
                            ["test1", "test2"],
                            b"1",
                        ],
                        [
                            "entity_04",
                            False,
                            [True, False],
                            None,
                            [1.2, 3.4],
                            1,
                            [1, 2],
                            "test",
                            ["test1", "test2"],
                            b"1",
                        ],
                        [
                            "entity_05",
                            False,
                            [True, False],
                            1.2,
                            None,
                            1,
                            [1, 2],
                            "test",
                            ["test1", "test2"],
                            b"1",
                        ],
                        [
                            "entity_06",
                            False,
                            [True, False],
                            1.2,
                            [1.2, 3.4],
                            None,
                            [1, 2],
                            "test",
                            ["test1", "test2"],
                            b"1",
                        ],
                        [
                            "entity_07",
                            False,
                            [True, False],
                            1.2,
                            [1.2, 3.4],
                            1,
                            None,
                            "test",
                            ["test1", "test2"],
                            b"1",
                        ],
                        [
                            "entity_08",
                            False,
                            [True, False],
                            1.2,
                            [1.2, 3.4],
                            1,
                            [1, 2],
                            None,
                            ["test1", "test2"],
                            b"1",
                        ],
                        [
                            "entity_09",
                            False,
                            [True, False],
                            1.2,
                            [1.2, 3.4],
                            1,
                            [1, 2],
                            "test",
                            None,
                            b"1",
                        ],
                        [
                            "entity_10",
                            False,
                            [True, False],
                            1.2,
                            [1.2, 3.4],
                            1,
                            [1, 2],
                            "test",
                            ["test1", "test2"],
                            None,
                        ],
                    ],
                    columns=["entity_id"] + _TEST_FEATURE_IDS_FOR_DF_CONSTRUCTION,
                ),
            ),
        ],
    )
    def test_construct_dataframe(
        self, feature_ids, feature_value_types, entity_ids, feature_values, expected_df,
    ):
        entity_views = [
            _get_entity_view_proto(
                entity_id=entity_id,
                feature_value_types=feature_value_types,
                feature_values=entity_feature_values,
            )
            for (entity_id, entity_feature_values) in zip(entity_ids, feature_values)
        ]
        df = aiplatform.EntityType._construct_dataframe(
            feature_ids=feature_ids, entity_views=entity_views
        )
        assert df.equals(expected_df)


class TestFeature:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize(
        "feature_name, entity_type_id, featurestore_id",
        [
            (_TEST_FEATURE_NAME, None, None),
            (_TEST_FEATURE_ID, _TEST_ENTITY_TYPE_ID, _TEST_FEATURESTORE_ID),
        ],
    )
    def test_init_feature(
        self, feature_name, entity_type_id, featurestore_id, get_feature_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        aiplatform.Feature(
            feature_name=feature_name,
            entity_type_id=entity_type_id,
            featurestore_id=featurestore_id,
        )
        get_feature_mock.assert_called_once_with(
            name=_TEST_FEATURE_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_feature_raises_with_only_featurestore_id(self):
        aiplatform.init(project=_TEST_PROJECT)

        with pytest.raises(ValueError):
            aiplatform.Feature(
                feature_name=_TEST_FEATURE_NAME, featurestore_id=_TEST_FEATURESTORE_ID,
            )

    def test_init_feature_raises_with_only_entity_type_id(self):
        aiplatform.init(project=_TEST_PROJECT)

        with pytest.raises(ValueError):
            aiplatform.Feature(
                feature_name=_TEST_FEATURE_NAME, entity_type_id=_TEST_ENTITY_TYPE_ID,
            )

    @pytest.mark.usefixtures("get_feature_mock")
    def test_get_featurestore(self, get_featurestore_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_feature = aiplatform.Feature(feature_name=_TEST_FEATURE_NAME)
        my_featurestore = my_feature.get_featurestore()

        get_featurestore_mock.assert_called_once_with(
            name=my_featurestore.resource_name, retry=base._DEFAULT_RETRY
        )
        assert type(my_featurestore) == aiplatform.Featurestore

    @pytest.mark.usefixtures("get_feature_mock")
    def test_get_entity_type(self, get_entity_type_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_feature = aiplatform.Feature(feature_name=_TEST_FEATURE_NAME)
        my_entity_type = my_feature.get_entity_type()

        get_entity_type_mock.assert_called_once_with(
            name=my_entity_type.resource_name, retry=base._DEFAULT_RETRY
        )
        assert type(my_entity_type) == aiplatform.EntityType

    @pytest.mark.usefixtures("get_feature_mock")
    def test_update_feature(self, update_feature_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_feature = aiplatform.Feature(feature_name=_TEST_FEATURE_NAME)
        my_feature.update(labels=_TEST_LABELS_UPDATE)

        expected_feature = gca_feature.Feature(
            name=_TEST_FEATURE_NAME, labels=_TEST_LABELS_UPDATE,
        )
        update_feature_mock.assert_called_once_with(
            feature=expected_feature,
            update_mask=field_mask_pb2.FieldMask(paths=["labels"]),
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.parametrize(
        "entity_type_name, featurestore_id",
        [
            (_TEST_ENTITY_TYPE_NAME, None),
            (_TEST_ENTITY_TYPE_ID, _TEST_FEATURESTORE_ID),
        ],
    )
    def test_list_features(self, entity_type_name, featurestore_id, list_features_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_feature_list = aiplatform.Feature.list(
            entity_type_name=entity_type_name, featurestore_id=featurestore_id
        )

        list_features_mock.assert_called_once_with(
            request={"parent": _TEST_ENTITY_TYPE_NAME, "filter": None}
        )
        assert len(my_feature_list) == len(_TEST_FEATURE_LIST)
        for my_feature in my_feature_list:
            assert type(my_feature) == aiplatform.Feature

    @pytest.mark.usefixtures("get_feature_mock")
    def test_search_features(self, search_features_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_feature_list = aiplatform.Feature.search()

        search_features_mock.assert_called_once_with(
            request={"location": _TEST_PARENT, "query": None}
        )
        assert len(my_feature_list) == len(_TEST_FEATURE_LIST)
        for my_feature in my_feature_list:
            assert type(my_feature) == aiplatform.Feature

    @pytest.mark.usefixtures("get_feature_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_feature(self, create_feature_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_feature = aiplatform.Feature.create(
            feature_id=_TEST_FEATURE_ID,
            value_type=_TEST_FEATURE_VALUE_TYPE_STR,
            entity_type_name=_TEST_ENTITY_TYPE_ID,
            featurestore_id=_TEST_FEATURESTORE_ID,
            description=_TEST_DESCRIPTION,
            labels=_TEST_LABELS,
        )

        if not sync:
            my_feature.wait()

        expected_feature = gca_feature.Feature(
            value_type=_TEST_FEATURE_VALUE_TYPE_ENUM,
            labels=_TEST_LABELS,
            description=_TEST_DESCRIPTION,
        )
        create_feature_mock.assert_called_once_with(
            request=gca_featurestore_service.CreateFeatureRequest(
                parent=_TEST_ENTITY_TYPE_NAME,
                feature=expected_feature,
                feature_id=_TEST_FEATURE_ID,
            ),
            metadata=_TEST_REQUEST_METADATA,
        )
