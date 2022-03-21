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

from google.cloud import aiplatform
from google.cloud.aiplatform.compat.types import job_state as gca_job_state
from tests.system.aiplatform import e2e_base

_SCRIPT = """
from google.cloud import aiplatform
# Not initializing the Vertex SDK explicitly
# Checking the project ID
print(aiplatform.initializer.global_config.project)
assert not aiplatform.initializer.global_config.project.endswith("-tp")
"""


@pytest.mark.usefixtures("prepare_staging_bucket", "delete_staging_bucket")
class TestProjectIDInference(e2e_base.TestEndToEnd):

    _temp_prefix = "temp-vertex-sdk-project-id-inference"

    def test_project_id_inference(self, shared_state):
        # Collection of resources generated by this test, to be deleted during teardown
        shared_state["resources"] = []

        aiplatform.init(
            location=e2e_base._LOCATION,
            staging_bucket=shared_state["staging_bucket_name"],
        )

        worker_pool_specs = [
            {
                "machine_spec": {"machine_type": "n1-standard-4"},
                "replica_count": 1,
                "container_spec": {
                    "image_uri": "python:3.9",
                    "command": [
                        "sh",
                        "-exc",
                        """python3 -m pip install git+https://github.com/googleapis/python-aiplatform@main
                            "$0" "$@"
                            """,
                        "python3",
                        "-c",
                        _SCRIPT,
                    ],
                    "args": [],
                },
            }
        ]

        custom_job = aiplatform.CustomJob(
            display_name=self._make_display_name("custom"),
            worker_pool_specs=worker_pool_specs,
        )
        custom_job.run()

        shared_state["resources"].append(custom_job)

        assert custom_job.state == gca_job_state.JobState.JOB_STATE_SUCCEEDED
