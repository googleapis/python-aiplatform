from distutils.core import run_setup
import functools
import pathlib
import pytest
import subprocess
import shutil
import sys
import tarfile
import tempfile

from unittest import mock
from importlib import reload
from unittest.mock import patch

from google.cloud import aiplatform
from google.cloud.aiplatform.datasets import Dataset
from google.cloud.aiplatform import schema
from google.cloud.aiplatform import training_jobs
from google.cloud.aiplatform.training_jobs import _timestamped_copy_to_gcs
from google.cloud.aiplatform.training_jobs import _get_python_executable
from google.cloud.aiplatform.training_jobs import _TrainingScriptPythonPackager
from google.cloud.aiplatform_v1beta1 import FractionSplit
from google.cloud.aiplatform_v1beta1 import GcsDestination
from google.cloud.aiplatform_v1beta1 import InputDataConfig
from google.cloud.aiplatform_v1beta1 import Model
from google.cloud.aiplatform_v1beta1 import ModelContainerSpec
from google.cloud.aiplatform_v1beta1 import ModelServiceClient
from google.cloud.aiplatform_v1beta1 import PipelineServiceClient
from google.cloud.aiplatform_v1beta1 import PipelineState
from google.cloud.aiplatform_v1beta1 import TrainingPipeline

from google.cloud.aiplatform import initializer
from google.cloud import storage

from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value


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

_TEST_DISPLAY_NAME = "test-display-name"
_TEST_TRAINING_CONTAINER_IMAGE = "gcr.io/test-training/container:image"
_TEST_SERVING_CONTAINER_IMAGE = "gcr.io/test-serving/container:image"
_TEST_SERVING_CONTAINER_PREDICTION_ROUTE = "predict"
_TEST_SERVING_CONTAINER_HEALTH_ROUTE = "metadata"

_TEST_DATASET_NAME = "test-dataset-name"
_TEST_BASE_OUTPUT_DIR = "gs://test-base-output-dir"
_TEST_RUN_ARGS = {"test": "arg", "foo": 1}
_TEST_REPLICA_COUNT = 1
_TEST_MACHINE_TYPE = "n1-standard-4"
_TEST_ACCELERATOR_TYPE = "NVIDIA_TESLA_K80"
_TEST_INVALID_ACCELERATOR_TYPE = "NVIDIA_DOES_NOT_EXIST"
_TEST_ACCELERATOR_COUNT = 1
_TEST_MODEL_DISPLAY_NAME = "model-display-name"
_TEST_TRAINING_FRACTION_SPLIT = 0.6
_TEST_VALIDATION_FRACTION_SPLIT = 0.2
_TEST_TEST_FRACTION_SPLIT = 0.2

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
        reload(initializer)
        reload(aiplatform)

    def test_timestamp_copy_to_gcs_calls_gcs_client_with_bucket(
        self, mock_client_bucket
    ):

        mock_client_bucket, mock_blob = mock_client_bucket

        gcs_path = _timestamped_copy_to_gcs(
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

        gcs_path = _timestamped_copy_to_gcs(
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

        gcs_path = _timestamped_copy_to_gcs(
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

        gcs_path = _timestamped_copy_to_gcs(
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
                _get_python_executable()

    def test_get_python_executable_returns_python_executable(self):
        assert "python" in _get_python_executable().lower()


class TestTrainingScriptPythonPackager:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)
        with open(_TEST_LOCAL_SCRIPT_FILE_NAME, "w") as fp:
            fp.write(_TEST_PYTHON_SOURCE)

    def teardown_method(self):
        pathlib.Path(_TEST_LOCAL_SCRIPT_FILE_NAME).unlink()
        python_package_file = f"{_TrainingScriptPythonPackager._ROOT_MODULE}-{_TrainingScriptPythonPackager._SETUP_PY_VERSION}.tar.gz"
        if pathlib.Path(python_package_file).is_file():
            pathlib.Path(python_package_file).unlink()
        subprocess.check_output(
            ["pip3", "uninstall", "-y", _TrainingScriptPythonPackager._ROOT_MODULE]
        )

    def test_packager_creates_and_copies_python_package(self):
        tsp = _TrainingScriptPythonPackager(_TEST_LOCAL_SCRIPT_FILE_NAME)
        tsp.package_and_copy(copy_method=local_copy_method)
        assert pathlib.Path(
            f"{tsp._ROOT_MODULE}-{tsp._SETUP_PY_VERSION}.tar.gz"
        ).is_file()

    def test_created_package_module_is_installable_and_can_be_run(self):
        tsp = _TrainingScriptPythonPackager(_TEST_LOCAL_SCRIPT_FILE_NAME)
        source_dist_path = tsp.package_and_copy(copy_method=local_copy_method)
        subprocess.check_output(["pip3", "install", source_dist_path])
        module_output = subprocess.check_output(
            [_get_python_executable(), "-m", tsp.module_name]
        )
        assert "hello world" in module_output.decode()

    def test_requirements_are_in_package(self):
        tsp = _TrainingScriptPythonPackager(
            _TEST_LOCAL_SCRIPT_FILE_NAME, requirements=_TEST_REQUIREMENTS
        )
        source_dist_path = tsp.package_and_copy(copy_method=local_copy_method)
        with tarfile.open(source_dist_path) as tf:
            with tempfile.TemporaryDirectory() as tmpdirname:
                setup_py_path = f"{_TrainingScriptPythonPackager._ROOT_MODULE}-{_TrainingScriptPythonPackager._SETUP_PY_VERSION}/setup.py"
                tf.extract(setup_py_path, path=tmpdirname)
                setup_py = run_setup(
                    pathlib.Path(tmpdirname, setup_py_path), stop_after="init"
                )
                assert _TEST_REQUIREMENTS == setup_py.install_requires

    def test_packaging_fails_whith_RuntimeError(self):
        with patch("subprocess.Popen") as mock_popen:
            mock_subprocess = mock.Mock()
            mock_subprocess.communicate.return_value = (b"", b"")
            mock_subprocess.returncode = 1
            mock_popen.return_value = mock_subprocess
            tsp = _TrainingScriptPythonPackager(_TEST_LOCAL_SCRIPT_FILE_NAME)
            with pytest.raises(RuntimeError):
                tsp.package_and_copy(copy_method=local_copy_method)

    def test_package_and_copy_to_gcs_copies_to_gcs(self, mock_client_bucket):
        mock_client_bucket, mock_blob = mock_client_bucket

        tsp = _TrainingScriptPythonPackager(_TEST_LOCAL_SCRIPT_FILE_NAME)

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


class TestCustomTrainingJob:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)
        with open(_TEST_LOCAL_SCRIPT_FILE_NAME, "w") as fp:
            fp.write(_TEST_PYTHON_SOURCE)

    def teardown_method(self):
        pathlib.Path(_TEST_LOCAL_SCRIPT_FILE_NAME).unlink()

    @pytest.fixture
    def mock_pipeline_service_create(self):
        with mock.patch.object(
            PipelineServiceClient, "create_training_pipeline"
        ) as mock_create_training_pipeline:
            mock_create_training_pipeline.return_value = TrainingPipeline(
                name=_TEST_PIPELINE_RESOURCE_NAME,
                state=PipelineState.PIPELINE_STATE_SUCCEEDED,
                model_to_upload=Model(name=_TEST_MODEL_NAME),
            )
            yield mock_create_training_pipeline

    @pytest.fixture
    def mock_pipeline_service_create_with_no_model_to_upload(self):
        with mock.patch.object(
            PipelineServiceClient, "create_training_pipeline"
        ) as mock_create_training_pipeline:
            mock_create_training_pipeline.return_value = TrainingPipeline(
                name=_TEST_PIPELINE_RESOURCE_NAME,
                state=PipelineState.PIPELINE_STATE_SUCCEEDED,
            )
            yield mock_create_training_pipeline

    @pytest.fixture
    def mock_pipeline_service_create_and_get_with_fail(self):
        with mock.patch.object(
            PipelineServiceClient, "create_training_pipeline"
        ) as mock_create_training_pipeline:
            mock_create_training_pipeline.return_value = TrainingPipeline(
                name=_TEST_PIPELINE_RESOURCE_NAME,
                state=PipelineState.PIPELINE_STATE_RUNNING,
            )

            with mock.patch.object(
                PipelineServiceClient, "get_training_pipeline"
            ) as mock_get_training_pipeline:
                mock_get_training_pipeline.return_value = TrainingPipeline(
                    name=_TEST_PIPELINE_RESOURCE_NAME,
                    state=PipelineState.PIPELINE_STATE_FAILED,
                )

                yield mock_create_training_pipeline, mock_get_training_pipeline

    @pytest.fixture
    def mock_model_service_get(self):
        with mock.patch.object(ModelServiceClient, "get_model") as mock_get_model:
            mock_get_model.return_value = Model()
            yield mock_get_model

    @pytest.fixture
    def mock_python_package_to_gcs(self):
        with mock.patch.object(
            _TrainingScriptPythonPackager, "package_and_copy_to_gcs"
        ) as mock_package_to_copy_gcs:
            mock_package_to_copy_gcs.return_value = _TEST_OUTPUT_PYTHON_PACKAGE_PATH
            yield mock_package_to_copy_gcs

    @pytest.fixture
    def mock_dataset(self):
        ds = mock.MagicMock(Dataset)
        ds.name = _TEST_DATASET_NAME
        return ds

    def test_run_call_pipeline_service_create(
        self,
        mock_pipeline_service_create,
        mock_python_package_to_gcs,
        mock_dataset,
        mock_model_service_get,
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
        )

        mock_python_package_to_gcs.assert_called_once_with(
            gcs_staging_dir=_TEST_BUCKET_NAME,
            project=_TEST_PROJECT,
            credentials=initializer.global_config.credentials,
        )

        true_args = ["--test=arg", "--foo=1"]

        true_worker_pool_spec = {
            "replicaCount": _TEST_REPLICA_COUNT,
            "machineSpec": {
                "machineType": _TEST_MACHINE_TYPE,
                "acceleratorType": _TEST_ACCELERATOR_TYPE,
                "acceleratorCount": _TEST_ACCELERATOR_COUNT,
            },
            "pythonPackageSpec": {
                "executorImageUri": _TEST_TRAINING_CONTAINER_IMAGE,
                "pythonModule": _TrainingScriptPythonPackager.module_name,
                "packageUris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                "args": true_args,
            },
        }

        true_fraction_split = FractionSplit(
            training_fraction=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction=_TEST_TEST_FRACTION_SPLIT,
        )

        true_container_spec = ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        true_managed_model = Model(
            display_name=_TEST_MODEL_DISPLAY_NAME, container_spec=true_container_spec
        )

        true_input_data_config = InputDataConfig(
            fraction_split=true_fraction_split,
            dataset_id=mock_dataset.name,
            gcs_destination=GcsDestination(output_uri_prefix=_TEST_BASE_OUTPUT_DIR),
        )

        true_training_pipeline = TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "workerPoolSpecs": [true_worker_pool_spec],
                    "baseOutputDirectory": {"output_uri_prefix": _TEST_BASE_OUTPUT_DIR},
                },
                Value(),
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

        assert not job.is_failed

        assert job.state == PipelineState.PIPELINE_STATE_SUCCEEDED

    def test_run_called_twice_raises(
        self,
        mock_pipeline_service_create,
        mock_python_package_to_gcs,
        mock_dataset,
        mock_model_service_get,
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
            )

    def test_run_with_invalid_accelerator_type_raises(
        self,
        mock_pipeline_service_create,
        mock_python_package_to_gcs,
        mock_dataset,
        mock_model_service_get,
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
            )

    def test_run_with_incomplete_model_info_raises_with_model_to_upload(
        self,
        mock_pipeline_service_create,
        mock_python_package_to_gcs,
        mock_dataset,
        mock_model_service_get,
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
            )

    def test_run_call_pipeline_service_create_with_no_dataset(
        self,
        mock_pipeline_service_create,
        mock_python_package_to_gcs,
        mock_model_service_get,
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
        )

        mock_python_package_to_gcs.assert_called_once_with(
            gcs_staging_dir=_TEST_BUCKET_NAME,
            project=_TEST_PROJECT,
            credentials=initializer.global_config.credentials,
        )

        true_args = ["--test=arg", "--foo=1"]

        true_worker_pool_spec = {
            "replicaCount": _TEST_REPLICA_COUNT,
            "machineSpec": {
                "machineType": _TEST_MACHINE_TYPE,
                "acceleratorType": _TEST_ACCELERATOR_TYPE,
                "acceleratorCount": _TEST_ACCELERATOR_COUNT,
            },
            "pythonPackageSpec": {
                "executorImageUri": _TEST_TRAINING_CONTAINER_IMAGE,
                "pythonModule": _TrainingScriptPythonPackager.module_name,
                "packageUris": [_TEST_OUTPUT_PYTHON_PACKAGE_PATH],
                "args": true_args,
            },
        }

        true_container_spec = ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        true_managed_model = Model(
            display_name=_TEST_MODEL_DISPLAY_NAME, container_spec=true_container_spec
        )

        true_training_pipeline = TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.custom_task,
            training_task_inputs=json_format.ParseDict(
                {
                    "workerPoolSpecs": [true_worker_pool_spec],
                    "baseOutputDirectory": {"output_uri_prefix": _TEST_BASE_OUTPUT_DIR},
                },
                Value(),
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

    def test_run_returns_none_if_no_model_to_upload(
        self,
        mock_pipeline_service_create_with_no_model_to_upload,
        mock_python_package_to_gcs,
        mock_dataset,
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
        )

        assert model is None

    def test_get_model_raises_if_no_model_to_upload(
        self,
        mock_pipeline_service_create_with_no_model_to_upload,
        mock_python_package_to_gcs,
        mock_dataset,
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
        )

        with pytest.raises(RuntimeError):
            model = job.get_model()

    def test_run_raises_if_pipeline_fails(
        self,
        mock_pipeline_service_create_and_get_with_fail,
        mock_python_package_to_gcs,
        mock_dataset,
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
            )

        with pytest.raises(RuntimeError):
            model = job.get_model()

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
            job.is_failed

        with pytest.raises(RuntimeError):
            job.state

    def test_run_raises_if_no_staging_bucket(self):

        aiplatform.init(project=_TEST_PROJECT)

        job = training_jobs.CustomTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            script_path=_TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
        )

        with pytest.raises(RuntimeError):
            job.run(
                base_output_dir=_TEST_BASE_OUTPUT_DIR,
                args=_TEST_RUN_ARGS,
                replica_count=1,
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                training_fraction_split=_TEST_TRAINING_FRACTION_SPLIT,
                validation_fraction_split=_TEST_VALIDATION_FRACTION_SPLIT,
                test_fraction_split=_TEST_TEST_FRACTION_SPLIT,
            )
