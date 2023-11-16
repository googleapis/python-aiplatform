# -*- coding: utf-8 -*-

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

import dataclasses

from google.cloud.aiplatform.preview.vertex_ray.util.resources import Cluster
from google.cloud.aiplatform.preview.vertex_ray.util.resources import (
    Resources,
)
from google.cloud.aiplatform_v1beta1.types.machine_resources import DiskSpec
from google.cloud.aiplatform_v1beta1.types.machine_resources import (
    MachineSpec,
)
from google.cloud.aiplatform_v1beta1.types.persistent_resource import (
    PersistentResource,
)
from google.cloud.aiplatform_v1beta1.types.persistent_resource import RaySpec
from google.cloud.aiplatform_v1beta1.types.persistent_resource import (
    ResourcePool,
)
from google.cloud.aiplatform_v1beta1.types.persistent_resource import (
    ResourceRuntime,
)
from google.cloud.aiplatform_v1beta1.types.persistent_resource import (
    ResourceRuntimeSpec,
)


@dataclasses.dataclass(frozen=True)
class ProjectConstants:
    """Defines project-specific constants used by tests."""

    _TEST_VPC_NETWORK = "mock-vpc-network"
    _TEST_GCP_PROJECT_ID = "mock-test-project-id"
    _TEST_GCP_PROJECT_ID_OVERRIDE = "mock-test-project-id-2"
    _TEST_GCP_REGION = "us-central1"
    _TEST_GCP_REGION_OVERRIDE = "asia-east1"
    _TEST_GCP_PROJECT_NUMBER = "12345"
    _TEST_PARENT = f"projects/{_TEST_GCP_PROJECT_NUMBER}/locations/{_TEST_GCP_REGION}"
    _TEST_ARTIFACT_URI = "gs://path/to/artifact/uri"
    _TEST_BAD_ARTIFACT_URI = "/path/to/artifact/uri"
    _TEST_MODEL_GCS_URI = "gs://test_model_dir"
    _TEST_MODEL_ID = (
        f"projects/{_TEST_GCP_PROJECT_NUMBER}/locations/{_TEST_GCP_REGION}/models/456"
    )


@dataclasses.dataclass(frozen=True)
class ClusterConstants:
    """Defines cluster constants used by tests."""

    _TEST_LABELS = {"my_key": "my_value"}
    _TEST_VERTEX_RAY_HEAD_NODE_IP = "1.2.3.4:10001"
    _TEST_VERTEX_RAY_JOB_CLIENT_IP = "1.2.3.4:8888"
    _TEST_VERTEX_RAY_DASHBOARD_ADDRESS = (
        "48b400ad90b8dd3c-dot-us-central1.aiplatform-training.googleusercontent.com"
    )
    _TEST_VERTEX_RAY_PR_ID = "user-persistent-resource-1234567890"
    _TEST_VERTEX_RAY_PR_ADDRESS = (
        f"{ProjectConstants._TEST_PARENT}/persistentResources/" + _TEST_VERTEX_RAY_PR_ID
    )
    _TEST_CPU_IMAGE = "us-docker.pkg.dev/vertex-ai/training/ray-cpu.2-4.py310:latest"
    _TEST_GPU_IMAGE = "us-docker.pkg.dev/vertex-ai/training/ray-gpu.2-4.py310:latest"
    # RUNNING Persistent Cluster w/o Ray
    _TEST_RESPONSE_NO_RAY_RUNNING = PersistentResource(
        name=_TEST_VERTEX_RAY_PR_ADDRESS,
        resource_runtime_spec=ResourceRuntimeSpec(),
        resource_runtime=ResourceRuntime(),
        state="RUNNING",
    )
    # RUNNING
    # 1_POOL: merged worker_node_types and head_node_type with duplicate MachineSpec
    _TEST_HEAD_NODE_TYPE_1_POOL = Resources(
        accelerator_type="NVIDIA_TESLA_P100", accelerator_count=1
    )
    _TEST_WORKER_NODE_TYPES_1_POOL = [
        Resources(
            accelerator_type="NVIDIA_TESLA_P100", accelerator_count=1, node_count=2
        )
    ]
    _TEST_RESOURCE_POOL_0 = ResourcePool(
        id="head-node",
        machine_spec=MachineSpec(
            machine_type="n1-standard-4",
            accelerator_type="NVIDIA_TESLA_P100",
            accelerator_count=1,
        ),
        disk_spec=DiskSpec(
            boot_disk_type="pd-ssd",
            boot_disk_size_gb=100,
        ),
        replica_count=3,
    )
    _TEST_REQUEST_RUNNING_1_POOL = PersistentResource(
        resource_pools=[_TEST_RESOURCE_POOL_0],
        resource_runtime_spec=ResourceRuntimeSpec(
            ray_spec=RaySpec(resource_pool_images={"head-node": _TEST_GPU_IMAGE}),
        ),
        network=ProjectConstants._TEST_VPC_NETWORK,
    )
    _TEST_REQUEST_RUNNING_1_POOL_WITH_LABELS = PersistentResource(
        resource_pools=[_TEST_RESOURCE_POOL_0],
        resource_runtime_spec=ResourceRuntimeSpec(
            ray_spec=RaySpec(resource_pool_images={"head-node": _TEST_GPU_IMAGE}),
        ),
        network=ProjectConstants._TEST_VPC_NETWORK,
        labels=_TEST_LABELS,
    )
    # Get response has generated name, and URIs
    _TEST_RESPONSE_RUNNING_1_POOL = PersistentResource(
        name=_TEST_VERTEX_RAY_PR_ADDRESS,
        resource_pools=[_TEST_RESOURCE_POOL_0],
        resource_runtime_spec=ResourceRuntimeSpec(
            ray_spec=RaySpec(resource_pool_images={"head-node": _TEST_GPU_IMAGE}),
        ),
        network=ProjectConstants._TEST_VPC_NETWORK,
        resource_runtime=ResourceRuntime(
            access_uris={
                "RAY_DASHBOARD_URI": _TEST_VERTEX_RAY_DASHBOARD_ADDRESS,
                "RAY_HEAD_NODE_INTERNAL_IP": _TEST_VERTEX_RAY_HEAD_NODE_IP,
            }
        ),
        state="RUNNING",
    )
    # 2_POOL: worker_node_types and head_node_type have different MachineSpecs
    _TEST_HEAD_NODE_TYPE_2_POOLS = Resources()
    _TEST_WORKER_NODE_TYPES_2_POOLS = [
        Resources(
            machine_type="n1-standard-16",
            node_count=4,
            accelerator_type="NVIDIA_TESLA_P100",
            accelerator_count=1,
        )
    ]
    _TEST_RESOURCE_POOL_1 = ResourcePool(
        id="head-node",
        machine_spec=MachineSpec(
            machine_type="n1-standard-4",
        ),
        disk_spec=DiskSpec(
            boot_disk_type="pd-ssd",
            boot_disk_size_gb=100,
        ),
        replica_count=1,
    )
    _TEST_RESOURCE_POOL_2 = ResourcePool(
        id="worker-pool1",
        machine_spec=MachineSpec(
            machine_type="n1-standard-16",
            accelerator_type="NVIDIA_TESLA_P100",
            accelerator_count=1,
        ),
        disk_spec=DiskSpec(
            boot_disk_type="pd-ssd",
            boot_disk_size_gb=100,
        ),
        replica_count=4,
    )
    _TEST_REQUEST_RUNNING_2_POOLS = PersistentResource(
        resource_pools=[_TEST_RESOURCE_POOL_1, _TEST_RESOURCE_POOL_2],
        resource_runtime_spec=ResourceRuntimeSpec(
            ray_spec=RaySpec(
                resource_pool_images={
                    "head-node": _TEST_CPU_IMAGE,
                    "worker-pool1": _TEST_GPU_IMAGE,
                }
            ),
        ),
        network=ProjectConstants._TEST_VPC_NETWORK,
    )
    _TEST_RESPONSE_RUNNING_2_POOLS = PersistentResource(
        name=_TEST_VERTEX_RAY_PR_ADDRESS,
        resource_pools=[_TEST_RESOURCE_POOL_1, _TEST_RESOURCE_POOL_2],
        resource_runtime_spec=ResourceRuntimeSpec(
            ray_spec=RaySpec(resource_pool_images={"head-node": _TEST_GPU_IMAGE}),
        ),
        network=ProjectConstants._TEST_VPC_NETWORK,
        resource_runtime=ResourceRuntime(
            access_uris={
                "RAY_DASHBOARD_URI": _TEST_VERTEX_RAY_DASHBOARD_ADDRESS,
                "RAY_HEAD_NODE_INTERNAL_IP": _TEST_VERTEX_RAY_HEAD_NODE_IP,
            }
        ),
        state="RUNNING",
    )
    _TEST_CLUSTER = Cluster(
        cluster_resource_name=_TEST_VERTEX_RAY_PR_ADDRESS,
        python_version="3_10",
        ray_version="2_4",
        network=ProjectConstants._TEST_VPC_NETWORK,
        state="RUNNING",
        head_node_type=_TEST_HEAD_NODE_TYPE_1_POOL,
        worker_node_types=_TEST_WORKER_NODE_TYPES_1_POOL,
        dashboard_address=_TEST_VERTEX_RAY_DASHBOARD_ADDRESS,
    )
    _TEST_CLUSTER_2 = Cluster(
        cluster_resource_name=_TEST_VERTEX_RAY_PR_ADDRESS,
        python_version="3_10",
        ray_version="2_4",
        network=ProjectConstants._TEST_VPC_NETWORK,
        state="RUNNING",
        head_node_type=_TEST_HEAD_NODE_TYPE_2_POOLS,
        worker_node_types=_TEST_WORKER_NODE_TYPES_2_POOLS,
        dashboard_address=_TEST_VERTEX_RAY_DASHBOARD_ADDRESS,
    )
    _TEST_BEARER_TOKEN = "test-bearer-token"
    _TEST_HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(_TEST_BEARER_TOKEN),
    }
