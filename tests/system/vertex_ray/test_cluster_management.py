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
import ray


class TestClusterManagement(e2e_base.TestEndToEnd):
    _temp_prefix = "temp-rov-cluster-management"

    def test_cluster_management(self):
        assert ray.__version__ == "2.4.0"
        aiplatform.init(project="ucaip-sample-tests", location="us-central1")

        clusters = vertex_ray.list_ray_clusters()
        assert clusters[0].ray_version == "2_4"
