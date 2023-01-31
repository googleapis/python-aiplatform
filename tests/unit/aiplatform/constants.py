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

from google.protobuf import timestamp_pb2, duration_pb2

from google.cloud.aiplatform.utils import source_utils
from google.cloud.aiplatform import explain

from google.cloud.aiplatform.compat.services import (
    model_service_client,
)

from google.cloud.aiplatform.compat.types import (
    custom_job,
    encryption_spec,
    endpoint,
    io,
    model,
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
    _TEST_ACCELERATOR_TYPE = "NVIDIA_TESLA_K80"
    _TEST_ACCELERATOR_COUNT = 1
    _TEST_BOOT_DISK_TYPE = "pd-standard"
    _TEST_BOOT_DISK_SIZE_GB = 300
    _TEST_REDUCTION_SERVER_REPLICA_COUNT = 1
    _TEST_REDUCTION_SERVER_MACHINE_TYPE = "n1-highcpu-16"
    _TEST_REDUCTION_SERVER_CONTAINER_URI = (
        "us-docker.pkg.dev/vertex-ai-restricted/training/reductionserver:latest"
    )
    _TEST_STAGING_BUCKET = "gs://test-staging-bucket"
    _TEST_DISPLAY_NAME = "my_job_1234"
    _TEST_BASE_OUTPUT_DIR = f"{_TEST_STAGING_BUCKET}/{_TEST_DISPLAY_NAME}"
    _TEST_ENABLE_WEB_ACCESS = True
    _TEST_WEB_ACCESS_URIS = {"workerpool0-0": "uri"}
    _TEST_TRAINING_CONTAINER_IMAGE = "gcr.io/test-training/container:image"

    _TEST_RUN_ARGS = ["-v", "0.1", "--test=arg"]

    _TEST_WORKER_POOL_SPEC = [
        {
            "machine_spec": {
                "machine_type": "n1-standard-4",
                "accelerator_type": "NVIDIA_TESLA_K80",
                "accelerator_count": 1,
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
    _TEST_TIMEOUT = 8000
    _TEST_RESTART_JOB_ON_WORKER_RESTART = True

    _TEST_BASE_CUSTOM_JOB_PROTO = custom_job.CustomJob(
        display_name=_TEST_DISPLAY_NAME,
        job_spec=custom_job.CustomJobSpec(
            worker_pool_specs=_TEST_WORKER_POOL_SPEC,
            base_output_directory=io.GcsDestination(
                output_uri_prefix=_TEST_BASE_OUTPUT_DIR
            ),
            scheduling=custom_job.Scheduling(
                timeout=duration_pb2.Duration(seconds=_TEST_TIMEOUT),
                restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            ),
            service_account=ProjectConstants._TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
        ),
        labels=ProjectConstants._TEST_LABELS,
        encryption_spec=ProjectConstants._TEST_ENCRYPTION_SPEC,
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
    _TEST_DISPLAY_NAME = "test-display-name"
    _TEST_DEPLOYED_MODELS = [
        endpoint.DeployedModel(id=_TEST_ID, display_name=_TEST_DISPLAY_NAME),
        endpoint.DeployedModel(id=_TEST_ID_2, display_name=_TEST_DISPLAY_NAME_2),
        endpoint.DeployedModel(id=_TEST_ID_3, display_name=_TEST_DISPLAY_NAME_3),
    ]
    _TEST_TRAFFIC_SPLIT = {_TEST_ID: 0, _TEST_ID_2: 100, _TEST_ID_3: 0}


@dataclasses.dataclass(frozen=True)
class TensorboardConstants:
    """Defines constants used by tests that create Tensorboard resources."""

    _TEST_ID = "1028944691210842416"
    _TEST_TENSORBOARD_NAME = f"{ProjectConstants._TEST_PARENT}/tensorboards/{_TEST_ID}"
