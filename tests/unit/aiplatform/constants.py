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

from google.cloud.aiplatform.utils import source_utils


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
