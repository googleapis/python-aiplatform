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

from importlib import reload
from unittest.mock import patch

from google.api_core import exceptions
from google.cloud import aiplatform
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.tensorboard import uploader_main
from google.cloud.aiplatform.compat.types import (
    job_state as gca_job_state_compat,
)
from google.cloud.aiplatform.compat.types import (
    custom_job as gca_custom_job_compat,
)
from google.cloud.aiplatform.compat.services import (
    job_service_client,
)

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_CUSTOM_JOB_ID = "445768"
_TEST_CUSTOM_JOB_NAME = f"{_TEST_PARENT}/customJobs/{_TEST_CUSTOM_JOB_ID}"
_TEST_CUSTOM_JOBS_DISPLAY_NAME = "a custom job display name"
_TEST_PASSED_IN_EXPERIMENT_DISPLAY_NAME = "someDisplayName"


def _get_custom_job_proto(state=None, name=None):
    custom_job_proto = gca_custom_job_compat.CustomJob()
    custom_job_proto.name = name
    custom_job_proto.state = state
    custom_job_proto.display_name = _TEST_CUSTOM_JOBS_DISPLAY_NAME
    return custom_job_proto


@pytest.fixture
def get_custom_job_mock_not_found():
    with patch.object(
        job_service_client.JobServiceClient, "get_custom_job"
    ) as get_custom_job_mock:
        get_custom_job_mock.side_effect = exceptions.NotFound("not found")
        yield get_custom_job_mock


@pytest.fixture
def get_custom_job_mock():
    with patch.object(
        job_service_client.JobServiceClient, "get_custom_job"
    ) as get_custom_job_mock:
        get_custom_job_mock.side_effect = [
            _get_custom_job_proto(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED,
            ),
        ]
        yield get_custom_job_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestUploaderMain:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_get_default_custom_job_display_name(self, get_custom_job_mock):
        aiplatform.init(project=_TEST_PROJECT)
        assert (
            uploader_main.get_experiment_display_name_with_override(
                _TEST_CUSTOM_JOB_ID, None, _TEST_PROJECT, _TEST_LOCATION
            )
            == _TEST_CUSTOM_JOBS_DISPLAY_NAME
        )

    def test_non_decimal_experiment_name(self, get_custom_job_mock):
        aiplatform.init(project=_TEST_PROJECT)
        assert (
            uploader_main.get_experiment_display_name_with_override(
                "someExperimentName",
                _TEST_PASSED_IN_EXPERIMENT_DISPLAY_NAME,
                _TEST_PROJECT,
                _TEST_LOCATION,
            )
            == _TEST_PASSED_IN_EXPERIMENT_DISPLAY_NAME
        )
        get_custom_job_mock.assert_not_called()

    def test_display_name_already_specified(self, get_custom_job_mock):
        aiplatform.init(project=_TEST_PROJECT)
        assert (
            uploader_main.get_experiment_display_name_with_override(
                _TEST_CUSTOM_JOB_ID,
                _TEST_PASSED_IN_EXPERIMENT_DISPLAY_NAME,
                _TEST_PROJECT,
                _TEST_LOCATION,
            )
            == _TEST_PASSED_IN_EXPERIMENT_DISPLAY_NAME
        )
        get_custom_job_mock.assert_not_called()

    def test_custom_job_not_found(self, get_custom_job_mock_not_found):
        aiplatform.init(project=_TEST_PROJECT)
        assert (
            uploader_main.get_experiment_display_name_with_override(
                _TEST_CUSTOM_JOB_ID,
                _TEST_PASSED_IN_EXPERIMENT_DISPLAY_NAME,
                _TEST_PROJECT,
                _TEST_LOCATION,
            )
            == _TEST_PASSED_IN_EXPERIMENT_DISPLAY_NAME
        )
