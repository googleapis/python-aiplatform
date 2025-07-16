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
import re

from google.api_core import operation as ga_operation
from google.cloud import aiplatform
from google.cloud.aiplatform import vertex_ray
from google.cloud.aiplatform.vertex_ray.util.resources import (
    Resources,
    NodeImages,
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
    tc.ClusterConstants.TEST_RESPONSE_RUNNING_1_POOL
)
_TEST_RESPONSE_RUNNING_1_POOL_RESIZE.resource_pools[0].replica_count = 2
_TEST_RESPONSE_RUNNING_2_POOLS_RESIZE = copy.deepcopy(
    tc.ClusterConstants.TEST_RESPONSE_RUNNING_2_POOLS
)
_TEST_RESPONSE_RUNNING_2_POOLS_RESIZE.resource_pools[1].replica_count = 1

_TEST_RESPONSE_RUNNING_1_POOL_RESIZE_0_WORKER = copy.deepcopy(
    tc.ClusterConstants.TEST_RESPONSE_RUNNING_1_POOL
)
_TEST_RESPONSE_RUNNING_1_POOL_RESIZE_0_WORKER.resource_pools[0].replica_count = 1

_TEST_V2_4_WARNING_MESSAGE = (
    "After google-cloud-aiplatform>1.53.0, using Ray version = 2.4 will result in "
    "an error. Please use Ray version = 2.33.0, 2.42.0 or 2.47.1 (default) instead."
)


@pytest.fixture
def create_persistent_resource_1_pool_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "create_persistent_resource",
    ) as create_persistent_resource_1_pool_mock:
        create_persistent_resource_lro_mock = mock.Mock(ga_operation.Operation)
        create_persistent_resource_lro_mock.result.return_value = (
            tc.ClusterConstants.TEST_RESPONSE_RUNNING_1_POOL
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
            tc.ClusterConstants.TEST_RESPONSE_RUNNING_1_POOL
        )
        yield get_persistent_resource_1_pool_mock


@pytest.fixture
def get_persistent_resource_1_pool_custom_image_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "get_persistent_resource",
    ) as get_persistent_resource_1_pool_custom_image_mock:
        get_persistent_resource_1_pool_custom_image_mock.return_value = (
            tc.ClusterConstants.TEST_RESPONSE_RUNNING_1_POOL_CUSTOM_IMAGES
        )
        yield get_persistent_resource_1_pool_custom_image_mock


@pytest.fixture
def create_persistent_resource_1_pool_byosa_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "create_persistent_resource",
    ) as create_persistent_resource_1_pool_byosa_mock:
        create_persistent_resource_lro_mock = mock.Mock(ga_operation.Operation)
        create_persistent_resource_lro_mock.result.return_value = (
            tc.ClusterConstants.TEST_RESPONSE_RUNNING_1_POOL_BYOSA
        )
        create_persistent_resource_1_pool_byosa_mock.return_value = (
            create_persistent_resource_lro_mock
        )
        yield create_persistent_resource_1_pool_byosa_mock


@pytest.fixture
def get_persistent_resource_1_pool_byosa_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "get_persistent_resource",
    ) as get_persistent_resource_1_pool_byosa_mock:
        get_persistent_resource_1_pool_byosa_mock.return_value = (
            tc.ClusterConstants.TEST_RESPONSE_RUNNING_1_POOL_BYOSA
        )
        yield get_persistent_resource_1_pool_byosa_mock


@pytest.fixture
def create_persistent_resource_2_pools_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "create_persistent_resource",
    ) as create_persistent_resource_2_pools_mock:
        create_persistent_resource_lro_mock = mock.Mock(ga_operation.Operation)
        create_persistent_resource_lro_mock.result.return_value = (
            tc.ClusterConstants.TEST_RESPONSE_RUNNING_2_POOLS
        )
        create_persistent_resource_2_pools_mock.return_value = (
            create_persistent_resource_lro_mock
        )
        yield create_persistent_resource_2_pools_mock


@pytest.fixture
def create_persistent_resource_2_pools_custom_image_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "create_persistent_resource",
    ) as create_persistent_resource_2_pools_custom_image_mock:
        create_persistent_resource_lro_mock = mock.Mock(ga_operation.Operation)
        create_persistent_resource_lro_mock.result.return_value = (
            tc.ClusterConstants.TEST_RESPONSE_RUNNING_2_POOLS_CUSTOM_IMAGE
        )
        create_persistent_resource_2_pools_custom_image_mock.return_value = (
            create_persistent_resource_lro_mock
        )
        yield create_persistent_resource_2_pools_custom_image_mock


@pytest.fixture
def get_persistent_resource_2_pools_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "get_persistent_resource",
    ) as get_persistent_resource_2_pools_mock:
        get_persistent_resource_2_pools_mock.return_value = (
            tc.ClusterConstants.TEST_RESPONSE_RUNNING_2_POOLS
        )
        yield get_persistent_resource_2_pools_mock


@pytest.fixture
def get_persistent_resource_2_pools_custom_image_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "get_persistent_resource",
    ) as get_persistent_resource_2_pools_custom_image_mock:
        get_persistent_resource_2_pools_custom_image_mock.return_value = (
            tc.ClusterConstants.TEST_RESPONSE_RUNNING_2_POOLS_CUSTOM_IMAGE
        )
        yield get_persistent_resource_2_pools_custom_image_mock


@pytest.fixture
def list_persistent_resources_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "list_persistent_resources",
    ) as list_persistent_resources_mock:
        list_persistent_resources_mock.return_value = [
            tc.ClusterConstants.TEST_RESPONSE_RUNNING_1_POOL,
            tc.ClusterConstants.TEST_RESPONSE_NO_RAY_RUNNING,  # should be ignored
            tc.ClusterConstants.TEST_RESPONSE_RUNNING_2_POOLS,
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
def update_persistent_resource_1_pool_0_worker_mock():
    with mock.patch.object(
        PersistentResourceServiceClient,
        "update_persistent_resource",
    ) as update_persistent_resource_1_pool_0_worker_mock:
        update_persistent_resource_lro_mock = mock.Mock(ga_operation.Operation)
        update_persistent_resource_lro_mock.result.return_value = (
            _TEST_RESPONSE_RUNNING_1_POOL_RESIZE_0_WORKER
        )
        update_persistent_resource_1_pool_0_worker_mock.return_value = (
            update_persistent_resource_lro_mock
        )
        yield update_persistent_resource_1_pool_0_worker_mock


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


def cluster_eq(returned_cluster, expected_cluster):
    assert vars(returned_cluster.head_node_type) == vars(
        expected_cluster.head_node_type
    )
    assert vars(returned_cluster.worker_node_types[0]) == vars(
        expected_cluster.worker_node_types[0]
    )
    assert (
        returned_cluster.cluster_resource_name == expected_cluster.cluster_resource_name
    )
    assert returned_cluster.python_version == expected_cluster.python_version
    assert returned_cluster.ray_version == expected_cluster.ray_version
    assert returned_cluster.network == expected_cluster.network
    assert returned_cluster.state == expected_cluster.state


@pytest.mark.parametrize("ray_version", ["2.9", "2.33", "2.42", "2.47"])
@pytest.mark.usefixtures("google_auth_mock", "get_project_number_mock")
class TestClusterManagement:
    def setup_method(self, ray_version):
        importlib.reload(aiplatform.initializer)
        importlib.reload(aiplatform)
        aiplatform.init()

    def teardown_method(self, ray_version):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    @pytest.mark.usefixtures("get_persistent_resource_1_pool_mock")
    def test_create_ray_cluster_1_pool_gpu_success(
        self, create_persistent_resource_1_pool_mock, ray_version
    ):
        """If head and worker nodes are duplicate, merge to head pool."""
        cluster_name = vertex_ray.create_ray_cluster(
            head_node_type=tc.ClusterConstants.TEST_HEAD_NODE_TYPE_1_POOL,
            worker_node_types=tc.ClusterConstants.TEST_WORKER_NODE_TYPES_1_POOL,
            network=tc.ProjectConstants.TEST_VPC_NETWORK,
            cluster_name=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ID,
            ray_version=ray_version,
        )

        assert tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS == cluster_name

        test_persistent_resource = tc.ClusterConstants.TEST_REQUEST_RUNNING_1_POOL

        if ray_version == "2.9":
            head_node_image = tc.ClusterConstants.TEST_GPU_IMAGE_2_9
        elif ray_version == "2.33":
            head_node_image = tc.ClusterConstants.TEST_GPU_IMAGE_2_33
        elif ray_version == "2.42":
            head_node_image = tc.ClusterConstants.TEST_GPU_IMAGE_2_42
        else:
            head_node_image = tc.ClusterConstants.TEST_GPU_IMAGE_2_47
        test_persistent_resource.resource_runtime_spec.ray_spec.resource_pool_images[
            "head-node"
        ] = head_node_image

        request = persistent_resource_service.CreatePersistentResourceRequest(
            parent=tc.ProjectConstants.TEST_PARENT,
            persistent_resource=test_persistent_resource,
            persistent_resource_id=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ID,
        )

        create_persistent_resource_1_pool_mock.assert_called_with(
            request,
        )

    @pytest.mark.usefixtures("get_persistent_resource_1_pool_custom_image_mock")
    def test_create_ray_cluster_1_pool_custom_image_success(
        self, create_persistent_resource_1_pool_mock, ray_version
    ):
        """If head and worker nodes are duplicate, merge to head pool."""
        custom_images = NodeImages(
            head=tc.ClusterConstants.TEST_CUSTOM_IMAGE,
            worker=tc.ClusterConstants.TEST_CUSTOM_IMAGE,
        )
        cluster_name = vertex_ray.create_ray_cluster(
            head_node_type=tc.ClusterConstants.TEST_HEAD_NODE_TYPE_1_POOL,
            worker_node_types=tc.ClusterConstants.TEST_WORKER_NODE_TYPES_1_POOL,
            network=tc.ProjectConstants.TEST_VPC_NETWORK,
            cluster_name=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ID,
            custom_images=custom_images,
            nfs_mounts=[tc.ClusterConstants.TEST_NFS_MOUNT],
        )

        assert tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS == cluster_name

        request = persistent_resource_service.CreatePersistentResourceRequest(
            parent=tc.ProjectConstants.TEST_PARENT,
            persistent_resource=tc.ClusterConstants.TEST_REQUEST_RUNNING_1_POOL_CUSTOM_IMAGES,
            persistent_resource_id=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ID,
        )

        create_persistent_resource_1_pool_mock.assert_called_with(
            request,
        )

    @pytest.mark.usefixtures("get_persistent_resource_1_pool_mock")
    def test_create_ray_cluster_1_pool_gpu_with_labels_success(
        self, create_persistent_resource_1_pool_mock, ray_version
    ):
        """If head and worker nodes are duplicate, merge to head pool."""
        # Also test disable logging and metrics collection.
        cluster_name = vertex_ray.create_ray_cluster(
            head_node_type=tc.ClusterConstants.TEST_HEAD_NODE_TYPE_1_POOL,
            worker_node_types=tc.ClusterConstants.TEST_WORKER_NODE_TYPES_1_POOL,
            network=tc.ProjectConstants.TEST_VPC_NETWORK,
            cluster_name=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ID,
            labels=tc.ClusterConstants.TEST_LABELS,
            enable_metrics_collection=False,
            enable_logging=False,
            ray_version=ray_version,
        )

        assert tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS == cluster_name

        test_persistent_resource = (
            tc.ClusterConstants.TEST_REQUEST_RUNNING_1_POOL_WITH_LABELS
        )

        if ray_version == "2.9":
            head_node_image = tc.ClusterConstants.TEST_GPU_IMAGE_2_9
        elif ray_version == "2.33":
            head_node_image = tc.ClusterConstants.TEST_GPU_IMAGE_2_33
        elif ray_version == "2.42":
            head_node_image = tc.ClusterConstants.TEST_GPU_IMAGE_2_42
        else:
            head_node_image = tc.ClusterConstants.TEST_GPU_IMAGE_2_47

        test_persistent_resource.resource_runtime_spec.ray_spec.resource_pool_images[
            "head-node"
        ] = head_node_image

        request = persistent_resource_service.CreatePersistentResourceRequest(
            parent=tc.ProjectConstants.TEST_PARENT,
            persistent_resource=test_persistent_resource,
            persistent_resource_id=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ID,
        )

        create_persistent_resource_1_pool_mock.assert_called_with(
            request,
        )

    @pytest.mark.usefixtures("get_persistent_resource_2_pools_custom_image_mock")
    def test_create_ray_cluster_2_pools_custom_images_success(
        self, create_persistent_resource_2_pools_custom_image_mock, ray_version
    ):
        """If head and worker nodes are not duplicate, create separate resource_pools."""
        cluster_name = vertex_ray.create_ray_cluster(
            head_node_type=tc.ClusterConstants.TEST_HEAD_NODE_TYPE_2_POOLS_CUSTOM_IMAGE,
            worker_node_types=tc.ClusterConstants.TEST_WORKER_NODE_TYPES_2_POOLS_CUSTOM_IMAGE,
            network=tc.ProjectConstants.TEST_VPC_NETWORK,
            reserved_ip_ranges=["vertex-dedicated-range"],
            cluster_name=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ID,
        )

        assert tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS == cluster_name
        request = persistent_resource_service.CreatePersistentResourceRequest(
            parent=tc.ProjectConstants.TEST_PARENT,
            persistent_resource=tc.ClusterConstants.TEST_REQUEST_RUNNING_2_POOLS_CUSTOM_IMAGE,
            persistent_resource_id=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ID,
        )

        create_persistent_resource_2_pools_custom_image_mock.assert_called_with(
            request,
        )

    @pytest.mark.usefixtures("get_persistent_resource_2_pools_mock")
    def test_create_ray_cluster_2_pools_success(
        self, create_persistent_resource_2_pools_mock, ray_version
    ):
        """If head and worker nodes are not duplicate, create separate resource_pools."""
        # Also test PSC-I.
        psc_interface_config = vertex_ray.PscIConfig(
            network_attachment=tc.ClusterConstants.TEST_PSC_NETWORK_ATTACHMENT
        )
        cluster_name = vertex_ray.create_ray_cluster(
            head_node_type=tc.ClusterConstants.TEST_HEAD_NODE_TYPE_2_POOLS,
            worker_node_types=tc.ClusterConstants.TEST_WORKER_NODE_TYPES_2_POOLS,
            cluster_name=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ID,
            psc_interface_config=psc_interface_config,
            ray_version=ray_version,
        )

        test_persistent_resource = tc.ClusterConstants.TEST_REQUEST_RUNNING_2_POOLS

        if ray_version == "2.9":
            head_node_image = tc.ClusterConstants.TEST_CPU_IMAGE_2_9
            worker_node_image = tc.ClusterConstants.TEST_GPU_IMAGE_2_9
        elif ray_version == "2.33":
            head_node_image = tc.ClusterConstants.TEST_CPU_IMAGE_2_33
            worker_node_image = tc.ClusterConstants.TEST_GPU_IMAGE_2_33
        elif ray_version == "2.42":
            head_node_image = tc.ClusterConstants.TEST_CPU_IMAGE_2_42
            worker_node_image = tc.ClusterConstants.TEST_GPU_IMAGE_2_42
        else:
            head_node_image = tc.ClusterConstants.TEST_CPU_IMAGE_2_47
            worker_node_image = tc.ClusterConstants.TEST_GPU_IMAGE_2_47

        test_persistent_resource.resource_runtime_spec.ray_spec.resource_pool_images[
            "head-node"
        ] = head_node_image
        test_persistent_resource.resource_runtime_spec.ray_spec.resource_pool_images[
            "worker-pool1"
        ] = worker_node_image

        assert tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS == cluster_name
        request = persistent_resource_service.CreatePersistentResourceRequest(
            parent=tc.ProjectConstants.TEST_PARENT,
            persistent_resource=test_persistent_resource,
            persistent_resource_id=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ID,
        )

        create_persistent_resource_2_pools_mock.assert_called_with(
            request,
        )

    @pytest.mark.usefixtures("persistent_client_mock")
    def test_create_ray_cluster_initialized_success(
        self, get_project_number_mock, api_client_mock, ray_version
    ):
        """If initialized, create_ray_cluster doesn't need many call args."""
        aiplatform.init(
            project=tc.ProjectConstants.TEST_GCP_PROJECT_ID_OVERRIDE,
            location=tc.ProjectConstants.TEST_GCP_REGION_OVERRIDE,
            staging_bucket=tc.ProjectConstants.TEST_ARTIFACT_URI,
        )

        _ = vertex_ray.create_ray_cluster(
            network=tc.ProjectConstants.TEST_VPC_NETWORK,
        )

        create_method_mock = api_client_mock.create_persistent_resource

        # Assert that project override took effect.
        get_project_number_mock.assert_called_once_with(
            name="projects/{}".format(tc.ProjectConstants.TEST_GCP_PROJECT_ID_OVERRIDE)
        )
        # Assert that location override took effect.
        assert (
            tc.ProjectConstants.TEST_GCP_REGION_OVERRIDE
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

    @pytest.mark.usefixtures("get_persistent_resource_1_pool_byosa_mock")
    def test_create_ray_cluster_byosa_success(
        self, create_persistent_resource_1_pool_byosa_mock, ray_version
    ):
        """If head and worker nodes are duplicate, merge to head pool."""
        cluster_name = vertex_ray.create_ray_cluster(
            head_node_type=tc.ClusterConstants.TEST_HEAD_NODE_TYPE_1_POOL,
            worker_node_types=tc.ClusterConstants.TEST_WORKER_NODE_TYPES_1_POOL,
            service_account=tc.ProjectConstants.TEST_SERVICE_ACCOUNT,
            cluster_name=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ID,
            ray_version=ray_version,
        )

        assert tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS == cluster_name

        test_persistent_resource = tc.ClusterConstants.TEST_REQUEST_RUNNING_1_POOL_BYOSA

        if ray_version == "2.9":
            head_node_image = tc.ClusterConstants.TEST_GPU_IMAGE_2_9
        elif ray_version == "2.33":
            head_node_image = tc.ClusterConstants.TEST_GPU_IMAGE_2_33
        elif ray_version == "2.42":
            head_node_image = tc.ClusterConstants.TEST_GPU_IMAGE_2_42
        else:
            head_node_image = tc.ClusterConstants.TEST_GPU_IMAGE_2_47

        test_persistent_resource.resource_runtime_spec.ray_spec.resource_pool_images[
            "head-node"
        ] = head_node_image

        request = persistent_resource_service.CreatePersistentResourceRequest(
            parent=tc.ProjectConstants.TEST_PARENT,
            persistent_resource=test_persistent_resource,
            persistent_resource_id=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ID,
        )

        create_persistent_resource_1_pool_byosa_mock.assert_called_with(
            request,
        )

    def test_create_ray_cluster_2_4_deprecated_error(self, ray_version):
        with pytest.raises(RuntimeError) as e:
            vertex_ray.create_ray_cluster(
                head_node_type=Resources(node_count=3),
                network=tc.ProjectConstants.TEST_VPC_NETWORK,
                ray_version="2.4",
            )
        e.match(regexp=re.escape(_TEST_V2_4_WARNING_MESSAGE))

    def test_create_ray_cluster_head_multinode_error(self, ray_version):
        with pytest.raises(ValueError) as e:
            vertex_ray.create_ray_cluster(
                head_node_type=Resources(node_count=3),
                network=tc.ProjectConstants.TEST_VPC_NETWORK,
            )
        e.match(regexp=r"Resources.node_count must be 1.")

    def test_create_ray_cluster_python_version_error(self, ray_version):
        with pytest.raises(ValueError) as e:
            vertex_ray.create_ray_cluster(
                network=tc.ProjectConstants.TEST_VPC_NETWORK,
                python_version="3.8",
            )
        e.match(regexp=r"The supported Python versions are 3")

    def test_create_ray_cluster_ray_version_error(self, ray_version):
        with pytest.raises(ValueError) as e:
            vertex_ray.create_ray_cluster(
                network=tc.ProjectConstants.TEST_VPC_NETWORK,
                ray_version="2.1",
            )
        e.match(regexp=r"The supported Ray versions are ")

    def test_create_ray_cluster_same_pool_different_disk_error(self, ray_version):
        with pytest.raises(ValueError) as e:
            vertex_ray.create_ray_cluster(
                head_node_type=Resources(machine_type="n1-highmem-32", node_count=1),
                worker_node_types=[
                    Resources(
                        machine_type="n1-highmem-32",
                        node_count=32,
                        boot_disk_size_gb=1000,
                    )
                ],
                network=tc.ProjectConstants.TEST_VPC_NETWORK,
            )
        e.match(regexp=r"Worker disk size must match the head node's disk size if")

    @pytest.mark.usefixtures("create_persistent_resource_exception_mock")
    def test_create_ray_cluster_state_error(self, ray_version):
        with pytest.raises(ValueError) as e:
            vertex_ray.create_ray_cluster(
                network=tc.ProjectConstants.TEST_VPC_NETWORK,
            )

        e.match(regexp=r"Failed in cluster creation due to: ")

    def test_delete_ray_cluster_success(self, persistent_client_mock, ray_version):
        vertex_ray.delete_ray_cluster(
            cluster_resource_name=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS
        )

        persistent_client_mock.assert_called_once()

    @pytest.mark.usefixtures("persistent_client_error_mock")
    def test_delete_ray_cluster_error(self, ray_version):
        with pytest.raises(ValueError) as e:
            vertex_ray.delete_ray_cluster(
                cluster_resource_name=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS
            )

        e.match(regexp=r"Failed in cluster deletion due to: ")

    def test_get_ray_cluster_success(
        self, get_persistent_resource_1_pool_mock, ray_version
    ):
        cluster = vertex_ray.get_ray_cluster(
            cluster_resource_name=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS
        )

        get_persistent_resource_1_pool_mock.assert_called_once()
        cluster_eq(cluster, tc.ClusterConstants.TEST_CLUSTER)

    def test_get_ray_cluster_with_custom_image_success(
        self, get_persistent_resource_2_pools_custom_image_mock, ray_version
    ):
        cluster = vertex_ray.get_ray_cluster(
            cluster_resource_name=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS
        )

        get_persistent_resource_2_pools_custom_image_mock.assert_called_once()
        cluster_eq(cluster, tc.ClusterConstants.TEST_CLUSTER_CUSTOM_IMAGE)

    def test_get_ray_cluster_byosa_success(
        self, get_persistent_resource_1_pool_byosa_mock, ray_version
    ):
        cluster = vertex_ray.get_ray_cluster(
            cluster_resource_name=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS
        )

        get_persistent_resource_1_pool_byosa_mock.assert_called_once()
        cluster_eq(cluster, tc.ClusterConstants.TEST_CLUSTER_BYOSA)

    @pytest.mark.usefixtures("get_persistent_resource_exception_mock")
    def test_get_ray_cluster_error(self, ray_version):
        with pytest.raises(ValueError) as e:
            vertex_ray.get_ray_cluster(
                cluster_resource_name=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS
            )

        e.match(regexp=r"Failed in getting the cluster due to: ")

    def test_list_ray_clusters_success(
        self, list_persistent_resources_mock, ray_version
    ):
        clusters = vertex_ray.list_ray_clusters()

        list_persistent_resources_mock.assert_called_once()

        # first ray cluster
        cluster_eq(clusters[0], tc.ClusterConstants.TEST_CLUSTER)
        # second ray cluster
        cluster_eq(clusters[1], tc.ClusterConstants.TEST_CLUSTER_2)

    def test_list_ray_clusters_initialized_success(
        self, get_project_number_mock, list_persistent_resources_mock, ray_version
    ):
        aiplatform.init(
            project=tc.ProjectConstants.TEST_GCP_PROJECT_ID_OVERRIDE,
            location=tc.ProjectConstants.TEST_GCP_REGION_OVERRIDE,
            staging_bucket=tc.ProjectConstants.TEST_ARTIFACT_URI,
        )
        _ = vertex_ray.list_ray_clusters()

        # Assert that project override took effect.
        get_project_number_mock.assert_called_once_with(
            name="projects/{}".format(tc.ProjectConstants.TEST_GCP_PROJECT_ID_OVERRIDE)
        )
        # Assert that location override took effect.
        assert (
            tc.ProjectConstants.TEST_GCP_REGION_OVERRIDE
            in list_persistent_resources_mock.call_args.args[0].parent
        )

    @pytest.mark.usefixtures("list_persistent_resources_exception_mock")
    def test_list_ray_clusters_error(self, ray_version):
        with pytest.raises(ValueError) as e:
            vertex_ray.list_ray_clusters()

        e.match(regexp=r"Failed in listing the clusters due to: ")

    @pytest.mark.usefixtures("get_persistent_resource_1_pool_mock")
    def test_update_ray_cluster_1_pool(
        self, update_persistent_resource_1_pool_mock, ray_version
    ):
        new_worker_node_types = []
        for worker_node_type in tc.ClusterConstants.TEST_CLUSTER.worker_node_types:
            # resize worker node to node_count = 1
            worker_node_type.node_count = 1
            new_worker_node_types.append(worker_node_type)

        returned_name = vertex_ray.update_ray_cluster(
            cluster_resource_name=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS,
            worker_node_types=new_worker_node_types,
        )

        request = persistent_resource_service.UpdatePersistentResourceRequest(
            persistent_resource=_TEST_RESPONSE_RUNNING_1_POOL_RESIZE,
            update_mask=_EXPECTED_MASK,
        )
        update_persistent_resource_1_pool_mock.assert_called_once_with(request)

        assert returned_name == tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS

    @pytest.mark.usefixtures("get_persistent_resource_1_pool_mock")
    def test_update_ray_cluster_1_pool_to_0_worker(
        self, update_persistent_resource_1_pool_mock, ray_version
    ):

        new_worker_node_types = []
        for worker_node_type in tc.ClusterConstants.TEST_CLUSTER.worker_node_types:
            # resize worker node to node_count = 0
            worker_node_type.node_count = 0
            new_worker_node_types.append(worker_node_type)

        returned_name = vertex_ray.update_ray_cluster(
            cluster_resource_name=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS,
            worker_node_types=new_worker_node_types,
        )

        request = persistent_resource_service.UpdatePersistentResourceRequest(
            persistent_resource=_TEST_RESPONSE_RUNNING_1_POOL_RESIZE_0_WORKER,
            update_mask=_EXPECTED_MASK,
        )
        update_persistent_resource_1_pool_mock.assert_called_once_with(request)

        assert returned_name == tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS

    @pytest.mark.usefixtures("get_persistent_resource_2_pools_mock")
    def test_update_ray_cluster_2_pools(
        self, update_persistent_resource_2_pools_mock, ray_version
    ):

        new_worker_node_types = []
        for worker_node_type in tc.ClusterConstants.TEST_CLUSTER_2.worker_node_types:
            # resize worker node to node_count = 1
            worker_node_type.node_count = 1
            new_worker_node_types.append(worker_node_type)

        returned_name = vertex_ray.update_ray_cluster(
            cluster_resource_name=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS,
            worker_node_types=new_worker_node_types,
        )

        request = persistent_resource_service.UpdatePersistentResourceRequest(
            persistent_resource=_TEST_RESPONSE_RUNNING_2_POOLS_RESIZE,
            update_mask=_EXPECTED_MASK,
        )
        update_persistent_resource_2_pools_mock.assert_called_once_with(request)

        assert returned_name == tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS

    @pytest.mark.usefixtures("get_persistent_resource_2_pools_mock")
    def test_update_ray_cluster_2_pools_0_worker_fail(self, ray_version):

        new_worker_node_types = []
        for worker_node_type in tc.ClusterConstants.TEST_CLUSTER_2.worker_node_types:
            # resize worker node to node_count = 0
            worker_node_type.node_count = 0
            new_worker_node_types.append(worker_node_type)

        with pytest.raises(ValueError) as e:
            vertex_ray.update_ray_cluster(
                cluster_resource_name=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS,
                worker_node_types=new_worker_node_types,
            )

            e.match(regexp=r"must update to >= 1 nodes.")

    @pytest.mark.usefixtures("get_persistent_resource_1_pool_mock")
    def test_update_ray_cluster_duplicate_worker_node_types_error(self, ray_version):
        new_worker_node_types = (
            tc.ClusterConstants.TEST_CLUSTER_2.worker_node_types
            + tc.ClusterConstants.TEST_CLUSTER_2.worker_node_types
        )
        with pytest.raises(ValueError) as e:
            vertex_ray.update_ray_cluster(
                cluster_resource_name=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS,
                worker_node_types=new_worker_node_types,
            )

            e.match(regexp=r"Worker_node_types have duplicate machine specs")

    @pytest.mark.usefixtures("get_persistent_resource_1_pool_mock")
    def test_update_ray_cluster_mismatch_worker_node_types_count_error(
        self, ray_version
    ):
        with pytest.raises(ValueError) as e:
            new_worker_node_types = tc.ClusterConstants.TEST_CLUSTER_2.worker_node_types
            vertex_ray.update_ray_cluster(
                cluster_resource_name=tc.ClusterConstants.TEST_VERTEX_RAY_PR_ADDRESS,
                worker_node_types=new_worker_node_types,
            )

            e.match(
                regexp=r"does not match the number of the existing worker_node_type"
            )
