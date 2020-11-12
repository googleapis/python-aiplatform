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

from uuid import uuid4
import pytest
import os

import helpers

import create_batch_prediction_job_video_object_tracking_sample
import cancel_batch_prediction_job_sample
import delete_batch_prediction_job_sample

from google.cloud import aiplatform

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
LOCATION = "us-central1"
MODEL_ID = "20547673299877888"  # Permanent horses model
DISPLAY_NAME = f"temp_create_batch_prediction_vot_test_{uuid4()}"
GCS_SOURCE_URI = (
    "gs://ucaip-samples-test-output/inputs/vot_batch_prediction_input.jsonl"
)
GCS_OUTPUT_URI = "gs://ucaip-samples-test-output/"


@pytest.fixture
def shared_state():
    state = {}
    yield state


@pytest.fixture(scope="function", autouse=True)
def teardown(shared_state):
    yield

    assert "/" in shared_state["batch_prediction_job_name"]

    batch_prediction_job = shared_state["batch_prediction_job_name"].split("/")[-1]

    # Stop the batch prediction job
    cancel_batch_prediction_job_sample.cancel_batch_prediction_job_sample(
        project=PROJECT_ID, batch_prediction_job_id=batch_prediction_job
    )

    job_client = aiplatform.gapic.JobServiceClient(
        client_options={"api_endpoint": "us-central1-aiplatform.googleapis.com"}
    )

    # Waiting for batch prediction job to be in CANCELLED state
    helpers.wait_for_job_state(
        get_job_method=job_client.get_batch_prediction_job,
        name=shared_state["batch_prediction_job_name"],
    )

    # Delete the batch prediction job
    delete_batch_prediction_job_sample.delete_batch_prediction_job_sample(
        project=PROJECT_ID, batch_prediction_job_id=batch_prediction_job
    )


# Creating AutoML Video Object Tracking batch prediction job
def test_ucaip_generated_create_batch_prediction_vcn_sample(capsys, shared_state):

    model_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/models/{MODEL_ID}"

    create_batch_prediction_job_video_object_tracking_sample.create_batch_prediction_job_video_object_tracking_sample(
        project=PROJECT_ID,
        display_name=DISPLAY_NAME,
        model_name=model_name,
        gcs_source_uri=GCS_SOURCE_URI,
        gcs_destination_output_uri_prefix=GCS_OUTPUT_URI,
    )

    out, _ = capsys.readouterr()

    # Save resource name of the newly created batch prediction job
    shared_state["batch_prediction_job_name"] = helpers.get_name(out)
