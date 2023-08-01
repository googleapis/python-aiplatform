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

from google.cloud.aiplatform.compat.types import index as gca_index
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

_TEST_CONTENTS_DELTA_URI_UPDATE = "gs://contents_update"
_TEST_IS_COMPLETE_OVERWRITE_UPDATE = True

_TEST_INDEX_CONFIG_DIMENSIONS = 100
_TEST_INDEX_APPROXIMATE_NEIGHBORS_COUNT = 150
_TEST_LEAF_NODE_EMBEDDING_COUNT = 123
_TEST_LEAF_NODES_TO_SEARCH_PERCENT = 50

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
            name=my_index.resource_name, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures("get_index_mock")
    def test_update_index_metadata(self, update_index_metadata_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_index = aiplatform.MatchingEngineIndex(index_name=_TEST_INDEX_ID)
        updated_index = my_index.update_metadata(
            display_name=_TEST_DISPLAY_NAME_UPDATE,
            description=_TEST_DESCRIPTION_UPDATE,
            labels=_TEST_LABELS_UPDATE,
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
        )

        assert updated_index.gca_resource == expected

    @pytest.mark.usefixtures("get_index_mock")
    def test_update_index_embeddings(self, update_index_embeddings_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_index = aiplatform.MatchingEngineIndex(index_name=_TEST_INDEX_ID)
        updated_index = my_index.update_embeddings(
            contents_delta_uri=_TEST_CONTENTS_DELTA_URI_UPDATE,
            is_complete_overwrite=_TEST_IS_COMPLETE_OVERWRITE_UPDATE,
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
    def test_create_tree_ah_index(self, create_index_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
            display_name=_TEST_INDEX_DISPLAY_NAME,
            contents_delta_uri=_TEST_CONTENTS_DELTA_URI,
            dimensions=_TEST_INDEX_CONFIG_DIMENSIONS,
            approximate_neighbors_count=_TEST_INDEX_APPROXIMATE_NEIGHBORS_COUNT,
            distance_measure_type=_TEST_INDEX_DISTANCE_MEASURE_TYPE,
            leaf_node_embedding_count=_TEST_LEAF_NODE_EMBEDDING_COUNT,
            leaf_nodes_to_search_percent=_TEST_LEAF_NODES_TO_SEARCH_PERCENT,
            description=_TEST_INDEX_DESCRIPTION,
            labels=_TEST_LABELS,
            sync=sync,
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
        )

    @pytest.mark.usefixtures("get_index_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_brute_force_index(self, create_index_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_index = aiplatform.MatchingEngineIndex.create_brute_force_index(
            display_name=_TEST_INDEX_DISPLAY_NAME,
            contents_delta_uri=_TEST_CONTENTS_DELTA_URI,
            dimensions=_TEST_INDEX_CONFIG_DIMENSIONS,
            distance_measure_type=_TEST_INDEX_DISTANCE_MEASURE_TYPE,
            description=_TEST_INDEX_DESCRIPTION,
            labels=_TEST_LABELS,
            sync=sync,
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
        )
