# Copyright 2025 Google LLC
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
# pylint: disable=protected-access,bad-continuation
import copy
import importlib
from unittest import mock

from google.cloud import aiplatform
import vertexai
from google.cloud.aiplatform import initializer as aiplatform_initializer
from google.cloud.aiplatform.compat.services import job_service_client
from google.cloud.aiplatform.compat.types import (
    custom_job as gca_custom_job_compat,
)
from google.cloud.aiplatform.compat.types import io as gca_io_compat
from google.cloud.aiplatform.compat.types import (
    job_state as gca_job_state_compat,
)

# from google.cloud.aiplatform.utils import gcs_utils
# from google.genai import client
import pytest


_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
pytestmark = pytest.mark.usefixtures("google_auth_mock")
_TEST_PROJECT_NUMBER = "12345678"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_DISPLAY_NAME = f"{_TEST_PARENT}/customJobs/12345"
_TEST_BASE_OUTPUT_DIR = "gs://test_bucket/test_base_output_dir"

_TEST_CUSTOM_JOB_PROTO = gca_custom_job_compat.CustomJob(
    display_name=_TEST_DISPLAY_NAME,
    job_spec={
        "base_output_directory": gca_io_compat.GcsDestination(
            output_uri_prefix=_TEST_BASE_OUTPUT_DIR
        ),
    },
    labels={"trained_by_vertex_ai": "true"},
)


@pytest.fixture
def mock_create_custom_job():
    with mock.patch.object(
        job_service_client.JobServiceClient, "create_custom_job"
    ) as create_custom_job_mock:
        custom_job_proto = copy.deepcopy(_TEST_CUSTOM_JOB_PROTO)
        custom_job_proto.name = _TEST_DISPLAY_NAME
        custom_job_proto.state = gca_job_state_compat.JobState.JOB_STATE_PENDING
        create_custom_job_mock.return_value = custom_job_proto
        yield create_custom_job_mock


class TestPromptOptimizer:
    """Unit tests for the Prompt Optimizer client."""

    def setup_method(self):
        importlib.reload(aiplatform_initializer)
        importlib.reload(aiplatform)
        importlib.reload(vertexai)
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

    # @pytest.mark.usefixtures("google_auth_mock")
    # def test_prompt_optimizer_client(self):
    #     test_client = vertexai.Client(project=_TEST_PROJECT, location=_TEST_LOCATION)
    #     assert test_client is not None
    #     assert test_client._api_client.vertexai
    #     assert test_client._api_client.project == _TEST_PROJECT
    #     assert test_client._api_client.location == _TEST_LOCATION

    # @mock.patch.object(client.Client, "_get_api_client")
    # @mock.patch.object(
    #     gcs_utils.resource_manager_utils, "get_project_number", return_value=12345
    # )
    # def test_prompt_optimizer_optimize(
    #     self, mock_get_project_number, mock_client, mock_create_custom_job
    # ):
    #     """Test that prompt_optimizer.optimize method creates a custom job."""
    #     test_client = vertexai.Client(project=_TEST_PROJECT, location=_TEST_LOCATION)
    #     test_client.prompt_optimizer.optimize(
    #         method="vapo",
    #         config={
    #             "config_path": "gs://ssusie-vapo-sdk-test/config.json",
    #             "wait_for_completion": False,
    #         },
    #     )
    #     mock_create_custom_job.assert_called_once()
    #     mock_get_project_number.assert_called_once()
