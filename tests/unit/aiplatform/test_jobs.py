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

from google.auth import credentials as auth_credentials

from google.cloud import aiplatform

from google.cloud.aiplatform import jobs
from google.cloud.aiplatform import initializer

from google.cloud.aiplatform_v1beta1.services.job_service import (
    client as job_service_client_v1beta1,
)

from google.cloud.aiplatform_v1beta1.types import (
    batch_prediction_job as gca_batch_prediction_job_v1beta1,
    explanation as gca_explanation_v1beta1,
    io as gca_io_v1beta1,
    machine_resources as gca_machine_resources_v1beta1,
)

from google.cloud.aiplatform_v1.services.job_service import client as job_service_client

from google.cloud.aiplatform_v1.types import (
    batch_prediction_job as gca_batch_prediction_job,
    io as gca_io,
    job_state as gca_job_state,
)

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

_TEST_JOB_STATE_SUCCESS = gca_job_state.JobState(4)
_TEST_JOB_STATE_RUNNING = gca_job_state.JobState(3)
_TEST_JOB_STATE_PENDING = gca_job_state.JobState(2)

_TEST_GCS_INPUT_CONFIG = gca_batch_prediction_job.BatchPredictionJob.InputConfig(
    instances_format="jsonl",
    gcs_source=gca_io.GcsSource(uris=[_TEST_GCS_JSONL_SOURCE_URI]),
)
_TEST_GCS_OUTPUT_CONFIG = gca_batch_prediction_job.BatchPredictionJob.OutputConfig(
    predictions_format="jsonl",
    gcs_destination=gca_io.GcsDestination(output_uri_prefix=_TEST_GCS_BUCKET_PATH),
)

_TEST_BQ_INPUT_CONFIG = gca_batch_prediction_job.BatchPredictionJob.InputConfig(
    instances_format="bigquery",
    bigquery_source=gca_io.BigQuerySource(input_uri=_TEST_BQ_PATH),
)
_TEST_BQ_OUTPUT_CONFIG = gca_batch_prediction_job.BatchPredictionJob.OutputConfig(
    predictions_format="bigquery",
    bigquery_destination=gca_io.BigQueryDestination(output_uri=_TEST_BQ_PATH),
)

_TEST_GCS_OUTPUT_INFO = gca_batch_prediction_job.BatchPredictionJob.OutputInfo(
    gcs_output_directory=_TEST_GCS_BUCKET_NAME
)
_TEST_BQ_OUTPUT_INFO = gca_batch_prediction_job.BatchPredictionJob.OutputInfo(
    bigquery_output_dataset=_TEST_BQ_PATH
)

_TEST_EMPTY_OUTPUT_INFO = gca_batch_prediction_job.BatchPredictionJob.OutputInfo()

_TEST_GCS_BLOBS = [
    storage.Blob(name="some/path/prediction.jsonl", bucket=_TEST_GCS_BUCKET_NAME)
]

_TEST_MACHINE_TYPE = "n1-standard-4"
_TEST_ACCELERATOR_TYPE = "NVIDIA_TESLA_P100"
_TEST_ACCELERATOR_COUNT = 2
_TEST_STARTING_REPLICA_COUNT = 2
_TEST_MAX_REPLICA_COUNT = 12

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

_TEST_JOB_GET_METHOD_NAME = "get_fake_job"
_TEST_JOB_LIST_METHOD_NAME = "list_fake_job"
_TEST_JOB_CANCEL_METHOD_NAME = "cancel_fake_job"
_TEST_JOB_DELETE_METHOD_NAME = "delete_fake_job"
_TEST_JOB_RESOURCE_NAME = f"{_TEST_PARENT}/fakeJobs/{_TEST_ID}"

# TODO(b/171333554): Move reusable test fixtures to conftest.py file


@pytest.fixture
def fake_job_getter_mock():
    with patch.object(
        job_service_client.JobServiceClient, _TEST_JOB_GET_METHOD_NAME, create=True
    ) as fake_job_getter_mock:
        fake_job_getter_mock.return_value = {}
        yield fake_job_getter_mock


@pytest.fixture
def fake_job_cancel_mock():
    with patch.object(
        job_service_client.JobServiceClient, _TEST_JOB_CANCEL_METHOD_NAME, create=True
    ) as fake_job_cancel_mock:
        yield fake_job_cancel_mock


class TestJob:
    class FakeJob(jobs._Job):
        _job_type = "fake-job"
        _resource_noun = "fakeJobs"
        _getter_method = _TEST_JOB_GET_METHOD_NAME
        _list_method = _TEST_JOB_LIST_METHOD_NAME
        _cancel_method = _TEST_JOB_CANCEL_METHOD_NAME
        _delete_method = _TEST_JOB_DELETE_METHOD_NAME
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
        job_service_client.JobServiceClient, "get_batch_prediction_job"
    ) as get_batch_prediction_job_mock:
        get_batch_prediction_job_mock.side_effect = [
            gca_batch_prediction_job.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_JOB_NAME,
                display_name=_TEST_DISPLAY_NAME,
                state=_TEST_JOB_STATE_RUNNING,
            ),
            gca_batch_prediction_job.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_JOB_NAME,
                display_name=_TEST_DISPLAY_NAME,
                state=_TEST_JOB_STATE_SUCCESS,
            ),
            gca_batch_prediction_job.BatchPredictionJob(
                name=_TEST_BATCH_PREDICTION_JOB_NAME,
                display_name=_TEST_DISPLAY_NAME,
                state=_TEST_JOB_STATE_SUCCESS,
            ),
        ]
        yield get_batch_prediction_job_mock


@pytest.fixture
def create_batch_prediction_job_mock():
    with mock.patch.object(
        job_service_client.JobServiceClient, "create_batch_prediction_job"
    ) as create_batch_prediction_job_mock:
        create_batch_prediction_job_mock.return_value = gca_batch_prediction_job.BatchPredictionJob(
            name=_TEST_BATCH_PREDICTION_JOB_NAME,
            display_name=_TEST_DISPLAY_NAME,
            state=_TEST_JOB_STATE_SUCCESS,
        )
        yield create_batch_prediction_job_mock


@pytest.fixture
def create_batch_prediction_job_with_explanations_mock():
    with mock.patch.object(
        job_service_client_v1beta1.JobServiceClient, "create_batch_prediction_job"
    ) as create_batch_prediction_job_mock:
        create_batch_prediction_job_mock.return_value = gca_batch_prediction_job_v1beta1.BatchPredictionJob(
            name=_TEST_BATCH_PREDICTION_JOB_NAME,
            display_name=_TEST_DISPLAY_NAME,
            state=_TEST_JOB_STATE_SUCCESS,
        )
        yield create_batch_prediction_job_mock


@pytest.fixture
def get_batch_prediction_job_gcs_output_mock():
    with patch.object(
        job_service_client.JobServiceClient, "get_batch_prediction_job"
    ) as get_batch_prediction_job_mock:
        get_batch_prediction_job_mock.return_value = gca_batch_prediction_job.BatchPredictionJob(
            name=_TEST_BATCH_PREDICTION_JOB_NAME,
            display_name=_TEST_DISPLAY_NAME,
            model=_TEST_MODEL_NAME,
            input_config=_TEST_GCS_INPUT_CONFIG,
            output_config=_TEST_GCS_OUTPUT_CONFIG,
            output_info=_TEST_GCS_OUTPUT_INFO,
            state=_TEST_JOB_STATE_SUCCESS,
        )
        yield get_batch_prediction_job_mock


@pytest.fixture
def get_batch_prediction_job_bq_output_mock():
    with patch.object(
        job_service_client.JobServiceClient, "get_batch_prediction_job"
    ) as get_batch_prediction_job_mock:
        get_batch_prediction_job_mock.return_value = gca_batch_prediction_job.BatchPredictionJob(
            name=_TEST_BATCH_PREDICTION_JOB_NAME,
            display_name=_TEST_DISPLAY_NAME,
            model=_TEST_MODEL_NAME,
            input_config=_TEST_GCS_INPUT_CONFIG,
            output_config=_TEST_BQ_OUTPUT_CONFIG,
            output_info=_TEST_BQ_OUTPUT_INFO,
            state=_TEST_JOB_STATE_SUCCESS,
        )
        yield get_batch_prediction_job_mock


@pytest.fixture
def get_batch_prediction_job_empty_output_mock():
    with patch.object(
        job_service_client.JobServiceClient, "get_batch_prediction_job"
    ) as get_batch_prediction_job_mock:
        get_batch_prediction_job_mock.return_value = gca_batch_prediction_job.BatchPredictionJob(
            name=_TEST_BATCH_PREDICTION_JOB_NAME,
            display_name=_TEST_DISPLAY_NAME,
            model=_TEST_MODEL_NAME,
            input_config=_TEST_GCS_INPUT_CONFIG,
            output_config=_TEST_BQ_OUTPUT_CONFIG,
            output_info=_TEST_EMPTY_OUTPUT_INFO,
            state=_TEST_JOB_STATE_SUCCESS,
        )
        yield get_batch_prediction_job_mock


@pytest.fixture
def get_batch_prediction_job_running_bq_output_mock():
    with patch.object(
        job_service_client.JobServiceClient, "get_batch_prediction_job"
    ) as get_batch_prediction_job_mock:
        get_batch_prediction_job_mock.return_value = gca_batch_prediction_job.BatchPredictionJob(
            name=_TEST_BATCH_PREDICTION_JOB_NAME,
            display_name=_TEST_DISPLAY_NAME,
            model=_TEST_MODEL_NAME,
            input_config=_TEST_GCS_INPUT_CONFIG,
            output_config=_TEST_BQ_OUTPUT_CONFIG,
            output_info=_TEST_BQ_OUTPUT_INFO,
            state=_TEST_JOB_STATE_RUNNING,
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
            name=_TEST_BATCH_PREDICTION_JOB_NAME
        )

    def test_batch_prediction_job_status(self, get_batch_prediction_job_mock):
        bp = jobs.BatchPredictionJob(
            batch_prediction_job_name=_TEST_BATCH_PREDICTION_JOB_NAME
        )

        # get_batch_prediction() is called again here
        bp_job_state = bp.state

        assert get_batch_prediction_job_mock.call_count == 2
        assert bp_job_state == _TEST_JOB_STATE_SUCCESS

        get_batch_prediction_job_mock.assert_called_with(
            name=_TEST_BATCH_PREDICTION_JOB_NAME
        )

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
            table=f"{_TEST_BQ_DATASET_ID}.predictions", max_results=_TEST_BQ_MAX_RESULTS
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
        )

        if not sync:
            batch_prediction_job.wait()

        # Construct expected request
        expected_gapic_batch_prediction_job = gca_batch_prediction_job.BatchPredictionJob(
            display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
            model=_TEST_MODEL_NAME,
            input_config=gca_batch_prediction_job.BatchPredictionJob.InputConfig(
                instances_format="jsonl",
                gcs_source=gca_io.GcsSource(uris=[_TEST_BATCH_PREDICTION_GCS_SOURCE]),
            ),
            output_config=gca_batch_prediction_job.BatchPredictionJob.OutputConfig(
                gcs_destination=gca_io.GcsDestination(
                    output_uri_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX
                ),
                predictions_format="jsonl",
            ),
        )

        create_batch_prediction_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            batch_prediction_job=expected_gapic_batch_prediction_job,
        )

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
        )

        if not sync:
            batch_prediction_job.wait()

        # Construct expected request
        expected_gapic_batch_prediction_job = gca_batch_prediction_job.BatchPredictionJob(
            display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
            model=_TEST_MODEL_NAME,
            input_config=gca_batch_prediction_job.BatchPredictionJob.InputConfig(
                instances_format="jsonl",
                gcs_source=gca_io.GcsSource(uris=[_TEST_BATCH_PREDICTION_GCS_SOURCE]),
            ),
            output_config=gca_batch_prediction_job.BatchPredictionJob.OutputConfig(
                bigquery_destination=gca_io.BigQueryDestination(
                    output_uri=_TEST_BATCH_PREDICTION_BQ_DEST_PREFIX_WITH_PROTOCOL
                ),
                predictions_format="bigquery",
            ),
        )

        create_batch_prediction_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            batch_prediction_job=expected_gapic_batch_prediction_job,
        )

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
        )

        if not sync:
            batch_prediction_job.wait()

        # Construct expected request
        expected_gapic_batch_prediction_job = gca_batch_prediction_job_v1beta1.BatchPredictionJob(
            display_name=_TEST_BATCH_PREDICTION_JOB_DISPLAY_NAME,
            model=_TEST_MODEL_NAME,
            input_config=gca_batch_prediction_job_v1beta1.BatchPredictionJob.InputConfig(
                instances_format="jsonl",
                gcs_source=gca_io_v1beta1.GcsSource(
                    uris=[_TEST_BATCH_PREDICTION_GCS_SOURCE]
                ),
            ),
            output_config=gca_batch_prediction_job_v1beta1.BatchPredictionJob.OutputConfig(
                gcs_destination=gca_io_v1beta1.GcsDestination(
                    output_uri_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX
                ),
                predictions_format="csv",
            ),
            dedicated_resources=gca_machine_resources_v1beta1.BatchDedicatedResources(
                machine_spec=gca_machine_resources_v1beta1.MachineSpec(
                    machine_type=_TEST_MACHINE_TYPE,
                    accelerator_type=_TEST_ACCELERATOR_TYPE,
                    accelerator_count=_TEST_ACCELERATOR_COUNT,
                ),
                starting_replica_count=_TEST_STARTING_REPLICA_COUNT,
                max_replica_count=_TEST_MAX_REPLICA_COUNT,
            ),
            generate_explanation=True,
            explanation_spec=gca_explanation_v1beta1.ExplanationSpec(
                metadata=_TEST_EXPLANATION_METADATA,
                parameters=_TEST_EXPLANATION_PARAMETERS,
            ),
            labels=_TEST_LABEL,
        )

        create_batch_prediction_job_with_explanations_mock.assert_called_once_with(
            parent=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
            batch_prediction_job=expected_gapic_batch_prediction_job,
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
            )

        assert e.match(regexp=r"accepted prediction format")
