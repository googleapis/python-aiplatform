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

from distutils import core
import copy
import os
import functools
import importlib
import logging
import pathlib
import pytest
import subprocess
import shutil
import sys
import tarfile
import tempfile
import uuid
from unittest import mock
from unittest.mock import patch


from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import datasets
from google.cloud.aiplatform import explain
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import schema
from google.cloud.aiplatform import training_jobs
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.utils import source_utils
from google.cloud.aiplatform.utils import worker_spec_utils

from google.cloud.aiplatform.compat.services import (
    job_service_client,
    model_service_client,
    pipeline_service_client,
)

from google.cloud.aiplatform.compat.types import (
    custom_job as gca_custom_job,
    dataset as gca_dataset,
    encryption_spec as gca_encryption_spec,
    env_var as gca_env_var,
    io as gca_io,
    job_state as gca_job_state,
    model as gca_model,
    pipeline_state as gca_pipeline_state,
    training_pipeline as gca_training_pipeline,
)

from google.cloud import storage
from google.protobuf import json_format
from google.protobuf import struct_pb2
from google.protobuf import duration_pb2  # type: ignore
import constants as test_constants

_TEST_BUCKET_NAME = "test-bucket"
_TEST_GCS_PATH_WITHOUT_BUCKET = "path/to/folder"
_TEST_GCS_PATH = f"{_TEST_BUCKET_NAME}/{_TEST_GCS_PATH_WITHOUT_BUCKET}"
_TEST_GCS_PATH_WITH_TRAILING_SLASH = f"{_TEST_GCS_PATH}/"
_TEST_LOCAL_SCRIPT_FILE_NAME = (
    test_constants.TrainingJobConstants._TEST_LOCAL_SCRIPT_FILE_NAME
)
_TEST_TEMPDIR = tempfile.mkdtemp()
_TEST_LOCAL_SCRIPT_FILE_PATH = os.path.join(_TEST_TEMPDIR, _TEST_LOCAL_SCRIPT_FILE_NAME)
_TEST_PYTHON_SOURCE = """
print('hello world')
"""
_TEST_REQUIREMENTS = test_constants.TrainingJobConstants._TEST_REQUIREMENTS

_TEST_DATASET_DISPLAY_NAME = "test-dataset-display-name"
_TEST_DATASET_NAME = "test-dataset-name"
_TEST_DISPLAY_NAME = "test-display-name"
_TEST_METADATA_SCHEMA_URI_TABULAR = schema.dataset.metadata.tabular
_TEST_TRAINING_CONTAINER_IMAGE = (
    test_constants.TrainingJobConstants._TEST_TRAINING_CONTAINER_IMAGE
)
_TEST_TRAINING_CONTAINER_CMD = ["python3", "task.py"]
_TEST_SERVING_CONTAINER_IMAGE = (
    test_constants.TrainingJobConstants._TEST_TRAINING_CONTAINER_IMAGE
)
_TEST_SERVING_CONTAINER_PREDICTION_ROUTE = (
    test_constants.TrainingJobConstants._TEST_SERVING_CONTAINER_PREDICTION_ROUTE
)
_TEST_SERVING_CONTAINER_HEALTH_ROUTE = (
    test_constants.TrainingJobConstants._TEST_SERVING_CONTAINER_HEALTH_ROUTE
)
_TEST_MODULE_NAME = test_constants.TrainingJobConstants._TEST_MODULE_NAME

_TEST_METADATA_SCHEMA_URI_NONTABULAR = schema.dataset.metadata.image
_TEST_ANNOTATION_SCHEMA_URI = schema.dataset.annotation.image.classification

_TEST_BASE_OUTPUT_DIR = "gs://test-base-output-dir"
_TEST_SERVICE_ACCOUNT = test_constants.ProjectConstants._TEST_SERVICE_ACCOUNT
_TEST_BIGQUERY_DESTINATION = "bq://my-project"
_TEST_RUN_ARGS = test_constants.TrainingJobConstants._TEST_RUN_ARGS
_TEST_REPLICA_COUNT = test_constants.TrainingJobConstants._TEST_REPLICA_COUNT
_TEST_MACHINE_TYPE = test_constants.TrainingJobConstants._TEST_MACHINE_TYPE
_TEST_MACHINE_TYPE_TPU = test_constants.TrainingJobConstants._TEST_MACHINE_TYPE_TPU
_TEST_MACHINE_TYPE_TPU_V5E = (
    test_constants.TrainingJobConstants._TEST_MACHINE_TYPE_TPU_V5E
)
_TEST_REDUCTION_SERVER_REPLICA_COUNT = (
    test_constants.TrainingJobConstants._TEST_REDUCTION_SERVER_REPLICA_COUNT
)
_TEST_REDUCTION_SERVER_MACHINE_TYPE = (
    test_constants.TrainingJobConstants._TEST_REDUCTION_SERVER_MACHINE_TYPE
)
_TEST_REDUCTION_SERVER_CONTAINER_URI = (
    test_constants.TrainingJobConstants._TEST_REDUCTION_SERVER_CONTAINER_URI
)
_TEST_ACCELERATOR_TPU_TYPE = (
    test_constants.TrainingJobConstants._TEST_ACCELERATOR_TPU_TYPE
)
_TEST_ACCELERATOR_TYPE = test_constants.TrainingJobConstants._TEST_ACCELERATOR_TYPE
_TEST_INVALID_ACCELERATOR_TYPE = "NVIDIA_DOES_NOT_EXIST"
_TEST_ACCELERATOR_COUNT = test_constants.TrainingJobConstants._TEST_ACCELERATOR_COUNT
_TEST_BOOT_DISK_TYPE_DEFAULT = (
    test_constants.TrainingJobConstants._TEST_BOOT_DISK_TYPE_DEFAULT
)
_TEST_BOOT_DISK_SIZE_GB_DEFAULT = (
    test_constants.TrainingJobConstants._TEST_BOOT_DISK_SIZE_GB_DEFAULT
)
_TEST_BOOT_DISK_TYPE = test_constants.TrainingJobConstants._TEST_BOOT_DISK_TYPE
_TEST_BOOT_DISK_SIZE_GB = test_constants.TrainingJobConstants._TEST_BOOT_DISK_SIZE_GB
_TEST_MODEL_DISPLAY_NAME = test_constants.TrainingJobConstants._TEST_MODEL_DISPLAY_NAME
_TEST_LABELS = test_constants.ProjectConstants._TEST_LABELS
_TEST_MODEL_LABELS = test_constants.TrainingJobConstants._TEST_MODEL_LABELS

_TEST_TRAINING_FRACTION_SPLIT = (
    test_constants.TrainingJobConstants._TEST_TRAINING_FRACTION_SPLIT
)
_TEST_VALIDATION_FRACTION_SPLIT = (
    test_constants.TrainingJobConstants._TEST_VALIDATION_FRACTION_SPLIT
)
_TEST_TEST_FRACTION_SPLIT = (
    test_constants.TrainingJobConstants._TEST_TEST_FRACTION_SPLIT
)
_TEST_TRAINING_FILTER_SPLIT = "train"
_TEST_VALIDATION_FILTER_SPLIT = "validate"
_TEST_TEST_FILTER_SPLIT = "test"
_TEST_PREDEFINED_SPLIT_COLUMN_NAME = "split"
_TEST_TIMESTAMP_SPLIT_COLUMN_NAME = "timestamp"

_TEST_PROJECT = test_constants.ProjectConstants._TEST_PROJECT
_TEST_LOCATION = test_constants.ProjectConstants._TEST_LOCATION
_TEST_ID = test_constants.TrainingJobConstants._TEST_ID
_TEST_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/trainingPipelines/{_TEST_ID}"
)
_TEST_TENSORBOARD_RESOURCE_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/tensorboards/{_TEST_ID}"
)
_TEST_CUSTOM_JOB_RESOURCE_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/customJobs/{_TEST_ID}"
)
_TEST_MODEL_VERSION_DESCRIPTION = "My version description"
_TEST_MODEL_VERSION_ID = "2"
_TEST_ALT_PROJECT = "test-project-alt"
_TEST_ALT_LOCATION = "europe-west4"
_TEST_NETWORK = test_constants.TrainingJobConstants._TEST_NETWORK

_TEST_MODEL_INSTANCE_SCHEMA_URI = "instance_schema_uri.yaml"
_TEST_MODEL_PARAMETERS_SCHEMA_URI = "parameters_schema_uri.yaml"
_TEST_MODEL_PREDICTION_SCHEMA_URI = "prediction_schema_uri.yaml"
_TEST_MODEL_SERVING_CONTAINER_COMMAND = ["test_command"]
_TEST_MODEL_SERVING_CONTAINER_ARGS = ["test_args"]
_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES = {
    "learning_rate": 0.01,
    "loss_fn": "mse",
}
_TEST_ENVIRONMENT_VARIABLES = (
    test_constants.TrainingJobConstants._TEST_ENVIRONMENT_VARIABLES
)
_TEST_MODEL_SERVING_CONTAINER_PORTS = [8888, 10000]
_TEST_MODEL_DESCRIPTION = "test description"

_TEST_OUTPUT_PYTHON_PACKAGE_PATH = (
    test_constants.TrainingJobConstants._TEST_OUTPUT_PYTHON_PACKAGE_PATH
)
_TEST_PACKAGE_GCS_URIS = [_TEST_OUTPUT_PYTHON_PACKAGE_PATH] * 2
_TEST_PYTHON_MODULE_NAME = "aiplatform.task"

_TEST_MODEL_NAME = f"projects/{_TEST_PROJECT}/locations/us-central1/models/{_TEST_ID}"

_TEST_PIPELINE_RESOURCE_NAME = (
    f"projects/{_TEST_PROJECT}/locations/us-central1/trainingPipelines/{_TEST_ID}"
)
_TEST_CREDENTIALS = test_constants.TrainingJobConstants._TEST_CREDENTIALS


# Explanation Spec
_TEST_EXPLANATION_METADATA = explain.ExplanationMetadata(
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
_TEST_EXPLANATION_PARAMETERS = explain.ExplanationParameters(
    {"sampled_shapley_attribution": {"path_count": 10}}
)

# CMEK encryption
_TEST_DEFAULT_ENCRYPTION_KEY_NAME = "key_default"
_TEST_DEFAULT_ENCRYPTION_SPEC = gca_encryption_spec.EncryptionSpec(
    kms_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME
)

_TEST_PIPELINE_ENCRYPTION_KEY_NAME = "key_pipeline"
_TEST_PIPELINE_ENCRYPTION_SPEC = gca_encryption_spec.EncryptionSpec(
    kms_key_name=_TEST_PIPELINE_ENCRYPTION_KEY_NAME
)

_TEST_MODEL_ENCRYPTION_KEY_NAME = "key_model"
_TEST_MODEL_ENCRYPTION_SPEC = gca_encryption_spec.EncryptionSpec(
    kms_key_name=_TEST_MODEL_ENCRYPTION_KEY_NAME
)

_TEST_TIMEOUT = test_constants.TrainingJobConstants._TEST_TIMEOUT
_TEST_RESTART_JOB_ON_WORKER_RESTART = (
    test_constants.TrainingJobConstants._TEST_RESTART_JOB_ON_WORKER_RESTART
)

_TEST_DISABLE_RETRIES = test_constants.TrainingJobConstants._TEST_DISABLE_RETRIES
_TEST_MAX_WAIT_DURATION = test_constants.TrainingJobConstants._TEST_MAX_WAIT_DURATION
_TEST_ENABLE_WEB_ACCESS = test_constants.TrainingJobConstants._TEST_ENABLE_WEB_ACCESS
_TEST_ENABLE_DASHBOARD_ACCESS = True
_TEST_WEB_ACCESS_URIS = test_constants.TrainingJobConstants._TEST_WEB_ACCESS_URIS
_TEST_DASHBOARD_ACCESS_URIS = {"workerpool0-0:8888": "uri"}
_TEST_PERSISTENT_RESOURCE_ID = (
    test_constants.PersistentResourceConstants._TEST_PERSISTENT_RESOURCE_ID
)
_TEST_SPOT_STRATEGY = test_constants.TrainingJobConstants._TEST_SPOT_STRATEGY
_TEST_PSC_INTERFACE_CONFIG = (
    test_constants.TrainingJobConstants._TEST_PSC_INTERFACE_CONFIG
)

_TEST_BASE_CUSTOM_JOB_PROTO = gca_custom_job.CustomJob(
    job_spec=gca_custom_job.CustomJobSpec(),
)


def _get_custom_job_proto_with_enable_web_access(state=None, name=None, version="v1"):
    custom_job_proto = copy.deepcopy(_TEST_BASE_CUSTOM_JOB_PROTO)
    custom_job_proto.name = name
    custom_job_proto.state = state

    custom_job_proto.job_spec.enable_web_access = _TEST_ENABLE_WEB_ACCESS
    if state == gca_job_state.JobState.JOB_STATE_RUNNING:
        custom_job_proto.web_access_uris = _TEST_WEB_ACCESS_URIS
    return custom_job_proto


def _get_custom_job_proto_with_enable_dashboard_access(
    state=None, name=None, version="v1"
):
    custom_job_proto = copy.deepcopy(_TEST_BASE_CUSTOM_JOB_PROTO)
    custom_job_proto.name = name
    custom_job_proto.state = state

    custom_job_proto.job_spec.enable_dashboard_access = _TEST_ENABLE_DASHBOARD_ACCESS
    if state == gca_job_state.JobState.JOB_STATE_RUNNING:
        custom_job_proto.web_access_uris = _TEST_DASHBOARD_ACCESS_URIS
    return custom_job_proto


def _get_custom_job_proto_with_persistent_resource_id(
    state=None, name=None, version="v1"
):
    custom_job_proto = copy.deepcopy(_TEST_BASE_CUSTOM_JOB_PROTO)
    custom_job_proto.name = name
    custom_job_proto.state = state
    custom_job_proto.job_spec.persistent_resource_id = _TEST_PERSISTENT_RESOURCE_ID

    return custom_job_proto


def _get_custom_job_proto_with_scheduling(state=None, name=None, version="v1"):
    custom_job_proto = copy.deepcopy(_TEST_BASE_CUSTOM_JOB_PROTO)
    custom_job_proto.name = name
    custom_job_proto.state = state

    custom_job_proto.job_spec.scheduling.timeout = duration_pb2.Duration(
        seconds=_TEST_TIMEOUT
    )
    custom_job_proto.job_spec.scheduling.restart_job_on_worker_restart = (
        _TEST_RESTART_JOB_ON_WORKER_RESTART
    )
    custom_job_proto.job_spec.scheduling.disable_retries = _TEST_DISABLE_RETRIES
    custom_job_proto.job_spec.scheduling.max_wait_duration = duration_pb2.Duration(
        seconds=_TEST_MAX_WAIT_DURATION
    )

    return custom_job_proto


def _get_custom_job_proto_with_spot_strategy(state=None, name=None, version="v1"):
    custom_job_proto = copy.deepcopy(_TEST_BASE_CUSTOM_JOB_PROTO)
    custom_job_proto.name = name
    custom_job_proto.state = state

    custom_job_proto.job_spec.scheduling.strategy = _TEST_SPOT_STRATEGY
    return custom_job_proto


def _get_custom_job_proto_with_psc_interface_config(
    state=None, name=None, version="v1"
):
    custom_job_proto = copy.deepcopy(_TEST_BASE_CUSTOM_JOB_PROTO)
    custom_job_proto.name = name
    custom_job_proto.state = state

    custom_job_proto.job_spec.psc_interface_config = _TEST_PSC_INTERFACE_CONFIG
    return custom_job_proto


def local_copy_method(path):
    shutil.copy(path, ".")
    return pathlib.Path(path).name


@pytest.fixture
def get_training_job_custom_mock():
    with patch.object(
        pipeline_service_client.PipelineServiceClient, "get_training_pipeline"
    ) as get_training_job_custom_mock:
        get_training_job_custom_mock.return_value = (
            gca_training_pipeline.TrainingPipeline(
                name=_TEST_PIPELINE_RESOURCE_NAME,
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
                model_to_upload=gca_model.Model(name=_TEST_MODEL_NAME),
                training_task_definition=schema.training_job.definition.custom_task,
            )
        )

        yield get_training_job_custom_mock


@pytest.fixture
def get_training_job_custom_mock_no_model_to_upload():
    with patch.object(
        pipeline_service_client.PipelineServiceClient, "get_training_pipeline"
    ) as get_training_job_custom_mock:
        get_training_job_custom_mock.return_value = (
            gca_training_pipeline.TrainingPipeline(
                name=_TEST_PIPELINE_RESOURCE_NAME,
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
                model_to_upload=None,
                training_task_definition=schema.training_job.definition.custom_task,
            )
        )

        yield get_training_job_custom_mock


@pytest.fixture
def get_training_job_tabular_mock():
    with patch.object(
        pipeline_service_client.PipelineServiceClient, "get_training_pipeline"
    ) as get_training_job_tabular_mock:
        get_training_job_tabular_mock.return_value = (
            gca_training_pipeline.TrainingPipeline(
                name=_TEST_PIPELINE_RESOURCE_NAME,
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
                model_to_upload=gca_model.Model(name=_TEST_MODEL_NAME),
                training_task_definition=schema.training_job.definition.automl_tabular,
            )
        )

        yield get_training_job_tabular_mock


@pytest.fixture
def mock_client_bucket():
    with patch.object(storage.Client, "bucket") as mock_client_bucket:

        def blob_side_effect(name, mock_blob, bucket):
            mock_blob.name = name
            mock_blob.bucket = bucket
            return mock_blob

        MockBucket = mock.Mock(autospec=storage.Bucket)
        MockBucket.name = _TEST_BUCKET_NAME
        MockBlob = mock.Mock(autospec=storage.Blob)
        MockBucket.blob.side_effect = functools.partial(
            blob_side_effect, mock_blob=MockBlob, bucket=MockBucket
        )
        mock_client_bucket.return_value = MockBucket

        yield mock_client_bucket, MockBlob


@pytest.fixture
def mock_get_backing_custom_job_with_enable_web_access():
    with patch.object(
        job_service_client.JobServiceClient, "get_custom_job"
    ) as get_custom_job_mock:
        get_custom_job_mock.side_effect = [
            _get_custom_job_proto_with_enable_web_access(
                name=_TEST_CUSTOM_JOB_RESOURCE_NAME,
                state=gca_job_state.JobState.JOB_STATE_PENDING,
            ),
            _get_custom_job_proto_with_enable_web_access(
                name=_TEST_CUSTOM_JOB_RESOURCE_NAME,
                state=gca_job_state.JobState.JOB_STATE_RUNNING,
            ),
            _get_custom_job_proto_with_enable_web_access(
                name=_TEST_CUSTOM_JOB_RESOURCE_NAME,
                state=gca_job_state.JobState.JOB_STATE_RUNNING,
            ),
            _get_custom_job_proto_with_enable_web_access(
                name=_TEST_CUSTOM_JOB_RESOURCE_NAME,
                state=gca_job_state.JobState.JOB_STATE_RUNNING,
            ),
            _get_custom_job_proto_with_enable_web_access(
                name=_TEST_CUSTOM_JOB_RESOURCE_NAME,
                state=gca_job_state.JobState.JOB_STATE_SUCCEEDED,
            ),
            _get_custom_job_proto_with_enable_web_access(
                name=_TEST_CUSTOM_JOB_RESOURCE_NAME,
                state=gca_job_state.JobState.JOB_STATE_SUCCEEDED,
            ),
        ]
        yield get_custom_job_mock


@pytest.fixture
def mock_get_backing_custom_job_with_enable_dashboard_access():
    with patch.object(
        job_service_client.JobServiceClient, "get_custom_job"
    ) as get_custom_job_mock:
        get_custom_job_mock.side_effect = [
            _get_custom_job_proto_with_enable_dashboard_access(
                name=_TEST_CUSTOM_JOB_RESOURCE_NAME,
                state=gca_job_state.JobState.JOB_STATE_PENDING,
            ),
            _get_custom_job_proto_with_enable_dashboard_access(
                name=_TEST_CUSTOM_JOB_RESOURCE_NAME,
                state=gca_job_state.JobState.JOB_STATE_RUNNING,
            ),
            _get_custom_job_proto_with_enable_dashboard_access(
                name=_TEST_CUSTOM_JOB_RESOURCE_NAME,
                state=gca_job_state.JobState.JOB_STATE_RUNNING,
            ),
            _get_custom_job_proto_with_enable_dashboard_access(
                name=_TEST_CUSTOM_JOB_RESOURCE_NAME,
                state=gca_job_state.JobState.JOB_STATE_RUNNING,
            ),
            _get_custom_job_proto_with_enable_dashboard_access(
                name=_TEST_CUSTOM_JOB_RESOURCE_NAME,
                state=gca_job_state.JobState.JOB_STATE_SUCCEEDED,
            ),
            _get_custom_job_proto_with_enable_dashboard_access(
                name=_TEST_CUSTOM_JOB_RESOURCE_NAME,
                state=gca_job_state.JobState.JOB_STATE_SUCCEEDED,
            ),
        ]
        yield get_custom_job_mock


@pytest.fixture
def mock_get_backing_custom_job_with_persistent_resource_id():
    with patch.object(
        job_service_client.JobServiceClient, "get_custom_job"
    ) as get_custom_job_mock:
        get_custom_job_mock.side_effect = [
            _get_custom_job_proto_with_persistent_resource_id(
                name=_TEST_CUSTOM_JOB_RESOURCE_NAME,
                state=gca_job_state.JobState.JOB_STATE_PENDING,
            ),
            _get_custom_job_proto_with_persistent_resource_id(
                name=_TEST_CUSTOM_JOB_RESOURCE_NAME,
                state=gca_job_state.JobState.JOB_STATE_RUNNING,
            ),
            _get_custom_job_proto_with_persistent_resource_id(
                name=_TEST_CUSTOM_JOB_RESOURCE_NAME,
                state=gca_job_state.JobState.JOB_STATE_RUNNING,
            ),
            _get_custom_job_proto_with_persistent_resource_id(
                name=_TEST_CUSTOM_JOB_RESOURCE_NAME,
                state=gca_job_state.JobState.JOB_STATE_RUNNING,
            ),
            _get_custom_job_proto_with_persistent_resource_id(
                name=_TEST_CUSTOM_JOB_RESOURCE_NAME,
                state=gca_job_state.JobState.JOB_STATE_SUCCEEDED,
            ),
            _get_custom_job_proto_with_persistent_resource_id(
                name=_TEST_CUSTOM_JOB_RESOURCE_NAME,
                state=gca_job_state.JobState.JOB_STATE_SUCCEEDED,
            ),
        ]
        yield get_custom_job_mock


@pytest.mark.skipif(
    sys.executable is None, reason="requires python path to invoke subprocess"
)
@pytest.mark.usefixtures("google_auth_mock")
class TestTrainingScriptPythonPackagerHelpers:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)

    def test_timestamp_copy_to_gcs_calls_gcs_client_with_bucket(
        self, mock_client_bucket
    ):

        mock_client_bucket, mock_blob = mock_client_bucket

        gcs_path = utils._timestamped_copy_to_gcs(
            local_file_path=_TEST_LOCAL_SCRIPT_FILE_PATH,
            gcs_dir=_TEST_BUCKET_NAME,
            project=_TEST_PROJECT,
        )

        local_script_file_name = pathlib.Path(_TEST_LOCAL_SCRIPT_FILE_PATH).name

        mock_client_bucket.assert_called_once_with(_TEST_BUCKET_NAME)
        mock_client_bucket.return_value.blob.assert_called_once()

        blob_arg = mock_client_bucket.return_value.blob.call_args[0][0]
        assert blob_arg.startswith("aiplatform-")
        assert blob_arg.endswith(_TEST_LOCAL_SCRIPT_FILE_NAME)

        mock_blob.upload_from_filename.assert_called_once_with(
            _TEST_LOCAL_SCRIPT_FILE_PATH
        )
        assert gcs_path.endswith(local_script_file_name)
        assert gcs_path.startswith(f"gs://{_TEST_BUCKET_NAME}/aiplatform-")

    def test_timestamp_copy_to_gcs_calls_gcs_client_with_gcs_path(
        self, mock_client_bucket
    ):

        mock_client_bucket, mock_blob = mock_client_bucket

        gcs_path = utils._timestamped_copy_to_gcs(
            local_file_path=_TEST_LOCAL_SCRIPT_FILE_PATH,
            gcs_dir=_TEST_GCS_PATH_WITH_TRAILING_SLASH,
            project=_TEST_PROJECT,
        )

        local_script_file_name = pathlib.Path(_TEST_LOCAL_SCRIPT_FILE_PATH).name

        mock_client_bucket.assert_called_once_with(_TEST_BUCKET_NAME)
        mock_client_bucket.return_value.blob.assert_called_once()

        blob_arg = mock_client_bucket.return_value.blob.call_args[0][0]
        assert blob_arg.startswith(f"{_TEST_GCS_PATH_WITHOUT_BUCKET}/aiplatform-")
        assert blob_arg.endswith(f"{_TEST_LOCAL_SCRIPT_FILE_NAME}")

        mock_blob.upload_from_filename.assert_called_once_with(
            _TEST_LOCAL_SCRIPT_FILE_PATH
        )

        assert gcs_path.startswith(f"gs://{_TEST_GCS_PATH}/aiplatform-")
        assert gcs_path.endswith(local_script_file_name)

    def test_timestamp_copy_to_gcs_calls_gcs_client_with_trailing_slash(
        self, mock_client_bucket
    ):

        mock_client_bucket, mock_blob = mock_client_bucket

        gcs_path = utils._timestamped_copy_to_gcs(
            local_file_path=_TEST_LOCAL_SCRIPT_FILE_PATH,
            gcs_dir=_TEST_GCS_PATH,
            project=_TEST_PROJECT,
        )

        local_script_file_name = pathlib.Path(_TEST_LOCAL_SCRIPT_FILE_PATH).name

        mock_client_bucket.assert_called_once_with(_TEST_BUCKET_NAME)
        mock_client_bucket.return_value.blob.assert_called_once()

        blob_arg = mock_client_bucket.return_value.blob.call_args[0][0]
        assert blob_arg.startswith(f"{_TEST_GCS_PATH_WITHOUT_BUCKET}/aiplatform-")
        assert blob_arg.endswith(_TEST_LOCAL_SCRIPT_FILE_NAME)

        mock_blob.upload_from_filename.assert_called_once_with(
            _TEST_LOCAL_SCRIPT_FILE_PATH
        )

        assert gcs_path.startswith(f"gs://{_TEST_GCS_PATH}/aiplatform-")
        assert gcs_path.endswith(local_script_file_name)

    def test_timestamp_copy_to_gcs_calls_gcs_client(self, mock_client_bucket):

        mock_client_bucket, mock_blob = mock_client_bucket

        gcs_path = utils._timestamped_copy_to_gcs(
            local_file_path=_TEST_LOCAL_SCRIPT_FILE_PATH,
            gcs_dir=_TEST_BUCKET_NAME,
            project=_TEST_PROJECT,
        )

        mock_client_bucket.assert_called_once_with(_TEST_BUCKET_NAME)
        mock_client_bucket.return_value.blob.assert_called_once()
        mock_blob.upload_from_filename.assert_called_once_with(
            _TEST_LOCAL_SCRIPT_FILE_PATH
        )
        assert gcs_path.endswith(pathlib.Path(_TEST_LOCAL_SCRIPT_FILE_PATH).name)
        assert gcs_path.startswith(f"gs://{_TEST_BUCKET_NAME}")

    def test_get_python_executable_raises_if_None(self):
        with patch.object(sys, "executable", new=None):
            with pytest.raises(EnvironmentError):
                source_utils._get_python_executable()

    def test_get_python_executable_returns_python_executable(self):
        assert "python" in source_utils._get_python_executable().lower()


@pytest.mark.skipif(
    sys.executable is None, reason="requires python path to invoke subprocess"
)
@pytest.mark.usefixtures("google_auth_mock")
class TestTrainingScriptPythonPackager:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        with open(_TEST_LOCAL_SCRIPT_FILE_PATH, "w") as fp:
            fp.write(_TEST_PYTHON_SOURCE)

    def teardown_method(self):
        pathlib.Path(_TEST_LOCAL_SCRIPT_FILE_PATH).unlink()
        python_package_file = f"{source_utils._TrainingScriptPythonPackager._ROOT_MODULE}-{source_utils._TrainingScriptPythonPackager._SETUP_PY_VERSION}.tar.gz"
        if pathlib.Path(python_package_file).is_file():
            pathlib.Path(python_package_file).unlink()
        subprocess.check_output(
            [
                "pip3",
                "uninstall",
                "-y",
                source_utils._TrainingScriptPythonPackager._ROOT_MODULE,
            ]
        )

    def test_packager_creates_and_copies_python_package(self):
        tsp = source_utils._TrainingScriptPythonPackager(_TEST_LOCAL_SCRIPT_FILE_PATH)
        tsp.package_and_copy(copy_method=local_copy_method)
        assert pathlib.Path(
            f"{tsp._ROOT_MODULE}-{tsp._SETUP_PY_VERSION}.tar.gz"
        ).is_file()

    def test_requirements_are_in_package(self):
        tsp = source_utils._TrainingScriptPythonPackager(
            _TEST_LOCAL_SCRIPT_FILE_PATH, requirements=_TEST_REQUIREMENTS
        )
        source_dist_path = tsp.package_and_copy(copy_method=local_copy_method)
        with tarfile.open(source_dist_path) as tf:
            with tempfile.TemporaryDirectory() as tmpdirname:
                setup_py_path = f"{source_utils._TrainingScriptPythonPackager._ROOT_MODULE}-{source_utils._TrainingScriptPythonPackager._SETUP_PY_VERSION}/setup.py"
                tf.extract(setup_py_path, path=tmpdirname)
                setup_py = core.run_setup(
                    pathlib.Path(tmpdirname, setup_py_path), stop_after="init"
                )
                assert _TEST_REQUIREMENTS == setup_py.install_requires

    def test_packaging_fails_whith_RuntimeError(self):
        with patch("subprocess.Popen") as mock_popen:
            mock_subprocess = mock.Mock()
            mock_subprocess.communicate.return_value = (b"", b"")
            mock_subprocess.returncode = 1
            mock_popen.return_value = mock_subprocess
            tsp = source_utils._TrainingScriptPythonPackager(
                _TEST_LOCAL_SCRIPT_FILE_PATH
            )
            with pytest.raises(RuntimeError):
                tsp.package_and_copy(copy_method=local_copy_method)

    def test_package_and_copy_to_gcs_copies_to_gcs(self, mock_client_bucket):
        mock_client_bucket, mock_blob = mock_client_bucket

        tsp = source_utils._TrainingScriptPythonPackager(_TEST_LOCAL_SCRIPT_FILE_PATH)

        gcs_path = tsp.package_and_copy_to_gcs(
            gcs_staging_dir=_TEST_BUCKET_NAME, project=_TEST_PROJECT
        )

        mock_client_bucket.assert_called_once_with(_TEST_BUCKET_NAME)
        mock_client_bucket.return_value.blob.assert_called_once()

        mock_blob.upload_from_filename.call_args[0][0].endswith(
            "/trainer/dist/aiplatform_custom_trainer_script-0.1.tar.gz"
        )

        assert gcs_path.endswith("-aiplatform_custom_trainer_script-0.1.tar.gz")
        assert gcs_path.startswith(f"gs://{_TEST_BUCKET_NAME}")


@pytest.fixture
def mock_pipeline_service_create():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_training_pipeline"
    ) as mock_create_training_pipeline:
        mock_create_training_pipeline.return_value = (
            gca_training_pipeline.TrainingPipeline(
                name=_TEST_PIPELINE_RESOURCE_NAME,
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
                model_to_upload=gca_model.Model(name=_TEST_MODEL_NAME),
            )
        )
        yield mock_create_training_pipeline


@pytest.fixture
def mock_pipeline_service_create_with_version():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_training_pipeline"
    ) as mock_create_training_pipeline:
        mock_create_training_pipeline.return_value = (
            gca_training_pipeline.TrainingPipeline(
                name=_TEST_PIPELINE_RESOURCE_NAME,
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
                model_to_upload=gca_model.Model(
                    name=_TEST_MODEL_NAME, version_id=_TEST_MODEL_VERSION_ID
                ),
            )
        )
        yield mock_create_training_pipeline


def make_training_pipeline(state, add_training_task_metadata=True):
    return gca_training_pipeline.TrainingPipeline(
        name=_TEST_PIPELINE_RESOURCE_NAME,
        state=state,
        model_to_upload=gca_model.Model(name=_TEST_MODEL_NAME),
        training_task_inputs={"tensorboard": _TEST_TENSORBOARD_RESOURCE_NAME},
        training_task_metadata=(
            {"backingCustomJob": _TEST_CUSTOM_JOB_RESOURCE_NAME}
            if add_training_task_metadata
            else None
        ),
    )


def make_training_pipeline_with_version(state, add_training_task_metadata=True):
    return gca_training_pipeline.TrainingPipeline(
        name=_TEST_PIPELINE_RESOURCE_NAME,
        state=state,
        model_to_upload=gca_model.Model(
            name=_TEST_MODEL_NAME, version_id=_TEST_MODEL_VERSION_ID
        ),
        training_task_inputs={"tensorboard": _TEST_TENSORBOARD_RESOURCE_NAME},
        training_task_metadata=(
            {"backingCustomJob": _TEST_CUSTOM_JOB_RESOURCE_NAME}
            if add_training_task_metadata
            else None
        ),
    )


def make_training_pipeline_with_no_model_upload(state):
    return gca_training_pipeline.TrainingPipeline(
        name=_TEST_PIPELINE_RESOURCE_NAME,
        state=state,
    )


def make_training_pipeline_with_enable_web_access(state):
    training_pipeline = gca_training_pipeline.TrainingPipeline(
        name=_TEST_PIPELINE_RESOURCE_NAME,
        state=state,
        training_task_inputs={"enable_web_access": _TEST_ENABLE_WEB_ACCESS},
    )
    if state == gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING:
        training_pipeline.training_task_metadata = {
            "backingCustomJob": _TEST_CUSTOM_JOB_RESOURCE_NAME
        }
    return training_pipeline


def make_training_pipeline_with_enable_dashboard_access(state):
    training_pipeline = gca_training_pipeline.TrainingPipeline(
        name=_TEST_PIPELINE_RESOURCE_NAME,
        state=state,
        training_task_inputs={"enable_dashboard_access": _TEST_ENABLE_DASHBOARD_ACCESS},
    )
    if state == gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING:
        training_pipeline.training_task_metadata = {
            "backingCustomJob": _TEST_CUSTOM_JOB_RESOURCE_NAME
        }
    return training_pipeline


def make_training_pipeline_with_persistent_resource_id(state):
    training_pipeline = gca_training_pipeline.TrainingPipeline(
        name=_TEST_PIPELINE_RESOURCE_NAME,
        state=state,
        training_task_inputs={"persistent_resource_id": _TEST_PERSISTENT_RESOURCE_ID},
    )
    if state == gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING:
        training_pipeline.training_task_metadata = {
            "backingCustomJob": _TEST_CUSTOM_JOB_RESOURCE_NAME
        }
    return training_pipeline


def make_training_pipeline_with_scheduling(state):
    training_pipeline = gca_training_pipeline.TrainingPipeline(
        name=_TEST_PIPELINE_RESOURCE_NAME,
        state=state,
        training_task_inputs={
            "timeout": f"{_TEST_TIMEOUT}s",
            "restart_job_on_worker_restart": _TEST_RESTART_JOB_ON_WORKER_RESTART,
            "disable_retries": _TEST_DISABLE_RETRIES,
            "max_wait_duration": f"{_TEST_MAX_WAIT_DURATION}s",
        },
    )
    if state == gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING:
        training_pipeline.training_task_metadata = {
            "backingCustomJob": _TEST_CUSTOM_JOB_RESOURCE_NAME
        }
    return training_pipeline


def make_training_pipeline_with_spot_strategy(state):
    training_pipeline = gca_training_pipeline.TrainingPipeline(
        name=_TEST_PIPELINE_RESOURCE_NAME,
        state=state,
        training_task_inputs={
            "scheduling_strategy": _TEST_SPOT_STRATEGY,
        },
    )
    if state == gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING:
        training_pipeline.training_task_metadata = {
            "backingCustomJob": _TEST_CUSTOM_JOB_RESOURCE_NAME
        }
    return training_pipeline


def make_training_pipeline_with_psc_interface_config(state):
    training_pipeline = gca_training_pipeline.TrainingPipeline(
        name=_TEST_PIPELINE_RESOURCE_NAME,
        state=state,
        training_task_inputs={
            "psc_interface_config": _TEST_PSC_INTERFACE_CONFIG,
        },
    )
    if state == gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING:
        training_pipeline.training_task_metadata = {
            "backingCustomJob": _TEST_CUSTOM_JOB_RESOURCE_NAME
        }
    return training_pipeline


@pytest.fixture
def mock_pipeline_service_get(make_call=make_training_pipeline):
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "get_training_pipeline"
    ) as mock_get_training_pipeline:
        mock_get_training_pipeline.side_effect = [
            make_call(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
                add_training_task_metadata=False,
            ),
            make_call(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
            ),
            make_call(gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
            make_call(gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
            make_call(gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
            make_call(gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
            make_call(gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
            make_call(gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
            make_call(gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
            make_call(gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
        ]

        yield mock_get_training_pipeline


@pytest.fixture
def mock_pipeline_service_get_with_enable_web_access():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "get_training_pipeline"
    ) as mock_get_training_pipeline:
        mock_get_training_pipeline.side_effect = [
            make_training_pipeline_with_enable_web_access(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_PENDING,
            ),
            make_training_pipeline_with_enable_web_access(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
            ),
            make_training_pipeline_with_enable_web_access(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
            ),
            make_training_pipeline_with_enable_web_access(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
            ),
            make_training_pipeline_with_enable_web_access(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            ),
            make_training_pipeline_with_enable_web_access(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            ),
        ]

        yield mock_get_training_pipeline


@pytest.fixture
def mock_pipeline_service_get_with_enable_dashboard_access():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "get_training_pipeline"
    ) as mock_get_training_pipeline:
        mock_get_training_pipeline.side_effect = [
            make_training_pipeline_with_enable_dashboard_access(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_PENDING,
            ),
            make_training_pipeline_with_enable_dashboard_access(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
            ),
            make_training_pipeline_with_enable_dashboard_access(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
            ),
            make_training_pipeline_with_enable_dashboard_access(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
            ),
            make_training_pipeline_with_enable_dashboard_access(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            ),
            make_training_pipeline_with_enable_dashboard_access(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            ),
        ]

        yield mock_get_training_pipeline


@pytest.fixture
def mock_pipeline_service_get_with_persistent_resource_id():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "get_training_pipeline"
    ) as mock_get_training_pipeline:
        mock_get_training_pipeline.side_effect = [
            make_training_pipeline_with_persistent_resource_id(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_PENDING,
            ),
            make_training_pipeline_with_persistent_resource_id(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
            ),
            make_training_pipeline_with_persistent_resource_id(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
            ),
            make_training_pipeline_with_persistent_resource_id(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
            ),
            make_training_pipeline_with_persistent_resource_id(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            ),
            make_training_pipeline_with_persistent_resource_id(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            ),
        ]

        yield mock_get_training_pipeline


@pytest.fixture
def mock_pipeline_service_get_with_scheduling():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "get_training_pipeline"
    ) as mock_get_training_pipeline:
        mock_get_training_pipeline.side_effect = [
            make_training_pipeline_with_scheduling(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_PENDING,
            ),
            make_training_pipeline_with_scheduling(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
            ),
            make_training_pipeline_with_scheduling(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
            ),
            make_training_pipeline_with_scheduling(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
            ),
            make_training_pipeline_with_scheduling(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            ),
            make_training_pipeline_with_scheduling(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            ),
        ]

        yield mock_get_training_pipeline


@pytest.fixture
def mock_pipeline_service_get_with_spot_strategy():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "get_training_pipeline"
    ) as mock_get_training_pipeline:
        mock_get_training_pipeline.side_effect = [
            make_training_pipeline_with_spot_strategy(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_PENDING,
            ),
            make_training_pipeline_with_spot_strategy(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
            ),
            make_training_pipeline_with_spot_strategy(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
            ),
            make_training_pipeline_with_spot_strategy(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
            ),
            make_training_pipeline_with_spot_strategy(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            ),
            make_training_pipeline_with_spot_strategy(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            ),
        ]

        yield mock_get_training_pipeline


@pytest.fixture
def mock_pipeline_service_get_with_psc_interface_config():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "get_training_pipeline"
    ) as mock_get_training_pipeline:
        mock_get_training_pipeline.side_effect = [
            make_training_pipeline_with_psc_interface_config(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_PENDING,
            ),
            make_training_pipeline_with_psc_interface_config(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
            ),
            make_training_pipeline_with_psc_interface_config(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
            ),
            make_training_pipeline_with_psc_interface_config(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
            ),
            make_training_pipeline_with_psc_interface_config(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            ),
            make_training_pipeline_with_psc_interface_config(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            ),
        ]

        yield mock_get_training_pipeline


@pytest.fixture
def mock_pipeline_service_cancel():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "cancel_training_pipeline"
    ) as mock_cancel_training_pipeline:
        yield mock_cancel_training_pipeline


@pytest.fixture
def mock_pipeline_service_create_with_no_model_to_upload():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_training_pipeline"
    ) as mock_create_training_pipeline:
        mock_create_training_pipeline.return_value = (
            gca_training_pipeline.TrainingPipeline(
                name=_TEST_PIPELINE_RESOURCE_NAME,
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            )
        )
        yield mock_create_training_pipeline


@pytest.fixture
def mock_pipeline_service_create_with_enable_web_access():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_training_pipeline"
    ) as mock_create_training_pipeline:
        mock_create_training_pipeline.return_value = (
            make_training_pipeline_with_enable_web_access(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_PENDING,
            )
        )
        yield mock_create_training_pipeline


@pytest.fixture
def mock_pipeline_service_create_with_enable_dashboard_access():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_training_pipeline"
    ) as mock_create_training_pipeline:
        mock_create_training_pipeline.return_value = (
            make_training_pipeline_with_enable_dashboard_access(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_PENDING,
            )
        )
        yield mock_create_training_pipeline


@pytest.fixture
def mock_pipeline_service_create_with_persistent_resource_id():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_training_pipeline"
    ) as mock_create_training_pipeline:
        mock_create_training_pipeline.return_value = (
            make_training_pipeline_with_persistent_resource_id(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_PENDING,
            )
        )
        yield mock_create_training_pipeline


@pytest.fixture
def mock_pipeline_service_create_with_scheduling():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_training_pipeline"
    ) as mock_create_training_pipeline:
        mock_create_training_pipeline.return_value = (
            make_training_pipeline_with_scheduling(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_PENDING,
            )
        )
        yield mock_create_training_pipeline


@pytest.fixture
def mock_pipeline_service_create_with_spot_strategy():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_training_pipeline"
    ) as mock_create_training_pipeline:
        mock_create_training_pipeline.return_value = (
            make_training_pipeline_with_spot_strategy(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_PENDING,
            )
        )
        yield mock_create_training_pipeline


@pytest.fixture
def mock_pipeline_service_create_with_psc_interface_config():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_training_pipeline"
    ) as mock_create_training_pipeline:
        mock_create_training_pipeline.return_value = (
            make_training_pipeline_with_psc_interface_config(
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_PENDING,
            )
        )
        yield mock_create_training_pipeline


@pytest.fixture
def mock_pipeline_service_get_with_no_model_to_upload():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "get_training_pipeline"
    ) as mock_get_training_pipeline:
        mock_get_training_pipeline.return_value = (
            gca_training_pipeline.TrainingPipeline(
                name=_TEST_PIPELINE_RESOURCE_NAME,
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            )
        )
        yield mock_get_training_pipeline


@pytest.fixture
def mock_pipeline_service_create_and_get_with_fail():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_training_pipeline"
    ) as mock_create_training_pipeline:
        mock_create_training_pipeline.return_value = (
            gca_training_pipeline.TrainingPipeline(
                name=_TEST_PIPELINE_RESOURCE_NAME,
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
            )
        )

        with mock.patch.object(
            pipeline_service_client.PipelineServiceClient, "get_training_pipeline"
        ) as mock_get_training_pipeline:
            mock_get_training_pipeline.return_value = (
                gca_training_pipeline.TrainingPipeline(
                    name=_TEST_PIPELINE_RESOURCE_NAME,
                    state=gca_pipeline_state.PipelineState.PIPELINE_STATE_FAILED,
                )
            )

            yield mock_create_training_pipeline, mock_get_training_pipeline


@pytest.fixture
def mock_model_service_get():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as mock_get_model:
        mock_get_model.return_value = gca_model.Model(name=_TEST_MODEL_NAME)
        mock_get_model.return_value.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.DEDICATED_RESOURCES
        )
        mock_get_model.return_value.version_id = "1"
        yield mock_get_model


@pytest.fixture
def mock_model_service_get_with_version():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as mock_get_model:
        mock_get_model.return_value = gca_model.Model(
            name=_TEST_MODEL_NAME, version_id=_TEST_MODEL_VERSION_ID
        )
        mock_get_model.return_value.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.DEDICATED_RESOURCES
        )
        yield mock_get_model


@pytest.fixture
def mock_python_package_to_gcs():
    with mock.patch.object(
        source_utils._TrainingScriptPythonPackager, "package_and_copy_to_gcs"
    ) as mock_package_to_copy_gcs:
        mock_package_to_copy_gcs.return_value = _TEST_OUTPUT_PYTHON_PACKAGE_PATH
        yield mock_package_to_copy_gcs


@pytest.fixture
def mock_tabular_dataset():
    ds = mock.MagicMock(datasets.TabularDataset)
    ds.name = _TEST_DATASET_NAME
    ds.metadata_schema_uri = _TEST_METADATA_SCHEMA_URI_TABULAR
    ds._latest_future = None
    ds._exception = None
    ds._gca_resource = gca_dataset.Dataset(
        display_name=_TEST_DATASET_DISPLAY_NAME,
        metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TABULAR,
        labels={},
        name=_TEST_DATASET_NAME,
        metadata={},
    )
    return ds


@pytest.fixture
def mock_nontabular_dataset():
    ds = mock.MagicMock(datasets.ImageDataset)
    ds.name = _TEST_DATASET_NAME
    ds.metadata_schema_uri = _TEST_METADATA_SCHEMA_URI_NONTABULAR
    ds._latest_future = None
    ds._exception = None
    ds._gca_resource = gca_dataset.Dataset(
        display_name=_TEST_DATASET_DISPLAY_NAME,
        metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_NONTABULAR,
        labels={},
        name=_TEST_DATASET_NAME,
        metadata={},
    )
    return ds


@pytest.mark.usefixtures("google_auth_mock")
class TestCustomTrainingJob:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        self._local_script_file_name = os.path.join(
            _TEST_TEMPDIR, f"{uuid.uuid4()}-{_TEST_LOCAL_SCRIPT_FILE_NAME}"
        )
        with open(self._local_script_file_name, "w") as fp:
            fp.write(_TEST_PYTHON_SOURCE)

    def teardown_method(self):
        pathlib.Path(self._local_script_file_name).unlink()
        initializer.global_pool.shutdown(wait=True)

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_tabular_dataset(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_python_package_to_gcs,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
            service_account=_TEST_SERVICE_ACCOUNT,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
            explanation_metadata=_TEST_EXPLANATION_METADATA,
            explanation_parameters=_TEST_EXPLANATION_PARAMETERS,
        )

        model_from_job = job.run(
            dataset=mock_tabular_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            network=_TEST_NETWORK,
            args=_TEST_RUN_ARGS,
            environment_variables=_TEST_ENVIRONMENT_VARIABLES,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            model_labels=_TEST_MODEL_LABELS,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            timestamp_split_column_name=_TEST_TIMESTAMP_SPLIT_COLUMN_NAME,
            tensorboard=_TEST_TENSORBOARD_RESOURCE_NAME,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            model_from_job.wait()

        mock_python_package_to_gcs.assert_called_once_with(
            gcs_staging_dir=_TEST_BUCKET_NAME,
            project=_TEST_PROJECT,
            credentials=initializer.global_config.credentials,
        )

        true_args = _TEST_RUN_ARGS
        true_env = [
            {"name": key, "value": value}
            for key, value in _TEST_ENVIRONMENT_VARIABLES.items()
        ]

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": _TEST_ACCELERATOR_COUNT,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "python_package_spec": {
                "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                "python_module": _TEST_MODULE_NAME,
                "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                "args": true_args,
                "env": true_env,
            },
        }

        true_timestamp_split = gca_training_pipeline.TimestampSplit(
            training_fraction=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction=_TEST_TEST_FRACTION_SPLIT,
            key=_TEST_TIMESTAMP_SPLIT_COLUMN_NAME,
        )

        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
            for key, value in _TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
        ]

        ports = [
            gca_model.Port(container_port=port)
            for port in _TEST_MODEL_SERVING_CONTAINER_PORTS
        ]

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            env=env,
            ports=ports,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            labels=_TEST_MODEL_LABELS,
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            explanation_spec=gca_model.explanation.ExplanationSpec(
                metadata=_TEST_EXPLANATION_METADATA,
                parameters=_TEST_EXPLANATION_PARAMETERS,
            ),
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            timestamp_split=true_timestamp_split,
            dataset_id=mock_tabular_dataset.name,
            gcs_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_BASE_OUTPUT_DIR
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                    "service_account": _TEST_SERVICE_ACCOUNT,
                    "network": _TEST_NETWORK,
                    "tensorboard": _TEST_TENSORBOARD_RESOURCE_NAME,
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            labels=_TEST_LABELS,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        assert job._gca_resource == make_training_pipeline(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        mock_model_service_get.assert_called_once_with(
            name=_TEST_MODEL_NAME, retry=base._DEFAULT_RETRY
        )

        assert model_from_job._gca_resource is mock_model_service_get.return_value

        assert job.get_model()._gca_resource is mock_model_service_get.return_value

        assert not job.has_failed

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

        assert job._has_logged_custom_job

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    def test_custom_training_job_run_raises_with_impartial_explanation_spec(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_python_package_to_gcs,
        mock_tabular_dataset,
        mock_model_service_get,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
            explanation_metadata=_TEST_EXPLANATION_METADATA,
            # Missing the required explanations_parameters field
        )

        with pytest.raises(ValueError) as e:
            job.run(
                dataset=mock_tabular_dataset,
                base_output_dir=_TEST_BASE_OUTPUT_DIR,
                service_account=_TEST_SERVICE_ACCOUNT,
                network=_TEST_NETWORK,
                args=_TEST_RUN_ARGS,
                environment_variables=_TEST_ENVIRONMENT_VARIABLES,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                model_labels=_TEST_MODEL_LABELS,
                training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
                validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
                test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
                timestamp_split_column_name=_TEST_TIMESTAMP_SPLIT_COLUMN_NAME,
                tensorboard=_TEST_TENSORBOARD_RESOURCE_NAME,
                sync=False,
                create_request_timeout=None,
            )

        assert e.match(
            regexp=r"To get model explanation, `explanation_parameters` "
            "must be specified."
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    def test_custom_training_tabular_done(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_python_package_to_gcs,
        mock_tabular_dataset,
        mock_model_service_get,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
        )

        job.run(
            dataset=mock_tabular_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            args=_TEST_RUN_ARGS,
            environment_variables=_TEST_ENVIRONMENT_VARIABLES,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            model_labels=_TEST_MODEL_LABELS,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            timestamp_split_column_name=_TEST_TIMESTAMP_SPLIT_COLUMN_NAME,
            tensorboard=_TEST_TENSORBOARD_RESOURCE_NAME,
            sync=False,
            create_request_timeout=None,
        )

        assert job.done() is False

        job.wait()

        assert job.done() is True

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_tabular_dataset_and_timeout(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_python_package_to_gcs,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
        )

        model_from_job = job.run(
            dataset=mock_tabular_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            args=_TEST_RUN_ARGS,
            environment_variables=_TEST_ENVIRONMENT_VARIABLES,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            model_labels=_TEST_MODEL_LABELS,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            timestamp_split_column_name=_TEST_TIMESTAMP_SPLIT_COLUMN_NAME,
            tensorboard=_TEST_TENSORBOARD_RESOURCE_NAME,
            sync=sync,
            create_request_timeout=180.0,
        )

        if not sync:
            model_from_job.wait()

        true_args = _TEST_RUN_ARGS
        true_env = [
            {"name": key, "value": value}
            for key, value in _TEST_ENVIRONMENT_VARIABLES.items()
        ]

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": _TEST_ACCELERATOR_COUNT,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "python_package_spec": {
                "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                "python_module": _TEST_MODULE_NAME,
                "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                "args": true_args,
                "env": true_env,
            },
        }

        true_timestamp_split = gca_training_pipeline.TimestampSplit(
            training_fraction=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction=_TEST_TEST_FRACTION_SPLIT,
            key=_TEST_TIMESTAMP_SPLIT_COLUMN_NAME,
        )

        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
            for key, value in _TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
        ]

        ports = [
            gca_model.Port(container_port=port)
            for port in _TEST_MODEL_SERVING_CONTAINER_PORTS
        ]

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            env=env,
            ports=ports,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            labels=_TEST_MODEL_LABELS,
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            timestamp_split=true_timestamp_split,
            dataset_id=mock_tabular_dataset.name,
            gcs_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_BASE_OUTPUT_DIR
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                    "service_account": _TEST_SERVICE_ACCOUNT,
                    "network": _TEST_NETWORK,
                    "tensorboard": _TEST_TENSORBOARD_RESOURCE_NAME,
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            labels=_TEST_LABELS,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=180.0,
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_tabular_dataset_and_timeout_not_explicitly_set(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_python_package_to_gcs,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
        )

        model_from_job = job.run(
            dataset=mock_tabular_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            args=_TEST_RUN_ARGS,
            environment_variables=_TEST_ENVIRONMENT_VARIABLES,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            model_labels=_TEST_MODEL_LABELS,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            timestamp_split_column_name=_TEST_TIMESTAMP_SPLIT_COLUMN_NAME,
            tensorboard=_TEST_TENSORBOARD_RESOURCE_NAME,
            sync=sync,
        )

        if not sync:
            model_from_job.wait()

        true_args = _TEST_RUN_ARGS
        true_env = [
            {"name": key, "value": value}
            for key, value in _TEST_ENVIRONMENT_VARIABLES.items()
        ]

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": _TEST_ACCELERATOR_COUNT,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "python_package_spec": {
                "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                "python_module": _TEST_MODULE_NAME,
                "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                "args": true_args,
                "env": true_env,
            },
        }

        true_timestamp_split = gca_training_pipeline.TimestampSplit(
            training_fraction=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction=_TEST_TEST_FRACTION_SPLIT,
            key=_TEST_TIMESTAMP_SPLIT_COLUMN_NAME,
        )

        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
            for key, value in _TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
        ]

        ports = [
            gca_model.Port(container_port=port)
            for port in _TEST_MODEL_SERVING_CONTAINER_PORTS
        ]

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            env=env,
            ports=ports,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            labels=_TEST_MODEL_LABELS,
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            timestamp_split=true_timestamp_split,
            dataset_id=mock_tabular_dataset.name,
            gcs_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_BASE_OUTPUT_DIR
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                    "service_account": _TEST_SERVICE_ACCOUNT,
                    "network": _TEST_NETWORK,
                    "tensorboard": _TEST_TENSORBOARD_RESOURCE_NAME,
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            labels=_TEST_LABELS,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_bigquery_destination(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_python_package_to_gcs,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
        )

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
            training_encryption_spec_key_name=_TEST_PIPELINE_ENCRYPTION_KEY_NAME,
            model_encryption_spec_key_name=_TEST_MODEL_ENCRYPTION_KEY_NAME,
        )

        model_from_job = job.run(
            dataset=mock_tabular_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            bigquery_destination=_TEST_BIGQUERY_DESTINATION,
            args=_TEST_RUN_ARGS,
            environment_variables=_TEST_ENVIRONMENT_VARIABLES,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            predefined_split_column_name=_TEST_PREDEFINED_SPLIT_COLUMN_NAME,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            model_from_job.wait()

        true_args = _TEST_RUN_ARGS
        true_env = [
            {"name": key, "value": value}
            for key, value in _TEST_ENVIRONMENT_VARIABLES.items()
        ]

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": _TEST_ACCELERATOR_COUNT,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "python_package_spec": {
                "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                "python_module": _TEST_MODULE_NAME,
                "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                "args": true_args,
                "env": true_env,
            },
        }

        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
            for key, value in _TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
        ]

        ports = [
            gca_model.Port(container_port=port)
            for port in _TEST_MODEL_SERVING_CONTAINER_PORTS
        ]

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            env=env,
            ports=ports,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            encryption_spec=_TEST_MODEL_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            predefined_split=gca_training_pipeline.PredefinedSplit(
                key=_TEST_PREDEFINED_SPLIT_COLUMN_NAME
            ),
            dataset_id=mock_tabular_dataset.name,
            bigquery_destination=gca_io.BigQueryDestination(
                output_uri=_TEST_BIGQUERY_DESTINATION
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_PIPELINE_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        assert job._gca_resource == make_training_pipeline(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        mock_model_service_get.assert_called_once_with(
            name=_TEST_MODEL_NAME, retry=base._DEFAULT_RETRY
        )

        assert model_from_job._gca_resource is mock_model_service_get.return_value

        assert job.get_model()._gca_resource is mock_model_service_get.return_value

        assert not job.has_failed

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_pipeline_service_get",
        "mock_python_package_to_gcs",
        "mock_model_service_get",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_called_twice_raises(
        self,
        mock_tabular_dataset,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        job.run(
            dataset=mock_tabular_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            replica_count=1,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            sync=sync,
            create_request_timeout=None,
        )

        with pytest.raises(RuntimeError):
            job.run(
                dataset=mock_tabular_dataset,
                base_output_dir=_TEST_BASE_OUTPUT_DIR,
                args=_TEST_RUN_ARGS,
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
                validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
                test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
                sync=sync,
                create_request_timeout=None,
            )

        if not sync:
            job.wait()

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_with_invalid_accelerator_type_raises(
        self,
        mock_pipeline_service_create,
        mock_python_package_to_gcs,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        with pytest.raises(ValueError):
            job.run(
                dataset=mock_tabular_dataset,
                base_output_dir=_TEST_BASE_OUTPUT_DIR,
                args=_TEST_RUN_ARGS,
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_INVALID_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                sync=sync,
                create_request_timeout=None,
            )

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_with_two_splits_raises(
        self,
        mock_pipeline_service_create,
        mock_python_package_to_gcs,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        with pytest.raises(ValueError):
            job.run(
                dataset=mock_tabular_dataset,
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_INVALID_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                predefined_split_column_name=_TEST_PREDEFINED_SPLIT_COLUMN_NAME,
                training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
                validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
                test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
                sync=sync,
                create_request_timeout=None,
            )

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_with_incomplete_model_info_raises_with_model_to_upload(
        self,
        mock_pipeline_service_create,
        mock_python_package_to_gcs,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        with pytest.raises(RuntimeError):
            job.run(
                dataset=mock_tabular_dataset,
                base_output_dir=_TEST_BASE_OUTPUT_DIR,
                args=_TEST_RUN_ARGS,
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
                validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
                test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
                sync=sync,
                create_request_timeout=None,
            )

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_no_dataset(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_python_package_to_gcs,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        model_from_job = job.run(
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            environment_variables=_TEST_ENVIRONMENT_VARIABLES,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            training_filter_split=_TEST_TRAINING_FILTER_SPLIT,
            validation_filter_split=_TEST_VALIDATION_FILTER_SPLIT,
            test_filter_split=_TEST_TEST_FILTER_SPLIT,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            model_from_job.wait()

        mock_python_package_to_gcs.assert_called_once_with(
            gcs_staging_dir=_TEST_BUCKET_NAME,
            project=_TEST_PROJECT,
            credentials=initializer.global_config.credentials,
        )

        true_args = _TEST_RUN_ARGS
        true_env = [
            {"name": key, "value": value}
            for key, value in _TEST_ENVIRONMENT_VARIABLES.items()
        ]

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": _TEST_ACCELERATOR_COUNT,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "python_package_spec": {
                "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                "python_module": _TEST_MODULE_NAME,
                "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                "args": true_args,
                "env": true_env,
            },
        }

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            container_spec=true_container_spec,
            version_aliases=["default"],
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        assert job._gca_resource == make_training_pipeline(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        mock_model_service_get.assert_called_once_with(
            name=_TEST_MODEL_NAME, retry=base._DEFAULT_RETRY
        )

        assert model_from_job._gca_resource is mock_model_service_get.return_value

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create_with_enable_web_access",
        "mock_pipeline_service_get_with_enable_web_access",
        "mock_get_backing_custom_job_with_enable_web_access",
        "mock_python_package_to_gcs",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_enable_web_access(
        self, sync, caplog
    ):

        caplog.set_level(logging.INFO)

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        job.run(
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            enable_web_access=_TEST_ENABLE_WEB_ACCESS,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            job.wait()

        print(caplog.text)
        # TODO: b/383923584: Re-enable this test once the parent issue is fixed
        # assert "workerpool0-0" in caplog.text
        assert job._gca_resource == make_training_pipeline_with_enable_web_access(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

    # TODO: Update test to address Mutant issue b/270708320
    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create_with_enable_dashboard_access",
        "mock_pipeline_service_get_with_enable_dashboard_access",
        "mock_get_backing_custom_job_with_enable_dashboard_access",
        "mock_python_package_to_gcs",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_enable_dashboard_access(
        self, sync, caplog
    ):

        caplog.set_level(logging.INFO)

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        job.run(
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            enable_dashboard_access=_TEST_ENABLE_DASHBOARD_ACCESS,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            job.wait()

        print(caplog.text)
        # TODO: b/383923584: Re-enable this test once the parent issue is fixed
        # assert "workerpool0-0:8888" in caplog.text
        assert job._gca_resource == make_training_pipeline_with_enable_dashboard_access(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create_with_scheduling",
        "mock_pipeline_service_get_with_scheduling",
        "mock_python_package_to_gcs",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_scheduling(self, sync, caplog):

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        job.run(
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            sync=sync,
            create_request_timeout=None,
            disable_retries=_TEST_DISABLE_RETRIES,
            max_wait_duration=_TEST_MAX_WAIT_DURATION,
        )

        if not sync:
            job.wait()

        assert job._gca_resource == make_training_pipeline_with_scheduling(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        assert (
            job._gca_resource.state
            == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )
        assert job._gca_resource.training_task_inputs["timeout"] == f"{_TEST_TIMEOUT}s"
        assert (
            job._gca_resource.training_task_inputs["restart_job_on_worker_restart"]
            == _TEST_RESTART_JOB_ON_WORKER_RESTART
        )
        assert (
            job._gca_resource.training_task_inputs["disable_retries"]
            == _TEST_DISABLE_RETRIES
        )
        assert (
            job._gca_resource.training_task_inputs["max_wait_duration"]
            == f"{_TEST_MAX_WAIT_DURATION}s"
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create_with_spot_strategy",
        "mock_pipeline_service_get_with_spot_strategy",
        "mock_python_package_to_gcs",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_spot_strategy(self, sync):

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        job.run(
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            sync=sync,
            create_request_timeout=None,
            disable_retries=_TEST_DISABLE_RETRIES,
        )

        if not sync:
            job.wait()

        assert job._gca_resource == make_training_pipeline_with_spot_strategy(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        assert (
            job._gca_resource.state
            == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        assert (
            job._gca_resource.training_task_inputs["scheduling_strategy"]
            == _TEST_SPOT_STRATEGY
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create_with_psc_interface_config",
        "mock_pipeline_service_get_with_psc_interface_config",
        "mock_python_package_to_gcs",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_psc_interface_config(self, sync):

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        job.run(
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            sync=sync,
            create_request_timeout=None,
            disable_retries=_TEST_DISABLE_RETRIES,
            psc_interface_config=_TEST_PSC_INTERFACE_CONFIG,
        )

        if not sync:
            job.wait()

        assert job._gca_resource == make_training_pipeline_with_psc_interface_config(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        assert (
            job._gca_resource.state
            == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        assert (
            job._gca_resource.training_task_inputs["psc_interface_config"]
            == _TEST_PSC_INTERFACE_CONFIG
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create_with_no_model_to_upload",
        "mock_pipeline_service_get_with_no_model_to_upload",
        "mock_python_package_to_gcs",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_returns_none_if_no_model_to_upload(
        self,
        mock_tabular_dataset,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        model = job.run(
            dataset=mock_tabular_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            replica_count=1,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            sync=sync,
            create_request_timeout=None,
        )

        assert model is None

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create_with_no_model_to_upload",
        "mock_pipeline_service_get_with_no_model_to_upload",
        "mock_python_package_to_gcs",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_get_model_raises_if_no_model_to_upload(
        self,
        mock_tabular_dataset,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        job.run(
            dataset=mock_tabular_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            replica_count=1,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            job.wait()

        with pytest.raises(RuntimeError):
            job.get_model()

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_raises_if_pipeline_fails(
        self,
        mock_pipeline_service_create_and_get_with_fail,
        mock_python_package_to_gcs,
        mock_tabular_dataset,
        sync,
    ):

        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        with pytest.raises(RuntimeError):
            job.run(
                dataset=mock_tabular_dataset,
                base_output_dir=_TEST_BASE_OUTPUT_DIR,
                args=_TEST_RUN_ARGS,
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
                validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
                test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
                sync=sync,
                create_request_timeout=None,
            )

            if not sync:
                job.wait()

        with pytest.raises(RuntimeError):
            job.get_model()

    def test_raises_before_run_is_called(
        self, mock_pipeline_service_create, mock_python_package_to_gcs
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        with pytest.raises(RuntimeError):
            job.get_model()

        with pytest.raises(RuntimeError):
            job.has_failed

        with pytest.raises(RuntimeError):
            job.state

    def test_run_raises_if_no_staging_bucket(self):

        aiplatform.init(project=_TEST_PROJECT)

        with pytest.raises(RuntimeError):
            training_jobs.CustomTrainingJob(
                display_name=_TEST_DISPLAY_NAME,
                script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
                container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_distributed_training(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_python_package_to_gcs,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
        )

        model_from_job = job.run(
            dataset=mock_tabular_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            environment_variables=_TEST_ENVIRONMENT_VARIABLES,
            replica_count=10,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            model_from_job.wait()

        mock_python_package_to_gcs.assert_called_once_with(
            gcs_staging_dir=_TEST_BUCKET_NAME,
            project=_TEST_PROJECT,
            credentials=initializer.global_config.credentials,
        )

        true_args = _TEST_RUN_ARGS
        true_env = [
            {"name": key, "value": value}
            for key, value in _TEST_ENVIRONMENT_VARIABLES.items()
        ]

        true_worker_pool_spec = [
            {
                "replica_count": 1,
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                },
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
                "python_package_spec": {
                    "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                    "python_module": _TEST_MODULE_NAME,
                    "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                    "args": true_args,
                    "env": true_env,
                },
            },
            {
                "replica_count": 9,
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                },
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
                "python_package_spec": {
                    "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                    "python_module": _TEST_MODULE_NAME,
                    "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                    "args": true_args,
                    "env": true_env,
                },
            },
        ]

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            dataset_id=mock_tabular_dataset.name,
            gcs_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_BASE_OUTPUT_DIR
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": true_worker_pool_spec,
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        assert job._gca_resource == make_training_pipeline(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        mock_model_service_get.assert_called_once_with(
            name=_TEST_MODEL_NAME, retry=base._DEFAULT_RETRY
        )

        assert model_from_job._gca_resource is mock_model_service_get.return_value

        assert job.get_model()._gca_resource is mock_model_service_get.return_value

        assert not job.has_failed

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_distributed_training_with_reduction_server(
        self,
        mock_pipeline_service_create_with_no_model_to_upload,
        mock_pipeline_service_get_with_no_model_to_upload,
        mock_python_package_to_gcs,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        job.run(
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            environment_variables=_TEST_ENVIRONMENT_VARIABLES,
            replica_count=10,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            reduction_server_replica_count=_TEST_REDUCTION_SERVER_REPLICA_COUNT,
            reduction_server_machine_type=_TEST_REDUCTION_SERVER_MACHINE_TYPE,
            reduction_server_container_uri=_TEST_REDUCTION_SERVER_CONTAINER_URI,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            job.wait()

        mock_python_package_to_gcs.assert_called_once_with(
            gcs_staging_dir=_TEST_BUCKET_NAME,
            project=_TEST_PROJECT,
            credentials=initializer.global_config.credentials,
        )

        true_args = _TEST_RUN_ARGS
        true_env = [
            {"name": key, "value": value}
            for key, value in _TEST_ENVIRONMENT_VARIABLES.items()
        ]

        true_worker_pool_spec = [
            {
                "replica_count": 1,
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                },
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
                "python_package_spec": {
                    "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                    "python_module": _TEST_MODULE_NAME,
                    "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                    "args": true_args,
                    "env": true_env,
                },
            },
            {
                "replica_count": 9,
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                },
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
                "python_package_spec": {
                    "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                    "python_module": _TEST_MODULE_NAME,
                    "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                    "args": true_args,
                    "env": true_env,
                },
            },
            {
                "replica_count": _TEST_REDUCTION_SERVER_REPLICA_COUNT,
                "machine_spec": {"machine_type": _TEST_REDUCTION_SERVER_MACHINE_TYPE},
                "container_spec": {"image_uri": _TEST_REDUCTION_SERVER_CONTAINER_URI},
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
            },
        ]

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": true_worker_pool_spec,
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
        )

        mock_pipeline_service_create_with_no_model_to_upload.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        assert job._gca_resource == make_training_pipeline_with_no_model_upload(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        assert not job.has_failed

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

    @pytest.mark.usefixtures("get_training_job_custom_mock")
    def test_get_training_job(self, get_training_job_custom_mock):
        aiplatform.init(project=_TEST_PROJECT)
        job = training_jobs.CustomTrainingJob.get(resource_name=_TEST_NAME)

        get_training_job_custom_mock.assert_called_once_with(
            name=_TEST_NAME, retry=base._DEFAULT_RETRY
        )
        assert isinstance(job, training_jobs.CustomTrainingJob)

    @pytest.mark.usefixtures("get_training_job_custom_mock")
    def test_get_training_job_wrong_job_type(self, get_training_job_custom_mock):
        aiplatform.init(project=_TEST_PROJECT)

        # The returned job is for a custom training task,
        # but the calling type if of AutoMLImageTrainingJob.
        # Hence, it should throw an error.
        with pytest.raises(ValueError):
            training_jobs.AutoMLImageTrainingJob.get(resource_name=_TEST_NAME)

    @pytest.mark.usefixtures("get_training_job_custom_mock_no_model_to_upload")
    def test_get_training_job_no_model_to_upload(
        self, get_training_job_custom_mock_no_model_to_upload
    ):
        aiplatform.init(project=_TEST_PROJECT)

        job = training_jobs.CustomTrainingJob.get(resource_name=_TEST_NAME)

        with pytest.raises(RuntimeError):
            job.get_model(sync=False)

    @pytest.mark.usefixtures("get_training_job_tabular_mock")
    def test_get_training_job_tabular(self, get_training_job_tabular_mock):
        aiplatform.init(project=_TEST_PROJECT)

        with pytest.raises(ValueError):
            training_jobs.CustomTrainingJob.get(resource_name=_TEST_NAME)

    @pytest.mark.usefixtures("get_training_job_custom_mock")
    def test_get_training_job_with_id_only(self, get_training_job_custom_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        training_jobs.CustomTrainingJob.get(resource_name=_TEST_ID)
        get_training_job_custom_mock.assert_called_once_with(
            name=_TEST_NAME, retry=base._DEFAULT_RETRY
        )

    def test_get_training_job_with_id_only_with_project_and_location(
        self, get_training_job_custom_mock
    ):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        training_jobs.CustomTrainingJob.get(
            resource_name=_TEST_ID, project=_TEST_PROJECT, location=_TEST_LOCATION
        )
        get_training_job_custom_mock.assert_called_once_with(
            name=_TEST_NAME, retry=base._DEFAULT_RETRY
        )

    def test_get_training_job_with_project_and_location(
        self, get_training_job_custom_mock
    ):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        training_jobs.CustomTrainingJob.get(
            resource_name=_TEST_NAME, project=_TEST_PROJECT, location=_TEST_LOCATION
        )
        get_training_job_custom_mock.assert_called_once_with(
            name=_TEST_NAME, retry=base._DEFAULT_RETRY
        )

    def test_get_training_job_with_alt_project_and_location(
        self, get_training_job_custom_mock
    ):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        training_jobs.CustomTrainingJob.get(
            resource_name=_TEST_NAME, project=_TEST_ALT_PROJECT, location=_TEST_LOCATION
        )
        get_training_job_custom_mock.assert_called_once_with(
            name=_TEST_NAME, retry=base._DEFAULT_RETRY
        )

    def test_get_training_job_with_project_and_alt_location(self):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with pytest.raises(RuntimeError):
            training_jobs.CustomTrainingJob.get(
                resource_name=_TEST_NAME,
                project=_TEST_PROJECT,
                location=_TEST_ALT_LOCATION,
            )

    def test_unique_supported_training_schemas(self):
        """Ensure that the `_supported_training_schemas` across AutoML training
        classes and CustomTrainingJob contain unique values."""

        schemas = [
            schema
            for c in aiplatform.training_jobs._TrainingJob.__subclasses__()
            for schema in c._supported_training_schemas
            if c.__name__.startswith("AutoML")
        ]

        schemas.extend(
            aiplatform.training_jobs.CustomTrainingJob._supported_training_schemas
        )

        # Ensure all schemas across classes are unique
        assert len(set(schemas)) == len(schemas)

    @pytest.mark.usefixtures("get_training_job_tabular_mock")
    def test_get_and_return_subclass_automl(self):
        subcls = aiplatform.training_jobs._TrainingJob._get_and_return_subclass(
            resource_name=_TEST_PIPELINE_RESOURCE_NAME
        )

        assert isinstance(subcls, aiplatform.training_jobs.AutoMLTabularTrainingJob)

    @pytest.mark.usefixtures("get_training_job_custom_mock")
    def test_get_and_return_subclass_custom(self):
        subcls = aiplatform.training_jobs._TrainingJob._get_and_return_subclass(
            resource_name=_TEST_PIPELINE_RESOURCE_NAME
        )

        assert isinstance(subcls, aiplatform.training_jobs.CustomTrainingJob)

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_nontabular_dataset_without_model_display_name_nor_model_labels(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_python_package_to_gcs,
        mock_nontabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
        )

        model_from_job = job.run(
            dataset=mock_nontabular_dataset,
            annotation_schema_uri=_TEST_ANNOTATION_SCHEMA_URI,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            training_filter_split=_TEST_TRAINING_FILTER_SPLIT,
            validation_filter_split=_TEST_VALIDATION_FILTER_SPLIT,
            test_filter_split=_TEST_TEST_FILTER_SPLIT,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            model_from_job.wait()

        mock_python_package_to_gcs.assert_called_once_with(
            gcs_staging_dir=_TEST_BUCKET_NAME,
            project=_TEST_PROJECT,
            credentials=initializer.global_config.credentials,
        )

        true_args = _TEST_RUN_ARGS

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": _TEST_ACCELERATOR_COUNT,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "python_package_spec": {
                "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                "python_module": _TEST_MODULE_NAME,
                "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                "args": true_args,
            },
        }

        true_filter_split = gca_training_pipeline.FilterSplit(
            training_filter=_TEST_TRAINING_FILTER_SPLIT,
            validation_filter=_TEST_VALIDATION_FILTER_SPLIT,
            test_filter=_TEST_TEST_FILTER_SPLIT,
        )

        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
            for key, value in _TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
        ]

        ports = [
            gca_model.Port(container_port=port)
            for port in _TEST_MODEL_SERVING_CONTAINER_PORTS
        ]

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            env=env,
            ports=ports,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_DISPLAY_NAME + "-model",
            labels=_TEST_LABELS,
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            filter_split=true_filter_split,
            dataset_id=mock_nontabular_dataset.name,
            annotation_schema_uri=_TEST_ANNOTATION_SCHEMA_URI,
            gcs_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_BASE_OUTPUT_DIR
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        assert job._gca_resource == make_training_pipeline(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        mock_model_service_get.assert_called_once_with(
            name=_TEST_MODEL_NAME, retry=base._DEFAULT_RETRY
        )

        assert model_from_job._gca_resource is mock_model_service_get.return_value

        assert job.get_model()._gca_resource is mock_model_service_get.return_value

        assert not job.has_failed

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

    def test_run_call_pipeline_service_create_with_nontabular_dataset_raises_if_annotation_schema_uri(
        self,
        mock_nontabular_dataset,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
        )

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
        )

        with pytest.raises(Exception):
            job.run(
                dataset=mock_nontabular_dataset,
                base_output_dir=_TEST_BASE_OUTPUT_DIR,
                args=_TEST_RUN_ARGS,
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                create_request_timeout=None,
            )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_pipeline_service_get",
        "mock_python_package_to_gcs",
        "mock_model_service_get",
    )
    def test_cancel_training_job(self, mock_pipeline_service_cancel):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
        )

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        job.run()
        job.cancel()

        mock_pipeline_service_cancel.assert_called_once_with(
            name=_TEST_PIPELINE_RESOURCE_NAME
        )

    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_python_package_to_gcs",
        "mock_model_service_get",
    )
    def test_cancel_training_job_without_running(self, mock_pipeline_service_cancel):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
        )

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        with pytest.raises(RuntimeError) as e:
            job.cancel()

        assert e.match(regexp=r"TrainingJob has not been launched")

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create_with_persistent_resource_id",
        "mock_pipeline_service_get_with_persistent_resource_id",
        "mock_get_backing_custom_job_with_persistent_resource_id",
        "mock_python_package_to_gcs",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_persistent_resource_id(
        self, sync, caplog
    ):

        caplog.set_level(logging.INFO)

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        job.run(
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            sync=sync,
            create_request_timeout=None,
            persistent_resource_id=_TEST_PERSISTENT_RESOURCE_ID,
        )

        if not sync:
            job.wait()

        assert job._gca_resource == make_training_pipeline_with_persistent_resource_id(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_pipeline_service_get",
        "mock_python_package_to_gcs",
        "mock_model_service_get",
    )
    def test_training_job_tpu_v5e(self, mock_pipeline_service_create):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_description=_TEST_MODEL_DESCRIPTION,
        )

        job.run(
            machine_type=_TEST_MACHINE_TYPE_TPU_V5E,
            tpu_topology="2x2",
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
        )

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_DISPLAY_NAME + "-model",
            labels=_TEST_LABELS,
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            version_aliases=["default"],
        )

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE_TPU_V5E,
                "tpu_topology": "2x2",
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "python_package_spec": {
                "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                "python_module": _TEST_MODULE_NAME,
                "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
            },
        }

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_pipeline_service_get",
        "mock_python_package_to_gcs",
        "mock_model_service_get",
    )
    def test_training_job_tpu_v3_pod(self, mock_pipeline_service_create):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_description=_TEST_MODEL_DESCRIPTION,
        )

        job.run(
            machine_type=_TEST_MACHINE_TYPE_TPU,
            accelerator_type=_TEST_ACCELERATOR_TPU_TYPE,
            accelerator_count=32,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
        )

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_DISPLAY_NAME + "-model",
            labels=_TEST_LABELS,
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            version_aliases=["default"],
        )

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE_TPU,
                "accelerator_type": _TEST_ACCELERATOR_TPU_TYPE,
                "accelerator_count": 32,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "python_package_spec": {
                "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                "python_module": _TEST_MODULE_NAME,
                "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
            },
        }

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_pipeline_service_get",
        "mock_python_package_to_gcs",
        "mock_model_service_get",
    )
    def test_training_job_reservation_affinity(self, mock_pipeline_service_create):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_description=_TEST_MODEL_DESCRIPTION,
        )

        job.run(
            machine_type=_TEST_MACHINE_TYPE,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            reservation_affinity_type="ANY_RESERVATION",
        )

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_DISPLAY_NAME + "-model",
            labels=_TEST_LABELS,
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            version_aliases=["default"],
        )

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "reservation_affinity": {
                    "reservation_affinity_type": "ANY_RESERVATION"
                },
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "python_package_spec": {
                "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                "python_module": _TEST_MODULE_NAME,
                "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
            },
        }

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )


@pytest.mark.usefixtures("google_auth_mock")
class TestCustomContainerTrainingJob:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    def test_custom_container_training_tabular_done(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_tabular_dataset,
        mock_model_service_get,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
        )

        job.run(
            dataset=mock_tabular_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            environment_variables=_TEST_ENVIRONMENT_VARIABLES,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            model_labels=_TEST_MODEL_LABELS,
            predefined_split_column_name=_TEST_PREDEFINED_SPLIT_COLUMN_NAME,
            service_account=_TEST_SERVICE_ACCOUNT,
            tensorboard=_TEST_TENSORBOARD_RESOURCE_NAME,
            sync=False,
            create_request_timeout=None,
        )

        assert job.done() is False

        job.wait()

        assert job.done() is True

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_tabular_dataset(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            service_account=_TEST_SERVICE_ACCOUNT,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
            explanation_metadata=_TEST_EXPLANATION_METADATA,
            explanation_parameters=_TEST_EXPLANATION_PARAMETERS,
        )

        model_from_job = job.run(
            dataset=mock_tabular_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            environment_variables=_TEST_ENVIRONMENT_VARIABLES,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            model_labels=_TEST_MODEL_LABELS,
            predefined_split_column_name=_TEST_PREDEFINED_SPLIT_COLUMN_NAME,
            tensorboard=_TEST_TENSORBOARD_RESOURCE_NAME,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            model_from_job.wait()

        true_args = _TEST_RUN_ARGS
        true_env = [
            {"name": key, "value": value}
            for key, value in _TEST_ENVIRONMENT_VARIABLES.items()
        ]

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": _TEST_ACCELERATOR_COUNT,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "containerSpec": {
                "imageUri": _TEST_TRAINING_CONTAINER_IMAGE,
                "command": _TEST_TRAINING_CONTAINER_CMD,
                "args": true_args,
                "env": true_env,
            },
        }

        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
            for key, value in _TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
        ]

        ports = [
            gca_model.Port(container_port=port)
            for port in _TEST_MODEL_SERVING_CONTAINER_PORTS
        ]

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            env=env,
            ports=ports,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            labels=_TEST_MODEL_LABELS,
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            explanation_spec=gca_model.explanation.ExplanationSpec(
                metadata=_TEST_EXPLANATION_METADATA,
                parameters=_TEST_EXPLANATION_PARAMETERS,
            ),
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            predefined_split=gca_training_pipeline.PredefinedSplit(
                key=_TEST_PREDEFINED_SPLIT_COLUMN_NAME
            ),
            dataset_id=mock_tabular_dataset.name,
            gcs_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_BASE_OUTPUT_DIR
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                    "service_account": _TEST_SERVICE_ACCOUNT,
                    "tensorboard": _TEST_TENSORBOARD_RESOURCE_NAME,
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        assert job._gca_resource == make_training_pipeline(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        mock_model_service_get.assert_called_once_with(
            name=_TEST_MODEL_NAME, retry=base._DEFAULT_RETRY
        )

        assert model_from_job._gca_resource is mock_model_service_get.return_value

        assert job.get_model()._gca_resource is mock_model_service_get.return_value

        assert not job.has_failed

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

        assert job._has_logged_custom_job

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    def test_custom_container_training_job_run_raises_with_impartial_explanation_spec(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_tabular_dataset,
        mock_model_service_get,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
            explanation_metadata=_TEST_EXPLANATION_METADATA,
            # Missing the required explanations_parameters field
        )

        with pytest.raises(ValueError) as e:
            job.run(
                dataset=mock_tabular_dataset,
                base_output_dir=_TEST_BASE_OUTPUT_DIR,
                args=_TEST_RUN_ARGS,
                environment_variables=_TEST_ENVIRONMENT_VARIABLES,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                model_labels=_TEST_MODEL_LABELS,
                predefined_split_column_name=_TEST_PREDEFINED_SPLIT_COLUMN_NAME,
                service_account=_TEST_SERVICE_ACCOUNT,
                tensorboard=_TEST_TENSORBOARD_RESOURCE_NAME,
                create_request_timeout=None,
            )
        assert e.match(
            regexp=r"To get model explanation, `explanation_parameters` "
            "must be specified."
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_tabular_dataset_and_timeout(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
        )

        model_from_job = job.run(
            dataset=mock_tabular_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            environment_variables=_TEST_ENVIRONMENT_VARIABLES,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            model_labels=_TEST_MODEL_LABELS,
            predefined_split_column_name=_TEST_PREDEFINED_SPLIT_COLUMN_NAME,
            service_account=_TEST_SERVICE_ACCOUNT,
            tensorboard=_TEST_TENSORBOARD_RESOURCE_NAME,
            sync=sync,
            create_request_timeout=180.0,
        )

        if not sync:
            model_from_job.wait()

        true_args = _TEST_RUN_ARGS
        true_env = [
            {"name": key, "value": value}
            for key, value in _TEST_ENVIRONMENT_VARIABLES.items()
        ]

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": _TEST_ACCELERATOR_COUNT,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "containerSpec": {
                "imageUri": _TEST_TRAINING_CONTAINER_IMAGE,
                "command": _TEST_TRAINING_CONTAINER_CMD,
                "args": true_args,
                "env": true_env,
            },
        }

        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
            for key, value in _TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
        ]

        ports = [
            gca_model.Port(container_port=port)
            for port in _TEST_MODEL_SERVING_CONTAINER_PORTS
        ]

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            env=env,
            ports=ports,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            labels=_TEST_MODEL_LABELS,
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            predefined_split=gca_training_pipeline.PredefinedSplit(
                key=_TEST_PREDEFINED_SPLIT_COLUMN_NAME
            ),
            dataset_id=mock_tabular_dataset.name,
            gcs_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_BASE_OUTPUT_DIR
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                    "service_account": _TEST_SERVICE_ACCOUNT,
                    "tensorboard": _TEST_TENSORBOARD_RESOURCE_NAME,
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=180.0,
        )

        # assert job._gca_resource == make_training_pipeline(
        #     gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        # )

        # mock_model_service_get.assert_called_once_with(
        #     name=_TEST_MODEL_NAME, retry=base._DEFAULT_RETRY
        # )

        # assert model_from_job._gca_resource is mock_model_service_get.return_value

        # assert job.get_model()._gca_resource is mock_model_service_get.return_value

        # assert not job.has_failed

        # assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

        # assert job._has_logged_custom_job

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_tabular_dataset_and_timeout_not_explicitly_set(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
        )

        model_from_job = job.run(
            dataset=mock_tabular_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            environment_variables=_TEST_ENVIRONMENT_VARIABLES,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            model_labels=_TEST_MODEL_LABELS,
            predefined_split_column_name=_TEST_PREDEFINED_SPLIT_COLUMN_NAME,
            service_account=_TEST_SERVICE_ACCOUNT,
            tensorboard=_TEST_TENSORBOARD_RESOURCE_NAME,
            sync=sync,
        )

        if not sync:
            model_from_job.wait()

        true_args = _TEST_RUN_ARGS
        true_env = [
            {"name": key, "value": value}
            for key, value in _TEST_ENVIRONMENT_VARIABLES.items()
        ]

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": _TEST_ACCELERATOR_COUNT,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "containerSpec": {
                "imageUri": _TEST_TRAINING_CONTAINER_IMAGE,
                "command": _TEST_TRAINING_CONTAINER_CMD,
                "args": true_args,
                "env": true_env,
            },
        }

        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
            for key, value in _TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
        ]

        ports = [
            gca_model.Port(container_port=port)
            for port in _TEST_MODEL_SERVING_CONTAINER_PORTS
        ]

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            env=env,
            ports=ports,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            labels=_TEST_MODEL_LABELS,
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            predefined_split=gca_training_pipeline.PredefinedSplit(
                key=_TEST_PREDEFINED_SPLIT_COLUMN_NAME
            ),
            dataset_id=mock_tabular_dataset.name,
            gcs_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_BASE_OUTPUT_DIR
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                    "service_account": _TEST_SERVICE_ACCOUNT,
                    "tensorboard": _TEST_TENSORBOARD_RESOURCE_NAME,
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_bigquery_destination(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
            training_encryption_spec_key_name=_TEST_PIPELINE_ENCRYPTION_KEY_NAME,
            model_encryption_spec_key_name=_TEST_MODEL_ENCRYPTION_KEY_NAME,
        )

        model_from_job = job.run(
            dataset=mock_tabular_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            bigquery_destination=_TEST_BIGQUERY_DESTINATION,
            args=_TEST_RUN_ARGS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            timestamp_split_column_name=_TEST_TIMESTAMP_SPLIT_COLUMN_NAME,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            model_from_job.wait()

        true_args = _TEST_RUN_ARGS

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": _TEST_ACCELERATOR_COUNT,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "containerSpec": {
                "imageUri": _TEST_TRAINING_CONTAINER_IMAGE,
                "command": _TEST_TRAINING_CONTAINER_CMD,
                "args": true_args,
            },
        }

        true_timestamp_split = gca_training_pipeline.TimestampSplit(
            training_fraction=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction=_TEST_TEST_FRACTION_SPLIT,
            key=_TEST_TIMESTAMP_SPLIT_COLUMN_NAME,
        )

        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
            for key, value in _TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
        ]

        ports = [
            gca_model.Port(container_port=port)
            for port in _TEST_MODEL_SERVING_CONTAINER_PORTS
        ]

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            env=env,
            ports=ports,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            encryption_spec=_TEST_MODEL_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            timestamp_split=true_timestamp_split,
            dataset_id=mock_tabular_dataset.name,
            bigquery_destination=gca_io.BigQueryDestination(
                output_uri=_TEST_BIGQUERY_DESTINATION
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_PIPELINE_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        assert job._gca_resource == make_training_pipeline(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        mock_model_service_get.assert_called_once_with(
            name=_TEST_MODEL_NAME, retry=base._DEFAULT_RETRY
        )

        assert model_from_job._gca_resource is mock_model_service_get.return_value

        assert job.get_model()._gca_resource is mock_model_service_get.return_value

        assert not job.has_failed

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_pipeline_service_get",
        "mock_python_package_to_gcs",
        "mock_model_service_get",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_called_twice_raises(
        self,
        mock_tabular_dataset,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        job.run(
            dataset=mock_tabular_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            replica_count=1,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            sync=sync,
            create_request_timeout=None,
        )

        with pytest.raises(RuntimeError):
            job.run(
                dataset=mock_tabular_dataset,
                base_output_dir=_TEST_BASE_OUTPUT_DIR,
                args=_TEST_RUN_ARGS,
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
                validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
                test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
                sync=sync,
                create_request_timeout=None,
            )

        if not sync:
            job.wait()

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_with_invalid_accelerator_type_raises(
        self,
        mock_pipeline_service_create,
        mock_python_package_to_gcs,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        with pytest.raises(ValueError):
            job.run(
                dataset=mock_tabular_dataset,
                base_output_dir=_TEST_BASE_OUTPUT_DIR,
                args=_TEST_RUN_ARGS,
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_INVALID_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                sync=sync,
                create_request_timeout=None,
            )

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_with_two_split_raises(
        self,
        mock_pipeline_service_create,
        mock_python_package_to_gcs,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        with pytest.raises(ValueError):
            job.run(
                dataset=mock_tabular_dataset,
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_INVALID_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                predefined_split_column_name=_TEST_PREDEFINED_SPLIT_COLUMN_NAME,
                training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
                validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
                test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
                sync=sync,
                create_request_timeout=None,
            )

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_with_incomplete_model_info_raises_with_model_to_upload(
        self,
        mock_pipeline_service_create,
        mock_python_package_to_gcs,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
        )

        with pytest.raises(RuntimeError):
            job.run(
                dataset=mock_tabular_dataset,
                base_output_dir=_TEST_BASE_OUTPUT_DIR,
                args=_TEST_RUN_ARGS,
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
                validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
                test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
                sync=sync,
                create_request_timeout=None,
            )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_no_dataset(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        model_from_job = job.run(
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            model_from_job.wait()

        true_args = _TEST_RUN_ARGS

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": _TEST_ACCELERATOR_COUNT,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "containerSpec": {
                "imageUri": _TEST_TRAINING_CONTAINER_IMAGE,
                "command": _TEST_TRAINING_CONTAINER_CMD,
                "args": true_args,
            },
        }

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            container_spec=true_container_spec,
            version_aliases=["default"],
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        assert job._gca_resource == make_training_pipeline(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        mock_model_service_get.assert_called_once_with(
            name=_TEST_MODEL_NAME, retry=base._DEFAULT_RETRY
        )

        assert model_from_job._gca_resource is mock_model_service_get.return_value

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create_with_enable_web_access",
        "mock_pipeline_service_get_with_enable_web_access",
        "mock_get_backing_custom_job_with_enable_web_access",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_enable_web_access(
        self, sync, caplog
    ):

        caplog.set_level(logging.INFO)

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
        )

        job.run(
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            enable_web_access=_TEST_ENABLE_WEB_ACCESS,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            job.wait()

        print(caplog.text)
        # TODO: b/383923584: Re-enable this test once the parent issue is fixed
        # assert "workerpool0-0" in caplog.text
        assert job._gca_resource == make_training_pipeline_with_enable_web_access(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

    # TODO: Update test to address Mutant issue b/270708320
    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create_with_enable_dashboard_access",
        "mock_pipeline_service_get_with_enable_dashboard_access",
        "mock_get_backing_custom_job_with_enable_dashboard_access",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_enable_dashboard_access(
        self, sync, caplog
    ):

        caplog.set_level(logging.INFO)

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
        )

        job.run(
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            enable_dashboard_access=_TEST_ENABLE_DASHBOARD_ACCESS,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            job.wait()

        print(caplog.text)
        # TODO: b/383923584: Re-enable this test once the parent issue is fixed
        # assert "workerpool0-0:8888" in caplog.text
        assert job._gca_resource == make_training_pipeline_with_enable_dashboard_access(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create_with_scheduling",
        "mock_pipeline_service_get_with_scheduling",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_scheduling(self, sync, caplog):

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
        )

        job.run(
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            sync=sync,
            create_request_timeout=None,
            disable_retries=_TEST_DISABLE_RETRIES,
            max_wait_duration=_TEST_MAX_WAIT_DURATION,
        )

        if not sync:
            job.wait()

        assert job._gca_resource == make_training_pipeline_with_scheduling(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        assert (
            job._gca_resource.state
            == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )
        assert job._gca_resource.training_task_inputs["timeout"] == f"{_TEST_TIMEOUT}s"
        assert (
            job._gca_resource.training_task_inputs["restart_job_on_worker_restart"]
            == _TEST_RESTART_JOB_ON_WORKER_RESTART
        )
        assert (
            job._gca_resource.training_task_inputs["disable_retries"]
            == _TEST_DISABLE_RETRIES
        )
        assert (
            job._gca_resource.training_task_inputs["max_wait_duration"]
            == f"{_TEST_MAX_WAIT_DURATION}s"
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_returns_none_if_no_model_to_upload(
        self,
        mock_pipeline_service_create_with_no_model_to_upload,
        mock_pipeline_service_get_with_no_model_to_upload,
        mock_tabular_dataset,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
        )

        model = job.run(
            dataset=mock_tabular_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            replica_count=1,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            sync=sync,
            create_request_timeout=None,
        )

        assert model is None

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create_with_no_model_to_upload",
        "mock_pipeline_service_get_with_no_model_to_upload",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_get_model_raises_if_no_model_to_upload(
        self,
        mock_tabular_dataset,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
        )

        job.run(
            dataset=mock_tabular_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            replica_count=1,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            job.wait()

        with pytest.raises(RuntimeError):
            job.get_model()

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_raises_if_pipeline_fails(
        self,
        mock_pipeline_service_create_and_get_with_fail,
        mock_tabular_dataset,
        sync,
    ):

        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
        )

        with pytest.raises(RuntimeError):
            job.run(
                dataset=mock_tabular_dataset,
                base_output_dir=_TEST_BASE_OUTPUT_DIR,
                args=_TEST_RUN_ARGS,
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
                validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
                test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
                sync=sync,
                create_request_timeout=None,
            )

            if not sync:
                job.wait()

        with pytest.raises(RuntimeError):
            job.get_model()

    def test_raises_before_run_is_called(self, mock_pipeline_service_create):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        with pytest.raises(RuntimeError):
            job.get_model()

        with pytest.raises(RuntimeError):
            job.has_failed

        with pytest.raises(RuntimeError):
            job.state

    def test_run_raises_if_no_staging_bucket(self):

        aiplatform.init(project=_TEST_PROJECT)

        with pytest.raises(RuntimeError):
            training_jobs.CustomContainerTrainingJob(
                display_name=_TEST_DISPLAY_NAME,
                container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
                command=_TEST_TRAINING_CONTAINER_CMD,
            )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_distributed_training(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
        )

        model_from_job = job.run(
            dataset=mock_tabular_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            replica_count=10,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            model_from_job.wait()

        true_args = _TEST_RUN_ARGS

        true_worker_pool_spec = [
            {
                "replica_count": 1,
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                },
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
                "containerSpec": {
                    "imageUri": _TEST_TRAINING_CONTAINER_IMAGE,
                    "command": _TEST_TRAINING_CONTAINER_CMD,
                    "args": true_args,
                },
            },
            {
                "replica_count": 9,
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                },
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
                "containerSpec": {
                    "imageUri": _TEST_TRAINING_CONTAINER_IMAGE,
                    "command": _TEST_TRAINING_CONTAINER_CMD,
                    "args": true_args,
                },
            },
        ]

        true_fraction_split = gca_training_pipeline.FractionSplit(
            training_fraction=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction=_TEST_TEST_FRACTION_SPLIT,
        )

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            fraction_split=true_fraction_split,
            dataset_id=mock_tabular_dataset.name,
            gcs_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_BASE_OUTPUT_DIR
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": true_worker_pool_spec,
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        assert job._gca_resource == make_training_pipeline(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        mock_model_service_get.assert_called_once_with(
            name=_TEST_MODEL_NAME, retry=base._DEFAULT_RETRY
        )

        assert model_from_job._gca_resource is mock_model_service_get.return_value

        assert job.get_model()._gca_resource is mock_model_service_get.return_value

        assert not job.has_failed

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_distributed_training_with_reduction_server(
        self,
        mock_pipeline_service_create_with_no_model_to_upload,
        mock_pipeline_service_get_with_no_model_to_upload,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
        )

        job.run(
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            replica_count=10,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            reduction_server_replica_count=_TEST_REDUCTION_SERVER_REPLICA_COUNT,
            reduction_server_machine_type=_TEST_REDUCTION_SERVER_MACHINE_TYPE,
            reduction_server_container_uri=_TEST_REDUCTION_SERVER_CONTAINER_URI,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            job.wait()

        true_args = _TEST_RUN_ARGS

        true_worker_pool_spec = [
            {
                "replica_count": 1,
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                },
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
                "containerSpec": {
                    "imageUri": _TEST_TRAINING_CONTAINER_IMAGE,
                    "command": _TEST_TRAINING_CONTAINER_CMD,
                    "args": true_args,
                },
            },
            {
                "replica_count": 9,
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                },
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
                "containerSpec": {
                    "imageUri": _TEST_TRAINING_CONTAINER_IMAGE,
                    "command": _TEST_TRAINING_CONTAINER_CMD,
                    "args": true_args,
                },
            },
            {
                "replica_count": _TEST_REDUCTION_SERVER_REPLICA_COUNT,
                "machine_spec": {"machine_type": _TEST_REDUCTION_SERVER_MACHINE_TYPE},
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
                "container_spec": {"image_uri": _TEST_REDUCTION_SERVER_CONTAINER_URI},
            },
        ]

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": true_worker_pool_spec,
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
        )

        mock_pipeline_service_create_with_no_model_to_upload.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        assert job._gca_resource == make_training_pipeline_with_no_model_upload(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        assert not job.has_failed

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_nontabular_dataset(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_python_package_to_gcs,
        mock_nontabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
        )

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
        )

        model_from_job = job.run(
            dataset=mock_nontabular_dataset,
            annotation_schema_uri=_TEST_ANNOTATION_SCHEMA_URI,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            args=_TEST_RUN_ARGS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            model_labels=_TEST_MODEL_LABELS,
            training_filter_split=_TEST_TRAINING_FILTER_SPLIT,
            validation_filter_split=_TEST_VALIDATION_FILTER_SPLIT,
            test_filter_split=_TEST_TEST_FILTER_SPLIT,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            model_from_job.wait()

        true_args = _TEST_RUN_ARGS

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": _TEST_ACCELERATOR_COUNT,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "containerSpec": {
                "imageUri": _TEST_TRAINING_CONTAINER_IMAGE,
                "command": _TEST_TRAINING_CONTAINER_CMD,
                "args": true_args,
            },
        }

        true_filter_split = gca_training_pipeline.FilterSplit(
            training_filter=_TEST_TRAINING_FILTER_SPLIT,
            validation_filter=_TEST_VALIDATION_FILTER_SPLIT,
            test_filter=_TEST_TEST_FILTER_SPLIT,
        )

        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
            for key, value in _TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
        ]

        ports = [
            gca_model.Port(container_port=port)
            for port in _TEST_MODEL_SERVING_CONTAINER_PORTS
        ]

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            env=env,
            ports=ports,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            labels=_TEST_MODEL_LABELS,
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            filter_split=true_filter_split,
            dataset_id=mock_nontabular_dataset.name,
            annotation_schema_uri=_TEST_ANNOTATION_SCHEMA_URI,
            gcs_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_BASE_OUTPUT_DIR
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                    "service_account": _TEST_SERVICE_ACCOUNT,
                    "network": _TEST_NETWORK,
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            labels=_TEST_LABELS,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        assert job._gca_resource == make_training_pipeline(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        mock_model_service_get.assert_called_once_with(
            name=_TEST_MODEL_NAME, retry=base._DEFAULT_RETRY
        )

        assert model_from_job._gca_resource is mock_model_service_get.return_value

        assert job.get_model()._gca_resource is mock_model_service_get.return_value

        assert not job.has_failed

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

    def test_run_call_pipeline_service_create_with_nontabular_dataset_raises_if_annotation_schema_uri(
        self,
        mock_nontabular_dataset,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
        )

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
        )

        with pytest.raises(Exception):
            job.run(
                dataset=mock_nontabular_dataset,
                base_output_dir=_TEST_BASE_OUTPUT_DIR,
                args=_TEST_RUN_ARGS,
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                create_request_timeout=None,
            )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create_with_persistent_resource_id",
        "mock_pipeline_service_get_with_persistent_resource_id",
        "mock_get_backing_custom_job_with_persistent_resource_id",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_persistent_resource_id(
        self, sync, caplog
    ):

        caplog.set_level(logging.INFO)

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
        )

        job.run(
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            sync=sync,
            create_request_timeout=None,
            persistent_resource_id=_TEST_PERSISTENT_RESOURCE_ID,
        )

        if not sync:
            job.wait()

        print(caplog.text)
        assert job._gca_resource == make_training_pipeline_with_persistent_resource_id(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_pipeline_service_get",
        "mock_python_package_to_gcs",
        "mock_model_service_get",
    )
    def test_training_job_tpu_v5e(self, mock_pipeline_service_create):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_description=_TEST_MODEL_DESCRIPTION,
        )

        job.run(
            machine_type=_TEST_MACHINE_TYPE_TPU_V5E,
            tpu_topology="2x2",
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
        )

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_DISPLAY_NAME + "-model",
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            version_aliases=["default"],
        )

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE_TPU_V5E,
                "tpu_topology": "2x2",
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "containerSpec": {
                "imageUri": _TEST_TRAINING_CONTAINER_IMAGE,
                "command": _TEST_TRAINING_CONTAINER_CMD,
            },
        }

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_pipeline_service_get",
        "mock_python_package_to_gcs",
        "mock_model_service_get",
    )
    def test_training_job_tpu_v3_pod(self, mock_pipeline_service_create):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_description=_TEST_MODEL_DESCRIPTION,
        )

        job.run(
            machine_type=_TEST_MACHINE_TYPE_TPU,
            accelerator_type=_TEST_ACCELERATOR_TPU_TYPE,
            accelerator_count=32,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
        )

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_DISPLAY_NAME + "-model",
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            version_aliases=["default"],
        )

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE_TPU,
                "accelerator_type": _TEST_ACCELERATOR_TPU_TYPE,
                "accelerator_count": 32,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "containerSpec": {
                "imageUri": _TEST_TRAINING_CONTAINER_IMAGE,
                "command": _TEST_TRAINING_CONTAINER_CMD,
            },
        }

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_pipeline_service_get",
        "mock_python_package_to_gcs",
        "mock_model_service_get",
    )
    def test_training_job_reservation_affinity(self, mock_pipeline_service_create):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_description=_TEST_MODEL_DESCRIPTION,
        )

        job.run(
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=32,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            reservation_affinity_type="ANY_RESERVATION",
        )

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_DISPLAY_NAME + "-model",
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            version_aliases=["default"],
        )

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": 32,
                "reservation_affinity": {
                    "reservation_affinity_type": "ANY_RESERVATION"
                },
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "containerSpec": {
                "imageUri": _TEST_TRAINING_CONTAINER_IMAGE,
                "command": _TEST_TRAINING_CONTAINER_CMD,
            },
        }

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )


class Test_WorkerPoolSpec:
    def test_machine_spec_return_spec_dict(self):
        test_spec = worker_spec_utils._WorkerPoolSpec(
            replica_count=_TEST_REPLICA_COUNT,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            reservation_affinity_type="SPECIFIC_RESERVATION",
            reservation_affinity_key="compute.googleapis.com/reservation-name",
            reservation_affinity_values="projects/{project_id_or_number}/zones/{zone}/reservations/{reservation_name}",
        )

        true_spec_dict = {
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": _TEST_ACCELERATOR_COUNT,
                "reservation_affinity": {
                    "reservation_affinity_type": "SPECIFIC_RESERVATION",
                    "key": "compute.googleapis.com/reservation-name",
                    "values": "projects/{project_id_or_number}/zones/{zone}/reservations/{reservation_name}",
                },
            },
            "replica_count": _TEST_REPLICA_COUNT,
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
        }

        assert test_spec.spec_dict == true_spec_dict

    def test_machine_spec_return_spec_dict_with_boot_disk(self):
        test_spec = worker_spec_utils._WorkerPoolSpec(
            replica_count=_TEST_REPLICA_COUNT,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            boot_disk_type=_TEST_BOOT_DISK_TYPE,
            boot_disk_size_gb=_TEST_BOOT_DISK_SIZE_GB,
        )

        true_spec_dict = {
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": _TEST_ACCELERATOR_COUNT,
            },
            "replica_count": _TEST_REPLICA_COUNT,
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB,
            },
        }

        assert test_spec.spec_dict == true_spec_dict

    def test_machine_spec_return_spec_dict_with_no_accelerator(self):
        test_spec = worker_spec_utils._WorkerPoolSpec(
            replica_count=_TEST_REPLICA_COUNT,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_count=0,
            accelerator_type="ACCELERATOR_TYPE_UNSPECIFIED",
        )

        true_spec_dict = {
            "machine_spec": {"machine_type": _TEST_MACHINE_TYPE},
            "replica_count": _TEST_REPLICA_COUNT,
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
        }

        assert test_spec.spec_dict == true_spec_dict

    def test_machine_spec_spec_dict_raises_invalid_accelerator(self):
        test_spec = worker_spec_utils._WorkerPoolSpec(
            replica_count=_TEST_REPLICA_COUNT,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            accelerator_type=_TEST_INVALID_ACCELERATOR_TYPE,
        )

        with pytest.raises(ValueError):
            test_spec.spec_dict

    def test_machine_spec_spec_dict_is_empty(self):
        test_spec = worker_spec_utils._WorkerPoolSpec(
            replica_count=0,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            accelerator_type=_TEST_INVALID_ACCELERATOR_TYPE,
        )

        assert test_spec.is_empty

    def test_machine_spec_spec_dict_is_not_empty(self):
        test_spec = worker_spec_utils._WorkerPoolSpec(
            replica_count=_TEST_REPLICA_COUNT,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            accelerator_type=_TEST_INVALID_ACCELERATOR_TYPE,
        )

        assert not test_spec.is_empty


class Test_DistributedTrainingSpec:
    def test_machine_spec_returns_pool_spec(self):

        spec = worker_spec_utils._DistributedTrainingSpec(
            chief_spec=worker_spec_utils._WorkerPoolSpec(
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
                reservation_affinity_type="ANY_RESERVATION",
            ),
            worker_spec=worker_spec_utils._WorkerPoolSpec(
                replica_count=10,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
                reservation_affinity_type="SPECIFIC_RESERVATION",
                reservation_affinity_key="compute.googleapis.com/reservation-name",
                reservation_affinity_values="projects/{project_id_or_number}/zones/{zone}/reservations/{reservation_name}",
            ),
            server_spec=worker_spec_utils._WorkerPoolSpec(
                replica_count=3,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
                reservation_affinity_type="NO_RESERVATION",
            ),
            evaluator_spec=worker_spec_utils._WorkerPoolSpec(
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
            ),
        )

        true_pool_spec = [
            {
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                    "reservation_affinity": {
                        "reservation_affinity_type": "ANY_RESERVATION",
                    },
                },
                "replica_count": 1,
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
            },
            {
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                    "reservation_affinity": {
                        "reservation_affinity_type": "SPECIFIC_RESERVATION",
                        "key": "compute.googleapis.com/reservation-name",
                        "values": "projects/{project_id_or_number}/zones/{zone}/reservations/{reservation_name}",
                    },
                },
                "replica_count": 10,
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
            },
            {
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                    "reservation_affinity": {
                        "reservation_affinity_type": "NO_RESERVATION",
                    },
                },
                "replica_count": 3,
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
            },
            {
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                },
                "replica_count": 1,
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
            },
        ]

        assert spec.pool_specs == true_pool_spec

    def test_chief_worker_pool_returns_spec(self):

        chief_worker_spec = worker_spec_utils._DistributedTrainingSpec.chief_worker_pool(
            replica_count=10,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            reservation_affinity_type="SPECIFIC_RESERVATION",
            reservation_affinity_key="compute.googleapis.com/reservation-name",
            reservation_affinity_values="projects/{project_id_or_number}/zones/{zone}/reservations/{reservation_name}",
        )

        true_pool_spec = [
            {
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                    "reservation_affinity": {
                        "reservation_affinity_type": "SPECIFIC_RESERVATION",
                        "key": "compute.googleapis.com/reservation-name",
                        "values": "projects/{project_id_or_number}/zones/{zone}/reservations/{reservation_name}",
                    },
                },
                "replica_count": 1,
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
            },
            {
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                    "reservation_affinity": {
                        "reservation_affinity_type": "SPECIFIC_RESERVATION",
                        "key": "compute.googleapis.com/reservation-name",
                        "values": "projects/{project_id_or_number}/zones/{zone}/reservations/{reservation_name}",
                    },
                },
                "replica_count": 9,
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
            },
        ]

        assert chief_worker_spec.pool_specs == true_pool_spec

    def test_chief_worker_pool_returns_just_chief(self):

        chief_worker_spec = worker_spec_utils._DistributedTrainingSpec.chief_worker_pool(
            replica_count=1,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            reservation_affinity_type="SPECIFIC_RESERVATION",
            reservation_affinity_key="compute.googleapis.com/reservation-name",
            reservation_affinity_values="projects/{project_id_or_number}/zones/{zone}/reservations/{reservation_name}",
        )

        true_pool_spec = [
            {
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                    "reservation_affinity": {
                        "reservation_affinity_type": "SPECIFIC_RESERVATION",
                        "key": "compute.googleapis.com/reservation-name",
                        "values": "projects/{project_id_or_number}/zones/{zone}/reservations/{reservation_name}",
                    },
                },
                "replica_count": 1,
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
            }
        ]

        assert chief_worker_spec.pool_specs == true_pool_spec

    def test_machine_spec_raise_with_more_than_one_chief_replica(self):

        spec = worker_spec_utils._DistributedTrainingSpec(
            chief_spec=worker_spec_utils._WorkerPoolSpec(
                replica_count=2,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
            ),
        )

        with pytest.raises(ValueError):
            spec.pool_specs

    def test_machine_spec_handles_missing_pools(self):

        spec = worker_spec_utils._DistributedTrainingSpec(
            chief_spec=worker_spec_utils._WorkerPoolSpec(
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
            ),
            worker_spec=worker_spec_utils._WorkerPoolSpec(replica_count=0),
            server_spec=worker_spec_utils._WorkerPoolSpec(
                replica_count=3,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
            ),
            evaluator_spec=worker_spec_utils._WorkerPoolSpec(replica_count=0),
        )

        true_pool_spec = [
            {
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                },
                "replica_count": 1,
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
            },
            {},
            {
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                },
                "replica_count": 3,
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
            },
        ]

        assert spec.pool_specs == true_pool_spec


@pytest.mark.usefixtures("google_auth_mock")
class TestCustomPythonPackageTrainingJob:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.parametrize(
        "python_package_gcs_uri",
        [_TEST_OUTPUT_PYTHON_PACKAGE_PATH, _TEST_PACKAGE_GCS_URIS],
    )
    def test_run_call_pipeline_service_create_with_tabular_dataset(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
        python_package_gcs_uri,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            service_account=_TEST_SERVICE_ACCOUNT,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            python_package_gcs_uri=python_package_gcs_uri,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            explanation_metadata=_TEST_EXPLANATION_METADATA,
            explanation_parameters=_TEST_EXPLANATION_PARAMETERS,
        )

        model_from_job = job.run(
            dataset=mock_tabular_dataset,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            model_labels=_TEST_MODEL_LABELS,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            network=_TEST_NETWORK,
            args=_TEST_RUN_ARGS,
            environment_variables=_TEST_ENVIRONMENT_VARIABLES,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            model_from_job.wait()

        true_args = _TEST_RUN_ARGS
        true_env = [
            {"name": key, "value": value}
            for key, value in _TEST_ENVIRONMENT_VARIABLES.items()
        ]

        if isinstance(python_package_gcs_uri, str):
            package_uris = [python_package_gcs_uri]
        else:
            package_uris = python_package_gcs_uri

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": _TEST_ACCELERATOR_COUNT,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "python_package_spec": {
                "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                "python_module": _TEST_PYTHON_MODULE_NAME,
                "package_uris": package_uris,
                "args": true_args,
                "env": true_env,
            },
        }

        true_fraction_split = gca_training_pipeline.FractionSplit(
            training_fraction=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction=_TEST_TEST_FRACTION_SPLIT,
        )

        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
            for key, value in _TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
        ]

        ports = [
            gca_model.Port(container_port=port)
            for port in _TEST_MODEL_SERVING_CONTAINER_PORTS
        ]

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            env=env,
            ports=ports,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            labels=_TEST_MODEL_LABELS,
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
            explanation_spec=gca_model.explanation.ExplanationSpec(
                metadata=_TEST_EXPLANATION_METADATA,
                parameters=_TEST_EXPLANATION_PARAMETERS,
            ),
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            fraction_split=true_fraction_split,
            dataset_id=mock_tabular_dataset.name,
            gcs_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_BASE_OUTPUT_DIR
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                    "service_account": _TEST_SERVICE_ACCOUNT,
                    "network": _TEST_NETWORK,
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        assert job._gca_resource == make_training_pipeline(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        mock_model_service_get.assert_called_once_with(
            name=_TEST_MODEL_NAME, retry=base._DEFAULT_RETRY
        )

        assert model_from_job._gca_resource is mock_model_service_get.return_value

        assert job.get_model()._gca_resource is mock_model_service_get.return_value

        assert not job.has_failed

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    def test_custom_python_package_training_job_run_raises_with_wrong_package_uris(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_tabular_dataset,
        mock_model_service_get,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        wrong_package_gcs_uri = {"package": _TEST_OUTPUT_PYTHON_PACKAGE_PATH}

        with pytest.raises(ValueError) as e:
            training_jobs.CustomPythonPackageTrainingJob(
                display_name=_TEST_DISPLAY_NAME,
                labels=_TEST_LABELS,
                python_package_gcs_uri=wrong_package_gcs_uri,
                python_module_name=_TEST_PYTHON_MODULE_NAME,
                container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
                model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
                model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
                model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
                model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
                model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
                model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
                model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
                model_description=_TEST_MODEL_DESCRIPTION,
                model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
                explanation_metadata=_TEST_EXPLANATION_METADATA,
                explanation_parameters=_TEST_EXPLANATION_PARAMETERS,
            )

        assert e.match("'python_package_gcs_uri' must be a string or list.")

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    def test_custom_python_package_training_job_run_raises_with_impartial_explanation_spec(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_tabular_dataset,
        mock_model_service_get,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.CustomContainerTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            command=_TEST_TRAINING_CONTAINER_CMD,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
            explanation_metadata=_TEST_EXPLANATION_METADATA,
            # Missing the required explanations_parameters field
        )

        with pytest.raises(ValueError) as e:
            job.run(
                dataset=mock_tabular_dataset,
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                model_labels=_TEST_MODEL_LABELS,
                base_output_dir=_TEST_BASE_OUTPUT_DIR,
                service_account=_TEST_SERVICE_ACCOUNT,
                network=_TEST_NETWORK,
                args=_TEST_RUN_ARGS,
                environment_variables=_TEST_ENVIRONMENT_VARIABLES,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
                validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
                test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
                create_request_timeout=None,
            )
        assert e.match(
            regexp=r"To get model explanation, `explanation_parameters` "
            "must be specified."
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_tabular_dataset_with_timeout(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
        )

        model_from_job = job.run(
            dataset=mock_tabular_dataset,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            model_labels=_TEST_MODEL_LABELS,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            args=_TEST_RUN_ARGS,
            environment_variables=_TEST_ENVIRONMENT_VARIABLES,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            sync=sync,
            create_request_timeout=180.0,
        )

        if not sync:
            model_from_job.wait()

        true_args = _TEST_RUN_ARGS
        true_env = [
            {"name": key, "value": value}
            for key, value in _TEST_ENVIRONMENT_VARIABLES.items()
        ]

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": _TEST_ACCELERATOR_COUNT,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "python_package_spec": {
                "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                "python_module": _TEST_PYTHON_MODULE_NAME,
                "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                "args": true_args,
                "env": true_env,
            },
        }

        true_fraction_split = gca_training_pipeline.FractionSplit(
            training_fraction=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction=_TEST_TEST_FRACTION_SPLIT,
        )

        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
            for key, value in _TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
        ]

        ports = [
            gca_model.Port(container_port=port)
            for port in _TEST_MODEL_SERVING_CONTAINER_PORTS
        ]

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            env=env,
            ports=ports,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            labels=_TEST_MODEL_LABELS,
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            fraction_split=true_fraction_split,
            dataset_id=mock_tabular_dataset.name,
            gcs_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_BASE_OUTPUT_DIR
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                    "service_account": _TEST_SERVICE_ACCOUNT,
                    "network": _TEST_NETWORK,
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=180.0,
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_tabular_dataset_with_timeout_not_explicitly_set(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
        )

        model_from_job = job.run(
            dataset=mock_tabular_dataset,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            model_labels=_TEST_MODEL_LABELS,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            args=_TEST_RUN_ARGS,
            environment_variables=_TEST_ENVIRONMENT_VARIABLES,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            sync=sync,
        )

        if not sync:
            model_from_job.wait()

        true_args = _TEST_RUN_ARGS
        true_env = [
            {"name": key, "value": value}
            for key, value in _TEST_ENVIRONMENT_VARIABLES.items()
        ]

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": _TEST_ACCELERATOR_COUNT,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "python_package_spec": {
                "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                "python_module": _TEST_PYTHON_MODULE_NAME,
                "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                "args": true_args,
                "env": true_env,
            },
        }

        true_fraction_split = gca_training_pipeline.FractionSplit(
            training_fraction=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction=_TEST_TEST_FRACTION_SPLIT,
        )

        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
            for key, value in _TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
        ]

        ports = [
            gca_model.Port(container_port=port)
            for port in _TEST_MODEL_SERVING_CONTAINER_PORTS
        ]

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            env=env,
            ports=ports,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            labels=_TEST_MODEL_LABELS,
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            fraction_split=true_fraction_split,
            dataset_id=mock_tabular_dataset.name,
            gcs_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_BASE_OUTPUT_DIR
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                    "service_account": _TEST_SERVICE_ACCOUNT,
                    "network": _TEST_NETWORK,
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_tabular_dataset_without_model_display_name_nor_model_labels(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
        )

        model_from_job = job.run(
            dataset=mock_tabular_dataset,
            # model_display_name=_TEST_MODEL_DISPLAY_NAME,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            predefined_split_column_name=_TEST_PREDEFINED_SPLIT_COLUMN_NAME,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            model_from_job.wait()

        true_args = _TEST_RUN_ARGS

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": _TEST_ACCELERATOR_COUNT,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "python_package_spec": {
                "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                "python_module": _TEST_PYTHON_MODULE_NAME,
                "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                "args": true_args,
            },
        }

        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
            for key, value in _TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
        ]

        ports = [
            gca_model.Port(container_port=port)
            for port in _TEST_MODEL_SERVING_CONTAINER_PORTS
        ]

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            env=env,
            ports=ports,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_DISPLAY_NAME + "-model",
            labels=_TEST_LABELS,
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            predefined_split=gca_training_pipeline.PredefinedSplit(
                key=_TEST_PREDEFINED_SPLIT_COLUMN_NAME
            ),
            dataset_id=mock_tabular_dataset.name,
            gcs_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_BASE_OUTPUT_DIR
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        assert job._gca_resource == make_training_pipeline(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        mock_model_service_get.assert_called_once_with(
            name=_TEST_MODEL_NAME, retry=base._DEFAULT_RETRY
        )

        assert model_from_job._gca_resource is mock_model_service_get.return_value

        assert job.get_model()._gca_resource is mock_model_service_get.return_value

        assert not job.has_failed

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_bigquery_destination(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            training_encryption_spec_key_name=_TEST_PIPELINE_ENCRYPTION_KEY_NAME,
            model_encryption_spec_key_name=_TEST_MODEL_ENCRYPTION_KEY_NAME,
        )

        model_from_job = job.run(
            dataset=mock_tabular_dataset,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            bigquery_destination=_TEST_BIGQUERY_DESTINATION,
            args=_TEST_RUN_ARGS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            timestamp_split_column_name=_TEST_TIMESTAMP_SPLIT_COLUMN_NAME,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            model_from_job.wait()

        true_args = _TEST_RUN_ARGS

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": _TEST_ACCELERATOR_COUNT,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "python_package_spec": {
                "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                "python_module": _TEST_PYTHON_MODULE_NAME,
                "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                "args": true_args,
            },
        }

        true_timestamp_split = gca_training_pipeline.TimestampSplit(
            training_fraction=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction=_TEST_TEST_FRACTION_SPLIT,
            key=_TEST_TIMESTAMP_SPLIT_COLUMN_NAME,
        )

        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
            for key, value in _TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
        ]

        ports = [
            gca_model.Port(container_port=port)
            for port in _TEST_MODEL_SERVING_CONTAINER_PORTS
        ]

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            env=env,
            ports=ports,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            encryption_spec=_TEST_MODEL_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            timestamp_split=true_timestamp_split,
            dataset_id=mock_tabular_dataset.name,
            bigquery_destination=gca_io.BigQueryDestination(
                output_uri=_TEST_BIGQUERY_DESTINATION
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_PIPELINE_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        assert job._gca_resource == make_training_pipeline(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        mock_model_service_get.assert_called_once_with(
            name=_TEST_MODEL_NAME, retry=base._DEFAULT_RETRY
        )

        assert model_from_job._gca_resource is mock_model_service_get.return_value

        assert job.get_model()._gca_resource is mock_model_service_get.return_value

        assert not job.has_failed

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_pipeline_service_get",
        "mock_python_package_to_gcs",
        "mock_model_service_get",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_called_twice_raises(
        self,
        mock_tabular_dataset,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        job.run(
            dataset=mock_tabular_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            replica_count=1,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            sync=sync,
            create_request_timeout=None,
        )

        with pytest.raises(RuntimeError):
            job.run(
                dataset=mock_tabular_dataset,
                base_output_dir=_TEST_BASE_OUTPUT_DIR,
                args=_TEST_RUN_ARGS,
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                sync=sync,
                create_request_timeout=None,
            )

        if not sync:
            job.wait()

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_with_invalid_accelerator_type_raises(
        self,
        mock_pipeline_service_create,
        mock_python_package_to_gcs,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        with pytest.raises(ValueError):
            job.run(
                dataset=mock_tabular_dataset,
                base_output_dir=_TEST_BASE_OUTPUT_DIR,
                args=_TEST_RUN_ARGS,
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_INVALID_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
                validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
                test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
                sync=sync,
                create_request_timeout=None,
            )

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_with_two_split_raises(
        self,
        mock_pipeline_service_create,
        mock_python_package_to_gcs,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        with pytest.raises(ValueError):
            job.run(
                dataset=mock_tabular_dataset,
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_INVALID_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                predefined_split_column_name=_TEST_PREDEFINED_SPLIT_COLUMN_NAME,
                training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
                validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
                test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
                sync=sync,
                create_request_timeout=None,
            )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_with_incomplete_model_info_raises_with_model_to_upload(
        self,
        mock_pipeline_service_create,
        mock_python_package_to_gcs,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        with pytest.raises(RuntimeError):
            job.run(
                dataset=mock_tabular_dataset,
                base_output_dir=_TEST_BASE_OUTPUT_DIR,
                args=_TEST_RUN_ARGS,
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
                validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
                test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
                sync=sync,
                create_request_timeout=None,
            )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_no_dataset(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        model_from_job = job.run(
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            model_from_job.wait()

        true_args = _TEST_RUN_ARGS

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": _TEST_ACCELERATOR_COUNT,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "python_package_spec": {
                "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                "python_module": _TEST_PYTHON_MODULE_NAME,
                "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                "args": true_args,
            },
        }

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            container_spec=true_container_spec,
            version_aliases=["default"],
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        assert job._gca_resource == make_training_pipeline(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        mock_model_service_get.assert_called_once_with(
            name=_TEST_MODEL_NAME, retry=base._DEFAULT_RETRY
        )

        assert model_from_job._gca_resource is mock_model_service_get.return_value

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create_with_enable_web_access",
        "mock_pipeline_service_get_with_enable_web_access",
        "mock_get_backing_custom_job_with_enable_web_access",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_enable_web_access(
        self, sync, caplog
    ):

        caplog.set_level(logging.INFO)

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        job.run(
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            enable_web_access=_TEST_ENABLE_WEB_ACCESS,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            job.wait()

        print(caplog.text)
        # TODO: b/383923584: Re-enable this test once the parent issue is fixed
        # assert "workerpool0-0" in caplog.text
        assert job._gca_resource == make_training_pipeline_with_enable_web_access(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

    # TODO: Update test to address Mutant issue b/270708320
    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create_with_enable_dashboard_access",
        "mock_pipeline_service_get_with_enable_dashboard_access",
        "mock_get_backing_custom_job_with_enable_dashboard_access",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_enable_dashboard_access(
        self, sync, caplog
    ):

        caplog.set_level(logging.INFO)

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        job.run(
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            enable_dashboard_access=_TEST_ENABLE_DASHBOARD_ACCESS,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            job.wait()
        print(caplog.text)
        # TODO: b/383923584: Re-enable this test once the parent issue is fixed
        # assert "workerpool0-0:8888" in caplog.text
        assert job._gca_resource == make_training_pipeline_with_enable_dashboard_access(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create_with_scheduling",
        "mock_pipeline_service_get_with_scheduling",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_scheduling(self, sync, caplog):

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        job.run(
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            sync=sync,
            create_request_timeout=None,
            disable_retries=_TEST_DISABLE_RETRIES,
            max_wait_duration=_TEST_MAX_WAIT_DURATION,
        )

        if not sync:
            job.wait()

        assert job._gca_resource == make_training_pipeline_with_scheduling(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        assert (
            job._gca_resource.state
            == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )
        assert job._gca_resource.training_task_inputs["timeout"] == f"{_TEST_TIMEOUT}s"
        assert (
            job._gca_resource.training_task_inputs["restart_job_on_worker_restart"]
            == _TEST_RESTART_JOB_ON_WORKER_RESTART
        )
        assert (
            job._gca_resource.training_task_inputs["disable_retries"]
            == _TEST_DISABLE_RETRIES
        )
        assert (
            job._gca_resource.training_task_inputs["max_wait_duration"]
            == f"{_TEST_MAX_WAIT_DURATION}s"
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create_with_no_model_to_upload",
        "mock_pipeline_service_get_with_no_model_to_upload",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_returns_none_if_no_model_to_upload(
        self,
        mock_tabular_dataset,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        model = job.run(
            dataset=mock_tabular_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            replica_count=1,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            sync=sync,
            create_request_timeout=None,
        )

        assert model is None

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create_with_no_model_to_upload",
        "mock_pipeline_service_get_with_no_model_to_upload",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_get_model_raises_if_no_model_to_upload(
        self,
        mock_tabular_dataset,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        job.run(
            dataset=mock_tabular_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            replica_count=1,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            job.wait()

        with pytest.raises(RuntimeError):
            job.get_model()

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_raises_if_pipeline_fails(
        self,
        mock_pipeline_service_create_and_get_with_fail,
        mock_tabular_dataset,
        sync,
    ):

        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        with pytest.raises(RuntimeError):
            job.run(
                dataset=mock_tabular_dataset,
                base_output_dir=_TEST_BASE_OUTPUT_DIR,
                args=_TEST_RUN_ARGS,
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                sync=sync,
            )

            if not sync:
                job.wait()

        with pytest.raises(RuntimeError):
            job.get_model()

    def test_raises_before_run_is_called(self, mock_pipeline_service_create):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        with pytest.raises(RuntimeError):
            job.get_model()

        with pytest.raises(RuntimeError):
            job.has_failed

        with pytest.raises(RuntimeError):
            job.state

    def test_run_raises_if_no_staging_bucket(self):

        aiplatform.init(project=_TEST_PROJECT)

        with pytest.raises(RuntimeError):
            training_jobs.CustomPythonPackageTrainingJob(
                display_name=_TEST_DISPLAY_NAME,
                python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
                python_module_name=_TEST_PYTHON_MODULE_NAME,
                container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_distributed_training(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_tabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
        )

        model_from_job = job.run(
            dataset=mock_tabular_dataset,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            replica_count=10,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            model_from_job.wait()

        true_args = _TEST_RUN_ARGS

        true_worker_pool_spec = [
            {
                "replica_count": 1,
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                },
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
                "python_package_spec": {
                    "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                    "python_module": _TEST_PYTHON_MODULE_NAME,
                    "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                    "args": true_args,
                },
            },
            {
                "replica_count": 9,
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                },
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
                "python_package_spec": {
                    "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                    "python_module": _TEST_PYTHON_MODULE_NAME,
                    "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                    "args": true_args,
                },
            },
        ]

        true_fraction_split = gca_training_pipeline.FractionSplit(
            training_fraction=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction=_TEST_TEST_FRACTION_SPLIT,
        )

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            fraction_split=true_fraction_split,
            dataset_id=mock_tabular_dataset.name,
            gcs_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_BASE_OUTPUT_DIR
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": true_worker_pool_spec,
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        assert job._gca_resource == make_training_pipeline(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        mock_model_service_get.assert_called_once_with(
            name=_TEST_MODEL_NAME, retry=base._DEFAULT_RETRY
        )

        assert model_from_job._gca_resource is mock_model_service_get.return_value

        assert job.get_model()._gca_resource is mock_model_service_get.return_value

        assert not job.has_failed

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_distributed_training_with_reduction_server(
        self,
        mock_pipeline_service_create_with_no_model_to_upload,
        mock_pipeline_service_get_with_no_model_to_upload,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        job.run(
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            replica_count=10,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            reduction_server_replica_count=_TEST_REDUCTION_SERVER_REPLICA_COUNT,
            reduction_server_machine_type=_TEST_REDUCTION_SERVER_MACHINE_TYPE,
            reduction_server_container_uri=_TEST_REDUCTION_SERVER_CONTAINER_URI,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            job.wait()

        true_args = _TEST_RUN_ARGS

        true_worker_pool_spec = [
            {
                "replica_count": 1,
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                },
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
                "python_package_spec": {
                    "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                    "python_module": _TEST_PYTHON_MODULE_NAME,
                    "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                    "args": true_args,
                },
            },
            {
                "replica_count": 9,
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                },
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
                "python_package_spec": {
                    "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                    "python_module": _TEST_PYTHON_MODULE_NAME,
                    "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                    "args": true_args,
                },
            },
            {
                "replica_count": _TEST_REDUCTION_SERVER_REPLICA_COUNT,
                "machine_spec": {"machine_type": _TEST_REDUCTION_SERVER_MACHINE_TYPE},
                "container_spec": {"image_uri": _TEST_REDUCTION_SERVER_CONTAINER_URI},
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
                },
            },
        ]

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": true_worker_pool_spec,
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
        )

        mock_pipeline_service_create_with_no_model_to_upload.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        assert job._gca_resource == make_training_pipeline_with_no_model_upload(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        assert not job.has_failed

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_nontabular_dataset_without_model_display_name_nor_model_labels(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_python_package_to_gcs,
        mock_nontabular_dataset,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
        )

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
        )

        model_from_job = job.run(
            dataset=mock_nontabular_dataset,
            annotation_schema_uri=_TEST_ANNOTATION_SCHEMA_URI,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            service_account=_TEST_SERVICE_ACCOUNT,
            tensorboard=_TEST_TENSORBOARD_RESOURCE_NAME,
            training_filter_split=_TEST_TRAINING_FILTER_SPLIT,
            validation_filter_split=_TEST_VALIDATION_FILTER_SPLIT,
            test_filter_split=_TEST_TEST_FILTER_SPLIT,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            model_from_job.wait()

        true_args = _TEST_RUN_ARGS

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": _TEST_ACCELERATOR_COUNT,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "python_package_spec": {
                "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                "python_module": _TEST_PYTHON_MODULE_NAME,
                "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                "args": true_args,
            },
        }

        true_filter_split = gca_training_pipeline.FilterSplit(
            training_filter=_TEST_TRAINING_FILTER_SPLIT,
            validation_filter=_TEST_VALIDATION_FILTER_SPLIT,
            test_filter=_TEST_TEST_FILTER_SPLIT,
        )

        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
            for key, value in _TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
        ]

        ports = [
            gca_model.Port(container_port=port)
            for port in _TEST_MODEL_SERVING_CONTAINER_PORTS
        ]

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            env=env,
            ports=ports,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_DISPLAY_NAME + "-model",
            labels=_TEST_LABELS,
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            filter_split=true_filter_split,
            dataset_id=mock_nontabular_dataset.name,
            annotation_schema_uri=_TEST_ANNOTATION_SCHEMA_URI,
            gcs_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_BASE_OUTPUT_DIR
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                    "service_account": _TEST_SERVICE_ACCOUNT,
                    "tensorboard": _TEST_TENSORBOARD_RESOURCE_NAME,
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        assert job._gca_resource == make_training_pipeline(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

        mock_model_service_get.assert_called_once_with(
            name=_TEST_MODEL_NAME, retry=base._DEFAULT_RETRY
        )

        assert model_from_job._gca_resource is mock_model_service_get.return_value

        assert job.get_model()._gca_resource is mock_model_service_get.return_value

        assert not job.has_failed

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

        assert job._has_logged_custom_job

    def test_run_call_pipeline_service_create_with_nontabular_dataset_raises_if_annotation_schema_uri(
        self,
        mock_nontabular_dataset,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
        )

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_serving_container_args=_TEST_MODEL_SERVING_CONTAINER_ARGS,
            model_serving_container_environment_variables=_TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            model_serving_container_ports=_TEST_MODEL_SERVING_CONTAINER_PORTS,
            model_description=_TEST_MODEL_DESCRIPTION,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
        )

        with pytest.raises(Exception):
            job.run(
                dataset=mock_nontabular_dataset,
                base_output_dir=_TEST_BASE_OUTPUT_DIR,
                args=_TEST_RUN_ARGS,
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
            )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create_with_persistent_resource_id",
        "mock_pipeline_service_get_with_persistent_resource_id",
        "mock_get_backing_custom_job_with_persistent_resource_id",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_persistent_resource_id(
        self, sync, caplog
    ):

        caplog.set_level(logging.INFO)

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        job.run(
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            args=_TEST_RUN_ARGS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            sync=sync,
            create_request_timeout=None,
            persistent_resource_id=_TEST_PERSISTENT_RESOURCE_ID,
        )

        if not sync:
            job.wait()

        print(caplog.text)
        assert job._gca_resource == make_training_pipeline_with_persistent_resource_id(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_pipeline_service_get",
        "mock_python_package_to_gcs",
        "mock_model_service_get",
    )
    def test_training_job_tpu_v5e(self, mock_pipeline_service_create):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_description=_TEST_MODEL_DESCRIPTION,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
        )

        job.run(
            machine_type=_TEST_MACHINE_TYPE_TPU_V5E,
            tpu_topology="2x2",
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
        )

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_DISPLAY_NAME + "-model",
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            version_aliases=["default"],
        )

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE_TPU_V5E,
                "tpu_topology": "2x2",
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "python_package_spec": {
                "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                "python_module": _TEST_PYTHON_MODULE_NAME,
                "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
            },
        }

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_pipeline_service_get",
        "mock_python_package_to_gcs",
        "mock_model_service_get",
    )
    def test_training_job_tpu_v3_pod(self, mock_pipeline_service_create):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_description=_TEST_MODEL_DESCRIPTION,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
        )

        job.run(
            machine_type=_TEST_MACHINE_TYPE_TPU,
            accelerator_type=_TEST_ACCELERATOR_TPU_TYPE,
            accelerator_count=32,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
        )

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_DISPLAY_NAME + "-model",
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            version_aliases=["default"],
        )

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE_TPU,
                "accelerator_type": _TEST_ACCELERATOR_TPU_TYPE,
                "accelerator_count": 32,
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "python_package_spec": {
                "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                "python_module": _TEST_PYTHON_MODULE_NAME,
                "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
            },
        }

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_pipeline_service_get",
        "mock_python_package_to_gcs",
        "mock_model_service_get",
    )
    def test_training_job_reservation_affinity(self, mock_pipeline_service_create):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomPythonPackageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            python_package_gcs_uri=_TEST_OUTPUT_PYTHON_PACKAGE_PATH,
            python_module_name=_TEST_PYTHON_MODULE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            model_serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            model_serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            model_serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            model_serving_container_command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
            model_description=_TEST_MODEL_DESCRIPTION,
            model_instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
            model_parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
            model_prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
        )

        job.run(
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=32,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            reservation_affinity_type="ANY_RESERVATION",
        )

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_MODEL_SERVING_CONTAINER_COMMAND,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_DISPLAY_NAME + "-model",
            description=_TEST_MODEL_DESCRIPTION,
            container_spec=true_container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_MODEL_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_MODEL_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_MODEL_PREDICTION_SCHEMA_URI,
            ),
            version_aliases=["default"],
        )

        true_worker_pool_spec = {
            "replica_count": _TEST_REPLICA_COUNT,
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": 32,
                "reservation_affinity": {
                    "reservation_affinity_type": "ANY_RESERVATION"
                },
            },
            "disk_spec": {
                "boot_disk_type": _TEST_BOOT_DISK_TYPE_DEFAULT,
                "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB_DEFAULT,
            },
            "python_package_spec": {
                "executor_image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                "python_module": _TEST_PYTHON_MODULE_NAME,
                "package_uris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
            },
        }

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "worker_pool_specs": [true_worker_pool_spec],
                    "base_output_directory": {
                        "output_uri_prefix": _TEST_BASE_OUTPUT_DIR
                    },
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )


class TestVersionedTrainingJobs:
    @pytest.mark.usefixtures("mock_pipeline_service_get")
    @pytest.mark.parametrize(
        "mock_pipeline_service_get",
        ["make_training_pipeline_with_version"],
        indirect=True,
    )
    @pytest.mark.parametrize(
        "parent,location,project,model_id",
        [
            (_TEST_ID, _TEST_LOCATION, _TEST_PROJECT, None),
            (_TEST_MODEL_NAME, None, None, None),
            (None, None, None, _TEST_ID),
        ],
    )
    @pytest.mark.parametrize(
        "aliases,default,goal",
        [
            (["alias1", "alias2"], True, ["alias1", "alias2", "default"]),
            (None, True, ["default"]),
            (["alias1", "alias2", "default"], True, ["alias1", "alias2", "default"]),
            (["alias1", "alias2", "default"], False, ["alias1", "alias2", "default"]),
            (["alias1", "alias2"], False, ["alias1", "alias2"]),
            (None, False, []),
        ],
    )
    @pytest.mark.parametrize(
        "callable",
        [
            training_jobs.CustomTrainingJob,
            training_jobs.CustomContainerTrainingJob,
            training_jobs.CustomPythonPackageTrainingJob,
        ],
    )
    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    def test_run_pipeline_for_versioned_model(
        self,
        mock_pipeline_service_create_with_version,
        mock_python_package_to_gcs,
        mock_nontabular_dataset,
        mock_model_service_get_with_version,
        parent,
        location,
        project,
        model_id,
        aliases,
        default,
        goal,
        callable,
    ):
        aiplatform.init(
            project=project,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
            location=location,
        )
        job_args = {
            "display_name": _TEST_DISPLAY_NAME,
            "model_serving_container_image_uri": _TEST_SERVING_CONTAINER_IMAGE,
            "model_serving_container_predict_route": _TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            "model_serving_container_health_route": _TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            "model_instance_schema_uri": _TEST_MODEL_INSTANCE_SCHEMA_URI,
            "model_parameters_schema_uri": _TEST_MODEL_PARAMETERS_SCHEMA_URI,
            "model_prediction_schema_uri": _TEST_MODEL_PREDICTION_SCHEMA_URI,
            "model_serving_container_command": _TEST_MODEL_SERVING_CONTAINER_COMMAND,
            "model_serving_container_args": _TEST_MODEL_SERVING_CONTAINER_ARGS,
            "model_serving_container_environment_variables": _TEST_MODEL_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            "model_serving_container_ports": _TEST_MODEL_SERVING_CONTAINER_PORTS,
            "model_description": _TEST_MODEL_DESCRIPTION,
            "labels": _TEST_LABELS,
        }

        run_args = {
            "dataset": mock_nontabular_dataset,
            "annotation_schema_uri": _TEST_ANNOTATION_SCHEMA_URI,
            "base_output_dir": _TEST_BASE_OUTPUT_DIR,
            "args": _TEST_RUN_ARGS,
            "machine_type": _TEST_MACHINE_TYPE,
            "accelerator_type": _TEST_ACCELERATOR_TYPE,
            "accelerator_count": _TEST_ACCELERATOR_COUNT,
            "training_filter_split": _TEST_TRAINING_FILTER_SPLIT,
            "validation_filter_split": _TEST_VALIDATION_FILTER_SPLIT,
            "test_filter_split": _TEST_TEST_FILTER_SPLIT,
            "create_request_timeout": None,
            "model_id": model_id,
            "parent_model": parent,
            "is_default_version": default,
            "model_version_aliases": aliases,
            "model_version_description": _TEST_MODEL_VERSION_DESCRIPTION,
        }

        if issubclass(callable, (training_jobs.CustomContainerTrainingJob)):
            job_args = {
                "container_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                **job_args,
            }
        elif issubclass(callable, (training_jobs.CustomTrainingJob)):
            job_args = {
                "container_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                "script_path": _TEST_LOCAL_SCRIPT_FILE_NAME,
                **job_args,
            }
        elif issubclass(callable, training_jobs.CustomPythonPackageTrainingJob):
            job_args = {
                "python_package_gcs_uri": _TEST_OUTPUT_PYTHON_PACKAGE_PATH,
                "python_module_name": _TEST_PYTHON_MODULE_NAME,
                "container_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                **job_args,
            }

        job = callable(**job_args)

        model_from_job = job.run(**run_args)

        mock_pipeline_service_create_with_version.assert_called_once()
        _, tp_kwargs = mock_pipeline_service_create_with_version.call_args_list[0]
        training_pipeline = tp_kwargs["training_pipeline"]

        assert training_pipeline.model_id == (model_id if model_id else "")
        assert training_pipeline.parent_model == (_TEST_MODEL_NAME if parent else "")
        assert training_pipeline.model_to_upload.version_aliases == goal
        assert (
            training_pipeline.model_to_upload.version_description
            == _TEST_MODEL_VERSION_DESCRIPTION
        )

        assert model_from_job.version_id == _TEST_MODEL_VERSION_ID
