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

from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
import pytest

import cancel_training_pipeline_sample
import helpers

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
LOCATION = "us-central1"
DATASET_ID = "1084241610289446912"  # Permanent 50 Flowers Dataset
DISPLAY_NAME = f"temp_create_training_pipeline_test_{uuid4()}"
TRAINING_DEFINITION_GCS_PATH = "gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_image_classification_1.0.0.yaml"


@pytest.fixture(autouse=True)
def setup(shared_state, pipeline_client):
    training_task_inputs = json_format.ParseDict({}, Value())
    training_pipeline = pipeline_client.create_training_pipeline(
        parent=f"projects/{PROJECT_ID}/locations/{LOCATION}",
        training_pipeline={
            "display_name": DISPLAY_NAME,
            "training_task_definition": TRAINING_DEFINITION_GCS_PATH,
            "training_task_inputs": training_task_inputs,
            "input_data_config": {"dataset_id": DATASET_ID},
            "model_to_upload": {"display_name": f"Temp Model for {DISPLAY_NAME}"},
        },
    )

    shared_state["training_pipeline_name"] = training_pipeline.name

    yield


@pytest.fixture(autouse=True)
def teardown(shared_state, pipeline_client):
    yield

    pipeline_client.delete_training_pipeline(
        name=shared_state["training_pipeline_name"]
    )


def test_ucaip_generated_cancel_training_pipeline_sample(
    capsys, shared_state, pipeline_client
):
    # Run cancel pipeline sample
    training_pipeline_id = shared_state["training_pipeline_name"].split("/")[-1]

    cancel_training_pipeline_sample.cancel_training_pipeline_sample(
        project=PROJECT_ID, training_pipeline_id=training_pipeline_id
    )

    # Waiting for training pipeline to be in CANCELLED state, otherwise raise error
    helpers.wait_for_job_state(
        get_job_method=pipeline_client.get_training_pipeline,
        name=shared_state["training_pipeline_name"],
    )
