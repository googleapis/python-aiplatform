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
from importlib import reload
from unittest import mock
from unittest.mock import patch

from google.api_core import operation
from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.matching_engine._protos import match_service_pb2
from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import (
    Namespace,
    NumericNamespace,
    MatchNeighbor,
    HybridQuery,
)
from google.cloud.aiplatform.compat.types import (
    matching_engine_deployed_index_ref as gca_matching_engine_deployed_index_ref,
    index_endpoint as gca_index_endpoint,
    index as gca_index,
    match_service_v1beta1 as gca_match_service_v1beta1,
    index_v1beta1 as gca_index_v1beta1,
    service_networking as gca_service_networking,
    encryption_spec as gca_encryption_spec,
)
from google.cloud.aiplatform.compat.services import (
    index_endpoint_service_client,
    index_service_client,
    match_service_client_v1beta1,
)
import constants as test_constants

from google.protobuf import field_mask_pb2

import grpc

import pytest

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

# index_endpoint
_TEST_INDEX_ENDPOINT_ID = "index_endpoint_id"
_TEST_INDEX_ENDPOINT_PUBLIC_DNS = (
    "1114627793.us-central1-249381615684.vdb.vertexai.goog"
)
_TEST_INDEX_ENDPOINT_NAME = f"{_TEST_PARENT}/indexEndpoints/{_TEST_INDEX_ENDPOINT_ID}"
_TEST_INDEX_ENDPOINT_DISPLAY_NAME = "index_endpoint_display_name"
_TEST_INDEX_ENDPOINT_DESCRIPTION = "index_endpoint_description"
_TEST_INDEX_DESCRIPTION = test_constants.MatchingEngineConstants._TEST_INDEX_DESCRIPTION
_TEST_INDEX_ENDPOINT_VPC_NETWORK = "projects/{}/global/networks/{}".format(
    "12345", "network"
)

_TEST_LABELS = test_constants.MatchingEngineConstants._TEST_LABELS
_TEST_DISPLAY_NAME_UPDATE = (
    test_constants.MatchingEngineConstants._TEST_DISPLAY_NAME_UPDATE
)
_TEST_DESCRIPTION_UPDATE = (
    test_constants.MatchingEngineConstants._TEST_DESCRIPTION_UPDATE
)
_TEST_LABELS_UPDATE = test_constants.MatchingEngineConstants._TEST_LABELS_UPDATE

# deployment
_TEST_DEPLOYED_INDEX_ID = "deployed_index_id"
_TEST_DEPLOYED_INDEX_DISPLAY_NAME = "deployed_index_display_name"
_TEST_MIN_REPLICA_COUNT = 2
_TEST_MAX_REPLICA_COUNT = 2
_TEST_ENABLE_ACCESS_LOGGING = False
_TEST_RESERVED_IP_RANGES = ["vertex-ai-ip-range-1", "vertex-ai-ip-range-2"]
_TEST_DEPLOYMENT_GROUP = "prod"
_TEST_AUTH_CONFIG_AUDIENCES = ["a", "b"]
_TEST_AUTH_CONFIG_ALLOWED_ISSUERS = [
    "service-account-name-1@project-id.iam.gserviceaccount.com",
    "service-account-name-2@project-id.iam.gserviceaccount.com",
]

# deployment_updated
_TEST_MIN_REPLICA_COUNT_UPDATED = 4
_TEST_MAX_REPLICA_COUNT_UPDATED = 4

# request_metadata
_TEST_REQUEST_METADATA = test_constants.MatchingEngineConstants._TEST_REQUEST_METADATA

# Lists
_TEST_INDEX_ENDPOINT_LIST = [
    gca_index_endpoint.IndexEndpoint(
        name=_TEST_INDEX_ENDPOINT_NAME,
        display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
        description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
    ),
    gca_index_endpoint.IndexEndpoint(
        name=_TEST_INDEX_ENDPOINT_NAME,
        display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
        description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
    ),
    gca_index_endpoint.IndexEndpoint(
        name=_TEST_INDEX_ENDPOINT_NAME,
        display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
        description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
    ),
]

# Match
_TEST_QUERIES = [
    [
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
]
_TEST_QUERY_IDS = ["1", "2"]
_TEST_HYBRID_QUERIES = [
    HybridQuery(
        sparse_embedding_dimensions=[1, 2, 3],
        sparse_embedding_values=[0.1, 0.2, 0.3],
        rrf_ranking_alpha=0.2,
    ),
    HybridQuery(
        dense_embedding=_TEST_QUERIES[0],
        sparse_embedding_dimensions=[1, 2, 3],
        sparse_embedding_values=[0.1, 0.2, 0.3],
    ),
]
_TEST_NUM_NEIGHBOURS = 1
_TEST_FILTER = [
    Namespace(name="class", allow_tokens=["token_1"], deny_tokens=["token_2"])
]
_TEST_NUMERIC_FILTER = [
    NumericNamespace(name="cost", value_double=0.3, op="EQUAL"),
    NumericNamespace(name="size", value_int=0, op="GREATER"),
    NumericNamespace(name="seconds", value_float=-20.5, op="LESS_EQUAL"),
    NumericNamespace(name="duration", value_int=10, op="NOT_EQUAL"),
]
_TEST_NUMERIC_NAMESPACE = [
    match_service_pb2.NumericNamespace(name="cost", value_double=0.3, op=3),
    match_service_pb2.NumericNamespace(name="size", value_int=0, op=5),
    match_service_pb2.NumericNamespace(name="seconds", value_float=-20.5, op=2),
    match_service_pb2.NumericNamespace(name="duration", value_int=10, op="NOT_EQUAL"),
]
_TEST_IDS = ["123", "456", "789"]
_TEST_PER_CROWDING_ATTRIBUTE_NUM_NEIGHBOURS = 3
_TEST_APPROX_NUM_NEIGHBORS = 2
_TEST_FRACTION_LEAF_NODES_TO_SEARCH_OVERRIDE = 0.8
_TEST_RETURN_FULL_DATAPOINT = True
_TEST_LOW_LEVEL_BATCH_SIZE = 3
_TEST_ENCRYPTION_SPEC_KEY_NAME = "kms_key_name"
_TEST_PROJECT_ALLOWLIST = ["project-1", "project-2"]
_TEST_PRIVATE_SERVICE_CONNECT_IP_ADDRESS = "10.128.0.5"
_TEST_READ_INDEX_DATAPOINTS_RESPONSE = [
    gca_index_v1beta1.IndexDatapoint(
        datapoint_id="1",
        feature_vector=[1.0, 2.0, 3.0],
        restricts=[
            gca_index_v1beta1.IndexDatapoint.Restriction(
                namespace="class",
                allow_list=["token_1"],
                deny_list=["token_2"],
            )
        ],
    ),
    gca_index_v1beta1.IndexDatapoint(
        datapoint_id="2",
        feature_vector=[0, -1.0, 2.0],
        crowding_tag=gca_index_v1beta1.IndexDatapoint.CrowdingTag(
            crowding_attribute="1"
        ),
    ),
]
_TEST_PRIVATE_MATCH_NEIGHBOR_RESPONSE = [
    [
        MatchNeighbor(
            id="1",
            distance=0.1,
            feature_vector=[0.0, -1.0, 2.0],
            crowding_tag="0",
            restricts=[
                Namespace(
                    name="class",
                    allow_tokens=["token_1"],
                    deny_tokens=["token_2"],
                )
            ],
        ),
        MatchNeighbor(
            id="2",
            distance=0.1,
            feature_vector=[1.0, 2.0, 3.0],
            crowding_tag="0",
            restricts=[
                Namespace(
                    name="class",
                    allow_tokens=["token_1"],
                    deny_tokens=["token_2"],
                )
            ],
        ),
    ]
]
_TEST_TIMEOUT = 1800.0


def uuid_mock():
    return uuid.UUID(int=1)


# All index mocks
@pytest.fixture
def get_index_mock():
    with patch.object(
        index_service_client.IndexServiceClient, "get_index"
    ) as get_index_mock:
        index = gca_index.Index(
            name=_TEST_INDEX_NAME,
            display_name=_TEST_INDEX_DISPLAY_NAME,
            description=_TEST_INDEX_DESCRIPTION,
        )

        index.deployed_indexes = [
            gca_matching_engine_deployed_index_ref.DeployedIndexRef(
                index_endpoint=index.name,
                deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
            )
        ]

        get_index_mock.return_value = index
        yield get_index_mock


# All index_endpoint mocks
@pytest.fixture
def get_index_endpoint_mock():
    with patch.object(
        index_endpoint_service_client.IndexEndpointServiceClient, "get_index_endpoint"
    ) as get_index_endpoint_mock:
        index_endpoint = gca_index_endpoint.IndexEndpoint(
            name=_TEST_INDEX_ENDPOINT_NAME,
            display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
            description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
        )
        index_endpoint.deployed_indexes = [
            gca_index_endpoint.DeployedIndex(
                id=_TEST_DEPLOYED_INDEX_ID,
                index=_TEST_INDEX_NAME,
                display_name=_TEST_DEPLOYED_INDEX_DISPLAY_NAME,
                enable_access_logging=_TEST_ENABLE_ACCESS_LOGGING,
                reserved_ip_ranges=_TEST_RESERVED_IP_RANGES,
                deployment_group=_TEST_DEPLOYMENT_GROUP,
                automatic_resources={
                    "min_replica_count": _TEST_MIN_REPLICA_COUNT,
                    "max_replica_count": _TEST_MAX_REPLICA_COUNT,
                },
                deployed_index_auth_config=gca_index_endpoint.DeployedIndexAuthConfig(
                    auth_provider=gca_index_endpoint.DeployedIndexAuthConfig.AuthProvider(
                        audiences=_TEST_AUTH_CONFIG_AUDIENCES,
                        allowed_issuers=_TEST_AUTH_CONFIG_ALLOWED_ISSUERS,
                    )
                ),
            ),
            gca_index_endpoint.DeployedIndex(
                id=f"{_TEST_DEPLOYED_INDEX_ID}_2",
                index=f"{_TEST_INDEX_NAME}_2",
                display_name=_TEST_DEPLOYED_INDEX_DISPLAY_NAME,
                enable_access_logging=_TEST_ENABLE_ACCESS_LOGGING,
                reserved_ip_ranges=_TEST_RESERVED_IP_RANGES,
                deployment_group=_TEST_DEPLOYMENT_GROUP,
                automatic_resources={
                    "min_replica_count": _TEST_MIN_REPLICA_COUNT,
                    "max_replica_count": _TEST_MAX_REPLICA_COUNT,
                },
                deployed_index_auth_config=gca_index_endpoint.DeployedIndexAuthConfig(
                    auth_provider=gca_index_endpoint.DeployedIndexAuthConfig.AuthProvider(
                        audiences=_TEST_AUTH_CONFIG_AUDIENCES,
                        allowed_issuers=_TEST_AUTH_CONFIG_ALLOWED_ISSUERS,
                    )
                ),
            ),
        ]
        get_index_endpoint_mock.return_value = index_endpoint
        yield get_index_endpoint_mock


@pytest.fixture
def get_index_public_endpoint_mock():
    with patch.object(
        index_endpoint_service_client.IndexEndpointServiceClient, "get_index_endpoint"
    ) as get_index_public_endpoint_mock:
        index_endpoint = gca_index_endpoint.IndexEndpoint(
            name=_TEST_INDEX_ENDPOINT_NAME,
            display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
            description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
            public_endpoint_domain_name=_TEST_INDEX_ENDPOINT_PUBLIC_DNS,
        )
        index_endpoint.deployed_indexes = [
            gca_index_endpoint.DeployedIndex(
                id=_TEST_DEPLOYED_INDEX_ID,
                index=_TEST_INDEX_NAME,
                display_name=_TEST_DEPLOYED_INDEX_DISPLAY_NAME,
                enable_access_logging=_TEST_ENABLE_ACCESS_LOGGING,
                deployment_group=_TEST_DEPLOYMENT_GROUP,
                automatic_resources={
                    "min_replica_count": _TEST_MIN_REPLICA_COUNT,
                    "max_replica_count": _TEST_MAX_REPLICA_COUNT,
                },
                deployed_index_auth_config=gca_index_endpoint.DeployedIndexAuthConfig(
                    auth_provider=gca_index_endpoint.DeployedIndexAuthConfig.AuthProvider(
                        audiences=_TEST_AUTH_CONFIG_AUDIENCES,
                        allowed_issuers=_TEST_AUTH_CONFIG_ALLOWED_ISSUERS,
                    )
                ),
            ),
            gca_index_endpoint.DeployedIndex(
                id=f"{_TEST_DEPLOYED_INDEX_ID}_2",
                index=f"{_TEST_INDEX_NAME}_2",
                display_name=_TEST_DEPLOYED_INDEX_DISPLAY_NAME,
                enable_access_logging=_TEST_ENABLE_ACCESS_LOGGING,
                deployment_group=_TEST_DEPLOYMENT_GROUP,
                automatic_resources={
                    "min_replica_count": _TEST_MIN_REPLICA_COUNT,
                    "max_replica_count": _TEST_MAX_REPLICA_COUNT,
                },
                deployed_index_auth_config=gca_index_endpoint.DeployedIndexAuthConfig(
                    auth_provider=gca_index_endpoint.DeployedIndexAuthConfig.AuthProvider(
                        audiences=_TEST_AUTH_CONFIG_AUDIENCES,
                        allowed_issuers=_TEST_AUTH_CONFIG_ALLOWED_ISSUERS,
                    )
                ),
            ),
        ]
        get_index_public_endpoint_mock.return_value = index_endpoint
        yield get_index_public_endpoint_mock


@pytest.fixture
def deploy_index_mock():
    with patch.object(
        index_endpoint_service_client.IndexEndpointServiceClient,
        "deploy_index",
    ) as deploy_index_mock:
        deploy_index_lro_mock = mock.Mock(operation.Operation)
        deploy_index_mock.return_value = deploy_index_lro_mock
        yield deploy_index_mock


@pytest.fixture
def undeploy_index_mock():
    with patch.object(
        index_endpoint_service_client.IndexEndpointServiceClient,
        "undeploy_index",
    ) as undeploy_index_mock:
        undeploy_index_lro_mock = mock.Mock(operation.Operation)
        undeploy_index_mock.return_value = undeploy_index_lro_mock
        yield undeploy_index_mock


@pytest.fixture
def update_index_endpoint_mock():
    with patch.object(
        index_endpoint_service_client.IndexEndpointServiceClient,
        "update_index_endpoint",
    ) as index_endpoint_mock:
        index_endpoint_mock.return_value = gca_index_endpoint.IndexEndpoint(
            name=_TEST_INDEX_ENDPOINT_NAME,
            display_name=_TEST_DISPLAY_NAME_UPDATE,
            description=_TEST_DESCRIPTION_UPDATE,
            labels=_TEST_LABELS_UPDATE,
        )

        yield index_endpoint_mock


@pytest.fixture
def mutate_deployed_index_mock():
    with patch.object(
        index_endpoint_service_client.IndexEndpointServiceClient,
        "mutate_deployed_index",
    ) as mutate_deployed_index_mock:
        mutate_deployed_index_lro_mock = mock.Mock(operation.Operation)
        update_index_endpoint_mock.return_value = mutate_deployed_index_lro_mock
        yield mutate_deployed_index_mock


@pytest.fixture
def list_index_endpoints_mock():
    with patch.object(
        index_endpoint_service_client.IndexEndpointServiceClient, "list_index_endpoints"
    ) as list_index_endpoints_mock:
        list_index_endpoints_mock.return_value = _TEST_INDEX_ENDPOINT_LIST
        yield list_index_endpoints_mock


@pytest.fixture
def delete_index_endpoint_mock():
    with patch.object(
        index_endpoint_service_client.IndexEndpointServiceClient,
        "delete_index_endpoint",
    ) as delete_index_endpoint_mock:
        delete_index_endpoint_lro_mock = mock.Mock(operation.Operation)
        delete_index_endpoint_mock.return_value = delete_index_endpoint_lro_mock
        yield delete_index_endpoint_mock


@pytest.fixture
def create_index_endpoint_mock():
    with patch.object(
        index_endpoint_service_client.IndexEndpointServiceClient,
        "create_index_endpoint",
    ) as create_index_endpoint_mock:
        create_index_endpoint_lro_mock = mock.Mock(operation.Operation)
        create_index_endpoint_lro_mock.result.return_value = (
            gca_index_endpoint.IndexEndpoint(
                name=_TEST_INDEX_ENDPOINT_NAME,
                display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
                description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
            )
        )
        create_index_endpoint_mock.return_value = create_index_endpoint_lro_mock
        yield create_index_endpoint_mock


@pytest.fixture
def index_endpoint_match_queries_mock():
    with patch.object(
        grpc._channel._UnaryUnaryMultiCallable,
        "__call__",
    ) as index_endpoint_match_queries_mock:
        index_endpoint_match_queries_mock.return_value = (
            match_service_pb2.BatchMatchResponse(
                responses=[
                    match_service_pb2.BatchMatchResponse.BatchMatchResponsePerIndex(
                        deployed_index_id="1",
                        responses=[
                            match_service_pb2.MatchResponse(
                                neighbor=[
                                    match_service_pb2.MatchResponse.Neighbor(
                                        id="1", distance=0.1
                                    ),
                                    match_service_pb2.MatchResponse.Neighbor(
                                        id="2", distance=0.1
                                    ),
                                ],
                                embeddings=[
                                    match_service_pb2.Embedding(
                                        id="2",
                                        float_val=[1.0, 2.0, 3.0],
                                        restricts=[
                                            match_service_pb2.Namespace(
                                                name="class",
                                                allow_tokens=["token_1"],
                                                deny_tokens=["token_2"],
                                            )
                                        ],
                                        crowding_attribute=0,
                                    ),
                                    match_service_pb2.Embedding(
                                        id="1",
                                        float_val=[0, -1.0, 2.0],
                                        restricts=[
                                            match_service_pb2.Namespace(
                                                name="class",
                                                allow_tokens=["token_1"],
                                                deny_tokens=["token_2"],
                                            )
                                        ],
                                    ),
                                ],
                            )
                        ],
                    )
                ]
            )
        )
        yield index_endpoint_match_queries_mock


@pytest.fixture
def index_endpoint_batch_get_embeddings_mock():
    with patch.object(
        grpc._channel._UnaryUnaryMultiCallable,
        "__call__",
    ) as index_endpoint_batch_get_embeddings_mock:
        index_endpoint_batch_get_embeddings_mock.return_value = (
            match_service_pb2.BatchGetEmbeddingsResponse(
                embeddings=[
                    match_service_pb2.Embedding(
                        id="1",
                        float_val=[1.0, 2.0, 3.0],
                        restricts=[
                            match_service_pb2.Namespace(
                                name="class",
                                allow_tokens=["token_1"],
                                deny_tokens=["token_2"],
                            )
                        ],
                    ),
                    match_service_pb2.Embedding(
                        id="2",
                        float_val=[0, -1.0, 2.0],
                        crowding_attribute=1,
                    ),
                ]
            )
        )
        yield index_endpoint_batch_get_embeddings_mock


@pytest.fixture
def index_public_endpoint_match_queries_mock():
    with patch.object(
        match_service_client_v1beta1.MatchServiceClient, "find_neighbors"
    ) as index_public_endpoint_match_queries_mock:
        index_public_endpoint_match_queries_mock.return_value = (
            gca_match_service_v1beta1.FindNeighborsResponse(
                nearest_neighbors=[
                    gca_match_service_v1beta1.FindNeighborsResponse.NearestNeighbors(
                        id="1",
                        neighbors=[
                            gca_match_service_v1beta1.FindNeighborsResponse.Neighbor(
                                datapoint=gca_index_v1beta1.IndexDatapoint(
                                    datapoint_id="1"
                                ),
                                distance=0.1,
                            )
                        ],
                    )
                ]
            )
        )
        yield index_public_endpoint_match_queries_mock


@pytest.fixture
def index_public_endpoint_read_index_datapoints_mock():
    with patch.object(
        match_service_client_v1beta1.MatchServiceClient, "read_index_datapoints"
    ) as index_public_endpoint_read_index_datapoints_mock:
        index_public_endpoint_read_index_datapoints_mock.return_value = (
            gca_match_service_v1beta1.ReadIndexDatapointsResponse(
                datapoints=[
                    gca_index_v1beta1.IndexDatapoint(
                        datapoint_id="1",
                        feature_vector=[0, 1, 2, 3],
                    )
                ]
            )
        )
        yield index_public_endpoint_read_index_datapoints_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestMatchingEngineIndexEndpoint:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize(
        "index_endpoint_name", [_TEST_INDEX_ENDPOINT_ID, _TEST_INDEX_ENDPOINT_NAME]
    )
    def test_init_index_endpoint(self, index_endpoint_name, get_index_endpoint_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=index_endpoint_name
        )

        get_index_endpoint_mock.assert_called_once_with(
            name=my_index_endpoint.resource_name, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures("get_index_endpoint_mock")
    def test_update_index_endpoint(self, update_index_endpoint_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=_TEST_INDEX_ENDPOINT_ID
        )
        updated_endpoint = my_index_endpoint.update(
            display_name=_TEST_DISPLAY_NAME_UPDATE,
            description=_TEST_DESCRIPTION_UPDATE,
            labels=_TEST_LABELS_UPDATE,
            request_metadata=_TEST_REQUEST_METADATA,
            update_request_timeout=_TEST_TIMEOUT,
        )

        expected = gca_index_endpoint.IndexEndpoint(
            name=_TEST_INDEX_ENDPOINT_NAME,
            display_name=_TEST_DISPLAY_NAME_UPDATE,
            description=_TEST_DESCRIPTION_UPDATE,
            labels=_TEST_LABELS_UPDATE,
        )

        update_index_endpoint_mock.assert_called_once_with(
            index_endpoint=expected,
            update_mask=field_mask_pb2.FieldMask(
                paths=["labels", "display_name", "description"]
            ),
            metadata=_TEST_REQUEST_METADATA,
            timeout=_TEST_TIMEOUT,
        )

        assert updated_endpoint.gca_resource == expected

    def test_list_index_endpoints(self, list_index_endpoints_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_index_endpoints_list = aiplatform.MatchingEngineIndexEndpoint.list()

        list_index_endpoints_mock.assert_called_once_with(
            request={"parent": _TEST_PARENT}
        )
        assert len(my_index_endpoints_list) == len(_TEST_INDEX_ENDPOINT_LIST)
        for my_index_endpoint in my_index_endpoints_list:
            assert isinstance(my_index_endpoint, aiplatform.MatchingEngineIndexEndpoint)

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_index_endpoint_mock")
    def test_delete_index_endpoint(self, delete_index_endpoint_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=_TEST_INDEX_ENDPOINT_ID
        )
        my_index_endpoint.delete(sync=sync)

        if not sync:
            my_index_endpoint.wait()

        delete_index_endpoint_mock.assert_called_once_with(
            name=my_index_endpoint.resource_name
        )

    @pytest.mark.usefixtures("get_index_endpoint_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_index_endpoint(self, create_index_endpoint_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
            display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
            network=_TEST_INDEX_ENDPOINT_VPC_NETWORK,
            description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
            labels=_TEST_LABELS,
            create_request_timeout=_TEST_TIMEOUT,
        )

        if not sync:
            my_index_endpoint.wait()

        expected = gca_index_endpoint.IndexEndpoint(
            display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
            network=_TEST_INDEX_ENDPOINT_VPC_NETWORK,
            description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
            labels=_TEST_LABELS,
        )
        create_index_endpoint_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            index_endpoint=expected,
            metadata=_TEST_REQUEST_METADATA,
            timeout=_TEST_TIMEOUT,
        )

    @pytest.mark.usefixtures("get_index_endpoint_mock")
    def test_create_index_endpoint_with_private_service_connect(
        self, create_index_endpoint_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        aiplatform.MatchingEngineIndexEndpoint.create(
            display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
            description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
            labels=_TEST_LABELS,
            enable_private_service_connect=True,
            project_allowlist=_TEST_PROJECT_ALLOWLIST,
            encryption_spec_key_name=_TEST_ENCRYPTION_SPEC_KEY_NAME,
        )

        expected = gca_index_endpoint.IndexEndpoint(
            display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
            description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
            labels=_TEST_LABELS,
            private_service_connect_config=gca_service_networking.PrivateServiceConnectConfig(
                project_allowlist=_TEST_PROJECT_ALLOWLIST,
                enable_private_service_connect=True,
            ),
            encryption_spec=gca_encryption_spec.EncryptionSpec(
                kms_key_name=_TEST_ENCRYPTION_SPEC_KEY_NAME
            ),
        )
        create_index_endpoint_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            index_endpoint=expected,
            metadata=_TEST_REQUEST_METADATA,
            timeout=None,
        )

    @pytest.mark.usefixtures("get_index_endpoint_mock")
    def test_create_index_endpoint_with_network_init(self, create_index_endpoint_mock):
        aiplatform.init(project=_TEST_PROJECT, network=_TEST_INDEX_ENDPOINT_VPC_NETWORK)

        aiplatform.MatchingEngineIndexEndpoint.create(
            display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
            description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
            labels=_TEST_LABELS,
            encryption_spec_key_name=_TEST_ENCRYPTION_SPEC_KEY_NAME,
        )

        expected = gca_index_endpoint.IndexEndpoint(
            display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
            network=_TEST_INDEX_ENDPOINT_VPC_NETWORK,
            description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
            labels=_TEST_LABELS,
            public_endpoint_enabled=False,
            encryption_spec=gca_encryption_spec.EncryptionSpec(
                kms_key_name=_TEST_ENCRYPTION_SPEC_KEY_NAME
            ),
        )

        create_index_endpoint_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            index_endpoint=expected,
            metadata=_TEST_REQUEST_METADATA,
            timeout=None,
        )

    @pytest.mark.usefixtures("get_index_public_endpoint_mock")
    def test_create_index_endpoint_with_public_endpoint_enabled(
        self, create_index_endpoint_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        aiplatform.MatchingEngineIndexEndpoint.create(
            display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
            description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
            public_endpoint_enabled=True,
            labels=_TEST_LABELS,
            encryption_spec_key_name=_TEST_ENCRYPTION_SPEC_KEY_NAME,
        )

        my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=_TEST_INDEX_ENDPOINT_ID
        )

        expected = gca_index_endpoint.IndexEndpoint(
            display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
            description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
            public_endpoint_enabled=True,
            labels=_TEST_LABELS,
            encryption_spec=gca_encryption_spec.EncryptionSpec(
                kms_key_name=_TEST_ENCRYPTION_SPEC_KEY_NAME
            ),
        )

        create_index_endpoint_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            index_endpoint=expected,
            metadata=_TEST_REQUEST_METADATA,
            timeout=None,
        )

        assert (
            my_index_endpoint.public_endpoint_domain_name
            == _TEST_INDEX_ENDPOINT_PUBLIC_DNS
        )

    def test_create_index_endpoint_missing_argument_throw_error(
        self, create_index_endpoint_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        expected_message = (
            "Please provide `network` argument for Private Service Access endpoint,"
            "or provide `enable_private_service_connect` for Private Service"
            "Connect endpoint, or provide `public_endpoint_enabled` to"
            "deploy to a public endpoint"
        )

        with pytest.raises(ValueError) as exception:
            _ = aiplatform.MatchingEngineIndexEndpoint.create(
                display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
                description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
                labels=_TEST_LABELS,
            )

        assert str(exception.value) == expected_message

    def test_create_index_endpoint_set_both_psa_and_public_throw_error(
        self, create_index_endpoint_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        expected_message = "One and only one among network, public_endpoint_enabled and enable_private_service_connect should be set."

        with pytest.raises(ValueError) as exception:
            _ = aiplatform.MatchingEngineIndexEndpoint.create(
                display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
                description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
                public_endpoint_enabled=True,
                network=_TEST_INDEX_ENDPOINT_VPC_NETWORK,
                labels=_TEST_LABELS,
            )

        assert str(exception.value) == expected_message

    def test_create_index_endpoint_set_both_psa_and_psc_throw_error(
        self, create_index_endpoint_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        expected_message = "One and only one among network, public_endpoint_enabled and enable_private_service_connect should be set."

        with pytest.raises(ValueError) as exception:
            _ = aiplatform.MatchingEngineIndexEndpoint.create(
                display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
                description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
                network=_TEST_INDEX_ENDPOINT_VPC_NETWORK,
                labels=_TEST_LABELS,
                enable_private_service_connect=True,
            )

        assert str(exception.value) == expected_message

    def test_create_index_endpoint_set_both_psc_and_public_throw_error(
        self, create_index_endpoint_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        expected_message = "One and only one among network, public_endpoint_enabled and enable_private_service_connect should be set."

        with pytest.raises(ValueError) as exception:
            _ = aiplatform.MatchingEngineIndexEndpoint.create(
                display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
                description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
                public_endpoint_enabled=True,
                labels=_TEST_LABELS,
                enable_private_service_connect=True,
            )

        assert str(exception.value) == expected_message

    @pytest.mark.usefixtures("get_index_endpoint_mock", "get_index_mock")
    def test_deploy_index(self, deploy_index_mock, undeploy_index_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=_TEST_INDEX_ENDPOINT_ID
        )

        # Get index
        my_index = aiplatform.MatchingEngineIndex(index_name=_TEST_INDEX_NAME)

        my_index_endpoint = my_index_endpoint.deploy_index(
            index=my_index,
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
            display_name=_TEST_DEPLOYED_INDEX_DISPLAY_NAME,
            min_replica_count=_TEST_MIN_REPLICA_COUNT,
            max_replica_count=_TEST_MAX_REPLICA_COUNT,
            enable_access_logging=_TEST_ENABLE_ACCESS_LOGGING,
            reserved_ip_ranges=_TEST_RESERVED_IP_RANGES,
            deployment_group=_TEST_DEPLOYMENT_GROUP,
            auth_config_audiences=_TEST_AUTH_CONFIG_AUDIENCES,
            auth_config_allowed_issuers=_TEST_AUTH_CONFIG_ALLOWED_ISSUERS,
            request_metadata=_TEST_REQUEST_METADATA,
            deploy_request_timeout=_TEST_TIMEOUT,
        )

        deploy_index_mock.assert_called_once_with(
            index_endpoint=my_index_endpoint.resource_name,
            deployed_index=gca_index_endpoint.DeployedIndex(
                id=_TEST_DEPLOYED_INDEX_ID,
                index=my_index.resource_name,
                display_name=_TEST_DEPLOYED_INDEX_DISPLAY_NAME,
                enable_access_logging=_TEST_ENABLE_ACCESS_LOGGING,
                reserved_ip_ranges=_TEST_RESERVED_IP_RANGES,
                deployment_group=_TEST_DEPLOYMENT_GROUP,
                automatic_resources={
                    "min_replica_count": _TEST_MIN_REPLICA_COUNT,
                    "max_replica_count": _TEST_MAX_REPLICA_COUNT,
                },
                deployed_index_auth_config=gca_index_endpoint.DeployedIndexAuthConfig(
                    auth_provider=gca_index_endpoint.DeployedIndexAuthConfig.AuthProvider(
                        audiences=_TEST_AUTH_CONFIG_AUDIENCES,
                        allowed_issuers=_TEST_AUTH_CONFIG_ALLOWED_ISSUERS,
                    )
                ),
            ),
            metadata=_TEST_REQUEST_METADATA,
            timeout=_TEST_TIMEOUT,
        )

        my_index_endpoint = my_index_endpoint.undeploy_index(
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID
        )

        undeploy_index_mock.assert_called_once_with(
            index_endpoint=my_index_endpoint.resource_name,
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
            metadata=_TEST_REQUEST_METADATA,
            timeout=None,
        )

    @pytest.mark.usefixtures("get_index_endpoint_mock", "get_index_mock")
    def test_mutate_deployed_index(self, mutate_deployed_index_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=_TEST_INDEX_ENDPOINT_ID
        )

        my_index_endpoint.mutate_deployed_index(
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
            min_replica_count=_TEST_MIN_REPLICA_COUNT_UPDATED,
            max_replica_count=_TEST_MAX_REPLICA_COUNT_UPDATED,
            request_metadata=_TEST_REQUEST_METADATA,
            mutate_request_timeout=_TEST_TIMEOUT,
        )

        mutate_deployed_index_mock.assert_called_once_with(
            index_endpoint=_TEST_INDEX_ENDPOINT_NAME,
            deployed_index=gca_index_endpoint.DeployedIndex(
                id=_TEST_DEPLOYED_INDEX_ID,
                automatic_resources={
                    "min_replica_count": _TEST_MIN_REPLICA_COUNT_UPDATED,
                    "max_replica_count": _TEST_MAX_REPLICA_COUNT_UPDATED,
                },
            ),
            metadata=_TEST_REQUEST_METADATA,
            timeout=_TEST_TIMEOUT,
        )

    @pytest.mark.usefixtures("get_index_endpoint_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_delete_index_endpoint_without_force(
        self, undeploy_index_mock, delete_index_endpoint_mock, sync
    ):

        my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=_TEST_INDEX_ENDPOINT_NAME
        )

        my_index_endpoint.delete(sync=sync)

        if not sync:
            my_index_endpoint.wait()

        # undeploy_index_mock should not be called unless force is set to True
        undeploy_index_mock.assert_not_called()

        delete_index_endpoint_mock.assert_called_once_with(
            name=_TEST_INDEX_ENDPOINT_NAME
        )

    @pytest.mark.usefixtures("get_index_endpoint_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_delete_index_endpoint_with_force(
        self, undeploy_index_mock, delete_index_endpoint_mock, sync
    ):

        my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=_TEST_INDEX_ENDPOINT_NAME
        )
        my_index_endpoint.delete(force=True, sync=sync)

        if not sync:
            my_index_endpoint.wait()

        # undeploy_index_mock should be called if force is set to True
        assert undeploy_index_mock.call_count == 2

        delete_index_endpoint_mock.assert_called_once_with(
            name=_TEST_INDEX_ENDPOINT_NAME
        )

    @pytest.mark.usefixtures("get_index_endpoint_mock")
    def test_index_endpoint_match_queries_backward_compatibility(
        self, index_endpoint_match_queries_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=_TEST_INDEX_ENDPOINT_ID
        )

        my_index_endpoint.match(
            _TEST_DEPLOYED_INDEX_ID,
            _TEST_QUERIES,
            _TEST_NUM_NEIGHBOURS,
            _TEST_FILTER,
        )

        batch_request = match_service_pb2.BatchMatchRequest(
            requests=[
                match_service_pb2.BatchMatchRequest.BatchMatchRequestPerIndex(
                    deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
                    requests=[
                        match_service_pb2.MatchRequest(
                            num_neighbors=_TEST_NUM_NEIGHBOURS,
                            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
                            float_val=_TEST_QUERIES[0],
                            restricts=[
                                match_service_pb2.Namespace(
                                    name="class",
                                    allow_tokens=["token_1"],
                                    deny_tokens=["token_2"],
                                )
                            ],
                        )
                    ],
                )
            ]
        )

        index_endpoint_match_queries_mock.assert_called_with(batch_request)

    @pytest.mark.usefixtures("get_index_endpoint_mock")
    def test_private_service_access_hybrid_search_match_queries(
        self, index_endpoint_match_queries_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=_TEST_INDEX_ENDPOINT_ID
        )

        my_index_endpoint.match(
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
            num_neighbors=_TEST_NUM_NEIGHBOURS,
            filter=_TEST_FILTER,
            queries=_TEST_HYBRID_QUERIES,
            per_crowding_attribute_num_neighbors=_TEST_PER_CROWDING_ATTRIBUTE_NUM_NEIGHBOURS,
            approx_num_neighbors=_TEST_APPROX_NUM_NEIGHBORS,
            fraction_leaf_nodes_to_search_override=_TEST_FRACTION_LEAF_NODES_TO_SEARCH_OVERRIDE,
            low_level_batch_size=_TEST_LOW_LEVEL_BATCH_SIZE,
            numeric_filter=_TEST_NUMERIC_FILTER,
        )

        batch_request = match_service_pb2.BatchMatchRequest(
            requests=[
                match_service_pb2.BatchMatchRequest.BatchMatchRequestPerIndex(
                    deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
                    low_level_batch_size=_TEST_LOW_LEVEL_BATCH_SIZE,
                    requests=[
                        match_service_pb2.MatchRequest(
                            num_neighbors=_TEST_NUM_NEIGHBOURS,
                            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
                            float_val=_TEST_HYBRID_QUERIES[i].dense_embedding,
                            restricts=[
                                match_service_pb2.Namespace(
                                    name="class",
                                    allow_tokens=["token_1"],
                                    deny_tokens=["token_2"],
                                )
                            ],
                            per_crowding_attribute_num_neighbors=_TEST_PER_CROWDING_ATTRIBUTE_NUM_NEIGHBOURS,
                            approx_num_neighbors=_TEST_APPROX_NUM_NEIGHBORS,
                            fraction_leaf_nodes_to_search_override=_TEST_FRACTION_LEAF_NODES_TO_SEARCH_OVERRIDE,
                            numeric_restricts=_TEST_NUMERIC_NAMESPACE,
                            sparse_embedding=match_service_pb2.SparseEmbedding(
                                float_val=_TEST_HYBRID_QUERIES[
                                    i
                                ].sparse_embedding_values,
                                dimension=_TEST_HYBRID_QUERIES[
                                    i
                                ].sparse_embedding_dimensions,
                            ),
                            rrf=match_service_pb2.MatchRequest.RRF(
                                alpha=_TEST_HYBRID_QUERIES[i].rrf_ranking_alpha,
                            )
                            if _TEST_HYBRID_QUERIES[i].rrf_ranking_alpha
                            else None,
                        )
                        for i in range(len(_TEST_HYBRID_QUERIES))
                    ],
                )
            ]
        )

        index_endpoint_match_queries_mock.assert_called_with(batch_request)

    @pytest.mark.usefixtures("get_index_endpoint_mock")
    def test_private_service_access_index_endpoint_match_queries(
        self, index_endpoint_match_queries_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=_TEST_INDEX_ENDPOINT_ID
        )

        my_index_endpoint.match(
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
            num_neighbors=_TEST_NUM_NEIGHBOURS,
            filter=_TEST_FILTER,
            queries=_TEST_QUERIES,
            per_crowding_attribute_num_neighbors=_TEST_PER_CROWDING_ATTRIBUTE_NUM_NEIGHBOURS,
            approx_num_neighbors=_TEST_APPROX_NUM_NEIGHBORS,
            fraction_leaf_nodes_to_search_override=_TEST_FRACTION_LEAF_NODES_TO_SEARCH_OVERRIDE,
            low_level_batch_size=_TEST_LOW_LEVEL_BATCH_SIZE,
            numeric_filter=_TEST_NUMERIC_FILTER,
        )

        batch_request = match_service_pb2.BatchMatchRequest(
            requests=[
                match_service_pb2.BatchMatchRequest.BatchMatchRequestPerIndex(
                    deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
                    low_level_batch_size=_TEST_LOW_LEVEL_BATCH_SIZE,
                    requests=[
                        match_service_pb2.MatchRequest(
                            num_neighbors=_TEST_NUM_NEIGHBOURS,
                            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
                            float_val=_TEST_QUERIES[i],
                            restricts=[
                                match_service_pb2.Namespace(
                                    name="class",
                                    allow_tokens=["token_1"],
                                    deny_tokens=["token_2"],
                                )
                            ],
                            per_crowding_attribute_num_neighbors=_TEST_PER_CROWDING_ATTRIBUTE_NUM_NEIGHBOURS,
                            approx_num_neighbors=_TEST_APPROX_NUM_NEIGHBORS,
                            fraction_leaf_nodes_to_search_override=_TEST_FRACTION_LEAF_NODES_TO_SEARCH_OVERRIDE,
                            numeric_restricts=_TEST_NUMERIC_NAMESPACE,
                        )
                        for i in range(len(_TEST_QUERIES))
                    ],
                )
            ]
        )

        index_endpoint_match_queries_mock.assert_called_with(batch_request)

    @pytest.mark.usefixtures("get_index_endpoint_mock")
    def test_index_private_service_access_endpoint_find_neighbor_queries(
        self, index_endpoint_match_queries_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_private_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=_TEST_INDEX_ENDPOINT_ID
        )

        my_private_index_endpoint.find_neighbors(
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
            queries=_TEST_QUERIES,
            num_neighbors=_TEST_NUM_NEIGHBOURS,
            filter=_TEST_FILTER,
            per_crowding_attribute_neighbor_count=_TEST_PER_CROWDING_ATTRIBUTE_NUM_NEIGHBOURS,
            approx_num_neighbors=_TEST_APPROX_NUM_NEIGHBORS,
            fraction_leaf_nodes_to_search_override=_TEST_FRACTION_LEAF_NODES_TO_SEARCH_OVERRIDE,
            return_full_datapoint=_TEST_RETURN_FULL_DATAPOINT,
            numeric_filter=_TEST_NUMERIC_FILTER,
        )

        batch_match_request = match_service_pb2.BatchMatchRequest(
            requests=[
                match_service_pb2.BatchMatchRequest.BatchMatchRequestPerIndex(
                    deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
                    requests=[
                        match_service_pb2.MatchRequest(
                            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
                            num_neighbors=_TEST_NUM_NEIGHBOURS,
                            float_val=test_query,
                            restricts=[
                                match_service_pb2.Namespace(
                                    name="class",
                                    allow_tokens=["token_1"],
                                    deny_tokens=["token_2"],
                                )
                            ],
                            per_crowding_attribute_num_neighbors=_TEST_PER_CROWDING_ATTRIBUTE_NUM_NEIGHBOURS,
                            approx_num_neighbors=_TEST_APPROX_NUM_NEIGHBORS,
                            fraction_leaf_nodes_to_search_override=_TEST_FRACTION_LEAF_NODES_TO_SEARCH_OVERRIDE,
                            numeric_restricts=_TEST_NUMERIC_NAMESPACE,
                        )
                        for test_query in _TEST_QUERIES
                    ],
                )
            ]
        )
        index_endpoint_match_queries_mock.assert_called_with(batch_match_request)

    @pytest.mark.usefixtures("get_index_endpoint_mock")
    def test_index_private_service_connect_endpoint_match_queries(
        self, index_endpoint_match_queries_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=_TEST_INDEX_ENDPOINT_ID
        )

        my_index_endpoint.private_service_connect_ip_address = (
            _TEST_PRIVATE_SERVICE_CONNECT_IP_ADDRESS
        )
        my_index_endpoint.match(
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
            queries=_TEST_QUERIES,
            num_neighbors=_TEST_NUM_NEIGHBOURS,
            filter=_TEST_FILTER,
            per_crowding_attribute_num_neighbors=_TEST_PER_CROWDING_ATTRIBUTE_NUM_NEIGHBOURS,
            approx_num_neighbors=_TEST_APPROX_NUM_NEIGHBORS,
        )

        batch_request = match_service_pb2.BatchMatchRequest(
            requests=[
                match_service_pb2.BatchMatchRequest.BatchMatchRequestPerIndex(
                    deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
                    requests=[
                        match_service_pb2.MatchRequest(
                            num_neighbors=_TEST_NUM_NEIGHBOURS,
                            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
                            float_val=_TEST_QUERIES[0],
                            restricts=[
                                match_service_pb2.Namespace(
                                    name="class",
                                    allow_tokens=["token_1"],
                                    deny_tokens=["token_2"],
                                )
                            ],
                            per_crowding_attribute_num_neighbors=_TEST_PER_CROWDING_ATTRIBUTE_NUM_NEIGHBOURS,
                            approx_num_neighbors=_TEST_APPROX_NUM_NEIGHBORS,
                        )
                    ],
                )
            ]
        )

        index_endpoint_match_queries_mock.assert_called_with(batch_request)

    @pytest.mark.usefixtures("get_index_public_endpoint_mock")
    def test_index_public_endpoint_find_neighbors_queries_backward_compatibility(
        self, index_public_endpoint_match_queries_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_public_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=_TEST_INDEX_ENDPOINT_ID
        )

        my_public_index_endpoint.find_neighbors(
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
            queries=_TEST_QUERIES,
            num_neighbors=_TEST_NUM_NEIGHBOURS,
            filter=_TEST_FILTER,
            per_crowding_attribute_neighbor_count=_TEST_PER_CROWDING_ATTRIBUTE_NUM_NEIGHBOURS,
            approx_num_neighbors=_TEST_APPROX_NUM_NEIGHBORS,
            fraction_leaf_nodes_to_search_override=_TEST_FRACTION_LEAF_NODES_TO_SEARCH_OVERRIDE,
            return_full_datapoint=_TEST_RETURN_FULL_DATAPOINT,
        )

        find_neighbors_request = gca_match_service_v1beta1.FindNeighborsRequest(
            index_endpoint=my_public_index_endpoint.resource_name,
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
            queries=[
                gca_match_service_v1beta1.FindNeighborsRequest.Query(
                    neighbor_count=_TEST_NUM_NEIGHBOURS,
                    datapoint=gca_index_v1beta1.IndexDatapoint(
                        feature_vector=_TEST_QUERIES[0],
                        restricts=[
                            gca_index_v1beta1.IndexDatapoint.Restriction(
                                namespace="class",
                                allow_list=["token_1"],
                                deny_list=["token_2"],
                            )
                        ],
                    ),
                    per_crowding_attribute_neighbor_count=_TEST_PER_CROWDING_ATTRIBUTE_NUM_NEIGHBOURS,
                    approximate_neighbor_count=_TEST_APPROX_NUM_NEIGHBORS,
                    fraction_leaf_nodes_to_search_override=_TEST_FRACTION_LEAF_NODES_TO_SEARCH_OVERRIDE,
                )
            ],
            return_full_datapoint=_TEST_RETURN_FULL_DATAPOINT,
        )

        index_public_endpoint_match_queries_mock.assert_called_with(
            find_neighbors_request
        )

    @pytest.mark.usefixtures("get_index_public_endpoint_mock")
    def test_index_public_endpoint_find_neighbors_queries(
        self, index_public_endpoint_match_queries_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_public_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=_TEST_INDEX_ENDPOINT_ID
        )

        my_public_index_endpoint.find_neighbors(
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
            num_neighbors=_TEST_NUM_NEIGHBOURS,
            filter=_TEST_FILTER,
            per_crowding_attribute_neighbor_count=_TEST_PER_CROWDING_ATTRIBUTE_NUM_NEIGHBOURS,
            approx_num_neighbors=_TEST_APPROX_NUM_NEIGHBORS,
            fraction_leaf_nodes_to_search_override=_TEST_FRACTION_LEAF_NODES_TO_SEARCH_OVERRIDE,
            return_full_datapoint=_TEST_RETURN_FULL_DATAPOINT,
            queries=_TEST_HYBRID_QUERIES,
        )

        find_neighbors_request = gca_match_service_v1beta1.FindNeighborsRequest(
            index_endpoint=my_public_index_endpoint.resource_name,
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
            queries=[
                gca_match_service_v1beta1.FindNeighborsRequest.Query(
                    neighbor_count=_TEST_NUM_NEIGHBOURS,
                    datapoint=gca_index_v1beta1.IndexDatapoint(
                        restricts=[
                            gca_index_v1beta1.IndexDatapoint.Restriction(
                                namespace="class",
                                allow_list=["token_1"],
                                deny_list=["token_2"],
                            )
                        ],
                        sparse_embedding=gca_index_v1beta1.IndexDatapoint.SparseEmbedding(
                            values=[0.1, 0.2, 0.3], dimensions=[1, 2, 3]
                        ),
                    ),
                    rrf=gca_match_service_v1beta1.FindNeighborsRequest.Query.RRF(
                        alpha=0.2,
                    ),
                    per_crowding_attribute_neighbor_count=_TEST_PER_CROWDING_ATTRIBUTE_NUM_NEIGHBOURS,
                    approximate_neighbor_count=_TEST_APPROX_NUM_NEIGHBORS,
                    fraction_leaf_nodes_to_search_override=_TEST_FRACTION_LEAF_NODES_TO_SEARCH_OVERRIDE,
                ),
                gca_match_service_v1beta1.FindNeighborsRequest.Query(
                    neighbor_count=_TEST_NUM_NEIGHBOURS,
                    datapoint=gca_index_v1beta1.IndexDatapoint(
                        feature_vector=_TEST_QUERIES[0],
                        restricts=[
                            gca_index_v1beta1.IndexDatapoint.Restriction(
                                namespace="class",
                                allow_list=["token_1"],
                                deny_list=["token_2"],
                            )
                        ],
                        sparse_embedding=gca_index_v1beta1.IndexDatapoint.SparseEmbedding(
                            values=[0.1, 0.2, 0.3], dimensions=[1, 2, 3]
                        ),
                    ),
                    per_crowding_attribute_neighbor_count=_TEST_PER_CROWDING_ATTRIBUTE_NUM_NEIGHBOURS,
                    approximate_neighbor_count=_TEST_APPROX_NUM_NEIGHBORS,
                    fraction_leaf_nodes_to_search_override=_TEST_FRACTION_LEAF_NODES_TO_SEARCH_OVERRIDE,
                ),
            ],
            return_full_datapoint=_TEST_RETURN_FULL_DATAPOINT,
        )

        index_public_endpoint_match_queries_mock.assert_called_with(
            find_neighbors_request
        )

    @pytest.mark.usefixtures("get_index_public_endpoint_mock")
    def test_index_public_endpoint_find_neiggbor_query_by_id(
        self, index_public_endpoint_match_queries_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_pubic_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=_TEST_INDEX_ENDPOINT_ID
        )

        my_pubic_index_endpoint.find_neighbors(
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
            num_neighbors=_TEST_NUM_NEIGHBOURS,
            filter=_TEST_FILTER,
            per_crowding_attribute_neighbor_count=_TEST_PER_CROWDING_ATTRIBUTE_NUM_NEIGHBOURS,
            approx_num_neighbors=_TEST_APPROX_NUM_NEIGHBORS,
            fraction_leaf_nodes_to_search_override=_TEST_FRACTION_LEAF_NODES_TO_SEARCH_OVERRIDE,
            return_full_datapoint=_TEST_RETURN_FULL_DATAPOINT,
            embedding_ids=_TEST_QUERY_IDS,
        )

        find_neighbors_request = gca_match_service_v1beta1.FindNeighborsRequest(
            index_endpoint=my_pubic_index_endpoint.resource_name,
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
            queries=[
                gca_match_service_v1beta1.FindNeighborsRequest.Query(
                    neighbor_count=_TEST_NUM_NEIGHBOURS,
                    datapoint=gca_index_v1beta1.IndexDatapoint(
                        datapoint_id=_TEST_QUERY_IDS[i],
                        restricts=[
                            gca_index_v1beta1.IndexDatapoint.Restriction(
                                namespace="class",
                                allow_list=["token_1"],
                                deny_list=["token_2"],
                            )
                        ],
                    ),
                    per_crowding_attribute_neighbor_count=_TEST_PER_CROWDING_ATTRIBUTE_NUM_NEIGHBOURS,
                    approximate_neighbor_count=_TEST_APPROX_NUM_NEIGHBORS,
                    fraction_leaf_nodes_to_search_override=_TEST_FRACTION_LEAF_NODES_TO_SEARCH_OVERRIDE,
                )
                for i in range(len(_TEST_QUERY_IDS))
            ],
            return_full_datapoint=_TEST_RETURN_FULL_DATAPOINT,
        )

        index_public_endpoint_match_queries_mock.assert_called_with(
            find_neighbors_request
        )

    @pytest.mark.usefixtures("get_index_public_endpoint_mock")
    def test_index_public_endpoint_match_queries_with_numeric_filtering(
        self, index_public_endpoint_match_queries_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_public_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=_TEST_INDEX_ENDPOINT_ID
        )

        my_public_index_endpoint.find_neighbors(
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
            queries=_TEST_QUERIES,
            num_neighbors=_TEST_NUM_NEIGHBOURS,
            filter=_TEST_FILTER,
            per_crowding_attribute_neighbor_count=_TEST_PER_CROWDING_ATTRIBUTE_NUM_NEIGHBOURS,
            approx_num_neighbors=_TEST_APPROX_NUM_NEIGHBORS,
            fraction_leaf_nodes_to_search_override=_TEST_FRACTION_LEAF_NODES_TO_SEARCH_OVERRIDE,
            return_full_datapoint=_TEST_RETURN_FULL_DATAPOINT,
            numeric_filter=_TEST_NUMERIC_FILTER,
        )

        find_neighbors_request = gca_match_service_v1beta1.FindNeighborsRequest(
            index_endpoint=my_public_index_endpoint.resource_name,
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
            queries=[
                gca_match_service_v1beta1.FindNeighborsRequest.Query(
                    neighbor_count=_TEST_NUM_NEIGHBOURS,
                    datapoint=gca_index_v1beta1.IndexDatapoint(
                        feature_vector=_TEST_QUERIES[0],
                        restricts=[
                            gca_index_v1beta1.IndexDatapoint.Restriction(
                                namespace="class",
                                allow_list=["token_1"],
                                deny_list=["token_2"],
                            )
                        ],
                        numeric_restricts=[
                            gca_index_v1beta1.IndexDatapoint.NumericRestriction(
                                namespace="cost", value_double=0.3, op="EQUAL"
                            ),
                            gca_index_v1beta1.IndexDatapoint.NumericRestriction(
                                namespace="size", value_int=0, op="GREATER"
                            ),
                            gca_index_v1beta1.IndexDatapoint.NumericRestriction(
                                namespace="seconds", value_float=-20.5, op="LESS_EQUAL"
                            ),
                            gca_index_v1beta1.IndexDatapoint.NumericRestriction(
                                namespace="duration", value_int=10, op="NOT_EQUAL"
                            ),
                        ],
                    ),
                    per_crowding_attribute_neighbor_count=_TEST_PER_CROWDING_ATTRIBUTE_NUM_NEIGHBOURS,
                    approximate_neighbor_count=_TEST_APPROX_NUM_NEIGHBORS,
                    fraction_leaf_nodes_to_search_override=_TEST_FRACTION_LEAF_NODES_TO_SEARCH_OVERRIDE,
                )
            ],
            return_full_datapoint=_TEST_RETURN_FULL_DATAPOINT,
        )

        index_public_endpoint_match_queries_mock.assert_called_with(
            find_neighbors_request
        )

    def test_post_init_numeric_filter_invalid_operator_throws_exception(
        self,
    ):
        expected_message = (
            "Invalid operator 'NOT_EQ', must be one of the valid operators."
        )
        with pytest.raises(ValueError) as exception:
            NumericNamespace(name="cost", value_int=3, op="NOT_EQ")

        assert str(exception.value) == expected_message

    def test_post_init_numeric_namespace_missing_value_throws_exception(self):
        aiplatform.init(project=_TEST_PROJECT)

        expected_message = (
            "Must choose one among `value_int`,"
            "`value_float` and `value_double` for "
            "intended precision."
        )

        with pytest.raises(ValueError) as exception:
            NumericNamespace(name="cost", op="EQUAL")

        assert str(exception.value) == expected_message

    def test_index_public_endpoint_match_queries_with_numeric_filtering_value_type_mismatch_throws_exception(
        self,
    ):
        expected_message = "value_int must be of type int, got <class 'float'>."

        with pytest.raises(ValueError) as exception:
            NumericNamespace(name="cost", value_int=0.3, op="EQUAL")

        assert str(exception.value) == expected_message

    @pytest.mark.usefixtures("get_index_public_endpoint_mock")
    def test_index_public_endpoint_read_index_datapoints(
        self, index_public_endpoint_read_index_datapoints_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_public_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=_TEST_INDEX_ENDPOINT_ID
        )

        my_public_index_endpoint.read_index_datapoints(
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
            ids=_TEST_IDS,
        )

        read_index_datapoints_request = (
            gca_match_service_v1beta1.ReadIndexDatapointsRequest(
                index_endpoint=my_public_index_endpoint.resource_name,
                deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
                ids=_TEST_IDS,
            )
        )

        index_public_endpoint_read_index_datapoints_mock.assert_called_with(
            read_index_datapoints_request
        )

    @pytest.mark.usefixtures("get_index_endpoint_mock")
    def test_index_endpoint_batch_get_embeddings(
        self, index_endpoint_batch_get_embeddings_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=_TEST_INDEX_ENDPOINT_ID
        )

        my_index_endpoint._batch_get_embeddings(
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID, ids=["1", "2"]
        )

        batch_request = match_service_pb2.BatchGetEmbeddingsRequest(
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID, id=["1", "2"]
        )

        index_endpoint_batch_get_embeddings_mock.assert_called_with(batch_request)

    @pytest.mark.usefixtures("get_index_endpoint_mock")
    def test_index_endpoint_read_index_datapoints_for_private_service_access(
        self, index_endpoint_batch_get_embeddings_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=_TEST_INDEX_ENDPOINT_ID
        )

        response = my_index_endpoint.read_index_datapoints(
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID, ids=["1", "2"]
        )

        batch_request = match_service_pb2.BatchGetEmbeddingsRequest(
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID, id=["1", "2"]
        )

        index_endpoint_batch_get_embeddings_mock.assert_called_with(batch_request)

        assert response == _TEST_READ_INDEX_DATAPOINTS_RESPONSE

    @pytest.mark.usefixtures("get_index_endpoint_mock")
    def test_index_endpoint_read_index_datapoints_for_private_service_connect(
        self, index_endpoint_batch_get_embeddings_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=_TEST_INDEX_ENDPOINT_ID
        )

        my_index_endpoint.private_service_connect_ip = (
            _TEST_PRIVATE_SERVICE_CONNECT_IP_ADDRESS
        )
        response = my_index_endpoint.read_index_datapoints(
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
            ids=["1", "2"],
        )

        batch_request = match_service_pb2.BatchGetEmbeddingsRequest(
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID, id=["1", "2"]
        )

        index_endpoint_batch_get_embeddings_mock.assert_called_with(batch_request)

        assert response == _TEST_READ_INDEX_DATAPOINTS_RESPONSE


class TestMatchNeighbor:
    def test_from_index_datapoint(self):
        index_datapoint = gca_index_v1beta1.IndexDatapoint()
        index_datapoint.datapoint_id = "test_datapoint_id"
        index_datapoint.feature_vector = [1.0, 2.0, 3.0]
        index_datapoint.crowding_tag = gca_index_v1beta1.IndexDatapoint.CrowdingTag(
            crowding_attribute="test_crowding"
        )
        index_datapoint.restricts = [
            gca_index_v1beta1.IndexDatapoint.Restriction(
                namespace="namespace1", allow_list=["token1"], deny_list=["token2"]
            ),
        ]
        index_datapoint.numeric_restricts = [
            gca_index_v1beta1.IndexDatapoint.NumericRestriction(
                namespace="namespace2",
                value_int=0,
            )
        ]

        result = MatchNeighbor(
            id="index_datapoint_id", distance=0.3
        ).from_index_datapoint(index_datapoint)

        assert result.feature_vector == [1.0, 2.0, 3.0]
        assert result.crowding_tag == "test_crowding"
        assert len(result.restricts) == 1
        assert result.restricts[0].name == "namespace1"
        assert result.restricts[0].allow_tokens == ["token1"]
        assert result.restricts[0].deny_tokens == ["token2"]
        assert len(result.numeric_restricts) == 1
        assert result.numeric_restricts[0].name == "namespace2"
        assert result.numeric_restricts[0].value_int == 0
        assert result.numeric_restricts[0].value_float is None
        assert result.numeric_restricts[0].value_double is None

    def test_from_embedding(self):
        embedding = match_service_pb2.Embedding(
            id="test_embedding_id",
            float_val=[1.0, 2.0, 3.0],
            crowding_attribute=1,
            restricts=[
                match_service_pb2.Namespace(
                    name="namespace1", allow_tokens=["token1"], deny_tokens=["token2"]
                ),
            ],
            numeric_restricts=[
                match_service_pb2.NumericNamespace(
                    name="namespace2", value_int=10, value_float=None, value_double=None
                )
            ],
        )

        result = MatchNeighbor(id="embedding_id", distance=0.3).from_embedding(
            embedding
        )

        assert result.feature_vector == [1.0, 2.0, 3.0]
        assert result.crowding_tag == "1"
        assert len(result.restricts) == 1
        assert result.restricts[0].name == "namespace1"
        assert result.restricts[0].allow_tokens == ["token1"]
        assert result.restricts[0].deny_tokens == ["token2"]
        assert len(result.numeric_restricts) == 1
        assert result.numeric_restricts[0].name == "namespace2"
        assert result.numeric_restricts[0].value_int == 10
        assert not result.numeric_restricts[0].value_float
        assert not result.numeric_restricts[0].value_double
