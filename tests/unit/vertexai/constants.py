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

from vertexai.preview._workflow.shared import configs
from google.cloud.aiplatform_v1beta1.types.persistent_resource import (
    PersistentResource,
    ResourcePool,
)

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_CLUSTER_NAME = "test-cluster"
_TEST_CLUSTER_CONFIG = configs.PersistentResourceConfig(name=_TEST_CLUSTER_NAME)
_TEST_CLUSTER_RESOURCE_NAME = f"{_TEST_PARENT}/persistentResources/{_TEST_CLUSTER_NAME}"


_TEST_PERSISTENT_RESOURCE_ERROR = PersistentResource()
_TEST_PERSISTENT_RESOURCE_ERROR.state = "ERROR"

# move to constants
_TEST_REQUEST_RUNNING_DEFAULT = PersistentResource()
resource_pool = ResourcePool()
resource_pool.machine_spec.machine_type = "n1-standard-4"
resource_pool.replica_count = 1
resource_pool.disk_spec.boot_disk_type = "pd-ssd"
resource_pool.disk_spec.boot_disk_size_gb = 100
_TEST_REQUEST_RUNNING_DEFAULT.resource_pools = [resource_pool]


_TEST_PERSISTENT_RESOURCE_RUNNING = PersistentResource()
_TEST_PERSISTENT_RESOURCE_RUNNING.state = "RUNNING"
