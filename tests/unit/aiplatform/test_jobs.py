# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
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

from unittest import mock
from importlib import reload
from unittest.mock import patch

from google.cloud import storage
from google.cloud import bigquery

from google.cloud import aiplatform
from google.cloud.aiplatform import jobs
from google.cloud.aiplatform import initializer

from google.cloud.aiplatform_v1beta1 import types
from google.cloud.aiplatform_v1beta1.types import job_state
from google.cloud.aiplatform_v1beta1.types import batch_prediction_job
from google.cloud.aiplatform_v1beta1.services import job_service


_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_ID = "1028944691210842416"
_TEST_ALT_ID = "8834795523125638878"
_TEST_DISPLAY_NAME = "my_job_1234"
_TEST_BQ_DATASET_ID = "bqDatasetId"
_TEST_BQ_JOB_ID = "123459876"
_TEST_BQ_MAX_RESULTS = 100
_TEST_GCS_BUCKET_NAME = "my-bucket"

_TEST_BQ_PATH = f"bq://projectId.{_TEST_BQ_DATASET_ID}"
_TEST_GCS_BUCKET_PATH = f"gs://{_TEST_GCS_BUCKET_NAME}"
_TEST_GCS_JSONL_SOURCE_URI = f"{_TEST_GCS_BUCKET_PATH}/bp_input_config.jsonl"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"

_TEST_MODEL_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/models/{_TEST_ALT_ID}"
)
_TEST_BATCH_PREDICTION_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/batchPredictionJobs/{_TEST_ID}"

_TEST_JOB_STATE_SUCCESS = job_state.JobState(4)
_TEST_JOB_STATE_RUNNING = job_state.JobState(3)
_TEST_JOB_STATE_PENDING = job_state.JobState(2)

_TEST_GCS_INPUT_CONFIG = batch_prediction_job.BatchPredictionJob.InputConfig(
    instances_format="jsonl",
    gcs_source=types.GcsSource(uris=[_TEST_GCS_JSONL_SOURCE_URI]),
)
_TEST_GCS_OUTPUT_CONFIG = batch_prediction_job.BatchPredictionJob.OutputConfig(
    predictions_format="jsonl",
    gcs_destination=types.GcsDestination(output_uri_prefix=_TEST_GCS_BUCKET_PATH),
)

_TEST_BQ_INPUT_CONFIG = batch_prediction_job.BatchPredictionJob.InputConfig(
    instances_format="bigquery",
    bigquery_source=types.BigQuerySource(input_uri=_TEST_BQ_PATH),
)
_TEST_BQ_OUTPUT_CONFIG = batch_prediction_job.BatchPredictionJob.OutputConfig(
    predictions_format="bigquery",
    bigquery_destination=types.BigQueryDestination(output_uri=_TEST_BQ_PATH),
)

_TEST_GCS_OUTPUT_INFO = batch_prediction_job.BatchPredictionJob.OutputInfo(
    gcs_output_directory=_TEST_GCS_BUCKET_PATH
)
_TEST_BQ_OUTPUT_INFO = batch_prediction_job.BatchPredictionJob.OutputInfo(
    bigquery_output_dataset=_TEST_BQ_PATH
)

_TEST_EMPTY_OUTPUT_INFO = batch_prediction_job.BatchPredictionJob.OutputInfo()

_TEST_ITER_DIRS_BQ_QUERY = f"SELECT * FROM {_TEST_BQ_DATASET_ID}.predictions LIMIT 100"

_TEST_GCS_BLOBS = [
    storage.Blob(name="some/path/prediction.jsonl", bucket=_TEST_GCS_BUCKET_NAME)
]


# TODO(b/171333554): Move reusable test fixtures to conftest.py file
class TestJob:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    # Test Fixtures

    @pytest.fixture
    def get_batch_prediction_job_gcs_output_mock(self):
        with patch.object(
            job_service.JobServiceClient, "get_batch_prediction_job"
        ) as get_batch_prediction_job_mock:
            get_batch_prediction_job_mock.return_value = batch_prediction_job.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_NAME,
                display_name=_TEST_DISPLAY_NAME,
                model=_TEST_MODEL_NAME,
                input_config=_TEST_GCS_INPUT_CONFIG,
                output_config=_TEST_GCS_OUTPUT_CONFIG,
                output_info=_TEST_GCS_OUTPUT_INFO,
                state=_TEST_JOB_STATE_SUCCESS,
            )
            yield get_batch_prediction_job_mock

    @pytest.fixture
    def get_batch_prediction_job_bq_output_mock(self):
        with patch.object(
            job_service.JobServiceClient, "get_batch_prediction_job"
        ) as get_batch_prediction_job_mock:
            get_batch_prediction_job_mock.return_value = batch_prediction_job.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_NAME,
                display_name=_TEST_DISPLAY_NAME,
                model=_TEST_MODEL_NAME,
                input_config=_TEST_GCS_INPUT_CONFIG,
                output_config=_TEST_BQ_OUTPUT_CONFIG,
                output_info=_TEST_BQ_OUTPUT_INFO,
                state=_TEST_JOB_STATE_SUCCESS,
            )
            yield get_batch_prediction_job_mock

    @pytest.fixture
    def get_batch_prediction_job_empty_output_mock(self):
        with patch.object(
            job_service.JobServiceClient, "get_batch_prediction_job"
        ) as get_batch_prediction_job_mock:
            get_batch_prediction_job_mock.return_value = batch_prediction_job.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_NAME,
                display_name=_TEST_DISPLAY_NAME,
                model=_TEST_MODEL_NAME,
                input_config=_TEST_GCS_INPUT_CONFIG,
                output_config=_TEST_BQ_OUTPUT_CONFIG,
                output_info=_TEST_EMPTY_OUTPUT_INFO,
                state=_TEST_JOB_STATE_SUCCESS,
            )
            yield get_batch_prediction_job_mock

    @pytest.fixture
    def get_batch_prediction_job_running_bq_output_mock(self):
        with patch.object(
            job_service.JobServiceClient, "get_batch_prediction_job"
        ) as get_batch_prediction_job_mock:
            get_batch_prediction_job_mock.return_value = batch_prediction_job.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_NAME,
                display_name=_TEST_DISPLAY_NAME,
                model=_TEST_MODEL_NAME,
                input_config=_TEST_GCS_INPUT_CONFIG,
                output_config=_TEST_BQ_OUTPUT_CONFIG,
                output_info=_TEST_BQ_OUTPUT_INFO,
                state=_TEST_JOB_STATE_RUNNING,
            )
            yield get_batch_prediction_job_mock

    @pytest.fixture
    def storage_list_blobs_mock(self):
        with patch.object(storage.Client, "list_blobs") as list_blobs_mock:
            list_blobs_mock.return_value = _TEST_GCS_BLOBS
            yield list_blobs_mock

    @pytest.fixture
    def bq_list_rows_mock(self):
        with patch.object(bigquery.Client, "list_rows") as list_rows_mock:

            list_rows_mock.return_value = mock.Mock(bigquery.table.RowIterator)
            yield list_rows_mock

    # Unit Tests

    def test_init_job_class(self):
        """
        Raises TypeError since abstract property '_getter_method' is not set,
        the _Job class should only be instantiated through a child class.
        """
        with pytest.raises(TypeError):
            jobs._Job(valid_job_name=_TEST_BATCH_PREDICTION_NAME)

    def test_init_batch_prediction_job_class(
        self, get_batch_prediction_job_bq_output_mock
    ):
        aiplatform.BatchPredictionJob(
            batch_prediction_job_name=_TEST_BATCH_PREDICTION_NAME
        )
        get_batch_prediction_job_bq_output_mock.assert_called_once_with(
            name=_TEST_BATCH_PREDICTION_NAME
        )

    def test_batch_prediction_job_status(self, get_batch_prediction_job_bq_output_mock):
        bp = aiplatform.BatchPredictionJob(
            batch_prediction_job_name=_TEST_BATCH_PREDICTION_NAME
        )

        # get_batch_prediction() is called again here
        bp_job_state = bp.status()

        assert get_batch_prediction_job_bq_output_mock.call_count == 2
        assert bp_job_state == _TEST_JOB_STATE_SUCCESS

        get_batch_prediction_job_bq_output_mock.assert_called_with(
            name=_TEST_BATCH_PREDICTION_NAME
        )

    def test_batch_prediction_iter_dirs_gcs(
        self, get_batch_prediction_job_gcs_output_mock, storage_list_blobs_mock
    ):
        bp = aiplatform.BatchPredictionJob(
            batch_prediction_job_name=_TEST_BATCH_PREDICTION_NAME
        )
        blobs = bp.iter_outputs()

        storage_list_blobs_mock.assert_called_once_with(
            _TEST_GCS_OUTPUT_INFO.gcs_output_directory
        )

        assert blobs == _TEST_GCS_BLOBS

    def test_batch_prediction_iter_dirs_bq(
        self, get_batch_prediction_job_bq_output_mock, bq_list_rows_mock
    ):
        bp = aiplatform.BatchPredictionJob(
            batch_prediction_job_name=_TEST_BATCH_PREDICTION_NAME
        )

        bp.iter_outputs()

        bq_list_rows_mock.assert_called_once_with(
            table=f"{_TEST_BQ_DATASET_ID}.predictions", max_results=_TEST_BQ_MAX_RESULTS
        )

    def test_batch_prediction_iter_dirs_while_running(
        self, get_batch_prediction_job_running_bq_output_mock
    ):
        """
        Raises RuntimeError since outputs cannot be read while BatchPredictionJob is still running
        """
        with pytest.raises(RuntimeError):
            bp = aiplatform.BatchPredictionJob(
                batch_prediction_job_name=_TEST_BATCH_PREDICTION_NAME
            )
            bp.iter_outputs()

    def test_batch_prediction_iter_dirs_invalid_output_info(
        self, get_batch_prediction_job_empty_output_mock
    ):
        """
        Raises NotImplementedError since the BatchPredictionJob's output_info
        contains no output GCS directory or BQ dataset.
        """
        with pytest.raises(NotImplementedError):
            bp = aiplatform.BatchPredictionJob(
                batch_prediction_job_name=_TEST_BATCH_PREDICTION_NAME
            )
            bp.iter_outputs()
