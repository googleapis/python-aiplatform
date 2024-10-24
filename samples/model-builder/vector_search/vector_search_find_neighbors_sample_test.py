# Copyright 2023 Google LLC
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

from unittest.mock import call

import test_constants as constants
from vector_search import vector_search_find_neighbors_sample


def test_vector_search_find_neighbors_sample(
    mock_sdk_init, mock_index_endpoint_init, mock_index_endpoint_find_neighbors
):
    vector_search_find_neighbors_sample.vector_search_find_neighbors(
        project=constants.PROJECT,
        location=constants.LOCATION,
        index_endpoint_name=constants.VECTOR_SEARCH_INDEX_ENDPOINT,
        deployed_index_id=constants.VECTOR_SEARCH_DEPLOYED_INDEX_ID,
        queries=constants.VECTOR_SERACH_INDEX_QUERIES,
        num_neighbors=10
    )

    # Check client initialization
    mock_sdk_init.assert_called_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    # Check index endpoint initialization with right index endpoint name
    mock_index_endpoint_init.assert_called_with(
        index_endpoint_name=constants.VECTOR_SEARCH_INDEX_ENDPOINT)

    # Check index_endpoint.find_neighbors is called with right params.
    mock_index_endpoint_find_neighbors.assert_has_calls(
        [
            call(
                deployed_index_id=constants.VECTOR_SEARCH_DEPLOYED_INDEX_ID,
                queries=constants.VECTOR_SERACH_INDEX_QUERIES,
                num_neighbors=10,
            ),
            call(
                deployed_index_id=constants.VECTOR_SEARCH_DEPLOYED_INDEX_ID,
                queries=constants.VECTOR_SERACH_INDEX_HYBRID_QUERIES,
                num_neighbors=10,
            ),
        ],
        any_order=False,
    )


def test_vector_search_find_neighbors_jwt_sample(
    mock_sdk_init, mock_index_endpoint_init, mock_index_endpoint_find_neighbors
):
    vector_search_find_neighbors_sample.vector_search_find_neighbors_jwt(
        project=constants.PROJECT,
        location=constants.LOCATION,
        index_endpoint_name=constants.VECTOR_SEARCH_INDEX_ENDPOINT,
        deployed_index_id=constants.VECTOR_SEARCH_DEPLOYED_INDEX_ID,
        queries=constants.VECTOR_SERACH_INDEX_QUERIES,
        num_neighbors=10,
        signed_jwt=constants.VECTOR_SEARCH_PRIVATE_ENDPOINT_SIGNED_JWT,
    )

    # Check client initialization
    mock_sdk_init.assert_called_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    # Check index endpoint initialization with right index endpoint name
    mock_index_endpoint_init.assert_called_with(
        index_endpoint_name=constants.VECTOR_SEARCH_INDEX_ENDPOINT)

    # Check index_endpoint.find_neighbors is called with right params.
    mock_index_endpoint_find_neighbors.assert_called_with(
        deployed_index_id=constants.VECTOR_SEARCH_DEPLOYED_INDEX_ID,
        queries=constants.VECTOR_SERACH_INDEX_QUERIES,
        num_neighbors=10,
        signed_jwt=constants.VECTOR_SEARCH_PRIVATE_ENDPOINT_SIGNED_JWT,
    )
