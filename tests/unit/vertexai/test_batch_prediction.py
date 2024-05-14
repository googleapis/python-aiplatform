# -*- coding: utf-8 -*-

# Copyright 2024 Google LLC
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
"""Unit tests for generative model batch prediction."""
# pylint: disable=protected-access

import pytest
from unittest import mock

import vertexai
from google.cloud.aiplatform import base as aiplatform_base
from google.cloud.aiplatform import initializer as aiplatform_initializer
from google.cloud.aiplatform.compat.services import job_service_client
from google.cloud.aiplatform.compat.types import (
    batch_prediction_job as gca_batch_prediction_job_compat,
)
from google.cloud.aiplatform.compat.types import (
    job_state as gca_job_state_compat,
)
from vertexai.preview import batch_prediction


_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"

_TEST_GEMINI_MODEL_NAME = "gemini-1.0-pro"
_TEST_GEMINI_MODEL_RESOURCE_NAME = f"publishers/google/models/{_TEST_GEMINI_MODEL_NAME}"
_TEST_PALM_MODEL_NAME = "text-bison"
_TEST_PALM_MODEL_RESOURCE_NAME = f"publishers/google/models/{_TEST_PALM_MODEL_NAME}"

_TEST_BATCH_PREDICTION_JOB_ID = "123456789"
_TEST_BATCH_PREDICTION_JOB_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/batchPredictionJobs/{_TEST_BATCH_PREDICTION_JOB_ID}"
_TEST_JOB_STATE_SUCCESS = gca_job_state_compat.JobState(4)


# TODO(b/339230025) Mock the whole service instead of methods.
@pytest.fixture
def get_batch_prediction_job_mock():
    with mock.patch.object(
        job_service_client.JobServiceClient, "get_batch_prediction_job"
    ) as get_job_mock:
        get_job_mock.return_value = gca_batch_prediction_job_compat.BatchPredictionJob(
            name=_TEST_BATCH_PREDICTION_JOB_NAME,
            model=_TEST_GEMINI_MODEL_RESOURCE_NAME,
            state=_TEST_JOB_STATE_SUCCESS,
        )
        yield get_job_mock


@pytest.fixture
def get_batch_prediction_job_invalid_model_mock():
    with mock.patch.object(
        job_service_client.JobServiceClient, "get_batch_prediction_job"
    ) as get_job_mock:
        get_job_mock.return_value = gca_batch_prediction_job_compat.BatchPredictionJob(
            name=_TEST_BATCH_PREDICTION_JOB_NAME,
            model=_TEST_PALM_MODEL_RESOURCE_NAME,
            state=_TEST_JOB_STATE_SUCCESS,
        )
        yield get_job_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestBatchPredictionJob:
    """Unit tests for BatchPredictionJob."""

    def setup_method(self):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

    def teardown_method(self):
        aiplatform_initializer.global_pool.shutdown(wait=True)

    def test_init_batch_prediction_job(self, get_batch_prediction_job_mock):
        batch_prediction.BatchPredictionJob(_TEST_BATCH_PREDICTION_JOB_ID)

        get_batch_prediction_job_mock.assert_called_once_with(
            name=_TEST_BATCH_PREDICTION_JOB_NAME, retry=aiplatform_base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures("get_batch_prediction_job_invalid_model_mock")
    def test_init_batch_prediction_job_invalid_model(self):
        with pytest.raises(
            ValueError,
            match=(
                f"BatchPredictionJob '{_TEST_BATCH_PREDICTION_JOB_ID}' "
                f"runs with the model '{_TEST_PALM_MODEL_RESOURCE_NAME}', "
                "which is not a GenAI model."
            ),
        ):
            batch_prediction.BatchPredictionJob(_TEST_BATCH_PREDICTION_JOB_ID)
