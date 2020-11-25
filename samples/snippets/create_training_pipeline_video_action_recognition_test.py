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

import create_training_pipeline_video_action_recognition_sample

from google.cloud import aiplatform

LOCATION = "us-central1"
PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
DATASET_ID = "6881957627459272704"  # permanent_swim_run_videos_action_recognition_dataset
DISPLAY_NAME = f"temp_create_training_pipeline_video_action_recognition_test_{uuid.uuid4()}"
MODEL_DISPLAY_NAME = f"Temp Model for {DISPLAY_NAME}"
MODEL_TYPE = "CLOUD"
API_ENDPOINT = "us-central1-aiplatform.googleapis.com"

@pytest.fixture
def shared_state():
    state = {}
    yield state


@pytest.fixture
def pipeline_client():
    client_options = {"api_endpoint": API_ENDPOINT}
    pipeline_client = aiplatform.gapic.PipelineServiceClient(
        client_options=client_options
    )
    yield pipeline_client


@pytest.fixture
def model_client():
    client_options = {"api_endpoint": API_ENDPOINT}
    model_client = aiplatform.gapic.ModelServiceClient(
        client_options=client_options)
    yield model_client


@pytest.fixture(scope="function", autouse=True)
def teardown(shared_state, model_client, pipeline_client):
    yield
    model_client.delete_model(name=shared_state["model_name"])
    pipeline_client.delete_training_pipeline(
        name=shared_state["training_pipeline_name"]
    )


# Training AutoML Vision Model
def test_create_training_pipeline_video_action_recognition_sample(
    capsys, shared_state, pipeline_client
):
    create_training_pipeline_video_action_recognition_sample.create_training_pipeline_video_action_recognition_sample(
        project=PROJECT_ID,
        display_name=DISPLAY_NAME,
        dataset_id=DATASET_ID,
        model_display_name=MODEL_DISPLAY_NAME,
        model_type=MODEL_TYPE,
    )

    out, _ = capsys.readouterr()

    assert "response:" in out

    # Save resource name of the newly created training pipeline
    shared_state["training_pipeline_name"] = helpers.get_name(out)

    # Poll until the pipeline succeeds because we want to test the model_upload step as well.
    helpers.wait_for_job_state(
        get_job_method=pipeline_client.get_training_pipeline,
        name=shared_state["training_pipeline_name"],
        expected_state="SUCCEEDED",
        timeout=5000,
        freq=20,
    )

    training_pipeline = pipeline_client.get_training_pipeline(
        name=shared_state["training_pipeline_name"]
    )

    # Check that the model indeed has been uploaded.
    assert training_pipeline.model_to_upload.name != ""

    shared_state["model_name"] = training_pipeline.model_to_upload.name
