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

import importlib
import pytest
from unittest import mock

from google.cloud import aiplatform
import vertexai
from google.cloud.aiplatform import base as aiplatform_base
from google.cloud.aiplatform import initializer as aiplatform_initializer
from google.cloud.aiplatform.compat.services import (
    job_service_client,
    model_service_client,
)
from google.cloud.aiplatform.compat.types import (
    batch_prediction_job as gca_batch_prediction_job_compat,
    io as gca_io_compat,
    job_state as gca_job_state_compat,
    model as gca_model,
)
from vertexai.preview import batch_prediction
from vertexai.generative_models import GenerativeModel


_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_BUCKET = "gs://test-bucket"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_DISPLAY_NAME = "test-display-name"

_TEST_GEMINI_MODEL_NAME = "gemini-1.0-pro"
_TEST_GEMINI_MODEL_RESOURCE_NAME = f"publishers/google/models/{_TEST_GEMINI_MODEL_NAME}"
_TEST_TUNED_GEMINI_MODEL_RESOURCE_NAME = "projects/123/locations/us-central1/models/456"
_TEST_PALM_MODEL_NAME = "text-bison"
_TEST_PALM_MODEL_RESOURCE_NAME = f"publishers/google/models/{_TEST_PALM_MODEL_NAME}"

_TEST_GCS_INPUT_URI = "gs://test-bucket/test-input.jsonl"
_TEST_GCS_INPUT_URI_2 = "gs://test-bucket/test-input-2.jsonl"
_TEST_GCS_OUTPUT_PREFIX = "gs://test-bucket/test-output"
_TEST_BQ_INPUT_URI = "bq://test-project.test-dataset.test-input"
_TEST_BQ_OUTPUT_PREFIX = "bq://test-project.test-dataset.test-output"
_TEST_INVALID_URI = "invalid-uri"


_TEST_BATCH_PREDICTION_JOB_ID = "123456789"
_TEST_BATCH_PREDICTION_JOB_NAME = (
    f"{_TEST_PARENT}/batchPredictionJobs/{_TEST_BATCH_PREDICTION_JOB_ID}"
)
_TEST_JOB_STATE_RUNNING = gca_job_state_compat.JobState(3)
_TEST_JOB_STATE_SUCCESS = gca_job_state_compat.JobState(4)

_TEST_GAPIC_BATCH_PREDICTION_JOB = gca_batch_prediction_job_compat.BatchPredictionJob(
    name=_TEST_BATCH_PREDICTION_JOB_NAME,
    display_name=_TEST_DISPLAY_NAME,
    model=_TEST_GEMINI_MODEL_RESOURCE_NAME,
    state=_TEST_JOB_STATE_RUNNING,
)


# TODO(b/339230025) Mock the whole service instead of methods.
@pytest.fixture
def generate_display_name_mock():
    with mock.patch.object(
        aiplatform_base.VertexAiResourceNoun, "_generate_display_name"
    ) as generate_display_name_mock:
        generate_display_name_mock.return_value = _TEST_DISPLAY_NAME
        yield generate_display_name_mock


@pytest.fixture
def complete_bq_uri_mock():
    with mock.patch.object(
        batch_prediction.BatchPredictionJob, "_complete_bq_uri"
    ) as complete_bq_uri_mock:
        complete_bq_uri_mock.return_value = _TEST_BQ_OUTPUT_PREFIX
        yield complete_bq_uri_mock


@pytest.fixture
def get_batch_prediction_job_with_bq_output_mock():
    with mock.patch.object(
        job_service_client.JobServiceClient, "get_batch_prediction_job"
    ) as get_job_mock:
        get_job_mock.return_value = gca_batch_prediction_job_compat.BatchPredictionJob(
            name=_TEST_BATCH_PREDICTION_JOB_NAME,
            display_name=_TEST_DISPLAY_NAME,
            model=_TEST_GEMINI_MODEL_RESOURCE_NAME,
            state=_TEST_JOB_STATE_SUCCESS,
            output_info=gca_batch_prediction_job_compat.BatchPredictionJob.OutputInfo(
                bigquery_output_table=_TEST_BQ_OUTPUT_PREFIX
            ),
        )
        yield get_job_mock


@pytest.fixture
def get_batch_prediction_job_with_gcs_output_mock():
    with mock.patch.object(
        job_service_client.JobServiceClient, "get_batch_prediction_job"
    ) as get_job_mock:
        get_job_mock.return_value = gca_batch_prediction_job_compat.BatchPredictionJob(
            name=_TEST_BATCH_PREDICTION_JOB_NAME,
            display_name=_TEST_DISPLAY_NAME,
            model=_TEST_GEMINI_MODEL_RESOURCE_NAME,
            state=_TEST_JOB_STATE_SUCCESS,
            output_info=gca_batch_prediction_job_compat.BatchPredictionJob.OutputInfo(
                gcs_output_directory=_TEST_GCS_OUTPUT_PREFIX
            ),
        )
        yield get_job_mock


@pytest.fixture
def get_batch_prediction_job_with_tuned_gemini_model_mock():
    with mock.patch.object(
        job_service_client.JobServiceClient, "get_batch_prediction_job"
    ) as get_job_mock:
        get_job_mock.return_value = gca_batch_prediction_job_compat.BatchPredictionJob(
            name=_TEST_BATCH_PREDICTION_JOB_NAME,
            display_name=_TEST_DISPLAY_NAME,
            model=_TEST_TUNED_GEMINI_MODEL_RESOURCE_NAME,
            state=_TEST_JOB_STATE_SUCCESS,
            output_info=gca_batch_prediction_job_compat.BatchPredictionJob.OutputInfo(
                gcs_output_directory=_TEST_GCS_OUTPUT_PREFIX
            ),
        )
        yield get_job_mock


@pytest.fixture
def get_gemini_model_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            name=_TEST_TUNED_GEMINI_MODEL_RESOURCE_NAME,
            model_source_info=gca_model.ModelSourceInfo(
                source_type=gca_model.ModelSourceInfo.ModelSourceType.GENIE
            ),
        )
        yield get_model_mock


@pytest.fixture
def get_non_gemini_model_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            name=_TEST_TUNED_GEMINI_MODEL_RESOURCE_NAME,
        )
        yield get_model_mock


@pytest.fixture
def get_batch_prediction_job_invalid_model_mock():
    with mock.patch.object(
        job_service_client.JobServiceClient, "get_batch_prediction_job"
    ) as get_job_mock:
        get_job_mock.return_value = gca_batch_prediction_job_compat.BatchPredictionJob(
            name=_TEST_BATCH_PREDICTION_JOB_NAME,
            display_name=_TEST_DISPLAY_NAME,
            model=_TEST_PALM_MODEL_RESOURCE_NAME,
            state=_TEST_JOB_STATE_SUCCESS,
        )
        yield get_job_mock


@pytest.fixture
def create_batch_prediction_job_mock():
    with mock.patch.object(
        job_service_client.JobServiceClient, "create_batch_prediction_job"
    ) as create_job_mock:
        create_job_mock.return_value = _TEST_GAPIC_BATCH_PREDICTION_JOB
        yield create_job_mock


@pytest.fixture
def cancel_batch_prediction_job_mock():
    with mock.patch.object(
        job_service_client.JobServiceClient, "cancel_batch_prediction_job"
    ) as cancel_job_mock:
        yield cancel_job_mock


@pytest.fixture
def delete_batch_prediction_job_mock():
    with mock.patch.object(
        job_service_client.JobServiceClient, "delete_batch_prediction_job"
    ) as delete_job_mock:
        yield delete_job_mock


@pytest.fixture
def list_batch_prediction_jobs_mock():
    with mock.patch.object(
        job_service_client.JobServiceClient, "list_batch_prediction_jobs"
    ) as list_jobs_mock:
        list_jobs_mock.return_value = [
            _TEST_GAPIC_BATCH_PREDICTION_JOB,
            gca_batch_prediction_job_compat.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_JOB_NAME,
                display_name=_TEST_DISPLAY_NAME,
                model=_TEST_PALM_MODEL_RESOURCE_NAME,
                state=_TEST_JOB_STATE_SUCCESS,
            ),
        ]
        yield list_jobs_mock


@pytest.mark.usefixtures(
    "google_auth_mock", "generate_display_name_mock", "complete_bq_uri_mock"
)
class TestBatchPredictionJob:
    """Unit tests for BatchPredictionJob."""

    def setup_method(self):
        importlib.reload(aiplatform_initializer)
        importlib.reload(aiplatform)
        importlib.reload(vertexai)
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

    def teardown_method(self):
        aiplatform_initializer.global_pool.shutdown(wait=True)

    def test_init_batch_prediction_job(
        self, get_batch_prediction_job_with_gcs_output_mock
    ):
        batch_prediction.BatchPredictionJob(_TEST_BATCH_PREDICTION_JOB_ID)

        get_batch_prediction_job_with_gcs_output_mock.assert_called_once_with(
            name=_TEST_BATCH_PREDICTION_JOB_NAME, retry=aiplatform_base._DEFAULT_RETRY
        )

    def test_init_batch_prediction_job_with_tuned_gemini_model(
        self,
        get_batch_prediction_job_with_tuned_gemini_model_mock,
        get_gemini_model_mock,
    ):
        batch_prediction.BatchPredictionJob(_TEST_BATCH_PREDICTION_JOB_ID)

        get_batch_prediction_job_with_tuned_gemini_model_mock.assert_called_once_with(
            name=_TEST_BATCH_PREDICTION_JOB_NAME, retry=aiplatform_base._DEFAULT_RETRY
        )
        get_gemini_model_mock.assert_called_once_with(
            name=_TEST_TUNED_GEMINI_MODEL_RESOURCE_NAME,
            retry=aiplatform_base._DEFAULT_RETRY,
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

    @pytest.mark.usefixtures(
        "get_batch_prediction_job_with_tuned_gemini_model_mock",
        "get_non_gemini_model_mock",
    )
    def test_init_batch_prediction_job_with_invalid_tuned_model(
        self,
    ):
        with pytest.raises(
            ValueError,
            match=(
                f"BatchPredictionJob '{_TEST_BATCH_PREDICTION_JOB_ID}' "
                f"runs with the model '{_TEST_TUNED_GEMINI_MODEL_RESOURCE_NAME}', "
                "which is not a GenAI model."
            ),
        ):
            batch_prediction.BatchPredictionJob(_TEST_BATCH_PREDICTION_JOB_ID)

    @pytest.mark.usefixtures("get_batch_prediction_job_with_gcs_output_mock")
    def test_submit_batch_prediction_job_with_gcs_input(
        self, create_batch_prediction_job_mock
    ):
        job = batch_prediction.BatchPredictionJob.submit(
            source_model=_TEST_GEMINI_MODEL_NAME,
            input_dataset=_TEST_GCS_INPUT_URI,
            output_uri_prefix=_TEST_GCS_OUTPUT_PREFIX,
        )

        assert job.gca_resource == _TEST_GAPIC_BATCH_PREDICTION_JOB
        assert job.state == _TEST_JOB_STATE_RUNNING
        assert not job.has_ended
        assert not job.has_succeeded

        job.refresh()
        assert job.state == _TEST_JOB_STATE_SUCCESS
        assert job.has_ended
        assert job.has_succeeded
        assert job.output_location == _TEST_GCS_OUTPUT_PREFIX

        expected_gapic_batch_prediction_job = gca_batch_prediction_job_compat.BatchPredictionJob(
            display_name=_TEST_DISPLAY_NAME,
            model=_TEST_GEMINI_MODEL_RESOURCE_NAME,
            input_config=gca_batch_prediction_job_compat.BatchPredictionJob.InputConfig(
                instances_format="jsonl",
                gcs_source=gca_io_compat.GcsSource(uris=[_TEST_GCS_INPUT_URI]),
            ),
            output_config=gca_batch_prediction_job_compat.BatchPredictionJob.OutputConfig(
                gcs_destination=gca_io_compat.GcsDestination(
                    output_uri_prefix=_TEST_GCS_OUTPUT_PREFIX
                ),
                predictions_format="jsonl",
            ),
        )
        create_batch_prediction_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            batch_prediction_job=expected_gapic_batch_prediction_job,
            timeout=None,
        )

    @pytest.mark.usefixtures("get_batch_prediction_job_with_bq_output_mock")
    def test_submit_batch_prediction_job_with_bq_input(
        self, create_batch_prediction_job_mock
    ):
        job = batch_prediction.BatchPredictionJob.submit(
            source_model=_TEST_GEMINI_MODEL_NAME,
            input_dataset=_TEST_BQ_INPUT_URI,
            output_uri_prefix=_TEST_BQ_OUTPUT_PREFIX,
        )

        assert job.gca_resource == _TEST_GAPIC_BATCH_PREDICTION_JOB
        assert job.state == _TEST_JOB_STATE_RUNNING
        assert not job.has_ended
        assert not job.has_succeeded

        job.refresh()
        assert job.state == _TEST_JOB_STATE_SUCCESS
        assert job.has_ended
        assert job.has_succeeded
        assert job.output_location == _TEST_BQ_OUTPUT_PREFIX

        expected_gapic_batch_prediction_job = gca_batch_prediction_job_compat.BatchPredictionJob(
            display_name=_TEST_DISPLAY_NAME,
            model=_TEST_GEMINI_MODEL_RESOURCE_NAME,
            input_config=gca_batch_prediction_job_compat.BatchPredictionJob.InputConfig(
                instances_format="bigquery",
                bigquery_source=gca_io_compat.BigQuerySource(
                    input_uri=_TEST_BQ_INPUT_URI
                ),
            ),
            output_config=gca_batch_prediction_job_compat.BatchPredictionJob.OutputConfig(
                bigquery_destination=gca_io_compat.BigQueryDestination(
                    output_uri=_TEST_BQ_OUTPUT_PREFIX
                ),
                predictions_format="bigquery",
            ),
        )
        create_batch_prediction_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            batch_prediction_job=expected_gapic_batch_prediction_job,
            timeout=None,
        )

    def test_submit_batch_prediction_job_with_gcs_input_without_output_uri_prefix(
        self, create_batch_prediction_job_mock
    ):
        vertexai.init(staging_bucket=_TEST_BUCKET)
        model = GenerativeModel(_TEST_GEMINI_MODEL_NAME)
        job = batch_prediction.BatchPredictionJob.submit(
            source_model=model,
            input_dataset=[_TEST_GCS_INPUT_URI, _TEST_GCS_INPUT_URI_2],
        )

        assert job.gca_resource == _TEST_GAPIC_BATCH_PREDICTION_JOB

        expected_gapic_batch_prediction_job = gca_batch_prediction_job_compat.BatchPredictionJob(
            display_name=_TEST_DISPLAY_NAME,
            model=_TEST_GEMINI_MODEL_RESOURCE_NAME,
            input_config=gca_batch_prediction_job_compat.BatchPredictionJob.InputConfig(
                instances_format="jsonl",
                gcs_source=gca_io_compat.GcsSource(
                    uris=[_TEST_GCS_INPUT_URI, _TEST_GCS_INPUT_URI_2]
                ),
            ),
            output_config=gca_batch_prediction_job_compat.BatchPredictionJob.OutputConfig(
                gcs_destination=gca_io_compat.GcsDestination(
                    output_uri_prefix=f"{_TEST_BUCKET}/gen-ai-batch-prediction"
                ),
                predictions_format="jsonl",
            ),
        )
        create_batch_prediction_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            batch_prediction_job=expected_gapic_batch_prediction_job,
            timeout=None,
        )

    def test_submit_batch_prediction_job_with_bq_input_without_output_uri_prefix(
        self, create_batch_prediction_job_mock
    ):
        model = GenerativeModel(_TEST_GEMINI_MODEL_NAME)
        job = batch_prediction.BatchPredictionJob.submit(
            source_model=model,
            input_dataset=_TEST_BQ_INPUT_URI,
        )

        assert job.gca_resource == _TEST_GAPIC_BATCH_PREDICTION_JOB

        expected_gapic_batch_prediction_job = gca_batch_prediction_job_compat.BatchPredictionJob(
            display_name=_TEST_DISPLAY_NAME,
            model=_TEST_GEMINI_MODEL_RESOURCE_NAME,
            input_config=gca_batch_prediction_job_compat.BatchPredictionJob.InputConfig(
                instances_format="bigquery",
                bigquery_source=gca_io_compat.BigQuerySource(
                    input_uri=_TEST_BQ_INPUT_URI
                ),
            ),
            output_config=gca_batch_prediction_job_compat.BatchPredictionJob.OutputConfig(
                bigquery_destination=gca_io_compat.BigQueryDestination(
                    output_uri=_TEST_BQ_OUTPUT_PREFIX
                ),
                predictions_format="bigquery",
            ),
        )
        create_batch_prediction_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            batch_prediction_job=expected_gapic_batch_prediction_job,
            timeout=None,
        )

    @pytest.mark.usefixtures("create_batch_prediction_job_mock")
    def test_submit_batch_prediction_job_with_tuned_model(
        self,
        get_gemini_model_mock,
    ):
        job = batch_prediction.BatchPredictionJob.submit(
            source_model=_TEST_TUNED_GEMINI_MODEL_RESOURCE_NAME,
            input_dataset=_TEST_BQ_INPUT_URI,
        )

        assert job.gca_resource == _TEST_GAPIC_BATCH_PREDICTION_JOB
        get_gemini_model_mock.assert_called_once_with(
            name=_TEST_TUNED_GEMINI_MODEL_RESOURCE_NAME,
            retry=aiplatform_base._DEFAULT_RETRY,
        )

    def test_submit_batch_prediction_job_with_invalid_source_model(self):
        with pytest.raises(
            ValueError,
            match=(
                f"Model '{_TEST_PALM_MODEL_RESOURCE_NAME}' is not a Generative AI model."
            ),
        ):
            batch_prediction.BatchPredictionJob.submit(
                source_model=_TEST_PALM_MODEL_NAME,
                input_dataset=_TEST_GCS_INPUT_URI,
            )

    @pytest.mark.usefixtures("get_non_gemini_model_mock")
    def test_submit_batch_prediction_job_with_non_gemini_tuned_model(self):
        with pytest.raises(
            ValueError,
            match=(
                f"Model '{_TEST_TUNED_GEMINI_MODEL_RESOURCE_NAME}' "
                "is not a Generative AI model."
            ),
        ):
            batch_prediction.BatchPredictionJob.submit(
                source_model=_TEST_TUNED_GEMINI_MODEL_RESOURCE_NAME,
                input_dataset=_TEST_GCS_INPUT_URI,
            )

    def test_submit_batch_prediction_job_with_invalid_model_name(self):
        invalid_model_name = "invalid/model/name"
        with pytest.raises(
            ValueError,
            match=(f"Invalid format for model name: {invalid_model_name}."),
        ):
            batch_prediction.BatchPredictionJob.submit(
                source_model=invalid_model_name,
                input_dataset=_TEST_GCS_INPUT_URI,
            )

    def test_submit_batch_prediction_job_with_invalid_input_dataset(self):
        with pytest.raises(
            ValueError,
            match=(
                f"Unsupported input URI: {_TEST_INVALID_URI}. "
                "Supported formats: 'gs://path/to/input/data.jsonl' and "
                "'bq://projectId.bqDatasetId.bqTableId'"
            ),
        ):
            batch_prediction.BatchPredictionJob.submit(
                source_model=_TEST_GEMINI_MODEL_NAME,
                input_dataset=_TEST_INVALID_URI,
            )

        invalid_bq_uris = ["bq://projectId.dataset1", "bq://projectId.dataset2"]
        with pytest.raises(
            ValueError,
            match=("Multiple Bigquery input datasets are not supported."),
        ):
            batch_prediction.BatchPredictionJob.submit(
                source_model=_TEST_GEMINI_MODEL_NAME,
                input_dataset=invalid_bq_uris,
            )

    def test_submit_batch_prediction_job_with_invalid_output_uri_prefix(self):
        with pytest.raises(
            ValueError,
            match=(
                f"Unsupported output URI: {_TEST_INVALID_URI}. "
                "Supported formats: 'gs://path/to/output/data' and "
                "'bq://projectId.bqDatasetId'"
            ),
        ):
            batch_prediction.BatchPredictionJob.submit(
                source_model=_TEST_GEMINI_MODEL_NAME,
                input_dataset=_TEST_GCS_INPUT_URI,
                output_uri_prefix=_TEST_INVALID_URI,
            )

    def test_submit_batch_prediction_job_without_output_uri_prefix_and_bucket(self):
        with pytest.raises(
            ValueError,
            match=(
                "Please either specify output_uri_prefix or "
                "set staging_bucket in vertexai.init()."
            ),
        ):
            batch_prediction.BatchPredictionJob.submit(
                source_model=_TEST_GEMINI_MODEL_NAME,
                input_dataset=_TEST_GCS_INPUT_URI,
            )

    @pytest.mark.usefixtures("create_batch_prediction_job_mock")
    def test_cancel_batch_prediction_job(self, cancel_batch_prediction_job_mock):
        job = batch_prediction.BatchPredictionJob.submit(
            source_model=_TEST_GEMINI_MODEL_NAME,
            input_dataset=_TEST_GCS_INPUT_URI,
            output_uri_prefix=_TEST_GCS_OUTPUT_PREFIX,
        )
        job.cancel()

        cancel_batch_prediction_job_mock.assert_called_once_with(
            name=_TEST_BATCH_PREDICTION_JOB_NAME,
        )

    @pytest.mark.usefixtures("get_batch_prediction_job_with_gcs_output_mock")
    def test_delete_batch_prediction_job(self, delete_batch_prediction_job_mock):
        job = batch_prediction.BatchPredictionJob(_TEST_BATCH_PREDICTION_JOB_ID)
        job.delete()

        delete_batch_prediction_job_mock.assert_called_once_with(
            name=_TEST_BATCH_PREDICTION_JOB_NAME,
        )

    def tes_list_batch_prediction_jobs(self, list_batch_prediction_jobs_mock):
        jobs = batch_prediction.BatchPredictionJob.list()

        assert len(jobs) == 1
        assert jobs[0].gca_resource == _TEST_GAPIC_BATCH_PREDICTION_JOB

        list_batch_prediction_jobs_mock.assert_called_once_with(
            request={"parent": _TEST_PARENT}
        )
