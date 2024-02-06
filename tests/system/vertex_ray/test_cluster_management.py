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

from google.cloud import aiplatform
from google.cloud.aiplatform.preview import vertex_ray
from tests.system.aiplatform import e2e_base
import datetime
import ray

RAY_VERSION = "2.4.0"
CLUSTER_RAY_VERSION = "2_4"
PROJECT_ID = "ucaip-sample-tests"


class TestClusterManagement(e2e_base.TestEndToEnd):
    _temp_prefix = "temp-rov-cluster-management"

    def test_cluster_management(self):
        assert ray.__version__ == RAY_VERSION
        aiplatform.init(project=PROJECT_ID, location="us-central1")

        # CPU default cluster
        head_node_type = vertex_ray.Resources()
        worker_node_types = [vertex_ray.Resources()]

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        cluster_resource_name = vertex_ray.create_ray_cluster(
            head_node_type=head_node_type,
            worker_node_types=worker_node_types,
            cluster_name=f"ray-cluster-{timestamp}-test-cluster-management",
        )

        cluster_details = vertex_ray.get_ray_cluster(cluster_resource_name)
        assert cluster_details.ray_version == CLUSTER_RAY_VERSION
        assert cluster_details.state == "RUNNING"

        found_cluster = False
        for cluster in vertex_ray.list_ray_clusters():
            if cluster.cluster_resource_name == cluster_resource_name:
                assert cluster.ray_version == CLUSTER_RAY_VERSION
                assert cluster.state == "RUNNING"
                found_cluster = True

        if not found_cluster:
            raise ValueError(
                f"Cluster {cluster_resource_name} not found in list_ray_clusters"
            )

        vertex_ray.delete_ray_cluster(cluster_resource_name)
        # Ensure cluster was deleted
        for cluster in vertex_ray.list_ray_clusters():
            assert cluster.cluster_resource_name != cluster_resource_name
