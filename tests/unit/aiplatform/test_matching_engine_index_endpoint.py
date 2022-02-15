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
from google.cloud.aiplatform_v1.services.index_endpoint_service import (
    client as index_endpoint_service_client,
)
from google.cloud.aiplatform_v1.types import (
    index_endpoint as gca_index_endpoint,
    index as gca_index,
)
from google.cloud.aiplatform.compat.types import (
    matching_engine_index_endpoint as gca_matching_engine_index_endpoint,
    matching_engine_deployed_index_ref as gca_matching_engine_deployed_index_ref,
)
from google.cloud.aiplatform_v1.services.index_service import (
    client as index_service_client,
)

# project
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"

# index
_TEST_INDEX_ID = "index_id"
_TEST_INDEX_NAME = f"{_TEST_PARENT}/indexes/{_TEST_INDEX_ID}"
_TEST_INDEX_DISPLAY_NAME = f"index_display_name"

# index_endpoint
_TEST_INDEX_ENDPOINT_ID = "index_endpoint_id"
_TEST_INDEX_ENDPOINT_NAME = f"{_TEST_PARENT}/indexEndpoints/{_TEST_INDEX_ENDPOINT_ID}"
_TEST_INDEX_ENDPOINT_DISPLAY_NAME = f"index_endpoint_display_name"
_TEST_INDEX_ENDPOINT_DESCRIPTION = f"index_endpoint_description"
_TEST_INDEX_DESCRIPTION = f"index_description"

_TEST_LABELS = {"my_key": "my_value"}
_TEST_DISPLAY_NAME_UPDATE = "my new display name"
_TEST_DESCRIPTION_UPDATE = "my description update"
_TEST_LABELS_UPDATE = {"my_key_update": "my_value_update"}

# deployment
_TEST_DEPLOYED_INDEX_ID = f"deployed_index_id"
_TEST_DEPLOYED_INDEX_DISPLAY_NAME = f"deployed_index_display_name"
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
_TEST_DEPLOYED_INDEX_ID_UPDATED = f"deployed_index_id_updated"
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


# request_metadata
_TEST_REQUEST_METADATA = ()

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
                index_endpoint=index.name, deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
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
            gca_matching_engine_index_endpoint.DeployedIndex(
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
                deployed_index_auth_config=gca_matching_engine_index_endpoint.DeployedIndexAuthConfig(
                    auth_provider=gca_matching_engine_index_endpoint.DeployedIndexAuthConfig.AuthProvider(
                        audiences=_TEST_AUTH_CONFIG_AUDIENCES,
                        allowed_issuers=_TEST_AUTH_CONFIG_ALLOWED_ISSUERS,
                    )
                ),
            ),
        ]

        get_index_endpoint_mock.return_value = index_endpoint
        yield get_index_endpoint_mock


@pytest.fixture
def deploy_index_mock():
    with mock.patch.object(
        index_endpoint_service_client.IndexEndpointServiceClient, "deploy_index",
    ) as deploy_index_mock:
        deploy_index_lro_mock = mock.Mock(operation.Operation)
        deploy_index_mock.return_value = deploy_index_lro_mock
        yield deploy_index_mock


@pytest.fixture
def undeploy_index_mock():
    with mock.patch.object(
        index_endpoint_service_client.IndexEndpointServiceClient, "undeploy_index",
    ) as undeploy_index_mock:
        undeploy_index_lro_mock = mock.Mock(operation.Operation)
        undeploy_index_mock.return_value = undeploy_index_lro_mock
        yield undeploy_index_mock


@pytest.fixture
def update_index_endpoint_mock():
    with patch.object(
        index_endpoint_service_client.IndexEndpointServiceClient,
        "update_index_endpoint",
    ) as update_index_endpoint_mock:
        update_index_endpoint_lro_mock = mock.Mock(operation.Operation)
        update_index_endpoint_mock.return_value = update_index_endpoint_lro_mock
        yield update_index_endpoint_mock


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
    with mock.patch.object(
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
        create_index_endpoint_lro_mock.result.return_value = gca_index_endpoint.IndexEndpoint(
            name=_TEST_INDEX_ENDPOINT_NAME,
            display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
            description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
        )
        create_index_endpoint_mock.return_value = create_index_endpoint_lro_mock
        yield create_index_endpoint_mock


class TestMatchingEngineIndex:
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
        my_index_endpoint.update(
            display_name=_TEST_DISPLAY_NAME_UPDATE,
            description=_TEST_DESCRIPTION_UPDATE,
            labels=_TEST_LABELS_UPDATE,
            request_metadata=_TEST_REQUEST_METADATA,
        )

        expected = gca_index_endpoint.IndexEndpoint(
            name=_TEST_INDEX_ENDPOINT_NAME,
            display_name=_TEST_DISPLAY_NAME_UPDATE,
            description=_TEST_DESCRIPTION_UPDATE,
        )

        update_index_endpoint_mock.assert_called_once_with(
            index_endpoint=expected,
            update_mask=field_mask_pb2.FieldMask(
                paths=["labels", "display_name", "description"]
            ),
            labels=_TEST_LABELS_UPDATE,
            metadata=_TEST_REQUEST_METADATA,
        )

    def test_list_index_endpoints(self, list_index_endpoints_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_index_endpoints_list = aiplatform.MatchingEngineIndexEndpoint.list()

        list_index_endpoints_mock.assert_called_once_with(
            request={"parent": _TEST_PARENT, "filter": None}
        )
        assert len(my_index_endpoints_list) == len(_TEST_INDEX_ENDPOINT_LIST)
        for my_index_endpoint in my_index_endpoints_list:
            assert type(my_index_endpoint) == aiplatform.MatchingEngineIndexEndpoint

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
            index_endpoint_id=_TEST_INDEX_ENDPOINT_ID,
            display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
            description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
            labels=_TEST_LABELS,
        )

        if not sync:
            my_index_endpoint.wait()

        expected = gca_index_endpoint.IndexEndpoint(
            name=_TEST_INDEX_ENDPOINT_ID,
            display_name=_TEST_INDEX_ENDPOINT_DISPLAY_NAME,
            description=_TEST_INDEX_ENDPOINT_DESCRIPTION,
            labels=_TEST_LABELS,
        )
        create_index_endpoint_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            index_endpoint=expected,
            metadata=_TEST_REQUEST_METADATA,
        )

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
        )

        deploy_index_mock.assert_called_once_with(
            index_endpoint=my_index_endpoint.resource_name,
            deployed_index=gca_matching_engine_index_endpoint.DeployedIndex(
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
                deployed_index_auth_config=gca_matching_engine_index_endpoint.DeployedIndexAuthConfig(
                    auth_provider=gca_matching_engine_index_endpoint.DeployedIndexAuthConfig.AuthProvider(
                        audiences=_TEST_AUTH_CONFIG_AUDIENCES,
                        allowed_issuers=_TEST_AUTH_CONFIG_ALLOWED_ISSUERS,
                    )
                ),
            ),
            metadata=_TEST_REQUEST_METADATA,
        )

        my_index_endpoint = my_index_endpoint.undeploy_index(
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID
        )

        undeploy_index_mock.assert_called_once_with(
            index_endpoint=my_index_endpoint.resource_name,
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID,
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_index_endpoint_mock", "get_index_mock")
    def test_mutate_deployed_index(self, mutate_deployed_index_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=_TEST_INDEX_ENDPOINT_ID
        )

        my_index_endpoint.mutate_deployed_index(
            index_id=_TEST_INDEX_ID,
            deployed_index_id=_TEST_DEPLOYED_INDEX_ID_UPDATED,
            display_name=_TEST_DEPLOYED_INDEX_DISPLAY_NAME_UPDATED,
            min_replica_count=_TEST_MIN_REPLICA_COUNT_UPDATED,
            max_replica_count=_TEST_MAX_REPLICA_COUNT_UPDATED,
            enable_access_logging=_TEST_ENABLE_ACCESS_LOGGING_UPDATED,
            reserved_ip_ranges=_TEST_RESERVED_IP_RANGES_UPDATED,
            deployment_group=_TEST_DEPLOYMENT_GROUP_UPDATED,
            auth_config_audiences=_TEST_AUTH_CONFIG_AUDIENCES_UPDATED,
            auth_config_allowed_issuers=_TEST_AUTH_CONFIG_ALLOWED_ISSUERS_UPDATED,
            request_metadata=_TEST_REQUEST_METADATA,
        )

        mutate_deployed_index_mock.assert_called_once_with(
            index_endpoint=_TEST_INDEX_ENDPOINT_NAME,
            deployed_index=gca_matching_engine_index_endpoint.DeployedIndex(
                id=_TEST_DEPLOYED_INDEX_ID_UPDATED,
                index=_TEST_INDEX_NAME,
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
            ),
            metadata=_TEST_REQUEST_METADATA,
        )
