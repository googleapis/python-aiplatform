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

import os

import pytest
from unittest import mock

from google.cloud import aiplatform
from google.cloud.aiplatform.constants import base as constants
from google.cloud.aiplatform.utils import resource_manager_utils
from google.cloud.aiplatform.compat.types import job_state as gca_job_state
from tests.system.aiplatform import e2e_base

_PREBUILT_CONTAINER_IMAGE = (
    "us-docker.pkg.dev/vertex-ai/training/sklearn-cpu.1-0:latest"
)
_CUSTOM_CONTAINER_IMAGE = "python:3.8"

_DIR_NAME = os.path.dirname(os.path.abspath(__file__))
_LOCAL_TRAINING_SCRIPT_PATH = os.path.join(
    _DIR_NAME, "test_resources/custom_job_script.py"
)


@mock.patch.object(
    constants,
    "AIPLATFORM_DEPENDENCY_PATH",
    "google-cloud-aiplatform @ git+https://github.com/googleapis/"
    f"python-aiplatform.git@{os.environ['KOKORO_GIT_COMMIT']}#egg=google-cloud-aiplatform"
    if os.environ.get("KOKORO_GIT_COMMIT")
    else constants.AIPLATFORM_DEPENDENCY_PATH,
)
@mock.patch.object(
    constants,
    "AIPLATFORM_AUTOLOG_DEPENDENCY_PATH",
    "google-cloud-aiplatform[autologging] @ git+https://github.com/googleapis/"
    f"python-aiplatform.git@{os.environ['KOKORO_GIT_COMMIT']}#egg=google-cloud-aiplatform"
    if os.environ.get("KOKORO_GIT_COMMIT")
    else constants.AIPLATFORM_AUTOLOG_DEPENDENCY_PATH,
)
@pytest.mark.usefixtures(
    "prepare_staging_bucket", "delete_staging_bucket", "tear_down_resources"
)
class TestCustomJob(e2e_base.TestEndToEnd):

    _temp_prefix = "temp-vertex-sdk-custom-job"

    def setup_class(cls):
        cls._experiment_name = cls._make_display_name("experiment")[:60]
        cls._experiment_run_name = cls._make_display_name("experiment-run")[:60]

        project_number = resource_manager_utils.get_project_number(e2e_base._PROJECT)
        cls._service_account = f"{project_number}-compute@developer.gserviceaccount.com"

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
            requirements=["scikit-learn", "pandas"],
        )
        try:
            custom_job.run()
        finally:
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
            requirements=["scikit-learn", "pandas"],
        )
        try:
            custom_job.run()
        finally:
            shared_state["resources"].append(custom_job)

        assert custom_job.state == gca_job_state.JobState.JOB_STATE_SUCCEEDED

    def test_from_local_script_enable_autolog_prebuilt_container(self, shared_state):

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            staging_bucket=shared_state["staging_bucket_name"],
            experiment=self._experiment_name,
        )

        shared_state["resources"].append(
            aiplatform.metadata.metadata._experiment_tracker.experiment
        )

        display_name = self._make_display_name("custom-job")

        custom_job = aiplatform.CustomJob.from_local_script(
            display_name=display_name,
            script_path=_LOCAL_TRAINING_SCRIPT_PATH,
            container_uri=_PREBUILT_CONTAINER_IMAGE,
            requirements=["scikit-learn", "pandas"],
            enable_autolog=True,
        )

        try:
            with aiplatform.start_run(self._experiment_run_name) as run:
                shared_state["resources"].append(run)
                custom_job.run(
                    experiment=self._experiment_name,
                    experiment_run=run,
                    service_account=self._service_account,
                )
        finally:
            shared_state["resources"].append(custom_job)

        assert custom_job.state == gca_job_state.JobState.JOB_STATE_SUCCEEDED

    def test_from_local_script_enable_autolog_custom_container(self, shared_state):

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
            requirements=["scikit-learn", "pandas"],
            enable_autolog=True,
        )

        # Let the job auto-create the experiment run.
        try:
            custom_job.run(
                experiment=self._experiment_name,
                service_account=self._service_account,
            )
        finally:
            shared_state["resources"].append(custom_job)
            experiment_run_resource = aiplatform.Context.get(
                custom_job.job_spec.experiment_run
            )
            if experiment_run_resource:
                shared_state["resources"].append(experiment_run_resource)

        assert custom_job.state == gca_job_state.JobState.JOB_STATE_SUCCEEDED
