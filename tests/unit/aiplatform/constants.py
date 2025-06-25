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

# Use this file to store global variables that will be shared across multiple tests

import dataclasses
from datetime import datetime
from unittest import mock
from google.auth import credentials as auth_credentials
from google.protobuf import timestamp_pb2, duration_pb2

from google.cloud.aiplatform.utils import source_utils
from google.cloud.aiplatform import explain
from google.cloud.aiplatform import utils
from google.cloud.aiplatform import schema
from google.cloud.aiplatform.metadata import constants as metadata_constants

from google.cloud.aiplatform.compat.services import (
    model_service_client,
)

from google.cloud.aiplatform.compat.types import (
    context,
    custom_job,
    encryption_spec,
    endpoint,
    io,
    model,
    tensorboard_data,
    tensorboard_experiment,
    tensorboard_run,
    tensorboard_time_series,
)


@dataclasses.dataclass(frozen=True)
class ProjectConstants:
    """Defines project-specific constants used by tests."""

    _TEST_PROJECT = "test-project"
    _TEST_LOCATION = "us-central1"
    _TEST_ENCRYPTION_KEY_NAME = "key_1234"
    _TEST_ENCRYPTION_SPEC = encryption_spec.EncryptionSpec(
        kms_key_name=_TEST_ENCRYPTION_KEY_NAME
    )
    _TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
    _TEST_SERVICE_ACCOUNT = "vinnys@my-project.iam.gserviceaccount.com"
    _TEST_LABELS = {"my_key": "my_value"}
    _TEST_ENABLE_CUSTOM_SERVICE_ACCOUNT_TRUE = True


@dataclasses.dataclass(frozen=True)
class TrainingJobConstants:
    """Defines constants used by tests that create training jobs."""

    _TEST_OUTPUT_PYTHON_PACKAGE_PATH = "gs://test-staging-bucket/trainer.tar.gz"
    _TEST_MODULE_NAME = (
        f"{source_utils._TrainingScriptPythonPackager._ROOT_MODULE}.task"
    )
    _TEST_LOCAL_SCRIPT_FILE_NAME = "____test____script.py"
    _TEST_REQUIREMENTS = ["pandas", "numpy", "tensorflow"]
    _TEST_ENVIRONMENT_VARIABLES = {
        "MY_PATH": "/path/to/my_path",
    }
    _TEST_REPLICA_COUNT = 1
    _TEST_MACHINE_TYPE = "n1-standard-4"
    _TEST_MACHINE_TYPE_TPU = "cloud-tpu"
    _TEST_MACHINE_TYPE_TPU_V5E = "ct5lp-hightpu-4t"
    _TEST_ACCELERATOR_TPU_TYPE = "TPU_V3"
    _TEST_ACCELERATOR_TYPE = "NVIDIA_TESLA_K80"
    _TEST_ACCELERATOR_COUNT = 1
    _TEST_BOOT_DISK_TYPE = "pd-standard"
    _TEST_BOOT_DISK_SIZE_GB = 300
    _TEST_REDUCTION_SERVER_REPLICA_COUNT = 1
    _TEST_REDUCTION_SERVER_MACHINE_TYPE = "n1-highcpu-16"
    _TEST_REDUCTION_SERVER_CONTAINER_URI = (
        "us-docker.pkg.dev/vertex-ai-restricted/training/reductionserver:latest"
    )
    _TEST_DATASET_DISPLAY_NAME = "test-dataset-display-name"
    _TEST_DATASET_NAME = "test-dataset-name"
    _TEST_DISPLAY_NAME = "test-display-name"
    _TEST_BUCKET_NAME = "test-bucket"
    _TEST_GCS_PATH_WITHOUT_BUCKET = "path/to/folder"
    _TEST_GCS_PATH = f"{_TEST_BUCKET_NAME}/{_TEST_GCS_PATH_WITHOUT_BUCKET}"
    _TEST_GCS_PATH_WITH_TRAILING_SLASH = f"{_TEST_GCS_PATH}/"
    _TEST_MODEL_DISPLAY_NAME = "model-display-name"
    _TEST_MODEL_LABELS = {"model_key": "model_value"}
    _TEST_STAGING_BUCKET = "gs://test-staging-bucket"
    _TEST_DISPLAY_NAME = "my_job_1234"
    _TEST_BASE_OUTPUT_DIR = f"{_TEST_STAGING_BUCKET}/{_TEST_DISPLAY_NAME}"
    _TEST_ENABLE_WEB_ACCESS = True
    _TEST_WEB_ACCESS_URIS = {"workerpool0-0": "uri"}
    _TEST_TRAINING_CONTAINER_IMAGE = "gcr.io/test-training/container:image"

    _TEST_RUN_ARGS = ["-v", "0.1", "--test=arg"]

    _TEST_MACHINE_SPEC = {
        "machine_type": "n1-standard-4",
        "accelerator_type": "NVIDIA_TESLA_K80",
        "accelerator_count": 1,
    }
    _TEST_WORKER_POOL_SPEC = [
        {
            "machine_spec": _TEST_MACHINE_SPEC,
            "replica_count": 1,
            "disk_spec": {"boot_disk_type": "pd-ssd", "boot_disk_size_gb": 100},
            "container_spec": {
                "image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                "command": [],
                "args": _TEST_RUN_ARGS,
            },
        }
    ]
    _TEST_TPU_V5E_WORKER_POOL_SPEC = [
        {
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE_TPU_V5E,
                "tpu_topology": "2x2",
            },
            "replica_count": 1,
            "disk_spec": {"boot_disk_type": "pd-ssd", "boot_disk_size_gb": 100},
            "container_spec": {
                "image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
            },
        }
    ]
    _TEST_TPU_V3_WORKER_POOL_SPEC = [
        {
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE_TPU,
                "accelerator_type": _TEST_ACCELERATOR_TPU_TYPE,
                "accelerator_count": 32,
            },
            "replica_count": 1,
            "disk_spec": {"boot_disk_type": "pd-ssd", "boot_disk_size_gb": 100},
            "container_spec": {
                "image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
            },
        }
    ]
    _TEST_RESERVATION_AFFINITY_WORKER_POOL_SPEC = [
        {
            "machine_spec": {
                "machine_type": "n1-standard-4",
                "accelerator_type": "NVIDIA_TESLA_K80",
                "accelerator_count": 1,
                "reservation_affinity": {
                    "reservation_affinity_type": "ANY_RESERVATION"
                },
            },
            "replica_count": 1,
            "disk_spec": {"boot_disk_type": "pd-ssd", "boot_disk_size_gb": 100},
            "container_spec": {
                "image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
                "command": [],
                "args": _TEST_RUN_ARGS,
            },
        }
    ]
    _TEST_ID = "1028944691210842416"
    _TEST_NETWORK = (
        f"projects/{ProjectConstants._TEST_PROJECT}/global/networks/{_TEST_ID}"
    )
    _TEST_RESERVED_IP_RANGES = ["example_ip_range"]
    _TEST_TIMEOUT = 8000
    _TEST_TIMEOUT_SECONDS = duration_pb2.Duration(seconds=_TEST_TIMEOUT)
    _TEST_RESTART_JOB_ON_WORKER_RESTART = True
    _TEST_DISABLE_RETRIES = True
    _TEST_MAX_WAIT_DURATION = 8000

    _TEST_BASE_CUSTOM_JOB_PROTO = custom_job.CustomJob(
        display_name=_TEST_DISPLAY_NAME,
        job_spec=custom_job.CustomJobSpec(
            worker_pool_specs=_TEST_WORKER_POOL_SPEC,
            base_output_directory=io.GcsDestination(
                output_uri_prefix=_TEST_BASE_OUTPUT_DIR
            ),
            scheduling=custom_job.Scheduling(
                timeout=_TEST_TIMEOUT_SECONDS,
                restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
                disable_retries=_TEST_DISABLE_RETRIES,
                max_wait_duration=(
                    duration_pb2.Duration(seconds=_TEST_MAX_WAIT_DURATION)
                ),
            ),
            service_account=ProjectConstants._TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
        ),
        labels=ProjectConstants._TEST_LABELS,
        encryption_spec=ProjectConstants._TEST_ENCRYPTION_SPEC,
    )
    _TEST_PIPELINE_RESOURCE_NAME = f"projects/{ProjectConstants._TEST_PROJECT}/locations/us-central1/trainingPipelines/{_TEST_ID}"
    _TEST_BUCKET_NAME = "test-bucket"
    _TEST_TENSORBOARD_RESOURCE_NAME = f"projects/{ProjectConstants._TEST_PROJECT}/locations/{ProjectConstants._TEST_LOCATION}/tensorboards/{_TEST_ID}"
    _TEST_MODEL_NAME = f"projects/{ProjectConstants._TEST_PROJECT}/locations/us-central1/models/{_TEST_ID}"
    _TEST_CUSTOM_JOB_RESOURCE_NAME = f"projects/{ProjectConstants._TEST_PROJECT}/locations/{ProjectConstants._TEST_LOCATION}/customJobs/{_TEST_ID}"
    _TEST_CREDENTIALS = mock.Mock(spec=auth_credentials.AnonymousCredentials())
    _TEST_SERVING_CONTAINER_PREDICTION_ROUTE = "predict"
    _TEST_SERVING_CONTAINER_HEALTH_ROUTE = "metadata"
    _TEST_MODEL_DISPLAY_NAME = "model-display-name"
    _TEST_TRAINING_FRACTION_SPLIT = 0.6
    _TEST_VALIDATION_FRACTION_SPLIT = 0.2
    _TEST_TEST_FRACTION_SPLIT = 0.2
    _TEST_BOOT_DISK_TYPE_DEFAULT = "pd-ssd"
    _TEST_BOOT_DISK_SIZE_GB_DEFAULT = 100
    # # DUPLICATE: THIS NEEDS TO BE MOVED TO THE TRAINING JOB TEST THAT USES IT
    _TEST_PIPELINE_RESOURCE_NAME = (
        "projects/my-project/locations/us-central1/trainingPipelines/12345"
    )
    _TEST_DEFAULT_ENCRYPTION_KEY_NAME = "key_default"
    _TEST_SPOT_STRATEGY = custom_job.Scheduling.Strategy.SPOT
    _TEST_PSC_INTERFACE_CONFIG = {"network_attachment": "network_attachment_value"}

    def create_tpu_job_proto(tpu_version):
        worker_pool_spec = (
            TrainingJobConstants._TEST_TPU_V5E_WORKER_POOL_SPEC
            if tpu_version == "v5e"
            else TrainingJobConstants._TEST_TPU_V3_WORKER_POOL_SPEC
        )
        return custom_job.CustomJob(
            display_name=TrainingJobConstants._TEST_DISPLAY_NAME,
            job_spec=custom_job.CustomJobSpec(
                worker_pool_specs=worker_pool_spec,
                base_output_directory=io.GcsDestination(
                    output_uri_prefix=TrainingJobConstants._TEST_BASE_OUTPUT_DIR
                ),
                scheduling=custom_job.Scheduling(
                    timeout=TrainingJobConstants._TEST_TIMEOUT_SECONDS,
                    restart_job_on_worker_restart=TrainingJobConstants._TEST_RESTART_JOB_ON_WORKER_RESTART,
                ),
                service_account=ProjectConstants._TEST_SERVICE_ACCOUNT,
                network=TrainingJobConstants._TEST_NETWORK,
            ),
        )


@dataclasses.dataclass(frozen=True)
class ModelConstants:
    """Defines constants used by tests that create model resources."""

    _TEST_MODEL_NAME = "123"
    _TEST_ID = "1028944691210842416"
    _TEST_VERSION_ID = "2"
    _TEST_MODEL_RESOURCE_NAME = model_service_client.ModelServiceClient.model_path(
        ProjectConstants._TEST_PROJECT, ProjectConstants._TEST_LOCATION, _TEST_ID
    )
    _TEST_MODEL_PARENT = f"projects/{ProjectConstants._TEST_PROJECT}/locations/{ProjectConstants._TEST_LOCATION}/models/{_TEST_MODEL_NAME}"
    _TEST_VERSION_ALIAS_1 = "myalias"
    _TEST_VERSION_ALIAS_2 = "youralias"
    _TEST_MODEL_VERSION_DESCRIPTION_2 = "My version 2 description"
    _TEST_SERVING_CONTAINER_IMAGE = "gcr.io/test-serving/container:image"
    _TEST_EXPLANATION_PARAMETERS = explain.ExplanationParameters(
        {"sampled_shapley_attribution": {"path_count": 10}}
    )
    _TEST_LABEL = {"team": "experimentation", "trial_id": "x435"}
    _TEST_MODEL_OBJ_WITH_VERSION = model.Model(
        version_id=_TEST_VERSION_ID,
        create_time=timestamp_pb2.Timestamp(),
        update_time=timestamp_pb2.Timestamp(),
        display_name=_TEST_MODEL_NAME,
        name=f"{_TEST_MODEL_PARENT}@{_TEST_VERSION_ID}",
        version_aliases=[_TEST_VERSION_ALIAS_1, _TEST_VERSION_ALIAS_2],
        version_description=_TEST_MODEL_VERSION_DESCRIPTION_2,
    )
    _TEST_MODEL_EVAL_METRICS = {
        "auPrc": 0.80592036,
        "auRoc": 0.8100363,
        "logLoss": 0.53061414,
        "confidenceMetrics": [
            {
                "confidenceThreshold": -0.01,
                "recall": 1.0,
                "precision": 0.5,
                "falsePositiveRate": 1.0,
                "f1Score": 0.6666667,
                "recallAt1": 1.0,
                "precisionAt1": 0.5,
                "falsePositiveRateAt1": 1.0,
                "f1ScoreAt1": 0.6666667,
                "truePositiveCount": "415",
                "falsePositiveCount": "415",
            },
            {
                "recall": 1.0,
                "precision": 0.5,
                "falsePositiveRate": 1.0,
                "f1Score": 0.6666667,
                "recallAt1": 0.74216866,
                "precisionAt1": 0.74216866,
                "falsePositiveRateAt1": 0.25783134,
                "f1ScoreAt1": 0.74216866,
                "truePositiveCount": "415",
                "falsePositiveCount": "415",
            },
        ],
    }


@dataclasses.dataclass(frozen=True)
class EndpointConstants:
    """Defines constants used by tests that create endpoints."""

    _TEST_DISPLAY_NAME = "test-display-name"
    _TEST_DISPLAY_NAME_2 = "test-display-name-2"
    _TEST_DISPLAY_NAME_3 = "test-display-name-3"
    _TEST_ID = "1028944691210842416"
    _TEST_ID_2 = "4366591682456584192"
    _TEST_ID_3 = "5820582938582924817"
    _TEST_ENDPOINT_NAME = f"projects/{ProjectConstants._TEST_PROJECT}/locations/{ProjectConstants._TEST_LOCATION}/endpoints/{_TEST_ID}"
    _TEST_ENDPOINT_NAME_2 = f"projects/{ProjectConstants._TEST_PROJECT}/locations/{ProjectConstants._TEST_LOCATION}/endpoints/{_TEST_ID_2}"
    _TEST_DISPLAY_NAME = "test-display-name"
    _TEST_DEPLOYED_MODELS = [
        endpoint.DeployedModel(id=_TEST_ID, display_name=_TEST_DISPLAY_NAME),
        endpoint.DeployedModel(id=_TEST_ID_2, display_name=_TEST_DISPLAY_NAME_2),
        endpoint.DeployedModel(id=_TEST_ID_3, display_name=_TEST_DISPLAY_NAME_3),
    ]
    _TEST_TRAFFIC_SPLIT = {_TEST_ID: 0, _TEST_ID_2: 100, _TEST_ID_3: 0}
    _TEST_MODEL_ID = "1028944691210842416"
    _TEST_PREDICTION = [[1.0, 2.0, 3.0], [3.0, 3.0, 1.0]]
    _TEST_VERSION_ID = "1"
    _TEST_MODEL_NAME = f"projects/{ProjectConstants._TEST_PROJECT}/locations/{ProjectConstants._TEST_LOCATION}/models/{_TEST_ID}"


@dataclasses.dataclass(frozen=True)
class TensorboardConstants:
    """Defines constants used by tests that create Tensorboard resources."""

    _TEST_ID = "1028944691210842416"
    _TEST_DISPLAY_NAME = "my_tensorboard_1234"
    _TEST_TENSORBOARD_NAME = f"{ProjectConstants._TEST_PARENT}/tensorboards/{_TEST_ID}"
    _TEST_TENSORBOARD_EXPERIMENT_ID = "test-experiment"
    _TEST_TENSORBOARD_EXPERIMENT_NAME = (
        f"{_TEST_TENSORBOARD_NAME}/experiments/{_TEST_TENSORBOARD_EXPERIMENT_ID}"
    )

    _TEST_TENSORBOARD_RUN_ID = "test-run"
    _TEST_TENSORBOARD_RUN_NAME = (
        f"{_TEST_TENSORBOARD_EXPERIMENT_NAME}/runs/{_TEST_TENSORBOARD_RUN_ID}"
    )
    _TEST_TENSORBOARD_RUN = tensorboard_run.TensorboardRun(
        name=_TEST_TENSORBOARD_RUN_NAME,
        display_name=_TEST_DISPLAY_NAME,
    )
    _TEST_TENSORBOARD_TIME_SERIES_ID = "test-time-series"
    _TEST_TENSORBOARD_TIME_SERIES_NAME = (
        f"{_TEST_TENSORBOARD_RUN_NAME}/timeSeries/{_TEST_TENSORBOARD_TIME_SERIES_ID}"
    )
    _TEST_TIME_SERIES_DISPLAY_NAME = "accuracy"
    _TEST_TENSORBOARD_TIME_SERIES = tensorboard_time_series.TensorboardTimeSeries(
        name=_TEST_TENSORBOARD_TIME_SERIES_NAME,
        display_name=_TEST_TIME_SERIES_DISPLAY_NAME,
        value_type=tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR,
    )
    _TEST_TENSORBOARD_TIME_SERIES_DATA = tensorboard_data.TimeSeriesData(
        tensorboard_time_series_id=_TEST_TENSORBOARD_TIME_SERIES_ID,
        value_type=tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR,
        values=[
            tensorboard_data.TimeSeriesDataPoint(
                scalar=tensorboard_data.Scalar(value=1.0),
                step=1,
                wall_time=utils.get_timestamp_proto(),
            )
        ],
    )

    _TEST_TENSORBOARD_EXPERIMENT = tensorboard_experiment.TensorboardExperiment(
        name=_TEST_TENSORBOARD_EXPERIMENT_NAME,
        display_name=_TEST_DISPLAY_NAME,
    )


@dataclasses.dataclass(frozen=True)
class PipelineJobConstants:
    """Defines constants used by tests that create PipelineJob resources."""

    _TEST_PIPELINE_JOB_ID = "sample-test-pipeline-202111111"
    _TEST_PIPELINE_JOB_NAME = f"projects/{ProjectConstants._TEST_PROJECT}/locations/{ProjectConstants._TEST_LOCATION}/pipelineJobs/{_TEST_PIPELINE_JOB_ID}"
    _TEST_PIPELINE_CREATE_TIME = datetime.now()


@dataclasses.dataclass(frozen=True)
class DatasetConstants:
    """Defines constants used by tests that create Dataset resources."""

    _TEST_ID = "1028944691210842416"
    _TEST_NAME = f"projects/{ProjectConstants._TEST_PROJECT}/locations/{ProjectConstants._TEST_LOCATION}/datasets/{_TEST_ID}"
    _TEST_DISPLAY_NAME = "my_dataset_1234"
    _TEST_ENCRYPTION_KEY_NAME = "key_1234"
    _TEST_METADATA_SCHEMA_URI_TEXT = schema.dataset.metadata.text
    _TEST_ENCRYPTION_SPEC = encryption_spec.EncryptionSpec(
        kms_key_name=_TEST_ENCRYPTION_KEY_NAME
    )
    _TEST_METADATA_SCHEMA_URI_NONTABULAR = schema.dataset.metadata.image
    _TEST_NONTABULAR_DATASET_METADATA = None
    _TEST_IMPORT_SCHEMA_URI = schema.dataset.ioformat.image.single_label_classification
    _TEST_IMPORT_SCHEMA_URI_IMAGE = (
        schema.dataset.ioformat.image.single_label_classification
    )
    _TEST_DATA_LABEL_ITEMS = None
    _TEST_REQUEST_METADATA = ()
    _TEST_SOURCE_URI_GCS = "gs://my-bucket/my_index_file.jsonl"


@dataclasses.dataclass(frozen=True)
class ExperimentConstants:
    """Defines constants used by Experiments and Metadata tests."""

    _TEST_EXPERIMENT = "test-experiment"
    _TEST_CONTEXT_ID = _TEST_EXPERIMENT
    _TEST_METADATA_PARENT = f"projects/{ProjectConstants._TEST_PROJECT}/locations/{ProjectConstants._TEST_LOCATION}/metadataStores/default"
    _TEST_CONTEXT_NAME = f"{_TEST_METADATA_PARENT}/contexts/{_TEST_CONTEXT_ID}"
    _TEST_EXPERIMENT_DESCRIPTION = "test-experiment-description"

    _EXPERIMENT_MOCK = context.Context(
        name=_TEST_CONTEXT_NAME,
        display_name=_TEST_EXPERIMENT,
        description=_TEST_EXPERIMENT_DESCRIPTION,
        schema_title=metadata_constants.SYSTEM_EXPERIMENT,
        schema_version=metadata_constants.SCHEMA_VERSIONS[
            metadata_constants.SYSTEM_EXPERIMENT
        ],
        metadata={**metadata_constants.EXPERIMENT_METADATA},
    )

    _TEST_METADATASTORE = f"projects/{ProjectConstants._TEST_PROJECT}/locations/{ProjectConstants._TEST_LOCATION}/metadataStores/default"


@dataclasses.dataclass(frozen=True)
class MatchingEngineConstants:
    """Defines constants used by tests that create MatchingEngine resources."""

    _TEST_INDEX_ID = "index_id"
    _TEST_INDEX_NAME = f"{ProjectConstants._TEST_PARENT}/indexes/{_TEST_INDEX_ID}"
    _TEST_INDEX_DISPLAY_NAME = "index_display_name"
    _TEST_INDEX_DESCRIPTION = "index_description"
    _TEST_LABELS = {"my_key": "my_value"}
    _TEST_LABELS_UPDATE = {"my_key_update": "my_value_update"}
    _TEST_DISPLAY_NAME_UPDATE = "my new display name"
    _TEST_DESCRIPTION_UPDATE = "my description update"
    _TEST_REQUEST_METADATA = ()


@dataclasses.dataclass(frozen=True)
class PersistentResourceConstants:
    """Defines constants used by tests that create PersistentResource resources."""

    _TEST_PERSISTENT_RESOURCE_ID = "test_persistent_resource_id"
    _TEST_PERSISTENT_RESOURCE_DISPLAY_NAME = "test_display_name"
    _TEST_RESOURCE_POOL = {
        "machine_spec": TrainingJobConstants._TEST_MACHINE_SPEC,
        "replica_count": 1,
    }
