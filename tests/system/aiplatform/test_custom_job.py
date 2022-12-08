# -*- coding: utf-8 -*-

# Copyright 2022 Google LLC
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

import os

import pytest

from google.cloud import aiplatform
from google.cloud.aiplatform.compat.types import job_state as gca_job_state
from tests.system.aiplatform import e2e_base

_PREBUILT_CONTAINER_IMAGE = "gcr.io/cloud-aiplatform/training/tf-cpu.2-2:latest"
_CUSTOM_CONTAINER_IMAGE = "python:3.8"

_DIR_NAME = os.path.dirname(os.path.abspath(__file__))
_LOCAL_TRAINING_SCRIPT_PATH = os.path.join(
    _DIR_NAME, "test_resources/custom_job_script.py"
)


@pytest.mark.usefixtures(
    "prepare_staging_bucket", "delete_staging_bucket", "tear_down_resources"
)
class TestCustomJob(e2e_base.TestEndToEnd):

    _temp_prefix = "temp-vertex-sdk-custom-job"

    def test_from_local_script_prebuilt_container(self, shared_state):
        shared_state["resources"] = []

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            staging_bucket=shared_state["staging_bucket_name"],
        )

        display_name = self._make_display_name("custom-job")

        custom_job = aiplatform.CustomJob.from_local_script(
            display_name=display_name,
            script_path=_LOCAL_TRAINING_SCRIPT_PATH,
            container_uri=_PREBUILT_CONTAINER_IMAGE,
        )
        custom_job.run()

        shared_state["resources"].append(custom_job)

        assert custom_job.state == gca_job_state.JobState.JOB_STATE_SUCCEEDED

    def test_from_local_script_custom_container(self, shared_state):

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            staging_bucket=shared_state["staging_bucket_name"],
        )

        display_name = self._make_display_name("custom-job")

        custom_job = aiplatform.CustomJob.from_local_script(
            display_name=display_name,
            script_path=_LOCAL_TRAINING_SCRIPT_PATH,
            container_uri=_CUSTOM_CONTAINER_IMAGE,
        )
        custom_job.run()

        shared_state["resources"].append(custom_job)

        assert custom_job.state == gca_job_state.JobState.JOB_STATE_SUCCEEDED
