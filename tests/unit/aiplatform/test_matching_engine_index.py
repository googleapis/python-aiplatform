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

import pytest
import uuid

from unittest import mock
from importlib import reload
from unittest.mock import patch

from google.api_core import operation
from google.protobuf import field_mask_pb2

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.compat.services import (
    index_service_client,
)

from google.cloud.aiplatform.compat.types import (
    index as gca_index,
    encryption_spec as gca_encryption_spec,
    index_service as gca_index_service,
)
import constants as test_constants

# project
_TEST_PROJECT = test_constants.ProjectConstants._TEST_PROJECT
_TEST_LOCATION = test_constants.ProjectConstants._TEST_LOCATION
_TEST_PARENT = test_constants.ProjectConstants._TEST_PARENT


# index
_TEST_INDEX_ID = test_constants.MatchingEngineConstants._TEST_INDEX_ID
_TEST_INDEX_NAME = test_constants.MatchingEngineConstants._TEST_INDEX_NAME
_TEST_INDEX_DISPLAY_NAME = (
    test_constants.MatchingEngineConstants._TEST_INDEX_DISPLAY_NAME
)
_TEST_CONTENTS_DELTA_URI = "gs://contents"
_TEST_INDEX_DISTANCE_MEASURE_TYPE = "SQUARED_L2_DISTANCE"
_TEST_INDEX_FEATURE_NORM_TYPE = "UNIT_L2_NORM"

_TEST_CONTENTS_DELTA_URI_UPDATE = "gs://contents_update"
_TEST_IS_COMPLETE_OVERWRITE_UPDATE = True

_TEST_INDEX_CONFIG_DIMENSIONS = 100
_TEST_INDEX_APPROXIMATE_NEIGHBORS_COUNT = 150
_TEST_LEAF_NODE_EMBEDDING_COUNT = 123
_TEST_LEAF_NODES_TO_SEARCH_PERCENT = 50
_TEST_SHARD_SIZES = ["SHARD_SIZE_SMALL", "SHARD_SIZE_LARGE", "SHARD_SIZE_MEDIUM"]

_TEST_INDEX_DESCRIPTION = test_constants.MatchingEngineConstants._TEST_INDEX_DESCRIPTION


_TEST_LABELS = test_constants.MatchingEngineConstants._TEST_LABELS
_TEST_DISPLAY_NAME_UPDATE = (
    test_constants.MatchingEngineConstants._TEST_DISPLAY_NAME_UPDATE
)
_TEST_DESCRIPTION_UPDATE = (
    test_constants.MatchingEngineConstants._TEST_DESCRIPTION_UPDATE
)
_TEST_LABELS_UPDATE = test_constants.MatchingEngineConstants._TEST_LABELS_UPDATE

# request_metadata
_TEST_REQUEST_METADATA = test_constants.MatchingEngineConstants._TEST_REQUEST_METADATA

# Lists
_TEST_INDEX_LIST = [
    gca_index.Index(
        name=_TEST_INDEX_NAME,
        display_name=_TEST_INDEX_DISPLAY_NAME,
        description=_TEST_INDEX_DESCRIPTION,
    ),
    gca_index.Index(
        name=_TEST_INDEX_NAME,
        display_name=_TEST_INDEX_DISPLAY_NAME,
        description=_TEST_INDEX_DESCRIPTION,
    ),
    gca_index.Index(
        name=_TEST_INDEX_NAME,
        display_name=_TEST_INDEX_DISPLAY_NAME,
        description=_TEST_INDEX_DESCRIPTION,
    ),
]

# Index update method
_TEST_INDEX_BATCH_UPDATE_METHOD = "BATCH_UPDATE"
_TEST_INDEX_STREAM_UPDATE_METHOD = "STREAM_UPDATE"
_TEST_INDEX_EMPTY_UPDATE_METHOD = None
_TEST_INDEX_INVALID_UPDATE_METHOD = "INVALID_UPDATE_METHOD"
_TEST_INDEX_UPDATE_METHOD_EXPECTED_RESULT_MAP = {
    _TEST_INDEX_BATCH_UPDATE_METHOD: gca_index.Index.IndexUpdateMethod.BATCH_UPDATE,
    _TEST_INDEX_STREAM_UPDATE_METHOD: gca_index.Index.IndexUpdateMethod.STREAM_UPDATE,
    _TEST_INDEX_EMPTY_UPDATE_METHOD: None,
    _TEST_INDEX_INVALID_UPDATE_METHOD: None,
}

# Encryption spec
_TEST_ENCRYPTION_SPEC_KEY_NAME = "TEST_ENCRYPTION_SPEC"

_TEST_DATAPOINT_IDS = ("1", "2")
_TEST_DATAPOINT_1 = gca_index.IndexDatapoint(
    datapoint_id="0",
    feature_vector=[0.00526886899, -0.0198396724],
    restricts=[
        gca_index.IndexDatapoint.Restriction(namespace="Color", allow_list=["red"])
    ],
    numeric_restricts=[
        gca_index.IndexDatapoint.NumericRestriction(
            namespace="cost",
            value_int=1,
        )
    ],
)
_TEST_DATAPOINT_2 = gca_index.IndexDatapoint(
    datapoint_id="1",
    feature_vector=[0.00526886899, -0.0198396724],
    numeric_restricts=[
        gca_index.IndexDatapoint.NumericRestriction(
            namespace="cost",
            value_double=0.1,
        )
    ],
    crowding_tag=gca_index.IndexDatapoint.CrowdingTag(crowding_attribute="crowding"),
)
_TEST_DATAPOINT_3 = gca_index.IndexDatapoint(
    datapoint_id="2",
    feature_vector=[0.00526886899, -0.0198396724],
    numeric_restricts=[
        gca_index.IndexDatapoint.NumericRestriction(
            namespace="cost",
            value_float=1.1,
        )
    ],
)
_TEST_DATAPOINTS = (_TEST_DATAPOINT_1, _TEST_DATAPOINT_2, _TEST_DATAPOINT_3)
_TEST_TIMEOUT = 1800.0
_TEST_UPDATE_MASK = ["all_restricts"]


def uuid_mock():
    return uuid.UUID(int=1)


# All Index Mocks
@pytest.fixture
def get_index_mock():
    with patch.object(
        index_service_client.IndexServiceClient, "get_index"
    ) as get_index_mock:
        get_index_mock.return_value = gca_index.Index(
            name=_TEST_INDEX_NAME,
            display_name=_TEST_INDEX_DISPLAY_NAME,
            description=_TEST_INDEX_DESCRIPTION,
        )
        yield get_index_mock


@pytest.fixture
def update_index_metadata_mock():
    with patch.object(
        index_service_client.IndexServiceClient, "update_index"
    ) as update_index_mock:
        index_lro_mock = mock.Mock(operation.Operation)
        index_lro_mock.result.return_value = gca_index.Index(
            name=_TEST_INDEX_NAME,
            display_name=_TEST_DISPLAY_NAME_UPDATE,
            description=_TEST_DESCRIPTION_UPDATE,
            labels=_TEST_LABELS_UPDATE,
        )
        update_index_mock.return_value = index_lro_mock
        yield update_index_mock


@pytest.fixture
def update_index_embeddings_mock():
    with patch.object(
        index_service_client.IndexServiceClient, "update_index"
    ) as update_index_mock:
        index_lro_mock = mock.Mock(operation.Operation)
        index_lro_mock.result.return_value = gca_index.Index(
            name=_TEST_INDEX_NAME,
        )
        update_index_mock.return_value = index_lro_mock
        yield update_index_mock


@pytest.fixture
def list_indexes_mock():
    with patch.object(
        index_service_client.IndexServiceClient, "list_indexes"
    ) as list_indexes_mock:
        list_indexes_mock.return_value = _TEST_INDEX_LIST
        yield list_indexes_mock


@pytest.fixture
def delete_index_mock():
    with mock.patch.object(
        index_service_client.IndexServiceClient, "delete_index"
    ) as delete_index_mock:
        delete_index_lro_mock = mock.Mock(operation.Operation)
        delete_index_mock.return_value = delete_index_lro_mock
        yield delete_index_mock


@pytest.fixture
def create_index_mock():
    with patch.object(
        index_service_client.IndexServiceClient, "create_index"
    ) as create_index_mock:
        create_index_lro_mock = mock.Mock(operation.Operation)
        create_index_lro_mock.result.return_value = gca_index.Index(
            name=_TEST_INDEX_NAME,
            display_name=_TEST_INDEX_DISPLAY_NAME,
            description=_TEST_INDEX_DESCRIPTION,
        )
        create_index_mock.return_value = create_index_lro_mock
        yield create_index_mock


@pytest.fixture
def upsert_datapoints_mock():
    with patch.object(
        index_service_client.IndexServiceClient, "upsert_datapoints"
    ) as upsert_datapoints_mock:
        yield upsert_datapoints_mock


@pytest.fixture
def remove_datapoints_mock():
    with patch.object(
        index_service_client.IndexServiceClient, "remove_datapoints"
    ) as remove_datapoints_mock:
        yield remove_datapoints_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestMatchingEngineIndex:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize("index_name", [_TEST_INDEX_ID, _TEST_INDEX_NAME])
    def test_init_index(self, index_name, get_index_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_index = aiplatform.MatchingEngineIndex(index_name=index_name)

        get_index_mock.assert_called_once_with(
            name=my_index.resource_name,
            retry=base._DEFAULT_RETRY,
        )

    @pytest.mark.usefixtures("get_index_mock")
    def test_update_index_metadata(self, update_index_metadata_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_index = aiplatform.MatchingEngineIndex(index_name=_TEST_INDEX_ID)
        updated_index = my_index.update_metadata(
            display_name=_TEST_DISPLAY_NAME_UPDATE,
            description=_TEST_DESCRIPTION_UPDATE,
            labels=_TEST_LABELS_UPDATE,
            update_request_timeout=_TEST_TIMEOUT,
        )

        expected = gca_index.Index(
            name=_TEST_INDEX_NAME,
            display_name=_TEST_DISPLAY_NAME_UPDATE,
            description=_TEST_DESCRIPTION_UPDATE,
            labels=_TEST_LABELS_UPDATE,
        )

        update_index_metadata_mock.assert_called_once_with(
            index=expected,
            update_mask=field_mask_pb2.FieldMask(
                paths=["labels", "display_name", "description"]
            ),
            metadata=_TEST_REQUEST_METADATA,
            timeout=_TEST_TIMEOUT,
        )

        assert updated_index.gca_resource == expected

    @pytest.mark.usefixtures("get_index_mock")
    def test_update_index_embeddings(self, update_index_embeddings_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_index = aiplatform.MatchingEngineIndex(index_name=_TEST_INDEX_ID)
        updated_index = my_index.update_embeddings(
            contents_delta_uri=_TEST_CONTENTS_DELTA_URI_UPDATE,
            is_complete_overwrite=_TEST_IS_COMPLETE_OVERWRITE_UPDATE,
            update_request_timeout=_TEST_TIMEOUT,
        )

        expected = gca_index.Index(
            name=_TEST_INDEX_NAME,
            metadata={
                "contentsDeltaUri": _TEST_CONTENTS_DELTA_URI_UPDATE,
                "isCompleteOverwrite": _TEST_IS_COMPLETE_OVERWRITE_UPDATE,
            },
        )

        update_index_embeddings_mock.assert_called_once_with(
            index=expected,
            update_mask=field_mask_pb2.FieldMask(paths=["metadata"]),
            metadata=_TEST_REQUEST_METADATA,
            timeout=_TEST_TIMEOUT,
        )

        # The service only returns the name of the Index
        assert updated_index.gca_resource == gca_index.Index(name=_TEST_INDEX_NAME)

    def test_list_indexes(self, list_indexes_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_indexes_list = aiplatform.MatchingEngineIndex.list()

        list_indexes_mock.assert_called_once_with(request={"parent": _TEST_PARENT})
        assert len(my_indexes_list) == len(_TEST_INDEX_LIST)
        for my_index in my_indexes_list:
            assert isinstance(my_index, aiplatform.MatchingEngineIndex)

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_index_mock")
    def test_delete_index(self, delete_index_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_index = aiplatform.MatchingEngineIndex(index_name=_TEST_INDEX_ID)
        my_index.delete(sync=sync)

        if not sync:
            my_index.wait()

        delete_index_mock.assert_called_once_with(name=my_index.resource_name)

    @pytest.mark.usefixtures("get_index_mock")
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.parametrize(
        "index_update_method",
        [
            _TEST_INDEX_STREAM_UPDATE_METHOD,
            _TEST_INDEX_BATCH_UPDATE_METHOD,
            _TEST_INDEX_EMPTY_UPDATE_METHOD,
            _TEST_INDEX_INVALID_UPDATE_METHOD,
        ],
    )
    @pytest.mark.parametrize("shard_size", _TEST_SHARD_SIZES)
    def test_create_tree_ah_index(
        self, create_index_mock, sync, index_update_method, shard_size
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
            display_name=_TEST_INDEX_DISPLAY_NAME,
            contents_delta_uri=_TEST_CONTENTS_DELTA_URI,
            dimensions=_TEST_INDEX_CONFIG_DIMENSIONS,
            approximate_neighbors_count=_TEST_INDEX_APPROXIMATE_NEIGHBORS_COUNT,
            distance_measure_type=_TEST_INDEX_DISTANCE_MEASURE_TYPE,
            feature_norm_type=_TEST_INDEX_FEATURE_NORM_TYPE,
            leaf_node_embedding_count=_TEST_LEAF_NODE_EMBEDDING_COUNT,
            leaf_nodes_to_search_percent=_TEST_LEAF_NODES_TO_SEARCH_PERCENT,
            description=_TEST_INDEX_DESCRIPTION,
            labels=_TEST_LABELS,
            sync=sync,
            index_update_method=index_update_method,
            encryption_spec_key_name=_TEST_ENCRYPTION_SPEC_KEY_NAME,
            create_request_timeout=_TEST_TIMEOUT,
            shard_size=shard_size,
        )

        if not sync:
            my_index.wait()

        config = {
            "treeAhConfig": {
                "leafNodeEmbeddingCount": _TEST_LEAF_NODE_EMBEDDING_COUNT,
                "leafNodesToSearchPercent": _TEST_LEAF_NODES_TO_SEARCH_PERCENT,
            }
        }

        expected = gca_index.Index(
            display_name=_TEST_INDEX_DISPLAY_NAME,
            metadata={
                "config": {
                    "algorithmConfig": config,
                    "dimensions": _TEST_INDEX_CONFIG_DIMENSIONS,
                    "approximateNeighborsCount": _TEST_INDEX_APPROXIMATE_NEIGHBORS_COUNT,
                    "distanceMeasureType": _TEST_INDEX_DISTANCE_MEASURE_TYPE,
                    "featureNormType": _TEST_INDEX_FEATURE_NORM_TYPE,
                    "shardSize": shard_size,
                },
                "contentsDeltaUri": _TEST_CONTENTS_DELTA_URI,
            },
            description=_TEST_INDEX_DESCRIPTION,
            labels=_TEST_LABELS,
            index_update_method=_TEST_INDEX_UPDATE_METHOD_EXPECTED_RESULT_MAP[
                index_update_method
            ],
            encryption_spec=gca_encryption_spec.EncryptionSpec(
                kms_key_name=_TEST_ENCRYPTION_SPEC_KEY_NAME
            ),
        )

        create_index_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            index=expected,
            metadata=_TEST_REQUEST_METADATA,
            timeout=_TEST_TIMEOUT,
        )

    @pytest.mark.usefixtures("get_index_mock")
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.parametrize(
        "index_update_method",
        [
            _TEST_INDEX_STREAM_UPDATE_METHOD,
            _TEST_INDEX_BATCH_UPDATE_METHOD,
            _TEST_INDEX_EMPTY_UPDATE_METHOD,
            _TEST_INDEX_INVALID_UPDATE_METHOD,
        ],
    )
    @pytest.mark.parametrize("shard_size", _TEST_SHARD_SIZES)
    def test_create_tree_ah_index_with_empty_index(
        self, create_index_mock, sync, index_update_method, shard_size
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
            display_name=_TEST_INDEX_DISPLAY_NAME,
            contents_delta_uri=None,
            dimensions=_TEST_INDEX_CONFIG_DIMENSIONS,
            approximate_neighbors_count=_TEST_INDEX_APPROXIMATE_NEIGHBORS_COUNT,
            distance_measure_type=_TEST_INDEX_DISTANCE_MEASURE_TYPE,
            feature_norm_type=_TEST_INDEX_FEATURE_NORM_TYPE,
            leaf_node_embedding_count=_TEST_LEAF_NODE_EMBEDDING_COUNT,
            leaf_nodes_to_search_percent=_TEST_LEAF_NODES_TO_SEARCH_PERCENT,
            description=_TEST_INDEX_DESCRIPTION,
            labels=_TEST_LABELS,
            sync=sync,
            index_update_method=index_update_method,
            encryption_spec_key_name=_TEST_ENCRYPTION_SPEC_KEY_NAME,
            create_request_timeout=_TEST_TIMEOUT,
            shard_size=shard_size,
        )

        if not sync:
            my_index.wait()

        config = {
            "treeAhConfig": {
                "leafNodeEmbeddingCount": _TEST_LEAF_NODE_EMBEDDING_COUNT,
                "leafNodesToSearchPercent": _TEST_LEAF_NODES_TO_SEARCH_PERCENT,
            }
        }

        expected = gca_index.Index(
            display_name=_TEST_INDEX_DISPLAY_NAME,
            metadata={
                "config": {
                    "algorithmConfig": config,
                    "dimensions": _TEST_INDEX_CONFIG_DIMENSIONS,
                    "approximateNeighborsCount": _TEST_INDEX_APPROXIMATE_NEIGHBORS_COUNT,
                    "distanceMeasureType": _TEST_INDEX_DISTANCE_MEASURE_TYPE,
                    "featureNormType": _TEST_INDEX_FEATURE_NORM_TYPE,
                    "shardSize": shard_size,
                },
            },
            description=_TEST_INDEX_DESCRIPTION,
            labels=_TEST_LABELS,
            index_update_method=_TEST_INDEX_UPDATE_METHOD_EXPECTED_RESULT_MAP[
                index_update_method
            ],
            encryption_spec=gca_encryption_spec.EncryptionSpec(
                kms_key_name=_TEST_ENCRYPTION_SPEC_KEY_NAME
            ),
        )

        create_index_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            index=expected,
            metadata=_TEST_REQUEST_METADATA,
            timeout=_TEST_TIMEOUT,
        )

    @pytest.mark.usefixtures("get_index_mock")
    def test_create_tree_ah_index_backward_compatibility(self, create_index_mock):
        aiplatform.init(project=_TEST_PROJECT)

        aiplatform.MatchingEngineIndex.create_tree_ah_index(
            display_name=_TEST_INDEX_DISPLAY_NAME,
            contents_delta_uri=_TEST_CONTENTS_DELTA_URI,
            dimensions=_TEST_INDEX_CONFIG_DIMENSIONS,
            approximate_neighbors_count=_TEST_INDEX_APPROXIMATE_NEIGHBORS_COUNT,
            distance_measure_type=_TEST_INDEX_DISTANCE_MEASURE_TYPE,
            feature_norm_type=_TEST_INDEX_FEATURE_NORM_TYPE,
            leaf_node_embedding_count=_TEST_LEAF_NODE_EMBEDDING_COUNT,
            leaf_nodes_to_search_percent=_TEST_LEAF_NODES_TO_SEARCH_PERCENT,
            description=_TEST_INDEX_DESCRIPTION,
            labels=_TEST_LABELS,
        )

        config = {
            "treeAhConfig": {
                "leafNodeEmbeddingCount": _TEST_LEAF_NODE_EMBEDDING_COUNT,
                "leafNodesToSearchPercent": _TEST_LEAF_NODES_TO_SEARCH_PERCENT,
            }
        }

        expected = gca_index.Index(
            display_name=_TEST_INDEX_DISPLAY_NAME,
            metadata={
                "config": {
                    "algorithmConfig": config,
                    "dimensions": _TEST_INDEX_CONFIG_DIMENSIONS,
                    "approximateNeighborsCount": _TEST_INDEX_APPROXIMATE_NEIGHBORS_COUNT,
                    "distanceMeasureType": _TEST_INDEX_DISTANCE_MEASURE_TYPE,
                    "featureNormType": _TEST_INDEX_FEATURE_NORM_TYPE,
                    "shardSize": None,
                },
                "contentsDeltaUri": _TEST_CONTENTS_DELTA_URI,
            },
            description=_TEST_INDEX_DESCRIPTION,
            labels=_TEST_LABELS,
        )

        create_index_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            index=expected,
            metadata=_TEST_REQUEST_METADATA,
            timeout=None,
        )

    @pytest.mark.usefixtures("get_index_mock")
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.parametrize(
        "index_update_method",
        [
            _TEST_INDEX_STREAM_UPDATE_METHOD,
            _TEST_INDEX_BATCH_UPDATE_METHOD,
            _TEST_INDEX_EMPTY_UPDATE_METHOD,
            _TEST_INDEX_INVALID_UPDATE_METHOD,
        ],
    )
    @pytest.mark.parametrize("shard_size", _TEST_SHARD_SIZES)
    def test_create_brute_force_index(
        self, create_index_mock, sync, index_update_method, shard_size
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_index = aiplatform.MatchingEngineIndex.create_brute_force_index(
            display_name=_TEST_INDEX_DISPLAY_NAME,
            contents_delta_uri=_TEST_CONTENTS_DELTA_URI,
            dimensions=_TEST_INDEX_CONFIG_DIMENSIONS,
            distance_measure_type=_TEST_INDEX_DISTANCE_MEASURE_TYPE,
            feature_norm_type=_TEST_INDEX_FEATURE_NORM_TYPE,
            description=_TEST_INDEX_DESCRIPTION,
            labels=_TEST_LABELS,
            sync=sync,
            index_update_method=index_update_method,
            encryption_spec_key_name=_TEST_ENCRYPTION_SPEC_KEY_NAME,
            create_request_timeout=_TEST_TIMEOUT,
            shard_size=shard_size,
        )

        if not sync:
            my_index.wait()

        config = {"bruteForceConfig": {}}

        expected = gca_index.Index(
            display_name=_TEST_INDEX_DISPLAY_NAME,
            metadata={
                "config": {
                    "algorithmConfig": config,
                    "dimensions": _TEST_INDEX_CONFIG_DIMENSIONS,
                    "approximateNeighborsCount": None,
                    "distanceMeasureType": _TEST_INDEX_DISTANCE_MEASURE_TYPE,
                    "featureNormType": _TEST_INDEX_FEATURE_NORM_TYPE,
                    "shardSize": shard_size,
                },
                "contentsDeltaUri": _TEST_CONTENTS_DELTA_URI,
            },
            description=_TEST_INDEX_DESCRIPTION,
            labels=_TEST_LABELS,
            index_update_method=_TEST_INDEX_UPDATE_METHOD_EXPECTED_RESULT_MAP[
                index_update_method
            ],
            encryption_spec=gca_encryption_spec.EncryptionSpec(
                kms_key_name=_TEST_ENCRYPTION_SPEC_KEY_NAME,
            ),
        )

        create_index_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            index=expected,
            metadata=_TEST_REQUEST_METADATA,
            timeout=_TEST_TIMEOUT,
        )

    @pytest.mark.usefixtures("get_index_mock")
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.parametrize(
        "index_update_method",
        [
            _TEST_INDEX_STREAM_UPDATE_METHOD,
            _TEST_INDEX_BATCH_UPDATE_METHOD,
            _TEST_INDEX_EMPTY_UPDATE_METHOD,
            _TEST_INDEX_INVALID_UPDATE_METHOD,
        ],
    )
    def test_create_brute_force_index_with_empty_index(
        self, create_index_mock, sync, index_update_method
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_index = aiplatform.MatchingEngineIndex.create_brute_force_index(
            display_name=_TEST_INDEX_DISPLAY_NAME,
            dimensions=_TEST_INDEX_CONFIG_DIMENSIONS,
            distance_measure_type=_TEST_INDEX_DISTANCE_MEASURE_TYPE,
            feature_norm_type=_TEST_INDEX_FEATURE_NORM_TYPE,
            description=_TEST_INDEX_DESCRIPTION,
            labels=_TEST_LABELS,
            sync=sync,
            index_update_method=index_update_method,
            encryption_spec_key_name=_TEST_ENCRYPTION_SPEC_KEY_NAME,
            create_request_timeout=_TEST_TIMEOUT,
        )

        if not sync:
            my_index.wait()

        config = {"bruteForceConfig": {}}

        expected = gca_index.Index(
            display_name=_TEST_INDEX_DISPLAY_NAME,
            metadata={
                "config": {
                    "algorithmConfig": config,
                    "dimensions": _TEST_INDEX_CONFIG_DIMENSIONS,
                    "approximateNeighborsCount": None,
                    "distanceMeasureType": _TEST_INDEX_DISTANCE_MEASURE_TYPE,
                    "featureNormType": _TEST_INDEX_FEATURE_NORM_TYPE,
                    "shardSize": None,
                },
            },
            description=_TEST_INDEX_DESCRIPTION,
            labels=_TEST_LABELS,
            index_update_method=_TEST_INDEX_UPDATE_METHOD_EXPECTED_RESULT_MAP[
                index_update_method
            ],
            encryption_spec=gca_encryption_spec.EncryptionSpec(
                kms_key_name=_TEST_ENCRYPTION_SPEC_KEY_NAME,
            ),
        )

        create_index_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            index=expected,
            metadata=_TEST_REQUEST_METADATA,
            timeout=_TEST_TIMEOUT,
        )

    @pytest.mark.usefixtures("get_index_mock")
    def test_create_brute_force_index_backward_compatibility(self, create_index_mock):
        aiplatform.init(project=_TEST_PROJECT)

        aiplatform.MatchingEngineIndex.create_brute_force_index(
            display_name=_TEST_INDEX_DISPLAY_NAME,
            contents_delta_uri=_TEST_CONTENTS_DELTA_URI,
            dimensions=_TEST_INDEX_CONFIG_DIMENSIONS,
            distance_measure_type=_TEST_INDEX_DISTANCE_MEASURE_TYPE,
            feature_norm_type=_TEST_INDEX_FEATURE_NORM_TYPE,
            description=_TEST_INDEX_DESCRIPTION,
            labels=_TEST_LABELS,
        )

        config = {"bruteForceConfig": {}}

        expected = gca_index.Index(
            display_name=_TEST_INDEX_DISPLAY_NAME,
            metadata={
                "config": {
                    "algorithmConfig": config,
                    "dimensions": _TEST_INDEX_CONFIG_DIMENSIONS,
                    "approximateNeighborsCount": None,
                    "distanceMeasureType": _TEST_INDEX_DISTANCE_MEASURE_TYPE,
                    "featureNormType": _TEST_INDEX_FEATURE_NORM_TYPE,
                    "shardSize": None,
                },
                "contentsDeltaUri": _TEST_CONTENTS_DELTA_URI,
            },
            description=_TEST_INDEX_DESCRIPTION,
            labels=_TEST_LABELS,
        )

        create_index_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            index=expected,
            metadata=_TEST_REQUEST_METADATA,
            timeout=None,
        )

    @pytest.mark.usefixtures("get_index_mock")
    def test_upsert_datapoints(self, upsert_datapoints_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_index = aiplatform.MatchingEngineIndex(index_name=_TEST_INDEX_ID)
        my_index.upsert_datapoints(
            datapoints=_TEST_DATAPOINTS,
        )

        upsert_datapoints_request = gca_index_service.UpsertDatapointsRequest(
            index=_TEST_INDEX_NAME,
            datapoints=_TEST_DATAPOINTS,
        )

        upsert_datapoints_mock.assert_called_once_with(upsert_datapoints_request)

    @pytest.mark.usefixtures("get_index_mock")
    def test_upsert_datapoints_dynamic_metadata_update(self, upsert_datapoints_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_index = aiplatform.MatchingEngineIndex(index_name=_TEST_INDEX_ID)
        my_index.upsert_datapoints(
            datapoints=_TEST_DATAPOINTS,
            update_mask=_TEST_UPDATE_MASK,
        )

        upsert_datapoints_request = gca_index_service.UpsertDatapointsRequest(
            index=_TEST_INDEX_NAME,
            datapoints=_TEST_DATAPOINTS,
            update_mask=field_mask_pb2.FieldMask(paths=_TEST_UPDATE_MASK),
        )

        upsert_datapoints_mock.assert_called_once_with(upsert_datapoints_request)

    @pytest.mark.usefixtures("get_index_mock")
    def test_remove_datapoints(self, remove_datapoints_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_index = aiplatform.MatchingEngineIndex(index_name=_TEST_INDEX_ID)
        my_index.remove_datapoints(
            datapoint_ids=_TEST_DATAPOINT_IDS,
        )

        remove_datapoints_request = gca_index_service.RemoveDatapointsRequest(
            index=_TEST_INDEX_NAME,
            datapoint_ids=_TEST_DATAPOINT_IDS,
        )

        remove_datapoints_mock.assert_called_once_with(remove_datapoints_request)
