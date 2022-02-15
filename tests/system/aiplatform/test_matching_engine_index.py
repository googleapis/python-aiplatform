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

from datetime import datetime

from google.cloud import aiplatform
from tests.system.aiplatform import e2e_base
from google.cloud.aiplatform.compat.types import (
    matching_engine_index_endpoint as gca_matching_engine_index_endpoint,
)

# project
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"

_TEST_INDEX_ID = "index_id"
_TEST_INDEX_DISPLAY_NAME = f"index_display_name"
_TEST_INDEX_DESCRIPTION = f"index_description"
_TEST_INDEX_DISTANCE_MEASURE_TYPE = "SQUARED_L2_DISTANCE"

_TEST_INDEX_CONFIG_DIMENSIONS = 100
_TEST_INDEX_APPROXIMATE_NEIGHBORS_COUNT = 150
_TEST_LEAF_NODE_EMBEDDING_COUNT = 123
_TEST_LEAF_NODES_TO_SEARCH_PERCENT = 50


_TEST_CONTENTS_DELTA_URI = f"gs://ivanmkc-test2/matching-engine/initial"
_TEST_CONTENTS_DELTA_URI_UPDATE = "gs://y-test2/matching-engine/incremental"
_TEST_IS_COMPLETE_OVERWRITE = True
_TEST_INDEX_DISTANCE_MEASURE_TYPE = "SQUARED_L2_DISTANCE"


_TEST_LABELS = {"my_key": "my_value"}
_TEST_DISPLAY_NAME_UPDATE = "my new display name"
_TEST_DESCRIPTION_UPDATE = "my description update"
_TEST_LABELS_UPDATE = {"my_key_update": "my_value_update"}

_TEST_INDEX_ENDPOINT_ID = "index_endpoint_id"
_TEST_DEPLOYED_INDEX_ID = f"deployed_index_id"
_TEST_DEPLOYED_INDEX_DISPLAY_NAME = f"deployed_index_display_name"
_TEST_DEPLOYED_INDEX_DISPLAY_NAME_UPDATED = f"deployed_index_display_name_updated"
_TEST_MIN_REPLICA_COUNT_UPDATED = 4
_TEST_MAX_REPLICA_COUNT_UPDATED = 4
_TEST_ENABLE_ACCESS_LOGGING_UPDATED = True
_TEST_RESERVED_IP_RANGES_UPDATED = [
    "vertex-ai-ip-range-1-updated",
    "vertex-ai-ip-range-2-updated",
]
_TEST_DEPLOYMENT_GROUP_UPDATED = "prod-updated"
_TEST_AUTH_CONFIG_AUDIENCES_UPDATED = ["a-updated", "b-updated"]
_TEST_AUTH_CONFIG_ALLOWED_ISSUERS_UPDATED = [
    "service-account-name-1-updated@project-id.iam.gserviceaccount.com",
    "service-account-name-2-updated@project-id.iam.gserviceaccount.com",
]


class TestMatchingEngine(e2e_base.TestEndToEnd):

    _temp_prefix = "temp_vertex_sdk_e2e_matching_engine_test"


def test_create_get_list_matching_engine_index(self, shared_state):
    aiplatform.init(
        project=e2e_base._PROJECT, location=e2e_base._LOCATION,
    )

    # Generate random timestamp
    TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M%S")
    index_id = f"{_TEST_INDEX_ID}_{TIMESTAMP}"

    # Create an index
    index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
        index_id=index_id,
        display_name=_TEST_INDEX_DISPLAY_NAME,
        contents_delta_uri=_TEST_CONTENTS_DELTA_URI,
        dimensions=_TEST_INDEX_CONFIG_DIMENSIONS,
        approximate_neighbors_count=_TEST_INDEX_APPROXIMATE_NEIGHBORS_COUNT,
        distance_measure_type=_TEST_INDEX_DISTANCE_MEASURE_TYPE,
        leaf_node_embedding_count=_TEST_LEAF_NODE_EMBEDDING_COUNT,
        leaf_nodes_to_search_percent=_TEST_LEAF_NODES_TO_SEARCH_PERCENT,
        description=_TEST_INDEX_DESCRIPTION,
        labels=_TEST_LABELS,
    )

    shared_state["resources"] = [index]
    shared_state["index"] = index
    shared_state["index_name"] = index.resource_name

    # Verify that the retrieved index is the same
    get_index = aiplatform.MatchingEngineIndex(index_name=index.resource_name)
    assert index.resource_name == get_index.resource_name

    # Verify that the index count has increased
    list_indexes = aiplatform.MatchingEngineIndex.list()
    assert get_index.resource_name in [index.resource_name for index in list_indexes]

    # Update the index metadata
    updated_index = get_index.update_metadata(
        display_name=_TEST_DISPLAY_NAME_UPDATE,
        description=_TEST_DESCRIPTION_UPDATE,
        labels=_TEST_LABELS_UPDATE,
    )

    assert updated_index.display_name == _TEST_DISPLAY_NAME_UPDATE
    assert updated_index.description == _TEST_DESCRIPTION_UPDATE
    assert updated_index.labels == _TEST_LABELS

    # Update the index embeddings
    updated_index = get_index.update_embeddings(
        contents_delta_uri=_TEST_CONTENTS_DELTA_URI_UPDATE,
        is_complete_overwrite=_TEST_IS_COMPLETE_OVERWRITE,
    )

    assert updated_index.contents_delta_uri == _TEST_CONTENTS_DELTA_URI

    # Create endpoint
    my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
        index_endpoint_name=_TEST_INDEX_ENDPOINT_ID
    )

    # Deploy endpoint
    my_index_endpoint = my_index_endpoint.deploy_index(
        index=index,
        deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
        display_name=_TEST_DEPLOYED_INDEX_DISPLAY_NAME,
    )

    # Update endpoint
    updated_index_endpoint = my_index_endpoint.update(
        display_name=_TEST_DISPLAY_NAME_UPDATE,
        description=_TEST_DESCRIPTION_UPDATE,
        labels=_TEST_LABELS_UPDATE,
    )

    assert updated_index_endpoint.display_name == _TEST_DISPLAY_NAME_UPDATE
    assert updated_index_endpoint.description == _TEST_DESCRIPTION_UPDATE
    assert updated_index_endpoint.labels == _TEST_LABELS

    # Mutate deployed index
    my_index_endpoint.mutate_deployed_index(
        index_id=index.id,
        deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
        display_name=_TEST_DEPLOYED_INDEX_DISPLAY_NAME_UPDATED,
        min_replica_count=_TEST_MIN_REPLICA_COUNT_UPDATED,
        max_replica_count=_TEST_MAX_REPLICA_COUNT_UPDATED,
        enable_access_logging=_TEST_ENABLE_ACCESS_LOGGING_UPDATED,
        reserved_ip_ranges=_TEST_RESERVED_IP_RANGES_UPDATED,
        deployment_group=_TEST_DEPLOYMENT_GROUP_UPDATED,
        auth_config_audiences=_TEST_AUTH_CONFIG_AUDIENCES_UPDATED,
        auth_config_allowed_issuers=_TEST_AUTH_CONFIG_ALLOWED_ISSUERS_UPDATED,
    )

    deployed_index = my_index_endpoint.deployed_indexes[0]

    assert deployed_index == gca_matching_engine_index_endpoint.DeployedIndex(
        id=_TEST_DEPLOYED_INDEX_ID,
        index=index.name,
        display_name=_TEST_DEPLOYED_INDEX_DISPLAY_NAME_UPDATED,
        enable_access_logging=_TEST_ENABLE_ACCESS_LOGGING_UPDATED,
        reserved_ip_ranges=_TEST_RESERVED_IP_RANGES_UPDATED,
        deployment_group=_TEST_DEPLOYMENT_GROUP_UPDATED,
        automatic_resources={
            "min_replica_count": _TEST_MIN_REPLICA_COUNT_UPDATED,
            "max_replica_count": _TEST_MAX_REPLICA_COUNT_UPDATED,
        },
        deployed_index_auth_config=gca_matching_engine_index_endpoint.DeployedIndexAuthConfig(
            auth_provider=gca_matching_engine_index_endpoint.DeployedIndexAuthConfig.AuthProvider(
                audiences=_TEST_AUTH_CONFIG_AUDIENCES_UPDATED,
                allowed_issuers=_TEST_AUTH_CONFIG_ALLOWED_ISSUERS_UPDATED,
            )
        ),
    )

    # Undeploy endpoint
    my_index_endpoint = my_index_endpoint.undeploy_index(index=index)

    # Delete index and check that count has returned to the starting value
    index.delete()
    list_indexes = aiplatform.MatchingEngineIndex.list()
    assert get_index.resource_name not in [
        index.resource_name for index in list_indexes
    ]
