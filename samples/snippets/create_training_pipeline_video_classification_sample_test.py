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

from google.cloud import aiplatform
import pytest

import create_training_pipeline_video_classification_sample
import helpers

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
DATASET_ID = "3757409464110546944"  # Permanent 5 class sports dataset
DISPLAY_NAME = f"temp_create_training_pipeline_vcn_test_{uuid4()}"


@pytest.fixture(scope="function", autouse=True)
def teardown(shared_state, pipeline_client):
    yield

    pipeline_client.cancel_training_pipeline(
        name=shared_state["training_pipeline_name"]
    )

    # Waiting for training pipeline to be in CANCELLED state
    helpers.wait_for_job_state(
        get_job_method=pipeline_client.get_training_pipeline,
        name=shared_state["training_pipeline_name"],
    )

    # Delete the training pipeline
    pipeline_client.delete_training_pipeline(
        name=shared_state["training_pipeline_name"]
    )


# Training AutoML Vision Model
def test_ucaip_generated_create_training_pipeline_video_classification_sample(
    capsys, shared_state
):

    create_training_pipeline_video_classification_sample.create_training_pipeline_video_classification_sample(
        project=PROJECT_ID,
        display_name=DISPLAY_NAME,
        dataset_id=DATASET_ID,
        model_display_name=f"Temp Model for {DISPLAY_NAME}",
    )

    out, _ = capsys.readouterr()
    assert "response:" in out

    # Save resource name of the newly created training pipeline
    shared_state["training_pipeline_name"] = helpers.get_name(out)
