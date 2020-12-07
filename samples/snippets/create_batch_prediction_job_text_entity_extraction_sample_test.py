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

import pytest

import create_batch_prediction_job_text_entity_extraction_sample
import helpers

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
LOCATION = "us-central1"
MODEL_ID = "6305215400179138560"  # Permanent medical entity NL model
DISPLAY_NAME = f"temp_create_batch_prediction_ten_test_{uuid4()}"
GCS_SOURCE_URI = (
    "gs://ucaip-samples-test-output/inputs/batch_predict_TEN/ten_inputs.jsonl"
)
GCS_OUTPUT_URI = "gs://ucaip-samples-test-output/"


@pytest.fixture(autouse=True)
def teardown(shared_state, job_client):
    yield

    job_client.cancel_batch_prediction_job(
        name=shared_state["batch_prediction_job_name"]
    )

    # Waiting for batch prediction job to be in CANCELLED state
    helpers.wait_for_job_state(
        get_job_method=job_client.get_batch_prediction_job,
        name=shared_state["batch_prediction_job_name"],
    )

    # Delete the batch prediction job
    job_client.delete_batch_prediction_job(
        name=shared_state["batch_prediction_job_name"]
    )


# Creating AutoML Text Entity Extraction batch prediction job
def test_ucaip_generated_create_batch_prediction_ten_sample(capsys, shared_state):

    model_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/models/{MODEL_ID}"

    create_batch_prediction_job_text_entity_extraction_sample.create_batch_prediction_job_text_entity_extraction_sample(
        project=PROJECT_ID,
        display_name=DISPLAY_NAME,
        model=model_name,
        gcs_source_uri=GCS_SOURCE_URI,
        gcs_destination_output_uri_prefix=GCS_OUTPUT_URI,
    )

    out, _ = capsys.readouterr()

    # Save resource name of the newly created batch prediction job
    shared_state["batch_prediction_job_name"] = helpers.get_name(out)
