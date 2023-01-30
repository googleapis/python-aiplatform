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

from google.protobuf import timestamp_pb2

from google.cloud.aiplatform.utils import source_utils
from google.cloud.aiplatform import explain

from google.cloud.aiplatform.compat.services import (
    model_service_client,
)

from google.cloud.aiplatform.compat.types import (
    model as gca_model,
)


@dataclasses.dataclass(frozen=True)
class ProjectConstants:
    """Defines project-specific constants used by tests."""

    _TEST_PROJECT = "test-project"
    _TEST_LOCATION = "us-central1"


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
    _TEST_MODEL_OBJ_WITH_VERSION = gca_model.Model(
        version_id=_TEST_VERSION_ID,
        create_time=timestamp_pb2.Timestamp(),
        update_time=timestamp_pb2.Timestamp(),
        display_name=_TEST_MODEL_NAME,
        name=f"{_TEST_MODEL_PARENT}@{_TEST_VERSION_ID}",
        version_aliases=[_TEST_VERSION_ALIAS_1, _TEST_VERSION_ALIAS_2],
        version_description=_TEST_MODEL_VERSION_DESCRIPTION_2,
    )
