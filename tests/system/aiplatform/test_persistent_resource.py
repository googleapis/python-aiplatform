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

import importlib

from google.cloud import aiplatform
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import persistent_resource
from google.cloud.aiplatform.compat.types import (
    machine_resources_v1 as gca_machine_resources,
)
from google.cloud.aiplatform.compat.types import (
    persistent_resource_v1 as gca_persistent_resource,
)
from tests.system.aiplatform import e2e_base
import pytest


_TEST_MACHINE_TYPE = "n1-standard-4"
_TEST_INITIAL_REPLICA_COUNT = 2


@pytest.mark.usefixtures("tear_down_resources")
class TestPersistentResource(e2e_base.TestEndToEnd):
    _temp_prefix = "test-pr-e2e"

    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)

        aiplatform.init(project=e2e_base._PROJECT, location=e2e_base._LOCATION)
        self.resources = []

    def test_create_persistent_resource(self, shared_state):
        # PersistentResource ID must be shorter than 64 characters.
        # IE: "test-pr-e2e-ea3ae19d-3d94-4818-8ecd-1a7a63d7418c"
        resource_id = self._make_display_name("")
        resource_pools = [
            gca_persistent_resource.ResourcePool(
                machine_spec=gca_machine_resources.MachineSpec(
                    machine_type=_TEST_MACHINE_TYPE,
                ),
                replica_count=_TEST_INITIAL_REPLICA_COUNT,
            )
        ]

        test_resource = persistent_resource.PersistentResource.create(
            persistent_resource_id=resource_id, resource_pools=resource_pools
        )

        shared_state["resources"] = [test_resource]

        assert (
            test_resource.state
            == gca_persistent_resource.PersistentResource.State.RUNNING
        )
