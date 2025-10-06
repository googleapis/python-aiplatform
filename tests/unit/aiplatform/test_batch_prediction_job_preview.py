# -*- coding: utf-8 -*-

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

from importlib import reload
from unittest import mock
from unittest.mock import patch

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.compat.services import (
    job_service_client,
)
from google.cloud.aiplatform.compat.types import (
    batch_prediction_job as gca_batch_prediction_job_compat,
    io as gca_io_compat,
    job_state as gca_job_state_compat,
    machine_resources as gca_machine_resources_compat,
    manual_batch_tuning_parameters as gca_manual_batch_tuning_parameters_compat,
    reservation_affinity_v1 as gca_reservation_affinity_compat,
)
from google.cloud.aiplatform.preview import jobs as preview_jobs
import constants as test_constants
import pytest

# TODO(b/242108750): remove temporary logic once model monitoring for batch prediction is GA
_TEST_API_CLIENT = job_service_client.JobServiceClient

_TEST_PROJECT = test_constants.ProjectConstants._TEST_PROJECT
_TEST_LOCATION = test_constants.ProjectConstants._TEST_LOCATION
_TEST_ID = test_constants.TrainingJobConstants._TEST_ID
_TEST_ALT_ID = "8834795523125638878"
_TEST_DISPLAY_NAME = test_constants.TrainingJobConstants._TEST_DISPLAY_NAME
_TEST_SERVICE_ACCOUNT = test_constants.ProjectConstants._TEST_SERVICE_ACCOUNT

_TEST_JOB_STATE_SUCCESS = gca_job_state_compat.JobState(4)
_TEST_JOB_STATE_RUNNING = gca_job_state_compat.JobState(3)
_TEST_JOB_STATE_PENDING = gca_job_state_compat.JobState(2)

_TEST_PARENT = test_constants.ProjectConstants._TEST_PARENT

_TEST_MODEL_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/models/{_TEST_ALT_ID}"
)

_TEST_BATCH_PREDICTION_JOB_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/batchPredictionJobs/{_TEST_ID}"
_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME = "test-batch-prediction-job"

_TEST_BATCH_PREDICTION_GCS_SOURCE = "gs://example-bucket/folder/instance.jsonl"

_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX = "gs://example-bucket/folder/output"

_TEST_MACHINE_TYPE = "n1-standard-4"
_TEST_ACCELERATOR_TYPE = "NVIDIA_TESLA_P100"
_TEST_ACCELERATOR_COUNT = 2
_TEST_RESERVATION_AFFINITY_TYPE = "SPECIFIC_RESERVATION"
_TEST_RESERVATION_AFFINITY_KEY = "compute.googleapis.com/reservation-name"
_TEST_RESERVATION_AFFINITY_VALUES = [
    "projects/fake-project-id/zones/fake-zone/reservations/fake-reservation-name"
]


@pytest.fixture
def get_batch_prediction_job_mock():
    with patch.object(
        _TEST_API_CLIENT, "get_batch_prediction_job"
    ) as get_batch_prediction_job_mock:
        get_batch_prediction_job_mock.side_effect = [
            gca_batch_prediction_job_compat.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_JOB_NAME,
                display_name=_TEST_DISPLAY_NAME,
                state=_TEST_JOB_STATE_PENDING,
            ),
            gca_batch_prediction_job_compat.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_JOB_NAME,
                display_name=_TEST_DISPLAY_NAME,
                state=_TEST_JOB_STATE_RUNNING,
            ),
            gca_batch_prediction_job_compat.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_JOB_NAME,
                display_name=_TEST_DISPLAY_NAME,
                state=_TEST_JOB_STATE_SUCCESS,
            ),
            gca_batch_prediction_job_compat.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_JOB_NAME,
                display_name=_TEST_DISPLAY_NAME,
                state=_TEST_JOB_STATE_SUCCESS,
            ),
        ]
        yield get_batch_prediction_job_mock


@pytest.fixture
def create_batch_prediction_job_mock():
    with mock.patch.object(
        _TEST_API_CLIENT, "create_batch_prediction_job"
    ) as create_batch_prediction_job_mock:
        create_batch_prediction_job_mock.return_value = (
            gca_batch_prediction_job_compat.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_JOB_NAME,
                display_name=_TEST_DISPLAY_NAME,
                state=_TEST_JOB_STATE_SUCCESS,
            )
        )
        yield create_batch_prediction_job_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestBatchPredictionJobPreview:

    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_batch_prediction_job(self, get_batch_prediction_job_mock):
        preview_jobs.BatchPredictionJob(
            batch_prediction_job_name=_TEST_BATCH_PREDICTION_JOB_NAME
        )
        get_batch_prediction_job_mock.assert_called_once_with(
            name=_TEST_BATCH_PREDICTION_JOB_NAME, retry=base._DEFAULT_RETRY
        )

    def test_batch_prediction_job_status(self, get_batch_prediction_job_mock):
        bp = preview_jobs.BatchPredictionJob(
            batch_prediction_job_name=_TEST_BATCH_PREDICTION_JOB_NAME
        )

        # get_batch_prediction() is called again here
        bp_job_state = bp.state

        assert get_batch_prediction_job_mock.call_count == 2
        assert bp_job_state == _TEST_JOB_STATE_RUNNING

        get_batch_prediction_job_mock.assert_called_with(
            name=_TEST_BATCH_PREDICTION_JOB_NAME, retry=base._DEFAULT_RETRY
        )

    def test_batch_prediction_job_done_get(self, get_batch_prediction_job_mock):
        bp = preview_jobs.BatchPredictionJob(
            batch_prediction_job_name=_TEST_BATCH_PREDICTION_JOB_NAME
        )

        assert bp.done() is False
        assert get_batch_prediction_job_mock.call_count == 2

    @mock.patch.object(preview_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(preview_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_batch_prediction_job_mock")
    def test_batch_predict_create_with_reservation(
        self, create_batch_prediction_job_mock, sync
    ):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        # Make SDK batch_predict method call
        batch_prediction_job = preview_jobs.BatchPredictionJob.create(
            model_name=_TEST_MODEL_NAME,
            job_display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            gcs_destination_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX,
            sync=sync,
            create_request_timeout=None,
            service_account=_TEST_SERVICE_ACCOUNT,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            reservation_affinity_type=_TEST_RESERVATION_AFFINITY_TYPE,
            reservation_affinity_key=_TEST_RESERVATION_AFFINITY_KEY,
            reservation_affinity_values=_TEST_RESERVATION_AFFINITY_VALUES,
        )

        batch_prediction_job.wait_for_resource_creation()

        batch_prediction_job.wait()

        # Construct expected request
        expected_gapic_batch_prediction_job = gca_batch_prediction_job_compat.BatchPredictionJob(
            display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
            model=_TEST_MODEL_NAME,
            input_config=gca_batch_prediction_job_compat.BatchPredictionJob.InputConfig(
                instances_format="jsonl",
                gcs_source=gca_io_compat.GcsSource(
                    uris=[_TEST_BATCH_PREDICTION_GCS_SOURCE]
                ),
            ),
            output_config=gca_batch_prediction_job_compat.BatchPredictionJob.OutputConfig(
                gcs_destination=gca_io_compat.GcsDestination(
                    output_uri_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX
                ),
                predictions_format="jsonl",
            ),
            service_account=_TEST_SERVICE_ACCOUNT,
            dedicated_resources=gca_machine_resources_compat.BatchDedicatedResources(
                machine_spec=gca_machine_resources_compat.MachineSpec(
                    machine_type=_TEST_MACHINE_TYPE,
                    accelerator_type=_TEST_ACCELERATOR_TYPE,
                    accelerator_count=_TEST_ACCELERATOR_COUNT,
                    reservation_affinity=gca_reservation_affinity_compat.ReservationAffinity(
                        reservation_affinity_type=_TEST_RESERVATION_AFFINITY_TYPE,
                        key=_TEST_RESERVATION_AFFINITY_KEY,
                        values=_TEST_RESERVATION_AFFINITY_VALUES,
                    ),
                ),
            ),
            manual_batch_tuning_parameters=gca_manual_batch_tuning_parameters_compat.ManualBatchTuningParameters(),
        )

        create_batch_prediction_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            batch_prediction_job=expected_gapic_batch_prediction_job,
            timeout=None,
        )

    @mock.patch.object(preview_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(preview_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures("get_batch_prediction_job_mock")
    def test_batch_predict_job_submit(self, create_batch_prediction_job_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        # Make SDK batch_predict method call
        batch_prediction_job = preview_jobs.BatchPredictionJob.submit(
            model_name=_TEST_MODEL_NAME,
            job_display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            gcs_destination_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX,
            service_account=_TEST_SERVICE_ACCOUNT,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            reservation_affinity_type=_TEST_RESERVATION_AFFINITY_TYPE,
            reservation_affinity_key=_TEST_RESERVATION_AFFINITY_KEY,
            reservation_affinity_values=_TEST_RESERVATION_AFFINITY_VALUES,
        )

        batch_prediction_job.wait_for_resource_creation()
        assert batch_prediction_job.done() is False
        assert (
            batch_prediction_job.state
            != preview_jobs.gca_job_state.JobState.JOB_STATE_SUCCEEDED
        )

        batch_prediction_job.wait_for_completion()
        assert (
            batch_prediction_job.state
            == preview_jobs.gca_job_state.JobState.JOB_STATE_SUCCEEDED
        )

        # Construct expected request
        expected_gapic_batch_prediction_job = gca_batch_prediction_job_compat.BatchPredictionJob(
            display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
            model=_TEST_MODEL_NAME,
            input_config=gca_batch_prediction_job_compat.BatchPredictionJob.InputConfig(
                instances_format="jsonl",
                gcs_source=gca_io_compat.GcsSource(
                    uris=[_TEST_BATCH_PREDICTION_GCS_SOURCE]
                ),
            ),
            output_config=gca_batch_prediction_job_compat.BatchPredictionJob.OutputConfig(
                gcs_destination=gca_io_compat.GcsDestination(
                    output_uri_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX
                ),
                predictions_format="jsonl",
            ),
            service_account=_TEST_SERVICE_ACCOUNT,
            dedicated_resources=gca_machine_resources_compat.BatchDedicatedResources(
                machine_spec=gca_machine_resources_compat.MachineSpec(
                    machine_type=_TEST_MACHINE_TYPE,
                    accelerator_type=_TEST_ACCELERATOR_TYPE,
                    accelerator_count=_TEST_ACCELERATOR_COUNT,
                    reservation_affinity=gca_reservation_affinity_compat.ReservationAffinity(
                        reservation_affinity_type=_TEST_RESERVATION_AFFINITY_TYPE,
                        key=_TEST_RESERVATION_AFFINITY_KEY,
                        values=_TEST_RESERVATION_AFFINITY_VALUES,
                    ),
                ),
            ),
            manual_batch_tuning_parameters=gca_manual_batch_tuning_parameters_compat.ManualBatchTuningParameters(),
        )

        create_batch_prediction_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            batch_prediction_job=expected_gapic_batch_prediction_job,
            timeout=None,
        )
