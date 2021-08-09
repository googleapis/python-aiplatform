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
import uuid

import pytest

import create_data_labeling_job_specialist_pool_sample
import helpers

API_ENDPOINT = os.getenv("DATA_LABELING_API_ENDPOINT")
PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
LOCATION = "us-central1"
DATASET_ID = "1905673553261363200"
SPECIALIST_POOL_ID = "5898026661995085824"
INPUTS_SCHEMA_URI = "gs://google-cloud-aiplatform/schema/datalabelingjob/inputs/image_classification_1.0.0.yaml"
DISPLAY_NAME = f"temp_create_data_labeling_job_specialist_pool_test_{uuid.uuid4()}"

INSTRUCTIONS_GCS_URI = (
    "gs://ucaip-sample-resources/images/datalabeling_instructions.pdf"
)
ANNOTATION_SPEC = "rose"


@pytest.fixture(scope="function", autouse=True)
def teardown(teardown_data_labeling_job):
    yield


# Creating a data labeling job for images
@pytest.mark.skip(reason="Flaky job state.")
def test_create_data_labeling_job_specialist_pool_sample(capsys, shared_state):

    dataset = f"projects/{PROJECT_ID}/locations/{LOCATION}/datasets/{DATASET_ID}"
    specialist_pool = f"projects/{PROJECT_ID}/locations/{LOCATION}/specialistPools/{SPECIALIST_POOL_ID}"

    create_data_labeling_job_specialist_pool_sample.create_data_labeling_job_specialist_pool_sample(
        project=PROJECT_ID,
        display_name=DISPLAY_NAME,
        dataset=dataset,
        specialist_pool=specialist_pool,
        instruction_uri=INSTRUCTIONS_GCS_URI,
        inputs_schema_uri=INPUTS_SCHEMA_URI,
        annotation_spec=ANNOTATION_SPEC,
        api_endpoint=API_ENDPOINT,
    )

    out, _ = capsys.readouterr()

    # Save resource name of the newly created data labeing job
    shared_state["data_labeling_job_name"] = helpers.get_name(out)
