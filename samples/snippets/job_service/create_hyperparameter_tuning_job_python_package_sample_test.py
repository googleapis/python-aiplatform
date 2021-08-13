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

import os
import uuid

import create_hyperparameter_tuning_job_python_package_sample
import pytest

import helpers

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
DISPLAY_NAME = (
    f"temp_create_hyperparameter_tuning_job_python_package_test_{uuid.uuid4()}"
)

EXECUTOR_IMAGE_URI = "us.gcr.io/cloud-aiplatform/training/tf-gpu.2-1:latest"
PACKAGE_URI = "gs://cloud-samples-data-us-central1/ai-platform-unified/training/python-packages/trainer.tar.bz2"
PYTHON_MODULE = "trainer.hptuning_trainer"


@pytest.fixture(scope="function", autouse=True)
def teardown(teardown_hyperparameter_tuning_job):
    yield


@pytest.mark.skip(reason="https://github.com/googleapis/java-aiplatform/issues/420")
def test_create_hyperparameter_tuning_job_python_package_sample(capsys, shared_state):

    create_hyperparameter_tuning_job_python_package_sample.create_hyperparameter_tuning_job_python_package_sample(
        project=PROJECT_ID,
        display_name=DISPLAY_NAME,
        executor_image_uri=EXECUTOR_IMAGE_URI,
        package_uri=PACKAGE_URI,
        python_module=PYTHON_MODULE,
    )

    out, _ = capsys.readouterr()
    assert "response" in out

    shared_state["hyperparameter_tuning_job_name"] = helpers.get_name(out)
