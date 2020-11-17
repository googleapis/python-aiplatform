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

import uuid
import pytest
import os

import helpers

import create_batch_prediction_job_video_action_recognition_sample

from google.cloud import aiplatform

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
LOCATION = "us-central1"
MODEL_ID = "3530998029718913024"  # permanent_swim_run_videos_action_recognition_model
DISPLAY_NAME = f"temp_create_batch_prediction_job_video_action_recognition_test_{uuid.uuid4()}"
GCS_SOURCE_URI = "gs://automl-video-demo-data/ucaip-var/swimrun_bp.jsonl"
GCS_OUTPUT_URI = "gs://ucaip-samples-test-output/"
API_ENDPOINT = "us-central1-aiplatform.googleapis.com"

@pytest.fixture
def shared_state():
    state = {}
    yield state


@pytest.fixture
def job_client():
    client_options = {"api_endpoint": API_ENDPOINT}
    job_client = aiplatform.gapic.JobServiceClient(
        client_options=client_options)
    yield job_client


@pytest.fixture(scope="function", autouse=True)
def teardown(shared_state, job_client):
    yield
    job_client.delete_batch_prediction_job(
        name=shared_state["batch_prediction_job_name"]
    )


# Creating AutoML Video Object Tracking batch prediction job
def test_create_batch_prediction_job_video_action_recognition_sample(
    capsys, shared_state, job_client
):

    model = f"projects/{PROJECT_ID}/locations/{LOCATION}/models/{MODEL_ID}"

    create_batch_prediction_job_video_action_recognition_sample.create_batch_prediction_job_video_action_recognition_sample(
        project=PROJECT_ID,
        display_name=DISPLAY_NAME,
        model=model,
        gcs_source_uri=GCS_SOURCE_URI,
        gcs_destination_output_uri_prefix=GCS_OUTPUT_URI,
    )

    out, _ = capsys.readouterr()

    # Save resource name of the newly created batch prediction job
    shared_state["batch_prediction_job_name"] = helpers.get_name(out)

    # Waiting for batch prediction job to be in CANCELLED state
    helpers.wait_for_job_state(
        get_job_method=job_client.get_batch_prediction_job,
        name=shared_state["batch_prediction_job_name"],
        expected_state="SUCCEEDED",
        timeout=600,
        freq=20,
    )
