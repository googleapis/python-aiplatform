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

import pytest
import copy

from unittest import mock
from importlib import reload
from unittest.mock import patch

from google.cloud import storage
from google.cloud import bigquery

from google.api_core import operation
from google.auth import credentials as auth_credentials

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import jobs
from google.cloud.aiplatform import model_monitoring

from google.cloud.aiplatform.compat.types import (
    batch_prediction_job as gca_batch_prediction_job_compat,
    explanation as gca_explanation_compat,
    io as gca_io_compat,
    job_state as gca_job_state_compat,
    machine_resources as gca_machine_resources_compat,
    manual_batch_tuning_parameters as gca_manual_batch_tuning_parameters_compat,
    model_deployment_monitoring_job as gca_model_deployment_monitoring_job_compat,
    model_monitoring as gca_model_monitoring_compat,
    batch_prediction_job_v1beta1 as gca_batch_prediction_job_v1beta1,
    job_state_v1beta1 as gca_job_state_v1beta1,
    model_monitoring_v1beta1 as gca_model_monitoring_v1beta1,
    explanation_metadata_v1beta1 as gca_explanation_metadata_v1beta1,
)

from google.cloud.aiplatform.compat.services import (
    job_service_client,
    job_service_client_v1beta1,
)
from google.protobuf import field_mask_pb2  # type: ignore
from google.protobuf import duration_pb2  # type: ignore

import constants as test_constants

# TODO(b/242108750): remove temporary logic once model monitoring for batch prediction is GA
_TEST_API_CLIENT = job_service_client.JobServiceClient
_TEST_API_CLIENT_BETA = job_service_client_v1beta1.JobServiceClient

_TEST_PROJECT = test_constants.ProjectConstants._TEST_PROJECT
_TEST_LOCATION = test_constants.ProjectConstants._TEST_LOCATION
_TEST_ID = test_constants.TrainingJobConstants._TEST_ID
_TEST_ALT_ID = "8834795523125638878"
_TEST_DISPLAY_NAME = test_constants.TrainingJobConstants._TEST_DISPLAY_NAME
_TEST_BQ_PROJECT_ID = "projectId"
_TEST_BQ_DATASET_ID = "bqDatasetId"
_TEST_BQ_TABLE_NAME = "someBqTable"
_TEST_BQ_JOB_ID = "123459876"
_TEST_BQ_MAX_RESULTS = 100
_TEST_GCS_BUCKET_NAME = "my-bucket"
_TEST_SERVICE_ACCOUNT = test_constants.ProjectConstants._TEST_SERVICE_ACCOUNT


_TEST_BQ_PATH = f"bq://{_TEST_BQ_PROJECT_ID}.{_TEST_BQ_DATASET_ID}"
_TEST_GCS_BUCKET_PATH = f"gs://{_TEST_GCS_BUCKET_NAME}"
_TEST_GCS_JSONL_SOURCE_URI = f"{_TEST_GCS_BUCKET_PATH}/bp_input_config.jsonl"
_TEST_PARENT = test_constants.ProjectConstants._TEST_PARENT

_TEST_MODEL_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/models/{_TEST_ALT_ID}"
)

_TEST_MODEL_VERSION_ID = "2"
_TEST_VERSIONED_MODEL_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/models/{_TEST_ALT_ID}@{_TEST_MODEL_VERSION_ID}"

_TEST_PUBLISHER_MODEL_NAME = (
    f"publishers/google/models/text-model-name@{_TEST_MODEL_VERSION_ID}"
)

_TEST_BATCH_PREDICTION_JOB_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/batchPredictionJobs/{_TEST_ID}"
_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME = "test-batch-prediction-job"

_TEST_BATCH_PREDICTION_GCS_SOURCE = "gs://example-bucket/folder/instance.jsonl"
_TEST_BATCH_PREDICTION_GCS_SOURCE_LIST = [
    "gs://example-bucket/folder/instance1.jsonl",
    "gs://example-bucket/folder/instance2.jsonl",
]
_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX = "gs://example-bucket/folder/output"
_TEST_BATCH_PREDICTION_BQ_PREFIX = "ucaip-sample-tests"
_TEST_BATCH_PREDICTION_BQ_DEST_PREFIX_WITH_PROTOCOL = (
    f"bq://{_TEST_BATCH_PREDICTION_BQ_PREFIX}"
)

_TEST_MDM_JOB_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/modelDeploymentMonitoringJobs/{_TEST_ID}"
_TEST_ENDPOINT = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/endpoints/{_TEST_ID}"
)

_TEST_JOB_STATE_SUCCESS = gca_job_state_compat.JobState(4)
_TEST_JOB_STATE_RUNNING = gca_job_state_compat.JobState(3)
_TEST_JOB_STATE_PENDING = gca_job_state_compat.JobState(2)

_TEST_JOB_STATE_SUCCESS_V1BETA1 = gca_job_state_v1beta1.JobState(4)
_TEST_JOB_STATE_RUNNING_V1BETA1 = gca_job_state_v1beta1.JobState(3)
_TEST_JOB_STATE_PENDING_V1BETA1 = gca_job_state_v1beta1.JobState(2)

_TEST_GCS_INPUT_CONFIG = gca_batch_prediction_job_compat.BatchPredictionJob.InputConfig(
    instances_format="jsonl",
    gcs_source=gca_io_compat.GcsSource(uris=[_TEST_GCS_JSONL_SOURCE_URI]),
)
_TEST_GCS_OUTPUT_CONFIG = (
    gca_batch_prediction_job_compat.BatchPredictionJob.OutputConfig(
        predictions_format="jsonl",
        gcs_destination=gca_io_compat.GcsDestination(
            output_uri_prefix=_TEST_GCS_BUCKET_PATH
        ),
    )
)

_TEST_BQ_INPUT_CONFIG = gca_batch_prediction_job_compat.BatchPredictionJob.InputConfig(
    instances_format="bigquery",
    bigquery_source=gca_io_compat.BigQuerySource(input_uri=_TEST_BQ_PATH),
)
_TEST_BQ_OUTPUT_CONFIG = (
    gca_batch_prediction_job_compat.BatchPredictionJob.OutputConfig(
        predictions_format="bigquery",
        bigquery_destination=gca_io_compat.BigQueryDestination(
            output_uri=_TEST_BQ_PATH
        ),
    )
)

_TEST_GCS_OUTPUT_INFO = gca_batch_prediction_job_compat.BatchPredictionJob.OutputInfo(
    gcs_output_directory=_TEST_GCS_BUCKET_NAME
)
_TEST_BQ_OUTPUT_INFO = gca_batch_prediction_job_compat.BatchPredictionJob.OutputInfo(
    bigquery_output_dataset=_TEST_BQ_PATH, bigquery_output_table=_TEST_BQ_TABLE_NAME
)
_TEST_BQ_OUTPUT_INFO_INCOMPLETE = (
    gca_batch_prediction_job_compat.BatchPredictionJob.OutputInfo(
        bigquery_output_dataset=_TEST_BQ_PATH
    )
)

_TEST_EMPTY_OUTPUT_INFO = (
    gca_batch_prediction_job_compat.BatchPredictionJob.OutputInfo()
)

_TEST_GCS_BLOBS = [
    storage.Blob(name="some/path/prediction.jsonl", bucket=_TEST_GCS_BUCKET_NAME)
]

_TEST_MACHINE_TYPE = "n1-standard-4"
_TEST_ACCELERATOR_TYPE = "NVIDIA_TESLA_P100"
_TEST_ACCELERATOR_COUNT = 2
_TEST_STARTING_REPLICA_COUNT = 2
_TEST_MAX_REPLICA_COUNT = 12
_TEST_BATCH_SIZE = 16

_TEST_LABEL = {"team": "experimentation", "trial_id": "x435"}

_TEST_EXPLANATION_METADATA = aiplatform.explain.ExplanationMetadata(
    inputs={
        "features": {
            "input_tensor_name": "dense_input",
            "encoding": "BAG_OF_FEATURES",
            "modality": "numeric",
            "index_feature_mapping": ["abc", "def", "ghj"],
        }
    },
    outputs={"medv": {"output_tensor_name": "dense_2"}},
)
_TEST_EXPLANATION_PARAMETERS = aiplatform.explain.ExplanationParameters(
    {"sampled_shapley_attribution": {"path_count": 10}}
)

_TEST_EXPLANATION_METADATA_V1BETA1 = gca_explanation_metadata_v1beta1.ExplanationMetadata(
    inputs={
        "features": gca_explanation_metadata_v1beta1.ExplanationMetadata.InputMetadata(
            input_tensor_name="dense_input",
            encoding=gca_explanation_metadata_v1beta1.ExplanationMetadata.InputMetadata.Encoding.BAG_OF_FEATURES,
            modality="numeric",
            index_feature_mapping=["abc", "def", "ghj"],
        )
    },
    outputs={
        "medv": gca_explanation_metadata_v1beta1.ExplanationMetadata.OutputMetadata(
            output_tensor_name="dense_2"
        )
    },
)

_TEST_JOB_GET_METHOD_NAME = "get_custom_job"
_TEST_JOB_LIST_METHOD_NAME = "list_custom_job"
_TEST_JOB_CANCEL_METHOD_NAME = "cancel_custom_job"
_TEST_JOB_DELETE_METHOD_NAME = "delete_custom_job"
_TEST_JOB_RESOURCE_NAME = f"{_TEST_PARENT}/customJobs/{_TEST_ID}"

_TEST_MDM_JOB_DRIFT_DETECTION_CONFIG = {"TEST_KEY": 0.01}
_TEST_MDM_USER_EMAIL = "TEST_EMAIL"
_TEST_MDM_SAMPLE_RATE = 0.5
_TEST_MDM_LABEL = {"TEST KEY": "TEST VAL"}
_TEST_LOG_TTL_IN_DAYS = 1
_TEST_MDM_NEW_NAME = "NEW_NAME"

_TEST_MDM_OLD_JOB = (
    gca_model_deployment_monitoring_job_compat.ModelDeploymentMonitoringJob(
        name=_TEST_MDM_JOB_NAME,
        display_name=_TEST_DISPLAY_NAME,
        endpoint=_TEST_ENDPOINT,
        state=_TEST_JOB_STATE_RUNNING,
    )
)

_TEST_MDM_EXPECTED_NEW_JOB = gca_model_deployment_monitoring_job_compat.ModelDeploymentMonitoringJob(
    name=_TEST_MDM_JOB_NAME,
    display_name=_TEST_MDM_NEW_NAME,
    endpoint=_TEST_ENDPOINT,
    state=_TEST_JOB_STATE_RUNNING,
    model_deployment_monitoring_objective_configs=[
        gca_model_deployment_monitoring_job_compat.ModelDeploymentMonitoringObjectiveConfig(
            deployed_model_id=model_id,
            objective_config=gca_model_monitoring_compat.ModelMonitoringObjectiveConfig(
                prediction_drift_detection_config=gca_model_monitoring_compat.ModelMonitoringObjectiveConfig.PredictionDriftDetectionConfig(
                    drift_thresholds={
                        "TEST_KEY": gca_model_monitoring_compat.ThresholdConfig(
                            value=0.01
                        )
                    }
                )
            ),
        )
        for model_id in [
            model.id for model in test_constants.EndpointConstants._TEST_DEPLOYED_MODELS
        ]
    ],
    logging_sampling_strategy=gca_model_monitoring_compat.SamplingStrategy(
        random_sample_config=gca_model_monitoring_compat.SamplingStrategy.RandomSampleConfig(
            sample_rate=_TEST_MDM_SAMPLE_RATE
        )
    ),
    labels=_TEST_MDM_LABEL,
    model_monitoring_alert_config=gca_model_monitoring_compat.ModelMonitoringAlertConfig(
        email_alert_config=gca_model_monitoring_compat.ModelMonitoringAlertConfig.EmailAlertConfig(
            user_emails=[_TEST_MDM_USER_EMAIL]
        )
    ),
    model_deployment_monitoring_schedule_config=gca_model_deployment_monitoring_job_compat.ModelDeploymentMonitoringScheduleConfig(
        monitor_interval=duration_pb2.Duration(seconds=3600)
    ),
    log_ttl=duration_pb2.Duration(seconds=_TEST_LOG_TTL_IN_DAYS * 86400),
    enable_monitoring_pipeline_logs=True,
)

_TEST_THRESHOLD_KEY = "TEST_KEY"
_TEST_THRESHOLD_VAL = 0.1
_TEST_MODEL_MONITORING_SKEW_CFG = gca_model_monitoring_v1beta1.ModelMonitoringObjectiveConfig.TrainingPredictionSkewDetectionConfig(
    skew_thresholds={
        _TEST_THRESHOLD_KEY: gca_model_monitoring_v1beta1.ThresholdConfig(
            value=_TEST_THRESHOLD_VAL
        )
    },
    attribution_score_skew_thresholds={
        _TEST_THRESHOLD_KEY: gca_model_monitoring_v1beta1.ThresholdConfig(
            value=_TEST_THRESHOLD_VAL
        )
    },
)

_TEST_MODEL_MONITORING_DRIFT_CFG = gca_model_monitoring_v1beta1.ModelMonitoringObjectiveConfig.PredictionDriftDetectionConfig(
    drift_thresholds={
        _TEST_THRESHOLD_KEY: gca_model_monitoring_v1beta1.ThresholdConfig(
            value=_TEST_THRESHOLD_VAL
        )
    },
    attribution_score_drift_thresholds={
        _TEST_THRESHOLD_KEY: gca_model_monitoring_v1beta1.ThresholdConfig(
            value=_TEST_THRESHOLD_VAL
        )
    },
)

_TEST_MODEL_MONITORING_TRAINING_DATASET = (
    gca_model_monitoring_v1beta1.ModelMonitoringObjectiveConfig.TrainingDataset(
        dataset="", target_field=""
    )
)
_TEST_MODEL_MONITORING_ALERT_CFG = gca_model_monitoring_v1beta1.ModelMonitoringAlertConfig(
    email_alert_config=gca_model_monitoring_v1beta1.ModelMonitoringAlertConfig.EmailAlertConfig(
        user_emails=[""]
    ),
    enable_logging=False,
)

_TEST_MODEL_MONITORING_CFG = gca_model_monitoring_v1beta1.ModelMonitoringConfig(
    objective_configs=[
        gca_model_monitoring_v1beta1.ModelMonitoringObjectiveConfig(
            training_dataset=_TEST_MODEL_MONITORING_TRAINING_DATASET,
            training_prediction_skew_detection_config=_TEST_MODEL_MONITORING_SKEW_CFG,
            prediction_drift_detection_config=_TEST_MODEL_MONITORING_DRIFT_CFG,
            explanation_config=gca_model_monitoring_v1beta1.ModelMonitoringObjectiveConfig.ExplanationConfig(
                enable_feature_attributes=True
            ),
        )
    ],
    alert_config=_TEST_MODEL_MONITORING_ALERT_CFG,
    analysis_instance_schema_uri="",
)

# TODO(b/171333554): Move reusable test fixtures to conftest.py file


@pytest.fixture
def fake_job_getter_mock():
    with patch.object(
        _TEST_API_CLIENT, _TEST_JOB_GET_METHOD_NAME, create=True
    ) as fake_job_getter_mock:
        fake_job_getter_mock.return_value = {}
        yield fake_job_getter_mock


@pytest.fixture
def fake_job_cancel_mock():
    with patch.object(
        _TEST_API_CLIENT, _TEST_JOB_CANCEL_METHOD_NAME, create=True
    ) as fake_job_cancel_mock:
        yield fake_job_cancel_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestJob:
    class FakeJob(jobs._Job):
        _job_type = "custom-job"
        _resource_noun = "customJobs"
        _getter_method = _TEST_JOB_GET_METHOD_NAME
        _list_method = _TEST_JOB_LIST_METHOD_NAME
        _cancel_method = _TEST_JOB_CANCEL_METHOD_NAME
        _delete_method = _TEST_JOB_DELETE_METHOD_NAME
        _parse_resource_name_method = "parse_custom_job_path"
        _format_resource_name_method = "custom_job_path"
        resource_name = _TEST_JOB_RESOURCE_NAME

    def setup_method(self):
        reload(initializer)
        reload(aiplatform)
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    # Unit Tests
    def test_init_job_class(self):
        """
        Raises TypeError since abstract property '_getter_method' is not set,
        the _Job class should only be instantiated through a child class.
        """
        with pytest.raises(TypeError):
            jobs._Job(job_name=_TEST_BATCH_PREDICTION_JOB_NAME)

    @pytest.mark.usefixtures("fake_job_getter_mock")
    def test_cancel_mock_job(self, fake_job_cancel_mock):
        """Create a fake `_Job` child class, and ensure the high-level cancel method works"""
        fake_job = self.FakeJob(job_name=_TEST_JOB_RESOURCE_NAME)
        fake_job.cancel()

        fake_job_cancel_mock.assert_called_once_with(name=_TEST_JOB_RESOURCE_NAME)


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
def get_batch_prediction_job_v1beta1_mock():
    with patch.object(
        _TEST_API_CLIENT_BETA, "get_batch_prediction_job"
    ) as get_batch_prediction_job_v1beta1_mock:
        get_batch_prediction_job_v1beta1_mock.side_effect = [
            gca_batch_prediction_job_v1beta1.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_JOB_NAME,
                display_name=_TEST_DISPLAY_NAME,
                state=_TEST_JOB_STATE_PENDING_V1BETA1,
            ),
            gca_batch_prediction_job_v1beta1.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_JOB_NAME,
                display_name=_TEST_DISPLAY_NAME,
                state=_TEST_JOB_STATE_RUNNING_V1BETA1,
            ),
            gca_batch_prediction_job_v1beta1.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_JOB_NAME,
                display_name=_TEST_DISPLAY_NAME,
                state=_TEST_JOB_STATE_SUCCESS_V1BETA1,
            ),
            gca_batch_prediction_job_v1beta1.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_JOB_NAME,
                display_name=_TEST_DISPLAY_NAME,
                state=_TEST_JOB_STATE_SUCCESS_V1BETA1,
            ),
        ]
        yield get_batch_prediction_job_v1beta1_mock


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


@pytest.fixture
def create_batch_prediction_job_v1beta1_mock():
    with mock.patch.object(
        _TEST_API_CLIENT_BETA, "create_batch_prediction_job"
    ) as create_batch_prediction_job_v1beta1_mock:
        create_batch_prediction_job_v1beta1_mock.return_value = (
            gca_batch_prediction_job_v1beta1.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_JOB_NAME,
                display_name=_TEST_DISPLAY_NAME,
                state=_TEST_JOB_STATE_SUCCESS_V1BETA1,
            )
        )
        yield create_batch_prediction_job_v1beta1_mock


@pytest.fixture
def create_batch_prediction_job_mock_fail():
    with mock.patch.object(
        _TEST_API_CLIENT, "create_batch_prediction_job"
    ) as create_batch_prediction_job_mock:
        create_batch_prediction_job_mock.side_effect = RuntimeError("Mock fail")
        yield create_batch_prediction_job_mock


@pytest.fixture
def create_batch_prediction_job_with_explanations_mock():
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


@pytest.fixture
def get_batch_prediction_job_gcs_output_mock():
    with patch.object(
        _TEST_API_CLIENT, "get_batch_prediction_job"
    ) as get_batch_prediction_job_mock:
        get_batch_prediction_job_mock.return_value = (
            gca_batch_prediction_job_compat.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_JOB_NAME,
                display_name=_TEST_DISPLAY_NAME,
                model=_TEST_MODEL_NAME,
                input_config=_TEST_GCS_INPUT_CONFIG,
                output_config=_TEST_GCS_OUTPUT_CONFIG,
                output_info=_TEST_GCS_OUTPUT_INFO,
                state=_TEST_JOB_STATE_SUCCESS,
            )
        )
        yield get_batch_prediction_job_mock


@pytest.fixture
def get_batch_prediction_job_bq_output_mock():
    with patch.object(
        _TEST_API_CLIENT, "get_batch_prediction_job"
    ) as get_batch_prediction_job_mock:
        get_batch_prediction_job_mock.return_value = (
            gca_batch_prediction_job_compat.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_JOB_NAME,
                display_name=_TEST_DISPLAY_NAME,
                model=_TEST_MODEL_NAME,
                input_config=_TEST_GCS_INPUT_CONFIG,
                output_config=_TEST_BQ_OUTPUT_CONFIG,
                output_info=_TEST_BQ_OUTPUT_INFO,
                state=_TEST_JOB_STATE_SUCCESS,
            )
        )
        yield get_batch_prediction_job_mock


@pytest.fixture
def get_batch_prediction_job_incomplete_bq_output_mock():
    with patch.object(
        _TEST_API_CLIENT, "get_batch_prediction_job"
    ) as get_batch_prediction_job_mock:
        get_batch_prediction_job_mock.return_value = (
            gca_batch_prediction_job_compat.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_JOB_NAME,
                display_name=_TEST_DISPLAY_NAME,
                model=_TEST_MODEL_NAME,
                input_config=_TEST_GCS_INPUT_CONFIG,
                output_config=_TEST_BQ_OUTPUT_CONFIG,
                output_info=_TEST_BQ_OUTPUT_INFO_INCOMPLETE,
                state=_TEST_JOB_STATE_SUCCESS,
            )
        )
        yield get_batch_prediction_job_mock


@pytest.fixture
def get_batch_prediction_job_empty_output_mock():
    with patch.object(
        _TEST_API_CLIENT, "get_batch_prediction_job"
    ) as get_batch_prediction_job_mock:
        get_batch_prediction_job_mock.return_value = (
            gca_batch_prediction_job_compat.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_JOB_NAME,
                display_name=_TEST_DISPLAY_NAME,
                model=_TEST_MODEL_NAME,
                input_config=_TEST_GCS_INPUT_CONFIG,
                output_config=_TEST_BQ_OUTPUT_CONFIG,
                output_info=_TEST_EMPTY_OUTPUT_INFO,
                state=_TEST_JOB_STATE_SUCCESS,
            )
        )
        yield get_batch_prediction_job_mock


@pytest.fixture
def get_batch_prediction_job_running_bq_output_mock():
    with patch.object(
        _TEST_API_CLIENT, "get_batch_prediction_job"
    ) as get_batch_prediction_job_mock:
        get_batch_prediction_job_mock.return_value = (
            gca_batch_prediction_job_compat.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_JOB_NAME,
                display_name=_TEST_DISPLAY_NAME,
                model=_TEST_MODEL_NAME,
                input_config=_TEST_GCS_INPUT_CONFIG,
                output_config=_TEST_BQ_OUTPUT_CONFIG,
                output_info=_TEST_BQ_OUTPUT_INFO,
                state=_TEST_JOB_STATE_RUNNING,
            )
        )
        yield get_batch_prediction_job_mock


@pytest.fixture
def storage_list_blobs_mock():
    with patch.object(storage.Client, "list_blobs") as list_blobs_mock:
        list_blobs_mock.return_value = _TEST_GCS_BLOBS
        yield list_blobs_mock


@pytest.fixture
def bq_list_rows_mock():
    with patch.object(bigquery.Client, "list_rows") as list_rows_mock:
        list_rows_mock.return_value = mock.Mock(bigquery.table.RowIterator)
        yield list_rows_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestBatchPredictionJob:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_batch_prediction_job(self, get_batch_prediction_job_mock):
        jobs.BatchPredictionJob(
            batch_prediction_job_name=_TEST_BATCH_PREDICTION_JOB_NAME
        )
        get_batch_prediction_job_mock.assert_called_once_with(
            name=_TEST_BATCH_PREDICTION_JOB_NAME, retry=base._DEFAULT_RETRY
        )

    def test_batch_prediction_job_status(self, get_batch_prediction_job_mock):
        bp = jobs.BatchPredictionJob(
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
        bp = jobs.BatchPredictionJob(
            batch_prediction_job_name=_TEST_BATCH_PREDICTION_JOB_NAME
        )

        assert bp.done() is False
        assert get_batch_prediction_job_mock.call_count == 2

    @pytest.mark.usefixtures("get_batch_prediction_job_gcs_output_mock")
    def test_batch_prediction_iter_dirs_gcs(self, storage_list_blobs_mock):
        bp = jobs.BatchPredictionJob(
            batch_prediction_job_name=_TEST_BATCH_PREDICTION_JOB_NAME
        )
        blobs = bp.iter_outputs()

        storage_list_blobs_mock.assert_called_once_with(
            _TEST_GCS_OUTPUT_INFO.gcs_output_directory, prefix=None
        )

        assert blobs == _TEST_GCS_BLOBS

    @pytest.mark.usefixtures("get_batch_prediction_job_bq_output_mock")
    def test_batch_prediction_iter_dirs_bq(self, bq_list_rows_mock):
        bp = jobs.BatchPredictionJob(
            batch_prediction_job_name=_TEST_BATCH_PREDICTION_JOB_NAME
        )

        bp.iter_outputs()

        bq_list_rows_mock.assert_called_once_with(
            table=f"{_TEST_BQ_PROJECT_ID}.{_TEST_BQ_DATASET_ID}.{_TEST_BQ_TABLE_NAME}",
            max_results=_TEST_BQ_MAX_RESULTS,
        )

    @pytest.mark.usefixtures("get_batch_prediction_job_incomplete_bq_output_mock")
    def test_batch_prediction_iter_dirs_bq_raises_on_empty(self, bq_list_rows_mock):
        bp = jobs.BatchPredictionJob(
            batch_prediction_job_name=_TEST_BATCH_PREDICTION_JOB_NAME
        )
        with pytest.raises(RuntimeError) as e:
            bp.iter_outputs()
        assert e.match(
            regexp=(
                "A BigQuery table with predictions was not found,"
                " this might be due to errors. Visit http"
            )
        )

    @pytest.mark.usefixtures("get_batch_prediction_job_running_bq_output_mock")
    def test_batch_prediction_iter_dirs_while_running(self):
        """
        Raises RuntimeError since outputs cannot be read while BatchPredictionJob is still running
        """
        with pytest.raises(RuntimeError):
            bp = jobs.BatchPredictionJob(
                batch_prediction_job_name=_TEST_BATCH_PREDICTION_JOB_NAME
            )
            bp.iter_outputs()

    @pytest.mark.usefixtures("get_batch_prediction_job_empty_output_mock")
    def test_batch_prediction_iter_dirs_invalid_output_info(self):
        """
        Raises NotImplementedError since the BatchPredictionJob's output_info
        contains no output GCS directory or BQ dataset.
        """
        with pytest.raises(NotImplementedError):
            bp = jobs.BatchPredictionJob(
                batch_prediction_job_name=_TEST_BATCH_PREDICTION_JOB_NAME
            )
            bp.iter_outputs()

    @mock.patch.object(jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_batch_prediction_job_mock")
    def test_batch_predict_gcs_source_and_dest(
        self, create_batch_prediction_job_mock, sync
    ):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        # Make SDK batch_predict method call
        batch_prediction_job = jobs.BatchPredictionJob.create(
            model_name=_TEST_MODEL_NAME,
            job_display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            gcs_destination_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX,
            sync=sync,
            create_request_timeout=None,
            service_account=_TEST_SERVICE_ACCOUNT,
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
        )

        create_batch_prediction_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            batch_prediction_job=expected_gapic_batch_prediction_job,
            timeout=None,
        )

    @mock.patch.object(jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_batch_prediction_job_mock")
    def test_batch_predict_gcs_source_and_dest_with_timeout(
        self, create_batch_prediction_job_mock, sync
    ):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        # Make SDK batch_predict method call
        batch_prediction_job = jobs.BatchPredictionJob.create(
            model_name=_TEST_MODEL_NAME,
            job_display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            gcs_destination_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX,
            sync=sync,
            create_request_timeout=180.0,
            service_account=_TEST_SERVICE_ACCOUNT,
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
        )

        create_batch_prediction_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            batch_prediction_job=expected_gapic_batch_prediction_job,
            timeout=180.0,
        )

    @mock.patch.object(jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_batch_prediction_job_mock")
    def test_batch_predict_gcs_source_and_dest_with_timeout_not_explicitly_set(
        self, create_batch_prediction_job_mock, sync
    ):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        # Make SDK batch_predict method call
        batch_prediction_job = jobs.BatchPredictionJob.create(
            model_name=_TEST_MODEL_NAME,
            job_display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            gcs_destination_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX,
            sync=sync,
            service_account=_TEST_SERVICE_ACCOUNT,
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
        )

        create_batch_prediction_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            batch_prediction_job=expected_gapic_batch_prediction_job,
            timeout=None,
        )

    @mock.patch.object(jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures("get_batch_prediction_job_mock")
    def test_batch_predict_job_done_create(self, create_batch_prediction_job_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        # Make SDK batch_predict method call
        batch_prediction_job = jobs.BatchPredictionJob.create(
            model_name=_TEST_MODEL_NAME,
            job_display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            gcs_destination_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX,
            sync=False,
            service_account=_TEST_SERVICE_ACCOUNT,
        )

        batch_prediction_job.wait_for_resource_creation()

        assert batch_prediction_job.done() is False

        batch_prediction_job.wait()

        assert batch_prediction_job.done() is True

    @mock.patch.object(jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_batch_prediction_job_mock")
    def test_batch_predict_gcs_source_bq_dest(
        self, create_batch_prediction_job_mock, sync
    ):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        batch_prediction_job = jobs.BatchPredictionJob.create(
            model_name=_TEST_MODEL_NAME,
            job_display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            bigquery_destination_prefix=_TEST_BATCH_PREDICTION_BQ_PREFIX,
            sync=sync,
            create_request_timeout=None,
            service_account=_TEST_SERVICE_ACCOUNT,
        )

        batch_prediction_job.wait_for_resource_creation()

        batch_prediction_job.wait()

        assert (
            batch_prediction_job.output_info
            == gca_batch_prediction_job_compat.BatchPredictionJob.OutputInfo()
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
                bigquery_destination=gca_io_compat.BigQueryDestination(
                    output_uri=_TEST_BATCH_PREDICTION_BQ_DEST_PREFIX_WITH_PROTOCOL
                ),
                predictions_format="bigquery",
            ),
            service_account=_TEST_SERVICE_ACCOUNT,
        )

        create_batch_prediction_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            batch_prediction_job=expected_gapic_batch_prediction_job,
            timeout=None,
        )

    @mock.patch.object(jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_batch_prediction_job_mock")
    def test_batch_predict_with_all_args(
        self, create_batch_prediction_job_with_explanations_mock, sync
    ):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        creds = auth_credentials.AnonymousCredentials()

        batch_prediction_job = jobs.BatchPredictionJob.create(
            model_name=_TEST_MODEL_NAME,
            job_display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            gcs_destination_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX,
            predictions_format="csv",
            model_parameters={},
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            starting_replica_count=_TEST_STARTING_REPLICA_COUNT,
            max_replica_count=_TEST_MAX_REPLICA_COUNT,
            generate_explanation=True,
            explanation_metadata=_TEST_EXPLANATION_METADATA,
            explanation_parameters=_TEST_EXPLANATION_PARAMETERS,
            labels=_TEST_LABEL,
            credentials=creds,
            sync=sync,
            create_request_timeout=None,
            batch_size=_TEST_BATCH_SIZE,
            service_account=_TEST_SERVICE_ACCOUNT,
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
                predictions_format="csv",
            ),
            dedicated_resources=gca_machine_resources_compat.BatchDedicatedResources(
                machine_spec=gca_machine_resources_compat.MachineSpec(
                    machine_type=_TEST_MACHINE_TYPE,
                    accelerator_type=_TEST_ACCELERATOR_TYPE,
                    accelerator_count=_TEST_ACCELERATOR_COUNT,
                ),
                starting_replica_count=_TEST_STARTING_REPLICA_COUNT,
                max_replica_count=_TEST_MAX_REPLICA_COUNT,
            ),
            manual_batch_tuning_parameters=gca_manual_batch_tuning_parameters_compat.ManualBatchTuningParameters(
                batch_size=_TEST_BATCH_SIZE
            ),
            generate_explanation=True,
            explanation_spec=gca_explanation_compat.ExplanationSpec(
                metadata=_TEST_EXPLANATION_METADATA,
                parameters=_TEST_EXPLANATION_PARAMETERS,
            ),
            labels=_TEST_LABEL,
            service_account=_TEST_SERVICE_ACCOUNT,
        )

        create_batch_prediction_job_with_explanations_mock.assert_called_once_with(
            parent=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
            batch_prediction_job=expected_gapic_batch_prediction_job,
            timeout=None,
        )

    @mock.patch.object(jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_batch_prediction_job_v1beta1_mock")
    def test_batch_predict_with_all_args_and_model_monitoring(
        self, create_batch_prediction_job_v1beta1_mock, sync
    ):
        from google.cloud.aiplatform.compat.types import (
            io_v1beta1 as gca_io_compat,
            batch_prediction_job_v1beta1 as gca_batch_prediction_job_compat,
            machine_resources_v1beta1 as gca_machine_resources_compat,
            manual_batch_tuning_parameters_v1beta1 as gca_manual_batch_tuning_parameters_compat,
            explanation_v1beta1 as gca_explanation_compat,
        )

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        creds = auth_credentials.AnonymousCredentials()
        mm_obj_cfg = model_monitoring.ObjectiveConfig(
            skew_detection_config=model_monitoring.SkewDetectionConfig(
                data_source="",
                target_field="",
                skew_thresholds={_TEST_THRESHOLD_KEY: _TEST_THRESHOLD_VAL},
                attribute_skew_thresholds={_TEST_THRESHOLD_KEY: _TEST_THRESHOLD_VAL},
            ),
            drift_detection_config=model_monitoring.DriftDetectionConfig(
                drift_thresholds={_TEST_THRESHOLD_KEY: _TEST_THRESHOLD_VAL},
                attribute_drift_thresholds={_TEST_THRESHOLD_KEY: _TEST_THRESHOLD_VAL},
            ),
            explanation_config=model_monitoring.ExplanationConfig(),
        )
        mm_alert_cfg = model_monitoring.EmailAlertConfig(user_emails=[""])
        batch_prediction_job = jobs.BatchPredictionJob.create(
            model_name=_TEST_MODEL_NAME,
            job_display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            gcs_destination_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX,
            predictions_format="csv",
            model_parameters={},
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            starting_replica_count=_TEST_STARTING_REPLICA_COUNT,
            max_replica_count=_TEST_MAX_REPLICA_COUNT,
            generate_explanation=True,
            explanation_metadata=_TEST_EXPLANATION_METADATA,
            labels=_TEST_LABEL,
            credentials=creds,
            sync=sync,
            create_request_timeout=None,
            batch_size=_TEST_BATCH_SIZE,
            model_monitoring_objective_config=mm_obj_cfg,
            model_monitoring_alert_config=mm_alert_cfg,
            analysis_instance_schema_uri="",
            service_account=_TEST_SERVICE_ACCOUNT,
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
                predictions_format="csv",
            ),
            dedicated_resources=gca_machine_resources_compat.BatchDedicatedResources(
                machine_spec=gca_machine_resources_compat.MachineSpec(
                    machine_type=_TEST_MACHINE_TYPE,
                    accelerator_type=_TEST_ACCELERATOR_TYPE,
                    accelerator_count=_TEST_ACCELERATOR_COUNT,
                ),
                starting_replica_count=_TEST_STARTING_REPLICA_COUNT,
                max_replica_count=_TEST_MAX_REPLICA_COUNT,
            ),
            manual_batch_tuning_parameters=gca_manual_batch_tuning_parameters_compat.ManualBatchTuningParameters(
                batch_size=_TEST_BATCH_SIZE
            ),
            explanation_spec=gca_explanation_compat.ExplanationSpec(
                metadata=_TEST_EXPLANATION_METADATA_V1BETA1,
            ),
            generate_explanation=True,
            model_monitoring_config=_TEST_MODEL_MONITORING_CFG,
            labels=_TEST_LABEL,
            service_account=_TEST_SERVICE_ACCOUNT,
        )
        create_batch_prediction_job_v1beta1_mock.assert_called_once_with(
            parent=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
            batch_prediction_job=expected_gapic_batch_prediction_job,
            timeout=None,
        )

    @pytest.mark.usefixtures("create_batch_prediction_job_mock_fail")
    def test_batch_predict_create_fails(self):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        batch_prediction_job = jobs.BatchPredictionJob.create(
            model_name=_TEST_MODEL_NAME,
            job_display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            bigquery_destination_prefix=_TEST_BATCH_PREDICTION_BQ_PREFIX,
            sync=False,
            service_account=_TEST_SERVICE_ACCOUNT,
        )

        with pytest.raises(RuntimeError) as e:
            batch_prediction_job.wait()
        assert e.match(regexp=r"Mock fail")

        with pytest.raises(RuntimeError) as e:
            batch_prediction_job.output_info
        assert e.match(
            regexp=r"BatchPredictionJob resource has not been created. Resource failed with: Mock fail"
        )

        with pytest.raises(RuntimeError) as e:
            batch_prediction_job.partial_failures
        assert e.match(
            regexp=r"BatchPredictionJob resource has not been created. Resource failed with: Mock fail"
        )

        with pytest.raises(RuntimeError) as e:
            batch_prediction_job.completion_stats
        assert e.match(
            regexp=r"BatchPredictionJob resource has not been created. Resource failed with: Mock fail"
        )

        with pytest.raises(RuntimeError) as e:
            batch_prediction_job.iter_outputs()
        assert e.match(
            regexp=r"BatchPredictionJob resource has not been created. Resource failed with: Mock fail"
        )

    @pytest.mark.usefixtures("get_batch_prediction_job_mock")
    def test_batch_predict_no_source(self, create_batch_prediction_job_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        # Make SDK batch_predict method call without source
        with pytest.raises(ValueError) as e:
            jobs.BatchPredictionJob.create(
                model_name=_TEST_MODEL_NAME,
                job_display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
                bigquery_destination_prefix=_TEST_BATCH_PREDICTION_BQ_PREFIX,
                service_account=_TEST_SERVICE_ACCOUNT,
            )

        assert e.match(regexp=r"source")

    @pytest.mark.usefixtures("get_batch_prediction_job_mock")
    def test_batch_predict_two_sources(self, create_batch_prediction_job_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        # Make SDK batch_predict method call with two sources
        with pytest.raises(ValueError) as e:
            jobs.BatchPredictionJob.create(
                model_name=_TEST_MODEL_NAME,
                job_display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
                gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
                bigquery_source=_TEST_BATCH_PREDICTION_BQ_PREFIX,
                bigquery_destination_prefix=_TEST_BATCH_PREDICTION_BQ_PREFIX,
                service_account=_TEST_SERVICE_ACCOUNT,
            )

        assert e.match(regexp=r"source")

    @pytest.mark.usefixtures("get_batch_prediction_job_mock")
    def test_batch_predict_no_destination(self):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        # Make SDK batch_predict method call without destination
        with pytest.raises(ValueError) as e:
            jobs.BatchPredictionJob.create(
                model_name=_TEST_MODEL_NAME,
                job_display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
                gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
                service_account=_TEST_SERVICE_ACCOUNT,
            )

        assert e.match(regexp=r"destination")

    @pytest.mark.usefixtures("get_batch_prediction_job_mock")
    def test_batch_predict_wrong_instance_format(self):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        # Make SDK batch_predict method call
        with pytest.raises(ValueError) as e:
            jobs.BatchPredictionJob.create(
                model_name=_TEST_MODEL_NAME,
                job_display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
                gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
                instances_format="wrong",
                bigquery_destination_prefix=_TEST_BATCH_PREDICTION_BQ_PREFIX,
                service_account=_TEST_SERVICE_ACCOUNT,
            )

        assert e.match(regexp=r"accepted instances format")

    @pytest.mark.usefixtures("get_batch_prediction_job_mock")
    def test_batch_predict_wrong_prediction_format(self):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        # Make SDK batch_predict method call
        with pytest.raises(ValueError) as e:
            jobs.BatchPredictionJob.create(
                model_name=_TEST_MODEL_NAME,
                job_display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
                gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
                predictions_format="wrong",
                bigquery_destination_prefix=_TEST_BATCH_PREDICTION_BQ_PREFIX,
                service_account=_TEST_SERVICE_ACCOUNT,
            )

        assert e.match(regexp=r"accepted prediction format")

    @pytest.mark.usefixtures("get_batch_prediction_job_mock")
    def test_batch_predict_job_with_versioned_model(
        self, create_batch_prediction_job_mock
    ):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        # Make SDK batch_predict method call
        _ = jobs.BatchPredictionJob.create(
            model_name=_TEST_VERSIONED_MODEL_NAME,
            job_display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            gcs_destination_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX,
            sync=True,
            service_account=_TEST_SERVICE_ACCOUNT,
        )
        assert (
            create_batch_prediction_job_mock.call_args_list[0][1][
                "batch_prediction_job"
            ].model
            == _TEST_VERSIONED_MODEL_NAME
        )

        # Make SDK batch_predict method call
        _ = jobs.BatchPredictionJob.create(
            model_name=f"{_TEST_ALT_ID}@{_TEST_MODEL_VERSION_ID}",
            job_display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            gcs_destination_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX,
            sync=True,
            service_account=_TEST_SERVICE_ACCOUNT,
        )
        assert (
            create_batch_prediction_job_mock.call_args_list[0][1][
                "batch_prediction_job"
            ].model
            == _TEST_VERSIONED_MODEL_NAME
        )

    @pytest.mark.usefixtures("get_batch_prediction_job_mock")
    def test_batch_predict_job_with_publisher_model(
        self, create_batch_prediction_job_mock
    ):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        # Make SDK batch_predict method call
        _ = jobs.BatchPredictionJob.create(
            model_name=_TEST_PUBLISHER_MODEL_NAME,
            job_display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            gcs_destination_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX,
            sync=True,
            service_account=_TEST_SERVICE_ACCOUNT,
        )
        assert (
            create_batch_prediction_job_mock.call_args_list[0][1][
                "batch_prediction_job"
            ].model
            == _TEST_PUBLISHER_MODEL_NAME
        )


@pytest.fixture
def get_mdm_job_mock():
    with mock.patch.object(
        _TEST_API_CLIENT, "get_model_deployment_monitoring_job"
    ) as get_mdm_job_mock:
        get_mdm_job_mock.side_effect = [
            _TEST_MDM_OLD_JOB,
            _TEST_MDM_OLD_JOB,
            _TEST_MDM_OLD_JOB,
            _TEST_MDM_EXPECTED_NEW_JOB,
        ]
        yield get_mdm_job_mock


@pytest.fixture
def update_mdm_job_mock(get_endpoint_with_models_mock):  # noqa: F811
    with mock.patch.object(
        _TEST_API_CLIENT, "update_model_deployment_monitoring_job"
    ) as update_mdm_job_mock:
        update_mdm_job_lro_mock = mock.Mock(operation.Operation)
        update_mdm_job_lro_mock.result.return_value = _TEST_MDM_EXPECTED_NEW_JOB
        update_mdm_job_mock.return_value = update_mdm_job_lro_mock
        yield update_mdm_job_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestModelDeploymentMonitoringJob:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_update_mdm_job(self, get_mdm_job_mock, update_mdm_job_mock):
        job = jobs.ModelDeploymentMonitoringJob(
            model_deployment_monitoring_job_name=_TEST_MDM_JOB_NAME
        )
        old_job = copy.deepcopy(job._gca_resource)
        drift_detection_config = aiplatform.model_monitoring.DriftDetectionConfig(
            drift_thresholds=_TEST_MDM_JOB_DRIFT_DETECTION_CONFIG
        )
        schedule_config = aiplatform.model_monitoring.ScheduleConfig(monitor_interval=1)
        alert_config = aiplatform.model_monitoring.EmailAlertConfig(
            user_emails=[_TEST_MDM_USER_EMAIL]
        )
        sampling_strategy = aiplatform.model_monitoring.RandomSampleConfig(
            sample_rate=_TEST_MDM_SAMPLE_RATE
        )
        labels = _TEST_MDM_LABEL
        log_ttl = _TEST_LOG_TTL_IN_DAYS
        display_name = _TEST_MDM_NEW_NAME
        new_config = aiplatform.model_monitoring.ObjectiveConfig(
            drift_detection_config=drift_detection_config
        )
        job.update(
            display_name=display_name,
            schedule_config=schedule_config,
            alert_config=alert_config,
            logging_sampling_strategy=sampling_strategy,
            labels=labels,
            bigquery_tables_log_ttl=log_ttl,
            enable_monitoring_pipeline_logs=True,
            objective_configs=new_config,
        )
        new_job = job._gca_resource
        assert old_job != new_job
        assert new_job.display_name == display_name
        assert new_job.logging_sampling_strategy == sampling_strategy.as_proto()
        assert (
            new_job.model_deployment_monitoring_schedule_config
            == schedule_config.as_proto()
        )
        assert new_job.labels == labels
        assert new_job.model_monitoring_alert_config == alert_config.as_proto()
        assert new_job.log_ttl.days == _TEST_LOG_TTL_IN_DAYS
        assert new_job.enable_monitoring_pipeline_logs
        assert (
            new_job.model_deployment_monitoring_objective_configs[
                0
            ].objective_config.prediction_drift_detection_config
            == drift_detection_config.as_proto()
        )
        get_mdm_job_mock.assert_called_with(
            name=_TEST_MDM_JOB_NAME, retry=base._DEFAULT_RETRY
        )
        update_mdm_job_mock.assert_called_once_with(
            model_deployment_monitoring_job=new_job,
            update_mask=field_mask_pb2.FieldMask(
                paths=[
                    "display_name",
                    "model_deployment_monitoring_schedule_config",
                    "model_monitoring_alert_config",
                    "logging_sampling_strategy",
                    "labels",
                    "log_ttl",
                    "enable_monitoring_pipeline_logs",
                    "model_deployment_monitoring_objective_configs",
                ]
            ),
            timeout=None,
        )
