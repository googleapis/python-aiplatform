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

import pytest

import create_custom_job_sample
import helpers

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
CONTAINER_IMAGE_URI = "gcr.io/ucaip-sample-tests/ucaip-training-test:latest"


@pytest.fixture(scope="function", autouse=True)
def teardown(shared_state, job_client):
    yield

    # Cancel the created custom job
    job_client.cancel_custom_job(name=shared_state["custom_job_name"])

    # Waiting for custom job to be in CANCELLED state
    helpers.wait_for_job_state(
        get_job_method=job_client.get_custom_job, name=shared_state["custom_job_name"],
    )

    # Delete the created custom job
    job_client.delete_custom_job(name=shared_state["custom_job_name"])


def test_ucaip_generated_create_custom_job(capsys, shared_state):
    create_custom_job_sample.create_custom_job_sample(
        display_name=f"temp_create_custom_job_test_{uuid.uuid4()}",
        container_image_uri=CONTAINER_IMAGE_URI,
        project=PROJECT_ID,
    )
    out, _ = capsys.readouterr()
    assert "response" in out

    shared_state["custom_job_name"] = helpers.get_name(out)
