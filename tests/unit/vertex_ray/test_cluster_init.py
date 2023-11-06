# Copyright 2023 Google LLC
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
import importlib

from google.api_core import operation as ga_operation
from google.cloud import aiplatform
from google.cloud.aiplatform.preview import vertex_ray
from google.cloud.aiplatform.preview.vertex_ray.util.resources import (
    Resources,
)
from google.cloud.aiplatform_v1beta1.services.persistent_resource_service import (
    PersistentResourceServiceClient,
)
from google.cloud.aiplatform_v1beta1.types import persistent_resource_service
import test_constants as tc
import mock
import pytest

from google.protobuf import field_mask_pb2  # type: ignore


# -*- coding: utf-8 -*-

_EXPECTED_MASK = field_mask_pb2.FieldMask(paths=["resource_pools.replica_count"])

# for manual scaling
_TEST_RESPONSE_RUNNING_1_POOL_RESIZE = copy.deepcopy(
    tc.ClusterConstants._TEST_RESPONSE_RUNNING_1_POOL
)
_TEST_RESPONSE_RUNNING_1_POOL_RESIZE.resource_pools[0].replica_count = 2
_TEST_RESPONSE_RUNNING_2_POOLS_RESIZE = copy.deepcopy(
    tc.ClusterConstants._TEST_RESPONSE_RUNNING_2_POOLS
)
_TEST_RESPONSE_RUNNING_2_POOLS_RESIZE.resource_pools[1].replica_count = 1


@pytest.fixture
def create_persistent_resource_1_pool_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "create_persistent_resource",
    ) as create_persistent_resource_1_pool_mock:
        create_persistent_resource_lro_mock = mock.Mock(ga_operation.Operation)
        create_persistent_resource_lro_mock.result.return_value = (
            tc.ClusterConstants._TEST_RESPONSE_RUNNING_1_POOL
        )
        create_persistent_resource_1_pool_mock.return_value = (
            create_persistent_resource_lro_mock
        )
        yield create_persistent_resource_1_pool_mock


@pytest.fixture
def get_persistent_resource_1_pool_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "get_persistent_resource",
    ) as get_persistent_resource_1_pool_mock:
        get_persistent_resource_1_pool_mock.return_value = (
            tc.ClusterConstants._TEST_RESPONSE_RUNNING_1_POOL
        )
        yield get_persistent_resource_1_pool_mock


@pytest.fixture
def create_persistent_resource_2_pools_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "create_persistent_resource",
    ) as create_persistent_resource_2_pools_mock:
        create_persistent_resource_lro_mock = mock.Mock(ga_operation.Operation)
        create_persistent_resource_lro_mock.result.return_value = (
            tc.ClusterConstants._TEST_RESPONSE_RUNNING_2_POOLS
        )
        create_persistent_resource_2_pools_mock.return_value = (
            create_persistent_resource_lro_mock
        )
        yield create_persistent_resource_2_pools_mock


@pytest.fixture
def get_persistent_resource_2_pools_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "get_persistent_resource",
    ) as get_persistent_resource_2_pools_mock:
        get_persistent_resource_2_pools_mock.return_value = (
            tc.ClusterConstants._TEST_RESPONSE_RUNNING_2_POOLS
        )
        yield get_persistent_resource_2_pools_mock


@pytest.fixture
def list_persistent_resources_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "list_persistent_resources",
    ) as list_persistent_resources_mock:
        list_persistent_resources_mock.return_value = [
            tc.ClusterConstants._TEST_RESPONSE_RUNNING_1_POOL,
            tc.ClusterConstants._TEST_RESPONSE_NO_RAY_RUNNING,  # should be ignored
            tc.ClusterConstants._TEST_RESPONSE_RUNNING_2_POOLS,
        ]
        yield list_persistent_resources_mock


@pytest.fixture
def create_persistent_resource_exception_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "create_persistent_resource",
    ) as create_persistent_resource_exception_mock:
        create_persistent_resource_exception_mock.side_effect = Exception
        yield create_persistent_resource_exception_mock


@pytest.fixture
def get_persistent_resource_exception_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "get_persistent_resource",
    ) as get_persistent_resource_exception_mock:
        get_persistent_resource_exception_mock.side_effect = Exception
        yield get_persistent_resource_exception_mock


@pytest.fixture
def list_persistent_resources_exception_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "list_persistent_resources",
    ) as list_persistent_resources_exception_mock:
        list_persistent_resources_exception_mock.side_effect = Exception
        yield list_persistent_resources_exception_mock


@pytest.fixture
def update_persistent_resource_1_pool_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "update_persistent_resource",
    ) as update_persistent_resource_1_pool_mock:
        update_persistent_resource_lro_mock = mock.Mock(ga_operation.Operation)
        update_persistent_resource_lro_mock.result.return_value = (
            _TEST_RESPONSE_RUNNING_1_POOL_RESIZE
        )
        update_persistent_resource_1_pool_mock.return_value = (
            update_persistent_resource_lro_mock
        )
        yield update_persistent_resource_1_pool_mock


@pytest.fixture
def update_persistent_resource_2_pools_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "update_persistent_resource",
    ) as update_persistent_resource_2_pools_mock:
        update_persistent_resource_lro_mock = mock.Mock(ga_operation.Operation)
        update_persistent_resource_lro_mock.result.return_value = (
            _TEST_RESPONSE_RUNNING_2_POOLS_RESIZE
        )
        update_persistent_resource_2_pools_mock.return_value = (
            update_persistent_resource_lro_mock
        )
        yield update_persistent_resource_2_pools_mock


@pytest.mark.usefixtures("google_auth_mock", "get_project_number_mock")
class TestClusterManagement:
    def setup_method(self):
        importlib.reload(aiplatform.initializer)
        importlib.reload(aiplatform)
        aiplatform.init()

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    @pytest.mark.usefixtures("get_persistent_resource_1_pool_mock")
    def test_create_ray_cluster_1_pool_gpu_success(
        self, create_persistent_resource_1_pool_mock
    ):
        """If head and worker nodes are duplicate, merge to head pool."""
        cluster_name = vertex_ray.create_ray_cluster(
            head_node_type=tc.ClusterConstants._TEST_HEAD_NODE_TYPE_1_POOL,
            worker_node_types=tc.ClusterConstants._TEST_WORKER_NODE_TYPES_1_POOL,
            network=tc.ProjectConstants._TEST_VPC_NETWORK,
            cluster_name=tc.ClusterConstants._TEST_VERTEX_RAY_PR_ID,
        )

        assert tc.ClusterConstants._TEST_VERTEX_RAY_PR_ADDRESS == cluster_name

        request = persistent_resource_service.CreatePersistentResourceRequest(
            parent=tc.ProjectConstants._TEST_PARENT,
            persistent_resource=tc.ClusterConstants._TEST_REQUEST_RUNNING_1_POOL,
            persistent_resource_id=tc.ClusterConstants._TEST_VERTEX_RAY_PR_ID,
        )

        create_persistent_resource_1_pool_mock.assert_called_with(
            request,
        )

    @pytest.mark.usefixtures("get_persistent_resource_1_pool_mock")
    def test_create_ray_cluster_1_pool_gpu_with_labels_success(
        self, create_persistent_resource_1_pool_mock
    ):
        """If head and worker nodes are duplicate, merge to head pool."""
        cluster_name = vertex_ray.create_ray_cluster(
            head_node_type=tc.ClusterConstants._TEST_HEAD_NODE_TYPE_1_POOL,
            worker_node_types=tc.ClusterConstants._TEST_WORKER_NODE_TYPES_1_POOL,
            network=tc.ProjectConstants._TEST_VPC_NETWORK,
            cluster_name=tc.ClusterConstants._TEST_VERTEX_RAY_PR_ID,
            labels=tc.ClusterConstants._TEST_LABELS,
        )

        assert tc.ClusterConstants._TEST_VERTEX_RAY_PR_ADDRESS == cluster_name

        request = persistent_resource_service.CreatePersistentResourceRequest(
            parent=tc.ProjectConstants._TEST_PARENT,
            persistent_resource=tc.ClusterConstants._TEST_REQUEST_RUNNING_1_POOL_WITH_LABELS,
            persistent_resource_id=tc.ClusterConstants._TEST_VERTEX_RAY_PR_ID,
        )

        create_persistent_resource_1_pool_mock.assert_called_with(
            request,
        )

    @pytest.mark.usefixtures("get_persistent_resource_2_pools_mock")
    def test_create_ray_cluster_2_pools_success(
        self, create_persistent_resource_2_pools_mock
    ):
        """If head and worker nodes are not duplicate, create separate resource_pools."""
        cluster_name = vertex_ray.create_ray_cluster(
            head_node_type=tc.ClusterConstants._TEST_HEAD_NODE_TYPE_2_POOLS,
            worker_node_types=tc.ClusterConstants._TEST_WORKER_NODE_TYPES_2_POOLS,
            network=tc.ProjectConstants._TEST_VPC_NETWORK,
            cluster_name=tc.ClusterConstants._TEST_VERTEX_RAY_PR_ID,
        )

        assert tc.ClusterConstants._TEST_VERTEX_RAY_PR_ADDRESS == cluster_name
        request = persistent_resource_service.CreatePersistentResourceRequest(
            parent=tc.ProjectConstants._TEST_PARENT,
            persistent_resource=tc.ClusterConstants._TEST_REQUEST_RUNNING_2_POOLS,
            persistent_resource_id=tc.ClusterConstants._TEST_VERTEX_RAY_PR_ID,
        )

        create_persistent_resource_2_pools_mock.assert_called_with(
            request,
        )

    @pytest.mark.usefixtures("persistent_client_mock")
    def test_create_ray_cluster_initialized_success(
        self, get_project_number_mock, api_client_mock
    ):
        """If initialized, create_ray_cluster doesn't need many call args."""
        aiplatform.init(
            project=tc.ProjectConstants._TEST_GCP_PROJECT_ID_OVERRIDE,
            location=tc.ProjectConstants._TEST_GCP_REGION_OVERRIDE,
            staging_bucket=tc.ProjectConstants._TEST_ARTIFACT_URI,
        )

        _ = vertex_ray.create_ray_cluster(
            network=tc.ProjectConstants._TEST_VPC_NETWORK,
        )

        create_method_mock = api_client_mock.create_persistent_resource

        # Assert that project override took effect.
        get_project_number_mock.assert_called_once_with(
            name="projects/{}".format(tc.ProjectConstants._TEST_GCP_PROJECT_ID_OVERRIDE)
        )
        # Assert that location override took effect.
        assert (
            tc.ProjectConstants._TEST_GCP_REGION_OVERRIDE
            in create_method_mock.call_args.args[0].parent
        )
        assert (
            "asia-docker"
            in create_method_mock.call_args.args[
                0
            ].persistent_resource.resource_runtime_spec.ray_spec.resource_pool_images[
                "head-node"
            ]
        )

    def test_create_ray_cluster_head_multinode_error(self):
        with pytest.raises(ValueError) as e:
            vertex_ray.create_ray_cluster(
                head_node_type=Resources(node_count=3),
                network=tc.ProjectConstants._TEST_VPC_NETWORK,
            )
        e.match(regexp=r"Resources.node_count must be 1.")

    def test_create_ray_cluster_python_version_error(self):
        with pytest.raises(ValueError) as e:
            vertex_ray.create_ray_cluster(
                network=tc.ProjectConstants._TEST_VPC_NETWORK,
                python_version="3_8",
            )
        e.match(regexp=r"The supported Python version is 3_10.")

    def test_create_ray_cluster_ray_version_error(self):
        with pytest.raises(ValueError) as e:
            vertex_ray.create_ray_cluster(
                network=tc.ProjectConstants._TEST_VPC_NETWORK,
                ray_version="2_1",
            )
        e.match(regexp=r"The supported Ray version is 2_4.")

    @pytest.mark.usefixtures("create_persistent_resource_exception_mock")
    def test_create_ray_cluster_state_error(self):
        with pytest.raises(ValueError) as e:
            vertex_ray.create_ray_cluster(
                network=tc.ProjectConstants._TEST_VPC_NETWORK,
            )

        e.match(regexp=r"Failed in cluster creation due to: ")

    def test_delete_ray_cluster_success(self, persistent_client_mock):
        vertex_ray.delete_ray_cluster(
            cluster_resource_name=tc.ClusterConstants._TEST_VERTEX_RAY_PR_ADDRESS
        )

        persistent_client_mock.assert_called_once()

    @pytest.mark.usefixtures("persistent_client_error_mock")
    def test_delete_ray_cluster_error(self):
        with pytest.raises(ValueError) as e:
            vertex_ray.delete_ray_cluster(
                cluster_resource_name=tc.ClusterConstants._TEST_VERTEX_RAY_PR_ADDRESS
            )

        e.match(regexp=r"Failed in cluster deletion due to: ")

    def test_get_ray_cluster_success(self, get_persistent_resource_1_pool_mock):
        cluster = vertex_ray.get_ray_cluster(
            cluster_resource_name=tc.ClusterConstants._TEST_VERTEX_RAY_PR_ADDRESS
        )

        get_persistent_resource_1_pool_mock.assert_called_once()

        assert vars(cluster.head_node_type) == vars(
            tc.ClusterConstants._TEST_CLUSTER.head_node_type
        )
        assert vars(cluster.worker_node_types[0]) == vars(
            tc.ClusterConstants._TEST_CLUSTER.worker_node_types[0]
        )
        assert (
            cluster.cluster_resource_name
            == tc.ClusterConstants._TEST_CLUSTER.cluster_resource_name
        )
        assert (
            cluster.python_version == tc.ClusterConstants._TEST_CLUSTER.python_version
        )
        assert cluster.ray_version == tc.ClusterConstants._TEST_CLUSTER.ray_version
        assert cluster.network == tc.ClusterConstants._TEST_CLUSTER.network
        assert cluster.state == tc.ClusterConstants._TEST_CLUSTER.state

    @pytest.mark.usefixtures("get_persistent_resource_exception_mock")
    def test_get_ray_cluster_error(self):
        with pytest.raises(ValueError) as e:
            vertex_ray.get_ray_cluster(
                cluster_resource_name=tc.ClusterConstants._TEST_VERTEX_RAY_PR_ADDRESS
            )

        e.match(regexp=r"Failed in getting the cluster due to: ")

    def test_list_ray_clusters_success(self, list_persistent_resources_mock):
        clusters = vertex_ray.list_ray_clusters()

        list_persistent_resources_mock.assert_called_once()

        # first ray cluster
        assert vars(clusters[0].head_node_type) == vars(
            tc.ClusterConstants._TEST_CLUSTER.head_node_type
        )
        assert vars(clusters[0].worker_node_types[0]) == vars(
            tc.ClusterConstants._TEST_CLUSTER.worker_node_types[0]
        )
        assert (
            clusters[0].cluster_resource_name
            == tc.ClusterConstants._TEST_CLUSTER.cluster_resource_name
        )
        assert (
            clusters[0].python_version
            == tc.ClusterConstants._TEST_CLUSTER.python_version
        )
        assert clusters[0].ray_version == tc.ClusterConstants._TEST_CLUSTER.ray_version
        assert clusters[0].network == tc.ClusterConstants._TEST_CLUSTER.network
        assert clusters[0].state == tc.ClusterConstants._TEST_CLUSTER.state

        # second ray cluster
        assert vars(clusters[1].head_node_type) == vars(
            tc.ClusterConstants._TEST_CLUSTER_2.head_node_type
        )
        assert vars(clusters[1].worker_node_types[0]) == vars(
            tc.ClusterConstants._TEST_CLUSTER_2.worker_node_types[0]
        )
        assert (
            clusters[1].cluster_resource_name
            == tc.ClusterConstants._TEST_CLUSTER_2.cluster_resource_name
        )
        assert (
            clusters[1].python_version
            == tc.ClusterConstants._TEST_CLUSTER_2.python_version
        )
        assert (
            clusters[1].ray_version == tc.ClusterConstants._TEST_CLUSTER_2.ray_version
        )
        assert clusters[1].network == tc.ClusterConstants._TEST_CLUSTER_2.network
        assert clusters[1].state == tc.ClusterConstants._TEST_CLUSTER_2.state

    def test_list_ray_clusters_initialized_success(
        self, get_project_number_mock, list_persistent_resources_mock
    ):
        aiplatform.init(
            project=tc.ProjectConstants._TEST_GCP_PROJECT_ID_OVERRIDE,
            location=tc.ProjectConstants._TEST_GCP_REGION_OVERRIDE,
            staging_bucket=tc.ProjectConstants._TEST_ARTIFACT_URI,
        )
        _ = vertex_ray.list_ray_clusters()

        # Assert that project override took effect.
        get_project_number_mock.assert_called_once_with(
            name="projects/{}".format(tc.ProjectConstants._TEST_GCP_PROJECT_ID_OVERRIDE)
        )
        # Assert that location override took effect.
        assert (
            tc.ProjectConstants._TEST_GCP_REGION_OVERRIDE
            in list_persistent_resources_mock.call_args.args[0].parent
        )

    @pytest.mark.usefixtures("list_persistent_resources_exception_mock")
    def test_list_ray_clusters_error(self):
        with pytest.raises(ValueError) as e:
            vertex_ray.list_ray_clusters()

        e.match(regexp=r"Failed in listing the clusters due to: ")

    @pytest.mark.usefixtures("get_persistent_resource_1_pool_mock")
    def test_update_ray_cluster_1_pool(self, update_persistent_resource_1_pool_mock):

        new_worker_node_types = []
        for worker_node_type in tc.ClusterConstants._TEST_CLUSTER.worker_node_types:
            # resize worker node to node_count = 1
            worker_node_type.node_count = 1
            new_worker_node_types.append(worker_node_type)

        returned_name = vertex_ray.update_ray_cluster(
            cluster_resource_name=tc.ClusterConstants._TEST_VERTEX_RAY_PR_ADDRESS,
            worker_node_types=new_worker_node_types,
        )

        request = persistent_resource_service.UpdatePersistentResourceRequest(
            persistent_resource=_TEST_RESPONSE_RUNNING_1_POOL_RESIZE,
            update_mask=_EXPECTED_MASK,
        )
        update_persistent_resource_1_pool_mock.assert_called_once_with(request)

        assert returned_name == tc.ClusterConstants._TEST_VERTEX_RAY_PR_ADDRESS

    @pytest.mark.usefixtures("get_persistent_resource_2_pools_mock")
    def test_update_ray_cluster_2_pools(self, update_persistent_resource_2_pools_mock):

        new_worker_node_types = []
        for worker_node_type in tc.ClusterConstants._TEST_CLUSTER_2.worker_node_types:
            # resize worker node to node_count = 1
            worker_node_type.node_count = 1
            new_worker_node_types.append(worker_node_type)

        returned_name = vertex_ray.update_ray_cluster(
            cluster_resource_name=tc.ClusterConstants._TEST_VERTEX_RAY_PR_ADDRESS,
            worker_node_types=new_worker_node_types,
        )

        request = persistent_resource_service.UpdatePersistentResourceRequest(
            persistent_resource=_TEST_RESPONSE_RUNNING_2_POOLS_RESIZE,
            update_mask=_EXPECTED_MASK,
        )
        update_persistent_resource_2_pools_mock.assert_called_once_with(request)

        assert returned_name == tc.ClusterConstants._TEST_VERTEX_RAY_PR_ADDRESS
