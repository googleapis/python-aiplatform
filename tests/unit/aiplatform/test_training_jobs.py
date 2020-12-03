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

from distutils import core
import functools
import importlib
import pathlib
import pytest
import subprocess
import shutil
import sys
import tarfile
import tempfile
from unittest import mock
from unittest.mock import patch

from google.cloud import aiplatform
from google.cloud.aiplatform import datasets
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import schema
from google.cloud.aiplatform import training_jobs
from google.cloud.aiplatform_v1beta1.services.model_service import (
    client as model_service_client,
)
from google.cloud.aiplatform_v1beta1.services.pipeline_service import (
    client as pipeline_service_client,
)
from google.cloud.aiplatform_v1beta1.types import io as gca_io
from google.cloud.aiplatform_v1beta1.types import model as gca_model
from google.cloud.aiplatform_v1beta1.types import pipeline_state as gca_pipeline_state
from google.cloud.aiplatform_v1beta1.types import (
    training_pipeline as gca_training_pipeline,
)
from google.cloud.aiplatform_v1beta1 import Dataset as GapicDataset

from google.cloud import storage
from google.protobuf import json_format
from google.protobuf import struct_pb2


_TEST_BUCKET_NAME = "test-bucket"
_TEST_GCS_PATH_WITHOUT_BUCKET = "path/to/folder"
_TEST_GCS_PATH = f"{_TEST_BUCKET_NAME}/{_TEST_GCS_PATH_WITHOUT_BUCKET}"
_TEST_GCS_PATH_WITH_TRAILING_SLASH = f"{_TEST_GCS_PATH}/"
_TEST_LOCAL_SCRIPT_FILE_NAME = "____test____script.py"
_TEST_LOCAL_SCRIPT_FILE_PATH = f"path/to/{_TEST_LOCAL_SCRIPT_FILE_NAME}"
_TEST_PROJECT = "test-project"
_TEST_PYTHON_SOURCE = """
print('hello world')
"""
_TEST_REQUIREMENTS = ["pandas", "numpy", "tensorflow"]

_TEST_DATASET_DISPLAY_NAME = "test-dataset-display-name"
_TEST_DATASET_NAME = "test-dataset-name"
_TEST_DISPLAY_NAME = "test-display-name"
_TEST_METADATA_SCHEMA_URI_TABULAR = schema.dataset.metadata.tabular
_TEST_TRAINING_CONTAINER_IMAGE = "gcr.io/test-training/container:image"
_TEST_SERVING_CONTAINER_IMAGE = "gcr.io/test-serving/container:image"
_TEST_SERVING_CONTAINER_PREDICTION_ROUTE = "predict"
_TEST_SERVING_CONTAINER_HEALTH_ROUTE = "metadata"

_TEST_DATASET_NAME = "test-dataset-name"
_TEST_BASE_OUTPUT_DIR = "gs://test-base-output-dir"
_TEST_RUN_ARGS = ["-v", 0.1, "--test=arg"]
_TEST_REPLICA_COUNT = 1
_TEST_MACHINE_TYPE = "n1-standard-4"
_TEST_ACCELERATOR_TYPE = "NVIDIA_TESLA_K80"
_TEST_INVALID_ACCELERATOR_TYPE = "NVIDIA_DOES_NOT_EXIST"
_TEST_ACCELERATOR_COUNT = 1
_TEST_MODEL_DISPLAY_NAME = "model-display-name"
_TEST_TRAINING_FRACTION_SPLIT = 0.6
_TEST_VALIDATION_FRACTION_SPLIT = 0.2
_TEST_TEST_FRACTION_SPLIT = 0.2
_TEST_PREDEFINED_SPLIT_COLUMN_NAME = "split"

_TEST_OUTPUT_PYTHON_PACKAGE_PATH = "gs://test/ouput/python/trainer.tar.gz"

_TEST_MODEL_NAME = "projects/my-project/locations/us-central1/models/12345"

_TEST_PIPELINE_RESOURCE_NAME = (
    "projects/my-project/locations/us-central1/trainingPipeline/12345"
)


def local_copy_method(path):
    shutil.copy(path, ".")
    return pathlib.Path(path).name


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


class TestTrainingScriptPythonPackagerHelpers:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)

    def test_timestamp_copy_to_gcs_calls_gcs_client_with_bucket(
        self, mock_client_bucket
    ):

        mock_client_bucket, mock_blob = mock_client_bucket

        gcs_path = training_jobs._timestamped_copy_to_gcs(
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

        gcs_path = training_jobs._timestamped_copy_to_gcs(
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

        gcs_path = training_jobs._timestamped_copy_to_gcs(
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

        gcs_path = training_jobs._timestamped_copy_to_gcs(
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
                training_jobs._get_python_executable()

    def test_get_python_executable_returns_python_executable(self):
        assert "python" in training_jobs._get_python_executable().lower()


class TestTrainingScriptPythonPackager:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        with open(_TEST_LOCAL_SCRIPT_FILE_NAME, "w") as fp:
            fp.write(_TEST_PYTHON_SOURCE)

    def teardown_method(self):
        pathlib.Path(_TEST_LOCAL_SCRIPT_FILE_NAME).unlink()
        python_package_file = f"{training_jobs._TrainingScriptPythonPackager._ROOT_MODULE}-{training_jobs._TrainingScriptPythonPackager._SETUP_PY_VERSION}.tar.gz"
        if pathlib.Path(python_package_file).is_file():
            pathlib.Path(python_package_file).unlink()
        subprocess.check_output(
            [
                "pip3",
                "uninstall",
                "-y",
                training_jobs._TrainingScriptPythonPackager._ROOT_MODULE,
            ]
        )

    def test_packager_creates_and_copies_python_package(self):
        tsp = training_jobs._TrainingScriptPythonPackager(_TEST_LOCAL_SCRIPT_FILE_NAME)
        tsp.package_and_copy(copy_method=local_copy_method)
        assert pathlib.Path(
            f"{tsp._ROOT_MODULE}-{tsp._SETUP_PY_VERSION}.tar.gz"
        ).is_file()

    def test_created_package_module_is_installable_and_can_be_run(self):
        tsp = training_jobs._TrainingScriptPythonPackager(_TEST_LOCAL_SCRIPT_FILE_NAME)
        source_dist_path = tsp.package_and_copy(copy_method=local_copy_method)
        subprocess.check_output(["pip3", "install", source_dist_path])
        module_output = subprocess.check_output(
            [training_jobs._get_python_executable(), "-m", tsp.module_name]
        )
        assert "hello world" in module_output.decode()

    def test_requirements_are_in_package(self):
        tsp = training_jobs._TrainingScriptPythonPackager(
            _TEST_LOCAL_SCRIPT_FILE_NAME, requirements=_TEST_REQUIREMENTS
        )
        source_dist_path = tsp.package_and_copy(copy_method=local_copy_method)
        with tarfile.open(source_dist_path) as tf:
            with tempfile.TemporaryDirectory() as tmpdirname:
                setup_py_path = f"{training_jobs._TrainingScriptPythonPackager._ROOT_MODULE}-{training_jobs._TrainingScriptPythonPackager._SETUP_PY_VERSION}/setup.py"
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
            tsp = training_jobs._TrainingScriptPythonPackager(
                _TEST_LOCAL_SCRIPT_FILE_NAME
            )
            with pytest.raises(RuntimeError):
                tsp.package_and_copy(copy_method=local_copy_method)

    def test_package_and_copy_to_gcs_copies_to_gcs(self, mock_client_bucket):
        mock_client_bucket, mock_blob = mock_client_bucket

        tsp = training_jobs._TrainingScriptPythonPackager(_TEST_LOCAL_SCRIPT_FILE_NAME)

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
        mock_create_training_pipeline.return_value = gca_training_pipeline.TrainingPipeline(
            name=_TEST_PIPELINE_RESOURCE_NAME,
            state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            model_to_upload=gca_model.Model(name=_TEST_MODEL_NAME),
        )
        yield mock_create_training_pipeline


@pytest.fixture
def mock_pipeline_service_create_with_no_model_to_upload():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_training_pipeline"
    ) as mock_create_training_pipeline:
        mock_create_training_pipeline.return_value = gca_training_pipeline.TrainingPipeline(
            name=_TEST_PIPELINE_RESOURCE_NAME,
            state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
        )
        yield mock_create_training_pipeline


@pytest.fixture
def mock_pipeline_service_create_and_get_with_fail():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_training_pipeline"
    ) as mock_create_training_pipeline:
        mock_create_training_pipeline.return_value = gca_training_pipeline.TrainingPipeline(
            name=_TEST_PIPELINE_RESOURCE_NAME,
            state=gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
        )

        with mock.patch.object(
            pipeline_service_client.PipelineServiceClient, "get_training_pipeline"
        ) as mock_get_training_pipeline:
            mock_get_training_pipeline.return_value = gca_training_pipeline.TrainingPipeline(
                name=_TEST_PIPELINE_RESOURCE_NAME,
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_FAILED,
            )

            yield mock_create_training_pipeline, mock_get_training_pipeline


@pytest.fixture
def mock_model_service_get():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as mock_get_model:
        mock_get_model.return_value = gca_model.Model()
        yield mock_get_model


@pytest.fixture
def mock_python_package_to_gcs():
    with mock.patch.object(
        training_jobs._TrainingScriptPythonPackager, "package_and_copy_to_gcs"
    ) as mock_package_to_copy_gcs:
        mock_package_to_copy_gcs.return_value = _TEST_OUTPUT_PYTHON_PACKAGE_PATH
        yield mock_package_to_copy_gcs


@pytest.fixture
def mock_dataset():
    ds = mock.MagicMock(datasets.Dataset)
    ds.name = _TEST_DATASET_NAME
    ds._latest_future = None
    ds._gca_resource = GapicDataset(
        display_name=_TEST_DATASET_DISPLAY_NAME,
        metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TABULAR,
        labels={},
        name=_TEST_DATASET_NAME,
        metadata={},
    )
    return ds


class TestCustomTrainingJob:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        with open(_TEST_LOCAL_SCRIPT_FILE_NAME, "w") as fp:
            fp.write(_TEST_PYTHON_SOURCE)

    def teardown_method(self):
        pathlib.Path(_TEST_LOCAL_SCRIPT_FILE_NAME).unlink()

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create(
        self,
        mock_pipeline_service_create,
        mock_python_package_to_gcs,
        mock_dataset,
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

        model_from_job = job.run(
            dataset=mock_dataset,
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
            predefined_split_column_name=_TEST_PREDEFINED_SPLIT_COLUMN_NAME,
            sync=sync,
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
            "replicaCount": _TEST_REPLICA_COUNT,
            "machineSpec": {
                "machineType": _TEST_MACHINE_TYPE,
                "acceleratorType": _TEST_ACCELERATOR_TYPE,
                "acceleratorCount": _TEST_ACCELERATOR_COUNT,
            },
            "pythonPackageSpec": {
                "executorImageUri": _TEST_TRAINING_CONTAINER_IMAGE,
                "pythonModule": training_jobs._TrainingScriptPythonPackager.module_name,
                "packageUris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                "args": true_args,
            },
        }

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
            display_name=_TEST_MODEL_DISPLAY_NAME, container_spec=true_container_spec
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            fraction_split=true_fraction_split,
            predefined_split=gca_training_pipeline.PredefinedSplit(
                key=_TEST_PREDEFINED_SPLIT_COLUMN_NAME
            ),
            dataset_id=mock_dataset.name,
            gcs_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_BASE_OUTPUT_DIR
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "workerPoolSpecs": [true_worker_pool_spec],
                    "baseOutputDirectory": {"output_uri_prefix": _TEST_BASE_OUTPUT_DIR},
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
        )

        assert job._gca_resource is mock_pipeline_service_create.return_value

        mock_model_service_get.assert_called_once_with(name=_TEST_MODEL_NAME)

        assert model_from_job._gca_resource is mock_model_service_get.return_value

        assert job.get_model()._gca_resource is mock_model_service_get.return_value

        assert not job.has_failed

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_called_twice_raises(
        self,
        mock_pipeline_service_create,
        mock_python_package_to_gcs,
        mock_dataset,
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

        job.run(
            dataset=mock_dataset,
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
        )

        with pytest.raises(RuntimeError):
            job.run(
                dataset=mock_dataset,
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
            )

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_with_invalid_accelerator_type_raises(
        self,
        mock_pipeline_service_create,
        mock_python_package_to_gcs,
        mock_dataset,
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
                dataset=mock_dataset,
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
            )

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_with_incomplete_model_info_raises_with_model_to_upload(
        self,
        mock_pipeline_service_create,
        mock_python_package_to_gcs,
        mock_dataset,
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
                dataset=mock_dataset,
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
            )

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_no_dataset(
        self,
        mock_pipeline_service_create,
        mock_python_package_to_gcs,
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

        model_from_job = job.run(
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
            "replicaCount": _TEST_REPLICA_COUNT,
            "machineSpec": {
                "machineType": _TEST_MACHINE_TYPE,
                "acceleratorType": _TEST_ACCELERATOR_TYPE,
                "acceleratorCount": _TEST_ACCELERATOR_COUNT,
            },
            "pythonPackageSpec": {
                "executorImageUri": _TEST_TRAINING_CONTAINER_IMAGE,
                "pythonModule": training_jobs._TrainingScriptPythonPackager.module_name,
                "packageUris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                "args": true_args,
            },
        }

        true_container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME, container_spec=true_container_spec
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "workerPoolSpecs": [true_worker_pool_spec],
                    "baseOutputDirectory": {"output_uri_prefix": _TEST_BASE_OUTPUT_DIR},
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
        )

        assert job._gca_resource is mock_pipeline_service_create.return_value

        mock_model_service_get.assert_called_once_with(name=_TEST_MODEL_NAME)

        assert model_from_job._gca_resource is mock_model_service_get.return_value

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_returns_none_if_no_model_to_upload(
        self,
        mock_pipeline_service_create_with_no_model_to_upload,
        mock_python_package_to_gcs,
        mock_dataset,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        model = job.run(
            dataset=mock_dataset,
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
        )

        assert model is None

    @pytest.mark.parametrize("sync", [True, False])
    def test_get_model_raises_if_no_model_to_upload(
        self,
        mock_pipeline_service_create_with_no_model_to_upload,
        mock_python_package_to_gcs,
        mock_dataset,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        job.run(
            dataset=mock_dataset,
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
        mock_dataset,
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
                dataset=mock_dataset,
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

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_distributed_training(
        self,
        mock_pipeline_service_create,
        mock_python_package_to_gcs,
        mock_dataset,
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

        model_from_job = job.run(
            dataset=mock_dataset,
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
        )

        if not sync:
            model_from_job.wait()

        mock_python_package_to_gcs.assert_called_once_with(
            gcs_staging_dir=_TEST_BUCKET_NAME,
            project=_TEST_PROJECT,
            credentials=initializer.global_config.credentials,
        )

        true_args = _TEST_RUN_ARGS

        true_worker_pool_spec = [
            {
                "replicaCount": 1,
                "machineSpec": {
                    "machineType": _TEST_MACHINE_TYPE,
                    "acceleratorType": _TEST_ACCELERATOR_TYPE,
                    "acceleratorCount": _TEST_ACCELERATOR_COUNT,
                },
                "pythonPackageSpec": {
                    "executorImageUri": _TEST_TRAINING_CONTAINER_IMAGE,
                    "pythonModule": training_jobs._TrainingScriptPythonPackager.module_name,
                    "packageUris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                    "args": true_args,
                },
            },
            {
                "replicaCount": 9,
                "machineSpec": {
                    "machineType": _TEST_MACHINE_TYPE,
                    "acceleratorType": _TEST_ACCELERATOR_TYPE,
                    "acceleratorCount": _TEST_ACCELERATOR_COUNT,
                },
                "pythonPackageSpec": {
                    "executorImageUri": _TEST_TRAINING_CONTAINER_IMAGE,
                    "pythonModule": training_jobs._TrainingScriptPythonPackager.module_name,
                    "packageUris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
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
            display_name=_TEST_MODEL_DISPLAY_NAME, container_spec=true_container_spec
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            fraction_split=true_fraction_split,
            dataset_id=mock_dataset.name,
            gcs_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_BASE_OUTPUT_DIR
            ),
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "workerPoolSpecs": true_worker_pool_spec,
                    "baseOutputDirectory": {"output_uri_prefix": _TEST_BASE_OUTPUT_DIR},
                },
                struct_pb2.Value(),
            ),
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
        )

        assert job._gca_resource is mock_pipeline_service_create.return_value

        mock_model_service_get.assert_called_once_with(name=_TEST_MODEL_NAME)

        assert model_from_job._gca_resource is mock_model_service_get.return_value

        assert job.get_model()._gca_resource is mock_model_service_get.return_value

        assert not job.has_failed

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED


class Test_MachineSpec:
    def test_machine_spec_return_spec_dict(self):
        test_spec = training_jobs._MachineSpec(
            replica_count=_TEST_REPLICA_COUNT,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
        )

        true_spec_dict = {
            "machineSpec": {
                "machineType": _TEST_MACHINE_TYPE,
                "acceleratorType": _TEST_ACCELERATOR_TYPE,
                "acceleratorCount": _TEST_ACCELERATOR_COUNT,
            },
            "replicaCount": _TEST_REPLICA_COUNT,
        }

        assert test_spec.spec_dict == true_spec_dict

    def test_machine_spec_return_spec_dict_with_no_accelerator(self):
        test_spec = training_jobs._MachineSpec(
            replica_count=_TEST_REPLICA_COUNT,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_count=0,
            accelerator_type="ACCELERATOR_TYPE_UNSPECIFIED",
        )

        true_spec_dict = {
            "machineSpec": {"machineType": _TEST_MACHINE_TYPE},
            "replicaCount": _TEST_REPLICA_COUNT,
        }

        assert test_spec.spec_dict == true_spec_dict

    def test_machine_spec_spec_dict_raises_invalid_accelerator(self):
        test_spec = training_jobs._MachineSpec(
            replica_count=_TEST_REPLICA_COUNT,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            accelerator_type=_TEST_INVALID_ACCELERATOR_TYPE,
        )

        with pytest.raises(ValueError):
            test_spec.spec_dict

    def test_machine_spec_spec_dict_is_empty(self):
        test_spec = training_jobs._MachineSpec(
            replica_count=0,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            accelerator_type=_TEST_INVALID_ACCELERATOR_TYPE,
        )

        assert test_spec.is_empty

    def test_machine_spec_spec_dict_is_not_empty(self):
        test_spec = training_jobs._MachineSpec(
            replica_count=_TEST_REPLICA_COUNT,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            accelerator_type=_TEST_INVALID_ACCELERATOR_TYPE,
        )

        assert not test_spec.is_empty


class Test_DistributedTrainingSpec:
    def test_machine_spec_returns_pool_spec(self):

        spec = training_jobs._DistributedTrainingSpec(
            chief_spec=training_jobs._MachineSpec(
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
            ),
            worker_spec=training_jobs._MachineSpec(
                replica_count=10,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
            ),
            parameter_server_spec=training_jobs._MachineSpec(
                replica_count=3,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
            ),
            evaluator_spec=training_jobs._MachineSpec(
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
            ),
        )

        true_pool_spec = [
            {
                "machineSpec": {
                    "machineType": _TEST_MACHINE_TYPE,
                    "acceleratorType": _TEST_ACCELERATOR_TYPE,
                    "acceleratorCount": _TEST_ACCELERATOR_COUNT,
                },
                "replicaCount": 1,
            },
            {
                "machineSpec": {
                    "machineType": _TEST_MACHINE_TYPE,
                    "acceleratorType": _TEST_ACCELERATOR_TYPE,
                    "acceleratorCount": _TEST_ACCELERATOR_COUNT,
                },
                "replicaCount": 10,
            },
            {
                "machineSpec": {
                    "machineType": _TEST_MACHINE_TYPE,
                    "acceleratorType": _TEST_ACCELERATOR_TYPE,
                    "acceleratorCount": _TEST_ACCELERATOR_COUNT,
                },
                "replicaCount": 3,
            },
            {
                "machineSpec": {
                    "machineType": _TEST_MACHINE_TYPE,
                    "acceleratorType": _TEST_ACCELERATOR_TYPE,
                    "acceleratorCount": _TEST_ACCELERATOR_COUNT,
                },
                "replicaCount": 1,
            },
        ]

        assert spec.pool_specs == true_pool_spec

    def test_chief_worker_pool_returns_spec(self):

        chief_worker_spec = training_jobs._DistributedTrainingSpec.chief_worker_pool(
            replica_count=10,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
        )

        true_pool_spec = [
            {
                "machineSpec": {
                    "machineType": _TEST_MACHINE_TYPE,
                    "acceleratorType": _TEST_ACCELERATOR_TYPE,
                    "acceleratorCount": _TEST_ACCELERATOR_COUNT,
                },
                "replicaCount": 1,
            },
            {
                "machineSpec": {
                    "machineType": _TEST_MACHINE_TYPE,
                    "acceleratorType": _TEST_ACCELERATOR_TYPE,
                    "acceleratorCount": _TEST_ACCELERATOR_COUNT,
                },
                "replicaCount": 9,
            },
        ]

        assert chief_worker_spec.pool_specs == true_pool_spec

    def test_chief_worker_pool_returns_just_chief(self):

        chief_worker_spec = training_jobs._DistributedTrainingSpec.chief_worker_pool(
            replica_count=1,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
        )

        true_pool_spec = [
            {
                "machineSpec": {
                    "machineType": _TEST_MACHINE_TYPE,
                    "acceleratorType": _TEST_ACCELERATOR_TYPE,
                    "acceleratorCount": _TEST_ACCELERATOR_COUNT,
                },
                "replicaCount": 1,
            }
        ]

        assert chief_worker_spec.pool_specs == true_pool_spec

    def test_machine_spec_raise_with_more_than_one_chief_replica(self):

        spec = training_jobs._DistributedTrainingSpec(
            chief_spec=training_jobs._MachineSpec(
                replica_count=2,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
            ),
        )

        with pytest.raises(ValueError):
            spec.pool_specs

    def test_machine_spec_handles_missing_pools(self):

        spec = training_jobs._DistributedTrainingSpec(
            chief_spec=training_jobs._MachineSpec(
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
            ),
            worker_spec=training_jobs._MachineSpec(replica_count=0),
            parameter_server_spec=training_jobs._MachineSpec(
                replica_count=3,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
            ),
            evaluator_spec=training_jobs._MachineSpec(replica_count=0),
        )

        true_pool_spec = [
            {
                "machineSpec": {
                    "machineType": _TEST_MACHINE_TYPE,
                    "acceleratorType": _TEST_ACCELERATOR_TYPE,
                    "acceleratorCount": _TEST_ACCELERATOR_COUNT,
                },
                "replicaCount": 1,
            },
            {"machineSpec": {"machineType": "n1-standard-4"}, "replicaCount": 0},
            {
                "machineSpec": {
                    "machineType": _TEST_MACHINE_TYPE,
                    "acceleratorType": _TEST_ACCELERATOR_TYPE,
                    "acceleratorCount": _TEST_ACCELERATOR_COUNT,
                },
                "replicaCount": 3,
            },
        ]

        assert spec.pool_specs == true_pool_spec
