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

import importlib
from unittest import mock

import vertexai
from vertexai._genai import prompt_optimizer
from vertexai._genai import types
from google.genai import client
import pytest


_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
pytestmark = pytest.mark.usefixtures("google_auth_mock")
_TEST_PROJECT_NUMBER = "12345678"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_DISPLAY_NAME = f"{_TEST_PARENT}/customJobs/12345"
_TEST_BASE_OUTPUT_DIR = "gs://test_bucket/test_base_output_dir"


class TestPromptOptimizer:
    """Unit tests for the Prompt Optimizer client."""

    def setup_method(self):
        importlib.reload(vertexai)
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

    @pytest.mark.usefixtures("google_auth_mock")
    def test_prompt_optimizer_client(self):
        test_client = vertexai.Client(project=_TEST_PROJECT, location=_TEST_LOCATION)
        assert test_client.prompt_optimizer is not None

    @mock.patch.object(client.Client, "_get_api_client")
    @mock.patch.object(prompt_optimizer.PromptOptimizer, "_create_custom_job_resource")
    def test_prompt_optimizer_optimize(self, mock_custom_job, mock_client):
        """Test that prompt_optimizer.optimize method creates a custom job."""
        test_client = vertexai.Client(project=_TEST_PROJECT, location=_TEST_LOCATION)
        test_client.prompt_optimizer.optimize(
            method="vapo",
            config=types.PromptOptimizerVAPOConfig(
                config_path="gs://ssusie-vapo-sdk-test/config.json",
                wait_for_completion=False,
                service_account="test-service-account",
            ),
        )
        mock_client.assert_called_once()
        mock_custom_job.assert_called_once()

    # TODO(b/415060797): add more tests for prompt_optimizer.optimize
