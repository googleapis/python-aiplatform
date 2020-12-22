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

import create_batch_prediction_job_video_action_recognition_sample
import helpers

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
LOCATION = "us-central1"
MODEL_ID = "3530998029718913024"  # permanent_swim_run_videos_action_recognition_model
DISPLAY_NAME = (
    f"temp_create_batch_prediction_job_video_action_recognition_test_{uuid.uuid4()}"
)
GCS_SOURCE_URI = "gs://automl-video-demo-data/ucaip-var/swimrun_bp.jsonl"
GCS_OUTPUT_URI = "gs://ucaip-samples-test-output/"


@pytest.fixture(scope="function", autouse=True)
def teardown(teardown_batch_prediction_job):
    yield


# Creating AutoML Video Object Tracking batch prediction job
def test_create_batch_prediction_job_video_action_recognition_sample(
    capsys, shared_state, job_client
):

    model_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/models/{MODEL_ID}"

    create_batch_prediction_job_video_action_recognition_sample.create_batch_prediction_job_video_action_recognition_sample(
        project=PROJECT_ID,
        display_name=DISPLAY_NAME,
        model_name=model_name,
        gcs_source_uri=GCS_SOURCE_URI,
        gcs_destination_output_uri_prefix=GCS_OUTPUT_URI,
    )

    out, _ = capsys.readouterr()

    # Save resource name of the newly created batch prediction job
    shared_state["batch_prediction_job_name"] = helpers.get_name(out)
