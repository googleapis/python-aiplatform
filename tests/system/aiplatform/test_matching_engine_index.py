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

import uuid

from google.cloud import aiplatform
from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import (
    Namespace,
)
from google.cloud import aiplatform_v1
from tests.system.aiplatform import e2e_base

# project
_TEST_INDEX_DISPLAY_NAME = "index_display_name"
_TEST_STREAM_INDEX_DISPLAY_NAME = "stream_index_display_name"
_TEST_INDEX_DESCRIPTION = "index_description"
_TEST_INDEX_DISTANCE_MEASURE_TYPE = "SQUARED_L2_DISTANCE"

_TEST_INDEX_CONFIG_DIMENSIONS = 100
_TEST_INDEX_APPROXIMATE_NEIGHBORS_COUNT = 150
_TEST_LEAF_NODE_EMBEDDING_COUNT = 123
_TEST_LEAF_NODES_TO_SEARCH_PERCENT = 50


_TEST_CONTENTS_DELTA_URI = (
    "gs://cloud-samples-data-us-central1/vertex-ai/matching_engine/glove100/initial"
)
_TEST_CONTENTS_DELTA_URI_UPDATE = (
    "gs://cloud-samples-data-us-central1/vertex-ai/matching_engine/glove100/incremental"
)
_TEST_IS_COMPLETE_OVERWRITE = True
_TEST_INDEX_DISTANCE_MEASURE_TYPE = "SQUARED_L2_DISTANCE"


_TEST_LABELS = {"my_key": "my_value"}
_TEST_DISPLAY_NAME_UPDATE = "my new display name"
_TEST_DESCRIPTION_UPDATE = "my description update"
_TEST_LABELS_UPDATE = {"my_key_update": "my_value_update"}

# ENDPOINT
_TEST_INDEX_ENDPOINT_DISPLAY_NAME = "endpoint_name"
_TEST_PUBLIC_INDEX_ENDPOINT_DISPLAY_NAME = "public_endpoint_name"
_TEST_INDEX_ENDPOINT_DESCRIPTION = "my endpoint"
_TEST_PUBLIC_INDEX_ENDPOINT_DESCRIPTION = "my public endpoint"

# DEPLOYED INDEX
_TEST_DEPLOYED_INDEX_ID = f"deployed_index_id_{uuid.uuid4()}".replace("-", "_")
_TEST_DEPLOYED_INDEX_DISPLAY_NAME = f"deployed_index_display_name_{uuid.uuid4()}"
_TEST_DEPLOYED_INDEX_ID_PUBLIC = f"deployed_index_id_{uuid.uuid4()}".replace("-", "_")
_TEST_DEPLOYED_INDEX_DISPLAY_NAME_PUBLIC = f"deployed_index_display_name_{uuid.uuid4()}"
_TEST_DEPLOYED_STREAM_INDEX_ID = f"deployed_index_id_{uuid.uuid4()}".replace("-", "_")
_TEST_DEPLOYED_STREAM_INDEX_DISPLAY_NAME = f"deployed_index_display_name_{uuid.uuid4()}"
_TEST_DEPLOYED_STREAM_INDEX_ID_PUBLIC = f"deployed_index_id_{uuid.uuid4()}".replace(
    "-", "_"
)
_TEST_DEPLOYED_STREAM_INDEX_DISPLAY_NAME_PUBLIC = (
    f"deployed_index_display_name_{uuid.uuid4()}"
)
_TEST_MIN_REPLICA_COUNT_UPDATED = 4
_TEST_MAX_REPLICA_COUNT_UPDATED = 4

# QUERY
_TEST_MATCH_QUERY = query = [
    -0.11333,
    0.48402,
    0.090771,
    -0.22439,
    0.034206,
    -0.55831,
    0.041849,
    -0.53573,
    0.18809,
    -0.58722,
    0.015313,
    -0.014555,
    0.80842,
    -0.038519,
    0.75348,
    0.70502,
    -0.17863,
    0.3222,
    0.67575,
    0.67198,
    0.26044,
    0.4187,
    -0.34122,
    0.2286,
    -0.53529,
    1.2582,
    -0.091543,
    0.19716,
    -0.037454,
    -0.3336,
    0.31399,
    0.36488,
    0.71263,
    0.1307,
    -0.24654,
    -0.52445,
    -0.036091,
    0.55068,
    0.10017,
    0.48095,
    0.71104,
    -0.053462,
    0.22325,
    0.30917,
    -0.39926,
    0.036634,
    -0.35431,
    -0.42795,
    0.46444,
    0.25586,
    0.68257,
    -0.20821,
    0.38433,
    0.055773,
    -0.2539,
    -0.20804,
    0.52522,
    -0.11399,
    -0.3253,
    -0.44104,
    0.17528,
    0.62255,
    0.50237,
    -0.7607,
    -0.071786,
    0.0080131,
    -0.13286,
    0.50097,
    0.18824,
    -0.54722,
    -0.42664,
    0.4292,
    0.14877,
    -0.0072514,
    -0.16484,
    -0.059798,
    0.9895,
    -0.61738,
    0.054169,
    0.48424,
    -0.35084,
    -0.27053,
    0.37829,
    0.11503,
    -0.39613,
    0.24266,
    0.39147,
    -0.075256,
    0.65093,
    -0.20822,
    -0.17456,
    0.53571,
    -0.16537,
    0.13582,
    -0.56016,
    0.016964,
    0.1277,
    0.94071,
    -0.22608,
    -0.021106,
]

_TEST_FILTER = [Namespace("name", ["allow_token"], ["deny_token"])]


# STREAM UPDATE
_TEST_DATAPOINT_1 = aiplatform_v1.types.index.IndexDatapoint(
    datapoint_id="upsert_0",
    feature_vector=_TEST_MATCH_QUERY,
    restricts=[
        aiplatform_v1.types.index.IndexDatapoint.Restriction(
            namespace="Color", allow_list=["red"]
        )
    ],
    numeric_restricts=[
        aiplatform_v1.types.index.IndexDatapoint.NumericRestriction(
            namespace="cost",
            value_int=1,
        )
    ],
)
_TEST_DATAPOINT_2 = aiplatform_v1.types.index.IndexDatapoint(
    datapoint_id="upsert_1",
    feature_vector=_TEST_MATCH_QUERY,
    numeric_restricts=[
        aiplatform_v1.types.index.IndexDatapoint.NumericRestriction(
            namespace="cost",
            value_double=0.1,
        )
    ],
    crowding_tag=aiplatform_v1.types.index.IndexDatapoint.CrowdingTag(
        crowding_attribute="crowding"
    ),
)
_TEST_DATAPOINT_3 = aiplatform_v1.types.index.IndexDatapoint(
    datapoint_id="5",
    feature_vector=_TEST_MATCH_QUERY,
    numeric_restricts=[
        aiplatform_v1.types.index.IndexDatapoint.NumericRestriction(
            namespace="cost",
            value_float=1.1,
        )
    ],
)
_TEST_STREAM_INDEX_DATAPOINTS = [
    _TEST_DATAPOINT_1,
    _TEST_DATAPOINT_2,
    _TEST_DATAPOINT_3,
]


class TestMatchingEngine(e2e_base.TestEndToEnd):

    _temp_prefix = "temp_vertex_sdk_e2e_matching_engine_test"

    def test_create_get_list_matching_engine_index(self, shared_state):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        # Clean up resources from previous test runs.
        for index_endpoint in aiplatform.MatchingEngineIndexEndpoint.list():
            for deployed_index in index_endpoint.deployed_indexes:
                index_endpoint.undeploy_index(deployed_index_id=deployed_index.id)
            index_endpoint.delete()

        for index in aiplatform.MatchingEngineIndex.list():
            index.delete()

        # Create an index
        index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
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

        # Create index and check that it is listed
        list_indexes = aiplatform.MatchingEngineIndex.list()
        assert get_index.resource_name in [
            index.resource_name for index in list_indexes
        ]

        # Update the index metadata
        updated_index = get_index.update_metadata(
            display_name=_TEST_DISPLAY_NAME_UPDATE,
            description=_TEST_DESCRIPTION_UPDATE,
            labels=_TEST_LABELS_UPDATE,
        )

        assert updated_index.name == get_index.name
        # TODO: Reinstate assertions once b/220005272 is fixed.
        # assert updated_index.display_name == _TEST_DISPLAY_NAME_UPDATE
        # assert updated_index.description == _TEST_DESCRIPTION_UPDATE
        # assert updated_index.labels == _TEST_LABELS_UPDATE

        # Update the index embeddings
        updated_index = get_index.update_embeddings(
            contents_delta_uri=_TEST_CONTENTS_DELTA_URI_UPDATE,
            is_complete_overwrite=_TEST_IS_COMPLETE_OVERWRITE,
        )

        assert updated_index.name == get_index.name

        # Create endpoint and check that it is listed
        psa_index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
            display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
            description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
            network=e2e_base._VPC_NETWORK_URI,
            labels=_TEST_LABELS,
        )
        assert psa_index_endpoint.resource_name in [
            index_endpoint.resource_name
            for index_endpoint in aiplatform.MatchingEngineIndexEndpoint.list()
        ]

        assert psa_index_endpoint.labels == _TEST_LABELS
        assert psa_index_endpoint.display_name == _TEST_INDEX_ENDPOINT_DISPLAY_NAME
        assert psa_index_endpoint.description == _TEST_INDEX_ENDPOINT_DESCRIPTION

        # Create endpoint and check that it is listed
        public_index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
            display_name=_TEST_PUBLIC_INDEX_ENDPOINT_DISPLAY_NAME,
            description=_TEST_PUBLIC_INDEX_ENDPOINT_DESCRIPTION,
            public_endpoint_enabled=True,
            labels=_TEST_LABELS,
        )
        assert public_index_endpoint.resource_name in [
            index_endpoint.resource_name
            for index_endpoint in aiplatform.MatchingEngineIndexEndpoint.list()
        ]

        assert public_index_endpoint.labels == _TEST_LABELS
        assert (
            public_index_endpoint.display_name
            == _TEST_PUBLIC_INDEX_ENDPOINT_DISPLAY_NAME
        )
        assert (
            public_index_endpoint.description == _TEST_PUBLIC_INDEX_ENDPOINT_DESCRIPTION
        )

        shared_state["resources"].append(psa_index_endpoint)

        # Deploy endpoint
        psa_index_endpoint = psa_index_endpoint.deploy_index(
            index=index,
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
            display_name=_TEST_DEPLOYED_INDEX_DISPLAY_NAME,
        )

        # Deploy public endpoint
        public_index_endpoint = public_index_endpoint.deploy_index(
            index=index,
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID_PUBLIC,
            display_name=_TEST_DEPLOYED_INDEX_DISPLAY_NAME_PUBLIC,
            min_replica_count=_TEST_MIN_REPLICA_COUNT_UPDATED,
            max_replica_count=_TEST_MAX_REPLICA_COUNT_UPDATED,
        )

        # Update endpoint
        updated_index_endpoint = psa_index_endpoint.update(
            display_name=_TEST_DISPLAY_NAME_UPDATE,
            description=_TEST_DESCRIPTION_UPDATE,
            labels=_TEST_LABELS_UPDATE,
        )

        assert updated_index_endpoint.labels == _TEST_LABELS_UPDATE
        assert updated_index_endpoint.display_name == _TEST_DISPLAY_NAME_UPDATE
        assert updated_index_endpoint.description == _TEST_DESCRIPTION_UPDATE

        # Mutate deployed index
        psa_index_endpoint.mutate_deployed_index(
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
            min_replica_count=_TEST_MIN_REPLICA_COUNT_UPDATED,
            max_replica_count=_TEST_MAX_REPLICA_COUNT_UPDATED,
        )

        # deployed index on private endpoint.
        deployed_index = psa_index_endpoint.deployed_indexes[0]

        assert deployed_index.id == _TEST_DEPLOYED_INDEX_ID
        assert deployed_index.index == index.resource_name
        assert (
            deployed_index.automatic_resources.min_replica_count
            == _TEST_MIN_REPLICA_COUNT_UPDATED
        )
        assert (
            deployed_index.automatic_resources.max_replica_count
            == _TEST_MAX_REPLICA_COUNT_UPDATED
        )

        # deployed index on public endpoint.
        deployed_index_public = public_index_endpoint.deployed_indexes[0]

        assert deployed_index_public.id == _TEST_DEPLOYED_INDEX_ID_PUBLIC
        assert deployed_index_public.index == index.resource_name
        assert (
            deployed_index_public.automatic_resources.min_replica_count
            == _TEST_MIN_REPLICA_COUNT_UPDATED
        )
        assert (
            deployed_index_public.automatic_resources.max_replica_count
            == _TEST_MAX_REPLICA_COUNT_UPDATED
        )

        # TODO: Test `psa_index_endpoint.match` request. This requires running this test in a VPC.
        # results = psa_index_endpoint.match(
        #     deployed_index_id=_TEST_DEPLOYED_INDEX_ID, queries=[_TEST_MATCH_QUERY]
        # )

        # assert results[0][0].id == 870

        # TODO: Test `psa_index_endpoint.match` with filter.
        # This requires uploading a new content of the Matching Engine Index to Cloud Storage.
        # results = psa_index_endpoint.match(
        #     deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
        #     queries=[_TEST_MATCH_QUERY],
        #     num_neighbors=1,
        #     filter=_TEST_FILTER,
        # )
        # assert results[0][0].id == 9999

        # FindNeighbors query for public index
        results = public_index_endpoint.find_neighbors(
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID_PUBLIC,
            queries=[_TEST_MATCH_QUERY],
        )
        assert results[0][0].id == "0"

        # Undeploy index from private endpoint
        psa_index_endpoint = psa_index_endpoint.undeploy_index(
            deployed_index_id=deployed_index.id
        )

        # Undeploy index from public endpoint
        public_index_endpoint = public_index_endpoint.undeploy_index(
            deployed_index_id=deployed_index_public.id
        )

        # Delete index and check that it is no longer listed
        index.delete()
        list_indexes = aiplatform.MatchingEngineIndex.list()
        assert get_index.resource_name not in [
            index.resource_name for index in list_indexes
        ]

        # Delete index endpoint and check that it is no longer listed
        psa_index_endpoint.delete()
        assert psa_index_endpoint.resource_name not in [
            index_endpoint.resource_name
            for index_endpoint in aiplatform.MatchingEngineIndexEndpoint.list()
        ]

        # Delete public index endpoint
        public_index_endpoint.delete()
        assert public_index_endpoint.resource_name not in [
            index_endpoint.resource_name
            for index_endpoint in aiplatform.MatchingEngineIndexEndpoint.list()
        ]

    def test_matching_engine_stream_index(self, shared_state):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        # Clean up resources from previous test runs.
        for index_endpoint in aiplatform.MatchingEngineIndexEndpoint.list():
            for deployed_index in index_endpoint.deployed_indexes:
                index_endpoint.undeploy_index(deployed_index_id=deployed_index.id)
            index_endpoint.delete()

        for index in aiplatform.MatchingEngineIndex.list():
            index.delete()

        # Create an index
        stream_index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
            display_name=_TEST_STREAM_INDEX_DISPLAY_NAME,
            contents_delta_uri=_TEST_CONTENTS_DELTA_URI,
            dimensions=_TEST_INDEX_CONFIG_DIMENSIONS,
            approximate_neighbors_count=_TEST_INDEX_APPROXIMATE_NEIGHBORS_COUNT,
            distance_measure_type=_TEST_INDEX_DISTANCE_MEASURE_TYPE,
            leaf_node_embedding_count=_TEST_LEAF_NODE_EMBEDDING_COUNT,
            leaf_nodes_to_search_percent=_TEST_LEAF_NODES_TO_SEARCH_PERCENT,
            description=_TEST_INDEX_DESCRIPTION,
            labels=_TEST_LABELS,
            index_update_method="STREAM_UPDATE",
        )

        shared_state["resources"].append(stream_index)
        shared_state["stream_index"] = stream_index
        shared_state["stream_index_name"] = stream_index.resource_name

        # Verify that the retrieved index is the same
        get_index = aiplatform.MatchingEngineIndex(
            index_name=stream_index.resource_name
        )
        assert stream_index.resource_name == get_index.resource_name

        # Create index and check that it is listed
        list_indexes = aiplatform.MatchingEngineIndex.list()
        assert get_index.resource_name in [
            index.resource_name for index in list_indexes
        ]

        # Update the index metadata
        updated_index = get_index.update_metadata(
            display_name=_TEST_DISPLAY_NAME_UPDATE,
            description=_TEST_DESCRIPTION_UPDATE,
            labels=_TEST_LABELS_UPDATE,
        )

        assert updated_index.name == get_index.name

        # Update the index embeddings
        updated_index = get_index.update_embeddings(
            contents_delta_uri=_TEST_CONTENTS_DELTA_URI_UPDATE,
            is_complete_overwrite=_TEST_IS_COMPLETE_OVERWRITE,
        )

        assert updated_index.name == get_index.name

        # Create endpoint and check that it is listed
        psa_index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
            display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
            description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
            network=e2e_base._VPC_NETWORK_URI,
            labels=_TEST_LABELS,
        )
        assert psa_index_endpoint.resource_name in [
            index_endpoint.resource_name
            for index_endpoint in aiplatform.MatchingEngineIndexEndpoint.list()
        ]

        assert psa_index_endpoint.labels == _TEST_LABELS
        assert psa_index_endpoint.display_name == _TEST_INDEX_ENDPOINT_DISPLAY_NAME
        assert psa_index_endpoint.description == _TEST_INDEX_ENDPOINT_DESCRIPTION

        # Create endpoint and check that it is listed
        public_index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
            display_name=_TEST_PUBLIC_INDEX_ENDPOINT_DISPLAY_NAME,
            description=_TEST_PUBLIC_INDEX_ENDPOINT_DESCRIPTION,
            public_endpoint_enabled=True,
            labels=_TEST_LABELS,
        )
        assert public_index_endpoint.resource_name in [
            index_endpoint.resource_name
            for index_endpoint in aiplatform.MatchingEngineIndexEndpoint.list()
        ]

        assert public_index_endpoint.labels == _TEST_LABELS
        assert (
            public_index_endpoint.display_name
            == _TEST_PUBLIC_INDEX_ENDPOINT_DISPLAY_NAME
        )
        assert (
            public_index_endpoint.description == _TEST_PUBLIC_INDEX_ENDPOINT_DESCRIPTION
        )

        shared_state["resources"].append(psa_index_endpoint)

        # Deploy endpoint
        psa_index_endpoint = psa_index_endpoint.deploy_index(
            index=stream_index,
            deployed_index_id=_TEST_DEPLOYED_STREAM_INDEX_ID,
            display_name=_TEST_DEPLOYED_INDEX_DISPLAY_NAME,
        )

        # Deploy public endpoint
        public_index_endpoint = public_index_endpoint.deploy_index(
            index=stream_index,
            deployed_index_id=_TEST_DEPLOYED_STREAM_INDEX_ID_PUBLIC,
            display_name=_TEST_DEPLOYED_INDEX_DISPLAY_NAME_PUBLIC,
            min_replica_count=_TEST_MIN_REPLICA_COUNT_UPDATED,
            max_replica_count=_TEST_MAX_REPLICA_COUNT_UPDATED,
        )

        # Update endpoint
        updated_index_endpoint = psa_index_endpoint.update(
            display_name=_TEST_DISPLAY_NAME_UPDATE,
            description=_TEST_DESCRIPTION_UPDATE,
            labels=_TEST_LABELS_UPDATE,
        )

        assert updated_index_endpoint.labels == _TEST_LABELS_UPDATE
        assert updated_index_endpoint.display_name == _TEST_DISPLAY_NAME_UPDATE
        assert updated_index_endpoint.description == _TEST_DESCRIPTION_UPDATE

        # Mutate deployed index
        psa_index_endpoint.mutate_deployed_index(
            deployed_index_id=_TEST_DEPLOYED_STREAM_INDEX_ID,
            min_replica_count=_TEST_MIN_REPLICA_COUNT_UPDATED,
            max_replica_count=_TEST_MAX_REPLICA_COUNT_UPDATED,
        )

        # deployed index on private endpoint.
        deployed_index = psa_index_endpoint.deployed_indexes[0]

        assert deployed_index.id == _TEST_DEPLOYED_STREAM_INDEX_ID
        assert deployed_index.index == stream_index.resource_name
        assert (
            deployed_index.automatic_resources.min_replica_count
            == _TEST_MIN_REPLICA_COUNT_UPDATED
        )
        assert (
            deployed_index.automatic_resources.max_replica_count
            == _TEST_MAX_REPLICA_COUNT_UPDATED
        )

        # deployed index on public endpoint.
        deployed_index_public = public_index_endpoint.deployed_indexes[0]

        assert deployed_index_public.id == _TEST_DEPLOYED_STREAM_INDEX_ID_PUBLIC
        assert deployed_index_public.index == stream_index.resource_name
        assert (
            deployed_index_public.automatic_resources.min_replica_count
            == _TEST_MIN_REPLICA_COUNT_UPDATED
        )
        assert (
            deployed_index_public.automatic_resources.max_replica_count
            == _TEST_MAX_REPLICA_COUNT_UPDATED
        )

        # TODO: Test `psa_index_endpoint.match` request. This requires running this test in a VPC.
        # results = psa_index_endpoint.match(
        #     deployed_index_id=_TEST_DEPLOYED_INDEX_ID, queries=[_TEST_MATCH_QUERY]
        # )

        # assert results[0][0].id == 870

        # TODO: Test `psa_index_endpoint.match` with filter.
        # This requires uploading a new content of the Matching Engine Index to Cloud Storage.
        # results = psa_index_endpoint.match(
        #     deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
        #     queries=[_TEST_MATCH_QUERY],
        #     num_neighbors=1,
        #     filter=_TEST_FILTER,
        # )
        # assert results[0][0].id == 9999

        # Upsert datapoint to stream index
        stream_index.upsert_datapoints(datapoints=_TEST_STREAM_INDEX_DATAPOINTS)

        # Remove datapoint upserted to stream index
        stream_index.remove_datapoints(datapoint_ids="upsert_0")

        # Undeploy index from private endpoint
        psa_index_endpoint = psa_index_endpoint.undeploy_index(
            deployed_index_id=deployed_index.id
        )

        # Undeploy index from public endpoint
        public_index_endpoint = public_index_endpoint.undeploy_index(
            deployed_index_id=deployed_index_public.id
        )

        # Delete index and check that it is no longer listed
        stream_index.delete()
        list_indexes = aiplatform.MatchingEngineIndex.list()
        assert get_index.resource_name not in [
            index.resource_name for index in list_indexes
        ]

        # Delete index endpoint and check that it is no longer listed
        psa_index_endpoint.delete()
        assert psa_index_endpoint.resource_name not in [
            index_endpoint.resource_name
            for index_endpoint in aiplatform.MatchingEngineIndexEndpoint.list()
        ]

        # Delete public index endpoint
        public_index_endpoint.delete()
        assert public_index_endpoint.resource_name not in [
            index_endpoint.resource_name
            for index_endpoint in aiplatform.MatchingEngineIndexEndpoint.list()
        ]
