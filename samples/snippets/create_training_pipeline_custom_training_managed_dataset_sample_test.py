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
from google.cloud import aiplatform

import create_training_pipeline_custom_training_managed_dataset_sample
import helpers

API_ENDPOINT = "us-central1-aiplatform.googleapis.com"

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
DISPLAY_NAME = f"temp_create_training_pipeline_custom_training_managed_dataset_test_{uuid.uuid4()}"
MODEL_DISPLAY_NAME = f"Temp Model for {DISPLAY_NAME}"

DATASET_ID = "1084241610289446912"  # permanent_50_flowers_dataset
ANNOTATION_SCHEMA_URI = "gs://google-cloud-aiplatform/schema/dataset/annotation/image_classification_1.0.0.yaml"

TRAINING_CONTAINER_SPEC_IMAGE_URI = "gcr.io/ucaip-test/custom-container-managed-dataset:latest"
MODEL_CONTAINER_SPEC_IMAGE_URI = "gcr.io/cloud-aiplatform/prediction/tf-gpu.1-15:latest"

BASE_OUTPUT_URI_PREFIX = "gs://ucaip-samples-us-central1/training_pipeline_output/custom_training_managed_dataset"


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


def test_create_training_pipeline_custom_training_managed_dataset_sample(
    capsys, shared_state, pipeline_client
):
    create_training_pipeline_custom_training_managed_dataset_sample.create_training_pipeline_custom_training_managed_dataset_sample(
        project=PROJECT_ID,
        display_name=DISPLAY_NAME,
        model_display_name=MODEL_DISPLAY_NAME,
        dataset_id=DATASET_ID,
        annotation_schema_uri=ANNOTATION_SCHEMA_URI,
        training_container_spec_image_uri=TRAINING_CONTAINER_SPEC_IMAGE_URI,
        model_container_spec_image_uri=MODEL_CONTAINER_SPEC_IMAGE_URI,
        base_output_uri_prefix=BASE_OUTPUT_URI_PREFIX,
    )

    out, _ = capsys.readouterr()

    # Save resource name of the newly created training pipeline
    shared_state["training_pipeline_name"] = helpers.get_name(out)

    # Poll until the pipeline succeeds because we want to test the model_upload step as well.
    helpers.wait_for_job_state(
        get_job_method=pipeline_client.get_training_pipeline,
        name=shared_state["training_pipeline_name"],
        expected_state="SUCCEEDED",
        timeout=1800,
        freq=20,
    )

    training_pipeline = pipeline_client.get_training_pipeline(
        name=shared_state["training_pipeline_name"]
    )

    # Check that the model indeed has been uploaded.
    assert training_pipeline.model_to_upload.name != ""

    shared_state["model_name"] = training_pipeline.model_to_upload.name
