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
import sys

from google.cloud.aiplatform.vertex_ray.util.resources import Cluster
from google.cloud.aiplatform.vertex_ray.util.resources import (
    AutoscalingSpec,
    PscIConfig,
    Resources,
)
from google.cloud.aiplatform_v1beta1.types.machine_resources import DiskSpec
from google.cloud.aiplatform_v1beta1.types.machine_resources import (
    MachineSpec,
)
from google.cloud.aiplatform_v1beta1.types.persistent_resource import (
    PersistentResource,
)
from google.cloud.aiplatform_v1beta1.types.persistent_resource import (
    RayLogsSpec,
    RayMetricSpec,
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
from google.cloud.aiplatform_v1beta1.types.persistent_resource import (
    ServiceAccountSpec,
)
from google.cloud.aiplatform_v1beta1.types.service_networking import (
    PscInterfaceConfig,
)
import ray
import pytest


rovminversion = pytest.mark.skipif(
    sys.version_info > (3, 10), reason="Requires python3.10 or lower"
)
# TODO(b/363340317)
xgbversion = pytest.mark.skipif(
    ray.__version__ != "2.9.3", reason="Requires xgboost 1.7 or higher"
)

predictionrayversion = pytest.mark.skipif(
    ray.__version__ != "2.9.3", reason="Not currently supported on Ray 2.33"
)


@dataclasses.dataclass(frozen=True)
class ProjectConstants:
    """Defines project-specific constants used by tests."""

    TEST_VPC_NETWORK = "mock-vpc-network"
    TEST_GCP_PROJECT_ID = "mock-test-project-id"
    TEST_GCP_PROJECT_ID_OVERRIDE = "mock-test-project-id-2"
    TEST_GCP_REGION = "us-central1"
    TEST_GCP_REGION_OVERRIDE = "asia-east1"
    TEST_GCP_PROJECT_NUMBER = "12345"
    TEST_PARENT = f"projects/{TEST_GCP_PROJECT_NUMBER}/locations/{TEST_GCP_REGION}"
    TEST_ARTIFACT_URI = "gs://path/to/artifact/uri"
    TEST_BAD_ARTIFACT_URI = "/path/to/artifact/uri"
    TEST_MODEL_GCS_URI = "gs://test_model_dir"
    TEST_MODEL_ID = (
        f"projects/{TEST_GCP_PROJECT_NUMBER}/locations/{TEST_GCP_REGION}/models/456"
    )
    TEST_SERVICE_ACCOUNT = "service-account@project.iam.gserviceaccount.com"


@dataclasses.dataclass(frozen=True)
class ClusterConstants:
    """Defines cluster constants used by tests."""

    TEST_LABELS = {"my_key": "my_value"}
    TEST_VERTEX_RAY_HEAD_NODE_IP = "1.2.3.4:10001"
    TEST_VERTEX_RAY_JOB_CLIENT_IP = "1.2.3.4:8888"
    TEST_VERTEX_RAY_DASHBOARD_ADDRESS = (
        "48b400ad90b8dd3c-dot-us-central1.aiplatform-training.googleusercontent.com"
    )
    TEST_VERTEX_RAY_CLIENT_ENDPOINT = (
        "88888.us-central1-1234567.staging-ray.vertexai.goog:443"
    )
    TEST_VERTEX_RAY_PR_ID = "user-persistent-resource-1234567890"
    TEST_VERTEX_RAY_PR_ADDRESS = (
        f"{ProjectConstants.TEST_PARENT}/persistentResources/" + TEST_VERTEX_RAY_PR_ID
    )
    TEST_CPU_IMAGE_2_9 = "us-docker.pkg.dev/vertex-ai/training/ray-cpu.2-9.py310:latest"
    TEST_GPU_IMAGE_2_9 = "us-docker.pkg.dev/vertex-ai/training/ray-gpu.2-9.py310:latest"
    TEST_CPU_IMAGE_2_33 = (
        "us-docker.pkg.dev/vertex-ai/training/ray-cpu.2-33.py310:latest"
    )
    TEST_GPU_IMAGE_2_33 = (
        "us-docker.pkg.dev/vertex-ai/training/ray-gpu.2-33.py310:latest"
    )
    TEST_CUSTOM_IMAGE = "us-docker.pkg.dev/my-project/ray-custom-image.2.9:latest"
    TEST_PSC_NETWORK_ATTACHMENT = "my-network-attachment"
    # RUNNING Persistent Cluster w/o Ray
    TEST_RESPONSE_NO_RAY_RUNNING = PersistentResource(
        name=TEST_VERTEX_RAY_PR_ADDRESS,
        resource_runtime_spec=ResourceRuntimeSpec(),
        resource_runtime=ResourceRuntime(),
        state="RUNNING",
    )
    # RUNNING
    # 1_POOL: merged worker_node_types and head_node_type with duplicate MachineSpec
    TEST_HEAD_NODE_TYPE_1_POOL = Resources(
        accelerator_type="NVIDIA_TESLA_P100", accelerator_count=1
    )
    TEST_WORKER_NODE_TYPES_1_POOL = [
        Resources(
            accelerator_type="NVIDIA_TESLA_P100", accelerator_count=1, node_count=2
        )
    ]
    TEST_RESOURCE_POOL_0 = ResourcePool(
        id="head-node",
        machine_spec=MachineSpec(
            machine_type="n1-standard-16",
            accelerator_type="NVIDIA_TESLA_P100",
            accelerator_count=1,
        ),
        disk_spec=DiskSpec(
            boot_disk_type="pd-ssd",
            boot_disk_size_gb=100,
        ),
        replica_count=3,
    )
    TEST_REQUEST_RUNNING_1_POOL = PersistentResource(
        resource_pools=[TEST_RESOURCE_POOL_0],
        resource_runtime_spec=ResourceRuntimeSpec(
            ray_spec=RaySpec(
                resource_pool_images={"head-node": TEST_GPU_IMAGE_2_9},
                ray_metric_spec=RayMetricSpec(disabled=False),
                ray_logs_spec=RayLogsSpec(disabled=False),
            ),
        ),
        psc_interface_config=None,
        network=ProjectConstants.TEST_VPC_NETWORK,
    )
    TEST_REQUEST_RUNNING_1_POOL_WITH_LABELS = PersistentResource(
        resource_pools=[TEST_RESOURCE_POOL_0],
        resource_runtime_spec=ResourceRuntimeSpec(
            ray_spec=RaySpec(
                resource_pool_images={"head-node": TEST_GPU_IMAGE_2_9},
                ray_metric_spec=RayMetricSpec(disabled=True),
                ray_logs_spec=RayLogsSpec(disabled=True),
            ),
        ),
        psc_interface_config=None,
        network=ProjectConstants.TEST_VPC_NETWORK,
        labels=TEST_LABELS,
    )
    TEST_REQUEST_RUNNING_1_POOL_CUSTOM_IMAGES = PersistentResource(
        resource_pools=[TEST_RESOURCE_POOL_0],
        resource_runtime_spec=ResourceRuntimeSpec(
            ray_spec=RaySpec(
                resource_pool_images={"head-node": TEST_CUSTOM_IMAGE},
                ray_metric_spec=RayMetricSpec(disabled=False),
                ray_logs_spec=RayLogsSpec(disabled=False),
            ),
        ),
        psc_interface_config=None,
        network=ProjectConstants.TEST_VPC_NETWORK,
    )
    TEST_REQUEST_RUNNING_1_POOL_BYOSA = PersistentResource(
        resource_pools=[TEST_RESOURCE_POOL_0],
        resource_runtime_spec=ResourceRuntimeSpec(
            ray_spec=RaySpec(
                resource_pool_images={"head-node": TEST_GPU_IMAGE_2_9},
                ray_metric_spec=RayMetricSpec(disabled=False),
                ray_logs_spec=RayLogsSpec(disabled=False),
            ),
            service_account_spec=ServiceAccountSpec(
                enable_custom_service_account=True,
                service_account=ProjectConstants.TEST_SERVICE_ACCOUNT,
            ),
        ),
        psc_interface_config=None,
        network=None,
    )
    # Get response has generated name, and URIs
    TEST_RESPONSE_RUNNING_1_POOL = PersistentResource(
        name=TEST_VERTEX_RAY_PR_ADDRESS,
        resource_pools=[TEST_RESOURCE_POOL_0],
        resource_runtime_spec=ResourceRuntimeSpec(
            ray_spec=RaySpec(
                resource_pool_images={"head-node": TEST_GPU_IMAGE_2_9},
                ray_metric_spec=RayMetricSpec(disabled=False),
                ray_logs_spec=RayLogsSpec(disabled=False),
            ),
        ),
        psc_interface_config=None,
        network=ProjectConstants.TEST_VPC_NETWORK,
        resource_runtime=ResourceRuntime(
            access_uris={
                "RAY_DASHBOARD_URI": TEST_VERTEX_RAY_DASHBOARD_ADDRESS,
                "RAY_HEAD_NODE_INTERNAL_IP": TEST_VERTEX_RAY_HEAD_NODE_IP,
            }
        ),
        state="RUNNING",
    )
    # Get response has generated name, and URIs
    TEST_RESPONSE_RUNNING_1_POOL_CUSTOM_IMAGES = PersistentResource(
        name=TEST_VERTEX_RAY_PR_ADDRESS,
        resource_pools=[TEST_RESOURCE_POOL_0],
        resource_runtime_spec=ResourceRuntimeSpec(
            ray_spec=RaySpec(
                resource_pool_images={"head-node": TEST_CUSTOM_IMAGE},
                ray_metric_spec=RayMetricSpec(disabled=False),
            ),
        ),
        psc_interface_config=None,
        network=ProjectConstants.TEST_VPC_NETWORK,
        resource_runtime=ResourceRuntime(
            access_uris={
                "RAY_DASHBOARD_URI": TEST_VERTEX_RAY_DASHBOARD_ADDRESS,
                "RAY_HEAD_NODE_INTERNAL_IP": TEST_VERTEX_RAY_HEAD_NODE_IP,
            }
        ),
        state="RUNNING",
    )
    TEST_RESPONSE_RUNNING_1_POOL_BYOSA = PersistentResource(
        name=TEST_VERTEX_RAY_PR_ADDRESS,
        resource_pools=[TEST_RESOURCE_POOL_0],
        resource_runtime_spec=ResourceRuntimeSpec(
            ray_spec=RaySpec(
                resource_pool_images={"head-node": TEST_GPU_IMAGE_2_9},
                ray_metric_spec=RayMetricSpec(disabled=False),
            ),
            service_account_spec=ServiceAccountSpec(
                enable_custom_service_account=True,
                service_account=ProjectConstants.TEST_SERVICE_ACCOUNT,
            ),
        ),
        psc_interface_config=None,
        network=None,
        resource_runtime=ResourceRuntime(
            access_uris={
                "RAY_DASHBOARD_URI": TEST_VERTEX_RAY_DASHBOARD_ADDRESS,
                "RAY_CLIENT_ENDPOINT": TEST_VERTEX_RAY_CLIENT_ENDPOINT,
            }
        ),
        state="RUNNING",
    )
    TEST_RESPONSE_1_POOL_BYOSA_PRIVATE = PersistentResource(
        name=TEST_VERTEX_RAY_PR_ADDRESS,
        resource_pools=[TEST_RESOURCE_POOL_0],
        resource_runtime_spec=ResourceRuntimeSpec(
            ray_spec=RaySpec(
                resource_pool_images={"head-node": TEST_GPU_IMAGE_2_9},
                ray_metric_spec=RayMetricSpec(disabled=False),
            ),
            service_account_spec=ServiceAccountSpec(
                enable_custom_service_account=True,
                service_account=ProjectConstants.TEST_SERVICE_ACCOUNT,
            ),
        ),
        psc_interface_config=None,
        network=ProjectConstants.TEST_VPC_NETWORK,
        resource_runtime=ResourceRuntime(
            access_uris={
                "RAY_DASHBOARD_URI": TEST_VERTEX_RAY_DASHBOARD_ADDRESS,
                "RAY_CLIENT_ENDPOINT": TEST_VERTEX_RAY_CLIENT_ENDPOINT,
            }
        ),
        state="RUNNING",
    )
    # 2_POOL: worker_node_types and head_node_type have different MachineSpecs
    TEST_HEAD_NODE_TYPE_2_POOLS = Resources()
    TEST_WORKER_NODE_TYPES_2_POOLS = [
        Resources(
            machine_type="n1-standard-16",
            autoscaling_spec=AutoscalingSpec(min_replica_count=1, max_replica_count=4),
            accelerator_type="NVIDIA_TESLA_P100",
            accelerator_count=1,
        )
    ]
    TEST_HEAD_NODE_TYPE_2_POOLS_CUSTOM_IMAGE = Resources(custom_image=TEST_CUSTOM_IMAGE)
    TEST_WORKER_NODE_TYPES_2_POOLS_CUSTOM_IMAGE = [
        Resources(
            machine_type="n1-standard-16",
            autoscaling_spec=AutoscalingSpec(min_replica_count=1, max_replica_count=4),
            accelerator_type="NVIDIA_TESLA_P100",
            accelerator_count=1,
            custom_image=TEST_CUSTOM_IMAGE,
        )
    ]
    TEST_RESOURCE_POOL_1 = ResourcePool(
        id="head-node",
        machine_spec=MachineSpec(
            machine_type="n1-standard-16",
        ),
        disk_spec=DiskSpec(
            boot_disk_type="pd-ssd",
            boot_disk_size_gb=100,
        ),
        replica_count=1,
    )
    TEST_RESOURCE_POOL_2 = ResourcePool(
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
        autoscaling_spec=ResourcePool.AutoscalingSpec(
            min_replica_count=1,
            max_replica_count=4,
        ),
    )
    TEST_REQUEST_RUNNING_2_POOLS = PersistentResource(
        resource_pools=[TEST_RESOURCE_POOL_1, TEST_RESOURCE_POOL_2],
        resource_runtime_spec=ResourceRuntimeSpec(
            ray_spec=RaySpec(
                resource_pool_images={
                    "head-node": TEST_CPU_IMAGE_2_9,
                    "worker-pool1": TEST_GPU_IMAGE_2_9,
                },
                ray_metric_spec=RayMetricSpec(disabled=False),
                ray_logs_spec=RayLogsSpec(disabled=False),
            ),
        ),
        psc_interface_config=PscInterfaceConfig(
            network_attachment=TEST_PSC_NETWORK_ATTACHMENT
        ),
    )
    TEST_REQUEST_RUNNING_2_POOLS_CUSTOM_IMAGE = PersistentResource(
        resource_pools=[TEST_RESOURCE_POOL_1, TEST_RESOURCE_POOL_2],
        resource_runtime_spec=ResourceRuntimeSpec(
            ray_spec=RaySpec(
                resource_pool_images={
                    "head-node": TEST_CUSTOM_IMAGE,
                    "worker-pool1": TEST_CUSTOM_IMAGE,
                },
                ray_metric_spec=RayMetricSpec(disabled=False),
                ray_logs_spec=RayLogsSpec(disabled=False),
            ),
        ),
        psc_interface_config=None,
        network=ProjectConstants.TEST_VPC_NETWORK,
        reserved_ip_ranges=["vertex-dedicated-range"],
    )
    # Responses
    TEST_RESOURCE_POOL_2.replica_count = 1
    TEST_RESPONSE_RUNNING_2_POOLS = PersistentResource(
        name=TEST_VERTEX_RAY_PR_ADDRESS,
        resource_pools=[TEST_RESOURCE_POOL_1, TEST_RESOURCE_POOL_2],
        resource_runtime_spec=ResourceRuntimeSpec(
            ray_spec=RaySpec(
                resource_pool_images={
                    "head-node": TEST_CPU_IMAGE_2_9,
                    "worker-pool1": TEST_GPU_IMAGE_2_9,
                },
                ray_metric_spec=RayMetricSpec(disabled=False),
            ),
        ),
        psc_interface_config=PscInterfaceConfig(
            network_attachment=TEST_PSC_NETWORK_ATTACHMENT
        ),
        network=None,
        reserved_ip_ranges=None,
        resource_runtime=ResourceRuntime(
            access_uris={
                "RAY_DASHBOARD_URI": TEST_VERTEX_RAY_DASHBOARD_ADDRESS,
            }
        ),
        state="RUNNING",
    )
    TEST_RESPONSE_RUNNING_2_POOLS_CUSTOM_IMAGE = PersistentResource(
        name=TEST_VERTEX_RAY_PR_ADDRESS,
        resource_pools=[TEST_RESOURCE_POOL_1, TEST_RESOURCE_POOL_2],
        resource_runtime_spec=ResourceRuntimeSpec(
            ray_spec=RaySpec(
                resource_pool_images={
                    "head-node": TEST_CUSTOM_IMAGE,
                    "worker-pool1": TEST_CUSTOM_IMAGE,
                },
                ray_metric_spec=RayMetricSpec(disabled=False),
            ),
        ),
        network=ProjectConstants.TEST_VPC_NETWORK,
        reserved_ip_ranges=["vertex-dedicated-range"],
        resource_runtime=ResourceRuntime(
            access_uris={
                "RAY_DASHBOARD_URI": TEST_VERTEX_RAY_DASHBOARD_ADDRESS,
                "RAY_HEAD_NODE_INTERNAL_IP": TEST_VERTEX_RAY_HEAD_NODE_IP,
            }
        ),
        state="RUNNING",
    )
    TEST_CLUSTER = Cluster(
        cluster_resource_name=TEST_VERTEX_RAY_PR_ADDRESS,
        python_version="3.10",
        ray_version="2.9",
        network=ProjectConstants.TEST_VPC_NETWORK,
        reserved_ip_ranges=None,
        service_account=None,
        state="RUNNING",
        head_node_type=TEST_HEAD_NODE_TYPE_1_POOL,
        worker_node_types=TEST_WORKER_NODE_TYPES_1_POOL,
        dashboard_address=TEST_VERTEX_RAY_DASHBOARD_ADDRESS,
        ray_metric_enabled=True,
        ray_logs_enabled=True,
    )
    TEST_CLUSTER_2 = Cluster(
        cluster_resource_name=TEST_VERTEX_RAY_PR_ADDRESS,
        python_version="3.10",
        ray_version="2.9",
        network="",
        reserved_ip_ranges="",
        service_account=None,
        state="RUNNING",
        head_node_type=TEST_HEAD_NODE_TYPE_2_POOLS,
        worker_node_types=TEST_WORKER_NODE_TYPES_2_POOLS,
        dashboard_address=TEST_VERTEX_RAY_DASHBOARD_ADDRESS,
        ray_metric_enabled=True,
        ray_logs_enabled=True,
        psc_interface_config=PscIConfig(network_attachment=TEST_PSC_NETWORK_ATTACHMENT),
    )
    TEST_CLUSTER_CUSTOM_IMAGE = Cluster(
        cluster_resource_name=TEST_VERTEX_RAY_PR_ADDRESS,
        network=ProjectConstants.TEST_VPC_NETWORK,
        reserved_ip_ranges=["vertex-dedicated-range"],
        service_account=None,
        state="RUNNING",
        head_node_type=TEST_HEAD_NODE_TYPE_2_POOLS_CUSTOM_IMAGE,
        worker_node_types=TEST_WORKER_NODE_TYPES_2_POOLS_CUSTOM_IMAGE,
        dashboard_address=TEST_VERTEX_RAY_DASHBOARD_ADDRESS,
        ray_metric_enabled=True,
        ray_logs_enabled=True,
        labels={},
    )
    TEST_CLUSTER_BYOSA = Cluster(
        cluster_resource_name=TEST_VERTEX_RAY_PR_ADDRESS,
        python_version="3.10",
        ray_version="2.9",
        network="",
        reserved_ip_ranges="",
        service_account=ProjectConstants.TEST_SERVICE_ACCOUNT,
        state="RUNNING",
        head_node_type=TEST_HEAD_NODE_TYPE_1_POOL,
        worker_node_types=TEST_WORKER_NODE_TYPES_1_POOL,
        dashboard_address=TEST_VERTEX_RAY_DASHBOARD_ADDRESS,
        ray_metric_enabled=True,
        ray_logs_enabled=True,
    )
    TEST_BEARER_TOKEN = "test-bearer-token"
    TEST_HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(TEST_BEARER_TOKEN),
    }
