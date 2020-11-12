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

import pytest
import os
from uuid import uuid4
from google.cloud import aiplatform

import helpers

import create_data_labeling_job_images_sample
import cancel_data_labeling_job_sample
import delete_data_labeling_job_sample

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
API_ENDPOINT = os.getenv("DATA_LABELING_API_ENDPOINT")
LOCATION = "us-central1"
DATASET_ID = "1905673553261363200"
DISPLAY_NAME = f"temp_create_data_labeling_job_test_{uuid4()}"
INSTRUCTIONS_GCS_URI = (
    "gs://ucaip-sample-resources/images/datalabeling_instructions.pdf"
)
ANNOTATION_SPEC = "daisy"


@pytest.fixture
def shared_state():
    state = {}
    yield state


@pytest.fixture(scope="function", autouse=True)
def teardown(capsys, shared_state):
    yield

    assert "/" in shared_state["data_labeling_job_name"]

    data_labeling_job_id = shared_state["data_labeling_job_name"].split("/")[-1]

    client_options = {"api_endpoint": API_ENDPOINT}
    client = aiplatform.gapic.JobServiceClient(client_options=client_options)

    name = client.data_labeling_job_path(
        project=PROJECT_ID, location=LOCATION, data_labeling_job=data_labeling_job_id
    )
    client.cancel_data_labeling_job(name=name)

    # Verify Data Labelling Job is cancelled, or timeout after 400 seconds
    helpers.wait_for_job_state(
        get_job_method=client.get_data_labeling_job, name=name, timeout=400, freq=10
    )

    # Delete the data labeling job
    response = client.delete_data_labeling_job(name=name)
    print("Delete LRO:", response.operation.name)
    delete_data_labeling_job_response = response.result(timeout=300)
    print("delete_data_labeling_job_response", delete_data_labeling_job_response)

    out, _ = capsys.readouterr()
    assert "delete_data_labeling_job_response" in out


# Creating a data labeling job for images
def test_ucaip_generated_create_data_labeling_job_sample(capsys, shared_state):

    dataset_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/datasets/{DATASET_ID}"

    create_data_labeling_job_images_sample.create_data_labeling_job_images_sample(
        project=PROJECT_ID,
        display_name=DISPLAY_NAME,
        instruction_uri=INSTRUCTIONS_GCS_URI,
        dataset=dataset_name,
        annotation_spec=ANNOTATION_SPEC,
        api_endpoint=API_ENDPOINT,
    )

    out, _ = capsys.readouterr()

    # Save resource name of the newly created data labeing job
    shared_state["data_labeling_job_name"] = helpers.get_name(out)
