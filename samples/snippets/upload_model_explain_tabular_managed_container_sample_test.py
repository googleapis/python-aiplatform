# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from uuid import uuid4

import pytest

import helpers

import upload_model_explain_tabular_managed_container_sample

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
IMAGE_URI = "gcr.io/cloud-aiplatform/prediction/tf2-cpu.2-1:latest"
ARTIFACT_URI = "gs://ucaip-samples-us-central1/model/boston_housing/"
DISPLAY_NAME = f"temp_upload_model_test_{uuid4()}"

INPUT_TENSOR_NAME = "dense_input"
OUTPUT_TENSOR_NAME = "dense_2"


@pytest.fixture(scope="function", autouse=True)
def teardown(teardown_model):
    yield


def test_ucaip_generated_upload_model_explain_tabular_managed_constainer_sample(capsys, shared_state):

    upload_model_explain_tabular_managed_container_sample.upload_model_explain_tabular_managed_container_sample(
        display_name=DISPLAY_NAME,
        artifact_uri=ARTIFACT_URI,
        container_spec_image_uri=IMAGE_URI,
        project=PROJECT_ID,
        input_tensor_name=INPUT_TENSOR_NAME,
        output_tensor_name=OUTPUT_TENSOR_NAME,
        feature_names=["crim", "zn", "indus", "chas", "nox", "rm", "age",
                       "dis", "rad", "tax", "ptratio", "b", "lstat"]
    )

    out, _ = capsys.readouterr()

    shared_state["model_name"] = helpers.get_name(out, key="model")
