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


import pytest
import uuid
import os

import helpers

import cancel_custom_job_sample
import create_custom_job_sample
import delete_custom_job_sample

from google.cloud import aiplatform

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
CONTAINER_IMAGE_URI = "gcr.io/ucaip-test/ucaip-training-test:latest"


@pytest.fixture
def shared_state():
    state = {}
    yield state


@pytest.fixture(scope="function", autouse=True)
def teardown(shared_state):
    yield

    custom_job_id = shared_state["custom_job_name"].split("/")[-1]

    # Cancel the created custom job
    cancel_custom_job_sample.cancel_custom_job_sample(
        project=PROJECT_ID, custom_job_id=custom_job_id
    )

    client_options = {"api_endpoint": "us-central1-aiplatform.googleapis.com"}
    job_client = aiplatform.gapic.JobServiceClient(client_options=client_options)

    # Waiting for custom job to be in CANCELLED state
    helpers.wait_for_job_state(
        get_job_method=job_client.get_custom_job, name=shared_state["custom_job_name"],
    )

    # Delete the created custom job
    delete_custom_job_sample.delete_custom_job_sample(
        project=PROJECT_ID, custom_job_id=custom_job_id
    )


def test_ucaip_generated_create_custom_job(capsys, shared_state):
    create_custom_job_sample.create_custom_job_sample(
        display_name=f"temp_create_custom_job_test_{uuid.uuid4()}",
        container_image_uri=CONTAINER_IMAGE_URI,
        project=PROJECT_ID,
    )
    out, _ = capsys.readouterr()
    assert "response" in out

    shared_state["custom_job_name"] = helpers.get_name(out)
