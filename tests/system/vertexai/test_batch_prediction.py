# -*- coding: utf-8 -*-

# Copyright 2024 Google LLC
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
#
# pylint: disable=protected-access, g-multiple-import
"""System tests for GenAI batch prediction."""

import time
import pytest

import vertexai
from tests.system.aiplatform import e2e_base
from vertexai.generative_models import GenerativeModel
from vertexai.preview import batch_prediction


_GEMINI_MODEL_NAME = "gemini-1.0-pro"
_GEMINI_MODEL_RESOURCE_NAME = f"publishers/google/models/{_GEMINI_MODEL_NAME}"
_GCS_INPUT_URI = "gs://ucaip-samples-us-central1/model/llm/batch_prediction/gemini_batch_prediction_input.jsonl"
_BQ_INPUT_URI = (
    "bq://ucaip-sample-tests.ucaip_test_us_central1.gemini_batch_prediction_input"
)


@pytest.mark.usefixtures(
    "prepare_staging_bucket",
    "delete_staging_bucket",
    "prepare_bigquery_dataset",
    "delete_bigquery_dataset",
    "tear_down_resources",
)
class TestBatchPrediction(e2e_base.TestEndToEnd):
    """System tests for GenAI batch prediction."""

    _temp_prefix = "temp-genai-batch-prediction"

    def test_batch_prediction_with_gcs_input(self, shared_state):
        shared_state["resources"] = []

        vertexai.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            staging_bucket=f"gs://{shared_state['staging_bucket_name']}",
        )

        # Pass the model name and do not specify the output prefix.
        job = batch_prediction.BatchPredictionJob.submit(
            source_model=_GEMINI_MODEL_NAME,
            input_dataset=_GCS_INPUT_URI,
        )
        shared_state["resources"].append(job)

        assert (
            job.model_name == _GEMINI_MODEL_RESOURCE_NAME
        ), f"Unexpected model name {job.model_name} in the job."

        # Refresh the job until complete
        while not job.has_ended:
            time.sleep(10)
            job.refresh()

        assert job.has_succeeded, f"The job has failed with error: {job.error.message}."
        assert job.output_location.startswith(
            f"gs://{shared_state['staging_bucket_name']}/gen-ai-batch-prediction/"
        ), f"Unexpected output location: {job.output_location}."

    def test_batch_prediction_with_bq_input(self, shared_state):
        vertexai.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        model = GenerativeModel(_GEMINI_MODEL_NAME)

        # Pass the model object and specify the output prefix.
        job = batch_prediction.BatchPredictionJob.submit(
            source_model=model,
            input_dataset=_BQ_INPUT_URI,
            output_uri_prefix=f"bq://{shared_state['bigquery_dataset_id']}",
        )
        shared_state["resources"].append(job)

        assert (
            job.model_name == _GEMINI_MODEL_RESOURCE_NAME
        ), f"Unexpected model name {job.model_name} in the job."

        # Refresh the job until complete
        while not job.has_ended:
            time.sleep(10)
            job.refresh()

        assert job.has_succeeded, f"The job has failed with error: {job.error.message}."
        assert job.output_location.startswith(
            f"bq://{shared_state['bigquery_dataset_id']}.predictions"
        ), f"Unexpected output location: {job.output_location}."
