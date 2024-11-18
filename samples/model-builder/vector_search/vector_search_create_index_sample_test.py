# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest.mock import ANY

import test_constants as constants
from vector_search import vector_search_create_index_sample


def test_vector_search_create_index_sample(
    mock_sdk_init,
    mock_index_create_tree_ah_index,
):
    vector_search_create_index_sample.vector_search_create_index(
        project=constants.PROJECT,
        location=constants.LOCATION,
        display_name=constants.VECTOR_SEARCH_INDEX_DISPLAY_NAME,
        gcs_uri=constants.VECTOR_SEARCH_GCS_URI,
    )

    # Check client initialization
    mock_sdk_init.assert_called_with(
        project=constants.PROJECT,
        location=constants.LOCATION,
    )

    # Check index creation
    mock_index_create_tree_ah_index.assert_called_with(
        display_name=constants.VECTOR_SEARCH_INDEX_DISPLAY_NAME,
        contents_delta_uri=constants.VECTOR_SEARCH_GCS_URI,
        description=ANY,
        dimensions=ANY,
        approximate_neighbors_count=ANY,
        leaf_node_embedding_count=ANY,
        leaf_nodes_to_search_percent=ANY,
        index_update_method="BATCH_UPDATE",
        distance_measure_type=ANY,
    )


def test_vector_search_create_streaming_index_sample(
    mock_sdk_init,
    mock_index_create_tree_ah_index,
):
    vector_search_create_index_sample.vector_search_create_streaming_index(
        project=constants.PROJECT,
        location=constants.LOCATION,
        display_name=constants.VECTOR_SEARCH_INDEX_DISPLAY_NAME,
        gcs_uri=constants.VECTOR_SEARCH_GCS_URI,
    )

    # Check client initialization
    mock_sdk_init.assert_called_with(
        project=constants.PROJECT,
        location=constants.LOCATION,
    )

    # Check index creation
    mock_index_create_tree_ah_index.assert_called_with(
        display_name=constants.VECTOR_SEARCH_INDEX_DISPLAY_NAME,
        contents_delta_uri=constants.VECTOR_SEARCH_GCS_URI,
        description=ANY,
        dimensions=ANY,
        approximate_neighbors_count=ANY,
        leaf_node_embedding_count=ANY,
        leaf_nodes_to_search_percent=ANY,
        index_update_method="STREAM_UPDATE",
        distance_measure_type=ANY,
    )
