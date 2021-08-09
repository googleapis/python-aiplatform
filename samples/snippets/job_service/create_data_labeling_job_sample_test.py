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

import create_data_labeling_job_sample
import helpers

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
API_ENDPOINT = os.getenv("DATA_LABELING_API_ENDPOINT")
LOCATION = "us-central1"
DATASET_ID = "1905673553261363200"
DISPLAY_NAME = f"temp_create_data_labeling_job_test_{uuid4()}"
INPUTS_SCHEMA_URI = "gs://google-cloud-aiplatform/schema/datalabelingjob/inputs/image_classification.yaml"
INSTRUCTIONS_GCS_URI = (
    "gs://ucaip-sample-resources/images/datalabeling_instructions.pdf"
)
ANNOTATION_SPEC = "daisy"


@pytest.fixture(scope="function", autouse=True)
def teardown(teardown_data_labeling_job):
    yield


# Creating a data labeling job for images
@pytest.mark.skip(reason="Flaky job state.")
def test_ucaip_generated_create_data_labeling_job_sample(capsys, shared_state):

    dataset_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/datasets/{DATASET_ID}"

    create_data_labeling_job_sample.create_data_labeling_job_sample(
        project=PROJECT_ID,
        display_name=DISPLAY_NAME,
        instruction_uri=INSTRUCTIONS_GCS_URI,
        dataset_name=dataset_name,
        inputs_schema_uri=INPUTS_SCHEMA_URI,
        annotation_spec=ANNOTATION_SPEC,
        api_endpoint=API_ENDPOINT,
    )

    out, _ = capsys.readouterr()

    # Save resource name of the newly created data labeing job
    shared_state["data_labeling_job_name"] = helpers.get_name(out)
