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

from unittest import mock

import test_constants as constants
from vector_search import vector_search_match_sample


def test_vector_search_match_hybrid_queries_sample(
    mock_sdk_init, mock_index_endpoint_init, mock_index_endpoint_match
):
    vector_search_match_sample.vector_search_match_hybrid_queries(
        project=constants.PROJECT,
        location=constants.LOCATION,
        index_endpoint_name=constants.VECTOR_SEARCH_INDEX_ENDPOINT,
        deployed_index_id=constants.VECTOR_SEARCH_DEPLOYED_INDEX_ID,
        num_neighbors=10,
    )

    # Check client initialization
    mock_sdk_init.assert_called_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    # Check index endpoint initialization with right index endpoint name
    mock_index_endpoint_init.assert_called_with(
        index_endpoint_name=constants.VECTOR_SEARCH_INDEX_ENDPOINT)

    # Check index_endpoint.match is called with right params.
    mock_index_endpoint_match.assert_called_with(
        deployed_index_id=constants.VECTOR_SEARCH_DEPLOYED_INDEX_ID,
        queries=mock.ANY,
        num_neighbors=10,
    )


def test_vector_search_match_jwt_sample(
    mock_sdk_init, mock_index_endpoint_init, mock_index_endpoint_match
):
    vector_search_match_sample.vector_search_match_jwt(
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

    # Check index_endpoint.match is called with right params.
    mock_index_endpoint_match.assert_called_with(
        deployed_index_id=constants.VECTOR_SEARCH_DEPLOYED_INDEX_ID,
        queries=constants.VECTOR_SERACH_INDEX_QUERIES,
        num_neighbors=10,
        signed_jwt=constants.VECTOR_SEARCH_PRIVATE_ENDPOINT_SIGNED_JWT,
    )


def test_vector_search_match_psc_manual_sample(
    mock_sdk_init,
    mock_index_endpoint,
    mock_index_endpoint_init,
    mock_index_endpoint_match
):
    vector_search_match_sample.vector_search_match_psc_manual(
        project=constants.PROJECT,
        location=constants.LOCATION,
        index_endpoint_name=constants.VECTOR_SEARCH_INDEX_ENDPOINT,
        deployed_index_id=constants.VECTOR_SEARCH_DEPLOYED_INDEX_ID,
        queries=constants.VECTOR_SERACH_INDEX_QUERIES,
        num_neighbors=10,
        ip_address=constants.VECTOR_SEARCH_PSC_MANUAL_IP_ADDRESS,
    )

    # Check client initialization
    mock_sdk_init.assert_called_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    # Check index endpoint initialization with right index endpoint name
    mock_index_endpoint_init.assert_called_with(
        index_endpoint_name=constants.VECTOR_SEARCH_INDEX_ENDPOINT)

    # Check index endpoint PSC IP address is set
    assert mock_index_endpoint.private_service_connect_ip_address == (
        constants.VECTOR_SEARCH_PSC_MANUAL_IP_ADDRESS
    )

    # Check index_endpoint.match is called with right params.
    mock_index_endpoint_match.assert_called_with(
        deployed_index_id=constants.VECTOR_SEARCH_DEPLOYED_INDEX_ID,
        queries=constants.VECTOR_SERACH_INDEX_QUERIES,
        num_neighbors=10,
    )


def test_vector_search_match_psc_automation_sample(
    mock_sdk_init, mock_index_endpoint_init, mock_index_endpoint_match
):
    vector_search_match_sample.vector_search_match_psc_automation(
        project=constants.PROJECT,
        location=constants.LOCATION,
        index_endpoint_name=constants.VECTOR_SEARCH_INDEX_ENDPOINT,
        deployed_index_id=constants.VECTOR_SEARCH_DEPLOYED_INDEX_ID,
        queries=constants.VECTOR_SERACH_INDEX_QUERIES,
        num_neighbors=10,
        psc_network=constants.VECTOR_SEARCH_VPC_NETWORK,
    )

    # Check client initialization
    mock_sdk_init.assert_called_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    # Check index endpoint initialization with right index endpoint name
    mock_index_endpoint_init.assert_called_with(
        index_endpoint_name=constants.VECTOR_SEARCH_INDEX_ENDPOINT)

    # Check index_endpoint.match is called with right params.
    mock_index_endpoint_match.assert_called_with(
        deployed_index_id=constants.VECTOR_SEARCH_DEPLOYED_INDEX_ID,
        queries=constants.VECTOR_SERACH_INDEX_QUERIES,
        num_neighbors=10,
        psc_network=constants.VECTOR_SEARCH_VPC_NETWORK,
    )
